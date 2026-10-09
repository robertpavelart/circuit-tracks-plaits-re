# Phase20C5 — software-enforced persistent state design

## Current Phase20C6-ARCHSELECT — 2026-10-07

**SELECT-A, CONDITIONAL preference; patch readiness remains PARTIAL.** Equal
comparison retains the P:[3FF0,3FF7) design because its original auxiliary/
guard/post behavior is specified. B's lower X-state cost is real within the
sealed timing model, but no seven-word takeover subset or finite bypass contract
is qualified. Global A admission risks are retained, not minimized by assertion.

Known A origin instructions5, proposed windows4, conditional unchanged literal
reviews10; all additional adapter/control boundary totals remain unresolved.
Same natural9D9 save set26 for both; no minimal all-mode reduction proved.
Paired hypothetical P-workspace plus wrapper mean12629.78/max-style19516 for A,
8461.54/14341 for B; guard/bypass/converter/retained stock costs excluded. Complete
costs remain null. No existing866/1626 budget target became an upper bound.

Authentic full boot is not required for a constrained offline fixture, but all
required edits/continuations must be finite. Neither architecture meets that
gate now. Next only20C7-A-COVERAGE: reuse existing candidate obligations and
close required exemptions/adapters/typed P-control boundaries. No next phase
started, image emitted or hardware justified. See plaits-architecture-selection.md
and plaits-selected-takeover-feasibility.md; phase20c-archselect/final-v1.

The Phase20C5 design below is preserved as evidence.

2026-10-07. **Overall PARTIAL. Design only.** Exactly two domains considered;
appended P is preferred. No safe ownership certificate, object reservation,
DSP patch, extended boot stream, executable test image or flash-ready image was
produced. No hardware, packets, debug probes, downloads or broad memory search.

This phase supersedes the *next design step* in Phase20C4, not its REFUSED natural
ownership result. Existing numerical P-state qualification stays sealed.
VERIFIED means checked original bytes or pinned manual facts; TESTED refers to
design-spec tests unless explicitly referring to the earlier numerical suite.
MEASURED is existing trace data. CALCULATED costs are conditional software models,
not hardware measurements. No BOUNDED-PROOF of complete modified-runtime ownership
is claimed. CONDITIONAL and UNRESOLVED gates remain explicit below.

## Domain decision

|Exactly two domains|Required exclusions/change|Cost and consequence|Decision|
|---|---|---|---|
|A. appended P:[3FF0,3FF7)|Typed owner P stores/reads; fixed memory mode; DMA admission; complete CPU control-register/store and control-flow coverage; trusted quiescent startup|Existing high-P renderer549P, conditional mean12111.7855/max18510 cycles before proposed workspace/wrapper; retain all stock lookup/auxiliary work; block P-DMA during ownership|**CHOSEN, CONDITIONAL architecture**|
|B. reclaimed X:[57B,582)|Remove selected preparation/lane producers AND consumers in both passes before use; guard every foreign X commit/DMA; replace request/results/auxiliary/guard contract|Existing high-X renderer549P, conditional mean7943.5521/max13335; selected original generator DISABLED; complete takeover cost UNRESOLVED|**Not selected; more invasive fallback**|

The X candidate is exactly the first seven words of slot0's active 42-field
generator record, not spare RAM. Slot stride4A separates neighboring records
geometrically, but excludes neither shared writes nor host/foreign aliases.
Domain A avoids surrendering those active fields. No third storage search.

The selected numerical bank0/slot0 label is the established selector contract;
equating every such numerical context with a particular UI Synth1 voice remains
conditional. The proposal is one mono selected path for the entire runtime;
other slots and bank1 retain stock processing, subject to new global admission
and timing costs. There is no mode switching or polyphony implementation.

## Explicit ownership and activation

The seven numeric words are **P:[0x3FF0,0x3FF7)**, private to the owner initializer
and renderer. This is a proposed allocation under the conditional compatible
core0 MS110 mapping P:[0,4000), X:[0,6000), Y:[0,4000). Equal numeric X/Y addresses
are not aliases of private P under that mapping. Capacity is not ownership.
No actual memory mode, physical core assignment or ROM residue was fabricated.

