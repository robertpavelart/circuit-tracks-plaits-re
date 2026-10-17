> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 20A-TIMING — offline VariableSaw cycle audit

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

## Phase 20A-REGOPT update — exact renderer preferred (2026-10-07)

**IMPLEMENTED / TESTED / MEASURED:**442P,7 persistentX,3 spillX+16 work registers,
32 outputY,0LUT, stack3. All388096 original+focused samples and all block states
match native golden/oracle exactly; event order and helper unchanged.
**CALCULATED / CONDITIONAL:** matched43-suite min6278,mean7270.1787,max12390
(-22.1511% mean,STRONG). Focused stress raises all-validated max12670/upper12682;
structural upper23902. Ten-copy raw mean44.37%,worst77.33%,structural145.89%
against conditional163840. Stock headroom/ABI/RAM remain **UNRESOLVED**.
Report:[plaits-register-optimization.md](<plaits-register-optimization.md>).
Canonical:builds/phase20a-regopt/final-report/. The prior optimization next step
below is complete; next is control/state-aware structural-bound refinement.

2026-10-06. **SOURCE-DERIVED / MEASURED / CALCULATED / CONDITIONAL.** The
unchanged native-DIV renderer's existing deterministic traces support an
8,035..16,001-cycle best documented estimate per32-sample block, mean9,338.83.
The observed-path upper is16,013; a broader conservative valid-API control-flow
bound is30,123. All are conditional on the stated architecture/memory model.
One isolated mono primitive has substantial conditional compute margin; ten
simultaneous worst observed renders leave almost none for other processing.

This phase executes no renderer or stock firmware. It reads the validated
700P native program,38,641,041 issued PCs,7520 block boundaries and the
preserved restoring traces. Algorithm, code, oracle, firmware/originals and
stock RAM ownership are unchanged. No hardware, MIDI/SysEx, model switching,
polyphony or P:0x9DD integration. Host wall-clock times are not timing evidence.

## A. Sources, assumptions and scope

Pinned DSP56300FM Rev5 AppendixA/3.5/5.3 and DSP56724RM Rev1
4.3/3.2 provide the timing/forwarding, private-memory and pipeline rules.
[dsp56300-timing-model.md](<dsp56300-timing-model.md>) records exact pages/hashes
and per-rule DOCUMENTED EXACT / DEVICE-FAMILY ASSUMPTION / UNRESOLVED status.
Existing manuals only; no download/install. Visual inspection confirms one
malformed short-MOVE timing row. Short stores use2 cycles in best/upper,
1 in lower; interpretation remains an explicit assumption.

**CONDITIONAL admitted platform:** same DSP56300 core timing, private internal
P/X/Y, resident stack with SEN0, linear addressing, no DMA/IRQs/shared or external
access. Actual Circuit memory/bus activity and physical clock are **UNRESOLVED**.
Finite upper bounds here do not bound the actual Circuit scheduler.

## B. Instruction-family census

**MEASURED** from existing PC traces:453 executed sites,23 families;458 static
instruction sites occupy700 P words. The five unexecuted sites are three
integer-part loop instructions and the two zero-denominator return instructions;
their timing is covered separately by the static helper bound.

| Family | Mean issued instructions /32 |
|---|---:|
|Long absolute X MOVE|1423.804|
|Short absolute X MOVE|833.647|
|Long immediate MOVE/MOVEC|371.538|
|Register MOVE|37.637|
|Y MOVE with postincrement|32|
|ADD /SUB /CMP|345.218 /131.765 /249.527|
|ASL /ASR /ROL|199.690 /23.777 /37.637|
|Signed MPY|126.062|
|CLR /TST /NEG|37.637 /37.637 /1.879|
|ANDI|37.637|
|Conditional Jcc|287.164|
|JMP|19.906|
|JSR /RTS|37.637 /37.637|
|DO /REP|1 /37.637|
|DIV|790.368|
|MAC /MACR /P-data /simultaneous XY /same-space multiaccess|0|

Exclusive family totals sum to the baseline5,138.4363 mean issued instructions;
overlapping memory/AGU/accumulator/parallel features are separately labeled.
`instruction-census.csv` includes minimum and maximum blocks, whole-suite mean,
and mean/max stress, sweep, continuity and frequency-cap cases. Wide census
and cycle components are exported for every block, not just these summaries.

Minimum:case41 bounded_stress block163,4414 issued,8035 calculated cycles.
Maximum:case42 frequency_cap block1,8956 issued,16001 calculated cycles.

## C. Native DIV, call and stack costs

**SOURCE-DERIVED / CALCULATED:** DIV1 cycle/iteration, REP setup5,
ANDI3, untaken denominator JEQ5, taken fraction JLT4, resident RTS3.
Other seven helper instructions cost1 each; DIV->MOVE A0,A adds1 arithmetic
stall. Sum:21+5+3+5+4+3+7+1 = **49 cycles/call**, versus33 issued opcodes.
Caller JSR adds3: **52 cycles including the call instruction**.

