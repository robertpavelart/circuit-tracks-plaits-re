"""Append phase31 result without altering earlier report text."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
p=R/'notes/qspi82000-hardware-readiness.md'
prior=(O/'phase30-report-before.md').read_bytes()
assert hashlib.sha256(prior).hexdigest()==json.loads((R/'builds/phase30-chunked-storage/validation.json').read_text())['report_sha256']
section='''

## Phase31 — storage error recovery

**PROVEN:** the phase30 architecture and buffer are unchanged. This section supersedes phase30's H4 admission status only: **H4 = FAIL**, because bounded failure is part of that gate and fails in all six tested fault models. Normal completion remains proven within the offline model. H1/H2 are unchanged and were not re-investigated. No hardware, firmware, IRQ ownership or reference-source changes occur.

Full address-level findings, callers, completion/error closure and policy comparison are in [phase31 findings](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase31-storage-error-recovery/findings.md>). Machine evidence: [stock-path-audit.json](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase31-storage-error-recovery/stock-path-audit.json>), [fault-replay.json](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase31-storage-error-recovery/fault-replay.json>), and [validation.json](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase31-storage-error-recovery/validation.json>). The unchanged phase30 report is archived alongside them.

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
'''
current=p.read_bytes()
assert current==prior or current==prior+section.encode('utf8')
p.write_bytes(prior+section.encode('utf8'))
print('Appended phase31; phase30 text preserved byte for byte')
