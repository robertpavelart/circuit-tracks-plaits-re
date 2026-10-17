> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20F — pinned VA_VARIANT=2 at MIDI vpre: admission failure

2026-10-15. **ONE COMPLETE PLAITS ENGINE: UNQUALIFIED. Placement/regression admission: FAIL.** No complete DSP VA+Voice implementation was built or claimed. The required reduced layout deletes code used by the unchanged MIDI2 regression track. I corrected the prior recommendation instead of retaining its invalid budget or weakening MIDI2 tests.

**PROVEN:** original B1.3 core0 occupies `0000,3FED)`, 16,365 P words, leaving19 below4000. The Phase20E 1,196-word budget =19 existing tail +1,177 words removed from a shared two-track renderer/control module. This is a conditional budget for replacing BOTH original MIDI engines. It is not1,196 words available beside an unchanged MIDI2 engine.

The deleted code is shared, not two separately duplicated engines:

| Original P range | Words | Needed by unchanged MIDI2 |
|---|---:|---|
| `[36AD,3876)` | 457 | Pitch, shape, morph and dual control |
| `[3999,3B82)` | 489 | Single/dual oscillators, interactions and VA noise |
| `[3D9E,3E1F)` | 129 | TINC pitch table |
| Scattered VA-drum control changes | 102 net | Original VA envelope/filter/noise behavior |
| Total restoration charge | **1,177** | Restoring the original shared module leaves **19** words |

