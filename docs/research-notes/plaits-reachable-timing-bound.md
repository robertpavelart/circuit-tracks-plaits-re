> Historical experiment scope, not the current global project stop point. [Current state](../CURRENT_STATUS.md).

# Phase 20A-BOUND — legal VariableSaw timing domain

Completed 2026-10-07. **TESTED / CALCULATED:** the unchanged 442-P-word renderer
has a new reset-reachable, DSP-tested maximum of **13,335 cycles/block** in the
pinned timing model. **PROVEN-BOUND / CONDITIONAL:** a conservative upper is
**13,379**, including the existing 12-cycle pipeline allowance. The old 23,902
upper falls by **10,523 cycles (44.026%)**. The 44-cycle gap is 12 intentional
boundary cycles plus **32 UNRESOLVED event-ordering cycles**. This is not a proof
that the search found the global reachable maximum, or that the upper is attained.

No renderer, arithmetic, firmware, original/, core, baseline or upstream code
changed. No hardware, MIDI/SysEx, model switching, polyphony or stock integration.
Canonical exports: `builds/phase20a-bound/final/`. New analysis-only scripts:
`plaits/poc/bound/{domain,search,verify,prove,export}.py`.

## A–D. Variable paths and exact event bounds

**PROVEN-BOUND:** let F=2^22 (phase/frequency), Q=2^21 (amplitude/shape), H=F/4.
Raw frequency words 1..F/2 clamp to 1..H. Target PW clamps to [2*f,F-2*f]; at
f=H it is forced to F/2. Shape is 0..Q. All states considered originate at the
existing reset and advance through real 32-sample blocks. No retained state is
injected. `next` and shape affect amplitude arithmetic but not event decisions.

| Variable path | Exact condition / constraint | Maximum per block |
|---|---|---:|
|Frequency clamp, P:0x203|raw f >= H; forces PW=F/2|once|
|PW lower/upper clamp, 0x216/0x21C|mutually incompatible for f<H|one clamp|
|Frequency/PW/shape carry, 0x25C/26C/27C|error>=32|31 each, 93 total|
|PW event, 0x293/297|high=0 and advanced phase>=PW; sets high=1|8|
|Wrap, 0x2B8|advanced phase>=F, reached with high=1; subtract F, high=0|8|
|Combined event|PW and wrap are if/elif, strictly alternate|16|
|Event sign, 0x345|PW additions vs wrap subtractions|one sign/event|
|Naive branch, 0x36B|phase>=PW vs phase<PW|one/sample|
|Ratio denominator guard, 0x3AA|zero denominator|unreachable in legal state|
|Ratio integer loop, 0x3AC|n>=d|normally 0; at most two k=1 calls in exception|

Each sample has exactly one naive waveform ratio call. Each event adds three:
event location plus two frequency/PW normalizations. **Exact legal total:32..80
calls/block**, not 32*four arbitrary helper calls. Both endpoints are DSP-tested.
Shape zero/one does not skip correction arithmetic. Notch BLEP and triangle
integrated-BLEP are two correction kinds at the same event, not separate events.
There are at most 32 correction pairs /64 current-next individual terms/block.

PW and wrap cannot happen as two events in the same sample. Adjacent PW/wrap
events are possible: the tested tiny-frequency upward-ramp fixture demonstrates
them. Separate wraps are at least four samples apart. Current and next correction
terms overlap across adjacent samples exactly as in the unchanged oracle.

Every conditional instruction and its constraint is in branch-constraints.csv.
No branch based on an amplitude/shape result was omitted; the compact state model
includes all three ramp carries, high/PW/wrap, naive side and helper integer parts.

## Exact phase/ramp proof

**PROVEN-BOUND:** for every interpolated field c and j=1..32,

`c_j = c_0 + floor(j*(c_target-c_0)/32)`.

