> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20D — one MIDI-track VariableSaw at reference vpre

2026-10-15. **Offline DSP experiment PASS within its declared fixture. Complete ARM/device integration UNKNOWN.**

One VariableSaw engine replaces MIDI1's oscillator in the CIRCUITS-HACKS B1.3 DSP `vpre` architecture. MIDI2 stays the reference oscillator and is the regression control. No hardware, firmware upload, flash-ready image, reference-repository changes, or second VariableSaw voice. Existing sealed renderer, integer oracle, interpreter library, and original firmware inputs remain unchanged.

Confidence terminology: **PROVEN** means reproduced bytes/execution/assertions in this offline fixture. **STRONG INFERENCE** means source-derived behavior or a plausible architectural interpretation. **UNKNOWN** means outside the exercised evidence.

## Canonical evidence and reproduction

- `builds/phase20d-midi-vpre/final-v1/verification.json`: final 4096-block result.
- `final-v1/blocks.csv`, `states.csv`, `raw.i32`, `rings.i32`, `mixed.i32`: every block, every sample, and every seven-word state transition.
- `final-v1/baseline/` and `replacement/`: complete instruction-PC traces, executed disassembly, and every X/Y write; reads of new objects are also recorded.
- `final-v1/context-invariance.json`: sample/state/input-strip/mixed output equality against the earlier constant-caller-context run.
- `final-v1/provenance.json` and `hashes.json`: executable/source/input identity and retained evidence hashes.
- `protocol-v1/protocol-verification.json`: real DSP mailbox decoder tests, including tag cancellation, repeated tag, disable/re-enable, and rapid trigger updates.
- `stimuli/mailbox.json`: source-derived coalescing/rate-limit model and the complete delivered message schedule.
- Harness source: `plaits/poc/midi_vpre/{prepare.py,runner.cpp,experiment.py,build.ps1,CMakeLists.txt}`.

Paths above are relative to `C:/Proj SSD/CODEX/CIRCUIT`. The read-only reference is `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main`.

Re-run against the retained DSP-only fixture using a **fresh** output directory:

```powershell
& ./builds/phase20d-midi-vpre/core/midi_vpre.exe builds/phase20d-midi-vpre/fixture builds/phase20d-midi-vpre/reproduce-new builds/phase20d-midi-vpre/stimuli/cases.tsv
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B plaits/poc/midi_vpre/experiment.py verify builds/phase20d-midi-vpre/reproduce-new
```

`prepare.py` reconstructs B1.3 in memory from the reference uploader COPY/ADD plan and our original BIN. It verifies the manifest image SHA-256 before exporting only the DSP program bytes. It does not save an application BIN/SYX. `patch_official.py`, the reference builders, and its uploaders are never run. All eight protected source/library/firmware inputs match their preparation hashes after execution.

## What actually executes

**PROVEN:** the reference core-0 bytes execute its actual `vpre` at P:$336E, mailbox decoder, voice-control arithmetic, normal track loop, VCA/FX/filter chain under the declared neutral settings, and original stock input-strip mixer P:$23E..$24E.

The oscillator hook is P:$3999 (`vc2_ngr`). At this point the reference already established ACT=2, ring mode, oscillator block R3, and the input-ring pointer. A DSP trampoline saves its context and selects only R6=$3B80 (MIDI1). For MIDI2 it restores context, executes the original four displaced words (two complete instructions), and resumes at $399D. MIDI1 renders into a dedicated Y block, copies 32 samples into the even samples of the input ring, restores context, and resumes at `vc2_nosc` P:$3B82. The ordinary chain and strip mixing then execute. The shared selector adds overhead to MIDI2's route but does not change its original oscillator arithmetic, output, parameters, or history.

**PROVEN:** oscillator reuse changes only absolute state/control/spill addresses, the R0 output-base immediate, and the top-level `JMP done` to `RTS`. Arithmetic, interpolation, correction order, native DIV helper, and event order are unchanged. The input is the already qualified `source-v7/high-x/variablesaw.asm`; the independent oracle is the unchanged `plaits/poc/fixed_model.py`.

Converter contract in this experiment:

- Frequency: the reference OSC1 increment X:$390B shifted right two, Q2.22. The renderer retains its own frequency cap.
- PWM: mailbox code 25 -> X:$3903, then `value/128` in Q2.22.
- Shape: mailbox code 24 -> X:$3902, then `value/128` in Q2.21.
- Reference note mailbox code 18 supplies NOTE and drives its original pitch-control calculation. These parameter meanings are an explicit experimental mapping; the shape mapping is not a claim that VariableSaw and the reference waveform family have the same sound.
- GATE/TRIG operate the reference envelope. VariableSaw phase remains continuous across note-off/retrigger while ACT=2, following the reference free-running source architecture. ACT=0 freezes all seven words. Re-enable resumes them without a second initialization.

