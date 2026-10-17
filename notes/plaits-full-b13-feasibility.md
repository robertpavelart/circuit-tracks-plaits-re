> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20E — full pinned Plaits / B1.3 offline feasibility audit

**Phase20F correction (2026-10-15):** the conditional 1,196-word budget below deletes shared code needed by BOTH MIDI tracks. It cannot host a new engine while retaining the original MIDI2 renderer/control unchanged. A 4,096-block DSP admission test found MIDI2 state and output changed in every block; restoring the original shared code restored exact regression, leaving only the original 19 P words. The earlier proposed one-track implementation within 1,196 words is therefore not admitted. See [Phase20F evidence and gates](<plaits-va-vpre-admission.md>). Other Phase20E source/resource findings retain their stated scope.

2026-10-15. **Verdict: NOT CURRENTLY FEASIBLE as a qualified full two-voice replacement.** This is a readiness verdict, not proof that a future optimized port is impossible. The complete fixed-point engine set has not been emitted or timed, the deployable P budget is very small, and large original histories/resources do not fit the small tested private-X fixture. **UNKNOWN** whether a sufficiently optimized architecture can satisfy every preservation requirement.

Only CIRCUIT audit tools/reports/host-test artifacts were written. No firmware container was generated; the reference repository was consumed read-only. All ranges below are half-open. **PROVEN** = reproduced pinned bytes/source structure or a specifically scoped offline assertion; **STRONG INFERENCE** = source-based design/resource implication; **UNKNOWN** = no implementation, ownership proof or worst-case timing evidence. Portability colours are engineering assessments, not measured feasibility gates.

## Evidence and reproduction

Pinned eurorack `08460a69a7e1f7a81c5a2abcc7189c9a6b7208d4`; stmlib `e3bd7c9cc00e4364166f9905c0509b6ffd0535ec`. **PROVEN:** all 183 source-manifest SHA-256 entries verify. [plaits/upstream/source-manifest.json](<../plaits/upstream/source-manifest.json>). No fetch or version substitution. The source is the 24-model revision, not the earlier 16-model product release.

New evidence: builds/phase20e-full-plaits-audit/source-inventory.json (local-only reference: `builds/phase20e-full-plaits-audit/source-inventory.json`; not distributed) (24 slots, 22 classes, transitive quoted dependencies, private fields, allocation/math/division/RNG/table/array evidence with file and line); builds/phase20e-full-plaits-audit/host-probe.csv (local-only reference: `builds/phase20e-full-plaits-audit/host-probe.csv`; not distributed) (host object and allocator measurements); builds/phase20e-full-plaits-audit/reclaim.json (local-only reference: `builds/phase20e-full-plaits-audit/reclaim.json`; not distributed) (byte-verified B1.3 DSP source reconstruction and assembler-only deletion counts). Existing calibration: builds/phase20d-midi-vpre/final-v1/verification.json (local-only reference: `builds/phase20d-midi-vpre/final-v1/verification.json`; not distributed) and [notes/plaits-midi-vpre-offline.md](<plaits-midi-vpre-offline.md>).

Reproduce with the bundled Python using `-B`: run `plaits/poc/full_audit/inventory.py`, `reclaim.py`, then PowerShell `build.ps1` and `host-direct/plaits_probe.exe`; redirect probe stdout to `host-probe.csv`, then run `report.py`. Host compilation uses the pinned code with three documented compatibility adaptations in a separate build overlay: omit GCC always_inline attributes; remove the four out-of-class template-specialization declarations rejected by MSVC while retaining definitions; give an unused empty pointer table a null element. `_USE_MATH_DEFINES` supplies M_PI. No oscillator arithmetic or pinned file is changed. CMake/Ninja compiler-ABI detection stalled and was cancelled; the successful build uses direct MSVC `/O2 /fp:strict /MD`. Host executables and compiler ABI artifacts are Windows programs, not device firmware.

**PROVEN:** each model slot was initialized/reset and host-rendered for 2,048 consecutive 24-sample blocks (49,152 MAIN/AUX sample pairs per slot). This measures allocator/layout and exercises dependencies; it is **not** an original ARM oracle, DSP port, bit-exactness test, complete branch coverage or WCET test. Host timings in CSV are explicitly host microseconds and are never converted to DSP cycles. Terrain energy was anomalously large (`2.17e32`) under abrupt full-range stimuli despite finite samples; that host smoke test is not a sound-correctness pass. Investigating it requires a bounded original-Voice stimulus oracle. Init high-nonzero-byte is a lower bound on touched arena extent, not a proof of maximum writes.

## A/B — complete voice, engines, and platform boundary

**PROVEN:** plaits/dsp/voice.cc — void Voice::Init (local-only reference: `plaits/upstream/plaits/dsp/voice.cc:37`; not distributed) registers the models in the table below. Slots 2/3/4 share one `SixOpEngine` object and executable. The original Voice embeds all 22 engine objects; they are **not a union**. `allocator->Free()` overlays engine arenas, so each track needs one peak arena, not the sum of all model arenas. Two tracks require two independent peak arenas and histories. A union of engine objects is a possible redesign but changes inactive-model persistence/reset semantics and must be compared against the original.

**PROVEN:** plaits/dsp/voice.h — struct Patch (local-only reference: `plaits/upstream/plaits/dsp/voice.h:125`; not distributed) defines note, engine, HARMONICS/TIMBRE/MORPH, three modulation amounts, decay and LPG colour. `Modulations` adds note/FM/engine/harmonics/timbre/morph/trigger/level plus patched flags. plaits/dsp/engine/engine.h — struct EngineParameters (local-only reference: `plaits/upstream/plaits/dsp/engine/engine.h:52`; not distributed) reduces the engine contract to trigger bits, note, three shape controls and accent. Engine classes own algorithm histories, their MAIN/AUX graph and `already_enveloped` behavior. The wrapper owns note smoothing, modulation curves/clamps/defaults, engine-CV hysteresis/latching, decay/LPG envelope, limiter, per-channel output gain and polarity/clipping.

**PROVEN:** plaits/dsp/voice.cc — void Voice::Render (local-only reference: `plaits/upstream/plaits/dsp/voice.cc:90`; not distributed) delays TRIGGER five control calls, uses thresholds 0.3/0.1, caches engine CV on rising edges, averages previous/current note, compresses LEVEL as `1.3*l/(0.3+abs(l))`, clamps to 0..1, and otherwise supplies accent 0.8. Patched flags choose external modulation versus the internal envelope. Amounts use the nonlinear attenuverter curve in `ApplyModulations`, not plain multiplication. Pitch is clamped -119..120; timbre/morph/harmonics 0..1. Speech special-cases prosody/speed; chiptune can select its own envelope. Enveloped engines bypass LPG, as can unpatched trigger+level. MAIN and AUX have distinct gain/limiter/LPG histories. Model changes call LoadUserData and Reset, reset MAIN limiter, and may reload a default FM bank. Reset is engine-specific; it is not uniformly clear-all or freeze/resume.

**STRONG INFERENCE:** a complete port must implement these wrapper behaviors, plus the engine graph, rather than retain B1.3 ADSR/VCF as a substitute for the Plaits LPG. Preserve the B1.3 chain for line-in/granular/return modes, but bypass or explicitly neutralize it in Plaits mode to avoid double enveloping/filtering. Note-off is a trigger/gate event policy, not a universal Plaits oscillator shutdown. Trigger-unpatched sustained behavior and overlapping tails must remain available.

ADC scanning, physical CV normalization detection, calibration, buttons/LEDs, module DAC/DMA and on-module flash programming belong to the Eurorack hardware/UI layer. They are not DSP requirements on Circuit. `UserData` data delivery is a requirement if custom FM banks/waves/terrain are promised, but its STM32 address/write implementation is not. plaits/user_data.h — class UserData (local-only reference: `plaits/upstream/plaits/user_data.h:66`; not distributed); plaits/plaits.cc — char shared_buffer (local-only reference: `plaits/upstream/plaits/plaits.cc:56`; not distributed). The original module has one 16,384-byte shared arena and 4,096-byte user-data storage. The TEST host path uses default banks/null custom data; custom data import is not exercised.

## C — rates, arithmetic, and portability

**PROVEN:** plaits/dsp/dsp.h — kSampleRate (local-only reference: `plaits/upstream/plaits/dsp/dsp.h:36`; not distributed) uses nominal 48,000 Hz, pitch correction 47,872.34 Hz, block=12, max=24. `Voice::Render(size=32)` and several original arenas are unsafe without resizing. Voice envelope coefficients and trigger delay use control-call cadence/kBlockSize, so resizing arrays alone is insufficient. A FIFO retaining 12-sample renders gives eight original renders per three Circuit 32-sample periods (96 samples); per-period work varies between two/three upstream calls and needs a worst-scheduling test. Direct 32-sample adaptation changes interpolation/control cadence unless specifically retimed. The original algorithms must be compared under the selected cadence, including six-op staggered tails, string note delay and speech variable-rate stepping.

**STRONG INFERENCE:** retain integer uint32 phase/RNG semantics with two DSP words where required; do not truncate to 24 bits. Use wide accumulators and per-variable Q formats for >1 amplitudes, pitch ratios, resonance and BLEP divisions. Replace IEEE bit-cast inverse-root/exponential helpers with separately validated approximations or multiword float emulation. A fractional table encoding cannot directly hold every original ratio/gain. There is no FFT/STFT engine in this pinned model set: additive is harmonic recurrence; modal is a resonator bank. No general FFT workspace should be invented. Plaits Grain/Swarm are oscillator grains, not B1.3 sample granular. Speech uses encoded LPC words, not recorded PCM sample playback.

**PROVEN:** stmlib/utils/random.h — class Random (local-only reference: `plaits/upstream/stmlib/utils/random.h:36`; not distributed) is a global 32-bit LCG (`1664525`, `1013904223`). Naively sharing it across MIDI1/2 would couple their noise. **STRONG INFERENCE:** save/restore an independent 32-bit RNG state per track or parameterize it; exact independent per-module sequencing requires matching call order/seeds. Original single-module global RNG behavior cannot simultaneously mean one global stream and two isolated-module streams. Document the chosen two-module semantics.

Engine-specific portability reasons, persistent members and dependencies follow. All engines use float-based shared pitch/interpolation machinery. Division/math counts in inventory are static source occurrences, never dynamic cost; transitive resource-header inclusion can overstate a model’s actual resource use. There is no render-time general heap allocation in the audited engine closure; `BufferAllocator` is a bounded arena allocator, allocated during Init, and Reset/Load may refill it.

