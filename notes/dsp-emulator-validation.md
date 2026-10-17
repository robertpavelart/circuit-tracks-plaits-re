> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 18 — validation and stop gates for offline replay

## Phase 19C-PARENT — static qualification and refusal validation

2026-10-06. **TESTED:** emulator/harness/parent/audit.py produces13 canonical
static exports that match the independent repeat byte-for-byte. Seven unit
tests and two CLI refusals pass. Protected originals/all10 DSP extracts,
codec roundtrip, sealed203-file core/19A harness, prior FULLHELPER implementation
and validated19A executable identity pass. Evidence: builds/phase19c-parent/
final-v3/, final-v3-repeat/, checks-v3/reproducibility.json.
**No DSP CPU was instantiated;0 new DSP instructions executed.** Normal
checkpoint gate remains CLOSED for missing parent-selecting predecessor and
actual caller state. Inactive helper snapshots cannot be relabeled normal.
D99's candidate effect-chain inherits LF1/LA=DAF/LC1..5, requiring separate
qualification if a genuine parent target is proved. No active-loop test was
silently substituted. [dsp-parent-replay.md](<dsp-parent-replay.md>) records
the stop condition, static evidence and design gates. Authentic boot remains
unresolved independently; no ROM/scheduler search automatically launched.

## Phase 19A — offline substrate implemented and fixture-tested

**IMPLEMENTED / TESTED:** pinned C++ core, forced interpreter, authoritative
P/X/Y/shared fixture bus, CPU/loop/DMA/peripheral transaction logging, selected
reads and CPU snapshots.37 synthetic fixtures pass in4 runs each across2
independent builds with byte-identical traces. No Circuit image/startup or
modified firmware execution. Exact source overlays reproduce; vendor/original
and extraction hashes unchanged. Source/site guard rejects an added store file.

See [dsp-emulator-phase19a.md](<dsp-emulator-phase19a.md>),
[dsp-emulator-write-paths.md](<dsp-emulator-write-paths.md>) and
builds/phase19a/reproducibility-final.json. Passed gates cover the supported fixture
configuration, not all chip/ISA/peripheral behavior. JIT remains disabled;
unknown-state, stock map/OMR/host tables, worker/ICC and timing are unresolved.

**Next:** separately requested Phase19B immutable loading/provenance and startup
prerequisite resolution. Do not automatically execute stock startup. Normal
X35F/high-X safety stays NOT-YET-DETERMINED; serviceNO; no allocation/Plaits.
Historical design/NOT RUN statements below refer to unperformed stock tests;
covered synthetic19A fixtures have now been executed as documented above.

DESIGN + STATIC ONLY,2026-10-06. All execution tests below are **NOT RUN**.
Phase18exporter checks filebytes/source witnesses, not execution semantics.

## Phase19A acceptance: before trusting any stock trace

1. PinC++commit/buildoptions,assertinterpreter; headless/nohardware dependencies.
   Prove everyenableddecode form used by boundedstockcode has an implementation.
   Existingdecoder/disassembly fixtures are necessary but notexecution proof.
2. Validate24bit sign/leftalignment,56bitaccumulators,MAC/scaling/rounding/
   saturation,CCRbranches and parallelreadbeforewrite. No invented opcode
   interpretation; architecturalexpectedvalues with primary/manual provenance.
3. Validate allreachedAGUmodes:pre/post increment/decrement,indexedN,negative
   N=-3/-4,legacyM=00FFFF,FFFFFF,3FFwrap,bitreverse andnonpower-of-two modulo
   where used. Do not generalize a linearfixture to everyM/OMR/SRmode.
4. DOcount0/1/2/32,REPcount0/1/32,two-word repeatedop,nestedloops,stackrestore,
   interrupts atallowedloopboundaries. ValidatezeroDOunder bothrelevantSRmodes
   beforeasserting203Acount0skip. UpstreamDO/REPhelper behavior needs testing,
   not adoption asarchitecturalfact.
5. JSR/RTS,SSH/SSLread/write sideeffects,fastvectorJSR/longentry,prioritymask,
   savedPC/SR,RTIrestoration. IncludeSHI156saves/restores and1B4audioISR.
6. Exhaustive **store-form** coveragefixtures: absolute,indirect,pre/post,indexed,
   modulo,parallelX:Y/L,same-value,bitread-modify-write,P MOVEM/peripheral,
   REP/DOstores,DMAcopy/fill/externalsink,ICCworker,sharedaliases,loader/host.
   Oneaccessordinal percommittedword; two parallelspacewrites remain distinct.
   Useguarded/canarybacking inofflinetest memory plusindependentexpectedtrace
   counts to catchbypass; unchangedcanaries alone cannot detectsame-valuestores.
