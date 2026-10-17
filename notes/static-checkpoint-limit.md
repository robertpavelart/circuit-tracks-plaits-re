> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20B5 — static checkpoint reconstruction limit

2026-10-07. **STATIC CHECKPOINT RECONSTRUCTION EXHAUSTED**.
Overall provenance **PARTIAL**; event/checkpoint gates closed.0 stock DSP/ARM
instructions executed. No hardware or runtime observation performed.

The final bounded consumer trace recovered group0 constructor/storage routing,
six-bit note records, twelve six-substep automation lanes, staged notifications
and state-dependent interpolation writes. It did not recover a complete audible
playback timeline or numerical histories. Unknown retained scheduler/allocator
state and DSP history remain material even if the first serialized notes and
current patch bytes are known. Another similar static provenance phase is
therefore not justified. This conclusion is about this checkpoint strategy and
available offline evidence, not every possible static research question.

## Minimum observation boundary

**SPECIFICATION ONLY:** one coherent snapshot at **P9D9**, immediately after
the original generator's32 mono stores and before9DD's post dispatch, with
provenance tying actual slot/bank/patch/project/event to the snapshot. Use original
post replay bounded beforeA95; subsequent original path includes peripheral
reads. Do not force or redirect execution to9D9 to manufacture this context.

P9D9 reloadsR0 fromY7 and includes originalthree NOPs. A post-only checkpoint
can omit upstreamP657 computation because prepared controls and original output
are captured. It cannot by itself qualify complete generator/event replay or
Plaits substitution. Capture one consistent epoch, not uncoordinated independent
word reads; coherence and permitted noninterference need separate qualification.
No safe board readout mechanism or permission to halt/read hardware is implied.

## Exact/conservative live-state specification

All addresses/strides below hexadecimal. i is actual DSP slot, never assumed0.
S=59F+28*i (Y slot state); Q=57B+4A*i (X coefficient record).
X andY post bases happen to equal5AB only forslot0; their strides differ.

|State|Capture requirement|Reduction/condition|
|---|---|---|
|CPU|PC; fullSR/OMR; R0..7,N0..7,M0..7; full56-bitA/B; X0/X1/Y0/Y1|InitialR0 is locally overwritten; retain full state for comparison. Do not forceSR/reset defaults.|
|Stack/loops|SP/SC/LA/LC/LF/FV and active hardwareSSH/SSL entries|Only resident active prefix, not arbitrary unused stack storage; retain actual inherited loops.|
|Interrupts|pending state/eligibility or proved exclusion throughA95|No invented idle/peripheral defaults.|
|X prepared post|[Q+30,Q+43), slot0:[5AB,5BE)|19 words include selectors/targets and gain delta/current.|
|Y retained post|[S+0C,S+1A), slot0:[5AB,5B9)|14 words: six nonlinear/coefficient histories plus eight recursive words. Phase20B6 corrects the 12-decimal-word advance to hexadecimal0C.|
|Original mono+guard|X:[2C46,2C67)|33 words; guard may affectCCR before overwrite.|
|Pointer/modifier restore|Y7,Y19,Y1A|Capture actual words, not initial values presumed retained.|
|Global post state|X0,X39,X3A,X3B,X3C,X40,XCC|Scratch destination, ramp/block/shift and group selection.|
|Group accumulator input|XCC=0:[2DF0,2E10); nonzero:[2E50,2E70)|Capture selected32 words, read atA8E beforeMAC/store.|
|Coefficient/nonlinear tables|X:[1600,1940),[2200,2400)|Can reference existing bytes only if exact runtime/table provenance proves identity; not recreated from guesses.|
|Selected Y coefficients|Actual sequences pointed by offsets;5/5 gives[F64,F69)|May omit initial bytes only after qualifying originalC2D overwrite-before-read in the observed mode.|
|Mode-dependent inputs|Pointer-selected scratch inputs used by actual selector|Capture actual ranges after selecting mode; do not label a conditional minimum universal.|

