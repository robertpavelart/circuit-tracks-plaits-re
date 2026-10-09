# Phase 19C-FULLHELPER: joined original helper replay

## Phase 19C-PARENT — latest qualification result

2026-10-06. See [dsp-parent-replay.md](dsp-parent-replay.md).
**VERIFIED:** parent P[1E15,1F11), four JSR sites and ten DOs mapped. No
decoded external direct entry; initialized valid effect targets and descriptors
exclude1E15. Actual normal target/stack/cursor/count preservation stays
**UNRESOLVED**. **VERIFIED conditional:** the candidate D99 effect-chain
predecessor carries LF1, LA=DAF, LC1..5 across the helper calls; it is outside
the tested LF0 class. No depth/state was selected to force compatibility.
**TESTED:**13 static exports identical,7 gate tests/2 CLI refusals;0 new DSP
instructions. Prior complete-helper results remain BOUNDED-PROOF and unchanged.
An unexecuted trace is not a no-access observation. Next: targeted effect
selector/table producer proof; then qualify active-loop replay only if a real
parent edge is established. No persistent reservation or implementation gate
opens. Canonical evidence: builds/phase19c-parent/final-v3/ and checks-v3/.

2026-10-06. **TESTED / BOUNDED-PROOF:** the complete original helper executes
and returns in the explicitly qualified structural checkpoint class. Actual
normal-runtime entry into that class and authentic boot remain **UNRESOLVED**.
No hardware, MIDI/SysEx, firmware changes, original/ changes, ROM search,
installation or Plaits implementation occurred.

## A. Boundaries and original control flow

VERIFIED immutable Selection0/channel0 bytes and existing decoder listing:

- Helper P:[1F5C,1F9B), final RTS1F9A. Previous RTS1F5B belongs to the
  preceding coefficient routine; next1F9B is a separate initialization entry.
- Direct callers1E80 and1EE5 are two-word JSR1F5C, continuations1E82/1EE7.
  These caller instructions execute, so no fabricated helper-return address
  is supplied in a snapshot.
- Callee P:[C9D,CB8), final RTSCB7. Calls are original short JSRs1F78/1F7F.
  There is no REP or conditional control-flow branch in the qualified helper
  plus callee path. MAXM and arithmetic affect data, not PC.

| Original DO | Body / raw last-word LA | Count | Executions/helper |
|---|---|---:|---:|
|1F6C|1F6E..1F6F /1F6F|X3A32|1|
|1F72|1F74..1F98 /1F98|immediate16|1|
|CA4|CA6..CAF /CAF|X3B16|32, inside C9D calls|
|1F85|1F87 /1F87|X3A32|16|
|1F90|1F92..1F97 /1F97|X3A32|16|

The assembler listing names the continuation after the raw loop endpoint.
Native interpreter executes all these DO instructions and its original loop
control; no manual expansion or PC reassignment occurs within a run.

## B. Live-ins and provenance

The snapshot schema is `ct-fullhelper-v1` in checkpoints.json. Each numerical
class binding is distinguished from a recovered stock value.

| Live state | Provenance / treatment |
|---|---|
| Entry PC | Original caller1E80 or1EE5; helper entered through actual JSR |
| X1D40/41/42 |1800/1840/18E0 from1E76/7A/7E, or19F0/1A30/1AD0 from1ED9/DD/E1 |
| X3A / X3B | Previously established stock32/16 count relations;140-related publication at148/149 |
| Cursor words | Y1820..182F alternating2CCC/2CEC; Y1A10..1A1F alternating2C02/2C24, initializer260A..261F |
| M0..6 |FFFF initializer2779..2780, conditioned on retention |
| M7 |FFFF or reviewed temporary3FF; both tested |
| SP/SC |SYMBOLIC finite healthy resident class SP=SC=d, d3..7 **before caller**; actual stock depth not recovered |
| LF/FV |SYMBOLIC inactive-loop class LF0/FV0; not asserted normal firmware invariant |
| LA/LC |Arbitrary SYMBOLIC incoming values; saved/restored, not used to select flow with LF0 |
| Hardware prefix0..d |Opaque SYMBOLIC48-bit cells, never read/popped by helper or caller return |
| SR13 |Candidate DSP56724/25 reserved compatibility bit0; conditional device profile |
| Other SR arithmetic bits |SYMBOLIC data modes; CA2 sets S1 via ORI08,MR; CB6 clears it via ANDIF7,MR |
| OMR memory bits |Retained shim-derived mask600080/value400080, conditional mapping relation |
| OMR.SEN / EP / SZ / XYS |SEN0/1 backing checked; no extension threshold reached, EP/SZ/XYS unconsumed |
| R0..7 at caller |SYMBOLIC until dominated local definition: R6/5/4 at5C/5E/60; R1/3 at68/6A; R0 at70; R2 at7E; R7 at89 |
| N0..7 |N1/N3=2 at62/63, N4=-3 at64, N5=-4 at66; others unconsumed SYMBOLIC |
| A/B/X/Y arithmetic registers |Defined before required uses; unknown coefficient/sample results stay SYMBOLIC |

