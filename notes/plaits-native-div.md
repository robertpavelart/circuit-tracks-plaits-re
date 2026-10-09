# Phase 20A-DIV — native ratio qualification and standalone comparison

## Phase 20A-REGOPT update — helper unchanged, caller optimized (2026-10-07)

**IMPLEMENTED / TESTED:** register/scratch scheduling variant retains the exact
18-word native helper,21 DIV iterations,49 observed helper cycles. Main program
442P;7 persistentX,3 spillX+16 work registers,32 outputY,0LUT, stack3.
Original43 cases and9 focused cases,388096 samples/all seven block states,
match golden/oracle exactly and repeat. **CALCULATED / CONDITIONAL:** matched
mean7270.1787 clocks (-22.1511%,STRONG), all-validated peak12670,upper12682,
structural23902. Native/restoring sources/artifacts remain unchanged.
Report:[plaits-register-optimization.md](plaits-register-optimization.md).
No stock allocation, firmware changes or integration; feasibility **UNRESOLVED**.

## Phase 20A-TIMING update — offline cycle model complete (2026-10-06)

**SOURCE-DERIVED / CALCULATED / CONDITIONAL:** native helper49 cycles in the
observed suite (52 including callerJSR), general valid ratio49..82; DIV1/iteration,
REPsetup5, ANDI3 and final accumulator-transfer stall1. Unchanged renderer
best8035..16001 clocks/32,mean9338.8336. Observed-path upper16013;
conservative valid-API structural upper30123 under private-memory/noIRQ/noDMA
assumptions. Conditional163840 budget:one mean5.70%,worst9.77%,structural18.39%.
Ten observedworst97.66% before stock work; integration remains **UNRESOLVED**.
No code/algorithm/oracle change or rerender. Reports:
[plaits-cycle-audit.md](plaits-cycle-audit.md),
[dsp56300-timing-model.md](dsp56300-timing-model.md).
Canonical timing exports:builds/phase20a-timing/final/, repeat/, checks/, rates/.
The earlier next-step statement below is now completed; next is a separately
requested standalone scratch/register-scheduling optimization, not integration.

2026-10-06. **IMPLEMENTED / TESTED / MEASURED:** the compact native DIV helper
is the preferred standalone VariableSaw variant. The complete unchanged test
suite passes twice with exactly the restoring implementation's samples and
block states. No oracle adjustment. Circuit feasibility remains **UNRESOLVED**.

Canonical evidence: `builds/phase20a-div/final-compact/`, `fixtures-compact/`,
`checks/`, `comparison/`. Earlier 22-word candidate, probes and failed exploratory
checks are retained separately. Immutable restoring reference remains under
`plaits/poc/` and `builds/phase20a-plaits/final/`; its source and artifact hashes
still match. New code is under `plaits/poc/div/`.

No hardware, firmware patching, stock RAM allocation, Circuit image execution,
original/ changes, MIDI/SysEx, model switching, polyphony or P:0x9DD integration.
Circuit ownership/ABI investigations remain frozen.

## A. DIV semantics and evidence

**SOURCE-DERIVED:** pinned DSP56300 Family Manual Rev.5, printed13-52..13-54
(PDF292..294); ROL printed13-165 (PDF405). Manual SHA256:
`b2e8e346fe55b05d20ad0e6bc03d45fd1e080d46d9a9cd9540271c0c37f5a31e`.
Local extracts/provenance are under `builds/phase20a-div/documentation/`.

- DIV source is signed24 fractional X0/X1/Y0/Y1. Destination is full56-bit
  A/B, containing a positive48-bit fractional dividend sign-extended to56.
- Valid fractional division requires dividend magnitude < divisor magnitude;
  divisor must be nonzero. Positive divisor is sufficient for this helper.
  Common operand scaling cancels; no leading-zero normalization is necessary
  after separating the integer part and establishing remainder < denominator.
- Each DIV shifts the full accumulator, inserts old C at bit0, then adds or
  subtracts the sign-extended divisor at bit24 according to prior operand signs.
  New C is1 when the new accumulator sign is nonnegative. Partial signed
  remainder occupies the high portion; delayed quotient bits occupy A0/B0.
- C holds the newly computed bit; it is inserted only on the following shift.
  For this contract,21 DIVs plus final carry insertion produce21 fractional
  bits. A0 after21 iterations holds20 useful bits; move A0 to A1, then ROL
  inserts the last bit. ROL itself rotates only accumulator bits47..24, not56.
- DIV changes C and V; V records a sign change caused by the left shift,
  and sticky L is set if V is set. S/E/U/N/Z are unchanged by DIV itself.
  Other helper instructions change flags; CCR is clobbered in the helper ABI.
- There is no saturating DIV result or division-by-zero trap to rely upon.
  Invalid input is outside the fractional-division precondition. The helper
  explicitly returns0 for denominator0 without issuing DIV. Negative inputs
  or n>=4d are outside its API, not alternative saturation behavior.
