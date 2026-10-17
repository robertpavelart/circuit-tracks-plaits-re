> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase56 — geometry snapshot lifecycle

**UNKNOWN: lifecycle is UNQUALIFIED.** The geometry shrinks enough to fit existing private capacity, but that capacity's current writers and the complete native startup/remount interlock are not qualified for reuse.

**PROVEN:** the required bounded FAT12/16 scalars encode losslessly into8 bytes;5 saved native-mount round trips,7 rejects and16 factor cases pass. Host can independently reconstruct and check the mapping domains; no device-only yes/no decision replaces the evidence. Unsupported layouts fail closed. A universal information-theoretic minimum is not claimed. [minimal-snapshot-layout.md](<minimal-snapshot-layout.md>), compact-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/compact-tests.json`; not distributed).

**PROVEN:**20044D70..20044D7B is an existing12-byte diagnostic-owned reservation. It has no unused bytes under its old format. Native getter initialization destroys a proposed geometry record, and native SysTick timeout corrupts compact geometry interpreted as legacy ACTIVE state. A proposed4+8 union requires adapting all those owners; the unsafe52-byte extension is not used. [ram-ownership.md](<ram-ownership.md>), [snapshot-liveness.md](<snapshot-liveness.md>), liveness-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/liveness-tests.json`; not distributed).

**PROVEN scoped:** isolated native commit helper tests pass12 mask/generation/flag combinations, two payload stores before validity, DMB,24-byte stack and original mask/supported register/flag preservation. Success16 instructions,10 mask-set entry instructions; full snapshot collection/packing/cycles and physical latency remain UNKNOWN. [async-startup-exclusion.md](<async-startup-exclusion.md>), commit-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/commit-tests.json`; not distributed).

**UNKNOWN:** no complete exclusion of every normal asynchronous producer before snapshot; Storage can service already queued work and PRIMASK cannot undo prior DMA. Full computed geometry-write/remount roots remain open. The census scans the entire exact image and saved initialization/RAM but is not represented as a complete alias theorem. A19A92-only invalidation hook would miss native197A0 slow remounts. [async-startup-exclusion.md](<async-startup-exclusion.md>), [remount-invalidation.md](<remount-invalidation.md>), census.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/census.json`; not distributed).

**PROVEN logical issue:** a safe later remount plus matching token cannot establish that an earlier unsafe epoch preserved82000. The model therefore sets a sticky history flag after a post-initial geometry change. It can export a new VALID current snapshot but refuses raw capture for the rest of that boot.7 lifecycle scenarios and4 orderings pass under explicit all-writers-intercepted/atomic-admission assumptions. [generation-gating.md](<generation-gating.md>), lifecycle-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/lifecycle-tests.json`; not distributed).

**UNKNOWN:** native authorization→queue-submit and ACTIVE→deferred geometry-change interlock; no successful abstract model is promoted into a firmware proof. Identity81000 and coefficients82000 have independent authorization predicates, but both remain disabled pending shared prerequisites.82000 still requires its fixed physical read after admission; mapping evidence is not coefficient evidence. [toctou-review.md](<toctou-review.md>).

|Gate |Result |

|---|---|

|Small independently auditable record |PROVEN8-byte admitted-domain encoding |

|Owned long-lived capacity |PROVEN existing12-byte owner; UNKNOWN new schema liveness |

|No overwrite through export/raw decision |PROVEN naive reuse fails; UNKNOWN redesigned native owner closure |

|Complete asynchronous startup exclusion |UNKNOWN |

|Atomic copy/publication |PROVEN isolated helper; UNKNOWN full source collection/hook/latency |

|All remount/binding invalidators |UNKNOWN completeness |

|Same-boot stale-token rejection |PROVEN conditional model; UNKNOWN native integration |

|Original-byte preservation across past epochs |PROVEN generation-only gap; STRONG INFERENCE sticky-history repair |

|Architecture build admission |UNKNOWN; no candidate build authorized |

**UNKNOWN — smallest next offline experiment:** integrate the proposed12-byte union owners solely in emulator fragments and replay existing getter/retained Master-FX init, SysTick quarantine, geometry export and atomic raw admission with write guards; preserve all old one-shot failure cases. Separately the normal startup queue and every geometry-changing producer must be closed before a final PASS. Do not build a full firmware or use a no-observed-write replay as a reachability proof. [revised-architecture.md](<revised-architecture.md>).

**PROVEN:** nine requested reports, saved test outputs and exact-image listings are present. validation.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/validation.json`; not distributed) verifies earlier evidence/pinned-source preservation and all report links. No hardware/MIDI ports, firmware/SYX output/transmission, historical candidate modification, or revival of the exhausted Phase53 branch occurred.

GEOMETRY SNAPSHOT LIFECYCLE = UNQUALIFIED