Write delta=32*a+r, 0<=r<32. The error accumulator implements this identity;
there are exactly r carry branches in the block. The script exhaustively checks
the remainder identity and representative signed quotient transitions; algebra
handles arbitrary quotients. The target is reached exactly at sample32.

Both endpoint PW bounds survive interpolation **exactly**, not with a one-word
tolerance: if continuous p>=2*f, floor(p)>=2*floor(f); if p+2*f<=F,
floor(p)+2*floor(f)<=F. Thus **2*f_j<=p_j<=F-2*f_j** throughout the ramp.
In particular p_j>f_j>=1, and both slope ratios are in (0,1/2].

For monotone linear frequency ramps, **f_j<=2*f_(j-1) for j>=2**. In the
increasing case write f_j=f0+j*a+floor(j*r/32); the carry increment is <=1
and f0>=1. The decreasing case is immediate. When high=0, retained phase is
strictly below previous PW. A PW crossing at j>=2 therefore has advanced phase
at most `F-2*f_prev-1+f_j <= F-1`. Ordinary wraps leave phase<f_j<PW.

Only sample1 can defer a wrap by taking a PW event beyond F. This requires
f1>=2*f0+1, hence **f0<H/33**. Sample2 necessarily wraps, leaving residue
less than 2*f2 and strictly below PW2. Because f2<=H/11 in this exception,
the residue is also <H. Subsequent samples obey the ordinary induction. At
every block boundary phase is in **[0,F)** and high=0 implies phase<PW;
previous_PW equals current PW. Reset satisfies these invariants.

Let S=sum(f_j). Since f_j<=H, S<=8F and boundary phase<F; therefore **W<=8**.
The wrap residue is <H even in the exceptional case. Three later advances
total at most 3H, still below F, proving the four-sample wrap separation.

Event alternation gives P<=W+1. To exclude P=9, first note it requires W=8,
initial high=0 and final high=1. W=8 implies S>7F. Also

`S <= (31/2)*f0 + (33/2)*ft <= (33/2)*(f0+ft)`.

Consequently f0+ft>14F/33 and min(f0,ft)>23F/132>F/32. A PW ramp increases
by at most F/32 per sample. In this eight-wrap class phase-PW therefore grows
strictly between wraps: after the last PW crossing it cannot retreat below the
final PW. This lemma is necessary; high=1 alone does not generally imply
phase>=PW during an arbitrary fast PW ramp.

With P=9 the initial phase<p0 and final phase>=pt then require

`S >= 8F + pt - p0 + 1 >= 7F + 2*ft + 2*f0 + 1`.

Combining with the ramp-sum bound requires
`(27/2)*f0 + (29/2)*ft >= 7F+1`, impossible because f0,ft<=F/4 make its
left side at most 7F. Thus **P<=8 and P+W<=16**. Constant quarter-rate
operation attains P=W=8 and 80 ratio calls after legal preparation.

## Ratio domains, including the rare exception

**PROVEN-BOUND:** PW event n=advanced_phase-PW>=0 and
d=previous_PW-PW+f. Since prior phase<previous_PW, n<d; thus d>0 and k=0.
Ordinary wrap t is residue/f<1. Naive ratios are below one whenever phase<F.
Both normalization ratios are <=1/2. The zero guard and k=2/3 paths cannot occur.

On the first-sample deferred PW event only its naive ratio can be in [1,3/2);
the next wrap t can be in [1,2). There are **at most two k=1 calls**, each
adding 11 modeled clocks. Other ratios are fractional. This is not assumed
absent just because the previous 52-case suite never exercised it.

For this class f0<H/33 and
`S <=15.5*f0+16.5*ft <4.25F`, so W<=5 and P<=6, total events<=11. Its
separate conservative upper is **11,603**, including the extra22 cycles.
It cannot dominate the ordinary 13,379 bound. The tested fixture is:
reset -> [f=110000,PW=F,shape=0] -> [1,F,0] -> [H,F/2,Q-1]. It starts the
last block at phase4170102, high0, f1 and PW4194302. Both k=1 calls occur;
PW/wrap are adjacent; the block costs10,837, with62 ratio calls and5+5 events.

