> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 18 — minimal offline stock DSP replay specification

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

2026-10-06. DESIGN + STATIC ANALYSIS ONLY. No harness written or run, emulator
build/execution, firmware modification, hardware/device access, MIDI/SysEx,
OnCE/JTAG, flashing or Plaits implementation. Analysis exporters only.

**Decision:** use the existing pinned C++ DSP56300 **interpreter first**.
The design can support targeted stock traces; it does not yet establish a
complete Circuit Tracks model or upgrade X35F/high-X availability. Explicit
missing-state gates must fail instead of inventing a successful execution.

## A–B. Core choice and comparison

**VERIFIED local source:** `builds/vendor/dsp56300`, commit
44353be2f0156cac970c6ab4f467ea1998b40605; GPLv3 LICENSE.md.
`DSP56K_FORCE_INTERPRETER=ON` selects interpreter execution. DO/REP, parallel
moves, AGU/modulo/bit reversal, system stack and interrupt implementations exist.
56362 SHI/ESAI/DMA/timer models are reusable foundations, not a validated56724
peripheral map. `dsp.h::execInterpreter`, `dsp.cpp::do_start/rep_exec` and
`dma.cpp` are newly inspected witnesses inphase18. Implementation and tests
existing in source do not certify full opcode/hardware coverage.

| Criterion | Chosen C++ core | Existing Rust toolkit |
|---|---|---|
|Pinned source|44353be2…|c60aeedb6a6014850204c71e53bc0cf5b3104222|
|Execution|Interpreter and JIT; force interpreter first|Cranelift JIT; no separate interpreter identified in reviewed crate|
|ISA coverage|DSP56300 implementation; reached instruction forms must pass fixtures; unknowns fatal|DSP56300 decoder/emitter; prior decoder tests do not validate execution|
|5672x relevance|Core family compatible candidate; derivative maps/ICC/EMC require adaptation|Same ISA relevance; embedder peripheral model missing|
|P/X/Y|Separate arrays plus bridge/mirror facilities; default topology unsuitable|Buffer/callback regions; direct-buffer stores bypass generic method|
|AGU/DO/REP|Implemented; legacyFFFF/loop-zero/parallel ordering must be validated|Implemented helpers/emitters; same validation obligations|
|Interrupts|Pending/vector/stack/RTI machinery|Interrupt core state and JIT handling|
|Peripherals|SHI/ESAI/DMA/timers for56362|Callback interface, not a Circuit Tracks model|
|Write interception|CPU bus paths available; peripheral/DMA fastpaths need mediation|Inline constant/dynamic stores require emitter hooks or all-RAM callbacks|
|License|GPLv3|MIT|
|Build|CMake≥3.15, C++17, existingasmjit/base; interpreter still linksasmjit|Rust/Cargo, Cranelift and target-lexicon dependencies|

**Recommendation:** C++ interpreter minimizes initial JIT instrumentation and
reuses peripheral/IRQ code. No GUI, wxWidgets, audio driver/plugin, VTune,
updater or hardware-facing test dependency is needed. Use a headless harness
target linked to the existing static library; debugger GUI OFF. Avoid upstream
Release flags as an unexamined validation profile; pin compiler/options and
enable assertions/sanitizers where available. No builds/installations now.
Do not write a decoder from scratch. Rust remains a useful independent decoder
and possible later differential implementation; agreement between cores alone
is not architectural truth.

## C. Exact program images and startup facts

**VERIFIED primary image:**
`firmware/dsp/build-4486/selection0-channel0.payload24.bin`,32538 bytes,
10846 big-endian24-bit words, SHA256
`b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855`.
Load P:[0,2A5E), entryPC0. P0 jumps100. Vector3E→1B4 (audio),44→156 (SHI).
The `.boot24.bin` has a6-byte count/address header; do not load it as opcodes.
Source ARM range starts offset1F0; payload starts1F6. P contains code **and**
constant tables; never execute a linear disassembly's data rows by assumption.

**VERIFIED worker image:** Selection0/channel1 payload,1092 bytes/364 words,
P:[0,16C), entry0→100; SHA256
`adf8da1b2b889d069eb52935dbdc4ce9092210d29df719937ca5ac5f62dfa91a`.
Worker main loop10E, lookup120/125/126. Keep separate P/private state for
each logical endpoint; physical core assignment remains a conditional profile.
Selection1 diagnostic programs are excluded from normal scenarios.

