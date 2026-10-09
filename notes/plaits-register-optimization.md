# Phase 20A-REGOPT — exact standalone register optimization

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


Completed2026-10-07. **IMPLEMENTED / TESTED / MEASURED:** preferred renderer
442P,7 persistentX,3 spillX+16 working registers,32 outputY,0 tables, stackpeak3.
**CALCULATED:** mean cycle reduction22.1511% over the unchanged43-case suite:
**STRONG**. Every sample/state remains exact against native-DIV golden and oracle.
Timing is **CONDITIONAL**, not physical DSP measurement or host benchmarking.

No hardware, MIDI/SysEx, Circuit image execution/patching, stock RAM reservation,
model switching, polyphony or P:0x9DD integration. Native/restoring baselines
remain hash-identical. Canonical delivery:builds/phase20a-regopt/final-report/.

## A–B. Liveness, register pressure and exact scheduling

**MEASURED / IMPLEMENTED:** all44 original scratch fields are documented in
scratch-liveness.csv:43 used, former ratio_integer_q atX:0xAB unused. Original
trace scratch accesses:6,501,445 reads/4,151,066 writes. CFG joins both conditional
branches, helper calls and the DO backedge. Peak live19;19 colors,16 register
colors+3 spills. Producer/consumer PCs, first/last static/dynamic use, read/write
counts, definition-to-read span and call/sample crossings are exported.
Completed liveness was reused during continuation, not restarted.

Y1,R1..R7,N0..N7 retain exact24-bit words. The three ramp step/remainder/error
triples live around sample iterations; event/poly/naive temporaries share colors.
Helper clobbers A/B/X1/CCR and preserves all16 selected registers. Every optimized
call checks those registers at entry/return. X0/Y0 remain operands; A/B/X1 are
not assumed free across calls. M0..M7 remain linear0xFFFFFF. R0 is the sole
output pointer; R1..R7 are data only. N0=pw_rem is written only in setup, far
before R0 addressing, so even a triplet-wide AGU interlock introduces no stall.
register-allocation.csv inventories all30 requested working registers.

**IMPLEMENTED exact word boundaries:** memory stores become A1 transfers,
not full-accumulator retention. Loads into A reconstruct the sign-extended word
with A0=0. MPY/ASR can leave low bits; those truncation boundaries remain.
Reloads disappear only when CFG data flow proves A0 already zero. Deleted
stores retain zero-cost narrow_N labels, checked by the host for signed24 range.
No saturation is silently bypassed in the tested admitted domain.

Dead X0 constant loads fold into equivalent immediate ADD/SUB/CMP only when
X0 is dead afterward and entry/edges permit. Short immediates use unsigned0..63;
other values retain signed24-bit long form, per pinned manual. Arithmetic order,
formats, interpolation, event decisions/current-next corrections and state
commit remain unchanged. All arithmetic-family execution counts match golden.

First candidate:21 dead scratch pairs removed. Refined candidate:50 static
instructions removed overall, including proven-zero reload/argument reductions.
No extra pointer chosen for3 short spill cells. No new parallel form selected:
local producer/store pairs depend on the new A and its word boundary. The three
qualified parallel helper forms remain. Branch counts/outcomes are unchanged;
immediate comparisons remove preparation moves, not BLEP decisions. No cheap
approximation/recomputation or reduced correction quality was introduced.

## C–E. Memory traffic, scratch and P words

**MEASURED**, original43-case suite:

| Access | Native baseline | Optimized | Removed |
|---|---:|---:|---:|
|X reads|11075975|4631046|6444929|
|X writes|5900052|1791373|4108679|
|Y output writes|240640|240640|0|

X operations removed10553608 (**62.1677%**). Long-absolute X accesses disappear.
Private standalone layout (hex):scratchX[0,3), stateX[20,27), controlsX[30,33),
outputY[0,20). These are not stock Circuit mappings.

| Resource | Native | Optimized |
|---|---:|---:|
|P words|700|442 (-258 /36.86%)|
|Persistent X words|7|7|
|Allocated scratch X words|44|3|
|Working register scratch|0|16|
|Input X /output Y|3 /32|3 /32|
|Tables|0|0|
|Data-memory words incl controls/output|86|45|
|Memory plus working-register words|86|61|
|Peak stack entries /words|3 /6|3 /6|
|Native ratio helper P words|18|18|

