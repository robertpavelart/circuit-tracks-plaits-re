# DSP host communication and ARM correlation — build 4486

Phase 4 update: see `voice-descriptor-map.md` for the instruction-level event,
note-to-phase and level-to-gain trace. The older synth-ownership hypothesis
below is now verified for note-controlled DSP voice generation. Y:0x150 is
an envelope coefficient/control; the ordinary start/release mailbox is
X:0x57A+0x4A*i, and the note target is Y:0x159+0x60*i.

2026-10-05. Static-only. DSP addresses are P/X/Y word addresses; ARM addresses
are byte addresses. VERIFIED is static evidence, not an on-device observation.

## Receive path and dispatcher

**VERIFIED, normal selection/channel zero:**

```text
SHI receive-FIFO-not-empty vector P:0x44
  JSR P:0x156
    save state to Y:0x2000..0x2005
    P:0x15E reads HRX at X:0xFFFF94
    P:0x15F tests GPIO PDRC bit 8 (X:0xFFFFBD)
      low: P:0x198 writes a data word through the saved address
      high: P:0x161 begins command-bit dispatch
    restore state; RTI at P:0x1B3
```

This is a GPIO-qualified, stateful memory-access protocol. The received top
byte is not a standalone note-on/note-off opcode namespace. No high-level
MIDI opcode dispatcher has been found in this receive routine.
The exact board wire connecting ARM auxiliary outputs and DSP GPIO bit 8 is
**HYPOTHESIS**; their command/data roles correlate on both sides.

NXP maps X:0xFFFF94 to HRX, X:0xFFFF93 to HTX, X:0xFFFF91 to HCSR and
X:0xFFFF90 to HCKR. The handler initializes/uses these exact regions, and
the receive vector matches the documented interrupt map.

## Verified normal-image transport operations

`W` below is a received, MSB-first 24-bit word. In 16-bit mode the received
two bytes occupy W bits 23..8 and the low byte is zero. Tests are priority
ordered: GPIO lane first, then bits 21, 22, 20, 19 and finally bit 23.

| Condition / usual first byte | Handler | Verified action | Observed length |
|---|---|---|---|
| data lane (GPIO bit 8 low) | P:0x198 | write W to saved X/Y address; increment X:0x10 | 3 bytes in 24-bit mode; 2 in 16-bit mode |
| command lane, W bit 21 / `20` | P:0x163 | store W in X:0x12; signal GPIO bit 9 | one command word |
| command lane, W bit 22 / `40` | P:0x1A0 | read saved X/Y address into HTX; increment pointer | one command word |
| W bit 20 / `10` | P:0x171 | set pointer to `(W<<8)-2`, low 24 bits | one command word |
| W bit 19 / `08`..`0B` | P:0x17B | pointer = W & 0x3FFFF | one command word |
| ordinary address / `00` | P:0x181/P:0x185 | pointer = W & 0x7FFF; retain W flags in X:0x11 | one command word |
| address form plus bit 23 / `80` or `88`..`8B` | P:0x188 | save flags; read X/Y word into HTX; increment pointer | command word plus another clocked word to retrieve reply |

W bit 15 selects Y when set and X when clear for ordinary address/read
transactions. Data writes/read-next use the saved selector in X:0x11.
Extended **write** address branches do not replace X:0x11, so they inherit
the previous memory-space state; they must not be treated as independently
self-describing packets. Combining flags changes priority, not necessarily
introducing a new command ID.

**VERIFIED width control:** main loop P:0x113 consumes the pending X:0x12
flag and calls P:0x12D. Control bit 8 selects HCSR values:

- `20 01 00`, received as W=0x200100: HCSR -> 0x10A5, **16-bit** SHI words.
- `20 00`, sent while in 16-bit mode, received as W=0x200000:
  HCSR -> 0x10A9, **24-bit** SHI words.

This follows the actual HCSR HM[1:0] bits and NXP Table 10-4. The input parser
`ct_dsp_protocol.py` only classifies supplied bytes offline; it never transmits.

## ARM boot versus runtime paths

**VERIFIED boot:** 0x08029260 -> 0x08029200 sends count/address/program words,
first bootstrap, then selected channel-zero and channel-one images. Do not
interpret those headers as runtime messages. Post-boot initialization uploads
numeric tables and subsequently uses the same runtime memory protocol.

**VERIFIED runtime constructors:**

