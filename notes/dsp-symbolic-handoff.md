> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 19B-SYMBOLIC — genuine dependency frontier

2026-10-06. SYMBOLIC support implemented; the success criterion was NOT MET.
Original main/worker instructions executed:0. No guessed ROM/reset values,
firmware changes, hardware, transmissions, ROM attachment search, Plaits or
scheduler replay.

The former blanket requirement for complete incoming state is replaced by
actual known-bit use checks. Local main100/101 semantics do not require unrelated
PCRG/PRRG bits to be concrete. Their partial results and carry are exported as
local transfer evaluations, not architectural stock execution with an ignored
interrupt boundary.

First BLOCKING dependency:

    unknown ROM-exit request state / PIC request priority / SR.I[1:0]
        -> instruction-boundary interrupt eligibility
        -> next original instruction OR handler diversion
        -> BLOCK before original P:0; also before requested P:100 profile

Permitted small-field completions include pending1/IPL2/I0 (eligible) and
pending1/IPL2/I3 (masked). These are diagnostic witnesses, not seeded or executed
stock states. Choosing an empty queue or masks3 would substitute unproved
handoff state. No new event injection does not exclude an inherited request.
Priority3/nonmaskable requests cannot be excluded by ordinary mask3 alone.
Actual chip interrupt pipeline/timing is not certified here; a symbolic local
bit operation cannot establish authentic first execution.

| State | Smallest relevant requirement |
|---|---|
| SR.I/request/PIC | Category C: material at the first boundary; prove eligibility/exclusion |
| PCRG/PRRG unrelated bits | Propagate SYMBOLIC; no full word required for local bit operations |
| Initial carry | Overwritten by100/101 from old bit13; can remain unknown without choosing106 |
| A/Z | Defined by102/104 on the reviewed path; unknown ICC data can leave equality undecided |
| SR.SA | Deferred category C at102 transfer;16/24-bit organization cannot be silently selected |
| OMR memory switch | Low P entry exists in reviewed candidate maps; full OMR is unnecessary solely for that |
| LF/LA/LC/stack extension | Conditional category C on loop/stack/interrupt use; no arbitrary stack zeros |
| SP/SC | Category A on explicit call path:107/108 before10F; inherited interrupt/loop use separately gated |
| R0/worker R5 | Category A on reviewed scalar paths:10B/105 before uses |
| Other R/N/M/data registers | No explicit main100..106 operands; later uses not yet qualified |

Bootstrap pre-second-ROM OMR mask600080/value400080 is retained historically.
Final carry depends on incoming first-ROM OMR bit21, not a proven literal0.
Second-ROM clobber exclusion is unknown, so no current OMR/carry seeds follow.
Worker receives no uploaded shim.

Both original images use verified boot PC0, immutable bytes and unresolved
control state. Both attempts stop before JMP100. The requested main100 check
stops at the same predicate. Actual100/101 execution, ICC polling, worker
105/107/109 publication and ACK are NOT REACHED. Neither core can begin, so
cooperative completion/scheduling was not implemented.

| Final A–N | Result |
|---|---|
| A representation | IMPLEMENTED masks/values/provenance; unknowns never coerced to0 |
| B peripherals | IMPLEMENTED qualified latch operations and limited ICC partial contract |
| C dependency rules | TESTED: material unknowns stop; irrelevant bits can propagate |
| D main prefix | 0 authentic instructions |
| E worker prefix | 0 authentic instructions |
| F main reaches ICC poll | NO |
| G worker publishes30002 | NO |
| H main receives it | NO |
| I main executed | 0 |
| J worker executed | 0 |
| K first blocker | Unknown interrupt recognition before application entry |
| L ROM listing necessary | Not uniquely: a sourced live-state/partial-mask exclusion could suffice; current evidence is insufficient |
| M continue startup | NO; deeper loop/mode/peripheral frontiers also remain |
| N best next step | Establish interrupt eligibility/exclusion at the first boundary, then re-evaluate the loop guard |