First candidate was482P; refinement442P. Memory scratch<=32/24 targets are met,
but16 working registers must also be counted:19 simultaneous transient values.
Decoder padding2 is separate. Future caller/IRQ register-preservation and stock
placement costs remain **UNRESOLVED**; this is not a usable stock allocation/ABI.

## F–J. Cycle comparison and success category

**CALCULATED / CONDITIONAL:** frozen Phase20A-TIMING rules, plus documented
immediate CMP1/2-clock forms. Memory/address costs, accumulator hazards, Jcc4/5,
DO/REP5, DIV1, calls3 remain. Short-store ambiguity uses1 lower/2 best-upper.
Private zero-wait internal memory, resident stack, no IRQ/DMA and family/device
correspondence remain assumptions. No host elapsed time is timing evidence.

| Same original43-case suite | Native | Optimized | Reduction |
|---|---:|---:|---:|
|Best min cycles/block|8035|6278|21.8668%|
|Best mean|9338.8336|7270.1787|22.1511%|
|Best max|16001|12390|22.5673%|
|Observed-path upper max|16013|12402|22.5504%|
|Conservative structural upper|30123|23902|20.6520%|
|Issued min/mean/max|4414 /5138.4363 /8956|3988 /4653.9590 /8136|Not cycles|

Optimized lower:6051 /7031.9642mean /12060max. Structural upper=
111startup+32*743 longest sample path+3 finalJMP+12 boundary allowance.
It retains all main branches/general ratio integer parts0..3, including
mutually inconsistent combinations; no bound on invalid state or actual async
Circuit activity. Helper stays49 cycles observed,52 inclJSR,49..82 general.

**Focused stress raises the observed peak:** native/optimized stress means
13413.3229 /10357.2810, maxima16532 /12670. Optimized worst is eight-step
control corners block5,8304 issued. Across all validated cases, max **12670**,
observed-path upper **12682**. Do not report12390 as the combined maximum.
The original matched mean defines the requested category: **STRONG**, not
EXCELLENT. No extra changes forced to reach30%.

The original timing exporter assumes named43-case representative groups.
Focused profiling produced complete per-block CSVs before rejecting different
group names. Those calculations were retained; stress_summary.py completes
their summary and analyzes golden focused traces without rerendering. Canonical
focused timing is stress-timing-summary/, not the partial exporter directory.

## K. Exact validation and determinism

**TESTED:**43 unchanged cases/7520 blocks/240640 samples twice. Inputs/oracle/
float reference/metrics/pitch/rate/continuity hashes identical to golden. Every
sample and seven-word block state exact.2048-block continuity and tested pitch
max0.9991969348cents unchanged. Float-reference RMS0.0219731, maximum edge
difference1.41453 and minimum spectrum0.9999439621 remain the baseline values;
there is no new bit-identical-float claim.

**TESTED focused:**9*512=4608 blocks/147456 samples, native golden and
optimized both repeated. Notch-heavy/triangle-heavy/blended quarter-rate events,
near-quarter PWM/shape extremes, lower-frequency extreme PW, rapid ramps,
eight-step corners and seeded random cases at48k/conditional48046.875Hz.
Exact golden and independent oracle agreement throughout; no saturation/address/
stack/helper-clobber failures. Simultaneous means both weighted corrections at
one event, not changing the exclusive PW-versus-wrap ordering.

Total52 cases,12128 blocks,**388096 samples**; integer max/RMS difference0.
All seven states after every block and exact event kind/order at each sample
match. Helper/branch/arithmetic counts match. Helper symbolic suffix is identical,
18P with relocated jump targets,21 DIVs. Full native traces/artifacts repeat
byte-identically within each implementation. Invalid-input/overwrite refusals
and immutable native/restoring/core/original-input guards pass.

## L–M. Revised conditional scaling

