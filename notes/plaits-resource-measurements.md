> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 20A — measured standalone VariableSaw resources

## Phase 20A-REGOPT update — smaller exact working frame (2026-10-07)

**MEASURED:** preferred standalone442P (was700),7 persistentX unchanged,
3 scratchX spills+16 working registers (was44 allocatedX),3 controlX,32 outputY,
0LUT, hardware stack3/6words. Memory total45; including work registers61.
Do not call the full temporary footprint three words. Original+focused388096
samples/states exact, baselines preserved. **CALCULATED / CONDITIONAL:** matched
cycles6278/7270.1787mean/12390; focused/all peak12670,upper12682; structural23902.
22.1511% matched mean reduction=STRONG. Actual device timing/stock margins
remain **UNRESOLVED**. Report:[plaits-register-optimization.md](<plaits-register-optimization.md>).

## Phase 20A-TIMING update — cycle estimate, unchanged resources (2026-10-06)

**MEASURED issued counts / SOURCE-DERIVED rules / CALCULATED cycles:**700P,
7persistent,44scratch,32output,LUT0 unchanged. Best model per32:min8035,
mean9338.8336,max16001; lower7808/9106.5277/15721; observed-path uppermax16013.
Conservative valid-API CFG upper30123. These assume private/internal/zero-wait,
resident stack, noDMA/IRQs and family-to-device timing correspondence. Actual
Circuit cycles/headroom remain **UNRESOLVED**. Detailed cost is not one clock
per issued opcode:lab/lim, branches,REP and accumulator hazards are included.
Native helper49 clocks observed,49..82 valid-domain, versus restoring mean222.5375
under the same model. Sources and scope:[plaits-cycle-audit.md](<plaits-cycle-audit.md>).
No renderer modified/rerun; timing phase does not change the resource tables below.

## Phase 20A-DIV update — preferred standalone resources (2026-10-06)

**MEASURED / TESTED:** nativeDIV variant700P, helper18P, retained7X,
allocated scratch44X (43 live; former helper slot retained unused), controls3X,
output32Y, LUT0. Stack peak3 entries/6words. Issued/32:min4414,
mean5138.436303,max8956;43.2442% mean reduction.283,027 helper calls,
33 issued opcodes each in this suite (33..48 for general admitted fixtures).
All samples/states exactly equal restoring baseline. Hardware cycles/headroom
remain **UNRESOLVED**; no stock allocation. Details and old/new table:
[plaits-native-div.md](<plaits-native-div.md>). Original20A measurements below
remain the preserved restoring baseline.

2026-10-06. **MEASURED / TESTED**, not a Circuit allocation or integration proof.
Canonical suite:builds/phase20a-plaits/final/; verification:checks/;
executables:core-final-v2/. New isolated program uses the sealed existing
Phase19A forced interpreter and its existing assembler. No large tool installed,
emulator source changed, Circuit image loaded or hardware contacted.

| Resource | Actual measured requirement |
|---|---:|
|Assembled program|708 P words /2124 bytes|
|Decoder tail NOP padding|2 mapped P words; not oscillator instructions|
|Persistent oscillator state|7 X words,0 Y words|
|Control input frame|3 X words, overwritten each call|
|Scratch / transient X variables|44 X words|
|Mono output|32 Y words|
|Logical data footprint including output/controls|86 words|
|Immutable synthesis LUTs|0 words|
|Exact restoring divider code|26 P words, included in708|
|Peak hardware stack|5 entries =10 24-bit words; restored depth0 after call|
|Upstream host sizeof(VariableSawOscillator)|28 bytes, float4 bytes; separate host ABI|

**State gate:** mutable retained oscillator state7 is<=64 (and<=128/256).
This is measured target representation, replacing earlier bit-preserving float
illustrations. Transient44/control3/output32 and hardware stack10 are separate;
do not call the full working footprint seven words or infer stock free memory.
Unused capacity in the harness is not a target resource requirement.

