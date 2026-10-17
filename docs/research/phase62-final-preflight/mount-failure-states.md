> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Mount / geometry protocol gate — FAIL

New exact-image native queries cover BOOT0, MOUNTING16, INVALID1D, FAILED15 and VALID11. BOOT/MOUNTING/INVALID/FAILED all emit **zero response packets**, preserve the record and submit no raw read. VALID returns the39-byte geometry response and moves to EXPORTED with session binding.

Thus the actual device protocol cannot distinguish NOT_READY, INVALID and FAILED to a host: they are identical silence. A timeout cannot truthfully be labeled NOT_READY. The host mock suite preserves this mismatch; it does not manufacture status packets that the frozen firmware cannot send. Lack of raw authorization means no raw-capture attempt is made, but the already-sent geometry session's durable marker remains and ambiguous silence isPOST_SEND failure, requiring power cycling. This does **not** satisfy a distinct successful NOT_READY response/nonburning-status workflow.

First successful mount/compact geometry is covered by current startup; first mount failure/nonqualifying geometry takes the existing terminal1D path, with no valid snapshot. Reservation-absent behavior is the already-passed7-case gate, not rerun. Retained28 native cases cover invalid geometry, remount/invalidation, wrong epoch and malformed authorization. The new continuity trace reveals a separate erroneous invalidation by the ordinary SD mount. A host cannot repair that by assuming silence means valid or overwriting state.

UNSAFE is a local host veto, not a permission to raw-read. AUTHORIZED is inferred only after a validated raw reply, not from an invented device ACK; authorization transmission itself is labeledAUTHORIZATION_SENT. FAILED cannot currently be queried as a distinct device reply. The successful compactD4000 format maps above the two target ranges; the mock unsafe case injects a policy veto and is not claimed as a native unsafe-volume discovery.

Required closure is a real, testable no-raw-read status response contract plus NOR-specific mount ownership, followed by fresh corrected-image qualification. Neither change was smuggled into the frozen image. Evidence: mount-state-protocol-tests.json (local-only reference: `builds/phase62-final-preflight/mount-state-protocol-tests.json`; not distributed), [resume_checks.py](<../../../builds/phase62-final-preflight/resume_checks.py>), continuity-startup-frontier.json (local-only reference: `builds/phase62-final-preflight/continuity-startup-frontier.json`; not distributed), live-host-tests.json (local-only reference: `builds/phase62-final-preflight/live-host-tests.json`; not distributed).
