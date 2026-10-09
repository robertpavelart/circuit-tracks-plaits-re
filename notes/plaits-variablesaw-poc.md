# Phase 20A — standalone DSP56300 VariableSaw proof of concept

## Phase 20A-DIV update — preferred standalone variant (2026-10-06)

**IMPLEMENTED / TESTED / MEASURED:** nativeDIV replaces only the ratio helper
in a separate standalone variant; restoring source/evidence remain unchanged.
700P,7 persistent,44 allocated scratch,32 output,0LUT; issued mean5138.4363
(43.2442% lower). Same43-case suite passes twice, exact old/oracle samples and
seven-word block states. Pitch/reference/continuity metrics are unchanged.
Report:[plaits-native-div.md](plaits-native-div.md); canonical evidence under
builds/phase20a-div/final-compact/, fixtures-compact/, checks/, comparison/.
Circuit integration/ownership/timing remain **UNRESOLVED**. Historical baseline
report below retains its original708P/restoring measurements.

2026-10-06. **IMPLEMENTED / TESTED / MEASURED:** a complete table-free,
fixed-point VariableSaw-derived oscillator executes in the existing isolated
DSP56300 interpreter, producing exactly32 mono samples per call. All Phase20A
success gates A–K pass within the exported test scope. This is standalone
implementation-study success, **not firmware integration readiness**.

Seven persistent X words,44 scratch X words,32 output Y words, zero immutable
tables,708 assembled P words. Across7520 blocks, issued cost is7632..16844
opcodes/call (mean9053.5811). Both complete native traces/outputs repeat exactly;
all240640 samples and all case-final state words equal an independent integer
oracle. Reference is the unchanged pinned upstream float class.

No Circuit image, hardware, MIDI/SysEx, flashing, firmware patch/injection,
original/ modification, stock state or X[5F00,6000) reservation. RAM-ownership
work stays frozen. No full Plaits Voice, model dispatcher, multivoice architecture,
stock filter/effect/envelope or eight-knob adapter was implemented.

## A. Exact source subset and provenance

Pinned official eurorack08460a69a7e1f7a81c5a2abcc7189c9a6b7208d4;
stmlib e3bd7c9cc00e4364166f9905c0509b6ffd0535ec. Existing183-file snapshot
and every recorded SHA256 were rechecked; nothing refetched or altered.
MIT authorship/notices remain in the original headers. New derived code identifies
Mutable Instruments/Emilie Gillet as its source.

**SOURCE-DERIVED include closure**, exactly six local headers:

| Header | Required definition/use |
|---|---|
|plaits/dsp/oscillator/variable_saw_oscillator.h|VariableSawOscillator.Init/Render/ComputeNaiveSample; notch depth.2|
|plaits/dsp/oscillator/oscillator.h|kMaxFrequency=.25; unrelated Oscillator class not instantiated|
|stmlib/dsp/parameter_interpolator.h|Three linear control interpolators; Next/destructor state update|
|stmlib/dsp/polyblep.h|This/Next stepBLEP and This/Next integratedBLEP polynomials|
|stmlib/dsp/dsp.h|Utility include, CONSTRAIN via stmlib; no LUT interpolator used by this primitive|
|stmlib/stmlib.h|Integer/size types, CONSTRAIN and copy-control macros|

System includes are algorithm,cmath/math.h,inttypes.h,stddef.h. Oscillator hot
path is float32, arithmetic/reciprocal/parameter interpolation and polynomial
correction; no RNG, wavetable, table interpolation, pitch LUT, allocator or
Voice dependency. Caller supplies normalized frequency; Hz/MIDI conversion is
explicitly outside the primitive. `dependencies.json` supplies hashes/functions.

`plaits/poc/reference.cpp` includes and calls the unmodified class. Upstream's
existing TEST portability branch permits host compilation; no replacement
oscillator function or source edit is used. Host sizeof is measured28 bytes.

## B–C. Architecture and API

Implementation files under plaits/poc:

- generate.py expands a small explicit arithmetic/control description into
  assembly text; existing assembler emits every machine word.
- runner.cpp uses sealed Phase19A forced interpreter and authoritative hooks,
  denies peripheral/P writes and validates32 ordered output writes/stack restore.
