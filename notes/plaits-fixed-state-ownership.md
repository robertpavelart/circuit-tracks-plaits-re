> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20C2 — bounded fixed-state ownership audit

2026-10-07. **OVERALL: REFUSED. Seven persistent X words proved: NO.**
No canonical firmware, renderer or existing evidence changed. No hardware,
MIDI/SysEx, repack, flash, executable patch, stock CPU execution or runtime-snapshot
work. Snapshot branch stays DEFERRED. No broad RAM sweep or new high-X search.

Canonical evidence: `builds/phase20c-fixedstate/final-v1/`; repeat/checks in
`repeat-v1/` and `checks-v1/`. Thirteen requested reports, candidate-specific
source witnesses, arithmetic checks and unchanged-standalone trace traffic.
Tools: `tools/ct_fixedstate_audit.py`, `tools/ct_fixedstate_verify.py`.

This is a rejection of the bounded candidates under the current architecture,
not proof that no possible seven-word allocation exists anywhere. Known retained
writers or unclosed relevant domains reject a candidate. The ledgers identify
known writer classes and explicit residuals; they do **not** claim complete
global writer/consumer closure. No absence-of-literal proof is substituted.

## A–E. Candidate pool and cross-block failure

The current design retains both request/completion passes, preparation, lookup
worker and the full mono/aux combiner. Replacing the final mono output does not
remove any of their writes or next-block consumers. Therefore there is **no
new generator-state ownership transfer** under that design.

Only inherited regions were examined: slot0's five-word tail and X[2CCC,2D0C)
scratch. Active coefficients/kernel, output/guard, post histories, group sums,
known host parameters and high-X remain excluded. The two-word nominal gap
[2C22,2C24) is also excluded: cardinality is insufficient and geometric boundaries
do not establish ownership of its cells.

**New VERIFIED tail accounting, slot0 E=57A:**

|X word|Retained writer|Reader/lifetime|Outcome|
|---|---|---|---|
|5BF..5C1, three words|281..2A2 sets X2B=E+45;70C loads R1;73B writes three terms|36D loads X2B;374 reads three terms in retained update branch, including later invocations|Not spare across blocks|
|5C2|2D8 reloads R7=E+1;2DD stores at+71 decimal =E+48|1BB7/1BDB allocator timestamp scan, bank0 six slots|Allocator-live|
|5C3|ARM21A22 stages zero;21A54/5E writes5C3+4A*i through292F8→19D|Full consumer semantics unresolved; conditional start reset is sufficient disqualifier|Not persistent under original lifecycle|

The three terms are described by arithmetic/data flow, not assigned oscillator
semantics without proof. The tail has **five**, not seven words. Extending it
to[5BF,5C6) crosses slot1 E=5C4 and Q=5C5, which remain stock. A seven-word
split including the first three terms still fails their retained writer/readers.

**VERIFIED conditional scratch writer domains:** completion822/824/829/82A
(or87D/87F/884/885) produces32 absolute-weight words in[2CCC,2CEC), using16
paired stores with linear addressing. Selected consumers are833/83F, or897 on
the alternate path. They finish before9B9, but next completion rewrites the same
cells. No cross-block ownership follows from that local last read.

Phase15 initialized Y1820+j cursors alternate2CCC/2CEC. Helper1F5C clears the
two32-word halves at1F6E/1F6F and accumulates through1F97;1F93 reads before each
store. Later1F09/1F0B consumes both halves. **CONDITIONAL address proof; actual
normal parent/foreign cursor preservation remains UNRESOLVED**, not declared
absent. This uncertainty independently prevents qualifying the second half.

The first seven words[2CCC,2CD3), second seven[2CEC,2CF3), and a representative
high-address split are ranked **REJECTED**. All58 contiguous seven-word windows
in the inherited64-word scratch span lie in the known conditional helper domain
and are service-addressable. No extra candidate regions were searched.

## D/F. Writers, lifecycle and service

