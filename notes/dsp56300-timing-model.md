# DSP56300 timing model — Phase 20A-TIMING

2026-10-06. **SOURCE-DERIVED / CALCULATED / CONDITIONAL.** This model evaluates
the existing standalone VariableSaw PC traces. It is not a cycle-accurate silicon
simulation, host benchmark, stock workload measurement or firmware allocation.
The renderer, numeric algorithm, native/restoring helpers and oracle are unchanged.

## Primary sources and applicability

Pinned local primary documents, not newly downloaded:

| Source | SHA256 | Relevant printed/PDF pages |
|---|---|---|
|DSP56300 Family Manual Rev.5|b2e8e346fe55b05d20ad0e6bc03d45fd1e080d46d9a9cd9540271c0c37f5a31e|3-19..21 /65..67;5-3 /83;12-10 /224; AppendixA-1..13 /425..437|
|DSP56724/DSP56725 Reference Manual Rev.1|3b9876887ca7ecfec99d6e331ce1587e13955d0ecb4d0e8643dafd1df689370f|1-8 /44;3-1..3 /75..77;4-4..6 /94..96|

**DOCUMENTED EXACT within the specified architectural premise:** AppendixA
table T assumes full instruction-fetch pipeline, internal P memory, no interlocks,
and post-update/no-update addressing. Addressing and interlocks are then added.
The manual defines one-cycle DIV throughput, five-cycle DO/REP setup,
three-cycle ANDI/JSR/RTS/JMP, and four-cycle short Jcc. Untaken Jcc adds one
cycle (A.2.6.3); this is not omitted because the instruction is untaken.

**DEVICE-FAMILY ASSUMPTION:** apply those detailed family timing tables to
the DSP56724 implementation. Device RM explicitly identifies DSP56300 cores,
seven stages, and two-cycle pipelined data-ALU latency with one instruction
initiated each clock; immediate ALU-to-ALU forwarding has no stall (4-4).
This is strong architecture correspondence, not physical Circuit timing proof.
No timing from a different implementation is silently imported. The emulator's
`opcodecycles.cpp` is not the authority: its generic totals omit the interlock
and untaken-branch accounting needed here.

**UNRESOLVED editorial row:** A-6 lists short absolute load1, then a malformed
`MOVE [x or y]aa` row2 without a source register. Visual inspection confirms
the malformed row is present in the PDF, not just extraction. Best/upper model
interprets row2 as store; this is an explicit **DEVICE-FAMILY ASSUMPTION**.
Lower model charges short stores1. No unsupported exact silicon claim is made.

## Instruction contributions

| Executed form | Base T | Extra | Evidence/class |
|---|---:|---|---|
|Register ADD/SUB/CMP/CLR/TST/NEG; ordinary DALU|1|Applicable accumulator move interlocks|A-6 default DALU row; device4-4 throughput; DOCUMENTED EXACT within premise|
|Signed MPY y0,x0,A|1|No stall to following ALU shift|A-7; DOCUMENTED EXACT|
|Immediate multi-bit ASL/ASR; ROL|1|ROL's register move overlaps ALU|A-2/A-6; DOCUMENTED EXACT|
|Register MOVE|1|Arithmetic/transfer stall if preceding instruction conflicts|A-6/A-9; DOCUMENTED EXACT|
|Long immediate MOVE/MOVEC|1|+lim1 =2 total; extension word counted once|A-6/A-7; DOCUMENTED EXACT|
|Long absolute X MOVE read/write|1|+lab1 =2 total; plus interlock if applicable|A-6; DOCUMENTED EXACT|
|Short absolute X load|1|Applicable interlock|A-6; DOCUMENTED EXACT|
|Short absolute X store|2 best /1 lower|Applicable interlock|Malformed second row; DEVICE-FAMILY ASSUMPTION|
|Y output MOVE A,Y:(R0)+|1|Observed transfer stall1; postincrement extra0|A-1/A-6/A-9; DOCUMENTED EXACT|
|ANDI #FE,CCR|3|No additional explicit-SR-read/bit-test stall form|A-2; DOCUMENTED EXACT within listed rules|
|Short absolute Jcc|4|+1 if not taken|A-4/A-13; DOCUMENTED EXACT|
|Short JMP/JSR/RTS|3|No stack extension in admitted instance|A-4/A-5/A-8; DOCUMENTED EXACT|
|DO #32|5|Ordinary backedge/exit0 extra|A-4;12-10; DOCUMENTED EXACT|
|REP #21|5|Each repeated DIV independently charged1; no loop-exit surcharge|A-8/A-4; DOCUMENTED EXACT|
|DIV Y0,A|1|Final DIV->MOVE A0,A interlock1 on transfer, not per DIV|A-4/A-9; DOCUMENTED EXACT|

