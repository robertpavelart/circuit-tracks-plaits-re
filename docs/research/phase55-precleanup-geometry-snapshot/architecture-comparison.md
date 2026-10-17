> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase55 — three architecture choices

|Aspect |A: late raw diagnostic |B: Phase54 stock-read535 snapshot |C: geometry gate + later conditional raw read |

|---|---|---|---|

|Boot modification |Guarded late command; dormant before request |Two early copy points plus completion/reset/retention logic |NOR mount-success copy plus validity/epoch lifecycle |

|Retention RAM |Existing12-byte latch/64-byte borrowed temporary |At least535 payload plus metadata |46 payload,47 minimum or52 aligned simple state, plus optional epoch/CRC |

|NOR operations added |23-byte plus8×64-byte raw reads |0 if stock-read copying suffices |0 for geometry; same9 raw reads only after separate gate |

|Storage/H4 |Additional raw-read deadlock exposure |No diagnostic reads, stock-read failure remains |Geometry adds none; later raw step retains H4 |

|Pre-read preservation |Unqualified without current-unit mapping |82000 stock read already after settings initialization |Could close with authoritative pre-cleanup mapping and stable epoch |

|Current-unit geometry |Missing prerequisite |Not eliminated for pre-82000-stock-read activity |Captured directly from actual native mounted objects, if hook/retention qualify |

|Containment |One shot, discard/no retry on failure |No BOTH/no export on failure; stock deadlock remains |No raw admission on missing/invalid geometry; old raw containment still required |

|Complexity |Small command already tested offline |Large retention and completion fences |Small copy but new retention/epoch/host interlock and separate raw admission |

|Current decision |Preservation unqualified |UNQUALIFIED |UNQUALIFIED: RAM ownership and lifecycle/global ordering still open |

Sources: [architecture-comparison.md](<../phase54-early-evidence-snapshot/architecture-comparison.md>), [mount-to-persistence-ordering.md](<mount-to-persistence-ordering.md>), [snapshot-ram-liveness.md](<snapshot-ram-liveness.md>), [host-gating.md](<host-gating.md>).

**STRONG INFERENCE — recommendation:** prefer C for the next bounded architecture work. It obtains the mapping native file operations actually use and needs far less retention than B. It does not depend on reviving the exhausted MSD authentication branch, and it avoids adding storage operations merely to query geometry. Keep A's already-qualified one-shot transport and failure containment for the separately admitted raw step.

**UNKNOWN:** C is not ready for a build or hardware designation. The mount window is established for the synchronous path, but full asynchronous pre-window exclusion, a fixed small RAM reservation, hook equivalence and mount-epoch invalidation remain unqualified. Do not treat47 bytes as automatically available because535 were not. No firmware/SYX or hardware action is initiated.
