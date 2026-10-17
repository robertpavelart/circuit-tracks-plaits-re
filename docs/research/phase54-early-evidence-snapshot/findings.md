> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase54 — early evidence snapshot decision

**UNKNOWN: the architecture is not qualified.** Both stock read/copy points exist, but three independent admission requirements remain open: pre-read preservation for82000, fixed535-byte RAM ownership/lifetime, and trustworthy physical completion before validity publication.

**PROVEN:**81000 is read as23 bytes into20006868; original byte14 is destroyed by STRB08025224. An application hook at25222 can see the intact original record before that store, conditional on complete read success.82000 is read as512 bytes into the table staging pointer (captured20005148), returned at08035EE6, uploaded then reused by the next descriptor. Six native boundary tests confirm both argument sets and the callers' failure-status handling. [stock-read-lifetimes.md](<stock-read-lifetimes.md>), reader-boundaries.json (local-only reference: `builds/phase54-early-evidence-snapshot/reader-boundaries.json`; not distributed).

**PROVEN:** the application81000 read precedes its Main filesystem mount; the82000 read comes **after** mount and settings initialization, including a conditional delete/flush producer. **UNKNOWN:** that this producer or other prior normal work can modify the actual unit's82000 source; no target mutation was demonstrated. The healthy reference FAT16 bounds exclude it, but are not authenticated current-unit bounds. Copying after that read cannot by itself eliminate the pre-capture preservation problem. Superseded malformed-state countermodels and later B1.3 background features are not imported. [writer-ordering.md](<writer-ordering.md>).

**UNKNOWN:** no fixed retention allocation is approved. Existing stock buffers are normalized/reused, and the explicitly reserved prior diagnostic heap-top area has only8 bytes of fixture headroom. No535-byte memory hole is inferred from that dump. [snapshot-ram-liveness.md](<snapshot-ram-liveness.md>).

**PROVEN:** unlike the MSD host path, these internal return points expose backend status. **UNKNOWN:** status0 implies a complete fresh DMA destination under all required failure cases; the native setup can skip DMA reprogramming if already enabled, and TEF/missing completion may never return. A copy-only hook cannot implement FAILED on a permanently waiting stock read. [completion-authentication.md](<completion-authentication.md>).

**STRONG INFERENCE:** RAM-only export can reuse the prior23+8x64+completion-CRC protocol and removes all additional diagnostic NOR/Storage requests and their late H4 exposure. It removes preservation dependence **after** snapshots, not before them; it does not prove recovery of a failed stock boot. No early-snapshot exporter/state implementation is claimed. [late-export-design.md](<late-export-design.md>), [architecture-comparison.md](<architecture-comparison.md>).

| Gate | Result |

|---|---|

|Exact stock readers and intact copy windows |PROVEN, scoped native/static evidence |

|Both reads before possible source mutation |UNKNOWN;82000 after startup persistence is the critical ordering gap |

|535 bytes retained in fixed owned RAM |UNKNOWN |

|Genuine completion before snapshot validity |UNKNOWN |

|RAM-only later export without new NOR reads |STRONG INFERENCE architecture; not implemented/qualified |

|Exact hook bytes/cycles/stack/allocation |UNKNOWN beyond two proposed4-byte sites and payload/state size arithmetic |

**UNKNOWN — smallest next experiment:** bounded native startup/content ordering replay from1F0F0 through the first35EE6, with normal accepted settings states and real queued persistence primitives, establishing a physical-write range invariant before the82000 read. A healthy-fixture no-write trace alone is insufficient. If the exclusion cannot be proved without missing geometry, record that the copy-only strategy does not bypass that prerequisite. Separate RAM reservation/lifetime and completion-fence proofs remain necessary even if ordering passes.

**PROVEN:** all eight requested reports are present. Evidence/source checks are recorded in validation.json (local-only reference: `builds/phase54-early-evidence-snapshot/validation.json`; not distributed); Phase53 evidence and the439 pinned reference sources are preserved. Only Phase54 scripts, listings, JSON and Markdown were written. No new firmware/SYX, candidate, hardware access, MIDI enumeration/opening or transmission. The exhausted existing-B1.3 geometry authentication branch was not rerun.

EARLY EVIDENCE SNAPSHOT = UNQUALIFIED