**VERIFIED startup:**100 waits on ICC030002;107/108 zeroSP/SC;10F→25DB calls
2A2D,2779,27F8,2644,260A,22A3.2779..2781 establishesM0..M7=00FFFF.
2788/2789 attempt X/Y[0,6000) zero writes;2791 clears sharedX[30000,38000).
25F3 waits forXFFF nonzero, then copies1024 X words C00→2800;2602 waits on
X193F, then1F9B initializes related coefficients. Do not label these host
values arbitrary readiness flags or force them to1 without proven provenance.

| Verified stock copy | Source P | Destination X | Words |
|---|---|---|---:|
|2620..2623|262C|1D53|16|
|2629/262A|263C|7D|8|
|271D|268C|1EDD|139|
|29F2|29F6|9DB|55|

The existing reconstructed manifest supplies exact copy expectations, not a
complete startup checkpoint.260A initializes Y1820..182F alternating2CCC/2CEC
and Y1A10..1A1F alternating2C02/2C24. Descriptors are twelve normal8-word
records X[EB,14B), followed by two scheduler records through15B; X14B=202B
is the recovered count-routine dispatch field. Ring/staging/bank/voice constants
and pointed-to state must derive from stock initialization and normal host
inputs, not blanketzero after startup. Phase4/5 descriptor/output maps are inputs.

No sentinel opcodes, patched waits, synthetic HALT/return trampoline inP or
replacement firmware. Stop externally at a verifiedPC/stack-return boundary.
Stock self-writes, if reached, update only modeledP and must preserve normal
cache invalidation while being logged; original files remain immutable.

## D. Initial registers and provenance

Use a declared **post-upload** entry profile, not a claimed boot-ROM simulation.
Prefer stock startup. The bootstrap establishes OMRbit7/22 set,21 clear, then
jumps into ROM; the complete ROM handoff/SR/otherOMR bits are **UNRESOLVED**.
Upstream resetHW'sPC/OMR=0, R/N=0, M=FFFFFF are emulator defaults, not Circuit
Tracks entry observations. They cannot silently substitute for a stock profile.

| State | Classification | Requirement |
|---|---|---|
|PC|VERIFIED INITIAL VALUE|0 at uploaded-image entry; stock branch100|
|SR/MR and interrupt masks|MUST BE MODELED|Declared reset/handoff bits;109ORI MR/10Abset21/25F1ANDI MR executed; loop/scaling modes retained|
|OMR|MUST BE MODELED|Known bootstrap bits plus explicit unknowns; chosen memory/core profile recorded, not whole-register proof|
|SP/SC|DERIVABLE BY RUNNING STOCK STARTUP|107/108=0 before firstJSR|
|SSH/SSL/system stack/SZ|MUST BE MODELED|Architecture side effects, nesting,DO/IRQ/RTI; unknown unused cells acceptable until read|
|R0..R7|DERIVABLE BY RUNNING STOCK STARTUP|Each first use must have provenance; R0=0 at2782; no assume allR retainzero|
|N0..N7|CAN START UNKNOWN conditionally|Read-before-write stops;1F5C initializesN1/N3=2,N4=-3,N5=-4; other liveN must be supplied/derived|
|M0..M7|DERIVABLE BY RUNNING STOCK STARTUP|2779..2781=00FFFF; ring/filter changes restored fromY1A; validate legacy mode, not assumeFFFFFF equivalent|
|A/B/X0/X1/Y0/Y1|CAN START UNKNOWN conditionally|Only dominated scratch; full-width arithmetic modeled before first live consumption|
|LA/LC/DO/REP flags|MUST BE MODELED|Real nested-loop/system-stack semantics and zero counts|
|VBA/IRQ priorities/pending events|MUST BE MODELED|Declared map/profile and stock configuration; no disable IRQs and call it normal|

Maintain initialized/provenance metadata forRAM/registers. Unknown memory reads
fault; unknown live operands affecting address/control/results fault. Explicit
unused scratch may remain unknown only with validated operand use/kill tracking.
Poison variants are useful tests, not a proof that unknown inputs never matter.
Isolated fixtures may seed documented registers/stack to enter a whole function,
but must be tagged conditional unit tests, separate from startup-derived normal
execution. Never begin at1F97 or203A with fabricated enclosing state.

## E. Memory profile and unresolved startup gate

