> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 8 — after-init memory audit for VariableSawOscillator

## Phase 14 update — invariant still unresolved

See [dsp-x35f-invariant.md](<dsp-x35f-invariant.md>), `builds/phase14/current/`.
**NOT-YET-DETERMINED:** X35F==0 at every normal203A entry. No disproof or
normal nonzero setter. A conditional first-writer lemma removes204B itself
as an initiating cause, but not as a high-X blocker once other writers/entry
domains remain unclosed. Service5E private clears cannot set a positive count.
Recovered paged stream now has2740C-byte initializer and conditional bound
[E7FFFE,E93A06); full pointer/count preservation remains separate.

The invariant gate did not pass, so candidate not re-evaluated. Previous
NORMAL-RUNTIME SAFE NOT-YET-DETERMINED / SERVICE-ROBUST NO remain; no256-word
allocation, Plaits implementation or compilation. Next:1F97's Y-held cursor
provenance/preservation; do not silently discard other unclosed store domains.

## Phase 13 update — allocation remains gated

[dsp-indirect-write-204b.md](<dsp-indirect-write-204b.md>), evidence
`builds/phase13/final/`, corrects the outstanding descriptor count hypothesis.
**VERIFIED:** boot clear and recovered ARM286E4 publish0 atX35F; the20 supplied
by27A10 is the separate X2FA source count.204B writes one word per record,
not a contiguous count-sized destination block. If35F remains0 in zero-skip
mode, there are no active records or204B stores. No nonzero publisher recovered.

**UNRESOLVED:** normal foreign-writer preservation of35F and previously open
effect/AGU/host/transition domains. Universal path collision and
**NORMAL-RUNTIME SAFE remain NOT-YET-DETERMINED**; **SERVICE-ROBUST stays NO**.
No256-word allocation or layout, and no Plaits implementation/compilation.
Static analysis is not proved exhausted. Next: scoped X35F preservation proof.

## Phase 12 update — normal-only allocation proof

See [dsp-effect-memory.md](<dsp-effect-memory.md>), `builds/phase12/final/`.
The user's two axes are independent: **NORMAL-RUNTIME SAFE: NOT-YET-DETERMINED**;
**SERVICE-ROBUST: NO** forX[5F00,6000). Service request5E is not a normal-RAM
blocker. No normal-safe256/128/64-word subrange, layout, reservation or port.

The recognized effect wrappers supply low R7 Y destinations; their selected1E15
stores cannot touch the initialized cursor tables under the documented modes.
The valid indirect table/+1 entry set excludes1E15, but normal selector and
table-writer closure is not proved. Initialized output buffers remain bounded
through2D0B; additional reviewed helper/input reads through2DAE. Global effects
and other scratch maxima remain **UNRESOLVED**, not inferred from those numbers.

31 external INIT RLE records now proveP[2309,2599) is data, removing apparent
DMA accesses there. Direct normal rearm remains low Y/fixed X peripheral.
Global indirect configuration still depends on normal destination producers,
including descriptor202B's R4 load2043/X store204B. Nine fixed host staging
records are256 words each inX[C00,D00). No normal high-X witness established.

Next: bound X364+5*k destination records and X35F count consumed by204B.
Service mitigationA/B/C/D is conceptual only; ordinary-state preservation and
service robustness must not be merged into one gate. Existing output scratch
X[2C46,2C66) and readable/filter2C66 retain their contract. No Plaits work.

## Phase 11 update — 2026-10-06

See [host-utility-269e4.md](<host-utility-269e4.md>) and `builds/phase11/replay/`.
No256-,128-, or64-word allocation is **VERIFIED AVAILABLE AFTER INIT**;
no theoretical layout or Plaits compilation/implementation.

**VERIFIED recovered host classification:**269E4 is framed service request5E,
and can run while Selection0 remains active. This is **SERVICE-ONLY OVERLAP**,
not a recovered ordinary voice/UI write. Each candidate word is admitted as a
single private X start. Read/write/op/mode/status schema is exported; private
write serialization actually yields zero. Normal availability remains a separate
proof from service isolation and unvalidated large-request behavior.

