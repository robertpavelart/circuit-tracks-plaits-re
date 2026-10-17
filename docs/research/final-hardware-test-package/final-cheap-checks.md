> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Current supersession notice — final pre-hardware review

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

Evidence precedence: [final allocation decision](<../final-indirect-resolution/findings.md>) controls the remaining software proof boundary; [USB joint-path closure](<../final-two-check-closure/usb-joint-closure.md>) records 36 passing focused cases. [Phase67](<../phase67-final-safety-disposition/findings.md>) retains its bounded configuration/query/authorization-to-capture-entry scope. The original audit body below preserves the earlier two-gap checkpoint. No model PASS is physical proof.

Only the allocation proof remains incomplete; no actual >8-byte post-READY allocation was found, absence not proven. User risk acceptance and reported favorable Claude review do not enable tools or convert UNKNOWN to PROVEN. No candidate hardware test has occurred. Exact identities/accepted risk/next step: [CURRENT_STATUS.md](<../../CURRENT_STATUS.md>), [NEXT_STEPS.md](<../../NEXT_STEPS.md>). No further peripheral emulation is requested.

## Historical original cheap-check audit — superseded status/next steps

The body below is preserved verbatim as historical evidence. Its concurrency UNKNOWN, two-gap decision and earlier recovery wording are superseded by the current notice, final joint closure and recovery-status.txt. It is not a competing current verdict. Candidate/tool byte accounts remain applicable.

# Final operational pre-hardware checks — Phase68

**OPERATIONAL PREFLIGHT = UNQUALIFIED. No hardware action is admitted.** User supplies the external Claude verdict REASONABLE TO PROCEED WITH CONTROLLED HARDWARE TEST; the review text itself was not supplied here. This audit addresses the additional requested gates, not a new peripheral phase. Phase67's bounded scoped PASS remains valid. The stronger all-root post-READY allocation census and full BOT/diagnostic concurrency closure are not established by that PASS or by this static inventory. No new firmware defect is demonstrated.

## HASH BINDING — PROVEN

Exact BIN SHA-256 `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9`; SYX SHA-256 `9b420521a366c65c13fb871778fdbab612ca126cbb4ad60d0fd5bc12ecd253da`; CRC-32/MPEG-2 `1BB21302`; marker N63DEV. Read-only independent SYX decode equals the BIN; CRC recomputed, not inferred from size/end. Exact package copies equal those frozen source files.

`phase-binding.json` identifies saved result files bearing the full exact hash. Phase64 continuity/model-tests/identity-preservation; Phase65 continuity/negative-tests/preservation; Phase66 continuity/model-tests/audit-identity explicitly bind that BIN. Phase64 startup.py decodes the Phase63 SYX and asserts the decoded image hash; Phase65 imports that loader and supplies its IMAGE to the selected runner; Phase66 independently decodes/asserts the same hash and injects IMAGE/CANDIDATE_SHA into its selected runner. No phase is NOT HASH-BOUND. Protocol-only helpers are not independently claimed complete firmware replays. No completed replay was rerun.

## CLASSIFIED DIFF — PROVEN byte accounting, STRONG INFERENCE semantics

`classified-diffs.json`, produced by `static_checks.py`, authenticates every final component/trampoline against saved metadata, every explicit patch against final bytes, retired pool FF clearing and appended FF padding. SC35D8 baseline SHA `1525c6662bbff9ced7e6055bb54e864615c30013f1b4dec4be6c404f8c750c05` is checked. **39,468 changed/added bytes, zero unexplained** versus SC35D8; **1,523 differences, zero unexplained** versus Phase61. These are different comparisons from Phase63's saved 1,558-byte Phase62→Phase63 diff. Added FF padding is counted in the baseline comparison; no regenerated image was used.

Every changed function is listed below; addresses and lengths refer to authenticated component metadata. All other component/trampoline identities remain equal. Marker changes N61GEO→N63DEV are identity changes. No unexplained code/data change was found.

| Function | Address | Phase61→Phase63 bytes | Known fix / consequence |

