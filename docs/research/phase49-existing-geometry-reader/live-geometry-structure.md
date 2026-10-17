> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase49 — live internal geometry

**PROVEN:** exact published B1.3 application SHA-256 is `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41` (435220 bytes). It is inspected in memory, never rebuilt or emitted. Phase48 established byte equality of the filesystem/mount/binding code across official4486, SC35D8, B1.3 and the corrected research diagnostic. This permits reusing those native layout results; it does not authenticate the user's mounted state. b13-inspection.json (local-only reference: `builds/phase49-existing-geometry-reader/b13-inspection.json`; not distributed); geometry-review.json (local-only reference: `builds/phase48-current-unit-geometry/geometry-review.json`; not distributed).

**PROVEN:** `0801F0A8` loads geometry address `20000A98`, binds disk object `20000AA0` through `0801AE3A`, and binds its wrapper from `[20006968]`. `0801ADDC` mounts `disk+10 = 20000AB0` using `08019A92(..., opt=1)`. The drive-0 filesystem pointer slot is `20005E5C`. The following fields are little-endian scalars, not network-order words. app-0801f0a8.asm (local-only reference: `builds/phase48-current-unit-geometry/app-0801f0a8.asm`; not distributed); app-0801addc.asm (local-only reference: `builds/phase48-current-unit-geometry/app-0801addc.asm`; not distributed).

| Address / FS offset | Size | Meaning / native evidence |

|---|---:|---|

|20000A98 |4|physical NOR base; initialized D4000; disk mapper `0801AF1E` |

|20000A9C |4|physical sector stride; initialized 1000 |

|20000AB0 / +00|1|FAT type: 0 unmounted, 1 FAT12, 2 FAT16, 3 FAT32; commit `08019A32` |

|20000AB1 / +01|1|logical drive, internal = 0 |

|20000AB2 / +02|1|FAT copies, 1 or 2; `080198BC` |

|20000AB3 / +03|1|window dirty flag; transient, not geometry |

|20000AB4 / +04|1|FSInfo flag (80 disabled/unknown, bit0 dirty); `080199CA` |

|20000AB5 / +05|1|padding, no validity claim |

|20000AB6 / +06|2|mount ID; assigned only after successful parse, `08019A40`; can wrap |

|20000AB8 / +08|2|fixed root entry count; `080198E0` |

|20000ABA / +0A|2|sectors/cluster; `080198CC` |

|20000ABC / +0C|2|bytes/sector from disk ioctl, checked against BPB; `08019814`, `0801989E` |

|20000AD0 / +20|4|n_fatent = data cluster count + 2; `08019960` |

|20000AD4 / +24|4|one FAT size, sectors; `080198B6` |

|20000AD8 / +28|4|volume base LBA; `08019962` |

|20000ADC / +2C|4|first FAT LBA; `08019964` |

|20000AE0 / +30|4|fixed root LBA (FAT12/16) or root cluster (FAT32); `08019996` / `08019984` |

|20000AE4 / +34|4|data start LBA; `08019966` |

**PROVEN:** reserved sectors = `fatbase - volbase`; first valid cluster = 2, last = `n_fatent-1`, with the bounds used by `08018698`. Total BPB sectors is consumed in `080198F0..0801992C` but is not retained as a dedicated field in this record. Derive `end = database + (n_fatent-2)*csize`; the BPB total lies in `[end-volbase, end-volbase+csize-1]`, further bounded by physical partition capacity. Do not print an invented exact total when csize > 1. app-08019734.asm (local-only reference: `builds/phase48-current-unit-geometry/app-08019734.asm`; not distributed); [target-address-equations.md](<../phase47-filesystem-state-closure/target-address-equations.md>).

**PROVEN:** the metadata needed is three spans: A98:8, AB0:14, AD0:24 = 46 bytes. It is not one contiguous 46-byte RAM structure. One encompassing span is `20000A98..20000AE7`, 80 bytes, including 34 unnecessary bytes. The FS header is 3C bytes followed by the 1000-byte sector window at `fs+3C`; next geometry starts at `20001AEC`. **STRONG INFERENCE:** the occupied FS extent is 103C bytes and the disk+FS extent 104C bytes; no C debug type declaration is present.

**PROVEN:** these are static application-RAM objects, initialized afresh at boot, not persistent NOR records. Geometry fields are assigned during mount, while cache flags/window/free-space state can change during operations. The mount commits type last and then ID/sync pointer. Unmount/remount or reset invalidates an old snapshot. **STRONG INFERENCE:** geometry stays stable during an ordinary mounted interval; **UNKNOWN:** atomicity of a hypothetical three-request snapshot during concurrent remount.

**PROVEN:** normal `08019A92` unregister/re-register clears the old object's type at `08019AB6`, clears a new object's type at `08019ABE`, and updates the registered pointer at `08019AC2`. Therefore a completed normal unmount does not leave a nonzero old type in the same record. The parser rejects type0. This does not eliminate a snapshot crossing the type-clear/type-commit interval or prove current device readiness. app-08019a92.asm (local-only reference: `builds/phase47-filesystem-state-closure/app-08019a92.asm`; not distributed) (same byte-equal FatFs module established in Phase48).

**PROVEN:** Storage-owned content work reaches these objects through disk/file wrappers; stock initialization also invokes mounting. The RTOS/file synchronization pointer is `fs+10` (`08019A46`), intentionally omitted from the 46-byte record. **UNKNOWN:** one universally exclusive task owner across all mount/export paths, and current task/mount validity on the user's unit. Type/ID plausibility alone does not prove an ongoing mounted state without acquisition provenance.

The public reference RAM decodes as FAT16, 4096 bytes/sector, csize1, reserved1, FATcount2, FATsize4, volume0, data13, clusters2..7968, inferred exact total7980. **PROVEN for that public snapshot only**; not current-unit evidence. parser-tests.json (local-only reference: `builds/phase49-existing-geometry-reader/parser-tests.json`; not distributed).
