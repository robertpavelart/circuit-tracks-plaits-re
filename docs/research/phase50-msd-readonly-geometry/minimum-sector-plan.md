> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase50 — minimum sectors and conditional host plan

**PROVEN geometry payload:** no FAT chains, files, identity region or coefficient region is needed. For an ordinary superfloppy FAT volume, one4096-byte sector at internal disk0 LBA0 suffices. If it is an MBR, add only the primary candidate VBR sector(s) in the order the stock mount probes them; normally2 sectors total, worst root+4 candidates=5 sectors/20480 bytes. No extended/GPT traversal is implemented by this stock mount path. app-08019734.asm (local-only reference: `builds/phase48-current-unit-geometry/app-08019734.asm`; not distributed).

| BPB offset (hex) | Field |

|---|---|

|0B u16 |bytes/sector, must4096 |

|0D u8 |sectors/cluster, power2 in1..128 |

|0E u16 |reserved sectors |

|10 u8 |FAT count1/2 |

|11 u16 |root entry count |

|13 u16,20 u32 |total sectors: use16 if nonzero else32 |

|16 u16,24 u32 |FAT size: use16 if nonzero else32 |

|2A u16 /2C u32 (FAT32) |version/root cluster |

|1FE |55AA boot signature, even on4096-byte sectors |

Stock recognizer additionally checks first byteE8/E9/EB and `FAT` at36hex or `FAT32` at52hex. Do not infer FATclass from its text label. For MBR, four16-byte entries at1BEhex: startLBA atentry+8 and extent at+C. Mount uses starts, not BPB hidden-sectors28hex, to establish volbase. Decoder imposes normal physical partition bounds in addition to native mount constraints.

Let `rootS=rootEntries*32/bps`; `overhead=reserved+nFAT*FATsize+rootS`; `N=floor((total-overhead)/spc)`. Stock class is FAT12 ifN<FF6, FAT16 ifN<FFF6, otherwise FAT32 ifN<0FFFFFF6. FATbase=vol+reserved; fixedroot=FATbase+nFAT*FATsize; data=vol+overhead; validclusters2..N+1. This internal32MiB/4096-byte backing cannot normally fit enough clusters for FAT32. Bounds/FATcapacity are checked, not assumed. [geometry_from_sector.py](<../../../builds/phase50-msd-readonly-geometry/geometry_from_sector.py>); geometry-tests.json (local-only reference: `builds/phase50-msd-readonly-geometry/geometry-tests.json`; not distributed).

**UNKNOWN full-session qualification: this is an offline conditional plan, not instructions to execute now.** Prerequisites: independently establish exact B1.3, stable internal mode1, LUN0 raw-block binding, a quiescent/no-unrelated-save interval, and host raw access without automount/repair or unsolicited mode/update traffic. The current state has not been queried. Do not toggle a persistent UI setting to satisfy this plan.

If those prerequisites are qualified separately, use the OS's existing read-only raw block/SCSI interface for the identified device; no drive number is guessed and no executable acquisition script is supplied. Expected inquiry `Novation`/`Circuit`/`1.00`, LUN0, capacity8192×4096; those alone are not a unit identity or base-window proof. In stable mode1, read ONLY:

1. USB LBA64 (`40` hex), count1,4096 bytes; save `msd_mode1_lun0_lba00000040.bin` atomically after exact-length successful transfer.

2. If and only if it is MBR, read USB LBA64+partition-start, count1,4096 bytes for the next needed primary candidate; stop at first stock-recognized VBR. Save each with its exact eight-digit USB LBA.

3. Save a host provenance manifest: unit/firmware, selected-mode evidence, backing relation, timestamps, command/OS status, LBA/count/length and SHA-256 of each complete returned sector. Hashes authenticate saved returned bytes, not unfiltered physical NOR or live RAM status. Reject failures/partial output and do not auto-retry a stalled Storage operation.

No volume/filesystem mount, directory listing, FAT read, read of81000/82000, save, flush, eject, reboot or firmware update belongs in this plan. Windows raw-device availability, permissions and preventing automount are **UNKNOWN** on this unit; no OS/device enumeration was performed. READ CAPACITY/TUR/INQUIRY add only their scalar replies, not unrelated sectors. Do not scan other bases in lieu of establishing mode.

Decoder accepts local files only: repeated `--sector USB_LBA=FILE`. It reuses Phase49 invariants without editing Phase49. Exact BPB total is now available; RAM mount/cache status is still **UNKNOWN**. Native B1.3 mount and parser agree on4 bounded superfloppies and1 primary-MBR layout;15 invalid/incomplete/binding cases are rejected. No generated test BPB is presented as actual-unit data. [test_geometry.py](<../../../builds/phase50-msd-readonly-geometry/test_geometry.py>); geometry-tests.json (local-only reference: `builds/phase50-msd-readonly-geometry/geometry-tests.json`; not distributed).
