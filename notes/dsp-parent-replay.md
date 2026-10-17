> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 19C-PARENT — normal predecessor and replay qualification

## Phase 19C-HOSTWRITE — parent execution still closed

2026-10-06. [dsp-host-write-provenance.md](<dsp-host-write-provenance.md>)
resolves ARM cache initialization toFFFF from stock initialized-data decoding.
It does not establish normal host cursor/order/extent preservation or a1E15
target. Private address setup updatesX10/X11; page/extended write forms retain
X11; cached data can inherit a read-advanced cursor. Nominal endpoint exclusions
are not effective-address proofs. Asset-loader lengths/page truncation/padding
and complete normal transition ancestry remain unresolved. No bridge recomputed,
no parent/helper or ARM CPU instructions executed, no new stock checkpoint.
Active-parent replay remains NO.204B remains independent, not reanalyzed.
Canonical evidence builds/phase19c-hostwrite/final-v3/ and checks-v3/.

## Phase 19C-TARGETBRIDGE — current target gate

2026-10-06. [dsp-effect-target-bridge.md](<dsp-effect-target-bridge.md>) records
**C: normal reachability UNRESOLVED**.640 conditional valid-table records
exclude1E15, but actual selector/table/descriptor0 preservation is unproved.
No parent execution or new actual active-loop/stack class derived. A future
stack proof must account for composite wrappers: DDC falls throughDE6; DCF
callsDDC and DD3 callsDE6 before the algorithm JSR. The earlier s+5 simple
wrapper budget applies to direct algorithm wrappers, not automatically those
additional-JSR routes. Table-valid domains must not become normal snapshots.
P19D host cursor/endpoints and204B/generic indirect contexts remain independent
obligations; no honest single-producer reduction achieved. Next: target-specific
normal ARM endpoint/cursor-retention proof intoP19D. No effect-chain hypothesis
removed, replay admitted, ROM/scheduler search, allocation or implementation.

2026-10-06. **VERIFIED static reconstruction; NORMAL-PATH UNRESOLVED.**
The original parent is mapped, but no defensible actual normal entry is
established. The requested stop condition applies: **0 parent instructions and
0 helper instructions executed in this phase**. No stock CPU instantiated,
checkpoint invented, hardware/device communication, firmware changes,
installation, ROM search or Plaits implementation.

The complete helper's previous **TESTED / BOUNDED-PROOF** result is retained.
It is not normal-runtime evidence. This phase also identifies why simply
reusing that inactive-loop snapshot would miss an important candidate caller
class: the effect chain carries an active outer DO.

## A. Parent boundaries and instruction-level structure

**VERIFIED:** both helper calls belong to P:[1E15,1F11), 167 decoded
instruction sites, RTS at1F10. The previous instruction1E14 is RTS;1F11 NOP
and1F12 RTS precede the separate coefficient routine1F13. This is the lexical
function boundary supported by control flow, not evidence of a runtime entry.
No decoded direct transfer from outside reaches any instruction in the parent.
Arbitrary computed entries and modified dispatch RAM remain separate unknowns.

| Parent instruction | Original target | Natural continuation |
|---|---|---|
|1E19 JSR|1FB2 prefix, including its EF2 call|1E1B|
|1E80 JSR|1F5C complete helper, family A|1E82|
|1EE3 JSR|1F13 coefficient update, including C3E calls|1EE5|
|1EE5 JSR|1F5C complete helper, family B|1EE7|

1E15/17 save incoming R6/R7 into X1D3A/B;1EED/EEF restore them for the
tail. They are not intrinsically X output pointers: the tail writes Y:(R7)+.
The parent contains no REP, explicit SP/SC/SSH/SSL/LA/LC/SR/OMR or modifier
register access, or direct peripheral access. Calls/DO/RTS implicitly use the
hardware stack. This parent-only observation does not certify its callees or
exclude an indirect peripheral address under an unproved context.

| DO site | Body / raw last-word LA | Count |
|---|---|---|
|1E22|1E24 /1E24|32 immediate|
|1E2C|1E2E /1E2E|16 immediate|
|1E3E|1E40 /1E40|X3A|
|1E4A|1E4C..1E4D /1E4D|X3A|
|1E57|1E59..1E5B /1E5B|16 immediate|
|1E6C|1E6E..1E73 /1E73|16 immediate|
|1E8B|1E8D..1E93 /1E93|8 immediate|
|1EBF|1EC1 /1EC1|16 immediate|
|1ECF|1ED1..1ED6 /1ED6|X3A|
|1F01|1F03..1F0E /1F0E|X3A|

