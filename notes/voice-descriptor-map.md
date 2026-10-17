> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 4 — event, descriptor and sample path (build 4486)

Phase 5 follow-up: see `voice-output-contract.md` for both lookup passes,
the selected final-gain alias and mono output seam. Slot0 Y:0x59F is a
mode/mask; Y:0x5A0 is its following phase word. On the selected lookup path,
request skips the phase store at P:0x7F9 and completion commits it.

All work is STATIC ANALYSIS. No device was opened, no firmware was executed,
and no binary was patched. DSP addresses below are **24-bit word addresses**;
ARM struct offsets are bytes. VERIFIED means supported by decoded instructions
and their matching input bytes, not observed on running hardware.

Sources: unchanged ARM BIN and Selection 0/channel 0 program payload; real
DSP56300 decoder from the pinned source described in `tools/PHASE3.md`.
Canonical excerpts/checks: `builds/phase4-trace/dsp-voice-path.asm` and
`builds/phase4-trace/trace.json`. The latter checks 2,040 DSP instruction rows
and 1,994 ARM report rows against source bytes, all twelve address formulas,
original hashes, decoding equality, and byte-identical SYX reconstruction.

Reproduce without hardware:

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_phase4_trace.py --output-dir builds/phase4-repeat-new
```

The output directory must not exist. This tool checks/excerpts the previously
generated disassembly; it does not independently prove every data-flow claim.
Regenerate DSP decoding with `ct_dsp_disasm.py` as documented in PHASE3.md.

## ARM functions and event state

**VERIFIED:** T = `0x200067FC`; S(i) = `0x20005F64 + 0x10*i`.

| Location | Verified role and evidence |
|---|---|
| T+4 | Bank selector, read throughout the allocation and parameter paths |
| T+5 | Selected slot, used for X/Y address calculations |
| T+7 | Allocation/action category; branches in 0x080219E8 change reset/update behavior |
| T+8 | Signed additive note offset, read at 0x080218F8 |
| T+0xA | Incoming note/index byte |
| T+0xB | Incoming level byte, squared at 0x0802192C |
| S(i)+0 | Assigned bank |
| S(i)+1 | Original note/index, matched by release function |
| S(i)+2 | `(input_level * input_level) >> 7` |
| S(i)+3 | Derived absolute note distance; also changed by parameter helper |
| S(i)+4 | 32-bit allocation/lifecycle state, initially `0x8000FFFF` |
| S(i)+8 | Bank-dependent source/category field |
| S(i)+9 | Note plus signed offset: negative values clamp to zero, values >=128 repeatedly subtract 12 |
| S(i)+0xD | Deferred release marker when bank hold field is nonzero |
| S(i)+0xE | Event-generation byte, used by 0x08021CE4 to release preceding generation |

**VERIFIED:** `0x08021D86(r0,r1,r2)` stages note/index, level and signed
offset in T+0xA, T+0xB, T+8 (`0x08021DA8..1DAC`), increments T+0xC, and
calls `0x080219E8` at `0x08021DB2`. The normal wrapper `0x08021DD4`
sets r2=0. `0x080497CA(bank,note,level)` tests level==0 at
`0x0804982E`; zero takes the release path through `0x08049758`, while
nonzero stores the note's held-bit and reaches `0x08021DD4` at
`0x08049890`. This establishes start versus release event classification.
The upstream `0x0803BD58` calls this wrapper at `0x0803BD76`.

**UNRESOLVED:** the exact external MIDI parser/status-byte origin is not
established here. Calling the second event datum velocity is supported by
its note-associated level scaling, rather than an independently decoded
MIDI status packet. No MIDI transmission or hardware inspection was used.

**VERIFIED role of 0x080219E8:** allocate/select a context via
`0x080217B4`, publish its bank, refresh per-slot parameters, construct packed
start/update flags, then tail-call event publisher `0x08021246` at
`0x08021C40`. It uses staged globals, not direct note arguments.
Depending on action, it can reset phase-related state and start/update the
current voice; calling it an unconditional reset is incorrect.

**VERIFIED role of 0x08021C48(r0):** scan twelve contexts and release every
matching bank/original-note context that satisfies its lifecycle test.
It reads DSP Y:0x122+0x60*i at `0x08021C76`; if the ARM high lifecycle
halfword is zero it requires the readback's bit 30. If bank state
`0x200059D8+0x9C*bank+0x98` is nonzero, set S(i)+0xD instead of releasing.
Otherwise update S(i)+4 (clear bits 31/30, set bit 16, low half=FFFF), set
T+5=i, and call `0x080212EA` at `0x08021CC8`.

Direct callers and bounded disassemblies are in `builds/phase4-*-callers.json`
and `builds/phase4-arm-*.asm`. Direct-call scans cannot enumerate all virtual
or indirect callers. The release caller `0x080497C4` is a tail branch.

## Descriptor versus pointed-to state

**VERIFIED:** descriptor D(i) = X:`0xEB+8*i`, i=0..11, occupying
X:[0xEB,0x14B). Eight fields, stride eight words. P:0x2881 initializes
them; P:0x198D executes them. The executor also visits two other descriptors
before X:0x15B; these must not be counted as additional synth voices.

| Descriptor field | VERIFIED initialization/consumer | ARM writes / interpretation |
|---|---|---|
| +0 | P:0x281; P:0x19A5 loads r1, P:0x19AC calls it | No event-path write found; dispatch function |
| +1 | X:0x1960+0xC*i; P:0x19A6 -> r0, P:0x281 -> X:2 | Kernel/table scratch pointer; internal use at P:0x387; no direct event write found |
| +2 | Y:0x11F+0x60*i; P:0x19A7 -> r4 | Control/state block V(i) |
| +3 | Y:0x131+0x60*i; P:0x19A8 -> r5 | Secondary pointer inside the same 0x60-word Y context |
| +4 | X:0x57A+0x4A*i; P:0x19A9 -> r7 | Event mailbox E(i), then prepared coefficients at E(i)+1 |
| +5 | Numeric pointer 0x59F+0x28*i; P:0x19AA -> y1; P:0x28F -> r3 | Used for Y sample-generator state in P:0x77F; not loaded into r3 by the executor itself |
| +6 | Zero; P:0x19AB -> r6 | P:0x2AB replaces r6. Precise general purpose UNRESOLVED |
| +7 | Bank word; P:0x282 reads x:(r3) after executor consumed seven words | ARM 0x08021A08 writes X:0xF2+8*i with bank (r1=bank<<8) |

The +5 initialization is a pointer value, not a claim that this pointed-to
block belongs to X: the sample consumer explicitly uses Y accesses. Earlier
generic descriptions of the descriptor as holding note/velocity values are
superseded: those values are in its pointed-to state, not eight scalar fields.

**VERIFIED:** P:0x2881's startup bank initializer has an increment followed
by a threshold comparison. Do not infer its precise six/six assignment from
the count alone. The event path explicitly overwrites +7; ARM allocation and
the DSP allocation helper independently establish the six/six grouping below.

## Proven ARM-to-DSP data flow

All scalar writes use `0x080292F8(channel=0,value,address)`. Its data sender
`0x080291E0` transmits the upper 24 bits of the supplied 32-bit value.
Address bit 15 selects Y; clear selects X. DSP P:0x198 writes the current
address and advances it; this is runtime addressed control, not boot traffic.

| ARM source / conversion | DSP destination (i=slot, b=bank) | Descriptor relationship / evidence |
|---|---|---|
| T+4; value=bank<<8 | X:0xF2+8*i = bank | D(i)+7; 0x080219FA..21A08 |
| S(i)+9; byte(note-60)<<24 | Y:0x159+0x60*i = signed(note-60)<<16 | V(i)+0x3A; 0x080272F2..27308 |
| Parameter-dependent note offset in 0x08027FA4 | Y:0x15C+0x60*i | V+0x3D; separate note-follow initialization seed, not replacement of Y:0x159 |
| Timing/rate conversion in 0x08027FA4 | Y:0x15A,0x15B+0x60*i | V+0x3B/+0x3C; note tracking step/smoothing controls, not direct frequency |
| S(i)+2 and parameter 0x27 -> 0x08027D9A | Y:0x14D+0x60*i | V+0x2E; first envelope target, written 0x0802715E |
| S(i)+2 and parameter 0x2C -> same helper | Y:0x153+0x60*i | V+0x34; second envelope target, written 0x08027214 |
| Packed start/update word, force bit31 | X:0x57A+0x4A*i = word>>8 | E(i); 0x08021246..2126E |
| Release word=0, force bit31 | E(i)=0x800000 | 0x080212EA -> 0x0802136E -> publisher |
| Release helpers' 0x7FFFFF00 | Y:0x146,147,13B,13D,13F,141 +0x60*i = 0x7FFFFF | Working/rate fields; 0x080212EA and 0x08021272 |
| Init/preceding-generation release constants | Y:0x150+0x60*i = 0x100000 or 0x200000 | V+0x31, envelope coefficient/control; not proven to be the ordinary note gate |
| Packed bank control / another packed word | X:0x296,297+0x172*b | Shared bank flags, not per-slot; 0x08021B4E/21B8E or alternate branches |
| Zero on start | X:0x5C3+0x4A*i | Last word of the X context; 0x08021A5E; exact role UNRESOLVED |

**VERIFIED:** the 0x60-word Y context contains DSP-modified flags V+3,
note-follow state V+0x10, primary level V+0x11 and scaled note V+0x16.
Read/modify/write sites are detailed below. The 0x4A-word X context contains
an event mailbox plus prepared generator/filter/gain coefficients. The
0x28-word Y sample context holds persistent sample state. Full field layouts
for all three blocks remain **UNRESOLVED**; a stride does not prove every
word is always active or that neighboring regions never have other uses.

## Two groups of six: evidence beyond the count

**VERIFIED:** ARM `0x080217B8..217C8` sets inclusive allocation bounds 0..5
for bank zero, 6..11 otherwise. The slot's bank byte is stored at
`0x0802192A`; the same bank is written into D+7 at `0x08021A08`.
DSP P:0x1BB3 likewise chooses r1=0 or 6, flags pointer Y:0x122 or 0x362,
timestamp pointer X:0x5C2 or 0x77E, then examines exactly six slots with
0x60/0x4A strides. It publishes a selected slot in X:0x35, which ARM reads
at `0x08021810`. It compares primary levels, flags and timestamps: this is
an allocation/stealing policy, not merely a bank-sized loop.

**VERIFIED:** D+7 selects X parameters with stride 0x172 at P:0x28B..298
and Y intermediate parameters with stride 0x2A. P:0xA84..A94 selects a
bank sample-sum buffer X:0x2DF0 (zero) or X:0x2E50 (nonzero).

**HYPOTHESIS, strongly supported:** these are Synth 1/Synth 2 with six
voices each. Two separately parameterized groups of six note-controlled,
sample-generating contexts are VERIFIED. The correspondence to the product's
UI names/numbers is not yet established by an independently traced track/UI
selector. Other allocation modes may have different note reuse behavior.

## Event/gate lifecycle

**VERIFIED:** P:0x29D reads E(i) into y1 and P:0x29E clears E(i). This is a
consumed event mailbox, not a persistent gate bit. P:0x2BD tests the signed
event; a negative event replaces the old Y:V+3 flags at P:0x2C0. Mask
0x7FFF7F removes event-marker bit23 and trigger bit7 before storing flags
at P:0x2C5. P:0x2C7 separately tests bit7 of the original event.

When trigger bit7 is set, P:0x2C9..33F updates component flags/state, records
a timestamp at E+0x48 and can reset generator state. It then updates
parameters and generates samples (P:0x33F..386). The normal packed start
path at ARM 0x08021B92..21C40 supplies bit7 in the DSP event's low byte.
The exact packed word varies with action and parameters.

Ordinary note release publishes 0x800000: marker set, trigger clear, all
processed flags zero. P:0x343 then uses retained primary level Y:0x130+i*0x60:
if >=0x100, processing continues at P:0x37A; below threshold the path can
update fading state and return at P:0x379 without the full generation path.
P:0x4D5 uses the cleared lifecycle flags to select decaying/releasing state
updates. This proves an activation/release lifecycle coupled to level state.
It does not support renaming Y:0x150 as a simple gate flag.

## Pitch to periodic sample state

Choose i=0, b=0, and the ordinary generator class >=8 path in P:0x77F.
This is a static control-flow witness, not an executed or recorded note.

1. **VERIFIED:** ARM staged note+offset becomes S+9 at 0x0802190E.
   0x080272F2..27308 writes `(note-60)<<16` to Y:0x159. The optional
   0x08027FA4 offset writes `(note+offset-60)<<16` to the separate seed
   Y:0x15C; P:0x327..32B copies that seed to current note Y:0x12F when
   processed flag bit6 is set. The target remains Y:0x159.
2. **VERIFIED:** P:0x4D5's two preceding six-word envelope-parameter passes
   advance r6 from Y:0x14D to 0x159. P:0x5C0 reads current Y:0x12F;
   P:0x5C1 reads target Y:0x159; P:0x5C2..5C9 computes signed target
   distance, limits it with Y:0x15A, and smooths with Y:0x15B.
3. **VERIFIED:** P:0x5CB stores updated note-follow state in Y:0x12F.
   P:0x5CA multiplies the prior current value by Y:0x13 (0x555555,
   initialized at P:0x280E); P:0x5CC stores that scaled result in Y:0x135.
   Parallel moves use the pre-ALU value; this is not an instantaneous
   direct copy of the newly written target.
4. **VERIFIED:** P:0x6A7 loads Y:(r5+4)=Y:0x135 and P:0x6A8 adds it
   to each of three frequency-control calculations. After scaling/clamping
   P:0x6B3..6B5 stores the results in bank intermediates Y:0x7F,83,87.
   Modulation contributions can also enter this calculation.
5. **VERIFIED:** P:0x387 runs three component preparations. P:0x3E1 reads
   those frequency controls; P:0x3E4..415 performs multiplies, shifts and
   a lookup through r2=X:0x2000 (Y:0x18). P:0x3F0..452 combines these with
   other controls. P:0x430 or 452 stores the resulting y1 in the prepared
   component word Q+9; Q=E+1+14*j for component j=0..2 on these paths.
6. **VERIFIED:** P:0x7E9 reads that prepared word into y0. P:0x7E4..7EA
   combines persistent Y state and an offset; P:0x7EF..7F2 repeatedly
   adds y0 to two phase tracks (one initially offset by 0x800000), writing
   phase/index data to X:0x2C46. P:0x7F3..7F9 updates persistent Y state.
   For i=0,j=0 the context begins at Y:0x59F and phase is Y:0x5A0;
   request skips P:0x7F9, while completion writes the phase. Subsequent setup
   restores/increments the state pointer at P:0x99A..99D.
7. **VERIFIED:** P:0x806..81B converts phase data into addressed lookup
   work; P:0x832..84B multiplies fetched values and accumulates samples
   into a three-component working buffer Y:0xA01 with stride three.
   The first processing pass queues lookups and returns; P:0x19BF can
   invoke P:0x77F again to complete pending contexts.

**VERIFIED pitch role:** the event's octave-wrapped note index controls
the advance of periodic sample-generator phase, through the exact consumers
above. This exceeds a string-name guess. **UNRESOLVED:** exact note-to-Hz
calibration, table contents for every configuration, all waveform classes,
and the complete interpolation/harmonic algorithm.

**VERIFIED worker boundary:** normal channel-one P:0x120 loads an address
from shared X work, P:0x125 reads X:(r0), and P:0x126 replaces the work word
with fetched data. Its ICC signaling matches channel-zero queue/await logic.
It is an address-lookup worker, not independently verified as another synth.
Physical core/channel assignment remains unresolved.

## Event level / velocity influence

**VERIFIED:** T+0xB -> S+2 = floor(level^2/128) at ARM 0x08021928..21932.
Helper 0x08027D9A reads S+2 at 0x08027DB2, combines it with sensitivity
parameter d=parameter-64, optionally inverts q for negative d, and produces
a multiplicative envelope-target factor. In exact integer terms:

```
q = level*level >> 7
v = q if d >= 0 else q XOR 127
p = abs(d) * (v-127)
factor = 0x7F00 + (0xFF if p == 0 else 4*p)
target24 = (tracking_helper_result * factor mod 2^32) >> 8
```

The tracking helper is 0x080284DE; it can also depend on the note. At zero
tracking depth it returns FFFF. Thus the input-level factor is distinct
from bank patch settings, but is intentionally patch-sensitive. Neutral
sensitivity (parameter=64) removes this input-level dependence.
With sensitivity=127 and tracking=FFFF, event levels 0..127 increase the
target monotonically; reproducible examples are in `trace.json`.

**VERIFIED:** writer 0x0802715E sends this target to Y:0x14D+0x60*i.
P:0x4E7 loads it, and P:0x4F3 loads primary level Y:0x130+0x60*i.
The paths through P:0x4F7..55B update that level toward the target or
decay it using flags/rates. In P:0x387, r4 has advanced three words from
V by P:0x4BE; adding 14 reaches Y:0x130. P:0x4C6 loads that level,
P:0x4C9 multiplies it by a parameter-derived coefficient, and
P:0x4CB..4D1 prepares a gain difference/ramp.

This proves note-associated input level affects DSP envelope level and
gain computation, rather than merely altering a patch-volume global.
Phase 5 closes the selected final gain alias: P:0x4D0/P:0x4D1 emit X:0x5BC/
0x5BD, consumed at P:0xA8A/P:0xA8D after the post subroutine's seven-word
advance. **UNRESOLVED:** every alternate branch and all post factor meanings.
Do not assume all envelope targets are
amplitude envelopes; the second target has other possible modulation uses.

## Samples, mixing and output boundary

**VERIFIED:** P:0x77F performs component phase progression and numerical
sample processing; P:0x9C8..9D8 combines the three component buffers through
multiplies/MACs. Subsequent choices include P:0xBDD and other processing
branches. P:0xA7F..A94 performs a ramped multiplication/addition into one
of X:0x2DF0 / X:0x2E50, chosen by D+7. P:0x759 clears these group buffers
before the descriptor passes. Slots assigned the same bank share this sum.

**VERIFIED:** the same DSP program processes each group further via
P:0x11E9/11F1, P:0x1203/1209 and P:0x125D/126A. P:0x120F includes
recursive state and MAC/subtract operations consistent with filtering.
The resulting streams reach Y:0x840 and Y:0x880; P:0x242..24E multiplies
and combines both into Y:0x800. Additional terms and further processing
are present, so this is not claimed as the only mix or final DAC buffer.
P:0x274 calls P:0x21C4, and the existing ESAI/DMA output map remains valid.
NXP's [DSP56724 reference manual](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf),
Table 5-9 and chapter 9, corroborates P:0x3E as ESAI transmit-last-slot
and the peripheral identity. Complete effect names/topology are UNRESOLVED.

**VERIFIED conclusion:** the stock normal payload executes note-controlled
periodic voice generation, envelope/gain arithmetic and bank mixing on the
DSP. ARM performs allocation, note/parameter conversion and addressed state
updates; the traced event traffic is control data rather than audio blocks.
This verifies DSP execution of stock voice synthesis. Calling every algorithm
"Nova", assigning all stock audio processing to the DSP, or asserting a
finished Plaits replacement boundary would go beyond this evidence.

## Single best next step

Phase 5 establishes the selected mono-buffer/final-gain contract. Next establish
clock/rate and RAM ownership, then perform a conditional compute/state study.
Absolute amplitude, a real preset snapshot and full replacement ABI remain
unresolved; no implementation yet.
