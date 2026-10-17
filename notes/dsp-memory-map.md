> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# DSP boot records and memory reconstruction — build 4486

Phase 4 update: `voice-descriptor-map.md` maps all eight dispatch fields,
separate pointed-to state blocks, and the verified note-to-phase and
level-to-gain data flow. The +5 pointer is consumed in Y memory; bank field
+7 is explicitly updated by ARM. Stock note-controlled DSP voice generation
is now verified; product UI bank naming remains a hypothesis.

2026-10-05. Strictly static analysis. DSP addresses in this document are
**24-bit word addresses**, not ARM byte addresses. Labels are analyst labels.
VERIFIED describes reproducible static evidence; no device RAM was accessed.

## Boot-record structure: all five streams

**VERIFIED:** each observed upload is exactly one count/address/data record:

| Stream byte range | Meaning |
|---|---|
| [0,3) | big-endian 24-bit payload-word count |
| [3,6) | big-endian 24-bit load address |
| [6,6+3*count) | exactly count program words |

There is no explicit record-type tag, memory-space field, terminator or separate
entry field in these streams. The uploaded word count excludes the two header
words. Thus the large stream has **10848 total words, 10846 payload words**.
Do not reinterpret incidental payload values as nested load-record headers.

The corroborated DSP56724-compatible SHI boot contract loads these words into
PRAM and begins executing at the load address. This P-space interpretation is
supported by the documented boot format and verified instruction/vector
patterns. Exact physical silicon remains **UNRESOLVED**.

| Stream | ARM source offset | Header count | P load range, exclusive end | Boot start | Program entry branch |
|---|---|---:|---|---|---|
| bootstrap | 0x196E0 | 8 | P:[0,0x8) | P:0 | P:6 jumps to P:0xFFFFFE |
| selection0-channel0 | 0x1F0 | 10846 / 0x2A5E | P:[0,0x2A5E) | P:0 | P:0 jumps to P:0x100 |
| selection0-channel1 | 0x8110 | 364 / 0x16C | P:[0,0x16C) | P:0 | P:0 jumps to P:0x100 |
| selection1-channel0 | 0x44EFC | 808 / 0x328 | P:[0,0x328) | P:0 | P:0 jumps to P:0x17F |
| selection1-channel1 | 0x4587C | 360 / 0x168 | P:[0,0x168) | P:0 | P:0 jumps to P:0x100 |

All loads start at zero. These are alternative/context-specific P images,
**not five segments to concatenate into one P address space**. The bootstrap
is uploaded/executed before the selected channel-zero image replaces P:0.
Its reviewed instructions change OMR bits 7, 22 and 21 before the ROM jump;
the complete consequences of those mode bits are **UNRESOLVED** here.

For an uploaded P address `p`, the source byte offset is
`stream_source_offset + 6 + 3*(p-load_address)`.
Source hashes remain in `firmware/dsp/build-4486/manifest.json`; a complete
machine-readable field/record map is `builds/phase3-boot-records.json`.
Parser: `tools/ct_dsp_boot.py`, with strict alignment/count/range checks.

## Architecture and disassembler validation

**VERIFIED:** the large payload contains executable DSP56300-family program
memory, interleaved with embedded constants/tables. It is not solely an opaque
data block. Independent NXP APR30 examples corroborate `0C0100` as JMP P:0x100,
`0AF080 + extension` as long JMP and `0BF080 + extension` as long JSR.
The reset/vector branches, peripheral operands and return instructions match.

