> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase51 — strict evidence acceptance

**PROVEN structural gate:** reuse unmodified [geometry_from_sector.py](<../../../builds/phase50-msd-readonly-geometry/geometry_from_sector.py>). Require exact4096-byte sector(s); proven mode1/LUN0 physical binding; stock-recognized jump/FAT marker plus55AA; bytes/sector4096; csize power2 in1..128; reserved>0; FATcount1/2; nonzero FAT size; fixed-root alignment; total16-or32 selection; internally consistent stock FAT class; enough FAT entries; primary MBR/VBR selection in stock order; volume and FAT/root/data regions within disk0's normal7980-sector backing. Missing MBR candidate, malformed/incomplete sector or any bound failure means **evidence=INVALID**, infer no geometry. Phase50's five native matches and15 rejection cases remain unchanged. geometry-tests.json (local-only reference: `builds/phase50-msd-readonly-geometry/geometry-tests.json`; not distributed).

**PROVEN additional acceptance boundary:** correct source unit/firmware, stable selected window, requested LBA/count, exact-length host completion and no-retry containment must accompany the bytes. **UNKNOWN:** a trustworthy independent signal that the lower NOR operation physically completed correctly despite lost status. The Phase51 gate [acceptance_gate.py](<../../../builds/phase51-msd-read-safety/acceptance_gate.py>) returns INVALID for structural failure, otherwise UNQUALIFIED; it has no option to force an authenticated PASS. Adapter fields in Phase50 are derived validators, never captured RAM mount status.

| Candidate validity signal | Assessment |

|---|---|

|SCSI GOOD / CSW residue0 |**PROVEN insufficient:** native failures1/2 also produce them |

|4096 returned bytes |**PROVEN insufficient:** caller always clears/sends that length after returned failures |

|Zero initialization |**PROVEN useful rejection:** catches native no-data failures, excludes tested old-buffer reuse; not a completeness checksum |

|FAT signature/BPB consistency |**PROVEN** rejects distinguishable errors; **STRONG INFERENCE** of meaningful geometry under ordinary successful-read assumptions; not transaction authentication |

|USB transport CRC / saved SHA-256 |**UNKNOWN** actual host transport result; saved hash only records returned bytes and cannot recover lower status; no application-level NOR sector checksum is present in this path |

|Backup VBR / second sector |**UNKNOWN** applicable copy/provenance for this unit; normal bounded FAT12/16 has no mandatory independent backup used by this mount path; MBR+VBR gives structure/binding corroboration, not read-status recovery |

|Repeated identical reads |**PROVEN** byte-identical histories can remain indistinguishable; **UNKNOWN** extra assurance on this unit; not prescribed because a stuck Storage read has no qualified retry/unwind |

|Mounted RAM cross-check |**UNKNOWN** no supported current B1.3 RAM geometry export, perPhase49 |

**PROVEN target equations conditional on authenticated BPB:** N=floor((total−reserved−nFAT*fatsz−rootS)/spc); data=vol+reserved+nFAT*fatsz+rootS; cluster2..N+1 maps to `D4000+1000*(data+(cluster−2)*spc+withinCluster)`. Bound FAT copies/root/FSInfo as well.81000 and82000 are below disk0 base by53000/52000hex (negative normal LBAs53/52hex); valid bounded maps cannot reach them. [physical-binding.md](<../phase50-msd-readonly-geometry/physical-binding.md>).

**UNKNOWN current-unit preservation result:** no sector was acquired/authenticated. A hypothetical/model BPB must not close that gate. Geometry proves normal filesystem write bounds only, not unrelated raw-write producers or all boot/background mutation.
