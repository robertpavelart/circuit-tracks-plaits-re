> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase57 — field lifetime coalescing and adaptation

**STRONG INFERENCE:** exactly the same12-byte capacity can carry the following union after all legacy owners are adapted. No extra fixed reservation, heap allocation or audio/parser/stack borrowing is proposed. The rejected52-byte extension remains unused.

|Addresses |BOOT / first mount in progress |VALID through export/host decision |After atomic raw admission |After terminal result |

|---|---|---|---|---|

|D70..D73 |Control32:phase3 bits,unexpected-event bit,epoch28; BOOT0→MOUNTING/epoch1 |VALID/EXPORTED,epoch1; control is sole publisher |ACTIVE,epoch1; admission/quarantine atomically mutate only control |SUCCESS orFAILED terminal; never rearm |

|D74 |Part of8-byte payload not valid until commit |Compact geometry byte0 |Target mask |Retain terminal bookkeeping |

|D75 |Same |Geometry byte1 |Session token |Same |

|D76 |Same |Geometry byte2 |Global chunk |Same |

|D77 |Same |Geometry byte3 |Read/reply/free ownership |Keep ownership while a request remains active |

|D78..D7B |Same |Geometry bytes4..7 |32-bit start tick |No timer rearm; preserve until safe end/reset |

**PROVEN lifetime condition:** the geometry becomes dead for this transaction only after exact-epoch/digest authorization is accepted and the transition toACTIVE is atomic. **Export alone is not enough**: the host has not yet approved, and the device still needs the retained bytes to validate the token. The model refuses geometry export afterACTIVE; no live geometry is overwritten sooner. [first_epoch_model.py](<../../../builds/phase57-first-mount-provenance/first_epoch_model.py>), epoch-model-tests.json (local-only reference: `builds/phase57-first-mount-provenance/epoch-model-tests.json`; not distributed).

|Legacy write/read |Conceptual adaptation |Semantics retained / proof limit |

|---|---|---|

|6B708/70A payload clear and6B714 magic store |Move one-time initialization/reservation to before constructors; remove later diagnostic-record clearing from lazy getter |Keep separate Master-FX initialization; getter must preserve all12 thereafter |

|Magic reads6B722/6B764 |Replace with reserved-limit and new lifecycle validity contract; code/protocol version supplies schema identity |Old4-byte magic cannot coexist with control32 in the same bytes |

|Timeout6B794 writing+4 |Read phase from control; onlyACTIVE uses starttick+8; setFAILED in control |5000-tick deadline, wrap arithmetic, no release/retry remain |

|Admission writes6B820/824/830 |Validate geometry token before overlay; publishACTIVE then initialize raw session/tick/target/owner under one admitted owner contract |Duplicate/second transaction rejected; no speculative Storage submit |

|Raw chunk/owner stores |Retain at+6/+7 only inACTIVE raw union |Read and USB-buffer lifetimes remain; fail does not free active descriptor/buffer |

|6BC46 success and6B9FE failure |Atomic control-phase publication;FAILED absorbs late completion |Preserve corrected terminal-race semantics; a byte+4 store is now incorrect |

**PROVEN model scope:**13 scenarios cover idempotent later getter use, nonACTIVE ticks, unexpected events before/during/after snapshot/export/admission, tick wrap, timeout/late success, normal success, reservation refusal and wrong epoch/digest/identity authorization. No second diagnostic transaction follows failure. Counts are model admissions, not9 native read requests. epoch-model-tests.json (local-only reference: `builds/phase57-first-mount-provenance/epoch-model-tests.json`; not distributed).

**UNKNOWN:** all native adapters, raw target-mask command, same-boot session binding and exact caller register/flag ABI are not implemented as a new image. Saved old native tests continue to qualify the unchanged old format only. The conceptual coalescing is feasible in12 bytes; it is not a passed native union regression.

**STRONG INFERENCE — initial publication requirement:** the new initializer must not publish allocator-limitD70 while the record still contains warm-entry residue that an ISR could interpret asACTIVE. Under a separately bounded ownership/PRIMASK contract, recheck old limit/cursor, initialize BOOT/payload first, then publish reserved limit last; restore the incoming mask. Later getter calls never repeat this initialization. The pure model treats reservation as atomic; its Python assignment order is not a proposed native store-order proof. Exact native early-reservation race/latency testing remains UNKNOWN.
