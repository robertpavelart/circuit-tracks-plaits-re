> Historical experiment scope, not the current global project stop point. [Current state](../CURRENT_STATUS.md).

# Phase 20B-SEAM — original-code boundary, replay refused

2026-10-07. **VERIFIED:** fresh byte checks establish the mono generation/post
boundary. **TESTED:** preflight refuses the stock checkpoint before CPU creation.
**UNRESOLVED:** successful stock/Plaits-fed post-processing, response, continuity
and retained stock cycles. These were not performed. The request explicitly
requires stopping when unresolved fields affect control flow, address generation,
scaling, modifiers or loop/stack state; this phase obeys that gate.

No hardware, MIDI/SysEx, flashing, modified firmware/repack, original/ edits,
stock payload overwrite, RAM reservation, model switching or polyphony. Original
stock execution was authorized conditionally, but no checkpoint passed admission.
The only new executed tests are host-side numeric fixtures and refusal tests.

## A. Exact selected seam

**VERIFIED:** the cleaner candidate checkpoint is **P:0x9D9**, not forcing entry
at9DD. DO32 at9C6 ends at9D8, whose last `move a,x:(r1)+` completes the32
mono words X:2C46,2C66). Natural fall-through then executes:

| P | Bytes | Instruction / purpose |
|---|---|---|
|9D9| raw instruction bytes omitted |load Y:7 intoR0, restoring the coefficient cursor|
|9DA..9DC| raw instruction bytes omitted |three NOPs before indirect R0 use|
|9DD| raw instruction bytes omitted |load X:(R0)+ intoA: first post selector|
|9DE| raw instruction bytes omitted |compare selector with0|
|9DF| raw instruction bytes omitted |zero selects the simple BDD post path|

9DD is already post-processing dispatch, not still lane synthesis. 9D9 is the
pointer-restoration entry immediately after completed generator output. Including
the original spacing also avoids inventing an AGU hazard/repair policy after a
future pointer restore. No direct decoded branch/call to9D9/9DD was recovered;
the verified predecessor is the original DO completion/fall-through.

Selected slot0 pointers derive from existing producers, not a preset value:
Q=57B, three14-word records then six coefficient reads lead to5AB;9B8 saves
it inY7. R4 has advanced toS+12=Y5AB. These equal numeric pointers address
different spaces. Use the full coefficient producer trace47D..4D3, not merely
old prose. The fresh export verifies1066 rows including producers, scheduler,
callees, group processing and modifier setup against unchanged payload bytes.

Modes follow original edges:

- selector0: A19 -> BDD -> A1F -> copy32 from2D2E back to2C46 -> A7F;
- selectors1/2: subtract a second scratch stream via9FD, BDD, then add it via
  A09; copy and gain/group accumulation follow;
- other selector values: A15 skips15 coefficient words and22 Y-state words
  then goes toA7F. This path does **not** demonstrate retained filtering.

Do not rename modes by a UI algorithm or treat other adjacent entry points
A2B/A39/etc as destinations of this selector without their own caller proof.
The narrow accounting boundary is **P:A95**, just after the32 group stores.
Full return is not a peripheral-free extension: even if A95's timing branch is
skipped, AA3 calls1BE8 and1BEB unconditionally reads X:FFFF88. No fake timer0
was supplied. Downstream group/mixer/FX paths are separately scheduled.

## B–D. ABI, representation and guard

