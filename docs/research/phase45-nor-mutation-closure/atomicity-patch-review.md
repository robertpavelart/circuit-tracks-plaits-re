> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Independent atomicity review

**PROVEN within the native boundary model:** the saved independent review is complete and was not rerun on resume. It decodes the actual original/corrected disk SYX independently using base128 block unpacking and bitwise MPEG-2 CRC, compares decoded BINs and classifies every changed byte. It imports no patch emitter. See [review implementation](<../../../builds/phase45-nor-mutation-closure/independent_atomicity_review.py>) and persisted results (local-only reference: `builds/phase45-nor-mutation-closure/independent-atomicity-review.json`; not distributed).

## Instruction and byte comparison

39 actual changed bytes are wholly within three declared regions: six-byte marker range080101E8–080101ED (four bytes differ), branch0806B9DC–0806B9DF, and32-byte fragment0806BC30–0806BC4F replacing FF slack. The JSON classifies every differing address/before/after byte; no other difference exists.

Original path: load state atB9E4, compare ACTIVE, branch, then store SUCCESS atB9EC without masking. An interrupt between check and store reproduces quarantine3→SUCCESS2 overwrite.

Corrected path:

```text
0806BC30 MRS r2,PRIMASK
0806BC34 CPSID i
0806BC36 MOVW r0,#4D70
0806BC3A MOVT r0,#2004
0806BC3E LDRB r1,[r0,#4]
0806BC40 CMP r1,#1
0806BC42 BNE 0806BC48
0806BC44 MOVS r1,#2
0806BC46 STRB r1,[r0,#4]
0806BC48 MSR PRIMASK,r2
0806BC4C B.W 0806B9EE
```

**PROVEN model result:**104 corrected boundary/state/mask combinations, covering initial states0/1/2/3 and PRIMASK0/1, preserve mask and never overwrite observed FAILED_QUARANTINED. Twelve skipped-branch boundary combinations are explicitly marked unreachable rather than described as injected. Six separate non-IDLE admission checks show zero Storage submissions and no writes. R3–R12/SP/LR are preserved; R0/R1/R2 and condition flags remain caller-volatile as in the existing command ABI. The inherited coupled native tests supplement this local ABI boundary.

## Atomicity and timeout ordering

If SysTick quarantines before the protected check, the state is3 and success is skipped. If timeout becomes pending while masked, it is delivered after mask restoration and sees SUCCESS2, so the native watchdog does not quarantine a completed transaction. If the incoming mask was1, it stays1. The model tests pending delivery immediately after MSR as well as every reachable instruction boundary.

The ACTIVE path from CPSID through MSR is nine instructions; eight instructions are entered with the newly set mask. There are no loops, calls, Storage waits, TX operations or bulk buffers inside this interval. Only address formation, one state-byte read/comparison and conditional one-byte store are protected. This is a bounded instruction count, not a measured physical cycle/latency bound.

Both terminal states reject a second capture. The correction creates no new read path; local terminal rejection and the inherited25-case coupled suite cover that contract. SysTick remains otherwise unmodified and pending maskable interrupts can run after restoration. NMI/fault/reset do not become masked by PRIMASK and are outside the successful ordinary instruction-path theorem; no recovery-after-fault guarantee is claimed.

**UNKNOWN:** physical interrupt latency, every fault/power interruption and full reset/background behavior. Independent atomicity passes its scoped review; it does not close the NOR producer graph or designate a final hardware candidate.