**VERIFIED local branch relation:**1E1B loads X7C;1E1D masks0C;1E1E branches
to1E31 when zero. That path reaches1E80. Nonzero takes the1E22 clear and
either1E26 or1E2F to1E82, bypassing family A. All four masked values
0/4/8/C converge on the family B path and1EE5, provided calls return and
loops complete. No actual X7C guard value was recovered or chosen.
Neither helper JSR lies inside a parent-local DO body. That does **not** imply
LF0: an inherited caller DO can remain active throughout the parent.

## B. Normal reachability and exact missing predecessor

**VERIFIED static normal-role edges:** scheduler113..12C calls audio routine
1D9 at12A. Its block branch calls198D at1FC and CB8 at260. CB8 proceeds
through its local block loops into the effect chainD87. These recovered roles
classify code; no authentic scheduler execution or actual parent dispatch is
claimed.

| Indirect site | Classification of recovered code | Parent-selection obligation |
|---|---|---|
|DB6 JMP(R1)|NORMAL EFFECT chain wrapper dispatch|X[9EA+5*X95A+i] would have to contain1E15|
|DBD JSR(R0)|NORMAL EFFECT algorithm wrapper|table-derived marker advanced by1 would have to equal1E15|
|DC5 JSR(R0)|NORMAL EFFECT algorithm wrapper|same|
|DCD JSR(R0)|NORMAL EFFECT algorithm wrapper|same|
|DEC JSR(R0)|NORMAL EFFECT algorithm wrapper|same, after x:(R0)+ prefetch|
|DF9 JSR(R0)|NORMAL EFFECT algorithm wrapper|same, after x:(R0)+ prefetch|
|19AC JSR(R1)|NORMAL AUDIO descriptor dispatcher|descriptor+0 would have to contain1E15|

For legacy linear addressing, i=0..4; algorithm markers originate at
X[9DB+X(95B+i)] through DA3/DAD. DB2 reads the wrapper atX:(R3)+ and
DB6 tail-jumps to it, retaining DAE's original return frame. The five algorithm
callers establish R6/R7 at low Y buffers840/840,800/880,880/880,880/9C0,
840/9C0. Those register facts do not establish their target is1E15.

29EC..29F4 copies55 original words P[29F6,2A2D) to X[9DB,A12):15 markers
and eight rows of five wrappers. **VERIFIED conditional exclusion:** with
selectors X95A0..7, X95B..95F0..14, preserved table and linear addressing,
neither wrapper targets nor algorithm marker+1 selects1E15. The original
55-entry table does not contain1E15 or the required marker1E14.

198D's ordinary JLT descriptor walk visits X[EB,15B) with stride8.
INIT2881..28CF supplies twelve281 entries, then202B and1A2B. **VERIFIED
initialized-descriptor exclusion:** none selects1E15. No direct INIT or SERVICE
caller was recovered. INIT1F9B tail-jumps1F13; it does not call the parent or
1F5C.

**UNRESOLVED:** all normal producers/preservation of X95A..95F, mutable
X[9DB,A12), descriptor+0 words and addressing context. The recovered ARM
parameter subset excludes effect selectors/table and cursor cells; that is not
all DSP/host writes. An out-of-domain index or changed target is not accepted
as normal merely because no local bounds check prevents it. Absence of a
literal/direct call does not prove dead code.

The first missing bridge is an instruction-backed normal publisher/retention
proof supplying a parent-selecting indirect target. Inventing that target in
RAM would manufacture the very reachability this phase is meant to prove.

## C–D. Caller-owned stack and inherited loop

**UNRESOLVED actual:** SP, SC, active depth, LF/FV, LA/LC and resident
frame provenance at parent entry. Startup107/108's explicit SP/SC clears are
not imported through an unexecuted startup/scheduler chain.

