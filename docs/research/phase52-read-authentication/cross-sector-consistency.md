> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase52 — filesystem relations are secondary evidence

**PROVEN BPB gate:** reuse Phase50 parser unchanged: stock jump/FAT markers,55AA,4096-byte sectors, power2 cluster size, reserved>0, FATcount1/2, sufficient FAT size, exact total selection, root alignment, stock-derived FAT class, data/cluster bounds and physical partition extent. The table text is not the FAT-class oracle. Native mount already matches five normal fixtures. [geometry_from_sector.py](<../../../builds/phase50-msd-readonly-geometry/geometry_from_sector.py>); geometry-tests.json (local-only reference: `builds/phase50-msd-readonly-geometry/geometry-tests.json`; not distributed).

**PROVEN relations:** firstFAT=vol+reserved; secondFAT=firstFAT+fatsz whennFAT2; fixedroot=firstFAT+nFAT*fatsz; data=fixedroot+rootEntries*32/bps. Valid clusters2..N+1 map through D4000+1000*(data+(cluster−2)*spc+withinCluster). For an authenticated bounded BPB, normal domains cannot reach81000/82000 below D4000. No current-unit BPB is acquired here.

| Cross-sector relation | Evidence value and limitation |

|---|---|

|First FAT reserved entries/media descriptor |A plausible normal FAT16 corroboration; the model usesFFF8/FFFF and allocated cluster entries. **UNKNOWN** exact current bytes. Native mount197A0 does not authenticate the volume by checking these FAT entry bytes, so literal model values are not a mandatory current-unit signature. |

|Two FAT copies |**PROVEN** stock window-flush1859A writes the second copy when configured. **STRONG INFERENCE** normally synchronized metadata; copies can share the same read failure/replay and are not independently authenticated. |

|Fixed-root location and directory records |BPB determines location; plausible entry clusters can be checked against2..N+1. **UNKNOWN** current names/allocation; zero unused entries/suffixes are legitimate and weaken completeness detection. |

|Reserved sectors |Only BPB/signature and volume offset are established; no supported invariant says all remaining reserved sectors have a fixed independent payload. |

|FAT32 backup VBR |Not used as an assumption. Bounded32MiB internal4096-byte layout cannot normally reach FAT32 cluster counts; no mandatory FAT16 backup sector is established by this mount. |

Native sources: app-08019734.asm (local-only reference: `builds/phase48-current-unit-geometry/app-08019734.asm`; not distributed); app-0801855c.asm (local-only reference: `builds/phase46-msd-filesystem-closure/app-0801855c.asm`; not distributed); app-080185de.asm (local-only reference: `builds/phase46-msd-filesystem-closure/app-080185de.asm`; not distributed). No current-unit FAT chain, root, volume label or fixed reference layout is inferred.

**PROVEN logical limitation:** coherent BPB/FAT/root bytes can be returned unchanged from a previous coherent snapshot and retain these relations. Host-side consistency is useful for rejecting distinguishable corruption, but it cannot alone attest current physical provenance. The older-target substitution test is a model of that ambiguity, not a newly found native replay path. authentication-experiment.json (local-only reference: `builds/phase52-read-authentication/authentication-experiment.json`; not distributed).