Startup2788 clears X[0,6000). That is acceptable **before** owned initialization;
it is not the reason for rejection. Surviving preparation, trigger/reset,
allocator, other voices, possible effect jobs and service writes are the blockers.
Patch/project/mode changes do not disable those paths in the current dispatcher.
Their unclosed foreign destinations remain explicit; no new asset analysis.

**VERIFIED service capability:** the recovered5E utility accepts private starts
below8000 for operation0/port0, has no candidate reservation check, and reaches
P19D in Selection0. Its private consumed-byte path sends a zero24-bit data word.
No service request was constructed or transmitted and no invocation was observed.
Physical ingress applicability remains separate from the static capability.

Address-cache uncertainty does not eliminate that capability. For any watched
cell a and initial cached address C:

- If C≠a, a one-word private start at a forces setup and writes zero to a.
- If C=a, a two-word private start at a−1 forces setup; serialized continuation
  reaches a on the second store.

All watched cells are safely inside the accepted private start interval. These
are integer address/cursor witnesses under valid decoded framing and coherent
serialized transfer, not wire packets or attained runtime states. The tests
exhaust all65536 cache values for one target and both cases at every watched cell.
Thus **SERVICE-ROBUST: NO** for all candidate words under current unrestricted
service behavior. Generic19D target filtering is not implemented.

The1500 prior nominal scalar rows were projected only onto the watched cells.
They contain no nominal hits in this pool. That is **not** complete preservation:
the byte-verified ARM start reset at5C3 is a separate known writer omitted from
that ledger. Normal cache hits use actual X10/X11 rather than the requested
endpoint; all-normal ordering/cursor/bulk domains remain UNRESOLVED. P204B's
record-driven destination and other mailbox/copy domains retain their prior
uncertainties, now recorded only as relevant candidate exclusions not closed.

## G–H. IRQ, worker and sharing

SHIISR156→198→19D can store into private X independently of selected voice work.
Preserving CPU registers does not restore its data writes. No range ownership
guard excludes the candidates. Reviewed ESAI ring/staging and DMA setup miss the
watched regions under retained mappings; runtime reprogramming/foreign domains
are not globally excluded. The lookup worker's queue writes are shared30002+
and private worker state; under the documented private-memory map their numeric
low addresses are not aliases to channel0 private X. Exact physical mapping and
foreign context remain conditional. None supplies an unconditional exclusion.

Slot0 tail is per-slot but retains allocator/lifecycle use. X2CCC..2D0B is global
scratch reused by other stock voices and effect work. Borrowing it persistently
would not preserve those paths. Extending the tail borrows another slot outright.

## I–J. Addressing and temporary workspace

No admitted short-address candidate. All evaluated seven-word layouts are above
3F, so fixed absolute contiguous or split access has **CALCULATED zero P-word
and nominal addressing-cycle delta relative to the549P all-long template**.
This does not qualify their storage or count new initialization/preservation.
Split fixed addresses need no new base register, but every split candidate fails
ownership. No renderer redesign occurred.

**Temporary X[2CCC,2CEC): NOT PROVEN.** Its32-word partition remains3 controls,
3 spills,26 saves. Local weight reads end before the selected combiner; ordinary
foreground effect calls cannot preempt another same-core foreground routine.
That helps local ordering only. Asynchronous SHI stores, all-normal cache/bulk
domains and later computed reader-before-write remain unclosed. No ownership
transfer is asserted and no temporary allocation admitted. This is independent
of the stronger persistent lifetime failure.

## Exactly two fallback architectures

**A — one-way selected-generator storage takeover. CONDITIONAL larger redesign.**
An illustrative seven-word subset[57B,582) lies inside slot0's generator record,
not free or seven original persistent scalars. Ownership would require disabling
selected387 producers and selected77F readers/writers in **both** passes before
any Plaits write. Preserve post-preparation pointer/accounting and global pending
work for all other slots. Resolve auxiliary and guard production anew; retain a
producer or enforce a justified restricted routing contract. Filter every actual
SHI/foreign destination reaching the owned range, including cached continuation;
normal reset/table aliases need closure too. Simply modifying9B9 cannot do this.
Selected stock reentry must be prohibited while those words hold Plaits state:
387 would destroy it. Other slots may remain stock, but their preservation needs
proof. This sacrifices the selected generator and changes the20C architecture;
no takeover, filter or patch implemented.

