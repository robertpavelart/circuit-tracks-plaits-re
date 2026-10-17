> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase47 — normal filesystem-state closure

**UNKNOWN: actual-unit pre-capture preservation remains unqualified.** The exact Phase46 synthetic FAT32 state is **PROVEN incompatible with the authenticated reference device's normal FAT16 geometry**. It is no longer presented as a demonstrated realistic startup state. No normal write to either evidence target was found in the new normal-state tests.

The latest continuation narrows this phase to normal valid firmware/filesystem/control flow. It supersedes the initial malformed-BOT and corrupted-state requests. No malformed-host, write-protection circumvention, pointer redirection or arbitrary storage-access investigation was performed. No hardware, MIDI ports, firmware transmission, new firmware image or hardware-candidate designation was used.

## Important results

- **PROVEN:** the authenticated running-RAM fixture has internal NOR FAT16 at physical baseD4000, volume LBA0,4096-byte sectors,1 sector/cluster,2 FATs of4 sectors,512 root entries, FAT start1/root9/dataD, valid clusters2..1F20, normal volume sectors0..1F2B. Full physical extent`[D4000,2000000)`. [real-filesystem-geometry.md](<real-filesystem-geometry.md>).
- **PROVEN:** all7967 valid cluster values were executed through the native mapper; none can address81000/82000. Required normal-geometry clusters would beFFFA2/FFFA3, outside allocation. The exact Phase46 FAT32 geometry/constructed FIL clusters cannot arise from normal writes, extension, deletion or reuse under this reference layout. [comparison](<countermodel-comparison.md>), [equations](<target-address-equations.md>).
- **PROVEN:** native path resolution identifies settings as`0:/Tracks/Globals/00_GLOB.cg`,128 bytes. Native validation accepts the authenticated RAM settings record. Valid and missing startup models emit no writes. A file created empty by the native API follows zero-size/defaults behavior. Dirty valid settings save writes model data/directory sectors; normal unlink writes directory and both FAT copies without erasing freed file data. [startup-persistence.md](<startup-persistence.md>).
- **STRONG INFERENCE:** this bounded layout describes a healthy unit retaining the same official internal format. **UNKNOWN:** this user's actual mounted geometry or an authoritative formatter/default-image invariant forcing every legitimate unit to match it. The upstream RAM dump is not a current snapshot from this unit. That is the remaining primary geometry fact; the Phase46 synthetic countermodel is not substituted for it.

## Coverage and limits

[normal_states.py](<../../../builds/phase47-filesystem-state-closure/normal_states.py>) / normal-states.json (local-only reference: `builds/phase47-filesystem-state-closure/normal-states.json`; not distributed) persist four normal native file-operation cases and three startup cases, plus exhaustive cluster arithmetic. Coherent modeled directories use the authenticated geometry. Native file lookup/read/write/unlink/sync and actual startup validator execute. Disk completions, content-service response boundaries and configuration query are explicit seams; this is not a full RTOS boot replay or actual unit directory image. [realistic-startup-states.md](<realistic-startup-states.md>) distinguishes supported normal states from unknown rejected-record provenance and unproved on-disk dirty flags.

The Phase46 conditional nonempty-invalid-settings deletion branch is retained as code evidence. This phase does not fabricate an invalid settings record and call it normal firmware output. The deletion mechanism itself is exercised on a valid normal file and bounded by the same geometry. A precise real-unit settings cluster is UNKNOWN, but is not required for the geometry-wide exclusion if that unit's bounds are authenticated.

[initialized-ram-callback.md](<initialized-ram-callback.md>) reuses exact callback initialization/normal write-protection evidence and follows only legitimate persistence callers. No superseded malformed-host gap is carried as a Phase47 blocker. Prior atomicity/update/rollback tests were reused unchanged; no new finding invalidates them. [target-preservation.md](<target-preservation.md>) includes the install→boot→optional cold boot→idle→enumeration→capture timeline, normal physical write ranges and separate target decisions.

## Critical decisions

| Target | Reconstructed reference normal filesystem | Actual unit, planned pre-capture sequence |
|---|---|---|
|81000..81016 |PROVEN NO NORMAL WRITE PATH through reviewed file-backed persistence |UNKNOWN: user-unit geometry not authenticated; explicit identity edit is separately excluded |
|82000..821FF |PROVEN NO NORMAL WRITE PATH through reviewed file-backed persistence |UNKNOWN: same missing geometry/format invariant, independent of identity-specific uncertainty |

**Can any NORMAL reachable firmware/filesystem path in the planned test sequence write or erase any byte in82000–821FF before capture? UNKNOWN.** No such normal path was demonstrated. The missing fact is an authenticated current-unit internal filesystem geometry/binding, or a proven normal formatter/default-storage invariant applying to it. The reference mounted structure proves its own layout, not that of this unit.

## Minimum benign evidence

1. Prefer an **already existing** current-unit runtime/status dump or saved storage report containing drive0 binding and mounted FS fields: type, sector/cluster size, volume/FAT/root/data bases, FAT size/count and n_fatent. Associate it with the unit and running firmware identity. Matching the bounded normal geometry closes this particular uncertainty without the23/512 target payloads or a complete NOR image.
2. Alternatively, an authenticated default internal-filesystem image or firmware formatter analysis that establishes the same physical-volume bound for this unit's normal format. None of the inspected existing RAM files supplies that current-unit provenance; no original NOR VBR was found in them.
3. If such evidence is absent, a **read-only geometry/status inspection through an already supported installed interface**, if available, is the next benign evidence source. Availability for this unit has not been established. No port was opened and no query was issued here. No new firmware diagnostic is proposed automatically.

## Decision table

| Category | Item |
|---|---|
|**BLOCKERS BEFORE FLASHING** |Authenticate current-unit normal internal-volume bounds/binding or the corresponding formatter/default-image invariant. Until then do not promote a reference-device conditional proof into actual-unit preservation or designate a hardware candidate. |
|**SHOULD VERIFY** |Independently check source-dump provenance, FAT16 field offsets, all-cluster native result and model/seam distinctions. Keep missing-file read-only open distinct from explicit open-always creation. Review rejected-settings provenance without inventing unsupported normal states. |
|**ACCEPTABLE HARDWARE-ONLY UNKNOWN** |Actual peripheral timing, physical NOR faults, real memory margins and unit-specific recovery execution remain untested. They do not replace the missing geometry provenance. |

validation.json (local-only reference: `builds/phase47-filesystem-state-closure/validation.json`; not distributed) checks reports, saved native results, prior Phase46 checksums and pinned reference sources. No historical results or candidate bytes were changed.

PREFLASH FILESYSTEM STATE CLOSURE = UNQUALIFIED
