> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase56 — write census and retention lifetime

**PROVEN — the unmodified candidate does overwrite the selected region.** Native getter5DBCC→6B6CC replaces a seeded12-byte new record with legacy magic+8 zero bytes. Preserving magic and putting the8-byte compact record at+4 instead also fails: its first byte is1 for the reference layout, so the native timeout hook interprets it as ACTIVE and changes it to3 after the modeled deadline. Both collisions are persisted, using code byte-equal to the corrected image. [liveness_probe.py](<../../../builds/phase56-geometry-snapshot-lifecycle/liveness_probe.py>), liveness-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/liveness-tests.json`; not distributed).

|Writer class |Known path / proof status |

|---|---|

|Initialization/clear |PROVEN getter6B708/70A clears payload;6B714 publishes magic. New early snapshot must prevent this later clear by replacing the owner contract, not just writing earlier. |

|Heap growth |PROVEN allocator1D7D8 reads limit/cursor and traps when exceeding limit. Existing reservationD70 protects bytes only after installed and while its limit is honored; earlier timing and every allocator alias are UNKNOWN. |

|Task stacks |PROVEN modeled Main/Storage bounds do not intersectD70; UNKNOWN all boot/IRQ/FPU stack high-water. No stack margin is counted as available memory. |

|DMA ranges |PROVEN selected QSPI/parser/MSD modeled DMA buffers do not intentionally targetD70; UNKNOWN complete all-controller boot DMA-range closure. |

|SysTick/callback |PROVEN watch6B748 reads state/tick and writes+4; SysTick5998E calls it. It must be converted to the new union phase protocol. |

|USB/SysEx |PROVEN admission6B798 writes state/session/tick and raw6B850 updates chunk/owner; no incoming frame is the retention owner, but these native writers still collide. |

|Audio/Master FX |PROVEN private record sits below retained220 bytes; service uses shared getter, whose repeated or first init behavior must preserve the new schema. All computed interior feature aliases are not globally closed. |

|Delayed work |PROVEN known old timeout accesses; UNKNOWN entire boot/deferred callback census. |

|Terminal success/failure |PROVEN existing corrected PRIMASK fragment6BC30 targets legacy state byte+4; it cannot remain unchanged under the new layout. |

Evidence: census.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/census.json`; not distributed), app-0801d7d8.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-0801d7d8.asm`; not distributed), app-08059970.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-08059970.asm`; not distributed), app-0806b6cc.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-0806b6cc.asm`; not distributed), app-0806b850.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-0806b850.asm`; not distributed), app-0806bc30.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-0806bc30.asm`; not distributed); previous scoped stack/DMA evidence: [findings.md](<../phase42-exact-rdiag-integration/findings.md>).

**STRONG INFERENCE:** replacement of those owners with one union lifecycle can preserve retention from mount to export/raw decision without allocating more memory. Read-only geometry export must not update the eight payload bytes; transitions update only control. At ACTIVE, reuse of payload for raw bookkeeping is intentional and occurs only after the geometry decision is committed. Every terminal failure retains no-retry ownership. The abstract model enforces this but is not a replay of all native writers.

**UNKNOWN — liveness gate remains open.** The selected record is owned and suitably sized after minimization, but the current native owner semantics conflict. No normal-path no-overwrite proof exists for a corrected union implementation because that implementation is not emitted. A canary-only host model cannot replace this proof. The two native collisions reject naive reuse; they do not prove a carefully integrated redesign impossible.