**VERIFIED conditional effect-chain constraint:**D99's original
DO#5 has raw LA=DAF and LC=5..1. Its body includes DAE JSRDB2, DB6's tail
jump and each algorithm-wrapper JSR. JSR does not clear LF; RTS does not
restore SR. Balanced nested local DO exits restore the inherited LA/LC/LF.
Therefore, **if this chain selects1E15 and its balanced local calls/loops
complete**, either helper JSR inherits LF1, LA=DAF, LC in[1,5]. The parent's
own loops have already exited at those call sites. **This class is outside
the already-tested FULLHELPER LF0 class**, even if its depth happens to be3..7.

This is a conditional structural deduction, not a recovered normal invocation.
No separate active-loop execution was admitted without the missing target
bridge and live frame state. FV is not asserted as recovered stock state;
the sealed core's counted-DO model clears it, but a model rule is not an
actual entry observation. Manual counted-DO and forever-state qualifications
remain distinct from boot provenance.

With s the healthy resident occupancy at1D9 entry and earlier local loops
closed, an algorithm-wrapper parent entry would have d=s+5:
CB8 JSR+1, D99 DO+2, DAE JSR+1, DB6 JMP+0, wrapper JSR+1.
If mutable wrapper RAM instead sent DB6 directly to1E15, d=s+4 and input
R6/R7 would require separate provenance. Both target alternatives are unproved.
Descriptor dispatch would have d=s+2 via1FC and19AC, without a dispatcher
DO; its inherited loop still depends on its caller.

At either parent helper JSR, prior balanced local callees leave depth d.
The helper would add at most6 resident entries, as certified in FULLHELPER;
it must preserve the active outer frames, rather than replace them with an
opaque inactive prefix. Exact healthy-resident eligibility, extension history
and interrupt occupancy cannot be computed without s and the actual entry
contract. No depth is chosen to fit the old d3..7 tests.

References reused locally: DSP56300FM Rev5, section5.4.3; DO PDF297..298
(printed13-57/58), JSR PDF329 (13-89), RTS PDF408 (13-168). PDF numbers are
one-based cached page labels. No new documentation retrieval.

## E. Count, pointer, cursor and foreign-mutation provenance

| State | Original establishment | Qualification |
|---|---|---|
|X1D40/41/42 family A|immediates1E74/78/7C; stores1E76/7A/7E →1800/1840/18E0|VERIFIED local data flow; actual parent invocation UNRESOLVED|
|X1D40/41/42 family B|immediates1ED7/DB/DF; stores1ED9/DD/E1 →19F0/1A30/1AD0|VERIFIED local data flow;1EE3's original1F13 call intervenes before helper|
|X3A32, X3B16|INIT2655/56 givesX38=50;2812/14 givesY15=1;140..149 publishes N=1<<(50>>4)=32, N/2=16|VERIFIED reviewed publication relation, including pre-subtraction parallel stores|
|normal count refresh|1F1 JSR140 in audio block, before198D/CB8|VERIFIED static call; input/count retention and foreign writers UNRESOLVED|
|Y1820..182F|260A..261D, eight pairs2CCC/2CEC|VERIFIED INIT relation; completion/retention unproved at actual parent entry|
|Y1A10..1A1F|2610..261F, eight pairs2C02/2C24|same|
|M0..7FFFF|2779..2781|VERIFIED explicit INIT; not re-established by parent|
|M7 temporary3FF|265, restored27F fromY1A|VERIFIED static local sequence; actual parent context unproved|

Known parent store operands and prior conditional prefix/tail/cursor exclusion
reports are exported. Parent X scalar/base writes occupy1D3A..1D64; its fixed
scratch at1ED6 is X[2C46,2C66) when32/linear. Direct parent writes include the
1E5A zero-ramp and1E90/93 difference-ramp stores at X[1D43,1D53), plus
1E43/48 updates at1D63/64. Complete helper scratch stays in its previously
tested2Cxx intervals only under retained cursor/count/modifier relations.
The parent's tail restores incoming R6/R7 and emits64 Y words; the input and
output bounds remain conditional on the specific low wrapper and modifier.

Local Y coefficient/state stores do not overwrite the cursor tables under
the previously reviewed32/16/linear setup. They are not a foreign-writer
proof. SHI19B can write Y indirectly,198 can write X indirectly; normal host
endpoint closure, IRQ timing, mailbox jobs, worker physical aliasing and
retention of Y1A/counts/base cells remain **UNRESOLVED**. No interrupt/actor
exclusion is inferred from a lack of direct parent peripheral instructions.

## F–K. Execution, memory results and remaining blockers