|---|---|---:|---|

|snapshot|0806D500|422→498|Reservation admission cap/cursor guard plus NOR disk-object predicate and first-mount/recheck comparison; incorporates the Phase62 reservation correction.|

|begin|0806CF00|54→76|NOR-only FS predicate; unchanged pre-export remount enters recheck instead of destroying the first snapshot.|

|register|0806DB00|68→72|Accept legitimate recheck lifecycle while retaining NOR registration binding.|

|slow|0806E100|60→64|Preserve legal first-mount/recheck lifecycle.|

|stride|0806ED00|76→80|Allow legitimate first-mount/recheck stride publication; later changes still invalidate.|

|entry|0806F900|228→274|Explicit READY/rejection/AUTHORIZED/terminal status dispatch.|

|export|0806FF00|176→184|Allow a new readiness-query session to replace an unconsumed export; explicit status framework. Frozen host policy is stricter: no automatic retry.|

|status|08074100|0→136|New 39-byte CRC-protected status packet emitter.|

|classify|08074400|0→94|Explicit lifecycle-to-status classifier.|

|status_drain|08074700|0→116|Bounded USB-only status drain.|

|raw|08070B00|536→604|Ownership fence before CPU reads and common frame exit; fence helper embedded in raw component.|

Semantic source cross-check: `builds/phase63-defect-closure/construct.py`, FENCE and module source transformations; saved reviewed component listings and sd-mount-fix/status-protocol/buffer-ownership reports. A metadata match establishes byte accounting, not independent semantic correctness by itself; saved counterexample/regression evidence supplies that separate layer.

## POST-READY ALLOCATION CENSUS — UNKNOWN / NOT CLOSED

`allocator-census.json` and `allocation-requests.csv` retain the exact candidate binding. The scan identifies 596 immediate allocator/wrapper **candidate** references (including potential decoded-data/mid-instruction false positives), not 596 proven reachable requests. Each row records caller, target, size where a saved Phase66 startup observation exists, and UNKNOWN post-READY/pending-capture reachability. Startup-observed sizes do not prove runtime reuse of the same callsite. No candidate was silently labeled runtime-safe or discarded because replay did not execute it.

The direct-edge worklists start at USB HS vector offset174→080574D0, Main loop0801D5AC, parser0801EB30, Storage08024014, BOT08026DB0, SCSI0803B27C, class callbacks080228A8/080228D6 and diagnostic0806F900. They encounter no allocator target through the traversed direct edges. **This does not close the requested census:** jump tables, computed branches and queued/virtual callbacks remain. The complete post-READY scheduled-task/handler set is not proven. Root results enumerate each unresolved dispatch; these are software reachability coverage, not a silicon-timing question.

Important exact unresolved mechanisms include Main's event dequeue/`BLX R6` at **0801D010**, reachable through the post-READY service loop; parser handler `BLX R8` at0801EB58; Storage operation jump table08024070 and virtual calls08024086/080240D8; BOT/SCSI backend calls0803B52E and0803B658. Many known fixed backend targets have historical evidence, but the complete callback-producing set and all state-dependent target/size arguments were not closed here. The inventory is deliberately not called a complete CFG. No full DWT/USB model was added.

**Answer: whether ANY >8-byte request can occur after READY or before/while capture is pending is UNKNOWN.** Zero new allocations on the Phase67 fixture remains PROVEN within that fixture. It is insufficient to state no reachable allocation exists from every requested root. A request >8 is not demonstrated as a concrete runtime occurrence; nor is absence qualified. Minimal remaining work is static closure of the event/callback producer set and reachable allocation-size arguments, using these exact unresolved sites, not another startup/peripheral replay.