- fixed_model.py is an independent integer oracle, not a substituted DSP renderer.
- reference.cpp wraps the pinned class; collect.py generates controls, executes
  both paths twice and exports comparisons; CMakeLists.txt/build.ps1 use existing
  local MSVC/CMake/Ninja and sealed libraries. No tool installed.
- emulator/tests/verify_variablesaw.py checks traces, opcodes, metrics, guards,
  source integrity, resource gates and refusal paths.

Conceptual public API:

```
render32(pitch_Hz, primary_shape_0_to_1, pulse_width_0_to_1,
         sample_rate, retained_state, output[32])
```

The host control adapter converts Hz/rate to rounded Q2.22; native DSP entry
takes three integer target words (normalized frequency,PW,shape), clamps and
interpolates them, and renders32 samples. This caller-side frequency conversion
is included in the documented contract, not claimed as zero-cost DSP MIDI math.
Output words are signed Q3.21, exported as sign-extended int32 raw vectors.
State persists in owned standalone memory; the output buffer is reused each call.

Phase/frequency/PW use Q2.22 for[0,1.25) phase headroom; audio/shape/corrections
Q3.21 for[−4,4). Three exact32-step integer ramps distribute remainders to reach
target values. Signed24×24 operations use56-bit accumulators; exact ratios use
a26-P-word21-bit restoring helper. Source event order, next-sample delay, notch
BLEP and triangle integratedBLEP are retained. See plaits-fixed-point.md for
all domains, rounding/overflow and division comparisons.

PoC control mapping is intentionally primitive-specific: pitch; an independent
shape control may serve as TIMBRE-like primary, PW as meaningful MORPH-like
secondary. HARMONICS has no role for this one oscillator. This is not a claim
to reproduce VirtualAnalogEngine's full macro mapping: its auxiliary detuning,
multiple oscillators and coupled MORPH shape/PW laws remain excluded.

## D–H. Actual resource contract

| Resource | MEASURED |
|---|---:|
|Retained mutable oscillator state|7 X words,0 Y|
|Control input frame|3 X words|
|Transient scratch|44 X words|
|Mono output|32 Y words|
|Logical data total including controls/output|86 words|
|Immutable tables|0 words|
|Program|708 P words (2124 bytes)|
|Divider, included above|26 P words|
|Hardware stack peak|5 entries /10 words|
|Issued opcodes per32 call|min7632,max16844,mean9053.5811|

The state gate is<=64 words; the full working footprint is not seven words.
Constants reside in already-counted P instructions. A separate measured65-word
reciprocal candidate table/math experiment is exported but unused. Native DIV
and LUT/Newton replacements need further standalone qualification.
No extra synthesis LUT placement is needed; future shareable code/table placement
and stock memory/ABI remain unqualified. Actual hardware cycles/headroom are
UNRESOLVED; a one-cycle/opcode model is only an optimistic estimate.

## I–L. Differential, continuity, pitch and determinism

**TESTED:**43 deterministic cases,7520 calls/240640 samples per full run.
Includes low/mid/high pitches, shape/PW extremes and midpoint; two separate
sample rates; joint control sweep; abrupt seeded stress; max-frequency clamp;
2048 continuous32-sample calls (65536 samples) without reinitializing state.

Two upstream runs are byte-identical. Eight native output files repeat
byte-identically, including full136,165,860-byte issued-PC trace, samples,
states, program words and block write hashes. Native output matches the integer
oracle exactly for every sample/all seven case-final state words. Original
host steady Render64 vs twoRender32 comparison also has maximum difference0.
Exact phase advances plus wrap counts and preserved delayed sample establish
block continuity. Large jumps at block boundaries can be real waveform events;
they are not automatically classified as resets.

**MEASURED raw numerical differences from float source:**

| Metric | Measured suite result |
|---|---:|
|Worst per-case RMS difference|.02197305, MIDI0 at48kHz|
|Long440Hz sequence RMS|.02131893|
|Abrupt stress RMS|.01756724|
|Joint sweep RMS|.00432103|
|Maximum absolute DC difference|.00033769|
|Maximum peak-amplitude difference|.00093019|
|Minimum constant-case magnitude-spectrum cosine similarity|.99994396|
|Maximum single-sample difference|1.41453290 in abrupt stress|

