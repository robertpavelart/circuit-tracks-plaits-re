> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase50 — exact B1.3 MSD backing

**PROVEN:** the inspected published B1.3 application is435220 bytes, SHA-256 `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`. Its initialized backend table and selected-window pointer are decoded from existing bytes. All examined MSD/SCSI/storage/mode ranges match official4486. The Advanced Setup range4709A differs because B1.3 patches the separate button24 branch; the button9 bit17 branch47070..47098 is intact. No image is built/emitted. b13-inspection.json (local-only reference: `builds/phase50-msd-readonly-geometry/b13-inspection.json`; not distributed); b13-08047016.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08047016.asm`; not distributed); b13-0804709a.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-0804709a.asm`; not distributed).

**PROVEN:** RAM200037AC points to table20003788. Callbacks (Thumb pointers) are init8057E31, capacity8057E35, ready8057E45, writeprotect8057E49, read8057E89, write8057EF5, maxLUN8057FB1, eject8057FB5, inquiry805B6B8. This is a raw NOR wrapper, **not the SD drive and not a FatFs file object**. Read loads `[20006968]` and calls its vtable+C, wrapper08024130; write calls vtable+10,08024164. b13-08057e30.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08057e30.asm`; not distributed); callback-table.json (local-only reference: `builds/phase46-msd-filesystem-closure/callback-table.json`; not distributed); [filesystem-lba-binding.md](<../phase46-msd-filesystem-closure/filesystem-lba-binding.md>).

| Property | Exact code result |

|---|---|

|Logical unit |Max-LUN callback returns0: intended sole LUN0; no advertised SD LUN |

|Interface |Stock MSD class200000F8; class descriptor805B3D8, interface2, class08/subclass06/protocol50, endpoints82 IN /02 OUT,64-byte max packets |

|Capacity |Always8192 blocks of4096 =32MiB; independent of selected base/end |

|Default initialized mode |Internal1, window record8038C3C = base94000,endD3FFF |

|Internal2 |Record8038C4C = baseD4000,end1FFFFFF |

|Internal3 |Record8038C44 = base0,end1FFFFFF |

|Physical medium |ARM external serial NOR via global20006968; independent of DSP external SDRAM and SD |

|Read |NOR address = selected base +4096×USB LBA; length4096×callback count |

|Write |Lower callback can read/compare/erase-first program; normal WRITE10 is blocked by constant protection1 |

**PROVEN:** the read callback does not enforce the window record's end. Even internal1 can read LBA64 (`94000 +40*1000 = D4000`), within its advertised8192-block limit and the real32MiB physical range. Native SCSI→callback tests observed exactly this wrapper submission. Thus the nominal94000..D3FFF descriptor must not be mistaken for the actual read admission bound. native-reads.json (local-only reference: `builds/phase50-msd-readonly-geometry/native-reads.json`; not distributed).

Answer: **PROVEN same physical NOR backend; PROVEN addressable same disk0 volume baseD4000**, by mode1 LBA64, internal2 LBA0 or internal3 LBAD4. **UNKNOWN:** the currently selected mode and active USB configuration on the user's unit. LUN0 LBA0 is not invariably that filesystem: in ordinary mode1 it is the different94000 region. **STRONG INFERENCE:** a coherent BPB acquired with established mode1 binding reconstructs the geometry used by stock mount. It still does not reveal RAM mount/cache/dirty state.

**PROVEN caveat:** USB class GET_MAX_LUN handler58ECC calls the max-LUN callback, then its zero result branches at58F08 to the error/stall path. The callback's intended LUN0 result is not proof a successful one-byte control reply is produced. **UNKNOWN:** actual Windows enumeration/fallback behavior for this exact composite mode. b13-08058eb0.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08058eb0.asm`; not distributed). No hardware-tested B1.3 raw-MSD geometry capture was found; older SC35D8 rdiag reports are not MSD evidence.
