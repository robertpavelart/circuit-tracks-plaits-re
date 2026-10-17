> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase57 — original12-byte ownership, before redesign

**PROVEN:** region20044D70..20044D7B is the existing Phase42/44 diagnostic reservation below220-byte Master FX state20044D7C..20044E57. The shared getter5DBCC branches to6B6CC; it lowers allocator limit[20002B44] toD70 only if the expected old limitE58 and cursor≤D70 hold. It uses no allocator call. Initial stores6B708/70A clear+4..11;6B714 writes magic4E4F5234 at+0..3. This is lazy runtime reservation, not reset initialization. [findings.md](<../phase42-exact-rdiag-integration/findings.md>), app-0806b6cc.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-0806b6cc.asm`; not distributed).

|Byte address |Current meaning |Writer candidates in exact owner bodies |

|---|---|---|

|0x20044d70|magic0|0x806b714|

|0x20044d71|magic1|0x806b714|

|0x20044d72|magic2|0x806b714|

|0x20044d73|magic3|0x806b714|

|0x20044d74|IDLE/ACTIVE/SUCCESS/FAILED|0x806b708, 0x806b794, 0x806b820, 0x806b9fe, 0x806bc46|

|0x20044d75|session|0x806b708, 0x806b824|

|0x20044d76|chunk|0x806b708, 0x806b8da|

|0x20044d77|buffer owner|0x806b708, 0x806b8de, 0x806b924, 0x806ba02|

|0x20044d78|start-tick0|0x806b70a, 0x806b830|

|0x20044d79|start-tick1|0x806b70a, 0x806b830|

|0x20044d7a|start-tick2|0x806b70a, 0x806b830|

|0x20044d7b|start-tick3|0x806b70a, 0x806b830|

**PROVEN scoped extraction:**23 accesses in known getter/watch/admission/raw/terminal bodies; [ownership.py](<../../../builds/phase57-first-mount-provenance/ownership.py>) performs register constant tracking and expands accesses to all12 bytes. ownership.json (local-only reference: `builds/phase57-first-mount-provenance/ownership.json`; not distributed) includes every extracted read PC as well as these writes. This is not an alias-complete global scanner. The old success store6B9EC is unreachable under the corrected6B9DC branch; actual success store is6BC46. Do not count the retired store as a live additional writer.

|Owner |Exact native activity |Before USB-ready / after USB-ready / required later |

|---|---|---|

|Getter6B6CC |Writes all12 at first reservation; checks magic at6B722 on subsequent calls; initializes separate Master FX via5DC06 when needed |Can run before USB; remains callable after USB; reservation/retained feature access still required |

|SysTick5998E→6B748 |Checks limit/magic, reads state+4/starttick+8, sets state3 at6B794 after5000 ticks if ACTIVE |Callable before/after USB; inert before reservation or outsideACTIVE; quarantine timeout still required during raw capture |

|USB admission6B798 |Reads+4 at6B818; writesACTIVE6B820,session6B824,starttick6B830 |On an admitted explicit USB request; pre-ready admission is structurally absent under no host request, but early IRQs exist; duplicate rejection still required |

|Raw6B850 |Reads session6B864; state checks6B8D0/6B918/6B9F6; writes chunk6B8DA,owner6B8DE/6B924/6BA02; failure6B9FE |After admission; tracking/ownership stays live through reads and USB drain, including a stuck transaction |

|Corrected terminal6BC30 |Reads state6BC3E; conditionally writesSUCCESS6BC46 under restored PRIMASK |Required after final successful transmit/drain; may never overwrite quarantine |

**PROVEN:** magic has runtime-long liveness; status/session/chunk/owner/tick overlap once a capture is ACTIVE. No existing byte is simply dead immediately after boot or geometry export. Before the first explicit request, session/chunk/tick are semantically dormant but getter/watch still interpret their storage. The region cannot accept new contents without replacing those interpretation contracts. Native collisions from Phase56 are retained, not rerun: liveness-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/liveness-tests.json`; not distributed).

Original timeline:RESET(unreserved/old SRAM residue)→first getter(reserve+zero+magic)→IDLE(watch checks)→explicit request(ACTIVE/session/tick)→chunk/read/reply ownership→SUCCESS or FAILED_QUARANTINED→no new capture before reset. Full reset-to-first-getter timing is UNKNOWN; the captured heap fixture alone does not establish it.
