> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase59 — Storage startup

**PROVEN native path:** Storage entry5767C runs after Main/UI in the modeled ready-list schedule. It binds SD completion waiter5765A and NOR waiter57650 via each wrapper's vtable+20. It then waits flag1 at576A0, drainsSD at576A6, drainsNOR at576B0, repeats. Waiter57650 consumes notification100; notifier57664 uses100/101. The worker does not invent a read until a producer supplies a record. app-08057650.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-08057650.asm`; not distributed), app-08023f2c.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-08023f2c.asm`; not distributed).

**PROVEN observed requests before snapshot:** identity read81000..81016; geometry control query returning4096-byte stride; BPB readD4000..D4FFF for the successful synthetic case. No request to82000..821FF is made. The identity read occurs before first mount. A queue item can precede Storage's first activation: Main's identity submission is processed once Storage registers/waits; preserved object notification flags carry the wake. modeled-valid-startup.json (local-only reference: `builds/phase59-scheduler-first-mount-order/modeled-valid-startup.json`; not distributed).

**PROVEN capability:** op2 and op3 worker branches can program/erase the NOR through22FDC/23078 and374D4/37494/37648; optional callbacks can reach other code. The worker alone supplies no address-range protection that proves upstream producers safe. Normal replay exercising only op0/1 is not a complete mutation proof.

**PROVEN delay test:** delayed completion leaves the read/wait active until a modeled completion notification is delivered using native1BDE8. Native ready-list removal/reinsertion and semaphore restoration execute; no host forced semaphore release is used. This is successful-completion scheduling evidence, not an error-unwind test and does not supersede H4. delayed-storage.json (local-only reference: `builds/phase59-scheduler-first-mount-order/delayed-storage.json`; not distributed), [findings.md](<../phase31-storage-error-recovery/findings.md>).

**UNKNOWN:** full earliest USB/timer/Content producer closure and actual controller ISR arbitration, so target preservation remains unqualified separately for both NOR regions.
