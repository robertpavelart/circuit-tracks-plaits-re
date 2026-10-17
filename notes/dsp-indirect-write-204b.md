> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 13 — count-gated indirect X write at P:204B

## Phase 19C-P204B — latest producer/replay gate (2026-10-06)

**Result D / UNRESOLVED:** no normal positive35F publisher, active compiled
record constructor or attained destination was recovered. P204B is not excluded
universally from highX, selectors95A..95F, table[9DB,A12), any descriptor+0 or
35F itself. No positive checkpoint admitted;0 original CPU instructions, no
count/destination seed. Prior zero-count and single-store calibration remain
unchanged, with calibration kept separate from normal positive evidence.

**VERIFIED / BOUNDED-PROOF:** complete recovered1B89/1B7B direct-caller paths
(20 caller/bank domains, nine wrapper sites) write outside35F and prospective
record[360,3C4) under recovered counts/linearM1.1A99 loads3C4 into sourceR4;
actual1B90 output isR1. The source20 count at2FA/46C is not compiled35F/4D1;
ARM286E4 always carries0. Exact schema remains threeY pointers, coefficient,
oneX destination; record+4 consumed at2043, read2048/write204B.

**VERIFIED latch:**203A reads35F→X1;2040 copiesX1→24-bitLC.2045 replacesX1
for arithmetic without changingLC. Later memory-count changes alone affect
future invocations; record fields are fetched during the loop, with no atomic
table guard or recovered positive fill/count publication.20 is only a layout
hypothesis, not an enforced normalN maximum. Zero-skip mode remains explicit.

Six fixed scalar-reader arguments exclude the35D→saved35F precursor; variable/
generic normal read arguments/cache ordering and other foreign-state aliases
remain open. SERVICE5E private writes clear words, not directly publish positive
count; service read capability is not a normal-only witness. Assets remain frozen.
Current detailed report:[dsp-p204b-provenance.md](<dsp-p204b-provenance.md>).
Evidence:builds/phase19c-p204b/final-v4/, final-v4-repeat/, checks-v4/.
21 identical exports, focused schema/caller/scope tests, original/core/prior
evidence guardsPASS. Next: targeted normalP19D saved-cursor/cache/count-table
provenance, no generic alias census or unqualified positive replay.
Older next-step statements below are historical, not newly authorized work.

## Phase 14 update — first-writer analysis

Current report: [dsp-x35f-invariant.md](<dsp-x35f-invariant.md>), evidence
`builds/phase14/current/`. **Invariant NOT-YET-DETERMINED;204B remains a blocker.**
No normal nonzero count setter recovered. Through202B's fixed35F load and
zero-skip mode,204B cannot be the first nonzero count writer; other aliases
still need closure. Zero stores and indexed bit clears preserve zero even
if aliased. Private service5E transmits0 and cannot itself set a positive count.

Recovered host stream count now traced208FA→355E8→47C64→395E4:2740C bytes,
13A06 words; conditional union[E7FFFE,E93A06), excluding35F. Foreign count/
cursor preservation remains open. The precise next DSP alias is1F97, whose
Y-held cursor must exclude[340,360) under stock32/linearM7. No claim that it
is the only unclosed store; full census retained. Candidate not re-evaluated.

2026-10-06. Static Selection0/channel0 analysis. No hardware, binary writes,
firmware patching, service packets, or Plaits implementation/compilation.
Evidence: `builds/phase13/final/`; producer: `tools/ct_indirect_204b_audit.py`.

**Result:** **NOT-YET-DETERMINED** for *every normal invocation*. **VERIFIED**:
the recovered boot-clear and ARM parameter-update paths set X35F to zero;
they do not publish twenty active records here. Under count preservation and
the documented zero-skip mode, P204B executes zero times and its write set is
empty. A universal preservation proof is still missing. No nonzero publisher
or normal high-X occupancy witness was recovered. This is a narrowed proof
obligation, not proof that a nonzero publisher exists.

**NORMAL-RUNTIME SAFE: NOT-YET-DETERMINED. SERVICE-ROBUST: NO.**
No 256-word allocation is proved or reserved. Static analysis is **not proved
exhausted**; this phase stops without beginning a broad audit.

## A–E. Structure, index, destination and extent

**VERIFIED**, with linear M0 for the table walk:

| X address | Consumer | Instruction-established use |
|---|---|---|
|35F|203A→2040|hardware DO iteration count N|
|360+5*k|203B initially;2044 thereafter|R5: Y source pointer, indexed by N5|
|361+5*k|203C initially;2046 thereafter|R6: Y source pointer, indexed by N6|
|362+5*k|203D initially;2047 thereafter|R7: unindexed Y factor pointer|
|363+5*k|203E initially;2049 thereafter|X0: MAC coefficient, semantic name unresolved|
|364+5*k|2043|R4: absolute X read/write address, proved by2048/204B|

