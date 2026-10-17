> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 19C-P204B — count and destination-record provenance

2026-10-06. **Result D: positive-count normal reachability remains UNRESOLVED.**
No recovered NORMAL Selection0 path publishes a positive raw count to X:35F
and constructs the five-word records consumed by P:203A/204B. Absence of a
publisher does not establish result A (always zero). Neither a bounded positive
normal destination set nor a normal collision witness was recovered.

**New VERIFIED / BOUNDED-PROOF findings:** all recovered direct1B89/1B7B paths
feeding store1B90 exclude X35F and the prospective compiled-record window
X[360,3C4) under their recovered counts/modifiers. The3C4 address is an X source,
not that helper's output. The DO count is latched into24-bit LC once; a later
count-cell store cannot change the current invocation by itself. Six fixed
scalar-read arguments exclude the35D precursor of a saved-cursor count alias.
Unknown normal argument/order/foreign-state domains remain explicit.

Strictly offline. No hardware, MIDI/SysEx, network, app launch, flashing, firmware
patching, original/ edits, positive35F seed, fabricated destination records or
Plaits implementation. **0 DSP/ARM CPU instructions executed in this phase.**
Existing zero-count/calibration traces are preserved as prior evidence and were
not rerun. The asset branch is frozen; its report hashes were checked without
reopening its analysis. No new generic344-indirect-store census was performed.

Canonical evidence: `builds/phase19c-p204b/final-v4/`, `final-v4-repeat/`,
`checks-v4/`. Earlier final/v2/v3 exports/checks remain intermediate evidence.
Producer `tools/ct_p204b_provenance.py`, focused static verifier
`emulator/tests/verify_p204b.py`. All reviewed original DSP/ARM instructions are
byte-checked against preserved firmware; ISA evidence uses the existing pinned
DSP56300FM.pdf, printed5-21 and13-56..58 (PDF pages101,296..298).

Addresses below are hexadecimal. P: denotes DSP program word address. Bare
ARM addresses in chains omit common prefix0x080; memory words retain X:/Y:.

## A. Complete instruction-supported schema

Under retained linear M0 table walking:

| Offset / X word | Register and readers | Instruction-established role | Producers |
|---|---|---|---|
|+0:360+5*k|R5 at203B/2044; Y read203F/204A|Y source pointer, indexed by N5|INIT2788→0; structured normal producer not recovered|
|+1:361+5*k|R6 at203C/2046; Y read2042|Second Y source pointer, indexed by N6|Same initialization; normal provenance UNRESOLVED|
|+2:362+5*k|R7 at203D/2047; Y read2045|Unindexed Y multiplicative-factor pointer|Same initialization; normal provenance UNRESOLVED|
|+3:363+5*k|X0 at203E/2049; MAC2049|Coefficient multiplied by Y1 into B|Same initialization; normal provenance UNRESOLVED|
|+4:364+5*k|R4 at2043; X read2048/store204B|Absolute X read/modify/write destination|Same initialization; normal provenance UNRESOLVED|

`record-schema.json` includes initialization, every recovered local reader,
writer categories and the missing global reader/writer closure for each field.
No musical semantic names, active voice count or initialized record destination
is inferred from those roles. Valid private service5E writes can clear any of
these selected private words, but do not supply a recovered normal builder.
Effective SHI/foreign computed aliases remain unclosed for every field.

P:203A loads X35F to X1;203B..203E prefetch the first four fields.203F reads
the indexed Y source even if N=0.2040 starts body2042..204B. Each iteration:

1. 2042 reads the second indexed Y source;2043 multiplies the two and loads
   current destination R4.
2. 2044 loads next R5.2045 transfers A to X1 and reads the current Y factor.
   2046 multiplies X1 by that factor while loading next R6;2047 loads next R7.
3. 2048 loads B from current X:(R4), transfers A to Y1.
   2049 adds the current X0×Y1 term to B while loading next X0.
4. 204A prefetches the next indexed Y source;204B stores B back to X:(R4).

The accumulator-to-register transfers retain ISA scaling/limiting semantics;
this establishes a weighted product accumulation, not a named synth parameter.
The last iteration still loads four words of the next record. For hypothetical
N=20 these are X[3C4,3C8), which is separate smoothing-source state. They are
not proved guard records or an enforced20-record capacity.

**VERIFIED:** one unindexed24-bit X store per active record. There is no R4
postincrement or length field at204B; M4 does not alter that unindexed address.
The exact set, if positive normal records were established, would be
`{d_k | k=0..N-1}`, with `d_k=X[364+5*k]` under linear M0. It is not a continuous
interval merely because count N is positive.

