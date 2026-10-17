> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 15 — P:1F97 cursor sources and preservation limit

2026-10-06. STATIC ONLY. No hardware, MIDI/SysEx transmission, flashing,
firmware execution/patch, original/extract changes or Plaits implementation.
No installations or external refetch. Reuses the existing decoder listing and
Phase6B/9/11/12/14 evidence. Tool: `tools/ct_p1f97_cursor_audit.py`; canonical
exports `builds/phase15/verified/`, repeat `builds/phase15/verified-repeat/`.
Earlier first/final/repeat exports are intermediate evidence; the canonical
version corrects the helper count premise toX3B=16, distinct fromX3C=31.

**Normal-family verdict: NOT-YET-DETERMINED**, both for reaching X[340,360)
and for writing exactly X35F. **VERIFIED conditional result: NO** with the
reviewed caller bases, initialized cursor cells, stock counts and modifiers.
No normal dangerous-cursor publisher or normal overlap witness was found.
The family is **not removed** from the count-word blocker set. The count-word
invariant remains NOT-YET-DETERMINED; no high-X allocation is established.

The useful local proof is now complete: the routine does not advance stored
cursor values across blocks, and its state/coefficient writes miss the cursor
cells. Universal preservation still depends on foreign writers and entry/
context state. A further broad static alias phase has **diminishing returns**
from the currently recovered state. This is not a proof static analysis is
theoretically impossible. No dynamic observation was performed.

## A. Function and write role

**VERIFIED:** helper boundaries P[1F5C,1F9B), withRTS1F9A. P1F97 is its
inner-loop read/modify/write store, not a function entry. Parent effect-family
routine is1E15..1F10; direct callers1E80 and1EE5. No recovered direct call into
1F97; the literal1F97 in the DO operand at1F90 is a loop-end address.

At1F5C/5E/60, inputs are saved X-state pointers:

| Field | Register | Local caller A | Local caller B |
|---|---|---|---|
|X1D40|R6: Y state/source base|1800, stored1E76|19F0, stored1ED9|
|X1D41|R5: Y coefficient source|1840, stored1E7A|1A30, stored1EDD|
|X1D42|R4: Y processing state|18E0, stored1E7E|1AD0, stored1EE1|

These are two branches/state families, **not named synths or DSP cores**.
A executes through1E80 when the local X7C&0C test at1E1D/1E1E is zero.
Nonzero branches bypass it to1E82. B reaches1EE5 after the later setup if the
parent routine completes. Parent normal reachability remains UNRESOLVED.

The helper setsN1=N3=2,N4=-3,N5=-4. It clears two X buffers through the first
two cursor cells at1F68/6A, countX3A. OuterDO1F72 has16 iterations. Each calls
C9D twice, then reloadsR7 fromY[R6+32] at1F89. R6 advances once at1F8C.
InnerDO1F90 usesX3A, stock32:

```text
A starts from Y[base+j+48] at1F8B
X1 = X[1D43+j] at1F8F
each inner iteration:
  A += X1                         1F92
  X0 = X[2C8A+i]                  parallel move1F92
  B = X[R7]                       1F93
  Y0 = limited/transferred A      1F94
  B += Y0 * X0                    1F95, DSP MAC semantics
  X[R7] = B; R7 advances by one   1F97
```

This is coefficient-based block processing followed by ramp-weighted
accumulation into X buffers. No additional synth/effect semantic name assigned.
Side effects include X scratch, Y scalar/state updates and helper arithmetic
registers. R7's postincrement usesM7; source-table traversal usesM6. With
legacy-linear addressing, the destination for cell valuec is[c,c+32).

## B–C. Complete recovered cursor table and initialization

**VERIFIED for the recovered bases/linearM6:**32 cells,16 per family. Each
cell and initialized value is exported individually in `cursor-table.csv` and
`cursor-table.json`, including writer PC, reader, output range and uncertainties.

| Y cells, j=0..15 | Parity | Initialized absolute X address |32-word write interval |
|---|---|---|---|
|1820+j|j even|2CCC|[2CCC,2CEC)|
|1820+j|j odd|2CEC|[2CEC,2D0C)|
|1A10+j|j even|2C02|[2C02,2C22)|
|1A10+j|j odd|2C24|[2C24,2C44)|

INIT25E4 calls260A. It setsR0=1820,R1=1A10 and four constants at260C/0E/12/14;
DO261A performs8 iterations, each storing an even/odd pair at261C/1D and
261E/1F. Earlier2789 clearsY[0,6000) to0. Later initialization establishes
the nonzero addresses before recovered normal processing. No alternative
runtime table reinitialization was established. Restart through this initializer
restores the same values. The values are **absolute X addresses**, proved by
1F93/1F97, rather than Y targets, relative deltas or sample/table indices.

