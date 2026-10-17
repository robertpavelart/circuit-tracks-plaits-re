> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20C6 — architecture selection

2026-10-07. **SELECT-A. CONDITIONAL preference; executable patch readiness remains
PARTIAL.** A has the better-specified route under the currently verified mono,
auxiliary and guard contract. This is not a proof of minimum elapsed engineering
time, global safety or hardware readiness. Neither architecture has a complete
finite patch set today. No implementation of the next phase was started.

All work was offline: original bytes and sealed ledgers were read, static
comparison reports and tests were created. No DSP execution, new numerical
renderer run, firmware patch/repack, packets, hardware, debug probes or memory
reservation. No new universal writer census or broad memory search. The device
must remain physically unopened. Future interaction is limited to normal USB-C,
MIDI and microSD/pack mechanisms where applicable; none was used here.

## Decision and equal comparison criteria

**A** reserves P:[3FF0,3FF7) in a one-way selected bank0/slot0 epoch, preserves
all original request/completion work and the full combiner, replaces mono32,
and returns to original P:9D9. Its global control/service/DMA policy and typed
P ownership are not yet qualified.

**B** would remove selected stock generator producers and consumers, reclaim
seven existing words and retain the necessary scheduling, auxiliary, guard and
post work. It could be more local and cheaper, but no seven-word subset and
complete replacement contract have been qualified. Disabling one producer does
not exclude reset, host/service, DMA or foreign indirect writers.

|Criterion|A|B|
|---|---|---|
|Stock modification surfaces|5 identified origin instructions in4 windows, plus unresolved sets|3 known anchors, not complete edits; dependency/bypass sets unresolved|
|Behavioral scope|Global admission and latency risk; selected mono changed|Local intent; shared routines, queues and external writers still matter|
|Ownership|Explicit P7 plus protected workspace/control objects, unproved|0 qualified words among84 selected-context candidates|
|Writer exclusion|Existing finite control/commit obligation ledger|Selected bypass alone does not prove foreign-writer exclusion|
|Save burden|Conservative26 words|Same26 at comparable natural9D9 boundary; no qualified reduction|
|Size|866P known partial,1626 planning,102 data|740P comparable-boundary constituents,39 minimum data, unknown bypass/protection glue|
|Cycles|Higher P-state cost and global guard overhead|Lower X-state numerical cost; retained/removed work and guard overhead unknown|
|Init|Exact once-only seed after admitted quiescence|Selected reset is not a proven ownership/seed transition|
|Failure|Incomplete guard can corrupt code or global DMA behavior|Wrong bypass/discriminator/cursor can affect queues and unrelated paths|
|Recovery|Unqualified normal-interface rollback|Same independent gate|
|Unrelated paths|Original arithmetic retained; global policy effects unresolved|Requires correct selected gates in shared routines and original fallbacks|
|Auditability|Retained original auxiliary/guard/post behavior is specified|Seven-word isolation and replacement dependencies not yet specified|
|Offline testing|Renderer exists; complete protected patch not finite|Renderer exists; complete takeover patch not finite|
|Future scaling|More protected objects/addressing/compute proof needed|Per-slot takeover and dependency proof needed|
|Final controls|Pitch calibration, PW/shape mapping and headroom unresolved|Same plus compatibility with retained stock sub-generators|

B's locality and cost advantages are **CONDITIONAL**, not demonstrated whole-
runtime advantages. A wins this comparison because it preserves a known required
contract; B would first need to prove an isolated object and an auxiliary/guard
replacement. This does not prove B impossible or prohibit revisiting it if that
contract becomes available. Do not advertise global A changes as harmless.

## Selected state and takeover evidence

`selected-slot-state-map.csv` labels552 individual addresses in the nominal
selected objects and identified shared dependencies. It does not claim the full
dynamic kernel/queue extent is known. UNKNOWN words are retained by policy.
Full nominal control V96 and sample S40 are represented word by word.

|Object|Exact half-open interval|Required treatment|
|---|---|---|
|Descriptor|X:[EB,F3)|Retain8 fields including function, pointers and bank|
|Control V|Y:[11F,17F)|Keep lifecycle/envelope/note/allocator fields; unknown scalars not free|
|Event mailbox|X:57A|Consume/clear at29D/29E; retain|
|Three generator records|X:[57B,5A5)|42 fields,14 per lane; auxiliary/phase dependencies remain|
|Six current coefficients|X:[5A5,5AB)|Retain ramps/combiner state|
|Post coefficient tail|X:[5AB,5BF)|Retain selector, nonlinear/filter/gain inputs|
|Lifecycle update terms|X:[5BF,5C2)|Retain three update terms|
|Timestamp|X:5C2|Allocator-owned; retain|
|Start-reset tail|X:5C3|Known ARM writer, full role UNKNOWN; retain|
|Three mask/phase pairs|Y:[59F,5A5)|Required lane/guard state, not six free words|
|Six ramp deltas|Y:[5A5,5AB)|Retain|
|Post sample state|Y:[5AB,5C7)|Retain28 words|
|Nominal kernel bases|X:[1960,196C)|Dynamic associated footprint not proved isolated|
|Kernel reset mirror|Y:[1960,196C)|Reset stores verified; complete consumers UNKNOWN|
|Kernel coefficient footprint|X:[19F0,19FC)|Base+90hex, dynamic stores; nominal interval not a bound|
|Kernel source footprint|X:[1A80,1A8C)|Base+120hex source, no ownership surrendered|

