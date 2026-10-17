# Final documentation audit — final pre-hardware review

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

17 October 2026 (Europe/Moscow). Documentation/state cleanup only: no reverse engineering, experimental runner, firmware build, host/uploader execution, hardware access, MIDI access or transmission. No live lock was changed. Candidate firmware is a temporary NOR diagnostic, not Plaits; it has not been hardware-tested. Phase67 FINAL PREFLIGHT CLOSURE = PASS remains scoped model evidence.

## Files updated

- [README.md](<../README.md>)
- [HARDWARE_TEST_PREFLIGHT.txt](<operations/HARDWARE_TEST_PREFLIGHT.txt>)
- HASHES.txt (local-only reference: `builds/final-hardware-test-package/HASHES.txt`; not distributed)
- README.txt (local-only reference: `builds/final-hardware-test-package/README.txt`; not distributed)
- [final-cheap-checks.md](<research/final-hardware-test-package/final-cheap-checks.md>)
- [CLAUDE_REVIEW_PACKAGE.md](<CLAUDE_REVIEW_PACKAGE.md>)
- [CLAUDE_REVIEW_PROMPT.md](<CLAUDE_REVIEW_PROMPT.md>)
- [CURRENT_STATUS.md](<CURRENT_STATUS.md>)
- [DOCUMENTATION_INDEX.md](<DOCUMENTATION_INDEX.md>)
- [FINAL_DOCUMENTATION_AUDIT.md](<FINAL_DOCUMENTATION_AUDIT.md>)
- [FINAL_PREFLASH_REVIEW.md](<FINAL_PREFLASH_REVIEW.md>)
- [HANDOFF.md](<HANDOFF.md>)
- [HARDWARE_TEST_PREFLIGHT.txt](<HARDWARE_TEST_PREFLIGHT.txt>)
- [MEMORY_AND_RESOURCE_STATUS.md](<MEMORY_AND_RESOURCE_STATUS.md>)
- [NEXT_STEPS.md](<NEXT_STEPS.md>)
- [PLAITS_RESEARCH_STATE.md](<PLAITS_RESEARCH_STATE.md>)
- [PROJECT_OVERVIEW.md](<PROJECT_OVERVIEW.md>)
- [RESEARCH_TIMELINE.md](<RESEARCH_TIMELINE.md>)
- [REVERSE_ENGINEERING_STATE.md](<REVERSE_ENGINEERING_STATE.md>)
- [SNAPSHOT_CONSISTENCY_AUDIT.md](<SNAPSHOT_CONSISTENCY_AUDIT.md>)
- [fixed-nor-evidence-diagnostic.md](<../notes/fixed-nor-evidence-diagnostic.md>)
- [qspi82000-hardware-readiness.md](<../notes/qspi82000-hardware-readiness.md>)

Documentation-only helpers: [update_final_state_docs.py](<../tools/update_final_state_docs.py>) and [audit_final_state_docs.py](<../tools/audit_final_state_docs.py>). Evidence/state receipts are under final-pre-hardware-documentation (local-only reference: `builds/final-pre-hardware-documentation`; not distributed); preserved before-copies are explicitly historical / SUPERSEDED, not a second current state. Historical note bodies and the original cheap-check audit body are retained beneath current/supersession notices. The old readiness note's legacy byte encoding is preserved with its historical body.

## Files left unchanged

Exact candidate SYX/BIN in both Phase63 and package, both rollback SYXs, live_host.py, uploader HTML, transport/codecs, operational-gate.json, recovery-status.txt and all other package content except README.txt, final-cheap-checks.md, HARDWARE_TEST_PREFLIGHT.txt and their HASHES.txt digests. All other historical phase evidence, runners, reference/pinned sources, firmware and Plaits PoCs remain unchanged by this task. No evidence was deleted. The earlier circuit-tracks-plaits-re source snapshot remains historical; its README/status/roadmap are not current release authority.

## Stale references found and contradictions resolved

- Root landing page and current overview/review/index/audit pages previously led with Phase67 PASS as current authority and hardware/model-only risk. They now retain that scoped result while naming the later allocation SOFTWARE UNKNOWN and operational UNQUALIFIED.
- HANDOFF/CURRENT_STATUS/NEXT_STEPS previously carried two competing status layers and listed both cheap-check gaps unresolved. They now record USB joint-path PASS (36 cases), with only the allocation proof open.
- Review prompts treated independent review as pending. The user-reported favorable Claude conclusion and accepted soft-brick/recovery risk are recorded; a separately reviewed operational release is next. No external review or message was initiated.
- Recovery entry/exit is now expressly user-reported physical evidence with no rehearsal transmission. Enumeration, handshake, both recovery flashes and non-booting-candidate recovery remain unproven; recovery is not guaranteed.
- Frozen package README/checklist and original cheap-check decision were stale. Current notices/checklist/README are corrected; the original audit remains historical. Package HASHES.txt was updated for documentation only.
- Memory/Plaits pages retain numerical/design evidence but no longer imply diagnostic PASS qualifies final resources. Authentic82000 is missing; P0282-0386 and final P/X/Y remain unqualified/UNKNOWN.
- Old hashes were searched across repository documentation. Preserved phase reports/source snapshots are historical evidence, not eligible candidates; current-page occurrences appear only in the historical table below. Machine inventory: stale-references.json. No historical evidence was rewritten to erase a prior result.

## HISTORICAL / FAILED / SUPERSEDED identities — DO NOT FLASH