### 00 — VA + VCF / VirtualAnalogVCFEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Two VariableShape oscillators, two SVFs, per-sample coefficient interpolation and soft clipping. Filter coefficient stability/range must be qualified. Output semantics: main low-pass; AUX high-pass. plaits/dsp/engine2/virtual_analog_vcf_engine.h — class VirtualAnalogVCFEngine (local-only reference: `plaits/upstream/plaits/dsp/engine2/virtual_analog_vcf_engine.h:40`; not distributed); plaits/dsp/engine2/virtual_analog_vcf_engine.cc — VirtualAnalogVCFEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine2/virtual_analog_vcf_engine.cc:60`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
stmlib::Svf svf_[2];
  VariableShapeOscillator oscillator_;
  VariableShapeOscillator sub_oscillator_;
  
  float previous_cutoff_;
  float previous_stage2_gain_;
  float previous_q_;
  float previous_gain_;
  float previous_sub_gain_;
```

No engine-specific arena allocation. Temporary interpolation/coefficient variables are on the C++ stack; a DSP port still needs declared register/spill workspace.

**PROVEN host accounting:** object 168 bytes; allocator reports 0 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 0 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 64 VariableShape sample steps + 64 SVF coefficient/process steps + nonlinear mixing.

Transitive dependencies: `plaits/dsp/engine2/virtual_analog_vcf_engine.cc`, `plaits/dsp/engine2/virtual_analog_vcf_engine.h`, `plaits/dsp/oscillator/oscillator.h`, `plaits/dsp/oscillator/variable_saw_oscillator.h`, `plaits/dsp/oscillator/variable_shape_oscillator.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/filter.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 01 — Phase distortion / PhaseDistortionEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Two oscillators at 2x oversampling, asymmetric triangle phase mapping, downsampling and ratios; retain interpolation and alias behavior. Output semantics: two phase-modulated/distorted variants. plaits/dsp/engine2/phase_distortion_engine.h — class PhaseDistortionEngine (local-only reference: `plaits/upstream/plaits/dsp/engine2/phase_distortion_engine.h:38`; not distributed); plaits/dsp/engine2/phase_distortion_engine.cc — PhaseDistortionEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine2/phase_distortion_engine.cc:54`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
VariableShapeOscillator shaper_;
  VariableShapeOscillator modulator_;
  float* temp_buffer_;
```

Arena allocation sites: plaits/dsp/engine2/phase_distortion_engine.cc — temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize * 4); (local-only reference: `plaits/upstream/plaits/dsp/engine2/phase_distortion_engine.cc:47`; not distributed) `temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize * 4);`.

**PROVEN host accounting:** object 112 bytes; allocator reports 384 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 128 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 128 oscillator sample steps at 2x + 32 output pairs.

Transitive dependencies: `plaits/dsp/engine2/phase_distortion_engine.cc`, `plaits/dsp/engine2/phase_distortion_engine.h`, `plaits/dsp/oscillator/oscillator.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/dsp/oscillator/variable_shape_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 02 — 6-op FM bank 1 / SixOpEngine

**PROVEN source structure; STRONG INFERENCE RED portability.** 32 algorithms and 32 unpacked patches per bank; 32-bit phases, six operator envelopes and two internal tail voices, staggered rendering, float amplitude >1. Output semantics: same soft-clipped FM signal. plaits/dsp/engine2/six_op_engine.h — class SixOpEngine (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.h:87`; not distributed); plaits/dsp/engine2/six_op_engine.cc — SixOpEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.cc:103`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
stmlib::HysteresisQuantizer2 patch_index_quantizer_;
  fm::Algorithms<6> algorithms_;
  fm::Patch* patches_;
  FMVoice voice_[kNumSixOpVoices];
  float* temp_buffer_;
  float* acc_buffer_;
  int active_voice_;
  int rendered_voice_;
```

Arena allocation sites: plaits/dsp/engine2/six_op_engine.cc — temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize * 4); (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.cc:82`; not distributed) `temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize * 4);`; plaits/dsp/engine2/six_op_engine.cc — acc_buffer_ = allocator->Allocate<float>(kMaxBlockSize * kNumSixOpVoices); (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.cc:83`; not distributed) `acc_buffer_ = allocator->Allocate<float>(kMaxBlockSize * kNumSixOpVoices);`; plaits/dsp/engine2/six_op_engine.cc — patches_ = allocator->Allocate<fm::Patch>(kNumPatchesPerBank); (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.cc:84`; not distributed) `patches_ = allocator->Allocate<fm::Patch>(kNumPatchesPerBank);`.

**PROVEN host accounting:** object 5904 bytes; allocator reports 5568 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 5,184 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: up to 384 operator sample stages + envelope/LFO/control work; one internal voice renders 64 samples per 32 output samples.

Transitive dependencies: `plaits/dsp/engine2/six_op_engine.cc`, `plaits/dsp/engine2/six_op_engine.h`, `plaits/dsp/fm/algorithms.cc`, `plaits/dsp/fm/algorithms.h`, `plaits/dsp/fm/dx_units.cc`, `plaits/dsp/fm/dx_units.h`, `plaits/dsp/fm/envelope.h`, `plaits/dsp/fm/lfo.h`, `plaits/dsp/fm/operator.h`, `plaits/dsp/fm/patch.h`, `plaits/dsp/fm/voice.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/hysteresis_quantizer.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 03 — 6-op FM bank 2 / SixOpEngine

**PROVEN source structure; STRONG INFERENCE RED portability.** Same shared SixOpEngine code/object, different default bank; do not count it as a second shared executable. Output semantics: same soft-clipped FM signal. plaits/dsp/engine2/six_op_engine.h — class SixOpEngine (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.h:87`; not distributed); plaits/dsp/engine2/six_op_engine.cc — SixOpEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.cc:103`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
stmlib::HysteresisQuantizer2 patch_index_quantizer_;
  fm::Algorithms<6> algorithms_;
  fm::Patch* patches_;
  FMVoice voice_[kNumSixOpVoices];
  float* temp_buffer_;
  float* acc_buffer_;
  int active_voice_;
  int rendered_voice_;
```

Arena allocation sites: plaits/dsp/engine2/six_op_engine.cc — temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize * 4); (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.cc:82`; not distributed) `temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize * 4);`; plaits/dsp/engine2/six_op_engine.cc — acc_buffer_ = allocator->Allocate<float>(kMaxBlockSize * kNumSixOpVoices); (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.cc:83`; not distributed) `acc_buffer_ = allocator->Allocate<float>(kMaxBlockSize * kNumSixOpVoices);`; plaits/dsp/engine2/six_op_engine.cc — patches_ = allocator->Allocate<fm::Patch>(kNumPatchesPerBank); (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.cc:84`; not distributed) `patches_ = allocator->Allocate<fm::Patch>(kNumPatchesPerBank);`.

**PROVEN host accounting:** object 5904 bytes; allocator reports 5568 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 5,184 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: same 384-stage ceiling as bank 1.

Transitive dependencies: `plaits/dsp/engine2/six_op_engine.cc`, `plaits/dsp/engine2/six_op_engine.h`, `plaits/dsp/fm/algorithms.cc`, `plaits/dsp/fm/algorithms.h`, `plaits/dsp/fm/dx_units.cc`, `plaits/dsp/fm/dx_units.h`, `plaits/dsp/fm/envelope.h`, `plaits/dsp/fm/lfo.h`, `plaits/dsp/fm/operator.h`, `plaits/dsp/fm/patch.h`, `plaits/dsp/fm/voice.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/hysteresis_quantizer.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 04 — 6-op FM bank 3 / SixOpEngine

**PROVEN source structure; STRONG INFERENCE RED portability.** Same shared SixOpEngine code/object, different default bank; banks are immutable/shared but live patches/history belong to the track. Output semantics: same soft-clipped FM signal. plaits/dsp/engine2/six_op_engine.h — class SixOpEngine (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.h:87`; not distributed); plaits/dsp/engine2/six_op_engine.cc — SixOpEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.cc:103`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
stmlib::HysteresisQuantizer2 patch_index_quantizer_;
  fm::Algorithms<6> algorithms_;
  fm::Patch* patches_;
  FMVoice voice_[kNumSixOpVoices];
  float* temp_buffer_;
  float* acc_buffer_;
  int active_voice_;
  int rendered_voice_;
```

Arena allocation sites: plaits/dsp/engine2/six_op_engine.cc — temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize * 4); (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.cc:82`; not distributed) `temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize * 4);`; plaits/dsp/engine2/six_op_engine.cc — acc_buffer_ = allocator->Allocate<float>(kMaxBlockSize * kNumSixOpVoices); (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.cc:83`; not distributed) `acc_buffer_ = allocator->Allocate<float>(kMaxBlockSize * kNumSixOpVoices);`; plaits/dsp/engine2/six_op_engine.cc — patches_ = allocator->Allocate<fm::Patch>(kNumPatchesPerBank); (local-only reference: `plaits/upstream/plaits/dsp/engine2/six_op_engine.cc:84`; not distributed) `patches_ = allocator->Allocate<fm::Patch>(kNumPatchesPerBank);`.

**PROVEN host accounting:** object 5904 bytes; allocator reports 5568 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 5,184 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: same 384-stage ceiling as bank 1.

Transitive dependencies: `plaits/dsp/engine2/six_op_engine.cc`, `plaits/dsp/engine2/six_op_engine.h`, `plaits/dsp/fm/algorithms.cc`, `plaits/dsp/fm/algorithms.h`, `plaits/dsp/fm/dx_units.cc`, `plaits/dsp/fm/dx_units.h`, `plaits/dsp/fm/envelope.h`, `plaits/dsp/fm/lfo.h`, `plaits/dsp/fm/operator.h`, `plaits/dsp/fm/patch.h`, `plaits/dsp/fm/voice.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/hysteresis_quantizer.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 05 — Wave terrain / WaveTerrainEngine

**PROVEN source structure; STRONG INFERENCE RED portability.** 2x trajectory and interpolation between two terrains, runtime divisions, sine LUT, integrated-wave terrains; optional 64x64 signed-byte custom terrain. Output semantics: terrain signal; sine of trajectory plus terrain. plaits/dsp/engine2/wave_terrain_engine.h — class WaveTerrainEngine (local-only reference: `plaits/upstream/plaits/dsp/engine2/wave_terrain_engine.h:44`; not distributed); plaits/dsp/engine2/wave_terrain_engine.cc — WaveTerrainEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine2/wave_terrain_engine.cc:180`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
float Terrain(float x, float y, int terrain_index);
  
  FastSineOscillator path_;
  float offset_;
  float terrain_;
  
  float* temp_buffer_;
  const int8_t* user_terrain_;