The initial four fields are loaded before DO. Each iteration reads the current
destination then preloads four fields for the next iteration. Final preloads
still occur; they are **not proved dedicated guard records**. At hypothetical
N=20 they read X[3C4,3C8), which1A99 uses as separate smoothing-source state.
The adjacent layout suggests room for20 five-word records; **HYPOTHESIS**, not
an instruction enforcing N<=20. `boot-clear-record-window.csv` exports all five
zero values for those20 positions at the **immediately-after-clear** checkpoint.
It does not claim twenty active records or final runtime values.

**VERIFIED conditional k domain:** k=0..N-1 for positive N, with hardware LC
latched at2040. Replacing X1 at2045 does not change that latched count. N=0
gives an empty k domain in zero-skip mode. No maximum valid k for all normal
invocations is proved. The source table's20 records are not a count bound here.

**VERIFIED per-record write:** one 24-bit word, read/modify/write:

`d_k = X[0x364 + 5*k]`

`write interval(k) = [d_k, d_k + 1)` in **X space**.

There is no destination postincrement at204B, no destination-length field,
and no `[d_k,d_k+N)` transfer. M4 cannot change the unindexed X:(R4) access.
For recovered zero-count paths, the exact write union is **empty**, rather than
X0: the initialized zero destination words are never consumed by2043.
For hypothetical positive N with unchanged clear values and k0..19, d_k=0;
this is a conditional calculation, not an observed normal invocation.

## Instruction-level consumer

| P | Operation and address implication |
|---|---|
|202B..2030|R1=967; clear38 X words, X[967,98D), under linear M1|
|2031..2039|multiply Y30 by integer60, ASR, A0→N5/N6; R0 fixed35F|
|203A..203E|read count and first four fields; R0 reaches364 under linear M0|
|203F|Y source prefetch occurs even if N=0|
|2040|DO X1, body2042..204B, continuation204C|
|2042..2043|multiply two Y source values; read current R4 destination|
|2044..2047|load next R5/R6/R7; multiply product by current Y:(R7) factor|
|2048|load B from current X:(R4), transfer computed A into Y1|
|2049|MAC current coefficient X0 with Y1 into B; load next coefficient|
|204A|prefetch next indexed Y source|
|204B|write B to same X:(R4)|

M0 governs table postincrements; N5/N6 and M5/M6 govern source indexing.
Startup2779..2781 sets all M registersFFFF in the documented legacy mode;
all normal entry preservation is **UNRESOLVED**. Y30 is initialized0 by
1BA8/1BA9, so the recovered source offset is0; generic foreign Y writers have
not been universally excluded. R0 is fixed35F: this consumer does **not** add
172*bank. Startup28AC..28C6 installs202B as a separate scheduler descriptor,
following the twelve voice descriptors. It is not twelve per-voice table copies.

**SOURCE-DERIVED:** DSP56300 DO skips a zero initial LC when SR compatibility
bit13 is clear; legacy set mode instead executes65536 iterations. See
[DSP56300FM, DO p13-57](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf).
The conditional DSP56724/25 register map reserves SR14..12 and resets them0:
[DSP56724RM, Table5-2](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf).
Do not confuse SR compatibility SC with the separate StackCount `sc` register.
Actual part/mode remains the earlier conditional hardware premise; no physical
identification or runtime observation was added.

## F–G. Provenance and mutation ledger

**VERIFIED INIT checkpoint:**2779 selects linear modifiers;2782 setsR0=0;
2783 setsX0=0;2784/2786 select6000 iterations;2788/2789 clear X/Y[0,6000).
Therefore X35F and the exported record window are zero immediately afterward.
No P-to-X initialized record image for360 was established. The31 RLE records
P[2309,2599) are **data**, populate external X[74000,7BC00), and cannot be used
as executable DMA instructions or local descriptor provenance. Phase12's data
correction is retained in this phase's instruction census.

**VERIFIED ARM count writer:**286BC inputs are r0=count, r1=bank. At286CA,
r1=count<<8;286D0 selects2FA+172*bank;286DA sends that count. At286D6 the second
address becomes35F+172*bank; **286E0 setsr1=0**, and286E4 sends zero. Bank0/1
thus gives X35F/X4D1, both zero. Normal27A10 supplies count20 to2872C; deferred
286F6 supplies explicit banks0/1 to286BC. The ARM serializer transmits bits31..8.
The separate source count is20; **the204B count is not20**.

