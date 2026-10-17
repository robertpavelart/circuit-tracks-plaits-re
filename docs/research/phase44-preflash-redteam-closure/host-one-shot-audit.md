> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: SUPERSEDED / DO NOT FLASH.

# Phase44 host one-shot audit

PROVEN — The Phase43 tool burned `NOR-CAPTURE-ATTEMPT.json` before MIDI port selection/open. A missing/ambiguous/busy port therefore wrongly consumed the attempt and printed a power-cycle requirement despite sending no diagnostic request. This behavior is corrected in Phase44 copies only; the existing Phase43 package and candidate are unchanged.

## Implementation and authority

- [capture_nor_evidence.py](<../../../builds/phase44-preflash-redteam-closure/capture_nor_evidence.py>): `run_capture`, its nested `commit`, `OneShot.run(before_send=...)`, and `main`.

- [ctremote_transport.py](<../../../builds/phase44-preflash-redteam-closure/ctremote_transport.py>): lazy `_api`, `ports`, exception-safe `Link.__init__`, and idempotent `Link.close`.

- host-source-identities.json (local-only reference: `builds/phase44-preflash-redteam-closure/host-source-identities.json`; not distributed) identifies the copied Phase43 inputs and modified Phase44 outputs.

PROVEN — PRE-SEND validation checks prior marker and destination, selects exactly one matching input/output, opens and prepares the link, then reaches a durable exclusive marker commit immediately before `transport.send(request(37))`. No-match, ambiguous name, capability-query error, input/output open error, input-buffer setup error, and input-start error create no permanent marker, transmit zero requests, and report `CAPTURE NOT SENT` / `NO DEVICE POWER CYCLE REQUIRED BY THIS ATTEMPT`. Existing-output failure is also pre-send. A fresh local attempt following such a failure has not consumed the device session.

PROVEN — The marker is created with exclusive mode, flushed and fsynced before the first send can begin. A process that loses the exclusive-create race does not remove the winner's marker, sends nothing, closes its own link, and conservatively reports the previously consumed session. An owned incomplete marker is removed if persistence fails before sending. There is no retry/rearm/reset command. The marker is intentionally retained after successful capture as well as post-send failure.

PROVEN — Once send can begin, output submission/driver errors are classified conservatively as POST-SEND, including ambiguous delivery. Marker remains burned, request count is at most one, partial reconstruction is discarded, and failure prints `CAPTURE FAILED`, `DO NOT RETRY`, `FULL POWER CYCLE REQUIRED`. `midiOutPrepareHeader` failure inside `send` also burns the marker conservatively: the boundary is entry to sending, not a claim that every send failure physically emitted bytes.

PROVEN — `ports` is a new CLI subcommand that calls only input/output inventory APIs. Import loads no WinMM DLL and opens no ports; `_api` loads WinMM only on explicit live inventory/capture invocation. No live CLI was invoked in this phase. Its tests use an injected mock WinMM object and inspect every recorded API call. Listing opens no ports and sends zero MIDI/SysEx bytes in the tested implementation.

PROVEN — Port initialization checks input prepare/add/start return codes and calls cleanup on partial initialization failure. Input-open failure allocates no successful handles; output-open failure closes input; later initialization failure tears down both handles and prepared buffers. Close is idempotent. Driver-owned buffers are retained if unprepare fails; the existing pending-output retention behavior remains. Reset/close APIs affect host resources and issue no diagnostic/storage command.

## Regression evidence

PROVEN — capture-tool-tests.json (local-only reference: `builds/phase44-preflash-redteam-closure/capture-tool-tests.json`; not distributed): all 25 inherited applicable host cases pass. These cover full valid 535-byte capture (23 + 512), silence/TEF-like truncation, missing/duplicate/reordered chunks, duplicate/early completion, session/address/checksum errors, disconnect, send timeout, truncated final frame, atomic publication error, existing output, initialization error, and four mock WinMM send cases. Only the valid stream publishes exactly the two expected files. All request-bearing cases send one request; repeat attempts are blocked before Link construction.

PROVEN — host-presend-tests.json (local-only reference: `builds/phase44-preflash-redteam-closure/host-presend-tests.json`; not distributed): all 17 additional cases pass: mocked listing; no match; ambiguous input/output; capability-query/input-open/output-open/prepare/add/start failures; idempotent successful cleanup; marker-before-send ordering; exclusive marker race; marker-fsync failure; ambiguous send failure; existing-output prevalidation. These assert zero requests/no marker/no power-cycle requirement for pre-send failures, resource cleanup, winner-marker preservation, and durable marker visibility inside the send mock.

The inherited suite changes only the expected pre-send classifications for existing destination and link initialization. No malformed-stream test was removed or skipped. Both suites run under `python -B`, use fake clocks, temporary directories, and mock driver APIs. No actual WinMM module loaded, port enumeration/open, USB/MIDI traffic, firmware generation, hardware access, or candidate modification occurred.

## Boundaries and remaining unknowns

UNKNOWN — Physical WinMM/USB driver behavior, close refusal, disconnect latency, filesystem power-loss durability, and externally confirmed full power cycle are not proven by mocks. Cleanup API calls are proven; a driver cannot be forced to release a handle successfully. Retained failed-unprepare buffers avoid premature deallocation. External removal/bypass of the attempt marker or use of another package is outside the tool's enforcement boundary. A process crash during marker creation may leave a conservative unusable marker despite no request; no automatic deletion or rearm is provided.

PROVEN — The 5-second whole-capture deadline, full completion validation/tail observation, atomic publication of both final files, exact names/lengths/checksums, and no post-send retry policy remain unchanged. H4 remains FAIL: this host fix does not unwind device Storage/semaphore state and does not alter firmware. It is a Phase44 host revision, not a claim that the archived Phase43 host tool already contained this correction.
