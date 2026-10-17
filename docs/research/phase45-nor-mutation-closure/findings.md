> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase45 — resumed NOR mutation closure and independent review

**UNKNOWN: complete ordinary-boot/background mutation-producer closure remains unqualified.** This phase recovered the interrupted work, retained persisted tests and advanced the graph through two previously unclosed producer families. It does not claim the requested exhaustive proof or designate a final hardware candidate.

No hardware access, live port inventory, MIDI open, firmware transmission, Plaits work or candidate generation occurred in Phase45. Historical Phase43 and corrected Phase44 artifacts remain unchanged. **OLD PHASE43 CANDIDATE: SUPERSEDED — DO NOT FLASH.** Preserve it as historical evidence.

## Recovered checkpoint

At resume,21 Phase45 files existed: scripts, listings and JSON evidence; no Markdown reports or final verdict existed. resume-checkpoint.json (local-only reference: `builds/phase45-nor-mutation-closure/resume-checkpoint.json`; not distributed) records their pre-continuation hashes. `update_dependency_review.py` was complete and had persisted results. Independent atomicity results were also complete. They were inspected and retained, not rerun. New tests address only newly identified MSD callback and mapped-write paths.

## Important discoveries

1. **PROVEN:** the actual diagnostic inherits SC35D8-era persist19/srcview, not every late B1.3 feature. Its custom post-load resync is RAM/DSP work; later timed persistence variants cannot be assumed present.
2. **PROVEN:** a NOR-capable USB mass-storage writer is referenced from **compressed initialized RAM**, `2000379C=08057EF5`. A flash-only function-pointer inventory misses it. Default mode1 selects a window beginning94000; whole-NOR mode3 permits block81/82 writes at81000/82000. Delayed USB mode remapping and its roots still require a complete invariant proof.
3. **PROVEN:** stock content/project file writes are not necessarily SD. Drive0's native disk mapper uses NOR baseD4000/4096-byte sectors; drive1 binds SD. Valid bounded partition writes exclude the targets. The mapper has no local LBA bound and32-bit arithmetic permits adversarial out-of-range LBAFFFAD/FFFAE to map81000/82000. **UNKNOWN:** whether accepted ordinary filesystem/restoration state can produce those LBAs. This is a precise upstream proof obligation, not a demonstrated normal-boot overwrite.
4. **PROVEN scoped:** independent atomicity review passes104 boundary/state/mask combinations plus six terminal-admission checks, classifies all39 differing bytes, and reproduces the old race without importing its emitter. The critical section is bounded to nine instructions CPSID→MSR, with eight entered under newly set PRIMASK; no calls/loops/Storage work occur there.
5. **PROVEN scoped:** all three named corrected update/rollback transitions install exact images, their38-byte compared headers differ, and every recorded NOR array read is covered by a prior erase/program. No old-staging array-byte dependency remains in those completed traces. This is not a universal interrupted-upload or whole-boot theorem.

## Required gate outcomes

