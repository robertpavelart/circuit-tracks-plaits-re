# Handoff — final pre-hardware review

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

Evidence precedence: [final allocation decision](<research/final-indirect-resolution/findings.md>) controls the remaining software proof boundary; [USB joint-path closure](<research/final-two-check-closure/usb-joint-closure.md>) records 36 passing focused cases. [Phase67](<research/phase67-final-safety-disposition/findings.md>) retains its bounded configuration/query/authorization-to-capture-entry scope. The frozen [package audit](<research/final-hardware-test-package/final-cheap-checks.md>) preserves the earlier two-gap history, with a current supersession notice. No model PASS is physical proof.

## Resume point

The independent Claude review is **reported by the user** as: **REASONABLE TO PROCEED WITH CONTROLLED HARDWARE TEST**, subject to explicitly accepted residual risk. The reported review found no concrete offline firmware blocker or bootloader-loss path and recognized the actual defect fixes. This records the supplied review conclusion, not a new independent review in this task. Later allocation findings remain SOFTWARE UNKNOWN even though earlier review emphasized hardware/model uncertainty. Neither favorable review nor accepted soft-brick risk changes OPERATIONAL PREFLIGHT = UNQUALIFIED or enables tools.

No further reverse engineering or peripheral modeling is the default continuation. Preserve the accepted allocation uncertainty explicitly; prepare a separately reviewed operational release before any later hardware session. Current candidate/tool identities: [CURRENT_STATUS.md](<CURRENT_STATUS.md>). Phase61/original Phase62 remain FAILED / SUPERSEDED / DO NOT FLASH; no candidate bytes were changed by this state update.

## CLOSED — known defects and focused synchronization check

| Item | Closure and scope |
|---|---|
| Phase61 reservation bug: VALID could publish into unreserved memory | Reservation guard added in Phase62, retained with seven Phase63 regressions. Phase61 FAILED / SUPERSEDED |
| SD mount invalidated retained NOR geometry | Phase63 separates NOR binding/epoch semantics; SD/NOR native tests pass |
| NOT_READY / INVALID / FAILED status ambiguity | Explicit 39-byte CRC-protected status protocol and matching host handling |
| DMA still referenced former Main stack storage after return | Ownership fence before CPU use and common return; 31 saved DMA cases and later focused joint cases pass in their scopes; no forced unwind |
| Late SUCCESS overwrote failure/quarantine | Absorbing failure/atomic terminal handling fixed earlier and retained |
| USB Storage / diagnostic joint path | **USB STORAGE JOINT PATH = PASS**: 36 focused cases, both request orders, failure/late completion, disconnect/remount and resets; declared native/model seams |

Evidence: [findings.md](<research/phase63-defect-closure/findings.md>), [sd-mount-fix.md](<research/phase63-defect-closure/sd-mount-fix.md>), [status-protocol.md](<research/phase63-defect-closure/status-protocol.md>), [buffer-ownership.md](<research/phase63-defect-closure/buffer-ownership.md>), [usb-joint-closure.md](<research/final-two-check-closure/usb-joint-closure.md>) and joint-results.json (local-only reference: `builds/final-two-check-closure/joint-results.json`; not distributed).

Saved Phase63 results: 7 reservation, 28 native, 13 status/mount, 31 DMA, 32 host containment and 3 install/rollback transitions. None was rerun for this documentation update. CLOSED refers to demonstrated defects and stated regression scopes, not guaranteed physical behavior.

## Primary accepted residual SOFTWARE uncertainty

**POST-READY ALLOCATION CENSUS = UNQUALIFIED.** Static analysis did not exhaustively resolve indirect/virtual targets, including **0x0803C91C**, **0x0803C9C4**, and registry/object-method sites. No actual post-READY allocation >8 bytes was found; its absence is NOT proven. The modeled heap cursor is `20044D68`, cap `20044D70`: eight bytes, not physical stack margin or replenished per-request capacity.

The recovered normal-publisher set for `08022E22` has seven targets. Four are allocator-free; three lead to unresolved virtual continuations. The expanded ledger covers 260 encountered indirect sites, 233 unresolved, and 73 target summaries. These are conservative traversal counts, not 233 proven allocation hazards or an exhaustive complete graph.