**SOURCE-DERIVED conditional profile:** candidate56724, MS=1/MSW1=1/MSW0=0;
endpoint0 proposedcore0 P[0,4000),X[0,6000),Y[0,4000); endpoint1 proposedcore1
P/X/Y[0,2000). Shared[30000,38000) has explicitly declared views/backing.
Actual part/core/boot mode and aliases remain conditional.
[DSP56724RM, Tables3-3..3-6](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf).

Word addresses are24-bit; RAM words storelow24bits in hostu32; arithmetic
uses architecture widths/sign/limiting, not hostfloat approximations. Key private
storage by(endpoint,space,address). X35F andY35F are distinct; workerX35F and
mainX35F are distinct. SharedX producer/Y consumer convention needs verified
translation to one backing store, not a global X/Y/P bridge. Log logical and
resolved physical addresses; retain origin views for aliases.

Sparse peripheral maps cover reached X/Y registers withinFFE000..FFFFFF;
do not turn that entire window into RAM. Sparse external ROM/table/EMC regions
require source hashes and defined contents/semantics. Startup accessesX40000
under EMC commands and X80000 initialization: not ordinary zero-filledRAM.
UnloadedP remains unknown/nonexecutable until a stock write initializes it.

**UNRESOLVED blocking discrepancy:** startupY[4000,6000) clear exceeds the
conditional privateY limit. Do not enlargeY to6000, alias it toX, silently
drop those writes or report full startup success. Resolve documented decoding/
external routing/discard behavior and selected mode first. Every attempted
access is logged; default invalid/unmapped accesses STOP. Any later legitimate
discard/open-bus rule must be explicit, evidenced, profile-specific and tested.
Partial init routines below that boundary may be validated separately.

Memory decoding must follow modeled OMR/configuration writes. A profile change
must not silently migrate, clear or merge backing stores. Resolve each access
through the current map; preserve unchanged backing contents and report changed
views explicitly. Unsupported remapping is a stop condition.

## F. Complete write interception contract

**DESIGN requirement, not a completed audit:** one authoritative memory/bus
transaction path for every CPU, worker, DMA,host and loader store. Record every
store including old==new, initialization and rejected attempts. No property
pass if any write path can bypass the logger.

Each record includes global ordinal, virtual tick, instruction ordinal, actor/
endpoint,scenario/BOOT_INIT/NORMAL/HOST_MODEL/UNIT_FIXTURE origin,PC (nullable
for nonCPU),causalPC,opcode word(s), access ordinal, logicalspace/effectiveword
address, canonical backing+offset, old/new24-bit values, Rn/Nn/Mn before/after
where applicable,SR/OMR, call path,IRQ depth,eventID and commit status. Absolute
stores use nullRn; DMA/workeradapter must not invent aCPU PC. Unknown old values
are tagged, not silentlyzero. Backing peeks must not trigger peripheral reads.

| Path | Required interception |
|---|---|
|CPU normal/absolute/AGU stores|DSP::memWrite→Memory::dspWrite plus translation metadata; EA before postupdate, after preupdate|
|P MOVEM/self-write|memWriteP/set plus exact opcode-cache invalidation for aliases; no stockfile write|
|MOVEP/bit/peripheral writes|memWritePeriph and every peripheral-mediated RAM destination|
|ParallelX:Y/L|Two space-specific commits grouped under one instruction; preserve architectural read/write ordering|
|DO/REP|Each executed iteration logged, not merely driverexeccalls; maintain PC/opcode/loop state|
|DMA|memCopy memcpy/getMemPtr and directmemFill paths must be scalarized or emit equivalent ordered per-word transactions; external bus included|
|Worker/shared/ICC|All writes routed through same canonical bus; progress/handshake changes also recorded|
|Loader/fixture/host writes|Separate provenance/epochs; no invisible RAM overlay between normal instructions|
|JIT|Disabled and asserted for first harness. Later use requires constant/dynamic/parallel/P stores and optimized loops audited and tested|
|Invalid/unmapped|Log attempted transaction, fault; no silentwrite-ignore|

**VERIFIED newly found bypasses:** interpreterDO runs internally;REP subsequent
iterations call a cached function without normal execInterpreter/onExec callback.
Per-instruction callback/retirement/event hooks need insertion at those boundaries.
`dma.cpp` hasmemcpy and directfill fastpaths independent of theJIT. Existing
onMemoryWrite alone supplies neither complete actor coverage nor adequateEA/
register/alias metadata. Default C++ bridge/mirrors cannot be trusted unchanged.
No core adaptations implemented inPhase18.

