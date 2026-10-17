> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase57 — asynchronous exclusion

**PROVEN:** application startup creates Main/UI/Storage/Content before enabling normal scheduling. Main begins1D4B0; UI1D680 services1E4BE/209E4; Storage5767C drains wrappers24014; Content22ACC waits and drains22AE4. Queue constructor366E0 stores read/write indices0. Exact ready/priorities/queued callbacks when Main reaches1AE06 remain UNKNOWN. A running-RAM snapshot is not the mount-time scheduler state. app-0801dd80.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0801dd80.asm`; not distributed), app-0801d680.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0801d680.asm`; not distributed), app-08022a0c.asm (local-only reference: `builds/phase57-first-mount-provenance/app-08022a0c.asm`; not distributed), app-080366e0.asm (local-only reference: `builds/phase57-first-mount-provenance/app-080366e0.asm`; not distributed).

|Context |A: pre-snapshot evidence mutation |B:12-byte overwrite |C: remount/invalidate before commit |

|---|---|---|---|

|Storage |UNKNOWN normal queued write producers; capability22FDC/23078 is known |No selected intentional private-record writer; complete DMA/alias closure UNKNOWN |Pending file jobs can call197A0 slow mount; pre-snapshot presence UNKNOWN |

|Content |Queue initially empty by native code; complete producer ordering after construction UNKNOWN |No direct private-record owner in reviewed worker |22AE4 content file paths can trigger lazy mount |

|UI/Main callbacks |Main cleanup is later; earlier UI dispatch transitive closure UNKNOWN |Shared getter can run from retained feature paths |Computed callback/lifecycle roots not fully closed |

|SysTick |Reviewed watch does no NOR/file write |PROVEN old6B794 private status write; needs new control adapter |No direct mount call in reviewed watch; total scheduler consequences UNKNOWN |

|USB service/IRQs |Normal WRITE10 protection reused; full pre-ready normal callback closure UNKNOWN |PROVEN explicit diagnostic admission/raw writers after accepted command; no authorization before geometry in proposed contract |Deferred mode callback reviewed; class teardown aliases not fully closed |

|DMA/QSPI IRQs |Reviewed handlers complete existing I/O, not file API producers; in-flight write before hook not excluded by masking |No selected intended payload overlap withD70; every initial DMA range not globally proved |Controller notifications can schedule queued work |

|Timers/deferred work |Known150-tick USB-mode callback; SC35D8 resync RAM/DSP |Known timeout owner remains live |Other native callback root predicates UNKNOWN |

**UNKNOWN — can any concurrent normal execution mutate a target before the snapshot?** No actual such write was established; complete queue/root exclusion is missing. **PROVEN:** current timeout/getter owners can overwrite new data unless adapted. **UNKNOWN:** complete native pre-commit invalidation interlock. These three questions have distinct statuses.

**PROVEN scoped reused atomicity:** Phase56 isolated commit helper success uses16 instructions,10 mask-set entry instructions,24-byte stack and DMB before validity;12 tests preserve supported registers/flags and incoming PRIMASK. This helper excludes a short publication race, not all earlier initialization/packing/preexisting DMA. It is reused as evidence, not rerun or installed. commit-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/commit-tests.json`; not distributed).

**UNKNOWN:** exact physical latency, forbidden interrupt budget and all-task pending work at mount. A bounded critical section is insufficient if a target write was already active or an earlier filesystem epoch already existed. No interrupts are disabled on hardware, and no unqualified short mask is asserted to close the global provenance requirement.
