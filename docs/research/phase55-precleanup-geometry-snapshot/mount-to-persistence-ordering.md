> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase55 — mount to first persistence

**PROVEN:** the application Main task calls0801F0A8 at0801D4C0, then content/settings initialization0801F0F0 at0801D4C4.1F0A8 binds NOR disk20000AA0 to[20006968] and invokes its initialization vtable,0801ADDC. It then initializes the separate SD disk20001AF4. This is synchronous Main initialization, not a new Storage job. Mount's sector reads are serviced through the existing disk/Storage path. app-0801d4b0.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-0801d4b0.asm`; not distributed), app-0801f0a8.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-0801f0a8.asm`; not distributed), app-0801addc.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-0801addc.asm`; not distributed); prior task context: [writer-ordering.md](<../phase54-early-evidence-snapshot/writer-ordering.md>).

**PROVEN:**1ADDC builds0:, calls08019A92(fs=disk+10,path,opt=1) at0801AE02.19A92 clears the old and new FS types at19AB6/19ABE, registers the pointer at19AC2, then calls197A0. The mount validates and assigns BPB-derived geometry. On the full successful parse,19A32 commits FAT type,19A40 writes mount ID,19A46 writes synchronization pointer and19A4A clears an internal field. At19A4C all these are complete and R0=0. At the caller **0801AE06** the complete successful mount has returned, before logging and before the next SD mount or content/settings construction. The common19A4C is also an error/fast-path exit and is not by itself a success-only hook. app-08019734.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-08019734.asm`; not distributed), app-08019a32.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-08019a32.asm`; not distributed), app-0801addc.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-0801addc.asm`; not distributed).

**PROVEN YES — a deterministic instruction window exists in the native synchronous Main path:**

`NOR mount success → 0801AE06 snapshot boundary → return from1ADDC/1F0A8 → 0801D4C4 content/settings construction → conditional persistence`.

This is a proof of the instruction window and ordering of these producers, not a universal no-other-task-write theorem. **UNKNOWN:** complete preemption/deferred-job closure across all normal boot roots has not been established. No full cold boot is claimed. A qualification requiring that no normal asynchronous persistence has already run must still establish that startup queue/root invariant, or place acquisition under an existing correctly owned mount exclusion. No long interrupt masking is proposed to hide this obligation.

| Producer | Earliest established edge relative to window | Result |

|---|---|---|

|Mount itself |19734 clears dirty flag before loading boot sector; BPB parse/optional FAT32 FSInfo read and metadata assignments follow |PROVEN no array-write calls in eight modeled native mount cases; reviewed code is read/parse, not formatting |

|Settings validation |1D4C4→1F0F0, constructor1FAD4→2CFB8→2D060 |PROVEN after Main NOR snapshot point |

|Conditional deletion/flush |2D060 invalid nonempty settings branch→3C97A/3CC54 |PROVEN known first startup persistence producer downstream; conditional, not every boot |

|FAT/directory updates |Unlink1A440→191A8/188E0→18612→1859A, or file writes |PROVEN downstream of initiating filesystem producer; earliest all-task invocation UNKNOWN |

|Settings changed callback |2D052 registration→3BAFC; callback2D278→2D2AC |PROVEN registration in later settings construction; later dirty save cannot precede its own registration |

|Project/session restoration/save |Later constructed content/session objects; stock save path2FE88→3C946 |STRONG INFERENCE normal Main startup is later; UNKNOWN full background scheduling closure |

|SC35D8 persist19 |c_pl_load/c_rs/c_dtick19 RAM/DSP work; c_pl_save funnels stock save |PROVEN no new custom raw NOR writer in reviewed resync; stock save remains separate |

|Deferred USB work |Normal write protection/mode callbacks preserved |PROVEN reused normal-path exclusions; no new malformed-host or late B1.3 timer investigation |

The exact first *physical* write for every boot state is **UNKNOWN**: valid/missing settings may produce no write, while conditional cleanup can. Do not relabel the earliest known producer as a proved exhaustive earliest scheduler event. Sources: [persistence-routes.md](<../phase46-msd-filesystem-closure/persistence-routes.md>), [startup-persistence.md](<../phase47-filesystem-state-closure/startup-persistence.md>), [background-write-analysis.md](<../phase45-nor-mutation-closure/background-write-analysis.md>), [target-preservation.md](<../phase47-filesystem-state-closure/target-preservation.md>).

**PROVEN:** eight fresh native tests run1ADDC and, in one case, the enclosing1F0A8 NOR-then-SD constructor. They include invalid BPB, failed read, not-ready disk, stale geometry, a changed valid layout and mount-ID wrap. No disk program/erase entry executes; mounted geometry is available at1AE06 only on success. Disk data/status/ioctl completion and UART logging are explicit seams. This does not rerun Phase47 or supply actual-unit NOR bytes. [audit.py](<../../../builds/phase55-precleanup-geometry-snapshot/audit.py>), mount-cases.json (local-only reference: `builds/phase55-precleanup-geometry-snapshot/mount-cases.json`; not distributed).