Wrappers may attach context, but emit only one commit record at the authoritative
bus boundary. Use transaction IDs to associate attempts, translation and commits
without double-counting them. The observer cannot alter emulated state or call
side-effecting reads. Track call paths from actual JSR/RTS and IRQ transitions;
distinguish DO-loop stack entries from return addresses.

## Selected read and entry observation

Optional read filters:X35F,X[340,360),X[5F00,6000),Y[1820,1830),Y[1A10,1A20).
Log actual read result at the normal read transaction; no second peripheral
read to obtain a value. Keep all writes even when read logging is sparse.
Capture every actual203A instruction after IRQ arbitration and before execution,
plus its load transaction, R0/mode/caller context and currentX35F. If an indirect
interior entry hasR0!=35F, record the divergence instead of forcing the address.
At1F97 record actualR7 destination and full pre/postAGU context.

## G–H. Minimal peripheral and worker contracts

| Module | Minimum classification/scope |
|---|---|
|SHI|NOT REQUIRED for isolatedunit replay; EVENT INJECTION with minimal FIFO/status/HTX/width/commandlane for normalhost-event replay throughstock44→156|
|ESAI|EVENT INJECTION SUFFICIENT for discrete two-slot frames and IRQ3E; no codec/DAC/USB/UI|
|DMA|FULL MODEL REQUIRED for the active channel modes, not all hardware: exact TX4/RX0 staging/rearm/transfers and writes; unsupported modes fault|
|Timers|MINIMAL STUB SUFFICIENT for reached virtualcounter reads; any enabled timing-sensitive IRQ/control behavior must be modeled, never genericzero|
|Interrupts|FULL MODEL REQUIRED for used priority/mask/fast-longentry/systemstack/RTI and service ordering|
|ICC/worker|MINIMAL derived adapter SUFFICIENT conditionally; exact queue accesses, state and timing contract required|
|GPIO/PLL/CIM/EMC|Minimal explicit register/handshake/map subset; unresolved startup semantics remain gates|

**Worker recommendation B:** deterministic derived model of stockchannel1
100..12A, consuming shared queue addresses, reading the correct workerX source,
replacing each queued word and publishing progress with stock ordering.759
reset handshake must assert/deassert paired pollbit23;775 waits on ICC progress.
Account for advertised progress before result store at121 versus final128,
queue boundary and event interleavings. Do not instantly complete everyrequest,
fill missing tables withzero, or return results in an assumed unifiedX/Y map.
Bind each result to source-region/hash or preceding buswrite provenance.

Fidelity order A(stockworker secondcore)>B(derivedadapter)>C(boundfixture
responses)>D(existingrequest-freepath). Effort order generally reverses.
B is the minimum integrated candidate only if its relevant read/write/handshake
trace agrees with the stock worker contract; otherwise useA or stop. Adapter
PCs are null with conceptual source labels, not falselyexecutedworker PCs.
C/D serve narrow tests only and cannot exclude all worker/normal aliases.
No new bypass branch added to stockP. If worker-private/table state or write
aliasing materially remains unknown, normal ownership verdict is blocked.

## Scheduler path and waits

**VERIFIED recovered order:**

1. Main113→1C53/1FD1 host/table jobs;X13 gates1FD6→1D9.
2.1D9 computes(YFFE−YFFD)&3FF; below300 returns without a block.
3.1EF..1F5→1C01/140/19F3/759;32-sample counts, group clears and workerreset.
4.1FC→198D traverses14 eight-word descriptors.19AC callsX14B target202B
   after the12voice records; **203A is in request pass**, not necessarily after
   effect processing.
5. Worker lookup activity overlaps request/completion;1FE→19BF consumes voice
   bitmap and77F;775 completion waits on consumed-result pointer.
6.200..22A group work;242..24E bank convergence;260→CB8 effects.
7.276→21C4 output;27B advancesYFFD by64 words for32frames. Interleaved3E→1B4
   ISR transfers two ringwords/frame, rearmsDMA and advancesYFFE bytwo.

**Do not invent the requested linear chain:**1F97 belongs inside1F5C, called
from1E80/1EE5 inparent1E15. Normal reachability of that parent remains unresolved;
valid immutable effect dispatch excludes its entry. Treat it as a separately
specified conditional fixture unless an actual stock event path reaches it.
No-target-hit is not a passing normal alias test.