Shared dependencies include Y:[A01,A61) lanes, X:[2C02,2C22) and[2C24,2C44)
auxiliary streams, X:[2C46,2C86) phase/mono scratch including2C66, pass/queue
globals, traversal cursors and bank0 sums. These are not selected persistent
storage. The queue begins at30002, but its full runtime extent is unresolved.
No separately proved persistent AUXILIARY-ONLY word was found: the sample/ramp
dependencies also feed mono or post paths; shared auxiliary buffers remain SHARED.

84 candidate words are classified, with **0 qualified** for takeover. The first
seven X record words are active, not naturally free. A conditional third-lane
phase-only slice might omit fields0,1,10..13 at X:597,598,5A1..5A4: six words.
Fields2..9 still enter repeat/branch/flags/coefficient/base/phase generation on
the inspected path. This is a thinning hypothesis, not a universal maximum or
ownership proof. Another kernel word would require dynamic producer/consumer
and other-slot closure. Replacing the auxiliary contract with new Plaits-derived
streams is a different, unvalidated selected-post design, not preservation of
the original auxiliary values.

## Exact obligations and edit counts

VERIFIED:9C8 computes lane0*c0;9CA stores pre-add A to auxiliary0 while adding
lane1*c1.9CD stores the first-two-lane sum to auxiliary1. Both are used by stock
post modes. Final mono alone cannot reconstruct those independent values.
Preserve lanes0/1 or qualify a new contract. Natural2C66 is produced by phase
stores around7F1 (sample16 on the selected track), not the combiner; do not
substitute zero, last sample, a checkpoint value or a new guard constant.

Both77F passes, bitmap publication, worker lookup result consumption, cursor
advancement, alternate phase-commit behavior, six ramps and Y7/R4 post cursors
remain obligations. Request cannot jump straight to9D9. B's earlier gate requires
its own selected discriminator; the proven late XCC=0/R4=5AB predicate cannot
be copied to an earlier entry with a different R4 value.

A identified origin instructions:9B9 dispatcher,202B helper clone entry,198 SHI
data clone entry,2A3D DMA0 arm,2A3E DMA1 arm. The two adjacent arm instructions
can form one whole-instruction window, giving4 proposed windows.10 other direct
audio literals/rearm sites are reviewed as conditional exemptions, **not counted
as edited sites**. New module save/transfer/init/validator/error/CFI components
are not existing stock sites. Complete edit count remains **UNRESOLVED**.

B has3 anchors:387 selected preparation,79D lane consumer and9B9 completion.
They are not3 fully specified patches. Reset333..339, phase/guard7E4..7F9,
cursor979..99D, bitmap791..799, worker queue operations, ramps9A5..9B8,
SHI198..19F and RMW2048/204B are additional dependency classes. Exact required
edits and continuation effects remain unresolved. Shared stock bodies must stay
available for every nonselected path.

## Save, initialization and service scope

Rerun of explicit liveness witnesses at the comparable natural9D9 boundary:
R0 is replaced before post use; R4 remains a post input;9DD defines full A.
IRQ168/16A/16C stores incoming A slices, and caller/all-mode observability is
not closed. Changing memory ownership does not waive that ABI. Keep the bounded
26 set: R1..R7,N0..N7,A2/A1/A0,B2/B1/B0,X0/X1,Y0/Y1,SR. M/OMR stay untouched;
loop/stack balance is a separate requirement. **No minimal all-runtime save set
or smaller B save set was proved.** Earlier B entry could add live-ins.

Comparable protected P26 saves cost104P/364 nominal cycles for either. A needs
the explicitly counted additional policy/shadow/status objects. B still needs
safe temporary workspace and appended code; reclaiming numeric X7 alone solves
neither. No hardware-stack or unowned short-X frame shortcut was admitted.

B cannot generally ignore or overwrite foreign state writes before use: phase,
delayed sample, previous PW, frequency/PW/shape history must survive blocks.
Resetting them on every selected activation is a different continuity contract.
The existing note reset seeds stock phase/envelope data, not all seven Plaits
values. A zero-frequency sentinel requires an owned reset and exclusion of
foreign zero writes; neither an automatic flag-free proof nor safe first entry.
B permits a narrower direct X7 check in principle, but a material reduction in
complete service/DMA/foreign protection has not been proved.

