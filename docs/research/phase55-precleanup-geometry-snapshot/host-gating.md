> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase55 — export, host admission and same-boot lifetime

**STRONG INFERENCE:** reuse rdiag framing, padded request validation, nibble encoding, checked transaction token, frame CRC and native USB router. Add a fixed geometry-only command returning the saved46 bytes plus version/magic, GEOMETRY_VALID/FAILED, mount-success/binding provenance and a software epoch. A bounded record fits the historical64-byte payload limit if header design stays within18 bytes; larger metadata needs checked fragmentation. Do not expose arbitrary RAM addresses or preserve an alternate live-Storage fallback. Exact command ID/wire encoding/export code are not allocated or implemented. Historical transport hardware evidence and prior offline command qualification are not hardware qualification of this new command. rdiag.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/rdiag.py`; not distributed), [findings.md](<../phase42-exact-rdiag-integration/findings.md>).

The geometry command reads the **retention record only**, never initiates Storage/NOR/SD/filesystem work and never automatically starts raw evidence acquisition. Snapshot pointer/binding checks happen at the mount hook. Remount/binding invalidation must update volatile validity/epoch when the underlying owner changes; a host token alone cannot establish that lifecycle. Packet CRC protects the transmitted record, not a missing RAM ownership proof.

**STRONG INFERENCE — future workflow, not present authorization:**

1. A separately qualified future build boots and captures native geometry before persistence.

2. USB becomes ready; host asks for the fixed snapshot only.

3. Host requires success/validity, expected version/code identity, fresh-mount/binding provenance, coherent epoch, exact46 bytes and CRC.

4. Validate native FAT class/count/size, sector/cluster constraints, root/data relationships and bounded nonwrapping physical mappings. Derive FAT copies, root/data and FAT32 FSInfo domains, expanding to physical erase boundaries where relevant.

5. Evaluate81000..81016 and82000..821FF independently. If82000 file-backed mutation is excluded and the retained non-filesystem exclusions and same-boot epoch still hold, host MAY admit the separate one-shot read. Geometry export itself does not admit/send it.

6. If unsafe, invalid or unknown: send no NOR evidence request. The future policy calls for restoring normal firmware by the separately qualified recovery procedure; no automatic cleanup/reset/restore is issued or certified here.

**PROVEN:** the native mapper computes32-bit base+stride*LBA. The supplied-record policy conservatively requires baseD4000, stride/BPS4096 and all normal domains within the reviewed32MiB bound, excluding wrap and both targets. For the modeled mounted FAT16 it derives FAT[D5000,DD000), root[DD000,E1000), data[E1000,2000000), so both target intervals are excluded. This reproduces Phase47 arithmetic, not an actual-unit conclusion. The physical capacity bound is a conservative acceptance condition; no new capacity query occurs. [geometry_parser.py](<../../../builds/phase49-existing-geometry-reader/geometry_parser.py>), [host_gate.py](<../../../builds/phase55-precleanup-geometry-snapshot/host_gate.py>).

**PROVEN:** nine pure host-gate tests accept authenticated-model layout, valid changed layout and fresh-success zero ID; reject nonzero mount status, invalid state, old mount, wrong backend, changed epoch and truncated record. Provenance booleans are explicit modeled inputs, not acquired attestation. `allow_raw_evidence=True` in these synthetic cases is not authorization to access this unit. host-gate-cases.json (local-only reference: `builds/phase55-precleanup-geometry-snapshot/host-gate-cases.json`; not distributed).

## Same-boot reasoning

**PROVEN, conditional mapping theorem:** with fixed registered FS/binding/base/stride and validated nonwrapping geometry, later normal FAT/directory/data/FSInfo writes remain inside those same domains. Settings deletion, flushing, file creation and allocation change entries/dirty state, not the geometry used to bound all valid clusters. Therefore they need not be prevented or delayed while the host examines the saved record. The exclusion also applies to writes made after snapshot but before USB/host acceptance. The conclusion does not rely on one particular file cluster. [real-filesystem-geometry.md](<../phase47-filesystem-state-closure/real-filesystem-geometry.md>), [startup-persistence.md](<../phase47-filesystem-state-closure/startup-persistence.md>).

**UNKNOWN — unconditional same-boot admission:** the future implementation must invalidate the snapshot on unmount/re-registration19A92, a changed binding1AE3A or sector-stride assignment1AEDE, and on reset. It must keep the raw command disabled if invalidated after geometry export but before the later raw request. Reuse the existing one-shot raw-capture latch/no-retry policy and add this epoch admission predicate; merely remembering that USB stayed connected is insufficient. Normal captures under an unchanged mounted epoch are architecturally plausible, but this lifetime interlock is not implemented/qualified. app-0801ae90.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-0801ae90.asm`; not distributed), [live-geometry-structure.md](<../phase49-existing-geometry-reader/live-geometry-structure.md>).

## Separate evidence-region decisions

**PROVEN conditional:** validated mapping excludes file-backed writes to both81000 and82000 in the model. **UNKNOWN:** current-unit acquisition and full pre-snapshot ordering. Identity-specific explicit writer25228/boot05DB4 programs81000 and erases[81000,82000), whose upper bound does **not** touch82000. Identity historical semantics therefore need not veto coefficient-only capture if shared prerequisites pass. The current combined23+512 command remains all-or-nothing until separately changed/qualified; do not silently call its identity output authenticated while relaxing that gate. [target-preservation.md](<../phase47-filesystem-state-closure/target-preservation.md>), [evidence-preservation.md](<../phase44-preflash-redteam-closure/evidence-preservation.md>).

**PROVEN:** C retains late raw-read H4 exposure. TEF/missing completion has no qualified bounded unwind: host discards partial output, does not retry/send another request/cleanup, and requires a power-cycle boundary under the established containment policy. No safe reboot/rollback proof is added by geometry capture. Geometry-command timeout alone adds no diagnostic Storage transaction; it still must not admit a raw request. [findings.md](<../phase31-storage-error-recovery/findings.md>), [findings.md](<../phase32-host-containment/findings.md>).
