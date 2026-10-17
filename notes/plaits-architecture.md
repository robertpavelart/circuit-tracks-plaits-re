> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 7 — official Plaits architecture, static comparison

2026-10-05. FEASIBILITY STUDY ONLY. No Circuit hardware, MIDI/SysEx, firmware
execution/patching, stock-artifact edits, DSP port, compilation, linking or injection.
SOURCE-DERIVED means inspected code; ESTIMATE is not emitted size or timing.

## Source identity and scope

Official [Mutable Instruments eurorack source](https://github.com/pichenettes/eurorack)
at commit **08460a69a7e1f7a81c5a2abcc7189c9a6b7208d4**. Shared official
[stmlib](https://github.com/pichenettes/stmlib) submodule is pinned by that
commit to **e3bd7c9cc00e4364166f9905c0509b6ffd0535ec**. No fork was used.
The source snapshot is `plaits/upstream/`, with Git-blob/SHA256 provenance in
`source-manifest.json`:183 files,1,241,908 bytes. CAD, binary firmware and large
vendor tool/library trees are excluded; no toolchain is installed.

Plaits and the selected stmlib code carry MIT notices, retained verbatim in
their source files. Repository README distinguishes STM32 MIT code from AVR
GPL code and CC-BY-SA hardware. The copied scope is the Plaits STM32 source
and shared DSP/utility text, not permission to relabel all repository assets.

`tools/ct_plaits_fetch.py` fetches a pinned snapshot and checks Git blob hashes;
`tools/ct_plaits_audit.py` checks every copied file and exports dependencies,
tables, fields, allocator sites and rate/block references. No source was edited.
Hardware dependency `stmlib/system/flash_programming.h` is deliberately outside
the copied DSP/utility subset: full Voice's `UserData` path is module-specific;
the selected engine/oscillator dependency closures have no missing quoted includes.
This snapshot is an analysis corpus, not a complete build checkout.

## Actual full call path

SOURCE-DERIVED from `plaits/plaits.cc`, `dsp/voice.{h,cc}`, `engine/engine.h`:

```text
hardware FillBuffer / CV and Patch preparation
  → Voice::Render(Patch, Modulations, Voice::Frame*, size)
  → delayed trigger/hysteresis, DecayEnvelope/LPGEnvelope, EngineRegistry selection
  → EngineParameters: trigger, note, timbre, morph, harmonics, accent
  → Engine::Render(..., float* out, float* aux, size, bool* already_enveloped)
  → ChannelPostProcessor: gain, optional limiter/LPG
  → clipped interleaved signed-short OUT/AUX frames
```

`Patch` contains9 floats plus engine integer: raw field payload40 bytes under
32-bit float/int assumptions. `Modulations` has8 floats and5 booleans:37-byte
payload, with padding/ABI not included. `EngineParameters` has5 floats plus
trigger integer:24-byte payload. These are source accounting, not DSP layout.
`NoteToFrequency` converts MIDI-style semitones into cycles/sample; it is not
an Hz-returning helper. At note69 it yields440/kCorrectedSampleRate.

`Voice::Init` registers24 model slots using22 engine object members; the
same SixOpEngine instance is registered three times. EngineRegistry holds24
pointers. Every engine object remains embedded in Voice; the objects are not
a union. `allocator->Free()` before each engine Init overlays allocated working
arenas, making pool requirement a peak rather than a sum. Reset on switching
models is part of this sharing contract. The original module provides a16384-
byte arena; it must not be multiplied by24 models or treated as24 separate pools.

## Minimum conceptual generator path

For one monophonic generator, a full Voice is not necessary:

```text
validated pitch/frequency + bounded shape controls
  → one selected oscillator/engine's Init and retained state
  → Render(float buffers, positive size)
  → conceptual numeric/range adapter (UNRESOLVED)
  → 32 mono DSP words at X:[2C46,2C66)
  → preserve readable/stock-neighbor X:2C66
  → stock P:9DD post/filter/gain/mix
```

This is a data-contract study, not implemented dispatcher/adapter code.
Stock gate/envelope/lifecycle/coefficient and scheduler work must remain valid.
Omitting Plaits' LPG/limiter and module postprocessing changes module behavior
but is appropriate to investigate a raw generator seam. It does not establish
that stock postprocessing can accept an assumed normalized amplitude.

Smallest useful source subset: `VariableSawOscillator` from the active
`VirtualAnalogEngine` OUT path, plus `ParameterInterpolator`, polynomial BLEP
helpers, limits and bounded controls. It has six float state fields and one
boolean. It needs no allocator, random generator, filter or waveform LUT.
Pitch conversion needs stmlib's two pitch-ratio arrays unless an independently
validated Circuit normalized frequency is supplied. Omitting those tables is
a HYPOTHESIS about control reuse, not a verified numeric compatibility claim.

## Essential versus optional components

| Classification | Actual source/components |
|---|---|
| REQUIRED FOR ANY derived voice | Retained oscillator state; positive-size rendering; defined frequency/controls; appropriate numeric helpers; output/control contract |
| REQUIRED for Engine API | EngineParameters and engine Init/Render; declared dependencies. Virtual dispatch/EngineRegistry are unnecessary for one fixed model |
| REQUIRED ONLY for specific engines | Sine/FM quantizer/FIR tables; wavefolding LUTs; delay lines, resonators, chord banks, speech frames, RNG or oversampling where used |
| UI/MODULATION CONVENIENCE | Patch/Modulations routing, attenuverter curves, engine quantizer, input-patched flags, trigger delay, internal control envelope |
| STM32/HARDWARE-SPECIFIC | plaits.cc main/drivers, ADC/DAC/DMA, UI/settings, bootloader, calibration, flash UserData and update receiver |
| NOT NEEDED at raw Circuit seam | Module signed16-bit Frame output, OUT/AUX interleave, module DAC polarity, full24-slot registry, unused AUX graph, Plaits LPG/limiter if deliberately retaining stock processing |

Full module fidelity would reintroduce some optional components. Patch/Voice
and bipolar AUX are not intrinsic requirements of a Plaits-derived oscillator.
Voice user-flash accesses and libm/ARM helpers cannot simply execute on DSP56300.

## Candidate engines ranked by architecture burden

1. **VirtualAnalogEngine-derived mono subset:** first VariableSawOscillator
   alone, then the full OUT graph (VariableShape sync + VariableSaw + two gain
   interpolators). Active VA_VARIANT=2 also computes two other oscillators for
   AUX; those AUX computations are overwritten in OUT before final OUT mixing.
   Theoretical OUT-only reduction therefore avoids them. Full original engine
   still has a24-float temp arena. No reduction was implemented.
2. **FMEngine, two-operator:** small scalar state, sine lookup/quantizer/FIR,
   but4× oversampling and32-bit phase handling increase compute/numeric risk.
   OUT-only could omit sub-phase/sub-FIR/AUX after dataflow verification; carrier
   feedback still requires its previous sample. This is not SixOpEngine.
3. **WaveshapingEngine:** small state and no allocator, but five int16 shapers,
   Hermite-interpolated fold tables and AUX sine dependency. OUT-only could omit
   triangle/sine/second folder, yet substantial shaper/folder data remains.

Poor first candidates: ParticleEngine's8192 uint16 diffuser words; StringEngine
delay histories/three strings; ModalEngine resonator bank; SpeechEngine datasets/
decoder/control; WavetableEngine's25344-element integrated-wave resource;
SixOpEngine's multi-voice FM/patch structures; WaveTerrain's table/work buffers;
ChiptuneEngine's chord/arpeggiator/polyphonic branch. NoiseEngine has modest
state but recomputes accurate SVF coefficients and inverse-root gain per sample,
plus RNG; small state is not proof of low compute cost.

## Block-size and timing semantics

SOURCE-DERIVED `dsp/dsp.h`: **kBlockSize=12**, **kMaxBlockSize=24**.
Original DAC initialization uses kBlockSize; Voice OUT/AUX arrays each hold24
floats. **Unmodified Voice::Render(size=32) is unsafe.** VA/Noise and other
engine arenas also use kMaxBlockSize. It is insufficient to resize just Voice.

VariableSaw, FMEngine and WaveshapingEngine use supplied size for loops and
parameter interpolation; the first has no size-bound arrays, and FM/Waveshaping
need only correctly sized caller buffers. These selected raw paths conceptually
support32. Full VA needs a larger temp allocation or split calls. Other models
use fixed buffers/subblocks: every selected closure must be checked separately.

Alternative full-Voice adaptation: retain12-sample renders and collect32 samples
with a FIFO. Over96 samples, eight12-sample renders feed three32-sample Circuit
periods; remainders cycle4/8/0. This requires scratch/history and a control-event
timing policy. Simply rendering12+12+8 each period changes Voice control cadence.
No buffer adapter was written.

Per block: Voice trigger delay/hysteresis, note smoothing, model selection,
internal envelopes, parameter targets. Per sample: phases, interpolation.Next,
BLEP/FIR/filter histories and sample output. Interpolator destructors commit the
last interpolated parameter, not merely the initially requested target.

Voice envelopes hardcode kBlockSize in decay/attack formulas rather than using
Render size. Five delayed trigger blocks nominally equal60 samples/1.25ms;
five32-sample blocks at conditional Circuit rate would be3.330ms. Raising array
limits alone would alter trigger delay, note smoothing and envelope time scales.

## Rate and numerical dependencies

SOURCE-DERIVED nominal **kSampleRate=48000**, corrected pitch-rate constant
**kCorrectedSampleRate=47872.34**, reflecting source's72MHz/47/32 hardware
divider comment. That is an upstream intended hardware correction, not a new
measurement. `a0=(440/8)/kCorrectedSampleRate`; NoteToFrequency subtracts9,
constrains −128..127 and multiplies a0*0.25*SemitonesToRatio.

Conditional Circuit48046.875Hz differs from nominal48k by0.09765625%; unchanged
corrected Plaits pitch normalization would be approximately **+6.300 cents**.
Neither rate similarity nor this calculation proves Circuit's physical rate.
Use the actual verified rate eventually; do not blindly transplant the divider
correction. Rate/block occurrences throughout copied source are exported in
`rate-block-references.csv`: envelope/decay, filters, physical delays, oscillator
frequency and model modulation rate assumptions remain distinct.
That text-reference inventory is not an exhaustive classification of implicit
rate dependencies: fixed per-sample coefficients such as FM's0.05 feedback
smoother, limiter attack/release and model recurrences also depend on cadence.
Full Voice trigger/envelope and every included model need separate retiming.

Most synthesis uses32-bit float, not fixed Q1.23. FM uses uint32 phase wrap;
resources mix float, int16, int8/uint8. Floating reciprocals, interpolation,
polynomial BLEP and libm/bit-cast helpers differ from DSP24 fractional MAC/MACR
and56-bit accumulators. Pitch-ratio tables exceed unity, so a single Q1.23
format is unsuitable for every variable/table. No fixed-point translations or
float emulation were designed. See the resource comparison for counts and risks.
