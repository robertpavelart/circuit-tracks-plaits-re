> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase47 — normal state coverage and limits

Latest instruction narrows this phase to normal valid firmware/filesystem behavior. No malformed BOT/CBW, protection circumvention, pointer redirection or arbitrary storage-access experiment was performed. The earlier request for malformed-host tests is superseded.

The test uses the authenticated mounted FAT16 geometry rather than generic FAT32 defaults. Minimal directories are modeled coherently: root Tracks cluster2, Globals cluster3, optional settings cluster4. Each subdirectory includes dot/parent entries. Allocated chains terminate normally; absent file leaves cluster4 free. These allocations are permitted by real geometry, not claimed to be a dump of actual directories. Native file lookup/open/read/write/unlink/sync run; disk reads/completions and the startup content-service boundary are explicit models. [normal_states.py](<../../../builds/phase47-filesystem-state-closure/normal_states.py>).

| Coverage | Provenance / result | Confidence |
|---|---|---|
|Clean valid filesystem, valid settings |Settings payload copied from authenticated RAM object+8; native validator returns1; native read/close then startup SIZE/READ |PROVEN within native model: no writes |
|Missing settings |Native read-only open returns4; actual startup zero-size/defaults branch |PROVEN within native model: no writes |
|Native-created empty settings file |Stock-compatible open-always flag13 creates empty directory entry; native close persists it; actual startup zero-size/defaults branch |PROVEN mechanism: directoryE2000 sector created, no additional startup writes; not a claim of an interrupted save on hardware |
|Ordinary dirty valid settings |Change project selection byte0 from0 to1 in authenticated payload; actual validator still returns1; native f_write/close |PROVEN native data+directory writes atE3000/E2000; no target overlap |
|Normal file deletion |Native unlink on valid allocated file |PROVEN native directory and both FAT updates; no target overlap or data-sector erase |
|Settings rejected by normal validation |Conditional validation/delete path exists; exact file state that normal completed firmware operations produce and reject was not authenticated |UNKNOWN provenance. Not counted as a demonstrated realistic startup execution. No new fabricated invalid settings state is admitted as normal evidence. Deletion mechanism separately bounded by native tests and geometry. |
|On-disk FAT clean-shutdown/dirty bit |Fixture has RAM cache dirty0 and FSInfo flag80; those are not proof about FAT clean-shutdown bits |UNKNOWN actual on-disk flag. Ordinary RAM dirty-cache behavior is tested; no unsupported automatic repair routine is invented. |
|Partially written settings |Native API can create an empty file before data; model demonstrates this ordering |PROVEN API mechanism, STRONG INFERENCE an interrupted creation can leave an empty file. No power-loss/partial-sector model or nonzero truncated record claimed. |

`normal-states.json` contains four native file-operation cases and three startup cases. Every emitted physical write has kind, address/end, erase-first request and target-overlap flags. Backend completion is modeled at24164; this is an observation of native submitted ranges, not physical flash behavior. Model read-only opens do not create missing files; open-always is used only in the explicit creation/write cases.

Additionally, native cluster conversion is tested for all7967 valid data clusters. This range result covers normal allocation, extension and chain reuse under this geometry without needing to fabricate a file in every cluster. It does not establish the current user's volume fields or every possible boot schedule.

The exact Phase46 synthetic FAT32 model is not a realistic state of the reconstructed FAT16 volume. That exclusion is **PROVEN scoped**. The extension to the present user unit remains **UNKNOWN** without its geometry provenance or a firmware/default-format invariant.

Evidence: normal-states.json (local-only reference: `builds/phase47-filesystem-state-closure/normal-states.json`; not distributed), geometry-provenance.json (local-only reference: `builds/phase47-filesystem-state-closure/geometry-provenance.json`; not distributed), fixture-geometry.json (local-only reference: `builds/phase47-filesystem-state-closure/fixture-geometry.json`; not distributed).
