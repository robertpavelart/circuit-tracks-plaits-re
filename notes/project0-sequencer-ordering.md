# Phase20B5 — project0 group0/pattern0 ordering

2026-10-07. Overall **PARTIAL**. **STATIC STRATEGY: EXHAUSTED**.
Offline static evidence only; original CPU execution remains0 instructions.
No Components launch, download, hardware, MIDI/SysEx, patch, repack or Plaits.
Canonical exports: `builds/phase20b-sequence/final/`; byte-identical `repeat/`;
nine passing static tests and source/report guards in `checks-v2/verification.json`.
Reproduction: `plaits/seam/sequence/README.md`. Existing prior reports retained.

## A. Serialized structure

**VERIFIED:** originalAF46 selects literal group0 at projectbase+2E4
(file740). Eight patterns useCA8/3240-byte stride;32 step slots use1C/28-byte
stride. Step region:[0,380); header/gap:[380,3A8);12 automation lanes eachC0
bytes,32 records of6 bytes, fill[3A8,CA8). All numbers in address formulas
are hexadecimal. Full raw32-step/12-lane export:pattern0-structure.json.

**VERIFIED:**3DC34..56 loads header halfword+380 and bytes+382/+383 into
property fields0/1/2. Cached bytes are0F00,00,03. **HYPOTHESIS:**0F may be
last-step index, implying16. Exact playback length remains **UNRESOLVED**;
no assumed16-step chronology is used.

**VERIFIED:**3F350..384 iterates six occupancy bits in step byte0, compares
record+4+4*i key and+6+4*i substep.3F88A..89C writes key, duration,
substep, level to the four-byte record. Duration writer3F856..886 computes
6*q+floor(6*r/rate), caps long duration at96 and substitutes1 for zero.
Substep is the packed source's high three bits; level is bits11..17.
This establishes storage semantics, not physical event pitch/velocity/gate.
Step bytes1..3 and probability/condition semantics remain **UNRESOLVED**.

## B–C. Original consumers and literal association

|Original ARM address|VERIFIED role|
|---|---|
|1FD34/1FD84|AF46 literal0 group source; construct2E2D8|
|2E35C/3F1F0|construct first child; parent+0C stores it|
|3F260|child+48 retains source group pointer|
|2D7C4/3CF58/3DC16|separate editing/view object and header binding|
|3F298/3F7BE|note recording/state and serialized-record updates|
|1D02A|lane pointer =child+48+CA8*pattern+C0*lane+3A8|
|3FC20|stage lane value and signal bitmap, bounded by count12|
|3FD32|derive tuple using current/previous tuples, rate and boundary state|
|3FE24|property notification; state-gated recording/pending processing|
|400A4|interpolation writes using retained previous value/mode|
|40188|current automation record write and retained interpolation state|
|3F8D4|publish same note-property pointer after state/record changes|

Addresses above have image prefix0x080 except flash vtables. Vtable805A5B4
contains3FC5E,3FCF4,3F61C,3F298,3F5B0,3F62A,3F67C,1D02A,2520A,3FE24.
2520A is a BX LR stub. Later code in its exploratory listing is unrelated
file/patch code. No interpretation of that later code as a clock consumer.
The constructor's final stack argument is12 automation lanes;139 is the
separate note-key state-table domain, not automation count or DSP voice count.

**PARTIAL:** literal group0/source binding established; bank0 embedded patch
binding is imported from20B4. Complete pattern event → synth/MIDI route →
497CA → allocatedDSP slot is **UNRESOLVED**. Do not name Synth1 from position
alone.2E56A routes into recording methods; it is not proven physical note-on.
The exported consumer graph is a constructor/storage/notification graph,
not a recovered audible-playback scheduler or complete sound dispatch graph.

## D–E. Patch identity and order