```

Arena allocation sites: plaits/dsp/engine2/wave_terrain_engine.cc — temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize * 4); (local-only reference: `plaits/upstream/plaits/dsp/engine2/wave_terrain_engine.cc:45`; not distributed) `temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize * 4);`.

**PROVEN host accounting:** object 64 bytes; allocator reports 384 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 128 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 64 trajectory samples + 128 terrain evaluations + 32 AUX sine lookups; each terrain evaluation has up to two divisions (conservative structural ceiling 256 terrain divisions, not cycles).

Transitive dependencies: `plaits/dsp/engine2/wave_terrain_engine.cc`, `plaits/dsp/engine2/wave_terrain_engine.h`, `plaits/dsp/oscillator/oscillator.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/dsp/oscillator/wavetable_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 06 — String machine / StringMachineEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Four divide-down generators, filters, chord ratios and 1024-float ensemble history. External precision differs from private fractional samples. Output semantics: ensemble left/right results. plaits/dsp/engine2/string_machine_engine.h — class StringMachineEngine (local-only reference: `plaits/upstream/plaits/dsp/engine2/string_machine_engine.h:39`; not distributed); plaits/dsp/engine2/string_machine_engine.cc — StringMachineEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine2/string_machine_engine.cc:85`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
void ComputeRegistration(float registration, float* amplitudes);
  
  ChordBank chords_;
  
  Ensemble ensemble_;
  StringSynthOscillator divide_down_voice_[kChordNumNotes];
  stmlib::NaiveSvf svf_[2];
  
  float morph_lp_;
  float timbre_lp_;
```

Arena allocation sites: plaits/dsp/chords/chord_bank.cc — ratios_ = allocator->Allocate<float>(kChordNumChords * kChordNumNotes); (local-only reference: `plaits/upstream/plaits/dsp/chords/chord_bank.cc:85`; not distributed) `ratios_ = allocator->Allocate<float>(kChordNumChords * kChordNumNotes);`; plaits/dsp/chords/chord_bank.cc — note_count_ = allocator->Allocate<int>(kChordNumChords); (local-only reference: `plaits/upstream/plaits/dsp/chords/chord_bank.cc:86`; not distributed) `note_count_ = allocator->Allocate<int>(kChordNumChords);`; plaits/dsp/chords/chord_bank.cc — sorted_ratios_ = allocator->Allocate<float>(kChordNumNotes); (local-only reference: `plaits/upstream/plaits/dsp/chords/chord_bank.cc:87`; not distributed) `sorted_ratios_ = allocator->Allocate<float>(kChordNumNotes);`; plaits/dsp/engine2/string_machine_engine.cc — ensemble_.Init(allocator->Allocate<Ensemble::E::T>(1024)); (local-only reference: `plaits/upstream/plaits/dsp/engine2/string_machine_engine.cc:49`; not distributed) `ensemble_.Init(allocator->Allocate<Ensemble::E::T>(1024));`.

**PROVEN host accounting:** object 304 bytes; allocator reports 4332 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 1,083 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 128 divide-down voice sample steps + two filters + 32 ensemble steps.

Transitive dependencies: `plaits/dsp/chords/chord_bank.cc`, `plaits/dsp/chords/chord_bank.h`, `plaits/dsp/engine/chord_engine.cc`, `plaits/dsp/engine/chord_engine.h`, `plaits/dsp/engine2/string_machine_engine.cc`, `plaits/dsp/engine2/string_machine_engine.h`, `plaits/dsp/fx/ensemble.h`, `plaits/dsp/fx/fx_engine.h`, `plaits/dsp/oscillator/oscillator.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/dsp/oscillator/string_synth_oscillator.h`, `plaits/dsp/oscillator/wavetable_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/cosine_oscillator.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/filter.h`, `stmlib/dsp/hysteresis_quantizer.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 07 — Chiptune / ChiptuneEngine

**PROVEN source structure; STRONG INFERENCE GREEN portability.** Counter/phase/arpeggiator and chord operations are direct fixed-point candidates; keep five internal chord voices plus bass, envelope and original quantization. Output semantics: arp/chord signal; bass triangle. plaits/dsp/engine2/chiptune_engine.h — class ChiptuneEngine (local-only reference: `plaits/upstream/plaits/dsp/engine2/chiptune_engine.h:40`; not distributed); plaits/dsp/engine2/chiptune_engine.cc — ChiptuneEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine2/chiptune_engine.cc:59`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
SuperSquareOscillator voice_[kChordNumVoices];
  NESTriangleOscillator<> bass_;
  
  ChordBank chords_;
  Arpeggiator arpeggiator_;
  stmlib::HysteresisQuantizer2 arpeggiator_pattern_selector_;
  
  float envelope_shape_;
  float envelope_state_;
  float aux_envelope_amount_;
```

Arena allocation sites: plaits/dsp/chords/chord_bank.cc — ratios_ = allocator->Allocate<float>(kChordNumChords * kChordNumNotes); (local-only reference: `plaits/upstream/plaits/dsp/chords/chord_bank.cc:85`; not distributed) `ratios_ = allocator->Allocate<float>(kChordNumChords * kChordNumNotes);`; plaits/dsp/chords/chord_bank.cc — note_count_ = allocator->Allocate<int>(kChordNumChords); (local-only reference: `plaits/upstream/plaits/dsp/chords/chord_bank.cc:86`; not distributed) `note_count_ = allocator->Allocate<int>(kChordNumChords);`; plaits/dsp/chords/chord_bank.cc — sorted_ratios_ = allocator->Allocate<float>(kChordNumNotes); (local-only reference: `plaits/upstream/plaits/dsp/chords/chord_bank.cc:87`; not distributed) `sorted_ratios_ = allocator->Allocate<float>(kChordNumNotes);`.

**PROVEN host accounting:** object 272 bytes; allocator reports 236 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 59 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: worst unpatched branch 160 SuperSquare sample steps + 32 NES bass steps; clocked branch 32 + 32.

Transitive dependencies: `plaits/dsp/chords/chord_bank.cc`, `plaits/dsp/chords/chord_bank.h`, `plaits/dsp/engine2/arpeggiator.h`, `plaits/dsp/engine2/chiptune_engine.cc`, `plaits/dsp/engine2/chiptune_engine.h`, `plaits/dsp/oscillator/nes_triangle_oscillator.h`, `plaits/dsp/oscillator/oscillator.h`, `plaits/dsp/oscillator/super_square_oscillator.h`, `plaits/dsp/oscillator/wavetable_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/hysteresis_quantizer.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 08 — Virtual analog / VirtualAnalogEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Active VA_VARIANT=2 includes three VariableShape/sync renders AND VariableSaw, with reciprocal gain normalization and separate MAIN/AUX graphs. Output semantics: variable square + saw; two monster-sync signals differenced. plaits/dsp/engine/virtual_analog_engine.h — class VirtualAnalogEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/virtual_analog_engine.h:40`; not distributed); plaits/dsp/engine/virtual_analog_engine.cc — VirtualAnalogEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/virtual_analog_engine.cc:78`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
float ComputeDetuning(float detune) const;
  
  VariableShapeOscillator primary_;
  VariableShapeOscillator auxiliary_;

  VariableShapeOscillator sync_;
  VariableSawOscillator variable_saw_;

  float auxiliary_amount_;
  float xmod_amount_;
  float* temp_buffer_;
```

Arena allocation sites: plaits/dsp/engine/virtual_analog_engine.cc — temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize); (local-only reference: `plaits/upstream/plaits/dsp/engine/virtual_analog_engine.cc:50`; not distributed) `temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize);`.

**PROVEN host accounting:** object 192 bytes; allocator reports 96 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 32 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 96 VariableShape sample steps + 32 VariableSaw steps + gain/mixing; only the VariableSaw primitive has DSP evidence.

Transitive dependencies: `plaits/dsp/engine/virtual_analog_engine.cc`, `plaits/dsp/engine/virtual_analog_engine.h`, `plaits/dsp/oscillator/oscillator.h`, `plaits/dsp/oscillator/variable_saw_oscillator.h`, `plaits/dsp/oscillator/variable_shape_oscillator.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 09 — Waveshaping / WaveshapingEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Two BLEP oscillators, interpolated int16 shaper bank, Hermite wavefolders and sine; immutable tables and overshoot/headroom are required. Output semantics: waveshaped/folded slope; overtone/triangle-derived output. plaits/dsp/engine/waveshaping_engine.h — class WaveshapingEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/waveshaping_engine.h:37`; not distributed); plaits/dsp/engine/waveshaping_engine.cc — WaveshapingEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/waveshaping_engine.cc:64`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
Oscillator slope_;
  Oscillator triangle_;
  float previous_shape_;
  float previous_wavefolder_gain_;
  float previous_overtone_gain_;
```

No engine-specific arena allocation. Temporary interpolation/coefficient variables are on the C++ stack; a DSP port still needs declared register/spill workspace.

**PROVEN host accounting:** object 96 bytes; allocator reports 0 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 0 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 64 oscillator sample steps + 32 shaper/folder/output operations.

Transitive dependencies: `plaits/dsp/engine/waveshaping_engine.cc`, `plaits/dsp/engine/waveshaping_engine.h`, `plaits/dsp/oscillator/oscillator.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/dsp.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 10 — 2-op FM / FMEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** 4x oversampling, three uint32 phases, phase feedback, sine interpolation and FIR accumulators. Reducing phase to 24 bits changes behavior. Output semantics: carrier; subcarrier. plaits/dsp/engine/fm_engine.h — class FMEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/fm_engine.h:36`; not distributed); plaits/dsp/engine/fm_engine.cc — FMEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/fm_engine.cc:56`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
uint32_t carrier_phase_;
  uint32_t modulator_phase_;
  uint32_t sub_phase_;
  
  float previous_carrier_frequency_;
  float previous_modulator_frequency_;
  float previous_amount_;
  float previous_feedback_;
  float previous_sample_;
  
  float sub_fir_;
  float carrier_fir_;
```

No engine-specific arena allocation. Temporary interpolation/coefficient variables are on the C++ stack; a DSP port still needs declared register/spill workspace.

**PROVEN host accounting:** object 64 bytes; allocator reports 0 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 0 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 384 SinePM calls + 256 downsampler Accumulate calls per 32 samples, plus feedback and control.

Transitive dependencies: `plaits/dsp/downsampler/4x_downsampler.h`, `plaits/dsp/engine/fm_engine.cc`, `plaits/dsp/engine/fm_engine.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 11 — Granular formant / GrainEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Two Grainlets, Z oscillator and DC blockers. This is synthetic formant/grainlet synthesis, not a sample-player or B1.3 SDRAM granular engine. Output semantics: grainlet combination; Z oscillator. plaits/dsp/engine/grain_engine.h — class GrainEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/grain_engine.h:41`; not distributed); plaits/dsp/engine/grain_engine.cc — GrainEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/grain_engine.cc:51`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
GrainletOscillator grainlet_[2];
  
  ZOscillator z_oscillator_;
  stmlib::OnePole dc_blocker_[2];
  
  float grain_balance_;