## B–F. Count, record and destination producers

`count-writers.csv`, `record-writers.csv`, `destination-domains.csv` distinguish
recovered writers/capabilities from unresolved aliases. They are not a claim
that every computed normal writer has been enumerated or excluded.

| Path | Class / recovered value | Count/record conclusion |
|---|---|---|
|P2788 from25DE→2779|**INIT-ONLY**, zero over X[0,6000)|Count and all prospective record fields0 immediately after completed clear|
|ARM286E4→292F8→P19D|**NORMAL PARAMETER**, r1=0 at286E0|Nominal35F+172*bank; bank0 writes0 to35F, bank1 to4D1|
|ARM269E4→26A9A→292F8→P19D|**SERVICE-ONLY**, private-byte upper24=0|Accepted count/record private starts can be cleared; no direct positive publisher|
|P19D,156→198/199|Normal/service transport; **UNRESOLVED** effective normal endpoint|Received X0 to saved X10 when X11.bit15 clear; possible address domain not an attained positive witness|
|P1B90, recovered direct callers|**BOUNDED-PROOF**, arithmetic A|All reviewed count/modifier domains exclude35F..3C3; unknown entry/foreign count remains separate|
|P1F97|Prior cursor/helper **BOUNDED-PROOF**|Initialized retained cursor intervals exclude count/table; normal parent and foreign preservation UNRESOLVED|
|P204B self/foreign alias|**NORMAL AUDIO** structural consumer; positive body state **UNRESOLVED**|Destination field not recovered; cannot be first positive35F writer from zero/zero-skip entry|
|Mailbox/table jobs, worker/other indirect context|Reviewed exclusions plus **UNRESOLVED** residual state|No count-specific positive publisher or coupled record constructor recovered|

Field initialization0 applies inside the completed clear's X[0,6000), including
the prospective20 positions. It is not initialization proof for unbounded k or
for table addresses beyond that extent.

**Absolute DSP writes:** inherited byte-checked canonical ledger has no absolute
X35F writer and no absolute write into prospective X[360,3C4). No new broad
operand scan is substituted for indirect closure. Selected existing sites are
reused in `scoped-alias-evidence.json`. Worker private addresses are not merged
with channel0 private X without physical/shared mapping evidence.

**NORMAL parameter family:** all1500 existing nominal scalar endpoint rows were
reprojected to count/prospective records. Only the delegated286E4 zero-count
endpoint intersects; no compiled-record field setter. This excludes that
recovered nominal family, not actual cache-hit/interleaved endpoints universally.
A redirected zero write remains zero wherever it lands; it is not a first
positive publisher. General nonzero SHI data remains a separate obligation.

### Distinguish the neighboring source table

ARM27A10 writes20 source entries at `2FB+172*b+5*i+{0,1,2,4}`, b0/1,
i0..19, plus a separate3D0+172*b tail. The last bank0 source word is **35E**.
Field3 is updated by DSP1B90's source-table smoothing path, with last address
**35D**. Neither writes compiled records beginning360 or count35F.

27AE2 supplies count20 to2872C→286BC.286DA publishes it to **2FA+172*b**;
286E0 clears r1, then286E4 writes **0 to35F+172*b**. Thus the recovered positive
source count20 is expressly not the compiled-consumer count. No copy/compilation
from that source table into360 was established.

### New shared-helper caller closure, within explicit bounds

There are two recovered direct source calls1A77/1A90 and nine caller sites into
wrapper1B7B. Its first JSR at1B82 calls1B89; then it restores N0, adds172 to saved
R1/source pointers and falls through1B89 for the second bank.1B90 writes through
**R1**.1B8C reads X through **R4**. Consequently1A99's R4=3C4 is a source address,
not a compiled-table destination. This resolves a specific apparent producer.

| Caller | First output base | Count | Stride | Second bank |
|---|---|---:|---:|---|
|1A77|2FE|20 from retained X2FA|5|Separate1A90 at470, count from X46C|
|1A9F|2E1|6|1|base+172|
|1AA7|2D5|3|4|base+172|
|1AAF|2D6|3|4|base+172|
|1AB7|2D8|1|1|base+172|
|1ABB|2DC|1|1|base+172|
|1ABF|2E0|1|1|base+172|
|1AC3|2E9|1|1|base+172|
|1AC7|2EE|1|1|base+172|
|1ACB|2F1|1|1|base+172|

Exact20 caller/bank address sets are exported in `smoothing-domains.json`.
Every set excludes35F and360..3C3, with original callers, linear M1 and recovered
counts retained. No neighboring-register heuristic is used as proof. These are
not universal exclusions of arbitrary indirect entries or foreign source counts.

