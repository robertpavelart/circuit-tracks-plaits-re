> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20B3 — original P:657 input record

2026-10-07. Overall **PARTIAL**; numerical preparation and seam replay
**REFUSED before CPU execution**. The source binding remains the authored
`Rudi saw poly`, logical bank0/slot0 from Phase20B2. This is not an observed
device selection or a recovered runtime invocation. No firmware is changed.

Canonical evidence: `builds/phase20b-inputrec/final-v3/`.
`p657-instructions.csv` is freshly decoded from the original payload;
six focused ranges are independently decoded and compared with the existing
byte-checked original instruction listing. ARM helpers are byte checked against
the original BIN. Scripts: `plaits/seam/inputrec/recover.py`, `verify.py`.

## Structure and lifetime

**VERIFIED code / CONDITIONAL bank0,slot0,linear AGU values:**

|Input|Origin|Selected relation|
|---|---|---|
|Y0|2A5..2A9|X control base2D5|
|Y1|descriptor+3,2AA|Y secondary voice pointer131|
|Y2|X298 at2AB/2AD; ARM2743C|Y shared modulation contextA0|
|Y3|294/298|Y temporary base7C|
|X29|2A0, event cursor increment|prepared coefficient base57B|
|X2B|299 N7=44(hex),2A1/2A2|prepared tail5BF|

P657..65E advances the X control pointer by25(hex). Two structures follow:

* X:[2D5,2FA): **37 bank-shared control words**, consumed in order after691.
* X:2FA: row count; X:2FB starts **five-word modulation rows**.

Row fields at `2FB+5*i`: Y source1 base, Y source2 base, absolute Y factor
pointer, smoothed amount, absolute Y accumulation destination.
67D/67E set N5=N6=Y1−131, giving zero for slot0. Source reads use
`Y:(source+N5/N6)`; the factor and accumulation destination are absolute.
There is no claim that this is one fixed-width per-voice serialized record.
The pointer fields and amounts are bank shared; source offsets select a voice.

**VERIFIED:** ARM27A10 constructs all20 rows, writes source/factor/destination
fields, stores20 amount targets atX3D0..3E3, then requests count20 through
2872C/286BC. 2872C can defer a count reduction relative to its retained pending
count; 286F6 completes deferred publication. No nonzero-depth compaction occurs
in these inspected helpers. Count20 is a constructor request, not an observed
P657 invocation. Count/sentinel retention remains **UNRESOLVED**.

**BOUNDED-PROOF, count20 / linear addressing:** initial reads at67F..683,
then five X reads per iteration at688,689,68B,68C,68E consume105 words,
X:[2FA,363). Each iteration consumes the current destination and preloads the
next row's four header fields. Last lookahead isX35F..362. 68F still reads
the next source1's Y word on the final iteration. ARM286E4 writesX35F=0,
but the unresolved normal retention invariant cannot be replaced by that
writer alone. Last-row R6/R7/amount preloads are not dereferenced in another
iteration. No fabricated sentinel, skipped source read or zero-count DO policy.

## Selected authored values and corrections

**VERIFIED source bytes:** filter content60..68 is
`00 0A 01 01 0D 00 02 36 4F`.
The existing Phase20B2 expected prepared fields0/1/5/5 are preserved.

|DSP input|Patch ID / content offset|Raw file|Original conversion/sink|Numerical active word|
|---|---|---:|---|---|
|X2E7|1F /61|10|2794A: corrected value<<24; transport upper24|UNRESOLVED|
|X2E8|24 /66|2|27964 via3B8BA; multiply01020408, transport upper24|UNRESOLVED|
|X3E7→X2E9|22 /64|13|2797E via282E4; AAAAAB*v+B7FFFFEC, runtime high-half addition;1AC1/1AC3→1B89 smoothing|UNRESOLVED|
|X2EA|26 /68|79|27998 via28314; subtract64, signed8,805A340 byte lookup and sign-dependent multiplier|UNRESOLVED|
|X2EB|23 /65|0|279B2 via3B8BA; multiply01020408|UNRESOLVED|

**VERIFIED:** these IDs have reverse correction indices22,21,20,24,23
respectively. Original360B2 obtains the raw getter value then adds a signed
runtime correction halfword, clipping to0..127 if correction is nonzero.
The halfwords are not present as active numerical state in the selected patch.
Raw0 in content65 therefore does **not** prove activeX2EB=0. Raw79 denotes
nominal+15 after subtract64 in28314, not the+49 depth of modulation slot0.

The complete37-word consumer map and known direct/helper/smoothing producers
are exported in `p657-field-provenance.csv`. Smoothed destinations include
2D5+4*i←3CA+i,2D6+4*i←3CD+i,2D8+4*i←3E4+i,2E1..2E6←3C4..3C9,
2E9←3E7,2EE←3E8,2F1←3E9 (1A99..1ACB→1B7B/1B89).
Unclosed delegated producers are marked **UNRESOLVED**, not treated as defaults.
X2F8/2F9 originate in note-associated envelope helpers. A complete numerical
binding of every consumed word is not claimed.

