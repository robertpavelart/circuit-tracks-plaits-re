> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase48 — normal mount validation and accepted alternatives

**PROVEN:** the mount code accepts normal bounded layouts other than the reference FAT16 layout. It cannot establish the current unit's exact geometry merely by knowing B1.3 is installed.

Native`0801ADDC → 08019A92 → 080197A0` mounts existing media. An already mounted/ready volume can return without remounting. A new mount obtains sector size via disk ioctl2, requires a power of2 in512..4096, then reads sector0. It recognizes a VBR or examines up to four MBR partition-start candidates. A recognized BPB is parsed; the code does not replace it with reference formatting constants.

The actual NOR geometry query at373EC operation3 returns4096, so a normally bound internal volume must have matching BPB bytes/sector4096. The generic mount's wider sector-size support also serves SD; it is not proof that internal NOR can choose512-byte sectors.

## Accepted parameter space

The validation rules, rather than one fixed tuple, describe the alternatives:

- BPB bytes/sector must match the backend query.
- Sectors/cluster is a nonzero byte power of2:1,2,4,8,16,32,64,128.
- FAT copies must be1 or2; reserved sector count must be nonzero.
- Root-entry count must be a whole number of sectors (for4096-byte sectors, a multiple of128 entries).
- FAT size comes from FAT16-size field if nonzero, otherwise FAT32-size field; total sectors from the16-bit field if nonzero, otherwise32-bit field.
- Let `S = reserved + FAT_count*FAT_size + root_entries/(bytes_per_sector/32)`. Total sectors must cover S; derived cluster count `N=floor((total-S)/sectors_per_cluster)` must be nonzero and below0FFFFFF6. FAT type is12 for N<FF6,16 for N<FFF6, otherwise32. Mounted n_fatent=N+2. FAT storage must be sufficient for those entries.
- FAT12/16 requires a nonzero fixed root-entry count. FAT32 requires its additional version/root-layout checks, including zero fixed-root entries and version0. The code supports FAT32 in general; a properly capacity-bounded7980-sector,4096-byte internal volume cannot have enough clusters to meet the FAT32 threshold.
- Volume start may be the direct VBR at LBA0 or an accepted MBR partition start. Mounted bases incorporate that start.

These are parser predicates, not a claim that every mathematical combination is emitted by the normal formatter. `08019904–080199B8` computes the layout and verifies internal FAT consistency. **PROVEN:** it does not compare the declared BPB/partition extent with the physical sector capacity. The current phase does not test oversized/corrupt layouts or seek ways to force them; the prior countermodel is reused only as the reason not to mistake internal consistency for physical provenance.

## New normal bounded tests

All four modeled BPBs declare7980 sectors,4096 bytes/sector, volume start0 and1 reserved sector, entirely within the known normal internal partition size. Native mount succeeds and emits no writes:

| Case |Cluster sectors |FAT copies × sectors |Root entries |Native type |FAT/root/data bases |n_fatent |
|---|---:|---|---:|---|---|---:|
|Reference tuple |1 |2×4 |512 |FAT16 |1/9/13 |7969 |
|Bounded alternative |2 |2×2 |512 |FAT12 |1/5/9 |3987 |
|Bounded alternative |1 |1×4 |512 |FAT16 |1/5/9 |7973 |
|Bounded alternative |1 |2×4 |1024 |FAT16 |1/9/17 |7965 |

These are coherent normal mount models, not unit acquisitions or claims about formatter output. Their purpose is narrow: prove the normal parser does not enforce the one reference tuple. They all remain physically above D4000 and do not themselves demonstrate any target write. Exact equality to the reference tuple is **not necessary** for preservation; any authenticated geometry whose full normal mapped write ranges remain within the partition would suffice.

Evidence: [geometry_review.py:mount](<../../../builds/phase48-current-unit-geometry/geometry_review.py>), geometry-review.json (local-only reference: `builds/phase48-current-unit-geometry/geometry-review.json`; not distributed), complete mount listing (local-only reference: `builds/phase48-current-unit-geometry/app-08019734.asm`; not distributed), NOR sector query (local-only reference: `builds/phase48-current-unit-geometry/app-080373ec.asm`; not distributed).