Known readers:1F68 readsj0,1F6A readsj1 for initial buffer clears;1F89 reads
all16 cells in the selected family. Other computed foreign readers/writers are
not globally closed. P1820 appearing as a code address elsewhere is not a
Y1820 operand. If a foreign writer redirectsX1D40 orM6, other Y cells could
feed the load; these32 cells are not claimed universally exhaustive under
unproved register/context state.

## D. Runtime mutation and local preservation

**VERIFIED locally:** advancedR7 is not written back to its Y source cell.
For each outer iterationj, R7 is freshly reloaded. Stored-cursor update is:

`c_next = c_old`, local persistent delta0.

Thus there is no accumulating32-word cursor drift on successive blocks from
this routine. This is conditional on foreign writers not changing the cells.

The scoped local Y footprints are:

| Writer | Family A | Family B | Why cursor cells are preserved |
|---|---|---|---|
|1F8C|[1800,1810)|[19F0,1A00)|one scalar store/outer; R6 increments|
|1F98|[1830,1840)|[1A20,1A30)|after increment, +47 means oldbase+j+48|
|C9D→CB2..CB5|[18E0,1960)|[1AD0,1B50)|2 calls*4 state stores*16 outer|
|1F13 coefficient copy|[1840,18E0)|[1A30,1AD0)|16*2*5 coefficient words|
|1E6C /1EBF|[1810,1820)|[1A00,1A10)|16 control words end before cursor table|
|1E57|[1830,1840)|same A-state region|begins after A cursor table|

C9D does not useR6/R7/M6/M7/R0. Its four R4 reads update1+1+1-3=0; four
final Y stores advanceR4 by4. Its ten coefficient reads in the DO body balance
eight+1 and two-4 updates, leavingR5 at its prefetched offset1. The caller's
`R5 -= N5` adds4, advancing to the next5-word coefficient set. Conditional
coefficient reads stay[1840,18E0)/[1A30,1AD0), outside cursor tables.
The helper DO uses stockX3B=16;X3C=31 is a different count. The stable
coefficient-address recurrence does not rely on confusing those fields.
1F43→C3E temporary Y writes lie within the conservative hull[F63,F78), also
outside them; it preservesR0 for the five-word coefficient copy. These are
address-flow proofs; no DSP arithmetic execution/emulation used.

**VERIFIED recovered ARM parameter exclusion:** the exact Phase9 Y sink map
has no watched-cell write. The reviewed low-output wrappers and stock normal
mailbox/transport families retain earlier scoped exclusions. **UNRESOLVED:**
every foreign DSP Y write, SHI normal endpoint, saved-context mutation and
source-base/modifier preservation. These are explicitly retained, not called
normal dangerous-cursor publishers. The existing Phase6B foreign Y-write
inventory is reused for these watched cells; no new broad alias census.

## E–G. Reach, modifiers, interval versus exact-word alias

**VERIFIED conditional unions:** A writesX[2CCC,2D0C); B writes
X[2C02,2C22) andX[2C24,2C44). B has a two-word hole[2C22,2C24); do not
collapse its union into one exact interval. Each helper invocation performs
16*32=512 stores but touches only64 distinct X words because parity-selected
buffers repeat. It does not write a512-word contiguous destination.

ForM7=3FF, these concrete bases lie in the aligned ring[2C00,3000). None of
the32 updates reaches its boundary, so all addresses equal the linear result.
No24-bit wrap occurs for the initialized values. INIT2781 selectsM7=FFFF;
265 temporarily selects3FF and27F restoresfromY1A, initializedFFFF at27FA.
The local routine/helpers do not changeM6/M7. Other modifier/restoration or
SR-mode corruption is not silently bounded by these two reviewed cases.

**VERIFIED arithmetic distinction, N=32 and linear24-bit addressing:**

- Any write into **X[340,360)** occurs iff basec lies in **[321,360)**.
- A write to **X35F specifically** occurs iff basec lies in **[340,360)**.

The wider first window corrects using the count-word test as a whole-interval
test. Examplec=321 reaches340 on its last store but never35F; c=33F reaches
35E but not35F. These are arithmetic fixtures, **not normal-state witnesses**.
c=320 ends at340 exclusive; c=360 begins above the target. High24-bit wrap
cannot introduce340 in only32 updates. No initialized cursor lies in either
forbidden window.

**F. Whole interval during every normal invocation: NOT-YET-DETERMINED.**
**G. Exactly35F during every normal invocation: NOT-YET-DETERMINED.**
Both are **VERIFIED NO under the stated initialized-state premises**. No
VERIFIED YES path or forbidden normal cursor setter recovered.

## Entry classes and H. Asynchronous mutations