| Requirement | Outcome / evidence |
|---|---|
|1. Complete primitive/transitive graph |**UNKNOWN complete closure**; expanded graph, initialized-RAM callback, filesystem/disk routes and exact remaining predicates documented in [nor-mutation-callgraph.md](<nor-mutation-callgraph.md>) |
|2. Reset→idle producer enumeration |**UNKNOWN**; authentic prefix and selected update proofs retained; full timer/USB/filesystem/background obligations unclosed. [boot-to-idle-mutation-closure.md](<boot-to-idle-mutation-closure.md>) |
|3. Background/deferred work |Custom variants narrowed; stock persistence backend and exact gaps identified. [background-write-analysis.md](<background-write-analysis.md>) |
|4–6. Separate preservation/authenticity |Identity **UNKNOWN**; coefficient prefix **UNKNOWN** through complete ordinary sequence, with stronger conditional preservation evidence. [target-preservation.md](<target-preservation.md>) |
|7. Independent atomicity |**PROVEN within native boundary model**. [atomicity-patch-review.md](<atomicity-patch-review.md>) |
|8. Changed-header/no-op |**PROVEN for three completed named transitions**; no silent install omission. [update-noop-review.md](<update-noop-review.md>) |
|9. Full final admission |Withheld because prior gates do not pass; existing validations retained rather than relabelled. [final-candidate-validation.md](<final-candidate-validation.md>) |
|10. Heap/stack |0 added startup allocation demand,12-byte capacity reservation,8-byte fixture heap margin; Main2460/Storage1068 minimum modeled guard margins; actual headroom **UNKNOWN**. [heap-stack-status.md](<heap-stack-status.md>) |
|11. Final candidate identity |**Not designated**; conditional gate unmet. Phase44 identity remains reproducibility evidence only; no old hash reused. |
|12. Documentation supersession |Old Phase43 remains DO NOT FLASH; current handoff points to this unqualified checkpoint. No README/checksum is promoted as a final hardware package. |
|13. Decision and hardware observation |See table below. |

## Explicit82000 answer

**UNKNOWN** whether a path in the complete planned ordinary boot/background schedule can modify any byte of82000–821FF after the chosen candidate installation and before capture. No concrete ordinary-boot modification was demonstrated. The exact remaining producers are MSD57EF4 with its mode/callback/SCSI-bound invariants, and mapped file-write1AF1E with upstream filesystem LBA/count/object-binding constraints. The saved direct-call scan does not close their root reachability.

**PROVEN conditional YES** for deliberately selected resource-update, factory chip erase and whole-array-MSD capabilities. Their existence is distinct from proving they occur in the intended sequence. If a writer actually ran, post-write bytes cannot automatically be accepted as original coefficient evidence; payload/version/provenance must be established. Identity's specific setters and RAM byte14 normalization are separately analysed; its uncertainty is not used as a substitute blocker for coefficients.

## Final decision table

| Category | Finding / required action |
|---|---|
| **BLOCKERS BEFORE FLASHING** |Close all mode writes and delayed callbacks through24918/248B4/38C54; prove physical-address/window bounds for MSD requests. Close filesystem LBA/count bounds and disk-binding invariants upstream of1AF1E across restore/save/flush. Complete computed callback/queue root closure, including command/config clients. Until then the critical82000 original-evidence gate and full final admission stay unqualified. |
| **SHOULD VERIFY** |Independent reviewer should review the new compressed-RAM callback edge, NOR-versus-SD file backend distinction, explicit input predicates and arithmetic tests. Retain post-install provenance separately for23 and512 bytes. Reuse existing independent atomicity/update results unless new evidence invalidates them. |
| **ACCEPTABLE HARDWARE-ONLY UNKNOWN** |Actual IRQ/USB/DMA/WinMM timing, actual fresh-boot heap headroom, physical flash/NOR faults and unit-specific rollback flashing remain unproved. These do not excuse the offline producer gaps. |

**PROVEN user-reported hardware evidence:** recovery/bootloader mode can be entered on this unit; it can then exit and boot B1.3 normally. This is entry/return evidence only. It is **not** evidence that rollback flashing has been tested. The agent performed no such action.

H4 remains FAIL for in-session NOR error unwind: after sending may begin, discard failures, no retry/second request/forced Storage release, full power cycle before further action. An unsent host port/open failure is handled separately by the corrected host. No claim of absolute safety or guaranteed recovery is made.

## Smallest next offline work

Start at the now-identified producer predicates, not another blanket no-write replay: prove the post-reset USB-mode invariant including its150-tick callback and complete the filesystem logical-block range proof feeding1AF1E. A completed exclusion of those roots must then be joined to the remaining queue/controller closure before final file-first candidate admission. Do not guess NOR payloads or designate an artifact merely because its isolated tests pass.

PREFLASH OFFLINE CLOSURE = UNQUALIFIED
