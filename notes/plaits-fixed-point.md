# Phase 20A — VariableSaw fixed-point contract

## Phase 20A-DIV update — exact contract retained (2026-10-06)

**SOURCE-DERIVED / IMPLEMENTED / TESTED:** the preferred standalone helper now
uses21 native DIV iterations plus A0->A1/ROL carry insertion, with integer-part
separation. It exactly preserves floor((n<<21)/d), including ratios up to4;
positive signed24 inputs, d>0, n<4d. Explicit d=0 guard returns0 outside the
valid ratio API. No rounding or oracle changes.37,016 isolated fixtures and
all43 unchanged oscillator cases pass; old/new samples and block states identical.
Full semantics, manual inconsistencies, recurrence proof and evidence:
[plaits-native-div.md](plaits-native-div.md). Restoring code below remains the
immutable baseline; its earlier future-DIV remarks are historical.

2026-10-06. **IMPLEMENTED / TESTED:** standalone DSP56300 assembler program and
independent integer oracle. No stock image, Circuit state/address allocation,
peripherals, firmware adapter, full Voice or hardware. Source is the pinned MIT
Mutable Instruments VariableSaw; the upstream files remain byte-identical.

## Source numeric behavior

**SOURCE-DERIVED:** phase, frequency, PW, waveshape, previous PW and next-sample
state are float32; high is bool. Init sets phase/next/shape0, previous PW/PW.5,
frequency.01, highfalse. Render accepts normalized cycles/sample, PW and shape.
It caps frequency at.25, forces PW.5 there, otherwise constrains target PW to
[2f,1−2f]. This primitive has no lower-frequency clamp in Render. The tested
API admits positive frequencies that quantize to at least one target quantum.
Controls PW/shape are bounded[0,1] by the standalone API.

Each of three ParameterInterpolator objects advances before generating a sample.
The source increment is float `(target−old)/size`, persisted by its destructor.
No uint32 phase, LUT index, RNG, allocator, pitch converter or full Voice is
required. Oscillator header dependencies declare other functions; those classes
are not instantiated by the reference wrapper.

Source reciprocal slopes are1/PW and1/(1−PW); event time divides by either
`previousPW−PW+frequency` or frequency. The naive triangle uses phase/PW or
1−(phase−PW)/(1−PW). A weighted naive notch/triangle feeds next-sample state;
output is `(2*this−1)/1.2`. The raw primitive can exceed unity: measured peak
1.16666675. Its output is not already a universally safe Q1.23 audio signal.

## Implemented representations

| Quantity | Representation / range | Reason |
|---|---|---|
|Phase|Signed24 Q2.22; tested0..1.25|Headroom preserves source's if/else-if event order and possible delayed wrap without a split phase word|
|Frequency|Q2.22 cycles/sample; positive quantum to.25 after cap|Same exact phase-add scale; precision measured across MIDI0..120|
|PW / previous PW|Q2.22|Same compare/event-time domain as phase and frequency|
|Shape/notch amount|Q3.21,0..1|Exact endpoints and room for subsequent products|
|Naive sample / next sample / corrections / output|Signed24 Q3.21, representable[−4,4)|Accommodates1.2 notch, negative corrections and transient headroom|
|Event t / triangle ratios|Q3.21|21 fractional bits and integer part; tested positive quotient domain<4|
|high|Raw24-bit0/1|Branch state; no fractional interpretation|
|Ramp steps|Signed24 in their parameter's scale|Floor division by32 plus remainder distribution|
|Ramp remainder/error|Raw0..31, transient|Exact target arrival after32 samples, no cumulative endpoint drift|
|Multiplication accumulator|DSP56-bit A|Signed24×24 fractional multiplication, followed by shift2 for Q3.21 products|
|Integer quotient accumulator|A remainder / B fraction|Exact restoring division with21 fractional iterations; DO loop state restored|

Q2.22 means one sign bit, one integer bit,22 fractional bits; Q3.21 means one
sign bit,two integer bits,21 fractional bits. Negative multiplications and shifts
round down through arithmetic truncation. The integer oracle uses the same
specified floor rule and matches every DSP sample/state bit in the measured suite.
Literal booleans/counts retain their distinct raw-integer semantics.

Phase adds frequency; it subtracts one only in the wrap branch. It never resets
at a block boundary. PW crossing is evaluated before wrap, exactly as source.
The source order matters when both conditions would otherwise be considered.

