# Phase 20B2-CHECKPOINT — PARTIAL provenance, REFUSED replay

2026-10-07. A real cached patch now supplies the selector and coefficient-offset
sources for a bounded original bank0/slot0 binding. The original coefficient
addresses and dynamic builder are reconstructed. **No concrete original CPU/
memory checkpoint naturally reaching9D9 was qualified.** The overall provenance
result is **PARTIAL**; replay admission is **REFUSED**, not softened into success.

Reports: [stock-coefficient-provenance.md](stock-coefficient-provenance.md) and
[stock-runtime-state.md](stock-runtime-state.md). Canonical evidence is
`builds/phase20b-checkpoint/final/`; new focused tools are under
`plaits/seam/checkpoint/`, tests in `emulator/tests/test_seam_checkpoint.py`.

No hardware, MIDI/SysEx, flashing/repacking, stock P patch, original/ edit,
arbitrary preset synthesis, Plaits feeding or broad RAM/ROM work. The existing
local decoder was used only for narrow ARM producer evidence; no tools installed.
Existing cached Components code and authored archive bytes were read statically,
never launched. Original ARM/DSP inputs and previous implementations are preserved.

## A–F. Context and provenance recovered

Selected input is **Rudi saw poly**, actual `patches/patch_0.syx` from the existing
Shawn Rudiman archive snapshot. This choice is justified by original bytes and
the strongest available getter/descriptor/bank-sink chain, not a historical mode0
fixture. It is a logical offline bank0/slot0 binding; actual device selection and
a note/lifecycle/history execution context are not supplied by this patch.

| Expected prepared field | Source-backed value | Complete producer chain |
|---|---:|---|
|X5AB|0|content60 ->descriptorID1E ->corrected getter ->27578 X2A8 ->47D/47E|
|X5AC|1|content62 ->descriptorID20 ->corrected getter ->2758E X2A9 ->47F/480|
|X5B1|5|content63 type1 ->2819C tablebyte080281CA ->X2AC ->497/49A|
|X5B2|5|same selector ->tablebyte080281CB ->X2AD ->499/49B|

**VERIFIED source / CALCULATED conditional results:** original reverse-index
initializer35F28 givesFF for IDs1E/20/21, so macro correction is bypassed for
these three fields. This avoids inventing zero modulation offsets. The six-pair
table and cursor arithmetic give intendedY:[F64,F69) for both C9D calls,
under the required no-scale pointer-transfer/linear-AGU environment. No numeric
CPU address observation is claimed. Selected helpers/producers are byte-verified.

These fiveY words are written by originalC2D atC65/C78/C7C/C7D/C7E before use;
they are not immutable table contents and were not filled manually. Numerical
builder inputs still depend on Y8F/Y90/Y91, retained histories, other coefficients,
stock tables and modes. X2AB is explicitly written0 byARM275AC..B0, simplifying
X5B0 to max(0,Y91-020000); Y94 is not required for this chosen flag path.

## B–C. No chosen admitted PC

Chosen executable checkpoint PC: **none**. Candidate387 produces coefficients
naturally and returns380->384->77F, but does not alone close the request/completion
bitmap, lookup/table/worker data, arithmetic/state and inherited frames. Candidate
19DD/19E6 is the completion call setup;9AC requires prior generator lane output;
9D9 requires all seam inputs. None provides deterministic peripheral-free natural
entry with every material value proved. No original32-word block was synthesized.

The analysis moves producer provenance upstream rather than copying many guessed
values into a seam snapshot. Relative caller/loop structure is supported by
original instructions; concrete numeric stack prefix and modes are not recovered.
Full authentic boot remains separate and was not made a mandatory substitute.

## G–J. Runtime/AGU/guard disposition

Y19=81FF andY1A=FFFF are proven initialization constants. Selected nonlinear1
setsM5 fromY19 then restoresY1A; its initialM5 is dead. N1/N3=2,N4=-3,N5=-4
have local producers. R0 reload/Y7=5AB andR4=S+12 relations are documented.
Other entry modifier retention is unresolved. Material SR SM/SA/DM/scaling and
true caller modes remain unknown;RM21 has initialized original provenance and
SC13=0 has conditional candidate-device architectural provenance. WholeSR/OMR
words are not taken from reset or an emulator constructor.

Generator DOs are complete at9D9; inheritedSP/SC/prefix/LA/LC/LF/FV remain
unqualified. The genuine guard value is unknown because no original generator
replay occurred. Static overwrite/prefetch/CCR facts do not imply a numeric guard
or universal policy.

## K–O. Admission, replay and state/cost results

**REFUSED before CPU creation.** Zero original stock instructions and zero new
ARM execution. The scripts perform byte checks, integer source calculations and
affine address enumeration, not emulation of the original preparation routine.
No upstream PC trace, natural32-word generator writes, stock-only post trace,
initial/final state measurement or nested/per-voice cycle result exists.

The trace directories contain explicit refusal records. stock-seam-cycles.csv
uses null for preparation, post region, nested-callee and gain/group costs.
state-mutations.csv distinguishes instruction-supported mutation roles from
unobserved numeric initial/final values. The existing raw Plaits timing result
is neither rerun nor promoted to stock workload timing.

Checkpoint-state categories:

