> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 19B-SYMBOLIC — partial state model

2026-10-06. IMPLEMENTED / TESTED: additive Python support in
emulator/harness/partial_state.py and symbolic_startup.py. The sealed Phase19A
concrete interpreter and defaults are unchanged. This is a narrow symbolic
transfer adapter for previously decoded original opcodes, not a full DSP decoder
or general chip emulator. Unknown behavior or a material unknown stops analysis.

Partial(width, known_mask, known_value, provenance) represents sets of values.
For 24-bit words, mask0 means fully unknown; maskFFFFFF means concrete. Unknown
positions in known_value are canonical padding0, not guessed concrete zeros.
Invalid encodings are rejected. Widths1/2 support control fields; wider values
are representable, but full accumulator/stack execution is not certified here.

| Local operation on an unknown latch | New mask | New value | Carry |
|---|---|---|---|
| PCRG BCLR13 | 002000 | 000000 | UNKNOWN old bit13 |
| PRRG BSET13 | 002000 | 002000 | UNKNOWN old bit13 |

SYMBOLIC: unrelated known and unknown bits are preserved exactly. These are
qualified configuration-latch transformations, not complete CPU/board execution.
Different old bit13 values produce different carry. Other latch/output state
remains unknown. Finite fixture classes validate target-bit/mask behavior, not
identical observable startup behavior. No pin levels or generic peripheral
side effects are invented.

Dependency rules require only relevant bits, not complete CPU snapshots.
Equality can prove false from a known mismatching bit; an undecided branch,
jump, effective address, count or modifier use fails closed. Unknown peripheral
values never become zero; unknown behavior stops. General DO/REP/DMA/modulo and
full CMP execution are not implemented by this narrow adapter. Their material
uses are guarded primitives and future obligations. Equality alone is not an
executed DSP CMP.

Interrupt eligibility is pending && (IPL==3 || IPL>=SR.I): ordinary levels0..2,
nonmaskable level3, and minimum admitted level I0..3. At most32 small control-field
completions are considered; no arbitrary 24-bit state search. A known absent
request makes masks irrelevant; a known mask can exclude an ordinary request
even if pending is unknown. Mask3 does not exclude a nonmaskable request.
Unknown eligibility stops before opcode execution. A known eligible request
also stops because handler delivery is outside this adapter. Injecting no new
event does not prove that inherited pending state is absent.
[DSP56300FM exception/status model](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf).

This predicate is not full PIC generation or pipeline-timing certification.
The existing core services interrupts before opcode fetch and uses the same
minimum-level relation. Neither its queue nor its defaults were changed.

The loop guard permits known inactive LF or a definitely non-end instruction;
an ambiguous inherited loop end stops. No LC/stack restore is guessed. Main
107/108 initialize SP/SC before the first explicit JSR at10F, but not before a
possible inherited interrupt/loop operation. R0 at10B and worker R5 at105 dominate
their reviewed scalar uses. Other R/N/M registers are unused by explicit main
100..106 addressing; later uses remain unreached, not universally certified.

Temporal OMR/carry provenance is preserved: the original shim establishes
pre-second-ROM OMR mask600080/value400080. Final shim carry equals incoming
first-ROM OMR bit21, not a proven numeric zero. The uninspected second ROM may
clobber both. Historical constraints retain their source PCs; they do not become
unsupported current handoff seeds. Reviewed candidate maps all cover low P:0/100,
so complete OMR knowledge is not needed solely for those addresses. SEN/XYS
become relevant on stack use, which is separately gated.

Before proven ICC publication, data/IF/ACK/enable are UNKNOWN at application
handoff, not reset0 or30002. The qualified synthetic enabled maskable-transfer
case requires known enable and an absent prior flag: publisher payload -> pending
-> receive payload -> flag clear -> ACK. Fixture payload123456 is not a stock
token. Unknown enable/overrun or unqualified empty/disabled ACK behavior stops.
[DSP56724RM sections13.1.2/13.2.2](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf#page=251).

No broad worker, cycle-accurate scheduler or fabricated completion was added.
If earlier gates pass later, newly reached mode/peripheral/full CMP deficiencies
must stop then. Fixture values cannot supply stock preconditions.

TESTED:24 focused tests in emulator/tests/test_partial_state.py cover masks,
old-bit carry, finite fixture classes, equality/taint refusal, interrupt
eligibility, temporal bootstrap provenance, qualified ICC/unknown handoff cases,
original identity and blocked original entry. Positive bit/ICC fixtures contain
no stock CPU execution. Original main and worker counts remain0.
