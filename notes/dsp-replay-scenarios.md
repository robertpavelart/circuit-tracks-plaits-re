# Phase 18 — deterministic stock replay scenarios

DESIGN ONLY,2026-10-06. No scenarios executed. Preconditions and coverage are
part of the result; a blocked/no-target execution must not count as success.
See dsp-emulator-spec.md for core/map/peripheral constraints.

## Event representation and provenance

Each scenario manifest binds image/core/map/initialcheckpoint/table hashes,
explicit unknowns, eventordinal/virtualtick, actor/space/address/value, source
ARM/DSP instruction, normal/init/service classification and scheduler placement.
Use normal ARM→DSP addressed word transfers at the SHI ingress with recovered
commandlane/word width and stock156 handler. No USB/UI/MIDI parser required and
no external packet constructor/transmission. Host-modelwrites are logical
offline events, recorded separately; directRAM fixture overlays are unit tests,
not fullhost/scheduler evidence. Never use service5E for normal scenarios.

Normal scalars from292F8/291E0 transmit upper24bits; addressbit15 selectsY.
Event sequences must preserve bank/slot arithmetic, exact conversions, write
ordering and release readback decisions; do not independently randomize fields.
Unknown patch/table fields block a scenario rather than become zero defaults.
No claim that all legal ARM publishers/worker jobs are recovered.

## Scenarios 0–5

| Scenario | Inputs/lowest-level source | Required outputs/coverage |
|---|---|---|
|0 startup+idle|Stock0→100→25DB; modeledworker startup; source-boundhostC00/2000/2200/1600 tables andnormalenable events|Startupclear/copies/cursors/descriptors,mainenable,one32-frame block,203A loads,allstores; fullstartup blocked byunresolvedY4000..6000/EMC/hostdata semantics|
|1 one group note|ARM219E8 slot/bank selection and21246 event publication;Y159 note target,Y14D envelope target andremaining required fields|Lifecycle281/29D,eventclear29E;request/completionphase;gain/mix32samples;203A/high-X ledger|
|2 multiple notes/slots|Slots0..5,then6..11/bothgroups with recordedallocation/release ordering from21C48|Descriptor/scratchreuse,workerqueue ordering,release/held/steal variants only wherepreconditions justified; not fullUI allocator emulation|
|3 patch/parameter|Knownnormalbank/parameterpublishers andconversions frombank-selector/voice maps|Bothbanks,retainedstate,descriptor/cursor/count preservation;exact source/value domains required|
|4 filter/effect|Validateddispatchindices/55-entrytable andnormalparameter writes|Selectedeffectbranches,ring/modifierrestore,scratchwrites;1F5C A/B conditionalfixtures separate ifnormal1E15 pathnot reached|
|5 transport/state|Recoverednormalenable/reset/banktransitionfields andorder only|Mode/epoch transitions,cursor/descriptorcount preservation; currentlyBLOCKED whereexactpublisher sequence unresolved|

Scenario1 example verified address formulas, not a complete preset fixture:
D=EB+8i;D+7=F2+8i bank word;E=57A+4Ai contains packedstart/update withbit23;
Y159+60i receives signed(note−60)<<16;Y14D+60i receives converted event-level
envelope target. ReleaseE=800000 follows212EA/2136E; fullrelease working-field
writes/readback decisions must also be modeled. Phase4source tables remain
authoritative; do not infer gate solely fromY150 or assign arbitrary Q coefficients.

Fixed events can be placed before/after selected instruction boundaries to test
interleaving variants. Emit all event schedules/manifests; arbitrary injection
into mid-parallel execution is prohibited unless architecture allows it.
Repeated blocks,changednotes/parameters and ringwrap must be explicit finite
coverage counts, not inferred from a single32-frame block.

## Conditional unit fixtures, separate from normal scenarios

U1: enter whole1F5C with callerA pointersX1D40=1800,X1D41=1840,X1D42=18E0,
or callerB19F0/1A30/1AD0. Derivecursor/constants from260A and140;X3A32,X3B16,
X3C31,Mregisters validated. RequiredYcoefficients/state andX2C8A/1D43 ramp
data need explicit fixture provenance. Return to a realcallerPC boundary using
modeledstackstate; externalstop predicate, noPpatch. Expect16×32=512 stores
at1F97 plus64initialclearstores separately. This validates localreach only.

U2: enter202B under validatedstockmode, stock-derivedzeroX35F and declared
following table fields. Record203Aload,zeroDOskip and absence204B. Synthetic
count1 fixtures exercise204B with boundedtestdata, tagged **UNIT_FIXTURE**:
they do not identify a normalpositivecount publisher. Never start directly at
203A or204B and call the result a normalstockentry.

## X35F and high-X reporting

Log allactors' X35F stores (includingzero/same-value),every actual203A execution,
actual loadaddress/value and pre/postR0/M0/PC/caller/IRQ context. Record current
X35F atentry and its actualreadtransaction. Success for a modelednormalrun
requires targethitcount>0,completehooks/events and everyobservedloadvalue0.
The recovered normal-entry profile additionally requires R0=35F at the actual
203A load and a zero X35F entry snapshot; a different address/entry mode is
a divergence requiring classification, not a passing count observation.
Nonzero means a counterexample **to that model trace**, requiring source/event
attribution before a claim about stock. No targethit/incomplete/unknown=BLOCKED
orNO_COVERAGE, notPASS. Never resetcount silently to finish a test.

ForX[5F00,6000),log each logical/canonicalstore withPC/callpath/scenario/value/
actor/epoch. Bootclear is expected INIT_TOUCH, not an after-initownershipfailure.
Choose a reproducible normalstartcheckpoint boundary afterallvalidatedINIT;
subsequent clears still count asnormalstores ifnormal events trigger them.
UnchangedRAM values do not exclude same-valuestores. Report attempts/unmapped
faults and alias-translatedstores as separate evidence. Absence in finite
scenarios is **empirical modeled coverage**, notAVAILABLE or universalPROOF.

Main high-X private bank must remain distinct from worker-private numerical
addresses. Sharedalias use must have explicitbacking resolution; no numeric
proximity inference. Anyunknown bypass invalidates both property conclusions.