- **A:** immutable ARM/DSP image, original340-byte patch and descriptor/ID/pair tables;
- **B:** none produced by earlier replayed stock code in this phase;
- **C:** conditional, source-backed expected selector/offset words and pointer relations;
- **D:** initialYF64..F68 may be irrelevant if originalC2D overwrites before C9D;
  initialR0 at9D9 is overwritten by the Y7 reload;
- **E:** modulation/control/history, material modes, remaining AGU/stack/loop,
  worker/generator numerical inputs and guard history.

Category-E items affect arithmetic results and addresses, so they cannot be
backed by arbitrary numbers or marked irrelevant. The stopping rule is applied
at the exact unresolved builder/state frontier, after substantial provenance work.

## P–S. Blockers, resumption and next step

The remaining scalar producer frontier is **P657's modulation/input record**:
685..690 writes weighted per-voice results;6D9 producesY8F,6DE Y90,6ED Y91.
Those feed47F..498. The required nonlinear/control/coefficient histories
Y5AB..5AE/5B7/5B8 are not cleared by the selected trigger loops; a preset file
does not contain their prior values. A chosen note/lifecycle/source-history
sequence and bounded CPU/frame context are still needed. No code-data constant
can substitute for these numerical states.

Plaits-fed replay now justified: **NO**. Phase20B numeric replay can resume:
**NO until the stock-only checkpoint qualifies**. Static provenance may continue
from this reduced frontier. Firmware patching, hardware, memory-safety claims
and model/polyphony work remain closed independently.

**Single best next step:** qualify the originalP657 modulation/control input
record for this exact source patch and one provenance-backed note/slot history,
including the retained post state and material CPU/frame context. This is more
specific than repeating the generic selector/offset investigation. If no such
history/context is present offline, report that missing evidence rather than
selecting neutral values. No new broad alias or ROM hunt is proposed.

## Deliverables and reproduction

All requested files exist underfinal/:selected-context.json, coefficient- /
selector- /address-offset-provenance.csv, agu-state.json, arithmetic-mode-state.json,
stack-loop-state.json, checkpoint-state.json, checkpoint-admission.json,
upstream-trace/, stock-seam-trace/, stock-seam-cycles.csv,state-mutations.csv,
guard-selected-context.json,validation.json. Additional source snippets, exact
reverse-index/sequence evidence and immutable patch copies retain provenance.

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B plaits/seam/checkpoint/recover.py --output-dir builds/phase20b-checkpoint/reproduce-new
& $taskPython -B emulator/tests/test_seam_checkpoint.py
& $taskPython -B plaits/seam/checkpoint/verify.py --suite-dir builds/phase20b-checkpoint/final --repeat-dir builds/phase20b-checkpoint/repeat --output-dir builds/phase20b-checkpoint/checks-new
```

Use fresh child directories. Existing disassembly is checked against original
bytes; recovery needs no application launch, decoder install or emulator build.
Nine tests check source values, correct reverse-index literal, coefficient AGU
domains, unknown-history/stack refusal, null cycles and no Plaits admission.
Repeat exports are byte-identical; source/payload/baseline guards and overwrite
refusal pass. These are static/refusal tests, not replay qualification.

## Phase20B3 update — no checkpoint admitted

Original657's37 control words and count-led five-word rows are reconstructed
in stock-p657-input-record.md. The selected rows target7C/91; count20 requires
35F..362 lookahead, and68F still reads the next source1. Active count, sentinel
retention and material modes cannot be guessed. Candidate33F,37A,657,387,C2D,
9D9 all remain refused. Same-name project0 differs from the selected patch in7
bytes; no exact event/lifecycle timeline admitted. Expected0/1/5/5 fields stay
conditional. Numerical preparation and seam execution remain0 instructions.
Canonical matrix:builds/phase20b-inputrec/final-v3/seam-admission-matrix.csv.

## Phase20B4 — cached event remains inadmissible

Project0 first embedded patch is source-bound tologicalbank0; its six changed
macro values reach original correction arithmetic. Stored-value recompute yields
differentX2E8,X2EA,X3E7 targets despite identical selectors/offsets. Event-time
automation convergence and complete event/slot chain are not proven. No exact
project event, history origin or checkpoint admitted. P657 structure preserved;
no stock preparation/seam or Plaits execution. See project0-event-context.md and
builds/phase20b-projectassoc/final-v2/qualification.json.
# Phase20B5 continuation — current checkpoint disposition (2026-10-07)

**PARTIAL provenance; replay REFUSED. STATIC CHECKPOINT RECONSTRUCTION EXHAUSTED.**
The final bounded project0 consumer attempt recovered serialized note/automation
geometry and storage/notification edges, but not a full audible playback order,
allocated slot, active patch state or material histories/modes. All numerical
checkpoint candidates remain inadmissible. P657/seven-byte analyses are reused;
0 original preparation/seam instructions and no Plaits input.
Earlier static continuation suggestions below are historical and superseded.
Current single next step: separately authorized coherent originalP9D9 snapshot
decision; exact/conservative ranges and omissions in static-checkpoint-limit.md
and builds/phase20b-sequence/final/runtime-snapshot-minimum.json. No snapshot
acquired. The clean boundary retains originalR0 restore/NOPs and captures
original32-word mono block+guard, actual slot post records/history and group
accumulator input. This is not an admitted or universally minimized checkpoint.
