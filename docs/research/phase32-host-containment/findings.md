> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase32 — one-shot host failure containment

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

| A complete normal stream | SUCCESS | 5.000 | Yes, synthetic512 | 1 | PROVEN |

| B truncated after completed chunk 0 | FAILED | 5.000 | No | 1 | PROVEN |

| C truncated after completed chunk 4 | FAILED | 5.000 | No | 1 | PROVEN |

| D truncated after completed chunk 7 | FAILED | 5.000 | No | 1 | PROVEN |

| E synthetic TEF indication at chunk 0 | FAILED | 0.100 | No | 1 | PROVEN |

| F synthetic TEF indication at chunk 4 | FAILED | 0.500 | No | 1 | PROVEN |

| G synthetic TEF indication at chunk 7 | FAILED | 0.800 | No | 1 | PROVEN |

| H corrupted packet CRC | FAILED | 0.400 | No | 1 | PROVEN |

| I duplicate chunk | FAILED | 0.400 | No | 1 | PROVEN |

| J missing chunk | FAILED | 0.500 | No | 1 | PROVEN |

| K reordered chunk | FAILED | 0.300 | No | 1 | PROVEN |

| L duplicate completion packet | FAILED | 1.000 | No | 1 | PROVEN |

| M completion before all chunks | FAILED | 0.500 | No | 1 | PROVEN |

| N total silence | FAILED | 5.000 | No | 1 | PROVEN |

| whole capture CRC incorrect | FAILED | 0.900 | No | 1 | PROVEN |

| completion missing | FAILED | 5.000 | No | 1 | PROVEN |

| wrong token | FAILED | 0.100 | No | 1 | PROVEN |

| partial trailing SysEx after valid completion | FAILED | 5.000 | No | 1 | PROVEN |

| actual TEF is silent at failed chunk 0 | FAILED | 5.000 | No | 1 | PROVEN |

| actual TEF is silent at failed chunk 4 | FAILED | 5.000 | No | 1 | PROVEN |

| actual TEF is silent at failed chunk 7 | FAILED | 5.000 | No | 1 | PROVEN |

| wrong absolute address with valid packet CRC | FAILED | 0.100 | No | 1 | PROVEN |

| wrong total size with valid packet CRC | FAILED | 0.100 | No | 1 | PROVEN |

| 63-byte chunk with valid CRC | FAILED | 0.100 | No | 1 | PROVEN |

| absolute deadline despite trickle | FAILED | 5.000 | No | 1 | PROVEN |

| fragmented valid stream | SUCCESS | 5.000 | Yes, synthetic512 | 1 | PROVEN |

| coalesced valid stream | SUCCESS | 5.000 | Yes, synthetic512 | 1 | PROVEN |

| coalesced duplicate completion | FAILED | 0.100 | No | 1 | PROVEN |

| late duplicate completion inside deadline | FAILED | 4.990 | No | 1 | PROVEN |

| partial frame total silence thereafter | FAILED | 5.000 | No | 1 | PROVEN |

PROVEN: **265 assertions**, 30 stream scenario groups (24 primary/extended cases plus trickle and five framing/timing cases), and two additional filesystem checks pass. Exactly the complete valid512-byte stream, in its three transport encodings, produces a final file. Failed sessions accept no digest, retain no reconstruction and suppress reuse. No automatic retry or storage cleanup command occurs. A duplicate completion arriving at4.99s is rejected; trickled packets cannot extend the5s deadline.

UNKNOWN: a finite observation window cannot establish that no unrelated/duplicate byte could ever arrive afterward. Acceptance is defined over the single bounded session; the lease is consumed on success as well as failure, so no subsequent attempt can interpret later bytes through this session. Real transport close/ingress scheduling and device performance are not qualified offline.

PROVEN: host failure containment passes its selected offline policy. **Device H4 remains FAIL for in-session recovery**; no semaphore release, request cancellation, safe reboot proof or second device read after failure is added. The device is treated as quarantined until a full power cycle. H1/H2 and every other hardware admission gate remain unchanged. STRONG INFERENCE: this wrapper is a suitable host policy boundary for a future separately authorized integration. UNKNOWN: live hardware qualification.

QSPI HOST FAILURE CONTAINMENT = PASS