```

No engine-specific arena allocation. Temporary interpolation/coefficient variables are on the C++ stack; a DSP port still needs declared register/spill workspace.

**PROVEN host accounting:** object 144 bytes; allocator reports 0 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 0 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 96 oscillator sample steps + 64 DC-blocker sample steps.

Transitive dependencies: `plaits/dsp/engine/grain_engine.cc`, `plaits/dsp/engine/grain_engine.h`, `plaits/dsp/oscillator/grainlet_oscillator.h`, `plaits/dsp/oscillator/oscillator.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/dsp/oscillator/vosim_oscillator.h`, `plaits/dsp/oscillator/z_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/filter.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 12 — Additive / AdditiveEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** 36 harmonics in three 12-harmonic batches; amplitude envelopes, cosine recurrence, exponential/power amplitude shaping and anti-alias attenuation. Output semantics: 24-harmonic spectrum; 12-harmonic alternative. plaits/dsp/engine/additive_engine.h — class AdditiveEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/additive_engine.h:41`; not distributed); plaits/dsp/engine/additive_engine.cc — AdditiveEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/additive_engine.cc:117`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
void UpdateAmplitudes(
      float centroid,
      float slope,
      float bumps,
      float* amplitudes,
      const int* harmonic_indices,
      size_t num_harmonics);
      
  HarmonicOscillator<kHarmonicBatchSize> harmonic_oscillator_[kNumHarmonicOscillators];
  
  float* amplitudes_;
```

Arena allocation sites: plaits/dsp/engine/additive_engine.cc — amplitudes_ = allocator->Allocate<float>(kNumHarmonics); (local-only reference: `plaits/upstream/plaits/dsp/engine/additive_engine.cc:42`; not distributed) `amplitudes_ = allocator->Allocate<float>(kNumHarmonics);`.

**PROVEN host accounting:** object 200 bytes; allocator reports 144 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 36 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: up to 1152 harmonic amplitude/sample stages (24 MAIN + 12 AUX harmonics) + amplitude calculation.

Transitive dependencies: `plaits/dsp/engine/additive_engine.cc`, `plaits/dsp/engine/additive_engine.h`, `plaits/dsp/oscillator/harmonic_oscillator.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/cosine_oscillator.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 13 — Wavetable / WavetableEngine

**PROVEN source structure; STRONG INFERENCE RED portability.** 25344 signed16 integrated samples, 3D interpolation and differentiation, per-sample reciprocal; allocated 64-pointer map actually writes 256 entries. Output semantics: interpolated/differentiated wave; quantized version. plaits/dsp/engine/wavetable_engine.h — class WavetableEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/wavetable_engine.h:37`; not distributed); plaits/dsp/engine/wavetable_engine.cc — WavetableEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/wavetable_engine.cc:113`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
float ReadWave(int x, int y, int z, int phase_i, float phase_f);
   
  float phase_;
  
  float x_pre_lp_;
  float y_pre_lp_;
  float z_pre_lp_;
  
  float x_lp_;
  float y_lp_;
  float z_lp_;

  float previous_x_;
  float previous_y_;
  float previous_z_;
  float previous_f0_;
  
  
  
  const int16_t** wave_map_;
  
  Differentiator diff_out_;
```

Arena allocation sites: plaits/dsp/engine/wavetable_engine.cc — wave_map_ = allocator->Allocate<const int16_t*>(kNumWavesPerBank); (local-only reference: `plaits/upstream/plaits/dsp/engine/wavetable_engine.cc:66`; not distributed) `wave_map_ = allocator->Allocate<const int16_t*>(kNumWavesPerBank);`.

**PROVEN host accounting:** object 88 bytes; allocator reports 512 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 256 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 256 Hermite wave reads = 1024 table element reads per 32 output samples, plus 32 gain reciprocals and filtering; uncached upper traffic.

Transitive dependencies: `plaits/dsp/engine/wavetable_engine.cc`, `plaits/dsp/engine/wavetable_engine.h`, `plaits/dsp/oscillator/oscillator.h`, `plaits/dsp/oscillator/wavetable_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 14 — Chord / ChordEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Five internal voices, divide-down and 128x15 wavetable oscillators, chord inversions and registrations. One MIDI note does not mean one internal oscillator. Output semantics: different mixes/voice groups of chord. plaits/dsp/engine/chord_engine.h — class ChordEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/chord_engine.h:41`; not distributed); plaits/dsp/engine/chord_engine.cc — ChordEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/chord_engine.cc:104`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
void ComputeRegistration(float registration, float* amplitudes);
  int ComputeChordInversion(
      float inversion,
      float* ratios,
      float* amplitudes);
  
  StringSynthOscillator divide_down_voice_[kChordNumVoices];
  WavetableOscillator<128, 15> wavetable_voice_[kChordNumVoices];
  ChordBank chords_;
  
  float morph_lp_;
  float timbre_lp_;
```

Arena allocation sites: plaits/dsp/chords/chord_bank.cc — ratios_ = allocator->Allocate<float>(kChordNumChords * kChordNumNotes); (local-only reference: `plaits/upstream/plaits/dsp/chords/chord_bank.cc:85`; not distributed) `ratios_ = allocator->Allocate<float>(kChordNumChords * kChordNumNotes);`; plaits/dsp/chords/chord_bank.cc — note_count_ = allocator->Allocate<int>(kChordNumChords); (local-only reference: `plaits/upstream/plaits/dsp/chords/chord_bank.cc:86`; not distributed) `note_count_ = allocator->Allocate<int>(kChordNumChords);`; plaits/dsp/chords/chord_bank.cc — sorted_ratios_ = allocator->Allocate<float>(kChordNumNotes); (local-only reference: `plaits/upstream/plaits/dsp/chords/chord_bank.cc:87`; not distributed) `sorted_ratios_ = allocator->Allocate<float>(kChordNumNotes);`.

**PROVEN host accounting:** object 384 bytes; allocator reports 236 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 59 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: five voice iterations, each can render divide-down and wavetable graphs; cost includes chord/inversion updates.

Transitive dependencies: `plaits/dsp/chords/chord_bank.cc`, `plaits/dsp/chords/chord_bank.h`, `plaits/dsp/engine/chord_engine.cc`, `plaits/dsp/engine/chord_engine.h`, `plaits/dsp/oscillator/oscillator.h`, `plaits/dsp/oscillator/string_synth_oscillator.h`, `plaits/dsp/oscillator/wavetable_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/hysteresis_quantizer.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 15 — Speech / SpeechEngine

**PROVEN source structure; STRONG INFERENCE RED portability.** Naive + SAM + LPC, five packed word banks, 1024 decoded 14-byte frames, 10th-order LPC, variable-rate synthesis, prosody and word decoding. Output semantics: formant/word speech; excitation/alternative speech. plaits/dsp/engine/speech_engine.h — class SpeechEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/speech_engine.h:41`; not distributed); plaits/dsp/engine/speech_engine.cc — SpeechEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/speech_engine.cc:59`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
stmlib::HysteresisQuantizer2 word_bank_quantizer_;
  
  NaiveSpeechSynth naive_speech_synth_;
  SAMSpeechSynth sam_speech_synth_;
  
  LPCSpeechSynthController lpc_speech_synth_controller_;
  LPCSpeechSynthWordBank lpc_speech_synth_word_bank_;
  
  float* temp_buffer_[2];
  float prosody_amount_;
  float speed_;
```

Arena allocation sites: [plaits/dsp/engine/speech_engine.cc — temp_buffer_[0] = allocator->Allocate<float>(kMaxBlockSize);](<C:/Proj SSD/CODEX/CIRCUIT/plaits/upstream/plaits/dsp/engine/speech_engine.cc:48>) `temp_buffer_[0] = allocator->Allocate<float>(kMaxBlockSize);`; [plaits/dsp/engine/speech_engine.cc — temp_buffer_[1] = allocator->Allocate<float>(kMaxBlockSize);](<C:/Proj SSD/CODEX/CIRCUIT/plaits/upstream/plaits/dsp/engine/speech_engine.cc:49>) `temp_buffer_[1] = allocator->Allocate<float>(kMaxBlockSize);`; plaits/dsp/speech/lpc_speech_synth_controller.cc — frames_ = allocator->Allocate<LPCSpeechSynth::Frame>( (local-only reference: `plaits/upstream/plaits/dsp/speech/lpc_speech_synth_controller.cc:119`; not distributed) `frames_ = allocator->Allocate<LPCSpeechSynth::Frame>(`; plaits/dsp/speech/lpc_speech_synth_controller.cc — word_boundaries_ = allocator->Allocate<int>(kLPCSpeechSynthMaxWords); (local-only reference: `plaits/upstream/plaits/dsp/speech/lpc_speech_synth_controller.cc:121`; not distributed) `word_boundaries_ = allocator->Allocate<int>(kLPCSpeechSynthMaxWords);`.

**PROVEN host accounting:** object 480 bytes; allocator reports 14656 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 12,384 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: max(naive+SAM, LPC+SAM, words-LPC) paths; LPC runs at variable synthesis cadence; decoded-bank load/reset is a separate switching cost.

Transitive dependencies: `plaits/dsp/engine/speech_engine.cc`, `plaits/dsp/engine/speech_engine.h`, `plaits/dsp/oscillator/oscillator.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/dsp/speech/lpc_speech_synth.cc`, `plaits/dsp/speech/lpc_speech_synth.h`, `plaits/dsp/speech/lpc_speech_synth_controller.cc`, `plaits/dsp/speech/lpc_speech_synth_controller.h`, `plaits/dsp/speech/lpc_speech_synth_words.cc`, `plaits/dsp/speech/lpc_speech_synth_words.h`, `plaits/dsp/speech/naive_speech_synth.cc`, `plaits/dsp/speech/naive_speech_synth.h`, `plaits/dsp/speech/sam_speech_synth.cc`, `plaits/dsp/speech/sam_speech_synth.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/filter.h`, `stmlib/dsp/hysteresis_quantizer.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 16 — Swarm / SwarmEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Eight independent SwarmVoice records with grain envelopes, saw/sine oscillators and RNG; event bursts change work and tails. Output semantics: swarm saw/grain mix; sine mix. plaits/dsp/engine/swarm_engine.h — class SwarmEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/swarm_engine.h:234`; not distributed); plaits/dsp/engine/swarm_engine.cc — SwarmEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/swarm_engine.cc:50`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
SwarmVoice* swarm_voice_;
```

Arena allocation sites: plaits/dsp/engine/swarm_engine.cc — swarm_voice_ = allocator->Allocate<SwarmVoice>(kNumSwarmVoices); (local-only reference: `plaits/upstream/plaits/dsp/engine/swarm_engine.cc:39`; not distributed) `swarm_voice_ = allocator->Allocate<SwarmVoice>(kNumSwarmVoices);`.

**PROVEN host accounting:** object 32 bytes; allocator reports 512 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 128 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 256 SwarmVoice output-sample steps plus grain triggers/oscillators/envelopes.

Transitive dependencies: `plaits/dsp/engine/swarm_engine.cc`, `plaits/dsp/engine/swarm_engine.h`, `plaits/dsp/oscillator/oscillator.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/dsp/oscillator/string_synth_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 17 — Filtered noise / NoiseEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Two clocked RNG streams, three SVFs, coefficient updates, per-sample inverse square root/division gain normalization; small state does not imply low CPU. Output semantics: LP/HP noise; two-band-pass mix. plaits/dsp/engine/noise_engine.h — class NoiseEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/noise_engine.h:39`; not distributed); plaits/dsp/engine/noise_engine.cc — NoiseEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/noise_engine.cc:57`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
ClockedNoise clocked_noise_[2];
  stmlib::Svf lp_hp_filter_;
  stmlib::Svf bp_filter_[2];
  
  float previous_f0_;
  float previous_f1_;
  float previous_q_;
  float previous_mode_;
  
  float* temp_buffer_;
```

Arena allocation sites: plaits/dsp/engine/noise_engine.cc — temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize); (local-only reference: `plaits/upstream/plaits/dsp/engine/noise_engine.cc:50`; not distributed) `temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize);`.

**PROVEN host accounting:** object 144 bytes; allocator reports 96 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 32 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 64 ClockedNoise sample steps + 96 SVF coefficient/process steps + 32 gain sqrt/division operations.

Transitive dependencies: `plaits/dsp/engine/noise_engine.cc`, `plaits/dsp/engine/noise_engine.h`, `plaits/dsp/noise/clocked_noise.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/filter.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 18 — Particles / ParticleEngine

