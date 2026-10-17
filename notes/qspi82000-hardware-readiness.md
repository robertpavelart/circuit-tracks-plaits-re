# Current readiness — final pre-hardware review

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

Evidence precedence: [final allocation decision](<../docs/research/final-indirect-resolution/findings.md>) controls the remaining software proof boundary; [USB joint-path closure](<../docs/research/final-two-check-closure/usb-joint-closure.md>) records 36 passing focused cases. [Phase67](<../docs/research/phase67-final-safety-disposition/findings.md>) retains its bounded configuration/query/authorization-to-capture-entry scope. The frozen [package audit](<../docs/research/final-hardware-test-package/final-cheap-checks.md>) preserves the earlier two-gap history, with a current supersession notice. No model PASS is physical proof.

Current risk acceptance, recovery limits, exact identities and future release preparation: [CURRENT_STATUS.md](<../docs/CURRENT_STATUS.md>). No authentic target capture has occurred; no new peripheral modeling or hardware action is requested.

**H4 remains FAILED (H4 = FAIL) for bounded in-session recovery.** On any failed or uncertain raw capture: discard all partial evidence; DO NOT RETRY; send no second diagnostic/Storage request or cleanup command; full physical power OFF, USB unplugged, session ends. No forced semaphore release. A reset, new process, session identifier or deleted attempt marker is not a power-cycle substitute.

## Historical Phase28–66 readiness entries below — superseded status/next steps

Older candidate hashes, banners and continuation instructions below are phase-scoped history, not current authority. Phase61/62 are failed/superseded; do not flash. Original bytes follow unchanged.

<!-- phase63-current -->
**Phase63 update: UNQUALIFIED.** Targeted mount/status/DMA fixes pass scoped regressions; continuous startup and complete postboot allocation coverage remain open. All live tools are locked. See [Phase63 findings](<../docs/research/phase63-defect-closure/findings.md>). Historical Phase61 and Phase62 images remain ineligible.

# QSPI $82000 hardware-readiness audit

2026-10-15. Candidate: unchanged phase27 fixed-range read diagnostic on B1.3. No application image, firmware-update SYX, device access, or reference/pinned-source edit was performed.

**PROVEN — the current candidate fails admission.** The diagnostic calls a Storage-task backend directly from Main. The real QSPI interrupt notifies Storage, while the real completion callback waits on Main. Execution blocks before checking the already-set controller-complete flag. This failure is reproduced with the actual phase27 handler and stock IRQ/wait instructions; it does not require original coefficient bytes. The earlier 197 checks remain valid within their modeled boundaries, but their modeled OS-wait success concealed this task-context requirement.

**UNKNOWN — target-byte preservation verdict: NOT PROVEN.** The modeled normal application-staging erase/program ranges avoid `$82000–$821FF`. That bounded result does not establish every bootloader/first-boot persistent operation. No evidence in this audit establishes that the target was modified either. Do not install this candidate to obtain evidence.

## Evidence and scope

The principal executable probes and their results are:

| Exact workspace path | Purpose |
|---|---|
| [full_failure_probe.py](<../builds/phase28-hardware-readiness/full_failure_probe.py>) / full-handler-failure.json (local-only reference: `builds/phase28-hardware-readiness/full-handler-failure.json`; not distributed) | Actual candidate handler, backend, QSPI IRQ, and current-task wait; decisive failure |
| [irq_context_test.py](<../builds/phase28-hardware-readiness/irq_context_test.py>) / irq-context-result.json (local-only reference: `builds/phase28-hardware-readiness/irq-context-result.json`; not distributed) | Independent Main-versus-Storage completion control |
| [storage_effects.py](<../builds/phase28-hardware-readiness/storage_effects.py>) / storage-effects-result.json (local-only reference: `builds/phase28-hardware-readiness/storage-effects-result.json`; not distributed) | Actual staging address/command algorithms with modeled completion |
| [stack_probe.py](<../builds/phase28-hardware-readiness/stack_probe.py>) / stack-probe-result.json (local-only reference: `builds/phase28-hardware-readiness/stack-probe-result.json`; not distributed) | Captured Main stack bounds, bounded successful-path model, guard control |
| [midi_schedule_test.py](<../builds/phase28-hardware-readiness/midi_schedule_test.py>) / midi-schedule-result.json (local-only reference: `builds/phase28-hardware-readiness/midi-schedule-result.json`; not distributed) | Actual router/USB packetizer with modeled completion and scheduler ticks |
| [objects.py](<../builds/phase28-hardware-readiness/objects.py>) / object-evidence.json (local-only reference: `builds/phase28-hardware-readiness/object-evidence.json`; not distributed) | Captured RTOS, updater, backend and MIDI object identities |
| static-evidence.json (local-only reference: `builds/phase28-hardware-readiness/static-evidence.json`; not distributed) | Host header selector, source hashes and stock/B1.3 instruction-span comparison |

**PROVEN:** these probes use `C:\Proj SSD\CODEX\CIRCUIT\plaits\poc\authentic_qualification\environment.py:authentic_session`, the pinned running-RAM fixture, verified stock instructions, and published B1.3 COPY/ADD spans. No complete candidate image is assembled. Static excerpts are in `C:\Proj SSD\CODEX\CIRCUIT\builds\phase28-hardware-readiness\`. Of 53 application excerpts compared, 52 match stock. The DIN excerpt differs only in the short-message callback at `$08021024`; B13-DIN-dispatch.txt (local-only reference: `builds/phase28-hardware-readiness/B13-DIN-dispatch.txt`; not distributed) confirms its SysEx branch `$0802102C–$08021042` still uses `$0801C894`. USB SysEx dispatch is unchanged.

**PROVEN:** the unchanged prior patch-plan.json (local-only reference: `builds/phase27-qspi-read/patch-plan.json`; not distributed) changes only application hook `$0801EB30–$0801EB33`, marker `$080101E8–$080101EB`, and appended fragment `$0807A414–$0807A735`. Fragment SHA-256 is `7cc4fe6ac3a031da839df2f45ae9cf69453ff12a4de32678527e752da28c5696`. Code/hook/marker changes total 810 bytes; prospective packaging requires two alignment bytes. Future aligned application size would be 436,024 bytes (`$6A738`). These are size calculations, not a generated application or approved package.

## Normal update storage path and target preservation

**PROVEN:** ct_fw.py:encode (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/ct_fw.py:117`; not distributed) emits INIT `$71`, HEADER `$7C` with **selector 0**, image version/size/CRC, WRITE `$72` blocks from block 1, then FINISH `$73` carrying vector block 0. Payload blocks are 32 bytes with `$FF` padding. Its exact header excerpt/hash is preserved in `static-evidence.json`; the encoder was inspected, not invoked to generate firmware.

**PROVEN:** ARM header handler `$08039088–$08039102` decodes the selector, checks `<4` at `$080390BC`, selects `[$20003CC8+4*selector]`, and stores the selected bundle at updater state `+$1C`. Captured descriptors are:

| Selector | Base | Capacity | Significance |
|---|---:|---:|---|
| 0 | `$00000000` | `$80000` | Normal application staging |
| 1 | `$000D4000` | `$1F2C000` | Separate storage bundle |
| 2 | `$00082000` | `$12000` | Coefficient/resource bundle; includes requested evidence |
| 3 | `$00094000` | `$40000` | Separate storage bundle |

Sources: 08038eec.asm (local-only reference: `builds/phase28-hardware-readiness/08038eec.asm`; not distributed), 080390d0.asm (local-only reference: `builds/phase28-hardware-readiness/080390d0.asm`; not distributed), `object-evidence.json:update_bundles`. An application update and a selector-2 resource update are different operations. The latter cannot be assumed harmless to this target.

**PROVEN within the peripheral model:** normal selector-0 staging produces the following half-open footprints for the prospective phase27 size. Completion/WIP are modeled; no physical NOR or firmware payload is used. The full payload erase loop executes; representative first/last/vector program blocks and metadata finalization execute. Payload write extent combines those observations with the unchanged sequential 32-byte transfer loop.

| Operation / exact routine | Command / reason | Address and erase/write extent | Target overlap |
|---|---|---|---|
| Updater `$08038EBA`, backend `$08023078`, low erase `$08037494` | WREN `$06`, sector erase `$20/$21`; prepare payload staging | 4-KiB-stepped erase model `0,$6B000)` | None in model |
| `$08038F04` block processing → `$08022FDC` → `$080374D4` | WREN `$06`, page program `$02/$12`; store blocks, vector block last | Padded writes `[0,$6A740)`; no erase requested by each payload write | None |
| `$08039008–$08039040` → backend write with erase flag 1 | Publish 23-byte staging metadata, then reset | Write `[$80000,$80017)`; erase model `[$80000,$81000)` | None in model |
| Bootloader `$08003B2A/$08003B36`, `$08003B9A`, `$08003C24` | Read staging header/payload, validate and install | Known selected calls read external staging; internal flash operations below | No target mutation identified in this selected chain |
| Bootloader identity read `$08005D98`; separate edit `$08005DB4` | Identity at `$81000`; write path exists for identity editing | Not exercised as a normal update operation; complete sector effects not qualified here | UNKNOWN for untraced invocations |
| Application controller setup `$080375FA/$08037614/$0803762E` | Command templates `$F5/$35/$B7` at `$0805BE3C/$0805BE2C/$0805BE4C` | Mode/address configuration, not a selected payload program/erase | Physical-device semantics not independently qualified here |
| First application coefficient initialization `$08035E28 → $08047C6C` | Read `$82000`, 512 bytes, destination `$20005148` | Target is consumed before the post-boot command | This observed operation is a read |

