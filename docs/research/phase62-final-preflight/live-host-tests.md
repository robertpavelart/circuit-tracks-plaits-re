> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Runnable Windows host and mock validation

`live_host.py` implements non-sending list, geometry-only and one-shot fixed capture commands using a byte-identical copy of the previously qualified WinMM transport. Imports/help do not load WinMM; live list is never invoked here. Live geometry/capture is locked unless preflight-verdict.json isPASS. It remains **NOT QUALIFIED** because this image fails startup/status/lifetime gates. No CLI bypass flag is exposed.

The injected backend/core has25 passing mock assertions: port ambiguity/open/preparation failures send0 and create no marker; transmitted attempts retain their marker on failure and block another launch before touching ports. Epoch/CRC/order/duplicate/length checks use the existing independent codec. Reconstructed files are published via one atomic directory rename only after a complete receiver and full EOS boundary. The pinned transport sends actual Windows SysEx only when a future qualified live command is explicitly invoked; none was invoked.

| Mock | Messages attempted | Raw authorization attempted | Result |

|---|---:|---|---|

|no-device|0|False|FAILED_PRE_SEND|

|ambiguous-device|0|False|FAILED_PRE_SEND|

|open-failure|0|False|FAILED_PRE_SEND|

|timeout-before-send|0|False|FAILED_PRE_SEND|

|timeout-after-send|1|False|FAILED_POST_SEND|

|malformed-geometry|1|False|FAILED_POST_SEND|

|stale-epoch|1|False|FAILED_POST_SEND|

|geometry-policy-unsafe|1|False|UNSAFE|

|safe-geometry-only-stop|1|False|GEOMETRY_SAFE|

|safe-full-capture|2|True|SUCCESS|

|duplicate-packet|2|True|FAILED_POST_SEND|

|missing-packet|2|True|FAILED_POST_SEND|

|out-of-order|2|True|FAILED_POST_SEND|

|duplicate-completion|2|True|FAILED_POST_SEND|

|MIDI-disconnect|1|False|FAILED_POST_SEND|

|USB-input-disconnect|2|True|FAILED_POST_SEND|

|end-boundary-premature-timeout|2|True|FAILED_POST_SEND|

|end-boundary-trailing-partial|2|True|FAILED_POST_SEND|

|authorization-driver-timeout|2|True|FAILED_POST_SEND|

|malformed-authorization-rejected-no-reply|2|True|FAILED_POST_SEND|

|optional-identity|2|True|SUCCESS|

|actual-device-NOT_READY-is-silence|1|False|FAILED_POST_SEND|

|actual-device-INVALID-is-silence|1|False|FAILED_POST_SEND|

|actual-device-FAILED-is-silence|1|False|FAILED_POST_SEND|

|unqualified-CLI-core-lock|0|False|FAILED_PRE_SEND|

Important scope: the3 NOT_READY/INVALID/FAILED cases deliberately reproduce actual device silence and yieldFAILED_POST_SEND. Those are successful **fail-closed host assertions**, not a passing protocol-state distinction gate. The malformed-auth mock models no reply after rejection, while native malformed authorization rejection is supplied by the retained28-case test. The unsafe mock injects a policy veto; it is not a new unsafe native geometry result. The second-launch marker check is executed after every transmitting case. No actual ports were listed/opened.

This is a real CLI implementation with a safety lock, not a qualified final live workflow. Evidence: [live_host.py](<../../../builds/phase62-final-preflight/live_host.py>), [live_host_tests.py](<../../../builds/phase62-final-preflight/live_host_tests.py>), live-host-tests.json (local-only reference: `builds/phase62-final-preflight/live-host-tests.json`; not distributed), [ctremote_transport.py](<../../../builds/phase62-final-preflight/ctremote_transport.py>). Its actual required device-status branch remains impossible to qualify against the frozen protocol. No alternate invented on-wire status format is accepted.