**PROVEN source structure; STRONG INFERENCE RED portability.** Six particle resonators, RNG/events, filter and 8192 uint16 diffuser delay samples. Natural 24-bit storage needs 8192 cells, not 4096. Output semantics: diffused/filter particles; direct particles. plaits/dsp/engine/particle_engine.h — class ParticleEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/particle_engine.h:40`; not distributed); plaits/dsp/engine/particle_engine.cc — ParticleEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/particle_engine.cc:50`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
Particle particle_[kNumParticles];
  Diffuser diffuser_;
  stmlib::Svf post_filter_;
```

Arena allocation sites: plaits/dsp/engine/particle_engine.cc — diffuser_.Init(allocator->Allocate<uint16_t>(8192)); (local-only reference: `plaits/upstream/plaits/dsp/engine/particle_engine.cc:42`; not distributed) `diffuser_.Init(allocator->Allocate<uint16_t>(8192));`.

**PROVEN host accounting:** object 248 bytes; allocator reports 16384 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 8,192 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 192 Particle sample steps + 32 post-filter and diffuser steps; event coefficient work adds variable cost.

Transitive dependencies: `plaits/dsp/engine/particle_engine.cc`, `plaits/dsp/engine/particle_engine.h`, `plaits/dsp/fx/diffuser.h`, `plaits/dsp/fx/fx_engine.h`, `plaits/dsp/noise/particle.h`, `stmlib/dsp/cosine_oscillator.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/filter.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 19 — Strings / StringEngine

**PROVEN source structure; STRONG INFERENCE RED portability.** Three StringVoice histories, each 1024 main + 256 stretch float samples; fractional delays, dispersion, nonlinear bridge and resampling at low pitch. Output semantics: string result; excitation/alternate result. plaits/dsp/engine/string_engine.h — class StringEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/string_engine.h:39`; not distributed); plaits/dsp/engine/string_engine.cc — StringEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/string_engine.cc:55`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
StringVoice voice_[kNumStrings];

  float f0_[kNumStrings];
  DelayLine<float, 16> f0_delay_;
  int active_string_;
  float* temp_buffer_;
```

Arena allocation sites: plaits/dsp/engine/string_engine.cc — temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize); (local-only reference: `plaits/upstream/plaits/dsp/engine/string_engine.cc:39`; not distributed) `temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize);`; plaits/dsp/engine/string_engine.cc — f0_delay_.Init(allocator->Allocate<float>(16)); (local-only reference: `plaits/upstream/plaits/dsp/engine/string_engine.cc:45`; not distributed) `f0_delay_.Init(allocator->Allocate<float>(16));`; plaits/dsp/physical_modelling/string.cc — string_.Init(allocator->Allocate<float>(kDelayLineSize)); (local-only reference: `plaits/upstream/plaits/dsp/physical_modelling/string.cc:47`; not distributed) `string_.Init(allocator->Allocate<float>(kDelayLineSize));`; plaits/dsp/physical_modelling/string.cc — stretch_.Init(allocator->Allocate<float>(kDelayLineSize / 4)); (local-only reference: `plaits/upstream/plaits/dsp/physical_modelling/string.cc:48`; not distributed) `stretch_.Init(allocator->Allocate<float>(kDelayLineSize / 4));`.

**PROVEN host accounting:** object 432 bytes; allocator reports 15520 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 3,888 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 96 StringVoice output-sample steps, each string Process includes fractional delay/filter/nonlinearity; excitation update and resampling vary.

Transitive dependencies: `plaits/dsp/engine/string_engine.cc`, `plaits/dsp/engine/string_engine.h`, `plaits/dsp/noise/dust.h`, `plaits/dsp/physical_modelling/delay_line.h`, `plaits/dsp/physical_modelling/string.cc`, `plaits/dsp/physical_modelling/string.h`, `plaits/dsp/physical_modelling/string_voice.cc`, `plaits/dsp/physical_modelling/string_voice.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/filter.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 20 — Modal resonator / ModalEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Up to 24 resonant modes, 48 filter histories and amplitude bank, excitation RNG/filter; coefficient precision and high-Q stability need independent checks. Output semantics: 24-mode resonator; excitation. plaits/dsp/engine/modal_engine.h — class ModalEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/modal_engine.h:37`; not distributed); plaits/dsp/engine/modal_engine.cc — ModalEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/modal_engine.cc:48`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
ModalVoice voice_;
  float* temp_buffer_;
  float harmonics_lp_;
```

Arena allocation sites: plaits/dsp/engine/modal_engine.cc — temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize); (local-only reference: `plaits/upstream/plaits/dsp/engine/modal_engine.cc:39`; not distributed) `temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize);`.

**PROVEN host accounting:** object 344 bytes; allocator reports 96 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 32 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: up to 768 mode sample stages plus excitation/filter/coefficient work.

Transitive dependencies: `plaits/dsp/engine/modal_engine.cc`, `plaits/dsp/engine/modal_engine.h`, `plaits/dsp/noise/dust.h`, `plaits/dsp/physical_modelling/modal_voice.cc`, `plaits/dsp/physical_modelling/modal_voice.h`, `plaits/dsp/physical_modelling/resonator.cc`, `plaits/dsp/physical_modelling/resonator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/cosine_oscillator.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/filter.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 21 — Bass drum / BassDrumEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Analog and synthetic bass drum graphs, envelopes, nonlinear resonator/transient/noise, overdrive. Both outputs require both drum algorithms. Output semantics: analog bass; synthetic bass. plaits/dsp/engine/bass_drum_engine.h — class BassDrumEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/bass_drum_engine.h:40`; not distributed); plaits/dsp/engine/bass_drum_engine.cc — BassDrumEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/bass_drum_engine.cc:48`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
AnalogBassDrum analog_bass_drum_;
  SyntheticBassDrum synthetic_bass_drum_;
  
  Overdrive overdrive_;
```

No engine-specific arena allocation. Temporary interpolation/coefficient variables are on the C++ stack; a DSP port still needs declared register/spill workspace.

**PROVEN host accounting:** object 192 bytes; allocator reports 0 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 0 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 32 analog-bass + 32 synthetic-bass + 32 overdrive sample steps.

Transitive dependencies: `plaits/dsp/drums/analog_bass_drum.h`, `plaits/dsp/drums/synthetic_bass_drum.h`, `plaits/dsp/engine/bass_drum_engine.cc`, `plaits/dsp/engine/bass_drum_engine.h`, `plaits/dsp/fx/overdrive.h`, `plaits/dsp/fx/sample_rate_reducer.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/filter.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 22 — Snare drum / SnareDrumEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Analog and synthetic snare graphs, multiple resonators, RNG, envelopes and nonlinear filters; evaluate trigger maxima and sustain mode separately. Output semantics: analog snare; synthetic snare. plaits/dsp/engine/snare_drum_engine.h — class SnareDrumEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/snare_drum_engine.h:38`; not distributed); plaits/dsp/engine/snare_drum_engine.cc — SnareDrumEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/snare_drum_engine.cc:47`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
AnalogSnareDrum analog_snare_drum_;
  SyntheticSnareDrum synthetic_snare_drum_;
```

No engine-specific arena allocation. Temporary interpolation/coefficient variables are on the C++ stack; a DSP port still needs declared register/spill workspace.

**PROVEN host accounting:** object 304 bytes; allocator reports 0 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 0 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 32 analog-snare + 32 synthetic-snare sample steps, each contains multiple oscillators/filters.

Transitive dependencies: `plaits/dsp/drums/analog_snare_drum.h`, `plaits/dsp/drums/synthetic_snare_drum.h`, `plaits/dsp/engine/snare_drum_engine.cc`, `plaits/dsp/engine/snare_drum_engine.h`, `plaits/dsp/oscillator/sine_oscillator.h`, `plaits/resources.cc`, `plaits/resources.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/filter.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/rsqrt.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

### 23 — Hi-hat / HiHatEngine

**PROVEN source structure; STRONG INFERENCE YELLOW portability.** Two HiHat template graphs with square/ring-mod metallic noise, Swing/Linear VCA and SVFs; two shared scratch buffers, independent graph histories. Output semantics: square-noise/swing hat; ring-mod/linear hat. plaits/dsp/engine/hi_hat_engine.h — class HiHatEngine (local-only reference: `plaits/upstream/plaits/dsp/engine/hi_hat_engine.h:38`; not distributed); plaits/dsp/engine/hi_hat_engine.cc — HiHatEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/hi_hat_engine.cc:46`; not distributed).

Persistent object members (functions excluded from the ownership count; the complete transitive object definitions are in the inventory):
```cpp
HiHat<SquareNoise, SwingVCA, true, false> hi_hat_1_;
  HiHat<RingModNoise, LinearVCA, false, true> hi_hat_2_;
  
  float* temp_buffer_;
