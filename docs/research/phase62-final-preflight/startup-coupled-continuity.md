> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Corrected startup→coupled continuity — FAIL

The frozen corrected image was installed **before** any startup instruction. Native scatter/constructor reservation, scheduler/task execution and first mount ran in one live Unicorn instance. No running-RAM or exported-geometry fixture was substituted into this continuity test. The prior prepared-fixture coupled replay is used only for separate stack tests, never to close this gate.

| Milestone | Actual12-byte record / result |

|---|---|

| Before constructor reservation | Reinitialized to`000000000000000000000000` by native init; reset/heap suite records allocator ordering |

| First snapshot committed at0801AE14 |`110000000180003480908F01`|

| Next normal SD mount begins |`1D0000000180003480908F01` — invalidated by0806CF26|

| USB-ready input-service boundary | NOT REACHED in bounded continuation; no fabricated record |

| Geometry export | NOT REQUESTED through an invented ready fixture |

| Authorization | NOT PERMITTED/NOT EXECUTED in this continuity run |

| Raw capture start | NOT REACHED; no raw request is substituted |

**PROVEN implementation defect:** shared call site0801AE02 invokes mount_begin08075014 for both NORFS20000AB0 and SDFS20001B04. begin0806CF00 does not filter itsR0 filesystem argument: after NOR commitsVALID11, the SD mount takes its nonzero-control path and writes1D at0806CF26. This is the **first** invalidation in the trace, before later modeled drive0 remounts. It does not require guessing physical timing. Normal SD handling is not a new NOR mount epoch, so the NOR diagnostic gate is incorrectly invalidated by an unrelated filesystem. Required correction is a scoped NOR-owner predicate, not disabling remount invalidation generally.

Later drive0 re-registration/slow mount/invalidation also occurs under the synthetic incomplete filesystem model; that needs separate interpretation after fixing the first definite SD-owner error. It must not be silently ignored to forceVALID.

The second bounded native continuation executes1104592 instructions and stops at0x8036348 (native instruction limit or ordinary return). The original10000 aggregate-PC visit guard stopped inside a bounded byte-clear loop224A8; that initial attempt is preserved undercontinuity-initial-attempt. Only that finite-loop guard was relaxed; no readiness or success state was manufactured. The later instruction frontier is a **model completion limit**, not proof of a hardware hang.

`continuity-frontier-sram.bin` and selected registers/model events are persisted. The emulator retains its exact live RAM/registers throughout each run, but no successful startup-to-coupled handoff is claimed and the disk snapshot is not claimed to contain a serializable complete peripheral/scheduler model. All inherited JEDEC/BPB/clock/SD/completion seams are explicit in the runner and event log.

Evidence: [startup_continuity.py](<../../../builds/phase62-final-preflight/startup_continuity.py>), continuity-status.json (local-only reference: `builds/phase62-final-preflight/continuity-status.json`; not distributed), continuity-startup-frontier.json (local-only reference: `builds/phase62-final-preflight/continuity-startup-frontier.json`; not distributed), continuity-frontier-sram.bin (local-only reference: `builds/phase62-final-preflight/continuity-frontier-sram.bin`; not distributed). Candidate unchanged.
