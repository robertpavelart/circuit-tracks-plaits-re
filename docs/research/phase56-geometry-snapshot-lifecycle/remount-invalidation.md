> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase56 — geometry-changing event inventory

**PROVEN:** exact-image direct/literal/initialized-pointer candidates and corroborating bodies are saved in census.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/census.json`; not distributed). Virtual targets are rooted in flash vtable0805BD1C (mount1ADDC,unmount1AE1C). Computed dispatch clients and all automatic predicates are not completely resolved; the table below is a concrete inventory with explicit gaps, not a claim of complete enumeration.

|Path / trigger |Automatic or user |Before geometry / before raw? |Geometry effect / required invalidation |

|---|---|---|---|

|1F0A8→1AE3A→vtable1ADDC |Automatic startup NOR then SD |Yes / yes |Writes backing wrapper atdisk+4, then mounts; initial NOR acquisition only after fresh success |

|1ADDC→19A92 at1AE02 |Mount/reinitialize object |Yes if initialization retried / yes |19AB6/19ABE clear type;19AC2 replaces registered pointer; invalidate NOR before registration |

|1AE1C→19A92 at1AE34 |Unmount via vtable+4 |Root trigger/predicate UNKNOWN; possible later volume teardown |Unregisters FS/type; invalidate before clear, not after |

|197A0 slow path197EC |Automatic lazy remount when type0/not-ready |Yes through ordinary file operations / yes |Clears type and reparses; hooking only19A92 misses this route |

|File APIs calling197A0 |Open19AFE; opendir1A0DA; path/status1A28C; free-space1A368; unlink1A44A; attribute/time1A4E6/1A626 |Normal content jobs; exact automatic vs UI predicates vary |Usually cached fast path; if media status changes, can enter the slow remount path |

|Disk ioctl1AE90 op2 at1AECC..1AEDE |Automatic mount sector-size query and any later supported query |Yes / yes |Stores queried stride togeometry+4; an identical query during initial mount is not proof of a post-valid change. Invalidate before actual change and normalize nested mount events. |

|Binding write1AE3A |Startup direct calls1F0B4/1F0C6; other computed users UNKNOWN |Yes / yes |Changes disk backing pointer even if geometry bytes match; NOR binding must be part of epoch |

|Full parse19A32..19A4A |Successful slow mount |Yes / yes |Publishes type/ID/sync; new snapshot must be tied to this completed generation |

|USB mode/eject248B4→38C54 |Settings/deferred/eject |May be before host/raw |Reviewed mode/class path itself has no direct f_mount/unmount call. Full class teardown virtual clients remain UNKNOWN; do not declare every USB transition a remount or prove none globally. |

|Reset/scatter/object reconstruction |Reset automatic; explicit restart separately controlled |Before new boot host request |Invalidates all volatile evidence; old token must never carry into new acquisition |

|Reformat/partition change |No formatter found in reviewed normal boot chain |UNKNOWN complete native interface root enumeration |Mount code is not formatting. No assumed format operation; any discovered writer/rebuilder must invalidate before changes. |

|Explicit factory/resource/updater/identity commands |User-driven, outside fixed capture workflow |Excluded policy, not quietly enabled |Can bypass file mappings. Keep them excluded; geometry is not authority for arbitrary raw writes. |

Sources: app-08019a92.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-08019a92.asm`; not distributed), app-08019734.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-08019734.asm`; not distributed), app-0801ae1c.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-0801ae1c.asm`; not distributed), app-0801ae90.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-0801ae90.asm`; not distributed), [formatter-layout.md](<../phase48-current-unit-geometry/formatter-layout.md>), [initialized-ram-callback.md](<../phase47-filesystem-state-closure/initialized-ram-callback.md>).

**UNKNOWN:** full alias proof for all stores into geometry/registered FS/backing objects, all vtable clients, and every reset/rebuilder path. Invalidation at19A92 alone is **PROVEN insufficient coverage** because native cached filesystem APIs can directly enter197A0's slow initialization. A concrete implementation must cover both paths without counting nested initial mount callbacks as independent historical epochs.