Waits/dependencies:ICCstartup102,hosttableXFFF25F3/X193F2602,ringoccupancy1D9,
worker pollbits769/76E,lookup progress779,main enableX13, reached mailboxjobs,
ESAI/DMA service. Every wait has a finite modeled-event/instruction budget and
diagnostic pending-state dump. Missingevent returns BLOCKED, not patchedNOP,
forcedPC/readvalue or hostsleep. Actual elapsed physical timing is not established.

## Determinism and implementation gates

Single-threaded virtual scheduler; no wallclock/audio/MIDI threads or randomness.
Use per-instruction/event ordinals, declared virtualcycle profile and stable
tie-order. Preserve instruction atomicity/parallel ordering; IRQ delivery occurs
only at validated architectural boundaries, includingDO/REP. Stage events are
acceptable for unitfixtures, not claimed physical timing. Timing-sensitive
integration needs supportedcyclecounts or explicit schedule variants and limits.

Canonical UTF8JSONL, LF, fixedschema/sortedkeys, integers/fixed-widthhex as declared,
no pointer addresses/walltime. Hash trace and canonical finalRAM/register/peripheral
state withSHA256; hash manifest of firmware/core/build/map/events/fixtures/model
versions. Same fullmanifest→byte-identicaltrace andstate. Keeptracecomplete; if
budget/storage limit reached, STOP with incomplete verdict, neverdropstores.

Planned phases (not implemented):19A core/bus/hooks/ISA+AGU+loop+IRQ fixtures;
19B immutable stock loading/startup prefix, then proveninitialization;19C targeted
scheduler/frame/SHI/workercontracts;20 validated stockscenarios/property traces.
**ESTIMATE:**2 stages to first validatedpartialstockexecution at19B;4 planned
stages to integratedtargetreplay at20. Map/hoststate/worker blockers may add work;
this is not a promised deadline or a full-device emulation estimate.

STOP on uncertaindecode/AGU/loop,hookbypass,uninitialized/unmapped access,
unsupportedperipheral/DMA,missingworkerdata,schedulerdivergence,nondeterminism,
logoverflow or materiallyunresolvedworkerbehavior. Modifiedfirmware remains
out of scope regardless of clean finite traces. More details in
[dsp-replay-scenarios.md](<dsp-replay-scenarios.md>) and
[dsp-emulator-validation.md](<dsp-emulator-validation.md>).

**Single best next step:** Phase19A only after explicit implementation instruction.
No allocation or stockinvariant upgrade follows this design.

## Static evidence reproduction

`tools/ct_replay_spec_audit.py` exports candidate/coverage/state/event requirements
and byte-checked existing DSP/source witnesses only; it is not the replayharness.

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_replay_spec_audit.py --output-dir builds/phase18/final
```

Use a fresh directory. Independentrepeat/integrity hashes:
`builds/phase18/reproducibility.json`. No binaries/source dependency refetch.

**VERIFIED export checks:**15 final/repeat static reports match byte-for-byte.
Both supplied firmware hashes, all five extracted stream/payload pairs,
decoded-BIN equality, exact SYX roundtrip and source/DSP witness checks pass.
These checks validate evidence integrity, not emulator semantics or execution.

## Phase 19B implementation status — 2026-10-06

**IMPLEMENTED / TESTED:** separate `emulator/stock/` load-only target reuses the
unchanged sealed19A core. It verifies the original Selection0/channel0 identity
before P loading and reads every loaded word back; headers are excluded. It
provides no stock interpreter execution entry. **0 stock instructions executed.**

**UNRESOLVED / BLOCKED:** post-bootstrap ROM handoff is not architectural reset.
The separate constructor probe's PC0/OMR0 differs from device SHI reset PCFFFFFE
and documented OMR CDP=3. Neither probe values nor presumed zero RAM may become
stock preconditions. Tagged unknown CPU/X/Y state and unloaded P tail are retained;
guarded reads deny unknown memory. Conditional hardware extents are metadata, not
a claim of actual allocation/map. No full stock operand/unknown-register tracker
or Circuit peripheral/event model is implemented by this loader.

See `dsp-boot-handoff.md`, `dsp-stock-startup.md`, `dsp-emulator-phase19b.md`.
The next gate is the minimum live handoff/GPIO/ICC contract for P0→100..106,
not scheduler replay. Canonical19B exports: `builds/phase19b/completed/` and
`completed-repeat/`. Phase19A synthetic certification remains unchanged;
stock-loading API validation adds no CPU execution/peripheral certification.