**C/D:** no proven normal positive-count publisher. Normal positive N min/max
and valid k domain are **UNRESOLVED**. The ISA LC is24-bit; raw positive count
bits could represent1..FFFFFF architecturally. That is not a proved normal domain
or permission to seed any count. No20 bound is enforced here; malformed/unbounded
normal counts cannot be categorized as service-only solely from these findings.

**E/F:** established record producer is the initialization clear only; service
zeroing capability is separate. Per-block, ARM or DSP construction of active
compiled records is **UNRESOLVED**. Immediately-after-clear d_k=0 for the
prospective20 positions, but count0 means none are consumed by2043/204B in
zero-skip mode. No normal destination field value or destination set is fabricated.

## G, K. Publication, self-modification and count latching

**VERIFIED local order:** completed boot clear visits35F before360, and afterward
both are zero. Recovered ARM order is separate source field/tail writes → source
count20 → compiled count0. This is not compiled-record fill→positive-count commit.
No positive count/table coupling, producer barrier, synchronization flag or
normal atomic publication sequence was recovered.

P:203A loads X35F once into X1.203B..203F leave X1 unchanged. **2040 DO X1**
copies that value into24-bit LC and saves outer loop state; actual loop endpoint
is204B, continuation204C.2045 subsequently overwrites X1 as arithmetic data;
there is no count-cell reload or LC assignment in body2042..204B.
See pinned manual5.4.4.3 and DO13-56..58; no new external source fetched.

**VERIFIED conditional self-alias behavior:** if an already-active record had
d_k=35F,204B would change the count word for later invocations, without changing
the already-latched current LC by that memory store alone. This is an implication,
not a recovered normal record. Current count/record/loop-state corruption by
other agents is not globally excluded. Starting with preserved35F=0 in zero-skip
mode,204B cannot be the first positive35F writer because its body never executes.

No interrupt mask/critical section or whole-table snapshot appears in202B..2070.
SHI156..1B3 and audio1B4..1D8 do not directly assign X1 or LC; reviewed IRQ code
therefore does not replace the local latch by a memory-count reread. SHI can still
write count or record memory between loads via19D. Other interrupt eligibility,
foreign loop state and worker/context preservation remain unclosed. Partially
updated record fields can affect later fetches; absence of a producer cannot prove
such partially initialized states impossible in every normal invocation.

Zero LC skips only with compatibility SC bit13 clear; legacy set mode runs65536
iterations. Conditional DSP56724/25 reserved/reset-bit evidence and previous
admitted checkpoint assumptions are retained, not converted into authentic boot.

## Targeted host/cursor precursor check

`count-alias-preconditions.json` records necessary equations, not reachable states:

- P19D needs effective saved X10=35F, X11.bit15=0 and received raw X0 nonzero.
  A cached scalar write skips address setup if its requested encoded address
  equals ARM cache20003D00; the store then follows actual saved cursor/space.
- If the only intervening cursor operation is private scalar read29344 at r,
  it leaves cursor r+2. Count35F therefore needs **r=35D**. For a record destination
  field364+5*k, the analogous precursor is r=362+5*k; actual normal k is unknown.
- A retained linear32-write1F97 run aliases35F iff cursor c is in[340,360).
  Existing initialized cursor values miss this; global preservation is open.

The existing19 scalar-read edge candidates were reused, without a new call scan.
Six fixed arguments (35,802F,8003,9,8008,9) exclude the X35D scalar-read precursor.
The private service read at26AD4 can accept35D, but is **SERVICE-ONLY**, not a normal
positive witness. Variable/inherited read arguments, generic wrapper29362 and
complete normal call ordering remain **UNRESOLVED**. Candidate call bytes and
existing argument windows are verified/exported; edges are not promoted to a
complete normal graph. The asset-reader row stays explicitly frozen, unanalysed.
No actual normal35D read followed by a coupled nonzero cached count store was found.

## H–L. Exact normal set, collisions and entry

| Question | All-normal result | Bounded zero-count evidence |
|---|---|---|
|Exact204B destination set|**UNRESOLVED**, not a numeric envelope or interval|Empty set|
|X:[5F00,6000) collision|**NOT-YET-DETERMINED**|**VERIFIED NO / BOUNDED-PROOF**|
|Each selector95A..95F|**NOT-YET-DETERMINED** individually|**VERIFIED NO / BOUNDED-PROOF**|
|X:[9DB,A12) table|**NOT-YET-DETERMINED**|**VERIFIED NO / BOUNDED-PROOF**|
|Each descriptor+0 EB,F3,FB,103,10B,113,11B,123,12B,133,13B,143,14B,153|**NOT-YET-DETERMINED** individually|**VERIFIED NO / BOUNDED-PROOF**|
|X35F self-alias|**NOT-YET-DETERMINED**|No204B store; first-violator lemma applies|

