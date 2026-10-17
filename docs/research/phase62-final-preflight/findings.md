> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Resumed Phase62 — frozen corrected candidate REJECTED for preflight

**FINAL PREFLIGHT CLOSURE = FAIL. DO NOT FLASH.** The earlier reservation fix remains qualified in its narrow scope. This continuation did not restart/repeat the7 reservation cases or28 native suite and did not alter either candidate. Required new tests found further concrete failures, so the corrected image cannot be promoted.

## Frozen identity

| Frozen corrected artifact — NOT QUALIFIED | Bytes | SHA-256 |

|---|---:|---|

| circuittracks-geometry-gated-nor-reservation-fix-unqualified.syx | raw instruction bytes omitted | `a73366ca6e9457018f71f153fb4e0815cebf69e491e487654dfaa5d2f5c75b32` |

| circuittracks-geometry-gated-nor-reservation-fix-unqualified.bin | raw instruction bytes omitted | `7d3964aabbba6e7dfe0cfa8b95b89294346bbeac49fcb20dd529609d6d507cd6` |

CRC-32/MPEG-2 **BF2E8F22**; application base08010000/end-exclusive08075100; image headroom44800 bytes; compared-header markerN62RSV. These are image bounds, not hardware RAM margin.

Original Phase61 remains permanently **SUPERSEDED / FAILED RESERVATION TEST / DO NOT FLASH**. Its original bytes/evidence remain unchanged; all112 Phase61 manifest entries still verify. The corrected image is **UNQUALIFIED UNTIL PREFLIGHT COMPLETES**, and this run has failed required gates. No future-final designation is made.

## REAL BLOCKERS REMAINING

1. **PROVEN in native startup:** shared mount_begin also handles SDFS20001B04 and invalidates the already committed NOR record at0806CF26. Snapshot`110000000180003480908F01` becomes`1D0000000180003480908F01`. This is an owner predicate defect; it cannot be repaired by a host fixture. Later native drive0 remounts also require interpretation without disabling the intended invalidation policy.

2. **PROVEN native protocol failure:** NOT_READY0/16, INVALID1D and FAILED15 queries emit identical silence. The required distinguishable status/nonburning readiness contract is absent. Host code cannot truthfully decode a nonexistent response.

3. **Requested unconditional stack-DMA invariant fails an explicit countermodel:** with TCF delivered before DMA.EN/NDTR are cleared, native Main returnsSUCCESS while DMA.EN=1,NDTR=64 and destination remains the former stack raw buffer. Physical occurrence of that ordering is UNKNOWN; normal tests assumed it away. Need a valid completion-order proof or explicit software ownership enforcement, not an asserted hardware-safe unwind.

4. Final live workflow cannot qualify until those firmware/continuity contracts are resolved. A real locked Windows utility and25 mock assertions now exist, but the candidate cannot satisfy its required status path. Pinned rollback files/uploader are provisioned; the reference uploader does not allowlist this failing candidate, and no candidate-update uploader is admitted.

## Completed independent checks

- New corrected-image native startup continued beyond the snapshot without substituting RAM/register state; it exposed the SD-owner defect. Full USB-ready→export→auth→raw continuity is **not** claimed. The1,104,592-instruction bound stops in the native continuation; this is a model frontier, not proof of a real hardware hang.

-15 new stack/DMA cases pass under their declared normal/late-completion model. New independent ordering probe falsifies the broader software invariant; these results are deliberately reported separately.

- Native scatter/constructor tests show FAILED/SUCCESS are reset and authorization cleared at each normal initialized boot. Warm reset can rearm the lifecycle; full physical power cycle remains mandatory by H4, enforced operationally by durable host markers rather than by a RAM power-cycle detector.

- New allocator boundary/exhaustion tests establish nonoverflow bounds andBKPT failure. CursorD68 is traced to the reference running-RAM dump, not the current unit. Full postboot/hardware headroom is not promoted from that fixture.

- Exact B1.3→corrected, corrected→official4486 and corrected→B1.3 replays all pass: exact installed images, no no-op, untouched bootloader, no option-byte operations and zero target write/erase overlaps. Actual B1.3 staging instructions and actual RAM selector at20003CC8 are authenticated; a code-window/table metadata labeling error is explicitly corrected/disclosed.

- Rollback SYXs and exact reference uploader are locally pinned. Official Novation-origin acquisition authentication remainsUNKNOWN; local matching hashes are not invented origin proof.

- Windows MSD risk, host timeout/attempt semantics and recovery evidence limits are documented without a device/port inquiry. Help/import/fake transport only; no live listing/open/send was run.

## CHEAP CHECKS / FIXES REMAINING

Correct NOR-only mount ownership and define native status responses, then use a **new identity** and rerun affected integration/continuity tests. Resolve the DMA lifetime ordering gate without forced unsafe cleanup; rerun adversarial ownership cases. Complete the actual startup→USB-ready seam with declared event models, all milestone records and final postboot allocation/path coverage. Bind the eventual passing hash to a reviewed uploader; qualify the live host against actual device responses rather than silence mocks. These are specific failed/unclosed gates, not permission to restart broad reverse engineering or repeat already-passed arithmetic/ports.

## HARDWARE-ONLY UNKNOWNS

Real boot/timing/USB/Storage/DMA behavior, actual geometry/data and RAM margin, hardware faults and exact-candidate rollback remain untested. The adversarial TCF ordering is not asserted as a hardware fact. Software/protocol failures above are **not** hidden in this category.

## CONTROLLED RISKS

H4FAIL remains: partial evidence rejected, no host retry/second diagnostic command, no second Storage attempt after an observed read failure, no forced semaphore/DMA cleanup, and full physical power removal after failed/uncertain capture. Multiple chunks within the single authorized capture are not host retry requests. A software/watchdog reset or new host process is not a power-cycle substitute. Unexpected MSD exposure is a stop condition; avoid filesystem mounting and use the scoped Windows policy described inwindows-msd-risk.md. Recovery entry/exit is only user-reported; handshake/rollback flashing are not tested.

## Package / documentation disposition

All requested focused report topics are recorded in this directory, with failures and remaining limits explicit. Prior stop-point reports are preserved undercheckpoint-before-resume-report. Global Phase61-withdrawal documentation is left unchanged as instructed: corrected-candidate checks have not all completed successfully, so no final designation/update of the4 current handoff pages is made. Existing withdrawal banners still prohibit both images. No firmware architecture or candidate byte was changed in this continuation.

Evidence: [startup-coupled-continuity.md](<startup-coupled-continuity.md>), [final-stack-audit.md](<final-stack-audit.md>), [heap-reservation-audit.md](<heap-reservation-audit.md>), [b13-updater-confirmation.md](<b13-updater-confirmation.md>), [windows-msd-risk.md](<windows-msd-risk.md>), [reset-state.md](<reset-state.md>), [timeout-ordering.md](<timeout-ordering.md>), [mount-failure-states.md](<mount-failure-states.md>), [live-host-tests.md](<live-host-tests.md>), [rollback-manifest.md](<rollback-manifest.md>), preflight-verdict.json (local-only reference: `builds/phase62-final-preflight/preflight-verdict.json`; not distributed).

FINAL PREFLIGHT CLOSURE = FAIL
