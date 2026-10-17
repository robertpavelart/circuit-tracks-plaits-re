> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20C — fixed one-path state and temporal storage

## Current Phase20C6 state comparison — 2026-10-07

**SELECT-A conditional; actual owned Circuit words0.** Prefer explicit P7
[3FF0,3FF7) and one-way epoch, retaining the Phase20C5 workspace/control design
and unresolved ownership gates. B examines84 selected generator-associated
words; none satisfies complete producer/consumer/external-writer isolation.
Six conditional third-lane record candidates are not a seven-word certificate.

Selected map552 covers descriptor8, X context74, Y control96, Y sample40,
kernel/base/reset and identified shared dependencies. Unknown field meanings
and dynamic extents remain unknown. Coefficient stores at kernel+90hex and
template sources+120hex are included; nominal12 stride does not bound them.
Mailbox/timestamp/post/envelope/ramp objects are not surrendered. No new free
memory search, allocation or Plaits math change. B reset/sentinel is not an
owned once-only initializer, and arbitrary service writes destroy continuity.

26 raw saved words at the natural9D9 boundary remain the comparable bound;
the exact minimal all-mode set is unresolved. See current architecture-selection
and takeover-feasibility notes, with immutable original/renderer guards intact.

## Current Phase20C5 software ownership - 2026-10-07

**PARTIAL design; no allocation.** Proposed P7:[3FF0,3FF7) uses the existing seed
[0,0,200000,0,A3D7,200000,0] after trusted startup and complete DMA quiescence.
A one-way bank0/slot0 gateway retains ownership, including idle, until reload/
reset. There is no eighth numeric or activation flag; gateway domination and
control-flow exclusion remain unproved. Separate P1 fault metadata at3FE0 is
explicitly counted.

Proposed P objects: policy[3F60,3F7E), typed shadow[3F80,3FA0), renderer save
[3FC0,3FDA), spills[3FDA,3FDD), controls[3FDD,3FE0), status[3FE0,3FE1), numeric
state[3FF0,3FF7). Total102P. Every object needs enforcement. The policy frame is
separate and serialized with R0 read-only; the shadow protocol is provisional.
M-register spill elimination would expand the save set26 to29 and reopen AGU/IRQ
proofs. X scratch borrowing remains unqualified. Hardware-stack-only saving
exhausts16 entries before caller/IRQ frames; keep the26-word preservation set.

Alternative deliberate X:[57B,582) takeover must suppress selected387/77F
writers AND readers in both passes and replace request/result/auxiliary/guard
contracts. It is not selected. Appended P preserves those original objects.
Natural ownership REFUSED and numerical P-state PASS remain unchanged. Current
notes/exports: plaits-enforced-state.md, plaits-selected-path-takeover.md and
phase20c-enforcedstate/final-v3. Earlier allocation discussion below is historical.

## Phase20C4 exact P-region ownership — 2026-10-07

**REFUSED; no stock state reserved.** Candidate P:[0x3FF0,0x3FF7) is a
conditional layout object above known appended code, with explicit pre/post
guards and load-epoch reset requirements. Current stock upload does not seed
it. A future complete0x3FF9-word object would load all seven literals on every
reload; diagnostics end the epoch. No extra flag is needed only after that
epoch is enforced. Normal DMA/register, computed execution, ROM/mode/cache and
complete object ownership remain unproved. Temporary X workspace remains
unqualified; previous standalone P-state arithmetic/continuity pass is retained.
See `plaits-p-region-ownership.md`; `builds/phase20c-pregion/final-v1/`.

## Current seven-word P-state result — 2026-10-07

**TESTED standalone contract PASS; Circuit ownership REFUSED.** Exactly seven
P data cells2D29..2D2F initializefrom21validatedBE24bytes once percase; exact
phase,next,previous_pw,high,frequency,pw,shape persist across2048blocks. No eighth
flag or persistentX. All43 cases match samples andsevenwords aftereveryblock.
This is a synthetic ownedobject, NOT a Circuit allocation. Currentstock upload
ends2A5E anddoesnotseedthese cells. Actualmode/allDMA/indirect/ROM/cache/loader
ownership remainsUNRESOLVED; previous32-word temporaryworkspace also unproved.
Seeplaits-p-state-qualification.md; reportbuilds/phase20c-pstate/final-v4/.
Historical declarations below about no renderer qualification apply to20C2.

## Current Phase20C2 ownership decision — 2026-10-07

**REFUSED. Qualified seven-word X set: NONE. Temporary workspace: NOT PROVEN.**
This is a bounded candidate result, not an all-X impossibility theorem.
Inherited slot0 tail is now accounted for:5BF..5C1 written73B/read374;5C2
timestamp written2DD/read1BDB;5C3 cleared by conditional ARM21A5E start path.
Five cells cannot supply seven;5C4/5C5 belong to slot1. This supersedes the
earlier UNKNOWN tail description below.

Scratch[2CCC,2CEC) is rewritten by retained lookup completion; the second half
[2CEC,2D0C) has service writes and unclosed effect/foreign domains. Every watched
private X cell is addressable by Selection0 service5E write, with no reservation
filter. Targeted scalar-ledger nonhits are not global preservation; a known start
reset was absent from that ledger and supplemented with byte evidence.

No state assigned. Fixed high/split access would retain549P template addressing
cost, but there is no qualified candidate. Exactly two fallback designs and exact
seven-field/init semantics:plaits-fixed-state-ownership.md,
plaits-state-initialization.md. Seven mutable P data words are structurally
possible only conditionally, do not satisfy the X gate, and incur MOVEM costs.
No firmware/renderer changes, snapshot work, allocation or positive lifetime
fixture. Current next step: scoped P-object/MOVEM qualification rather than
another broad X search. Evidence:builds/phase20c-fixedstate/final-v1/.

