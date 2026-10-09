# Phase 7 — static Plaits resource comparison

## Current Phase20C one-path design update — 2026-10-07

Snapshot acquisition is **DEFERRED**. Conditional live mono overwrite retains
the natural stock setup, both lookup passes, full auxiliary/mono combiner and
post-processing, returning to original9D9. A reconstructed checkpoint is not
required by this architecture. All original generator work remains; this is
additional compute, not a verified workload reduction.

**MEASURED existing layout / CALCULATED template:**81 absolute X sites and26
control sites enlarge442P to549P under prescribed high fixed-address forms.
713P partial module +2 padding excludes converter/init/eligibility/adapter.
Existing7520-block trace traffic implies587/673.3734/945 nominal extra cycles,
not relocated execution. Conservative conditional relocation envelope15343;
partial added workload15485 plus unresolved glue/interlocks/IRQ/waits. The original
13379 bound cannot be carried over as an integrated cost. Complete costs remainnull.

Fixed one-path data demand:7 persistent X +3 controls +3 spills +26 raw saves
=39 words; existing mono32 reused, no new output buffer. Fixed persistent base
unproved. Conditional32-word temporal candidateX[2CCC,2CEC) is not SAFE/allocated.
Generator Q/kernel/sample context words are still rewritten/needed by retained
prefix; none supplies a proved persistent block. Stock amplitude/pitch calibration,
actual wrapper and code/container deployment remain unresolved. No polyphony,
model switching, MIDI-track hosting or Synth2 timing fit claim.

Offline executable patch constructionNO; flashNO; runtime checkpoint branch remains
refused independently. Current details:four new Phase20C notes and
builds/phase20c-livepatch-design/final-v2/ and checks-v2/. Earlier broad checkpoint-next-step
recommendations are superseded by fixed-state ownership design work.

## Phase 20B-SEAM — replay admission refused (2026-10-07)

**VERIFIED:** fresh original-byte map selects9D9 (R0 reload +3NOPs), with9DD
as first post dispatcher andA95 as local group-output accounting boundary.
X2C66 entry prefetch can feed an executedMPY/CCR update; it is later overwritten
byC9F filter history onBDD paths. No universal zero/duplicate/arbitrary policy.

**TESTED REFUSAL:** unknown X5AB/5AC selectors, X5B1/5B2 coefficient addresses,
numeric/state/table/SR/AGU/stack/guard provenance prevent the requested checkpoint.
0 stock instructions,0 joined blocks, no CPU, no actual stock/Plaits-fed traces.
The request explicitly says to STOP for unresolved control/address/scaling/loop
fields. Static mode0 witnesses and boot-clear zeros were not promoted to presets.

Signed24 mono storage is verified; stable amplitude/audio unit and operative
adapter binding remainUNRESOLVED. Host-only explicit numeric adapter fixtures
pass; no stock scale/guard default or DSP adapter cost is assigned. Raw generator
upper13379 is retained; layerB/C costs and full1/2/4/10-voice budgets are null.
Ten leaves30050 only before all missing work. Exact integrated register spills,
code/state totals and pitch/knob conversion remainUNRESOLVED. Persistent RAM
safety/patch-design readiness/hardware flashing remainNO. No code/firmware/hardware
or model/polyphony integration changes.

Single next step:provenance-backed original coefficient/state preparation
checkpoint upstream of9D9; qualify stock-only post replay before Plaits feeding.
Reports:plaits-stock-seam.md,plaits-stock-abi.md,plaits-stock-workload.md.
Canonical:builds/phase20b-seam/final/; unexecuted trace dirs contain refusal.json.


## Phase 20A-BOUND — current timing result (2026-10-07)

**TESTED / CALCULATED:** unchanged442P renderer, reset-reachable maximum13335
cycles/block; all witness samples/seven states/fullPC traces exact, repeated.
**PROVEN-BOUND / CONDITIONAL:** upper13379 including12 boundary cycles, replacing
23902 for legal reset-evolved control/state. 8 PW+8 wraps maximum; exact32..80
ratio calls; at most93 carries. Rare first-sample deferred wrap is separately
bounded11603 and tested with two k=1 ratios. Residual44=12 allowance+32 unresolved
ordering cycles; upper is not claimed attained or globally tight.

