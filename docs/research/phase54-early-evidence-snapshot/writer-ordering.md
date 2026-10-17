> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase54 — source-read ordering

**PROVEN:** application order is identity read0801D4B4→1EC80→2520C; filesystem constructor/mount entry0801D4C0→1F0A8; content/settings construction0801D4C4→1F0F0 (includes1FAD4→2CFB8→2D060); initialization/service loop; then0801D582→1F51E→selector0/1F554→1F576→2108C→35E28→82000 read. This straight-line ordering is common to all four inspected application images. This is static instruction-order evidence, not a completed cold-boot scheduler replay. read-inspection.json (local-only reference: `builds/phase54-early-evidence-snapshot/read-inspection.json`; not distributed), app-0801d3e0.asm (local-only reference: `builds/phase54-early-evidence-snapshot/app-0801d3e0.asm`; not distributed), app-0801d550.asm (local-only reference: `builds/phase54-early-evidence-snapshot/app-0801d550.asm`; not distributed), app-0801f0a8.asm (local-only reference: `builds/phase54-early-evidence-snapshot/app-0801f0a8.asm`; not distributed), app-0801f900.asm (local-only reference: `builds/phase54-early-evidence-snapshot/app-0801f900.asm`; not distributed), app-0801f478.asm (local-only reference: `builds/phase54-early-evidence-snapshot/app-0801f478.asm`; not distributed).

| Producer/stage |81000 application snapshot |82000 stock-read snapshot |

|---|---|---|

| Filesystem mount1F0A8 |PROVEN before this Main call |PROVEN after this Main call |

| Settings validation2D060 |PROVEN before this constructor |PROVEN after constructor; valid/missing case can be read-only, but a cleanup branch exists |

| Settings delete/flush |PROVEN before the Main startup producer |UNKNOWN exclusion: conditional startup DELETE+flush precedes this read if selected |

| Settings-change callback/project/session persistence |STRONG INFERENCE later normal Main feature activity; no complete earlier asynchronous exclusion |UNKNOWN ordering of every callback/queued write before first table read |

| MSD |PROVEN inherited diagnostic normal WRITE10 protection rejects mutation; scheduling before A does not defeat that policy |PROVEN same normal write-protection invariant; no arbitrary B1.3 mode assumption or superseded malformed-host blocker |

| Background persistence |PROVEN before the later Main initialization stages; UNKNOWN complete earlier task/IRQ roots |UNKNOWN full stock background ordering; no invented B1.3 autosave timer |

| Updater metadata/installer |PROVEN selected selector0 installation ranges exclude A; no automatic identity rewrite found in reviewed normal boot |PROVEN selected selector0 installation ranges exclude B; no automatic resource rewrite found in reviewed normal boot |

| SC35D8 persist19 resync |PROVEN reviewed custom hook is RAM/DSP work, not raw NOR mutation |PROVEN same; stock file save surrounding it remains a separate obligation |

**PROVEN:** startup settings are0:/Tracks/Globals/00_GLOB.cg,128 bytes. Nonzero invalid settings can request DELETE0803C97A then flush0803CC54 inside initialization. This is an actual producer before the82000 stock read, not a later hypothetical timer. **UNKNOWN:** whether the actual unit selects that branch and whether any normal file-backed writer can reach82000 under that unit's geometry. No such actual target mutation has been demonstrated. [startup-persistence.md](<../phase47-filesystem-state-closure/startup-persistence.md>).

**PROVEN:** Phase47's normal reference FAT16 layout confines file-backed writes to[D4000,2000000); both evidence regions are outside. **STRONG INFERENCE:** a healthy unit retaining that format has the same protection. **UNKNOWN:** the needed current-unit bound/formatter invariant. Phase46's synthetic malformed geometry is superseded as a realistic counterexample; it is not resurrected here. The exhausted Phase53 authentication branch remains closed. Early copying after the82000 stock read does not bypass the missing **pre-read** invariant. [findings.md](<../phase47-filesystem-state-closure/findings.md>); [findings.md](<../phase53-existing-read-final-decision/findings.md>).

**PROVEN:** explicit identity edit25228 writes81000; resource updater selector2 starts82000; boot/application program/erase primitives remain. Selected updater metadata80000 sector ends81000 and does not itself overlap either target. The scoped normal selector0 installation and boot exclusions, and normal MSD write protection, are preserved from Phase47; excluded explicit update/factory/edit commands and arbitrary earlier histories are not reopened as new qualification requirements. A snapshot cannot recover bytes already changed before its read. The bootloader's earlier81000 read helps identify timing but is not retained across application startup by this design. [evidence-preservation.md](<../phase44-preflash-redteam-closure/evidence-preservation.md>), [target-preservation.md](<../phase47-filesystem-state-closure/target-preservation.md>), [persistence-routes.md](<../phase46-msd-filesystem-closure/persistence-routes.md>).

**PROVEN:** the diagnostic inherits SC35D8 persistence, not late B1.3 features: persist19 load/new set RAM flags; c_rs/c_dtick19 update RAM/DSP; save extension hook precedes stock file persistence. No later15/30-second timer is imported. [background-write-analysis.md](<../phase45-nor-mutation-closure/background-write-analysis.md>).

**UNKNOWN — overall pre-mutation ordering for both targets is not qualified.** A read/snapshot point before application mount is identified for81000. For82000 the proposed available stock read is too late to establish the requested simple read-before-all-filesystem-writers proof. Smallest next ordering experiment: trace the bounded Main path from1F0F0 through first35EE6, including accepted settings cleanup/content jobs and deferred callbacks, and establish a target-independent physical write exclusion. If no such invariant exists, the copy-only-after-existing-read design cannot meet its stated preservation goal. Do not reopen host MSD authentication or attempt a complete peripheral cold-boot emulation first.
