> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase57 — reset-to-terminal12-byte liveness

**PROVEN:** initialized data ends20003D02; scatter zero span20003D04,20006A54) does not touchD70. Therefore the private record has no automatic fresh-reset clear in those records; warm-entry SRAM residue cannot be trusted. Constructor iteration5B958 is an identified place to reserve/initialize before constructors without extending capacity. This is not yet an executed adapter. [ownership.json (local-only reference: `builds/phase57-first-mount-provenance/ownership.json`; not distributed), app-0805b590.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0805b590.asm`; not distributed), app-0805b958.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0805b958.asm`; not distributed), app-0801a7ea.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0801a7ea.asm`; not distributed).

|Lifetime stage |Permitted intended writes / existing conflicts |

|---|---|

|Reset/scatter |Native named ranges do not touch record. New one-time init must setBOOT once after allocator initialization; location/timing is proposed, not fully qualified. |

|Constructors/heap growth |Early limitD70 must protect region. Existing allocator traps above limit; all-constructor demand/aliases remain UNKNOWN. No new allocation. |

|First mount |Control→MOUNTING/epoch1; payload two words;VALID last. Any unexpected earlier root must quarantine; no accepted late first-use fallback. |

|Normal startup/USB-ready |Adapted lazy getter must not clear record; SysTick must ignore nonACTIVE geometry union. Existing native bodies violate these requirements, as saved collision tests prove. |

|Geometry export |Payload read only; control may changeVALID→EXPORTED. No Storage work and no parser ownership transfer of retained bytes. |

|Host authorization |Compare exact retained record/epoch/session; only then overlay8 payload bytes with raw transaction bookkeeping. |

|Raw read/reply |Existing session/chunk/owner/start-tick semantics move into the documented raw union; target mask occupies first payload byte. Source buffer itself remains separately owned by existing raw path. |

|Success |Conditional ACTIVE→SUCCESS only after output completion; ownerfree only if actually released. |

|Failure/timeout |FAILED absorbs late success and duplicate commands; keep active read ownership; no forced release/cleanup/retry. |

**PROVEN model:**13 cases show these logical transitions fit exactly12 bytes without hidden persistent model fields for epochs/state; `limit` denotes the already-existing allocator metadata, and `submits` is test observation, not proposed RAM. Event interception and atomicity are modeled assumptions. [first_epoch_model.py](<../../../builds/phase57-first-mount-provenance/first_epoch_model.py>), epoch-model-tests.json (local-only reference: `builds/phase57-first-mount-provenance/epoch-model-tests.json`; not distributed).

**UNKNOWN complete liveness:** direct owner references are enumerated in ownership.json (local-only reference: `builds/phase57-first-mount-provenance/ownership.json`; not distributed); indirect computed writes, all range-based clears, task/IRQ high-water and all DMA setup lifetimes have not been closed from reset through raw completion. Known Main/Storage stacks do not intersectD70 in prior fixtures, which does not prove every boot stack/DMA range. No fixture-only no-write result is offered as complete ownership proof.

**PROVEN:** old native getters/watch/admission/terminal logic still uses the historical schema. Historical native regression results remain valid because those bytes are unchanged; they cannot certify the unimplemented new coalesced owner adapters. A conceptual model passing does not satisfy the requested complete native liveness gate.
