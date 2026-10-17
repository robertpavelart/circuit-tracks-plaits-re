> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase54 — retention RAM ownership

**UNKNOWN:** no fixed535-byte retention area is qualified. Neither a single dump nor absence of observed writes supplies a lifetime/ownership contract. This phase chooses no destination address.

| Candidate | Known owner/lifetime | Decision |

|---|---|---|

|20006868..2000687E |Stock application identity cache,23 bytes; byte14 immediately zeroed; later identity edits can change it |PROVEN unsuitable for original23-byte retention without a new protection scheme |

|2000546C..20005482 |Bootloader identity cache |UNKNOWN survival through application scatter/BSS/constructors; not reserved across images |

|[20006A00], captured20005148..20005347 |DSP table staging; pointer copied from[2000327C] at1F55A/55E; reused in35E28 descriptor loop |PROVEN lifetime shorter than required; not retention |

|Phase44 latch20044D70..20044D7B |12-byte explicitly reserved one-shot state |PROVEN owned by old diagnostic; not535 free bytes |

|Master FX20044D7C..20044E57 |220-byte retained SC35D8 state |PROVEN live feature, not available |

|Heap below20044D70 |Captured cursor20044D68 leaves8 bytes in corrected diagnostic fixture |PROVEN insufficient in that fixture; UNKNOWN fresh-boot occupancy; no heap allocation allowed here |

|B1.3 heap-top variant20044D6C..20044E57 |Later236-byte feature reservation, different image/version |PROVEN not transferable as unused SC35D8 RAM |

|Main/Storage stacks; top-SRAM exception area |Task/IRQ storage and nesting |PROVEN excluded by requirements; measured margins do not grant ownership |

|MSD/DMA/parser buffers, including40024000 |Live protocol/DMA temporary memory |PROVEN excluded by requirements; cannot retain through arbitrary later activity |

|Other apparent BSS/alignment holes, two separate fixed buffers |No complete static/runtime writer exclusion or lifetime reservation exists |UNKNOWN, not safe based on a dump |

Evidence: [stock-read-lifetimes.md](<stock-read-lifetimes.md>), [heap-stack-status.md](<../phase45-nor-mutation-closure/heap-stack-status.md>), [findings.md](<../phase42-exact-rdiag-integration/findings.md>), [qspi82000-hardware-readiness.md](<../../../notes/qspi82000-hardware-readiness.md>). Later B1.3 lazy-state facts are shown only to prevent cross-image reuse, not assumed inherited by the diagnostic.

**PROVEN arithmetic:** extending the existing heap-top reservation down by540 bytes would place its lower edge at20044B54 (20044D70−21C). Captured cursor20044D68 is already above that proposed boundary. Reserving early would remove capacity consumed later; it does not make the existing allocation demand disappear. Even saving only byte14 plus retaining the other22 identity-cache bytes would require protection against later identity edits, and would still leave the512-byte table-retention problem. It is not an accepted optimization.

**STRONG INFERENCE:** explicit static reservation, exclusion from initialized/zeroed ranges after acquisition, allocator bounds and all task/DMA/parser/audio users is a viable methodology. Two disjoint reserved buffers can satisfy the same contract but do not reduce total demand. Preserve reset-time invalidation before every acquisition; retention need not survive reset and must not be reused as though it did.

**UNKNOWN:** exact address, allocator/scatter changes, worst-case demand and boot-to-export lifetime under normal restore/USB/audio. Minimum RAM qualification is a source/byte-derived region-ownership audit plus native startup allocation high-water/fail-closed replay and write guards through export. An explicitly reserved buffer must not disable retained Master FX or starve stock constructors. This cannot currently be certified as a copy-only patch using a known spare hole.