The isolated bus backs X256,Y32 and P4096 words for convenience. Semantic
allocations are stateX[20,27), controlsX[40,43), scratchX[80,AC), outputY[0,20).
Those are labels in a fresh synthetic emulator instance, not addresses reserved
or aliased in Circuit memory. Program begins at private P200; no stock P bytes
are loaded. Constructor/decoder NOP reads at0/1 and after program are padding,
not executed oscillator instructions; execution is restricted to actual assembled
instruction starts. Writes to P, peripherals or outside declared data slots fail.

Persistent fields are phase, delayed next sample, previous PW, high flag, retained
frequency, retained PW, retained shape. Scratch includes ramp steps/remainders/
errors and intermediate ratios/corrections. There is no mandatory lookup table,
second32-sample audio scratch array, RNG state, heap allocator, full Voice, LPG,
effect/filter state or MCU-style float object in the DSP rendering loop.

Immediate constants are already counted in P code; they are not another LUT
count. The optional measured65-word reciprocal candidate is a separate math
experiment, not loaded by the oscillator. Future table/code sharing across voices
is possible in principle; no multivoice dispatcher or RAM layout was implemented.

## Instruction cost

**MEASURED issued opcodes per32-sample call**, using authoritative before-opcode
hooks including real DO-body/call instructions:

| Scope | Minimum | Maximum | Mean |
|---|---:|---:|---:|
|All43 cases /7520 calls|7632|16844|9053.5811|
|440Hz long sequence,2048 calls|7872|8690|8337.9512|
|Joint pitch/PW/shape sweep|7796|11784|8757.3438|
|Abrupt bounded stress|7632|15052|9474.1953|
|Frequency cap.25, shape1|12678|16844|16778.9063|

One full suite issues68,082,930 opcodes. Repeated full runs have byte-identical
complete execution-PC streams, sample vectors, states and per-block authoritative
write hashes. Every issued instruction's opcode is recoverable from immutable
program.be24 and program.asm. Each raw PC trace is136,165,860 bytes; it is a
full trace, not just a summary hash. Host reference output also repeats exactly.

**ESTIMATE only:** treating each issued opcode as one cycle gives an optimistic
baseline; actual DSP cycles, branch/DO/JSR costs, memory wait states, clock and
stock processing budget are UNRESOLVED. No hardware cycle benchmark or Cycle
count proxy is passed off as measured timing. At48kHz/32=1500 calls/second,
the suite-average workload corresponds to13.5804 million issued opcodes/second
per oscillator; the measured worst block corresponds to25.266 million.
Ten independent copies would multiply these arithmetic estimates and compete
with other DSP work; this is not proof that the requested future architecture fits.

## Differential and safety gates

**TESTED:**43 cases,7520 blocks,240640 samples per run. Includes MIDI21/69/108
shape/PW endpoint/midpoint matrix; MIDI0/21/60/69/96/120 at both separate rates;
2048 continuous440Hz blocks;256 sweep blocks;256 deterministic abrupt stress
blocks;64 blocks exercising the source frequency cap.

DSP outputs and all seven final state words match the independent integer
oracle exactly. Original float reference and DSP both run twice. Sixteen-bit
audio examples are generated offline with one common.75 playback gain, and
their headers/frame counts are verified; unscaled raw float/fixed vectors remain.
No software/hardware audio playback was used to judge sound quality.

Prototype numerical checks pass: raw per-case RMS<.025, absolute DC difference
<.001, peak difference<.002 and tested pitch error<1.1cents. These are explicit
study acceptance limits, not universal error bounds or perceptual certification.
The raw maximum edge difference1.41453 is retained. Spectrum similarity of
constant cases is>=.99994396 after mean removal/Hann window; no phase realignment
or altered native output was used for the raw RMS metrics.

Guarded native run reported zero narrowing saturation, bad-address/peripheral
or instruction-budget failures. Oracle checked positive ratio denominators and
quotient<4. Final phase/high domains and exactly32 orderedY writes/call were
verified. Frequency0 is refused before any oscillator instruction; three
existing-output refusal paths preserve all existing suite artifacts.
These are bounded tested domains, not proof for arbitrary invalid parameters.

Original SYX/BIN expected hashes, in-memory roundtrip, all10 DSP extracts,
183 pinned upstream sources and sealed emulator/harness/previous helper hashes
remain intact. Circuit RAM ownership/integration gates remain FROZEN/UNRESOLVED.