Target controls are rounded to nearest positive fixed-point quantum; frequency
and PW cap/clamp then happen in DSP code. Each ramp computes
`step=floor(delta/32)`, `remainder=delta−32*step`. Every sample adds step, then
distributes remainder via a0..31 error. After32 steps the state equals the target
exactly; its deviation from the ideal affine ramp is below one parameter quantum.
This replaces float endpoint rounding without dropping interpolation.

Signed DSP MPY is assembled as `mpy y0,x0,a`. The local assembler's reversed
operand spelling can select a mixed-signed form, so the runner requires the
audited signed opcode0x2000D0. No opcode is generated manually. For stored Q3.21
values a,b, signed MPY followed by ASL2 produces `floor(a*b/2^21)` at the data
word transfer. Narrowing checks use the sealed core's left-aligned56-bit
accumulator representation; they do not mistake its eight backing pad bits for
additional signal magnitude. The core/source remains unchanged.

## Division and anti-alias strategy

**IMPLEMENTED:** avoid large reciprocal states by algebraic reformulation:

`triangle_step = (f/PW + f/(1−PW)) * shape`.

Ratios use an exact positive restoring divider: subtract integer parts, then21
fractional compare/subtract iterations. It occupies **MEASURED26 P words**, uses
one dedicated quotient scratch word plus registers/hardware loop state, and
needs no LUT. The target's tested denominator/quotient domain is positive/<4.
Oracle preflight rejects violations; native execution additionally fails closed
on bad addresses, narrowing saturation, output count/order or instruction budget.
The stress sweep produced no bad ratio, phase-wrap or saturation failure.

**SOURCE-DERIVED / IMPLEMENTED** step corrections:

`ThisBlep(t)=t²/2`, `NextBlep(t)=−(1−t)²/2`.

Integrated corrections use
`P(t)=3/16−t/2+3*t²/8−t⁴/16`, with ThisIntegrated=P(1−t), NextIntegrated=P(t).
Horner evaluation retains the same polynomial while reducing repeated work.
Both notch-step and triangle-corner corrections affect current and delayed-next
sample; no correction was dropped or replaced by a naive waveform variant.
The dominant baseline optimization opportunity is ratio division, not evidence
that the correction topology must be discarded. A reduced anti-alias variant
was not required for this complete polynomial PoC; real hardware budget remains
unresolved and may motivate a separately tested later variant.

**TESTED math comparison, not another DSP implementation:** a normalized
65-word reciprocal LUT (linear interpolation) has maximum sampled relative
error6.0489e−5; one Q3.21 Newton refinement reduces it to8.8835e−7.
The actual table bytes are exported for auditing, but the oscillator does not
load/use them. Candidate table size is measured65 words; additional scratch
2..4 words is an **ESTIMATE**; assembled P words/instruction savings are
**UNRESOLVED**, not manufactured measurements. Native DIV is another future
table-free candidate whose quotient scaling needs isolated qualification first.

## Accuracy and sample-rate contract

**MEASURED:** maximum absolute error0.9991969 cents over tested MIDI0..120 at
48kHz and conditional48046.875Hz. Hz quantization is bounded by
`sampleRate/(2*2^22)`, about.00572Hz; relative/cents error grows at the lowest
pitches. This is not a proof of<1cent for every continuous frequency.
At48kHz: MIDI21 error+.009606cents; MIDI69+.009606; MIDI120−.000245.

**SOURCE-DERIVED retuning:** a48kHz-normalized increment reused at48046.875Hz
would be+1.689833cents. Multiply it by **1024/1025** to retune, then quantize.
The suite computes Hz/rate separately for the two rates.48046.875 is only the
inherited conditional Circuit comparison, not a hardware measurement here.
The MI NoteToFrequency converter/pitch tables are not linked; its47872.34Hz
correction and+6.300328cent conditional comparison are a separate source fact,
not this PoC's increment formula.

**MEASURED against unchanged float source:** worst per-case raw RMS.0219731;
maximum DC difference.0003377; peak-amplitude difference below.000931;
magnitude-spectrum cosine similarity at least.99994396 for constant cases.
Long-run phase quantization can move a sharp edge by a few samples. Maximum
single-sample difference reaches1.41453 in abrupt stress tests, despite similar
spectra/peaks. Those unaligned errors are exported, not hidden by phase correction.
No bit-identical float or subjective listening claim is made.

All240640 samples/all case-final states match the independent integer oracle.
This plus exact accumulated phase advances establishes no added block resets;
large boundary jumps are intrinsic waveform events, not a discontinuity inserted
by the block API. See comparison-metrics.csv, pitch-accuracy.csv and
checks/spectral-comparison.json under builds/phase20a-plaits.