This failure identifies a genuine missing live control predicate, not proof
that every ROM register or a full ROM listing is necessary. A weaker known
constraint can decide it. A ROM listing is one possible source; other authoritative
handoff guarantees could substitute. X35F/high-X ownership and allocation
verdicts remain unchanged.

Reproduction uses the existing Python runtime and fresh outputs:

    python -B emulator/tests/test_partial_state.py -v
    python -B tools/ct_symbolic_startup.py --output-dir builds/phase19b-symbolic/new-audit
    python -B tools/ct_symbolic_startup.py --output-dir builds/phase19b-symbolic/new-repeat
    python -B tools/ct_symbolic_verify.py --first builds/phase19b-symbolic/new-audit --repeat builds/phase19b-symbolic/new-repeat --output-dir builds/phase19b-symbolic/new-checks

Here python means the pinned existing runtime at:
C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe

Canonical exports are builds/phase19b-symbolic/verified/ and verified-repeat/.
Earlier final/ directories precede added field-bound checks and expanded ledger.
The canonical exports contain blocking JSONL traces, partial masks, local GPIO
transfers, ICC contract, temporal history, first-use ledger, results/tests and
source/input hashes. unit-tests.txt has a duration line and is excluded from
canonical comparison; tests.json contains stable outcomes.

TESTED:24 focused tests pass;16 canonical files match between independent
invocations. Protected SYX/BIN and all ten extracted artifact hashes are intact;
the sealed203-file concrete source/harness guard passes. Evidence:
builds/phase19b-symbolic/checks/reproducibility.json.

Blocked traces and synthetic passes are not successful original stock execution.
No concrete C++ stock interpreter ran, and the symbolic architectural counters
remain0. The user's at-least-one-original-instruction milestone was not achieved.

## Phase 19B-IRQ — 2026-10-06

**UNRESOLVED interrupt-exclusion/convergence contract; original main0 / worker0.**
See `notes/dsp-interrupt-handoff.md` and `builds/phase19b-irq/final/`.

DOCUMENTED: PIC field00 is disabled,01/10/11 select IPL0/1/2; SR.I is bits9:8.
The always-on source at VBA+FC needs no external event when enabled. ICC NMI
and DMA-stall are IPL3 sources; ordinary mask3 alone cannot exclude them.
The SHI mode0 description specifies loading/entry, not a reviewed SR/PIC/FIFO
cleanup or interrupt-pipeline contract. No post-ROM reset value was promoted.

VERIFIED conditional on VBA0: main vector44 JSR156 writes Y2000..2002 and can
write HRX through inherited X10 to X/Y RAM; main vector3E JSR1B4 writes RAM/DMA.
Other nonreserved main vectors and every nonreserved worker vector are NOP/NOP.
Fast NOPs do not prove persistent peripheral requests clear or finite convergence.
VBA0 itself is not established after ROM. Upload order does not prove the exact
cross-core entry/publication interleaving. No 30002 was seeded.

SYMBOLIC source/vector classes are conditional architecture classes, not verified
reachable ROM exits. Exact first fetch also depends on pending/already fetched
interrupts and documented pipeline timing. The abstract field predicate alone
is insufficient. Loop inheritance remains deferred because IRQ resolution failed.
No stock or handler instructions executed; no scheduler replay enabled.

TESTED:16 canonical files match final/final-repeat;24 existing partial-state
checks pass;16 PIC/SR predicate cases pass; protected SYX/BIN and all ten DSP
extraction hashes match; sealed203-file concrete-core/harness guard passes.
Evidence: builds/phase19b-irq/checks/reproducibility.json.

The next prerequisite is a matching authoritative final SHI ROM-exit fragment
or handoff guarantee covering effective interrupt state/pipeline and VBA,
including second ROM entry. A full register dump is not required. Previous
phase gates and X35F/high-X ownership verdicts remain unchanged.
