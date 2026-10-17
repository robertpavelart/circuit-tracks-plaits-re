> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase58 —12-byte liveness scope

**PROVEN new closure through constructors:** initialized data/BSS do not overlap20044D70..20044D7B; native constructors with normal/poisoned RAM and early existing-capacity reservation produce0 narrow-range write intents, even same-value stores. Their11 native allocation ranges remain below20007750 and stack minimum2004FF78, far from private storage. Their synchronous path emits no DMA setup/MMIO, so no constructor-owned DMA targets that record. constructor-cases.json (local-only reference: `builds/phase58-preconstructor-liveness-closure/constructor-cases.json`; not distributed), constructor-cfg.json (local-only reference: `builds/phase58-preconstructor-liveness-closure/constructor-cfg.json`; not distributed).

**PROVEN limited continuation:** private marker survives new native postconstructor prefix through1B266. This does not cover task creation, USB-ready, geometry export or raw completion. startup-frontier.json (local-only reference: `builds/phase58-preconstructor-liveness-closure/startup-frontier.json`; not distributed).

|Writer class |Exact evidence / unresolved lifetime |

|---|---|

|Scatter zero/memcpy |Native zero[20003D04,20006A54), decoded initialized[20000000,20003D02), both excludeD70. Constructor RAM writes/allocations and stack ranges enumerated in JSON. |

|Heap |Allocator1D7D0/1D7D8 honors[20002B44]; earlyD70 constructor case fits. Full later allocation demand/aliases under early reservation UNKNOWN. No extra capacity reserved. |

|Old getter |6B708/+4 clear,6B70A/+8 clear,6B714 magic; later read6B722. These must not run against valid geometry unadapted. |

|Old timeout/ISR |SysTick→6B748 writes+4 at6B794; no unused byte can be borrowed without changing that schema. |

|Old Main/SysEx |Admission6B820/+4,6B824/+5,6B830/+8; raw6B8DA/+6,6B8DE/6B924/6BA02/+7; failure6B9FE/+4 |

|Old terminal |Corrected6BC46 writesSUCCESS at+4; legacy6B9EC is bypassed and must not be counted as live |

|Range memset/memcpy after constructors |UNKNOWN complete all-application indirect range closure; no future native lifecycle implementation tested |

|Task/IRQ stacks and DMA after scheduler |Known prior fixture bounds do not overlap; full boot/high-water/all-controller descriptor census UNKNOWN |

Original per-byte writer/reader inventory is preserved in ownership.json (local-only reference: `builds/phase57-first-mount-provenance/ownership.json`; not distributed), not rerun. Existing native collisions are preserved in liveness-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/liveness-tests.json`; not distributed): getter initialization clears the new record and timeout can corrupt compact geometry if old schema remains.

**UNKNOWN complete liveness through authorization:** a new native getter/watch/admission/raw/terminal adaptation has not been implemented or replayed. The SAFE constructor result removes one stage, not these proven later owner conflicts. Full no-overwrite proof cannot be inferred from the preconstructor marker tests or the unchanged historical native regressions.