| ARM entry | Packet/data behavior | Normal DSP correspondence |
|---|---|---|
| 0x080292DC | `00 AH AL` sets ordinary address | P:0x181/P:0x185 |
| 0x080292F8 | cached-address write; transmits ARM value bits 31..8 as one DSP word | address setup then P:0x198 |
| 0x080291E0 | three-byte data transfer under data lane | P:0x198 |
| 0x08029344 | `80 AH AL`, then `40 00 00`; returns initial word left-aligned by 8 | P:0x188 then P:0x1A0; pipeline clocks total 6 bytes |
| 0x08029314 | extended-address data write, value shifted into 24-bit format | P:0x17B then P:0x198 |
| 0x080294CA | builds bit-19 extended address | P:0x17B; ARM mask is 19 bits, DSP consumption masks 18 |
| 0x080295BA | `88` plus upper address bits, followed by `40 00 00` | P:0x17B/P:0x188/P:0x1A0 |
| 0x080294AC | `10 AH AL` paged address, with pointer compensation | P:0x171 |
| 0x080295E4 | sends `20 01 00`, then waits for ready | P:0x163 -> P:0x12D, enter 16-bit words |
| 0x08029626 | sends `20 00`, waits for ready | P:0x163 -> P:0x12D, return to 24-bit words |
| 0x0802968E / 0x080296B0 | DMA byte buffer transfer | P:0x198 in current word width |
| 0x08029528 | paged address + width switch + bulk read into ARM buffer | P:0x171, P:0x163, X/Y memory read/data path |
| 0x0803BAA2 | polling three-byte SPI transfer | HRX/HTX word clocking |
| 0x0803BA96 -> 0x080377DE | bulk SPI2 transfer using DMA1 RX3/TX4 | both boot and runtime use underlying SPI transport |

Variable data cannot be fully recovered as constant packets. Read pipelines
queue subsequent words; handler side effects and GPIO state are part of the
protocol. There is no verified dedicated SPI `note_on=0x90` command here.

## Secondary mailbox at Y:0x2C

**VERIFIED:** the ARM accesses this mailbox through ordinary Y-memory
address 0x802C. Main loop calls P:0x1C53, which interprets its low nibble as
a selector and derives an output pointer from the remaining bits.
This is separate from the immediate SHI handler at P:0x161.

| Selector | DSP branch / routines | Verified behavior |
|---:|---|---|
| 0 | P:0x1C64 -> 0x1CFE | generated table path, count 0x400 |
| 1 | P:0x1C70 -> 0x1CFE | generated table path, count 0x2000 |
| 2 | P:0x1C7D -> 0x1CF4 | generated/transformed table path; exact purpose unresolved |
| 3 | P:0x1C84 -> 0x1CE6,0x1CFE | copy/transform then generate table |
| 4 | P:0x1C94 -> 0x1CD0,0x1CFE | restore X:0x2800 -> X:0xC00, then generate |
| 5 | P:0x1CA2 -> 0x1CD9,0x1CFE | alternating-word transform then generate |
| 6 | P:0x1CB2 | copy 512 X:0xC00 words into selected Y destination |
| 7 | P:0x1CBB | derive destination and copy three words from X:0xC00 into X data |

Mailbox completion stores the short data immediate 0x80, i.e. 0x800000, to
Y:0x2C. ARM reads that left-aligned as 0x80000000 before posting more work.
ARM 0x08035E28 uses selectors 2, 3, 4, 5 and 0 and waits on this sentinel;
its 0x08035E66/0x08035F04 calls write the corresponding mailbox word.
**HYPOTHESIS:** these are waveform/table generation jobs. The exact oscillator
type names are not assigned from selector numbers alone.

## Concrete ARM-to-DSP correlations after boot

| ARM site/function | Proven destination/operation | DSP path / purpose status |
|---|---|---|
| 0x080210CA | write X:0x13 = 0x00000C | main loop P:0x125 tests X:0x13; enables processing path |
| 0x080210D6 | write X:0x14 = 1 | state initialization; deeper consumer unresolved |
| 0x080210F0 | write Y:0x150+0x60*i = 0x100000, i=0..11 | P:0x198 memory write; twelve-slot control/state **HYPOTHESIS** |
| 0x0802126E | write X:0x57A+0x4A*i with supplied flag/value | matches descriptor table initialized at P:0x2881 |
| 0x08021A08 | write X:0xF2+8*i = bank number | matches final word of twelve descriptors at X:0xEB |
| 0x08021D4A | write Y:0x150+0x60*i = 0x200000 | per-slot event update; exact gate/release meaning **UNRESOLVED** |
| 0x080270D0 | parameter lookup/conversion -> Y:0x148+0x60*i | parameter/state update; user-facing parameter name **UNRESOLVED** |
| 0x08035E66 / 0x08035F04 | write Y:0x2C table-job request | P:0x1C53 selector branches above |
| 0x08035ECE..0x08035EF4 | 16-bit buffer upload to table area, then restore 24-bit mode | width-control + data-memory path; table loader |
| 0x08048D98 | bulk read via 0x08029528 | confirms DSP-to-ARM buffer path; full data purpose unresolved |