- The nonrestoring partial remainder would require correction if returned;
  this helper discards it. Its quotient uses floor, not rounding or saturation.

**UNRESOLVED manual editorial inconsistencies:** the text says N iterations
for N bits, then says sixteen for24 bits; it also refers to39-bit/bit39/bit15
quantities amid the56/24-bit definition. These conflicting fragments are not
used as implementation rules. The consistent56-bit operational steps and
CCR definitions were tested against the sealed interpreter and independent
bit recurrence. This qualifies offline behavior, not physical DSP validation.

## B. Helper architecture and exact contract

**IMPLEMENTED:** positive signed24 X0=n, Y0=d; same output as fallback:
`A1 = floor((n << 21) / d)`, for n>=0, d>0, n<4d, n,d<=0x7FFFFF.
Result is Q3.21, representable0..0x7FFFFF. Inputs share their original scale.
X0/Y0, address registers/modifiers are preserved; A/B/X1/CCR are clobbered.

1. Clear B while loading d into A; TST d while moving n into A. A zero
   denominator branches to an explicit zero result/RTS.
2. Repeated compare/subtract computes k=floor(n/d) in B (0..3), leaving r=n-kd
   in A1 and A0=0. Shift B by21 to retain k*2^21 in registers.
3. Clear C explicitly; REP21 issues DIV Y0,A. No scratch writes or tables.
4. Move A0 to A1 without altering C; ROL A with parallel B1->X1 inserts C.
   Add X1 into A, return. All other VariableSaw instructions remain unchanged.

**SOURCE-DERIVED proof:** for r<d, nonrestoring recurrence is
R_j=2*R_(j-1)-d when R_(j-1)>=0, otherwise2*R_(j-1)+d.
Bit b_j=[R_j>=0]. After21 steps the stored quotient contains b1..b20;
appending b21 gives floor(r*2^21/d), including exact-divisibility boundaries.
Adding k*2^21 gives floor(n*2^21/d). |R_j|<=d; its accumulator placement
and one-bit shift stay far below signed56-bit overflow. Final positive24-bit
result fits A1, so no narrowing saturation is needed. No remainder restoration
or signed-quotient negation is needed in this positive API.

Synthetic standalone helper P:[0x4AA,0x4BC); integer loop0x4AD; fractional
setup0x4B2; REP0x4B4; DIV0x4B5; A0->A1 at0x4B6; ROL0x4B7;
normal RTS0x4B9; zero guard0x4BA..0x4BB. These are not stock Circuit addresses.

**TESTED isolated fixtures:**37,016 cases, each repeated;777,126 DIV iterations
per run independently checked for56-bit accumulator and complete SR evolution.
Exhaustive d=1..64, all0<=n<4d, both incoming C values; targeted fixed-point
rounding/integer boundaries and oscillator-domain extrema;10,000 seeded random
pairs covering the positive signed24 domain; explicit d=0 guards.
Independent integer quotient, C/V/L recurrence, unchanged DIV flags and repeated
exports all pass. Model masks exported sign-extended accumulator to56 bits.
Initial exploratory ROL-before-A0-move produced half quotients; isolated tests
rejected it before any oscillator substitution. Correct ordering is qualified.

## C–G. Resource and compute comparison

**MEASURED**, issued opcodes rather than hardware cycles:

| Item | Restoring | Compact native DIV | Delta/reduction |
|---|---:|---:|---:|
|Helper P words|26|18|-8|
|Complete oscillator P words|708|700|-8 (24 packed bytes)|
|Persistent X state|7|7|0|
|Allocated transient X scratch|44|44|0|
|Helper scratch words read/written|1|0|-1 live word|
|Control input X / output Y|3 /32|3 /32|0|
|Immutable LUT words|0|0|0|
|Peak stack entries / words|5 /10|3 /6|-2 entries /-4 words|
|Issued block minimum|7,632|4,414|42.1646%|
|Issued block mean|9,053.581117|5,138.436303|43.2442%|
|Issued block maximum|16,844|8,956|46.8297%|
|Full7520-block issued total|68,082,930|38,641,041|43.2442%|
|Observed helper opcodes/call incl RTS, excl caller JSR|118..156, mean137.025019|33|75.9168% mean|

The allocated layout is identical: scratch X:[0x80,0xAC). Former helper slot
X:0xAB is unused;43 scratch words remain live. No scratch compaction was made.
Logical data allocation remains86 words, excluding hardware stack/decoder padding.
DIV uses REP rather than the fallback's inner DO, explaining smaller stack peak.
Both retain depth0 after every render call.

General valid native helper cost is **TESTED**33+5*floor(n/d)=33..48 opcodes
including RTS, excluding caller JSR; zero guard5. All283,027 oscillator calls
in this suite have integer part0 and cost33. Calls per32-sample block:
32..80, mean37.636569;21 DIV iterations each,5,943,567 DIV opcodes per full run.
Trace-based counts match instrumentation. Every old/new block has the same
divider invocation count.