```

Arena allocation sites: plaits/dsp/engine/hi_hat_engine.cc — temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize * 2); (local-only reference: `plaits/upstream/plaits/dsp/engine/hi_hat_engine.cc:39`; not distributed) `temp_buffer_ = allocator->Allocate<float>(kMaxBlockSize * 2);`.

**PROVEN host accounting:** object 336 bytes; allocator reports 192 bytes at original max=24. **STRONG INFERENCE logical arena plan at 32-sample capacity:** 64 DSP cells under the explicit packing rules below, excluding object scalars and caller scratch. **UNKNOWN:** emitted P words and complete DSP timing. Structural work: 32 samples through each of two metallic-noise/filter/VCA graphs.

Transitive dependencies: `plaits/dsp/drums/hi_hat.h`, `plaits/dsp/engine/hi_hat_engine.cc`, `plaits/dsp/engine/hi_hat_engine.h`, `plaits/dsp/oscillator/oscillator.h`, `stmlib/dsp/dsp.h`, `stmlib/dsp/filter.h`, `stmlib/dsp/parameter_interpolator.h`, `stmlib/dsp/polyblep.h`, `stmlib/dsp/units.cc`, `stmlib/dsp/units.h`, `stmlib/utils/random.cc`, `stmlib/utils/random.h`. Full per-file division, nonlinear math, table, array and RNG evidence is retained in `source-inventory.json`; whether RNG is actually on a model’s active branch is determined by its Render graph, not by include presence.

## D — shared resources and one/two-instance accounting

**PROVEN:** generated plaits/resources.h — WAV_INTEGRATED_WAVES_SIZE (local-only reference: `plaits/upstream/plaits/resources.h:109`; not distributed) and actual array parsing account for 74,702 bytes / 41,686 source elements in `resources.cc`. This excludes pointer tables, speech banks/phoneme constants, FM `dx_units` constants and stmlib pitch tables. It is not DSP executable P size.

| Shared asset | Exact source count | Placement consequence |
|---|---:|---|
| syx_bank_0 (uint8_t) | 4,096 elements / 4,096 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| syx_bank_1 (uint8_t) | 4,096 elements / 4,096 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| syx_bank_2 (uint8_t) | 4,096 elements / 4,096 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_sine (float) | 641 elements / 2,564 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_fm_frequency_quantizer (float) | 130 elements / 520 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_fold (float) | 516 elements / 2,064 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_fold_2 (float) | 516 elements / 2,064 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_stiffness (float) | 65 elements / 260 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_svf_shift (float) | 257 elements / 1,028 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_4x_downsampler_fir (float) | 4 elements / 16 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_ws_inverse_tan (int16_t) | 257 elements / 514 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_ws_inverse_sin (int16_t) | 257 elements / 514 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_ws_linear (int16_t) | 257 elements / 514 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_ws_bump (int16_t) | 257 elements / 514 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_ws_double_bump (int16_t) | 257 elements / 514 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| lut_lpc_excitation_pulse (int8_t) | 640 elements / 640 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |
| wav_integrated_waves (int16_t) | 25,344 elements / 50,688 bytes | Shared once; 24-bit fixed float tables need scaling; byte/16-bit data need packing or one cell per value |

**PROVEN:** the integrated waves alone contain 25,344 signed16 values (50,688 bytes), exceeding the entire 16,384-word core-0 P range even before code if stored one value per P word; even maximally byte-packed in 24-bit words they require 16,896 words. Therefore an all-in-P full-resource port cannot fit. **STRONG INFERENCE:** place large immutable waves/word/FM banks in external data storage or another qualified storage route, share them once, and retain hot tables/cache in private data memory. Required external words for one signed16 sample per usable 16-bit SDRAM word = 25,344, shared between tracks; immutable capacity is less important than access schedule/precision.

Additional exact source resources: stmlib pitch-ratio arrays 257+257 floats (stmlib/dsp/units.h — lut_pitch_ratio_high (local-only reference: `plaits/upstream/stmlib/dsp/units.h:37`; not distributed)); speech word banks 1,233+900+1,552+2,524+4,802 = 11,011 bytes (plaits/dsp/speech/lpc_speech_synth_words.h — bank_0 (local-only reference: `plaits/upstream/plaits/dsp/speech/lpc_speech_synth_words.h:38`; not distributed)). Existing host FM patch struct is 156 bytes, 32 unpacked patches = 4,992 bytes per active bank. Those unpacked bytes can be 4,992 natural DSP cells or 1,664 packed 24-bit cells with extraction; sharing immutable decoded bank data is possible only after proving no mutation/Load aliasing across tracks. FM algorithm dispatch metadata initialized identically can also be shared after separating it from independent operator/envelope histories.

Arena estimates use one word per float-derived sample/scalar/address; one word per original uint16 diffuser sample; 12 unpacked fields per LPC frame; uint8 FM patch fields natural one-word cells; chord ratios/counts 59 cells; Swarm 8x64 host bytes is only a 128-cell scalar proxy. These are logical adaptation estimates, **not** proofs that all values can be represented accurately in one DSP word. Original float-exact preservation would need multiword representations and larger buffers. No arena is allocated to a live address here.

Speech: 1024x12 = 12,288 frame fields +32 word boundaries +64 temp samples = **12,384 natural cells/track**. Packing its original 14,336 frame bytes into 24-bit private words reduces frames to 4,779 cells, total 4,875 including boundaries/temp, at extraction cost. External backing limited to 16 useful bits changes packing. Particle: **8,192 delay cells/track**, 16,384 for two; original intentionally quantizes diffuser storage to uint16. String: 3x(1024+256)+16 pitch-delay+32 temp = **3,888 cells/track**, 7,776 for two, with independent histories. String machine: 1024 float delay +59 chord cells = **1,083/track**. Six-op: 128 temp+64 accumulation+4992 natural patch fields = **5,184 cells**.

Six-op natural arena total: **5,184 cells** (=128+64+4,992); packed patch variant is **1,856 cells** (=128+64+1664). Table counts do not include independent FMVoice objects. Wavetable declared map allocation is 64 pointers but `LoadUserData` fills four banks x64 = **256 pointers**. Host probe: allocator=512 bytes, highest initialized nonzero byte=2046 in the 2048-byte map. **PROVEN allocator-extent mismatch:** a port must allocate 256 map cells or eliminate the map, not reproduce the under-allocation.

**PROVEN host object accounting:** original `sizeof(Voice)=11,064` bytes, plus a 16,384-byte source arena =27,448 bytes per x64 host Voice plus arena; two =54,896, excluding separate output/DMA/user-data buffers. Host bytes are not DSP words. A rough one-cell-per-4-host-byte object proxy is 2,766 cells/track; x64 pointers/ABI padding overcount some fields, byte fields and 32-bit phase handling can undercount others. Keeping all original object histories plus the largest natural arena gives **~15,150 cells/track; ~30,300 for two** before caller workspace, the +16 output cells needed when enlarging Voice 24 to32, and FIFO (2766+12384), a planning proxy with UNKNOWN fidelity/ownership, not an allocation certificate. Sharing read-only FM dispatch metadata and packing cached frames can reduce it substantially; quantified final state needs an emitted layout.

A possible split: X holds per-track control, envelope, RNG, oscillator/filter scalars; Y holds small audio/delay histories; external holds large per-track delay/decoded caches and shared immutable assets; P holds shared executable code and only hot immutable tables if justified. Sequential rendering can share one dedicated save/temporary area (37 raw saves plus kernel spills/controls, sized for the largest model), but per-track persistent histories, MAIN/AUX envelope/filter state and FIFO remain independent. Require non-reentrancy or a separate ISR save contract; the previous 64-word workspace is not sufficient evidence for all models.

## E — precise B1.3 removal boundaries and what remains

**PROVEN bytes:** B1.3 original core-0 `0000,3FED)` =16,365 words; core-1 `[0000,07FF)` =2,047 words. The reference MIDI module `[336E,3E1F)` is 2,737 words; the read-only cached assembler reproduces every byte of that interval against the retained B1.3 fixture. [tools/vcf21_dsp.py — def code (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21_dsp.py:151`; not distributed); [plaits/poc/full_audit/reclaim.py](<../plaits/poc/full_audit/reclaim.py>). Actual subsequent relocation is not performed.

| Core-0 P interval | Words | Removal/retention |
|---|---:|---|
| `36AD,3876)` | 457 | Oscillator pitch/shape/morph/dual control; removable only with replacement Plaits control and preserved granular parameters |
| `[3999,3B82)` | 489 | Single/dual waveforms, interactions and VA-noise; retain preceding granular dispatch `[3970,3999)` |
| `[3D9E,3E1F)` | 129 | TINC oscillator pitch table; remove only once no retained caller reads it |
| `[336E,36AD)` | 831 | Mailbox and shared control; VA-only branches can be factored but much is required by line/gran modes |
| `[3876,3999)` | 291 | Ring/return selection, loops, save/restore and granular dispatch |
| `[3B82,3D9E)` | 540 | Shared VCA/FX/filter, return/feedback completion — retain for granular/line-in/FX-return functionality |

**PROVEN assembler counts:** removing the three oscillator islands yields 1,075 words, module=1,662, theoretical complete core-0=15,290 and **1,094 free words** below $4000. Disabling `VADRUM` after that surgery removes another **102 words net** from scattered control branches (source flag alternatives, not a single contiguous hole): total deletion **1,177**, theoretical core-0=15,188, free **1,196 words**. **STRONG INFERENCE:** the latter is the appropriate conditional budget when deleting VA-drum too. **UNKNOWN:** linked/functional preservation after deletion. The scripts do not output the modified machine-code array, an ARM image, or a firmware container.

This budget precedes replacement renderer, converter, init/reset, model dispatcher, wrapper, trampolines and relocation glue. The prior 523P VariableSaw +301P fixture adapter totals824 words: would leave **270** words from the oscillator-only 1094 budget, or **372** from the1177-deletion1196 budget, before new/full-Voice work. **STRONG INFERENCE:** a full 24-model set needs radical code/table placement work beyond this primitive. These are arithmetic margins for that fixture’s short-address code sizes, not a qualified deployable linker result.