**VERIFIED:** ARM routines 0x0802161A/0x080216C6/0x08021706 select slots using
occupancy/history values. 0x080217B4 sets slot ranges 0..5 or 6..11, according
to the bank. 0x08021C48 matches event data against stored slot data and invokes
updates. Note-like values are kept in 0..127 with repeated subtraction of 12
for octave wrapping. These are data-flow observations.

**HYPOTHESIS:** slot allocation corresponds to voice allocation; the bounded
octave-wrapped field is pitch and the squared/scaled input is velocity.
**UNRESOLVED:** a complete trace from raw MIDI status through these functions,
precise note-on/off flags, patch/preset selection, each oscillator/filter/
envelope parameter, macros, effect identities and all event field meanings.
These names must not be promoted to VERIFIED without completing those paths.

## Selection and channel routing

**VERIFIED:** 0x0801F51E dispatches a mode byte:

- mode 0 -> 0x0801F554 -> upload selection 0 and perform normal post-boot setup;
- mode 1 -> upload selection 1 through 0x0801F544, then calls 0x08029152;
- other values are stored but do not enter either reviewed upload branch.

Boot/application call 0x0801D582 supplies a zeroed mode. The service-message
handler 0x08026918 checks byte 7 of an existing incoming buffer. Values
0x5C, 0x5D and 0x71 force mode 1 when the current mode is not already 1,
using constant halfword 0x0001 at 0x08026B20. Those numbers are **ARM-side
service-message IDs**, not DSP SHI opcodes.

0x5C then writes test parameters through 0x0802916C to X:5..8; 0x71 reaches
0x0802918C and writes X:2; 0x5D runs 0x0801F4F4, using X:9/10 and reading
Y:3. The selection-one program reads X:9/10 at P:0x1CE, calls the pattern-test
routine at P:0x2D5 and publishes results in Y:3..8. This establishes a
diagnostic/test use of selection 1 without naming an undocumented user mode.

ARM path 0x0801F2E6..0x0801F302 restores mode zero when its enclosing
condition is reached and current mode is nonzero. The complete outer message
condition and all user-visible entry points remain **UNRESOLVED**.

Channel choice is deterministic during upload: bootstrap to channel 0,
table[selection] to channel 0 and table[selection+2] to channel 1. Channels
control different GPIO selectors (PD9/PD8), not an alternating voice number.
Normal runtime parameter calls predominantly use channel 0. Channel-one code
uses ICC/shared-memory services rather than the channel-zero SHI dispatcher.
That supports a cooperating-core interpretation; numeric physical core identity
and whether endpoint numbering equals core numbering remain **HYPOTHESES**.

## Answer to the engine-location question

**VERIFIED:** STM32 traffic includes DSP parameter/state memory updates,
table jobs, bulk 16-bit data uploads and readbacks. The large DSP program
configures ESAI audio DMA and executes substantial arithmetic processing
through twelve descriptors with matching ARM-side slot/bank structures.
It is not merely a boot loader or an opaque external data store.

**Strong HYPOTHESIS:** the normal channel-zero DSP program contains the stock
synthesis/audio engine, with ARM handling scheduling, slot allocation and
parameter conversion. This is much stronger evidence than the original upload
strings, but does not yet identify every synthesis algorithm or prove that all
audio/synth/effects work lives on the DSP. The simple claim that ARM only does
UI/sequencing is incomplete: ARM also allocates slots and constructs parameters.

The protocol-level answer is **lower-level addressed control/state and bulk
data**, rather than dedicated high-level note packets. That does not imply ARM
renders the audio waveform; the DSP's processing and ESAI paths provide
independent evidence of DSP audio work.

## Best next step and evidence

Trace one complete slot event: ARM 0x08021C48/0x080219E8 through the writes to
Y:0x150+0x60*i and X:0x57A+0x4A*i, then follow descriptor execution at
DSP P:0x198D -> P:0x281 to its consumers. Connect the upstream MIDI/event
classification and downstream sample calculation to establish exact gate,
pitch and velocity semantics for one voice before expanding parameter names.

Evidence: `builds/phase3-*.asm`, `builds/phase3-arm-callers.json` (275 candidate
direct-call sites, requiring code review), `builds/phase3-verification.json` and
the reconstructed-memory manifest. Whole-image sweeps are not a function map.
Reproduction commands are in `tools/PHASE3.md`.

[NXP DSP56724RM](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf)
supports register/vector/word-width interpretation; the packet bit dispatch
and ARM correlations above come from the local firmware instructions.
