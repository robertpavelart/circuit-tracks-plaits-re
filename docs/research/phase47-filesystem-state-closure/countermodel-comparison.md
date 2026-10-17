> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase47 — exact Phase46 model versus normal geometry

**PROVEN:** the exact Phase46 FAT32 state is invalid for the authenticated reference device's normal FAT16 geometry. **UNKNOWN:** whether this user's current volume has that same geometry. No attempt to force or redirect invalid states was made in Phase47.

| Prerequisite | Phase46 state | Normal reference constraint | Classification |
|---|---|---|---|
|FAT type |3/FAT32 |2/FAT16 |INVALID FOR REAL DEVICE GEOMETRY, scoped to fixture |
|Total sectors |110000 |1F2C |INVALID FOR REAL DEVICE GEOMETRY |
|FAT entries |10F001 |1F21 |INVALID FOR REAL DEVICE GEOMETRY |
|Data start |1001 |D |INVALID FOR REAL DEVICE GEOMETRY |
|Target-reaching cluster |FEFAE / FEFAF |2..1F20 |INVALID FOR REAL DEVICE GEOMETRY |
|FAT-chain entry |No actual chain supplied; constructed FIL starts at selected cluster |Normal FAT16 links and native cluster checks constrain traversal to mounted valid range; native directory/FAT interpretation does not establish the constructed FAT32 start cluster |INVALID FOR REAL DEVICE GEOMETRY for those exact cluster values |
|Volume start |0 |0 |VALID NORMAL STATE |
|Partition/base binding |NOR / D4000 |NOR / D4000 |VALID NORMAL STATE |
|Sector / cluster size |4096 /1 sector |4096 /1 sector |VALID NORMAL STATE |
|FIL mount ID |Copied from successful synthetic mount |Copied from native open/current mount, fixture ID2 |VALID NORMAL STATE as a consistency mechanism; it does not validate physical capacity |
|FIL start cluster |Explicitly constructed far above normal limit |Must come from real file lookup/allocation; normal cluster predicate rejects it for this geometry |INVALID FOR REAL DEVICE GEOMETRY |
|File pointer and size |0 before4096-byte write |Normal file may start at offset0 and extend |VALID NORMAL STATE alone; it cannot make an invalid cluster valid |
|Cached current sector / dirty |Constructed zero/clean values |Normal open initializes FIL; sync writes valid cached sector only when dirty |VALID NORMAL STATE alone; no reachability proof from these values |
|Directory entry |Not produced by native directory lookup |Normal file open must find/create a directory entry in the actual filesystem |UNKNOWN provenance in Phase46; not claimed as an authentic entry |

Normal extension and FAT-chain reuse choose/traverse valid clusters; normal deletion frees the chain and updates directory/FAT records. Neither changes the VBR into the oversized Phase46 volume. Under the fixture geometry, all permitted clusters have been enumerated through native18698, so changing file offset, chain position or settings contents cannot reproduce the exact Phase46 cluster addresses. This is a range argument, not merely no-write observation.

The Phase46 test remains valid in its stated scope: the native mount/writer lacks a universal physical-capacity check for arbitrary accepted BPBs. It does **not** show that normal Circuit Tracks formatting produces that BPB. Phase47 does not extend the investigation to corrupted layouts, malformed requests, or ways to bypass checks.

**UNKNOWN:** exact normal formatter output/current-unit volume provenance. The existing reference RAM proves one genuine device layout, not that every legitimate user-unit layout must match it. Normal data writes, metadata flushes and file deletion cannot establish the initial VBR's identity after the fact.

Evidence: Phase46 native-cases.json `fat` (local-only reference: `builds/phase46-msd-filesystem-closure/native-cases.json`; not distributed), fixture fields (local-only reference: `builds/phase47-filesystem-state-closure/fixture-geometry.json`; not distributed), provenance (local-only reference: `builds/phase47-filesystem-state-closure/geometry-provenance.json`; not distributed), normal native results (local-only reference: `builds/phase47-filesystem-state-closure/normal-states.json`; not distributed).
