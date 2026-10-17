> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase56 — asynchronous startup and copy atomicity

**UNKNOWN:** no complete proof that all normal concurrent execution cannot initiate persistence between native mount success and snapshot completion. Phase55's1AE06 Main instruction window is retained; it is not promoted to scheduler exclusion.

|Context |Authenticated evidence / unresolved predicate |

|---|---|

|Scheduler |Application kernel/current-TCB is live before Main mounting; captured Main TCB2000835C, Storage20009244. Bootloader SVC/PendSV/SysTick evidence is preserved but does not supply application ready queues at1AE06. Exact ready set/priorities at that point UNKNOWN. |

|Higher-priority tasks/UI |Native Main/UI/Storage/IDLE name candidates are present; one UI name is stale boot evidence. No standalone USB task can be inferred from a missing string. Actual preemption eligibility UNKNOWN. |

|Storage |5767C drains SD worker24014 at576A6 and NOR at576B0, then waits. A pending program/erase operation can execute if present; wrapper return does not attest that every other queue is empty. Normal pre-mount producer/queue closure UNKNOWN, not a claim a write occurred. |

|USB |Native IRQ/ring/TX plumbing can run asynchronously. Main parser work and normal write protection are reused; complete startup USB queue/callback predicates at mount UNKNOWN. |

|SysTick |5998C→6B748 includes the proven record-writing timeout hook. It is not a filesystem producer in the reviewed path, but breaks naive retention. |

|DMA IRQs |573E0→22826 QSPI completion and573EE DMA service notify/drain state. Selected IRQs do not themselves call file write; already active peripheral writes would not be stopped by a later PRIMASK mask. |

|Timers/deferred work |248CE schedules150-tick callback248B4→38C54; known body changes USB mode/class. SC35D8 persist19 resync is RAM/DSP. All deferred stock content producer predicates are not closed. |

Sources: census.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/census.json`; not distributed), app-0805767c.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-0805767c.asm`; not distributed), app-080573e0.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-080573e0.asm`; not distributed), app-08059970.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-08059970.asm`; not distributed), app-080248b4.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-080248b4.asm`; not distributed), app-08038c54.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-08038c54.asm`; not distributed), [findings.md](<../phase37-systick/findings.md>), [background-write-analysis.md](<../phase45-nor-mutation-closure/background-write-analysis.md>).

**PROVEN conditional capability:** queued op2/3 in native worker24014 reaches backend program/erase. **UNKNOWN:** a normal producer has queued such an operation before initial mount's copy. Neither “a queue could contain a write” nor “one model queue is empty” decides the required normal-boot reachability question. No invented simultaneous writer is presented as a measured failure.

## Native atomic commit microexperiment

**PROVEN scoped:** a46-byte isolated Thumb helper is assembled/executed only inside emulator memory; no image/SYX/patch is produced. Inputs:r0=private record pointer,r1/r2=already encoded payload,r3=expected INVALID generation/control. It preserves r0–r12, SP, supported APSR flags and prior PRIMASK; saves24 stack bytes. It saves flags/mask, masks interrupts, compares current control, writes two payload words, executes DMB, and writes VALID control **last**. A changed generation skips publication. [commit_probe.py](<../../../builds/phase56-geometry-snapshot-lifecycle/commit_probe.py>), commit-helper.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/commit-helper.asm`; not distributed), commit-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/commit-tests.json`; not distributed).

**PROVEN:**12 cases cover PRIMASK0/1, matching/mismatching generation and three supported flag patterns. Adjacent word canaries survive. Matching path16 instructions total,10 entered while a newly set mask is active; mismatch10 total,4 entered masked. The0x500F0000 input flag pattern reads back with GE bits unsupported by this emulator; physical GE preservation is not separately proved. The helper emits APSR_nzcvqg restoration but tests certify only modeled supported flags.

**STRONG INFERENCE estimate:** a no-stall one-instruction-per-cycle accounting gives16 instruction slots for success,10 of them masked, plus branch/load/store/stack/barrier stalls; it is an illustrative approximation, **not** modeled silicon cycles or a safe-latency bound. Actual M7 issue/cache/bus/DMB latency and forbidden IRQ-latency thresholds remain UNKNOWN. Source collection/packing and original caller wrapper add code/time/stack not measured here. Those totals must not be mislabeled a16-instruction complete snapshot.

**UNKNOWN:** the helper does not close the whole mount-success-to-source-read window. Its packed input could already be incoherent unless every geometry writer invalidates before mutation and generation is checked across collection. It masks only conditional copy+publication (plus the compare/control operations), never a wait or filesystem call. No short mask can cancel earlier in-flight NOR DMA. NMI/fault/reset are not masked and abort successful acquisition rather than being silently certified. Full snapshot packing/ownership/latency and asynchronous exclusion remain unqualified.