Ten raw copies:44.37% matched mean,81.39% reachable maximum,81.66% upper;
remaining30050 cycles /18.34% **TIGHT RAW MARGIN**. One/two/four raw generator
costs fit comfortably; actual stock workload/ABI/ownership/contention remain
**UNRESOLVED**. No renderer/firmware/hardware/polyphony/integration changes.
Next:offline stockP:0x9DD seam/ABI replay plus stock workload accounting before
any ten-voice claim, only under a separate phase request.

Report:notes/plaits-reachable-timing-bound.md. Evidence:builds/phase20a-bound/final/.
Earlier timing maxima/bounds below remain historical; this section supersedes
those values for the unchanged REGOPT renderer's legal standalone domain.


## Phase 20A-REGOPT update — stronger raw compute case (2026-10-07)

**IMPLEMENTED / TESTED / MEASURED:**442P,7 persistentX,3 spillX+16 work registers,
32 outputY,LUT0,stack3;388096 samples/all block states exact to native golden.
**CALCULATED / CONDITIONAL:** matched mean7270.1787 cycles (-22.1511%,STRONG),
all-validated peak12670, structural23902. Conceptual1+1+4+4 target:44.37% mean,
77.33% worst validated,145.89% structural at conditional163840 clocks/block.
Raw margin improves; no qualified stock scheduler/RAM/ABI fit. Remaining largest
family registerMOVE23.10%; no Circuit allocation/integration or polyphony.
Report:[plaits-register-optimization.md](plaits-register-optimization.md).
Stock costs/clock/contention remain **UNRESOLVED**; ownership work staysFROZEN.

## Phase 20A-TIMING update — conditional compute frontier (2026-10-06)

**SOURCE-DERIVED / CALCULATED / CONDITIONAL:** unchanged native renderer
bestmean9338.8336,worstobserved16001 cycles/32; observed-path upper16013,
valid-API structural upper30123. Against conditional163840 clocks:one mean5.70%,
worst9.77%,structural18.39%; ten mean57.00%,worst97.66%,structural183.86%.
One primitive has substantial standalone whole-period margin; ten are not
conservatively qualified once other work is considered. Twelve observedworst
already117.19%. Actual stock scheduling margin/RAM/ABI remains **UNRESOLVED**.
No stock opcode counts added to cycles. Largest modeled family is long-X MOVE
36.00%; candidate next standalone optimization is scratch/register scheduling,
not another divider change. No optimization/integration here. Full report:
[plaits-cycle-audit.md](plaits-cycle-audit.md).

## Phase 20A-DIV update — ratio compute risk reduced (2026-10-06)

**MEASURED / TESTED:** standalone VariableSaw now has a separate700P nativeDIV
variant:7 retained words,44 allocated scratch,32 output,0LUT; issued/32
4414..8956,mean5138.4363,43.2442% below the restoring baseline. All samples
and block states exactly equal the existing oracle/fallback. At48kHz this is
7.70765M mean /13.434M worst issued opcodes/second for one primitive.
Ten-copy arithmetic is **ESTIMATE** only; DSP cycles/stock headroom and RAM/ABI
remain **UNRESOLVED**. No fullVoice/model/polyphony or firmware integration.
Complete report:[plaits-native-div.md](plaits-native-div.md).

## Phase 20A — measured standalone primitive (2026-10-06)

**IMPLEMENTED / TESTED / MEASURED:** user-authorized standalone VariableSaw
fixed-point study now passes its bounded A–K gates. Reference includes unchanged
pinned MI headers; target executes a new708-P-word program in the sealed existing
DSP56300 interpreter, without a Circuit image/peripherals or any stock allocation.
Exact six-header subset and numeric contract are documented in
[plaits-variablesaw-poc.md](plaits-variablesaw-poc.md),
[plaits-fixed-point.md](plaits-fixed-point.md),
[plaits-resource-measurements.md](plaits-resource-measurements.md).