These are unaligned raw comparisons; no frequency/time warping hides phase
quantization. A sharp notch moving a few samples can give a large pointwise
error even with similar pitch/spectrum/DC/peak. Subjective sound equivalence was
not asserted from metrics or automatic playback. Prototype limits (RMS.025,
DC.001,peak.002,pitch1.1cents over the tested set) passed; they are study criteria,
not general perceptual/universal guarantees.

Frequency is measured from DSP phase differences plus actual wrap-event PCs,
not coarse FFT-bin estimates. At48kHz MIDI0 error−.999197cents,21+.009606,
69+.009606,120−.000245. At conditional48046.875Hz MIDI0+.690636,21+.257945,
69−.012468,120−.000919. Maximum absolute tested error.999197cents.
Retuning48kHz increments to that conditional rate requires **1024/1025** before
quantization; unretuned drift+1.689833cents. The MI47872.34Hz pitch converter
is not linked; its source-derived+6.300328cent comparison is separate.

The sweep/abrupt stress/native cap cases have no observed output blow-up,
bad ratio, narrowing saturation, invalid memory/peripheral access or phase-wrap
failure. Guard refusal of zero frequency occurs before any oscillator opcode.
This is bounded test coverage, not a proof for every invalid/future input.

## M–P. Feasibility consequence and next step

**MEASURED:**<=64 retained words is realistic for this primitive (seven), as
are<=128/256, independently of44 scratch and32 output words. This supersedes
illustrative per-scalar state estimates for this standalone representation only.

**IMPLEMENTED / TESTED:** this primitive is practical as an offline DSP56300
oscillator. **UNRESOLVED / conditional for Circuit:** actual free state/code
placement, inherited ABI, output scaling, original processing around P9DD,
timing, scheduling and future multiple-voice budget remain unproved/frozen.
Nothing here reserves X[5F00,6000), closes P204B or authorizes a firmware patch.

**Biggest technical risk:** compute cost. Table-free restoring division is small
in code/state but expensive in issued instructions; real memory/cycle costs
would increase an optimistic opcode budget. Source/fixed phase quantization
and future audio-scale adapter are separate fidelity/ABI issues.

**Single best next step:** qualify a native DSP56300 DIV-based ratio helper in
this isolated harness, then replace only the restoring divider and rerun the
same numerical/resource/determinism suite. This is a bounded standalone
optimization proposal, not automatic Phase20B work or firmware integration.

## Artifacts, verification and reproduction

Canonical builds/phase20a-plaits/final/ exports reference-first/repeat.f32,
oracle.i32,DSP output.i32/states.csv, complete execution-pc.u16, immutable
program.be24/asm/labels, comparison-metrics.csv/metrics.json,
pitch-accuracy.csv,instruction-counts.csv,resource-manifest.json,
dependencies.json, division/rate/provenance reports and six paired offline WAVs.
Long midshape audio pair:audio/39-reference.wav andaudio/39-DSP.wav.
WAVs use the same.75 playback gain; unscaled vectors remain unchanged.

checks/verification.json records A–K gatesPASS, full trace/opcode/spectral tests,
three overwrite refusals and zero-frequency refusal. Original SYX/BIN hashes,
in-memory roundtrip/all10 DSP extracts,183 upstream source hashes and sealed
core/harness/previous helper source guards pass. No core modification or Circuit
execution. Failed build/probe iterations are retained as intermediates, not
promoted to validated oscillator results.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& ./plaits/poc/build.ps1 -BuildDir builds/phase20a-plaits/new-core
& $py -B plaits/poc/collect.py --build-dir builds/phase20a-plaits/new-core --output-dir builds/phase20a-plaits/new-suite
& $py -B emulator/tests/verify_variablesaw.py --build-dir builds/phase20a-plaits/new-core --suite-dir builds/phase20a-plaits/new-suite --output-dir builds/phase20a-plaits/new-checks
```

Existing bundled Python/numpy and installed MSVC/CMake/Ninja only. Fresh output
paths mandatory. Each suite automatically runs every reference/DSP case twice.
The native wrapper links the exact existing MDd/iterator ABI of sealed19A;
wall-clock host speed is not reported as target timing.