The ownership epoch must start only after a trusted modified entry has:

1. Established immutable code/control-flow boundaries and the full writer policy.
2. Quiesced all eight DMA channels, accounted for pending words, and validated
   mapping, numeric/stack/interrupt profile and compatible handoff state.
3. Completed original initialization with early DMA arming gated/reordered;
   P:2A3D/2A3E cannot arm unreviewed configurations before admission.
4. Explicitly initialized all seven words and the separate temporary/control
   objects, then armed only admitted audio/configurations.
5. Entered a dominating, one-way bank0/slot0 gateway.

Ownership persists while the selected voice is idle and across every render;
slot reuse is not permission to restore its stock generator. Reload/reset or
diagnostic transition ends the epoch; the next payload must repeat admission
and initialization. No live fallback to the original selected generator.

No eighth numeric or activation flag is proposed: the one-way gateway is a
control-flow contract, **not yet proved**. A separate diagnostic fault word at
P:3FE0 is explicitly budgeted for denial reporting; it is additional persistent
metadata, not concealed in a phase/frequency field. Without control-flow and
startup closure, absence of an activation flag proves nothing.

## Initialization and temporary objects

Exact existing integer-renderer seed, in word order:

|P address|24-bit value|
|---|---|
|3FF0|000000|
|3FF1|000000|
|3FF2|200000|
|3FF3|000000|
|3FF4|00A3D7|
|3FF5|200000|
|3FF6|000000|

**CALCULATED:** seven unrolled long immediate loads plus long MOVEM stores,
28P/63 nominal startup cycles. Write after pending old transfers have finished,
not merely after loading literals. No per-block reinitialization. Temporary
frames/shadow/status must also be initialized before first read; their complete
startup implementation/cost is UNRESOLVED.

Proposed objects, all covered by the same future ownership policy:

|Purpose|P interval|Words|Lifetime|
|---|---|---:|---|
|Serialized policy save/config frame|[3F60,3F7E)|30|One nonreentrant guarded transaction; R0 read-only ABI|
|Typed control shadow|[3F80,3FA0)|32|Provisional 16x2; DO/call/IRQ/data protocol/headroom unqualified|
|Renderer save frame|[3FC0,3FDA)|26|One selected invocation|
|Renderer spills|[3FDA,3FDD)|3|One selected invocation|
|Fixed controls/frequency inputs|[3FDD,3FE0)|3|Prepared before selected render|
|Diagnostic fault latch|[3FE0,3FE1)|1|Ownership epoch|
|Numeric retained state|[3FF0,3FF7)|7|Ownership epoch|

Total **102P data words**, of which only seven are numeric renderer state.
These are deliberate proposed appended objects, not claims of naturally free
memory. Separate policy and renderer frames prevent sharing an interrupt-live
save frame. Two-word fences/guard bands and padding surround them; code is
limited to [2A5E,3F5C), **5374 conditional P words**. Fences are diagnostic aids,
not protection against an unrestricted writer or computed entry.

Peak19 scratch values versus16 helper-preserved registers leaves three spills.
Using M1..M3 as data would add three saves/restores and require AGU/IRQ mode
qualification (26 becomes29); no free-register claim. Preferred scratch strategy
converts the remaining18 long X sites to long P MOVEM at the explicit objects.
This conversion has **not been implemented or executed**.

Save alternatives: protected P26 frame costs104P/364 nominal cycles for52
transfers. Hardware-stack-only saving needs at least13 paired48-bit entries;
13+renderer3=16 before stock caller/IRQ frames, exhausting the documented16:
**REJECT**. X:[2CCC,2CEC) temporary loan would cost104P/104 nominal cycles but
loan lifetime, host/DMA and later readers remain UNRESOLVED. Three foreground-dead
A words could save12P/42 cycles, but IRQ saves incoming A before P:9DD; keep the
bounded26 set until that observable behavior is closed. R0 is already excluded
because P:9D9 reloads it. Raw MOVEM/CCR/stack/IRQ ABI is still a wrapper gate.

