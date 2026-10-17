> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase48 — current-unit geometry provenance

**UNKNOWN: existing evidence does not establish this user's actual mounted internal filesystem geometry.** No normal target-changing write was demonstrated. The current-unit closure gate remains unqualified; stop without hardware access or a new firmware diagnostic.

## What was established

1. **PROVEN search coverage:** whole-project inventory75,892 files,233 candidate records and14 ZIP reviews. Existing synthetic captures, offline updater/emulator outputs, official firmware, public/reference dumps, host patch assets and user-reported bootloader/B1.3 behavior were distinguished. None identified an authenticated current-unit mounted geometry record. [existing-unit-evidence.md](<existing-unit-evidence.md>).
2. **PROVEN:** normal initialization registers/mounts an existing filesystem. The internal raw baseD4000 and sector query4096 are fixed in the examined implementation; FAT type/cluster/FAT/root/data layout is parsed from existing BPB/MBR data. No authoritative formatter/default-image invariant forcing the reference tuple was found. [formatter-layout.md](<formatter-layout.md>).
3. **PROVEN:** four coherent, capacity-bounded normal BPBs mount through native code, including differing FAT12/FAT16, FAT-count and root-size layouts. All produce no mount writes. The reference tuple is therefore not a mandatory parser invariant. The complete accepted parameter rules are documented separately from the four examples. [mount-validation.md](<mount-validation.md>).
4. **PROVEN:** an existing clean SC35D8 BIN was located in the project and matches its published manifest hash. Official4486, SC35D8, B1.3 and corrected diagnostic match byte-for-byte in the examined filesystem module, mount, disk/volume binding and NOR geometry query, with identical initialized geometry records. **UNKNOWN:** equality of their mounted media state. [version-geometry-comparison.md](<version-geometry-comparison.md>).
5. **PROVEN:** the reference SC35D8 transport has a bounded read-only ARM-memory command, and its documentation reports hardware-tested memory/file reads. B1.3 does not have that verified dispatcher hook. A usable current-installation geometry query is **UNKNOWN**, not presumed available. [minimum-readonly-evidence.md](<minimum-readonly-evidence.md>).

## Required target answers

**Can the user's current device mount a NORMAL filesystem geometry in which a legitimate pre-capture write can reach82000–821FF? UNKNOWN.** The unknown is this unit's inherited mounted geometry/bounds or an applicable normal-format invariant, not a demonstrated realistic target write. Every newly tested normal bounded alternative excludes the targets; their acceptance does not authenticate the unit's existing volume. The mount parser itself does not prove physical capacity bounding of all stored BPB values.

**Can the user's current device mount a NORMAL filesystem geometry in which a legitimate pre-capture write can reach81000–81016? UNKNOWN.** Same geometry-provenance gap. Identity-specific edit callbacks remain separate and excluded from the planned normal test input; their existence is not used to block82000.

**STRONG INFERENCE:** a healthy unit retaining the expected capacity-bounded internal format preserves both targets through normal file-backed startup persistence. **PROVEN scoped:** the authenticated reference FAT16 geometry and all normal models examined have no such filesystem target path. Neither statement is relabelled as current-unit proof.

Exact equality with the reference geometry is **not required**. A smaller proof is sufficient: authenticate this unit's physical base/stride and mounted FAT/data/root bounds, then show every normal mapped write/sector erase stays above D4000. This avoids requesting unrelated data or a full storage image.

## Evidence boundary and stop

The minimum missing record is a current-unit mounted geometry/status report: backing/base/stride, FAT type/count, bytes/sector, sectors/cluster, root-entry count, FAT size, n_fatent and volume/FAT/root/data starts. The known static layout can represent it in three fixed metadata spans totaling46 bytes, or equivalent decoded scalar fields. Source-unit/firmware/acquisition provenance is required. No target payload or full memory dump is necessary.

Prefer an existing saved report first. If absent, a read-only report through an **already installed, known supported interface** would be the next benign evidence source; such availability on current B1.3 is not established. No read was executed, no port opened, no mode changed, and no new firmware diagnostic is proposed. This follows the user's section7 stop condition.

## Status table

| Item |Status |
|---|---|
|BLOCKER |Current-unit geometry/bounds provenance or an authoritative applicable normal-format invariant remains missing. |
|SHOULD VERIFY |Review the version byte comparisons, accepted normal alternatives and the distinction between SC35D8 transport capability and B1.3 availability. Do not use MSD capacity or SD file payloads as internal NOR geometry. |
|HARDWARE-ONLY UNKNOWN |Physical timing/faults remain outside this offline phase; they neither prove nor disprove the missing mounted geometry. |

geometry-review.json (local-only reference: `builds/phase48-current-unit-geometry/geometry-review.json`; not distributed) persists native mount/query and exact existing-image comparisons. validation.json (local-only reference: `builds/phase48-current-unit-geometry/validation.json`; not distributed) verifies saved results, reports/links, previous Phase47 evidence and pinned reference-source preservation. No earlier suites were restarted, historical files overwritten, firmware generated or candidate designated.

CURRENT-UNIT GEOMETRY CLOSURE = UNQUALIFIED
