> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Explicit status protocol and host containment

**PROVEN:** new commands retain fixed 232-byte request ownership, geometry `0E`, authorization `0F`, session 1..127 and exact same-epoch geometry echo. No arbitrary address command or storage cleanup/retry command is added.

`F0 7D 43 54 4F session code epoch[8 nibbles] zero[15] CRC[8 nibbles] F7` is exactly 39 bytes. CRC-32/MPEG-2 covers bytes4..29. Epoch=0 for NOT_READY and1 otherwise. The 15 reserved bytes must be zero.

| Code | Meaning / behavior |

|---:|---|

|1 NOT_READY|BOOT, MOUNTING or pre-export recheck; no state publication/raw request. After a complete valid quiet response window, host removes only its query marker and permits another query.|

|2 INVALID|Geometry/lifecycle rejected; no authorization/raw request.|

|3 UNSAFE|Mapping veto; clean stop with no authorization.|

|4 READY|Geometry follows. An unconsumed export may be queried again; session replacement invalidates the old session token.|

|5 FAILED|Fatal attempt; no raw retry, full physical power cycle required.|

|6 AUTHORIZED|Actual successful native authorization ACK, before raw dispatch.|

|7 SUCCESS|Actual terminal native success, after raw completion; host requires both the complete valid data stream and this status.|

**PROVEN:** `[status_emitter.py](<../../../builds/phase63-defect-closure/status_emitter.py>)` emits `status`74100, `classify`74400 and USB-only `status_drain`74700. Drain has a 5000-tick bound independent of FAILED/INVALID record gating. It invokes stock router20C90, which copies into its retained ring; no Storage API is called. Stack reply memory is not the USB hardware destination. Disconnection cannot be answered over a disconnected link.

**PROVEN:** device classification tests exercise all seven codes. READY→AUTHORIZED→SUCCESS packets also execute through actual command dispatch. UNSAFE is explicitly a classifier-state injection test: supported valid compact D4000 mappings cannot overlap these lower fixed targets. No authentic unsafe mounted geometry is claimed. Host additionally applies independent target reachability veto before authorizing.

**PROVEN in mocks:** 32 cases in host-tests.json (local-only reference: `builds/phase63-defect-closure/host-tests.json`; not distributed); malformed CRC/framing, stale session/epoch, duplicates/order/missing completion, disconnect, timeout and partial tails fail without output. Evidence publication remains the inherited all-validated atomic-directory rename. Raw time window10s starts before authorization send; send bound2s; geometry/query window10s. No automatic raw retries. Durably marked uncertain sends remain non-retryable.

**PROVEN in declared model:** if fatal storage ownership never releases, Main deliberately remains in its live frame. It cannot simultaneously send a new status from that blocked Main call. The host's absolute deadline therefore explicitly reports FAILED / DO NOT RETRY / POWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT. Native FAILED packets are sent on quiescent failure exits or processable status queries; this does not promise an outbound packet from an unrecoverably blocked/disconnected task.

**PROVEN:** initial 24-byte status integration failed in stock router/copy execution (`20D5A`); saved status24-coupled-counterexample.json (local-only reference: `builds/phase63-defect-closure/status24-coupled-counterexample.json`; not distributed). Its hardware cause is **UNKNOWN**. That encoding was rejected. Current 39-byte framing follows the already exercised geometry reply length and passes coupled router/USB execution. This does not classify the 24-byte fault as firmware-independent emulator behavior.

Host: [live_host.py](<../../../builds/phase63-defect-closure/live_host.py>); pure parser [status_protocol.py](<../../../builds/phase63-defect-closure/status_protocol.py>); deterministic mocks [host_tests.py](<../../../builds/phase63-defect-closure/host_tests.py>). CLI remains locked by UNQUALIFIED preflight; no MIDI inventory operation was run.