There are283,027 calls; every oscillator-suite numerator is below denominator.
General admitted helper bounds, for floor(n/d)=0/1/2/3:49/60/71/82 cycles,
including RTS and excluding JSR. Each extra integer iteration costs11 cycles.
Zero guard is10 cycles and is outside the valid division API, unused in this suite.
The helper has no memory traffic or stack spill; peak3 resident entries remains.

**CALCULATED static restoring comparison**, using the existing old trace under
the same timing rules, no rerender: helper mean222.5375 cycles (excludes caller
JSR), versus49; mean helper reduction77.9812%. Whole renderer estimate:
old13422..29233, mean15870.1908; native8035..16001, mean9338.8336;
mean modeled-cycle reduction41.1549%. This differs from the measured43.2442%
issued-opcode reduction because memory, branches and interlocks cost extra.

## D. Pipeline, memory, branches and loops

**SOURCE-DERIVED / CALCULATED:** long absolute/immediate fields add1 to their
nominal1-cycle MOVE; arithmetic and move-transfer accumulator hazards add1
where documented. Across the complete native trace:

| Contribution | Cycles |
|---|---:|
|Nominal instruction timing|50,026,135|
|Addressing lab/lim surcharges|13,500,972|
|Untaken conditional-jump additions|560,230|
|Accumulator arithmetic stalls|4,998,482|
|Accumulator transfer stalls|1,142,210|
|Total best documented model|70,228,029|

Jcc:1,599,241 taken and560,230 not taken; charges4/5 respectively. The audit
identifies clamp, ramp, phase-wrap, BLEP/sign, waveform and divider guard sites.
There is no branch to outer LA/LA-1, degenerate/annulled DO or REP.

Each block: DO setup5;31 ordinary zero-overhead backedges, one ordinary exit.
Every ratio call: REP setup5 and21 one-cycle DIVs. Setup is counted every call.
No invented per-iteration loop branch or loop-exit instruction is charged.
JSR/RTS3 each; no stack-extension delays, outer wrapper call or fake outer RTS.

Three helper-local arithmetic/register-move parallel forms cost1 each, not2.
No arithmetic+memory parallel instruction occurs. Separate X/Y/P buses and
one data access per instruction avoid same-space/XY conflicts in private RAM.
Y output has a transfer stall after its preceding A load, but R0 postincrement
has no separate cost. The first R0 use has at least135 intervening opcodes
after initialization; no AGU-register interlock. No modulo operation, explicit
SR-read/bit-test stall, external wait, DMA or IRQ occurs in the admitted model.
Actual device contention remains **UNRESOLVED**, not silently charged0 for Circuit.

## E–H. Three timing outputs and conservative structural bound

**CALCULATED**, clocks per32-sample block:

| Model | Minimum observed | Mean | Maximum observed |
|---|---:|---:|---:|
|Lower bound: ambiguous short stores1|7808|9106.5277|15721|
|Best documented estimate: short stores2|8035|9338.8336|16001|
|Observed-trace upper: best+12 boundary clocks|8047|9350.8336|16013|

**CONSERVATIVE STRUCTURAL UPPER:30,123 cycles.** Startup longest path156,
sample longest path936 ×32, final JMP3, boundary fill/drain allowance12.
Helper bound82 includes integer-part alternatives absent in the observed suite.
Both alternatives of every main branch are retained; some combined choices
are mutually inconsistent. This is a safe overapproximation under the valid
numeric API and private-memory assumptions, not a new observed worst case.
It is not a bound for invalid state, actual external waits or asynchronous work.

Representative best-model cycles:

| Case set | Min | Mean | Max |
|---|---:|---:|---:|
|2048-block continuity|8243|8697.6914|9087|
|Joint sweep|8259|9291.6211|11837|
|Abrupt bounded stress|8035|9899.5820|14339|
|Frequency cap|12301|15943.1875|16001|

## I–J. Conditional budgets, rates and voice scaling

**CONDITIONAL:** prior MCO/PCTL model gives Fsys246MHz; physical routing/
oscillator is unverified. At48kHz,32 frames give164,000 clocks /666.6667us.
At conditional48,046.875Hz, budget163,840 clocks /666.0163us. These are total
period budgets, not available generator budgets.

Applying the same pooled observed workload at the two rates:

| Rate | Mean utilization | Worst observed | Observed-path upper | Structural upper |
|---|---:|---:|---:|---:|
|48,000Hz|5.6944%|9.7567%|9.7640%|18.3677%|
|48,046.875Hz conditional|5.7000%|9.7662%|9.7736%|18.3856%|

This holds workload constant to compare budgets. Separate rate-tagged case
results are in `rates/rate-summary.csv`:48k6368 blocks mean9292.5411;
conditional1152 blocks mean9594.7283. Those groups contain different controls/
case mixtures. Matched six pitch cases at both rates give means9596.3533 /
9594.7283 and maxima14130 /14141; do not attribute the unmatched mean
difference to sample rate. All derive from the original traces.

**CALCULATED arithmetic only**, conditional163,840 budget:

| Primitive copies | Mean cycles /% | Worst observed cycles /% | Remaining after observed worst | Structural upper cycles /% | Remaining after structural upper |
|---|---|---|---:|---|---:|
|1|9338.83 /5.70|16001 /9.77|147839|30123 /18.39|133717|
|2|18677.67 /11.40|32002 /19.53|131838|60246 /36.77|103594|
|4|37355.33 /22.80|64004 /39.06|99836|120492 /73.54|43348|
|8|74710.67 /45.60|128008 /78.13|35832|240984 /147.09|-77144|
|10|93388.34 /57.00|160010 /97.66|3830|301230 /183.86|-137390|
|12|112066.00 /68.40|192012 /117.19|-28172|361476 /220.63|-197636|

`voice-scaling.csv` includes remaining clocks for all lower/mean/worst/upper
scenarios at both rates. Ten-copy observed-path upper160130 is97.7356%,
remaining3710 clocks. Scaling adds no actual scheduler, mixing, controls or
voice allocation. The conceptual target is1 Synth1 +1 Synth2 +4 MIDI1 +4 MIDI2;
it does not establish that stock MIDI tracks can host DSP voices.

## K. Hotspots and optimization gate

**MEASURED counts × SOURCE-DERIVED latency = CALCULATED model costs.**

| Ranked instruction family | Mean cycles/block | Share |
|---|---:|---:|
|Long absolute X MOVE, including hazards|3362.2463|36.003%|
|Short absolute X MOVE, including hazards|1298.2586|13.902%|
|Conditional Jcc|1223.1535|13.097%|
|DIV iterations|790.3680|8.463%|
|Long immediate MOVE|743.0766|7.957%|

Functional accounting: naive waveform/blend/output32.74%; per-sample parameter
ramps24.97%; ratio helper19.75%; phase/event decisions14.33%; BLEP correction
math5.82%. These are alternative partitions, not additive with family shares.
The fullhelper49-cycle cost includes setup/guards/return in addition to DIV.

Largest next optimization target: reduce scratch-memory traffic through register
reuse and legal ALU+MOVE scheduling, preserving the exact numeric contract.
As a smaller quantified candidate, moving standalone data to short-addressable
locations could remove871.53 mean long-load address clocks (~9.33%) if all such
loads could use that form; stores do not automatically save a cycle under the
two-cycle short-store interpretation. This is only a static opportunity estimate,
not a new layout, demonstrated optimization or stock RAM plan. No code optimized.

## L–N. Practicality and remaining uncertainty

**CONDITIONAL assessment:** one mono primitive looks comfortably within the
whole-period compute budget in this standalone memory model, including the
18.39% structural upper. This says nothing about unused time in stock firmware.

Ten simultaneous primitives are remotely plausible for average raw arithmetic
(57%), but not qualified for sustained worst-case operation: observed worst uses
97.66% before mixing/filter/effects/worker/interrupt work; structural upper183.86%
cannot prove fit. Exceeding a loose upper does not prove the actual workload
necessarily misses deadlines, but it prevents a conservative feasibility claim.
Twelve copies already exceed the budget at the observed worst. No scheduler/
polyphony implementation or Circuit integration follows.

**MEASURED earlier stock context only:** Phase19C-FULLHELPER's admitted
1F5C/C9D checkpoint paths issued9647 original opcodes each, including caller
JSR (385880 across40 cases). These are structurally qualified helper observations,
not authentic normal audio-block or voice costs. They are not added to these
calculated cycles, and no compatible full stock cycle model exists.

**Biggest remaining timing uncertainty:** actual available stock headroom,
including generator/filter/effects costs, worker activity, DMA/IRQ overhead,
scheduling margin and real memory contention/placement. Clock routing and
device timing correspondence also remain conditional. The short-store table
ambiguity changes the pooled mean by232.31 clocks (~2.49% of best estimate),
but resolving it alone would not qualify ten-voice stock integration.

## O. Single best next step and verification

Next: a separately authorized **standalone scratch-traffic/register-scheduling
optimization**, changing no waveform/numeric contract, followed by the same exact
oracle/reference suite and this timing audit. No optimization is implemented here.

**PASS under the explicit conditional standalone model, gates A–I.** Both full
audits are byte-identical; accounting checks reconcile38,641,041 PCs,
70,228,029 calculated clocks, all block/family/region totals and both rates.
Manual examples check forwarding, hazards, branches, REP/DIV and parallel forms.
All233120 DO backedges /7520 exits are confirmed, first AGU use is safely
separated, output overwrites refused, original inputs/core and native/restoring
source/artifact hashes preserved. No renderer rerun or host timing evidence.

Canonical artifacts under `builds/phase20a-timing/final/`:

- instruction-census.csv, instruction-timing.csv
- block-cycle-estimates.csv, block-instruction-census.csv
- hotspots.csv, voice-scaling.csv, timing-assumptions.json
- branch-audit.csv, native-helper-paths.json, structural-upper-bound.json
- cycle-summary.json, restoring-static-comparison.json, provenance/hashes

Repeat:repeat/; verification:checks/; rate exports:rates/ and rates-repeat/;
manual excerpts/visual evidence:documentation/. Analyzer and verifier are under
plaits/poc/timing/. Reproduction commands are in dsp56300-timing-model.md.