## Modulation routes

**VERIFIED:** selected20 raw rows are exported individually.
Row0=`[4,4,113,12]`, row2=`[7,0,68,12]`; all others=`[0,0,64,0]`.
Nominal signed depths are+49,+4,0. Their corrected targets and smoothed
amounts remain **UNRESOLVED**; even nominal0 is not silently declared active0.

Original2853C ADR points to0802900C: source0→Y17D,4→Y17C,7→Y126.
2855C/285B8 use the table at0805B5E0 (literal08028FF4):
destination12 has bytes`15 02`, destination0=`00 01`.
Thus bank0 destinations areY91 andY7C respectively. Destination/source IDs
bypass correction (reverseFF); only depth values in these rows are corrected.
27A76 writes factor pointerY10. Target amountsX3D0+i become retained
`X2FE+5*i` via1A70..1A77 and1B89, an old-value/target fractional MAC smoother.

66F reads priorY17C;671 readsX5C3;674 writes its smoothed replacement;
675 setsY17D fromY10. Row0 then usesY17C twice; row2 usesY126 andY17D.
No source snapshot or smoother epoch is available. Naming these sources
as particular LFO/envelope types is unnecessary and not asserted.

**BOUNDED-PROOF / CONDITIONAL:** 676/678 clears31 wordsY7C..9A. The
selected original row destinations only include7C and91. Therefore the
modulation terms atY8F andY90 are zero immediately after690, if pointer/mode
retention, count bounds, and no intervening alias hold. This is proved routing
within that path, not an executed address trace or global alias-ownership proof.

## Exact output producers

After691, R0 is2D5. Three four-word lanes and six more words leave R0=2E7
and R4=8F. Every full-accumulator transfer below retains the original limiter/
scale dependence; these are instruction expressions, not floating equations.

* **Y8F,6D9:** loadX2E7 intoA; add oldY8Fmod; CLR A IFMI; storeA.
* **Y90,6DE:** loadY90mod intoA; addX2E8 preloaded6D8; CLR A IFMI; storeA.
* **Y91,6ED:** loadX2E9 intoA; addY14; MAC(Y131,X2EA);
  MAC(Y135,X2EB); addY91mod; CLR A IFMI; transferA→X0;
  MPY(Y13,X0)→A; ASL A; storeA.

The6E2 parallel move readsY131 and postincrements R5 by2;6E3 advances
another2;6E4 readsY135. Both inputs are voice-state terms, not patch literals.
68A and68D transfer accumulator results through24-bit X1 between fractional
products;68E MAC uses the **old amount**, while preloading the next amount.
Do not evaluate the route as an untruncated host product.

Downstream:47F/481 preparesX5AD fromY8F;483..48B derivesX5AE/X5AF fromY90;
48D..498 derivesX5B0 fromY91 (the previously verifiedX2AB=0 case).
Further gain/coefficient history and mode conditions still apply.

Other source reads includeA0..A2 copy,A2/A3/A6 lane terms,Y148..14C
per-slot parameters,Y131/Y135,X40 and constantsY10/12/13/14/15.
P657 emits preparedY7D..9A, derived tailY9B..9E andX5BF..5C1.
The initial scratch copy writesY179..17B. The function returns at758.

## Admission and reproduction

No qualified event, retained histories, material modes, AGU or saved caller
prefix: no chosen checkpoint. The matrix retains0/1/5/5 as **CONDITIONAL
source-backed expected fields**, rather than numerical replay observations.
`preparation-traces/` and `stock-seam-traces/` contain explicit refusals,
zero executed instructions and null trace/cycle measurements.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B plaits/seam/inputrec/recover.py --output-dir builds/phase20b-inputrec/new-report
& $py -B plaits/seam/inputrec/recover.py --output-dir builds/phase20b-inputrec/new-repeat
& $py -B plaits/seam/inputrec/verify.py --suite-dir builds/phase20b-inputrec/new-report --repeat-dir builds/phase20b-inputrec/new-repeat --output-dir builds/phase20b-inputrec/new-checks
```

Fresh destinations required. Original SYX/BIN/DSP and prior renderer/seam
artifacts are checked; no refetch, Components launch or full boot expansion.

## Phase20B4 — macro context and corrected frequency target source

See rudi-saw-poly-differences.md andproject0-event-context.md. All20 route
literals/assignments are identical in the cached patch, but stored macro values
change filter/envelope controls. Under complete original stored-value recompute,
X2E8 transfer020408→2C58B1 andX2EA1C0000→0CAAAA are nonconvergent.
This is a conditional control-boundary calculation, not an admitted event.

Correction to the earlier X3E7 conversion description:282F4 PC literal28750
is805BCD0; LDRH[IP+4] reads immutable805BCD4=590C. The addend is fixed
flash data, not an unresolved runtime halfword. ConditionalX3E7 targets are
19B6AA→2FB6AA; currentX2E9 remains smoothed/history-dependent. Canonical
new evidence:builds/phase20b-projectassoc/final-v2/frequency-target-provenance.json.
No P657 structural restart; event/mode/history admission still incomplete.
