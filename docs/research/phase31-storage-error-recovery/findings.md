> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase31 — stock storage error recovery

PROVEN: this experiment leaves the phase30 normal 8×64-byte architecture, buffer, IRQ instructions, reference repository and pinned sources unchanged. Only evidence/scripts in phase31 and the appended readiness report are changed. No hardware access, firmware generation, live MIDI, NOR/SD program/erase or bootloader action occurs.

PROVEN: `fault_replay.py` imports the unchanged physical-address phase30 `Model`; it does not run earlier evidence writers. `stock-path-audit.json` records 75 verified direct call/tail sites for the selected routines, 38 literal-load candidates, vtables and captured RAM aliases. The halfword-aligned literal scan includes data decoded as possible instructions: candidates are not automatically reachable code. Direct sites from `reference/re/app.asm` are checked against actual B1.3 bytes.

UNKNOWN: completeness for arbitrary computed indirect callers, dynamically created aliases and full background scheduling. This report does not prove universal nonexistence of a recovery routine anywhere in firmware. It establishes the behavior of the actual selected backend and its inspected users; no usable stock unwind was found. The qualification remains open rather than converting this scoped negative result into a complete proof.

## Exact backend and users

PROVEN: captured NOR wrapper `$2000AC94`, global `$20006968`, points at backend `$20000378`, context `$20000000`, controller `$20005550`, QUADSPI `$A0001000`, DMA2 stream7 `$400264B8`. Backend vtable `$0805B1AC` contains these Thumb targets (table below gives even instruction addresses):

| Slot | ARM address | Actual behavior |
|---|---|---|
| +0 | `$08022F1E` | Initialization/configuration; not cancellation |
| +4 | `$0805C268` | Trivial leaf |
| +8 | `$08022F5E` | Configuration/status access |
| +C | `$08022F94` | Bounds/semaphore check, DMA read, release after completion |
| +10 | `$08022FDC` | Program path; not exercised |
| +14 | `$0805C26C` | Trivial leaf |
| +18 | `$08023078` | Erase path; not exercised |
| +1C | `$080230F8` | Wait for byte semaphore; no cancel |
| +20 | `$0802310A` | Completion/wait callback registration |

PROVEN: wrapper constructor `$08023F2C` is called at `$0801E3BE` for this NOR backend and at `$0801E3D8` for the separate SD backend `$20000338`. Wrapper vtable `$0805B1D8` supplies config `$080240FE`, read `$08024130`, write `$08024164`, erase `$080241B8`, synchronous wait `$08023FD6`; callback slot +20 is trivial `$0805C154`. There is no exposed cancel operation. Backend creation is `$0801DEFA → $08022F10`; direct initialization `$0801E076 → $08022F1E`.

PROVEN: enqueue `$08023F68` has direct calls `$0802411C/$08024154/$08024196/$080241AC/$080241DC/$08026C10`. `$080241AC` is also the common tail for asynchronous erase `$080241F0`; its only verified direct user is `$08024DB0`. It is not an asynchronous read API. The direct enqueue at `$08026C10` builds a status/config request and then calls the same wrapper wait. These paths converge on the same worker, not a second recovery service.

PROVEN: Storage `$0805767C` installs callback `$08057650`; it services NOR and SD through `$08024014` at `$080576A6/$080576B0`, then waits. NOR worker operation dispatch `$08024070` covers 0=config, 1=read, 2=program, 3=erase, 4=backend-semaphore wait. Only after backend return does `$080240C4` store status, `$080240D8` invoke request callback, and `$080240DE–$080240F6` clear synchronous ownership. Those instructions cannot execute for a still-blocked read.

PROVEN: literal-global users and their readable extracts are preserved in this directory and `stock-path-audit.json:literal_load_candidates`:

| User/call sites | Route and recovery relevance |
|---|---|
| `$0801E3C2` | Creates/publishes NOR queue wrapper |
| `$0801F0A8 → $0801AE3A` | Attaches wrapper to existing storage object at `$20000AA0` (+4 holds wrapper) |
| `$08024D5C` | Binds protocol/updater context `$20006930+8` to wrapper |
| `$08024DD0–$08025008` | Protocol dispatch, async erase callback `$08024E00`, read/send loop `$08024FDC`; sleep20 at `$08024DB6` is a repeated poll, not a timeout/abort |
| `$08025220/$0802523E` | Read/write 23-byte metadata at `$81000`; no recovery |
| `$08026C10/$08026C1A` | Queued query then same synchronous wait |
| `$08047C6C → $08024130` | Public wrapper read used by phase30 diagnostic |
| `$0805768E/$08057694` | Storage wrapper/callback registration |
| `$08057EB2/$08057ECC` | Wait plus read for storage comparison/processing |
| `$08057F30/$08057F44/$08057F94` | Wait, sector read, conditional sector write; not read-only recovery |

PROVEN: captured RAM also contains wrapper values at `$20000AA4/$20006938/$20006968/$2000952C/$20009570/$200095D4/$200095FC/$20009640`. Several high addresses contain saved PCs/stack records, including `$08024001/$08024161`, rather than proving additional live objects. The pointer census does not classify every stale stack word as a backend owner. Backend `$20000378` is referenced at wrapper +4; controller at context +0. No alternate owner-release service is established by these aliases.

