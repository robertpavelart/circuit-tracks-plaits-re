# Circuit Tracks / Plaits research

## Status — October 2026

| Question | Current state |
|---|---|
| Long-term goal | Four melodic Plaits tracks on Circuit Tracks, retaining useful sequencer, drums, mixer, FX and project workflow where feasible |
| Current artifact | Temporary NOR diagnostic firmware, **not Plaits** |
| Candidate hardware-tested | **NO**; only user-reported recovery entry/exit rehearsal |
| Known offline firmware blockers | None demonstrated |
| Operational release | **NOT YET ENABLED**; host and uploader LOCKED |
| Residual software uncertainty | Post-READY indirect allocation reachability with only eight bytes modeled heap gap |
| Recovery | Bootloader entry/exit physically rehearsed; recovery flashing not tested or guaranteed |
| Next step | Separately reviewed operational release → controlled hardware test preparation |

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

The independent Claude review is **reported by the user** as: **REASONABLE TO PROCEED WITH CONTROLLED HARDWARE TEST**, subject to explicitly accepted residual risk. The reported review found no concrete offline firmware blocker or bootloader-loss path and recognized the actual defect fixes. This records the supplied review conclusion, not a new independent review in this task. Later allocation findings remain SOFTWARE UNKNOWN even though earlier review emphasized hardware/model uncertainty. Neither favorable review nor accepted soft-brick risk changes OPERATIONAL PREFLIGHT = UNQUALIFIED or enables tools.

Start with [HANDOFF.md](<docs/HANDOFF.md>), [CURRENT_STATUS.md](<docs/CURRENT_STATUS.md>) (exact candidate/tool/rollback identities), [NEXT_STEPS.md](<docs/NEXT_STEPS.md>) and [DOCUMENTATION_INDEX.md](<docs/DOCUMENTATION_INDEX.md>).

**H4 remains FAILED (H4 = FAIL) for bounded in-session recovery.** On any failed or uncertain raw capture: discard all partial evidence; DO NOT RETRY; send no second diagnostic/Storage request or cleanup command; full physical power OFF, USB unplugged, session ends. No forced semaphore release. A reset, new process, session identifier or deleted attempt marker is not a power-cycle substitute.

Authentic `$82000-$821FF` coefficients have not been captured. P:`$0282-$0386` reclaim is not finally qualified; final safe P/X/Y budget remains UNKNOWN. Future four-track design shares model code and keeps independent track state; default mono, `MAX_TRACKS_PER_MODEL = 2`, `MAX_POLY_TRACKS = 2`, engine-specific polyphony, eventual 24 engines.

Historical build/evidence directories and the earlier `circuit-tracks-plaits-re/` source snapshot are preserved, not current operational instructions. Phase61/original Phase62 are FAILED / SUPERSEDED / DO NOT FLASH; Phase43 is SUPERSEDED. See [FINAL_DOCUMENTATION_AUDIT.md](<docs/FINAL_DOCUMENTATION_AUDIT.md>) for supersession and this update's audit.