## Costs and conditional one-voice envelope

Existing TESTED high-P state renderer:549P, conditional model
10785/12111.7855/18510 cycles min/mean/max. State-transfer premium versus high-X
is3855/4168.2334/5185. These are from sealed Phase20C P-state evidence, not a new
Circuit run. Its 43 cases,240640 samples, seven-state equivalence and2048-block
continuity do not qualify the proposed guard/workspace/wrapper.

Reading the existing34997772-PC trace yields7/20.3984/118 remaining X transfers
per block. A hypothetical same-width P conversion adds35/101.9920/590 nominal
cycles; paired inferred renderer totals10820/12213.7775/19100. **CALCULATED,
unexecuted**, with any new interlocks/ABI effects still to qualify.

Conservative conditional renderer relaxation:
`13379 + 1964 + 5*81*33 = 28708`.
This carries the old valid-control algebraic bound, long-address relaxation and
an overapproximation of at most33 visits to each of81 static memory sites.
Private zero-wait compatible numeric mode and unchanged renderer arithmetic
are conditions. It excludes global scheduler, DMA waits, IRQs and new policy.

|Runtime component|Added nominal/model cycles|Classification|
|---|---:|---|
|26-word P save/restore|364|CALCULATED; raw/IRQ ABI pending|
|Selected dispatcher|24|CALCULATED template|
|Fixed control/frequency setup|25|CALCULATED; actual pitch converter excluded|
|Return to original9D9|3|CALCULATED|
|Wrapper subtotal|416|Partial only|
|Selected writer suppression / retained combiner delta|0|None suppressed in A; stock combiner562 retained|
|P204B cloned helper entry|4 per call|CALCULATED|
|P204B peripheral classifier|21 extra per fast record;19+U_validator per slow record|Template, unassembled|
|SHI commit classifier|4..60 per simple unindexed X word|Bit-test template; false-branch penalty included; root admission/advance/reply extra|
|DMA admission / other actual-EA guards / control-flow checks|UNRESOLVED|Cannot claim finite total|

One-voice **partial** expression:

`28708 + 416 + Q*(4+21*Nfast+(19+U_validator)*Nslow)`
`+ serviceguards + otherEAguards + CFI + converter + interlocks + IRQ/DMAwaits`.

For illustrative Q=1,Nfast=20,Nslow=0: **29548 plus unresolved terms**. Neither
Q=1 nor N<=20 is established for normal stock operation; enforcing an N cap
would change the whole loop and require feature accounting. This is not a
one-voice WCET or a deadline-fit claim. DMA admission is nonblocking at runtime:
return NOT_READY if a configuration is not certified quiescent; no polling loop.

P sizes, **CALCULATED unassembled partial**:
renderer549 +save104 +controls10 +dispatcher16 +retained combiner clone32
+return1 =712; guarded P204B clone89 +partial SHI clone37 +initializer28 =>
**866P known subtotal**. No extra width for moving seven state operands to3FF0,
the remaining18 long operands to P, or retargeting renderer output. Replace the
renderer-internal two-word `move #>0,r0` with2C46; an outer setup is overwritten.

Planning allowances256 validator+96 startup+128 CFI+64 reply+216 simple Rn
veneers produce **1626P**. These are budget targets, not assembled costs or upper
bounds. Caller adapters, displaced instructions, actual indexed/modulo/parallel
EA calculation, pitch/headroom and complete initialization remain extra. Naively
inlining24P at344 candidates costs8256P, exceeding5374. Centralization and proved
exemptions are necessary; no fit certificate follows from1626<5374.

## Stock impact and readiness

