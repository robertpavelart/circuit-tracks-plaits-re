> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase47 — normal callback/persistence flow only

**PROVEN:** candidate scatter descriptor0805B7C8 decompresses initialized data from0805C3C4 into20000000 through native080596C4 before application constructors. Phase46 tested exact candidate/stock/B1.3 bytes and found identical table data. Reuse those persisted results; no callback corruption/redirection analysis is undertaken.

| Pointer/control route | Expected target and legitimate caller | Normal operation / destination |
|---|---|---|
|200037AC →20003788; slot+C at20003794 |08057E49, returns write protected; SCSI admission0803B5AA |Ordinary initialized WRITE10 requests rejected before mutation; reused Phase46 evidence |
|Slot+14 at2000379C |08057EF5; SCSI write continuation uses this slot |Lower writer is a capability, not an ordinary admitted write. No new malformed-state investigation; no normal pre-capture write demonstrated here. |
|Slot+1C at200037A4 |08057FB5; legitimate SCSI eject0803B758 |Schedules248CE timer callback248B4→38C54; modes0/1 stable, class/mode RAM reapplication, no array write in this callback |
|Settings observer ROM0805C0D8 |08029E01; constructor29DDC registers with35398 |Reads setting record2 bit17 and chooses normal USB mode0/1; no direct storage program/erase |
|Settings manager ROM0805BAB0 |0802D279; constructor2CFB8 publishes vtable and registers object via3BAFC; subscriber dispatcher3BB12 |Normal changed-state predicate2D300→save2D2AC→content op7 +flush. Internal settings file on NOR; normal physical volume`[D4000,2000000)` if reconstructed geometry holds. Can run before capture when dirty. |
|Startup settings load |Direct constructor2CFB8→2D060, not an initialized MSD callback |Invalid nonempty settings conditionally deletes type0/index0 and flushes; same normal filesystem range |
|Persist19 |Actual SC35D8 retained c_pl_load/c_rs/c_pl_save |Load/resync RAM/DSP; save funnels into stock session file path. Internal pack0 uses bounded NOR volume, other packs SD; no extra raw target write. |
|Identity edit callback |App25228 / boot05DB4 registered during identity object construction |Requires explicit identity-edit command, outside planned normal capture sequence;23-byte write81000, erase`[81000,82000)`. Registration and RAM byte14 normalization do not write NOR. |

**PROVEN scoped:** initialization and expected normal targets. **STRONG INFERENCE:** ordinary control flow preserves these targets and uses the reviewed paths. An absence-of-pointer-corruption theorem is not required or claimed under the latest normal-path scope. The remaining actual-unit uncertainty is filesystem geometry, not an unidentified target for the MSD table.

Evidence: [Phase46 initialized provenance](<../phase46-msd-filesystem-closure/initialized-ram-callback.md>), [Phase46 normal MSD paths](<../phase46-msd-filesystem-closure/msd-reachability.md>), Phase46 settings subscriber listings (local-only reference: `builds/phase46-msd-filesystem-closure/app-0802d280.asm`; not distributed), Phase47 native state results (local-only reference: `builds/phase47-filesystem-state-closure/normal-states.json`; not distributed).
