# Research timeline — final pre-hardware review

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

## Latest recorded decisions

| Event | Current interpretation |
|---|---|
| Independent Claude review, user-reported | REASONABLE TO PROCEED WITH CONTROLLED HARDWARE TEST, subject to accepted residual risk; not physical proof |
| Frozen operational package | Exact Phase63 candidate and rollback identities, locked host/uploader; no operational release enabled |
| Final two-check closure | USB STORAGE JOINT PATH = PASS, 36 focused cases; allocation remained UNQUALIFIED |
| Final indirect resolution | Seven normal Content targets recovered; remaining virtual/registry targets, including 0803C91C/0803C9C4, not exhaustively bound. No actual >8-byte post-READY allocation found; absence not proven |
| Recovery packaging correction | recovery-status.txt clarified; SHA-256 169f295e37fc8b39d51ec5e38a54d2d341d52cd7b2bca7b8d762ff6ff019008d; 633 manifest-listed files verified |
| Current user decision | Soft-brick/recovery risk accepted without guarantee; tools stay locked pending separately reviewed release |

Evidence precedence: [final allocation decision](<research/final-indirect-resolution/findings.md>) controls the remaining software proof boundary; [USB joint-path closure](<research/final-two-check-closure/usb-joint-closure.md>) records 36 passing focused cases. [Phase67](<research/phase67-final-safety-disposition/findings.md>) retains its bounded configuration/query/authorization-to-capture-entry scope. The frozen [package audit](<research/final-hardware-test-package/final-cheap-checks.md>) preserves the earlier two-gap history, with a current supersession notice. No model PASS is physical proof.

## Historical research milestones

Order follows recorded phase progression. Calendar dates are omitted where not established. **PROVEN** means the stated artifact/replay scope, not hardware success. Historical evidence files remain unchanged. All diagnostic images before Phase63, including Phase61/62, are SUPERSEDED — DO NOT FLASH. Earlier statuses/next steps are historical. Phase67 retains its scoped model result; later final allocation/joint-path decisions control current operational status. Phase63 bytes are unchanged.