**TESTED:** static audit and fail-closed qualification only. The seven unit
tests verify guard alternatives/unknown handling, control-edge parsing,
immutable opcode witnesses, output confinement/refusal and that a structural
snapshot or arbitrary `normal=True` flag cannot open the normal-entry gate.
Two CLI refusal checks reject required normal replay before creating output
and reject overwriting existing evidence.

**Executed original parent instructions:0. Helper instructions this phase:0.**
No natural parent JSR/helper-return/parent-exit trace exists. Previous40-run
FULLHELPER call/return certification is unchanged and remains BOUNDED-PROOF.
trace.jsonl is empty; watched-accesses.json explicitly says NOT EXECUTED.
These are absence of execution, not measured absence of accesses.

| Question | Result |
|---|---|
|Actual normal reachability1E80 /1EE5|UNRESOLVED / UNRESOLVED|
|Actual stack class recovered|NO; SP/SC/frame history unproved|
|Within old tested class|UNRESOLVED actual; candidate effect-chain LF1 is outside old LF0 class|
|Inherited loop compatible|No active-loop replay qualification; compatibility UNRESOLVED|
|Actual normal parent/helper can write high-X|UNRESOLVED; cannot report PROVEN NO FOR QUALIFIED NORMAL PARENT PATH|
|Actual path reads or writes X35F|UNRESOLVED actual path; VERIFIED no direct parent operand|
|Alters later203A count|UNRESOLVED universal/async; no local positive count producer or natural parent→203A edge proved|
|X35F invariant|NOT-YET-DETERMINED|
|New NORMAL-PATH execution evidence|None; only static predecessor constraints and conditional class distinction|

The exact remaining blockers are the target-producing predecessor, actual
caller stack/loop/extension state, preserved count/cursor/modifier/input
context, the symbolic guard/numerical-to-address dependencies in prefix and
coefficient callees, and asynchronous/foreign mutation contract. Do not
replace them with reset defaults or revive broad ROM/memory archaeology.

## L–N. Design gates and next step

**Theoretical verified256-word Plaits reservation X[5F00,6000):NO.** A
clearly hypothetical layout can still be sketched, but this phase supplies no
new normal ownership/reservation proof. Firmware implementation readiness:NO.
Whole-firmware normal memory safety stays NOT-YET-DETERMINED; service
robustness stays NO. No reservation, patch, port or hardware test was made.

**Single best next step:** a narrowly scoped producer/preservation proof for
normal effect selectors X95A..95F and the copied table X[9DB,A12). Establish
a genuine1E15-selecting value, or exclude that predecessor under proved normal
domains. Only a positive target bridge warrants a separate active-D99-loop
parent checkpoint/replay; do not seed the missing target or automatically
start boot/scheduler execution.

## Reproduction and files

New implementation: `emulator/harness/parent/audit.py`. New tests:
`emulator/tests/test_parent_gate.py`, `emulator/tests/verify_parent.py`.
No sealed core or prior helper implementation changes. Existing Python only.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B emulator/harness/parent/audit.py --output-dir builds/phase19c-parent/new-audit
& $py -B emulator/harness/parent/audit.py --output-dir builds/phase19c-parent/new-repeat
& $py -B emulator/tests/verify_parent.py --first builds/phase19c-parent/new-audit --repeat builds/phase19c-parent/new-repeat --output-dir builds/phase19c-parent/new-checks
```

Canonical evidence: `builds/phase19c-parent/final-v3/` and
`final-v3-repeat/`; verification `checks-v3/reproducibility.json` and
`checks-v3/unchanged-core-audit.json`. Earlier final/ and v2 exports/checks
are retained intermediate exports. v2 corrects the RTS manual page reference
and distinguishes the DB6 direct-tail depth alternative; v3 also includes
conditional zero-count skip edges for the four X3A-sourced parent DOs. These
edges do not seed an actual zero count or compatibility state.

Thirteen canonical files match byte-for-byte. Evidence includes complete
parent CFG, instruction witnesses, predecessor/initialized-target maps,
stack/loop and state provenance, memory/foreign obligations, closed execution
gate, explicitly unexecuted trace/watches, results and input/source hashes.
SYX/BIN hashes, in-memory decode/roundtrip equality, all10 DSP extraction
hashes, sealed203-file core/19A harness, prior FULLHELPER implementation and
validated19A executable identity pass. No existing firmware overwritten.
