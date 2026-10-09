# Phase 5 — selected voice output contract

## Phase 20B-SEAM — replay admission refused (2026-10-07)

**VERIFIED:** fresh original-byte map selects9D9 (R0 reload +3NOPs), with9DD
as first post dispatcher andA95 as local group-output accounting boundary.
X2C66 entry prefetch can feed an executedMPY/CCR update; it is later overwritten
byC9F filter history onBDD paths. No universal zero/duplicate/arbitrary policy.

**TESTED REFUSAL:** unknown X5AB/5AC selectors, X5B1/5B2 coefficient addresses,
numeric/state/table/SR/AGU/stack/guard provenance prevent the requested checkpoint.
0 stock instructions,0 joined blocks, no CPU, no actual stock/Plaits-fed traces.
The request explicitly says to STOP for unresolved control/address/scaling/loop
fields. Static mode0 witnesses and boot-clear zeros were not promoted to presets.

Signed24 mono storage is verified; stable amplitude/audio unit and operative
adapter binding remainUNRESOLVED. Host-only explicit numeric adapter fixtures
pass; no stock scale/guard default or DSP adapter cost is assigned. Raw generator
upper13379 is retained; layerB/C costs and full1/2/4/10-voice budgets are null.
Ten leaves30050 only before all missing work. Exact integrated register spills,
code/state totals and pitch/knob conversion remainUNRESOLVED. Persistent RAM
safety/patch-design readiness/hardware flashing remainNO. No code/firmware/hardware
or model/polyphony integration changes.

Single next step:provenance-backed original coefficient/state preparation
checkpoint upstream of9D9; qualify stock-only post replay before Plaits feeding.
Reports:plaits-stock-seam.md,plaits-stock-abi.md,plaits-stock-workload.md.
Canonical:builds/phase20b-seam/final/; unexecuted trace dirs contain refusal.json.


**Phase 6C update:** X:2C66 must remain readable and participates in
neighboring filter scratch. A universally arbitrary value or duplicate-last-
sample rule is not proved; retain stock neighboring behavior until all consumers
and status effects are closed. Boot clear no longer disqualifies persistent
RAM after init. Reading Plaits solely for conditional resource comparison may
begin; safe allocation, complete producer ABI and fit are still unresolved.

**Phase 6 revision:** selected loop subtotal corrected to 4,355; clock/rate
divider chain and shared scratch ownership audited in
[dsp-resource-audit.md](dsp-resource-audit.md). Earlier saved Phase 5 reports
with 3,635 are superseded, retained for provenance. The seam's complete
replacement ABI and safe state allocation remain **UNRESOLVED**.

**Phase 6B safety refinement:** output is still 32 words, but selected scaling
and gain loops prefetch a 33rd word, X:2C66 (BE2/BE6, A89/A93). Keep that
address readable; its final prefetched value is unused in the selected output.
Incoming r0/r4 and AGU/status/caller-loop context remain obligations; incoming
A and immediate branch condition codes are redefined by 9DD/9DE. No blanket
all-mode register-clobber permission is established. See
[dsp-memory-ownership.md](dsp-memory-ownership.md) and the exported clobber table.

2026-10-05. STATIC ANALYSIS ONLY. No device access, firmware execution,
transmission, binary patch, original/ modification or Plaits implementation.
Addresses in P/X/Y are hexadecimal 24-bit word addresses; ARM addresses are
bytes. Unprefixed address/stride formulas use hex; the 14-word record offsets
in section C/D and sample counts are decimal.
VERIFIED means supported by instructions/architecture documentation, not a
measured runtime observation. Symbols such as Q and N below are analyst labels.

## Scope and reproducibility

Selected context: slot 0, bank 0. Generalized slot formulas are included below.
Selected path witness: three lookup-mask lanes, mask 0x1FFF (wave-info index 1),
one inner repeat per lane, prepared Q+3 nonzero, Q+4=0, post mode=0, and a
nonzero normalization branch in P:0xAA8. N=32 follows initialization.
These are explicit path constraints, **not a recovered runtime preset**.
Wave-info bytes are available in the firmware; current host-provided parameter,
table and persistent-state values are not a runtime memory snapshot.