**UNKNOWN — ARM execution:** the ARM note/sender path is not executed. The reference checkout lacks the flash/RAM dumps required by `emu_sc05.py`, and no local Unicorn installation was found. Stimuli implement a documented subset of the reference `c_vsend` contract (priority, latest-value coalescing, 2 ms rate limit, one-bit tags) and deliver its words to the actual DSP decoder. They do not reproduce the complete ARM service scheduler, its 5-bit time bookkeeping, UI, note allocator, or concurrent transport. No synthetic ARM memory was misrepresented as a recorded device state.

## Address and ownership ledger

All ranges are half-open. **PROVEN** usability here means the strict fixture exercised them; it is not stock/device ownership.

| Space/range | Purpose and basis | Evidence boundary |
|---|---|---|
| X:[3E00,3E07) | Seven retained words: phase, next, previous_pw, high, frequency, pw, shape | Explicit CPU initialization; exact oracle state after every block. Within the reference's proposed high-X tail, not a complete lifetime certificate. |
| X:[3E20,3E60) | Dedicated 64-word workspace record | Does not borrow the reference register save area, voice records, weights, or live audio buffers. |
| X:[3E20,3E45) | 37 raw register/control saves | SR; A0/A1/A2; B0/B1/B2; X0/X1/Y0/Y1; R0..7; N0..7; M0..7; LA/LC. SR saved first and restored last. |
| X:[3E50,3E53) | Three normalized control words | Converter writes; renderer may clamp its own controls. |
| X:[3E58,3E5B) | Three sealed-renderer spills | No unrelated stock scratch borrowing. |
| X:3DFF,3E07 | Retained-state canaries | $5A1234; checked after every vpre and strip-mix block. |
| X:3E1F,3E60 | Workspace canaries | $5A1234; same checks. |
| Y:[3E00,3E20) | Dedicated raw 32-sample output | Private Harvard-space fixture allocation. Physical capacity/absence of stock users is UNKNOWN. |
| Y:3DFF,3E20 | Output canaries | $6B2345; checked after every block. |
| Y:[1000,1040) | Reference input ring, 32 interleaved frames | Y:$FFD points here; MIDI1 even, MIDI2 odd. Explicit caller fixture, not a recovered live pointer. |
| Y:[1100,1180) | Two explicitly silent stock-synth stems | Synthetic fixture inputs to the original four-strip mixer. |
| X:[0200,0300) | Four stereo strip-gain arrays | Constant $100000 for both outputs of each stem; initialized identically in both runs. |
| Y:[0800,0840) | Original stock strip-mixer stereo output | Exact independently calculated output for every frame. |
| X:[3400,3C00) | Existing reference controls/history/save records | B1.3's own objects, not newly claimed allocations. |
| X:3703E,3706E | Existing reference granular new-note counters | `vpre` writes these even with the oscillator engine selected. Explicitly admitted existing objects; no core-1 execution. |
| P:[0400,060B) | 523-word renderer | Synthetic overlay of retired stock-synth code in this isolated fixture; **not deployable/free stock P**. Short control targets account for the size difference from the 549-word high-P template. |
| P:[0800,092D) | 301-word adapter/init/call stubs | Same synthetic-overlay limitation. |
| P:3999..399A | Two-word trampoline hook | In-memory DSP fixture only; original four-word replay on the nonselected track. |

The input P program remains the B1.3 core-0 program outside these explicit overlays. Its physical load/count and memory mode are not requalified. Its full build has only 19 free P words; this fixture does not solve deployable code placement.

**PROVEN:** the final execution has zero reads/writes outside its declared X/Y data domains. All P writes are rejected. Every X/Y write is retained with block, phase, PC, address and value. Opcode-PC traces cover all execution; P tables are read from the verified reference image. New-object reads are retained individually; other admitted reference reads are counted. Shared counters discovered during bring-up were added as explicit existing reference objects, not silently classified as private state.

**UNKNOWN:** global indirect writers, SHI/service interference, interrupts/DMA, core-1 concurrency, real memory mode/backing, reset/reload/project lifetime and real-device cache/wait behavior. No naturally free-memory or complete mediation certificate follows.

## Numerical, lifetime and regression results

**PROVEN:** 4096 sequential 32-sample blocks: **4039 consecutive VariableSaw renders (129248 samples)** followed by 57 ACT-disabled idle blocks. Every raw sample and every seven-field transition equals the independent integer oracle; maximum difference **0**. Disabled blocks retain all seven words. Initialization writes all seven explicit values once, replacing poison: `[0,0,0x200000,0,41943,0x200000,0]`.

The workload covers note-on/off, multiple pitches through note 127, continuous render, PWM/shape updates and endpoints, 10244 phase wraps, 10244 PW-crossing events, rapid retrigger, mailbox bursts/coalescing, gate-idle render and ACT-disabled idle. No model switching or extra VariableSaw voices.

**PROVEN:** every block retains all new-object canaries. All 4039 selected adapter returns match their 37 saved register fields. The reference vpre's caller-preserved register/modifier/control set is checked after all 4096 vpre calls; A/B/CCR and the documented R5 return are treated according to the reference caller contract rather than invented all-register invariance.