| Path | Classification | Result |
|---|---|---|
|25E4→260A;2789|BOOT/INIT|known cursor initialization/clear|
|1E80→1F5C|UNRESOLVED actual entry; NORMAL EFFECT candidate if parent reached|localA setup and guard proved|
|1EE5→1F5C|UNRESOLVED actual entry; NORMAL EFFECT candidate if parent reached|localB setup proved|
|1F9B→1F13|related INIT coefficient setup|does not call1F5C|
|valid immutable effect dispatch|recovered NORMAL EFFECT graph|55-entry table/+1 targets exclude1E15; index/table preservation unclosed|
|SHI19B /service5E|normal/service transport /SERVICE respectively|potential cursor mutation capability, not an established normal publisher|

SHI can writeY throughX10/X11 at19B between initialization and use. Its
reviewed ISR preserves the relevant arithmetic/register context and does not
directly modifyR6/R7/M6/M7; data writes can still mutate source/state words.
Audio ISR's reviewed low buffers/input ring and saves exclude the watched
tables and do not directly change those registers. Mailbox Y output and
shared-worker/context closure remain the recorded scoped uncertainties.
Separate private-core/shared addresses must not be merged numerically.

**VERIFIED limited publication lemmas:** a direct16-bit SHI data word has
low8bits zero, so no such word is in[321,360) or[340,360). Private5E publishes0;
if written directly into one cursor cell, its stock linear32 run is[0,20),
outside both targets. These lemmas do **not** protect count/base/modifier
redirection, other24-bit/DSP writes, or arbitrary service activity. They do
not imply custom-state service robustness or universal normal exclusion.

## I–M. Stopping decision and observation proposal

**I. Family remains open**, so it is not removed and no new broad X35F census
or invariant re-evaluation is launched. Prior known count writes remain0;
normal SHI saved-pointer/context and other state-loaded nonzero stores remain
unclosed as documented in Phase14. No positive-count producer recovered.
**J. Invariant remains NOT-YET-DETERMINED.** Neither ordinary preset pointer
preservation nor absence of direct setters proves every normal entry.

**K. Another broad static phase is not justified by the present evidence.**
The local cursor algorithm is bounded; repeating generic alias inventories
will not establish the missing normal-state invariants. Further static work
has diminishing returns without a concrete new producer/entry constraint.
This does not assert mathematical/static impossibility or that all remaining
domains are truly arbitrary. A newly identified specific writer may justify
a future narrow trace.

**L. Minimum useful observation, proposed only:**

1. Establish whether an **existing read-only, nonhalting trace facility** can
   expose DSP data accesses. Availability, pin access and safety are UNRESOLVED;
   no debug interface is assumed to support this.
2. For every observed normal203A entry, capturePC, effective load address35F
   and the24-bit value read. This directly tests the stated invariant.
3. To test this family too, capture every observed1F97 effective X write address
   and data. Optional attribution:1F89 sourceY cell/R6/cursor value, M7/SR mode,
   caller and stock count. Data must be captured at the instruction event,
   rather than inferred from later RAM snapshots.
4. Future user-operated stock transitions would cover note/release, patch/bank/
   effect, scene/project/transport and successive audio blocks; boot/service
   events must be separated. A nonzero35F at a normal203A event disproves the
   invariant for that path. All-zero finite coverage does **not** prove it for
   every possible transition.

No observation performed. Current static-only authorization does not allow
hardware access or configuring a debugger. The proposal requires separate
authorization before any hardware action; no firmware instrumentation, logging
writes, activeMIDI/SysEx, breakpoint/halting workflow or device-memory write is
assumed permissible. Passive SPI capture alone cannot exclude DSP-internal
transient writes. If suitable observation is unavailable, retainUNRESOLVED;
do not substitute a patch or intrusive debugger operation.

**M. Single best next step:** assess availability of a suitable existing
read-only/nonhalting observation method for **203A count loads and1F97 effective
writes**, before proposing any hardware action. No automatic Phase16 alias audit.

## Reproduction

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_p1f97_cursor_audit.py --output-dir builds/phase15/verified
```

Use a fresh path for repeats; overwrites andoriginal/ writes refused. Exports
include all32 cells, INIT store intervals, helper/local-state proofs, addressing
fixtures, inherited watched-cell obligations, async/entry ledgers and the
unexecuted observation schema. Original hashes, all five stream/payload pairs,
decoded-BIN equality, exact codec roundtrip and canonical DSP bytes are checked.

**VERIFIED reproducibility:**16 reports match byte-for-byte between the two
canonical runs; hashes are in `builds/phase15/reproducibility.json`. Both runs
passed protected-input, extraction, codec and DSP-byte checks. The489 inherited
foreign Y candidates are an old unresolved inventory, possibly including data
decodes; they are not489 proved normal aliases or a new broad census.