**VERIFIED progress:** selector7 publisher49C0A has recovered index0..63,
maximum X destination1E8B. Startup effect pointer tables initialize to low
buffers with conditional maximum2D0B. Global producer/modifier and1E15 entry
closure remains unresolved. Neither fact proves persistence across every block.
All placements retain **UNRESOLVED / POTENTIALLY AVAILABLE** normal status.
No alternate search or fabricated ranking: the candidate is not disqualified
and no unavoidable static limit is proved. Next: close effect pointer-cell and
modifier invariants. Original/extract hashes and codec roundtrip are rechecked.

## Phase 10 update — 2026-10-06

Current verdict and instruction evidence: [dsp-high-x-audit.md](<dsp-high-x-audit.md>),
`builds/phase10/replay/`, and reusable `tools/ct_high_x_audit.py`.
X:[5F00,6000) remains **UNRESOLVED / POTENTIALLY AVAILABLE** after init.
No 256-,128-, or64-word subrange is **VERIFIED AVAILABLE AFTER INIT**;
therefore no theoretical allocation layout is authorized by the evidence.

**VERIFIED corrections:** X:[1B16,1B21) is an eleven-word asynchronous table-job
snapshot, not one destination. Its output R5 is used for Y stores; its reviewed
X workspace writes stay in [2400,2800) under the stated legacy modulo setup.
X:1D3A/B save Y-buffer pointers by instruction use, but the related effect
helper1F5C loads X write cursors from Y state at1F68/6A. Their producer and
normal reachability proof remains **UNRESOLVED**. Do not merge those two facts.

**SOURCE-DERIVED + VERIFIED stock DMA correction:** both DMA staging buffers
are Y: DMA0 writes[29,2C), DMA1 reads[21,24) and writes fixed X peripheral
FFFFA4. FFFFEB is DSR1, not DDR1. Eight channels are inventoried; arbitrary
reconfiguration is not globally excluded.

**Exact remaining host mechanism:** ARM269E4 accepts private start addresses
below8000, including this entire candidate;26A9A/26AD4 perform addressed
writes/reads. Caller1F30A is recovered, but full normal/service restrictions
are not. This capability is not normal-runtime occupancy evidence. It blocks
all smaller placements until closed. Next: trace that dispatcher condition.
Original hashes, all five extracted streams/payloads and exact codec roundtrip
are rechecked by the replay. No upstream refetch, compilation or port work.
Earlier next-step paragraphs and DMA-space interpretations are superseded.

## Phase 9 update — 2026-10-06

See [bank-selector-domain.md](<bank-selector-domain.md>) and builds/phase9/verified/.
**VERIFIED recovered normal parameter boundary:**bank0/1, independently of wider
event inputs. Shared one-token guard and dispatcher reset close HOST-BANK for
these parameter paths. Five separate tables yield456 distinctX destinations
within52..959 and375Y destinations withinFD..78F; exact holes remain in exports.
27A10's own101 sinks are supplemented by two possible immediate/deferred
destinations2FA+172*b and35F+172*b. Its abstract bank64→5F7B calculation is not
a normal callback witness in the recovered graph.

**Phase8 correction:**21F94/21FB2 resolve220CC→200067FC; the synth dirty setter
and dispatcher are connected. Earlier claimed alias separation is corrected below.
Global20006A0C contains different namespace dirty flags.

No persistent allocation or layout is verified. Other normal host/table traffic,
exact candidate DSP/worker/DMA/save/scratch exclusions and public event-producer
ancestry remain unresolved. CandidateX:[5F00,6000) is the next focused audit
target, not a chosen allocation. Earlier Phase8 gates remain historical; RAM
availability is still NOT-YET-DETERMINED and implementation readiness NO.

2026-10-06. STATIC ANALYSIS ONLY. No hardware, firmware execution, transmission,
patching, port implementation, compilation, injection or upstream refetch.
All DSP ranges below are half-open **24-bit word** addresses; ARM addresses are
byte addresses. Earlier evidence remains in place.

