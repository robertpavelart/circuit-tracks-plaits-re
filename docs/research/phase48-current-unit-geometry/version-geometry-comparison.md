> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase48 — official4486, SC35D8 and B1.3

**PROVEN:** exact existing images share the examined filesystem geometry code and initialized base/sector records. **UNKNOWN:** equality of their mounted on-storage geometry on this user's unit. Code identity is not media-state identity.

[geometry_review.py:versions](<../../../builds/phase48-current-unit-geometry/geometry_review.py>) reads existing artifacts only; no builder runs and no firmware image is emitted. SC35D8 was found at`builds/phase43-hardware-test-candidate/clean-sc35d8.bin`; its SHA matches the reference manifest. This extends the prior source-only SC35D8 comparison with exact bytes.

| Image |Existing image SHA-256 |
|---|---|
|Official4486 |b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da |
|SC35D8 |1525c6662bbff9ced7e6055bb54e864615c30013f1b4dec4be6c404f8c750c05 |
|B1.3 published COPY/ADD spans |2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41 |
|Corrected diagnostic, research only |0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738 |

All four match official bytes in these half-open ranges:

| Range |Functionality |
|---|---|
|0801855C..0801AF48 |Compiled FatFs module, mount/cluster/file/cache/disk adapters |
|080197A0..08019A50 |Mount parser specifically, also contained in above |
|0801F0A8..0801F1A8 |NOR/SD disk binding and volume construction/selection |
|080373EC..0803742E |NOR sector/capacity/status query |

Independent scatter decoding also gives identical initialized geometry at20000A98: baseD4000, sector1000. Full initialized-data hashes agree. Per-range hashes, image sizes and byte-equality flags are persisted in geometry-review.json (local-only reference: `builds/phase48-current-unit-geometry/geometry-review.json`; not distributed).

## B1.3 effect

| Question |Code-based answer |
|---|---|
|Reformat on normal boot? |**PROVEN:** examined binding/mount path does not format; it parses an existing volume and returns/logs failure. **UNKNOWN** global absence of every optional formatter outside that path. |
|Change FAT type/cluster size at mount? |**PROVEN:** same parser derives these from BPB. No B1.3-specific forced values in these bytes. It can mount accepted alternatives without converting them. |
|Change partition/volume base? |**PROVEN:** internal raw base remainsD4000; mounted volume start is VBR/MBR-derived. Those two bases must be distinguished. |
|Migrate an older layout? |No migration in the examined normal mount chain; **UNKNOWN** authoritative version-history/default-media migration invariant. Do not infer a migration from version names. |
|Preserve a non-reference existing normal layout? |**PROVEN capability:** unchanged native parser mounts the bounded alternatives without formatting or writing. The saved named internal-firmware installation traces also leave the internal filesystem region aboveD4000 untouched. |
|Replace volume content deliberately? |Inherited resource-upload header39088 selects table20003CC8; selector1 record has baseD4000/capacity1F2C000. Existing upload machinery can replace bytes in that resource region, including a volume image. This is not a resident formatter or a normal boot migration, and no such request is executed/proposed here. |

B1.3's `tools/rodisk.py` protects **mod-origin** internal-pack write/delete calls at3CC16/3CC34; stock callers remain permitted. It does not rewrite FAT geometry or make all internal storage read-only. The SC35D8-derived corrected diagnostic must not be assumed to inherit this later feature. Source: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/rodisk.py:arm_code/install`.

The **invariant established** is the examined mapping/parser/query implementation. The **invariant not established** is this unit's existing BPB, its mounted values, or universal normal formatter output. resource selector listing (local-only reference: `builds/phase48-current-unit-geometry/app-08039088.asm`; not distributed), prior authenticated selector records (local-only reference: `builds/phase44-preflash-redteam-closure/b13-selector-provenance.json`; not distributed), [prior installation evidence](<../phase45-nor-mutation-closure/update-noop-review.md>).
