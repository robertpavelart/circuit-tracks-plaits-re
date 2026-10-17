> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase55 — minimum practical geometry record

**PROVEN:** reuse the existing **46-byte packed record**, not a contiguous46-byte structure:20000A98:8 ||20000AB0:14 ||20000AD0:24. It contains mapping context and mounted geometry while omitting the filesystem sector window, path/FILE state, RTOS sync pointer and cached free-space values. This is the smallest already-reviewed compatible record, not a claim of mathematical minimum bit packing. [live-geometry-structure.md](<../phase49-existing-geometry-reader/live-geometry-structure.md>); [geometry_parser.py](<../../../builds/phase49-existing-geometry-reader/geometry_parser.py>).

|Packed offset |Source / FS offset |Bytes |Meaning |

|---|---|---:|---|

|0 |20000A98 |4 |Physical partition base |

|4 |20000A9C |4 |Disk mapper sector stride |

|8 |FS+00 |1 |FAT type0/1/2/3 = unmounted/FAT12/FAT16/FAT32 |

|9 |FS+01 |1 |Logical drive, must be0 |

|10 |FS+02 |1 |FAT count |

|11 |FS+03 |1 |Dirty-window status, not geometry |

|12 |FS+04 |1 |FSInfo flags |

|13 |FS+05 |1 |Padding, carries no validity meaning |

|14 |FS+06 |2 |Mount ID, may legitimately wrap to0 |

|16 |FS+08 |2 |Fixed root entry count |

|18 |FS+0A |2 |Sectors per cluster |

|20 |FS+0C |2 |Bytes per sector |

|22 |FS+20 |4 |n_fatent |

|26 |FS+24 |4 |Sectors per FAT |

|30 |FS+28 |4 |Volume base LBA |

|34 |FS+2C |4 |First FAT LBA |

|38 |FS+30 |4 |Fixed root LBA or FAT32 root cluster |

|42 |FS+34 |4 |Data start LBA |

**PROVEN:** FS=20000AB0, registered drive0 pointer[20005E5C]; FS header3C bytes followed by1000-byte sector cache. Occupied FS extent103C and disk+FS extent104C are **STRONG INFERENCE** from adjacent object layout and native offsets, not debug type declarations. Disk=20000AA0: +4 wrapper,[20006968] must match; +8 geometry pointer20000A98; +C drive0; +10 embedded FS. These backing checks must be performed by acquisition, since46 bytes alone do not contain the wrapper pointer or code identity. [live-geometry-structure.md](<../phase49-existing-geometry-reader/live-geometry-structure.md>), app-0801f0a8.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-0801f0a8.asm`; not distributed), app-0801ae90.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-0801ae90.asm`; not distributed).

**PROVEN:** derive reserved=fatbase−volbase; first cluster2, last=n_fatent−1; dataend=database+(n_fatent−2)*csize. The BPB total is not retained as an exact scalar. Its possible interval is[dataend−volbase,dataend+csize−1−volbase], subject to independently accepted physical bounds. With csize1 this is exact; otherwise do not invent an exact total. The native data/FAT/root/FSInfo write domains can be bounded without the lost trailing-sector remainder. FAT32 root is a cluster, not an LBA. [live-geometry-structure.md](<../phase49-existing-geometry-reader/live-geometry-structure.md>); [real-filesystem-geometry.md](<../phase47-filesystem-state-closure/real-filesystem-geometry.md>).

**STRONG INFERENCE:**46 bytes plus explicit fresh-success/binding/epoch validity is sufficient for the Phase47 normal-write exclusion calculation. A separate volatile header should convey version, success/FAILED, boot/mount epoch and integrity checks. Minimum logical payload+validity=47 bytes; an aligned46-byte payload padded48 plus a32-bit state is52. More metadata increases that number; no claim that a robust epoch/CRC header fits the minimum52 is made. The optional checksum authenticates transport/integrity, not the device's identity or physical medium by itself.

**PROVEN:** the supplied-record host model reuses the old parser and correctly handles a native successful zero mount ID with explicit fresh-success provenance, leaving the original bytes unchanged. It accepts the bounded model layouts and rejects incomplete/provenance-failed records. [host_gate.py](<../../../builds/phase55-precleanup-geometry-snapshot/host_gate.py>), host-gate-cases.json (local-only reference: `builds/phase55-precleanup-geometry-snapshot/host-gate-cases.json`; not distributed). No current-unit record has been obtained.