7. VerifyPC/opcode/eventattribution insideinternalDO/REPiterations. Outerexec
   callcount is notretiredinstructioncount. IRQ andeventorder must remain
   correct; don't injectextraIRQs intoREP if architecture forbids them.
8. Unknowninstruction,unmapped/undefinedmemory,unsupportedDMA/peripheralmode
   musthardfail. LogoldRAM withnonmutatingpeek;neverreadFIFO/status to logold.

Fixture expectations are independently authored from reviewedinstructions/
primaryarchitecture, not copied from emulator output. Crosscore/JIT comparisons
can expose discrepancies but are supplemental. Nohardware-facing upstream
difftest program is invoked. SyntheticfixtureP is separatetestdata; no stock
opcodeorfirmwarefile modification.

## Phase19B acceptance: stock load/startup

- VerifyexactpayloadSHA256,size24bitBE→P[0,2A5E),entry0→100 andvectors3E/44.
- Checkpost-uploadOMR/SR/mapprofile provenance; libraryresetdefaultsnotstockproof.
- RunstockSP/SCzero,M=00FFFF,clearloops/copies,cursorinitializer/descriptors
  when permitted bymapping. Captureallclearattempts includingY[4000,6000).
- Stop atout-of-mapYclear/EMCreadunless hardwaresemantics independentlyresolved;
  noRAMenlargement/silentignore. Partialprefix checkpoint isvalidonlyaspartial.
- CompareallfourP→Xcopiesbyte-for-byte withreconstructedmanifest, both16-cell
  cursorfamilies and14descriptorfields withdecodedinitializer expectations.
- Supplyhosttables/readinessconditionsfromverifiedsourceevents, notforcedflags.
  Hashalltables/fixtures. No fabricatedcompletepreset/checkpoint.

## Phase19C acceptance: service period and worker

-1D9threshold:below300no32-frameblock;at/above300callsequenceasrecorded.
-140constants:stockX3A32,X3B16,X3C31;32distinctsamplepositions,not31loops.
-198Drequest traverses14descriptors,includingX14B→202B→203A;19BFbitmap
  completion uses12voices. Distinguish counteddescriptors andactivevoices.
-759poll23reset edges, sharedqueuepublication,775result-progresswait,worker
  queue addressread120/source125/replacement126/finalprogress128 ordering.
  Missingrequests/lookupsource/progress event meansblocked, notinstantcompletion.
-Frameevent/DMA/audioISR order,twowords/frame,YFFE+2,YFFD+64perblock,
  ringM3FFwrap at400boundary; logtransfers, no codecneeded.
-Validateonlyselectednormalpaths.1F97normalreachisunresolved; do notdeclare
  itvisited merelybecauseahelperfixturepasses.

## Phase20 expected stock facts and differential traces

| Region | Independent static expectation | Required trace comparison |
|---|---|---|
|0/vectors|0→100;3E→1B4;44→156|branchdestination,opcodeboundary,IRQentry/RTI|
|260A|alternating2CCC/2CEC;2C02/2C24|32cursorcells and4copysegments exact|
|1F5C..1F9A|16outer×32inner=5121F97stores plus64clearstores;R7reload,no writeback|effectiveaddresses,loopcounts,cursorpreservation andhelperclobbers|
|CallerA initializedlinear|unionX[2CCC,2D0C)|Each512storewithinexpectedparityinterval;no340..360/35F|
|CallerB initializedlinear|X[2C02,2C22)∪[2C24,2C44)|Exactintervalunion;gap22..24notassumedcovered|
|202B..204C|R0=35F,countread203A;zeroDOskipunderverifiedmode|readbeforepostupdate,latchedcount,no204Bforzero;syntheticpositivecase separate|
|77F selectedmode|request versuscompletion;phasecommit7F9 onlycompletion|phase/register/pointer/memorywrites perstaticselectedpath|
|9C8..9D8/A8D..A94|mono32wordsX[2C46,2C66),gainramp/groupmix|samplecount,memorydestinations and24bitmath underknowncoefficients|
|Output|groupbuffers2DF0/2E50, ring32×2writes|callorder,64outputwords/pointeradvance,ISRinterleaving|

For eachknownbasicblock storeentrypreconditions,expectedPCsequence,register
deltas/flags,reads/writes andEAformula. Compare actualtrace atfirstdivergence
andstop withstate,eventqueue,callstack andprovenance. Don't automaticallyadjust
the expectation or fillmissingstate to obtain apass. Arithmetic unknowns remain
blockers where they influenceaddresses/control/outputs. Tables decodedascode
are notacceptedbasicblocks.

## Determinism, coverage and results

Two independentruns withsamefirmware/core/build/state/events/modelmanifest
mustproducebyte-identical canonicalJSONL traces andcanonicalfinalstate hashes.
Usevirtualtime/ordinal,stableeventties,nothostwalltime/pointers/threads. Increment
instructionordinalsforDO/REPiterations; lognonCPUactor eventsseparately.