## Completion and failure closure

PROVEN: `$08022F94` checks bounds and takes its byte semaphore. Busy returns 2 without acquisition; bounds failure returns 1. After `$08037430` returns it releases at `$08022FD4 → $0801BA12`, then returns 0. It has no TEF-status return branch after submission.

PROVEN: `$08037430` clears DMA flags through `$0801C4D4`, sets DMA through `$0801C072`, issues command through `$0803769C → $08022746`, waits through `$08037596`, and disables QSPI DMA requests only after completion. `$08022746` itself waits for BUSY to clear before issue. Its selected read enables TCIE, not TEIE. Its CPU loop has no finite failure counter.

PROVEN: completion wait `$08037596 → current-task callback → $08057650 → $0801BE1A → $0801CDC8` passes timeout **`$FFFFFFFF`**. The subsequent loop requires controller software bit0. Main `$08023FD6` separately yields until wrapper sync clears. Neither is a bounded timeout; 128 replay ticks are an observation window, not firmware milliseconds or an added timeout.

PROVEN: QSPI IRQ `$080573E0 → $08022826` acknowledges TCF/SMF only, setting software completion bits, then `$0805756E → $08057664 → $0801BDE8` signals Storage mask `$100`. A TEF-only injected IRQ can wake Storage but cannot satisfy the completion predicate, so Storage waits again. No error status travels to the request callback.

PROVEN: DMA IRQ `$080573EE` checks DMA2 HISR `$40026404` bit27 (TCIF7) and bit22 (FEIF7), acknowledges those through HIFCR `$4002640C`, then tails `$08022888`, which is `BX LR`. It does not test TEIF7 bit25 or deliver a same-backend error unwind. This DMA FIFO error is distinct from QUADSPI TEF.

PROVEN: initialization `$080373BC → $080226A2/$0801BEB0` sets up the controller/DMA, not the five-resource unwind. NOR init also issues exit/entry/address-mode commands with event waits. Status poll `$080375C0` has another indefinite wait. Backend semaphore wait `$080230F8` does not disable DMA, abort QSPI, empty a request or clear a queue. No inspected path coordinates DMA quiescence, peripheral completion/error clear, notification drainage, request completion and semaphore release after failure. No retry/error-notify service was identified in this closure.

UNKNOWN: exhaustive use of generic peripheral reset/DMA-disable helpers elsewhere. Their existence alone would not establish a safe same-resource unwind; the inspected initializer enables RCC AHB3 clock, not a qualified error reset service. No QSPI CR.ABORT write is observed in any of the six diagnostic fault traces.

## TEF meaning and practical risk

PROVEN: QUADSPI TEF is **peripheral transfer error**, SR `$A0001008` bit0. Its IRQ enable is CR `$A0001000` bit16, and acknowledgement is FCR `$A000100C` bit0. It is neither DMA TEIF7 nor DMA FIFO FEIF7. ST's STM32F7 HAL header identifies TEF with invalid-address access, FTF with FIFO threshold/data remaining, and TOF with memory-mapped timeout. The register identifiers are confirmed by the exact STM32F745 CMSIS header. These are documentation support, not claims that stock uses HAL's error callbacks/timeouts.

