> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase48 — initialization versus formatting

**PROVEN:** normal filesystem initialization mounts existing media. It does not reconstruct the reference FAT16 BPB from hardcoded formatting constants.

Native chain:

`0801F0A8 → 0801AE3A`: bind disk0 to NOR wrapper`[20006968]`, disk1 to SD wrapper`[2000696C]`; disk vtable init →`0801ADDC`; build drive path`0:` or`1:`; `08019A92(fs=object+10,path,opt=1)` registers and mounts; `080197A0` reads/validates boot sector and populates mounted fields. `0801AE1C` instead calls`08019A92` with null filesystem/opt0 to unregister: this is unmount, not a formatter. Mount failure is returned/logged by1ADDC; this shown chain does not fall into automatic formatting.

Sources: init/unmount listing (local-only reference: `builds/phase48-current-unit-geometry/app-0801addc.asm`; not distributed), binding (local-only reference: `builds/phase48-current-unit-geometry/app-0801f0a8.asm`; not distributed), mount (local-only reference: `builds/phase48-current-unit-geometry/app-08019734.asm`; not distributed).

| Geometry source question | Result |
|---|---|
|A. Fixed by firmware? |**PROVEN partially:** NOR mapping baseD4000 and native NOR sector query4096. FAT type, sectors/cluster, FAT sizes, root/data layout and total sectors are not fixed to reference values by this mount code. |
|B. Derived from capacity? |**PROVEN:** raw NOR query373EC operation2 derives a sector count from ID capacity; operation3 returns4096. The mount requests sector size, then derives filesystem counts from BPB; it does not choose a fresh filesystem layout from capacity. No native capacity read was executed here. |
|C. Existing boot sector? |**PROVEN YES:** BPB fields and optional MBR volume start determine layout. FAT type follows cluster count, not a constant or cosmetic type string. |
|D. User/configurable? |No ordinary settings/UI control for assigning FAT fields was found in this initialization chain. **UNKNOWN** global formatter availability. Legitimate pre-existing formatted volumes can differ. Inherited resource-image upload can replace volume bytes; that is not a resident formatter. |
|E. Version-dependent? |**PROVEN:** examined code/base/sector records identical across official4486, SC35D8, B1.3 and corrected diagnostic. Mounted state can still differ because existing media differs. |

**PROVEN native sector query:**373EC with operation3 returns1000 (4096) without a peripheral operation. query listing (local-only reference: `builds/phase48-current-unit-geometry/app-080373ec.asm`; not distributed), geometry-review.json (local-only reference: `builds/phase48-current-unit-geometry/geometry-review.json`; not distributed). The query fixes disk sector size, not the whole BPB.

The reference fixture's exact normal values remain FAT16,4096B/sector,1 sector/cluster,1 reserved,2 FATs×4 sectors,512 root entries,7980 total sectors, data start13, clusters2..7968, physical`[D4000,2000000)`. They are **PROVEN for that authenticated mounted fixture**, as derived in [Phase47 geometry](<../phase47-filesystem-state-closure/real-filesystem-geometry.md>). They are **UNKNOWN as exact current-unit values**.

No authenticated internal-VBR/default filesystem image or on-device formatter was identified that forces those exact values on every legitimate unit. The native free-space function1A358 is not f_mkfs. The reviewed disk-write callers belong to normal cache/data/directory/sync paths. This scoped finding is not claimed as a proof that no optional raw-image replacement or formatter exists anywhere in the firmware.

**UNKNOWN remaining formatter/default-layout invariant:** neither firmware image identity nor the reference BPB proves what existing volume this unit inherited. No new formatter execution, generated firmware or new diagnostic is proposed.
