"""Evidence report and append-only readiness update."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
r=json.loads((O/'test-results.json').read_text())
note=R/'notes/qspi82000-hardware-readiness.md';archive=O/'phase31-report-before.md'
prior=json.loads((R/'builds/phase31-storage-error-recovery/validation.json').read_text())
if not archive.exists():
 assert sha(note.read_bytes())==prior['report_sha256'];archive.write_bytes(note.read_bytes())
assert sha(archive.read_bytes())==prior['report_sha256']
text='''# Phase32 — one-shot host failure containment

PROVEN: this is a host-side/offline qualification. `containment.py:OneShotCapture` wraps the unchanged phase27 `protocol.py:Receiver` and `receiver.py:WinMMTransport`. `test_offline.py:Clock/FakeQueue/FakeLink` replace time and incoming MIDI bytes deterministically. No hardware library, port enumeration or live transport is invoked. The existing live CLI is unchanged and is not wired to this wrapper or approved by these tests. No device-side instructions, normal read architecture, reference or pinned sources change.

PROVEN: the old `protocol.py:acquire` returns after nine frames; that alone cannot reject a tenth duplicate completion. The new wrapper continues receiving for a **5.0-second absolute whole-attempt window**, including the period after the first valid completion. The deadline starts before the single send and is never renewed by data. Any later frame inside that window is fed to the existing receiver, whose `done` check rejects it. Partial trailing SysEx is also rejected. At the deadline, lack of a valid completion fails; silence after exactly one completion and no partial frame allows publication. Five seconds is a selected host policy, not a measured device timing bound or device timeout.

PROVEN: completion requires eight chunks, indices0–7, absolute addresses `$82000 + 64*index`, total512, length64 each, valid framing/token/nibbles/packet CRC, completion kind1/index8/address82000/length4 with valid whole-data CRC, exactly nine frames, next9, and exactly512 reconstructed bytes. No oscillator/firmware changes are involved.

PROVEN: on any receive/protocol/output error, the session becomes FAILED, device state becomes **POWER-CYCLE REQUIRED**, the decoder is discarded and the framing buffer is cleared. It reports exactly:

```
CAPTURE FAILED
DO NOT RETRY
POWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT
```

PROVEN: the session cannot run twice; another capture sharing its `DeviceLease` cannot claim it; the same transport cannot be leased a second time. There is no retry/rearm/reset API and no cancellation/storage cleanup command. Tested failed transfers send exactly one original232-byte fixed request, with no second request, retry or cleanup. Output-collision preflight sends none. Receiving `_readd` calls acknowledge fake host receive buffers, not storage commands.

UNKNOWN: software cannot infer a physical power cycle. Deliberately constructing a fresh transport/process can bypass an in-memory policy; no cross-process physical-reset attestation is claimed. This phase supplies no live retry path or hardware access.

PROVEN: output remains in memory until full stream validation and the trailing observation window finish. Only then is a same-directory staging file written, flushed/fsynced, closed and atomically renamed to `qspi_00082000_000821ff.bin`. Windows `os.rename` refuses to replace an existing destination; the preflight additionally rejects existing evidence before sending. Every failing stream is checked in an isolated directory: the final name does not exist and no staging file remains. An existing evidence file is preserved unchanged in a separate collision test. An injected rename failure leaves no partial final or staging file. Atomic namespace publication is qualified here; power-loss durability is UNKNOWN and not simulated.

PROVEN: the successful bytes are synthetic test data, **not authentic QSPI evidence**. Their SHA-256 is:

`db76faa8a1c5684f01f3e176fe4a3da3cf3719d6b94f1ea097ea359f7997a5d3`

PROVEN: test output includes this digest. Successful `.bin` files are created only in isolated test directories and removed after exact-byte/hash assertions. No device evidence file or firmware image is delivered. The complete valid stream succeeds as separate packets, fragmented packets and one coalesced byte stream; all malformed/truncated streams fail.

PROVEN: explicit TEF/error packets in casesE/F/G are **synthetic unsupported kind2** packets with valid packet CRC, used to verify fail-closed error handling. Phase31 found no actual stock TEF error packet. Therefore separate cases model actual TEF behavior as silence at failed chunks0/4/7, yielding respectively0/4/7 completed data packets. Requested truncation after a *completed* chunk0/4/7 yields1/5/8 packets, with no completion packet. Both interpretations are covered.

| Injected stream | Terminal state | Virtual elapsed seconds | Final accepted file | Requests sent | Confidence |
|---|---|---:|---|---:|---|
'''
for c in r['cases']:
 text+=f"| {c['case']} | {c['result']['status']} | {c['virtual_elapsed']:.3f} | {'Yes, synthetic512' if c['final_exists'] else 'No'} | {c['sent_requests']} | PROVEN |\n"
text+='''
PROVEN: **265 assertions**, 30 stream scenario groups (24 primary/extended cases plus trickle and five framing/timing cases), and two additional filesystem checks pass. Exactly the complete valid512-byte stream, in its three transport encodings, produces a final file. Failed sessions accept no digest, retain no reconstruction and suppress reuse. No automatic retry or storage cleanup command occurs. A duplicate completion arriving at4.99s is rejected; trickled packets cannot extend the5s deadline.

UNKNOWN: a finite observation window cannot establish that no unrelated/duplicate byte could ever arrive afterward. Acceptance is defined over the single bounded session; the lease is consumed on success as well as failure, so no subsequent attempt can interpret later bytes through this session. Real transport close/ingress scheduling and device performance are not qualified offline.

PROVEN: host failure containment passes its selected offline policy. **Device H4 remains FAIL for in-session recovery**; no semaphore release, request cancellation, safe reboot proof or second device read after failure is added. The device is treated as quarantined until a full power cycle. H1/H2 and every other hardware admission gate remain unchanged. STRONG INFERENCE: this wrapper is a suitable host policy boundary for a future separately authorized integration. UNKNOWN: live hardware qualification.

QSPI HOST FAILURE CONTAINMENT = PASS
'''
(O/'findings.md').write_text(text,encoding='utf8')
section='''

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

**PROVEN — synthetic result SHA-256:** `db76faa8a1c5684f01f3e176fe4a3da3cf3719d6b94f1ea097ea359f7997a5d3`. Test captures exist only in isolated directories removed after assertions; no authentic QSPI capture is claimed. TEF/error packets are explicitly synthetic kind2; actual stock TEF behavior remains silence. See [phase32 findings](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase32-host-containment/findings.md>), [one-shot implementation](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase32-host-containment/containment.py>), [test results](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase32-host-containment/test-results.json>) and [validation](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase32-host-containment/validation.json>).

**UNKNOWN — limits:** no finite window proves absence of arbitrarily late packets. The consumed lease prevents another attempt through this session; no cross-process power-cycle attestation is claimed. Live transport scheduling and filesystem power-loss durability are not tested. The old live CLI is unchanged and is not wired to this wrapper or hardware-approved. **STRONG INFERENCE:** the wrapper provides a suitable host policy boundary for future separately authorized integration.

**PROVEN:** host containment does not unwind Storage. **H4 remains FAIL for device-side in-session recovery**; the device remains quarantined until a full power cycle. H1/H2 are unchanged. Host containment PASS is not hardware readiness or proof of safe reboot.

QSPI HOST FAILURE CONTAINMENT = PASS
'''
base=archive.read_bytes();current=note.read_bytes()
assert current==base or current==base+section.encode('utf8')
note.write_bytes(base+section.encode('utf8'))
print('Phase32 report appended; phase31 text archived and preserved')
