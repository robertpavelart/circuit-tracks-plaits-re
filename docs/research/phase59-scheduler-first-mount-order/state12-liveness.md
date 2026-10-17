> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase59 — 12-byte ownership

**PROVEN new bounded evidence:** marker0123456789ABCDEF55AA55AA at20044D70..20044D7B remains byte-identical with zero narrow write intents in all9 new runs. Reservation uses existing allocator limit20002B44=D70, before constructors. No new RAM capacity is allocated for lifecycle state. Tests exercise native startup/task creation/selected SysTick/queue/mount paths. They do **not** contain a committed geometry record or execute adapted export/authorization/raw capture. case-summary.json (local-only reference: `builds/phase59-scheduler-first-mount-order/case-summary.json`; not distributed), [native_startup.py](<../../../builds/phase59-scheduler-first-mount-order/native_startup.py>).

|Known owner|Native access / lifetime obligation|

|---|---|

|Getter6B6CC|6B708 clears+4;6B70A clears+8;6B714 writes oldNOR4magic;6B722 later checksmagic. Under earlyD70 reservation with new control format, mismatch returns0 at6B744 rather than admitting export. Merely preventing clears does not make the diagnostic usable.|

|SysTick6B748|Reads old magic/state/start,6B794 writes quarantine byte+4 only if old schema ACTIVE and elapsed>=5000; new schema must replace interpretation. Marker test takes magic-mismatch path, not every old state branch.|

|Admission6B798|6B820 writes state+4;6B824 session+5;6B830 tick+8. These collide with geometry until atomic schema handover is implemented.|

|Raw6B850|6B8DA chunk+6;6B8DE/6B924/6BA02 owner+7;6B9FE failure+4; required postauthorization overlay only.|

|Corrected terminal|6BC46 success+4 underPRIMASK; old6B9EC bypassed by6B9DC, not counted as live.|

|Allocator / task stacks|Native allocations below reserved limit in bounded runs; stack/dma/global aliases through USB/export/authorization are not globally closed.|

Per-byte source of truth: ownership.json (local-only reference: `builds/phase57-first-mount-provenance/ownership.json`; not distributed); native getter/timeout bytes: app-0806b6cc.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-0806b6cc.asm`; not distributed). Existing collision tests: liveness-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/liveness-tests.json`; not distributed).

**UNKNOWN adapted native liveness:** no coordinated native BOOT→MOUNTING→VALID→EXPORTED→ACTIVE initializer, mount commit, getter, timeout, authorization and raw/terminal adaptation exists in the tested image. Geometry must remain immutable through authorization, then payload+4..11 may become transport fields; control epoch/failure must not be overwritten by late completion. Existing abstract lifecycle/isolated commit helpers are not a substitute. [adapted-ownership.md](<../phase58-preconstructor-liveness-closure/adapted-ownership.md>).

**UNKNOWN global unexpected writers:** all indirect range copies, task/IRQ stack high water and DMA descriptors after snapshot remain unclosed. No earlier phase is superseded by a marker-only run. This required gate remains open even if pre-mount producer exclusion is later closed.
