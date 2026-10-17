> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase47 — legitimate startup persistence

**PROVEN:** the object being validated is global settings file **`0:/Tracks/Globals/00_GLOB.cg`**, expected length128. This is not a project session or the23-byte identity record. Native path resolution`0803B08C` on the authenticated fixture's internal volume/global index produces that exact path; settings manager object is`2003974C`. Native validator`0802D108` accepts its existing128-byte RAM settings snapshot. geometry-provenance.json (local-only reference: `builds/phase47-filesystem-state-closure/geometry-provenance.json`; not distributed).

Startup constructor`0801FAD4 → 0802CFB8 → 0802D060` queries type0/index0 settings size. Length128 leads to read and validation. Successful validation skips deletion. Missing/zero-size state uses RAM defaults and skips deletion. Nonzero length mismatch or failed validation uses defaults and requests`0803C97A`, which submits DELETE op5 synchronously (null completion callback), followed by flush op8 through`0803CC54`. It does not delete on every boot.

`08036D26` resolves type0 through internal volume`[2000690C]` and index0 path, then file vtable+C →`08025D32 → 0801A440` (native unlink). Unlink marks the directory entry deleted through`080191A8`, frees the file's FAT chain through`080188E0`, and calls`08018612` to flush. The dirty window flag`fs+3` controls writes in`0801859A`; two FAT copies are updated when the window belongs to FAT1. Removing a file does not erase its former data clusters in the tested normal FAT16 route. Future legitimate allocation can reuse those freed clusters; all valid clusters remain within the data range.

**PROVEN scoped native execution:** `normal_states.py:Model.startup` executes the actual startup producer, native validation and native FatFs read/close operations on a coherent FAT16 directory model. Content-service responses form an explicit boundary; delete/flush native execution is tested separately on a valid normal file. This is not a scheduler/queue replay. The hardware configuration query35756 is modeled; no device is read.

| State / normal operation | Native observations | Physical write set in the model |
|---|---|---|
|Valid settings |SIZE128 →READ →actual validator accepts |None |
|Missing settings |Native read-only open returns missing; startup SIZE0 →defaults |None |
|Fresh empty file |Native open-always +close creates empty entry; startup SIZE0 →defaults |Creation writes directory`E2000,E3000)`; subsequent startup adds no writes |
|Ordinary dirty valid settings |Actual validator accepts changed payload; f_write128 +close/sync |Data`[E3000,E4000)` and directory`[E2000,E3000)` |
|Normal deletion mechanism |Native unlink of valid file at model cluster4 |Directory`[E2000,E3000)`, FAT1`[D5000,D6000)`, FAT2`[D9000,DA000)`; no freed-data write |
|Rejected settings cleanup |Conditional branch already established by Phase46 |Same deletion/sync mechanism if reached. Its **actual normal-state provenance remains UNKNOWN**; this phase does not invent a corrupted file to make it run. |

The model allocates Tracks/Globals/file to clusters2/3/4 with proper dot/parent entries. These are coherent valid allocations within the authenticated geometry, **not** the actual fixture's directory or user's file allocation. The exact normal global-settings file cluster in the real unit is **UNKNOWN**. The all-cluster range proof does not depend on it.

Normal persistence callbacks: settings subscriber is registered by`0802D052 → 0803BAFC`, vtable slot`0805BAB0=0802D279`; comparison`0802D300` triggers save`0802D2AC` only when changed. It writes128 bytes through content op7 and flushes. Main-side calls queue/wait for Storage operations; underlying file/NOR mutation runs on Storage. Startup cleanup can be requested during constructor execution before normal USB-ready/capture. Exact elapsed time is **UNKNOWN**; waiting is not an exclusion argument.

For the reconstructed volume, normal data/FAT/directory/metadata writes and their aligned sector erases all stay`[D4000,2000000)`. Normal project/session restoration may read/apply state and later dirty settings; its file-backed writes inherit the same range for internal pack0, while other packs use SD. The SC35D8 custom persist19 resync is RAM/DSP; its save hook copies extension state before stock session saving, without a new raw NOR destination. No later B1.3 persistence timer is assumed inherited.

Listings: [unlink/chain freeing (local-only reference: `builds/phase47-filesystem-state-closure/app-0801a440.asm`; not distributed), file delete adapter (local-only reference: `builds/phase47-filesystem-state-closure/app-08025d10.asm`; not distributed), global file writer (local-only reference: `builds/phase47-filesystem-state-closure/app-08036b1c.asm`; not distributed); startup/control listings and source hashes remain in [Phase46 persistence-routes.md](<../phase46-msd-filesystem-closure/persistence-routes.md>). No earlier evidence was overwritten.

**UNKNOWN:** user-unit geometry and specific physical settings allocations. No complete actual-unit boot trace was produced. The physical ranges above are native model outputs, not acquired evidence from the unit.
