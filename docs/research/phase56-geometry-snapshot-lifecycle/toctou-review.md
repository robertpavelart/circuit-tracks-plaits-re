> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase56 — TOCTOU and original-byte preservation

|T1 export→T2 read event |Required behavior / status |

|---|---|

|Same mounted geometry, normal settings deletion/flush |PROVEN conditional mapping theorem: changes entries/cache flags, not bounded geometry. Those normal writes remain outside both targets under accepted record/invariants. |

|Unmount/register/remount/lazy reparse |Invalidate before changes; reject old token. Sticky history blocks raw even for a new currently safe record unless all intervening epochs were separately qualified. |

|Backing wrapper/stride change |Invalidate even if FAT scalars coincide. Expected NOR identity/base/stride is part of capture contract. |

|Reset/boot/USB session loss |No token reuse; require fresh export/session binding. Current model has only same-boot generations, not a cross-boot identity proof. |

|Record corruption |Validate reserved bits/frame CRC; compare requested digest with retained bytes before admission. A digest is not complete arbitrary RAM-fault detection or ownership proof. |

|Simultaneous authorization and invalidation |Atomic winner; if invalidation wins,0 submits. If ACTIVE wins, geometry-changing producer must defer/reject before mutation. An increment-only observer is insufficient. |

|Queued/in-flight NOR mutation predating snapshot |Short PRIMASK cannot stop it. Startup producer/queue and source-preservation exclusion must already hold; UNKNOWN. |

|Change after first raw request queued |No safe cancellation/unwind is assumed. Prevent mutation under ACTIVE or fail/discard with original one-shot quarantine; do not release semaphore/retry. Exact native interlock UNKNOWN. |

|Factory/update/resource command |Excluded fixed workflow; geometry proof does not authorize it. An interface capable of bypassing file mappings must not silently be admitted alongside capture. |

Sources: [remount-invalidation.md](<remount-invalidation.md>), [generation-gating.md](<generation-gating.md>), [findings.md](<../phase31-storage-error-recovery/findings.md>), [target-preservation.md](<../phase47-filesystem-state-closure/target-preservation.md>).

**PROVEN conditional:** if the initial snapshot predates persistence, every writable mapping is bounded, all geometry-changing writers are intercepted before mutation, and authorization/admission is atomic, the host's same-epoch decision remains valid until raw acquisition. Model event orderings enforce that conditional contract. **UNKNOWN:** all antecedents for the actual native implementation.

**PROVEN:** geometry does not contain the512 coefficient bytes. Native DSP staging reused after35EE6 cannot later supply original evidence without retention. Therefore this architecture still needs the fixed82000..821FF physical read, admitted only after the geometry/preservation gate; it is not replaced by the mapping record. [stock-read-lifetimes.md](<../phase54-early-evidence-snapshot/stock-read-lifetimes.md>).

|Target |Independent intended admission |Current qualification |

|---|---|---|

|81000..81016 |Needs file-mapping exclusion plus separate identity-history policy; explicit identity erase ends82000 exclusive |UNKNOWN, raw disabled |

|82000..821FF |Needs file-mapping exclusion, initial epoch/history and no bypass writer; does not inherit identity-only veto |UNKNOWN, raw disabled |

The model accepts coefficient-only mask2 without identity authorization and rejects identity mask1 unless its separate predicate is provided. The existing combined23+512 command cannot silently become coefficient-only without a separately tested target-mask adaptation. H4 remains FAIL for late raw reads; host discard/no retry/power-cycle boundary containment stays required. No recovery/restore action is executed.
