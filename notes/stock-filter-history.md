# Phase20B3 — retained histories and coefficient admission

2026-10-07. **PARTIAL source provenance / numerical values UNRESOLVED.**
Reports: `builds/phase20b-inputrec/final-v3/history-provenance.csv`,
`history-initialization.json`, `coefficient-values.json`,
`seam-admission-matrix.csv`.

For selected slot0 S=59F and post-stateR4=S+12(hex)=5AB.
Fresh original nonlinear1 and BDD/C2D instructions confirm:

|Y history|Selected reads|Selected writes|Proved behavior / numerical origin|
|---|---|---|---|
|5AB|ACC|AD0|previous nonlinear control; value unknown|
|5AC|AEE|AEF|retained derived ramp value; value unknown|
|5AD|AF5|AF6|retained derived ramp value; value unknown|
|5AE|BED/BF3|BFD|smoothing of current prepared control; value unknown|
|5B7|C2D/C33|C34|coefficient-control prior word; value unknown|
|5B8|C04/C2D|C08/C3C/C2A|prior smoothing/peak word; value unknown|

**VERIFIED:** boot clear2789 provides zero only in its initial epoch.
Trigger33B..33E clearsY:[5AF,5B7) andY:[5BD,5C5). All six listed
words lie outside these half-open ranges. Even5B7, adjacent to the first
range, is not cleared. Repeated processing replaces their values. No recorded
last writer/number before a selected event is supplied by the patch archive.

The table lists selected-path writers, not an exhaustive generic alias census.
No absence-of-initializer claim is made across arbitrary modes/host aliases.
Candidate patch load, allocation, mode change and reassignment have not yielded
a bounded numerical last-writer chain for this exact invocation. Zeroing at a
trigger, allocation or file load would therefore be an unsupported history
injection. These remain explicit rejected candidates, not emulated origins.

AtBDD/AA8, previousY5AB affects normalization/ramping; Y5AC/Y5AD affect ramp
state. BFD updatesY5AE before downstream coefficient construction. C04/C08
usesY5B8 prior peak; C2D reads/updatesY5B7 andY5B8 before table interpolation.
Consequently a known current patch/control alone cannot reconstruct five
numerical coefficients independently of this prior state.

**VERIFIED original last local writers:** YF68←C65,YF67←C78,YF66←C7C,
YF65←C7D,YF64←C7E. OriginalC2D generates them before the selectedC9D
consumers, assuming the natural producer path is admitted. InitialY table
contents need not be guessed because that producer overwrites them. Its
inputs and modes, however, remain material. All five report values are null;
neither original CPU execution nor an independent numerical reconstruction
has been performed. No floating reference is substituted for stock arithmetic.

**UNRESOLVED material context:** SR SM20,SA17,DM14,S0/S1; OMR mapping;
modifier retention and full-accumulator pointer materialization; inherited
SP/SC/SSH/SSL/LA/LC/LF/FV prefix; natural generator/worker data andX2C66 guard.
Existing conditionalY19=81FF (multiple-wrap512),Y1A=FFFF (linear), local
N-strides and M5 restoration are preserved, not promoted to a full context.
657 does not set incoming address modifiers. Its owned DO loops close at758;
that is not a proof of empty inherited loop/stack state. C9D'sCA2/CB6 scaling
updates do not prove657 or C2D entry scaling.

All checkpoint candidates33F,37A,657,387,C2D,9D9 remain refused. Preparation
traces and stock-seam traces contain refusals with zero original instructions,
null cycles and no measured mutations. Stock replay cannot yet resume;
Plaits-fed replay is not justified. No patching, RAM reservation or hardware
readiness conclusion follows from this focused record qualification.

## Phase20B4 — parameter origin versus retained history

Original3602A's zero-fill applies toARM macro correction work halfwords,
not these retained DSP histories. Project full-copy/macro-only parameter loading
does not establish numerical last writers ofY5AB..5AE/5B7/5B8. No bounded
project-local origin admitted. Stored macro contexts are conditionally materially
different atX2E8/X2EA andX3E7 target; later event automation and source histories
remain unresolved. Coefficients/history values remain null and0 DSP instructions.
# Phase20B5 continuation — no bounded numerical origin (2026-10-07)

**UNRESOLVED / STATIC STRATEGY EXHAUSTED.** Project0 consumer/notification
tracing does not provide last numerical writers forY5AB..5AE/5B7/5B8.
Known selected trigger clear ranges[5AF,5B7),[5BD,5C5) exclude those six
words. Patch loading and ARM macro-work clears are not DSP history resets.
No all-runtime absence-of-reset proof claimed; no zero/neutral history injected.
Proposed observation uses actual slotY[S+12,S+1A), S=59F+28*i; slot0
[5AB,5B9), including recursive histories. Xpost base uses different stride
Q=57B+4A*i. See static-checkpoint-limit.md; no snapshot acquired or CPU run.
Earlier static-next-step text below is superseded by the Phase20B5 stopping rule.