Required Y coefficient/state/scalar words and X1D43..1D52 ramp data remain
unconstrained numerical data. No convenient zero coefficient/state snapshot
was invented. Every data-dependent output is null/SYMBOLIC_DATA, even where
a chosen transport backing happens to produce zero. Initial buffer-clear
stores are concrete0 from original CLR at1F66.

The finite stack/loop class is a **structural local precondition**, justified
by documented stack geometry and the verified push/pop budget. It is not a
claim that the stock device reaches any selected depth or inactive LF value.
Depths outside3..7, inconsistent/extended-history states and active inherited
loops with unqualified LA/LC are not admitted. They remain untested/unresolved
classes, rather than being declared impossible in normal firmware.

## C. Stack qualification

References: locally reused DSP56300FM Rev.5 sections5.4.2/5.4.3 and A.2.5
(PDF96..100,435..436). Hardware uses one shared48-bit stack for calls, loops
and long interrupts; these are logical frame roles, not three separate RAMs.

Original caller JSR adds1 frame. Outer DO adds2. C9D JSR adds1. C9D DO adds2.
Therefore maximum occupancy is d+6. Inner helper DO instead adds2 above the
outer frame, giving d+5. DO exits remove their2 frames; each RTS removes1.

The admitted pre-caller d3..7 class keeps occupancy in[3,13]. The documented
extension thresholds (empty atSC2, full atSC14) are never encountered during
executed pushes/pops. This makes unknown SEN, EP, SZ and XYS irrelevant in this
class. The sealed core does not certify general stack extension; none is needed
here. Prefix slots0..d stay opaque and unchanged. No native constructor/reset
stack value is promoted into firmware evidence.

Caller return frames and loop restart/saved frames are generated by original
JSR/DO instructions. Pre/post SP transitions, actual return PCs, LA/LC/flags,
peak occupancy and prefix preservation are checked. The last RTS naturally
reaches1E82/1EE7, where replay stops before the caller's next instruction.

INTERRUPT STACK: no events are injected in this isolated experiment. Existing
prefix frames could have unknown origins but are not consumed. IRQ/host/worker
interference is excluded by test scope, not proved absent in stock. Full ROM
entry IRQ/VBA/pipeline provenance remains unresolved independently.

## D–G. Joined execution and differential validation

**TESTED:**40 runs per invocation:2 families ×2 M7 alternatives ×5 finite
stack-depth completions ×2 backing checks. Each run executes9647 original
opcodes (9646 in helper/callee plus1 caller JSR). Total385880 per invocation.
The repeat covers the same states again, not additional distinct state coverage.

The original outer DO yields16 contexts. R6 advances once/context; cursor
source cells progress sequentially across16 alternating initialized words.
Each original inner DO yields32 writes at1F97: **512 accumulation stores**.
The initial original DO yields64 zero stores, alternating between two buffers.
Both C9D calls execute per context, giving32 callee calls/RTS pairs.

LC observations are checked as exact descending sequences: outer16..1;
accumulation32..1 repeated16 times; maximum loop32..1 repeated16 times;
callee16..1 repeated32 times; initial clear32..1 for both stores.
There are66 DO executions and33 call/return pairs including the caller.

Every helper executes **1728 X stores and160 Y stores**. The X total includes
512 cursor accumulations,64 clear stores and1152 callee scratch stores. Y stores
include128 callee state stores and32 outer scalar/ramp stores. Every actual
X/Y read/write passes the authoritative sealed19A memory bus callbacks.

Cursor accumulation ordering matches prior checkpoint ranges exactly, for
each j and modifier, using builds/phase19c-checkpoint/final/cursor-ranges.json:

| Family / parity | Exact X interval |
|---|---|
| A even |[2CCC,2CEC)|
| A odd |[2CEC,2D0C)|
| B even |[2C02,2C22)|
| B odd |[2C24,2C44)|

The two-word B gap is retained. All32 cursor words remain unchanged after the
complete helper. Stored cursor values do not advance by32 across invocations;
only the transient R7 advances. No numerical DSP semantic name is inferred.