No MAC/MACR, P-data MOVE, simultaneous X/Y access, same-space double-access,
preupdate addressing or modulo operation is executed. They receive zero counts,
not guessed timing. `instruction-timing.csv` identifies all458 static sites,
453 executed sites, machine opcode, word count, source rule, address surcharge,
actual interlock totals and applicability. All23 executed families are classified.

## Pipeline and parallel forms

**SOURCE-DERIVED** arithmetic stall: a move reads A/B or one of its subregisters
immediately after an ALU instruction targeting that same accumulator; add1 clock.
Transfer stall: a move reads an accumulator immediately after a move writes that
accumulator or any of its subregisters; add1 idle clock (3-20..21/A-9).
ALU-to-ALU dependency itself is forwarded and is not charged twice.

The analyzer applies those rules to consecutive *issued instructions*, including
DO backedges, REP iterations and real callee/return PCs. It does not add a
generic hazard to every dependency or assume one cycle per instruction.
No executed instruction matches both arithmetic and transfer hazards together;
the model refuses that case rather than inventing overlapping-stall behavior.

**MEASURED counts / CALCULATED additions:**4,998,482 arithmetic and1,142,210
transfer stalls in the38,641,041-opcode native trace. Explicit SR moves/bit-tests
and conditional Tcc address hazards are absent. Jcc tests CCR through its specified
control timing; no invented extra status-read stall is added. ANDI uses its
three-cycle control-register form, not a MOVE-from-SR or BTST form.

Exactly three parallel forms occur, once each per ratio call:

| Synthetic PC | Form | Cycles within admitted helper |
|---|---|---:|
|0x4AA|CLR B with Y0->A|1 total|
|0x4AB|TST A with X0->A|1 total|
|0x4B7|ROL A with B1->X1|1 total|

There are112.909707 such combined instructions per mean block. They are not
counted as two separate issue operations. No arithmetic+memory parallel form
is used by this renderer; memory MOVEs elsewhere are individual instructions.
At0x4B7 the prior instruction moves A0->A, but the parallel move reads B1;
the arithmetic use of A is forwarded, so no transfer stall is added there.

## Memory, AGU, loops and stack

**CONDITIONAL admitted memory:** private internal P:[0x200,0x4BC), X state,
controls/scratch below0xAC, Y:[0,0x20), all zero-wait. These addresses fit the
documented default *private* internal RAM on either DSP56724 core (RM3-2..3).
They are synthetic standalone labels, not Circuit stock reservations.

- X-only operations have one data access each. Y-only operations are the32
  output stores. No single instruction demands two accesses to the same space,
  simultaneous X/Y transfers, or P data transfers. Private P/X/Y buses are
  separate (RM4-6); ordinary data/fetch overlap has no added conflict here.
- Long-absolute/immediate instruction words carry their table lab/lim surcharge.
  Extension words are not counted as another opcode or charged again as a
  guessed fetch penalty. There is no external/cache/shared-bus wait in this model.
- Only explicit AGU destination is R0=0 atP:0x280. It precedes the first output
  by many more than the documented three-clock interlock window. M0..M7 are
  linear0xFFFFFF, initialized outside the renderer; no modifier writes occur
  during the call. R0 increments0..32; postincrement is part of nominal latency.