**PROVEN:** backend `$08023078` advances erase addresses by `$1000`; templates `$08037704/$08037714` select erase `$20/$21` and program `$02/$12`. Generic chip erase `$08037648` exists but is selected by the special all-ones range, not the modeled normal payload/metadata operations. No whole-backend read-only claim follows. See [08023078.asm (local-only reference: `builds/phase28-hardware-readiness/08023078.asm`; not distributed) and `storage-effects-result.json:calls`. The physical part's erase geometry is not independently verified in this audit; the footprints above are explicitly those of the instruction/address model.

**PROVEN:** bootloader `$08003B9A` validates product, CRC, size below `$70001`, and a differing `$26`-byte version block. Installer `$08003C24` calls erase at `$08010000`, `$08018000`, `$08020000`, `$08040000`, and `$08080000`. The last call is a **no-op**: `$08006020` rejects offsets `>= $70000` from application base. Effective application-sector erase is `$08010000,$08080000)`; bootloader `[$08000000,$08010000)` is excluded. Installer reads 32-byte staging blocks and programs eight internal-flash words per iteration through `$0800605E → $08007FAC`, then locks and compares CRC through `$08005C3C`. For the prospective image, padded internal writes end at `$0807A740`, below the physical end. Evidence: [08003c24.asm (local-only reference: `builds/phase28-hardware-readiness/08003c24.asm`; not distributed), 0800600e.asm (local-only reference: `builds/phase28-hardware-readiness/0800600e.asm`; not distributed), unchanged bootloader-evidence.asm (local-only reference: `builds/phase27-qspi-read/bootloader-evidence.asm`; not distributed).

**UNKNOWN:** a complete persistent-write census through bootloader constructors, other application tasks, SD/project restoration and first boot has not been established. No SD mutation is identified in the selected transfer/install/diagnostic chains; that is not proof of no SD writes anywhere during deployment. Full authentic application initialization remains blocked by the missing original coefficient data, as documented in [qspi82000-read-diagnostic.md](<qspi82000-read-diagnostic.md>) and [p0282-0386-reclaim-qualification.md](<p0282-0386-reclaim-qualification.md>). No complete first-boot replay is claimed. Installation preservation and first-boot preservation therefore remain **NOT PROVEN**.

**UNKNOWN:** there is no established target-writing boot branch that requires a startup capture hook. None was added. A post-boot capture cannot yet be certified to contain pre-installation bytes.

## Main stack and call context

**PROVEN:** task setup `$0801DDD4`, stack size at `$0801DDF6`, creates **Main**, entry `$0801D4B0`, `$300` words = **3,072 bytes**. Allocator `$0801C91C` converts words to bytes, fills `$A5`, stores stack base at TCB `+$30`, and aligns the initial top. Captured TCB is `$2000835C`, stack allocation `$2000775C,$2000835C)`, initial aligned top `$20008358`. A single early snapshot has 1,352 bytes of non-clean span below that top; it is not worst-case usage. Sources: [0801dd50.asm (local-only reference: `builds/phase28-hardware-readiness/0801dd50.asm`; not distributed), 0801c91c.asm (local-only reference: `builds/phase28-hardware-readiness/0801c91c.asm`; not distributed), `object-evidence.json:captured_Main_watermark`.

**PROVEN:** Main calls input service `$08020E94` at `$0801D5B8`. USB parser `$08035C58` returns a complete SysEx message; `$08020F6E–$08020F82` dispatches callback list `$200008F0` through `$0801C894`. The first callback is `$0801EB31`, the diagnostic hook. This is task context, not USB IRQ context. Its modeled active prefix is **128 bytes**: Main 40, service wrapper 8, service body 56, callback dispatcher 24. Evidence: 0801d4b0.asm (local-only reference: `builds/phase28-hardware-readiness/0801d4b0.asm`; not distributed), 08020e94.asm (local-only reference: `builds/phase28-hardware-readiness/08020e94.asm`; not distributed), 08020f50.asm (local-only reference: `builds/phase28-hardware-readiness/08020f50.asm`; not distributed).

**PROVEN within the successful-path model:** phase27's explicit dispatcher/frame/helper maximum is 616 bytes; executing the admitted stock read/callback helpers increases observed additional depth to **724 bytes**. With the 128-byte prefix, minimum SP is `$20008004`: **852 bytes** below aligned top, **2,212 bytes** above the four-byte low guard. Both boundary canaries survive the request/read/CRC/eight-data-packet/completion-packet model. A pressure control with a 2,372-byte prefix detects the low guard instead of returning a false success. `stack_probe.py` extracts the prior Model class without importing/rerunning its test script or changing phase27 artifacts.

**UNKNOWN:** this is not a complete static worst-case bound. The successful-path stack probe retains phase27's modeled OS wait and router endpoints; full scheduler depth, output-path depth on this same stack, interrupt nesting/FPU frames and later task watermark are unbounded here. The 1,352-byte captured watermark and the 724-byte additional depth must not simply be added as a certified maximum. DMA/cache accessibility and coherency of the actual stack buffer also remain unqualified. H3 does not pass.

## Actual QSPI completion: decisive failure

**PROVEN:** the intended sequence is backend semaphore acquisition → DMA setup → indirect-read command `$EB/$EC` → controller wait/callback → semaphore release → CRC/output. The backend is `$20000378`, controller `$20005550`, MMIO `$A0001000`. Phase27 issues exactly `$82000`, length `$200`, into its own stack buffer. It checks IPSR=0, backend vtable `$0805B1AC`, callback count 1 and callback slot `$08057651`; these checks do not validate the owning task.

**PROVEN:** application QSPI vector `$080101B0` is `$080573E1`. Handler `$080573E0` calls `$08022826`, which sees transfer-complete SR bit 1, acknowledges it, disables that interrupt and sets controller bit 0. The handler then loads global `$20006790` and notifies **Storage holder `$20008D38` / TCB `$20009244`**, mask `$100`, through `$0805756E → $08057664 → $0801BDE8`. The actual holder flag is written before OS notify `$0801CE60`. DMA IRQ `$080573EE` clears DMA flags; it is not the task-wakeup substitute. See 080573e0.asm (local-only reference: `builds/phase28-hardware-readiness/080573e0.asm`; not distributed), 080573ee.asm (local-only reference: `builds/phase28-hardware-readiness/080573ee.asm`; not distributed), 0801bde8.asm (local-only reference: `builds/phase28-hardware-readiness/0801bde8.asm`; not distributed).

**PROVEN:** wait `$08037596` queries current task `$0801CDB8`, obtains its holder via `$0801CD82`, dispatches callback `$08057650`, then waits through `$0801BE1A` on that holder's `$100` flag. In Main this is **`$20007750` / TCB `$2000835C`**. With scheduler active, missing flag enters OS wait `$0801CDC8` **before** controller-complete test `$080375B0`.

**PROVEN:** `full_failure_probe.py` runs the unchanged candidate and backend until the actual wait, preserves its live CPU context, supplies only modeled SR.TCF completion, executes the actual IRQ on a separate modeled interrupt stack, restores Main, and resumes the actual wait. It supplies no coefficient bytes and synthesizes no wait success. Observed result:

| Observable | Exact result |
|---|---|
| Actual backend arguments | `$20000378, $82000, $200080A0, $200` |
| IRQ notification destination | TCB `$20009244`, mask `$100` |
| Main wait destination | Holder `$20007750`, mask `$100` |
| Main flag / Storage flag / controller flag | `$0 / $100 / $1` |
| Stop | `$0801CDC8`, before controller flag test |
| Backend semaphore / emitted replies | `0` (held) / `0` |

**PROVEN:** independent `irq_context_test.py` reproduces the same mismatch; changing only the control case's current task to Storage makes the actual wait return and consume its notification. These tests model the peripheral event and OS notify endpoint, not a complete RTOS schedule. They prove the missing task notification in the admitted state, not that no unrelated future event could ever wake Main. An unrelated notification is not a valid completion mechanism. H4 fails.

## MIDI transmission and scheduler limits

**PROVEN:** [protocol.py](<../builds/phase27-qspi-read/protocol.py>) defines eight 162-byte data frames and one 42-byte completion frame: **1,338 SysEx bytes**, **1,784 USB-MIDI bytes**. This audit executes stock router `$08020C90`, port SysEx send/status/flush `$080359CE/$08035A28/$08035A50`, USB packetizer `$08035A98`, pipe `$08023208/$08023240`, and send `$08023160 → $0801E5C4`. Router storage capacity is `$168` (360 bytes); USB staging capacity is **64 bytes**. Prior pending output causes actual callback `$0801BE78` with delay 1, allowing a scheduler yield. Router copies caller bytes before the request buffer is reused. No added MIDI busy-wait loop is present.

**PROVEN within the model:** `midi_schedule_test.py` feeds existing synthetic phase27 frames through those actual functions, models only HAL USB submission/completion and OS ticks, and uses the actual release callback `$0801E624`.

| Completion model | Ticks | Actual sleep(1) calls | Completed USB transfers | Delivered bytes |
|---|---:|---:|---:|---:|
| One tick per USB completion | 34 | 32 | 33 | 1,784 USB / 1,338 SysEx |
| Three ticks per USB completion | 99 | 94 | 33 | 1,784 USB / 1,338 SysEx |
| Completion delayed 1,000 ticks | Observer stops at 101 | 101 | 0 | 0 |
| Disconnect after first yield | 2 | 1 | 0 | 0; router returns without capture |

**PROVEN within the model:** successful cases reconstruct exactly the existing synthetic 512 bytes, with at most one USB transfer / 64 bytes in flight. The final frame requires normal output service after the handler returns. The 101-tick observer limit is a test watchdog, not a firmware timeout. No new SYX was generated.

**UNKNOWN:** model ticks are not hardware timing measurements. This replay contains no active audio workload or measured task deadlines; it cannot establish uninterrupted audio, total task latency, sustained DIN behavior, or real USB disconnect timing. The router yields CPU, but Main remains occupied until each call returns. USB that remains connected and never completes can hold Main indefinitely. Additional packet pacing or a service-state machine may be needed after the read-context fix; this audit does not implement one. H5 remains unqualified.

## Failure behavior and read-only scope

| Failure | Evidence / consequence | Confidence |
|---|---|---|
| Backend/type/callback/bounds/busy rejection | Existing phase27 tests and ARM `$0807A5B8–$0807A628`: no success packets; host times out | PROVEN within prior model |
| Read initiation never completes / callback missing | No added firmware timeout. Current task mismatch blocks even with controller complete; backend semaphore remains held | PROVEN |
| Output queue full | Router yields through sleep(1), then retries; no finite firmware deadline established | PROVEN behavior; UNKNOWN deadline |
| Host disconnect | Modeled real router exits without a complete capture; receiver requires all nine packets and CRC before final save | PROVEN within model; UNKNOWN hardware timing |
| Duplicate request | Receiver rejects duplicate frames. Device has no persistent deduplication record; after a successful return, another identical request can perform another read. Blocked Main cannot service a second request normally | PROVEN design; STRONG INFERENCE blocked-service consequence |
| Malformed request | Prior 197 checks include malformed fixed fields, lengths, padding, command, context and callback rejection; no arbitrary range accepted | PROVEN within prior model |
| Reboot during read/transmission | No diagnostic persistent record is required on next boot. Partial host capture is not accepted as final evidence. Complete normal boot/recovery after this failure remains untested | PROVEN design; UNKNOWN recovery |

**PROVEN, selected diagnostic chain:** only read commands `$EB/$EC` are selected; there is no call to program `$08022FDC/$080374D4`, erase `$08037494`, SD write, internal-flash programming, option-byte programming, or persistent diagnostic-state storage. DMA writes a RAM buffer; controller/RTOS/semaphore and router/USB state are RAM/MMIO. Actual completion instructions audited here add no array-write command. H6 passes for this fixed diagnostic transaction, including its reproduced blocked state. It does not assert that unrelated B1.3 tasks never write persistent storage, or that installation is read-only. The old read-only-closure.json (local-only reference: `builds/phase27-qspi-read/read-only-closure.json`; not distributed) is preserved as historical phase27 scope, not rewritten to erase its open boundaries.

## Recovery and admission gates

**PROVEN:** the patch plan changes no bootloader bytes, recovery-button code, vectors, option-byte code or staging semantics. Pinned full internal-flash dump SHA-256 is `f3d85d64c9ead9205e5336dff49bb51f21d270ffa29b47c6f6971125d6d848a8`; first 64 KiB SHA-256 is `09fcb71d6583a5714cb96d496ffb423c0d7049754a4cb4413f588d6f54148643`. Boot main `$08002FDE` polls `$08003B66` before application apply/launch; `$08003AB0` checks logical IDs `$12/$08/$09`. Those code properties are independent of a functioning application handler.

**PROVEN as a report, not an independently observed recovery:** reference docs/NOTAS.md:29 (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md:29`; not distributed) reports normal uploader hardware testing on 2026-10-03 and names Scales + Preset + Note. It does not document recovery of this diagnostic after its task/semaphore failure. **STRONG INFERENCE:** unchanged bootloader entry remains architecturally available if its initialization succeeds. **UNKNOWN:** unit-specific recovery, power-interrupted update, and recovery from this candidate. A Main hang may make the application-mediated updater unavailable; unchanged boot code is not an absolute recovery guarantee.

| Gate | Confidence | Decision |
|---|---|---|
| H1 — installation preserves target | UNKNOWN | NOT PROVEN; known staging footprints avoid target, complete install closure remains open |
| H2 — first boot preserves target | UNKNOWN | NOT PROVEN; observed initializer reads target, complete write census unavailable |
| H3 — sufficient bounded stack | UNKNOWN | 852-byte modeled total / 2,212-byte guard margin; full worst case unbounded |
| H4 — valid DMA/IRQ/callback semantics | PROVEN | **Fails: Storage notification versus Main wait** |
| H5 — scheduler-safe output | UNKNOWN | Yield/backpressure proven in model; deadline/audio safety not proven |
| H6 — selected diagnostic strictly read-only | PROVEN | Passes for fixed transaction; not a whole-system or deployment assertion |
| H7 — bootloader/recovery region unchanged | PROVEN | Passes patch-plan/code preservation; actual failure recovery remains UNKNOWN |

**PROVEN:** the all-gates condition for designing an executable hardware capture/install procedure is not met. No hardware procedure or firmware package is admitted. The prior note's conditional live-capture example must not be treated as approval for this candidate. No SYX or firmware image was generated, and no physical action was performed.

**STRONG INFERENCE — smallest next offline experiment:** change only the diagnostic read submission to use the existing queued synchronous wrapper `$08047C6C → $08024130 → $08023F68`, preserving worker `$08024014` read-operation dispatch and the Storage-owned IRQ. Existing initializer use establishes this architecture; 08047c6c.asm (local-only reference: `builds/phase28-hardware-readiness/08047c6c.asm`; not distributed) and the earlier initializer evidence identify it. Then replay the actual Main caller, queued read, Storage worker, IRQ, completion/status handoff, buffer lifetime and semaphore release. Do not retarget the shared IRQ to Main or force notification flags. This change is proposed, not implemented here; its read-only closure, queue contents, failure behavior and stack bound would require fresh tests. Target-preservation closure and output scheduling would still remain separate gates even if that experiment passes.

**PROVEN:** phase27 evidence, phase26 evidence, the range-qualification note, 451 recorded reference inputs and 183 pinned upstream files were hash-checked unchanged by this audit's validation. No Plaits implementation or additional program-memory qualification was attempted.

QSPI82000 HARDWARE READINESS = FAIL

## Phase29 — existing Storage queue correction experiment

2026-10-15 continuation. **PROVEN:** the normal queued read corrects the previous Main/Storage notification mismatch in the emulator. **PROVEN:** the complete requested correction does not pass its failure requirements: a read without transfer-complete remains active with its semaphore held. **UNKNOWN:** physical ownership of a persistent 512-byte diagnostic buffer and a fully installed Main service attachment. Hardware readiness remains FAIL. H1/H2 have not been changed by this experiment.

The original validated phase28 report is preserved byte-for-byte in phase28-report-before.md (local-only reference: `builds/phase29-storage-wrapper/phase28-report-before.md`; not distributed). Earlier sections describe that rejected prototype; the measurements below apply only to the new emulator experiment.

### Exact stock wrapper, descriptor and worker

**PROVEN:** normal non-Storage callers use `$08047C6C → wrapper vtable+$C → $08024130`. The wrapper builds an operation-1 request, submits it through `$08023F68`, and calls `$08023FD6`, which yields until wrapper sync bit 0 clears. Calling that synchronous public read would keep the caller's frame alive, but would not implement the requested submit-and-return flow. The tested asynchronous version therefore uses **the same internal stock submission routine `$08023F68`**, supplying its supported completion callback instead of calling the synchronous wait. No backend, IRQ or task-notification code is replaced.

**PROVEN:** wrapper global `$20006968` points to `$2000AC94`, vtable `$0805B1D8`. Exact fields from objects.json (local-only reference: `builds/phase29-storage-wrapper/objects.json`; not distributed):

| Wrapper offset | Value / role |
|---|---|
| `+$00` | Vtable `$0805B1D8` |
| `+$04` | NOR backend `$20000378` |
| `+$08` | Queue descriptor `$2000ACB0` |
| `+$0C` byte | Pending-service count, saturated against byte `+$0D` (captured limit 1); not the queue's byte count |
| `+$10` word | Synchronous-caller wait bits; not needed by the asynchronous diagnostic |
| `+$14` | Storage notification holder `$20008D38` |
| `+$18` byte | Last backend return status; captured by callback before subsequent work can overwrite it |

**PROVEN:** queue `$2000ACB0` has buffer pointer `+$00 = $2000ACBC`, size `+$04:u16 = 73`, producer index `+$06:u16`, consumer index `+$08:u16`, element size `+$0A:u16 = 24`. Its 72 usable bytes hold three descriptors. `$08036708` verifies descriptor size and free capacity, then copies **all 24 request bytes** using `$08022190`; `$08036732` copies an element out using `$080221FC`. No pointer to the submitting function's local request is retained by the queue. The copied descriptor is:

| Offset / type | Fixed diagnostic value |
|---|---|
| `+$00:u16` | Operation **1**, read |
| `+$02:u16` | Flags 0 |
| `+$04:u32` | Source offset **`$82000`** |
| `+$08:pointer` | Payload destination; emulator address `$20060080`, **not a qualified physical buffer** |
| `+$0C:u32` | Length **512** |
| `+$10:callback` | Emulator callback `$0807B201` |
| `+$14:userdata` | Emulator diagnostic record `$20060010` |

Evidence: 08023e80.asm (local-only reference: `builds/phase29-storage-wrapper/08023e80.asm`; not distributed) at `$08023F68/$08024014/$08024130`, 080366e0.asm (local-only reference: `builds/phase29-storage-wrapper/080366e0.asm`; not distributed), 0802210a.asm (local-only reference: `builds/phase29-storage-wrapper/0802210a.asm`; not distributed). These excerpts come directly from verified **B1.3** spans.

**PROVEN:** Storage task entry `$0805767C` registers its callbacks, then loops at `$0805769C`: wait for event bit 1, drain SD wrapper work, then NOR wrapper work via `$08024014`. The captured callbacks were already registered, so replay starts at this unchanged event-loop boundary with the exact registers established by its prologue; it does not register duplicate callbacks. `$08024014` consumes the pending byte, dequeues through `$0803675C/$08036732`, dispatches operation 1 at `$0802408A–$08024096`, and invokes backend vtable `+$C → $08022F94 → $08037430`.

**PROVEN:** after backend return, worker `$080240C4` stores status at wrapper `+$18`; `$080240D0–$080240D8` calls request `+$10` with **R0 = worker's copied request, R1 = userdata**, in **Storage task context**. The callback pointer to the worker's stack request is valid only during that call; the tested callback retains no such pointer. It copies status into the persistent diagnostic record, executes DMB, and marks the record ready. No MIDI is emitted from Storage or IRQ. See 0805767c.asm (local-only reference: `builds/phase29-storage-wrapper/0805767c.asm`; not distributed) and 0807b200-emulator.asm (local-only reference: `builds/phase29-storage-wrapper/0807b200-emulator.asm`; not distributed).

### Constructed model and explicit allocation limit

**PROVEN:** [shims.py](<../builds/phase29-storage-wrapper/shims.py>) constructs emulator-only Thumb submit/callback/one-packet service routines of **144 / 24 / 264 bytes**. It reuses the prior exact-request ARM validator and independent ARM nibble/CRC helpers; only the command call is redirected **in emulator memory**. No application image, binary fragment file, update SYX or deployment patch plan is generated. These are the smallest decomposition tested here, not a proof of globally minimal code size.

**PROVEN:** the validator still requires exactly `$82000 / 512`, correct protocol/version/padding, normal task context and token range. The new submit routine accepts only USB-main input port 0 in this focused model; DIN admission is not claimed. It refuses a second request while phase is pending, ready or draining, and preflights 24 bytes of queue capacity before invoking the stock submission routine. This avoids deliberately entering `$08023F80–$08023F96`'s full-queue synchronous fallback in the admitted model. The preflight is not a newly established lock against arbitrary concurrent producers.

**PROVEN:** the captured stock bump allocator at `$0801CFA4 → $0801D7D8` has limit `[$20002B44]=$20044E58`, cursor `[$20002B48]=$20044D68`: **240 bytes remain**. Actual 512-byte and 1,024-byte allocation attempts both reach **BKPT `$0801D7F4`**, without returning an allocation or changing the cursor. Thus this allocator cannot supply even the raw payload at the captured state. This does not prove that every other possible memory strategy is impossible. It does reject treating the remaining heap as a proven 512-byte allocation. Evidence: [objects.py](<../builds/phase29-storage-wrapper/objects.py>), `objects.json:allocation_attempts`, 0801cfa4.asm (local-only reference: `builds/phase29-storage-wrapper/0801cfa4.asm`; not distributed), 0801d7d8.asm (local-only reference: `builds/phase29-storage-wrapper/0801d7d8.asm`; not distributed).

**UNKNOWN:** no persistent hardware buffer is admitted. To test task semantics without borrowing live buffers, the model deliberately uses the fixture's **nonphysical test mapping outside STM32 SRAM**:

| Test-only address | Size | Lifetime / purpose |
|---|---:|---|
| `$20060010` | 32 | Record: `+0` phase, `+4` captured status, `+8` token, `+$C` port, `+$10` next packet index |
| `$20060040` | 24 | Submission descriptor; copied by stock queue, retained for comparisons |
| `$20060080` | 512 | DMA-model payload, retained through callback, packetization and drain |
| `$20060290` | 232 | Packet staging, retained until stock router has copied it |
| `$20060388` | 8 | Packet pointer/length descriptor |

**PROVEN within the model:** each new allocation has eight-byte leading/trailing canaries; both task stacks have boundary guards. Guards are checked after task transitions and service calls. CPU writes into the payload are rejected: only the opaque DMA model supplies synthetic bytes after actual read-command setup. None of the buffer's lifetime depends on a returning submitter's stack. Request copies on the queue/worker stack are managed by the actual stock instructions. No physical ownership, DMA reachability or cache coherency is inferred from these emulator addresses.

### Main handoff and MIDI service

**PROVEN:** the chosen handoff is **B — mark completion, let Main service the result**. Storage callback captures the per-request status and marks phase 2; Main alone packetizes. Phases are 0 idle, 1 pending, 2 ready/emitting, 3 draining. A successful final router call does not immediately make the record reusable: Main waits for pending output to drain before returning to phase 0. Duplicate tests before dequeue, during DMA and after completion show no request/token/payload replacement.

**PROVEN by stock code:** Main `$0801D5AC` already polls periodic dispatcher `$0801E4BE` with object `$20000354`. Dispatcher reads timer state and calls each active callback at `$0801E51E`. 0801d5a4.asm (local-only reference: `builds/phase29-storage-wrapper/0801d5a4.asm`; not distributed), 0801e4ee.asm (local-only reference: `builds/phase29-storage-wrapper/0801e4ee.asm`; not distributed) and 0801e52c.asm (local-only reference: `builds/phase29-storage-wrapper/0801e52c.asm`; not distributed) identify the existing scheduling mechanism and timer-slot setter `$0801E538`.

**STRONG INFERENCE:** this Main service boundary is appropriate for a paced diagnostic reply callback. **UNKNOWN:** a free periodic slot, its ownership, registration lifetime, and full real scheduling integration have not been qualified. The current replay explicitly models that callback opportunity; it does not overwrite an existing timer slot or silently claim an installed service.

**PROVEN within the model:** Main flushes the actual USB port service, defers while its previous packet or USB IN transfer is pending, and calls the actual one-packet ARM encoder/router only when clear. There is at most one packet submitted per modeled opportunity, one 64-byte USB transfer in flight, and no call to the router's sleep(1) backpressure path. The actual `$08020C90`, `$080359CE/$08035A50/$08035A98`, USB pipe, HAL submission boundary and `$0801E624` completion-release instructions execute. Eight 162-byte packets and one 42-byte completion produce **1,338 SysEx / 1,784 USB-MIDI bytes in 33 USB transfers**. Independent Python packets, ARM packets, actual USB packet reconstruction, packet CRCs and whole-512-byte CRC agree exactly.

**PROVEN within the model:** normal completion with two-tick USB latency takes **76 modeled ticks**. The delayed/backpressure/two-request case uses five-tick USB latency and **358 total modeled ticks**, including eight delayed-DMA opportunities and two complete captures; 320 output opportunities defer, with zero busy-wait/sleep calls in Main. A counter records other runnable-task opportunities at each tick. **UNKNOWN:** those ticks are not measured hardware latency, and the counter is not execution of stock audio or a complete RTOS workload. Uninterrupted audio and real deadlines remain unproven. The fixture's USB-only preflight is not a general router-arbitration guarantee with unrelated producers.

### Separate stack measurements

**PROVEN:** Main has 768 words / **3,072 bytes**, allocation `$2000775C,$2000835C)`, aligned top `$20008358`. Storage setup `$0801DE36` selects `$140` words / **1,280 bytes**; captured Storage TCB `$20009244` stores stack base `$20008D44` at `+$30`, giving allocation `[$20008D44,$20009244)` and aligned top `$20009240`. Its entry is `$0805767C`, holder `$20008D38`. See [0801de04.asm (local-only reference: `builds/phase29-storage-wrapper/0801de04.asm`; not distributed) and `objects.json:Storage_TCB`.

| Path | Modeled prefix | Additional observed SP movement | Total from aligned top | Minimum SP | Bytes to low guard |
|---|---:|---:|---:|---|---:|
| Main validation/submission | 128 | 132 | **260** | `$20008254` | **2,804** |
| Main one-packet service | 56 | 80 | **136** | `$200082D0` | **2,928** |
| Main USB port flush | 40 | 72 | **112** | `$200082E8` | **2,952** |
| Storage event loop/dequeue/backend/wait/completion | 24 | 180 | **204** | `$20009174` | **1,068** |

**PROVEN within the model:** Main's 128-byte input prefix comes from the prior actual handler chain; Main's 56-byte service prefix models Main's 40-byte frame plus the periodic dispatcher's 16-byte frame. Storage's 24-byte prefix is its actual task prologue. No submitting function holds the 512-byte payload on stack. Guards survive; returning emulator entry calls preserve callee-saved registers and SP, and actual Storage worker returns at `$080576B4` preserve the task's callee-saved registers. Per-case counts and minimum SP are recorded in replay-result.json (local-only reference: `builds/phase29-storage-wrapper/replay-result.json`; not distributed).

**UNKNOWN:** these are bounded instruction-model depths, not complete worst-case stack proofs. OS notify/block endpoints, real exception/FPU nesting, installed service behavior and DMA/cache suitability are not qualified. The previous 852-byte defective-path estimate is not reused. H3 remains UNKNOWN even though both configured stack bounds are now identified.

### Ownership transition: old versus queued

**PROVEN:** the old phase28 failure remains unchanged: Main enters backend, semaphore becomes 0; IRQ sets Storage `$100`; Main flag remains 0; Main waits at `$0801CDC8`, no reply. The new normal-path transition is:

| Actual replay stage | Backend semaphore | Main flags | Storage flags | Diagnostic / queue state |
|---|---:|---|---|---|
| Main's asynchronous submit returns | 1 | 0 | `$1` | Phase 1; 24 queued bytes; pending byte 1 |
| Storage consumes event, dequeues, starts DMA and blocks | 0 | 0 | 0 | Phase 1; queue empty; worker owns in-flight request |
| Unchanged QSPI IRQ sees TCF | 0 | 0 | `$100` | Controller bit 0 set; request still pending |
| Storage's actual wait resumes; backend returns | 1 | 0 | 0 | Callback captures status 0 and sets phase 2 |
| Worker returns to next event wait | 1 | 0 | 0 | No queued request, pending byte 0; sync word 0 |
| Main sends/drains nine packets | 1 | 0 | 0 | Phase 3 until drain, then phase 0 |

**PROVEN:** IRQ `$080573E0`, global `$20006790`, Storage holder/TCB and notification mask `$100` are unchanged. Main never calls the backend or its wait in this model. Backend-entry assertions require current context Storage and exact arguments `[$20000378,$82000,$20060080,512]`. The original holder flag stores and consumption execute; OS endpoint modeling does not synthesize successful read return or set task-completion flags. DMA payload delivery and peripheral status are explicit external models.

### Failure and regression results

**PROVEN:** [replay.py](<../builds/phase29-storage-wrapper/replay.py>) completes **8 scenario groups with 172 explicit gate assertions**, in addition to per-instruction ownership checks, canary checks and register assertions. Passing a failure-reproduction assertion does not mean that the tested architecture passes admission.

| Required case | Observed result | Confidence |
|---|---|---|
| Normal completion | One read, one callback, nine exact frames, semaphore 1, queue/pending state cleared | PROVEN within model |
| Delayed IRQ | Eight intervening Main/worker opportunities; no premature packet or buffer reuse; eventual actual IRQ completes | PROVEN within model |
| Switches during DMA | Main can run while Storage blocks; Main flags untouched; actual worker context restored | PROVEN within model |
| Duplicate request pending | Refused before dequeue, during DMA and after completion; descriptor/token/payload preserved | PROVEN within model |
| Backend busy | Backend returns 2 without command; callback captures 2; Main clears request without packets. Existing owner's semaphore remains 0; it must not be released by a failed acquisition | PROVEN within model |
| QSPI completion error | Injected **TEF-only SR=1**, without TCF: unchanged IRQ notifies Storage `$100`, but controller completion bit remains 0; Storage consumes notification and blocks again, semaphore 0, phase 1, no callback | PROVEN within injected model |
| Temporarily full reply path | Main defers, retries on later service opportunities, then transmits exact output; no sleep/busy-wait | PROVEN within model |
| Host disappears after request | Phase 1 buffer retained through DMA; after actual completion, Main cancels unsent reply; semaphore 1 and no request left queued | PROVEN within model |
| Second request after success | Fresh token, second read/callback and second independent exact reconstruction, no stale state | PROVEN within model |
| Missing IRQ observation | Eight further opportunities do not complete read; no timeout is added, semaphore/request stay active | PROVEN within model |
| Fixed-request negative coverage | 149 malformed/command mutations plus non-USB input rejection; no request enqueued | PROVEN within model |

**PROVEN by code and injected execution:** `$08022826` checks TCF and status-match flags; the tested TEF-only path does not set the completion bit required by `$080375B0–$080375BC`. The low read `$08037430` has no tested error-status return or finite timeout; backend `$08022F94` only releases its semaphore after that call returns. The error-injected IRQ invocation is a controlled model, not a claim that TEF alone generates an IRQ under every physical register configuration. If no IRQ is delivered and no TCF follows, the same read remains blocked. No whole-device deadlock is claimed: Main remains runnable, but Storage's in-flight request and semaphore are stuck. This violates the requested no-stale-request/no-held-semaphore failure gate. No IRQ retarget, forced flag, synthetic completion or new driver was added to conceal it.

**STRONG INFERENCE — ordering risk:** actual submit order is queue copy → notify Storage at `$08023F9C` → pending-byte increment `$08023FA0–$08023FC8`. A forced scheduler switch immediately after notification lets the unchanged worker observe pending byte 0, leave the queued descriptor untouched, consume the event and return to waiting. Main then increments pending to 1 without a second event. Replay ends with 24 queued bytes, phase 1, semaphore still 1 and Storage flags 0. **UNKNOWN:** whether real task priority/RTOS scheduling/critical-section constraints permit this exact interleaving. This is recorded as a conditional scheduling risk, not declared a proven hardware race. The model does not qualify arbitrary preemption simply by testing switches during DMA.

### Read-only closure and gates

**PROVEN within the fixed-request fixture:** closure.json (local-only reference: `builds/phase29-storage-wrapper/closure.json`; not distributed) records 92 observed call/tail edges and 29 B1.3 source excerpts. Literal operation 1, fixed offset/length and queue-copy equality constrain TBB `$08024070` to its read branch. The callback target is the bounded emulator callback; it only stores RAM status/phase. Main's service calls CRC/encoding and stock MIDI output. The SD wrapper is visited by the unchanged Storage loop but its queue is empty; no SD operation is attributed to this diagnostic. Generic worker write/erase/other-operation branches are excluded by the operation constraint, not by their names. The actual emulator aborts on non-read worker dispatch, NOR program/erase entry, CPU flash write, CPU payload overwrite or QSPI command other than read. Observed QSPI command is **`$EC`**, indirect read, across the new scenarios; zero program/erase, SD write or internal-flash write is reached. No new claim about unrelated background jobs is made.

**UNKNOWN:** a future deployable version would still need runtime identity/ownership guards, a qualified physical buffer, safe service registration and scheduling proof. Exercised read-only closure does not certify deployment or the entire system.

| Gate | Confidence | Phase29 decision |
|---|---|---|
| H3 — task stack suitability | UNKNOWN | Main/Storage bounds and modeled margins established; full worst cases and buffer suitability unqualified |
| H4 — DMA/IRQ/callback correctness | PROVEN for normal correction; UNKNOWN for real schedule coverage | Original task mismatch corrected in normal replay; **required error/no-completion behavior fails**; submission preemption constraint unqualified |
| H5 — MIDI scheduler/output behavior | UNKNOWN | Paced actual output passes bounded backpressure model; timer-slot ownership, real deadlines/audio workload unqualified |
| H6 — selected diagnostic read-only | PROVEN within fixed-request fixture | No request-reachable persistent write in constrained model; physical deployment not admitted |
| H1 — installation target preservation | UNKNOWN | **NOT PROVEN**, unchanged from phase28 |
| H2 — first-boot target preservation | UNKNOWN | **NOT PROVEN**, unchanged from phase28 |

**PROVEN:** this experiment did not modify the old phase27 fragment/tests, IRQ, bootloader, DSP, reference repository or pinned sources; did not generate firmware/SYX; and did not access hardware. The phase29 validation manifest records preserved inputs and the authorized report append. The correction is rejected under the requested complete failure criteria despite proving the normal queued architecture. No capture/install procedure is admitted, and no Plaits port is started.

QSPI STORAGE-WRAPPER CORRECTION = FAIL

## Phase30 — eight physical-buffer chunks

2026-10-16. **PROVEN within offline execution:** eight stock queued 64-byte reads, exact synthetic reconstruction, a physical stock-buffer slice, request restoration and successful retries after recoverable busy/disconnect cases. **UNKNOWN:** a stock-compatible bounded Storage error/timeout unwind. TEF-only and missing-completion injections at chunks 0, 4 and 7 still retain transaction ownership. Per the requested timeout-ownership rule, the architecture remains **UNQUALIFIED**. H1/H2 are unchanged and were not investigated in this phase.

The validated phase29 report is preserved in phase29-report-before.md (local-only reference: `builds/phase30-chunked-storage/phase29-report-before.md`; not distributed). New evidence is [replay.py](<../builds/phase30-chunked-storage/replay.py>), replay-result.json (local-only reference: `builds/phase30-chunked-storage/replay-result.json`; not distributed), [stream.py](<../builds/phase30-chunked-storage/stream.py>), ownership-and-error-audit.json (local-only reference: `builds/phase30-chunked-storage/ownership-and-error-audit.json`; not distributed) and the phase30 validation manifest. No firmware, update SYX, hardware command, bootloader/DSP edit or reference-source edit was performed.

### Physical memory and the corrected heap accounting

**PROVEN:** phase29's 240-byte allocator margin describes the captured stock-RAM state **before B1.3's lazy retained-feature reservation**. Verified B1.3 manifest `report.sc17.sc14_state` / matching report entries identify `$20044D6C`; actual native routine `$0805DBDC:c_gst` reserves `$20044D6C,$20044E58)`, **236 bytes**, and leaves cursor `$20044D68`, only **4 bytes** below the new limit. Calling that real routine establishes this state; no heap-limit value is fabricated by the model.

**PROVEN:** a real 64-byte allocation **after** reservation traps at `$0801D7F4`. Allocating 64 bytes **before** reservation returns `$20044D68`, advances cursor to `$20044DA8`, and then makes actual `c_gst` return 0: its retained-feature guard disables the feature. It avoids overlap but is not an acceptable free-heap claim. The phase30 prototype makes **zero new heap allocations**. Source: [0805dbdc.asm (local-only reference: `builds/phase30-chunked-storage/0805dbdc.asm`; not distributed), [audit.py](<../builds/phase30-chunked-storage/audit.py>), and reference build_sc14.py:arm_code (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/build_sc14.py:75`; not distributed), whose state constant is relocated by later builders.

**PROVEN:** a usable physical storage candidate exists in the stock input parser, under a specific lifetime rule:

| Item | Exact address / size / owner |
|---|---|
| Parser | `$20009FF4`, reached through `[$200068B0+$C]`'s first parser pointer |
| Current SysEx descriptor | `parser+$24 → $2000A048`, count at `+0:u16`, data pointer at `+4` |
| Existing allocation | **`$2000A050`, 360 bytes**, owned by the stock Main SysEx parser |
| Borrowed raw slice | **`$2000A070–$2000A0AF`, 64 bytes**, offset 32, aligned to 16 bytes |
| Raw canaries | Four bytes each at `$2000A06C` and `$2000A0B0`, inside the serialized request allocation |
| New packet/state frame | **`$200081E8`, 188 bytes**, allocated by the live Main command prologue; packet starts `$200081F8` |

**PROVEN:** constructor `$08035BC8` allocates the parser's SysEx storage with capacity `$168=360`, records it at parser `+$10/+$14`, and selects its descriptor through `+$24`. Parser `$08035C58` has direct stock callers `$08020F62` (Main USB service) and `$08020FFC` (Main DIN service). The tests feed every request byte through this **actual parser**, require its return value 2, and verify the captured descriptor points to the exact request bytes and length. No fabricated input arena is used. Source: 08035b80.asm (local-only reference: `builds/phase30-chunked-storage/08035b80.asm`; not distributed), `ownership-and-error-audit.json:references`, and `Model.start`.

**PROVEN within the tested serialization:** Main stays inside its command callback while stock queue waits yield. Its parser cannot consume another message from that same Main loop until the callback returns. Diagnostic DMA writes only the 64-byte slice; Main reads it only after Storage completion. The prototype retains the token in its packet header, then reconstructs **all original 232 request bytes** before every returning exit, including busy rejection and disconnect. This prevents subsequent stock callbacks from seeing coefficient bytes as a new command. The unused last 128 bytes of the 360-byte allocation are checked unchanged. Raw/frame/stack canaries and the retained 236-byte B1.3 feature state are checked throughout replay.

**STRONG INFERENCE:** this is a physically plausible serialized borrow, supported by the actual parser, ownership path and replay. The addresses are DTCM, not guessed unused SRAM. STM32F74/75's documented AHBS path permits DMA access to DTCM; this differs from other STM32 families. [ST RM0385, section 2.1.1](https://www.st.com/resource/en/reference_manual/rm0385-stm32f75xxx-and-stm32f74xxx-advanced-armbased-32bit-mcus-stmicroelectronics.pdf). **UNKNOWN:** a complete concurrent USB/DIN/interrupt workload and real DMA/cache behavior were not executed on hardware. Buffer admission is limited to this captured object layout and non-returning callback discipline.

**PROVEN — deliberate architecture change:** this variant **yields without returning Main's command callback**. It does not preserve phase29's immediate-return asynchronous Main service. The borrowed parser buffer and command frame remain owned across every scheduler switch. Neither is released on a stuck read. An immediately returning asynchronous version still has no qualified persistent physical buffer here. Main input/UI service availability during the transaction is therefore a remaining scheduling limitation, not a solved H5 gate.

### Eight-read sequence and host integrity

**PROVEN:** `stream.py` keeps the native fixed-request validator. No host address or length is decoded into the backend arguments. Internal index 0–7 generates only:

| Chunk | Inclusive QSPI source |
|---:|---|
| 0 | `$82000–$8203F` |
| 1 | `$82040–$8207F` |
| 2 | `$82080–$820BF` |
| 3 | `$820C0–$820FF` |
| 4 | `$82100–$8213F` |
| 5 | `$82140–$8217F` |
| 6 | `$82180–$821BF` |
| 7 | `$821C0–$821FF` |

**PROVEN:** every chunk executes `$08047C6C → $08024130 → $08023F68`; original synchronous wait `$08023FD6` yields until the Storage worker clears wrapper `+$10` bit 0. Request operation is 1, source is the current fixed address, destination `$2000A070`, length 64, callback/userdata null. The stock wrapper's 24-byte request is copied into the existing queue and then into the worker frame; the submitting stack request does not escape by pointer. Storage `$0805767C/$08024014` owns backend `$08022F94 → $08037430`, DMA and the original IRQ notification. Main never acquires its semaphore or waits on the QSPI notification itself.

**PROVEN:** the normal loop is read → actual Storage completion/release → update streaming CRC → encode one packet → stock output-copy/send → yield until port and USB transfer drain → reuse the raw slice. Packet encoding reads exactly the just-completed 64 bytes. The running CRC is carried between chunks; the device never accumulates a 512-byte payload. The existing independent Python oracle and ARM encoders agree.

**PROVEN:** the router copies packet bytes at `$08020D46–$08020D5A` through `$0801AA14` into its existing 360-byte storage before caller packet reuse. The prototype additionally waits for complete output drain before the next read, checking both port descriptor indices and the actual USB IN byte semaphore at stream `+$1C`; an empty port descriptor alone is insufficient. Stock port flush `$08035A50` and real release callback `$0801E624` execute. No busy-wait or forced USB acknowledgement is introduced: drain waits call stock scheduler-yield `$0801BE60`. Successful completion sends eight 162-byte data packets and one 42-byte completion packet: **1,338 SysEx bytes / 1,784 USB-MIDI bytes / 33 USB transfers**.

**PROVEN:** the existing strict protocol.py:Receiver (local-only reference: `builds/phase27-qspi-read/protocol.py:39`; not distributed) still checks transaction token, chunk index, absolute address, raw length, packet CRC, completeness and whole-data CRC. New negative tests cover missing, duplicate, reordered, wrong-address, wrong-total, wrong-length, wrong-token, packet-CRC and whole-data-CRC failures. Wrong-address/length and whole-CRC tests use valid packet CRCs where appropriate, so they test more than incidental checksum corruption. Native request mutations for address, length and write-command selection enqueue no read; this focused prototype also refuses non-USB input.

**PROVEN within the synthetic test:** the normal host result is exactly the concatenation of eight separate 64-byte peripheral-model deliveries. `replay-result.json` records 512-byte SHA-256 and CRC/reconstruction success, with intended filename **`qspi_00082000_000821ff.bin`**. No capture file is written and no authentic QSPI data is supplied; this synthetic result must not be presented as device evidence.

### TEF, timeout ownership and the remaining unwind gap

**PROVEN:** QSPI `SR.TEF` is **bit 0**, its interrupt enable is `CR.TEIE`, and its clear bit is `FCR.CTEF`. QSPI TCF is bit 1; DMA stream transfer errors are separate signals. [ST's STM32F745 header](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-f7/master/Include/stm32f745xx.h) defines those symbols. This audit does not claim to reproduce every silicon condition that can raise TEF.

**PROVEN by actual stock instructions:** `$08022826` handles QSPI status bits 1 and 3, sets software completion bits, and acknowledges FCR bits 1 and 3. It has no TEF branch. QSPI IRQ `$080573E0` still notifies **Storage holder `$20008D38`, TCB `$20009244`, mask `$100`**. DMA IRQ `$080573EE` clears selected DMA status flags and calls `$08022888`, which returns immediately; it supplies no read error-unwind status. The selected read command enables TCIE, not TEIE. Therefore a forced TEF-only IRQ is explicitly an injection; it is not asserted to arise naturally with TEIE disabled. With no IRQ/TCF, the missing-completion path blocks as well.

**PROVEN:** the fixture executes original controller initializer `$080226A2` and DMA initializer `$0801BEB0` before the experiment. It does not assume zeroed peripherals are already usable. Recorded initial QSPI CR/DCR are `$01400F11/$00180000`; DMA CR/PAR are `$06010454/$A0001020`. Read setup programs actual AR, DLR=63, DMA destination and NDTR=64. Peripheral modeling explicitly supplies DMA bytes on normal completion, decrements NDTR to 0, auto-clears normal-mode DMA EN, and implements FCR write-one-to-clear effects. These hardware effects are modeled, not measured. The repeated-read test would be inaccurate if a completed DMA were left enabled in the model.

**PROVEN:** completion callback `$08057650 → $0801BE1A` calls RTOS wait `$0801CDC8` with **R3=`$FFFFFFFF`**, an indefinite wait. Low read `$08037596` loops until software controller bit 0 is set. Backend release `$08022FD4 → $0801BA12` is after that wait. Main's synchronous wrapper independently yields until its sync bit clears. Neither path contains the required finite error-unwind return. Register/call evidence is in 0801be1a.asm (local-only reference: `builds/phase30-chunked-storage/0801be1a.asm`; not distributed), 08022746.asm (local-only reference: `builds/phase30-chunked-storage/08022746.asm`; not distributed), 08022826.asm (local-only reference: `builds/phase30-chunked-storage/08022826.asm`; not distributed) and `ownership-and-error-audit.json:timeout`.

**PROVEN:** related stock interfaces do not establish cancellation: backend slot `+$1C → $080230F8` spins until the semaphore is free; `$080375C0` performs status polling with another indefinite event wait; backend initialization `$08022F1E` resets/configures and then performs command waits. No bounded abort/error-unwind entry was identified in the inspected controller/backend vtable, worker, callback or same RTOS-wait path. This is a scoped negative finding, not a proof that no other firmware routine exists. The QSPI LPTR timeout documented by ST is a memory-mapped low-power timeout, not a qualified watchdog for this indirect read. [RM0385, section 14.5.13](https://www.st.com/resource/en/reference_manual/dm00124865-stm32f7-series-advanced-armbased-32bit-mcus-stmicroelectronics.pdf).

**UNKNOWN:** a safe bounded unwind has not been demonstrated. Its owner must be Storage or a proven stock Storage cancellation service. It must quiesce DMA/peripheral access, preserve correct callback status, release only an acquired semaphore, and clear the request before returning its buffer. Main does none of these forcibly. No abort command, fabricated TCF, cross-task semaphore release, peripheral reset or new driver is implemented. A test watchdog stopping observation is not firmware recovery.

### Required scenarios and state after failure

**PROVEN:** **12 scenario groups and 37 explicit assertions** complete, with additional per-instruction address/ownership checks and guard assertions. Passing an assertion that reproduces a stuck request is not passing the recovery gate.

| Scenario | Result after observation | Confidence |
|---|---|---|
| Eight normal reads | Eight fixed sources, same physical destination; nine exact frames; semaphore 1, queue/pending/sync 0, callback returned, buffer reusable | PROVEN in model |
| TEF on chunk 0 / 4 / 7 | Respectively 0 / 4 / 7 data frames; semaphore **0**, queue/pending 0 but sync **1**, active worker read retained, no final completion, buffer not reusable | PROVEN in injected model |
| Missing completion on chunk 0 / 4 / 7 | Same ownership retention and frame counts; no actual recovery occurs | PROVEN in model |
| Backend busy before submit | Status 2 returns; no read command or packet; queue/sync cleared and borrowed input restored. Semaphore stays 0, belonging to the pre-existing owner | PROVEN in model |
| Request after busy | Succeeds only after the explicitly modeled **original Storage owner** releases through actual `$0801BA12`; diagnostic Main never releases it | PROVEN under stated owner model |
| Duplicate host command while active | Normal Main dispatcher cannot re-enter its live callback; no second read is started concurrently. Host input is modeled as deferred, not written over the active parser buffer | PROVEN non-reentrancy; full device ingress/overflow behavior UNKNOWN |
| MIDI backpressure between chunks | Five-tick USB completion model yields and eventually reconstructs exactly; no buffer reuse during transmission | PROVEN in model |
| Host disappears after chunk 3 | Four completed reads/frames; returns after no DMA remains; semaphore 1, queue/sync cleared, request restored | PROVEN in model |
| Request after reconnect | Fresh-token eight-chunk capture succeeds, no reboot | PROVEN in model |
| Request after TEF/missing completion | Cannot be admitted while Main and Storage retain the first request; no unsafe retry is executed | UNKNOWN safe recovery; requirement not met |

**PROVEN within failure models:** TEF final state is `SR=$1`, software completion 0, DMA NDTR=64 and EN remains set. Missing completion uses `SR=$20` (BUSY), likewise no software completion. After the injected notification is consumed, Storage flags are 0 and it waits again for `$100`; Main flags remain 0. The worker has already dequeued the descriptor, so queue emptiness is **not** request completion. All six failed chunks retain the same physical raw slice and live Main frame, without restoration or reuse. The extra 16 observer ticks prove no recovery in that window; the indefinite native wait explains why no finite bound is admitted.

**PROVEN in the forced interleaving test:** the synchronous wrapper also handles phase29's modeled notify-before-pending-increment risk: after Main resumes and increments pending, `$08023FD6` emits a **second** Storage event at `$08023FF8`. The early worker can return to waiting, then process the later signal and complete all eight chunks. This qualifies that specific interleaving under the new synchronous path; it is not a complete RTOS scheduling proof.

### Stack, RAM, read-only closure and gates

**PROVEN in the final model:** Main allocation remains `[$2000775C,$2000835C)`, 3,072 bytes; Storage remains `[$20008D44,$20009244)`, 1,280 bytes. Worst observed Main SP is **`$2000814C`**, **524 bytes** below aligned top, **2,540 bytes** to its low guard. Storage minimum is **`$20009174`**, **204 bytes** used and **1,068 bytes** to its guard. IRQ prologue uses 16 modeled bytes on the physical initial-MSP fixture; exception entry/FPU nesting is not included. No nonphysical SRAM mapping exists, and code/data accesses outside physical SRAM are rejected. [environment.py](<../builds/phase30-chunked-storage/environment.py>) constructs the fixture directly and never invokes the older emulator's artificial-stack `E.call` or DSP Session initialization.

| Memory item | Physical RAM cost / lifetime |
|---|---|
| Payload | 64 bytes borrowed inside existing 360-byte parser allocation; **0 new heap bytes** |
| Stock request | 24 bytes in the existing read-wrapper frame, then existing queue/worker copies |
| New command frame | **188 bytes**: packet capacity 164, packet descriptor 8, streaming CRC 4, local guards 8, padding 4 |
| Command register save | 20 stack bytes |
| Reused validator register save | 32 stack bytes |
| New persistent global state | **0 bytes**; index/token/status are in saved registers, packet or live frame |

**PROVEN:** the new command/validator occupy **240 stack bytes** in total, while observed complete Main depth is 524 including the 128-byte input prefix and stock queue/read helpers. The borrowed 64 bytes and two raw guards are already inside the parser's allocated request storage. No 512-byte allocation, guessed RAM or expired caller-stack payload appears in the prototype. **UNKNOWN:** full scheduler/interrupt stack maxima, actual DMA timing and ordinary Main/UI responsiveness while held in its command; H3/H5 therefore do not pass hardware admission.

**PROVEN within the constrained path:** every descriptor has operation 1 and length 64; internal index bounds restrict addresses to `$82000–$821FF`. Actual exercised QSPI command is `$EC` eight times in a normal capture. The emulator rejects NOR program/erase entry, non-read worker dispatch and CPU internal-flash write. Stock SD wrapper visits see no diagnostic SD request. RAM canaries/request restoration and MIDI output are not NOR writes. The selected graph contains 84 observed call/tail edges; immutable template/prototype instructions exist only in emulator ROM memory, with no firmware file generated. No whole-background-system no-write assertion is made.

| Gate | Confidence | Admission finding |
|---|---|---|
| B1 — real physical payload buffer | STRONG INFERENCE | Physical stock allocation and serialized lifetime PROVEN in replay; full concurrent device ownership not yet admitted |
| B2 — eight fixed reads | PROVEN | Complete normally in the stock-wrapper model |
| B3 — exact reconstruction | PROVEN | Exact synthetic 512-byte concatenation and both CRC levels |
| B4 — TEF unwind | PROVEN | **Not achieved**: injected errors retain semaphore/request/buffer |
| B5 — missing-completion bounded recovery | UNKNOWN | No proven stock-compatible bounded cancellation/unwind |
| B6 — request after failure | UNKNOWN | Busy/disconnect retries proven; TEF/missing-completion retry cannot proceed safely |
| B7 — stack/RAM bounds | UNKNOWN | Physical addresses and modeled depths proven; complete worst-case bound open |
| B8 — read-only | PROVEN | Selected fixed-read model excludes persistent writes |
| H3 | UNKNOWN | Both task bounds known; complete stack/DMA suitability unqualified |
| H4 | UNKNOWN | Normal ownership correct; bounded error/timeout recovery absent |
| H5 | UNKNOWN | Yield/drain tested; Main remains inside handler, full responsiveness/ingress/audio unqualified |
| H6 | PROVEN | Read-only within the fixed diagnostic scope |

**UNKNOWN — remaining blocker:** a proven Storage-owned bounded error/missing-completion unwind. Chunking solves normal payload capacity and establishes a physical-buffer strategy, but does not make an indefinite stock wait cancellable. Until that dependency and scheduling/ownership limits are resolved, there is no hardware-ready candidate and no installation/capture procedure. H1/H2 remain separately NOT PROVEN; no Plaits port, firmware generation or hardware action is authorized by this result.

QSPI CHUNKED READ ARCHITECTURE = UNQUALIFIED

## Phase31 — storage error recovery

**PROVEN:** the phase30 architecture and buffer are unchanged. This section supersedes phase30's H4 admission status only: **H4 = FAIL**, because bounded failure is part of that gate and fails in all six tested fault models. Normal completion remains proven within the offline model. H1/H2 are unchanged and were not re-investigated. No hardware, firmware, IRQ ownership or reference-source changes occur.

Full address-level findings, callers, completion/error closure and policy comparison are in [phase31 findings](<../docs/research/phase31-storage-error-recovery/findings.md>). Machine evidence: stock-path-audit.json (local-only reference: `builds/phase31-storage-error-recovery/stock-path-audit.json`; not distributed), fault-replay.json (local-only reference: `builds/phase31-storage-error-recovery/fault-replay.json`; not distributed), and validation.json (local-only reference: `builds/phase31-storage-error-recovery/validation.json`; not distributed). The unchanged phase30 report is archived alongside them.

**PROVEN — TEF:** QUADSPI SR `$A0001008` bit0 is peripheral transfer error, associated with invalid-address access. It is separate from DMA2 stream7 TEIF7 and FEIF7. CR.TEIE is bit16; FCR.CTEF bit0 acknowledges it. The stock selected command enables TCIE, not TEIE. QSPI IRQ `$080573E0 → $08022826` handles TCF/SMF only; DMA IRQ `$080573EE` clears TCIF7/FEIF7 and tails a no-op `$08022888`. No error completion/status is delivered to the pending read. [ST's STM32F7 QSPI definitions](https://raw.githubusercontent.com/STMicroelectronics/stm32f7xx-hal-driver/master/Inc/stm32f7xx_hal_qspi.h), [exact STM32F745 register definitions](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-f7/master/Include/stm32f745xx.h).

**UNKNOWN:** TEF alone does not establish that DMA and bus accesses are quiescent. The injected EN=1/NDTR64 state is a synthetic failure model, not a silicon measurement. Clearing a peripheral flag would not release the request, synchronize callbacks or prove the buffer reusable. No forced semaphore release was attempted.

**PROVEN — stock wait:** Storage completion `$08037596 → $08057650 → $0801BE1A → $0801CDC8` passes `$FFFFFFFF`, then requires controller bit0. Main `$08023FD6` yields until wrapper sync clears. Backend release `$08022FD4` and worker status/callback/sync clearing `$080240C4/$080240D8/$080240DE` are after return from that wait. Backend busy/bounds errors are pre-submission exits; they are not a transfer-error unwind. Initialization, semaphore-wait and status-poll routines do not provide the complete five-resource cancellation sequence.

**PROVEN — search coverage:** 75 verified direct call/tail sites for selected routines, 38 B1.3 literal-load candidates, all backend/wrapper vtable slots and captured RAM aliases are recorded. NOR consumers include the public read, protocol/updater metadata paths, queued status query and sector processing. All inspected operations converge on this worker/controller. **UNKNOWN:** exhaustive arbitrary computed indirect-call reachability outside the captured state. No safe bounded stock unwind was identified; this is not a universal nonexistence claim about the whole firmware.

**PROVEN — watchdog:** startup `$0801DA0A → $0801EAF8` enables IWDG. Idle loop `$0801CD30`, call `$0801CD4E`, invokes `$0801D760 → $0801EB1E`; the latter writes AAAA to `$40003000` to feed it. This does not test Storage progress. **STRONG INFERENCE:** a Storage wait can coexist with continued watchdog feeding. Watchdog restart is therefore not a guaranteed bounded recovery mechanism.

**PROVEN — replay:** 44 explicit assertions pass across six fault scenarios and a normal/second-normal control. Each existing TEF/missing-completion failure at chunks0/4/7 was reproduced and observed for **128 additional ticks**, with **128 actual idle-callback invocations per fault**. WFI wake and task switching remain explicit models; ticks are not hardware time. Every failure retains semaphore0, sync1, active request, live Main frame and borrowed buffer; queue/pending0 do not mean completion. Storage waits again on mask100 with timeoutFFFFFFFF. No stale notification forces false success. Selected QSPI commands are EC reads, all existing canaries remain intact and no abort/release is fabricated.

| Scenario | Completed data frames | Semaphore / sync | Buffer returned | Second successful read |
|---|---:|---|---|---|
| TEF chunk0 / 4 / 7 | 0 / 4 / 7 | 0 / 1 | No | Cannot safely admit while first request is active |
| Missing completion chunk0 / 4 / 7 | 0 / 4 / 7 | 0 / 1 | No | Cannot safely admit while first request is active |
| Normal followed by normal | 8 each, plus completion frame | 1 / 0 | Yes | Exact 512-byte synthetic reconstruction twice |

**PROVEN — policy A containment:** the smallest non-mutating response is to abandon the host capture, discard partial output, prohibit retries and leave the device request/buffer quarantined until an operator reboot. Do not return Main or restore/reuse its input while DMA ownership is unresolved. The selected fixed-read replay makes no persistent writes. **UNKNOWN:** full background application consequences and safe post-reboot recovery; existing H1/H2 do not become proven from containment. This is not in-session recovery and is not yet an accepted safe-reboot qualification.

**PROVEN — policy B:** the known application SYSRESETREQ at `$08039042–$0803905A` follows a 23-byte NOR staging-metadata program and backend wait. The enclosing updater is unsuitable for read-only recovery and may block on the same backend. Other discovered AIRCR loads set/read priority grouping or assert it; they are not reset APIs. **UNKNOWN:** a callable read-only stock reset contract; entering the updater's interior reset instructions is not a proven API or complete reset qualification.

**PROVEN — policy C:** stock idle feeds independently, so a stuck diagnostic does not guarantee IWDG expiry. Deliberately starving watchdog feeds would change policy/scheduling and is not implemented. No reset or power-cycle was performed.

**PROVEN — risk evidence:** all six failures here are injected. TEF-only IRQ invocation is artificial with selected TEIE disabled; missing completion deliberately withholds TCF/IRQ. Eight fixed accesses `$82000–$821FF` fit the actual FSIZE24 /32MiB setup, DLR63. **STRONG INFERENCE:** an invalid-address TEF is not expected for the validated request under correct configuration. **UNKNOWN:** actual hardware failure probability, lost-IRQ incidence and silicon post-error behavior. Exceptional faults remain possible; no frequency is invented. Normal stock read usage and successful modeled reads are not hardware reliability measurements.

**PROVEN:** phase27 host receiver already has an absolute per-frame timeout, raises without automatic retry and saves only after complete validation. **UNKNOWN — single smallest next experiment:** use the existing host receiver with the six truncated synthetic streams and a fake MIDI queue/clock; verify bounded host exit, no partial capture file, one sent request and explicit refusal of same-session retry. That qualifies host containment only; it does not provide device unwind, close H4, or revisit H1/H2.

**UNKNOWN — recovery admission:** no complete stock-compatible error unwind or qualified reboot strategy is established. A reboot boundary is required before retry under containment policy A; its safety remains unqualified. Existing normal read behavior is retained, but storage-error recovery is not admitted.

QSPI STORAGE ERROR RECOVERY = UNQUALIFIED

## Phase32 — one-shot host failure containment

**PROVEN:** the offline one-shot host wrapper passes. It reuses the unchanged phase27 `Receiver` and `WinMMTransport` with a deterministic fake MIDI queue and clock. Device-side architecture, normal8×64-byte read, buffer and IRQ ownership are unchanged. No firmware or hardware action occurs.

**PROVEN — timeout:** one **5.0-second absolute whole-attempt observation window**, starting before the single request, is never extended by incoming data. It includes a trailing observation period after completion: duplicate completion packets, including one at4.99s, fail. Silence before a valid completion, malformed/error frames and trailing partial SysEx fail. This is a host policy value, not a device timing measurement.

**PROVEN — success:** exactly eight sequential64-byte chunks at `$82000–$821FF`, valid addresses/index/total/token/framing, all packet CRCs and whole-capture CRC, exactly one valid completion and512 reconstructed bytes are required. Full in-memory validation precedes staging-file write/fsync/close and atomic no-replace Windows rename. The final evidence filename is never written progressively.

**PROVEN — failure:** FAILED / POWER-CYCLE REQUIRED; decoder and partial reconstruction discarded; no newly accepted `qspi_00082000_000821ff.bin`; no retry, second request or storage cleanup command. Reusing the capture, sharing its consumed lease or re-leasing its transport is blocked. The message is:

```
CAPTURE FAILED
DO NOT RETRY
POWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT
```

**PROVEN — tests:** all requested A–N cases pass containment: normal; truncated after completed chunks0/4/7; synthetic TEF/error indications at0/4/7; bad CRC; duplicate/missing/reordered chunk; duplicate/early completion; total silence. Additional tests cover actual TEF-style silence at failed chunks0/4/7, whole-data CRC, missing completion, token/address/total/length errors, fragmented/coalesced streams, trailing partial SysEx, trickled input, late duplicate completion, existing-file preservation and injected publication failure. **265 assertions,30 stream scenario groups and two filesystem checks pass.** Every failed stream produces no final file; only the complete valid512-byte stream, in three transport encodings, publishes synthetic output.

**PROVEN — synthetic result SHA-256:** `db76faa8a1c5684f01f3e176fe4a3da3cf3719d6b94f1ea097ea359f7997a5d3`. Test captures exist only in isolated directories removed after assertions; no authentic QSPI capture is claimed. TEF/error packets are explicitly synthetic kind2; actual stock TEF behavior remains silence. See [phase32 findings](<../docs/research/phase32-host-containment/findings.md>), [one-shot implementation](<../builds/phase32-host-containment/containment.py>), test results (local-only reference: `builds/phase32-host-containment/test-results.json`; not distributed) and validation (local-only reference: `builds/phase32-host-containment/validation.json`; not distributed).

**UNKNOWN — limits:** no finite window proves absence of arbitrarily late packets. The consumed lease prevents another attempt through this session; no cross-process power-cycle attestation is claimed. Live transport scheduling and filesystem power-loss durability are not tested. The old live CLI is unchanged and is not wired to this wrapper or hardware-approved. **STRONG INFERENCE:** the wrapper provides a suitable host policy boundary for future separately authorized integration.

**PROVEN:** host containment does not unwind Storage. **H4 remains FAIL for device-side in-session recovery**; the device remains quarantined until a full power cycle. H1/H2 are unchanged. Host containment PASS is not hardware readiness or proof of safe reboot.

QSPI HOST FAILURE CONTAINMENT = PASS

## Phase33 — installation preservation and power-cycle qualification

**UNKNOWN — QSPI one-shot hardware model remains UNQUALIFIED.** See [preservation/power-cycle report](<qspi82000-preservation-powercycle.md>) and phase33 evidence (local-only reference: `builds/phase33-preservation-powercycle/validation.json`; not distributed).

**PROVEN within the selected model:** all13,800 payload blocks pass native ARM SysEx unpacking and native NOR backend staging; the native boot validator enters the native installer from a differing B1.3 version. It executes110,400 modeled internal word-program calls and four effective sector erases. Installed bytes match the emulator-only phase30 prototype. NOR totals:13,801 program operations and109 erases of 4 KiB each. Staging writes`[$0,$6BD00)`, erases`[$0,$6C000)`; metadata program`[$80000,$80017)`, erase`[$80000,$81000)`. **Target writes=0; target erase overlaps=0** in this graph. No application/SYX file is exported. Boot bytes remain unchanged.

**UNKNOWN — H1:** host/RTOS update scheduling, full boot constructors and background/SD persistence are not fully coupled. The selected footprint does not qualify every installation operation. **UNKNOWN — H2:** genuine fresh reset attempts and unchanged-stock controls stop in startup decompression: boot`$0800929E` Unicorn invalid-instruction; app`$08059706` unmapped read`$1FFFFFB0`. Both zero/A5 diagnostic SRAM fixtures have the same boundary. No stable USB/MIDI state is reached; complete first-boot target read/write/erase counts are **UNKNOWN**, not zero. This is a fixture/emulator limit, not a proven firmware failure.

**PROVEN — P1:** success and six TEF/missing-completion native cases issue EC reads only, with no diagnostic-required NOR/SD/internal-flash mutation;42 assertions pass. **UNKNOWN — P2/P3:** fresh CPU/RAM/MMIO maps discard old modeled ownership, but that is not complete normal initialization or a proof SRAM always clears to zero. A full MCU/RTOS/DSP restart and post-reset write closure remain incomplete. The synthetic retained-NOR hash cannot prove the unexecuted suffix preserves target bytes.

**PROVEN — P4:** pinned64KiB bootloader unchanged; all8 modeled recovery-button subsets execute the unchanged native predicate correctly. **UNKNOWN:** unit-specific cold boot, actual power-cycle behavior and recovery installation. **STRONG INFERENCE:** read-only NOR interruption itself should not program/erase array data, and unchanged boot code retains its architectural recovery option. These do not close H2/P2/P3.

**PROVEN — correction:** phase31 prose reversed low helper names: erase is`$08037494`, program is`$080374D4` (phase28 and phase33 are correct). Prior evidence is retained unchanged; read-failure findings are unaffected.

**PROVEN:** phase32 host containment remains PASS; device H4 remains FAIL for in-session recovery. Intended policy is ONE REQUEST PER BOOT, success ends session, failure means no file/no retry and requires full power cycle before any new attempt. **UNKNOWN:** hardware admission remains blocked; no candidate generation follows. Minimum next offline experiment: qualify stock startup scatter decompression at the recorded stop boundaries, then resume real constructors/write tracing to a stable application state.

QSPI ONE-SHOT HARDWARE MODEL = UNQUALIFIED

## Phase34 — startup observer repaired; complete cold boot still open

**PROVEN:** the phase33 decompression failure is caused by an **all-address Unicorn RAM-read hook**, reproduced even with an empty callback. Restricting memory hooks to peripheral/register and internal-flash-store ranges makes the real, unchanged decompressor return. No firmware patch, PC skip, fabricated dictionary or decompressed-output injection is used. Corrected stock controls pass before diagnostic comparisons.

**PROVEN:** boot descriptor`$08009694`, source`$08009A84`/885bytes, destination`$20000004` produces11,084bytes. Application descriptor`$0805B7C8`, source`$0805C3C4`/2,582bytes, destination`$20000000` produces15,618bytes. Eight native controls match an independent byte-level oracle; four A5-SRAM controls also return. Old stops at`$0800929E`/`$08059706` are observer artifacts, not missing ROM/history/storage inputs. [Phase34 findings](<../docs/research/phase34-startup-decompression/findings.md>) provides registers, call chains, descriptors, hashes, RAM windows and the controlled hook ablation.

**PROVEN within explicit peripheral models:** ideal RCC readiness, native QSPI completion handlers for F5/35/B7, documented reference-part AF identity C22019 and native periodic SysTick advance the prefix further. These assumptions are recorded separately from the proven hook correction. Stock, unchanged B1.3 and diagnostic SRAM checkpoints agree. Application startup reaches an **SDMMC1 command wait at`$0801C63C`**, object`$20005548`, not a decompressor wait. Bootloader reaches SVC scheduler startup`$080031C2`, where architectural exception/context-switch service is missing. Main task setup has executed; Main/Storage task entry execution and normal USB/MIDI-ready state remain UNKNOWN.

**PROVEN observed-prefix target counts:** reads0 / writes0 / erase-overlaps0. **UNKNOWN full-boot counts:** reads UNKNOWN / writes UNKNOWN / erase-overlaps UNKNOWN. No automatic diagnostic array read occurs in the observed prefix. Unexecuted storage mounting/project/background paths are not silently counted as zero.

**PROVEN partial reset:** all six recorded stale-failure SRAM seeds are overwritten/reconstructed by native startup and constructors: semaphore1, sync/pending0, task flags0, DMA EN0/NDTR0. No application cleanup or same-boot retry is used. **UNKNOWN:** complete parser/diagnostic/task/DSP ownership and target preservation beyond the SDMMC stop. Partial native reset evidence does not qualify P2/P3.

**UNKNOWN H1/H2/P2/P3:** complete install/first-boot/reset closure is still missing SVC/PendSV and SDMMC/storage services. Phase33's selected13,801 NOR writes /109 erases still have zero target overlap; that unchanged evidence is not upgraded to a full-install claim. **PROVEN within prior scope:** P1 remains read-only diagnostic behavior; P4 remains unchanged bootloader code. Host containment stays PASS; H4 remains FAIL for in-session device recovery. No firmware generation, hardware access, reference/pinned-source edit or Plaits work occurred.

**UNKNOWN — smallest next offline experiment:** qualify native bootloader SVC entry/EXC_RETURN/PSP restoration from the actual initialized task frame at`$080031C2 → $08003188`, without forcing PC or task-ready flags. See validation (local-only reference: `builds/phase34-startup-decompression/validation.json`; not distributed) and [complete phase34 evidence](<../docs/research/phase34-startup-decompression/findings.md>).

QSPI PRESERVATION / COLD-BOOT MODEL = UNQUALIFIED

## Phase35 — native bootloader SVC and PSP restoration qualified

**PROVEN within the observed privileged basic-frame path:** stock first, then diagnostic execute the same native scheduler-start SVC `$080031C2`. Before entry: MSP=`$20050000`, PSP=0, CONTROL=0, LR=`$08002E2B`, PRIMASK/FAULTMASK=0, BASEPRI=`$C0`, xPSR=`$61000000`. SVC priority0 is unmasked. VTOR `$08000000`, vector `$0800002C → $08003189`. Architectural entry stacks eight words at MSP `$2004FFE0`, LR=`$FFFFFFF9`, IPSR=11; the actual handler executes unchanged.

**PROVEN:** native frame constructor `$08002D3C` creates the first task context; no host task frame is injected. Current-TCB global `$20005268` points to IDLE TCB `$20007EB8`, whose saved context is `$20007E6C`. Native `$0800318E` loads r4-r11/LR, and native `$08003192` restores PSP=`$20007E90`. BX LR uses the task's `$FFFFFFFD`; architectural unstack consumes the native frame once, restoring PC=`$08002A58`, PSP/SP=`$20007EB0`, CONTROL=2, privileged Thread mode. Original MSP SVC frame remains at `$2004FFE0`, as required when starting another context. No handler RAM writes or saved-frame corruption occur.

**PROVEN:** stock/diagnostic SVC records and complete SRAM match. Eight native idle instructions run with PSP, then request PendSV via ICSR. Both stop at `$08002A6E`, before executing further with unsupported pending service. This is a post-SVC task checkpoint, not stable USB/MIDI readiness. Twenty-two architectural fixtures pass, including PSP/MSP selection, padded/aligned frames, invalid EXC_RETURN/PC/Thumb/RAM rejection and single consumption. Unsupported nesting, FP return and unprivileged fixtures fail closed. **UNKNOWN:** full NVIC/PendSV and unprivileged/FP behavior; the inherited earlier IRQ/timing/NOR assumptions remain conditional. M7 STKALIGN=1 is explicitly modeled despite the flat CCR backing register.

**UNKNOWN:** H1/H2/P2/P3 and full-boot target counts. Observed-prefix target counts are0 reads/0 writes/0 erase overlaps only. P1 remains PROVEN in its prior diagnostic scope; P4 remains PROVEN for unchanged code. Host containment remains PASS; H4 remains FAIL in-session. Application SDMMC wait `$0801C63C` remains the separate, untouched phase34 boundary. No firmware generation, hardware access, reference/pinned edits or Plaits work occurred.

**UNKNOWN — exactly one next smallest experiment:** qualify native bootloader PendSV `$0800312C` from the real idle-generated pending state `$08002A6E`, including native task save/scheduler/restore and architectural return. It is not implemented here. See [phase35 findings](<../docs/research/phase35-svc-context/findings.md>), native stock trace (local-only reference: `builds/phase35-svc-context/stock.json`; not distributed), diagnostic trace (local-only reference: `builds/phase35-svc-context/diagnostic.json`; not distributed) and validation (local-only reference: `builds/phase35-svc-context/validation.json`; not distributed).

BOOTLOADER SVC / PSP MODEL = PASS

## Phase36 — first native PendSV context switch qualified

**PROVEN:** stock first, then diagnostic replay exactly the phase35 pending CPU/SRAM state at `$08002A6E`. Pre-entry MSP=`$2004FFE0`, PSP=`$20007EA0`, CONTROL=2, xPSR=`$21000000`, PRIMASK/BASEPRI/FAULTMASK=0, LR=`$08002D65`; native IDLE has set PendSV pending. VTOR vector `$08000038 → $0800312D` selects native entry `$0800312C`. Architectural entry stacks the actual Thread context on PSP `$20007E80`, consumes pending, enters Handler mode on MSP and installs EXC_RETURN `$FFFFFFFD`.

**PROVEN:** native `$08003142` saves r4-r11/LR at `$20007E5C`; `$08003146` writes that context pointer to IDLE TCB `$20007EB8`. Native scheduler `$080029D8` uses ready bitmap1 and priority0 list `$20005204` (count4), moves list index `$20005208` to node `$2000648C`, and selects owner TCB `$20006488`. Its native constructor frame at `$2000643C` belongs to bootloader Main by both recorded entry `$08002FDF` and name. No generic scheduler, task-ready flag or host-created task frame is substituted.

**PROVEN:** native handler restores r4-r11 and EXC_RETURN, then native `$0800317E` writes PSP=`$20006460`. Architectural BX/return consumes the hardware frame once, restoring PC=`$08002FDE`, PSP=`$20006480`, CONTROL=2, privileged Thread mode; MSP remains `$2004FFE0`. All seven native store intents, including unchanged-value stores, and per-instruction full-SRAM differences remain within the declared outgoing stack/MSP scratch/TCB/scheduler ranges. No unrelated RAM modification occurs in the switch. No FP save/restore instruction executes in the observed basic-frame path.

**PROVEN:** stock/diagnostic entire PendSV records and complete SRAM agree;32 new native-evidence/architectural-fixture checks pass. A minimal-observer stock control matches the detailed trace, avoiding the prior RAM-hook artifact. Malformed context/EXC_RETURN, alignment, pending consumption and single unstack are tested separately from native boot. **UNKNOWN:** a second PendSV does not occur before the first due post-scheduler tick; nested/FP/unprivileged and later scheduling remain unqualified.

**PROVEN within the inherited ideal2000-instruction cadence:** both execute Main and stop at `$08006EF2`, before delivering the first post-scheduler SysTick. This is an RTOS service boundary during ordinary ring-buffer work, not an SDMMC wait or a firmware-fault conclusion. The earlier pre-scheduler IRQ wrapper is not used for the scheduled context. **UNKNOWN:** real interrupt timing, full boot and stable USB/MIDI state. Application SDMMC `$0801C63C` remains the separate unchanged prior boundary and was not investigated.

**UNKNOWN:** H1/H2/P2/P3 and full-boot target counts. Observed-prefix target counts remain0 reads/0 writes/0 erase overlaps only. P1 remains PROVEN within prior diagnostic scope; P4 remains PROVEN unchanged boot code. H4 remains FAIL in-session; host containment remains PASS. No firmware generation, hardware access, reference/pinned edit or Plaits work occurred.

**UNKNOWN — exactly one next smallest experiment:** qualify native post-scheduler bootloader SysTick from the captured Main-context boundary `$08006EF2`, including any naturally requested PendSV; stop at the next unsupported boundary. See [phase36 findings](<../docs/research/phase36-pendsv-context/findings.md>), stock (local-only reference: `builds/phase36-pendsv-context/stock.json`; not distributed), diagnostic (local-only reference: `builds/phase36-pendsv-context/diagnostic.json`; not distributed) and validation (local-only reference: `builds/phase36-pendsv-context/validation.json`; not distributed).

BOOTLOADER PENDSV / CONTEXT MODEL = PASS

## Phase37 — native post-scheduler bootloader SysTick qualified

**PROVEN:** native configuration computes LOAD=`$1D4BF` (119,999) from represented core clock120MHz and writes CTRL=7: processor-clock source, counter and interrupt enabled. SysTick/PendSV priority bytes are both `$F0`. **STRONG INFERENCE:** intended1ms cadence if the clock equals120MHz. **UNKNOWN:** real timing; the existing ideal2000-instruction event source is retained and VAL is not decremented.

**PROVEN:** stock first, diagnostic second reproduce the phase36 CPU/SRAM checkpoint at `$08006EF2`: Main TCB `$20006488`, MSP=`$2004FFE0`, PSP=`$200063C4`, CONTROL=2, masks0. SysTick vector `$0800003C → $08009331` selects actual handler `$08009330`. Architectural entry consumes pending, enters Handler mode on MSP, and stacks the padded hardware frame at PSP `$200063A0`, xPSR=`$01000200`, EXC_RETURN=`$FFFFFFFD`.

**PROVEN:** actual `$0800935C` clock helper updates `$20000008` 7→8 and the handler updates `$20005518` 0→1. Kernel counter `$200053C0`, scheduler lists/bytes and current TCB remain unchanged. SysTick requests no PendSV. Native POP/architectural return consumes the frame once, restores every Thread register, returns to `$08006EF2`, PSP=`$200063C4`, MSP=`$2004FFE0`, CONTROL=2 and xPSR=`$01000000`. No synthetic software tick increment or scheduler-success flag is used.

**PROVEN:** old ideal wrapper matches live registers and scheduler/counter results but differs in10 stack words: omitted4-byte alignment pad and sentinel LR instead of EXC_RETURN. The native exception path is authoritative. Twenty-four new native-evidence/architectural checks pass; masking retains pending until unmask. Stock/diagnostic and minimal-observer controls match full final SRAM and CPU/context boundaries. **UNKNOWN:** tick-produced PendSV/tail chaining and a second post-scheduler tick are unobserved before the next boundary; neither event is fabricated.

**PROVEN:** later Main and UI each request PendSV through native `$08004720`, independently of SysTick. The unchanged phase36 native model switches Main→UI (`$08003048`, PSP `$20006E00`) then UI→Storage (`$08009202`, PSP `$20007468`), using constructor-created frames and checked ownership ranges. Storage stops at `$080051C2` after issuing `$EC`, address `$81000`, DLR22: an unsupported23-byte array-data read. No data/metadata or completion success is supplied. Bootloader has not completed; application SDMMC `$0801C63C` remains untouched.

**PROVEN observed-prefix target counts `$82000–$821FF`:** reads0 / writes0 / erase overlaps0. The pending `$81000–$81016` read is outside the target. **UNKNOWN:** complete-boot counts and H1/H2/P2/P3. P1 remains PROVEN in its prior diagnostic scope; P4 remains PROVEN unchanged bootloader bytes. Host containment remains PASS; H4 remains FAIL in-session. No firmware generation, hardware access, pinned/reference edit or Plaits work occurred.

**UNKNOWN — exactly one next smallest experiment:** qualify native bootloader Storage's23-byte `$EC` read at `$81000–$81016` using provenance-checked existing NOR bytes and native completion; establish byte provenance before replaying data, then stop at the next unsupported boundary. See [phase37 findings](<../docs/research/phase37-systick/findings.md>), stock (local-only reference: `builds/phase37-systick/stock.json`; not distributed), diagnostic (local-only reference: `builds/phase37-systick/diagnostic.json`; not distributed) and validation (local-only reference: `builds/phase37-systick/validation.json`; not distributed).

BOOTLOADER SYSTICK MODEL = PASS

## Phase38 — NOR81000 read identified; original payload not qualified

**PROVEN:** Main `$08003A42 → $08005D98` requests exactly23 bytes at external NOR `$81000–$81016`, destination `$2000546C`. Native synchronous wrapper `$08005880` submits a24-byte operation1 record through queue `$20007A60`; Storage TCB `$20007470` dequeues the copy at `$2000742C` and dispatches backend `$08005338 → $080076CC`. DMA has NDTR23, PAR `$A0001020`, M0AR `$2000546C`; native command is `$EC`, AR `$81000`, DLR22. Stock/diagnostic prefix observers preserve the phase37 CPU/SRAM endpoint exactly.

**PROVEN static consumer:** after return, `$08005DB0` overwrites identity-cache byte14 with zero. The later constructor/protocol paths inspect/copy14 alphanumeric identity bytes and register the record pointer for string formatting. **STRONG INFERENCE:** the first14 bytes are a serial/identity string. **UNKNOWN:** exact trailing bytes15–22 semantics and original record contents. Post-read RAM cannot establish the destroyed original byte14.

**PROVEN census; UNKNOWN NOR provenance:** reused1858 existing candidates and33 archive-container records, rehashed22 relevant capture/update files and checked the current project/reference file delta. No candidate proves file offset→physical NOR `$81000` mapping for all23 original bytes. Internal flash/application images, SRAM snapshots, generated reset/diagnostic data and updater metadata at `$80000` are not admitted substitutes. Full source paths, SHA-256 values, address spaces and rejections are recorded in [candidate sources](<../docs/research/phase38-nor81000/candidate-sources.md>) and catalog (local-only reference: `builds/phase38-nor81000/candidate-catalog.json`; not distributed).

**UNKNOWN:** no accepted source/offset/23-byte hex/slice SHA exists. No payload is extracted or injected, no IRQ/completion success is asserted, and no post-consumption checkpoint is claimed. The native DMA/QSPI completion, semaphore release, sync clear and caller-return paths are documented statically but remain unexecuted for this read. The semaphore remains held and Main/request ownership remains retained at the original `$080051C2` boundary.

**PROVEN observed-prefix target `$82000–$821FF` counts:**0 reads /0 writes /0 erase overlaps. **UNKNOWN:** post-read/full-boot counts and H1/H2/P2/P3. P1 remains PROVEN in its previous scope; P4 remains PROVEN unchanged code. H4 remains FAIL in-session; host containment remains PASS. No target data investigation, SDMMC work, firmware generation, hardware access or reference/pinned-source edit occurred.

**UNKNOWN — minimum missing prerequisite:** existing original bytes and acquisition metadata proving exact file-offset mapping to `$81000–$81016`, including byte14. Only then can the native Storage completion experiment proceed. See [phase38 findings](<../docs/research/phase38-nor81000/findings.md>), payload admission (local-only reference: `builds/phase38-nor81000/payload-admission.json`; not distributed) and validation (local-only reference: `builds/phase38-nor81000/validation.json`; not distributed).

NOR81000 STORAGE READ = UNQUALIFIED

## Phase39 — symbolic byte14 equivalence remains unqualified

**PROVEN static normal-return order:** `$08005DAE MOVS r2,0` then `$08005DB0 STRB r2,[r4,#$E]` zero `$2000547A`, byte14 of the boot record. Main performs no payload read/copy/compare/call/branch/yield between that read return and the store. The identity constructor and formatting-pointer publication occur afterward. **UNKNOWN:** full non-observability from DMA visibility across Storage/task/IRQ/indirect-reader activity; the immediate Main pair is not an all-task/all-IRQ proof, and no first observer is established.

**PROVEN focused provenance facts:** application reader `$0802520C` uses cache `$20006868`, distinct from bootloader `$2000546C`. The two previously authenticated-file RAM snapshots map to SRAM by loader code, but their candidate bytes0–13 and15–22 differ in both ranges. **UNKNOWN:** capture timing/population, intervening identity edits and equality to the22 original or unchanged post-read bytes for this exact request. Native edit helper `$08005E88 → $08005EAC` can replace the first14 bytes; whether it ran before a capture is unknown. The other22-byte gate therefore independently fails.

**PROVEN:** followed the user's section8 stop condition. Exhaustive native variants tested=0; no concrete23-byte NOR record, guessed byte14, completion signal, convergence result or boot advancement is fabricated. **UNKNOWN:** post-zero convergence, completed-read behavior and global semantic unobservability. Unknown byte14 alone is not the rejection reason:22 proved values plus a complete concurrency proof could admit the proposed equivalence without reconstructing original byte14.

**PROVEN inherited prefix counts for `$82000–$821FF`:**0 reads /0 writes /0 erase overlaps; no new prefix reached. **UNKNOWN:** full-boot/post-read counts, H1/H2/P2/P3. Stock and diagnostic retain the prior `$080051C2` boundary; no new emulation is claimed. Earlier P1/P4 scopes, H4 FAIL and host-containment PASS remain unchanged. No firmware generation, hardware access, pinned/reference edits, target-data investigation or SDMMC work occurred.

**UNKNOWN — next blocker:** request-linked unchanged provenance for the22 observable bytes, followed by complete completion-to-zero observer closure. See [phase39 findings](<../docs/research/phase39-nor81000-symbolic/findings.md>), other22 provenance (local-only reference: `builds/phase39-nor81000-symbolic/other22-provenance.json`; not distributed), ordering (local-only reference: `builds/phase39-nor81000-symbolic/byte14-ordering.json`; not distributed) and validation (local-only reference: `builds/phase39-nor81000-symbolic/validation.json`; not distributed).

NOR81000 SYMBOLIC BYTE14 QUALIFICATION = UNQUALIFIED

## Phase42 � exact SC35D8 integration qualified offline

**PROVEN:** the closed exact-base gate was reused: SC35D8 size `$5BC8C`, CRC `$73BA1238`, SHA-256 `1525c6662bbff9ced7e6055bb54e864615c30013f1b4dec4be6c404f8c750c05`. The internal candidate has the same size, CRC `$AC9987BA`, SHA-256 `9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6`. No new SYX or hardware access occurred.

**PROVEN in bounded native replay:** a 12-byte record at `$20044D70�$20044D7B` survives parser reuse and implements IDLE / ACTIVE / SUCCESS / FAILED_QUARANTINED. It extends the reference heap-top reservation by 12 bytes, preserves the existing 220-byte Master-FX state, and fails closed if reservation is unavailable. Duplicates and new sessions cannot rearm it. All requested A�O adversarial cases pass; the native RX ring, Main parser/fanout, Storage read path and native TX router execute. Pending input can overwrite the parser after return; the persistent latch, rather than serial dispatch, prevents another capture. Full 232-byte adversarial overwrite after return changes neither state nor admission.

**PROVEN:** native TX copies replies synchronously to `$20009BAC`; asynchronous USB IN uses independent `$20009B04`. Delayed/lost completion tests verify no premature buffer reuse. At 5000 counter ticks the device only quarantines; it never forces Storage release. H4 remains FAIL for in-session recovery. The host has a separate 5.0-second deadline, atomic publication, and one-attempt guards for both transport Link and lease. Native USB output reconstructs exactly 23 + 512 synthetic bytes; truncation/duplicate completion publishes nothing. The output under `builds/phase42-exact-rdiag-integration/synthetic-capture/` is synthetic, not device evidence.

**PROVEN for this exact image in the selected updater/install model:** both `$81000�$81016` and `$82000�$821FF` have zero direct writes and zero erase overlaps. Minimum half-open WRITE/ERASE gaps are respectively 4073/0 bytes and 8169/4096 bytes; zero means adjacent, not overlapping. Native validation/installer loops install the exact candidate. DSP, vectors, bootloader and option bytes remain unchanged. All pinned reference/Plaits and prior validated evidence hashes remain unchanged.

**STRONG INFERENCE:** guarded entry structure and unchanged startup keep the command dormant before an explicit request. **UNKNOWN:** complete cold-boot write census, actual unit heap headroom, physical I/O timing, actual NOR contents and hardware recovery. The selected updater trace uses modeled interfaces/completion; unchanged identity maintenance can erase its own sector if invoked. This offline qualification does not close those broader hardware/boot claims.

See [phase42 findings](<../docs/research/phase42-exact-rdiag-integration/findings.md>), exact patch map (local-only reference: `builds/phase42-exact-rdiag-integration/patch-map.json`; not distributed), native cases (local-only reference: `builds/phase42-exact-rdiag-integration/native-results.json`; not distributed) and installation trace (local-only reference: `builds/phase42-exact-rdiag-integration/installation.json`; not distributed).

**STRONG INFERENCE � next and only next phase:** candidate-SYX generation plus independent offline validation from this pinned BIN; no transmission. That phase has not been started.

EXACT RDIAG NOR INTEGRATION = PASS