**B — seven mutable P words in an extended uploaded object. CONDITIONAL structural
alternative; does not satisfy the seven-X-word gate.** RM3 and the one-record
P boot loader make a P object structurally possible. FM PDF372/373 documents
MOVEM read/write to P with all on-chip registers. Conditional5538-word P capacity
becomes5531 after seven state data words. Illustratively, after713P+2 padding,
data could occupy[2D29,2D30); this is not reserved and full glue would move it.
Partial module+padding+state is722P before unknown glue. Relocate the entire
uploaded stream; do not grow it in place or invent an X boot record.

Current compatible memory mode already has24K X capacity. Other reviewed maps
that increase P shrink X below required scratch;8K P alternatives cannot contain
the current2A5E image. No external X object/physical capacity/loader ownership was
proved. Thus B evaluates a P object, not a guessed extension of existing X RAM.

**SOURCE-DERIVED / CALCULATED:**63 existing static state-transfer sites could use
long MOVEM in place of long X MOVE, retaining the two-word template size. No
instructions changed or executed. FM timing is6 plus absolute extension1 versus
long X2: nominal+5 cycles per state transfer. Existing7520-block traffic yields
771/833.6467/1037 transfers and **3855/4168.23/5185** extra cycles min/mean/max
relative to long X. These are hypothetical table costs, not a new bound or physical
timing. P-bus/cache, CCR/accumulator semantics, interlocks and bit-equivalence
still require qualification. Never carry the15,485 partial envelope unchanged.

Private SHI19B/19D accesses X/Y, not this low private P object; shared aliasing at
30000 is distinct under the verified map. All P/DMA writers, actual modes and
mode changes still need closure. No P object is QUALIFIED. B best preserves the
retained-stock-work architecture, but storage/loader/cache/numeric proof is absent.

## K–Q. Initialization, fallback and readiness

Exact seven-word source layout and initialization are in
plaits-state-initialization.md. No eighth flag is inherently needed under a
proved deterministic initialization/ownership epoch. Arbitrary RAM activation
does not acquire that property; a separate armed flag would make eight and need
its own proof. Current candidates cannot retain dormant state when stock writes
resume. A requires one-way selected activation; B could retain dormant P state
within a proved no-reload/no-mode-change epoch.

|Gate|Result|
|---|---|
|Seven persistent X words proved?|**NO**|
|Temporary workspace proved?|**NO**|
|Initialization bounded?|Values/positive-frequency lemma **CONDITIONAL**; actual owner/activation PC unproved|
|Cross-block persistence proved?|**NO**|
|Other stock paths preserved?|Canonical code unchanged; proposed takeover not qualified|
|Addressing cost known?|Fixed high/split template bounded; no qualified candidate/integrated cost|
|Offline patched-image construction justified?|**NO**|
|Flashing justified?|**NO**|

Qualified-set lifetime fixture: **REFUSED** because no set qualified. Eleven
offline arithmetic/source/refusal tests pass, repeated exports identical and
all guarded source/original/previous reports unchanged. No memory seeded into a
CPU and no full firmware exercised. Tests are not a positive ownership certificate.

Largest blocker is cross-block ownership under retained stock/service writers.
**Single best next step:** a narrowly scoped qualification of fallbackB's
seven-word P-backed object and MOVEM numeric/cache contract. No further broad X
search or automatic renderer implementation. That would change storage ABI and
still would not retroactively qualify seven X words.

Reproduce with fresh directories:

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B tools/ct_fixedstate_audit.py --output-dir builds/phase20c-fixedstate/reproduce-new
& $taskPython -B tools/ct_fixedstate_audit.py --output-dir builds/phase20c-fixedstate/repeat-new
& $taskPython -B tools/ct_fixedstate_verify.py --suite-dir builds/phase20c-fixedstate/reproduce-new --repeat-dir builds/phase20c-fixedstate/repeat-new --output-dir builds/phase20c-fixedstate/checks-new
```