Do not count all 2,737 MIDI-module words as free: that would remove line filtering, granular gain/envelope/FX, return routing, mailbox and strip/feedback behavior. Do not delete Master FX `[2ACE,2C54)` =390P, source-selection `[2C54,2D59)` =261P, drums `[2D80,336E)` =1518P, sampler/tail `[3E1F,3FED)` =462P, or core-1 granular/glitch `[016C,07FF)` =1683P. The drums interval includes shared tables TATK/TDEC/TLFO/TF. Stock core-0 below2A5E and its source/stock hooks remain as in B1.3. P9B9/9D9 are not part of the selected MIDI seam. [tools/drums2_dsp.py — def code (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/drums2_dsp.py:70`; not distributed); tools/masterfx_dsp.py — def code (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/masterfx_dsp.py:48`; not distributed); tools/sampler_dsp.py — smp_post (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/sampler_dsp.py:4`; not distributed); tools/granular_dsp.py — def core1_code (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/granular_dsp.py:110`; not distributed).

**PROVEN data coupling:** X OSC1 `3900,3960)` (2x48) and OSC2 `[3960,39C0)` (2x48) are also granular control storage. Core-0 snapshots all192 cells to shared SHA `[37400,374C0)`; core-1 reads original OSC2 parameter offsets96+ (size/fine/spray/window/etc), not just OSC1. VB `[3B80,3BE0)` and S2 `[3800,3840)` are granular/line/return filter/envelope histories; FX `[3840,38A0)` and Y comb `[3400,3600)`, chorus `[3600,3A00)` are shared with those modes. SAVX `[38C0,38E0)`, TCNT3BF0 and FBSAVE3BF1 remain live. **Zero whole X/Y ranges are certified reclaimable by the current engine deletion alone.** Individual oscillator-history slots may be reused after a field-level lifetime proof, but mailbox writes, granular snapshots and mode changes must be checked. [tools/granular_dsp.py — CPT_LIST (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/granular_dsp.py:495`; not distributed); tools/granular_dsp.py — def core1_code (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/granular_dsp.py:110`; not distributed); tools/vcf21_dsp.py — SAVX (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21_dsp.py:47`; not distributed).

**STRONG INFERENCE narrower private-state candidate:** after removing all oscillator control/render islands, OSC2 history `396A,3971)` for MIDI1 and `[399A,39A1)` for MIDI2 gives seven cells per track at old OSC2 offsets+10..+16. Existing mailbox writes target+0..+8, and granular consumes OSC2 snapshot offsets+0,+1,+2,+3,+6,+7; its whole-record snapshot copies these history cells but does not interpret them in the inspected core1 source. This is a better source-derived candidate than assuming an anonymous high-X hole. **UNKNOWN ownership certification:** boot/init, ARM mode changes, diagnostics and every retained store still require traced regression; these are candidates, not allocated safe records. A dedicated temporary/save buffer remains separately required. [tools/vcf21_dsp.py — OS2B0 = (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21_dsp.py:64`; not distributed); tools/granular_dsp.py — X("r6", 96) (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/granular_dsp.py:229`; not distributed).

Keep shared X `37000,37621)` granular/glitch controls/state/snapshots, external Y glitch `[340000,380000)`, capture/sample slot ranges beginningE80000 and sampler privateX beginning3D00. Source-derived free external ranges do not certify timing, precision or exclusivity for a new Plaits allocator. Core1 is also the stock gather server and has one free P word; it is not a free second Plaits processor. Granular/glitch retention prevents assuming core1 is available for compute offload. [tools/granular_dsp.py — GB = (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/granular_dsp.py:38`; not distributed); tools/sampler_dsp.py — HIGH_BASE (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/sampler_dsp.py:37`; not distributed).

**STRONG INFERENCE asset-loading constraint:** B1.3 image size435220 bytes leaves23532 bytes below the reference builder limit0x70000. The50,688-byte wave array alone exceeds that tail, so immutable assets need compression/reclaimed ARM space or pack/file-backed loading as well as DSP-memory placement. This subtraction is not a verified bootloader-capacity claim: `ct_fw.py` explicitly calls its maximum a physical limit, not a bootloader verification. tools/build_sc16.py — assert len(img) <= 0x70000 (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/build_sc16.py:429`; not distributed); tools/ct_fw.py — MAX_IMAGE_SIZE (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/ct_fw.py:23`; not distributed); firmware/b1.3/manifest.json — image_size (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/firmware/b1.3/manifest.json:4`; not distributed). Actual asset loader and ARM code reclamation are UNKNOWN.

## F/G — performance model and two-track architecture

**PROVEN calibration only:** one sealed VariableSaw primitive integrated into actual DSP vpre yielded4039 exact rendered blocks,129248 samples, seven-state equality, per-block canaries, caller preservation and MIDI2 regression. Full fixture vpre+strip mixer: baseline max7458 instructions/11560 nominal cycles; replacement max13040/21235. Paired worst delta5584 instructions/9707 nominal cycles per32. Per-sample amortized worst delta174.5 instructions/303.34375 nominal cycles. Baseline mean7363.5815/11343.2029 perblock (230.1119 instructions/354.4751 cycles per sample); replacement mean10214.5181/17022.5168 (319.2037/531.9537 per sample). Maximum totals and maximum delta occur on different blocks; do not subtract unrelated maxima. Nominal calcCycles excludes pipeline interlocks, external waits, interrupts and concurrency. Standalone13379 upper uses a different conservative model. Neither number is full-VA or full-Voice WCET.

**UNKNOWN for all complete engines:** emitted DSP instructions/sample, cycles/sample, instructions/32, cycles/32, worst observed/derived block and wrapper overhead. No full engine has a faithful DSP56300 implementation here; the host engine graphs are executable source models, not target implementations. Structural primitive counts above identify where to implement/calibrate costs without inventing instruction-to-cycle conversions. A conservative numeric upper cannot be derived from float C++ source alone without defined fixed-point formats, rounding/range helpers, branching, table residency, memory waits and register scheduling. The table deliberately leaves costs null. Phase F’s requested complete numeric performance campaign is therefore **unresolved**, not passed off as a completed port.

A target cost model must be `C_engine = C_control + sum(N_primitive * C_primitive) + C_memory + C_spills + C_events`; issued-instruction count is a separate sum. Sample/32 figures follow only once every primitive and event path has qualified counts. Wrapper work includes trigger/model quantization, note/modulation envelope control, two LPG/limiter/postprocess paths and bank/Reset switching. Normal render and maximum switch/reset must have separate budgets: 1024-frame speech decode, 32 FM-patch unpack and 8192 diffuser clear cannot be hidden inside steady sample cost. Event work must be chunked/prepared or bounded at the audio deadline while preserving original transition semantics.

**PROVEN structural worst-work candidates, UNKNOWN cycle ranking:** 6-op two internal voices, FM4x, additive36 harmonics, modal24 modes, five-voice chord, four-voice string-machine and eight-voice swarm, noise per-sample coefficient math, and speech branch/decode costs. Wavetable/particles/string dominate memory traffic. A complexity ranking is not measured CPU ranking. Per-engine formulas count original internal generators, not MIDI notes; reducing them would fail algorithmic equivalence.

**STRONG INFERENCE architecture:** both MIDI tracks use the same shared P entry with separate private records/control staging/history/arenas/RNG/FIFO, sequentially called from vpre. Keep the existing mailbox/ARM note path but replace its paraphonic oscillator assignment with an explicit last-note mono policy; preserve held-note/legato/retrigger semantics and original Plaits internal tails. MAIN/AUX postprocessors belong to each voice. One shared dedicated caller workspace is possible only with non-reentrancy and tested switch/error/IRQ contracts. Do not reuse synthetic P400/P800 overlays: the stock synths must remain. Actual X3E00/Y3E00 usability was proven only in the finite fixture, not boot/full-lifetime ownership.

**UNKNOWN dual realtime gate:** nominal whole-period163840 cycles at conditional246MHz/48046.875Hz is a prior model, not measured available headroom. Required inequality is `C_stock_synths+drums+MasterFX+retained_B13+new_mailboxes+Voice1+Voice2+waits/IRQs <= deadline`. No full stock workload trace or two worst-engine target trace exists. Doubling9707 is not a dual-Plaits estimate: it is one primitive’s observed replacement delta and includes some shared glue. Source rate2ms limits each track to at most500 mailbox words/sec; it cannot carry sample-rate FM. Automation can reuse latest-value coalescing, but TRIGGER edges require an event/counter scheme and engine+parameter updates need staging/atomic commit to avoid mixed model controls. tools/vcf21.py — def use_ratelimit (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21.py:272`; not distributed); tools/vcf21.py — c_vsend (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21.py:275`; not distributed).

**PROVEN source traffic derivation; STRONG INFERENCE risk:** naive external Wavetable rendering performs8 Hermite reads/frame x4 source elements =32 element reads/frame,1024/block/track,2048 for two. Retained reference maximum32 grains x32samples x2 interpolation reads =2048/block, plus glitch and stock gathers. A hypothetical extension running dual wavetable and both granular voices simultaneously would reach4096 explicit reads/block before additional work. **PROVEN architecture constraint:** the present B1.3 granular voice and Plaits replacement would be alternative source modes on the same MIDI strip; two Plaits modes do not also run two granular voices. The4096 sum is therefore a warning for a future concurrent design, not the current dual-Plaits workload. Glitch, capture, stock gathers and unrelated FX can still run concurrently and require their own accounting. Reference reports clean3584/clicking4096/slower higher-load diagnostic behavior; those are reported hardware read-load results, not a universal cycle conversion or a new test. Caching consecutive wave data could reduce traffic; it must be modeled/implemented. docs/NOTAS.md — Umbral al oído (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md:1335`; not distributed); plaits/dsp/engine/wavetable_engine.cc — float x0y0z0 (local-only reference: `plaits/upstream/plaits/dsp/engine/wavetable_engine.cc:191`; not distributed).

## H — MAIN/AUX and stock mixing

| Option | Consequence |
|---|---|
| MAIN only | Preserves MAIN graph, loses AUX sounds; is an explicitly reduced output contract |
| MAIN+AUX sum | Changes sound/amplitude, can cancel/add or clip, especially redundant FM outputs; not original output semantics |
| MAIN/AUX selectable | Preserves the selected graph and leaves the existing per-track strip intact; render both if state/side effects require it; best minimal stock-mixing option |
| Separate internal paths | Best two-output semantics, but both input-ring lanes already host MIDI1/MIDI2; four independent stems need new routing/mixer/FX design. No safe spare stock path established |

**PROVEN:** B1.3 ring Y:RING_PTR[$FFD] is interleaved input1/input2; vpre writes one mono32 source per track and stock strip gain/pan/send processing follows. **STRONG INFERENCE:** use MAIN/AUX selectable as the minimal preserved-mixer contract, labelled as one selected output rather than full two-jack Plaits. A sum does not preserve the original relationship. Dropping AUX computation is permissible only after per-model dataflow/history proof; FM AUX carrier/sub feedback, shared scratch and grain/noise RNG may affect future MAIN. Both six-op outputs are identical, but that exception does not generalize.

## I — minimal controls and storage

**STRONG INFERENCE proposed mapping; not implemented:** retain existing B1.3 MIDI pages, shifted knobs, automation lanes and patch framework. Primary K1 MODEL (24 slots, quantized/hysteretic), K2 HARMONICS, K3 TIMBRE, K4 MORPH. Shift layer: pitch transpose, fine tune, LEVEL/accent, MAIN/AUX selector. Modulation page: FM amount, TIMBRE amount, MORPH amount, LPG colour; shift: modulation-source values and enabled/patched flags. Envelope/event page: decay, trigger mode/legato/retrigger, level-source mode, engine-CV or reserved. Granular remains an alternative MIDI-track source mode with its own original pages/parameter meanings; independently operating capture/glitch remain on their existing paths. Both MIDI tracks cannot simultaneously output Plaits and their granular source through the same two ring lanes without a new mixer/routing design. MIDI note supplies pitch; velocity maps LEVEL/accent only when its patched flag is selected. Source control resolution is7-bit for knobs; mapping24 models over128 values is sufficient, but resolution differs from original continuous knobs/CV. Bipolar amounts need signed decoding; do not silently repurpose TYPEZONE/MIX values while granular mode is active.

**PROVEN reuse basis:** ARM hooks `c_vnon/c_vnoff`, `c_vnote_on/off`, `c_vsend/c_vtick`, priority and dirty flags already transport note/velocity/gate/TRIG plus parameters. tools/vcf21.py — c_vnote_on (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21.py:1285`; not distributed); tools/vcf21.py — c_vsend (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21.py:275`; not distributed). The2ms coalescing schedule permits control-rate updates; it does not reproduce original external audio-rate FM/CV, nor prove simultaneous-event delivery. Preserve critical edge events ahead of coalesced knobs; model switch must snapshot controls coherently. The previous protocol test executed DSP decoder only; actual ARM service/UI execution remains UNKNOWN.

**PROVEN storage format:** tools/mpatch.py — What a patch holds (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/mpatch.py:15`; not distributed) defines a42-byte CTM1 record:26+8 parameter bytes, flags, step-drummer metadata, checksum/version;64 shared slots reside in172-byte padding after340 stock bytes in512-byte records. **STRONG INFERENCE:** 34 parameter bytes can carry the proposed control surface without removing stock fields, but requires a new version/tag or unambiguous engine mode and backwards compatible loader; framework capacity is not already Plaits storage. Preserve granular records/pages separately by mode. Automation has8 lanes, fewer than all Plaits parameters, so selectable lane assignments must remain explicit. tools/persist19.py — N_XM = (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/persist19.py:47`; not distributed) and tools/fxsess.py — MFX1 (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/fxsess.py:5`; not distributed) keep project/session infrastructure; do not reclaim it or the LED/session scratch based on an old comment. User-loaded FM/wavetable/terrain blobs require separate data storage/import/versioning not contained in42 bytes.

