# State consistency — final pre-hardware review

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

| Former contradiction | Current resolution |
|---|---|
| Phase67 PASS implies overall release PASS / all residual risk hardware-only | Phase67 scoped PASS retained; later all-root allocation census remains SOFTWARE UNKNOWN; operational preflight UNQUALIFIED |
| Both final cheap checks remain open | USB joint path PASS, 36 focused cases; allocation alone remains open |
| No actual >8-byte post-READY allocation found means none exists | Absence NOT proven; unresolved virtual/registry targets and eight-byte modeled gap retained |
| Allocation failure is safely NULL | Rejection reaches BKPT; artificial continuation returns FFFFFFFF, generic wrapper accepts it; physical routing UNKNOWN |
| Recovery entry rehearsal proves recovery flash | User-reported entry/exit/B1.3 boot with no transmission; enumeration/handshake/recovery flashing unproven |
| Accepted soft-brick risk closes an evidence gate or enables tools | Risk acceptance recorded separately; locks unchanged; new operational release requires separate review/hashes |
| Phase61/62 or Phase43 historical candidate remains current | Explicit FAILED/SUPERSEDED labels; only unchanged Phase63 identity current |
| A temporary diagnostic is Plaits firmware | No Plaits in candidate; authentic82000 missing; P0282 reclaim and final P/X/Y remain unqualified |
| Windows automount disable alone isolates storage | Deny-access policy prepared; physical enforcement untested; unexpected volume/storage access STOP |
| Model success repairs bounded unwind | H4 remains FAIL: discard/no retry/full physical power OFF/USB unplugged/session ends |

No candidate/tool bytes or historical experiment results were changed. Current identities and evidence: [CURRENT_STATUS.md](<CURRENT_STATUS.md>); final audit: [FINAL_DOCUMENTATION_AUDIT.md](<FINAL_DOCUMENTATION_AUDIT.md>).