**VERIFIED recovered ARM parameter-family census:** only286E4 overlaps
X[35F,3C4); no recovered parameter sink writes a five-word destination record
there. The census is exported and byte-checked; it is not all host traffic.

**VERIFIED distinct tables:**27A10 sends20 records at
X[2FB+172*b,35F+172*b), fields0/1/2/4, and tails3D0+172*b.
1A70→1B89 smooths field3 at2FE+172*b+5*i with recovered source count20.
657 consumes the source table and writes **Y:(R4)** at690, not X at204B.
4D5 operates the earlier banked control fields; no compiled-table producer was
established there. These routines are not evidence of a copy into360 or of
a nonzero35F publication. Later1A99 uses3C4 as an X *source* for smoothing;
1B90 writes throughR1, notR4, so this is not a compiled-table builder either.

**SERVICE:**5E can address count/record words while Selection0 remains active.
That defeats service robustness independently; it is not a normal-only blocker.

**UNRESOLVED every-writer closure:** an operand/literal scan does not enumerate
every computed alias. Remaining normal indirect X writes and host-transfer
domains have not all been excluded from35F,360..3C4, or modifiers/context.
The exported mutation ledger names proved paths and explicitly leaves foreign
writers unresolved. No claim that this is the complete writer/reader set.
Known consumer202B and recovery paths above are instruction-evidenced; unknown
aliases are retained. No semantic names for dormant fields are inferred.

## H–M. Collision, allocation gate and stopping condition

**H. P204B→X[5F00,6000): NOT-YET-DETERMINED universally.**
**VERIFIED NO conditionally** when X35F remains zero and zero-skip semantics
hold. This removes the supposed twenty-record/count-as-buffer scenario from
the blocker reasoning, but does not remove the count-preservation obligation.
For positive N the collision criterion is exactly whether any consumed d_k
is in[5F00,6000). No recovered normal d_k in that range. Unboundedness is not
a witness. No alternate-candidate search is justified by a proved collision.

No recovered high R4 values require peripheral/DMA reinterpretation: the proved
recovered path has no R4 stores. A future nonzero record must be classified in
X space, keeping private X, shared/external and peripheral addresses distinct;
numeric Y/core-private overlap is not an alias proof.

**I. Remaining obligations:** for this exact path, the single decisive missing
fact is **X35F==0 at each203A in normal Selection0** (or a complete nonzero
publisher/domain). The already documented effect selector/table/cursor,
AGU/context, paged transfer and scene/project/mode persistence obligations
remain separate. They have not been re-audited or silently declared closed.
The reviewed low ARM writes, selector7<=1E8B, X[C00,D00) staging, low effects
and direct DMA exclusion remain valid scoped evidence from Phase12.

**J. NORMAL-RUNTIME SAFE: NOT-YET-DETERMINED; SERVICE-ROBUST: NO.**
**K. Proven persistent256 words: no.** Successive-block and all normal
transition preservation cannot be certified from a conditional empty store
set. No allocation, state layout or sentinels created.
**L. Static analysis exhausted: not established.** Remaining pointers are
computed, but that alone does not make them statically unbounded. No passive
observation is presently proved necessary. If static closure ultimately fails,
the needed observation would be the value/provenance of X35F at203A, together
with any nonzero record destinations and table-walk modifiers across normal
transitions. Observation would be scoped evidence, not universal persistence
proof. None was performed or authorized by this report.
**M. Single best next step:** perform a targeted non-alias/preservation proof
for **X35F**, starting with the already-open normal effect indirect-write
domains and host transfer endpoints. If it is invariant zero, no dormant
destination values need interpretation. If a nonzero publisher is found,
follow that publisher only. No broad phase started automatically.

## Reproduction

Run with the existing Python runtime, no dependencies installed:

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_indirect_204b_audit.py --output-dir builds/phase13/final
```

Use a fresh path for another run; overwrites are refused. `validation.json`
records both expected original hashes, equality of decoded BIN, exact SYX
roundtrip, all five stream/payload hashes and instruction-byte checks. Evidence
contains source citations, per-field clear values, ARM overlap, formulas and
the unresolved allocation verdict. These are static evidence artifacts, not a
DSP execution trace or recovered runtime preset.

**VERIFIED reproducibility:** a second run under `builds/phase13/repeat/`
produced the same10 files byte-for-byte. `builds/phase13/reproducibility.json`
records their hashes. Both runs passed the original/extraction integrity and
codec equality checks. The complete all-normal table/writer domain remains
unresolved despite reproducible evidence; validation does not certify it.