**CALCULATED / CONDITIONAL:**246MHz model,163840 cycles/block at48046.875Hz;
164000 at48k. Table uses matched-suite mean and higher focused worst. No stock
work/mixing/scheduler/outer ABI is included.

| Copies | Mean cycles /% | All-validated worst cycles /% | Remaining after worst | Structural upper cycles /% |
|---|---|---|---:|---|
|1|7270.18 /4.44|12670 /7.73|151170|23902 /14.59|
|2|14540.36 /8.87|25340 /15.47|138500|47804 /29.18|
|4|29080.71 /17.75|50680 /30.93|113160|95608 /58.35|
|8|58161.43 /35.50|101360 /61.87|62480|191216 /116.71|
|10|72701.79 /44.37|126700 /77.33|37140|239020 /145.89|
|12|87242.14 /53.25|152040 /92.80|11800|286824 /175.06|

CSV includes remaining cycles for all scenarios at both rates. Ten-copy observed
upper126820 is77.40%, remaining37020; structural margin-75180. A loose upper
exceeding budget does not prove actual failure but prevents conservative fit.

Conceptual1Synth1+1Synth2+4MIDI1+4MIDI2=10: **44.37% mean,77.33% worst,
145.89% structural**. Raw demand improves; architecture remains **UNRESOLVED**
because stock processing/worker/IRQ/DMA/headroom and RAM/ABI are unbounded.
No MIDI-track voice hosting/routing/polyphony is established or implemented.

## N–P. Remaining hotspot and next step

**CALCULATED** original-suite family shares:

| Family | Before cycles/share | After cycles/share |
|---|---|---|
|Long X MOVE|3362.25 /36.00%|0 /0%|
|Register MOVE|75.27 /0.81%|1679.60 /23.10%|
|Short X MOVE|1298.26 /13.90%|1330.47 /18.30%|
|Conditional jumps|1223.15 /13.10%|1223.15 /16.82%|
|DIV iterations|790.37 /8.46%|790.37 /10.87%|

Residual spills/control accesses move to short space; total memory cost falls.
Unchanged branch/DIV shares rise as total cost shrinks. Functional naive blend/
output29.96%, ratio helper25.37%, ramps21.37% are a separate partition.

Further low-level optimization is worthwhile if focused on exact dual-accumulator/
legal parallel scheduling of register transfers, with smaller returns and strict
word-boundary/helper constraints. No specific unimplemented saving is promised.

**Single best next step:** tighten the control/state-aware structural bound using
legal event-count and ratio-domain invariants before another code change. The
23902-versus12670 gap now limits a conservative ten-primitive compute claim.
Remain offline; stock timing/ownership/integration are separate unresolved gates.

## Deliverables and reproduction

final-report/ contains requested scratch-liveness.csv, register-allocation.csv,
before-after-instruction-census.csv, before-after-cycles.csv,
hotspot-comparison.csv, voice-scaling.csv, exact-equivalence.json, plus memory/
options/golden/provenance/hash evidence. Numeric runs:final/, extended/;
timing:timing/, stress-timing-summary/; completed liveness:liveness/.

Separate implementations:restoring plaits/poc/generate.py; native baseline
div/generate_compact.py; optimized regopt/generate_final.py. First register
candidate generate_opt.py/core-probe/register-candidate remains available.

Use existing installed tools and fresh output directories:

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& plaits/poc/regopt/build_final.ps1 -BuildDir builds/phase20a-regopt/rebuild-new
& $taskPython -B plaits/poc/regopt/collect_final.py --output-dir builds/phase20a-regopt/suite-new --build-dir builds/phase20a-regopt/rebuild-new
& $taskPython -B plaits/poc/regopt/extended.py --output-dir builds/phase20a-regopt/stress-new --build-dir builds/phase20a-regopt/rebuild-new --assembly-dir builds/phase20a-regopt/suite-new/assembly
& $taskPython -B plaits/poc/regopt/timing_opt.py --suite-dir builds/phase20a-regopt/suite-new --output-dir builds/phase20a-regopt/timing-new
```

report.py/stress_summary.py/finalize.py complete reports from retained canonical
evidence and refuse existing outputs. No completed liveness repeated on resume,
external tool installed, device accessed or integration performed.
