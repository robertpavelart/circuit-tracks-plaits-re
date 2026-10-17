> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 20B-SEAM — local stock ABI obligations

## Phase 20B2-CHECKPOINT — PARTIAL provenance, replay REFUSED (2026-10-07)

**VERIFIED source / CALCULATED conditional:** existing authored Rudi saw poly
patch supplies routing0, nonlinear1, filtertype1. Original descriptors/getter,
reverse-index initializer (IDs1E/20/21 ->FF), bank sinks and DSP cursor chain
resolve expected X5AB=0,X5AC=1,X5B1=5,X5B2=5 for this bounded offline binding.
Both coefficient sequences are intendedY:F64..F68 under qualified pointer modes/
linearM5; originalC2D generates them beforeC9D, not immutable LUT constants.
Explicit ARM X2AB=0 removesY94 from the selectedX5B0 expression.

**PARTIAL / REFUSED:** no natural numeric checkpoint or original32-word generator
block. X5AD/5AE/5AF andX5B0 still require P657-producedY8F/Y90/Y91 modulation/
control values; retainedY5AB..5AE/5B7/5B8 are outside selected trigger reset ranges.
MaterialSR/AGU/stack/loop context and naturalguard remainUNRESOLVED.0 stock
instructions/CPU, no costs or fake traces. Full authentic boot was not required
or expanded; no preset/neutral histories or reset-depth frame guessed.

The Phase20B selector/offset source gaps are narrowed for this exact file,
while its numeric replay refusal remains valid. Plaits-fed replay/Phase20B
execution resumptionNO until stock-only qualification. No hardware, patching,
Plaits feeding or new RAM-safety analysis. Single next step:qualify P657 input
record for this exact patch plus one source-backed note/slot/history and bounded
CPU context. Reports:stock-seam-checkpoint.md,stock-coefficient-provenance.md,
stock-runtime-state.md. Canonical:builds/phase20b-checkpoint/final/.

2026-10-07. **VERIFIED static map; UNRESOLVED executable integration ABI.**
The replay admission gate is closed. See plaits-stock-seam.md and canonical
builds/phase20b-seam/final/{seam-liveins,seam-clobbers,numeric-adapter,guard-word}.json.

Entry9D9 restoresR0 fromY7 then waits three NOPs.9DD is first selector read;
the generator's last mono store is9D8. Proposed stopA95 excludes scheduler/
timing/peripheral work. Selected slot0 requires R4=Y5AB, Y7=5AB coefficient
cursor. At original9DD entry R0 would additionally have to be restored explicitly.
Incoming A is redefined and comparison flags overwritten, but SR arithmetic,
sticky flags and inherited loop/stack state are not all dead.

## Sample storage versus audio calibration

**VERIFIED:** X[2C46,2C66) contains32 two's-complement24-bit mono words.
Representable domain is [-8388608,8388607]. It is not interleaved stereo or the
earlier three-laneY layout. DSP signed fractional multiplication gives arithmetic
meaning to word/2^23; this does **not** establish a unity/full-scale stock audio
convention or an operational Q1.23 adapter. Generation includes full accumulator
transfers, limiting/scaling; the active SR modes must be qualified.

There is no proved DC removal or normalization at this seam. Depending on the
nonlinear selector, raw samples encounter normalization/table lookups, polynomial/
piecewise or recursive operations beforeBDD scaling. First sample multiplication
is therefore mode-dependent, not alwaysBE3. BE3/BE7 use X5AE as multiplicative
scale. C3E..C87 build coefficients from state/parameter-derived indexes into the
ARM-uploaded X1600..193F banks. C9D uses MACR feedback and persistedY history
while settingSR scalingbit11 atCA2 and clearing it atCB6. A8D..A94 updates
nonnegative gain and accumulates using old gain with ASR4/MAC/ASL4.

**UNRESOLVED:** full-scale audio unit, stable input interval for arbitrary stock
coefficients/state, DC tolerance, normalized amplitude, clipping rate/headroom.
Representability alone cannot establish feedback stability or safe +4-bit mix.
Stock coefficient tables are available in part, but all consumed dynamic state,
normalization table contents/domains and selected sequence offsets are not a
qualified numeric preset snapshot. No guessed safe amplitude was supplied.

The32 words can be read by more than one stage (e.g. subtract/preprocess then
post/gain). Exactly32 samples are emitted by the reviewed gain loop. Prefetch
can read a33rd word. Do not assert that every original raw word is globally
consumed exactly once across all modes or that final DAC output starts here.

## Guard history

Selected AA8-normalization-active path preloadsX2C66 atB1A iteration31; no next
output iteration consumes it. With normalization skipped, BE6 iteration31 reads
it intoX0, andBE7 actually multiplies it while storing the previousA. NewA is
not a33rd output, but MPY affects S/L/E/U/N/Z/V. C9F overwritesX2C66 with
retained filter history before recursive processing. A93 reads that later word
intoY0 on the final gain iteration. Bypass modes can leave the entry guard asY0
liveout. All-mode/caller/status closure is missing. No universal guard policy
is selected; preserve/zero/duplicate/arbitrary are untested stock policies.

## Live-in and clobber obligations

R4 andY7 are selected entry pointers; the M registers used by indirect addressing,
SR scaling/SM/SA/DM/RM and stack/loop environment must be preserved/qualified.
M initializedFFFF is known startup evidence, not an automatically retained seam
value. AA8 may changeM5 and restore it fromY1A. Stock and standalone memory-mode
assumptions must not be silently equated.

For the selected nonlinear branch the slotY state spans5AB..5B8, with two4-word
recursive history sets starting5AF and5B3. X5BC/5BD are final gain delta/current;
gain current is updated once/sample, and the parallel MAC uses the old value.
Other selectors change footprints/control. No observed concrete clobber set or
all-mode permission to overwrite caller registers exists.

The standalone renderer uses A/B,X0/X1/Y0/Y1,R0..7,N0..7, changesCCR and uses
resident DO/JSR stack entries. Its instruction code does not writeM/OMR; the
standalone wrapper supplies their private environment. Required restore at least
includes selectedR4 and the stock mode/modifier/loop contract;9D9 rematerializes
R0 fromY7. Exact register liveness/save words/cycles remain unknown. Saving a
nominal full register file does not by itself qualify inherited loop/stack state.

## Adapter and placement contract

Host-only stateless adapt32 is tested for explicit shift/rounding/symmetric
clipping, with no stock-facing defaults. A calibrated stock scale/clip/guard
binding is refused. Thus DSP adapter/call overhead is not measured or assigned0.

Plaits state7 words, controls3, scratch3+16 work registers, output32, LUT0 remain
verified standalone requirements. Integrated preservation/glue/adapter scratch
and pitch conversion are unresolved. None of these may be placed at current
literal standaloneX/Y addresses in stock: they overlap global state. Nor may
X2C46 shared scratch or Y59F's full40-word context be reclaimed persistently.
No stock RAM address or P placement is selected.442P is the unchanged renderer,
not an exact total integrated module size; its terminalJMP is a harness boundary,
not a valid direct-JSR return. A return/remapping/preservation design needs a
separate qualification. Firmware-patch design/hardware gates remain closed.
