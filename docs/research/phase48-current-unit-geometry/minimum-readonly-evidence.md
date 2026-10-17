> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase48 — minimum benign evidence, not executed

**UNKNOWN:** the current unit's mounted internal-volume bounds. Exact equality to the reference FAT16 layout is unnecessary. Any authenticated normally mounted layout with physical file/FAT/directory/sync extents confined above D4000 and below the partition end would close this particular storage question.

Stop at this evidence boundary. No new firmware diagnostic, installation, mode change, device read or arbitrary memory dump is proposed or executed.

## Minimum fields

Prefer an **existing current-unit** geometry/status export or runtime snapshot already in the user's possession. It should identify the source unit/firmware and acquisition context, then supply:

| Record |Fields needed |
|---|---|
|Internal block mapping |NOR backing/drive0, physical base, sector stride |
|Mounted filesystem header |FAT type, logical drive, FAT count, root-entry count, sectors/cluster, bytes/sector |
|Mounted filesystem bounds |n_fatent, FAT size in sectors, volume start, FAT start, root location, data start |

For the authenticated4486/B1.3 static object layout these correspond to **three fixed metadata spans totaling46 bytes**, if an already supported read-only interface can expose them:

- `20000A98`,8 bytes: physical base and sector stride.
- `20000AB0`,14 bytes: mounted FS header through sector size.
- `20000AD0` (`fs+20`),24 bytes: n_fatent/FAT size/volume/FAT/root/data fields.

This is a bounded geometry record, not a request for full RAM, filesystem contents, identity bytes or coefficient bytes. Addresses are supplied only to define the existing symbols precisely; no request bytes, executable acquisition script or live command is generated. An equivalent decoded scalar status report is preferable if available. The record must be from the mounted application, not before-main initialization or an emulator.

Total sectors can be reported directly from an existing VBR/status record, but is not an additional mandatory payload if the normal write-domain bound can be proved from mounted fields. For example, evaluate with wide checked host arithmetic:

`data_end_LBA = data_start + (n_fatent-2)*sectors_per_cluster`.

Also bound both FAT copies and fixed-root sectors; validate volume/sector-size consistency and normal FAT class. For the reference tuple, data_end=1F2C and physical end=D4000+1000×1F2C=2000000. A different valid bounded tuple can pass too. No file payload, FAT-chain dump or exact settings-file cluster is necessary under the normal-valid-state scope.

## Already tested interfaces versus current availability

**PROVEN code capability:** reference`tools/rdiag.py` command2 reads up to64 bytes within ARM flash/RAM; `tools/ctremote.py:req_mem/dec_mem` implements the host side. The three metadata spans above fit this existing size limit. `docs/NOTAS.md` at the SC35D8 hardware-results section reports ping, application-header memory read and stock-file reads on the reference author's hardware. These are documentation reports, not live tests by this agent. The exact geometry spans were not reported as hardware-acquired there.

**PROVEN version distinction:** SC35D8 dispatcher0801EB30 contains the rdiag branch. B1.3 has the original stock prologue at that location, and its manifest lacks the rdiag feature. The verified SC35D8 entry hook is not installed in the exact published B1.3 bytes. **UNKNOWN:** a currently installed, independently supported B1.3 interface exposing these fields. Do not assume the SC35D8 command is available simply because the host tool exists; no suggestion to install SC35D8 is made.

The corrected research diagnostic admits fixed NOR command13 only; its existence does not provide a current-unit geometry query. Stock file-content commands provide file bytes, not mounted FS fields. Normal MSD capacity reports8192×4096 independently of selected window/BPB, so a capacity response alone is insufficient. No stock read-only geometry command has been established in the examined evidence.

**Minimum next evidence:** an already saved current-unit report containing these scalar fields; failing that, the same bounded report from an interface **already known to be installed and supported on this unit**. Establishing such interface availability remains a prerequisite. Under the present no-hardware/no-new-firmware instructions, stop without executing it or inventing a replacement diagnostic.

Sources: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/rdiag.py` command2/FLASH/RAM/NMAX; same root`tools/ctremote.py:req_mem`; same root`docs/NOTAS.md` SC35D8 hardware result dated2026-10-09; version bytes (local-only reference: `builds/phase48-current-unit-geometry/geometry-review.json`; not distributed), Phase46 capacity callback (local-only reference: `builds/phase46-msd-filesystem-closure/app-08057e30.asm`; not distributed), Phase43 admission evidence (local-only reference: `builds/phase43-hardware-test-candidate/native-regression.json`; not distributed).