Measured retained state7 X words, scratch44 X, controls3 X, output32 Y;
total logical data86 words, tables0, hardware stack peak5 entries/10 words.
The raw primitive state gate is<=64 words; this replaces the earlier illustrative
scalar/bit-preserving state estimate for this implemented representation only.
Actual upstream host sizeof28 bytes is measured separately. Full Voice/VA engine
and pitch converter resource estimates below are not reclassified as implemented.

43 cases/7520 blocks/240640 samples per run; every fixed DSP sample/final state
matches the integer oracle; full native traces/output repeat byte-identically.
Cost7632..16844 issued opcodes/32 block, mean9053.5811. Real cycles, available
compute budget and stock code/RAM placement remainUNRESOLVED. Worst raw RMS
against float source.0219731; tested pitch error<=.999197cents; large individual
edge differences remain documented, not hidden by phase alignment.
Standalone implementation practical:YES; Circuit integration readiness:NO.

Circuit RAM-ownership/P204B work is FROZEN and unresolved. No X[5F00,6000)
reservation, P9DD adapter, firmware injection, hardware, MIDI/SysEx or full Voice.
Future best step is a native DIV ratio-helper qualification/optimization in the
same isolated harness, followed by the same suite. Older “do not implement” and
after-init next-step statements below are historical, superseded only for the
newly authorized standalone study. They remain valid integration limitations.

## Phase 8 resource update — 2026-10-06

The source comparison is unchanged; no upstream refetch, compilation or port.
See [plaits-poc-memory.md](plaits-poc-memory.md) for the after-init audit.

**SOURCE-DERIVED:**raw VariableSawOscillator has six float scalars plusbool,
25 payload bytes excluding ABI;13 DSP words is only a bit-preserving illustration.
Its32-sample rendering has no mandatory internal32-element temporary array.
It is table-free if supplied independently validated normalized frequency;
source pitch conversion's2056-byte tables remain a separate dependency.

**UNRESOLVED:** no64/128/256/512/1024 contiguous words are verified available.
256 remains a planning target. Boot clear is allowed; normal host, variable DSP
effect/table pointers, worker queue, DMA and save/scratch exclusions remain open.
No future allocation layout is assigned without the required proof.

**HYPOTHESIS:**direct output into stockX:[2C46,2C66) could eliminate an additional
output buffer during serial completion, subject to the numeric/live-state/guard
ABI. That scratch is runtime occupied and cannot retain generator state.
P-code fit/container placement, shared pitch tables and compute headroom remain
separate blockers. Conceptual comparison YES; allocation-qualified design
NOT-YET-DETERMINED; implementation readiness **NO**.

2026-10-05. Feasibility only. **VERIFIED** Circuit instruction evidence;
**SOURCE-DERIVED** pinned upstream; **ESTIMATE** planning/accounting;
**HYPOTHESIS** proposed reduction; **UNRESOLVED** fit or unproved ABI/timing.
No hardware, transmission, firmware/source patches, DSP port, compilation,
linking or injection. Stock payloads are unchanged.

**Conclusion:** a small Plaits-derived generator is plausibly compatible, not
proved to fit. Best first theoretical target is VariableSawOscillator from the
VirtualAnalogEngine OUT graph. Complete Plaits Voice/all engines is a poor first
target. Resource-comparison readiness remains YES; implementation readiness NO.

## A/B. Provenance and minimum architecture