`collision-results.csv` exports46 individual target/scope results. No normal
reachable positive destination is reported, and unknown sets are UNKNOWN,
not populated using hypothetical record data. Neither normal high-X exclusion
nor normal high-X collision is proved.

**VERIFIED structural NORMAL AUDIO entry:** audio-ready block1D9.. calls198D
at1FC; scheduler walks14 eight-word descriptors EB..153. Initialization28AC/28BC
installs202B at descriptor+0 X14B after twelve voice entries.19A5 loads R1 and
19AC calls it.202B..2070 is the complete routine; count consumer203A..204B is
its embedded loop. With the initialized descriptor/function context retained,
this is a normal audio path into203A; no authentic full startup is required to
identify its role. Actual all-normal descriptor/entry preservation and positive
count entry remain **UNRESOLVED**; no direct interior203A call was recovered.

N=0 skips204B, but not initial field reads/Y prefetch. Broader202B also clears38
X words at2030, X[967,98D), independently of the record loop. The empty set
claim concerns204B, not every write in202B. Previous two zero-count entries and
the separately labeled single-store calibration remain unchanged; calibration
is expressly not evidence of a normal positive invocation.

## M–Q. Replay gate, consequences and next step

**Original positive-count replay executed: NO.** No defensible positive NORMAL
checkpoint exists with count/records/destinations and qualified stack/loop
provenance. This phase therefore instantiates no CPU and executes0 instructions;
neither zero replay nor old calibration was rerun to substitute for that gate.

**Persistent RAM:** P204B is not removed as a blocker for X[5F00,6000).
Normal high-X safety remains NOT-YET-DETERMINED, service robustness:NO,
verified256-word reservation:NO. No allocation, sentinel or Plaits layout.

**Target bridge:** P204B is not removed from selector/table/descriptor+0 mutation
obligations. No positive target-producing state or all-normal exclusion was
proved. P1E15 reachability staysUNRESOLVED; active-parent replay:NO; bridge not
recomputed. Other previously scoped exclusions are retained independently.

**Remaining independent blockers:** normal effective host/cache/space/order
provenance to count/record words; foreign cursor/modifier and entry retention;
other inherited indirect-context/worker physical shared mapping obligations.
The frozen asset result remains dataset-specific and selection-qualified; it
was not reconsidered or silently promoted to universal closure.

**Single best next step:** target the normal saved-X10/cache producers feeding
P19D specifically for35F and compiled-record words, including the variable/generic
scalar-read arguments and ordering exposed here. Recover an actual coherent
normal publisher or an exclusion before any positive replay. Do not restart a
generic write/asset/ROM census or seed the missing state. Further broad static
alias enumeration has diminishing returns; a bounded producer/ordering obligation
is still meaningful. If its provenance remains unknowable from existing inputs,
stop rather than turn an unbounded envelope into a witness. No live observation
or hardware permission follows from this recommendation.

## Reproduction and preservation

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_p204b_provenance.py --output-dir builds/phase19c-p204b/new-final
& $py -B tools/ct_p204b_provenance.py --output-dir builds/phase19c-p204b/new-repeat
& $py -B emulator/tests/verify_p204b.py --first builds/phase19c-p204b/new-final --repeat builds/phase19c-p204b/new-repeat --output-dir builds/phase19c-p204b/new-checks
```

Existing Python/pypdf only, no dependency installation. Fresh project output
paths required; originals/existing outputs refused. All requested machine-readable
files are in final-v4:count-writers.csv, record-schema.json, record-writers.csv,
destination-domains.csv and collision-results.csv, plus original byte witnesses,
caller address sets, count latch/order/precondition/read ledgers and input hashes.

**TESTED PASS:**21 final reports match byte-for-byte;20 bounded smoothing domains,
nine wrapper callers,160 nominal ARM source-table writes, five fields,
46 collision/scope checks,19 inherited read edges/six fixed exclusions,
two preserved zero-count entries;33 prior checkpoint/FULLHELPER/PACKLINK evidence
members hash-guarded. Two overwrite refusals; original SYX/BIN expected hashes
and in-memory decode/roundtrip, all10 DSP stream/payload extracts,
sealed19A core/harness and prior helper source guards pass.0 CPU instructions,
no positive seed or fabricated records. Evidence reproducibility does not prove
the unresolved universal normal state.
