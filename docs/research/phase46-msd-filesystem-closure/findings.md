> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase46 — MSD, filesystem and persistence closure

**UNKNOWN: pre-capture preservation remains unqualified.** No ordinary-boot overwrite was demonstrated. This phase closes important provenance/admission questions, but finds that accepted filesystem geometry can defeat the assumed physical partition bound. The corrected Phase44 research candidate remains **undesignated**. Historical Phase43 remains **SUPERSEDED — DO NOT FLASH**. No firmware was generated, hardware accessed, MIDI port inventoried/opened, or firmware transmitted.

## Results that change the Phase45 analysis

1. **PROVEN:** the real initialized MSD backend returns **write protected**. Eighteen native SCSI WRITE(10) tests reject before data admission or storage write, including target LBAs, bounds, zero/large count and overflow cases. Phase45's lower-callback capability is not a demonstrated accepted USB write. [msd-reachability.md](<msd-reachability.md>).
2. **PROVEN:** native decompression from exact stock4486, B1.3 and corrected diagnostic produces identical callback table/pointer and identical complete initialized-data hash. Startup settings observer selects0/1, not whole-array mode3. SCSI eject is another150-tick mode-reapplication root, with0/1 stable. Boot's normal registered descriptor contains Audio/MIDI interfaces, no MSD interface. [initialized-ram-callback.md](<initialized-ram-callback.md>).
3. **PROVEN:** drive0 is NOR baseD4000 with4096-byte sectors; drive1 is SD. Native FAT mount accepts a synthetic oversized FAT32 BPB. Accepted clusters then pass native cluster conversion and **native f_write**, emittingFFFAD/FFFAE. Existing native mapper evidence maps these to81000/82000 with erase-first. This is a countermodel to a universal bound, not authentic unit data or a complete startup overwrite. [filesystem-lba-binding.md](<filesystem-lba-binding.md>), [address-bounds-audit.md](<address-bounds-audit.md>).
4. **PROVEN:** automatic startup settings validation can request DELETE+flush for a nonempty invalid record. No save-button action is needed to reach that producer branch. A stock changed-settings subscriber is independently registered and can submit128-byte write+flush. **UNKNOWN:** actual pre-capture dirty/metadata state and physical destinations. [persistence-routes.md](<persistence-routes.md>).

## Requested gates

| Requirement | Outcome |
|---|---|
|MSD activation/bounds |PROVEN normal boot configuration and app mode/WRITE10 predicates; STRONG INFERENCE ordinary host traffic has no array write. UNKNOWN complete malformed-BOT continuation/CBW state proof; lower callback itself lacks selected-window bounds. |
|Filesystem binding |PROVEN NOR/SD object constructors, geometry, disk dispatcher and native arithmetic. UNKNOWN actual volume/allocation and all startup producer predicates. Native accepted-volume countermodel defeats unconditional safety. |
|Integer safety |PROVEN32-bit wrap exists and can survive accepted mount/cluster/f_write checks with constructed FIL states. UNKNOWN occurrence with actual unit metadata; no assumed physical out-of-array alias. |
|Initialized RAM |PROVEN exact candidate initialization source, table, native targets and found consumers. STRONG INFERENCE ordinary lifetime target stability; UNKNOWN exhaustive computed alias-write exclusion. Standalone SC35D8 binary absent; source inheritance distinguished from direct exact-byte tests. |
|Persistence |PROVEN automatic invalid-settings cleanup and registered changed-settings save routes; known retained SC35D8 resync is RAM/DSP. UNKNOWN complete actual-state destination closure. |
|T0–T7 |Defined precisely; filesystem startup/idle rows prevent complete producer closure. [timeline](<boot-to-capture-mutation-timeline.md>). |
|Critical82000 |**UNKNOWN** — exact unresolved settings cleanup/save → FAT metadata/data →1A7AC/1AF1E routes named in [separate matrices](<target-preservation-matrix.md>). |
|Identity81000 |**UNKNOWN**, separately assessed. Identity setter's own erase ends82000; identity-only uncertainty is not used to block82000. |
|Final candidate designation |Withheld. No new firmware, no final-package hashes, no documentation promotion. Exact tested BIN authenticated as Phase44 research artifact only. |

## Reused evidence and validation boundary

native-cases.json (local-only reference: `builds/phase46-msd-filesystem-closure/native-cases.json`; not distributed) persists three native application decompressions plus boot decompression/descriptor extraction, two native settings-mode cases,18 SCSI rejections, native synthetic FAT mount/cluster conversion/two f_write paths, and three settings startup producer cases. [native_cases.py](<../../../builds/phase46-msd-filesystem-closure/native_cases.py>) states every seam: modeled disk I/O, constructed FIL records, USB registration seams, and deliberately invalid settings validation/defaults seams. These are not represented as complete cold boot, directory lookup or physical storage tests.

The [Phase45 independent atomicity review](<../phase45-nor-mutation-closure/atomicity-patch-review.md>) and [named update/rollback dependency results](<../phase45-nor-mutation-closure/update-noop-review.md>) remain valid in their scopes; no new finding invalidates them. They were reused, not rerun. Phase45's eight lower MSD tests/five mapper tests also remain valid; their interpretation is narrowed by real SCSI protection and strengthened by accepted filesystem input tests.

The exact research BIN used here has SHA-256`0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738`. The conditional final-SYX admission step is not invoked because storage closure did not pass. A hash is not a designation. check-evidence.json (local-only reference: `builds/phase46-msd-filesystem-closure/check-evidence.json`; not distributed) verifies prior saved evidence/source preservation and report links; it is not firmware admission.

## Decision table

| Category | Remaining item |
|---|---|
|**BLOCKERS BEFORE FLASHING** |Complete actual pre-capture filesystem geometry/allocation and startup/dirty producer closure, or demonstrate a sufficient invariant at the physical disk interface. Native oversized-volume acceptance means “FatFs checks LBAs” is no longer an adequate proposed proof. Close malformed-BOT state/continuation and callback lifetime invariants if claiming universal host-input isolation. Critical82000 remains UNKNOWN, so candidate stays undesignated. |
|**SHOULD VERIFY** |Independently review the constant write-protect table slot, the new startup settings DELETE route, native mount/f_write countermodel and modeled seams. Review callbacks by decompressed data, not raw-flash pointer scanning. Keep81000 and82000 provenance separate. Preserve existing atomicity/update evidence. |
|**ACCEPTABLE HARDWARE-ONLY UNKNOWN** |Actual USB/IRQ/DMA timing, NOR faults and actual fresh heap/stack margins remain untested. User-reported bootloader entry/normal return is not rollback-flashing evidence. These do not resolve an offline filesystem proof gap. |

**Smallest next offline experiment:** follow the native settings constructor`0802CFB8 → 0802D060` and registered changed-settings callback`0802D278` through real type0 file lookup/delete/save/flush with explicit accepted FAT geometry constraints, recording every disk0 LBA/count into1AF1E. First close or reject the oversized-volume/allocation predicate; do not spend another run proving only that one healthy fixture happened not to write. A completed real-unit preservation claim additionally needs authenticated relevant filesystem geometry/allocation provenance, or an independently justified invariant excluding target-reaching writes. No target bytes may be guessed to get there. This report does not authorize a new build or hardware action.

PREFLASH STORAGE CLOSURE = UNQUALIFIED