## E–G. Bound construction and search

**CALCULATED:** exact frozen instruction/interlock costs give these sample costs
before interpolation carries, with the 49-cycle fractional helper:

| Legal path | Cycles |
|---|---:|
|high=0, no event, lower naive|200|
|high=1, no event, lower /upper naive|192 /204|
|PW event, upper naive|581|
|Wrap, lower naive|552|

All three carry paths add exactly10 cycles each, independently of the later
event path. This is checked over all104 enumerated branch/carry cost profiles.
The finite 32-step DP exhausts high flag, event counts and wrap cooldown with
P,W<=8. It includes only the appropriate naive side for PW/wrap/low no-event.
It visits1863 states in the ordinary class and1623 in the exceptional class.

Its main-body base upper is `8*581+8*552+16*204 = 12328`.
Therefore **13379 = 12328 + 93*10 + 106 setup +3 exit +12 boundary**.
The count/carry/setup maxima are individually legal and occur together in the
tested maximum; the remaining conservatism is the distribution of the 16 no-event
samples between high and low. The DP is an **aggregate relaxation**, not an
exhaustive exact-state reachability certificate. Its maximizing wrap/PW ordering
is not claimed reachable. No general-helper k3 or 32-events-per-block maxima are
quietly retained. **UNRESOLVED:**32 event-ordering clocks after the boundary
allowance; claiming a globally tight/attained13,379 would exceed the evidence.

The old normal-partition bound decomposes reproducibly:

| Tightening | Bound | Removed cycles |
|---|---:|---:|
|Old general helper/all CFG branches|23902|—|
|Fractional helper49 instead of general82|19678|4224|
|Exclude both clamp branches together|19673|5|
|93 carries instead of96|19643|30|
|Bound/couple events, naive paths and wrap separation|13379|6264|

The first step alone would be unsafe globally; the separate exceptional11,603
class closes that gap. Total removal10523. Old bound failure did not prove actual
deadline failure; it independently maximized mutually inconsistent event/helper
paths. This phase closes those large sources of looseness.

**TESTED / CALCULATED:** seeded search20002001,50,000 trials,375,000 target
evaluations plus legal preparation blocks. It retains every improved maximum
and the exact reset history. The best witness arose at trial685 after13 blocks:
initial [phase3521130,high1,f1048545,PW2097153,shape0], target raw
[1048544,4194302,2097151]. The PW clamps to2097216; ramp remainders are31/31/31.
It uses8 PW events,8 wraps,80 ratios and **13,335 clocks**,8706 issued opcodes.
This is665 clocks above the previous stress maximum. Mean7270.1787 stays the
original43-case matched-suite mean, not the biased adversarial mean.

All nine search records, the exception and the32-call minimum fixture were
executed twice:11 cases,91 blocks,2912 samples. Every output and all seven
retained words match the unchanged integer oracle exactly; full PC trace
matches the compact model, and the existing instruction timing calculation
matches each block. Repeat files/traces are byte-identical. The program hash
is unchanged: e774502b36f3ad9ddc303a04da0cce566677203a761c04e72c6c313ad7a0fbc5.

The compact model was also qualified against **all existing52 cases /12128
blocks /388096 samples**: exact full PCs, phase/high/control states and block
cycles, without rerendering or repeating liveness. No observed input violates
the domain lemmas. Proof is algebra plus finite cost DP; passing traces alone
is not the proof. Search is adversarial, not exhaustive over full24-bit states.

Abrupt ramps are more expensive than steady controls: they can retain16 events
while adding93 carries (930 cycles), as the witness shows. A zero-delta steady
control block has no carry cost. The steady quarter-rate prepared case costs
12,390. Frequency/PW/shape ramps do not raise the 16-event bound; they change
event ordering and add interpolation cost. No algorithm optimization occurred.