Official [eurorack revision](https://github.com/pichenettes/eurorack/tree/08460a69a7e1f7a81c5a2abcc7189c9a6b7208d4/plaits)
**08460a69a7e1f7a81c5a2abcc7189c9a6b7208d4**; official stmlib submodule
**e3bd7c9cc00e4364166f9905c0509b6ffd0535ec**. MIT code notices retained.
Snapshot: `plaits/upstream`,183 hash-verified files/1,241,908 bytes, excluding
vendor/CAD/binaries. See `plaits-architecture.md` for scope and actual classes.

Minimum path: validated note/frequency and bounded controls → retained
VariableSawOscillator → mono float block → as-yet unspecified numerical adapter
→ X:[2C46,2C66) → stock P:9DD. Preserve lifecycle/filter/gain/scheduler and
neighboring2C66 behavior. Neither full Voice nor module drivers/OUT-AUX short
conversion is required for that derived-generator experiment.

## C–E. Candidate and compatibility comparison

| Candidate | Code/state | Tables | Hot math / risk | First-use ranking |
|---|---|---|---|---|
| VA-derived primitive, then mono OUT | Few scalar states; full VA is larger | Pitch converter only; primitive itself table-free | Float interpolation; reciprocals and event BLEP polynomials; no RNG/oversampling |1 |
| Two-op FMEngine | Tiny scalar state, no allocator | Pitch, sine,130-point quantizer,4-tap FIR |4× loop, uint32 phases, sine interpolation, feedback and downsampling |2 |
| WaveshapingEngine | Small oscillator/state, no allocator | Five257-point int16 shapers, two516-point float folders, sine/pitch | BLEP slopes, table crossfade, two Hermite folders |3 |

SOURCE-DERIVED primitive rendering can use32 samples; FM/Waveshaping also loop
over size without fixed internal block arrays. Full Voice is capped24 and native
12; full VA temp buffer is24. Thus direct raw rendering and full module rendering
have different block compatibility. Full Voice needs buffering or future changes,
including control-time retiming; simply calling it with32 is not compatible.

Rate comparison is conditional: Circuit48046.875 versus Plaits nominal48000 and
pitch correction47872.34. Unchanged pitch conversion gives approximately+6.300
cents at that conditional Circuit rate. Frequency, decay, filter/delay and block
control scaling all require separate audit; no global numerical adapter is specified.

Numeric comparison:

| Plaits source | Circuit DSP |
|---|---|
|32-bit float phases/coefficients/audio, normalized frequency |24-bit data; fractional24×24 MAC/MACR;56-bit accumulators |
| FM uint32 modulo phase, shifts and float PM-to-integer conversion |A uint32 phase is not one24-bit word; precision/wrap redesign or multiword handling needed |
| int16 shaper values divided by32768, float folding/pitch/sine tables |Format/scaling required per table; not every table fits signed unity fraction |
| Raw engine float outputs; module gain/LPG/limiter then Clip16 |Seam32 signed24 words; amplitude, headroom and all-mode scaling unresolved |

32-bit bit patterns need two individually addressable24-bit words if retained
as whole scalars. ceil(bytes/3) is only an ideal packed-storage floor, not a usable
object/array layout. A one-word fixed representation can be smaller but is a
future numerical design with range/precision obligations, not source equivalence.
The state illustrations rebind pointers to native DSP addresses; they do not
copy or bit-preserve original ARM pointer values. Float/u32 bit-preservation
counts and native pointer accounting must not be confused with a target ABI.

## F. Persistent state and scratch

SOURCE-DERIVED scalar field payloads below assume float/u32/pointer=4 bytes,
bool=1 byte. They exclude Engine base metadata, vptr, padding, control packets,
stack, render buffers and compiler ABI. DSP columns are illustrative scalar
counts, not C++ sizeof or a target allocation.

| Source component | Fields | Raw payload bytes | One-word/scalar illustration | Bit-preserving scalar words |
|---|---|---:|---:|---:|
| VariableSaw |6 float + bool |25 |7 |13 |
| Full VA engine |35 float +4 bool + pointer |148 |40 |75 |
| FMEngine |7 float +3 uint32 |40 |10 |20 |
| WaveshapingEngine |15 float +2 bool |62 |17 |32 |

FM's one-word phase illustration changes source width; it is not bit-exact.
Engine base additionally contains two gains and already_enveloped flag, plus
virtual-object layout. FM Init does not explicitly reset sub_fir/carrier_fir;
the original global Voice provides zero-initialized storage. An isolated design
must account for initialization instead of assuming Init/Reset covers every field.

One full Voice persistent inventory (SOURCE-DERIVED, not sizeof):

| Group | Actual retained members / sharing |
|---|---|
| Model objects |22 embedded engine objects; their oscillator/filter/history state is per Voice |
| Selection |EngineRegistry pointers/count; engine_quantizer_, engine_cv_, previous_engine_index_, reload_user_data_ |
| Pitch/trigger |previous_note_, trigger_state_, trigger_delay_line_[8], trigger_delay_ pointer/cursor wrapper |
| Envelopes |DecayEnvelope value; LPGEnvelope vactrol/gain/frequency/hf-bleed/ramp-up state |
| Output processing |Two ChannelPostProcessor objects: limiter peak and LPG previous gain/SVF coefficients and integrator states |
| Render workspace |out_buffer_[24], aux_buffer_[24]; reused buffers, not32-safe unchanged |
| Allocated model workspace |Allocator pool peak overlaid between models; delay/diffuser/speech state within it; switching/reset policy required |
| Inputs/resources |Patch/Modulations are caller inputs; immutable LUTs are shared, not copied into each Voice |

Theoretical mono reductions (SOURCE-DERIVED dependence, not implemented):
VA OUT-only keeps sync+VariableSaw, two gain histories and temp pointer:
17 floats+2 bool+pointer=74 payload bytes; FM OUT-only drops sub-phase/FIR:
6 floats+2 uint32=32 bytes; waveshaping OUT-only drops triangle/AUX-only controls:
8 floats+bool=33 bytes. All still need numerical policy, control and scratch.

Full Voice has at least **324 bytes** in OUT/AUX arrays, trigger-delay array,
24 registry pointers and registry count alone under32-bit host assumptions.
All22 engine object members, envelope/quantizer/post state and other fields
add to this. This is a lower bound, not an estimate of full sizeof(Voice).
The module provides a16,384-byte shared arena; ParticleEngine alone allocates
8192 uint16 entries=16,384 bytes. Engines overlay that arena, not their member
objects. User-data receiver also uses the module arena; this is outside minimal
generator requirements and unsuitable for casual multi-voice replication.

Full VA allocates24 floats=96 bytes; a future direct32-sample version would
need32 floats=128 bytes. FM/Waveshaping/primitive allocate no arena. Raw
OUT/AUX32-float blocks total256 bytes; mono-only can remove AUX after graph
closure. These may be transient shared workspace, not mandatory per-voice state.
Stock scratch cannot be claimed available merely because it is transient.

ESTIMATE audit targets, not proved requirements or available allocations:
PoC A reserve128–25624-bit words for persistent controls/state and local work,
excluding separate tables/output; PoC B reduced common Voice plus these three
small models approximately0.75–1.5KiB of source-like object/work state before
tables (uncertain padding and choices); PoC C all-model Voice needs the16KiB
arena plus its unmeasured large embedded object and render buffers.

## G. Tables and immutable data

SOURCE-DERIVED initializer/declaration audit:

| Table | Type/count | Source bytes | Sharing / need |
|---|---|---:|---|
| lut_pitch_ratio_high/low |float257 each |2056 total |Shared pitch conversion;256 explicit initializers each plus implicit zero last element |
| lut_sine |float641 |2564 |Shared; FM SinePM only indexes0..512, so513-element theoretical subset suffices for that helper |
| lut_fm_frequency_quantizer |float130 |520 |FM harmonics→ratio |
| lut_4x_downsampler_fir |float4 |16 |FM4× decimation |
| lut_fold/lut_fold_2 |float516 each |4128 total |Hermite folding with neighboring guard entries; second folder AUX-only |
| Five lut_ws_* tables |int16,257 each |2570 total |Wave shapers and crossfade; pointer-array metadata extra |
| wav_integrated_waves |int16,25344 |50688 |Wavetable/terrain-family data, not minimal oscillator |
| Three syx_bank_* resources |uint8,4096 each |12288 total |Six-op presets, not two-op FM |

These are immutable const arrays generated offline in resources/units source
and intended for original firmware flash/ROM, not tables generated per voice
at boot. Pitch helper references const units tables; no generator invocation
was run. Shared tables are not multiplied by active voice count.

Complete referenced-array totals (exclude pointer arrays, tiny constants and
full speech datasets; no quantization or trimming performed):

| Set | Source bytes | Whole-scalar bit-preserving DSP words |
|---|---:|---:|
| VA/pitch or primitive plus Plaits pitch conversion |2056 |1028 |
| Full two-op FM table set |5156 |2578 |
| Full waveshaping table set |11318 |5659 |
| VA+FM+waveshaping union, shared common tables |11854 |5927 |

A mono FM subset using513 sine entries has4644 source bytes/2322 bit-preserving
words. Mono waveshaping excluding AUX-only sine/second folder has6690 source
data bytes before pointer-array metadata. Fixed/table packing might reduce
counts but changes precision/access cost; appropriate formats are unresolved.

All scalar arrays in `plaits/resources.cc` sum **74,702 bytes**, or43,815
whole-element bit-preserving DSP words (speech tables in other sources add more).
Carrying all of that in the5538-word P tail is **LIKELY TOO LARGE** even before
code. This does not prove all-model Plaits impossible with separate external
storage or a different layout; neither storage is established here. Even the
three-model whole-scalar table union exceeds that tail before code.

Tables could theoretically occupy P constants, X/Y data or external memory;
each choice consumes its own resource and affects access latency. P/X/Y shared
aliasing is not a substitute for a storage allocation proof. No table placement
or stock waveform/table reclamation is proposed as verified.

## H. Source footprint, not target code size

Reusable quoted-include closures plus paired.cc files provide two lexical
proxies. Generated numeric resource/units bodies are excluded from code counts.
Unused header functions, templates and inactive VA variants are included.

| Closure | Files | Noncomment/nonblank lines | Function-definition candidates |
|---|---:|---:|---:|
| VariableSaw primitive |6 |553 |40 |
| VirtualAnalogEngine |14 |1110 |76 |
| FMEngine |15 |811 |78 |
| WaveshapingEngine |17 |1126 |98 |
| VA+FM+waveshaping shared closure |24 |1766 |129 |
| Full Voice/all engines |125 |12149 |700 |

Primitive's actual hot graph is much smaller than all40 textual candidates:
Init/Render/ComputeNaiveSample, parameter interpolation and four BLEP polynomial
helpers. Full Voice closure has a deliberately omitted flash hardware dependency.
Minimal dispatcher+one engine lies within its closure plus small control/output
glue; multiple engines share helper code, so closure counts cannot be summed.

**UNRESOLVED:** ARM section/map sizes for this exact revision and DSP P words.
No authoritative exact-revision linked map was supplied and none was built.
No ARM bytes→P-word conversion is defensible. Reciprocal strategy, fixed versus
software float, multiword integers, dead-code removal and adapter code could
expand or contract instruction footprint substantially.5538 words is a ceiling,
not a demonstrated code-size estimate. Full Voice is far riskier than one
primitive by source graph/data burden; no invented target byte count is used.

## I. Compute characterization

| Path | Source-derived hot work | Relative risk, ESTIMATE |
|---|---|---|
| Single VariableSaw |3 interpolator increments/sample; phase progression;2 variable reciprocals/sample; piecewise naive waveform; conditional edge division and4 polynomial BLEP calls; final constant normalization |MEDIUM arithmetic-port risk, LOW relative graph size |
| Full VA model |3 sync-capable VariableShape streams plus VariableSaw and mixing; per-block several pitch conversions; per-sample reciprocals/reset timing |MEDIUM–HIGH; mono OUT-only lowers work |
| Two-op FM |4 substeps/output;3 SinePM per substep=12 interpolated sine calls/24 table reads, phase/feedback math and two FIR streams; mono OUT hypothesis reduces to8 sine calls/output |MEDIUM–HIGH despite tiny state |
| Waveshaping |2 bandlimited slopes;4 int16 table reads/sample for adjacent shapers; crossfade;2 Hermite folder evaluations with4 reads each; AUX sine interpolation |MEDIUM compute, HIGH data-placement risk |
| NoiseEngine, not selected |2 noise streams,3 SVFs with accurate coefficient updates and inverse-root gain per sample |HIGH on a fractional-only target |
| Full Voice/physical/speech/six-op set |Model-dependent loops, memories, transforms, envelopes and data |HIGH–VERY HIGH, no single upper bound |

Multiplications in polynomial/interpolation/filter work suit MAC arithmetic
conceptually. Division, fractional/exponent range, wrap semantics and precision
are the difficulties; float operation counts are not DSP cycles. In primitive
the edge path adds many polynomial products; branch frequency and source
optimizations change cost. No exact utilization or worst-case voice budget is
claimed. Original ARM CPU72MHz is not proof of fit on a246MHz conditional DSP.

## J/K. Control and output contracts

| Circuit evidence | Potential Plaits input | Remaining gap |
|---|---|---|
| Current/target note and prepared phase increments |EngineParameters.note or normalized frequency |Exact units, offset, rate and precision mapping; increments are not automatically interchangeable |
| Lifecycle activation/release and slot flags |trigger rising/high/low; gate policy |Retain descriptor/envelope semantics; source trigger delay is optional, not required MIDI latency |
| Squared event level→sensitivity/envelope→stock gain |Potential accent/level if model needs it |Avoid doubling velocity/envelope; VA raw generator need not multiply level again |
| Existing patch/modulation banks |harmonics/timbre/morph, model choice |No semantic control mapping established; new model selector/UI path absent |

Raw candidate engines emit separate mono float OUT/AUX arrays; raw float is not
uniformly clipped or guaranteed within[-1,1]. BLEP overshoot, sync difference,
nonlinear folders and gain change range; DC depends on shape/asymmetry. Full
module ChannelPostProcessor applies per-engine gain, optional limiter/LPG,
negative32767 scale and Clip16 to interleaved short frames. That module polarity
and normalization must not be assumed correct for Circuit's pre-filter seam.

Circuit requires32 signed24-bit mono stored words, retains stock filter/gain/mix,
and reads2C66. Nominal Q1.23 interpretation, absolute headroom, +4-bit mix
scaling, all-mode SR/MR behavior and guard value remain unresolved. Never use
simple float×8388607 conversion or duplicate-last guard as a proved adapter.
Stock current note/envelope/filter/phase and pending bitmap must still update.

## L/M. Three theoretical PoCs and resource matrix

Safest→riskiest, without implementation:

| PoC | Program / persistent state / tables | Scheduler/control / risk |
|---|---|---|
| A: one mono VA-derived primitive on one branch/slot |P words unknown, small graph;25-byte scalar state,128–256-word planning reserve;0 generator LUT or2056-byte pitch tables |Retain stock control/post/mix and scheduling; fixed model/bounded shape controls; reciprocals/scaling/ABI unresolved |
| B: reduced Voice-like dispatcher and3-model subset |P unknown and larger shared graph;~0.75–1.5KiB source-like object/work estimate;11854-byte complete shared table union |Model switching/reset/arena sharing and new controls; block adaptation if Voice semantics retained; numerical/timing risk rises |
| C: broad/full Voice integration |P unknown, huge graph;full objects+16KiB pool;≥74702-byte generated resources |24-model selection, user data, model envelopes and control cadence; substantial scheduler/host work; highest risk |

PoC B is a theoretical *reduced* Voice architecture; unchanged official Voice
still embeds22 objects. None of these descriptions grants safe state allocation
or changes a stock parameter/firmware byte.

| Resource | Minimum / one-engine estimate | Multi-engine estimate | Circuit envelope | Status |
|---|---|---|---|---|
| Program words |UNRESOLVED; primitive small source graph |UNRESOLVED; greater graph and data access |Conditional5538 additional P words; relocation unproved |POSSIBLE for small subset; UNKNOWN fit |
| Persistent X/Y |Primitive7 illustrative fixed or13 bit-preserving scalar words, plus controls/work;128–256-word planning target |Reduced subset~0.75–1.5KiB source-like state/work; full much larger |X8192/Y4096 candidates;zero proved available words |UNKNOWN |
| Shared tables |0 if independently validated frequency supplied; pitch2056B; FM5156B |3-engine union11854B; full≥74702B |No verified table allocation; P also needed for code |UNKNOWN; full P-only copy LIKELY TOO LARGE |
| Scratch |Mono32-float source block128B; full VA additionally temp128B at32 |Shared per-active-engine arena and OUT/AUX; full16KiB pool |Stock scratch lifetimes known only partially |UNKNOWN |
| Output block |32 mono words conceptually available from selected raw renderers |Full Voice needs≤24 chunks/adaptation |Verified32-word seam+readable neighbor |POSSIBLE length; UNKNOWN numeric adapter |
| Compute |Reciprocal/BLEP arithmetic; FM4×; no cycle bound |Modes/group interactions increase unknowns |Conditional163840 total cycles/period, not voice headroom |UNKNOWN |
| Rate |Normalized frequency can be retuned conceptually |All model/control/physical-rate assumptions require audit |Conditional48046.875Hz |POSSIBLE; no final physical rate proof |

No row is labelled FIT while Circuit ownership or headroom is unverified.

## N–Q. Blockers, archaeology and decision

- **Circuit reverse-engineering:** normal host/DSP pointer exclusion, bank-selector
  invariant20006800, DMA/effect ownership, phase/scheduler clobbers and guard reuse.
- **Plaits porting:** float→fractional/multiword choices, reciprocal math, uint32
  wrap, block/control retiming and model subset/reset semantics.
- **Resources:** no verified persistent/table region, no target code size, container
  relocation/device size acceptance and no available execution headroom.
- **ABI/numeric:** absolute amplitude/DC/scaling/rounding, stock state side effects,
  complete live/clobber set and2C66 value/lifetime.
- **Toolchain:** only a decoder exists; no validated DSP compiler/assembler/linker,
  target build/layout or cycle-validation workflow established. None installed.

| Requested decision | Answer |
|---|---|
| A: obviously impossible? |NO for a small derived subset; broad untouched Voice is a poor fit hypothesis, not a universal impossibility proof |
| B: small engine plausibly compatible? |YES, VA-derived primitive; plausibility only |
| C: unverified X/Y remains primary blocker? |YES for safe implementation, even though minimal scalar needs are small |
| D: program uncertainty primary? |YES; data/code placement and container extension unresolved |
| E: timing primary? |YES; neither source operations nor MHz proves spare cycles |
| F: bank-selector proof before designing PoC? |NO for the conceptual architectures above; YES before claiming allocation safety through banked-host exclusion, unless an independent proof replaces it |
| G: mono seam still best? |HYPOTHESIS YES for retaining stock lifecycle/post/mix; no better proved ABI emerged from Plaits source |
| H: first theoretical target? |VariableSawOscillator from VA OUT, then optionally mono OUT's sync+variable-saw graph |

Firmware archaeology must continue before an implementation-ready PoC design.
Source reading now lets that work target a modest allocation rather than
assuming the full16KiB module arena is the first requirement.

**Single best next step:** prove an after-init **256-word state/work allocation**
for one monophonic primitive, closing normal bank-selector/host destination and
DSP runtime exclusions for that exact range. Keep pitch-table placement,
numerical ABI and execution headroom as separate proofs; do not implement yet.

## Reproduction

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_plaits_audit.py --output-dir builds/phase7
```

Choose a fresh output directory. Reports:comparison.json,dependency-closures.json,
tables.csv,state-fields.csv,rate-block-references.csv,allocator-sites.csv.
Source byte/field/table inventories are reproducible; estimates are explicitly
labelled. No target binaries or C++ sizeof results are produced.