- DO at0x282 has raw LA=0x4A8 (assembler endpoint0x4A9), count32. It has31
  ordinary zero-overhead backedges and one ordinary exit. No degenerate/annulled
  loop, branch to LA/LA-1 or explicit ENDDO is present. The one-word output
  store at LA satisfies relevant endpoint restrictions.
- REP at0x4B4 repeats one DIV at0x4B5 exactly21 times, preserving the outer
  DO context. It does not create a new stack frame. Five setup clocks are charged
  for each occurrence, not once for the entire render.
- Only local subroutine is ratio. JSR/RTS each cost3, and stack depth is3:
  two outer-DO entries plus one ratio return. SEN=0 and initially empty resident
  stack exclude stack-extension memory traffic. Loop cleanup restores depth0.
- No injected dispatch/caller/audio scheduler cost is included. The validated
  renderer ends with its actual three-cycle JMP to done; no extra outer RTS
  was fabricated. A future real caller would have additional costs.

**UNRESOLVED outside this domain:** actual Circuit placement, shared-bus
arbitration, external waits/cache, DMA, IRQs and workers. Device RM1-8/4-6
specifies additional P shared-bus wait and arbitration; those mechanisms cannot
be folded into a finite bound without their configuration/activity. No unconditional
Circuit upper bound is claimed.

## Three timing outputs and broader bound

Each issued instruction is charged `T + EA surcharge + false-Jcc extra +
arithmetic/transfer stall`. Memory-wait, explicit-status and AGU additions are0
in the admitted domain. The emitted per-block CSV records each component.

1. **LOWER BOUND:** apply known interlocks/timing, but use1 for the ambiguous
   short-store row; full pipeline and no boundary allowance.
2. **BEST DOCUMENTED ESTIMATE:** same calculation with short stores2;
   steady full pipeline, private zero-wait memory and no asynchronous activity.
3. **OBSERVED-TRACE CONSERVATIVE UPPER:** best+12. Six clocks to fill and six
   to drain the seven-stage pipeline are allowed at the block boundary. This is
   a conservative **CALCULATED** allowance, not measured silicon overhead.
   Branch penalties already included are not duplicated as another flush charge.

Separate **CONSERVATIVE STRUCTURAL UPPER**,30,123 cycles: longest acyclic
startup156 +32×longest sample path936 +final JMP3 +boundary12. JSR is replaced
by a bounded82-cycle helper, valid for integer part0..3 under the established
ratio API n<4d. Both alternatives of every main conditional branch are retained,
including mutually inconsistent choices. Previous-opcode state is preserved
for hazards; after a summarized callee the previous instruction is its RTS.
There is no implicit assumption that the observed high-frequency test is the
absolute worst state. This structural bound is intentionally less tight and
still conditional on valid numeric API, resident memory and no IRQ/DMA.

Neither bound covers invalid inputs, interrupts, external waits or unidentified
silicon behavior. The finite upper bounds and conditional success gates apply
only to this explicit standalone execution model.

## Reproduction and validation

New read-only analysis scripts: `plaits/poc/timing/audit.py`, `verify.py`.
They read pinned PDFs/manifests and existing native/restoring PC traces. No CPU
is instantiated, assembler rebuilt, renderer rerun or wall-clock benchmark used.

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B plaits/poc/timing/audit.py --output-dir builds/phase20a-timing/run-new
& $taskPython -B plaits/poc/timing/audit.py --output-dir builds/phase20a-timing/repeat-new
& $taskPython -B plaits/poc/timing/verify.py --first builds/phase20a-timing/run-new --repeat builds/phase20a-timing/repeat-new --output-dir builds/phase20a-timing/checks-new
```

Outputs refuse existing directories. Canonical evidence is `final/`, `repeat/`,
`checks/` under builds/phase20a-timing. Hash manifests identify source and trace
inputs; deterministic reports are compared byte-for-byte. No hardware gate opens.