**Result: UNRESOLVED. No contiguous allocation, including 64 or 256 words, is
VERIFIED AVAILABLE AFTER INIT.** No allocation is chosen and no future state
layout is drafted. This is a missing ownership proof, not evidence that no RAM
is physically available. Phase 8's primary allocation goal remains unmet.

## Reproduction and evidence standard

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_poc_memory_audit.py --output-dir builds/phase8/verified
```

Use a fresh output directory; existing directories and original/ are refused.
The replay uses standard Python, existing byte-checked ARM/DSP listings and
explicit reviewed formulas. It needs no decoder installation, network, compiler
or device. ARM evidence was prepared with the existing Capstone dependency;
DSP decoding remains the previously validated DSP56300 decoder.

Exports include audit.json, bank-writes.csv, parameter-callbacks.csv,
bank-destinations.csv, bounded-effect-intervals.csv, allocation-search.csv,
unresolved-exclusions.csv, stack-register-inventory.csv, reviewed-dsp.asm,
input-integrity.json, evidence/ and unchanged partial Phase 6C inputs in inherited/.
The source-level resource claims retain the pinned Phase 7 revisions.
**Canonical final exports:builds/phase8/verified/**. Earlier root/final/repeat
exports are retained as intermediate evidence. Additional final exports are
candidate-exclusion-envelopes.csv, DMA-register-inventory.csv,
direct-candidate-operands.csv and coefficient-index-bound.json.

**VERIFIED** means the stated local instruction/data fact is byte checked, not
that the entire program's calling modes or mutable state have been solved.
An abstract input-domain enumeration is not a runtime reachability witness.

## A. Selector domain and initialization

The selector is ARM byte **20006800 = parent 200067FC +4**. Byte **20006801
= parent+5** is the current slot and is a different variable.

**VERIFIED INIT-ONLY:** scatter descriptor at0805B7B4 contains words
FFFBF037 / 00002D50 / 20003D04 / 00000000. Its signed relative callback
resolves to Thumb0801A7EB, code0801A7EA. The helper loads count/destination
atA818/A7F0, clears with zero r5 atA802 plus halfword/byte tails, and terminates
on zero count. ARM interval[20003D04,20006A54) includes selector and slot:
both boot as0. Independently08021092 loads0;08021098 STRH parent+4 clears both.
Reentry into initialization has not been excluded; reset-survival is not claimed.

| Reviewed selector mutation | Input and restrictions | Classification |
|---|---|---|
|08021496 STRB parent+4|Incoming r0; no internal 0/1 clamp|VERIFIED mutation; global input domain UNRESOLVED|
|0804963A STRB direct|Saved incoming r0; no internal clamp|VERIFIED mutation|
|0804978C STRB direct|Incoming r0;0x10 returns before store|VERIFIED mutation; other inputs not bounded to0/1|
|0804982C STRB direct|Incoming r0;0xFF and0x10 branches bypass store|VERIFIED mutation; other inputs not bounded to0/1|
|08021098 STRH parent+4|Constant0; overlaps both bytes|VERIFIED BOOT/reinitialization witness|

**VERIFIED bounded paths:**0803BE0C/BE0E supply0 to49634;
BE16/BE18 supply1.080214BE invokes2148C with0 at14C0/14C2 and1 at14C6/14CC.
Callers at213B8 and4966E are recorded in evidence/phase8-dirty-callers.json.
The latter inherits49634's argument, not an independent clamp.

2148C stores the selector *before* examining parent+18+2*bank flags. It walks
16 callbacks at0805A384 using BLX at214AC. Table index6 is Thumb08027A11,
actual entry **08027A10**;08027A12 is its stride-constant instruction, not entry.
This establishes a concrete route to the formerly unbounded constructor.

**UNRESOLVED:** complete global normal domain and all alias/indirect mutation
paths. Literal scan records four exact20006800 pools and25 candidate loads;
parent aliases are separately scanned. These scans are not exhaustive alias
proofs. Channel thunks08029A08/29A12 route arguments to3BD58/3BD94 and then
497CA/49758. The CMP channel,#2 at3BD7C occurs after497CA and does not guard
its store. No proven SERVICE-ONLY ancestry excludes these writers.
Conservative byte domain is0..255; global normal0/1 remains unproved.

**VERIFIED use-site bound:**08021D8E loads parent+4;21D9A masks AND1;
21D9E adds9D;21DA2 writes **X:9D or X:9E** regardless of the byte's wider domain.
That mask cannot be transferred to other readers. Group/bank relationships
are supported by allocation/parameter behavior; UI Synth1/2 names remain hypotheses.

## B. Address propagation and normal destinations

**VERIFIED local formula at08027A10:**27A38 multiplies byte b by172;
27A44 truncates to16 bits;27A48 adds2FB. For i=0..19, writes occur at:

`encode16(0x2FB + 0x172*b + 5*i + j), j ∈ {0,1,2,4}`

The calls are27A5E/27A72/27A80/27AB8. Field+3 is skipped.
27ABC/27ABE/27AC0 bound20 iterations.27AC6..27ADC write another20 words at
`encode16(0x3D0 + 0x172*b + k), k=0..19`.27AF0 writes global X:95.
Each listed write is one word. These are the function's own writes, not a
complete footprint of every callee. Ordinary host encoding uses bit15 forY
and low15 bits as address.

| Conditional bank | Record-write hull (contains skipped words) | Tail interval |
|---:|---|---|
|0|X:[2FB,35F)|X:[3D0,3E4)|
|1|X:[46D,4D1)|X:[542,556)|

Thus this complete local destination family excludes both high candidates
**under b∈{0,1}**. The exported256-value enumeration deliberately retains the
missing global invariant. Example **b=64 → X:5F7B** at the first call overlaps
X:[5F00,6000). This is an abstract counterexample to a byte-width-only exclusion,
**not evidence of a normal write at5F7B**, and does not disqualify that RAM as
physically occupied. Other bytes can set the protocol's Y selector bit.

**VERIFIED inherited bounded families:** slot i=0..11 gives sparse descriptor
publication X:F2+8*i; event contexts57A+4A*i; control contextsY:[11F,59F).
Boot/reentry tables X:[1600,1940),[2000,2200),[2200,2400) remain separate from
normal UI writes. Reviewed ordinary constants stay below the candidates.
Full normal addressed/bulk/cached destination closure remains **UNRESOLVED**;
Phase6C's205 unresolved call records are preserved, not205 proven arbitrary
normal accesses. New evidence narrows a family without claiming to solve them all.

**Corrected in Phase9:**3602A performs70 comparisons and calls21E9C to mark
**200067FC+16/+18** flags, consumed by213D4/2148C. The actual PC-relative
literal target is220CC. Global dirty callbacks214F4/21544/21578 use separate
20006A0C state/tables.360EE's0/1 preparation calls do not themselves write
20006800; the connected dispatcher sets its own0/1 argument before invoking
callbacks. See the Phase9 report for serialization and local-domain proof.

## C. Candidate occupancy and indirect closure

| Candidate | Initialization | After-init classification |
|---|---|---|
|X:[4000,6000),8192 words|VERIFIED clear; INIT-ONLY|POTENTIALLY AVAILABLE; UNRESOLVED exclusions|
|Y:[3000,4000),4096 words|VERIFIED clear; INIT-ONLY|POTENTIALLY AVAILABLE; UNRESOLVED exclusions|

No reviewed direct normal access proves either entire candidate occupied.
No absence-of-literal-access result proves a subrange available. Each unresolved
entry in unresolved-exclusions.csv records origin, access, missing bound and
affected memory space. Unknown intervals conservatively prevent availability
throughout the affected candidate until origins/modes/bounds are closed; this
is uncertainty coverage, not an assertion of actual full-space traffic.

- **HOST-BANK:** wider selector writers/callback reachability, as above.
- **HOST-OTHER:** computed/cached/bulk helper base/count and mode ancestry.
- **MAILBOX:** P:1C53..1C5F derives r5 from Y:2C; selected normal external bases
 100000/128800/151000 do not overlap candidates, but complete multistage and
 retained X:1B16 destination bounds remain unproved. Selectors1/6/7 lack normal
 callers; capability is neither normal occupancy nor SERVICE-ONLY proof.
- **DSP-EFFECT:** P:CE2..CED calls1157; Y:7FE supplies n7. The coefficient index
 arithmetic is now bounded separately below; retained buffer origins, helper
 footprints and calling modifiers remain unresolved.
 The preceding CC4 loop is bounded atN=32: X:[2EF0,2F30),[1BB2,1BF2),
 [1BF2,1C32);Y:[840,880),[880,8C0),[9C0,A00). It does not close the helper.
- **DSP-TABLE:** P:1E15 saves incoming r6/r7 in X:1D3A/1D3B; later1E33/1EC2/
 1EED paths reload them. Entry mode, sources and full extents remain unresolved;
 these instructions must not be called proven normal audio candidate occupancy.
- **QUEUE, DMA, SAVE-SCRATCH:** exclusions below remain incomplete.

**VERIFIED ISA-derived arithmetic:**1166 loads y0=19;1168 performs signed
fractional MPY of y0 and signed24(x0);116A moves B1 directly into n2. Therefore
`n2=floor(19*signed24(x0)/2^23)` is within[-19,18] even without a bound on the
earlier mutable parameter. The alternate1164→1172 branch retains n2=3 from1160.
Direct B1 transfer does not apply accumulator scaling/limiting. With linear M2,
r2=9B1 at1162 gives X:[99E,9C4) for116E/1175, excluding both candidates.
This conditional address bound does not solve M2 at entry or later circular
buffer pointers loaded at119F. The documented arithmetic/storage semantics are
in [DSP56300FM §§3.1.2–3.1.3](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf).
The endpoint calculation and instruction-byte checks are replayed in the tool.

## Worker/shared boundary

**VERIFIED instruction behavior:** worker105 initializes r5=30002;
107 publishes X:30000;114 reloads on ICC reset.117..11E compares endpoint with
cursor and processes the difference.120 loads queued address to r0;125 reads
X:(r0);126 replaces the queue entry and advances r5. Normal globalP:759 resets
the queue with ICC handshake before processing. Producer endpoint stores occur
atP:81B/876/8D5/917/954. Variable repeat DO at7C8 prevents a global count bound.

**SOURCE-DERIVED architecture:** under the conditional DSP56724 map,
shared[30000,38000) is physically aliased through P/X/Y; private low X/Y on
different cores are separate. Worker reading numeric lowX therefore does not
prove it reads channel-zero's privateX at the same number.
Legacy modifier `$XXFFFF` selects24-bit linear addressing, not a shared-bank
or16-bit modulo queue. This applies to M5=00FFFF when SR.EMA=0;
EMA bit18 resets0, while global mode/SR closure remains unproved.
See [DSP56300FM §4.5.1](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf)
and [DSP56724RM SR/EMA and memory map](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf).
Architectural overflow is modulo2^24, not at38000.

**ESTIMATE / selected profile:**192 requests per voice ×12 voices gives2304
queue words, endpoint30902. This lies in shared RAM but is not a maximum across
all repeats/modes/jobs. Endpoint/capacity, queued-source bounds and all-mode wrap
prevention remain **UNRESOLVED**. No actual wrap into low RAM has been proved.

## DMA, stack and scratch

**Phase10 correction to this historical setup:**P:2A2D writes DCR0=285AC4;
count2, fixed source X:FFFFA8, incrementing destination Y:29..2B. DCR1=286251
uses incrementing source Y:21..23, fixed destination X:FFFFA4.1BC rearms DDR0;
1BE rearms DSR1. Both staging buffers are Y. Primary DMA decoding now supports
these three-transfer intervals; complete reconfiguration exclusion remains
unresolved. See the Phase10 report and DMA-reviewed-bounds.json.

**SOURCE-DERIVED:** the architectural return/loop stack is not an ordinary X/Y
heap allocation. stack-register-inventory.csv records explicit SSH/SSL/SP/SC/
LA/LC references, including stock software use of hardware stack registers.
**UNRESOLVED:** maximum nesting/IRQ growth and all software save/scratch pointer
footprints. A hardware stack distinction cannot prove arbitrary X/Y scratch safe.

Known stock scratch, audio rings, SHI saveY:[2000,2006), group sumsX:2DF0/2E50
and lane/output work remain **VERIFIED RUNTIME OCCUPIED**, subject to their
individual exact field/lifetime maps. Initialization'sX/Y:[0,6000) clear is
**INIT-ONLY**, not a persistent runtime owner.

## D–I. Allocation search and lifetime

| Gate | Result |
|---|---|
|A:64 contiguous words VERIFIED AVAILABLE AFTER INIT?|NOT-YET-DETERMINED|
|B:128 words?|NOT-YET-DETERMINED|
|C:256 words?|NOT-YET-DETERMINED|
|D:512 words?|NOT-YET-DETERMINED|
|E:1024 words?|NOT-YET-DETERMINED|
|F:normal ARM cannot overwrite chosen allocation?|NOT-YET-DETERMINED; none chosen|
|G:DSP/worker/DMA cannot overwrite it?|NOT-YET-DETERMINED|
|H:persistent across successive blocks?|NOT-YET-DETERMINED|
|I:coexists safely with stock output seam?|NOT-YET-DETERMINED for an allocation|
|J:if256 proven, RAM still primary blocker?|Condition not met; currently YES|

Search exports cover all word-aligned starts for64/128/256/512/1024 in both
candidates. None passes the unresolved-exclusion criteria. Largest **verified**
X andY allocation: **none established (0 proved words)**. A genuine disqualification
would require an occupied overlap, not merely one unresolved pointer. Boot clear
does not disqualify an after-init allocation; stock reload/reset would erase it.
No minimum planning layout is assigned without the requested256-word proof.

## J. Relationship to output seam

**VERIFIED RUNTIME OCCUPIED:**X:[2C46,2C66) is global reused32-sample output
scratch;P:9DD starts retained voice processing. X:2C66 is prefetched by stock
scaling/gain and also participates in neighboring filter scratch. Selected final
prefetch is unused numerically, but universal guard-value freedom is unresolved.
Persistent generator state cannot live in this reused output region.

**SOURCE-DERIVED:** the selected raw primitive can write a32-sample block and
has no mandatory internal32-element temporary array. **HYPOTHESIS:** a future
translated primitive could render directly into2C46 during the serial completion
window, consumed by retained post/mix before scratch is reused. This would avoid
an additional output buffer. Scaling, live-register/state effects, scheduler
obligations and neighboring scratch behavior need proof; buffer elimination is
not an established ABI or permission to reclaim2C66.

## K–M. Separate resources, readiness and next step

- **SOURCE-DERIVED persistent scalar payload:** six floats plusbool,25 bytes
 excluding ABI/padding.13 DSP words is a bit-preserving float-storage illustration,
 not a fixed-point design.128–256 words remains a planning allowance, not measured
 requirement or available memory.
- **SOURCE-DERIVED tables:** VariableSawOscillator itself is table-free with
 independently validated normalized frequency. Source NoteToFrequency requires
 two257-float tables; that pitch adapter is separate from the primitive.
- **UNRESOLVED P memory:** translated code words, placement and ARM container
 relocation/acceptance. Conditional5538-word P tail is not an algorithm-fit proof.
- **UNRESOLVED timing/numeric:** execution headroom, all-mode live/clobber/phase
 contract, absolute scaling, fractional conversion and guard scratch ABI.

**Readiness:** conceptual resource study YES; allocation-qualified PoC design
NOT-YET-DETERMINED; implementation readiness **NO**. The primary RAM proof has
not closed; no code, firmware changes or allocation layout is produced.

**Single best next step:** resolve the input producers and indirect ancestry of
channel thunks08029A08/08029A12 →3BD58/3BD94 →497CA/49758, then prove whether
their wider selector writes can survive into2148C's banked parameter callbacks.
This tests a concrete normal-host exclusion rather than assuming every global
selector read is a two-bank value. Other DSP/DMA exclusions remain independently
necessary even if that invariant is proved.
