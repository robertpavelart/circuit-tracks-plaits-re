> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase47 — normal internal filesystem geometry

**PROVEN for the authenticated reference-device RAM fixture; UNKNOWN for the current user's unit.** These scopes must not be merged. fixture-geometry.json (local-only reference: `builds/phase47-filesystem-state-closure/fixture-geometry.json`; not distributed) preserves the first checkpoint. geometry-provenance.json (local-only reference: `builds/phase47-filesystem-state-closure/geometry-provenance.json`; not distributed) pins the source and native settings path.

Source: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/ctre/Firmware-Analysis/ram_dump_firmware_0x08037988.bin`, SHA-256 `26a29670c0c1918217b7eadf8f89fe6df97994d3cc6e1c0ed65ac522e161094c`. This is the previously authenticated upstream dump,327679 bytes, loaded at20000000. Filesystem object`20000AB0`, referenced by`[20005E5C]`, lies inside it. No missing external-NOR bytes were supplied to extract these fields.

| Input | Value | Confidence / derivation |
|---|---|---|
|Backing medium |ARM external NOR, drive0 |PROVEN: disk object20000AA0 points to wrapper2000AC94, geometry20000A98; native constructor1F0A8 binds NOR global20006968. Not DSP SDRAM. |
|Partition byte base |D4000 |PROVEN initialized geometry20000A98 and running fixture |
|Volume start LBA |0 |PROVEN mounted `fs+28` |
|FAT type |FAT16 |PROVEN `fs+0=2`, native branch convention |
|Bytes/sector |4096 (`1000`) |PROVEN `fs+C` |
|Sectors/cluster |1 |PROVEN `fs+A`;4096 bytes/cluster |
|FAT copies |2 |PROVEN `fs+2` |
|FAT size |4 sectors/copy |PROVEN `fs+24` |
|First FAT LBA |1 |PROVEN `fs+2C` |
|Reserved sectors |1 |PROVEN derived first FAT minus volume start for this mounted layout |
|Root entries |512 |PROVEN `fs+8`;4 sectors of32-byte entries |
|Root start |9 |PROVEN `fs+30` |
|Data start |D |PROVEN `fs+34` |
|Number of FAT entries |1F21 |PROVEN `fs+20` |
|Valid data clusters |2..1F20 inclusive |PROVEN native cluster predicate18698,7967 clusters |
|Total logical sectors |1F2C (7980), LBAs0..1F2B |PROVEN derived for this normal mounted geometry:13 metadata sectors +7967 one-sector clusters; agrees with partition capacity. No trailing partial-cluster ambiguity because cluster size1. Original VBR is not independently present. |
|Physical mapping |D4000 +4096×LBA |PROVEN native mapper1AF1E; these bounded inputs cannot overflow32 bits |
|Complete physical volume |`[D4000,2000000)` |PROVEN arithmetic for this geometry |
|FAT1 / FAT2 |`[D5000,D9000)` / `[D9000,DD000)` |PROVEN arithmetic |
|Fixed root / data |`[DD000,E1000)` / `[E1000,2000000)` |PROVEN arithmetic |
|Initial cache flags |window dirty0; FSInfo flag80 |PROVEN fixture `fs+3/+4`; FAT16 does not execute FAT32 FSInfo writes. |

**PROVEN native coverage:** [normal_states.py](<../../../builds/phase47-filesystem-state-closure/normal_states.py>) executes18698 for **every** valid cluster2..1F20; all7967 results are LBAsD..1F2B. This is exhaustive cluster arithmetic for this mounted geometry, not an exhaustive boot schedule.

Drive1 fixture object20001AF4 binds SD, sector size512, filesystem type0 (unmounted). Its live geometry cannot be invented from zero fields. Normal SD writes use a different backend and do not become NOR writes. Internal pack0/settings use drive0; other accepted pack IDs use drive1, as already established in Phase46.

**STRONG INFERENCE:** a healthy device using this unchanged internal layout excludes both targets from normal file data, directory and FAT writes, regardless of the settings file's particular cluster. **UNKNOWN:** an authenticated formatter/default-image invariant requiring this exact layout on every unit. No formatter was executed, and the original NOR VBR/FAT/directory image was not found in the inspected evidence. Native filesystem mount accepts geometry from disk; RAM fields are not compile-time formatting constants. Function1A358 is free-space querying, not evidence of formatting.

existing-ram-inventory.json (local-only reference: `builds/phase47-filesystem-state-closure/existing-ram-inventory.json`; not distributed) records the four existing RAM dumps inspected. Only the firmware-running snapshot has this mounted structure; the boot/before-main dumps cannot substitute for a current-unit VBR. No external NOR filesystem image or authentic target capture was found among the project's named RAM/NOR/QSPI image artifacts; the existing phase27/42 capture files are explicitly synthetic.

Native mapping/mount definitions are retained in [Phase46 filesystem-lba-binding.md](<../phase46-msd-filesystem-closure/filesystem-lba-binding.md>); this phase adds actual mounted fields instead of redoing that audit.
