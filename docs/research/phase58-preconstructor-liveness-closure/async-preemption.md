> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase58 — preemption before validity

**PROVEN:**5B958 runs before application1D3C8 creates/starts its scheduler tasks. No Content/Storage task executes *through the synchronous constructor dispatcher*. Its helper functions perform no MMIO access in all3 native cases, hence do not submit DMA or Storage work themselves. This closes the constructor-specific uncertainty; it does not assert a complete architectural IRQ scheduler replay.

|Source |Exact entry/work |What is established / open |

|---|---|---|

|SysTick |5998C→6B748 watch→599B8;59992 counter update |PROVEN old watch can write private status when legacyACTIVE; later owner adaptation required. Early postscatter limitE58 makes watch reject unreserved state; early publication still requires ordered initialization. |

|Scheduler |1DE78→1CABC/startup; eventual task context switches |UNKNOWN full application ready set, priority/queue ordering at mount; earlier bootloader SVC/PendSV models are not substituted |

|Storage |5767C→24014 worker, op2 program/op3 erase |Can service an existing queued write; UNKNOWN normal early producer predicates |

|Content |22ACC→22AE4; enqueues22A5C |Constructor queue366E0 initializes empty; subsequent normal pre-mount producers not closed |

|UI |1D680→1E4BE/209E4, changed-state path1C894 |Exact entry identified; all callback clients before Main mount not transitive-closed |

|USB |IRQ/ring/Main dispatcher1EB30, output20C90 |Normal WRITE10 protection reused; no inferred standalone USB task from name absence; full pre-ready callback roots UNKNOWN |

|QSPI/DMA IRQs |573E0→22826;573EE→22888/notification |Reviewed handlers signal/completion, not direct file writes. They do not prove an earlier DMA operation absent. |

|Timers |248CE150 ticks→248B4→38C54; service1E4BE |Known USB mode/class work; full deferred predicate closure UNKNOWN |

|Constructor58344 |584C4 initializes fields, including clearing callback+18 |PROVEN no timer registration/call here; the prior constructor-specific deferred uncertainty is removed |

Sources: [async-startup-exclusion.md](<../phase56-geometry-snapshot-lifecycle/async-startup-exclusion.md>), [async-exclusion.md](<../phase57-first-mount-provenance/async-exclusion.md>), app-080584c4.asm (local-only reference: `builds/phase58-preconstructor-liveness-closure/app-080584c4.asm`; not distributed), constructor-cases.json (local-only reference: `builds/phase58-preconstructor-liveness-closure/constructor-cases.json`; not distributed).

**UNKNOWN:** no proof excludes every asynchronous82000 mutation before snapshot. No actual such mutation is demonstrated. A short PRIMASK region around publication cannot undo a previously queued or in-flight write or certify earlier epochs. Exact physical latency/forbidden interrupt budget are unqualified. The existing12-case isolated commit proof remains valid for its own register/flag/mask/publish-last contract, but is not rerun or used as whole-history evidence. commit-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/commit-tests.json`; not distributed).

No IRQs or device tasks are run on hardware, and no peripheral success state is inserted to hide the new clock frontier or old authentic NOR boundary.
