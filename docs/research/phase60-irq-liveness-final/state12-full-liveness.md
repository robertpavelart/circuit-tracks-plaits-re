> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase60 — full-lifetime writer census

**PROVEN known owner ledger:** the existing12-byte record is20044D70..D7B. The saved per-bytePhase57 ledger contains23 known direct accesses; it is preserved and referenced rather than rescanned as if new. Phase60 adds native owner semantics and actual first-mount scalar collection, but does not claim a globally complete alias/range proof. ownership.json (local-only reference: `builds/phase57-first-mount-provenance/ownership.json`; not distributed), owner-model-tests.json (local-only reference: `builds/phase60-irq-liveness-final/owner-model-tests.json`; not distributed).

|Lifetime / writer|Exact old path|Adapted obligation / evidence|

|---|---|---|

|Early initialization|6B708 clears+4;6B70A clears+8;6B714 old magic|Native init fragment clears all12 before publishing allocator limit; later idempotent invocation preserves geometry|

|Getter / USB ready|5DBCC→6B6CC;6B722 reads magic|Getter model never writes12; real getter currently rejects new control rather than implementing export|

|SysTick / timeout|5998C→6B748;6B794 writes+4|Native new tick readsACTIVE/start tick and changes only control toFAILED|

|Parser/SysEx admission|24D2C→6B798;6B820/+4,6B824/+5,6B830/+8|Compare same epoch and all8 geometry bytes before transport overlay; native fragment tested, call-site wiring not installed|

|Raw transaction|6B850;6B8DA/+6;6B8DE/6B924/6BA02/+7|OnlyACTIVE overlay; actual chunk/USB/Storage callbacks still require adapter integration|

|Failure/quarantine|6B9FE/+4|Control FAILED absorbs late completion; owner retained|

|Corrected completion|6B9DC bypasses6B9EC;6BC46 stores+4|New complete fragment checksACTIVE and updates control; old byte store must be redirected|

|Mount snapshot/epoch|1AE06;197A0/19A92;1AE3A/1AEDE|Actual record collected; begin/commit/invalidate fragments tested; native invalidator/commit hooks not wired|

|Range-based init/copy|Scatter source[20000000,20003D02),zero[20003D04,20006A54)|ExcludesD70, previously qualified; unchanged|

|Heap / stack / DMA|1D7D0 allocator; active task stacks; DMA destinations|Early limitD70 honored in existing fixtures; new native helper stack36 bytes; tested reads excludeD70. Post-mount USB/range-copy aliases are not fully traced through old raw/parser callbacks|

**PROVEN geometry liveness in the adapted native model:** actual first-mount46-byte scalars are collected from20000A98,20000AB0 and20000AD0, packed losslessly with the preservedPhase56 codec, copied into the private payload by native commit, exported byte-for-byte and compared again by native authorization. NonACTIVE tick, getter, parser-reset model and host wait preserve them. The model's parser-reset is an explicit no-write owner operation, **not execution of every real parser-reset callback**. [adapted_owner.py](<../../../builds/phase60-irq-liveness-final/adapted_owner.py>), owner-export.asm (local-only reference: `builds/phase60-irq-liveness-final/owner-export.asm`; not distributed), owner-authorize.asm (local-only reference: `builds/phase60-irq-liveness-final/owner-authorize.asm`; not distributed).

**UNKNOWN full native lifetime:** the actual24D2C→6B798/6B850 paths and their reset/range-copy/late completion descendants have not been redirected and replayed with this union. No whole-image USB-ready→geometry-export→host-decision→raw pipeline is claimed. Existing collision evidence remains relevant, not superseded: liveness-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/liveness-tests.json`; not distributed).

The record's8 geometry bytes become dead only after successful atomic authorization, not on export. The later8-byte transport overlay is intentional lifetime reuse, not simultaneous independent authorization storage.
