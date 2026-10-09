# Phase20C2 — exact seven-word layout and initialization contract

## Follow-up P-object test — 2026-10-07

**IMPLEMENTED/TESTED standalone:** allseven exactinitialrawwords below are loaded
from21validatedBE24bytes into a poisoned syntheticPobject once percase. All43
cases,including2048continuousblocks,match theunchangedintegeroracle andsealed
REGOPTsample/statevalues. Noextraflag; noresetbetweenblocks. **Circuitinit remains
REFUSED:** illustrativeP[2D29,2D30) is outsideoriginalPupload[0,2A5E); enlarged
ownedobject/authenticloader/mode/epoch notqualified. Details andcosts:
plaits-p-state-qualification.md. The20C2 statement below that noCPUexecution
occurred is historical; the follow-up ran onlyisolatedstandalonecode.

2026-10-07. **VERIFIED source layout; CONDITIONAL initialization design.** No
state block or initialization PC qualified. Renderer/oracle remain unchanged.
No firmware patch, CPU execution or arbitrary reset-state assumption.

The source is `plaits/poc/fixed_model.py`, Program.names in generate.py and the
sealed REGOPT assembly/layout. User descriptions such as previous phase and
integrator do not imply extra fields. The actual retained order is:

|Offset|Name|Format/role|Exact baseline initialization|
|---:|---|---|---:|
|0|phase|Q2.22 phase, including legal deferred-wrap excursions|0|
|1|next|signedQ3.21 delayed naive/BLEP/integrated-BLEP contribution, consumed as next sample's this|0|
|2|previous_pw|Q2.22 previous sample PW; event denominator uses previous_pw−pw+frequency|0x200000|
|3|high|boolean0/1, PW-crossed/unwrapped event state; not a previous-phase word|0|
|4|frequency|Q2.22 retained current frequency, next block interpolation starts here|41943 /0xA3D7|
|5|pw|Q2.22 retained current PW|0x200000|
|6|shape|Q3.21 retained current shape|0|

Frequency41943 is exact positive round(.01×2^22), from the existing baseline
initializer. It is not a recovered stock pitch or a new oscillator algorithm.
There is no separate previous-phase word or additional integrator scalar.
Signed data/rounding/state ordering must remain exact in any future storage ABI.
Future X addresses are null: seven-X ownership is REFUSED.

## First activation

Preferred contract: after a **proven ownership transition**, explicitly initialize
all seven words once, before the first render. Do not reset them every block.
Startup clear is acceptable before that store, but the existence of an earlier
clear says nothing about values at an arbitrary later activation. Stock selected
paths can overwrite the current candidates in between.

For fallbackB, a future owned P data object could include these exact initial
words in the enlarged count/load payload, before execution atP0. This would
establish a cold-upload epoch only after loader/object/P-writer/memory-map proof.
It is a structural design, not a built image or replay seed. Selection reload or
mode changes end the epoch unless separately proved compatible.

## Flag requirement

**CONDITIONAL: zero extra persistent words are needed** if deterministic startup
initialization is proved. A first-entry wrapper can also use frequency0 as a
marker if an owned startup operation explicitly publishes it and the wrapper
initializes all seven before entering the renderer. Zero must never be passed
as a valid retained frequency or inferred from unknown activation RAM.

The positive-frequency invariant follows the unchanged interpolation:

`f(k) = c + floor(k*(t−c)/32), 0≤k≤32`

For legal c,t≥1, f(k)≥min(c,t)≥1. The positive target domain and qualified numeric
modes are prerequisites. Thus frequency0 is outside the legal retained domain;
it can encode a marker without changing valid state representation. This is
not protection against foreign writes: a service clear to frequency would still
violate ownership and could spuriously restart the oscillator.

If a separately armed dynamic first-entry flag is required, it needs **one more
persistent word, eight total**, with independent ownership/initialization. An
extra uninitialized flag does not solve arbitrary RAM activation. No flag word
was allocated or implementation selected.

## Falling back to stock

Current candidate X fields are not safe dormant Plaits storage. Original generator
preparation, event reset and global scratch overwrite them; an unchanged stock
path cannot reconstruct their Plaits histories. Under fallbackA, selected takeover
must be one-way until a separately designed reset/reinitialization/recovery epoch;
do not implement dynamic switching. Other slots remain independent stock paths
only after writer/reader proof.

Under an owned fallbackB P object, numeric dispatcher fallback could leave Plaits
state dormant because retained private X/Y producers do not directly write P.
This is conditional on all P/DMA writers, OMR/cache mode and upload epochs being
closed. Re-entry behavior is retention within that epoch, explicit re-seed after
reload, never guessed stock defaults. Idle/retrigger policies remain separately
specified; this phase does not redefine note allocation or envelopes.

**Readiness:** numeric initialization values and the marker lemma are bounded.
Actual state ownership, first activation PC, cross-block persistence and guarded
execution are unproved. No qualified-set lifetime fixture or executable patch
construction, and flashing remains NO. See plaits-fixed-state-ownership.md.