**VERIFIED:** live memory/register interfaces, gain aliases and block loop
counts below. **UNRESOLVED:** every numeric word of a concrete running voice,
arbitrary branch combinations and absolute output normalization. A complete
numeric generation cycle cannot honestly be reconstructed from this image alone.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_voice_contract.py --output-dir builds/phase5-new
```

Use a fresh directory. The tool verifies input hashes, codec equality,
disassembly bytes, both coefficient-emission alternatives, subroutine pointer
advances, static loop counts and exact table exports. It is address accounting,
not an instruction emulator. Canonical output: `builds/phase5-contract/`.
DSP excerpts contain 2,276 byte-checked instruction rows. ARM reports are
listed and byte-checked in contract.json. Decoder/source provenance is in PHASE3.md.

## A. Selected slot memory and required state

| Region / register | Slot 0 | Slot i / evidence |
|---|---|---|
| Descriptor D, 8 words | X:EB..F2 | X:EB+8*i; initialization P:2881, call P:19AC |
| Bank field | X:F2=0 | D+7; ARM 08021A08 explicitly publishes bank |
| Control V | Y:11F | Y:11F+60*i; processed flags V+3=Y:122 |
| Secondary Y pointer | Y:131 | Y:131+60*i |
| Note-follow state | Y:12F | V+10; target Y:159, step Y:15A, smooth Y:15B, seed Y:15C |
| Primary envelope | Y:130 | V+11; target Y:14D |
| Event E | X:57A | X:57A+4A*i, consumed/cleared P:29D/29E |
| Prepared coefficients Q | X:57B..5BE | E+1; 68 words before E+45 scratch area |
| Sample-state S | Y:59F | Y:59F+28*i; 40-word context stride |
| Three mask/mode words | Y:59F,5A1,5A3 | S+0,2,4; not themselves phase values |
| Three persistent phase words | Y:5A0,5A2,5A4 | S+1,3,5 on the selected lookup path |
| Post-processing Y state | starts Y:5AB | S+0xC at P:9DD; inside the same 40-word context |
| Kernel coefficient scratch | X:1960 | X:1960+C*i; prepared by P:387; template around X:1A80 |
| Bank parameters | X:296 | X:296+172*b; coefficient preparation uses subsequent words |
| Bank intermediates | Y:7C | Y:7C+2A*b; temporary parameter values rebuilt per context |
| Three-lane scratch | Y:A01..A60 | N*3=96 words, interleaved, shared/reused between voices |
| Phase/index/raw sample scratch | X:2C46..2C85 | 2*N phase/index words; first N words later hold mono output |
| Other scratch | X:2CCC,2C02,2C24,2D2C,2D2E,2D4E,2D50,2C68,2DB0; Y:F68/F6D/F77 | Shared work areas; guard/neighbor words also used by filters |
| Lookup queue | X:30002 onward | producer X:2F31, consumer X:2F32, auxiliary X:2F34; shared with worker |
| Pass bitmap | X:2F30 | bit23 pass marker, low bits pending context work |
| Bank/context scratch | X:CC=0, X:2C=0 | bank and current context index for slot 0 |
| Group sum | X:2DF0..2E0F | bank0; bank1 X:2E50..2E6F; N=32 words |

**VERIFIED correction/precision:** P:79D reads Y:(r4)+ mask/mode, so phase
loads/stores at P:7E4/7F9 use the following word, S+1. The descriptor's S
pointer is the context base, not the first phase word. P:99A/99C advances
to the next mask/phase pair.

Required shared constants include block-count words X:39..41, Y:10..1C,
lookup tables and the no-scaling status on the output boundary. Modulo registers
are initialized to FFFF; selected filters temporarily change them and restore
them from Y:1A. Any theoretical replacement must respect shared scratch and
the sequential descriptor scheduler, not reserve these areas permanently.

## B. Why both P:77F passes exist

**VERIFIED entry:** r3 points to D+7; r0=Q; r4=S. P:77F copies bank to
X:CC. First entry comes from P:384 after preparation. Second entry comes
from P:19E6, which reloads D+4, advances it by one to Q and reloads D+5=S.

| Behavior | Lookup request pass | Lookup completion pass |
|---|---|---|
| Condition | X:2F30 bit23 set by P:1998/1999 | bit23 cleared at P:19BF; pending bitmap bit selects context |
| Scratch clearing | no Y:A01 clear at entry | P:789..78D clears 3*N Y words |
| Pending status | P:791..799 ORs current context bit into bitmap | scheduler consumes bitmap with shifts/tests |
| Common loads | mode/mask Y:(r4)+, Q record, persistent phase, N counters | same addresses, plus fetched lookup values |
| Selected arithmetic | P:7EF..7F2 builds phase tracks, P:806..815 converts to masked lookup addresses | recomputes tracks, P:826..82A builds absolute weights, P:832..84B combines fetched values |
| Selected phase commit | P:7F7 skips P:7F9 | P:7F9 writes S+1; once per selected generation cycle |
| Lookup destination | shared X queue through r1=X:2F31; publish X:30000 | wait P:775 then read returned values through Y:(r5)+, r5=X:2F32 pointer |
| Samples | address work; first return at P:9A4 | additive samples in Y:A01+lane+3*k |
| Post-processing | skipped at P:99E..9A4 | P:9A5 onward |

**VERIFIED:** worker P:120 loads each requested address, P:125 reads X:(r0),
P:126 replaces the shared queue word with fetched data. The consumer explicitly
reads via Y:(r5)+. Preserve this X-producer/Y-consumer shared-memory convention;
it is not safe to assume all X and Y addresses are interchangeable.
P:775 waits for the ICC-published completion pointer; different paths require
N, 2*N or other queue counts.

The outer DO #3 at P:79B establishes three interleaved numerical lanes. Masks
>=8 lead to lookup generation. Small mode values use a different path; Q+3=0
and Q+4 flags select other arithmetic/lookup schemes at P:8A4,8FA,936,95B.
The inner repeat count is Q+2, not automatically three voices or three synths.
Some alternate paths commit phase during the request pass (e.g. P:8D2/913).
Do not generalize the selected pass's phase-commit rule to every branch.

**HYPOTHESIS:** the lanes are oscillator/periodic-source branches. The
interleaving, independent phase pairs and numerical combination are verified;
marketing layer/oscillator names are not recovered.

## C/D. Inputs and generated sample interfaces

Each selected lane j uses a 14-word record Q+14*j. P:387 emits this layout
under either flag0 alternative (P:41C..44A or P:44C..458).

| Word | Verified use, with meanings limited to data flow |
|---|---|
| +0 | X kernel pointer; P:7A4 -> r3 |
| +1 | Control fraction/gain-like word; P:7A5, P:7A6 |
| +2 | Inner repeat count; DO X:(r0)+ at P:7C8 |
| +3 | Nonzero/zero branch selector; P:7D0..7D5 |
| +4 | Flags; P:7D1 -> n3, selects lookup schemes |
| +5 | Multiplicative coefficient; P:7D2 -> x1 |
| +6 | Multiplicative phase/correction coefficient; P:7DE |
| +7,+8 | Lookup-base/correction terms, consumed P:7DF/7E7 |
| +9 | Periodic phase increment, P:7E9 -> y0 -> P:7F1/7F2 |
| +10..13 | Lookup-result/interpolation coefficients, e.g. P:832..845 |

Lifecycle and note-follow inputs are handled in P:281/P:4D5/P:657/P:387
before this region. Relevant raw state remains Y:122 flags, Y:12F current
note, Y:159 target and Y:130 primary level. Prepared Q words additionally
depend on patch bank, per-voice modulation and table information; their
numeric values cannot be filled with an invented preset.

**VERIFIED lane output:** 32 signed 24-bit stored words per lane at
Y:A01+j+3*k for k=0..31, additive when inner repeats require it.
P:9C8..9D8 combines the lanes using coefficient ramps into a **mono**
32-word block X:[2C46,2C66). This is the raw per-voice output before the
selected post-processing region. No stereo/pan interpretation is required.

## E. Gain aliases: producer to final group multiplication

**VERIFIED pointer accounting:** after three 14-word records r7=X:5A5.
P:470 repeats the two coefficient reads P:472/476 three times: six words,
not two. The following emissions reach:

| Producer | Slot 0 coefficient | Meaning / consumer |
|---|---|---|
| P:47E | X:5AB | Post-processing selection word; P:9DD |
| P:4C7 | X:5BB | Parameter/header consumed into n6 at P:A7F; exact role unresolved |
| P:4D0 | X:5BC | Gain ramp delta; P:A8A -> y1 |
| P:4D1 | X:5BD | Persistent current gain; P:A8D reads, P:A91 updates each sample |
| P:4D3 | X:5BE | Further parameter read from bank; not the direct final gain operand |

Generalized addresses add 0x4A*i. The gain ramp/current words are E+0x42/+0x43.
P:4CA reads the previous current gain through x:(r7+1), which is X:5BD.

At P:9DD r0=X:5AB. Consuming mode leaves 5AC. The selected P:BDD call
consumes **seven** words: P:AA8,AA9,BDF,BEC,BF3,C10,C1A. Its other helpers
do not advance r0 on this path. r0=5B3 on return; P:A1F adds eight to
reach 5BB. P:A7F consumes header, P:A8A consumes delta, and P:A8D then
addresses current gain at 5BD. This closes the alias left open in phase 4.

**VERIFIED origin of final target gain:** P:4BE advances the control pointer
to Y:130; P:4C6 loads that primary envelope level. P:4C3/4C4 load X:2B2
and X:2B3 from the selected bank, while P:4BF/4C1 load global X:98C and
X:95. P:4C6 computes a patch coefficient plus its global modulation term;
P:4C9 multiplies by the envelope level. P:4CB..4D1 turns target-current
difference into a ramp using X:39 (five, i.e. 32-sample smoothing here).
ARM 080275D8..27618 obtains bank parameter 0x1C, converts it via
080281D4 -> 08027EE8 -> 0803B928, and writes X:2B3+172*b. Parameter
identity beyond a patch-derived level coefficient remains unresolved.

The event level reaches this target through the squared input, sensitivity
helper, Y:14D target and Y:130 envelope documented in phase 4. Neutral
sensitivity removes event-level dependence; patch gain is therefore distinct
from velocity influence. X:98C/X:95's broader source semantics are unresolved.

**VERIFIED final operation P:A8D..A94:** read old current gain g; compute
new g=max(0,g+delta) and store it; multiply the sample by **old g** in the
parallel MAC; right-shift old group sum four bits before MAC, then left-shift
the result four bits and store back. The pre-ALU parallel move matters.
Ignoring finite-width effects, the mix relation is:

`group_next ≈ group_old + 16 * fractional_product(sample, old_gain)`.

This is not an exact floating-point equation: shifts, discarded low bits,
transfer limiting and intermediate precision matter. Final accumulation
has no separate group-gain operand. Group processing/gain happens later.

Before that multiplication, the selected path also applies six coefficient
ramps (P:9AC..9B7), lane combination (P:9C8..9D8), nonlinear/recursive
post-processing (P:BDD and callees) and its input scaling P:BDF..BE7.
These branch/filter factors must not all be renamed "velocity" or "volume".
The final envelope/patch gain alias is closed; the semantic provenance of
every post-processing factor and every alternate mode is **UNRESOLVED**.

## F. Numeric contract

**VERIFIED architecture:** 24-bit X/Y words; 24x24 fractional multiplies;
56-bit A/B accumulators (8 extension + 24 high + 24 low bits). Ordinary
MAC and explicitly rounded MACR differ. Full-accumulator transfers use the
DSP limiter; direct A1/B1 transfers do not mean the same operation.
NXP [DSP56724RM section 4.3.1](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf)
and [DSP56300 Family Manual sections 3.1.6/5.4.1.2](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf)
support these rules. Saturated full-accumulator transfers clamp to 7FFFFF/800000.

P:10A sets SR bit21 (rounding mode); do not misidentify this as arithmetic
saturation bit20. P:CA2 sets MR bit3 (SR scaling bit11) during recursive
filter arithmetic; P:CB6 clears it. The selected output seam occurs after
that temporary scaling has been removed. Preserve SR/MR behavior across a seam.

**VERIFIED:** the stored raw block is 24 bits per word, not floating-point
samples; output uses no explicit final MACR, so a blanket claim of rounded
output is incorrect. Filter paths do include MACR. The group mixer explicitly
uses the ASR4/MAC/ASL4 sequence above and limiter-aware accumulator transfers.

**HYPOTHESIS:** Q1.23 is a useful nominal interpretation for raw sample/gain
words. **UNRESOLVED:** absolute full-scale convention through the complete
output chain, headroom, scaling for every mode, and all hardware input/output
widths. Do not send a presumed unity-normalized Q1.23 block to the +4-bit mix
without proving its magnitude against stock coefficients.

## G. Generator versus downstream processing

| Stage | Verified behavior / qualified interpretation |
|---|---|
| Before generation | Gate/lifecycle, level and note tracking; modulation and coefficient preparation P:4D5/657/387 |
| P:77F generation region | Masked periodic phase progression, table addressing, worker lookup, weighted result combination; alternative procedural paths |
| Immediately after lane generation | Six ramps and three-lane numerical combination; raw mono X:2C46 block |
| Before group accumulation | Selected P:BDD: nonlinear normalization/lookup and recursive two-stage filtering (MACR feedback/state stores at P:CA6..CB5); prepared gain ramp |
| Group accumulation | P:A7F..A94, shared bank sum |
| After group accumulation | Bank-specific processing P:11E9/11F1,1203/1209,125D/126A; two bank streams combine at P:242..24E, with more downstream terms |

Interpolation and recursive filtering are supported by arithmetic/state flow.
Waveshaping is a supported interpretation of nonlinear sample-dependent
transforms, but exact distortion/effect algorithm names are **HYPOTHESIS**.
Per-voice stereo panning is not established at the mono seam. No claim that
every region inside P:77F is purely an oscillator is justified.

## H. Table and work-buffer dependencies

| Table/area | Size / indexing / initialization |
|---|---|
| Y:E30..F3E wave-info | 0x10F words copied from P:28DD at P:28D9; 7-word records for indices <14 via ARM 08028132. Index1=Y:E37, mask 1FFF, bytes exported |
| Wave blocks, e.g. index1 base X:128800 | ARM 08035E28 builds pointer list at 20005D40 starting 100000; generated families advance 28800, but indices3..12 alias the preceding base (Phase6C correction). 08028132/281C2 publishes base and wave-info pointer. Prepared bases/index masks reach lookup work. Complete valid table footprint is not inferred from allocation stride |
| X:1B10 | Five words copied from P:272C at P:2679; adjacent interpolation in P:3B0..3B3; valid index range depends on parameter |
| X:2000..21FF | 512 words generated by ARM 080293BC; recurrence and interpolation in frequency preparation, shared among slots |
| X:2200..23FF | 512 ARM-generated words at 080293F0; Y:1C pointer, indexed by normalization result P:B1C; shared |
| X:1600..193F | 832 upper-24-bit words uploaded from ARM flash 08052BB4 at 08029430; exact exported bytes/hash in contract.json. Filter interpolation banks include 1600 plus row offsets,1840,1880,18C0,1900; individual index bounds require the path parameters |
| X:1960+0xC*i / X:1A80 | Per-slot kernel coefficients and shared template, initialized from P:2720 at P:2666..2671, subsequently transformed in P:387 |
| X queue/Y returned data | Transient lookup work/results, not immutable synthesis tables |
| X/Y scratch listed above | Transient generated indices, weights, raw blocks and filter state; must be reusable across voices |

**VERIFIED mailbox relationship:** waveform-index1 pointer is assigned by
ARM table setup using selector3. DSP P:1C84 calls transform P:1CE6 and
generator P:1CFE; destination derives from the mailbox high bits. Other wave
indices select operations 2,4,5,0. This establishes a runtime/boot table-job
dependency, not a guessed table name. Operation2 builds a different shorter
iterative structure. Full byte-perfect reconstruction of these generated
wave blocks is **UNRESOLVED**; neither the parser nor exports fabricate them.

## I. Cadence and audio scheduling

**VERIFIED initialization:** P:2655/2656 sets X:38=0x50. P:140 derives
X:39=5, X:3A=32, X:3B=16, X:3C=31, X:3D=15, X:3E=64, X:3F=96 and
X:40=0. This establishes a block-based N=32 path, not one call per sample.
The reviewed direct DSP references to X:38 contain its startup store and
consumer; host-addressed modification remains possible.

P:1D9 tests ring occupancy `(Y:FFE-Y:FFD)&0x3FF` against 0x300. Only when
the condition is satisfied does it clear work sums (P:759), execute descriptor
request pass P:198D, completion pass P:19BF, group processing and output.
Active contexts can generate once per serviced block, using two function
entries where lookup completion is needed. Release/idle paths can skip work.
The output path advances a ring pointer and uses ESAI/DMA buffers. P:1B4
services the ESAI last-slot interrupt and DMA addresses. ISR re-entry,
main-loop timing, ring occupancy and worker completion all affect cadence.

**Phase 6 VERIFIED programming / conditional model:** PCTL=002028 gives
Fsys=41×EXTAL under DSP56724 mapping. ARM sets MCO1=HSE/4 using a 24 MHz
HSE firmware assumption; physical MCO1→EXTAL wiring is **HYPOTHESIS**.
ESAI uses 24-bit words, two 32-bit slots and nominal Fsys/5120 frame rate.
Conditional model: 246 MHz and 48,046.875 Hz; 163,840 Fsys cycles per
32-frame period. These are total period cycles, not available voice cycles.
Actual board clock/rate and finite available headroom remain **UNRESOLVED**.
Timing hooks were not read. See the Phase 6 scheduler and clock evidence.

## J. Conservative static budget evidence

For the explicit selected path, the reusable loop counter counts decoded
instructions, not extension words or cycles. Its major-loop subtotal is
**4,355 channel-zero issued instructions per 32-word voice block**
(about 136/sample). Phase 6 corrected two DO loops to X:3C=31 iterations,
rather than 15. The normalization loop alone contributes 704; two
recursive filter bodies 320; component combination 544; final mix 256.
Hardware DO loops account for most of these repeated instructions.

The request produces 192 lookup words for three lanes on this profile;
worker fetch body P:120..126 contributes another **1,152 instructions**
on the worker, excluding synchronization. More inner repeats or different
lookup schemes change these counts. P:775/worker polling waits are unbounded
from static input alone and cannot be assigned a fabricated finite cycle cost.

**HYPOTHESIS engineering estimate:** roughly 5,000–7,000 channel-zero issued
instructions per selected voice block after fixed setup/call overhead, before
upstream control preparation, global audio work, IRQs and stalls. The counted
subtotal is the verified part; this range is not a worst-case bound.
Twelve active contexts would multiply the selected subtotal to 52,260 per
block, plus other work. Actual active count is lifecycle/patch dependent.
**UNRESOLVED:** available headroom and feasibility of any specific alternative
algorithm. Published peak MIPS is not a measurement of this board/program.

## K/L. Ranked theoretical replacement boundaries

These are static candidates, **not demonstrated safe firmware patches**.

| Rank | Boundary | Preserved stock behavior / tradeoff |
|---|---|---|
| 1, smallest lane-generation region | Produce Y:A01+j+3*k before P:9A5 | Retains six ramps, three-lane combination, post-processing, gain and group mix; must satisfy two-pass bitmap/queue expectations and stock lane controls |
| 2, best practical candidate | Produce mono X:[2C46,2C66) and enter P:9DD | Retains stock per-voice post-processing/filter, envelope/patch gain and downstream mix; replaces lane generation plus lane combination |
| 3 | Produce mono block immediately before P:A7F | Retains final gain/group mixing but removes stock per-voice nonlinear/filter processing |
| 4, most invasive | Replace descriptor handler P:281 | Also owns lifecycle/control/coefficient updates, allocation feedback and sample scheduling; much broader contract |

**VERIFIED local contract at recommended mono seam P:9DD, slot0:**

- INPUT BUFFER: X:2C46..2C65, exactly 32 signed 24-bit stored mono words.
  Absolute amplitude normalization remains unresolved; use the stock
  full-accumulator transfer/limiter convention and preserve scaling mode.
- LIVE POINTERS: r0=X:5AB (post coefficient selector), r4=Y:5AB
  (per-voice post state). Both have numeric value 5AB; they are different spaces.
  General formulas: r0=E(i)+0x31; r4=S(i)+0xC.
- OTHER INPUT STATE: X:CC=bank, X:2C=current context, X:39..41 block/scaling
  constants, Y:10..1C constants/table pointers and valid per-voice filter state.
  Downstream paths set their own r1/r3/r5/r6/r7 before use; this is not a
  promise that caller registers or SR may be arbitrarily clobbered.
- GENERATOR CONTROL available upstream: Y:12F/159 current/target note,
  Y:122 lifecycle flags, Y:130 envelope, bank parameters, prepared Q records
  including phase increments Q+9+14*j. Input-to-alternative parameter mapping
  still needs a design; raw note and increment have different representations.
- OUTPUT: selected post path transforms the mono block and uses the existing
  ramp/current gain at X:5BC/5BD before accumulating into bank sum X:2DF0
  (slot0). There is no direct final DAC output at this seam.
- PERSISTENCE: preserve stock lifecycle/envelope/note-follow/filter state.
  Alternative generator state must be separately defined; the known 40-word
  sample context contains downstream state and cannot all be reclaimed.
- SIDE EFFECTS: fulfill/replace request/completion bitmap transitions, avoid
  stale queue work and consumer-pointer mismatches, update generator state
  exactly once per block, retain X:CC and context timing/accounting. Bypassing
  P:775 requires coherent queue scheduling, not merely filling a sample buffer.
- TABLES: an alternative may avoid stock waveform/kernel tables, but preserving
  the selected stock post path still requires its normalization/coefficient
  tables and the SR/modulo-register save/restore behavior.

**UNRESOLVED global ABI:** exact clobber sets for all branch combinations,
ownership of every unused RAM word, worst-case scheduling deadlines and
amplitude calibration. The local buffer/pointer contract is established;
a fully safe drop-in replacement ABI is not yet established.

## M/N. Readiness and next step

**Phase 6 gate: NOT-YET-DETERMINED** for a resource-qualified comparison.
Conditional limits support preliminary estimates, but hard fit and safe
implementation are unproved. Candidate P tail is 5,538 words under the
conditional mode; no persistent state RAM is **VERIFIED AVAILABLE**.
X:2C46 is shared scratch used by both per-voice and global routines, not
private or persistent voice storage. It must survive through selected
P:A94 consumption. The full obligation ledger is in dsp-resource-audit.md.

Single best next firmware step (Phase 6C): prove the normal domain of the bank
selector at20006800 and propagate it through parameter-address constructors,
then close the other host/mailbox and DSP indirect bounds. Both candidates are
INIT-TOUCHED, which does not disqualify after-init availability. No Plaits
implementation or source analysis was started.
UI bank naming was not pursued beyond existing six/six evidence; it does not
change the replacement boundary and remains a hypothesis.