**VERIFIED CONDITIONAL**, reused20B4: projectF438 selects full340-byte copy
throughF450/3BBE2 or F454..49C macro/keyboard-only updates according to retained
identity state. A partial update of an active authored patch yields the cached
patch's exact seven differences. Full copy also selects cached data. Native
pack/patch slot, active branch and bank at actual dispatch remain **UNRESOLVED**.
The logical bank0 load binding alone is not runtime active-bank evidence.

**VERIFIED local order:** the same3FE24 pending branch calls400A4 at3FF0E
before40188 at3FF1A.400A4 uses previous value and+40..43 state to write
half-weight or one-third/two-third values orFF;40188 writes current value
at6*step+converted-substep and retains prior state for the next update.
These are recording/interpolation writes; they do not establish playback's
interpolation policy or prove automation precedes the audible note.

**UNRESOLVED chronological order:** patch activation, stored macro recompute,
automation application, parameter callback, note-on, allocator and DSP publication.
Editing callbacks are not a chronological playback witness. Missing runtime
tuple sources, bitmap/pending values, enable, boundary, config, phase and previous
state materially affect branches. File layout cannot supply these values.

## F–I. First event, automation and equivalence

**VERIFIED serialized candidates:** first occupied step0 has mask03 and
two records `[51,18,0,106]`, `[82,2,0,106]`. They have identical encoded
substep0. They are not admitted as MIDI notes/velocities or uniquely ordered
first audible events. Playhead, traversal, recording history, frontend route,
probability/condition interpretation and physical dispatch remain **UNRESOLVED**.

**MEASURED raw automation:** only lanes2,8,9 contain nonFF bytes:52,53,15
respectively. Lane2's first step is allFF; lane8 starts1,4,7,12,18,22;
lane9 starts127 thenFF. All others are FF throughout. Original400A4 explicitly
handles FF as unavailable interpolation data. Empty lane bytes do not prove
zero or default effective parameters. Flash8059080 pairs map input indexes0..7
to group0 lanes0..7, indexes8/9 toFF; they do not bind all12 lane meanings
to material patch callbacks. Lane identities, previous value, application time,
locks versus continuous playback and pre-note effective values remain **UNRESOLVED**.

**CALCULATED CONDITIONAL**, reused stored-value original conversion results:

|DSP target|Authored|Cached|Stored relation|First-note runtime relation|
|---|---|---|---|---|
|X2E7|0A0000|0A0000|IDENTICAL|UNRESOLVED|
|X2E8|020408|2C58B1|DIFFERENT|UNRESOLVED|
|X2EA|1C0000|0CAAAA|DIFFERENT|UNRESOLVED|
|X2EB|000000|000000|IDENTICAL|UNRESOLVED|
|X3E7 target|19B6AA|2FB6AA|DIFFERENT|UNRESOLVED|

Additional material corrected inputs remain as20B4: oscillator2 level,
envelope1 decay, envelope2 decay/release, chorus level and keyboard source.
All event-time values stay null; no changed oracle, neutral value or assumed
automation convergence. Stored load context **MATERIALLY DIFFERENT**;
first-note runtime **INSUFFICIENT EVIDENCE**.

## J–Q. Closure, stopping rule and next step

Y91 retains upstream envelope/modulation/smoothing dependencies; allocator
occupancy/age/steal history and exactDSP slot are unknown. No numerical
last-writer origin for Y5AB..5AE/5B7/5B8. Trigger clears [5AF,5B7) and
[5BD,5C5); these six are excluded. Project loading and ARM correction-buffer
clears do not initialize them. Boot-clear is a different epoch.

Provenance-qualified event: **NO**. Checkpoint reconstruction/replay resume:
**NO**. **STATIC CHECKPOINT RECONSTRUCTION EXHAUSTED**. This is the final
broad static association attempt; further similar phases would repeat the
same absent scheduler, allocator and numerical history evidence.

Minimum snapshot specification:static-checkpoint-limit.md and
runtime-snapshot-minimum.json. **Single best next step:** separately authorize
one coherent provenance-qualified original post-generation snapshot atP9D9,
including actual slot/patch context and material live-ins. Do not acquire it
in this phase. No stock seam or Plaits execution has been performed.