PROVEN in four isolated allocator ABI cases: rejection reaches BKPT; if execution is artificially continued after BKPT, R0=`FFFFFFFF`, accepted by the generic wrapper as nonzero. Physical exception routing remains UNKNOWN. Safe failure cannot be assumed. These isolated inputs do not prove a post-READY occurrence. See [findings.md](<research/final-indirect-resolution/findings.md>), indirect-ledger.csv (local-only reference: `builds/final-indirect-resolution/indirect-ledger.csv`; not distributed), and [failure-semantics.md](<research/final-indirect-resolution/failure-semantics.md>).

## Diagnostic architecture

Reserved record `$20044D70-$20044D7B`; adjacent Master FX begins `$20044D7C`. First-mount geometry/lifecycle → RAM-only 0E export → independent host validation → exact first-epoch/geometry/session 0F authorization → fixed read. Required target `$82000-$821FF` is 512 bytes in eight ordered 64-byte chunks; optional `$81000-$81016` is 23 bytes separately authorized. There is no host-selected address/length. A dedicated Main stack frame remains owned until DMA/request/backend release. Epoch/session binding is not cryptographic or globally unique across power cycles.

**H4 remains FAILED (H4 = FAIL) for bounded in-session recovery.** On any failed or uncertain raw capture: discard all partial evidence; DO NOT RETRY; send no second diagnostic/Storage request or cleanup command; full physical power OFF, USB unplugged, session ends. No forced semaphore release. A reset, new process, session identifier or deleted attempt marker is not a power-cycle substitute.

## Recovery and accepted risk

**PROVEN — by user report on the physical unit:** recovery/bootloader mode can be entered; full power cycling exits recovery; B1.3 boots normally afterward; no firmware was transmitted during that rehearsal. This does not mean the diagnostic candidate was tested.

**UNKNOWN / NOT PROVEN:** recovery-mode host enumeration, uploader handshake in recovery, actual recovery flashing of B1.3 or official 4486, recovery from a non-booting diagnostic candidate, and guaranteed recovery. Physical candidate-specific recovery is **HARDWARE-ONLY UNKNOWN**.

**STRONG INFERENCE from the saved offline scope:** no concrete bootloader-loss path has been identified. **PROVEN in modeled install/rollback operations:** bootloader lies outside application erase/program ranges and remains unchanged. This is narrower than physical recovery success.

The user explicitly accepts the possibility of a soft brick requiring recovery, provided the bootloader remains accessible. Recovery success is not guaranteed. Acceptance does not convert UNKNOWN into PROVEN, close the allocation census, enable tools or authorize hardware action in this documentation task. See [recovery-status.txt](<operations/recovery-status.txt>).

## Next steps, not actions authorized here

1. Keep repository documentation current and operational tools locked.
2. Prepare a **separately reviewed operational release**, with new exact tool hashes and explicit treatment of the accepted allocation uncertainty; do not manually toggle the frozen locks.
3. In a future explicitly authorized session, verify all hashes on the actual sending machine and apply/verify Windows/MSD policy before connection. Stop if isolation cannot be established.
4. Conduct the controlled hardware test only under that separately reviewed release and explicit user decision.
5. Query geometry first; independently validate the retained geometry and `$82000` safety on the host.
6. Authorize only the exact validated epoch/geometry/session; exactly one fixed capture. Optional `$81000` identity requires separate target authorization.
7. On success, validate/hash/archive complete evidence and restore B1.3 using the agreed rollback plan.
8. On any failure, discard partial evidence, no retry or second diagnostic/Storage request, full physical power OFF, USB unplugged, session ends.

Read [FINAL_PREFLASH_REVIEW.md](<FINAL_PREFLASH_REVIEW.md>), [CLAUDE_REVIEW_PACKAGE.md](<CLAUDE_REVIEW_PACKAGE.md>) and [MEMORY_AND_RESOURCE_STATUS.md](<MEMORY_AND_RESOURCE_STATUS.md>). Four-track Plaits remains a future design; authentic target bytes and final resource budgets are still missing.