Result schema records scenario,mode,preconditions,boot/normalboundary,target
PCcounts,writeractors/hookcoverage,IRQ/eventschedules,unknowns/faults,first
nonzero203Aload/high-Xnormalstore andtrace/stateSHA256. Property resultnames:
PASS_MODELED,VIOLATION_MODELED,NO_COVERAGE,BLOCKED,TRACE_INCOMPLETE.
Never translatePASS_MODELED into stockuniversalPROOF or AVAILABLE RAM.

Stop/deny progression on uncertaindecode,AGU/modulofailure,unhookedstore,
schedulerdivergence,materialworkeruncertainty,nondeterminism orotherunknown
inputs. No modifiedfirmware orPlaits follows from thesetests.

**ESTIMATE planned stages:**19Acore/hooks,19Bstockstartup,19Cmodels/scheduler,
20validatedreplay. Firstvalidatedstockprefixmayoccur at19B(secondstage);
firstintegratedownershipcoverageat20(fourthstage), subjecttoexplicitgates.

## Phase 19B actual result — 2026-10-06

**TESTED MATCH:** original stock P payload loaded/read back through Memory API,
10846 ordered load transactions, exact BE24 equality, header exclusion,
16 native load-decoded instruction byte/length matches and four direct targets.
Two completed invocations yield21 byte-identical exports. Unknown X/Y/P-tail
reads are denied; wrong identity, existing output and out-of-phase output are
rejected before loading/overwriting. Both input firmware hashes remain intact.
The existing203-file19A source guard and harness hashes pass before each load.

**STARTUP BLOCKED / NO EXECUTION COVERAGE:** 0 stock instructions. Chip reset
documentation and a separate empty-program constructor probe do not establish
the ROM handoff. Constructor PC/OMR reset-profile differences are recorded;
no stock execution mismatch occurred. Startup clears, tables, cursors,
descriptors, real peripheral accesses, interrupts and peer waits are NOT REACHED.
Peripheral/event fidelity is NOT MODELED by the load-only driver.

**Hash semantics:** P.loaded24.bin is concrete original readback. CPU/P/X/Y
tagged records serialize known/unknown state, not full executed final snapshots.
The empty execution/transaction/watch files are explicitly not passing replay
traces. Deterministic loading/gate reporting is tested; stock execution
determinism is NOT TESTED. The reset probe has no loaded stock image and executes
zero instructions. It cannot satisfy post-ROM register provenance.

Evidence: `builds/phase19b/checks/reproducibility.json`, completed load reports,
primary-manual pages under documentation/verified. Reproduction and exact scope
are in `dsp-emulator-phase19b.md`. Do not reuse fixture tags/defaults, force a
worker response, infer RAM ownership or begin19C automatically.

## Phase19B-HANDOFF validation — 2026-10-06

New audit byte-checks existing ARM witnesses against BIN and decodes the original
bootstrap/main100..106/worker100..12A through the existing static DSP decoder.
No interpreter execution is used. All input hashes are checked before/after.
The partial handoff manifest retains null unknowns; a separate inspector rejects
guessedSR, resetGPIO used as handoff, preseededICC token and execution enable.
Two static exports must match exactly; evidence and gate tests are under
`builds/phase19b-handoff/checks/`. Source guard checks the unchanged19A boundary.

**Still BLOCKED / NO EXECUTION COVERAGE:** architectural reset, bootstrap-local
preservation and application handoff are distinct. GPIO control latch semantics
are documented but handoff latch values unproved. ICC receive read side effects
must accompany peer-data reflection; disabled/empty ACK cases remain unresolved.
Explicit stack/AGU operands are absent from100..106, but inherited loop/IRQ
control is not established. Stock/worker/bootstrap executed instruction counts
remain0; the runtime startup/clear/table/cursor tests stay NOT REACHED.

## Phase 19B-SYMBOLIC focused validation

24 tests under `emulator/tests/test_partial_state.py` pass for partial-value
encoding, old-bit carry/latch masks, equality/taint refusal, small interrupt-field
equivalence, qualified synthetic ICC pending/ACK, and blocked original identity/
entry. Positive fixtures supply no stock ROM preconditions. These tests do not
certify full DSP decoding/CMP/chip IRQ generation or timing.

Original main/worker counts0: pending/PIC priority/SR.I makes the boundary before
P:0 ambiguous. Synthetic absent-request and masked-request cases show complete
SR/PIC words need not always be known. No empty queue, masks3, zero ICC read,
preseeded30002 or unproved post-ROM shim preservation was assumed. Evidence is
under `builds/phase19b-symbolic/`; stock startup checks remain NOT REACHED.

## Phase 19C-CHECKPOINT — 2026-10-06