**PROVEN exhaustion instructions:** `0801D7D8` rounds R0 to four-byte size, compares cursor+size against the cap from20002B44, commits20002B48 only if admitted. Rejection at **0801D7F4 executes BKPT #1**; if execution continues,0801D800 loads R0=FFFFFFFF and returns at0801D804. It does not return NULL. Generic allocator0801CFA4 calls the wrapper at0801CFAE and tests `CBNZ R0` at0801CFB2: FFFFFFFF is accepted as nonzero, not gracefully handled. Example construction caller0801CFDC requests12 and checks only zero at0801CFE0; the variable-sized companion request is0801CFD2. These constructor paths are not proven reachable after READY. Physical BKPT exception/debug behavior is UNKNOWN here; no claim of graceful fault recovery. Allocation overflow/wrap for arbitrary hostile sizes is not excluded by the normal nonoverflow bound. Physical memory/stack margin remains UNKNOWN.

## STACK/FENCE STATUS — PROVEN in saved Phase63 model

Phase63 `dma-regression.json`, not Phase61 measurements: minimum Main SP **200080FC**, Main frame **20008198**, used604 bytes below high guard20008358; low guard2000775C gives2460 bytes of model guard separation. Storage minSP20009174, used204. These are prepared-model measurements, not physical margin or a full symbolic maximum.

Raw entry08070B06 pushes20 bytes,08070B08 subtracts260: **280-byte local/save contribution**. R7=frame base; payload R7+192..255 (fixture20008258..20008297); packet+16; guards+12,+180,+188,+256. Fence08070D00 adds24 bytes (five saved registers including LR plus4), then calls native yield0801BE60 if an owner remains. It **yields**, rather than pure busy-spinning or releasing owners; its own caller/RTOS frames add depth.

Fence predicates:400264B8 EN=0,400264BC NDTR=0,[20006968]+16 request flag0,[[20006968]+4]+8 semaphore1. At08070D36 native yield; back edge08070D3A→08070D04. Both before read consumption and common exit require all conditions. Raw exit calls the fence before08070CB6 ADD SP/POP. Thus a timeout/TEF/missing completion can retain the frame indefinitely. Saved31 cases include TEF/missing0/4/8, late same-request completion, TCF-before-DMA-release, duplicate IRQ/timeouts, disconnect pending, producer preemption and busy backend. No frame return with pending ownership was admitted in those tests. They were read, not rerun; no bounded unwind or physical completion guarantee is asserted.

## USB STORAGE CONCURRENCY — partial PROVEN, complete exclusion UNKNOWN

Exact candidate retains BOT/SCSI and its initialized backend. Backend table20003788 via global200037AC: READ08057E88, WRITE08057EF4, ready08057E44, protection08057E48. Host READ10 dispatcher0803B480..0803B52E invokes the read callback. That zeroes its transfer buffer, drains via vtable+1C→08023FD6, invokes vtable+C→08024130 with selected base+(LBA<<12), then filters/substitutes serial-marker content and returns0 even if the lower result was not successful. This generic SCSI success is not diagnostic authenticity.

Queued wrapper08024130→08023F68 submits a24-byte operation1 descriptor through08036708; wrapper drain08023FD6 sets request/wait state at wrapper+16, signals task at+20 and yields0801BE60 until clear. Storage task08024014 dispatches to the shared NOR backend08022F94→08037430. Phase66 wrapper global20006968→2000AC94; backend pointer wrapper+4→20000378; same shared backend semaphore offset+8 and request/queue state are relevant to the diagnostic fence. These exact pointer values are synthetic boot-model state, not physical-unit observation.

**Can Windows storage activity be outstanding while the diagnostic waits? STRONG INFERENCE YES:** endpoint traffic/queued work need not vanish when Main yields, and previously queued host Storage work can precede the diagnostic read. Endpoint reception and class dispatch are asynchronous to Main. The exposed class can exist from retained settings; Phase67's saved composite has both registered children. No exclusive-storage admission lock is established merely by diagnostic authorization.

**UNKNOWN:** complete joint IRQ→endpoint-queue→consumer context/ordering and all outstanding BOT callback lifetimes during this diagnostic. The endpoint/virtual callback dispatch gap named in the allocator census also prevents calling this a proven complete concurrent replay. Do not assert BOT directly performs a blocking Storage call inside USB IRQ solely from a callback xref; current evidence establishes eventual BOT/SCSI→Storage submission, not every caller context.