The full32-row matrix is `feature-impact.csv`. A preserves old selected request/
completion producers/readers and auxiliary/guard data; selected mono output is
replaced. Synth2 and nonselected paths keep original arithmetic/state by design,
but system timing and global denied DMA/register requests can still affect them.
FX/post modes1/2 may retain stock auxiliary contributions; pure Plaits-only
output is not claimed. DMA P copies/overlays are DISALLOWED during ownership;
unknown legitimate users remain UNRESOLVED, not declared harmless. Unrelated
services are not globally disabled; forbidden writes must return an error.
Reload/update ends ownership. MIDI/drum/pack/project impact of global admission
is still UNRESOLVED where dependencies have not been closed.

|A–R requested final decision|Result|
|---|---|
|A chosen domain|CONDITIONAL appended P|
|B exact seven-word object|P:[3FF0,3FF7), not reserved|
|C epoch|Trusted admitted startup through reload/reset; one-way selected gateway|
|D P204B protection|Whole-helper guarded clone, preserve prefetch/DO; actual X-control commits admitted|
|E DMA|All8 reviewed; no stock P source/destination; pinned audio0/1; safe X/Y2..7 conditional|
|F service|Actual X/Y commit check per word; deny/advance/report; no numeric X/P alias confusion|
|G selected writers|None removed in chosen A; B must remove selected387/77F producers|
|H selected readers|Old selected consumers retained in A; no stock reads of new P data; B requires bypass|
|I init|Exact7 seed after quiescence;28P/63 nominal cycles|
|J save|Separate protected P26,104P/364 cycles; stack-only rejected|
|K stock impact|Selected mono changed; global policy impact conditional/unresolved; explicit feature matrix|
|L added P|866 partial,1626 planning;102 proposed data; complete size UNRESOLVED|
|M added cycles|Component table above; complete per-block delta UNRESOLVED|
|N one voice|29548+unknown under illustrative Q1/N20; no complete bound|
|O offline patched test image justified?|**NO**|
|P hardware flash justified?|**NO**; recovery independently unqualified|
|Q largest blocker|Actual-EA/commit and control-flow coverage; no stock centralized trap|
|R next|Finite ISA/source coverage certificate, exemptions or exact adapters, before construction|

The missing certificate includes trusted pre-quiescence entry, memory/ROM mode
preservation, all indirect-control/return paths, typed owner capabilities and
CPU writes that could configure DMA/control registers. Guarding only SHI and
P204B cannot guarantee ownership. Software observation without mediation is
insufficient. The next work is confined to these enumerated control points and
the344 decoded candidates, not another free-memory or broad alias census.

Recovery remains a separate future normal-external-interface acceptance and
rollback gate; no dependency on board access or OnCE/JTAG/SWD.

## Reproducible evidence

Canonical `builds/phase20c-enforcedstate/final-v3/`, `repeat-v3/`, `checks-v3/`.
All14 requested reports plus33 supporting members;47 members repeat identical.
17 TESTED boundary/space/DMA/quiescence/refusal/arithmetic tests;
797 guarded original/firmware/renderer/prior-evidence inputs unchanged.
8682 DSP listing rows byte-checked by reused reader. Old trace counted only;
stock CPU execution0, new renderer execution0. No native guard assembled.
`probe-v1` and v1/v2 exports are preserved. Finalized predicate rejects incomplete
channel snapshots; v2 adds chip-specific DTD6/7 evidence and the DCH caveat.
V3 corrects the bit-classifier false-branch timing to4..60, with explicit
instruction-cost arithmetic and pinned appendix pages.

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B tools/ct_enforcedstate_design.py --output-dir builds/phase20c-enforcedstate/new-final
& $taskPython -B tools/ct_enforcedstate_design.py --output-dir builds/phase20c-enforcedstate/new-repeat
& $taskPython -B tools/ct_enforcedstate_verify.py --first builds/phase20c-enforcedstate/new-final --repeat builds/phase20c-enforcedstate/new-repeat --out builds/phase20c-enforcedstate/new-checks
```

Outputs must be fresh children of the phase directory; overwrites refused.
Original hashes remain SYX `bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd`,
BIN `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da`,
Selection0/channel0 `b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855`.
