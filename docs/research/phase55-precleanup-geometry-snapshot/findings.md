> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase55 — pre-cleanup geometry snapshot

**UNKNOWN: architecture remains UNQUALIFIED.** A precise native mount boundary and sufficient compact record are established. Safe fixed retention and a complete startup/lifetime interlock are not.

**PROVEN YES — synchronous instruction window:** NOR f_mount returns at0801AE06 with complete geometry before the enclosing1F0A8 finishes and before Main calls settings/content construction at0801D4C4. The full mount clears stale type, parses geometry, commits ID/synchronization state and returns0 on success. **UNKNOWN:** a universal no-prior-asynchronous-persistence claim across every boot root; the scoped Main order is not mislabeled full RTOS closure. [mount-to-persistence-ordering.md](<mount-to-persistence-ordering.md>).

**PROVEN:** eight native mount tests pass, including stale/failed mounts, not-ready media, different layout, mount-ID wrap and the NOR-then-SD constructor. Nine offline supplied-record host tests pass. Model disk completions/logging and provenance predicates are explicit; no current-unit filesystem bytes or full cold boot were acquired. mount-cases.json (local-only reference: `builds/phase55-precleanup-geometry-snapshot/mount-cases.json`; not distributed), host-gate-cases.json (local-only reference: `builds/phase55-precleanup-geometry-snapshot/host-gate-cases.json`; not distributed).

**PROVEN:** the46-byte record consists of three spans, not a contiguous structure. It captures the fields native filesystem mappings actually use; fresh successful mount/binding provenance can supply current-unit authority without another physical READ(10). A mount ID of0 is valid after wrap and is not sufficient failure evidence. **STRONG INFERENCE:** the proposed capture contract supplies authoritative mounted-state geometry when correctly implemented on the unit. [geometry-record.md](<geometry-record.md>), [geometry-authenticity.md](<geometry-authenticity.md>).

**UNKNOWN:** no47/52-byte fixed retention location is qualified. Extending the current reservation by52 places its boundary at20044D3C,44 bytes below the fixture cursor20044D68. Historical diagnostic log buffers belong to live Master-FX LEDs. No parser/stack/DMA/filesystem scratch or unproved RAM hole is borrowed. [snapshot-ram-liveness.md](<snapshot-ram-liveness.md>).

**STRONG INFERENCE:** use a4-byte replacement of the mount call at1AE02, preserving the existing call exactly once and copying after its success. Do not patch through the1AE06 IT block naively. Exact added bytes/cycles/stack and fixed RAM remain UNKNOWN until a concrete hook is emitted and verified; none is emitted now. [snapshot-hook.md](<snapshot-hook.md>).

**PROVEN conditional:** stable validated geometry bounds later normal writes even after cleanup changes files, allowing a same-boot argument. **UNKNOWN unconditional:** remount/rebinding/stride/reset invalidation and raw-admission epoch enforcement are not implemented. Geometry export must never submit Storage or automatically trigger raw capture.81000 identity-specific uncertainty is separate from82000 coefficient preservation. Architecture C is recommended conditionally; later raw capture retains H4/no-retry containment. [host-gating.md](<host-gating.md>), [architecture-comparison.md](<architecture-comparison.md>).

|Gate |Result |

|---|---|

|Precise native fresh mount success window |PROVEN YES, synchronous Main path |

|All normal boot tasks cannot persist before acquisition |UNKNOWN complete queue/root exclusion |

|Record suffices for native mapping bounds |PROVEN fields/arithmetic; STRONG INFERENCE actual-unit hook contract |

|Small fixed RAM ownership through USB export |UNKNOWN |

|Read-only geometry export |STRONG INFERENCE design,0 added Storage requests; not implemented |

|Same-boot admission after geometry |PROVEN conditional geometry theorem; UNKNOWN epoch interlock |

|Actual-unit82000 preservation |UNKNOWN until qualified acquisition/host gate, independent of identity-only concern |

**UNKNOWN — smallest next experiment:** qualify one named small retention reservation (at least52 bytes for the simple aligned record, more if retaining epoch/CRC), including constructor allocation and retained LED/Master-FX/USB liveness. The trivial heap-top extension fails the existing fixture. In parallel conceptually, the identified mount site still requires bounded startup queue exclusion and lifecycle invalidation; no new engine port, firmware build or hardware action is authorized.

**PROVEN:** all eight requested reports and saved tests are in this directory. validation.json (local-only reference: `builds/phase55-precleanup-geometry-snapshot/validation.json`; not distributed) checks prior Phase54 preservation, pinned sources, exact-image equality and report links. Earlier suites and Phase53's exhausted authentication branch were not rerun. No firmware generation/modification, SYX, candidate designation, hardware access, MIDI enumeration/opening or transmission occurred.

PRECLEANUP GEOMETRY SNAPSHOT = UNQUALIFIED