Final known addresses: R0=1D53, R2=2CA9, R3=2CAA; R4=1960/1B50;
R5=18E0/1AD0; R6=1810/1A00; R7=2D0C/2C44. N5 remains-4.
Incoming LA/LC identities, resident depth and opaque prefix are preserved;
LF/FV return to0. RTS preserves no complete SR word, and callee S1 is cleared;
unresolved numerical flags/registers are not exported as stock values.

Multiple backing representations change arithmetic, unread prefix and incoming
LA/LC contents, and toggle SEN. Address/control projections must remain
identical. This is a metamorphic test plus audited data-only dependency proof,
not exhaustive numeric-state or all-SR enumeration. Symbolic values are refused
if used as a pointer/count/control input. Only original helper/callee/caller
PCs are admitted; peripheral access and unexpected exits refuse.

## H–L. Watches, integration and scope

**PROVEN FOR CHECKPOINT DOMAIN:** no read or write at X35F, in X[340,360),
or in X[5F00,6000). All complete-helper X stores remain below high-X.
The largest observed X access is2D0B for A and2CA9 for B. Zero watched events
are exported separately; full traces retain all X/Y traffic.

This proves local non-interference with the count word for the admitted class,
not that its incoming value was zero. No35F snapshot is seeded here. The helper
does not publish a count or record destination for203A. Its final R0=1D53 and
N5=-4 do not directly satisfy203A's preparation. No natural1F5C→203A execution
chain is established; those routines are not artificially joined. Positive
count publication/table walking stays UNRESOLVED; prior204B calibration remains
validation only.

New BOUNDED-PROOF: real nested DO/JSR/RTS preserves the qualified resident stack
and initialized cursor cells while reproducing the formerly isolated body
address ordering. Remaining universal obligations: actual normal parent entry,
actual caller stack/inherited-loop class, foreign count/cursor/base/modifier
mutations, IRQ/mailbox/worker interference, other high-X aliases and persistence
through every normal transition. No cursor family is removed from the universal
blocker set solely on these conditioned runs.

## M–O. Design gates and next step

| Gate | Result |
|---|---|
| A complete helper defensibly executable? |YES for the explicitly bounded structural class; actual normal class UNRESOLVED |
| B original DO gives32 cursor iterations? |YES per context,16 contexts, plus real callee/clear loops |
| C CALL/RTS/stack validate? |YES in the admitted resident class |
| D complete-helper writes below high-X? |YES in that class |
| E writes35F? |NO in that class |
| F persistent-memory argument stronger? |YES locally; no universal ownership closure |
| G sufficiently supported theoretical persistent Plaits layout? |NO verified persistent layout; only a conditional hypothetical sketch with explicit unproved reservation |
| H firmware implementation ready? |NO |

Single best next step: recover the actual caller stack/inherited-loop class and
normal reachability of1E80/1EE5, connecting the tested structural relation to
a specific normal path. Avoid another broad alias census or automatically
joining203A, boot replay, hardware work or Plaits integration.

## Reproduction and files

Implementation: emulator/harness/fullhelper/{replay.cpp,CMakeLists.txt,
build.ps1,collect.py}; tests: emulator/tests/verify_fullhelper.py. Existing
MSVC/CMake and sealed19A libraries reused; no installs/source-core changes.

```powershell
./emulator/harness/fullhelper/build.ps1 -BuildDir builds/phase19c-fullhelper/new-build
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B emulator/harness/fullhelper/collect.py --exe builds/phase19c-fullhelper/new-build/ct_fullhelper.exe --output-dir builds/phase19c-fullhelper/new-audit
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B emulator/harness/fullhelper/collect.py --exe builds/phase19c-fullhelper/new-build/ct_fullhelper.exe --output-dir builds/phase19c-fullhelper/new-repeat
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B emulator/tests/verify_fullhelper.py --exe builds/phase19c-fullhelper/new-build/ct_fullhelper.exe --first builds/phase19c-fullhelper/new-audit --repeat builds/phase19c-fullhelper/new-repeat --output-dir builds/phase19c-fullhelper/new-checks
```

Canonical exports final/ and final-repeat/ contain partial snapshots, original
instruction witnesses, full traces, watched events, final CPU/X/Y symbolic
states, per-run reports, result and source/input hashes. Earlier probe/first/
are intermediate. Checks/reproducibility.json records byte-identical evidence,
7 refusal gates, original/extraction hashes, sealed203-file core/19A harness
guard and validated19A fixture-binary identity. No original binary was patched.