- [ST STM32F7 QSPI header, QSPI_FLAG_TE/FT/TO and IRQ definitions](https://raw.githubusercontent.com/STMicroelectronics/stm32f7xx-hal-driver/master/Inc/stm32f7xx_hal_qspi.h)
- [ST STM32F745 register header](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-f7/master/Include/stm32f745xx.h)
- [RM0385 sections 14.3.13/14.3.14, 14.4, 14.5.3/4/13](https://www.st.com/resource/en/reference_manual/rm0385-stm32f75xxx-and-stm32f74xxx-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)

PROVEN: FCR acknowledgement clears a flag; it does not itself cancel DMA, drain callbacks or release the backend. **UNKNOWN:** whether an actual silicon TEF leaves all participants stopped, including DMA/bus transactions. The phase30 injected state deliberately leaves DMA EN set and NDTR64; that is a synthetic failure state, not a silicon post-TEF measurement. It is insufficient to authorize semaphore release even if QSPI happens to have stopped.

PROVEN: selected DCR `$00180000` encodes FSIZE24; eight reads are wholly within configured 32MiB, `$82000–$821FF`, each DLR63. Backend start-address bounds and all eight actual read setups pass. **STRONG INFERENCE:** an address-error TEF is not an expected outcome of this fixed validated request under correct configuration. Normal repeated-read architecture and two exact successful requests establish model behavior, not hardware reliability.

PROVEN: the six observed faults are synthetic injections. Forced TEF-only IRQ invocation is artificial because stock selected TEIE is disabled. Missing completion deliberately withholds TCF/IRQ. **UNKNOWN:** real incidence, hardware error distribution, or probability of lost completion. Exceptional configuration/peripheral/IRQ faults remain possible; no numeric risk or observed-hardware rate is claimed. Missing completion is an availability fault and need not imply a NOR data error.

## Watchdog and reset policies

PROVEN: startup `$0801DA0A → $0801EAF8` configures IWDG `$40003000`: key5555, PR4, RLRFFF, keyCCCC. `$0801EB1E` stores **AAAA**, a feed. Idle loop `$0801CD30`, at `$0801CD4E`, calls `$0801D760 → $0801EB1E`, then WFI at `$0801D766`. No test of Storage progress occurs. Direct/tail feed callers include `$0801D4A6/$0801D562/$0801D762/$0801DA0E/$0801DB48/$0801DBE2/$0801F50A/$08024FFC/$080297D6/$0803CCDE`.

PROVEN in replay: for each stuck request, invoke the actual idle callback 128 times on a physical fixture stack, preserving saved CPU contexts. Each invocation writes only IWDG AAAA among peripheral/system writes and leaves resource state unchanged. WFI wake is explicitly modeled; no scheduler timing or watchdog downcounter is simulated. **STRONG INFERENCE:** normal idle service can keep this watchdog alive during a Storage wait; it cannot be relied on for bounded missing-completion recovery. Deliberately starving feeds would be a new policy and is not implemented.

PROVEN: the AIRCR literal-load census finds `$0801BB50/$0801BB6C/$0801D288/$08039046`. The first two set/read interrupt priority grouping; `$0801D288` compares grouping for an assertion. The reset sequence `$08039042–$0803905A` writes SYSRESETREQ via `$E000ED0C` using key `$05FA0004` and loops. Its enclosing updater path first programs 23-byte staging metadata at `$80000` and waits for backend completion. It is unsuitable for a read-only error exit and may itself be blocked behind Storage. Jumping into the interior reset instructions is not a demonstrated callable stock API or complete reboot qualification.

| Policy | Finding | Confidence |
|---|---|---|
| A — abandon diagnostic, operator reboot later | Smallest containment: host discards incomplete result; no retry; device keeps Main frame, descriptor and buffer quarantined. Do not return Main, reuse parser buffer, clear queue or release semaphore. Selected model makes no persistent writes. Actual safe reboot and background application effects remain unqualified. | PROVEN selected containment; UNKNOWN complete reboot safety |
| B — existing normal application reset | No callable, read-only stock reset API was established. Enclosing known updater writes NOR; interior SYSRESETREQ is not an unwind and would need a separate entry contract/reset qualification. Not accepted as a proven recovery strategy. | PROVEN known path; UNKNOWN safe alternative |
| C — watchdog restart | Stock idle independently feeds IWDG; reset is not guaranteed by a stuck Storage transaction. Not accepted as a bounded recovery strategy. | PROVEN feed path; STRONG INFERENCE scheduling consequence |

PROVEN: phase27 host `receiver.py:WinMMTransport.receive` already has an absolute per-frame receive deadline and raises TimeoutError without automatic retry; `protocol.py:acquire` saves no partial capture. This is a host failure boundary, not a device timeout. **UNKNOWN:** host timeout cannot return device buffer ownership or prove next-boot safety.

## Replay outcome and gates

PROVEN: **44 assertions**, six fault cases plus normal/second-normal control. For every fault: initial reproduction, 128 additional ticks and 128 native idle callbacks; semaphore0, queue0, pending0, sync1, Main not returned, active chunk retained, buffer not reusable. Storage re-enters its native infinite mask100 wait. Notification flags end0. Guards remain intact; all selected QSPI operations are EC reads. No forced completion, release, queue edit, peripheral reset, watchdog starvation or second request over a live transaction is attempted.

| Fault | Data frames | Semaphore | Sync | Second successful read after fault |
|---|---:|---:|---:|---|
| TEF chunk0 / 4 / 7 | 0 / 4 / 7 | 0 | 1 | Not safely admissible; no unwind |
| Missing chunk0 / 4 / 7 | 0 / 4 / 7 | 0 | 1 | Not safely admissible; no unwind |
| Two consecutive normal captures | 9 each, including final completion | 1 | 0 | Exact synthetic reconstruction on both |

PROVEN: **H4 status = FAIL**, specifically its bounded-failure requirement for the six tested fault models. Normal DMA/IRQ/callback behavior remains PROVEN within phase30's model. **UNKNOWN:** an unexamined independent stock recovery service or a qualified safe reboot policy; neither is assumed. H1/H2 are unchanged and were not re-investigated.

UNKNOWN: there is no admitted in-session TEF/missing-completion recovery. A reboot boundary is required before another capture under policy A; that statement is not a proof that any particular reboot is safe. Containment alone therefore does not qualify storage-error recovery or hardware readiness.

UNKNOWN — single smallest next experiment: exercise the **existing host receiver's absolute timeout/no-retry path** with the six truncated synthetic fault streams and a fake MIDI queue/clock. Require bounded host exit, no partial capture file, exactly one sent request, and explicit refusal of a same-session retry. This would qualify host-side containment only; it would neither reset hardware nor close unchanged H1/H2 or device-side H4.

QSPI STORAGE ERROR RECOVERY = UNQUALIFIED
