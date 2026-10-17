> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase47 — normal pre-capture preservation

Latest scope: normal valid firmware/filesystem states only. Malformed-host/protection-bypass questions from the first Phase47 attachment are superseded and are not carried forward as blockers here. No adversarial requests or pointer redirection were investigated.

## Planned sequence and normal mutation producers

| Stage | Normal persistent-storage action | Physical range / confidence |
|---|---|---|
|Install |Previously qualified named selector0 staging +metadata publication |PROVEN scoped: staged erase`[0,5C000)`, metadata erase`[80000,81000)`, metadata program`[80000,80017)`; both targets excluded. Existing Phase44/45 evidence reused. |
|Bootloader |Identity read/normalization in RAM, staged-image validation/internal install |Reviewed normal paths do not program either target; identity setters require excluded explicit commands. Native complete peripheral boot is not newly replayed. |
|App initialization |NOR/SD binding, filesystem mount, settings load/defaults/conditional cleanup |For reconstructed normal FAT16 volume: any file-backed mutations stay`[D4000,2000000)`; valid/missing startup models produce none. Actual unit geometry UNKNOWN. |
|Optional cold boot |Repeats boot and initialization |Same conditional filesystem bound; cold boot is not evidence of original-byte preservation by itself. |
|Normal idle |Changed-settings subscriber/file cache flush; pending stock content work |Same internal volume range or SD medium; exact dirty predicates need not be false to preserve targets if geometry bound holds. |
|USB enumeration |Normal descriptor/control/MSD ready/capacity/read traffic |Reused normal WRITE10 protection rejects mutation; mode0/1/eject reapplication has no direct array write. No malformed-host claim. |
|Capture |One fixed read-only request for23+512 bytes |PROVEN scoped read path. It cannot establish whether earlier startup changed bytes. |

For the native directory model, specific normal mutations were:

| Class | Observed set |
|---|---|
|DIRECT DATA WRITE |Dirty settings save`[E3000,E4000)` |
|FAT WRITE |Deletion`[D5000,D6000)`, `[D9000,DA000)` |
|DIRECTORY WRITE |Creation/save/deletion`[E2000,E3000)` |
|METADATA WRITE |Directory/FAT above; no additional FAT32 FSInfo write in FAT16 |
|ERASE |Each emitted write requests erase-first for its aligned4096-byte sector; range remains identical to that sector. Physical completion is modeled, not measured. |

Actual settings cluster/directory sectors are UNKNOWN; the displayed allocations are model choices. All valid normal clusters and FAT/root sectors are bounded independently of those choices.

## A —81000..81016

**PROVEN NO NORMAL WRITE PATH for the reconstructed reference FAT16 filesystem** through reviewed file data/FAT/directory/sync routes. Those physical ranges beginD4000. The selected installation's metadata erase ends exactly81000, with no overlap. Identity-specific setters can write81000 only with explicit edit commands, which the planned sequence excludes; RAM byte14 clearing is not such a write.

**Current user-unit normal pre-capture classification: UNKNOWN.** Missing fact: authenticated mounted filesystem geometry/binding for this unit, or a proven formatter/default-image invariant applying to its inherited storage. Exact file allocation is not needed to exclude targets once all normal sector bounds are authenticated.

## B —82000..821FF

**PROVEN NO NORMAL WRITE PATH for the reconstructed reference FAT16 filesystem** through reviewed normal file persistence. Native mapping of all7967 permitted clusters excludes this region. Normal deletion/extension/reuse cannot produce the Phase46 FAT32 cluster values under that geometry. This is stronger than a no-write replay.

**Can any NORMAL reachable firmware/filesystem path in the planned test sequence write or erase any byte in82000–821FF before capture? UNKNOWN for this user's actual unit.** The exact missing fact is the current unit's mounted internal-volume geometry (volume start, bytes/sector, sectors/cluster, FAT/data bases and entry/sector bounds), or authoritative normal formatting/default-image proof constraining it to the reconstructed bounded layout. The reference dump is from another device; the firmware mount reads on-storage BPB fields rather than enforcing these exact mounted constants. No normal target-changing write was demonstrated.

If the unit's normal geometry matches the authenticated layout, the normal-path exclusion chain is:

`settings/project file operations → drive0 → NOR baseD4000, sector4096 → valid sectors0..1F2B → aligned writes/erases within[D4000,2000000)`;
`other packs → drive1 → SD`;
`normal MSD WRITE10 → initialized protection → reject`;
`normal mode/eject/resync → RAM/DSP only`;
`selected install → bounded staging/80000 metadata`;
`fixed diagnostic → READ only`.

The identity-only callback does not block82000: its erase ends82000, exclusive. No claim about malformed inputs is needed for this normal-path chain.

Evidence: [normal geometry](<real-filesystem-geometry.md>), [target equations](<target-address-equations.md>), normal test outputs (local-only reference: `builds/phase47-filesystem-state-closure/normal-states.json`; not distributed), [callback flow](<initialized-ram-callback.md>), [unchanged installation evidence](<../phase45-nor-mutation-closure/update-noop-review.md>).
