> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 20B2 — bounded caller state obligations

## Phase20B6 — live-input design refinement (2026-10-07)

**CONDITIONAL selected post-only liveness**, no captured values or replay.
Actual routing0/nonlinear1/offset5/5 must be observed. R4, material modifiers,
SR/OMR, SP/SC/LA/LC/active frames, retained memory and table provenance remain
required. Incoming otherR/N/data registers are overwritten or unused locally;
full-state comparison/debug restore still requires their raw values. M5 is
replaced from capturedY19/Y1A on this selected path. LF/FV derive from SR.
P657 sourceY8F..91 may be omitted after prepared post targets are captured.
OriginalC2D overwrites selectedYF64..68 before reads under the qualified modes/
modifiers/offsets and no async write; other sequences remain mode-dependent.
No default modifiers, empty stack or guessed numeric histories introduced.

Correct Ypost formula: S=59F+28*i, startS+0C, endS+1A, slot0[5AB,5B9).
The earlier S+12 annotation intended decimal12; hexadecimal0C is correct.
Xcoefficient stride4A differs. Preserve capturedR4/Y7 and corroborate slot,
not choose slot0. Details:runtime-snapshot-schema.md and final-v4 live-field CSV.
Preferred OnCE boundary is rawnext9DD after9DC NOP, with labelled normalization
to9D9 only after boundary/IRQ/writer proof. Capture preinspection pipeline/SR
before forced debug instructions; SSH reads pop stack and may trigger extension.
Core import design uses raw56-bit A/B via typedAPI, not left-aligned internal
struct copy. No importer/CPU constructed. Static strategy EXHAUSTED; hardware
design conditional; flashingNO. Earlier static-next-step prose is historical.

2026-10-07. **PARTIAL static provenance / numeric checkpoint REFUSED.**
Full authentic boot is not required by the study. A bounded original caller
checkpoint could suffice, but none with zero material category-E fields was
recovered. No CPU, unknown-value backing or reset-default register word is used.

## Material arithmetic/memory modes

SM20, SA17, DM14 and scalingS0/S1 at10/11 remain unresolved at the selected
entry. They affect multiplication, limiting/full transfers and possibly address
materialization. P10A setsRM21 in the initialized normal class; retention is
instruction-supported conditionally, not an executed seam state. C9D setsS1
atCA2 and clears it atCB6 but does not retroactively establish entryS0/S1.

SC13 can be0 under the conditional DSP56724/25 architectural invariant from
pinned RM table5-2, as previously qualified for checkpoints; that is separate
from the hardware stack counter also calledSC. LF15/FV16 and the true saved
frames remain material to loops. First9DD/9DE replacesA/comparison flags;
sticky/full-status/history irrelevance is not completely proved.

No complete OMR value is supplied. Absence of an OMR write inside the local
post region is not proof that all memory-mode bits are irrelevant. Bootstrap
mask600080/value400080 does not establish a concrete bounded caller context.
Unknown modes are not filled from documented reset state or an emulator constructor.
This is a bounded-checkpoint evidence gap, not an instruction to solve ROM boot.

## AGU provenance

| Field | Instruction-backed value/relation | Scope |
|---|---|---|
|Y19|81FF,2842/2844|multiple-wrap modulo512; initialized retention premise|
|Y1A|FFFF,27F8/27FA|linear XXFFFF per pinned FM4.5.1; initialized retention premise|
|M2|3FF restoresY1A during each lane preparation|last local modifier write if387 completes|
|M5|ADC loadsY19, B24 restoresY1A|selected nonlinear1 path; incomingM5 dead before normalization table indexing|
|R0|9D9 reloadsY7, expected5AB|selected producer prefix|
|R4|S+12=5AB|three lane-state pairs and six coefficient ramps|
|N1/N3|2 atC0E/C0F|local original producers|
|N4/N5|-3/-4 atBE8/BEA|local original producers|

Other address-relevant M values still require the selected upstream invocation's
actual last-writer/retention proof. Initialization2779..2781 is evidence, not
permission to default every modifier. M5=81FF is not equivalent toFFFF; normal
nonlinear normalization can intentionally wrap a512-word table. Registers used
as data in standalone Plaits have no relevance to this stock checkpoint.

## Natural caller and hardware-loop state

The completion-pass chain has original JSRs:

`12A->1D9 (return12C) ->1FE->19BF (return200) ->19E6->77F (return19E7)`.

The request/preparation chain is distinct:

`1FC->198D ->19AC descriptor call281 ->37E->387 (return380)`
`->384->77F (return386)`.

387's return follows380..382 pointer reloads, then384's generator call.
Request bit23 can select a return at9A4; the lookup completion path requires
worker-generated queue data and can wait on ICC at775..77D. Moving a checkpoint
to387 alone does not make entry9D9 deterministic or eliminate peripherals.
Starting9AC requires already generated numerical lane buffers; manually injecting
those would not be original natural generator output.

Local loops79B..99D,9AC..9B7 and9C6..9D8 are closed before9D9. This proves
no *owned* generator DO remains active there, not that inheritedLF/FV/LA/LC
or prefix frames are zero. Relative stack depth s+3 follows the completion
call chain only under its balanced/inactive-intervening-frame premises; s and
its frames remain unresolved. P107/108 explicitly initializeSP/SC, but are not
substituted for a later runtime snapshot. SP/SC/SSH/SSL/LA/LC/LF/FV remain null
in the proposed checkpoint, never an invented reset-depth prefix.

## Histories, guard and stop

Y5AB..5AE andY5B7/5B8 survive the selected trigger-reset ranges. The first
processing assumption would need an actual bounded earlier execution/preservation
proof, not just a source preset file or startup clear. Gain/envelope and recursive
histories remain numerical inputs; unknown arithmetic result data cannot be treated
as symbolic-but-irrelevant here.

X2C66's natural value is not recovered. The generator uses overlapping phase/
index scratch before the32-word mono overwrite, so padding/zero cannot be assumed.
Selected nonlinear1 may or may not take the normalization branch depending on
X5AD/Y5AB and N5. Its guard read and possible raw-scaling multiply/CCR changes
cannot be classified dynamically. C9F's later history overwrite andA93 prefetch
are static facts, not observations in a recovered context.

The only proposed stop isA95. AA3/timer-dependent scheduling is excluded.
No replay, state mutation measurement, continuity or cycle measurement occurred.
Category-E modes/history/pointers forbid numerical admission; no stock/Plaits
integration or RAM-safety promotion follows.

## Phase20B3 input-stage context

657 loads its own pointers fromY0..3/X29; bank0/slot0 expected addresses are
2D5,131,A0,7C,57B. R0 reads37 controls and a count-led five-word stream.
M0/M1/M2/M4/M5/M6/M7 entry retention is material;657 does not set them.
N5/N6 initially0 forslot0, then691 setsN5=2; N1 is read frommodulatedY7C.
SourceR5/R6/R7 within modulation derive from original patch pointer tables,
but full transfer modes, count/sentinel preservation remain unqualified.

Natural trigger path calls657 twice:33F,then37A→4D5→37C; both have distinct
source-state epochs. Owned DOs667/676/685/698/70F/741 close by758, not proof
of empty inheritedSP/SC/LA/LC/LF/FV. No arbitrary status word or saved-frame
prefix is injected. Mode/history/address guards keep checkpoint PC null.
See arithmetic-context.json,agu-context.json,caller-stack-context.json under
builds/phase20b-inputrec/final-v3. Source qualification PARTIAL;0 CPU replay.
