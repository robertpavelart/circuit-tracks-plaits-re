# Next steps — decision boundary

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

The independent Claude review is **reported by the user** as: **REASONABLE TO PROCEED WITH CONTROLLED HARDWARE TEST**, subject to explicitly accepted residual risk. The reported review found no concrete offline firmware blocker or bootloader-loss path and recognized the actual defect fixes. This records the supplied review conclusion, not a new independent review in this task. Later allocation findings remain SOFTWARE UNKNOWN even though earlier review emphasized hardware/model uncertainty. Neither favorable review nor accepted soft-brick risk changes OPERATIONAL PREFLIGHT = UNQUALIFIED or enables tools.

## Future sequence

1. Keep repository documentation current and operational tools locked.
2. Prepare a **separately reviewed operational release**, with new exact tool hashes and explicit treatment of the accepted allocation uncertainty; do not manually toggle the frozen locks.
3. In a future explicitly authorized session, verify all hashes on the actual sending machine and apply/verify Windows/MSD policy before connection. Stop if isolation cannot be established.
4. Conduct the controlled hardware test only under that separately reviewed release and explicit user decision.
5. Query geometry first; independently validate the retained geometry and `$82000` safety on the host.
6. Authorize only the exact validated epoch/geometry/session; exactly one fixed capture. Optional `$81000` identity requires separate target authorization.
7. On success, validate/hash/archive complete evidence and restore B1.3 using the agreed rollback plan.
8. On any failure, discard partial evidence, no retry or second diagnostic/Storage request, full physical power OFF, USB unplugged, session ends.

**H4 remains FAILED (H4 = FAIL) for bounded in-session recovery.** On any failed or uncertain raw capture: discard all partial evidence; DO NOT RETRY; send no second diagnostic/Storage request or cleanup command; full physical power OFF, USB unplugged, session ends. No forced semaphore release. A reset, new process, session identifier or deleted attempt marker is not a power-cycle substitute.

## Windows / MSD — prepared, not physically applied or tested

Automount control alone is NOT sufficient isolation. Removable-storage access denial policy is prepared in [windows-msd-policy.txt](<operations/windows-msd-policy.txt>); applicability/enforcement with this unit remains HARDWARE-ONLY UNKNOWN. No scan/repair, format, Explorer browsing, SD changes or filesystem utilities. Close Components, DAWs and other MIDI users. Unexpected mounted volume or storage access means STOP. No OS policy was changed here.

Do not continue infinite offline investigation, port Plaits, regenerate a diagnostic image, silently relabel the allocation census PASS, or enable the frozen live tools. The accepted residual SOFTWARE UNKNOWN is documented in [CURRENT_STATUS.md](<CURRENT_STATUS.md>) and [findings.md](<research/final-indirect-resolution/findings.md>). Hardware behavior and candidate-specific recovery remain HARDWARE-ONLY UNKNOWN. Existing recovery rehearsal is not a tested recovery flash. This task stops at documentation; preparation/review and any hardware action require the separately defined future scope.