| Milestone | Result/current interpretation |
|---|---|
| Stock baseline | **PROVEN:** official 4486 / 1.2.1, 314844-byte BIN, CRC `4E74DA9E`; identity in historical baseline evidence, separate from Phase61. |
| DSP upload discovery | **PROVEN:** ARM upload/bootstrap protocol and extracted core0/core1 programs; ROM handoff and live init are separate boundaries. |
| Stock synth localization | **PROVEN:** descriptors, generation/output seams and ARM parameter paths mapped; broad deletion remains **UNKNOWN**. |
| B1.3 reconstruction/vpre | **PROVEN:** reference code/mailboxes, strip insertion and offline VariableSaw experiments. One Plaits track while retaining the other old oscillator is **SUPERSEDED** as final architecture. |
| Dual replacement/Layout A | **PROVEN within retained replay:**1075 reclaimed P words, 8192-block stock/master comparison. Layout B extra 102 not admitted. |
| Source pinning/Modal wrapper | **PROVEN:** pinned 24-model source; native 12 → Circuit 32 host scheduling exact over 4096 blocks. |
| Modal numeric port | **PROVEN:** wide fixed recurrence experiment; complete engine **UNKNOWN**. |
| Native optimization | **PROVEN:** D isolated 220 P /100 X histories per voice; worst 77697 modeled cycles. Earlier coarse/762600-cycle implementation **SUPERSEDED as best kernel**. |
| Four-track decision/resource audit | Four Plaits tracks, max 2 tracks/model, max 2 poly tracks. Four-Modal requirement **SUPERSEDED**; final safe P/X/Y **UNKNOWN**. |
| P:$0282–$0386/coefficient provenance | Candidate 261 words **UNKNOWN**; authentic initializer blocked on 512-byte NOR `$82000` coefficients. |
| Phase27 | **PROVEN synthetic/offline scope:** read transport prototype. Its 512-byte/artificial high-SRAM allocation approach is **SUPERSEDED** by physical small-buffer architecture. Synthetic BIN/SYX replies are not NOR evidence. |
| Phase28 | Stack/IRQ/Storage effects examined; direct-backend/context assumptions **SUPERSEDED** by actual task submission. |
| Phase29 | **PROVEN scoped native replay:** synchronous Storage queue/worker/IRQ ownership; arena/service fixtures explicit. |
| Phase30 | **PROVEN normal scoped path:** eight 64-byte chunks through one physical parser window, no 512-byte device allocation. Error unwind unqualified. |
| Phase31 | **FAIL H4:** TEF/missing completion retain Storage/request/buffer ownership; no bounded in-session unwind. |
| Phase32 | **PROVEN offline:** fake clock/transport, 5 s absolute deadline, complete validation, atomic acceptance and no retry. Initially a 512-byte host wrapper, not live integration. |
| Phase33 | Installation/power-cycle preservation investigation: selected prefixes, not universal boot preservation. |
| Phase34 | Startup decompression observation corrected; broad RAM hooks could perturb emulation. Complete boot **UNKNOWN**. |
| Phase35 | **PROVEN scoped:** first privileged basic-frame SVC; not all exceptions/RTOS behavior. |
| Phase36 | **PROVEN scoped:** first Idle→Main PendSV; not every task/interleaving. |
| Phase37 | **PROVEN scoped:** native SysTick and Main/UI/Storage transitions reach 23-byte identity read; physical cadence conditional. |
| Phase38 | **PROVEN:** missing NOR `$81000–$81016` boot data is concrete blocker; identity interpretation **STRONG INFERENCE**. |
| Phase39 | Byte 14 zeroing order mapped; symbolic equivalence **UNKNOWN** due to other 22 provenance and observer closure. No exhaustive variants claimed. |
| Phase40 | Taint/prefix artifacts exist; no completed universal qualification. Acquisition takes priority; do not label this phase PASS. |
| Reuse audit | Reference rdiag USB/SysEx/small SD-content transport implemented and reported hardware-tested. DSP SDRAM tests do not prove ARM NOR. Full peripheral emulation is not universally required before designing post-boot acquisition. |
| Phase41 fixed diagnostic | **PROVEN scoped offline prototype:** fixed 535-byte architecture; exact-base/ownership limits later **SUPERSEDED** by phase42. |
| Phase42 exact SC35D8 | **PROVEN offline:** exact rebuild, persistent 12-byte latch, RX/TX ownership, containment and selected installation replay. “SYX not yet generated” **SUPERSEDED by phase43**. |
| Phase43 — HISTORICAL / SUPERSEDED | Earlier scoped offline PASS, followed by race discovery in Phase44. **SUPERSEDED — DO NOT FLASH.** |
| Phase44 — SUPERSEDED diagnostic | Red-team review reproduced quarantine→SUCCESS race; separate atomic correction and changed-header/no-op review. Its research candidate is **SUPERSEDED — DO NOT FLASH**. |
| Phase45–48 | NOR mutation/storage/filesystem preservation and current-unit geometry investigation; historical obligations motivated the geometry gate. |
| Phase49–53 | Existing B1.3 geometry-reader/MSD branch exhausted: Phase53 **PROVEN NO** for sufficient authentication via inspected unmodified interfaces; no repeated-read scheme pending. |
| Phase54–60 | Early snapshot, compact geometry, lifecycle, scheduler/first-mount/IRQ provenance and adapted-owner models. Intermediate model results are not candidate hardware evidence. |
| Focused final triage | TIM2/display DMA and RTC alarm **SAFE / IRRELEVANT** for the specified NOR/geometry concerns; five legacy owners remained the schema-integration task. |
| Phase61 — HISTORICAL / SUPERSEDED | Reservation-negative failure discovered later; **FAILED reservation test / DO NOT FLASH.** |
| Phase62 — HISTORICAL / SUPERSEDED | Reservation guard fixed; then preflight failed SD invalidation, status ambiguity and DMA lifetime. **DO NOT FLASH.** |
| Phase63 | Those three concrete defects fixed/regression-tested; N63DEV identity unchanged thereafter. Then-UNQUALIFIED frontier was model/startup/allocation coverage. |
| Phase64 | Narrow SPI2 model closure; no firmware change. |
| Phase65 | SHI coefficient-transfer closure: 144 uploads, 148 startup jobs posted, 147 idle completions observed. Synthetic inputs are not authentic unit contents. |
| Phase66 | USB controller READY, geometry intact; 3,186 allocator returns without failures/overlap. DWT logging stop is model coverage, not firmware defect. |
| Phase67 — scoped model | Historical scoped disposition B; bounded configuration/query/authorization reaches capture entry with zero new allocations. Later all-root allocation analysis retains a separate SOFTWARE UNKNOWN. **FINAL PREFLIGHT CLOSURE = PASS**, no hardware test. |

Later offline PASS does not supersede H4 FAIL. Reference hardware-tested SD diagnostics are not a hardware test of the final raw-NOR candidate.

Evidence: [baseline](<../notes/baseline.txt>), [DSP handoff](<../notes/dsp-boot-handoff.md>), [vpre](<../notes/plaits-midi-vpre-offline.md>), [Layout A](<../notes/stock-master-signal-path-qualification.md>), [Modal](<../notes/plaits-modal-dsp-port.md>), [optimization](<../notes/plaits-modal-native-optimization.md>), [four-track](<../notes/four-track-plaits-resource-architecture.md>), [reclaim](<../notes/p0282-0386-reclaim-qualification.md>), [phase27](<../notes/qspi82000-read-diagnostic.md>), [readiness](<../notes/qspi82000-hardware-readiness.md>), [preservation](<../notes/qspi82000-preservation-powercycle.md>), [reuse](<../notes/circuits-hacks-diagnostic-reuse-audit.md>), [fixed diagnostic](<../notes/fixed-nor-evidence-diagnostic.md>), [phase43](<research/phase43-hardware-test-candidate/findings.md>).

Current identity/stop point: [CURRENT_STATUS.md](<CURRENT_STATUS.md>) and [HANDOFF.md](<HANDOFF.md>). Next action is separately reviewed operational-release preparation; no automatic hardware action or further research.
