> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase58 — exact adapted ownership contract

**STRONG INFERENCE:** retain exactly the existing12 bytes. No extra heap allocation/reservation. Before constructors, initialize BOOT/epoch0 after checking old allocator contract; publish limitD70 only after a fully initialized record, preserving incoming mask. Later getters validate reservation/control and initialize only separate Master-FX storage, never clear the diagnostic record. This early initializer and later adapters are a specification, not emitted code.

|Byte |After first valid mount, through authorization |Writers in that phase |Readers in that phase |After atomic authorization |

|---|---|---|---|---|

| raw instruction bytes omitted |Control byte0:phase/unexpected-event/epoch|Boot init; normalized mount guard; commit; export/admission; timeout/terminal|Getter/schema guard; mount hook; SysTick; export/admission; raw terminal|Same control byte; never payload|

| raw instruction bytes omitted |Control byte1:phase/unexpected-event/epoch|Boot init; normalized mount guard; commit; export/admission; timeout/terminal|Getter/schema guard; mount hook; SysTick; export/admission; raw terminal|Same control byte; never payload|

| raw instruction bytes omitted |Control byte2:phase/unexpected-event/epoch|Boot init; normalized mount guard; commit; export/admission; timeout/terminal|Getter/schema guard; mount hook; SysTick; export/admission; raw terminal|Same control byte; never payload|

| raw instruction bytes omitted |Control byte3:phase/unexpected-event/epoch|Boot init; normalized mount guard; commit; export/admission; timeout/terminal|Getter/schema guard; mount hook; SysTick; export/admission; raw terminal|Same control byte; never payload|

| raw instruction bytes omitted |Canonical geometry byte0|First-mount copy only; immutable VALID→EXPORTED|Fixed geometry exporter and exact-token/digest verifier|Authorized target mask|

| raw instruction bytes omitted |Canonical geometry byte1|First-mount copy only; immutable VALID→EXPORTED|Fixed geometry exporter and exact-token/digest verifier|Session|

| raw instruction bytes omitted |Canonical geometry byte2|First-mount copy only; immutable VALID→EXPORTED|Fixed geometry exporter and exact-token/digest verifier|Chunk|

| raw instruction bytes omitted |Canonical geometry byte3|First-mount copy only; immutable VALID→EXPORTED|Fixed geometry exporter and exact-token/digest verifier|Buffer owner|

| raw instruction bytes omitted |Canonical geometry byte4|First-mount copy only; immutable VALID→EXPORTED|Fixed geometry exporter and exact-token/digest verifier|Start-tick byte0|

| raw instruction bytes omitted |Canonical geometry byte5|First-mount copy only; immutable VALID→EXPORTED|Fixed geometry exporter and exact-token/digest verifier|Start-tick byte1|

| raw instruction bytes omitted |Canonical geometry byte6|First-mount copy only; immutable VALID→EXPORTED|Fixed geometry exporter and exact-token/digest verifier|Start-tick byte2|

| raw instruction bytes omitted |Canonical geometry byte7|First-mount copy only; immutable VALID→EXPORTED|Fixed geometry exporter and exact-token/digest verifier|Start-tick byte3|

RAW-phase writer/read ownership:target/session/starttick only admitted-command setup;chunk/owner only raw worker/USB ownership tracking;tick read by ACTIVE-only timeout;control transitions atomically by timeout/terminal/invalidation. AfterFAILED, owner is retained while Storage/DMA remains active; never release/clear solely to reuse RAM. AfterSUCCESS, ownerfree only after actual output/read release. No second diagnostic transaction or rearm. Geometry is dead **only after authorization**, not merely export.

**PROVEN original-lifetime constraint:** old magic checks remain live indefinitely in current getter/watch, so their values are not naturally dead after mount. All those interpreters must be adapted together; simply assigning the first4 bytes to generation is invalid. Raw session/chunk/owner/tick are dormant before admission but their old storage is still interpreted by initialization/timeout. Their new union ownership begins only after old native access contracts are replaced. [existing-12byte-ownership.md](<../phase57-first-mount-provenance/existing-12byte-ownership.md>).

**STRONG INFERENCE epoch policy:** only expected first NOR mount can turn BOOT→MOUNTING/epoch1→VALID; unexpected earlier root/unmount, later remount/rebind/stride change or changed generation quarantines and disables raw authorization. Cover both19A92 and197A0 slow paths, plus disk-binding/stride writes. New geometry from a later safe epoch is not accepted to certify earlier history. Token binds epoch, exact geometry digest and fresh host session. [epoch-invariant.md](<../phase57-first-mount-provenance/epoch-invariant.md>).

**UNKNOWN:** native store sites/ABI and complete invalidator coverage for this contract. Saved13 strict-first-epoch model cases and12 commit cases are reused at their explicit abstract/local scopes, not rerun as fake new qualification. Original one-shot containment must be preserved by future adapters; no passing full-native adapter suite is claimed.