Caller R/N/LA/LC values vary by block; M alternates the two linear encodings $00FFFF and $FFFFFF. Raw samples, retained states, both input-ring streams and stock mixed output are byte-identical to the earlier constant-caller-context run. Nonlinear M, scaling/rounding modes and IRQ frames are not qualified.

**PROVEN:** MIDI2's input-strip output and primary records match baseline after every block. A broader projection of **389133 writes** to its OSC1/OSC2, VCF/VCA, FX, second filter stage, comb/chorus and shared counter is identical between baseline/replacement: SHA-256 `d3c0510ba36d73cd7e55b58d0b7d4e0b3d2e8976d21e5d769624da578e5fb52f`.

**PROVEN:** the original stock mixer produces exactly `-(MIDI1 + MIDI2)/2`, narrowed at the original accumulator precision, under the fixture's two silent synth stems and $100000 gains. All stereo samples agree with that independent calculation. Later drum/master/FX/DMA work is outside this experiment.

## Mailbox results

**PROVEN:** the additional 14-block real-DSP decoder suite accepts PWM writes only at blocks 1/3/5 with values 100/127/0. It ignores an initial equal tag, a repeated tag, and two writes whose final tag cancels the transition. ACT disable/re-enable and rapid triggers preserve exact VariableSaw/oracle continuity. The experiment does not pretend that a mailbox is a lossless note-event queue.

**STRONG INFERENCE:** the source-derived sender model coalesces 1489 superseded values and emits 1114 messages, never less than 2 ms apart. Its latest-value and suppression tests pass. **UNKNOWN:** whether the actual ARM instruction path and task timing exhibit the same schedule. The actual DSP receiving behavior is independently exercised, but sender-model assertions are not ARM execution evidence.

## Timing

The full measured DSP scope is **vpre + original P:$23E..$24E strip mixing**, with both baseline reference MIDI tracks enabled and only MIDI1 replaced. Instructions are the interpreter's issued-instruction counter, independently reconciled with complete PC traces (30161230 baseline and 41838666 replacement instructions, plus 16 initialization instructions each).

Cycles below are **nominal modeled DSP cycles from the unchanged interpreter `calcCycles`/Table-A model**, not physical measurements or a WCET. The model explicitly excludes previous-instruction interlocks, physical IRQ/DMA contention, calibrated external/shared waits and hardware pipeline fill. It is not interchangeable with our 13379 bound, which has additional timing assumptions/interlocks.

| Per 32-sample block | Mean instructions | Maximum instructions | Mean modeled cycles | Maximum modeled cycles |
|---|---:|---:|---:|---:|
| Baseline reference vpre + mixer | 7363.58 | 7458 | 11343.20 | 11560 |
| One VariableSaw replacement + mixer | 10214.52 | 13040 | 17022.52 | 21235 |
| Matched delta | +2850.94 | +5584 | **+5679.31** | **+9707** |

For rendered blocks only, cycle delta min/mean/max is **3521 / 5756.12 / 9707**. ACT-disabled blocks pay the other-track selector overhead: +79 instructions / +237 nominal cycles.

Worst delta is block **685**: baseline 7402 instructions / 11396 cycles; replacement 12986 / 21103; delta **5584 instructions / 9707 cycles**. It has eight wraps and eight PW crossings, f=$100000, PW=$200000, shape=0. The maximum replacement total is reported independently in `blocks.csv`; it need not coincide with maximum matched delta.

**UNKNOWN:** a complete physical deadline margin, ARM service cost, all-state WCET, and a matched integration estimate using our full conservative timing model. No frequency/clock budget or feasibility percentage is invented.

## Gates

| Gate | Result | Confidence and scope |
|---|---|---|
| G1: exact output for 2048+ blocks? | **PASS** | PROVEN for 4039 consecutive DSP renders and the oracle; authentic ARM delivery UNKNOWN. |
| G2: seven-word private-X state stable? | **PASS in fixture** | PROVEN values/continuity/idle lifetime; real stock ownership UNKNOWN. |
| G3: dedicated temporary/save workspace stable? | **PASS in fixture** | PROVEN bounds/canaries and use; asynchronous preservation UNKNOWN. |
| G4: required caller registers/modifiers preserved? | **PASS in fixture** | PROVEN 37-field adapter restoration and declared vpre caller preservation, under tested numeric/linear-M profile. |
| G5: other MIDI track unaffected? | **PASS for audio/state** | PROVEN output, records and 389133-write projection; shared dispatch overhead is explicitly counted. |
| G6: full integration cycle delta? | **MEASURED, conditional** | +5679.31 mean / +9707 worst nominal DSP cycles for vpre+mixer; full ARM/device timing UNKNOWN. |
| G7: evidence invalidating this architecture? | **No numerical/ABI invalidation found** | PROVEN fixture success supports a one-voice experiment. Insufficient deployed P placement, unexecuted ARM path and unqualified concurrent ownership remain open; they prevent a deployment claim. |

No two-track VariableSaw or additional-voice work follows these results.
