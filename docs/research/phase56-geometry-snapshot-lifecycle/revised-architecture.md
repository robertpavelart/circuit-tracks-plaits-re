> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase56 — proposed minimal architecture and decision

**STRONG INFERENCE — retain optionA:** canonical geometry8 bytes + control4 within the existing12-byte private diagnostic capacity. This avoids the unqualified52-byte extension and does not use heap tail, stack, parser, DMA, filesystem scratch or audio state. The owned capacity is real; its new lifecycle is not yet qualified.

BOOT: reserve the existing12-byte private record before mount without an allocator call; initialize EMPTY. During the first normalized NOR mount transaction, verify binding/source status, gather canonical fields, compare generation and commit VALID last at the established successful-mount boundary. Retain all stock Main/Storage ownership and original mount exactly once.

HOST STEP1: fixed geometry-only request; read retained bytes only, no Storage/NOR/filesystem API. Return exact compact fields, validity/history/generation, protocol/code version and checked framing. Host independently reconstructs domains and evaluates each fixed target.

HOST STEP2: explicit target mask/current-session/generation/record-digest authorization. Device atomically checks admissibility, marks ACTIVE, overlays geometry payload with raw bookkeeping and issues only the requested fixed read(s). No arbitrary address, automatic capture or retry. Every remount/binding changer must invalidate before mutation and lose against ACTIVE admission safely.

|Cost |Phase55 proposal |Phase56 proposal / proof limit |

|---|---|---|

|Geometry payload |46 |8 bytes, tested bounded FAT12/16 scalar encoding |

|Simple geometry+state |52 additional bytes |12-byte union replacing an existing12-byte owner;0 additional reservation proposed |

|New heap allocation |0 but capacity reduction52 |0; early reservation of existing capacity/liveness UNKNOWN |

|Site hook |4-byte mount-call replacement |Same site plus all lifecycle/legacy-owner adaptations; total code UNKNOWN |

|Atomic helper |Not emitted |46 emulator-only ARM bytes;16 success instructions,24-byte temporary stack; not a complete hook |

|Added NOR for geometry |0 |0 |

|Raw H4 |Retained after host gate |Retained; old failure containment must survive union redesign |

|Remount safety |Epoch interlock missing |Abstract interlock and sticky history model tested; native coverage/interlock UNKNOWN |

**PROVEN:** this phase produces documentation, scans, pure models and one isolated emulator commit helper, never a firmware image/SYX. No existing candidate is modified. **UNKNOWN:** total pack/collect/wrapper code size/cycles/latency; the helper's exact counts must not be presented as full integration cost.

**UNKNOWN — architecture remains unqualified.** Concrete progress is the8-byte representation, a12-byte owned-capacity strategy, two reproduced native liveness collisions, a bounded commit helper and a corrected history-aware gate model. Remaining requirements are all-native owner replacement/liveness, early reservation timing, startup producer/queue exclusion, complete geometry-writer interception and real admission/defer behavior. Only after those close may a later phase build a candidate; this phase does not authorize that build.