## Size and timing comparison

Existing TESTED549P high-address renderers: A P-state conditional mean12111.79,
observed model max18510; B X-state7943.55/max13335. These are standalone trace-
derived cycle models, not stock measurements or integrated worst cases.
State handling is already included: nominal P transfers mean5835.53/max7259
versus X1667.29/max2074; their difference is not added twice.

Equal planning scenario: same P26 frame, three P spills, three P controls, same
completion wrapper and original combiner. Existing7520 paired rows project:

|Partial component|A|B|
|---|---:|---:|
|Renderer plus hypothetical P temporary conversion, mean|12213.78|8045.54|
|Same renderer projection, max-style|19100|13925|
|Save/dispatcher/controls/return|416|416|
|Partial wrapper mean|12629.78|8461.54|
|Partial wrapper max-style|19516|14341|
|Loose conditional renderer+wrapper relaxation|29124|18729|

These conversions are **CALCULATED, unexecuted**. Neither row is an integrated
one-voice upper bound. A adds helper/SHI/DMA/control enforcement, converter,
eligibility, interlocks and IRQ/DMA waits. Its earlier illustrative Q1/N20
29548+unknown envelope is not a normal Q/N bound. B additionally needs exact
bypass/phase-only/scheduling/ownership logic and an identified retained-stock
slice. A retains all stock generator work (combiner562 included). For B, removed
work must be subtracted only after a real bypass proves it removed; no savings
were fabricated from an unimplemented branch. Whole-runtime mean/max/upper
remain null for both.

A866P partial and1626 planning targets exclude unknown complete glue;102P data.
B same-boundary constituent estimate549 renderer+104 save+59 controls/dispatcher/
combiner/return+28 init=740P, plus unbounded remaining glue. Its minimum explicit
data is reclaimed X7+temporary P32=39, with guard/control metadata extra and
unqualified. This is not a guarantee that B is smaller in total. No finite upper
range or capacity-fit certificate exists; conditional A code capacity5374P.

## Global risk, testing, scalability and next phase

A's global admission can affect bank1, other bank0 voices, MIDI tracks, drums,
FX, packs/projects, service and update paths. B has more local intent, but missed
producer/consumer suppression can reinterpret numeric words as pointers/counts;
bad queue progression or a wrong shared-routine discriminator can affect the
whole DSP. Better selected-only failure containment has **not been demonstrated**.
Rollback remains a separate normal-interface gate for both; no board/probe option.

A finite offline patched fixture needs all required origin edits and branch/
continuation effects specified. Known hooks alone do not meet this criterion.
Neither architecture qualifies now. **Authentic full boot is not required** for
an explicitly constrained offline fixture; its initial state/profile can be a
declared harness contract, not a fabricated authentic checkpoint. Runtime
pre-quiescence trust and hardware recovery remain separate later gates. Proposed
tests include negative writes, cursor/queue/bitmap progression, untouched guard/
aux/post state, fallback bytes, raw registers/IRQ/stack and continuity/reset.
No fixture was constructed in this phase.

Neither architecture is proved a scalability dead end. More mono bank paths need
separate objects/addressing and timing/ownership proof. MIDI1/MIDI2 internal synth
hosting or three voices each is not established by the existing12 contexts.
Controls/pitch calibration/headroom remain unresolved. No implementation/promise.

**Exact next phase:20C7-A-COVERAGE.** Close only A's required actual-EA control
commit exemptions/adapters and typed P/control boundaries, with exact origins,
continuations and costs. Reuse the existing344 candidate obligation ledger;
do not start another memory search or universal census. Qualify an explicit
constrained fixture profile rather than require authentic boot. Stop before
patched construction if the required set remains unbounded. This phase was
not started automatically. Offline patch now **NO**; flashing **NO**.

## Reproduction and validation

All16 requested reports plus12 supporting members in
`builds/phase20c-archselect/final-v1/`; repeat-v1/checks-v1.
**TESTED:**15 focused source/contract tests;28 members repeat identical;
851 guarded inputs unchanged;8682 original DSP rows byte-checked. State map552,
candidate map84; no ownership certificate. Probe-v1 is preserved and superseded
by the added kernel-offset evidence and final component cost tables.

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B tools/ct_archselect.py --output-dir builds/phase20c-archselect/new-final
& $taskPython -B tools/ct_archselect.py --output-dir builds/phase20c-archselect/new-repeat
& $taskPython -B tools/ct_archselect_verify.py --first builds/phase20c-archselect/new-final --repeat builds/phase20c-archselect/new-repeat --out builds/phase20c-archselect/new-checks
```

Fresh children only; overwrites refused. Sandbox setup failed on initial reads;
the approved fallback ran workspace report/test commands outside that broken
sandbox. This was an execution-environment failure, not an approval rejection or
permission to access hardware. All firmware/original byte guards remained intact.