[vcf21_dsp.py — def code (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21_dsp.py:151`; not distributed); vcf21_dsp.py — L("vp_loop") (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21_dsp.py:742`; not distributed); vcf21_dsp.py — control("vc_") (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21_dsp.py:750`; not distributed); vcf21_dsp.py — def channel (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21_dsp.py:455`; not distributed); reclaim.py (local-only reference: `plaits/poc/full_audit/reclaim.py:1`; not distributed). **UNKNOWN:** whether an additional semantics-preserving refactor could reclaim space while retaining MIDI2; the current deletion does not do that. Even retaining only legacy oscillator control/render/TINC would charge1,075 words and leave121, while dropping VA control would change MIDI2's engine capabilities. The existing sealed VariableSaw primitive alone is523P in the previous short-target fixture, exceeding either19 or121 before the other three oscillators/LPG/glue. This is a size comparison for existing code, not a mathematical lower bound on every future implementation.

## Actual DSP admission test

**PROVEN:** executed4,096 consecutive32-sample blocks for three machines: original B1.3; the actual source-reduced shared module; and restored original code. MIDI1 was disabled to isolate MIDI2. Identical MIDI2 mailbox words exercised notes/gates/retrigger, oscillator shape/PW, single/dual and VA modes, with reference-style latest-value coalescing/2ms scheduling. All active DSP bytes came from original B1.3 or the byte-verified source assembler. No host callback rendered or replaced audio.

- Reduced layout: MIDI2 state mismatch **4096 /4096**, output mismatch **4096 /4096**. First mismatch block0, sample0. These failures are preserved in `blocks.csv`; they are the reason admission fails.
- Original MIDI2 executed **841,060** instructions in the deleted control island and **16,826,657** in the deleted renderer island. Those are issued instructions, not cycles or P sizes.
- Restored original code: all4,096 MIDI2 state/output blocks exact to the original; mixed output exact as well. State comparison covers240 cells across VB, OSC1, OSC2, second-filter-stage and FX records. It is an offline fixture regression, not full-device verification.
- Caller register/modifier/LA/LC/OMR/SP/SC checks and fixture ring/mixer/stem/gain canaries pass after every vpre/mixer call. X/Y writes traced; P runtime writes rejected. No private Plaits DSP allocations exist, so these checks cannot qualify a future engine workspace or its ABI.
- The stock strip mixer executed identical instruction paths; independently checked **786,432** output samples against its accumulator arithmetic. Different reduced-layout audio produces different mixed samples; that is expected and does not excuse MIDI2 regression.

Evidence: verification.json (local-only reference: `builds/phase20f-va-vpre-admission/verification.json:1`; not distributed), blocks.csv (local-only reference: `builds/phase20f-va-vpre-admission/run-v1/blocks.csv:1`; not distributed), native.json (local-only reference: `builds/phase20f-va-vpre-admission/run-v1/native.json:1`; not distributed), per-machine `access.csv`, `pc.u16`, `executed.asm`; harness admission.cpp (local-only reference: `plaits/poc/va_vpre/admission.cpp:1`; not distributed) and admission.py (local-only reference: `plaits/poc/va_vpre/admission.py:1`; not distributed).

The reduced fixture keeps the sampler tail at its original P addresses, puts zeros only in the deleted module's gap, repairs the external P:D22 vret operand, and uses only a3-word call/stop stub atP:3FF0,3FF3) inside the old19-word tail. There are **no P:0400/P:0800 stock-synth overlays**. All other stock words below2A5E are equal apart from that explicit vret operand; all sampler-tail words are equal. Full ARM relinking/boot/core1/concurrent operation is UNKNOWN. Raw `.be24` fixtures are DSP-only programs, not application BIN/SYX firmware containers.

## Exact selected original behavior

**PROVEN source structure:** MODEL=8, `VirtualAnalogEngine`, active `VA_VARIANT=2`. [virtual_analog_engine.h — VA_VARIANT (local-only reference: `plaits/upstream/plaits/dsp/engine/virtual_analog_engine.h:36`; not distributed); virtual_analog_engine.cc — void VirtualAnalogEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/virtual_analog_engine.cc:78`; not distributed).

- Engine pitch: `NoteToFrequency` plus HARMONICS detuning intervals; cycles/sample normalized using upstream corrected47,872.34Hz constant. engine.h — inline float NoteToFrequency (local-only reference: `plaits/upstream/plaits/dsp/engine/engine.h:39`; not distributed).
- Engine HARMONICS sets detuning; TIMBRE sets sync amount/square PWM and gain; MORPH sets variable-shape/PW, saw shape/gain. Preserve all clamps/normalization and two gain interpolators.
- AUX: primary and auxiliary monster-sync `VariableShapeOscillator` renders, differenced at0.5 gain. MAIN: synced variable square plus VariableSaw, mixed with interpolated normalized gains. Three distinct VariableShape instances plus one VariableSaw; sealed VariableSaw alone is not this engine.
- `Init` initializes the four oscillators/two gain histories and a24-float temp arena; `Reset` is empty. Model-switch Voice behavior therefore differs from calling Init/reset-all. virtual_analog_engine.cc — void VirtualAnalogEngine::Init (local-only reference: `plaits/upstream/plaits/dsp/engine/virtual_analog_engine.cc:40`; not distributed).
- Trigger/accent are not directly read by this VA engine. Original Voice owns delayed0.3/0.1 trigger hysteresis, internal decay/LPG, note averaging, patched-source choices and nonlinear modulation amount curves/clamps. LEVEL compression sets accent and may drive LPG; unpatched default accent0.8 does not become an automatic VA amplitude multiplier.
- VA metadata: already_enveloped=false, MAIN/AUX gain0.8. Voice may bypass LPG when neither trigger nor level is patched; otherwise it processes both channels with independent LPG filter/gain histories. Positive VA gain does not execute limiter audio processing, though limiter state initialization/reset remains in the original wrapper. Output polarity and16-bit clipping are preserved in the host reference.

voice.cc — void Voice::Init (local-only reference: `plaits/upstream/plaits/dsp/voice.cc:37`; not distributed); voice.cc — void Voice::Render (local-only reference: `plaits/upstream/plaits/dsp/voice.cc:90`; not distributed); voice.h — ApplyModulations (local-only reference: `plaits/upstream/plaits/dsp/voice.h:183`; not distributed); envelope.h — class LPGEnvelope (local-only reference: `plaits/upstream/plaits/dsp/envelope.h:36`; not distributed); low_pass_gate.h — class LowPassGate (local-only reference: `plaits/upstream/plaits/dsp/fx/low_pass_gate.h:40`; not distributed). Module ADC/DAC/calibration/UI/flash mechanisms are excluded. The TEST host UserData accessor supplies null custom data; no save/programming function is called.

## Implemented 12-to-32 scheduler and pinned host oracle

**PROVEN host-only:** two independent original `Voice` instances, fixed MODEL=8. Reference A renders a natural sequence of full12-sample blocks. Adapter B requests32 samples, consumes FIFO remainder and renders complete12-sample blocks only. Over three Circuit blocks the pattern is **3/3/2 renders**, with FIFO remainder **4/8/0**. No12+12+8 truncation, array-cap enlargement, oscillator arithmetic changes or envelope coefficient changes.

Completed4,096 Circuit blocks =131,072 MAIN/AUX sample pairs, **10,923** original render calls, including deferred Init reset, note on/off/retrigger, pitch/HARMONICS/TIMBRE/MORPH/LEVEL sweeps and internal/external modulation, ping/level-driven/bypass LPG modes. Output max absolute/RMS/DC difference between A and B is **0 signed16 units**. **74** named persistent scalar/filter/envelope/trigger-delay fields match bit-for-bit after each internal render; host arena canaries pass. This comparison verifies FIFO scheduling against the same pinned host implementation, **not an independent fixed-point arithmetic oracle or ARM-vs-DSP equality**.

Control/reset selection uses internal-render start sample `s`: Circuit control index `floor(s/32)`. Already-prefetched4/8 samples retain earlier controls; new changes become visible at the next12-sample boundary (0..11 samples later). Trigger delay remains five original control calls,60 samples, followed by the original hysteresis. The adapter does not split or reset oscillator state across FIFO extraction. Final four lookahead samples are retained. Host replay uses identical clocks/staging in A and B. None of this proves actual ARM mailbox scheduling or audio-rate CV transport. `controls.tsv` is the host oracle stream; `cases.tsv` is the separate MIDI2 admission stream. No DSP Plaits candidate exists to feed the host stream to.

Fidelity: **BIT-EXACT** for host FIFO output and the named host state fields versus natural pinned-host rendering; **UNKNOWN** for a DSP fixed-point conversion. **STRONG INFERENCE:** the scheduling preserves the original discrete algorithm/control cadence. Playback on the conditional Circuit48,046.875Hz rate without retiming would shift original corrected-rate pitch approximately+6.30 cents and rescale durations. No rate correction was silently inserted. A faithful Circuit port must explicitly qualify sample-rate/parameter semantics; same sample sequence alone is not identical physical-time pitch.

Host source oracle.cpp (local-only reference: `plaits/poc/va_vpre/oracle.cpp:1`; not distributed); result verification.json (local-only reference: `builds/phase20f-va-vpre-admission/oracle-v1/verification.json:1`; not distributed); blocks/raw pairs in `oracle-v1/`. Build uses pinned engine object files from Phase20E plus actual `voice.cc`, MSVC strict float and the already documented host-only compatibility overlay. Private-member exposure is instrumentation only. No other engine is rendered or ported.

## Memory and nominal timing

New shared DSP engine code **0P**, immutable DSP tables **0P**: not implemented after admission failure. Restoring unchanged legacy MIDI2 charges1,177 of the purported1,196 free words, leaving **19P** before any new engine/glue. The admission caller stub temporarily uses3 of those19; that is test infrastructure, not production engine cost.

Persistent/temporary X, Y and external/shared Plaits allocations: **not allocated, costs UNKNOWN**. Logical upstream active-state census:39 VA oscillator/gain cells plus35 tracked Voice/LPG/filter/trigger metadata =74 tracked scalar fields, before Patch/Modulations/control staging, buffers and caller saves. This is source/host accounting, not a fixed-point layout. Original temp24 floats, MAIN/AUX24 each; FIFO adapter holds up to40 frames transiently before extracting32, with up to8 frames left at completed blocks. The host full Voice also embeds inactive engine objects/16KiB arena because it is the actual pinned wrapper. Those inactive objects are not a proposed fixed-engine DSP allocation. No claim of X/Y address ownership or canary-qualified DSP workspace is made.

Nominal DSP comparison below is **original versus stripped legacy path**, including vpre + original strip mixer + equal caller-stub overhead. It is not complete Plaits timing. calcCycles excludes interlocks/IRQ/DMA/external waits; issued counts remain separate.

| Fixture path | Instructions/block min / mean / max | Nominal cycles/block min / mean / max |
|---|---|---|
| Original B1.3 MIDI2 | 3950 / 5386.5754 / 7783 | 6025 / 8271.0557 / 12046 |
| Reduced module, MIDI2 broken | 1032 / 1047.0444 / 1091 | 1736 / 1767.5886 / 1871 |

Worst original observed total at block549; worst reduced at block524. Renderer-only, wrapper-only and complete Plaits worst cycles **UNKNOWN**. Host execution time is not substituted. Reduced-path savings measure removal of MIDI2 synthesis and are not available while MIDI2 must remain unchanged.

## P1–P9 gates

| Gate | Result | Confidence/scope |
|---|---|---|
| P1 complete engine fits real budget | **Admission FAIL; engine fit UNKNOWN** | PROVEN1,196 assumption removes MIDI2; restored original leaves19, not a valid1196 budget beside MIDI2 |
| P2 bounded private persistent state | UNKNOWN | No DSP engine allocation admitted |
| P3 original32-sample adaptation | PASS host scheduler; DSP UNKNOWN | PROVEN full12 renders/FIFO preserve131072 output pairs and named state; rate semantics remain explicit |
| P4 quantified DSP numerical error | UNKNOWN | Host-FIFO error0; no DSP-vs-pinned candidate comparison |
| P5 vpre ABI | PASS admission fixture; Plaits UNKNOWN | Registers/modifiers/stack checked4096 times per machine; no Plaits adapter tested |
| P6 MIDI2 unchanged | **FAIL reduced layout; PASS restored** | PROVEN4096 mismatches versus4096 exact restored blocks |
| P7 stock mixing | PASS fixture arithmetic/path; complete integration UNKNOWN | PROVEN independent mixer oracle and restored output; silent synthetic stock synth stems |
| P8 worst complete modeled cycles | UNKNOWN | Only legacy original/reduced counts above were measured |
| P9 second shared-code instance plausible | UNKNOWN | No completed, placed/timed first engine; do not infer from VariableSaw alone |

Exact blockers: the contradictory deletion/MIDI2 requirement; then missing complete VariableShape/VA and Voice/LPG fixed-point port, qualified private state/save/output/FIFO layout, DSP arithmetic oracle/error acceptance bounds, full integration/register/stock-feature regression and target timing. No additional engine or second instance was attempted. This admission rejection is not proof that future code refactoring/placement cannot succeed.

**Next necessary technical step:** prove a genuine P allocation that retains the original shared MIDI2 code (or a separately proven exact legacy-preserving refactor). Only then can a complete engine implementation use an admitted budget. No permission was inferred to drop MIDI2, occupy stock-synth P, delete unrelated features or increase the budget.

Verified unchanged: **825 reference files**, **183 pinned source files**. No hardware, firmware container, flash-ready artifact or reference-repository edit. Sources and retained output hashes are in `verification.json`/`hashes.json`.