**TESTED / BOUNDED-PROOF:** original-opcode address-only checkpoint slices are
implemented using the sealed Phase19A interpreter and authoritative memory hooks.
See notes/dsp-checkpoint-replay.md and notes/dsp-checkpoint-state.md.
Canonical traces: builds/phase19c-checkpoint/final/ and final-repeat/.

4164 cases execute24656 original opcodes per invocation:24576 at1F92..1F97,
64 cursor loads at1F89,14 zero-consumer instructions at203A..2040, and2
single204B consumer-calibration instructions. Unknown arithmetic/store data
remains SYMBOLIC/null. Numeric backing encodings are not stock values.
No authentic boot, full1F5C/1F90 DO loop or positive-count consumer loop executes.

The32 initialized cursor cells and each32-address body projection reproduce
X[2CCC,2CEC),[2CEC,2D0C),[2C02,2C22),[2C24,2C44), for M7FFFF/3FF.
There are no cursor-slice writes to X35F, X[340,360) or X[5F00,6000).
Both initialized-zero203A entries read35F0, load the four initial fields and
perform the Y prefetch before DO0 skips204B. One-word204B behavior is calibrated
separately with cleared destination0; no normal positive producer is invented.

These are PROVEN FOR CHECKPOINT DOMAIN address properties, not universal stock
invariants. Isolated slices do not replay inherited loop edges/stack/call paths
or async interference. Cursor/count/record/modifier preservation and parent
reachability remain UNRESOLVED. No family is removed from the universal blocker
set. X35F normal invariant / persistent high-X availability remain
NOT-YET-DETERMINED; service robustness remains NO. No Plaits PoC gate passes.

TESTED:13 canonical files identical;6 schema tests;5 native refusal gates;
protected original SYX/BIN and all ten extraction hashes intact; sealed203-file
core plus existing19A harness guard passes. Linked-library/binary hashes are
exported separately. Evidence: builds/phase19c-checkpoint/final-checks/reproducibility.json.

Next: qualify the complete1F5C nested-loop checkpoint stack/control relation
and symbolic-data interface to join the isolated body slices through original
DO/call instructions. Do not invent stack defaults or turn this into a ROM
search, hardware session, firmware patch or automatic scheduler replay.

## Phase 19C-FULLHELPER — 2026-10-06

**TESTED / BOUNDED-PROOF:** complete original P:[1F5C,1F9B) helper and
P:[C9D,CB8) callee now execute as joined control flow, including the real
caller JSR at1E80/1EE5 and natural return to1E82/1EE7.
See notes/dsp-full-helper-replay.md; canonical exports are
builds/phase19c-fullhelper/final/ and final-repeat/.

The admitted class is explicit: initialized caller pointers/counts/cursors,
retained M0..6FFFF and M7FFFF/3FF; healthy resident SP=SC=d, d3..7 before
caller; inactive LF/FV; opaque prefix and incoming LA/LC. These depths/flags
are SYMBOLIC finite structural class bindings, not recovered actual stock
stack values or normal-runtime invariants. Other/active/extension-dependent
classes refuse; no guessed ROM or reset stack is used.

40 cases per invocation execute385880 original opcodes,9647 per case
(including one caller JSR). Original DO yields16 contexts x32 stores at1F97,
64 initial clears,32 C9D calls and returns,66 DO executions. Complete helper
per case writes1728 X words and160 Y words. Actual LC countdowns, address
ordering, return frames, peak d+6, restored depth/LA/LC and unchanged opaque
prefix all match. Cursor words remain unchanged; all body intervals match
Phase19C-CHECKPOINT. Numeric arithmetic data/results remain SYMBOLIC/null.

PROVEN FOR CHECKPOINT DOMAIN: no read/write to X35F, X[340,360) or
X[5F00,6000). This is not an incoming-zero proof or universal ownership.
No natural helper-to203A chain or positive-count publisher is established.
Actual normal parent entry/stack/loop class, foreign mutations and async
interference remain UNRESOLVED. Universal X35F invariant/high-X persistence
and service robustness verdicts remain unchanged. No persistent Plaits layout
or firmware-implementation gate passes; only explicitly hypothetical design
assumptions remain possible. No Plaits work was performed.

TESTED:11 canonical exports match byte-for-byte, including full traces,
watched accesses and final symbolic CPU/X/Y state. Seven refusal gates pass;
protected SYX/BIN and all ten extraction hashes match; sealed203-file core
and19A harness source guard plus validated19A binary identity pass.
Evidence: builds/phase19c-fullhelper/checks/reproducibility.json.

Single best next step: resolve actual normal reachability and stack/loop entry
of parent1E15 feeding1E80/1EE5, connecting the local structural class to a
specific normal path. Do not artificially join203A or launch broad alias,
ROM-source, hardware, scheduler or Plaits work automatically.