2026-10-07. **UNRESOLVED persistent placement.** No stock RAM reserved and no word
declared SAFE. Fixed-address one-voice state is evaluated before a relocatable
per-voice ABI. It removes pointer/index machinery but does not create free memory.

Canonical `state-lifetime.csv` lists individual words for the selected slot,
output/side streams, sample state and candidate work areas. The complementary
generator-memory-operands.csv includes every decoded X/Y operand in the scoped
preparation/generation region. Dynamic count/base/modifier entries remain explicit
unknowns; this is not an exhaustive global points-to proof. Local labels below
never imply exclusive lifetime or global ownership.

## D–E. Exact demand, placement not invented

Unchanged REGOPT needs seven persistent X words: phase, next BLEP state,
previous_pw, high flag, frequency, pw and shape. Three control words and three
spill words are also required, with16 working registers. Existing mono32 is the
output; no additional32-word buffer is needed. Conservative26-word raw register
save area brings temporary demand to **32 words** and total data demand to
**39 words**: seven retained plus32 temporary.

**Exact persistent base: UNRESOLVED/null.** No fabricated fixed block or per-voice
address. The standalone X20..26, X30..32 and X0..2 literals are unqualified stock
globals/protocol/control space. Keeping short addresses for speed is not permission
to overwrite them. X5F00..6000 is not selected or promoted.

**CONDITIONAL temporal candidate, not allocated:** X[2CCC,2CEC),32 words, after
the retained combiner and before9D9. Proposed partition only if ownership closes:
controls[2CCC,2CCF), spills[2CCF,2CD2), raw saves[2CD2,2CEC). This fits exactly.
It is global per-invocation workspace, not persistent per-voice state. It avoids
clobbering the still-live auxiliary buffers or guard.

Reasons it is only conditional: selected lookup completion writes/reads absolute
phase weights via822/82D or87D/88B; those local reads are complete before9B9.
Other stock users include1EFA/1F97 effect work and260C startup. Their later
reader-before-write relationships and all relevant async/host/DMA domains have
not been proved for temporary substitution. Not being read by selected post code
alone does not prove a safe lifetime. It cannot hold retained Plaits state across
blocks because original generator/effect paths overwrite it.

## Generator versus post words

|Candidate|Classification and lifetime|Decision|
|---|---|---|
|XQ first42, slot0[57B,5A5)|GENERATOR-PRIVATE local consumers;387 prepares every block,77F consumes/updates|Reject persistent storage while these paths remain|
|XQ six current ramp words[5A5,5AB)|GENERATOR-PRIVATE current/ramp history; next preparation reads it and9B7 commits|Not surrendered by retaining the combiner|
|X post[5AB,5BF)|POST-PROCESSING-LIVE selectors, targets, histories/gain inputs|Leave untouched|
|X[1960,196C) nominal kernel stride|GENERATOR-PRIVATE local path;387 dynamic kernel producer and lane consumers|Reject persistent reuse; stride12 not free12|
|Y[59F,5A5)|GENERATOR-PRIVATE masks/phases;387/reset and request/completion accesses|Keep all original state; not spare phase words|
|Y[5A5,5AB)|GENERATOR-PRIVATE six ramp deltas|Needed by original coefficient ramps|
|Y[5AB,5C7)|POST-PROCESSING-LIVE retained sample/filter state|Leave untouched; complete mode-dependent ownership still conditioned|
|X event-tail5BF..5C3|SHARED/UNKNOWN allocator/time/event fields|No seven-word allocation established|
|X2C02/2C24 side streams|POST-PROCESSING-LIVE for some modes|Preserve original combiner values|
|X2C46..2C65|SHARED output scratch, exact32-word invocation contract|Direct audio overwrite only|
|X2C66|POST-PROCESSING-LIVE guard/filter neighbor|Preserve natural value|
|YA01..A60|SHARED three-lane scratch, overwritten each completion|Not persistent storage|

These rejections are stronger than absence-of-post-read reasoning: existing
producers and next-invocation consumers remain in the chosen design. A different
architecture that bypasses producer/lane work might release some words, but would
reopen request, phase, queue, auxiliary and guard obligations. It is not the same
minimal mono-overwrite design and is not silently selected.

## Fixed addressing versus per-voice relocation

Preferred conditional ABI: one fixed retained seven-word block, one fixed temporary
block, no new allocator and no dynamic per-slot base registers. All81 absolute X
sites can map directly to those owned addresses if later proved. Since plausible
stock-context addresses exceed the short range, the template uses long absolute
forms and retains all16 allocated scratch registers. Indirect base addressing
would consume a register or require a new allocation/spill analysis; not implemented.
Y storage would require changed memory-space accesses and its own proof; it does
not free the existing Y sample context by relabeling it.

Initialization must also be owned. Valid retained frequency is positive, so a
zero frequency sentinel could indicate not-yet-initialized state **only after**
the block's startup/reset lifetime is proven. Then explicitly initialize all seven
words once; do not reset them each render. Continuous phase across slot reuse is
a possible first policy; note-retrigger/idle behavior is not yet specified or
proved. Do not use missing lifecycle knowledge as a default reset.

Alternatives ranked: prove one fixed retained block; prove a selected generator
context can be released by a different producer/bypass design; evaluate a changed
memory-space ABI; larger persistent allocation remains last and unproved. None
is admitted merely from small demand or unused-looking addresses.

**Next required proof:** a particular fixed seven-word domain, all normal writers/
readers, reset and async behavior across blocks. No safe persistent words were
identified under the current retained-stock-prefix design. Executable prototype
and patch construction remain refused.