Read-only host requests do not themselves change geometry or request NOR program/erase. Normal WRITE10 is rejected by initialized write-protection; lower write capability and malformed continuation exclusion are separate. Unrelated queued persistence can still be serviced by a drain. Shared-queue contention may delay the diagnostic; the Phase63 busy-backend test preserves raw-frame ownership/failure containment, but is not complete simultaneous host-BOT proof. No demonstrated raw-buffer alias or one-shot bypass is claimed, and their universal absence is not inferred. The intended operational control therefore denies OS removable-storage access before connection; automount disable alone is insufficient. Complete concurrency exclusion remains an unclosed operational gate rather than hardware-only uncertainty.

## HOST TOOL STATUS — PROVEN mock freeze, LIVE LOCKED

`live_host.py`, version1.0.0-phase68-locked; exact SHA in HASHES.txt/host-tool-identity.txt. Pure local codec dependencies and lazy WinMM transport are included. All live CLI operations, including list, check operational-gate.json before transport import. No unlock CLI switch. `live_host.py mock` passed32 fake-clock/transport cases; no transport import, MIDI ports, emulator or native runner. An initial mock temp-directory ACL problem was confined to test setup; placing temporary mock IO within the workspace resolved it. No hardware action occurred.

New freeze differences from the preserved Phase63 host: all live actions locked; same-process human approval after geometry validation and before authorization; durable marker retained even for NOT_READY (stricter no-retry policy); package-local codec imports and mock command. Capture mode initially sends geometry only; authorization is a separate subsequent send in that same process after local validation and explicit approval. A standalone geometry-only run ends the session and cannot be reused to capture. Exact protocol, timing, publication and port logic are in host-tool-identity.txt. Real WinMM/USB timing remains UNKNOWN.

## UPLOADER STATUS — PROVEN exact binding, LIVE LOCKED

One byte-identical frozen Phase63 uploader serves candidate, B1.3 restore and official4486 restore. Its three allowlisted hashes, product checks and no-op limits are in uploader-identity.txt. No new enabled uploader was constructed, opened or sent. A locked intended tool is frozen; an operational live release is withheld pending the unclosed gates and explicit user decision.

## ROLLBACK PROVENANCE — PROVEN local bytes, origin UNKNOWN

Both rollback SYXs are included as exact copies of provisioned files; hashes/sizes in rollback-manifest.txt/HASHES.txt. B1.3 is manifest-matched official+COPY/ADD reconstruction. Official4486 local bytes match prior evidence, but **not authenticated against an independently acquired Novation-origin copy**. No vendor provenance or physical rollback is invented.

## WINDOWS/MSD POLICY — prepared, not applied

windows-msd-policy.txt distinguishes mount prevention from storage denial. Windows may issue filesystem-related writes if a writable volume mounts; the candidate's normal WRITE10 protection is an additional defense, not permission to browse/repair or proof of all BOT states. Preconnection procedure combines recorded automount policy with removable-storage deny-all policy; if not supported/effective on the sending machine, STOP. No OS policy or device state changed here. Class-policy applicability and actual enumeration remain unverified.

## RECOVERY STATUS — user report only

PROVEN BY USER (as supplied in this request): recovery/bootloader mode can be entered, and a power cycle exits to B1.3. No new observation here. Host recovery enumeration, uploader handshake, known-good recovery flash and recovery from a non-booting candidate remain UNKNOWN. See recovery-status.txt.

## Decision

The package is frozen and human-readable, but **not released for a hardware test**. Hash binding, byte classification, saved fence evidence and mock host behavior pass their scopes. The requested all-root allocator/size closure and complete Storage/BOT concurrency proof are not closed. These are specific offline coverage gaps, not demonstrated firmware corruption and not correctly relabeled hardware-only. No firmware change is justified. Do not broaden peripheral emulation, open MIDI or transmit. Keep existing Phase67 evidence and this audit.

OPERATIONAL PREFLIGHT = UNQUALIFIED
