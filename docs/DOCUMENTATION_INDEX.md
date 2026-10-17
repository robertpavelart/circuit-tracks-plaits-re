# Documentation index — final pre-hardware review

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

- [HANDOFF.md](<HANDOFF.md>)
- [CURRENT_STATUS.md](<CURRENT_STATUS.md>)
- [NEXT_STEPS.md](<NEXT_STEPS.md>)
- [PROJECT_OVERVIEW.md](<PROJECT_OVERVIEW.md>)
- [FINAL_PREFLASH_REVIEW.md](<FINAL_PREFLASH_REVIEW.md>)
- [MEMORY_AND_RESOURCE_STATUS.md](<MEMORY_AND_RESOURCE_STATUS.md>)
- [REVERSE_ENGINEERING_STATE.md](<REVERSE_ENGINEERING_STATE.md>)
- [PLAITS_RESEARCH_STATE.md](<PLAITS_RESEARCH_STATE.md>)
- [RESEARCH_TIMELINE.md](<RESEARCH_TIMELINE.md>)
- [CLAUDE_REVIEW_PACKAGE.md](<CLAUDE_REVIEW_PACKAGE.md>)
- [CLAUDE_REVIEW_PROMPT.md](<CLAUDE_REVIEW_PROMPT.md>)
- [SNAPSHOT_CONSISTENCY_AUDIT.md](<SNAPSHOT_CONSISTENCY_AUDIT.md>)
- [FINAL_DOCUMENTATION_AUDIT.md](<FINAL_DOCUMENTATION_AUDIT.md>)
- [HARDWARE_TEST_PREFLIGHT.txt](<HARDWARE_TEST_PREFLIGHT.txt>)

## Evidence precedence and labels

Evidence precedence: [final allocation decision](<research/final-indirect-resolution/findings.md>) controls the remaining software proof boundary; [USB joint-path closure](<research/final-two-check-closure/usb-joint-closure.md>) records 36 passing focused cases. [Phase67](<research/phase67-final-safety-disposition/findings.md>) retains its bounded configuration/query/authorization-to-capture-entry scope. The frozen [package audit](<research/final-hardware-test-package/final-cheap-checks.md>) preserves the earlier two-gap history, with a current supersession notice. No model PASS is physical proof.

Current central authority is [CURRENT_STATUS.md](<CURRENT_STATUS.md>), reconciled with the latest user-supplied state and saved final closure evidence. Historical reports remain intact. The old package two-gap text is retained as a dated audit body with a supersession notice; only the allocation gap remains open. Phase61/original Phase62 are FAILED / SUPERSEDED / DO NOT FLASH; Phase43 is SUPERSEDED. The earlier `circuit-tracks-plaits-re/` tree is a historical source snapshot, not a second current release.

PROVEN means the stated artifact/code/model scope, or expressly attributed user physical report. STRONG INFERENCE means supported interpretation. UNKNOWN means not established; HARDWARE-ONLY UNKNOWN identifies unresolved physical behavior, not the software allocation proof gap. FAILED records a failed gate/test; SUPERSEDED prevents historical candidates/instructions from being treated as current. Accepted risk does not alter any label.

Current package: README.txt (local-only reference: `builds/final-hardware-test-package/README.txt`; not distributed). Packaging recovery record: [recovery-status.txt](<operations/recovery-status.txt>). This update's machine audit: audit.json (local-only reference: `builds/final-pre-hardware-documentation/audit.json`; not distributed).