See [plaits-stock-abi.md (local-only reference: `docs/research-notes/plaits-stock-abi.md`; not distributed) for precise obligations and
`seam-liveins.json`, `guard-word.json`, `seam-clobbers.json`. Signed24 mono
storage is verified; absolute audio normalization and stable feedback headroom
are not. Q1.23 is not adopted as a calibrated stock buffer/audio ABI.

X2C66 must be readable. In the selected raw scaling path its final prefetch
enters an **executed** multiply atBE7 while the parallel store emits previousA.
The new product does not become a33rd scaled output. MPY can update CCR;
the pinned FM printed13-138 (PDF378) lists S,L,E,U,N,Z,V changed, C unchanged.
Therefore the raw guard is not simply a speculative read with no machine-state
effects. On active normalization, B1A instead preloads the next word at the last
iteration and the next iteration never executes.

Before recursion the firstC9D call writes Y-history-derivedX0 intoX2C66 atC9F.
This overwrites the original guard. A93's final gain-loop prefetch reads this
later history on the selected BDD path; itsY0 is not used for a33rd group output.
On the selector-bypass path there is no such overwrite, and Y0 liveout can retain
the original guard. Exact flags/caller state and every mode are not qualified.

**UNRESOLVED:** universal arbitrary-readable, zero, duplicate-last or preserve
policy. None was selected or tested on stock. A duplicate-last requirement is
not proved. Local data-term deadness is not a full-state/caller independence proof.

## E–I. Adapter and execution results

`plaits/seam/adapter.py` implements a **TESTED isolated numeric primitive**:
32 signedQ3.21 words, explicit power-of-two shift, nearest rounding with ties
away from zero on right shifts, explicit symmetric clipping limit, reported
clipping/headroom, zero persistent arithmetic state. An independent Fraction
oracle checks6016 values over47 shifts/four limits. This is a numeric fixture,
not an operational stock converter. `adapt_stock32` refuses because stock
word-per-unit scale, feedback headroom and guard policy remain unresolved.
No Q3.21->Q1.23 shift2 default or assumed unity amplitude was smuggled in.
DSP adapter P words/cycles/scratch/clobbers are **UNRESOLVED**, not host timing.

**TESTED REFUSAL:** the checkpoint has no guessed preset, addresses, SR/OMR,
modifiers, stack prefix or numerical backing. Exact blockers include:

| Field | Consumer and significance |
|---|---|
|X5AB, X5AC|9DD dispatch; AA8 nonlinear selection|
|X5AD /Y5AB|normalization state and sample-dependent N5 table index|
|X5AE|BDF/BE3/BE7 input scale|
|X5AF/5B0 andY5AE|recursive control/coefficient table generation|
|X5B1, X5B2|C10/C1A -> addF5F ->R5 coefficient-sequence address|
|SR SM/SA/DM/SC/scaling, RM|fractional arithmetic, limiting and MACR; ROM defaults are not a seam snapshot|
|M registers/Y19/Y1A|address modifiers and temporary restore behavior|
|SP/SC/frame prefix/LA/LC/LF/FV|nested calls/hardware loops; cannot manufacture a reset-depth entry|
|guard/status history|CCR effects and later caller liveout closure|

A mode0 branch witness from static Phase5 is **not** a recovered stock preset.
Boot-clear zeros are not numeric values after voice coefficient preparation.
The previous symbolic whole-helper replay cannot furnish this checkpoint:
there, unknown numerical data did not control addresses; here it does atB1C,
C3E..C57 andC10/C1A. Both its scope and its opaque numerical encodings remain
unchanged. No older successful helper replay was promoted to seam success.

Stock baseline replay: **REFUSED**. Plaits-fed stock replay: **REFUSED**.
Parameter response and stock-vs-Plaits output/DC/peak/RMS comparison: **not run**.
2048-block joined continuity: **not run**; standalone continuity remains valid
but cannot stand in for retained stock filter/gain continuity. Trace directories
contain explicit refusal records, no fabricated EXEC/audio traces.0 stock
instructions/0 joined blocks/0 CPU instances. Eleven unit tests pass.

## J–O. Workload and budgets

See plaits-stock-workload.md (local-only reference: `docs/research-notes/plaits-stock-workload.md`; not distributed). No retained per-voice,
group/block, adapter or call-glue cycle measurement is available. LayerA remains
the validated prior renderer; layersB/C are **UNRESOLVED**. Do not turn issued
body counts from Phase5/6 into stock cycles. Known ten-generator upper subtotal
133790 leaves30050 for **all** missing work; no complete ten-voice fit claim.

## P–S. Register, size and control design constraints

The standalone instruction program clobbers workingR/N, A/B andX/Y data regs
and CCR. It does not itself install the wrapper's M/SR/OMR environment; wrapper
initialization must not be misreported as renderer instructions. At9D9 R0 can
be reloaded fromY7; R4 and the stock arithmetic/AGU/stack/loop environment must
survive. Exact caller liveouts, spill words and save/restore cycles are not closed.
The union is an obligation inventory, not a measured universal clobber certificate.

**VERIFIED standalone:**7 persistent X,3 control X,3 scratch X+16 working
registers,32 output Y,0 immutable LUT. Stateless numeric primitive needs0 retained
words; integrated adapter and preservation storage remain unknown. Guard readability
does not grant ownership. No whole stock40-word context is reclaimed.

**VERIFIED code:**442P shared renderer, but its terminalJMP reaches the harness
stop, not a callable RTS contract. Literal X0..2/X20..26/X30..32 andY0..1F
overlap stock globals (includingY7). A direct JSR to unchanged bytes in stock
memory is therefore not a ready architecture. A future remapped standalone module
could append a design-only1-word RTS, plus adapter/preservation/control conversion;
none is assembled, placed or patched here. Exact total addedP remains unknown.

The existing stock allocator/note-follow path is usable as an upstream design
boundary: Y12F current, Y159 target, Y15C seed reach periodic increment preparation.
The phase4 record preserves the ARM note construction and DSP lookup chain.
A future converter still needs stock pitch units ->Hz/rate ->clampedQ2.22
frequency. Copying a table-mask-dependent stock increment to Plaits is unproved.
The allocator need not be replaced conceptually; no converter/knob/MIDI mapping
was implemented. VariableSaw has pitch/PW/shape, no independent HARMONICS control.
PW and shape are MORPH-like/TIMBRE-like design candidates. Stock-side cutoff/
resonance/envelope goals remain conditional on qualifying retained processing.

## T–W. Readiness and next step

All runtime readiness questions are **UNRESOLVED**: localABI satisfaction,
retained processing/response/continuity, complete one/two/four/ten voice compute,
exact integrated preservation and sizes. **Offline firmware-patch design readiness:
NO at present. Hardware flashing: NO.** Preliminary static boundary design is
documented; it is not an implementation-qualified patch design.

Largest blocker: one provenance-backed selected stock coefficient/state/mode/
stack checkpoint, especially address-producing X5B1/5B2 and nonlinear/filter
state. Full authentic boot remains unresolved independently. Neither X5F00..6000
nor any persistent stock allocation is promoted; Phase19 ownership stays frozen.

**Single best next step:** recover a bounded original coefficient-preparation
checkpoint upstream of9D9 for one known offline preset/context; close its mode,
table-sequence, numeric-mode/AGU and stack provenance, then qualify stock-only
post replay before attempting a Plaits-fed block. No new hardware observation,
ROM download, patching or automatic broad search is initiated.

## Deliverables/reproduction

Fresh-output only, existing Python; no tool installation/build required:

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B plaits/seam/audit.py --output-dir builds/phase20b-seam/reproduce-new
& $taskPython -B emulator/tests/test_stock_seam.py
& $taskPython -B plaits/seam/verify.py --suite-dir builds/phase20b-seam/final --repeat-dir builds/phase20b-seam/repeat --output-dir builds/phase20b-seam/checks-new
```

Canonical final/ has all requested named exports, plus seam-map/guard/provenance/
hash reports. Unknown resource/cycle totals use null. stock-baseline-traces/
and plaits-fed-traces/ contain refusal.json explicitly marked unexecuted. repeat/
is byte-identical; checks/ records unit tests, byte verification, immutable
renderer/native/restoring/core/upstream/original guards and overwrite refusal.