The first qualified native candidate uses22P/35..53 opcodes and full oscillator
704P, mean5,213.709441, min4,478, max9,116. It also passes twice exactly.
The18-word helper is the smallest candidate qualified here. Absolute global
instruction-minimality is **UNRESOLVED**; no exhaustive code synthesis claim.
Only helper-local parallel moves/integer counting were compacted.

## H–K. Unchanged numerical and deterministic validation

**TESTED:** original43 cases,7520 blocks,240640 samples per run, unchanged
case/input bytes and unchanged independent integer oracle. Main assembly prefix
is identical; machine words before helper are identical except the final JMP
target relocation. Variable layout, event ordering, ramps, multiplication,
BLEP/integratedBLEP corrections, waveform/pitch/control laws are unchanged.

- Restoring versus native: maximum integer sample difference0, RMS0,
  spectrum similarity1.0; every seven-word block state is identical.
- Native versus independent oracle: all samples and states exact.
- Native versus pinned upstream float: metrics byte-identical to baseline.
  Worst case RMS0.0219730517; maximum point difference1.4145329 in abrupt
  stress; maximum DC difference0.0003376943; peak difference0.0009301901;
  minimum constant-case magnitude-spectrum cosine0.9999439621.
  Existing float/fixed event-timing differences remain openly reported.
- Maximum tested pitch error0.9991969348 cents;48kHz and conditional
  48.046875kHz cases unchanged. The conditional rate is not measured hardware.
- Joint sweeps, bounded abrupt stress, frequency cap and2048 continuous blocks
  pass. Upstream warmed64-versus32+32 maximum difference0.
- Both full native runs reproduce all eight exported files, including complete
  77,282,082-byte issued-PC traces, output/state/write hashes. Float references
  repeat and match baseline hashes. All A–K original acceptance gates pass.
- Invalid frequency rejected before CPU execution; three overwrite refusals
  preserve output. Original SYX/BIN roundtrip, all10 extracted stream/payload
  hashes,183 upstream sources, sealed core and original baseline provenance pass.

The helper's zero guard is never taken in the tested oscillator workload.
No audio playback or hardware was used; WAVs are offline exports with the same
common playback gain and headers as the original suite.

## L–N. Recommendation, Circuit practicality and next step

**TESTED / IMPLEMENTED recommendation:** use compact native DIV for subsequent
standalone studies. Keep restoring generator/oracle/executable/evidence unchanged
as the reference fallback. No numeric reason to retain restoring as the preferred
renderer in this admitted domain. This does not authorize firmware integration.

**MEASURED derived throughput:** at48kHz/32, the observed mean/worst workload is
7.70765 /13.434 million issued opcodes per second for one primitive, compared
with13.58037 /25.266 million previously. A simple ten-copy extrapolation is an
**ESTIMATE**77.08 /134.34 million issued opcodes per second before mixing,
controls, stock work and scheduling; no multivoice implementation was made.
This materially reduces the known divider risk. Actual DSP cycle costs, clock,
memory/pipeline penalties, available stock headroom, P placement, persistent RAM
ownership and output ABI remain **UNRESOLVED**. Circuit readiness remains NO.

**Single best next step:** an offline instruction-cycle/pipeline audit of this
unchanged compact renderer, deriving a defensible worst-case32-sample timing
bound from the pinned DSP manual and full traces. Keep it standalone; no further
optimization or Circuit integration follows automatically.

## Reproduction

Use existing local tools only; every output directory must be fresh. From the
project root, with the already installed Python executable:

```powershell
& plaits/poc/div/build.ps1 -BuildDir builds/phase20a-div/rebuild-new
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B plaits/poc/div/qualify_compact.py --output-dir builds/phase20a-div/fixtures-new --fixture-exe builds/phase20a-div/rebuild-new/div_fixture.exe
& $taskPython -B plaits/poc/div/collect_compact.py --output-dir builds/phase20a-div/suite-new --build-dir builds/phase20a-div/rebuild-new
& $taskPython -B plaits/poc/div/verify_div.py --suite-dir builds/phase20a-div/suite-new --build-dir builds/phase20a-div/rebuild-new --output-dir builds/phase20a-div/checks-new
```

`compare.py` compares any admitted new suite with the preserved restoring
baseline; its canonical report additionally references this phase's canonical
checks/fixtures. Canonical command:

```powershell
& $taskPython -B plaits/poc/div/compare.py --suite-dir builds/phase20a-div/final-compact --output-dir builds/phase20a-div/comparison-new
```

Collector/verifier are narrow adapters of the original suite for the generator,
output root and new resource/trace-size expectations. Test controls, oracle,
reference, metrics, acceptance limits, rates and continuity logic are unchanged.
Both complete old and new evidence sets are hash-verified during comparison.