All entries below are historical / SUPERSEDED, not current candidates. Phase61 and original Phase62 specifically FAILED later qualification. Keeping their hashes prevents accidental substitution.

| Historical evidence directory | Superseded artifact | Historical SHA-256 |
|---|---|---|
| phase43-hardware-test-candidate | `circuittracks-4486-nor-evidence-test.bin` | `9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6` |
| phase43-hardware-test-candidate | `circuittracks-4486-nor-evidence-test.syx` | `59be0e5733c70783c278ff5f89e575d77eef4dd3f6389841eac4a488111df32b` |
| phase44-preflash-redteam-closure | `circuittracks-4486-nor-evidence-atomic-test.bin` | `0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738` |
| phase44-preflash-redteam-closure | `circuittracks-4486-nor-evidence-atomic-test.syx` | `1fc80908552cd1901e52559cf8117e9fbf5c878b258c79c6cdea2572ceb031af` |
| phase61-final-geometry-gated-candidate | `circuittracks-final-geometry-gated-nor-test.bin` | `af5b62e371c1f9e6972b573e766088e54da6fadfcba911e62f25bd0edb0c763f` |
| phase61-final-geometry-gated-candidate | `circuittracks-final-geometry-gated-nor-test.syx` | `fe36e18bc83448b0e25cc21b8323e0e64e153f6e04abc042546f4a20e83731d3` |
| phase62-final-preflight | `circuittracks-geometry-gated-nor-reservation-fix-unqualified.bin` | `7d3964aabbba6e7dfe0cfa8b95b89294346bbeac49fcb20dd529609d6d507cd6` |
| phase62-final-preflight | `circuittracks-geometry-gated-nor-reservation-fix-unqualified.syx` | `a73366ca6e9457018f71f153fb4e0815cebf69e491e487654dfaa5d2f5c75b32` |

## Current candidate identity

Phase63 N63DEV: SYX 569229 bytes, SHA-256 `9b420521a366c65c13fb871778fdbab612ca126cbb4ad60d0fd5bc12ecd253da`; BIN 413952 bytes, SHA-256 `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9`. CRC-32/MPEG-2 `1BB21302`; application `0x08010000..0x08075100` end-exclusive. CRC is referenced from saved identity evidence, not a newly run decoder/build. Full rollback/tool identities: [CURRENT_STATUS.md](<CURRENT_STATUS.md>).

## Current preflight status and next step

No concrete offline firmware blocker demonstrated. Accepted residual SOFTWARE uncertainty: unresolved post-READY indirect/virtual allocation reachability, especially 0803C91C/0803C9C4 and registry/object methods, with 8 bytes modeled gap. No actual >8-byte post-READY allocation found; absence NOT proven. Allocator rejection reaches BKPT; artificially continuing returns FFFFFFFF accepted by generic wrapper; physical routing UNKNOWN. USB joint path PASS is preserved within its 36-case declared scope, not physical proof.

Reported independent review: REASONABLE TO PROCEED WITH CONTROLLED HARDWARE TEST, subject to accepted residual risk. User accepts possible soft brick requiring recovery provided bootloader remains accessible; this does not guarantee recovery, close the census or authorize hardware. Next: separately reviewed operational-release preparation/new tool hashes, actual-machine hash verification and Windows/MSD policy, then an explicitly authorized controlled test. Geometry first, host validation of82000 safety, exact epoch/session authorization, one fixed capture, restore B1.3 on success. H4 remains FAILED (H4 = FAIL): discard/no retry/no second diagnostic or Storage request/full physical power OFF/USB unplugged/end session.

## Verification and Git hygiene

Read-only artifact hashing confirms candidate/rollback/tool identities and all 633 package manifest entries. Only four package documentation/manifest files changed; recovery-status.txt retains SHA-256 `169f295e37fc8b39d51ec5e38a54d2d341d52cd7b2bca7b8d762ff6ff019008d`. No old test suite was rerun. The machine audit records internal links, status assertions, stale hash inventory, exact preserved hashes and changed files in audit.json (local-only reference: `builds/final-pre-hardware-documentation/audit.json`; not distributed).

Earlier saved hash receipts describe their own packaging snapshots; the updated package HASHES.txt controls current documentation bytes. Candidate/tool/rollback identities and the saved experiment results were not changed by documentation supersession.

Verification results: **231 local link occurrences, zero broken**, across 15 current pages and 3 current notices; **633 package manifest entries verified**; 22 old-hash occurrences classified as historical, zero current eligible historical candidates. Current status-language assertions and exact candidate/rollback/tool reference checks pass. These are documentation/hash checks, not new firmware or hardware experiments.

Neither the project root nor the earlier source snapshot contains Git metadata in this working copy. No staging/commit/push occurred and no history was rewritten. Existing snapshot .gitignore already excludes Python caches, editor artifacts and generated builds/binaries; it was left unchanged. No root .gitignore was added without a Git checkout. Do not stage historical/proprietary artifacts or documentation-before copies indiscriminately when preparing a future commit. Documentation helpers ran with Python -B.

## Proposed commit — not executed

`docs: update project state through final pre-hardware review`

- document Phase63 identity and Phase61/62 supersession;
- record actual defect closures and Phase64-67 scoped modeling;
- record final USB joint-path PASS and unresolved allocation proof;
- reconcile rollback/recovery/locked-tool status and accepted soft-brick risk;
- clarify separately reviewed release preparation and future controlled-test sequence.

REPOSITORY STATE = CURRENT THROUGH FINAL PRE-HARDWARE REVIEW