## H–N. Raw scaling and gates

**CALCULATED / CONDITIONAL:** same246MHz/48046.875Hz model,163840 clocks per
32 samples, private zero-wait P/X/Y, resident stack, no IRQ/DMA/shared bus.
Short stores cost2 under the retained manual-table interpretation. Detailed
DSP56300 tables are still a device-family assumption for DSP56724. These are
emulator instruction traces with calculated cycles, **not silicon measurements**.
No finite unconditional Circuit bound or stock cycle headroom is established.

| Copies | Reachable cycles /% | Derived upper cycles /% | Remaining at upper |
|---|---|---|---:|
|1|13335 /8.14|13379 /8.17|150461|
|2|26670 /16.28|26758 /16.33|137082|
|4|53340 /32.56|53516 /32.66|110324|
|8|106680 /65.11|107032 /65.33|56808|
|10|133350 /81.39|133790 /81.66|30050|
|12|160020 /97.67|160548 /97.99|3292|

Ten conceptual copies (1+1+4+4): mean44.37%, reachable81.39%, upper81.66%.
Remaining at upper **30050 cycles /18.34%: TIGHT RAW MARGIN**. The reachable
estimate leaves30490 /18.61%; adding its12/copy boundary leaves30370 /18.54%.
The old structural percentage145.89% is superseded for this legal domain.

One/two mono generators are comfortably within the **raw generator compute**
budget; a four-copy bank is plausible with67.34% raw margin. Eight copies have
34.67% **USEFUL RAW MARGIN**. Twelve leave2.01% and are **INSUFFICIENT RAW MARGIN
FOR COMFORT**. Ten merits further evaluation, not a ten-voice Circuit claim.
No MIDI-track audio hosting, scheduling or polyphony implementation is implied.

Confidence is high in the derived bound **within the stated model**, with the
explicit32-clock reachability slack. Stock workload, memory ownership/placement,
caller/IRQ register preservation, dispatch/mixing/filter/effects, contention and
physical clock remain **UNRESOLVED**. A further renderer optimization is not
required just to fall below the raw budget. It may be needed if subsequent stock
workload/ABI costs consume the tight18.34% ten-copy margin.

## O. Single best next step and reproduction

**Single best next step:** an explicitly scoped, offline stock P:0x9DD seam/ABI
replay and stock workload accounting, before any ten-voice claim or integration.
Measure the retained-register/caller preservation and remaining stock cost
against the30050-cycle ten-copy raw allowance. This phase does not execute it.
One/two/four-copy resource paths can be evaluated alongside the conceptual ten;
no automatic reduced-polyphony design or further code optimization follows.

Use fresh output paths. Existing wrapper destinations must remain inside
phase20a-regopt; verify.py copies its new evidence into phase20a-bound, preserving
the executable and its destination guards. No new build/install is needed.

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B plaits/poc/bound/search.py --output-dir builds/phase20a-bound/search-new --trials 50000
& $taskPython -B plaits/poc/bound/verify.py --output-dir builds/phase20a-bound/verify-new --search-dir builds/phase20a-bound/fixtures
& $taskPython -B plaits/poc/bound/prove.py --output-dir builds/phase20a-bound/proof-new
& $taskPython -B plaits/poc/bound/export.py --output-dir builds/phase20a-bound/export-new
```

export.py reads the frozen final proof/replay artifacts; its reports reproduce
byte-for-byte with unchanged sources/inputs. Fixture history is retained in
fixtures/witnesses.json and adversarial-cases.csv, including both exception ratios.
Deliverables: event-domain.json, branch-constraints.csv, ratio-call-bounds.csv,
adversarial-cases.csv, reachable-cycle-maxima.csv, tight-cycle-bound.json,
voice-scaling.csv, provenance.json, hashes.json. Full replay:verified-final/;
finite proof:proof-final/; deeper search:search-deep/. Earlier exploratory reports
are retained and clearly superseded, not overwritten.