No local DSP decoder was found on PATH or in checked local tool directories.
Existing Rust 1.98.0 compiled only the core/disassembler components of the
MIT-licensed [mborgerson DSP56300 project](https://github.com/mborgerson/dsp56300)
at commit `c60aeedb6a6014850204c71e53bc0cf5b3104222`. These libraries have no
external dependencies. No cargo package downloads, emulator execution or new
toolchain installation occurred. Capstone was used only for ARM, not DSP.

The downloaded C++ [dsp56300 project](https://github.com/dsp56300/dsp56300) at
`44353be2f0156cac970c6ab4f467ea1998b40605` was also inspected as an alternative;
it was not compiled or used to produce the delivered disassembly.

Validation:

- 135 upstream decoder tests and 61 disassembler tests passed.
- A separate NXP APR30 byte fixture produced the expected JMP/JSR/NOP/RTS text.
- Normal image vectors P:0x3E/P:0x44 target valid instruction boundaries
  P:0x1B4/P:0x156, ending in RTI.
- Every direct branch inside reviewed normal SHI ISR P:[0x156,0x1B4) targets
  another decoded boundary within that handler.
- Startup SHI, ESAI, ICC and GPIO addresses agree with DSP56724-family maps.
- Short data-register immediates are left-aligned; for example `move #$80,x0`
  supplies 0x800000, not 0x000080. This matters for mailbox-idle interpretation.

**UNRESOLVED:** exact DSP part/package, complete DSP5672x-specific instruction
coverage and all code/data boundaries. Whole-image linear sweeps include data
decoded as instructions; the 469 `dc` lines in the large image are not a
decoder-failure percentage. Preserve raw word columns, particularly for data.

## Normal channel-zero P layout and important entries

| P region/entry | Status and role |
|---|---|
| 0 | VERIFIED reset branch to 0x100 |
| [0,0x100) | VERIFIED mostly zero vector area, with handlers at 0x3E and 0x44 |
| 0x3E -> 0x1B4 | VERIFIED ESAI transmit-last-slot vector and audio-buffer ISR |
| 0x44 -> 0x156 | VERIFIED SHI receive-FIFO-not-empty vector and receive ISR |
| 0x100 | VERIFIED startup; waits for ICC value 0x030002 at Y:0xFFFFD4 |
| 0x113 | VERIFIED main loop; checks transport-control flag and calls work routines |
| 0x12D | VERIFIED SHI width reconfiguration, consuming X:0x12 bit 8 |
| [0x156,0x1B4) | VERIFIED host memory-transaction parser/dispatcher |
| 0x198D | VERIFIED descriptor executor, indirect call at 0x19AC |
| 0x1C53 | VERIFIED secondary mailbox dispatch on Y:0x2C low nibble |
| 0x25DB | VERIFIED startup orchestration and host-initialization waits |
| 0x2779 | VERIFIED X/Y/shared-memory clear and external-interface setup |
| 0x2881 | VERIFIED twelve processing descriptors at X:0xEB, eight words each |
| 0x29EC | VERIFIED copy of 55-entry indirect-target table to X:0x9DB |
| 0x2A2D | VERIFIED ESAI, DMA, GPIO and SHI setup |

The image has executable routines and P-resident data throughout, not a single
proven text/data split. No blanket classification of P:[0x100,0x2A5E) as code.

## Known X/Y initialization and runtime layout

The following are instruction-derived regions, not additional boot records.

| Space/range or address | Evidence / meaning |
|---|---|
| X:[0,0x6000), Y:[0,0x6000) | VERIFIED startup zero loops at P:0x2786; subsequently modified |
| X:[0x30000,0x38000) | VERIFIED startup clear at P:0x278F; shared-memory worker uses this region |
| X:0x10 | VERIFIED current host word pointer |
| X:0x11 | VERIFIED saved transaction flags, including X/Y bit 15 |
| X:0x12 | VERIFIED host transport-control mailbox |
| Y:[0x2000,0x2006) | VERIFIED saved registers/accumulators for normal SHI ISR |
| Y:0x2C | VERIFIED application/table-service mailbox; negative/0x800000 idle state |
| X:[0xEB,0x14B) | VERIFIED twelve eight-word processing descriptors |
| Y:0x11F+0x60*i, Y:0x131+0x60*i | VERIFIED per-descriptor parameter/state bases, i=0..11 |
| X:0x57A+0x4A*i | VERIFIED per-descriptor state base; ARM updates same stride |
| X:0x59F+0x28*i | VERIFIED additional per-descriptor base |
| X:0x1960+0xC*i | VERIFIED per-descriptor base |
| X:[0x9DB,0xA12) | VERIFIED 55-entry indirect-target table copied from P:0x29F6 |
| Y:[0x1000,0x1400) | VERIFIED ring-buffer clear at P:0x2652; pointers Y:0xFFD/0xFFE |
| X:0xC00 / X:0x2800 | VERIFIED 1024-word host table and copied table in startup path |
| X:0x2000 / X:0x2200 | VERIFIED ARM-generated post-boot numeric tables |
| X:[0x1600,0x1940) | VERIFIED ARM upload of 832 numeric values |

Descriptor executor P:0x198D reads fields, performs `JSR (r1)` at P:0x19AC and
advances through twelve descriptors plus subsequent processing descriptors.
Initialization at P:0x2898 uses a zero/one descriptor field and a comparison
against six after incrementing its counter; its precise initial grouping is not
assumed. ARM independently maintains twelve slots in ranges 0..5 and 6..11
and writes bank values to corresponding descriptor fields. Interpreting these as two six-voice synth
banks is a strong **HYPOTHESIS**, supported by code/data relationships, not a
string-name inference.

Reviewed P-to-X copies exported by `ct_dsp_reconstruct.py`:

| Copy instruction | P source | X destination | Words |
|---|---|---|---:|
| 0x2620 | 0x262C | 0x1D53 | 16 |
| 0x2629 | 0x263C | 0x7D | 8 |
| 0x271D | 0x268C | 0x1EDD | 139 |
| 0x29F2 | 0x29F6 | 0x9DB | 55 |

Outputs and hashes: `firmware/dsp/reconstructed-4486/manifest.json`. It includes
the full uploaded P payload and four exact initialized-table segments, plus all
55 target values. This is explicitly **partial** X/Y reconstruction: remaining
constant stores, transformed tables, hardware state, host-written data and
execution-dependent state are not fabricated into a complete RAM image.

## Other selectable images

**VERIFIED:** both channel-one programs implement an ICC/shared-memory worker:
they advertise 0x030002, use X:0x30000 and exchange Y:0xFFFFD0/0xFFFFD1 poll
bits and Y:0xFFFFD7 data with the other processing context. Normal channel-one
main loop is P:0x10E; alternative channel-one loop is P:0x109.
The normal channel-zero entry waits on the matching ICC word at Y:0xFFFFD4.
These relationships strongly support two cooperating DSP cores/SHI endpoints,
but physical core numbering and GPIO-to-chip pin wiring remain **UNRESOLVED**.

**VERIFIED:** selection-one channel-zero starts at P:0x17F, configures ESAI/SHI,
and runs test loops at P:0x2D5/0x2E6 that write/compare patterns in X memory,
increment an error count and publish results in Y:0x3..0x8. Its audio ISR is
P:0x1E4 and simpler SHI memory handler is P:0x224. Its receive handler does not
implement all normal-image operations: no normal bit-21 width-control branch,
no normal extended-address branches, and no equivalent auto-increment read-next.

Normal/alternative selection conditions and command correlation are recorded in
`notes/dsp-command-map.md`. Selection one is a verified diagnostic-capable
program; its complete user-facing mode name and activation workflow are
**UNRESOLVED**.

## References and reproduction

- [NXP DSP56724RM](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf): Tables 5-5, 5-9, 10-1, 10-4; SHI and memory maps.
- [NXP APR30](https://www.nxp.com/docs/en/application-note/APR30.pdf): Example 3-14, independently published opcode examples.
- `tools/PHASE3.md`: source audit, build and offline reproduction commands.
- `builds/phase3-verification.json`: integrity checks and reviewed ISR targets.