## J/K — fidelity and final gates

| Fidelity | Current evidence |
|---|---|
| BIT-EXACT | Phase20D VariableSaw target vs its sealed independent **integer** oracle, only for declared domain. Not original ARM float equality or full VA |
| NUMERICALLY EQUIVALENT | Not established for any complete DSP engine/wrapper; requires defined error bounds, behavior boundaries and sample/state comparisons |
| ALGORITHMICALLY EQUIVALENT | Intended target preserving algorithm graphs, internal generators, resources, parameter behavior and tails; not yet implemented |
| PERCEPTUALLY EQUIVALENT | No listening/perceptual qualification; do not use it as a substitute for numeric validation |
| NOT YET PORTED | All22 complete engine classes, full Voice/LPG/modulation, MAIN/AUX routing, switching and dual architecture |

**PROVEN representation difference / STRONG INFERENCE fidelity limit:** DSP56300 fixed-point output/state is not IEEE float bit-exactness; original MAIN/AUX also deliberately clips to signed16 and flips polarity. Float emulation could reproduce defined operations at greater code/cycle/state cost but has not been built. Retiming rate/block, transport latency/coalescing,7-bit controls, missing audio-rate CV, one selected output, custom-data limitations and truncating internal tails prevent an unqualified “1:1” claim. Intentional module ADC/UI omission is a platform substitution, not a missing synthesis engine.

| Gate | Answer | Confidence and reason |
|---|---|---|
| F1 complete engine set in P | Not demonstrated; all-resources-in-P impossible | PROVEN wave data exceeds total P; UNKNOWN shared executable size after externalizing resources; only1196 conditional replacement words |
| F2 two states safely in private data RAM | Not demonstrated | PROVEN only seven words/private-X in prior fixture; STRONG INFERENCE full natural histories exceed the small retained-mod tail; UNKNOWN final packed/external layout ownership |
| F3 simultaneous worst engines deadline | Not demonstrated | UNKNOWN target engine/wrapper costs, full-stock load, waits and dual scheduling |
| F4 stock Synth1/Synth2 unchanged | Architecturally possible | STRONG INFERENCE MIDI seam/deletion touches no stock generator; previous P overlays cannot be retained; UNKNOWN whole-program regression |
| F5 rest of B1.3 intact | Conditional, unproven | PROVEN substantial granular/VCF/FX/state coupling; keep those shared sections; UNKNOWN relocation/full regression |
| F6 ARM/UI/mailbox reuse | Yes as architecture | PROVEN existing contracts/protocol fixture; STRONG INFERENCE new mapping/staging/versioned storage can reuse them; UNKNOWN implemented ARM path |
| F7 faithful unavailable features | Full engines/wrapper, dual worst timing, original audio-rate CV, complete independent MAIN/AUX routing, custom data imports | NOT YET PORTED/UNKNOWN; fixed integer primitive is a subset |
| F8 verdict | **NOT CURRENTLY FEASIBLE** | Qualification verdict: no complete target build/size/state/timing/preservation proof. Does not prove future impossibility or justify engine exclusions without further evidence |

## Final engine table and totals

State column is **host object bytes + logical 32-capacity arena cells**, not a measured DSP layout. Complete DSP P cost and worst modeled cycles are UNKNOWN. Arena is per active engine and shared within one track; do not sum24 slots or double-count six-op classes/banks. A dedicated caller workspace, wrapper and buffers remain additional. Every row’s fidelity is NOT YET PORTED at complete-engine scope.

| Engine | Fidelity | P cost | State cost (object B + arena cells) | Worst cycles/32 | Status |
|---|---|---|---:|---|---|
| 00 VA + VCF | NOT YET PORTED | UNKNOWN | 168 B + 0 | UNKNOWN | YELLOW; source/allocator audited |
| 01 Phase distortion | NOT YET PORTED | UNKNOWN | 112 B + 128 | UNKNOWN | YELLOW; source/allocator audited |
| 02 6-op FM bank 1 | NOT YET PORTED | UNKNOWN | 5,904 B + 5,184 | UNKNOWN | RED; source/allocator audited |
| 03 6-op FM bank 2 | NOT YET PORTED | UNKNOWN | 5,904 B + 5,184 | UNKNOWN | RED; source/allocator audited |
| 04 6-op FM bank 3 | NOT YET PORTED | UNKNOWN | 5,904 B + 5,184 | UNKNOWN | RED; source/allocator audited |
| 05 Wave terrain | NOT YET PORTED | UNKNOWN | 64 B + 128 | UNKNOWN | RED; source/allocator audited |
| 06 String machine | NOT YET PORTED | UNKNOWN | 304 B + 1,083 | UNKNOWN | YELLOW; source/allocator audited |
| 07 Chiptune | NOT YET PORTED | UNKNOWN | 272 B + 59 | UNKNOWN | GREEN; source/allocator audited |
| 08 Virtual analog | NOT YET PORTED | UNKNOWN | 192 B + 32 | UNKNOWN | YELLOW; source/allocator audited |
| 09 Waveshaping | NOT YET PORTED | UNKNOWN | 96 B + 0 | UNKNOWN | YELLOW; source/allocator audited |
| 10 2-op FM | NOT YET PORTED | UNKNOWN | 64 B + 0 | UNKNOWN | YELLOW; source/allocator audited |
| 11 Granular formant | NOT YET PORTED | UNKNOWN | 144 B + 0 | UNKNOWN | YELLOW; source/allocator audited |
| 12 Additive | NOT YET PORTED | UNKNOWN | 200 B + 36 | UNKNOWN | YELLOW; source/allocator audited |
| 13 Wavetable | NOT YET PORTED | UNKNOWN | 88 B + 256 | UNKNOWN | RED; source/allocator audited |
| 14 Chord | NOT YET PORTED | UNKNOWN | 384 B + 59 | UNKNOWN | YELLOW; source/allocator audited |
| 15 Speech | NOT YET PORTED | UNKNOWN | 480 B + 12,384 | UNKNOWN | RED; source/allocator audited |
| 16 Swarm | NOT YET PORTED | UNKNOWN | 32 B + 128 | UNKNOWN | YELLOW; source/allocator audited |
| 17 Filtered noise | NOT YET PORTED | UNKNOWN | 144 B + 32 | UNKNOWN | YELLOW; source/allocator audited |
| 18 Particles | NOT YET PORTED | UNKNOWN | 248 B + 8,192 | UNKNOWN | RED; source/allocator audited |
| 19 Strings | NOT YET PORTED | UNKNOWN | 432 B + 3,888 | UNKNOWN | RED; source/allocator audited |
| 20 Modal resonator | NOT YET PORTED | UNKNOWN | 344 B + 32 | UNKNOWN | YELLOW; source/allocator audited |
| 21 Bass drum | NOT YET PORTED | UNKNOWN | 192 B + 0 | UNKNOWN | YELLOW; source/allocator audited |
| 22 Snare drum | NOT YET PORTED | UNKNOWN | 304 B + 0 | UNKNOWN | YELLOW; source/allocator audited |
| 23 Hi-hat | NOT YET PORTED | UNKNOWN | 336 B + 64 | UNKNOWN | YELLOW; source/allocator audited |

1. **Total shared Plaits executable P: UNKNOWN.** Resources contain41686 elements in resources.cc alone; do not store all in P. Shared wave data25344 signed16 values; float LUT2129 values; three default FM banks12288 bytes; additional speech/pitch/FM constants as above. Code/tables shared once, histories independent.
2. **Per-track X/Y:** final split/addresses UNKNOWN. Planning proxy~2766 object cells plus natural peak12384 arena cells, plus dedicated save/output/FIFO. Packing/sharing reduces this; precision can increase it.
3. **Two tracks:** planning proxy~30300 object+arena cells before save/output/FIFO; immutable assets shared, peak arenas separate. Two particle histories16384 cells; two string histories7776; two natural speech arenas24768. These are alternative active-engine footprints, not additive per-track requirements.
4. **B1.3 P reclaimed:** PROVEN assembler shrink1075 oscillator islands; another102 net VA-control =1177 conditional words. Retained VCF/VCA/FX/line/gran infrastructure yields1196 freeP including old19. No whole X/Y allocation is newly certified.
5. **Remaining P margin:** `1196 - P_shared_renderers - P_tables_in_P - P_wrapper/adapter/relocation`; UNKNOWN. Prior824P primitive fixture would leave372 conditionally, before full-Voice changes.
6. **Worst simultaneous timing:** UNKNOWN; neither host timings nor twiceVariableSawdelta is an answer.
7. **Memory dominators:** wavetable immutable assets; particle diffuser; speech decoded frames; three-string histories; six-op cached patches and dispatch/object metadata.
8. **CPU dominators:** candidate6-op/FM4x/additive/modal/noise/speech/chord/swarm; measured ranking UNKNOWN. Memory-bound candidateswavetable/particle/string.
9. **Exact blockers:** emitted shared code size; qualified live X/Y/external ownership; complete fixed-point ranges/helpers/phase/RNG; rate/cadence and event/switch semantics; full-Voice envelope/LPG; mailbox atomicity and edge retention; large-data bandwidth/precision; simultaneous worst models with complete retained workload; whole-feature regression; MAIN/AUX and custom-data contract.
10. **Single best next offline experiment:** implement and qualify the complete pinned `VirtualAnalogEngine` VA_VARIANT=2 plus Voice modulation/LPG for **one MIDI track**, using an explicit1196-word conditional P budget and retaining the other track as reference control. Share/test VariableShape and sealed VariableSaw arithmetic, preserve both output graphs, account all wrapper/switch costs, use private records and dedicated buffers/canaries, and compare samples/state to an independent bounded fixed-point oracle and pinned float reference. First rebuild/execute the stripped reference module in an offline fixture with oscillator/line/granular/FX-return regression. No stock P overlays or firmware container. Failure to fit/time that complete first model is actionable before attempting full24-model or dual worst-engine work.