This is a **CONDITIONAL conservative specification**, not an admitted complete
checkpoint. Selected branch, mapping, modifiers and scratch pointers must still
be concretely validated. Untouched output scratch need not be captured if
overwritten before read; input group accumulation cannot be omitted. No exact
minimum register subset across every selector has been proven.

## Additional event-provenance evidence, not post-only numerical live-ins

Capture actual patch bytes/hash, bank, native identity if available, allocated
voice slot, project/group/pattern/step/subtick and lifecycle identity. Include
ARM player tuple/config sources+0C..24, pending13-byte array+28, bitmap+2C,
phase+35, bitmap+38, prior12-byte array+3C, interpolation+40..43, enable+44,
source+48, note property+4C, rate+50 and relevant packed note records, plus
allocator occupancy/age/release/steal and active macro/correction state.

For upstream event reconstruction add X:[2D5+100*b,363+100*b) bank controls/
modulation rows and Y:[8F,92), natural envelope/source records and their preceding
state. These are not necessary to *local post-only* arithmetic after prepared
state is captured. The nominal controls0/1/5/5 and stored-value conversions
remain conditional until their captured state matches. P657 preparation was
not rerun and no history substituted.

**Single best next step:** seek separate authorization and a feasible method for
one provenance-qualified coherent original9D9 snapshot. Prefer an existing
trusted offline trace/snapshot if available; otherwise assess observation safety
before acquisition. No acquisition is authorized or performed by this phase.
Do not launch another similar static sequence-association phase.

## Phase20B6 — acquisition design completed (2026-10-07)

**READY-FOR-ACQUISITION-DESIGN**, conditional; static strategy stays EXHAUSTED.
No snapshot acquired and no replay admitted. Preferred architectural route is
external DSP OnCE; actual board access/tool/stack/coherence remains unverified.
Pinned manual says program-fetch breakpoints acknowledge *after* matching
execution: a last-NOP9DC trigger gives candidate rawnext9DD. Numeric replay
normalization to9D9 requires capturedR0=Y7, unchanged original prefix and no
intervening mutation/IRQ; raw state retained, no timing-equivalence claim.
Exact9D9 capture via32nd9D8 comparator needsDO exit confirmation.

Selected post minimum now omits Xpost's eight skipped words, upstreamY8F..91
and initialYF64..68 only under the overwrite/linear-addressing proof. Correct
Ypost formula is S+0C (12decimal words), not S+12hex. Previous exports preserved.
See runtime-snapshot-schema.md and runtime-snapshot-acquisition.md; exports:
builds/phase20b-snapshot-design/final-v4/. Stock5E cannot freeze/capture CPU or
stack; sequential reads are insufficient. Hook routes remain design hypotheses
with placement, stack, transport and recovery gaps. **Flashing justified: NO.**
Next: qualify actual DSP TAP exposure and controller capability using existing
documentation. Any physical inspection/connection requires separate authorization.

## Phase20B7 disposition — 2026-10-07

**STATIC CHECKPOINT RECONSTRUCTION remains EXHAUSTED.** No broad checkpoint,
event association, firmware patch or stock replay resumed. Documentation-only
OnCE qualification found a visible candidate six-pad footprint beside the public
V3.2 DSPB56724AG board, without package-to-pad continuity proof. J3 evidence points
to MCU SWD. Physical statusREADY-FOR-PIN-VERIFICATION (conditionalactualunit),
toolingPLAUSIBLE TOOLCHAIN, qualifiedcontrollerNONE. Coherence/raw-stack/full
pipeline capture and active ARM/DSP provenance remainUNRESOLVED.

External OnCE remains preferred conditionally; not disproved, hook not promoted.
Connection/flash/capture admissionNO. Single next step is separately authorized
limited powered-off actual-board identity/continuity verification, not debugger
attachment. New notes:circuit-dsp-tap-qualification.md,once-controller-qualification.md,
snapshot-coherence-plan.md; guarded deterministic reportsfinal-v2/checks-v2 under
builds/phase20b-tapqual/. No snapshot acquired and no unknown value replaced.
