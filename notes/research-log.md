# Research log — Circuit Tracks build 4486

## Phase20C6-ARCHSELECT (2026-10-07)

**SELECT-A / CONDITIONAL preference.** Neither complete protected offline patch
nor hardware readiness is qualified. Device must remain unopened; future normal
USB-C/MIDI/microSD-pack interaction only where applicable. No such interaction,
probe, packet, DSP execution, math change, polyphony, firmware patch/repack or
new universal writer/free-memory census was performed. Sandbox setup failed
before initial reads; the approved read/report/test fallback preserved all bytes.

**VERIFIED source/dependencies:** reused8682 byte-checked DSP listing rows.
552 individual nominal selected/shared addresses classified; full V96/S40 and
X74 mapped, UNKNOWN semantics retained. Kernel3B5/3BB/3BF/3C2 shows coefficient
base1960+90hex=19F0 and source+120hex=1A80;97B reads +144decimal. Dynamic extents
are unresolved, not bounded by nominal12-word stride. Auxiliary0 is lane0*c0
pre-add at9CA; auxiliary1 is first-two-lane sum at9CD. Natural2C66 comes from
phase-track store7F1, not the final combiner. Two passes/bitmap/worker/cursors/
ramps/post state remain obligations. UI bank0=Synth1 remains HYPOTHESIS.

**CONDITIONAL B thinning:** retain complete first2 lanes for original auxiliaries
and a third-lane phase/guard slice; possible omitted record fields0,1,10..13
are X597,598,5A1..5A4. Six candidates, not a maximum theorem or ownership proof.
84 generator-associated words considered,0 qualified. Seventh kernel/other word
needs its own producer/consumer/other-slot/service closure. Original first7
[57B,582) collides with retained lane0 work. New Plaits-derived auxiliaries
would require a different selected-post contract, not presumed equivalent.

**VERIFIED/CONDITIONAL edit accounting:** A5 identified origin instructions
9B9/202B/198/2A3D/2A3E in4 proposed windows;10 direct safe-profile review sites
are not counted as changed. B3 anchors387/79D/9B9, no complete finite bypass
set. Unknown control/adaptor sets stay separate from numeric site counts.
Explicit comparable-boundary liveness rerun: R0 redefined9D9, R4 post-live,
A defined9DD but IRQ168/16A/16C snapshots plus caller/all-mode closure unresolved.
26 conservative raw words remain for both; minimum or B reduction not proved.
Arbitrary service writes cannot be ignored/reset without losing state continuity.

**MEASURED old traces / CALCULATED projections:**7520 paired block rows reused,
no renderer rerun. P-state mean12111.79/max18510 versus high-X7943.55/13335.
With hypothetical P temporaries and comparable416-cycle wrapper: A partial
12629.78 mean/19516 max-style, B8461.54/14341. Conditional renderer+wrapper
relaxations29124/18729 exclude guards/bypass/converter/stock/IRQ/DMA and are not
whole-voice bounds. State costs already included, not double-added. A866P partial,
1626 planning,102 data; B740 comparable constituents/39 minimum data plus unknown
glue. No B removed-stock saving fabricated. Whole costs remain null.

**TESTED deliverables:**16 requested reports,28 members repeat identical,
15 focused source/contract/refusal tests,851 input guards unchanged. Tools
ct_archselect.py/ct_archselect_verify.py and test_archselect.py; new architecture-
selection/takeover-feasibility notes; requested six notes updated. Canonical
phase20c-archselect/final-v1/repeat-v1/checks-v1; probe-v1 preserved/superseded.

**Decision:** A preserves the verified auxiliary/guard/post contract; B's object,
locality, replacement and total-cost advantages remain unqualified. A global
risk remains explicit; not a universal impossibility finding for B. Authentic
full boot is not required for a constrained offline fixture, but all edits and
continuations must be finite; neither candidate satisfies that now. Exact next
phase20C7-A-COVERAGE: only needed actual-EA control-store exemptions/adapters and
typed P/control boundaries, reusing the344 obligation ledger. Not begun. Offline
patched construction NO; flashing NO; external recovery stays a separate gate.

## Phase20C5-ENFORCEDSTATE (2026-10-07)

**PARTIAL / design only.** Exactly two domains: preferred appended P7[3FF0,3FF7)
versus reclaimed X7[57B,582). No broad memory search, renderer/firmware patch,
CPU execution, packet, repack, hardware, probe, installation or download.
Natural X/P ownership REFUSED and sealed numerical P-state PASS are preserved.

**VERIFIED original instruction evidence:** helper202B..2070 is70P; entry202B/C
is a two-word MOVE. CountX35F is latched by2040 DO withLA204B. Destination
X364+5*k loadsR4 at2043; destination read2048, MAC/next coefficient2049, next Y
prefetch204A and commit204B. No per-record count or normal positive N bound.
Whole-helper clone is preferred over a long hook atLA. A five-NOP tail accounts
for documented endpoint restrictions but actual guard encoding/ABI is unqualified.
SHI198 data entry bypasses168..16C A saving; protect actual commit19D per word.

**VERIFIED pinned-manual refinements:** FM PDF205 restricts DMA I/O access to
TX/RX data registers, not generic DMA-to-DMA-control writes. CPU indirect control
commits remain unclosed. FM195/203..205: DE clear may leave a current/captured word
pending. Ordered DE0/DTD1/DACT0 is required, not DE alone. RM115 addsDTD6/7 at
DSTR6/7; inconsistent DCH[10:9]/[2:0] wording is not used for quiescence. FM99/100
has16x48-bit stack entries:26-word saves need at least13 paired entries plus
renderer3, leaving no caller/IRQ space. Stack-only strategy rejected. FM438/439
DO hazards and372/373 MOVEM/CCR rules apply. FM426..431/437 supports guard cost
arithmetic; false bit branches add1, so SHI classifier is4..60, correcting4..48.

**CONDITIONAL design:** central nonblocking DMA/control validator with distributed
actual-EA commit adapters. Pin audio0/1, review safe X/Y2..7, prohibit P-DMA during
one-way ownership. Trusted startup/quiescence/init gateway through reload/reset.
X3FF0 is not P3FF0 under fixed mapping. Preserve selected387/77F request/completion,
combiner/auxiliary/guard work; replace final mono only. No selected writers/readers
removed in preferred A. B requires bypassing both passes and a new aux/guard
contract, plus foreign host/DMA X guards. No naturally free region is assumed.

**CALCULATED proposed storage/cost:** P26 save +P3 spills +P3 controls +P30 policy
+P32 typed shadow +P1 fault +P7 numeric =102P. Shadow/ABI/reentrancy remain open.
Seed[0,0,200000,0,A3D7,200000,0] costs28P/63 nominal init cycles after quiescence.
No hidden eighth numeric/activation flag; diagnostic metadata is counted. Save26
costs104P/364 cycles. Voice wrapper712P, guarded204B89P, partial SHI37P and init28P
sum866P; planning1626P versus5374 conditional capacity is not a fit proof.
Naive344x24P=8256 exceeds capacity; caller/EA/CFI/converter/init costs remain extra.

**MEASURED existing trace / CALCULATED hypothetical conversion:**7520 blocks,
34997772 PC ordinals reused. Remaining18 X sites transfer7/20.3984/118 words,
adding35/101.9920/590 nominal cycles if changed to P. Inferred totals are
10820/12213.7775/19100; no changed renderer execution. Conditional renderer bound
28708 plus wrapper416 yields illustrative Q1/N20 total29548+unknown. Q/N are not
stock bounds. Original combiner562 remains. Output R0 immediate must be changed
inside the renderer; an outer setup is overwritten, retarget width/cycle delta0.

**TESTED evidence:** all14 requested reports plus33 supporting members;47 members
repeat identical;17 focused spec/boundary/arithmetic/refusal tests;797 protected
inputs unchanged.8682 DSP listing rows byte-checked by reused reader. No guard
assembled/executed or object reserved. New tools ct_enforcedstate_design.py and
ct_enforcedstate_verify.py, tests emulator/tests/test_enforcedstate_design.py.
Canonical final-v3/repeat-v3/checks-v3; probe-v1 andv1/v2 preserved. Three new
notes and requested historical updates completed. Original SYX/BIN/DSP hashes
and older renderer/evidence inputs remain guarded.

**UNRESOLVED:**344 decoded indirect X/L candidates need actual-EA/parallel/RMW
exemptions or adapters; this is not an all-normal registry. Typed owner P accesses,
computed calls/returns/INIT/ROM exclusion, immutable code/trusted startup/mode,
policy/IRQ/FIFO/stack ABI, global N/Q/guard counts, pitch/headroom and recovery
remain open. Two hooked writers are not complete mediation. Offline patched
construction NO; flashing NO. **Next:** finite source/ISA coverage certificate
for DMA/control-capable stores and P/control boundaries before any patch image.

## Phase20B6-SNAPSHOT-DESIGN (2026-10-07)

**READY-FOR-ACQUISITION-DESIGN / CONDITIONAL**, not availability, acquisition
or flashing. Static checkpoint strategy remains EXHAUSTED. No device/debugger,
MIDI/SysEx, firmware/payload change, stockCPU or Plaits. Twelve requested design
exports underbuilds/phase20b-snapshot-design/final-v4; repeat-v4/checks-v4.
Reusable exporter tools/ct_snapshot_design.py and design verifier/tests added.

**VERIFIED pinned primary documentation:** DSP56300FM7.2.4 (PDF136) executed
program-fetch breakpoints acknowledge after matching instruction; MOVE memory
access breakpoints after following instruction. FM7.2.5/7.2.7 requires preserving
PAB/PIL/PDB before injection; PABEX is would-execute location. FM5.4.3(PDF96/97)
16x48 stack and SSHpop side effect; OMR.SEN extension and SP/SC/LA/LC/SR frames
must be accounted. RM22(PDF457..460) two serial4-bit TAPs, per-core/coupled debug,
different JTAG0/1 instructions; four external signals in RM2.21, no boardTRST
assumption. Actual silicon/core/pads/voltage/security/tool remain UNRESOLVED.
RM6.1.1 XOGDB versus visible Table6-2 YOGDB label conflict checked in rendered
PDF118/119; resolve before selecting opcode. DMAS is stall-interrupt threshold,
not a freeze control. No new network retrieval or installation.

**BOUNDED-PROOF / CONDITIONAL liveness:** selected routing0/nonlinear1/5/5
post inputs can omit incoming locally redefinedR/N/data values, skippedX[5B3,5BB),
upstreamY8F..91 and initialYF64..68 under original overwrite/modifier/async proof.
IncomingSR/OMR/R4/materialM, active stack and retained histories remain required.
RawR0 still needed for raw9DD normalization proof/full-state preservation.
**CALCULATED erratum:** S59F+12decimal=5AB; use S+0C..S+1A for14 Ywords.
Old20B5 numeric slot0 range was correct, its stated hexadecimalformula was not;
previous exports retained, current specification corrected explicitly.

**VERIFIED reused stock source:**5E operation1 reads X/Y via269E4/29344/SHI156
and replies37B0C/20C90; it changesX10/X11/Y2000..2005 and does not capture CPU/
stack or freeze seam. Physical endpoint remains unresolved. Selection1 tests
cannot capture normal selection0. ARM debug exposesARM, notDSP private state.
Additional ARM patch provenance path reused3BE60(view+344+4*bank) and3BBE8/
3BC06(model+0C pointer-cell/byte-buffer,model+10 length). Runtime root and coherent
ARM/DSP coordination remain unresolved; no getter/function invoked.

**DESIGN HYPOTHESIS:** inline save/copy/commit hook with first status/subfields,
AGU, loop/stack, data and bounded memory; no assembly, buffer reservation or patch.
**CALCULATED inventory / ESTIMATE:**100 datawords;43 conservative fullregister
words; activeSEN0stack0..30;metadata24..48 ->167..221 beforetables,1511..1565
with1344 selectedtablewords; rough160..320P words. Not measured or placement proof.
Rank1 OnCE,2 hook+stock readback,3 hook+MCU bridge, all conditional. Recovery/
bootloader independence and brokenDSP rollback remain UNRESOLVED; flashingNO.

**TESTED:**8 design checks, exact repeat reports/text/PNG equality, byte checks
for original seam and unchanged SYX/BIN/DSP/previous20B5/source hashes. No real
snapshot, formal schema meta-validator, importer or replay tested. Machine-readable
bundle/typedimport and strict admission designed only. Existing CPU gate unchanged.
Next: qualify DSP TAP board exposure and controller boundary/stack/coherence
capability from existing documentation; physical work requires separate authorization.

## Phase20B4-PROJECTASSOC — PARTIAL, event use refused (2026-10-07)

**VERIFIED:** byte35 issettings.keyboardOctave(encoded−1/0); bytes221,238,
255,272,289,306 are stored values of zero-based macros1..6. All32 macro
assignment rows and20 modulation rows are identical. Original descriptors5,
BF,D0,E1,F2,103,114 agree with installed field offsets. None is assumed UI-only.

**VERIFIED:** originalEEFE project loader mapsfilebase26D14 tologicalbank0
parameter view+344 and26E68 tobank1+348. AF66 synth identity records atCD64
have literalbyte0=0/32; pack/native slot interpretation stillUNRESOLVED.
F438..F49C chooses full340-byte copy or macro-value/keyboard-only update.
**TESTED conditional serialized merge:** applying that update set toauthored
patch producescached340 bytes exactly; matching retainedID does not ignore them.

**VERIFIED original formula / CALCULATED conditional:**35F84 clamps signed
value−start, multiplies signeddepth−64 by2, SDIV truncates toward0, accumulates
signed16 correction atdestination−1.3602A clearsARM work and aggregates8
macros;360B2 clips corrected parameters. Stored contexts change8 correction
destinations. Nonconvergent transfers: X2E8 020408→2C58B1, X2EA1C0000→0CAAAA.
**VERIFIED supersession of20B3:**282F4 literal28750=805BCD0;LDRH805BCD4=590C,
fixed flash addend. ConditionalX3E7 targets19B6AA→2FB6AA; currentX2E9unknown.

**CALCULATED conditional:** row0/2 depth corrections0; targetX3D0=31FFCE,
X3D2=02AAA8. SmoothedX2FE/X308 andsourceY17C/Y126/Y131/Y135 remain
UNRESOLVED. Equal route bytes do not closeY91. ARM macro work clear is not
DSP history clear; no bounded retainedY history origin admitted.

**VERIFIED layout, not event semantics:**AF46/ADB2 andB03E..B0BE corroborate
two first groups, eight3240-byte patterns/group,32 steps with28-byte stride.
Raw first record preserved; note/gate/velocity names and playback association
not guessed. Conditionalload/recompute=MATERIALLY DIFFERENT; selectedevent-time
context=INSUFFICIENT EVIDENCE. No existential non-equivalence claim acrossall events.

**TESTED:**31 focused/previous regressions including4096 independent macro
fixtures; repeated exports byte-identical; original/prior20B/20B2/20B3/renderer
hashes and overwrite guards pass.0 stock instructions; no hardware, downloads,
Components launch, stock patch orPlaits input. Evidence:builds/phase20b-projectassoc/
final-v2 andchecks-v2. Best next step:traceproject0group0pattern0 original
sequencer/automation consumer andevent routing toqualify or reject convergence.

## Phase 20B3-INPUTREC — PARTIAL qualification; replay REFUSED (2026-10-07)

**VERIFIED:** fresh original657..758 and focused caller/AA8/BDD/C2D/smoother
decoding matches the byte-checked canonical original.37 bank-control words
X2D5..2F9; count at2FA and five-word rows at2FB. Original27A10 constructs20
rows;2872C/286BC count publication can defer shrink, not compact neutral rows.
**BOUNDED-PROOF count20/linear:**105 X reads include final lookahead35F..362;
68F still dereferences the preloaded source1 on the last iteration.

**VERIFIED source / CALCULATED conditional:** authored filter bytes60..68 are
00,0A,01,01,0D,00,02,36,4F. Row0[4,4,113,12],row2[7,0,68,12],others
[0,0,64,0]. Original source table maps0/4/7 toY17D/17C/126. Destination
table0805B5E0 maps12 toY91 and0 toY7C. Under original routing/linear AGU
and no intervening alias,676 clear plus690 destinations proves8F/90 modulation
zero;91 remains driven by retained per-slot sources and smoothed amounts.
Exact original6D9/6DE/6ED producer chains are exported; output values not guessed.

**VERIFIED:** control IDs1F/22/23/24/26 and modulation depth IDs have runtime
correction indices, unlike the already-qualified selector IDs. Raw0/nominal
depth0 do not prove corrected/smoothed0. X2E9 andX2FE+5*i have1B89 prior-value
smoothing; patch bytes alone cannot establish their active numerical values.

**TESTED source comparison:** four cached project members; project0 same-name
340-byte record at158996 differs at35,221,238,255,272,289,306, six in macro
records per installed mapping. Exact selected340-byte match absent in all four.
No actual note/slot history inferred from a name match or guessed project fields.

**VERIFIED selected-path history / UNRESOLVED numerical origin:**Y5AB..5AE,
5B7/5B8 survive trigger clears[5AF,5B7),[5BD,5C5). AA8 andBDD/C2D writers
confirmed; boot zero is not a qualified runtime last writer. All six values,
YF64..68, material modes/modifiers/stack and natural guard remain unresolved.
No checkpoint admitted; preparation and seam refusals precede CPU execution.

**TESTED:**19 focused/previous checkpoint regressions; fresh repeated exports
byte-identical, source hashes and overwrite refusal pass. OriginalSYX/BIN/DSP,
prior20B/20B2 and renderer/nativeDIV/restoring artifacts preserved.
Evidence: builds/phase20b-inputrec/final-v3 andchecks-v4.0 stock instructions,
no Components launch/refetch, hardware, full boot, patching or Plaits feeding.
Best next step: qualify project0 event/patch material equivalence and original
macro correction state before selecting a bounded numerical event/history.

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


## Phase 20A-BOUND — current timing result (2026-10-07)

**TESTED / CALCULATED:** unchanged442P renderer, reset-reachable maximum13335
cycles/block; all witness samples/seven states/fullPC traces exact, repeated.
**PROVEN-BOUND / CONDITIONAL:** upper13379 including12 boundary cycles, replacing
23902 for legal reset-evolved control/state. 8 PW+8 wraps maximum; exact32..80
ratio calls; at most93 carries. Rare first-sample deferred wrap is separately
bounded11603 and tested with two k=1 ratios. Residual44=12 allowance+32 unresolved
ordering cycles; upper is not claimed attained or globally tight.

Ten raw copies:44.37% matched mean,81.39% reachable maximum,81.66% upper;
remaining30050 cycles /18.34% **TIGHT RAW MARGIN**. One/two/four raw generator
costs fit comfortably; actual stock workload/ABI/ownership/contention remain
**UNRESOLVED**. No renderer/firmware/hardware/polyphony/integration changes.
Next:offline stockP:0x9DD seam/ABI replay plus stock workload accounting before
any ten-voice claim, only under a separate phase request.

Report:notes/plaits-reachable-timing-bound.md. Evidence:builds/phase20a-bound/final/.
Earlier timing maxima/bounds below remain historical; this section supersedes
those values for the unchanged REGOPT renderer's legal standalone domain.


## 2026-10-07 — Phase 20A-REGOPT: exact scratch/register optimization complete

- **IMPLEMENTED / MEASURED:** reuse completed44-field liveness, peak19/colors19;
 16 helper-preserved registers Y1/R1..7/N0..7 +3 shortX spills. First candidate
 482P/21 dead pairs; refined442P/50 static instructions removed. ExplicitA1
 word boundaries retained; reload removed only with provenA0=0; deadX0 literals
 fold into equivalent unsigned6/signed24 immediate ALU. No format/interpolation/
 event/correction algorithm change, no quality reduction. Helper18P unchanged.
- **MEASURED:**7 persistentX,3 spillX+16 work registers,3 controlsX,32outputY,
 LUT0, stack3. Data-memory45/including registers61 vs86. Xreads11075975→4631046,
 Xwrites5900052→1791373;10553608 removed (62.1677%); all long-X accesses removed.
 Register/scratch addresses belong solely to private standalone emulator.
- **TESTED:**43 unchanged cases/7520blocks/240640samples twice plus9 focused
 cases/4608blocks/147456samples, golden and optimized both repeated.388096
 samples/all7 block states exact to golden/oracle; event kind/order per sample,
 arithmetic/branch/helper counts unchanged. Current metrics/pitch/rates/2048
 continuity hash-identical. No saturation/address/stack/register-clobber failure.
 Native/restoring sources/artifacts, core and original inputs remain intact.
- **CALCULATED / CONDITIONAL:** same frozen timing rules with documented
 CMP immediate1/2; matchedmin6278/mean7270.1787/max12390, upper12402, structural
 23902. Focused corner block5 raises all-validatedmax12670/upper12682 (gold16532).
 Mean gain22.1511%=STRONG. The named-scope timing exporter left complete stress
 block CSVs; a separate summary completes them without renderer/liveness rerun.
- **CALCULATED hotspots:**long-X0%,registerMOVE23.10%,short-X18.30%,Jcc16.82%,
 DIV10.87%. Helper49 clocks/21DIV unchanged. No new parallel form or branch
 removal; preparation/memory traffic optimized with exact word semantics.
- **CONDITIONAL arithmetic target:**1/2/4/8/10/12 scaling exported at48k and
 48046.875Hz. Ten1+1+4+4:mean44.37%,worst77.33%,structural145.89%;37140clocks
 remain after worst before any stock work. Actual timing/headroom/RAM/ABI
 **UNRESOLVED**; no feasibility declaration or MIDI-track DSP hosting claim.
- **Next:**control/state-aware structural-bound refinement, offline, before
 further source changes. More dual-accumulator/parallel scheduling may help
 register traffic, but no saving or integration is presumed.

Report:notes/plaits-register-optimization.md. Canonical:builds/phase20a-regopt/
final-report/; numeric:final/, extended/; liveness:liveness/; timing:timing/,
stress-timing-summary/. No hardware/MIDI/SysEx, firmware/original modification,
stock reservation, model switching, polyphony or P9DD integration.

## 2026-10-06 — Phase 20A-TIMING: offline cycle and pipeline audit

- **SOURCE-DERIVED:** pinned FMRev5 AppendixA/3.5 and DSP56724RMRev1
  private-memory/seven-stage/forwarding description. DIV1,REP/DOsetup5,
  ANDI3,JSR/RTS3,Jcc4 +false1; lab/lim and accumulator interlocks accounted.
  Family-to-device timing correspondence explicitly **CONDITIONAL**. Visual
  table review confirms malformed short-store row:best/upper2,lower1;
  exact physical short-store timing remains **UNRESOLVED**.
- **MEASURED static trace census:**453 executed sites/23families,38,641,041
  issuedPCs/7520blocks. X-only/Y-output; noP-data/XY/double-space/MAC/MACR.
  Parallel CLR/TST/ROL register moves counted once. DO32:233120backedges,
  7520exits; REP21 each of283027calls; firstR0use>=135 intervening opcodes.
- **CALCULATED:**native helper49 cycles observed (52 inclcaller),49..82
  general ratio0<=n<4d; restoring mean222.5375 from old traces, no rerender.
  Model accounts70,228,029 clocks, including13,500,972 address extras,
  560230untaken-jump clocks,4998482arithmetic/1142210transfer stalls.
- **CALCULATED three observed outputs:**lower7808/9106.5277/15721;
  best8035/9338.8336/16001; upperbest+12:8047/9350.8336/16013.
  Separate conservative valid-API CFG upper30123 =156+32*936+3+12.
  Bounds admit only privateinternal/zero-wait/residentstack/noDMA/noIRQ.
  Unconditional Circuit upper remains **UNRESOLVED**.
- **CONDITIONAL clock/rate comparison:**246MHz prior model,164000clocks
  at48k,163840 at48046.875Hz. Pooledone mean5.70%,worst9.77%,structural18.39%
  atconditionalrate. Ten-copy arithmetic mean57.00%,worst97.66%,structural183.86%
  before other work. Different rate-tagged case mixtures and matched six-pitch
  comparisons exported separately; no hardware audio/clock measurement.
- **CALCULATED hotspots:**long-X MOVE36.00%,short-X MOVE13.90%,Jcc13.10%,
  DIV8.46%,longimmMOVE7.96%. Nextcandidate:scratch/register/parallel scheduling;
  code unchanged. Largest unknown:normal stock headroom and memory/async effects.
  Previous9647-stock-opcode helper checkpoints remain context, not added cycles.
- **MEASURED reproducibility / preservation:**two full analysis runs byte-identical;
  manual-example/accounting/loop/AGU/rate/refusal checks pass conditional gatesA-I.
  Renderer/native/restoring sources and artifacts, oracle, original inputs and
  sealed core preserved. No CPU execution, host benchmark, hardware, firmware
  changes, stockRAM reservation, model switching, polyphony or P9DD integration.

New notes:plaits-cycle-audit.md, dsp56300-timing-model.md. Reusable static tools:
plaits/poc/timing/. Canonical evidence:builds/phase20a-timing/final/, repeat/,
checks/, rates/ and documentation/. Single next step:separately authorized
standalone scratch-traffic/register-scheduling optimization with unchanged
numeric contract and full regression+timing revalidation. Integration stays closed.

## 2026-10-06 — Phase 20A-DIV: exact native ratio qualification

- **SOURCE-DERIVED:** pinned DSP56300FM Rev5 pp13-52..54 specifies fractional
  nonrestoring DIV, full56 accumulator/24-bit signed divisor, sign-based MSP
  add/subtract, delayed quotient carry and C/V/stickyL effects. ROL p13-165
  rotates A1 only. Manual contradictory sixteen/24 and39/56 text retained as
  **UNRESOLVED editorial discrepancies**, not copied into decoding assumptions.
- **IMPLEMENTED:** separate18P guarded helper, integer-part reduction,21 DIVs,
  A0->A1 then ROL with finalcarry, no table/scratch writes; exactQ3.21 floor
  contract unchanged. Parallel moves confined to helper.22P candidate retained;
  restoring source/oracle/exes and original baseline hashes unchanged.
- **TESTED:**37,016 isolated cases repeated;777,126 DIV iterations/run match
  independent56-bit/C/V/L model and integer quotients. Small divisors exhaustive,
  signed24 extrema/rounding boundaries, seededrandom and both C inputs. Zero
  denominator returns0 without DIV. Initial wrong ROL ordering was rejected in
  isolated probes and corrected before substitution; probe evidence retained.
- **MEASURED:** preferred oscillator700P (−8),7 persistentX,44 allocatedscratch
  (43 live), controls3X/output32Y/LUT0; stackpeak3 entries (was5). Issued/block
  min4414,mean5138.436303,max8956;43.2442% mean reduction. Complete run
  38,641,041 opcodes;283,027 divider calls,32..80/block, all33 issued/call in
  oscillator suite; isolated generaldomain33..48. Helper mean cost−75.9168%.
- **TESTED:** unchanged43 cases/7520 blocks/240640 samples twice. All old/new/
  oracle outputs and seven-field block states exact; fullnative trace/files
  repeat. Controls/oracle/reference/metrics/pitch/rates hash-identical to baseline.
  Integer old/new maximum/RMSdifference0; spectrum1.0. Main assembly identical,
  machine prefix differs only in final jump relocation. All originalA–K gates,
  input/overwrite refusals, originalSYX/BIN roundtrip,10extract/183source/core
  and original20A source/artifact preservation checks pass.
- **MEASURED:** float-reference RMS.0219731, edge difference1.41453,
  spectrum>=.9999439621 and pitchmax.9991969cents unchanged.2048-block
  continuity and warmed reference64 vs32+32 pass. No changed oracle or hidden
  phase alignment. Conditional48046.875Hz remains comparison only.
- **UNRESOLVED:** DSP hardware cycles/clock/headroom, Circuit RAM/ABI/placement
  unchanged. At48k derived mean7.70765M/worst13.434M issued/sec perprimitive;
  multivoice extrapolation is an **ESTIMATE**, not an implementation or timing proof.
- **Next step:** offline instruction-cycle/pipeline audit of the unchanged native
  renderer's full traces. No new optimization/integration follows automatically.

Report:notes/plaits-native-div.md. Evidence:builds/phase20a-div/fixtures-compact/,
final-compact/, checks/, comparison/. New reusable adapters:plaits/poc/div/.
Offline standalone only; no device access, MIDI/SysEx, firmware/original changes,
stock allocation, model switching, polyphony or P9DD integration.

## 2026-10-06 — Phase 20A: standalone fixed-point VariableSaw implemented

- **SOURCE-DERIVED:** pinned eurorack08460a69.../stmlibe3bd7c9... exact six-header
  closure:VariableSaw,Oscillator(kMaxFrequency),stmlibdsp,parameter_interpolator,
  polyblep,stmlib. No Voice, RNG, LUT, allocator or linked pitch converter.
  Reference uses unchanged headers with upstream TEST host portability branch.
  All183 source hashes retained; no refetch/download or source edits.
- **IMPLEMENTED:** standalone assembly via existing assembler/sealed19A core;
  Q2.22 phase/frequency/PW, Q3.21 audio/shape/corrections, exact32-step integer
  ramps, two-sample step and integratedBLEP; algebraicf/PW+f/(1−PW) avoids large
  reciprocals. Table-free exact21-bit restoring ratio helper; no stock image or
  Circuit address/state reservation. Caller converts pitchHz/sampleRate.
- **MEASURED:** program708P words/2124bytes, divider26P included; persistent7X/
  0Y, scratch44X, controls3X, output32Y, logicaldata86; tables0. Hardware stack
  peak5 entries/10 words, restoreddepth0. Upstream hostsizeof28 bytes.
  Issued opcodes/32:min7632,max16844,mean9053.5811;68,082,930 perfullsuite.
  Real hardware cycles/budgetUNRESOLVED; host execution time is not target timing.
- **TESTED:**43 cases,7520 blocks,240640 samples/run, both fullDSP and float
  reference repeated. Eight native exports, including full136,165,860byte PC
  trace and outputs/states/write hashes, byte-identical. AllDSP samples and all
  case-final states exactlymatch independent integeroracle.2048 consecutive
  blocks preserve phase/delayed state; warmed reference64 vs32+32 difference0.
- **MEASURED differential:** worstRMS.0219731, maxDCdelta.0003377, peakdelta
  <.000931, constant magnitude-spectrum similarity>=.99994396. Max pointwise
  edge difference1.41453 under abruptstress retained; no time/phase realignment
  or subjective listening claim. Maximum tested pitch error.999197cents over
  MIDI0..120 at separate48k/conditional48046.875 rates; retune ratio1024/1025.
- **TESTED resource strategy:**65-word normalized reciprocal candidate math
  exported separately; maxsampled relativeerror6.0489e−5, oneNewton8.8835e−7.
  Not loaded/assembled into oscillator; LUT/Newton/nativeDIV costs remain
  qualified estimates or unresolved until a separate implementation.
- **TESTED guards:**zero badratio/narrowing saturation/address/peripheral/phase
  failures in bounded suite;32 ordered outputs/call. Zero frequency refused
  before execution; three overwrite refusals. OriginalSYX/BIN hashes/roundtrip,
  all10extracts,183upstream sources, sealed203-file core/harness/priorhelper
  guardsPASS. No firmware/hardware/MIDI/SysEx/stockP/stockRAM work.
- Report:notes/plaits-variablesaw-poc.md plus fixed-point/resource reports;
  implementation:plaits/poc/; verifier:emulator/tests/verify_variablesaw.py.
  Canonical:builds/phase20a-plaits/final/, core-final-v2/, checks/.
- **A–K gatesPASS within tested standalone scope.** RAM-ownership work FROZEN;
  no persistent Circuit allocation or firmware integration readiness. Desired
  monoSynth1/2/fourvoiceMIDI1/2 architecture/8controls retained, not implemented.
  Single next step: qualify native DSPDIV ratio helper and rerun unchanged
  differential/cost suite; no automatic integration or broader port.

## 2026-10-06 — Phase 19C-P204B: count latch and bounded producer exclusions

- **VERIFIED schema:** original203A reads35F; records360+5*k contain threeY
  pointers(R5/R6/R7), MAC coefficientX0, absoluteX destinationR4.2043 loads+4,
  2048 readsX:(R4),204B stores one unindexed word. Last iteration prefetches
  next four words;20 capacity is HYPOTHESIS only, not enforced normalN.
- **VERIFIED ISA/latch:**203A→X1,2040DO→24-bitLC;2045 overwritesX1 for
  arithmetic, notLC. Later35F stores alone affect future counts. Primary manual
  existing DSP56300FM printed5-21/13-56..58 retained with page/hash provenance;
  no source download. Record fetches lack whole-table snapshot/positive commit.
- **INIT-ONLY / NORMAL-PATH:** count0 from2788 clear andARM286E4; sourcecount20
  from27AE2→286DA belongs2FA+172*bank, not35F. No compiled fill/publish chain
  recovered. Private5E byte writes carryupper24zero, SERVICE-ONLY. GenericP19D
  nonzero value/effective count-table address remainsUNRESOLVED.
- **New BOUNDED-PROOF:** all direct1B89/1B7B caller domains, including nine
  wrapper sites/two banks (20 domains), exclude35F and360..3C3.1A99's3C4 is
  read viaR4/1B8C; output isR1/1B90. Full per-call address sets exported;
  recovered count20/linearM1/context premises explicit. No generic344 recensus.
- **VERIFIED necessary alias equations, not normal witnesses:** P19D needs
  X10=35F,X11Xspace andreceivedX0nonzero. Sole intervening scalar read r leaves
  r+2, so count precursorr35D. Existing19 reader edge candidates reused;
  six fixed arguments exclude that precursor. Service26AD4 is separate;
  variable/generic normal read/ordering closure not recovered.1F97 prior
  bounded initialized cursor proof retained, not replayed or globally promoted.
- **Result D / UNRESOLVED:** no normal positive publisher or defensive positive
  checkpoint. NormalN min/max, destination set, highX/target-cell/self collision
  allNOT-YET-DETERMINED. Do not choose always-zero from missing publisher.
  P204B remains high-X/target-bridge blocker; no P1E15 closure/recomputation,
  active-parent replayNO; persistent256-word reservationNO; no Plaits work.
- **TESTED PASS:**21 canonical reports repeat-identically;20 smoothing domains,
  160 nominal source-field stores, five fields,46 collision/scope checks,
  19 inherited read edges/six fixed exclusions, two preserved zero entries;
  33 prior checkpoint/FULLHELPER/PACKLINK evidence files hash-guarded; two
  overwrite refusals; original SYX/BIN hashes/codecroundtrip/all10extracts,
  sealed19A core/harness and helper sources intact.0 DSP/ARM instructions;
  no count/record seeds, firmware/user-file/hardware changes or asset analysis.
- Report:notes/dsp-p204b-provenance.md. Collector:tools/ct_p204b_provenance.py;
  verifier:emulator/tests/verify_p204b.py. Canonical evidence:
  builds/phase19c-p204b/final-v4/, final-v4-repeat/, checks-v4/.
- **Next:** targeted normalP19D saved-cursor/cache provenance to35F and compiled
  records, including variable/generic scalar-read arguments/order. Recover a
  genuine producer or exclusion before positive replay; no broad census/seeding.

## 2026-10-06 — Phase 19C-PACKLINK: scoped native correspondence recovered

- **VERIFIED installed source:** Components1.72.1 ASAR SHA25678e69be6909ecaf9...
  extracted read-only; retained manifest/integrity/source hashes. No app launched.
  Existing completed extraction/metadata discovery reused after interruption.
- **VERIFIED / SOURCE-DERIVED NORMAL-PATH:** Tracks N7 ZIP loader assigns member
  arraybuffer to samples[i].target.fileData. f0 setter stores binary unchanged;
  y0 creates64 immutable slotIndex values. sendEntitySet/S8 carries explicit
  destinationPackId and slotIndex, cloning raw bytes. Source witnesses export
  character+UTF8 offsets and hashes; no sample renderer invoked for ZIP imports.
- **VERIFIED ARM bridge:** wire PCM5→39570/3958A internal4→category2. Begin397C8
  records pack/slot; data3A34A→392FC inverse bit packing; raw writer36C94 resolves
  backend25D98. Header fields/L unchanged on successful transferred-header path.
  Missing fallback26610→3B0B4 formats `%02d` plus `_PCM.wav`; app Q4 later
  prefixes same index to sanitized sample filename.39E96→1F1C0 retains index.
  Name/copy worker36D82 uses raw4096-byte read/write chunks, no WAV codec.
- **VERIFIED missing behavior:** reset binary undefined; worker DELETE8; firmware
 39B0E→3CC34→worker5→36CCC→26680 clears entry/presence, unlinks, then2645E
  reindexes. Successful absent slots stay absent, not zero WAVs. ACTUAL-DATA:
  *New Pack1 missing38..63; MyPack_01 missing49..51,56..61 (35 total).
- **VERIFIED / qualification:** compareChecksum skips by CRC32+name or already
  absent status. Offline evidence cannot prove byte identity of reused native
  content. Full mapping requires completed identical native inputs and no foreign
  duplicate-index entries/edits. Small encoded tail at39320 additionally requires
  nontrapping SDIV state for completion; no authentic CPU state assumed.
- **ACTUAL-DATA identity:** all12 retain full archive hash/cache key/name/product/
  version; no embedded stable ID. Existing API metadata exactly matches remote
  IDs530016(MyPack_01),521732(*New Pack1); not native destination IDs. Historical
  log event at12447 associates DLR / Sofa Sound with destination23 in2024;
  sanitized export excludes telemetry identifiers. Current selected pack is
  **UNRESOLVED**; neither cache mtime nor that event establishes loader context.
- **DATASET-SPECIFIC / NORMAL ASSET EXCLUDED:** all12 conditional identical native
  mappings reuse768 exact arithmetic rows and all24,576 negative interval tests.
  No clipping/wrap; largest A64BF4400. No geometric→X/Y promotion; X11 retains
  STATE-DEPENDENT. Selected closure:NO; universal closure:NO. Scoped current-app
  UI time gate does not establish universal firmware acceptance/serialization.
- **VERIFIED evidence maintenance:** historical hash-manifest self-entry defect
  fixed in collectors; old exports preserved, explicit defect ledger and all
  other member checks retained. No firmware/core/user-file modifications.
- Final report: notes/dsp-pack-native-link.md. Canonical evidence:
  builds/phase19c-packlink/final-v2/, final-v2-repeat/, arm-final-v2/;
  focused reproducibility/preservation checks:checks-v2/.
- **TESTED / PASS:**12 canonical exports identical;17 exact source witnesses;
 733 real WAVs/68,013,066 bytes,266055 pure256-byte chunks and8677 pure8192-byte
  chunks;35 absent slots/768 exact numerical map rows;3 overwrite refusals.
  Thirteen short-tail cases retain nontrapping-SDIV completion caveat.21 existing
  user-source hash/size/mtime guards; original SYX/BIN identity/in-memory roundtrip,
  all10 extracts, sealed19A/prior helper source guards pass.0 CPU instructions,
  no Components execution or wire messages generated/transmitted.
- **STOP / next:** no further asset archaeology without new existing offline
  native/selection evidence. Single next independent obligation:P:0x204B normal
  positive-count/record destination provenance. Not analyzed here. Parent replay
  remainsNO; target bridge/X35F/RAM availability not promoted. No Plaits work.

## 2026-10-06 — Phase 19C-ASSETDATA:12 actual cached packs, no model overlaps

- **VERIFIED read-only coverage:** project/Documents/Downloads/Desktop and
  Components roaming/local roots,30,721 metadata files/24 ZIPs, zero canonical
  scan errors. Skip reparse/cloud/git/node_modules/venv/phase outputs; no full disk
  crawl. NonZIP/opaque containers remain uninspected. No standalone native PCM/
  NCS/NCM clues found. Initial Components read denial resolved by approved
  read-only access; no app/network/hardware/ACL changes.
- **ACTUAL-DATA VERIFIED:**12 ZIPs in Components Cache_Data have index.json
  product=circuit-tracks, version2.0,64 sample URL entries. Sources f_00008c,
  133,185,186,197,198,199,19a,19b,19c,19d,1d1. Real names/full hashes/paths/
  mtimes/member listing provenance in[dsp-asset-offline-data.md](dsp-asset-offline-data.md)
  and dataset-manifest.csv.52,223,108 bytes of original ZIP snapshots retained;
 1601 file members hashed/CRC-checked without decoding audio samples.
- **VERIFIED archive maps:**samples[i].url=samples/sample_i.wav for each0..63;
  unique members/URLs.10 packs contain64 WAVs; *New Pack1 missing38..63,
  MyPack_01 missing49..51/56..61, all absent positions have empty metadata names.
  Missing L stays blank, model advance256; no invented WAV/header or mixed packs.
  Associated genuine project_i.ncs members present in several archives; no
  native selected_SESSION.ncs/_META.ncm mapping inferred from cached filenames.
- **ACTUAL-DATA VERIFIED:**733 WAVs all stock-predicate accepted, complete
  declared file/data extents, fmt16/dataoffset44/format1/mono48kHz16-bit;
  L range1640..1454496. Exact per-file L/size/header/hash in wav-metadata.csv.
  Python wave independently confirms parameters/framecount×2 for all733.
- **DATASET-SPECIFIC GEOMETRIC:**12 independent64-record models,768 actual-data
  progressions, no E80000 clipping or24-bit wrap. A64 endpoints: Shawn7CA800,
  *New Pack1 998E00,Synthwave81F000,BlankFor.ms82CA00,Ali832100,
  Post Industrial7C8300,Peak828B00,Team Novation7F3B00,Factory6F4F00,
  Shadow Child6F9200,DLR6DCE00,MyPack_01 BF4400. Every combined main+padding
  interval[57FFFE,A64-2); all24576 requested target rows exclude cells.
  Exact page residues/main counts/padding intervals in actual-address-progression.csv.
- **UNRESOLVED applicability:**sample_i.wav native filename parser returnsFF;
  archive indices come actual index.json, not forced native parsing. Selected
  native pack and slot/content preservation not established. Archive-model
  geometry is closed for unchanged datasets under that correspondence, not an
  actual-device trace or universal normal host-preservation proof. X11 remains
  STATE-DEPENDENT; no X/Y-write claim. Other host order/ancestry,204B and DSP
  aliases remain separate. Parent replayNO, bridge unchanged,0 new CPU ops.
- **VERIFIED reproducibility/protection:**25 recursively counted files repeat
  identically;733 independent actual headers,768 instruction-loop arithmetic,
 24576 interval checks, overwrite refusal,1273 candidate source hashes/sizes/mtimes
  unchanged; original firmware/roundtrip/all10 extracts/sealed19A/priorhelper checksPASS.
  Canonical builds/phase19c-assetdata/final/,final-repeat/,checks/; discovery-v2
  reuses source ZIP snapshots from discovery/archives/. No user-file modification.
- **Next:** identify selected pack and archive-to-native correspondence using
  existing offline selection/import metadata; no replacements or hardware exports.
  Blanket absence-of-source-data stopping condition is superseded, missing
  applicability remains. Optional text clarification requested, no selection seeded.

Reproduce: pinned Python `tools/ct_assetdata_analyze.py --discovery-dir
builds/phase19c-assetdata/discovery-v2 --output-dir builds/phase19c-assetdata/new-analysis`,
then a separate new-repeat; `emulator/tests/verify_assetdata.py --discovery-dir
builds/phase19c-assetdata/discovery-v2 --first builds/phase19c-assetdata/new-analysis
--repeat builds/phase19c-assetdata/new-repeat --output-dir builds/phase19c-assetdata/new-checks
--verify-original-sources`. Discovery roots/limits are in the report and
tools/ct_assetdata_discover.py. No downloads/installations/device operations.

## 2026-10-06 — Phase 19C-BACKENDBOUND: concrete backend, normal data stop

- **VERIFIED correction:**36AF0 literal37268 resolves20003730;36AF6 loads
  backend20003738. Literal37264=20006914 is the separate selection-container
  slot. Earlier ASSETBOUND's20006914+8 attribution was incorrect; original
  exports preserved, page/chunk/padding algebra unchanged.
- **VERIFIED:** complete26610..667C signatureC,B,category,index,stackflags.
  Stock367DA flags0/type4→category2; missing lookup returns12; present path
  invokesB.vtable+0, final status1 returns1/otherwise0. No category guard inside;
  index guard/presence comes3B084→1A9F6→5C24A→48EB0. Flags1 fallback is
  not stock asset mode. It returns status, not a newly allocated source object.
- **INIT-ONLY VERIFIED:** initialized type map3730 type4byte=2. Descriptor
  805A4F8 category2capacity64,labelPCM,suffix_PCM.wav.263F8 creates5 categories
  (caps64/16/64/2/2);3ADF0 allocates8-byte presence map and64×40-byte names
  forcategory2.3AE34 clears/rebuilds map fromdirectory; accepted index<capacity.
  1F1C0 accepts2/3decimaldigits+underscore, truncatesindexto8bits; duplicates/
  aliases can overwrite indexed names. No lengths stored in these name records.
- **VERIFIED graph/lifecycle:**1F0F0 allocates90-byteB,25C98 assigns805B150,
  file storage0x1028=4136bytes, activeptr0/openflag0;1F11E publishes20003738.
  1F162/1F166 publishes40-byteplain selection container at20006914, distinct
  fromB. B open25CB8/close25D10/read25D4C/seek25E08/size25E1C/path5C274.
- **VERIFIED extent contract:** mode13open retainslow6flags at19AF4/19C04;
  directory-record+1C→file+C size at19BE0..BE8.19CC6 initializescount0,
  checksobject/error/readflag, then clampscount tosize-position19CF6..9D02.
  Prefixcopy19DF4..E0E leavesdestinationtailuntouched.25D4C ignoresseekstatus;
  1A14C..158 clampsbeyondEOFonlywithwritebit1clear;mode13keepsbit1,seekmay
  allocate/growextent1A1CE..1DA/1A20A..21A. No storage operations executed.
- **VERIFIED failure behavior:**36B08 shortcount→status4; loader49ABE/49B36
  ignoresstatus. Header64bytes clearedbeforeeachread; nocopyfailure leaveszero,
  partialprefix canstillpasspredicate. Mainbuffersnotclearedperread; retained
  suffixdataunknown. No headerL/filesize or aggregate64 check in recoveredchain.
  **UNRESOLVED NORMAL-PATH:** upstreamimportvalidation/storage/actualfiles.
- **VERIFIED X11 slice:**297D6 tails1EB1E storeAAAA to40003000, noSHIsetup.
  Width20xx updatesX12/HCSRonly;page171..178retainsX11. EndC03suffixstorescacheC04;
  final802CmisspublishesprivateYflag atDSP185. **Conditional Y** forserialized
  laterrecords;firstspaceunknown/foreignhostwaitorderingunclosed, overall
  **STATE-DEPENDENT**, no actualnormalX-overlapwitness.
- **EXCLUDED local:** main/allfirsttwo padding results unchanged.64 unseeded
  source/progressionrows/256criticalpagechecks:8 first-twoexclusions,248normal
  UNRESOLVED. No strongernormalaggregatebound, no invented64sequence.
  Requestedselector/table/descriptor0assetcontributionsUNRESOLVED;familyNOTCLOSED.
- **UNRESOLVED ancestry:**3CC46 selection/loadtransitioncandidate through
  30CBC/30E10;5BFD0INITpointerpublicationdoesnotproveboot/runtimeentryclass.
  No wholeproject/sessionformat analysis or genericaliases.
- **STOP applied:** no actualsourceassets available. Needexistingoffline selected
  container PCM directory withactualindexednames/order/missingentries/sizes/
  completeheaders; fullfilesforreadconsistency;selectionassociation and relevant
  existing_SESSION.ncs/_META.ncm/pathmetadata. Backing-volumegeometry/imageonly
  ifclaimingpartitionbudget. No hardware export/transmission requested.
- **VERIFIED validation:**12 repeat-identical canonicalfiles,8 contracttests,
  overwrite refusal,expectedSYX/BIN/roundtrip/all10extracts/sealed19A/priorhelper
  checksPASS;0CPUops. Canonicalbuilds/phase19c-backendbound/final-v3/,checks-v3/,
  probe-canonical/. Detailedmap:dataflow/roles/premises in
  [dsp-asset-backend-bounds.md](dsp-asset-backend-bounds.md).
- **Next:** obtainexistingoffline sourcefiles andcomputeactualcumulativeaddresses.
  Keepotherhostcache/order/ancestry,204B,DSPindirectwritersindependent;
  targetbridgeunchanged,parentreplayNO.

Reproduce with pinned Python: `tools/ct_backend_probe.py --output-dir
builds/phase19c-backendbound/new-probe`; `tools/ct_backend_bounds.py --probe-dir
builds/phase19c-backendbound/new-probe --output-dir builds/phase19c-backendbound/new-audit`
and new-repeat; `emulator/tests/verify_backend_bounds.py --probe-dir
builds/phase19c-backendbound/new-probe --first builds/phase19c-backendbound/new-audit
--repeat builds/phase19c-backendbound/new-repeat --output-dir
builds/phase19c-backendbound/new-checks`. Fresh confined outputs; no installations.

## 2026-10-06 — Phase 19C-ASSETBOUND: predicate envelope and padding aliases

- **VERIFIED:** completing49A1C path calls49A80 exactly64 times, indices0..63;
  initial3676C==1 refuses before the loop. Per-record selector(4,i,FF), reused
  cleared64-byte header at2000665C. Object20000A7C callbacks are not a static
  64-length table. Original initialized vtable805B9EC and callback805BFCD at
  20000A8C are **INIT-ONLY values**, not proof of actual normal/boot execution.
- **VERIFIED source slice:**49ABE→3CBD6→3CA52 submits opcode6; worker22AE4's
  table22B28 case6 targets22BBE→36A7E; type4 selects via367DA→26610, then
  calls backend20006914+8 vtable+10 at36B02.36B08 checks read count but the
  loader ignores3CBD6 status at49ABE/49B36. Backend normal data/limits unresolved.
- **VERIFIED:** exact51BA0 predicate comparesRIFF/WAVE/fmt-space/data;
  q=u32(p+10), data headerp+14+q, L=u32(p+18+q). Literal51C0C=0124F801;
  unsigned51BEA excludesL>=19,200,001. Other fields:p+16 u16=1,p+18 u32=48000,
  p+22 u16=16. No local q bounds, format tag/RIFF size/file length/read-success
  or aggregate64 limit. Normal valid assets versus malformed/external policy
  remains **UNRESOLVED**, as does all-foreign header-buffer mutation exclusion.
- **VERIFIED stable-header envelope:**q_i=floor(L_i/512)0..37500 for valid,
  zero for invalid; R8=256*(1+q_i), max927D00. A_i=580000+256*i+256*sum(q_j,j<i).
  A64 range584000..24F74000; no32-bit overflow, no early24-bit truncation.
  Actual64 L values remain absent; no record metadata seeded or invented.
- **VERIFIED:** every49AD0 directly calls294AC; scalar-address cache cannot
  suppress the fresh page header. S=((A&FFFF00)-2)mod2^24. Record0 one page,
  record1 37501 pages; each later predicate-envelope record permits all65536
  pages. Pages repeat for aligned A differences multiple1000000. Actual normal
  repeats/intersections require stronger source domain and retainedX11 space.
- **VERIFIED:** main chunk<=800 bytes,1024 DSP16-bit words, tail0/256/512/768;
  strict virtual end<E80000 before send. Clipped N is distinct from returnedR8.
  Main low requested targets **EXCLUDED** for all64 transactions in the local
  ordered/framed model. Smaller length partial tail can emit more than maxL
  after chunk clipping; canonical final-v2 corrects initial intermediate N_max.
- **VERIFIED:** unconditional256-word padding49B94 has no fresh address/guard.
  First two records exclude all requested cells locally. Later padding is
  **PROJECT-DATA DEPENDENT**: page0 wraps exactly[FFFFFE,1000000)+[0,FE),
  hittingEB/F3/FB but not103; page100 hits remaining descriptor0 cells; pages
  900/A00 coverselectors95A..95F and table[9DB,A12). These are predicate-domain
  alternatives, not normal observed writes. Page write retainsX11 X/Y selection.
- **UNRESOLVED ancestry:**3CC46 through3CC44 has selection/load-transition
  predecessors30CBC/30E10; exact normal project/session/patch classification
  open.5BFD0 callback initialization value known, runtime ancestry open. Raw
  pointer match5C628 lies in compressed source, not an executable call edge.
- **UNRESOLVED conclusion:** asset host-mutation family NOT CLOSED; requested
  cell asset classifications PROJECT-DATA DEPENDENT, actual normalX writable
  unknown. Other host cache/order/transition paths,204B and DSP indirect writes
  stay independent. No target-bridge recomputation or active-parent replay.
- **VERIFIED artifacts/checks:**64 symbolic record/progression rows,128 interval
  rows,2048 target tests (992 predicate-possible,1056 exclusions);11 canonical
  files identical across repeats,9 arithmetic tests, overwrite refusal and
  original SYX/BIN/roundtrip/all10 extracts/sealed19A/prior fullhelper checksPASS.
  Zero CPU instructions, offline only. Details and exact instruction witnesses:
  [dsp-asset-loader-bounds.md](dsp-asset-loader-bounds.md), canonical
  builds/phase19c-assetbound/final-v2/,checks-v2/,probe-canonical/.
- **Single best next step:**26610/backend20006914+8 accepted normal aggregate
  length validation, then retainedX11 space before claiming normalX intersections.
  If constraints require absent asset files, obtain offline data rather than seed.

Reproduce with pinned Python:
`tools/ct_asset_probe.py --output-dir builds/phase19c-assetbound/new-probe`,
then `tools/ct_asset_bounds.py --probe-dir builds/phase19c-assetbound/new-probe
--output-dir builds/phase19c-assetbound/new-audit` and a separate new-repeat;
`emulator/tests/verify_asset_bounds.py --probe-dir builds/phase19c-assetbound/new-probe
--first builds/phase19c-assetbound/new-audit --repeat builds/phase19c-assetbound/new-repeat
--output-dir builds/phase19c-assetbound/new-checks`. All output paths exclusive.

## 2026-10-06 — Phase 19C-HOSTWRITE: INIT cache recovered, normal domains open

- **VERIFIED INIT-ONLY:** ARM walker5B590 processes[5B7B4,5B7D8). Record
  5B7C4 invokes596C4 codec, source[5C3C4,5CDDA),2582 bytes;574 records expand
  to[20000000,20003D02),15618 bytes. Cache20003D00/01 equalsFFFF. Decode hash
  2db584abde65123402067c89720f5a10e12c40650b700d6af2f13ed93743e04f.
  No bytes in[3D02,3D04) or actual boot state invented; evidence-only file.
- **VERIFIED local cache:**29306/2932A compare full requestedR6 to cached
  halfword; hit skips setup;29340 publishesrequested+1 low16.2942C/29488
  update table cursors;295A4 bulk-read invalidatesFFFF. Scalar/extended reads,
  address/width/bulk-write wrappers have no explicit corresponding invalidation.
  No separate port/width/generation tag; cross-context coherence UNRESOLVED.
- **VERIFIED DSP protocol:** private185/186 updatesX11/X10; extended17D and
  page175 write forms retainX11.190/19E/1AC advance/publishX10.19D one X store
  per data word,19B forY. Scalar-read address/prefetch plus read-next leavesa+2.
  Canonical direct writers checked;231B is proved RLE data,199 is JCLR read.
  Foreign cursor aliases independent; no new DSP alias census/204B analysis.
- **VERIFIED targeted inventory:**323 direct edge candidates after DSP-stream
  data exclusion, not a complete actual NORMAL graph.1500 nominal scalar rows
  have zero requested-cell intersections. Parameter unique456X/374Y, extra
  specialY111; maximumX959. Sparse+7 event publication excludesdescriptor+0.
  Helper51B54 usesr0&3 tobound9F..A2 and99..9C. Effective cache-hit domains open.
- **VERIFIED separation:** extended per-word29314 direct caller26A76 belongs
  to recovered5E SERVICE-ONLY. Bulk16-bit paths separate. Correctly framed data
  count bytes/width,24-bit wrap and whole intervals tested; value width does
  not supply destination safety. Reviewed staging nineC00..D00 records and
  E7FFFE..E93A06 selected stream exclude requested cells under retained premises.
- **VERIFIED asset bound obligation:**49A1C starts580000, with callers3CC46
  and5BFD0;64 entries.49C34→51B80 supplies metadata lengthL;R8=256+
  ((L&FFFFFE00)>>1) for valid header.49A6A advances next address byR8;
  page usesbits23:8. Main chunks<=2048bytes are checked before emission;
  49B94 adds256 padding words without new address or that guard. Returned
  advance is not the clipped emitted count. No normal total/page-wrap bound
  proved and no fabricated file-length/cursor state or target-producing witness.
- **UNRESOLVED:** all-normal effective host preservation, call/transition
  ancestry, cache-hit order/port/width and asset progression. All requested
  ranges and14 descriptor0 words NOT-YET-DETERMINED. No target-bridge recompute,
  no real1E15 state, no active-parent replay.204B independently retained.
- **TESTED:**19 final-v3 exports identical,10 tests/overwrite refusal; original
  SYX/BIN/all10 extracts/codec/core203/19A harness/prior-helper hashes intact.
  0 ARM/DSP CPU instructions. Existing local Capstone5.0.7 read-only access
  approved outside sandbox; no install/network/hardware/packets/firmware changes.

Report/commands: [dsp-host-write-provenance.md](dsp-host-write-provenance.md).
Tools ct_hostwrite_probe.py, ct_arm_init_cache.py, ct_hostwrite_audit.py;
tests test_hostwrite.py/verify_hostwrite.py. Evidence builds/phase19c-hostwrite/
probe-final/, final-v3/, final-v3-repeat/, checks-v3/reproducibility.json.
**Next:** normal metadata length/total advance49C34→51B80→R8→49A6A, including
page truncation and padding; cache ordering/204B remain independent.

## 2026-10-06 — Phase 19C-TARGETBRIDGE: conditional targets, unresolved production

- **VERIFIED:** exact D87..DB6 row/index/target data flow; table copy
  P[29F6,2A2D)→X[9DB,A12),55 words. Table-valid selector requirements0..7
  and0..14 are not proved normal masks/domains. No selector values seeded.
- **VERIFIED wrapper correction/detail:** DDC copy loop endsDE5 and falls
  throughDE6→DEC; DCF's JSRDDC reaches that algorithm call before its clear
  path; DD3 reachesDEC through JSRDE6. Six initialized wrapper entry targets;
  DC5/DCD wrappers are absent from all valid initialized rows. Extra wrapper
  JSRs require accounting in any future parent stack qualification.
- **VERIFIED conditional enumeration:**40 row/stage lookups plus600 algorithm
  lookups=640 records. Algorithm target setE19/E1C/E23/E31/E3B/E3D/E44/E4B/
  E54/E6F/E78. No1E15 and no required1E14 marker. This is not an actual
  normal reachable-state set; normal_domains/normal_targets remain null.
- **VERIFIED recovered producers:** INIT2788 zeros selectors and table;
  INIT29F3 supplies original target words; INIT descriptors supply12×281,
  202B,1A2B. No canonical direct absolute X/L store targets the requested
  cells. Existing561-operand census reprojected narrowly, not regenerated
  broadly.308 unclosed address envelopes are not308 real normal aliases.
- **VERIFIED recovered host exclusions:** finite parameter maximumX959;
  exact parameter/deferred/suffix cells and reviewed mailbox/stream domains
  exclude requested selectors/table/descriptor0 under their premises. Event
  descriptor+7 writes do not become +0 overlaps.16-bit data low8bits0 excludes
  direct raw1E14/1E15 publication only, not selector corruption.
- **VERIFIED SERVICE-ONLY capability:**5E private zero writes can change the
  copied table; no operation performed. **UNRESOLVED table classification**:
  normal mutation/retention not closed, so no IMMUTABLE or SERVICE-ONLY MUTABLE
  classification claimed. No normal patch/UI/effect-type target publisher found.
- **UNRESOLVED bridge C:** all six normal1E15 site decisions remain
  NOT-YET-DETERMINED, including DC5/DCD despite their conditional row exclusion.
  Descriptor19AC also unresolved. No exact normal target-producing state, sole
  remaining producer or justified active-parent replay.19D and204B plus generic
  contexts are independent obligations.0 DSP instructions/no checkpoint.
- **TESTED:**16 final-v2 exports byte-identical to repeat;7 boundary/routing/
  representation/original-table tests and overwrite refusal pass. OriginalSYX/BIN,
  all10 extracts, codec roundtrip, sealed203-file core/19A harness and prior
  FULLHELPER implementation remain intact. No hardware/packets, ROM search,
  firmware change, large install or Plaits work.

Reproduction: tools/ct_effect_target_bridge.py --output-dir fresh child of
builds/phase19c-targetbridge/; emulator/tests/test_target_bridge.py and
verify_target_bridge.py. Exact commands/report:
[dsp-effect-target-bridge.md](dsp-effect-target-bridge.md), canonical final-v2/,
final-v2-repeat/, checks-v2/reproducibility.json. **Next:** close normal ARM
scalar/width/bulk endpoint and cursor-retention provenance intoP19D for these
exact cells; preserve independent204B and generic-context obligations.

## 2026-10-06 — Phase 19C-PARENT: target bridge remains unproved

- **VERIFIED:** original parent P[1E15,1F11),167 decoded instruction sites,
  RTS1F10; direct JSRs1E19→1FB2,1E80→1F5C,1EE3→1F13,1EE5→1F5C.
  Ten DOs, no REP/explicit stack or modifier-register operations/direct I/O.
  No decoded external direct transfer to the parent; preceding1E14 is RTS.
- **VERIFIED local guard relation:** X7C&0C=0 selects family A then B;
  masked4/8/C bypass A and converge on B, conditioned on finite loops/returns.
  Actual guard value remains SYMBOLIC; no zero-default snapshot.
- **VERIFIED conditional predecessor constraint:** normal-role chain D99
  DO#5 surrounds DAE→DB2→DB6→algorithm-wrapper calls. If they selected1E15,
  helper entry inherits LF1/LA=DAF/LC1..5. Parent-local loops do not surround
  the helper sites. This class is outside FULLHELPER's tested LF0 class.
  Actual depth/frame history/FV remain UNRESOLVED; no compatibility forced.
- **VERIFIED retained target exclusion:** original55-word P29F6..2A2C
  table, copied29EC..29F4 toX9DB..A11, valid selectors and marker+1 targets
  exclude1E15. INIT descriptors contain12×281,202B,1A2B, also excluding it.
  **UNRESOLVED:** normal selector/index/target-table and descriptor retention.
  These are conditional exclusions, not a dead-code or universal normal proof.
- **VERIFIED local provenance:** parent immediate publications establish
  familyA1800/1840/18E0 at1E76/7A/7E, familyB19F0/1A30/1AD0 at1ED9/DD/E1.
  INITX38=50/Y15=1 and140..149 publish X3A32/X3B16; normal call1F1 refreshes
  counts before effect dispatch. INIT260A..261F establishes both cursor tables.
  All foreign/async retention obligations remain separate and UNRESOLVED.
- **TESTED:**13 final-v3 static exports match independent repeat;7 unit
  tests/2 CLI refusal gates and firmware/extract/codec/sealed-core/prior-helper
  guards pass. **0 parent and0 helper instructions this phase.** No actual
  normal checkpoint or bus trace; empty watches mean NOT EXECUTED.
- **UNRESOLVED:** actual normal parent high-X and35F read/write behavior;
  X35F invariant remains NOT-YET-DETERMINED. No positive count writer, natural
  parent→203A link, persistent allocation or firmware readiness established.
- User stop condition16 applied. No invented normal target/stack state, ROM
  search, scheduler replay, hardware, MIDI/SysEx, firmware changes or Plaits.
  **Next:** targeted producer/preservation proof for X95A..95F and copied
  X9DB..A11, proving a parent edge or excluding that predecessor.

Commands and exact evidence: [dsp-parent-replay.md](dsp-parent-replay.md),
emulator/harness/parent/audit.py, emulator/tests/test_parent_gate.py,
emulator/tests/verify_parent.py; builds/phase19c-parent/final-v3/,
final-v3-repeat/, checks-v3/reproducibility.json. Manuals/core reused locally.

2026-10-05 (Europe/Moscow). Static analysis only. No hardware communication,
MIDI/SysEx transmission, device-memory access, flashing or firmware patching.
All original inputs and `notes/baseline.txt` were preserved. New notes and
offline derived artifacts were created. VERIFIED below denotes static evidence,
not a hardware observation.

## Baseline

**VERIFIED:** initial complete tree contained seven directories (`original`,
`firmware`, `tools`, `notes`, `ghidra`, `plaits`, `builds`) and exactly four files:
the original SYX, existing BIN, `ct_fw_tool.py`, and `baseline.txt`. No project
AGENTS.md was found in the checked project/ancestor locations.

Read the complete utility and baseline notes. The utility reconstructs the
first 32 firmware bytes from UPDATE_FINISH and the remaining bytes from
UPDATE_WRITE. Its non-reflected CRC uses polynomial 0x04C11DB7 and initial
0xFFFFFFFF. Its build routine pads the final chunk with FF and preserves the
template INIT/header fields. Original tool was not edited.

**VERIFIED:**

| Check | Result |
|---|---|
| SYX bytes | 432961 |
| SYX SHA256 | bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd |
| BIN bytes | 314844 / 0x4CDDC |
| BIN SHA256 | b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da |
| Expected hash comparison | both match |
| Decoded SYX versus existing BIN | byte-for-byte equal |
| SYX -> BIN -> SYX in-memory roundtrip | byte-for-byte equal |
| Rebuilt SYX SHA256 | identical to original SYX hash |
| CRC | 0x4E74DA9E |
| WRITE messages | 9838 |
| Target field | 0x64, utility labels Circuit Tracks |
| INIT / HEADER version fields | both numeric 1394 |

The user-supplied marketing firmware version 1.2.1 is **UNRESOLVED** from these
numeric version fields alone. Build 4486 is supported by the embedded identifier
`GB1.1.5143.4486`; no alternate interpretation of its other components is assumed.

Reproduction: `ct_fw_tool.py roundtrip` without output, and `ct_static.py baseline`.
Evidence: `builds/baseline.json` and `builds/repro/baseline.json`.

## Tools and method

**VERIFIED:** PATH did not expose Python, Ghidra, analyzeHeadless or ARM objdump.
Bundled Python was located through the desktop runtime dependency inventory.
No accessible Ghidra was found in additional checked tool locations; Java alone
was present. This is not a claim that no installation exists anywhere on disk.

Capstone 5.0.9 (1.3 MB wheel) was installed into `builds/python-deps` after
approval for network access. The first sandboxed pip attempt failed with WinError
10013; the approved project-local install succeeded. Capstone's installed files
were inaccessible to the sandbox, so static disassembly ran with approved access
outside it. No large external tools were installed.

Reusable offline scripts now provide baseline checks, vector/string survey,
Thumb disassembly, cross-reference candidates, protected extraction, initialized
data reconstruction, reviewed call/vector summaries, and verification.
`tools/run_recon.ps1` reproduces them into a fresh directory without installation
or hardware operations. Capstone modes are Thumb, little-endian and M-class.

## Vector and string reconnaissance

**VERIFIED:** base 0x08010000 gives exclusive end 0x0805CDDC, MSP 0x20050000,
reset vector 0x0805C00D and reset code 0x0805C00C. The 114-entry table ends at
0x1C8, then metadata replaces handler-like values. The STM32F745 reference
layout corroborates the extent and reserved slots. All 105 nonzero handlers
are Thumb addresses in the image. Of external entries, 76 are four-byte
self-loop defaults, 19 are other handlers and 3 are zero. Core entries add
10 nonzero and 5 reserved zeros. Complete addresses are in the firmware map
and machine-readable survey/evidence reports.

**VERIFIED:** all supplied strings occur at the supplied addresses. Both DSP
messages include LF followed by NUL. A second build string is at 0x0801D790.
The ASCII scanner finds 3298 runs, including incidental text and the metadata
prefix `d` preceding the string at 0x080101CE. Useful file-name/sample-memory
strings and their addresses are recorded in the firmware map.

**VERIFIED:** reset veneer, FPU setup and part of the runtime startup path were
reviewed. Direct source/call targets are recorded in the map; function labels
are analyst names. There is no full recovery of all program functions.

## DSP-labelled upload path

**VERIFIED:** exact pointer, literal-load and MOVW/MOVT searches do not locate
the supplied message addresses. ADR-aware scanning finds references at
0x0801F560 and 0x0801F56C inside 0x0801F554. The function emits the messages
around its call to 0x08029260 at 0x0801F568 with selection zero. Its dispatcher
0x0801F51E uses selection zero for mode zero and selection one for mode one.
The application path 0x0801D4B0 passes a zeroed mode at 0x0801D582.

**VERIFIED:** uploader 0x08029260 resets/control-sequences the interface, sends
a bootstrap to channel zero, sends one selected stream to each of two channels,
then waits on the channel-zero input. Selection zero additionally invokes
numeric table initialization through 0x08029492. The pointer table and transfer
algorithm establish exact source ranges, rather than entropy-based guesses.
All discovered functions, call sites, polling and data ranges are in the map.

**VERIFIED:** sender 0x08029200 derives count from header bytes 1/2, adds two
words, sends `(count+2)*3` bytes in at most 170-word chunks, and waits between
chunks. The flash bytes are passed directly to the transport: no ARM-side DSP
decompression is present in this reviewed path.

**VERIFIED:** five streams were extracted without padding or source changes.
All start with count/load-address headers; all load addresses are zero:

| Stream | Offset | Bytes including header | Payload words |
|---|---|---:|---:|
| bootstrap | 0x196E0 | 30 | 8 |
| selection0-channel0 | 0x1F0 | 32544 | 10846 |
| selection0-channel1 | 0x8110 | 1098 | 364 |
| selection1-channel0 | 0x44EFC | 2430 | 808 |
| selection1-channel1 | 0x4587C | 1086 | 360 |

Outputs: `firmware/dsp/build-4486/`, with header-inclusive `.boot24.bin`,
payload-only `.payload24.bin`, addressed `.words.txt` and `manifest.json`.
The manifest records every stream/payload SHA256 and its source range.
The format corresponds to NXP DSP56724 SHI boot documentation (linked in the
firmware map). Actual silicon identity and DSP memory layout remain unproven.

## Transport and reconstructed initialized data

**VERIFIED:** the reviewed transport is SPI with DMA for bulk transfer and a
polling byte-transfer routine for 24-bit commands. Its polling routine accesses
status at peripheral +8 and data at +0xC, with TX/RX readiness bits 1/0.
The DMA routine writes memory pointer/count and enables the stream.

**VERIFIED by static translation:** ARM startup data, separate from DSP streams,
are compressed. Decompressor 0x080596C4 consumes the 2582-byte source at
0x0805C3C4, using literal runs and backward byte references. The output is
15618 bytes at conceptual address 0x20000000, ending at 0x20003D02. There is a
two-byte gap before the zero-init region at 0x20003D04; it is not silently filled.
The derived output hash is
`2db584abde65123402067c89720f5a10e12c40650b700d6af2f13ed93743e04f`.
It is an offline reconstructed data view, not observed device memory.

**VERIFIED:** following the code's transport pointer offsets through this view
identifies SPI2 (0x40003800), DMA1 stream 3 RX (0x40026058), DMA1 stream 4 TX
(0x40026070), both targeting SPI2 DR at 0x4000380C. IRQ handlers for those
streams reference the same transport object 0x2000016C. The pointer chain and
configuration addresses are reproduced by `ct_data_decode.py` and documented
in the firmware map. Static channel GPIO selectors are PD9/PD8, auxiliary
outputs PD0/PD1, and input lines PD7/PD4. Physical wiring is not established.

**VERIFIED:** post-upload functions send 512 values beginning at 0x2000,
512 at 0x2200 and 832 flash-sourced values at 0x1600. Their algorithmic role
and DSP memory-space interpretation remain **UNRESOLVED**.

## Hypotheses and limits

- **HYPOTHESIS:** the DSP belongs to DSP56724/56725 or a compatible DSP56300
  family; 24-bit boot format, two channel groups and SPI fit that family.
- **HYPOTHESIS:** channels zero/one correspond to its two cores or SHI ports.
- **HYPOTHESIS:** the large normal-selection payload implements synthesis;
  the small alternative pair may support another operating mode.
- **UNRESOLVED:** exact MCU/DSP models, complete UI/sequencer/audio partition,
  stock Nova synthesis ownership, voice algorithms, audio interfaces and Plaits
  feasibility. A DSP-labelled upload is proven; synth-on-DSP is not yet proven.
- **UNRESOLVED:** remaining computed/indirect references and DSP-internal
  code/data loading. Linear sweep outputs are not automatically code evidence.

## Verification and final state

**VERIFIED:** the complete workflow ran again into `builds/repro`. Original
and repeated extraction manifests and stream bytes match exactly; all extracted
streams match their source ranges. Re-encoding word listings reproduces payload
bytes. Initialized data reconstruction is repeatable. `ct_verify.py` passed
hashes, roundtrip, vector bounds, ADR sites, all five extracted ranges/hashes,
SPI2/DMA pointer chains, malformed-back-reference rejection, overwrite refusal,
and protection of `original/`.

Reproduction command:

```powershell
$py = 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& ./tools/run_recon.ps1 -Python $py -OutputDirectory './builds/fresh-run'
& $py -B tools/ct_verify.py --reports builds/fresh-run --dsp firmware/dsp/build-4486
```

No source inputs were overwritten. No work in `plaits/` began.
Single best next step: static DSP56300-family disassembly of the normal-selection
channel-zero payload, validating entry/vectors before tracing its host-command
dispatcher toward voice/sample processing.

## Created-file inventory

- Notes: `research-log.md`, `firmware-map.md`, `todo.md` under `notes/`.
- Tools: `ct_static.py`, `ct_dsp_extract.py`, `ct_data_decode.py`,
  `ct_evidence.py`, `ct_verify.py`, `run_recon.ps1`, `requirements-static.txt`,
  `README.md` under `tools/`. Existing `ct_fw_tool.py` was unchanged.
- Ghidra status/import guidance: `ghidra/README.md`.
- DSP extraction: 15 stream/payload/word-list files and one manifest under
  `firmware/dsp/build-4486/`.
- Canonical repeatable baseline, survey, cross-references, bounded disassembly,
  reconstructed initialized data, call/vector evidence, and repeated DSP files
  under `builds/repro/`. Earlier exploratory reports remain under `builds/`.
- Project-local Capstone dependency under `builds/python-deps/`.

Final verification also compared survey and bounded call/vector evidence from
the first and repeated runs: both were identical. Final SHA256 checks on the
original SYX and existing BIN still matched the expected hashes.

## Phase 3 — DSP reconstruction and host command analysis

2026-10-05. All work remained offline/static. No USB/MIDI, SysEx transmission,
flashing, firmware patching or Plaits work. Original files and the phase-2 DSP
extractions were preserved. Full findings: `dsp-memory-map.md` and
`dsp-command-map.md`.

**VERIFIED:** every extracted stream contains exactly one SHI count/address/data
record, not a typed sequence of invented nested records. Large selection0/channel0
has 10848 total words, including two header words and 10846 payload words.
All five loads start at zero. Program-entry branches are normal channel0 P:0x100,
normal channel1 P:0x100, alternative channel0 P:0x17F, alternative channel1
P:0x100. Bootstrap modifies OMR then branches to P:0xFFFFFE.

**VERIFIED:** executable DSP56300-family instruction encoding was corroborated
with NXP APR30 examples before disassembly. No local DSP decoder was found in
the checked locations. Rust 1.98.0 already existed. Two source repositories
were downloaded with approved network access; no large toolchain was installed.
The selected MIT-licensed Rust decoder commit is
`c60aeedb6a6014850204c71e53bc0cf5b3104222`. Only core/disassembler libraries
and a local adapter were compiled, without dependency downloads or firmware
execution. 135 decoder and 61 disassembler tests passed. A separate published
opcode fixture passed. Source revisions and audit/build instructions are in
`tools/PHASE3.md`.

**VERIFIED:** P:0x44 -> P:0x156 is the normal SHI receive path. It reads
X:0xFFFF94, qualifies traffic using GPIO bit 8, dispatches command bits beginning
at P:0x161 and returns via RTI at P:0x1B3. The implemented protocol performs
X/Y addressed writes, reads/read-next, paged/extended address setup and control
mailbox writes. No dedicated note opcode namespace is present in that ISR.
All reviewed direct branch targets lie on decoded boundaries inside the ISR.

**VERIFIED:** control `20 01 00` enters 16-bit SHI mode and `20 00` returns to
24-bit mode via X:0x12 -> main loop P:0x113 -> P:0x12D -> HCSR. Commands and
data use distinct GPIO qualification. Reads have pipeline side effects. Normal
extended-write address paths inherit the saved X/Y selector. Packet formats,
lengths and correlated ARM functions are documented in the command map.

**VERIFIED:** a secondary dispatcher at P:0x1C53 reads mailbox Y:0x2C, with
selectors 0..7 and explicit table-generation/copy/transform routines. ARM
0x08035E28 posts jobs and waits for the same idle sentinel; this is distinct
from the SHI parser. Exact waveform type names remain **UNRESOLVED**.

**VERIFIED:** the normal program configures ESAI and audio DMA. Vector P:0x3E
is ESAI transmit-last-slot, targeting P:0x1B4, not a DSP DMA-channel vector.
Startup clears X/Y:[0,0x6000) and shared X:[0x30000,0x38000), later modifies
them and copies reviewed P tables into X space. Four copied segments and full
uploaded P bytes were exported under `firmware/dsp/reconstructed-4486/`, with
source offsets, destinations and hashes. This is partial X/Y initialization
reconstruction, not an observed RAM image. The 55-entry copied target table
has valid in-image instruction-boundary targets.

**VERIFIED:** DSP startup creates twelve descriptors with matching ARM slot
addresses/strides, using a zero/one field and a comparison against six. The exact
initial split is not assumed because the counter increments before comparison.
ARM explicitly divides slots into 0..5 and 6..11 and writes bank values to
matching descriptor fields. ARM allocates slots and writes state/parameters through the memory protocol.
Examples include X:0xF2+8*i bank values and Y:0x150+0x60*i control values.
Note-like data wrap in octaves within 0..127; velocity-like data are squared
and scaled. Exact note/pitch/velocity semantics remain **HYPOTHESES** until
the upstream event path and downstream sample calculations are fully linked.

**VERIFIED:** both channel-one programs implement ICC/shared-memory work;
normal channel0 waits for the matching ICC startup value. Alternative channel0
implements memory pattern tests and result reporting plus an audio path.
ARM service-message IDs 0x5C, 0x5D and 0x71 force selection one through
0x0801F51E when necessary. Normal boot supplies mode zero. Channel choice uses
fixed pointer-table indexing and separate GPIO selectors. Exact physical core
numbering and undocumented user-facing diagnostic entry names are **UNRESOLVED**.

**Strong HYPOTHESIS:** the large normal DSP image implements stock synthesis/
audio processing. Evidence now includes twelve banked processing contexts,
substantial DSP arithmetic, matched host parameter/state writes and the ESAI
audio path. ARM also allocates slots and converts parameters, so a strict
UI-only ARM model is too simple. Complete synth/effect ownership and exact
algorithm identities remain **UNRESOLVED**. SPI traffic is lower-level addressed
control plus bulk data; that does not prove the ARM renders audio samples.

New tools: `ct_dsp_boot.py`, `ct_dsp_disasm.py`, `ct_dsp_reconstruct.py`,
`ct_dsp_protocol.py`, `ct_arm_calls.py`, `ct_phase3_verify.py`, `dsp_disasm.rs`,
`build_dsp_decoder.ps1`, `PHASE3.md`. New notes: `dsp-memory-map.md`,
`dsp-command-map.md`. Evidence: `builds/phase3-*.asm/json`, reviewed reconstructed
segments and pinned source/decoder build directories. Tests passed for original
hashes, stream structure, malformed streams, decoder fixture, ISR branches,
protocol classification and exact copied-table bytes.

Single best next step: trace one complete MIDI/event-to-slot-to-sample path,
linking ARM 0x080219E8/0x08021C48 to the corresponding DSP descriptor and
gate/pitch/velocity consumers. Do not begin integration.

**VERIFIED final repetition:** record maps, the large-image disassembly and
all exported reconstruction files reproduce byte-for-byte in fresh outputs.
Twenty reviewed direct ISR branches land at valid decoded boundaries. Final
SYX and BIN hashes still match the expected original values. The canonical
verification report is `builds/phase3-verification-final.json`.

## Phase 4 — static event-to-voice investigation

2026-10-05. No hardware access, firmware execution, transmission, binary
patching, Plaits integration or changes inside original/. No new dependencies
or toolchain installations were needed. Bounded ARM decoding used existing
Capstone; DSP decoding used the existing verified DSP56300 tool.

The complete reviewed map, offsets, instruction addresses, qualifications and
reproduction commands are in `voice-descriptor-map.md`. That file is the
canonical detailed record for the following discoveries.

**VERIFIED:** ARM 0x08021D86 stages note, level and signed note offset before
calling 0x080219E8. 0x080497CA(bank,note,level) selects release when level==0
and start when nonzero; 0x08049890 reaches the start wrapper, while
0x080497C4 reaches 0x08021C48. 0x0803BD58 is an upstream event entry.
Exact external MIDI status/parser provenance is **UNRESOLVED**.

**VERIFIED:** 0x080219E8 allocates/selects a slot, publishes its bank,
refreshes parameters and posts start/update flags. 0x08021C48 scans twelve
slots, matches bank plus original note, checks lifecycle/readback state,
and releases or defers according to the bank hold field. ARM state T at
0x200067FC and slot S(i) at 0x20005F64+0x10*i have the byte offsets listed
in the new map. Level is squared and divided by 128 at 0x0802192C..21932;
note is offset, clamped/wrapped in octaves and stored at S+9.

**VERIFIED:** descriptors are eight words at X:0xEB+8*i. Their fields are
dispatch P:0x281; X kernel scratch pointer (0xC stride); Y control pointer
(0x60 stride); secondary Y pointer; X event/coefficient pointer (0x4A
stride); Y sample-state pointer (0x28 stride); initialized zero field;
bank. P:0x19A5..19AC loads the first seven and calls the dispatch pointer;
P:0x282 reads the eighth. +5 passes through y1 before r3, and its pointed-to
sample accesses are Y, not an inferred X memory block. Two other descriptors
follow the twelve voice contexts in the execution loop.

**VERIFIED:** ARM bounds 0..5/6..11 at 0x080217B8..217C8 are independently
corroborated by DSP P:0x1BB3..1BE7, which examines six levels/flags/timestamps
and returns a selected slot through X:0x35. ARM writes bank to X:0xF2+8*i
at 0x08021A08. Bank selects X parameter stride 0x172, Y intermediate stride
0x2A, and mixed sample buffers X:0x2DF0 / X:0x2E50. Product UI names
"Synth 1/Synth 2" for these banks remain a strong **HYPOTHESIS**.

**VERIFIED:** X:0x57A+0x4A*i is a consumed event mailbox, read/cleared at
P:0x29D/29E. Marker bit23 chooses flag replacement; trigger bit7 selects
activation processing at P:0x2C7; masked flags persist at Y:0x122+0x60*i.
Ordinary release publishes 0x800000 and clears persistent lifecycle flags.
Primary level and a 0x100 threshold control whether release processing
continues. Y:0x150 is an envelope coefficient/control, not established as
a simple gate bit. This corrects the earlier suggested Y:0x150 gate focus.

**VERIFIED pitch data flow:** ARM 0x080272F2..27308 writes note-60 in
Y:0x159+0x60*i (signed, shifted 16). Parameter helper 0x08027FA4 writes a
separate note+offset-60 seed to Y:0x15C and sets follow step/smoothing.
P:0x327..32B conditionally copies the seed to current note, without changing
the Y:0x159 target. This distinction follows the helper's stack arguments.
DSP P:0x5C0..5CD tracks this target in Y:0x12F, emits scaled state Y:0x135;
P:0x6A7..6B5 uses it in three frequency controls. P:0x3E1..452 converts
these with arithmetic and lookup into prepared component increments.
P:0x7E9 reads an increment, P:0x7F1/7F2 repeatedly advances phase and
P:0x7F9 stores persistent sample state. P:0x832..84B processes fetched
values and accumulates component samples. Exact Hz/algorithm identity is
**UNRESOLVED**, but the periodic-generator pitch role is supported by data flow.

**VERIFIED event-level influence:** S+2 feeds 0x08027D9A's parameter-sensitive
factor; 0x0802715E writes Y:0x14D+0x60*i. P:0x4E7 and 4F3 read target and
primary level Y:0x130; lifecycle-dependent processing updates the level.
P:0x4C6/4C9 reads and multiplies this level into gain preparation.
This is per-note level influence, distinct from a bank-only patch volume.
Neutral sensitivity removes dependence. Complete final gain coefficient
aliasing on every processing branch remains **UNRESOLVED**.

**VERIFIED sample path:** P:0x77F generates phase/lookup work and consumes
fetched values; channel-one P:0x120..126 is an address-fetch worker.
P:0x9C8..9D8 combines component samples; P:0xA7F..A94 scales/accumulates
into the bank-selected buffer. Processing continues in the same DSP program
through recursive arithmetic and other effect-like stages; P:0x242..24E
combines both bank streams from Y:0x840/0x880 into Y:0x800, with additional
terms present. NXP DSP56724RM Table 5-9/chapter 9 corroborates the existing
ESAI identification; complete output/effect topology is **UNRESOLVED**.

**VERIFIED conclusion:** stock note-controlled voice synthesis executes on
the DSP, with ARM performing allocation and control/parameter conversion.
The traced event writes are control values, not audio buffers. This supersedes
the broad phase-3 synthesis-ownership hypothesis for voice generation only;
it does not prove all audio/effects ownership or recovered Nova algorithm names.

Created `tools/ct_phase4_trace.py`, `tools/PHASE4.md`,
`notes/voice-descriptor-map.md`, bounded `builds/phase4-arm-*.asm`, caller
reports and `builds/phase4-trace/`. Updated this log, todo and cross-linked
the older DSP maps. The reusable script checks original hashes, decoder equality,
roundtrip equality, raw bytes for 2,040 DSP and 1,994 ARM instruction rows,
reviewed instruction anchors, twelve slot formulas and level-scaling examples.
These are integrity/reproducibility checks, not runtime verification.

**VERIFIED final repetition:** both generated phase-4 outputs reproduce
byte-for-byte in `builds/phase4-trace-repeat`. Both original SHA256 values
still match; decoded BIN and rebuilt SYX equality checks passed again.
Exclusive-output checks also passed: an existing output directory was refused
without altering its report, and an original/ destination was refused without
creating it. The new Python source compiles successfully without bytecode output.

Best next step: reconstruct one concrete parameter configuration and
symbolically trace both passes of P:0x77F through the remaining gain aliases
and output path to define a complete per-voice input/output contract.

## Phase 5 — selected output contract and theoretical seams

2026-10-05. Read the user's attachment request; continued STATIC ANALYSIS only.
No hardware, transmission, firmware execution/emulation, flashing, patching,
original changes, new tool installation or Plaits implementation. Detailed
verified discoveries, addresses and reproducible commands are recorded in
`voice-output-contract.md`, which is the canonical phase-5 evidence map.

**VERIFIED selected-slot map:** D=X:EB, V=Y:11F, E=X:57A, Q=X:57B,
S=Y:59F, parameter bank X:296/intermediates Y:7C, bank sum X:2DF0.
Three 14-word coefficient records precede six ramp words and post coefficients.
Mode/mask words are Y:59F/5A1/5A3; phases are Y:5A0/5A2/5A4. The context
base is not itself the first phase word. The new map identifies control,
note/envelope, post-state, work scratch, queue and generalized slot addresses.

**VERIFIED two-pass purpose:** X:2F30 bit23 identifies request; low bits mark
pending contexts. P:19BF clears bit23 for completion. Worker P:120..126
replaces addresses with fetched data; P:775 waits for ICC completion. Request
returns at P:9A4 before post-processing, whereas completion consumes lookup
values, generates samples and continues. On the selected nonzero-Q+3 path,
request skips P:7F9, completion commits phase once. Other branches can update
phase during request. Three interleaved lanes are verified; product layer/
oscillator terminology is not assigned from the count.

**VERIFIED final gain alias:** P:4C7/4D0/4D1/4D3 emit X:5BB/5BC/5BD/5BE.
After consuming mode at X:5AB, selected P:BDD consumes seven coefficient
words (including AA8's reads); P:A1F adds eight to reach X:5BB. P:A8A
loads delta X:5BC; P:A8D reads current gain X:5BD; P:A91 updates it.
The producer multiplies Y:130 envelope by the bank X:2B3 coefficient with
global X:98C-X:95 modulation. ARM 080275D8..27618 supplies X:2B3 through
patch parameter 0x1C. This closes phase 4's selected final-gain alias.
Every post-processing factor's semantic source remains **UNRESOLVED**.

**VERIFIED raw mono seam:** P:9C8..9D8 combines numerical lanes into
32 words X:[2C46,2C66). At selected P:9DD, r0=X:5AB and r4=Y:5AB
(S+0xC). Retaining post mode0 retains nonlinear normalization/lookup,
recursive filtering, stock final gain and group mix. Final mix is
ASR4/MAC/ASL4 and uses old gain in its parallel MAC while storing the new
gain. Full finite-width scaling is recorded in the output contract.

**VERIFIED architecture:** primary NXP manuals corroborate 24-bit stored
words/fractional operands, 56-bit accumulators, full-transfer limiting,
MAC versus MACR and scaling modes. P:10A sets SR bit21 (rounding mode),
not bit20 arithmetic saturation. P:CA2/CB6 temporarily changes MR scaling.
**HYPOTHESIS:** nominal Q1.23 raw samples/gains. Absolute full-scale through
the complete output path is **UNRESOLVED**; normalized unity is not assumed.

**VERIFIED tables:** wave-info records have seven words, copied P:28DD ->
Y:E30. Index1 Y:E37 has mask1FFF; ARM 08028132 selects its pointer and
base. ARM 08035E28 assigns index1 base X:128800 via mailbox selector3,
handled P:1C84 -> 1CE6/1CFE. Complete generated waveform bytes remain
unresolved. Shared X:2000/2200 tables are ARM-generated. X:[1600,1940)
is an exact 832-word upper-24-bit upload from ARM flash 08052BB4; exported
SHA256=2a4b91e20f8ac7263b1977c45db798efc2ea41b7bdb2efbbcfe5cd0bdec0c13e.
Filter interpolation bases and initialization sources are listed in the map.

**VERIFIED cadence:** P:2656 initializes X:38=50 hex; P:140 derives N=32,
half/loop/stride constants. P:1D9 services blocks conditionally on ring
occupancy before both descriptor passes/group/output processing. ESAI/DMA
configuration and timing counters exist. DSP clock, samples/second and live
headroom are **UNRESOLVED**; no counters or devices were read.

**VERIFIED conditional instruction evidence:** selected major-loop bodies
total 3,635 channel-zero issued instructions per 32-word voice block, plus
1,152 worker fetch-body instructions for 192 lookups. Setup, control
preparation, other calls/loops, IRQs and repeated waits are excluded.
**HYPOTHESIS** allowance of roughly 4,000–6,000 channel-zero instructions
for this selected generation/post path is not a worst-case bound or CPU
percentage. Twelve active contexts multiply the selected subtotal to 43,620;
actual active count and cycle costs remain unobserved.

**Candidate seam HYPOTHESIS:** mono X:2C46 -> P:9DD is the best practical
theoretical generator-replacement boundary retaining stock post/filter/gain/mix.
A narrower three-lane Y:A01 boundary retains more combination behavior but
has a more complex queue contract. Before A7F and descriptor P:281 retain
progressively less stock behavior. Local I/O, persistence, scratch, shared
tables and scheduler side effects are explicit. A safe drop-in ABI has not
been proven; no patch was made.

Enough evidence exists for a feasibility study, not safe port implementation.
Clock/rate, RAM ownership, amplitude and full ABI remain unresolved. Existing
six/six allocation is verified; UI Synth1/2 naming remains a hypothesis and
was not pursued substantially. Best next step: establish clock/sample-rate
and RAM ownership, then perform the conditional compute/state study.

Created `tools/ct_voice_contract.py`, `tools/PHASE5.md`,
`notes/voice-output-contract.md`, bounded `builds/phase5-arm-*.asm` and
`builds/phase5-contract/`. Updated voice descriptor map and todo. The tool
is byte-checked address/loop accounting, not an emulator or runtime trace.

**VERIFIED final checks:** all four canonical phase-5 output files reproduce
byte-for-byte in `builds/phase5-contract-repeat`. New Python source compiles
without bytecode output. Existing output and original/ destinations are
refused without changes. Final SYX and BIN SHA256 values match the supplied
baseline; decoding equality and byte-identical SYX rebuild passed again.

## 2026-10-05 — Phase 6 static resource audit

Safety scope retained: no hardware, firmware execution, transmission, patch,
original/ modification or Plaits implementation/compilation. No new tools
were installed. Full evidence ledger, assumptions, instruction addresses and
primary manual links are in `dsp-resource-audit.md`; formal seam obligations
also update `voice-output-contract.md`.

**VERIFIED:** P:10B/10D programs PCTL X:FFFF7D=002028. Under DSP56724
register definitions, PEN=1, NR=1, NF=41, NO=1, DF=0 gives Fsys=41×EXTAL.
ARM 0801B1E8..0801B1F4 programs RCC_CFGR MCO1=HSE/4; getter literal
0801BD3C supplies a 24 MHz HSE assumption. **HYPOTHESIS:** MCO1 is wired
to DSP EXTAL, yielding 246 MHz under that assumption. Physical oscillator,
part/core assignment, ROM/indirect clock changes remain **UNRESOLVED**.

**VERIFIED:** ESAI TX TCCR=ECC309, TCR=817D10; RX RCCR=0CC30A,
RCR=017D01; SAICR=40, at P:2A3F..2A53. Device-map field arithmetic:
one TX line/two slots, one RX line/two slots, 24-bit data in 32-bit slots,
RX synchronized to TX. Documented nominal Fsys clock routing gives bit
clock Fsys/80 and frame clock Fsys/5120. No direct normal/worker PDRH
override found; unreviewed indirect/ROM changes are not excluded.
**HYPOTHESIS nominal physical model:** 48,046.875 Hz. **VERIFIED** ARM
LE16 at 0805BCD0=48047 corroborates that rounded rate, not actual wiring.
**Conditional ratio:** 5120 cycles/frame, 163840 cycles/32-frame period;
available voice headroom is **UNRESOLVED**.

**VERIFIED scheduler/ring flow:** readiness P:1D9 tests pointer difference
modulo 3FF against 300 hex; preparation/reset P:759 precedes descriptor
request P:198D and completion P:19BF. Selected P:9DD post path consumes
the mono block before group accumulation at A94. Group processing precedes
P:242 convergence, effects and P:21C4 output into X ring, then Y:FFD
advances 64 words. ESAI last-slot ISR P:1B4 rearms DMA staging and advances
Y:FFE by two words/frame. X/Y:[1000,1400) are 512-frame output/input
rings. No DMA half/full deadline was inferred. **UNRESOLVED:** finite
worst-case waits, exact DMA arbitration and output-ring underrun bound.

**VERIFIED scratch reuse:** 26 immediate X:2C46 base references occur in
voice phase/index, raw production, post/gain and global/table/mix routines.
Reviewed access families/PCs are enumerated in the audit. Startup clears it;
selected contents must survive through A94. It is not per-voice persistent
storage or an established double buffer. **UNRESOLVED:** exhaustive indirect
reader/writer exclusion, including arbitrary queue/host addresses.

**VERIFIED normal load:** contiguous P:[0,2A5E), 10846 payload words;
highest loaded 2A5D. Bootstrap sets MS/MSW1/MSW0=1/1/0. Conditional
DSP56724 core0 capacity P4000/X6000/Y4000 leaves a **POTENTIALLY AVAILABLE**
P tail of 5538 words (16614 packed bytes). No dead region or load hole
was proved. Loader 08029200 has a 16-bit count and 170-word chunks;
following stream starts ARM offset 8110, so no in-place append was proved.
Candidate X:[4000,6000), Y:[3000,4000), shared:[34003,38000) are
**POTENTIALLY AVAILABLE**, not free. Zero safely available RAM words have
been *proved*; this is not a claim of zero physically unused words. Shared
P/X/Y:[30000,38000) alias one physical region under the manual.

**VERIFIED worker evidence:** request/result replaces one shared word per
X-address fetch; selected three-lane profile queues 192 words/voice/block.
Stock mode<8 P:7A7..7C2 has a request-free voice branch using cached data.
**HYPOTHESIS:** a local generator can retain that per-voice scheduling
pattern; removing global worker/reset or repurposing both programs is not
proved safe. Maximum outstanding work/capacity/backpressure are unresolved.

**Correction, superseding Phase 5 counts above:** P:80E and P:83B DO loops
use X:3C=N−1=31, not 15. Correct contributions 558 and 837 increase selected
major-loop subtotal from 3635 to **4355** issued instructions/voice/block.
Worker fetch subtotal remains **1152**. For 1/6/12 identical selected voices,
channel-zero subtotals are 4355/26130/52260; worker 1152/6912/13824.
**HYPOTHESIS** 5000–7000 selected local instructions/voice/block is an
allowance, not a cycle bound; global/control/IRQ/stall/synchronization costs
are excluded. Old Phase 5 output files remain unchanged as historical
superseded reports; corrected output is `builds/phase6-corrected-contract`.

Created `tools/ct_resource_audit.py`, `tools/PHASE6.md`,
`notes/dsp-resource-audit.md`, Phase 6 ARM reports, `builds/phase6-audit`
JSON/CSV/ASM and corrected contract exports. Updated `ct_voice_contract.py`
with corrected counts and explicit DO-register checks; updated output
contract/todo. Candidate CFG has 6106 rows; its unresolved transfers mean
it is not a dead-code or complete access proof.

Reproduction commands from project root (fresh output directories required):

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_resource_audit.py --output-dir builds/phase6-audit-repeat
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_voice_contract.py --output-dir builds/phase6-corrected-contract-repeat
```

**VERIFIED final checks:** both sets of four reports reproduce byte-for-byte;
both tool sources compile without bytecode output; existing output and
original/ destinations refuse writes. Decode equality and SYX roundtrip pass
in each run. Final SHA256 values remain SYX
`bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd`
and BIN `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da`.

**Gate: NOT-YET-DETERMINED** for resource-qualified Plaits comparison.
No safe persistent state allocation, finite voice headroom or complete
all-mode replacement ABI is established. Best next step: bounded points-to
audit against candidate X/Y persistent-state ranges, including host/table
jobs and worker computed accesses. No Plaits work has begun.

## 2026-10-05 — Phase 6B ownership, clobber and range audit

Strict static scope retained. No hardware, transmission, firmware execution,
patches, original/ edits, installations or Plaits compilation/source analysis.
Created `notes/dsp-memory-ownership.md`, `tools/ct_memory_ownership.py` and
twelve machine-readable/evidence exports under `builds/phase6b/`. Updated
resource/output contracts and todo. Detailed interval premises, instruction
addresses, gate answers and limitations are in the ownership note.

**VERIFIED normal initialization:** caller P:25DE enters P:2779; m0..m7
become FFFF. r0=0, x1=6000, DO at 2786 writes X:(r0), Y:(r0)+, producing
X/Y:[0,6000), including all of both candidate ranges. P:278F also clears
shared X:[30000,38000). Thus no subrange qualifies under the requested
no-initialization-use criterion. **UNRESOLVED:** persistent runtime occupancy;
initial clear does not prove a later persistent data owner. Largest VERIFIED
AVAILABLE X/Y range remains none; no allocation threshold from256 to4096
words has been proved.

**VERIFIED inventory result:** canonical four-image listings contain1102
decoded X/Y absolute operands,2766 indirect operands,219 DO/REP entries
and845 immediate address-register values. Reports separate normal and
diagnostic images. These are listing counts, not reachable-code proofs.
Unresolved indirect accesses conservatively retain the full24-bit envelope.
Reviewed affine loops export base/count/stride intervals; existing four
P-to-X copies provide hash-checked initialized-value exports. Complete
interprocedural range/initialization coverage remains **UNRESOLVED**.

**VERIFIED interpretation caution:** r0=3C00/4900/4063/4863/5863 at
P:27AF..27F2 is written into EMC configuration registers FFFE53/FFFE1A/
FFFE4B, not those low-RAM addresses. Device-map interpretation was checked
against NXP DSP56724RM tables3-7/chapter21. X:3235/3237/3239 bases are
not Y pointers merely by numeric overlap with the Y candidate.

**VERIFIED worker path:** queued address at P:120 feeds unrestricted X read
P:125; P:126 replaces its shared queue word. DO count is producer endpoint
minus r5; no global endpoint/wrap bound proved. Fixed wrapper Y:[0,16)
(22 words) is private worker storage. Equal low addresses across different
cores do not automatically alias; documented shared30000..37FFF does.
Physical channel/core assignment remains conditional.

**VERIFIED host reach:** ordinary ARM constructor080292DC/080292F8 feeds
normal DSP SHI mask7FFF/bit15 space selector; candidate addresses are
accepted without a range guard. Mailbox selector6 P:1CB2..1CB5 copies512
X:C00 words to host-derived Y:r5. **UNRESOLVED:** whether normal stock ARM
call arguments actually enter candidates, including every table job. Reviewed
external table-job bases do not prove all-call exclusion. Existing ARM direct
call candidates are exported with that limitation.

**VERIFIED seam refinement:** r0/r4 are live coefficient/post-state cursors
at9DD. A and immediate condition codes are overwritten by9DD/9DE; SR/MR
modes remain separate live obligations. The clobber export preserves unknown
all-mode register/modifier/loop-stack requirements. BE2/BE6 andA89/A93
prefetch33 raw words while generating32 outputs, reaching X:2C66. That
word must remain readable, though its last prefetched value is unused for
the selected block. No universal alternate-producer clobber permission follows.

**VERIFIED selected bypass obligations:** global759 queue reset/ICC handshake,
198D pending bitmap,19BF completion consumption, mode<8 request skip and
cached completion fill remain. Lookup phase commit7F9 and conditional
prepared-coefficient updates980..998 cannot be assumed unnecessary for a
mono-only alternative. **UNRESOLVED:** complete alternate-generator state policy.

**VERIFIED count/transport mechanics:** hypothetical4000-word payload uses
4002 stream words/49158 bytes within ARM uploader count/chunk operations.
At stored offset1F0, its end would be C1F6, overlapping the following stream
at8110. **LIKELY POSSIBLE** conditional extension after repacking; physical
mode/ROM acceptance and relocation safety remain unresolved. No patch made.

**VERIFIED selected major-loop partition:** request750, completion
generation/ramp/combination2197, retained post/gain1408 =4355 issued
instructions per selected voice. Post-result copy separately64; worker1152
overlaps on its core. These are bounded selected bodies, not full service
cycles. Synchronization, dynamic counts, effects/host/IRQ/stall totals and
available generation window remain **UNRESOLVED**.

Reproduce from project root with fresh output directory:

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_memory_ownership.py --output-dir builds/phase6b-repeat
```

**VERIFIED final checks:** all twelve exports reproduce byte-for-byte;
Python source compiles without bytecode output; existing-output/original/
destination guards refuse writes. Both source SHA256 values remain exactly
the supplied baseline. Decode equality and byte-identical SYX roundtrip pass
inside each run. Reviewed affine startup and prefetch intervals were checked;
unsupported control-flow bodies are rejected by the analyzer.

**Revised gate: NOT-YET-DETERMINED** for resource-qualified Plaits comparison.
Safe state, all-mode clobbers and finite headroom are not established. Single
best next step: close all normal ARM addressed-service/mailbox destination
ranges before completing remaining DSP effects/indirect ownership proof.

## 2026-10-05 — Phase 6C runtime destination audit

**User correction applied:** deterministic boot clear is INIT-TOUCHED, not a
disqualification of persistent allocation after initialization. Earlier Phase6B
no-initialization-use conclusions are superseded. Runtime availability still
requires exclusion of normal dependencies; diagnostic capability and another
core's private numeric address are not channel-zero runtime ownership.

Static constraints retained: no hardware, firmware execution, transmission,
patches, original/ edits or Plaits source/compilation. Existing Capstone was
read outside the sandbox because its dependency directory is inaccessible in
the sandbox; no installation occurred. New tool `ct_runtime_ownership.py`
creates exclusive fresh reports under `builds/phase6c/final`; preliminary
root/refined exports are preserved. Created `notes/dsp-runtime-ownership.md`;
updated ownership/resource/output notes and todo.

**VERIFIED scan/report facts:** all halfword starts scanned for twelve addressed,
bulk and width-helper entries yielded300 candidate calls/tail branches,
including258 to080292F8 and19 to08029344. Constant-suffix destination maps
contain84 normal-family,1 boot-family and10 test-family entries;205 remain
unresolved in destination, extent or mode. These are candidate listing facts,
not complete callgraph/reachability proofs. Every candidate has argument and
mode evidence or explicit unknowns; computed values are not fabricated.
Resolved normal constants do not overlap the candidate X/Y ranges. Known
slot/table interval families remain bounded only under their reviewed premises.
Complete normal runtime destination exclusion is **UNRESOLVED**.

**VERIFIED service families:**2916C delegates X:5..8 test writes;2918C
reaches X:2 helper;29134 uses X:9/10;29072 reads Y:3. Mode ancestry of
every alternate wrapper entry remains unresolved. Normal banked parameter
constructor27A12 reads selector byte at20006800 and multiplies by172;
normal0/1 domain needs a writer proof, not a guess from two-bank count.

**VERIFIED mailbox refinement:** selector2 enters1CF4: x0=324 is an
arithmetic coefficient, x1=1 supplies DO at1DB1, and1DB4 writes one Y word
through derived r4. It does not write324 words. Selectors6/7 copy512/3
words respectively but normal posts were not proved. Normal35E28 table jobs
publish selectors2/3/4/5/0 from external bases. Pointer-list indices3..12
alias the preceding base;28800 is generated-family stride, not every index's
unique allocation. Full multistage/generated destinations remain unresolved.

**VERIFIED relocation evidence:** table08029700 stores S0ch0/S1ch0/S0ch1/
S1ch1 pointers in that order;29276 constructs table pointer,2928E/292A4
select rows. Embedded count determines upload length; sources byte-addressed,
table entries4 bytes. Exact u32 scan found one extra S0ch0 match0801B8F3;
bounded decoding shows it spans AND/OR instruction bytes, not a pointer load.
Constructed semantic references remain unresolved.

**VERIFIED stronger collision:** expanded first stream ends rawC1F6 and
crosses ARM clock code0801B1A8 (rawB1A8), not just the following DSP blob.
Moving channel1 alone cannot solve it. Relocating the enlarged first stream
through its table entry is **LIKELY POSSIBLE structurally**, with no proved
free container region or device size/ROM acceptance. Appending that whole
stream requires49158 bytes; minimal packed payload growth16614 does not
justify shifting absolute ARM code. SYX encoder has32-bit size/CRC/chunk
mechanics; no enlarged firmware file was produced.

**VERIFIED guard refinement:**2C66 readable for selected prefetch; its last
numeric sample is unused in the selected32-output result. It is also neighboring
filter scratch: C13 sets that base; C9F/CA0 populate stock history there.
Universally arbitrary value, duplicate-last rule and all-mode later/status
effects remain **UNRESOLVED**. Conservative contract retains stock neighbor
behavior. Timing remains selected bounded loop subtotals only; async reset/
lookup/mailbox waits, dynamic counts, groups/effects, IRQ and external-memory
timing prevent a worst-case generation-window proof.

Largest VERIFIED AVAILABLE AFTER INIT X/Y allocations: none established.
Thresholds256..4096 and safe fit remain **NOT-YET-DETERMINED**, not proof of
physical exhaustion. Conditional DSP56724/core0/mode map still offers5538
additional P words independently of ARM-container issues.

**Revised narrow readiness gate: YES** to reading Plaits solely for resource
comparison against conditional constraints and explicit unknowns. This does
not require an established allocation, and does not imply implementation,
fit, safe ABI or deployment readiness. No Plaits source was read in this phase.
Best next firmware step: prove normal writers/domain of selector20006800,
then propagate that bound through related parameter-address constructors.

Reproduce with existing local Python/Capstone and a fresh directory:

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_runtime_ownership.py --output-dir builds/phase6c/repeat
```

**VERIFIED final checks:** all14 final reports reproduce byte-for-byte; source
syntax compiles without bytecode output; existing-output and original/ guards
refuse writes. Each run confirms decoding equality and exact SYX rebuild.
Final SYX/BIN hashes match supplied baseline. A complete interprocedural
runtime ownership and destination proof has not been achieved.

## 2026-10-05 — Phase 7 official Plaits static resource comparison

Feasibility only. No Circuit hardware, MIDI/SysEx transmission, firmware
execution, binary or stock-payload edits, original/ writes, Plaits port,
compilation/linking or injection. After the user's continuation message,
existing pinned source/reports were used without refetch or restart.

**VERIFIED provenance:** official pichenettes/eurorack commit
`08460a69a7e1f7a81c5a2abcc7189c9a6b7208d4`, matching official stmlib gitlink
`e3bd7c9cc00e4364166f9905c0509b6ffd0535ec`. Copied183 text source files,
1,241,908 bytes to plaits/upstream; Git blob and SHA256 provenance retained.
No fork. Initial broad vendor selection exceeded the download cap and was
rejected before destination creation; narrowed copy omitted vendor/CAD/binaries
and toolchains. Existing permission escalation was used only for network/source
reads. MIT notices preserved; repository hardware/AVR licensing remains separate.

**SOURCE-DERIVED architecture:** Voice Render prepares EngineParameters,
selects model, renders separate float OUT/AUX, then uses gain/optional limiter/
LPG and Clip16 with module polarity into interleaved short frames. Registry24
slots reference22 embedded engine objects (SixOp repeated); allocated arenas
overlay via allocator.Free, embedded objects do not. Module pool16384 bytes;
Particle diffuser alone allocates8192 uint16 entries. Raw generator needs no
full Voice, drivers/UI/flash/user-data or module post chain by definition of
the investigated Circuit seam; safe omission/behavior remains a design question.

**SOURCE-DERIVED block/rate constraints:** native12, max Voice buffers24;
unmodified Voice32 call is unsafe. Selected raw VariableSaw/FM/Waveshaping
loops can conceptually render32 with correctly sized caller buffers. Full VA
temp allocation24 must be handled separately. Five native trigger-delay calls
represent60 samples/nominal1.25ms;32-sample calls would produce160 samples/
conditional3.330ms. Hardcoded per-block envelopes/note smoothing require
retiming, not merely larger arrays. Source nominal rate48000 and corrected
pitch normalization47872.34 are distinct. **Conditional calculation:** unchanged
pitch conversion at Circuit48046.875 yields about+6.300 cents. Physical Circuit
clock/rate and voice headroom remain unresolved. Named rate/block occurrences
are exported; implicit fixed coefficients are not exhaustively classified.

**SOURCE-DERIVED scalar payloads under32-bit float/u32 assumptions:** primitive
VariableSaw6 floats+bool=25 bytes; full VA35 floats+4 bool+pointer=148 bytes;
FM7 floats+3 uint32=40 bytes; Waveshaping15 floats+2 bool=62 bytes. These
exclude base/vptr/padding/control/render/stack; no C++ sizeof measured. State
field witnesses were independently checked. Full Voice wrapper arrays/registry
alone lower-bound324 bytes, plus all engines and peak arena. Per-model states,
filters/history/envelopes/random/lookup dependencies are distinguished in notes.

**SOURCE-DERIVED tables:** pitch high/low257 floats each (256 explicit plus
implicit zero),2056 bytes; sine641 floats; FM quantizer130/FIR4 floats; folder
tables516 floats each; five257-point int16 shapers. Referenced full-array sets
are VA/pitch2056 bytes, FM5156, Waveshaping11318; deduplicated three-model
union11854. All scalar arrays in generated Plaits resources sum74702 bytes,
excluding pointer metadata and further speech datasets. Full data in the5538-
word P tail is LIKELY TOO LARGE; alternate/quantized storage is not proved.
Shared data is not multiplied per voice. Bit-preserving float/u32 whole-scalar
storage requires two24-bit words; native pointer rebinding and fixed formats
are estimates, not source ABI preservation or universally Q1.23.

**SOURCE-DERIVED footprint proxies:** primitive closure6 files/553 noncomment
lines/40 lexical function candidates; VA14/1110/76; FM15/811/78; Waveshaping
17/1126/98; three-model union24/1766/129; full Voice125/12149/700. Includes
unused header functions, inactive variants/templates, excludes numeric table
bodies; no DSP P-word or exact-revision ARM-section size inferred. Selected
closures complete; full hardware UserData flash dependency deliberately omitted.

**SOURCE-DERIVED hot work / ESTIMATE risk:** primitive has3 interpolation
updates, phase progression,2 reciprocals/sample and conditional edge/BLEP
polynomials. FM4× loop computes12 interpolated sine calls/output including
AUX; OUT-only hypothesis8. Waveshaping mixes adjacent int16 tables, two
Hermite folders and AUX sine. No source-operation→DSP-cycle conversion, CPU
percentage or available-headroom claim. ARM-specific float sqrt/saturation
helpers and32-bit phases would need a future numerical/toolchain strategy.

**HYPOTHESIS ranked first target:** VariableSaw-derived VA mono branch, then
VA OUT graph, two-op FM and Waveshaping. Broad Voice, particle/string/speech/
wavetable/six-op families are poor first targets due data/state/math. Theoretical
OUT-only graph reductions are documented without source changes. Existing
Circuit note/lifecycle/level/patch evidence supports conceptual inputs but no
proved unit/control/amplitude mapping. Guard2C66 and stock phase/scheduler/
filter/gain semantics remain obligations. No numerical adapter is specified.

**ESTIMATE planning PoCs:** A primitive on one branch/slot, small source state
and128–256 DSP-word reserve target excluding tables/output; B reduced Voice/
three-model subset~0.75–1.5KiB source-like state/work plus shared tables;
C broad Voice plus16KiB pool and large data. These are architectures/risk
rankings, not code-size, allocation or fit proofs. Conditional Circuit limits
remain5538 extra P words, candidate X8192/Y4096 words, no verified persistent
allocation, and163840 total cycles/32-frame period, not available voice cycles.

**Decisions:** small derived Plaits is not obviously impossible; one primitive
is plausible. Persistent RAM, P/container space, timing and numeric/clobber ABI
remain primary blockers. Bank-selector proof is unnecessary for conceptual
PoC descriptions but required for an allocation argument relying on banked
normal-host exclusion. Mono seam remains best HYPOTHESIS, not a complete ABI.
Resource reading/comparison YES; implementation readiness NO. Continue firmware
archaeology before an implementation-ready PoC design. Best next step: prove
one256-word after-init state/work region, with pitch tables and headroom separate.

Created notes/plaits-architecture.md, notes/plaits-resource-comparison.md,
tools/ct_plaits_fetch.py, tools/ct_plaits_audit.py, plaits/README.md and six
machine-readable reports under builds/phase7. Updated todo/research log.
Reports reproduce with a fresh directory, without network or compilation:

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_plaits_audit.py --output-dir builds/phase7-repeat
```

**VERIFIED final checks:** all six exports reproduce byte-for-byte; all183
upstream files match both Git blob and SHA256 identities. Python analysis
script syntax and original/existing-output guards pass; no upstream code was
executed or compiled. Both original SHA256 values match supplied baseline;
decoded BIN equality, exact SYX rebuild and CRC4E74DA9E pass. All five extracted
DSP streams/payloads match manifest hashes and their bytes in original BIN.

## Phase 8 — 2026-10-06 — after-init RAM proof audit

Static only; no firmware execution, hardware, transmissions, patches, compilation,
port, injection, large-tool installation or upstream refetch. Prior work retained.
Full results:notes/plaits-poc-memory.md; replay:tools/ct_poc_memory_audit.py;
exports:builds/phase8/. The primary256-word allocation goal remains **UNRESOLVED**.

**VERIFIED initialization:**0805B7B4's scatter wordsFFFBF037/2D50/20003D04/0
resolve to Thumb clear helper0801A7EB.0801A7EA's zero stores clear ARM
[20003D04,20006A54), including20006800 selector and20006801 slot.08021098
also stores zero halfword at parent200067FC+4. DSPP:2782/2784/2786/2788/2789
clearX/Y:[0,6000) at init; this is INIT-ONLY, not a runtime disqualification.

**VERIFIED mutations/call paths:** byte stores08021496(parent+4),0804963A,
0804978C,0804982C.214BE supplies0/1 to2148C;3BDF2'sBE0C/0E andBE16/18
supply0/1 to49634.49758's0x10 path returns;497CA's0xFF/0x10 branches bypass
its selector store. Other inputs lack0/1 guards.3BD58 calls497CA before its
CMP#2, so that comparison cannot constrain the prior store.29A08/29A12 thunks
feed these routing paths. **UNRESOLVED:** global normal/service domains and
all aliases/indirect callers. Conservative byte-domain0..255 is not actual reachability.

**VERIFIED callback/formula:**2148C stores selector then dispatches16 entries
at0805A384; entry6 is Thumb08027A11, actual function08027A10.27A38/44/48
form bank*172+2FB;27A5E/72/80/AB8 write20 stride5 records at offsets0,1,2,4,
skipping3.27ABC..AC0 bounds20 iterations.27AC6..ADC writes20 tail words at
bank*172+3D0;27AF0 writes globalX:95. Conditional0/1 record hulls are
X:[2FB,35F),[46D,4D1), tails[3D0,3E4),[542,556). Abstract byte64 reaches
X:5F7B, a counterexample to a byte-width-only exclusion, **not a normal write
witness**.27A12 is the stride instruction, correcting earlier function-entry shorthand.

**VERIFIED independent use-site:**21D8E reads selector,21D9A AND1,21D9E adds9D,
21DA2 writesX:9D/9E. Slotbyte20006801 is distinct; allocator bounds must be
propagated independently. **CORRECTED IN PHASE9:**3602A compares70 parameters
and calls21E9C to mark200067FC dirty flags, consumed by213D4/2148C. The original
Phase8 alias separation was incorrect because its PC-relative literal address
was misresolved.360EE's0/1 preparation calls do not themselves storeselector.

**VERIFIED conditional effect prefix:**N=32 and linear AGU boundP:CC4's body
toX:[2EF0,2F30),[1BB2,1BF2),[1BF2,1C32),Y:[840,880),[880,8C0),[9C0,A00).
**UNRESOLVED:** following1157 index/pointer bounds;Y:7FE→n7 and scaled
parameter→X:9B1+n2. P:1E15 savesr6/r7 inX:1D3A/B;1E33/1EC2/1EED reuse
them. Calling mode, origin, modifier and full footprint remain unresolved;
not counted as proved normal audio occupancy of candidates.

**VERIFIED worker behavior:**105 startsr5=30002,107 publishes30000,114 reloads
on ICC reset,117..11E uses endpoint-cursor count,120 reads queuedaddress,
125 fetchesX:(r0),126 replacesqueue/advancescursor. Normal endpoint stores
81B/876/8D5/917/954 and repeatDO7C8 leave globalcount unresolved.
**SOURCE-DERIVED:**DSP56300FM4.5.1 `$XXFFFF` is legacy24-bitlinear;
DSP56724RM SR.EMA bit18 resets0. UnderEMA0 M5=00FFFF is not a shared-bank
ring; overflowmodulus2^24, not38000. Actual globalmode/SR closure unresolved.
Conditional shared[30000,38000) aliasesP/X/Y; different-core lowprivateX/Y
does not alias solely by numeric equality. **ESTIMATE selected profile:**
12×192 queuewords givesendpoint30902; not maximum/repeat/wrap proof.

**VERIFIED DMA registers:**2A2D..2A3D setDCR0=285AC4/count2/sourceFFFFA8/
destination29 andDCR1=286251/count2/sourceFFFFA4/destination21;2A3E enables
channel1.1BC/1BE rearm29/21;reviewed stagingX21/Y29 andrings[1000,1400)
arelow. **UNRESOLVED:**exactDCRspace/stride/count expansion and complete
writer/reconfiguration exclusion. No complete DMA interval set is invented.
Stack-register inventory is lexical, not maximum-depth proof; software saves/
scratch remain unresolved. Hardware stack distinction is not freeX/Y proof.

**Allocation result:**X:[4000,6000) andY:[3000,4000) remain POTENTIALLY
AVAILABLE / UNRESOLVED after init. Eight blocker families record precise
origins/missingbounds/spaces.64/128/256/512/1024 gates all NOT-YET-DETERMINED.
Largest verified allocation none in either space; no chosenbase/state layout.
Zero provedwords must not be interpreted as zero physicallyfreewords.

**VERIFIED stock output ownership / SOURCE-DERIVED primitive:**32-word
X:[2C46,2C66) scratch remains runtimeoccupied and is reused, with readable/filter
neighbor2C66. Selected rawprimitive has no mandatory32-element temp array.
**HYPOTHESIS:**directfuture rendering could avoid anotheroutputbuffer within
serialcompletion lifetime; numeric/live-state/guard obligations unresolved.
Six floats+bool, table-free primitive and separate pitchadapter claims remain
Phase7 SOURCE-DERIVED;256 is planning, not actual requirement. P/container,
timing and numericABI remain separate. Implementation readiness **NO**.

**Single best next step:**close29A08/29A12 input/indirect ancestry and whether
widerselector writes can survive into2148C's normal bankedcallbacks, then
continue independent exact-region DSP/worker/DMA/save exclusions.

**Additional VERIFIED ISA-derived bound:**P:1166 y0=19,1168 signedfractional
MPY,116A directB1→n2 yieldfloor(19*signed24(x0)/2^23), hence[-19,18].
The alternate1164→1172 branch keepsn2=3 from1160. AccumulatorB1 transfer is
unscaled; conditional linearM2 withr2=9B1 givesX:[99E,9C4) for116E/1175.
This narrows the earlier1157 index uncertainty; its retained circularbuffer
origins/modifiers and whole-helper footprint remain **UNRESOLVED**.
Primary semantics:[DSP56300FM §§3.1.2–3.1.3](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf).

**VERIFIED final replay:**canonical exportsbuilds/phase8/verified/ reproduce
byte-for-byte across45 files inverified-repeat/. Earlierroot/final/repeat
reports are preserved as intermediate versions;README identifiesthecanonicalset.
No originalor extracteddata overwritten. Script syntax, existingdirectory/
firmwarefile refusal and original/subdirectory protection all pass.
OriginalSYX/BIN hashes matchbaseline; in-memorydecodeequality, exactSYXroundtrip
andCRC4E74DA9E pass. Allfiveextractedstreams/payloads matchmanifest andsourceBIN;
all183pinnedPlaitsfiles matchmanifestSHA256/size. Canonical normalch0 inventory
has0absolutehighcandidateoperands,29DMAregisteroperands and11hardwarestack
registeroperands; these arelistinginventories, not freeRAM/globalreachabilityproofs.

Creatednotes/plaits-poc-memory.md andtools/ct_poc_memory_audit.py; updated
dsp-runtime-ownership.md, dsp-memory-ownership.md, plaits-resource-comparison.md,
research-log.md andtodo.md. No safeallocation/layout isclaimed. Continued
analysis isrequired before the requestedprimaryallocationgoal isfulfilled.

## Phase 9 — 2026-10-06 — local selector-domain closure

Static-only continuation. No hardware, MIDI/SysEx, flashing, firmware execution,
binary patches, original/ edits, upstream refetch or Plaits compilation/port.
No broad DSP ownership audit repeated. Full evidence:notes/bank-selector-domain.md;
canonical exportsbuilds/phase9/verified/, address propagationranges-verified/.

**VERIFIED interface/signatures:**29A08 discards r0this, forwards incoming
r1namespace/r2key/r3level to3BD58;29A12 forwards r1namespace/r2key to3BD94.
No masks/clamps in thunks. Each has one exactThumbpointer reference at805B860/
864 and no direct call candidate.2989C's298B4/BE binds vptr805B860 fromheader
805B858. Wider accepted register inputs are not proved normalproducerdomains.
Upstream virtual caller/object-flow, sequencer/MIDI/external schemas remain
**UNRESOLVED**; no inferred parserlabel is presented as verified.

**VERIFIED special branches:**49758 namespace10 returnsbeforeselectorstore.
497CA namespace10 skipsstore, keys3C/3E/40/41 dispatchindices0..3 through51B54.
Key40 is not selector64. Drum interpretation is **HYPOTHESIS**, four-trigger
mapping VERIFIED.497CA FF branch skipsstore andcalls28FC2→namespace21,param9
→Y111;2AB48 is a constantFF directwitness.20/21 are separateparameterobjects,
not proved validnotechannels or DSP uploadselection/core IDs.

**VERIFIED incoming parameter edges:**2148C has recoveredcalls214C2/14CC
(explicit0/1) and4966E.49634's recoveredcallers3BE0E/18 supply0/1 fromrefresh
maskbits0/1.29A00 carriesrefreshmask, notnotechannel.21496 storesits bankargument
before16-callbackdispatch214AC. Index6 at805A39C holdsThumb27A11, entry27A10.
213D4 independentlystoresbankloopcounter0/1 at213E6; slotcounter0..11 at21414.

**VERIFIED serialization:**1E000 loads2000030C;1E03C constructsguardwith1F4B0;
1E044 storespointer.1F4B4 loads1;1F4B8/BA storecount/capacity1 at+C/D.
21064 atomicallydecrementswithLDREXB/STREXB/wait;29028 releasesbelowcapacity.
3BD6C/3BDA6(eventwriters),3BE04(refresh),1F4E4(parameterservice),1D5D4(audio/
slotservice) acquire same `*[2000030C]+C`. Releasepathsare29028 or1D5DC..5FC.
Recoverednormalwrapperscannotconcurrentlyreplace selector inprotectedcallback.
Validnormalinitialization/immutabletables/guardprotocol scope isexplicit; this
is not an arbitrarycodeinjection/corruptionproof.

**CORRECTED VERIFIED dirtyflag alias:**align4(21F94+4)+134=220CC;
align4(21FB2+4)+118=220CC; wordthere200067FC. Phase8's21FCC/20006A0C
associationwasincorrect.21E9C categories9..18 markparent+18+2*bank bits0..9;
categories1/2/3/5 markparent+16+bank.3602A's70-entry comparisonsetter is
connectedto213D4/2148C.20006A0C holdsseparate global10/20/21 flags.
Phase8 notesandhistorical logparagraph corrected, rawearlierexports preserved.

**VERIFIED recovered localdomains:**bankedparametercallbacks bank0/1;
slotcallbacks bank0/1 andslot0..11;27AFA fixedglobaladdresses withoutbankread.
At27A10 selectors10/40/all2..255 are **IMPOSSIBLE BY CALLER BOUNDS in the
recovered normal graph**, not globally impossiblebytevalues orSERVICE-ONLY.
TheabstractPhase8 bank64→5F7B arithmetic remainscorrect but isnotnormal
parameter-dispatch reachability. HOST-BANK removed for these recoveredpaths.

**VERIFIED complete recovered tables:**805A384 bank16(tenimplemented,sixBXLR
stubs),21478 slotfive,21534 namespace10four,805B3B0 namespace20ten,215B8
namespace21three(twoimplemented,oneBXLRstub):38validentries. All tables
exportedseparatelywithcallback/helper/constructor/domain/counts. Reservedslot
pendingbits5..7 andnamespace21bit3producerbounds are **UNRESOLVED**:215C4's
D0002800 is instructionbytes, notfourthfunctionpointer; namespace21setterID12
canrequestbit3 butnormalinputadmissibility isunproved. No inventedcallback.

**VERIFIED address propagation:**helpers28132/2819C/28204/28336/283D8,
27DE0/27F34/27FA4/28096 andsharedtailswriteprovidedregister/stackdestinations.
Exportedformulaspreservebankstride172,slotstride60,groupYstrideE;callback27556
hasunbankedX2AB/2B2 andslot2712E/271E4 haveunbankedX2F8/2F9.
27A10 own101sinks:20stride5recordsfields0/1/2/4,tail20,global95.
**New VERIFIED delegation:**27AE4→2872C can immediately2873C→286BC or defer;
286DA/286E4 write2FA+172*b and35F+172*b. Deferred286F6 usesindependent0/1
constants2870C/2871E. Count20/timingdoesnotwidenaddressdomain.103possible
destinations doesnotmean103synchronouswrites oneveryinvocation.

**VERIFIED recovered-family union:**456distinctXwords,375Ywords; boundsX52..959,
YFD..78F(inclusive), exactholes in normal-parameter-intervals.csv.1382propagated
sinkrecords include finitebank/slotcontexts andconditional/deferredpaths, not
per-blocktraffic/cycles. Opaquenumericresultsnever become guessedaddresses;
no unresolveddestinationargument orunsupportedpathin currenttableexport.
Thisisnot thecompleteintervalsetofallothernormalhost/addressed/bulkjobs.

**VERIFIED candidate-family exclusion:**zero recoveredparameterdestinations
overlapX[4000,6000) orY[3000,4000).64/128/256/512-startsearch excludesnone
throughthesefamilies. **UNRESOLVED persistentavailability:**othernormalhost/
table/DSP/worker/DMA/save/scratch exclusions remain; noallocation/layout.

**VERIFIED parameter namespace construction:**29906/26/40/5A/74 createIDs
0/1/10/20/21;3BE60 accepts those, returnsNULLforordinarynonnegative2/3/40.
ThisdoesnotidentifyMIDItrackselectors. UIbank0→Synth1/bank1→Synth2 is
**HYPOTHESIS**; MIDI1/2 identitiesremain **UNRESOLVED**. Desiredfuturemono/
mono/fourvoice/fourvoice targetandeightcontrols are recordedin
notes/control-architecture.md asuserintentonly; no parameter IDs orimplementation.

**Singlebestnextstep:**auditexactcandidateX[5F00,6000) againstremainingnormal
non-parameterhost/table andretainedDSPtablepointerjobs, startingX1B16 and
P1E15→X1D3A/1D3B. Keepotherexclusionsindependent; implementationreadinessNO.

**VERIFIED final checks:** eight address-propagation exports and twelve proof
exports reproduce byte-for-byte in ranges-repeat/ and verified-repeat/.
Syntax checks and existing-output/original-subdirectory protection pass for
all three new scripts. Original SYX/BIN hashes match the supplied baseline;
decode equality and exact in-memory SYX round-trip pass. All five extracted
DSP streams/payloads retain manifest hashes and match their source BIN bytes.
No firmware, extracted payload, original file or pinned Plaits source was edited.

Created notes/bank-selector-domain.md, notes/control-architecture.md,
tools/ct_bank_domain.py, tools/ct_parameter_ranges.py and
tools/ct_bank_domain_report.py. Updated dsp-runtime-ownership.md,
plaits-poc-memory.md, research-log.md and todo.md. Canonical exports are
builds/phase9/verified/ with ranges-verified/ as their address-propagation inputs.
The local bank proof is scoped to the recovered normal graph; upstream event
origins and full persistent allocation proof remain unresolved.

## Phase 10 — exact high-X candidate audit, 2026-10-06

Request: prove/disqualify channel-zero private X:[5F00,6000) after init,
without binary edits, hardware access, transmission, porting or compilation.
Continued existing evidence; did not repeat Phase9's low parameter graph or
refetch pinned Plaits sources. Report: notes/dsp-high-x-audit.md.

**VERIFIED byte evidence:** tools/ct_high_x_audit.py byte-checks the canonical
Selection0/channel0 DSP listing and this phase's ARM disassembly windows.
It rechecks original SYX/BIN hashes, CRC4E74DA9E, decode equality and exact
in-memory roundtrip, and all ten stream/payload hashes in the five-block
extraction manifest. No input firmware was overwritten.

**VERIFIED X1B16 layout:** P1D26/1D41 set R2=1B16;1D32..3C save eleven
words and1D48..52 restore them. Fields are R0,R1,M1,R4,N4,M4,R5,N5,B1,
stage/progress X0,and R3. R0/R1/R3 are consumed as X coefficient/workspace
cursors; R4/R5 are consumed as Y generator/output cursors. X1B15 is the
active/remaining field;1B21 holds size.1CCD resumes the asynchronous job.
This corrects treating X1B16 as a single arbitrary X output destination.

**SOURCE-DERIVED addressing + VERIFIED setup:** initial R1=2400/2500 and
M1=3FF belong to the aligned1024-word ring[2400,2800) in legacy EMA=0
addressing. Generator1E08/0A writes within that ring;1DBF exports to Y.
Small-N export reads[2400,2802), including two lookahead words, with linear
M2. Reviewed recurrence1D74..84 consumes256 coefficients for16 stages,
512 for18, starting C00; foreign job-state mutation remains unclosed.
Machine outputs separate reviewed premises from a universal runtime proof.

**VERIFIED mailbox distinction:** selectors0/1/3/4/5 generate to Y; selector2
has one Y store, selector6 a512-word X→Y copy. Selector7 actually writes X:
1CBB..C3 forms1D8D+4*index from X:C00;1CC4..C7 copies three words.
Abstract index105D would yield[5F01,5F04) with linear M1, but no such normal
publisher/value is proved. Backup transforms1CD0/1CD9/1CE6 locally read
[2800,2A00) and write[C00,E00). No selector7 normal ownership witness.

**VERIFIED P1E15 pointer uses:**1E15/17 save R6/R7 into X1D3A/B;1E33,
1EC2,1EED/EEF reload them for Y accesses1E3D/40,1ED2,1F03/0D/0E.
These are Y-buffer pointers by use. Direct-edge/aligned-word census finds no
1E15 entry reference; **UNRESOLVED normal reachability**, not a dead-code proof.

**VERIFIED distinct effect mechanism:**1E74..7E or1ED7..EE1 populate
X1D40/41/42 with1800/1840/18E0 or19F0/1A30/1AD0.1F5C loads them;
1F68/6A read Y:(R6+32/33) into R1/R3, then1F6E/6F write X through those
cursors.1F89/93/97 similarly loads and uses R7. **UNRESOLVED** complete
Y-state cursor producers, all modifiers/iteration progression and normal entry.
Therefore the Y-pointer correction does not establish a global effects X bound.

**VERIFIED ARM utility mechanism:**269E4 request decoder;26A3C..50 accepts
shared[30000,38000) or private input below8000.26A9A write/26AD4 read use
incrementing UXTH addresses via292F8/29344; mode controls port/8000 space flag.
1F30A calls269E4;26B08/14 encode/respond. **HYPOTHESIS:** addressed service
role. **UNRESOLVED:** dispatcher conditions restricting normal vs service,
operation/mode and count/address ancestors. Domain covers every candidate word;
capability is not a normal-runtime occupancy witness.

**VERIFIED selected bulk evidence:**35E28 publishes selectors2/3/4/5/0 with
external bases and low stagingC00.48DAA caller395EC suppliesE80000.49A80's
page comes from its second argument, and49A66 repeatedly calls it with an
accumulating address. Global normal bulk maximum and cached-stream cursor
wrap/producer closure remain **UNRESOLVED**.21E58..64's16-bit-derived
intermediate is bounded by57FF, then21E70 adds4000 flag and stores ARM state;
that window does not prove a new SHI read at the transformed address.

**SOURCE-DERIVED architectural correction:** DSP56724RM table3-7 has eight
DMA channels; channel1 FFFFEB is DSR1 andFFFFEA DDR1. APR23 table1-2
defines DSS/DDS and DAM fields; DSP56300FM10.5.3.1 gives modeA DCO+1 count.
**VERIFIED stock controls:**285AC4 gives fixed X:FFFFA8→Y:[29,2C);
286251 gives Y:[21,24)→fixed X:FFFFA4, three transfers each.1BC rearms
DDR0;1BE rearms DSR1. Both RAM staging areas are Y, correcting older X:21
claims. No private X RAM destination exists in this reviewed configuration.
Eight-channel register census includes raw table decodes without treating them
as reachable writes. Y:FFFFE6 is EMBC, not X DMA; worker Y ICC is separate.
Primary links and decoding premises are in dsp-high-x-audit.md.

**VERIFIED selected saves:** audio YF3F/F40 with hardware SSH/SSL and balanced
restores1CF..1D8; SHI Y2000..2005; table snapshot X1B16..1B20. Hardware stack
is distinct from X/Y heap. **UNRESOLVED** all indirect save/scratch footprints,
DMA reconfiguration and universal effects maxima. Worker private low addresses
remain a distinct domain; no proved channel-zero high-X worker write follows
from numeric equality. Conditional part/core alias assumptions remain explicit.

**Allocation/persistence result: UNRESOLVED.** INIT-only clearing is permitted.
No literal candidate access or periodic clear established; no universal survival
across blocks/jobs/mode transitions proved. All contiguous placements checked:
256words1,128words129,64words193. The unclosed utility domain covers every
placement; shrinking does not solve it. No VERIFIED AVAILABLE AFTER INIT
subrange; no theoretical layout. Output X2C46..2C65 /neighbor2C66 remains stock
scratch. No knob/UI pass or port implementation.

**VERIFIED reproducibility:** thirteen replay exports are byte-identical between
builds/phase10/replay/ and replay-repeat/. Syntax and existing-output/original-
subdirectory refusal checks pass; validation.json records the checks. Original
SHA256 hashes and five extracted streams/payloads remain at baseline.
Created tools/ct_high_x_audit.py and notes/dsp-high-x-audit.md; updated
plaits-poc-memory.md,dsp-memory-ownership.md,dsp-runtime-ownership.md,
research-log.md,todo.md. ARM evidence retained in four phase10/arm-* directories.

**Single best next step:** close ARM dispatcher branch1F308/1F30A→269E4's
normal/service and request argument constraints. Keep the separate1F5C cursor,
DMA/global AGU and physical alias proofs outstanding. Implementation readiness NO.

## Phase 11 — host utility classification and narrowed cursor blockers

2026-10-06. Static only; continued Phase10, with no firmware/original/extract
changes, hardware access, transmission, upstream refetch, installations or
Plaits implementation/compilation. Full report: notes/host-utility-269e4.md.
Reproduction: tools/ct_host_utility_audit.py --output-dir fresh-directory.

**VERIFIED ingress and request ID:**2484C compares the five-byte prefix at
248AC (F0 00 20 29 01), byte5=63, byte6=70 and length>=9.24880 calls1F284.
1F28C/28E checks byte7=5E and1F290 branches1F308;1F30A calls269E4 with
the same context.1EB30's input identifiers0/1 call2484C at1EB40. Boot1EC92
loads the callback pointer1EB31 from literal1EDE0 and installs it through251E8.
Temporary context+0 is a routing mask from1<<identifier; context+4 is Buffer*.
Buffer+0 is the incoming pointer and+4 byte length. Physical ingress identities
and complete upstream publisher ancestry remain **UNRESOLVED**.

**VERIFIED recovered classification: SERVICE-ONLY invocation, not Selection1-
only.** The separate bit4 guard is at1F30E..314 after the utility call;
2484C's enable check2488E also occurs afterward.5E never requests a diagnostic
upload. Boot1D582/1F51E still loads Selection0 normally; separate request60
controls other flags/mode restoration. Thus this service can be invoked while
Selection0 is active. Ordinary audio/UI publishers of5E are not established;
do not claim a universal VERIFIED NO about execution during normal-mode use.
Only direct269E4 call found is1F30A; no exact entry pointer found by the flash/
decoded-init census. Absence is not proof against every computed call.

**VERIFIED complete decoded schema:**269EC..26A00 uses UXTH(length−9) and
incoming+8→stack90 via391C6. Header fields: operation byte+0,mode byte+1,
opaque echoed cookie32+2,address32+6,count16+A,slots+C with4-byte stride.
Modes0/1 choose transport port0 X/Y;2/3 port1 X/Y;4..FF fall back port0/X.
These are transport/space modes, not upload-selection or MIDI track labels.
26A3C..50 accepts private start[0,8000) or shared[30000,38000). No local end
check or count<=32 clamp. Private loops increment, then UXTH; DSP181 masks
7FFF and188/198 use bit15 for X/Y. Count0 performs no transfer but accepts.
Replies encode status2 accepted,3 invalid start,4 unsupported operation, plus
mode,cookie,address,count and4*count scratch bytes under response ID5E.
No stable function-return status ABI is established. Write branches do not
populate the read-response scratch payload; no intended semantics inferred.

**VERIFIED implementation detail:** private26A90 LDRB reads one byte per
4-byte slot;26A9A passes it unchanged to292F8.291E0 serializes31..8, so
the private DSP write word is zero. Shared26A74 and29336 each shift8,
giving transmitted word byte<<8. Read branches store32-bit helper returns.
Single-word backed service requests cover every candidate start5F00..5FFF;
private writes require the valid cached-cursor invariant, whereas scalar reads
explicitly program addresses. This is **SERVICE-ONLY OVERLAP**, not observed
or ordinary synth traffic. No wire request was constructed or transmitted.

**VERIFIED codec mechanics:**391C6 cross-byte shifts decode8 seven-bit bytes
into7;3924E does the reverse.256 deterministic full-group fixtures reproduce.
Large-length group counters truncate; the usual ceiling group arithmetic is
scoped to small lengths. The read scratch span[10,90) holds32 returns;
count32 reply140 bytes packs to160 in[90,130). This is conditional capacity,
not an enforced buffer/schema bound. Malformed/oversized behavior unproved.

**VERIFIED effect cursor producers found:** boot25E4→260A initializes eight
two-word pairs: Y[1820,1830) alternating2CCC/2CEC andY[1A10,1A20)2C02/2C24.
1F68/6A reads first two cells;1F89 reads each+32 cell over16 R6 increments
at1F8C. Initialized32/linear X footprint maximum2D0B (alternate maximum2C43).
Under linear setup,1F8C/98 write other Y state,1F13 outputs160 coefficient
words from1840/1A30, and1E6C ends1820 exclusively: local writes preserve
the pointer cells. **UNRESOLVED** global foreign Y writers, actual1E15 entry
and modifier invariant. M6's only explicit canonical writer is startup2780;
M3 has state-loaded temporary mode584 and restore5BE; M1/M7 also change.
No universal effects/scratch maximum is asserted from those local facts.

**VERIFIED selector7 publisher correction:**49C0A publishes Y2C.49BFC uses
mask7FFFF0 from49C30, adds7 before shift8; alternate49BF8 loads74000700
from49C2C. Both yield low nibble7. Index X:C00 is written at49BBC from
49A80's first argument. Sole recovered direct caller49A66 supplies0..63
through49A50/64/6C/6E.49BCC/49BDC/49BEA provideC01..C03 metadata.
DSP1CBB..C7 copies three words to1D8D+4*i: max written1E8B,end1E8C.
Thus the recovered publisher excludes high X under linear M1 and preserved
staging. Outer loader49A1C begins external cursor580000 and iterates64 inputs;
3CC46 caller/5BFD0 decode candidate retained separately. Its load/reload mode
ancestry and foreign/interleaved publisher closure remain **UNRESOLVED**.
The earlier hypothetical selector7 index105D is not a normal witness.

**Verdict:** X[5F00,6000) remains **UNRESOLVED / POTENTIALLY AVAILABLE** normal
after-init storage with **SERVICE-ONLY OVERLAP**. No normal occupancy witness;
no verified256/128/64-word region. All1/129/193 placements remain unproved.
No layout. Alternative search not triggered because neither disqualification
nor a single unavoidable static blocker is established. Do not rank another
range by absence of references. Producer/AGU and loader/transport closure may
still be static. Actual external request occurrence and physical part/alias
assignment would require independent observation/evidence if unavailable from
records; no dynamic action performed or claimed necessary for this service proof.

**VERIFIED final checks:** ten replay exports reproduce byte-for-byte in
builds/phase11/replay/ and replay-repeat/. Source syntax and overwrite/original-
subdirectory refusal checks pass (validation.json). Original SYX/BIN hashes,
CRC4E74DA9E, decode equality/exact roundtrip and all five stream/payload manifest
hashes remain unchanged. Created notes/host-utility-269e4.md and
tools/ct_host_utility_audit.py; updated dsp-high-x-audit.md,dsp-runtime-ownership.md,
plaits-poc-memory.md,research-log.md,todo.md. No original or binary writes.

**Single best next step:** prove normal preservation of Y[1820,1830) and
Y[1A10,1A20) plus entry modifier state at1F5C, using the recovered initialization
and actual reachable entries. An exact unclosed alias source is incoming
R7→X1D3B, reloaded1EEF and used for Y stores1F0D/0E; its destination could
change those cursor tables unless excluded. No such overwrite is demonstrated.
Convert the new low constants into a full normal
exclusion; do not repeat the classified service-capability audit. Readiness NO.

## Phase 12 — normal-only effect/scratch and reconfiguration audit

2026-10-06. Continued Phase11; static only. User-defined safety axes kept
independent: **NORMAL-RUNTIME SAFE NOT-YET-DETERMINED; SERVICE-ROBUST NO**
for X[5F00,6000). Service5E is explicitly not a normal allocation blocker.
No original/extract changes, hardware access, transmission, firmware patching,
Plaits implementation, installs or upstream refetch. Full report:
notes/dsp-effect-memory.md. Reusable tool: tools/ct_effect_memory_audit.py.

**VERIFIED R7 path mechanics:**1E15/17 save R6/R7 in X1D3A/B;1EED/EEF
restore them;1EF1 sets N6=2;1F01 loops X3A. With stock32 and linear addressing,
1F03 reads32 Y words at stride2,1F0D/0E write64 contiguous Y words. The
save containers do not imply X-space output. Reviewed algorithm wrappers
DBD/DC5/DCD/DEC/DF9 set (R6,R7)=(840,840),(800,880),(880,880),(880,9C0),
(840,9C0), respectively. If they select1E15, its output is Y[840,880),
[880,8C0),or[9C0,A00), excluding both cursor tables. Concrete legacy M7=3FF
keeps those starts in aligned[800,C00), also excluding the tables. **Conditional
caller-family result**, not an arbitrary/unbounded saved-pointer assumption or
proof that1E15 is actually selected.

**VERIFIED dispatch structure:** seven canonical indirect transfers:DB6,DBD,
DC5,DCD,DEC,DF9,19AC. Descriptor initializer28xx assigns twelve281 entries,
then202B and1A2B. ChainD87..DB6 uses X95A as a five-wrapper-row selector and
X95B..95F as indices into the55-word table X9DB copied from P29F6. Its first15
words are algorithm marker entries, remaining40 eight5-wrapper rows. The
algorithm wrapper advances R0 before calling it. Neither1E15 nor1E14 appears
in the initialized table; all+1 algorithm targets exclude1E15. Required normal
domains are95A0..7 and95B..95F0..14. INIT zero defaults satisfy them;
**UNRESOLVED** every normal indirect writer/index producer/table preservation.
No dead-code claim from absence of literal calls. Recovered normal parameter
intervals exclude X[95A,960),[9DB,A12),Y[1820,1830),[1A10,1A20), rechecked
without repeating the Phase9 callback analysis.

**VERIFIED modifier progress:** M3 temporary load584→restore5BE is a
branch/call-free segment; full canonical modifier references exported.
M6's only explicit modification is startup2780. M7's temporary3FF at265 is
restored27F; M1 has temporary modes and restored paths. **SOURCE-DERIVED**
legacy EMA=0 and concrete base/alignment premises remain explicit; global
Y1A indirect-writer and arbitrary-entry/callee invariants are not proved.
Known cursor init260A and local preservation from Phase11 remain valid.

**VERIFIED additional arithmetic bound:** C3E band mask700000 and signed24
y0 ASR17 yield N1/N3[-64,63] after cancelling ASL/ASR. With linear modifiers,
its lookup bases give conservative X read hull[15C0,1941), including1940
lookahead. It excludes5F00 without pretending valid presets use both extrema.
Selected1E15 tail X reads:[1D6D,1D8E) including prefetch,[2C02,2C22),
[2C24,2C44),[2CCC,2D0C); C9D fixed neighboring scratch hull[2C44,2CAA).
1FB2 reads32 X words from2D70 at stride2, maximum2DAE with odd-address holes.
Its EF2 helper uses low X0/1 and coefficient7D..84 under linear setup.
Bounded subset lowest0/highest2DAE; initialized indirect output highest2D0B.
**UNRESOLVED full normal effect union/max**, not renamed from this subset.

**VERIFIED concrete normal writer:** descriptorX14B selects202B.2035 starts
R0=35F;203A reads count and203B..3E four header words.2043 loads R4 from
X364+5*k;204B writes X:(R4) without an address clamp. Normal source record/
count/destination producers remain **UNRESOLVED**; no high-X/peripheral value
is established. This is a normal-only candidate/DMA proof obligation, not an
arbitrary service capability or a guessed whole-address-space occupancy.

**VERIFIED structured INIT map:**22F8..2308 consumes31 RLE records from2309.
Each contains X destination,run-count,then value/repeat pairs. All repeats
positive; every record expands1024 words; exact source end2599. Sorted output
union X[74000,7BC00),31744 words. This proves P[2309,2599) is data, including
the previously apparent DMA-register jset instructions. Encoding is startup
data expansion, not boot payload compression. Full record/run map exported;
no extract changed. External-memory interpretation remains conditional on the
documented hardware map; no availability inferred from INIT usage.

**VERIFIED direct DMA census:** after the RLE-data classification, all eight-
channel direct references are INIT setup/enable2A2D..3E or NORMAL fixed ISR
rearm1BC/1BE. Reviewed DMA0 writesY[29,2C), DMA1 readsY[21,24) and writes
fixed X peripheralFFFFA4. No direct normal reconfiguration targets private X.
**Complete normal indirect DMA exclusion NOT-YET-DETERMINED**, including
unclosed204B destination producers; no actual high-X DMA configuration proved.
Interrupt saves remain low Y/table snapshot low X; hardware stack separate.
Global other scratch maximum stays unresolved, not the highest known literal.
Private worker and shared-domain distinction unchanged.

**VERIFIED mailbox staging count:** ARM35F20 points80567EC; nine stride12
records each have halfword count256.35E28's16-bit512-byte upload stages
X[C00,D00). Recovered normal selectors0/2/3/4/5 use Y output; backups write
X[C00,E00), workspace[2400,2800), selector7 maximum1E8B. **VERIFIED recovered
publisher-family exclusion**, not universal context preservation while other
normal indirect writes are unclosed. Selectors1/6 have no recovered normal
publisher and also Y output. No high-X normal mailbox witness.

**VERIFIED reboot-entry census:**1F554 has one direct caller1F536 and no exact
entry pointer found.1F51E callers are boot1D582 and service consumers1F302,
26962/2698A/269AA; uploader29260 callers1F544/1F568. Existing reviewed code
classifies these roots; halfword/data candidates retained. DSP2779 clear enters
through25DE initialization, not ordinary block reset in the recovered graph.
Normal voice lifecycle/bank writes retain prior low bounds. Full patch/scene/
project and indirect-write/stream persistence remain **UNRESOLVED**; full DSP
reboot is distinct from block reset. No candidate-specific periodic clear proved.

**Allocation:** all1/129/193 placements of256/128/64 words retain normal
NOT-YET-DETERMINED, now solely for normal producer/AGU/persistence obligations.
Service5E is not the search blocker. SERVICE-ROBUST is independentlyNO; no
normal occupancy witness, available subrange, chosen allocation or layout.
Output2C46..2C65/readable-filter2C66 stays stock scratch.

**USER-REQUESTED conceptual service mitigations only:** prohibit5E while
custom state active; reject complete overlapping write extents including
space/wrap/aliases; consistent pause/snapshot/restore with separate safe
storage; or an allocation outside accepted domains if independently proved.
Conditional private X/Y RAM is inside the utility's private accepted window;
no-end-check means excluded starts alone do not prove alternate service safety.
No mitigation implemented or asserted established.

**VERIFIED final checks:**16 final exports reproduce byte-for-byte in
builds/phase12/final/ and final-repeat/. Syntax and overwrite/original-
subdirectory refusal checks pass (validation.json). Original SYX/BIN hashes,
CRC4E74DA9E, exact decode/roundtrip and all five stream/payload manifest hashes
unchanged. Created notes/dsp-effect-memory.md,tools/ct_effect_memory_audit.py;
updated dsp-high-x-audit.md,plaits-poc-memory.md,dsp-memory-ownership.md,
research-log.md,todo.md. Caller scans retained underphase12. No firmware writes.

**Single best next step:** bound the normal X364+5*k destination records and
countX35F consumed by204B, excluding candidate and DMA registers. Keep valid
effect-chain index/table preservation and all-mode persistence proofs separate.
Normal allocation and implementation readiness remain unproved.

## Phase 13 — scoped P204B destination/count reconstruction

2026-10-06. Static only. Created `tools/ct_indirect_204b_audit.py`,
`notes/dsp-indirect-write-204b.md`, and fresh evidence `builds/phase13/final/`.
Updated high-X, effect-memory, PoC-memory and todo. No inputs/firmware/Plaits
changed; no hardware, device execution or installation.

**VERIFIED consumer:** count X35F→203A→DO2040; five-word records begin360,
destination field364+5*k→R4 at2043.2048 readsX:(R4),204B writes one word to
the same unindexed address. R4 has no postincrement; M4 does not affect it.
The table walk requires retained linear M0 for364+5*k. The body preloads four
next-record words even in its last iteration. These are not proved dedicated
guards; hypothetical count20 reaches separate state3C4..3C7.

**VERIFIED producer correction:** ARM286BC shifts its input count by8 and
writes X2FA+172*bank at286DA. It then explicitly setsr1=0 at286E0 and sends
zero to X35F+172*bank at286E4. Normal27A10 supplies20 to the source-count path,
not to35F. Deferred286F6 supplies banks0/1. The recovered parameter sink
census has only286E4 inX[35F,3C4), with no compiled-record sinks. Census scope
is recovered parameter families, not every normal host write.

**VERIFIED INIT checkpoint:**2779..2789 clears X/Y[0,6000), so count and the
exported20 record positions are all zero immediately after clear. No local
RLE descriptor source was established. P[2309,2599) remains verified data,
with externalX[74000,7BC00) output; removed from instruction census.

**VERIFIED separate paths:**657 consumes source records2FB+172*b and writes
Y at690.1A70/1A89→1B89 smooths source field3 at2FE+172*b+5*i; it does not
write destination records360.1A99 uses3C4 as a source;1B90 writesR1, notR4.
28AC installs202B as its own scheduler descriptor, not twelve per-voice copies.
1BA8/1BA9 initializesY30=0; global foreign-writer closure is not asserted.

**SOURCE-DERIVED:** [DSP56300FM DO13-57](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf)
specifies zero-LC skip when compatibility SR13=0, versus65536 iterations in
legacy compatibility mode. [DSP56724RM Table5-2](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf)
marksSR14..12 reserved/reset0. This is distinct from StackCount `sc` and retains
the earlier actual-part/mode premise.

**VERIFIED conditional result:** preserved count0 in zero-skip mode gives an
emptyk/destination set; no204B overlap. **HYPOTHESIS:** the adjacent layout
accommodates20 records. No instruction-enforced20 bound or maximum valid k
is claimed. **UNRESOLVED:** foreign normal indirect writes preserving35F;
no nonzero producer recovered, and no universal proof from that absence.
Path collision **NOT-YET-DETERMINED**; overall **NORMAL-RUNTIME SAFE
NOT-YET-DETERMINED**, **SERVICE-ROBUST NO**. No persistent256-word allocation.
Existing independent selector/cursor/modifier/host/mode obligations remain.

Reproduction (fresh paths, refusal to overwrite):

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_indirect_204b_audit.py --output-dir builds/phase13/final
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_indirect_204b_audit.py --output-dir builds/phase13/repeat
```

Validation retains expected SYX SHA256bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd
and BIN SHA256b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da,
decoded equality, exact in-memory codec roundtrip and all five extraction hashes.
DSP listing and selected ARM listing bytes are checked against preserved payloads.
Static exhaustion **not established**: computed pointers alone do not prove
static impossibility. No observation was performed. The precise fact potentially
needed if static closure fails is35F at203A and provenance/destinations of any
nonzero publication across normal transitions; sampled observation would not
prove universal persistence. **Single next step:** targeted X35F non-alias/
preservation through already-open normal effect writers and host endpoints.

**VERIFIED reproduction:** both Phase13 runs completed; all10 generated
reports match byte-for-byte. `builds/phase13/reproducibility.json` contains the
comparison hashes. Both original hashes, all five stream/payload hashes,
decoded equality and exact codec roundtrip passed. No protection invariant
was inferred from those integrity checks.

## Phase 14 — count-word first-writer and alias ledger

2026-10-06. STATIC ONLY. Created `notes/dsp-x35f-invariant.md` and
`tools/ct_x35f_invariant_audit.py`; evidence `builds/phase14/current/`.
Updated204B/high-X/PoC/todo. No originals/binaries/extracts/Plaits changes,
hardware or packets, firmware execution, installation or implementation.

**VERIFIED census:**561 recognized X/L write operands outside established data
blocks;344 indirect,311 without complete global domains in this ledger.
Every unclosed entry retains pointer/modifier/count/range uncertainty, not an
actual normal alias witness. No absolute DSP35F write. Exact recovered ARM
parameter map has one35F sink,286E4, zero. Count-specific boot clear includes35F.
Separate channel1 worker census has no absolute35F writer; shared queue/private
address domains and earlier extent/map uncertainty remain separate.

**VERIFIED local zero-preservation:**26 store sites have reviewed zero producers;
four indexed bit clears also preserve a zero word on alias.1F6E/6F clear0,
whereas1F97 may write a MAC-updated word. **VERIFIED conditional induction
step:** fixedR0=35F at2035, unindexed count read203A, zero-skipDO2040 mean204B
cannot be the first nonzero count writer through recovered202B entry.
No circular assumption that destination records are already bounded.

**VERIFIED recovered entry:** startup28AC/28BC copies202B into descriptorX14B;
198D/19AC walks14 eight-word descriptors. No direct202B/203A edges; aligned
target202B appears onlyP28AD, count35F onlyP2036, no203A pointer word. Arbitrary
computed entry and descriptor preservation remain **UNRESOLVED**. Boot clear
does not dominate every later possible foreign write.

**VERIFIED new ARM count chain:**208FA loads [08020940]=2740C bytes;208FC→355E8
uses record20006990 fromliteral35670;355F2→47C54;47C64 stores length atrecord+4.
47C54 tests **minimum25800**, not maximum.395E0 obtains the same record via
literal3A2BC;395E4 loads its count,395E8 fixesE80000;395EC→48DAA→48E26 streams
even chunks<=4096 bytes. Payload13A06 words; two16-bit prefill words use
E7FFFE/E7FFFF; conditional union[E7FFFE,E93A06), no wrap or35F overlap.
Record/cursor/mode preservation and full entry ancestry remain **UNRESOLVED**.
39674's header40 branch alone is not normal/service classification evidence.

**VERIFIED service correction:** private5E→26A9A sends zero after upper24
serialization of its byte input. It can clear35F, not directly publishpositiveN.
It is not a normal invariant disproof; custom-state SERVICE-ROBUST staysNO.

**Precise unresolved nonzero alias:**1F89 loadsR7=Y[R6+32],1F93 readsX[R7],
1F95 MAC-updatesB,1F97 storesB throughX:(R7)+. With recovered1800/19F0 bases,
outer16/inner32 and linearM7, source cells areY1820..182F or1A10..1A1F;
35F is touched iff a cursor is in[340,360). Factory2CCC/2CEC/2C02/2C24 excludes
that interval. All normal foreign-writer/actual-entry/modifier preservation
is **UNRESOLVED**. No producer of a forbidden cursor or positivecount found.
Other possible aliases remain explicit; no claim this is the sole unknown.

**Invariant NOT-YET-DETERMINED**, no disproof.204B remains a high-X blocker.
The user gates candidate re-evaluation on VERIFIED, so candidate not re-audited
or re-ranked; previous normal NOT-YET-DETERMINED/serviceNO retained. No256-word
allocation or Plaits. Transition/asynchronous ledgers retain scene/project,
soft-reset, SHI saved-pointer and context uncertainty. Static exhaustion is not
proved; no runtime observation performed. **Single next step:** targeted1F97
Y-held cursor preservation against[340,360), with entry/modifier premises.

Reproduce with a fresh output directory:

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_x35f_invariant_audit.py --output-dir builds/phase14/current
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_x35f_invariant_audit.py --output-dir builds/phase14/current-repeat
```

Targeted ARM caller/pointer windows and arguments are recorded in each
arm-*/provenance.json. Existing Capstone used without installation. Canonical
DSP/ARM bytes, both baseline hashes, all five extraction pairs, decoded equality
and exact codec roundtrip are checked in each run. Comparison hashes live in
`builds/phase14/reproducibility.json`.

**VERIFIED Phase14 repeat:**14 reports match byte-for-byte. Both original
SHA256 values remain the supplied expected hashes; all extraction pairs,
decoded equality, codec roundtrip and byte checks passed. No input protection
or runtime invariant is inferred from report reproducibility.

## Phase 15 — P1F97 cursor-family bounds and stopping decision

2026-10-06. STATIC ONLY. Created `tools/ct_p1f97_cursor_audit.py` and
`notes/dsp-p1f97-cursors.md`; updated the35F invariant, high-X audit and todo.
Canonical evidence: `builds/phase15/verified/`. No original, binary, extraction
or Plaits changes; no hardware, packets, firmware execution/patch, installation
or upstream refetch.

**VERIFIED structure:** helperP[1F5C,1F9B), direct callers1E80/1EE5 from
parent1E15. Local R6 bases1800/19F0 are set at1E76/1ED9; R5 coefficient bases
1840/1A30, R4 state bases18E0/1AD0. CallerA followsX7C&0C==0; B follows the
later setup if the parent completes. Actual normal parent entry is **UNRESOLVED**.
1F97 performs a ramp-weighted X read/modify/write accumulation: A increments by
X1, Y0 receivesA, B readsX[R7], MAC addsY0*X0, store advancesR7. Stock outer16,
inner32 gives512 stores per call,64 distinct initialized addresses.

**VERIFIED32 initialized cells:**25E4→260A initializes eight pairs at261C/1D
and261E/1F. Y1820+j alternates2CCC/2CEC; Y1A10+j alternates2C02/2C24, j0..15.
Earlier2789 clearsY to0. Values are absolute X addresses by1F93/1F97 use.
1F68/6A reads the first two cells;1F89 reads each selected stage cell. No
stored cursor update: c_next=c_old. AdvancedR7 is never written back, so the
reviewed routine creates no block-to-block pointer drift.

**VERIFIED local preservation, with reviewed bases and linear modes:**1F8C
writesYbase..base+F;1F98 writesbase+30..base+3F (hex offsets). Coefficient/state
writes from1F13/C9D lie1840..195F or1A30..1B4F, outside cursor tables. C9D does
not useR6/R7/M6/M7/R0. Four state reads have net0 pointer change; four stores
advanceR4 by4. Its ten coefficient reads balance8*(+1)+2*(-4)=0 per DO body;
prefetch+1 and the caller's+4 advance to the next five-word set. Stock helper
DO usesX3B=16, distinct fromX3C=31; the canonical export corrects that premise
from the intermediate exports. C3E temporary Y writes[F63,F78) exclude the
tables and preserveR0. Detailed operand/interval proofs are exported.

**VERIFIED conditional X unions:**A[2CCC,2D0C); B[2C02,2C22) and[2C24,2C44),
retaining the two-word hole. M7=FFFF linear and the concrete3FF ring[2C00,3000)
produce identical32-address paths without wrap. **VERIFIED arithmetic:** a
32-word run overlaps[340,360) iff its base is in[321,360); it writes exactly35F
iff the base is in[340,360). Base321 reaches340 but not35F; base320 ends at340
exclusive. These fixtures are arithmetic, not normal-state counterexamples.
No initialized value lies in either forbidden window.

**VERIFIED limited publication lemmas:**16-bit SHI words have low8 bits zero;
no multiple256 lies in either forbidden window. A direct private5E cursor
write sends0, giving[0,20) in the preserved stock linear case. Neither lemma
protects other24-bit/DSP writes, base/count/modifier redirection or arbitrary
service activity.

**UNRESOLVED global preservation:** the recovered normal parameter Y map
excludes watched cells, but foreign DSP Y writes, normal SHI endpoints, saved
X1D40 state, entry/modifiers and physical alias/queue premises remain open.
Reused489 old foreign Y-write candidates for watched-cell obligations only;
these can include data decodes and are not489 proved normal aliases. No new
broad census. The valid immutable55-entry effect table/+1 set excludes1E15,
but index/table preservation remains open, so no dead-code claim. Reviewed
audio ISR low Y stores/saves exclude tables; SHI19B retains mutation capability.
No normal dangerous-cursor publisher was established.

**Both normal target/35F alias verdicts: NOT-YET-DETERMINED.** Initialized local
cases are VERIFIED NO. The family is not removed; the count invariant remains
NOT-YET-DETERMINED without a new broad re-evaluation. No high-X allocation.
Further broad static alias analysis has **diminishing returns** from current
state; static impossibility is not proved. Another broad phase is not justified
without concrete new producer/entry constraints.

**Observation proposal only:** minimum event=normalPC203A, effective load
address35F,24-bit value read. The family test addsPC1F97, effective X write
address and data; optional R6/source Y cell/cursor, M7/SR/caller/count attribution.
Read-only, nonhalting facility availability is UNRESOLVED. No debug port or
safe configuration is assumed. Future hardware actions require separate
authorization; no firmware logging/patches, active MIDI/SysEx or assumed-safe
halts/breakpoints. Finite all-zero coverage is not universal proof; passive SPI
alone or later RAM snapshots cannot exclude internal transient writes. If
suitable observation is unavailable, retain UNRESOLVED. **Single best next
step:** assess observation availability before any hardware action.

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_p1f97_cursor_audit.py --output-dir builds/phase15/verified
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_p1f97_cursor_audit.py --output-dir builds/phase15/verified-repeat
```

**VERIFIED repeat:**16 reports match byte-for-byte. Original hashes, all five
extraction pairs, decoded-BIN equality, exact SYX roundtrip and canonical DSP
bytes passed. Fresh paths and overwrite refusal retained. Observation JSON
contains logical requirements only, no device commands or execution.
`builds/phase15/reproducibility.json` records the report hashes.


## Phase 16 — static observation-path assessment (2026-10-06)

**VERIFIED:** service5E reaches ARM269E4 through1EB30→2484C→1F284→1F30A,
before the late Selection/service guard. Operation1 is READ;0 is WRITE.
Logical framing isF00020290163705E, packed body, F7. READ body12 bytes:
operation/selector/cookieLE32/addressLE32/countLE16. Reply body repeats
selector/cookie/address/count with status2/3/4 and left-aligned24-bit values
in LE32 slots. The codec is contiguous MSB-first7-bit grouping, not an MSB
prefix-byte scheme (391C6/3924E);37B0C constructs the reply envelope.

**VERIFIED:** count accepts16 bits without a local clamp; reviewed stack layout
fits32 READ words, not256.32 is conditional local capacity, not a certified
safe maximum. Encoder pads through complete7-byte groups by reading unspecified
tail bytes; malformed/oversized messages are not certified safe.

**VERIFIED:**29344/29504 issue address-read plus READNEXT through synchronous
SPI polling. DSP156..1B3 saves registers intoY2000..2005 and publishes flags
and advancing cursor toX11/X10. Those private RAM writes persist after RTI.
The second transaction returns the desired word while fetching the following
word; X5FFF consequently accesses6000. No strictly state-free5E observation.

**VERIFIED conditional model:**292F8 may reuse cached destination20003D00;
scalar29344 does not explicitly invalidate it. A service read can leave a
different DSP cursor for a following cache-hit normal write. Actual normal
interleaving/other invalidators **UNRESOLVED**; no runtime bug claimed.

**VERIFIED:** ARM completion/SPI loops are synchronous; SHI ISR preempts DSP
foreground, then RTI resumes. No reviewed explicit debug halt/audio-disable
or interrupt mask, but global side effects, timing, freshness and glitch-free
operation **UNRESOLVED**. Logical SysEx callback/routing recovered; specific
USB/DIN/proprietary physical driver chain **UNRESOLVED**. Components origin
remains **HYPOTHESIS**.

**Gate:** AYES, BNO, CNO, DYES, ENOT-YET-DETERMINED, FYES (client omission
of WRITE only), GNO. No hardware recommendation; no ct_read_dsp.py created.
Sampling targets/matrix, sparse-versus-chunk costs and a client architecture
are exported as blocked proposals only. Snapshots cannot prove every203A
entry, and unchanged zero cannot exclude transient or same-value writes.

**SOURCE-DERIVED:** primary DSP56724RM4.3.5 and DSP56300FM7.2.4–7.2.6
do not establish a compliant alternative: documented memory inspection uses
forced instructions/debug mode; flow trace is not private-RAM data trace.
Exact chip/board topology and any other passive facility **UNRESOLVED**.
Links and evidence are in dsp-readonly-observation.md and primary-documentation.json.

No invariant/allocation upgrade: X35F and normal high-X safety remain
NOT-YET-DETERMINED; service robustnessNO. Single best next step: exact-chip/
board documentation assessment of genuinely passive data observation.

Evidence: builds/phase16/final/; new targeted ARM windows underphase16;
canonical DSP listing and prior phase11 evidence reused without refetch.
Reproduce with a fresh output directory:

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_readonly_observation_audit.py --output-dir builds/phase16/repeat
```

All analysis remains STATIC ONLY: no port enumeration, transmission, service
execution, firmware patch, device-memory operation or Plaits work.

**VERIFIED Phase16 final checks:**14 reports in final/ and repeat/ match
byte-for-byte; builds/phase16/reproducibility.json records their SHA256 values.
Both supplied firmware hashes, all five extraction pairs, decoded-BIN equality,
exact SYX roundtrip, ARM/DSP byte witnesses and256 codec-group fixtures pass.
Existing-output refusal was exercised and rejected the replay without changes.
No original or firmware binary was modified.


## Phase 17 — exact debug/board/passive observation assessment (2026-10-06)

**VERIFIED local evidence:** existing DSP56300 disassembly, SHI/ESAI/ICC and
external-memory paths reused without new binary decoding or source refetch.
C++ emulator commit44353be2f0156cac970c6ab4f467ea1998b40605 and Rust toolkit
c60aeedb6a6014850204c71e53bc0cf5b3104222 remain pinned. Local source witnesses
exported with lines/hashes; no emulator build/execution/instrumentation.

**SOURCE-DERIVED:** DSP56724EC Table19/package figures:56724AG144-pinLQFP,
56725AF80-pinLQFP; candidate parts dualDSP56300. DSP56724RM chapter22:
two chained4-bitTAPs, percoreOnCE and configurabledebugcoupling. AN2073sec5
explicitly stops normalDSP56300operation forOnCE access; SC140EOnCE background
features not transferable. AN1839 memoryread example injectsMOVEP toOGDB and
incrementsR0; watchpoints/tracecounter enterDebugmode; flowbuffer12×25bit with
readpointer changes doesnot logeffectiveX/Ywrites. Citations with locators in
builds/phase17/final/citations.json and dsp-debug-observation.md.

**STRONG HYPOTHESIS:** actualDSPB56724AG. First-party CircuitTracksReverseEngineering
README lists56724AG,SDRAM/latch andTC2050-compatibledebugheader/J3references.
Indexed teardowncomment reports56725AG, not corroborated by datasheetTable19.
Exactpart/package/unitrevision andDSPpadcontinuity **UNRESOLVED**. Public
diagram/photo fetch failed; shellnetwork denied; no inventedpinout or hardware
fallback. Existing firmware compatibility doesnot prove physicalsilicon.

**VERIFIED source reading:** C++ reviewed SHI/ESAI/DMA models and configurable
single/parallelwrite routing provide a plausibleoffline basis. RustJIT inline
RAMstores bypassgenericwrite_memory. Completehookcoverage,56724peripherals,
initialstate,eventordering/interrupts/dualcore/DMAremain **UNRESOLVED**.
Decoder validation isnot execution validation. Finite modeled traces cannot
prove universalstockinvariants. Instrumentedfirmware isconceptonly/prohibited.

**Gate:** ANO,BNO,CNOT-YET-DETERMINED,DNO,EYES(conditionallymodeled),FYES.
SPIhostcapturecannot excludeinternalDSP-onlystores; ESAI/GPIO/ICCprovide no
completeprivatememoryproof. No qualifyingpassivestate facilityestablished.
Hardware staysdisconnected;5Erejected;X35F/high-XnormalNOT-YET-DETERMINED;
serviceNO. No allocation/Plaits work.

**Single bestnextstep:** staticcoverage/readinessspecification foroffline1F97/203A
replay, not emulatorimplementation/execution or moregenericaliascensuses.

Reproducible offline export (fresh output path):

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_debug_facility_audit.py --output-dir builds/phase17/repeat
```

Publicdocumentation consulted throughweb, no large tool/dependency installation.
No deviceenumeration,JTAG/OnCEconnection,MIDI/SysEx,5Eexecution,flash,patch,
device-memorywrites,originalchanges or emulator/difftestexecution.

**VERIFIED Phase17 reproduction:**9 final/repeat reports byte-identical;
builds/phase17/reproducibility.json records report and input hashes. Supplied
SYX/BIN hashes, all five DSP extraction pairs, decodedBIN equality, exactSYX
roundtrip and local source-witness assertions passed. Original files remain
unchanged. These are offline integrity checks, not emulator execution tests.


## Phase 18 — minimal offline DSP replay design (2026-10-06)

**VERIFIED local source:** C++ commit44353be2f0156cac970c6ab4f467ea1998b40605
supports forced interpreter; chosen for firstimplementation over RustJIT.
GPLv3/MIT sources and existing build dependencies compared without build/refetch.
DO internally calls interpreter; REP subsequentiterations callcached opcode
directly; DMA memcpy/fill paths can bypass perword writes. Fullinstrumentation
needs explicit perinstruction/transaction coverage beyond generic hooks.

**VERIFIED reused stock evidence:** Selection0/channel0 P[0,2A5E), entry0→100,
3E→1B4 and44→156; workerP[0,16C). Startup107/108zeroSP/SC,2779M=00FFFF,
X/Y attempted6000clear/shared8000clear,fourP→Xcopies,cursorinitialization and
14schedulerdescriptors exported from bytechecked canonical listings.
203A occurs via X14B→202B during descriptorrequest pass;1F97 belongs to1F5C,
parent1E15 normalreach stillunresolved. No inventedlinearstage sequence.

**SOURCE-DERIVED conditional map:** DSP56724RM Tables3-3..3-6 reconfirmed:
proposedcore0 P4000/X6000/Y4000 andcore1each2000 words under declaredmode.
StartupY[4000,6000) behavior remainsUNRESOLVED; donot enlargeRAM/ignorestores.
Post-uploadSR/OMR,EMCcommands/hosttables andworker state are explicitgates.

**DESIGN only:** unified actor/space/core bus and canonicalalias backing,
allstores including samevalue/parallel/P/DMA/host/worker, selective readfilters,
203Aentry+actualread,1F97EA attribution, deterministic virtualevents/traceSHA256.
Normalhostword events follow recoveredARMprotocol, noexternalMIDI/UI emulation.
Six normal scenarios andseparateconditionalunitfixtures designed, NOTRUN.
WorkerB derivedadapter preferred if lookup/progress/handshake fidelity agrees;
otherwise realstockworkerA orSTOP. No instantcompletion/missingtablezeros.

**Validation planned, not executed:** ISA/arithmetic,AGU/DO/REP0,stack/IRQ,
storepathcoverage,stockcopies/cursors/phase/sampleloops,static-vs-trace first
divergence,determinism andtargethitcoverage. Firmware modifications remain
prohibited. No allocation/X35F invariant upgrade; bothnormalNOT-YET-DETERMINED,
serviceNO;hardwaredisconnected/5Erejected.

**Implementation sequence:**19A core/bus/hooks/tests;19B stockstartup;19C
scheduler/peripheral/workercontracts;20 validatedstockreplay. ESTIMATE2stages
to validatedstockprefix,4planned tointegratedtargetreplay, subjecttogates.
**Singlebestnextstep:**19A onlyafter explicitimplementationinstruction.

Created dsp-emulator-spec.md,dsp-replay-scenarios.md,dsp-emulator-validation.md;
updated debug/invariant/high-X/log/todo. Offline evidenceexporter:

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_replay_spec_audit.py --output-dir builds/phase18/final
```

This exporter produces specifications/source and DSPbyte witnesses only,
not a replayharness. No hardware,emulatorbuild/run,firmware/DSPexecution,
modifiedfirmware,MIDI/SysEx,OnCE/JTAG,flashing,originalchanges orPlaits work.

**VERIFIED Phase18 export reproduction:**15 final/repeat reports byte-identical;
builds/phase18/reproducibility.json records their hashes. Firmware SHA256,
all five extraction pairs, decoded-BIN equality, exactSYXroundtrip and bytechecked
DSP/source witnesses pass. This is evidence-integrity verification only; all
proposed emulator execution/validation tests remain NOT RUN.


## Phase 19A — first offline emulator implementation (2026-10-06)

**IMPLEMENTED:** localcopy of core44353be2f0156cac970c6ab4f467ea1998b40605,
forcedinterpreter headlessharness and authoritative P/X/Y/shared fixture bus.
Exactsmall missingAsmJit3577608cab0bc509f856ebf6e41b2f9d9f71acc4 fetched;
existing MSVC19.44.35228/CMake/Ninja/SDK used, no toolchain install.
Independent Debug/x64 C++17 builds succeed; binary hashes differ withPDB/path
metadata, deterministicfixturetraces match. No JITDSPexecution/instrumentation.

RAM/fetch overrides, CPU opcode callbacks, explicitREPiteration hooks and
scalarizedDMA memcpy/fill paths implemented. Standard memorywrite-only hook
was insufficient. MSVC read/write template ambiguity resolved byexplicitnull
specializationargument, noinventedISAencoding. CanonicalJSONL logs same-value,
CPU/AGU/parallel/loop/P/DMA/actor stores; watches/faults/registersnapshots added.
Rn attribution remainsnull whereambiguous. Fixtures are synthetic, finalP400;
earlier exploratorysyntheticP100 wasnever Circuit stockcode.

**TESTED:**34 fixtures ×4runs across2independentbuilds, allpass. REP4 stores;
DO3/offset/nested2×3;M3 modulo4 wrapbothdirections;linear/pre/post/indexed;
parallel2spacewrites;samezero writes;DMAcopy/fill/fixed/P/shared/controller;
vector20→handler600→RTI PC/SR/SPrestoration;invalidCPUread/write/peripheral;
configuredYsizefault;readwatch;actorbus. Pstore077084000040 independently
decoded with existingRustdisassembler asMOVEMx0,p40. CanonicaltracesSHA256
andprotected/binaryhashes inbuilds/phase19a/reproducibility.json.

**VERIFIED source/integrity:**203 sourcefilesregistered plusharness/build/test
hashes; restoredDMAfastpaths/changed/newsource failreviewguard. A negativesource
copy addinganunregisteredstore.cpp wasrejected;live/vendor/firmwareuntouched.
Exactlocaloverlays reproducedindependently. OriginalSYX/BIN/all5extractionpairs
retainknownSHA256. Reviewdiff normalizeslineendings;overlays preserveexactbytes.

**UNRESOLVED outsidefixturemode:** fullISA/legacySRmodes,stockinitial/map/ROM,
YclearoutsideRAM,EMC/hosttables,workerICC/CircuitDMA/ESAItiming,external/rawpointer
APIs andJIT. No stockstartup/scheduler/image ormodifiedCircuitDSPexecution.
All19Agatespasswithsupportedmode scope; no normalownershipproof/allocation.
Singlebestnextstep: separatelyrequested19Bimmutablestockload/entryprerequisites,
notautomaticstartup. X35F/high-XnormalNOT-YET-DETERMINED,serviceNO.

Created notes/dsp-emulator-phase19a.md anddsp-emulator-write-paths.md; implementation
andtests underemulator/; canonicaltracesfinal/ and repeat/ underphase19a.
No hardware,MIDI/SysEx,OnCE/JTAG,flashing,originalchanges orPlaits work.


**Phase19A final coverage extension:** tested the remaining active DMA fill/copy branches: P-destination fill, peripheral-source repeated-read fill and peripheral destination copy. All37 fixtures pass in4runs across2independent builds. Canonical outputs are builds/phase19a/validated/ and validated-repeat/; reproducibility-final.json supersedes the interim34-fixture report. Source/harness registry updated after review and positive audit passes. No stock execution or firmware changes.

## 2026-10-06 — Phase 19B immutable stock load and handoff audit

**IMPLEMENTED / TESTED / MATCH:** new separate load-only executable under
emulator/stock reuses the unchanged19A source/build recipe, with forced interpreter
configuration. Exact original Selection0/channel0 payload SHA256
b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855 is checked before
loading;32538 bytes become10846 BE24 words in P[0,2A5E). The boot stream's two
metadata words are excluded. Stream SHA449c347018a7f318f6eede928446a341f2d3d7d41eb7f2e18d6c71a90d42efb4
and BIN offset1F0..8110 linkage match the existing extraction manifest.
All10846 P words read back identically through core Memory API. Const original
bytes/file are separate from mutable P bus state; no source write API is used.

**VERIFIED load decoding:** native decoder on actual loaded P matches16 existing
instruction boundaries/bytes and direct targets 0→100,3E→1B4,44→156,106→102.
No instruction was executed. Three initializedness guards deny X0,Y0 and unloaded
P2A5E reads. Canonical load/probe/gate exports completed and completed-repeat
are21 byte-identical files; three negative safety tests pass (synthetic wrong
identity, existing output, out-of-phase output). Source guard still verifies203
core files and all sealed19A harness files. Protected SYX/BIN/stream/payload
hashes remain unchanged after each load and negative tests.

**SOURCE-DERIVED authoritative reset evidence:** archived official NXP
DSP56300FM Rev5 and DSP56724RM Rev1 and exported selected text/layout pages/hashes
under builds/phase19b/documentation/verified. Family reset specifies M=FFFFFF,
SP/SC/VBA=0; device SR diagram specifies C00300 and OMR CDP=3 plus mode-pin nibble.
Other scratch numeric reset contents were not established; EP/SZ are explicitly
not initialized. No invented zero defaults. See dsp-boot-handoff.md for exact
sections/URLs and per-register classification.

**EMULATOR VERIFIED, not stock state:** separate constructor-only empty-program
probe shows PC/OMR=0,SR=C00300,R/N=0,M=FFFFFF,SP/SC/VBA=0,accumulator/loop/stack
implementation zeros,SZ=BADBAD. **MISMATCH if reused as DSP56724 reset profile:**
SHI reset PCFFFFFE and OMR priority bits differ. The constructor probe permits
only its explicit reset priority-register zero writes, never stock peripheral
operations. Initial development first/ failed at that probe adapter (no stock
CPU/instruction); completed outputs supersede intermediate directories.

**VERIFIED static startup dependence:** ARM sends bootstrap, then main, then
worker. Bootstrap sets OMR7/22,clears21 and jumpsFFFFFE; subsequent ROM handoff is
not proven reset. Stock P100/101 access GPIO control/direction; P102 reads
YFFFFD4 and104 compares030002. Device manual identifies this as ICDR4 reflecting
peer ICDR3; existing worker P109 publishes030002 toYFFFFD7. This is an anticipated
dependency only: worker was not loaded/run, no fake completion supplied.

**UNRESOLVED / execution BLOCKED:** post-ROM live SR/OMR/loop/interrupt state,
GPIO handoff,ICC event/worker timing,conditional Y4000..6000 clear extent,
EMC/external accesses and ARM table readiness. **0 stock instructions; original
DSP firmware successfully executed offline: NO.** Clear/table/cursor/descriptor
results NOT REACHED; no stock runtime peripheral faults, execution mismatches or
execution-determinism result. Tagged unknown CPU/X/Y hashes are partial-state
representations, not actual executed final register/RAM images. Watch logs empty;
X35F/high-X ownership remains NOT-YET-DETERMINED.

Reproduction: emulator/stock/build.ps1, tools/ct_stock_load_audit.py,
emulator/stock/verify.py and tools/ct_dsp_reset_docs.py; exact commands andA–P
report in notes/dsp-emulator-phase19b.md. Created that note plus dsp-stock-startup.md
and dsp-boot-handoff.md; updated spec/validation/todo/log. Only official reference
manuals downloaded; no upstream refetch or new tool install. No hardware,
MIDI/SysEx,OnCE/JTAG,flashing,binary patch,original changes,Plaits or scheduler.

**Single best next step:** establish the minimum documented post-ROM
handoff/GPIO/ICC contract for P0→100..106 before enabling any stock execution.
Further separately authorized contract work is justified;19C was not started.

## 2026-10-06 — Phase19B-HANDOFF, minimum state and peer publication

**VERIFIED:** byte-checked five original instructions100/101/102/104/106 and
their seven words; existing decoder re-decoded the original main/worker/bootstrap.
Explicit early operands require no stack or R/N/M addressing; inherited loop/
interrupt state is still a separate prerequisite. P0→100 entry is boot-record
derived, not constructor-derived. No original instruction was executed.

**DOCUMENTED:** candidate-device PCRG YFFFFFA and PRRG YFFFFF9 reset0001E1,
R/W mask3CFFEF. These are control latches, not pin samples; no read-clear
configuration side effect described.100/101 configuresbit13 output. GPIO
post-ROM words and actual output latch/board pin wiring remainUNRESOLVED;
no board-level input sample is needed for these configuration reads.

**VERIFIED bootstrap:**30-byte SHI record has6 metadata bytes and24 code bytes;
count8/load0; seven instructions, final two-wordJMPFFFFFE. X0/OMR are modified
byset7/set22/clear21; finalC=oldOMR.bit21. OtherSR bits are explicitly untouched,
as are stack/AGU/peripheral/ICC/shared registers in the body. This does not
establish preservation through either ROM pass. No bootstrap execution occurred.

**VERIFIED static ICC value role:** originalworker105R5=30002,107X30000=R5,
109YFFFFD7=R5;121/128 later publish progress after queue processing. Main102
readsYFFFFD4 and104/106 polls for equality30002; main779 consumes progress too.
Value is initial shared-queue cursor/progress pointer and startup rendezvous,
not an arbitrary command token. **DOCUMENTED:** peerICDR3 reflected inICDR4;
receive read clears correspondingIF and acknowledges maskable transfer viaACK.
Exact disabled/empty ACK transitions remainUNRESOLVED, no fabricated stub.

**VERIFIED ARM ordering:** uploadcalls29284bootstrap,29294main,292A6worker.
Mode0 documentation starts each program atloadP0. First main102 versus worker109
interleaving remainsUNRESOLVED; no seed30002 atmainhandoff. Physical endpoint-to-
core numbering still conditional. Originalworker109 source identity is verified,
but worker execution gate fails earlier unmodeledperipheral/control prerequisites.

**UNRESOLVED ROM source:** existing NXP manuals supply reset/boot/data-register
contracts, not a complete reviewed ROM exit snapshot. Targeted searchfound
publicDSP56725-bootloader NXPforum thread reporting support-supplied source; it
is a discovery lead only. Web opens failed and directpublicpage returnedHTTP403;
no attachments retrieved, source trusted, access bypass or supportmessage sent.
No unrelated-familyROM can substitute. No core/source/tool refetch or installation.

Created dsp-rom-handoff.md,dsp-bootstrap-analysis.md,dsp-icc-startup.md; updated
19B handoff/startup/report/validation,todo/log. Tools ct_handoff_contract.py and
ct_handoff_verify.py export reproducible offline evidence; emulator/stock/
handoff_gate.py inspects explicit provenance only, withPC0 as sole eligible
numericassignment. All otherhandoff fields null; guessedSR/GPIO/ICC/execution
enable rejected. Canonicalfinal/final-repeat andchecks underphase19b-handoff.

**Execution decision:** longestcurrentlydefensibleprefix0; main/worker/bootstrap
execution0.19B2gateA/E/F NOT-YET-DETERMINED,B/G/H NO,C YESconditionalpairing,
D YESuploadorderonly. No controlledstartupresumed or19C/scheduler/Plaits work.
Originalinputs preserved; no hardware,MIDI/SysEx,JTAG/OnCE,flashingorpatching.
X35F/high-X normalownership remainsNOT-YET-DETERMINED.

**Single best next step:** acquire authentic matching DSP56724/25 ROM loader
source/listing and statically audit SHI reset/re-entry exits forliveSR/OMR/IRQ
andPCRG/PRRG before authorizing any original stock micro-execution.

## 2026-10-06 — Phase19B-ROM public recovery and documentary comparison

**VERIFIED recovery observations:** knownNXPthread nowloads in normalin-app
browser, anonymously/read-only. Its DOM has noattachment/download/ASM/TXT/ZIP
links. PublicattachmentsAPI returnsCLI403/browserblocked; currentarchiveindex
empty andavailabilityAPI nosnapshot. HistoricalFreescaleindex requests timed
out. This is notproof sourceisgloballyabsent. No login/securitybypass/private
state inspection/supportmessage occurred; temporarybrowser tabclosed.

**ROM source NOT RECOVERED:** filenames/revision/date/hash remainunknown. Forum
reports ofsupport-supplied56721/25 equivalence areUNRESOLVEDleads, nottrustedcode.
No actualROMsource/binary, exitPC/opcodes/clobberlist orconditionals inspected.
No speculativeexecutableROM reconstructed from bootformat: that contract does
not uniquely determine CPU/peripheralresidue.

**DOCUMENTED:** archivednewofficialDSP56720RM Rev1.1(02/2008), compared with
existingDSP56724RM Rev1(02/2009). BothDSP56300coresCOMPATIBLE; reviewedSHI
XFFFF90..94mappingIDENTICAL; ICCpeerpairingCOMPATIBLE; PCRG/PRRGmapping/reset
IDENTICALforrevieweddiagrams. RAM/extraHDIhostmodesDEVICE-SPECIFIC. Mode110
56721P6000/X9000/Y8000 differs56724core0P4000/X6000/Y4000 andcore1all2000.
No wholeROM compatibilityverdict fromthese sharedregisters.

**SOURCE-DERIVED candidate fact:** main2A5Ewords exceed56724core0defaultP1000,
fitconfigured110P4000; original8wordshim setsmodeand reentersROM. Itsrole is
mode-setter/ROMreentry, notactualSHIloader. Post-ROMmodepreservation/actualsilicon
stillunproved. Mainhas twoROMpasses separatedbyshim; workeronepass/no uploadedshim.
Worker100 writesHCSR0,HENdisabled, notwholepost-write statuswordzeroproof.

Created dsp-rom-loader-source.md; updatedhandoff/bootstrap/ICC/startup/log/todo.
Publicfetchtwo scripts andofflinect_rom_exit_audit.py exportsourcecatalog,
documentwitnesses/applicability,abstractexitlimitations,timeline,peripheral
unknowns,main-handoff.json/worker-handoff.json andclosedgates underphase19b-rom.
OnlyPC0 has sourcedexplicitassignment; unknownregisters/peripheralsnull, nozero
defaults. Stagedrealworker/mainrendezvous remainsHYPOTHESIS/design afterfuture
gates; no realpublication/ACK/branch tracegenerated.

**BLOCKED primary goal:** exactROMexitstate remainsUNRESOLVED; main/worker
entrygatesNOT-YET-DETERMINED, reachedperipheralmodelsunqualified, firstexecution
NO.0 originalmain/worker/bootstrapinstructions.19B2notresumed; no19C/audio/Plaits,
hardware,MIDI/SysEx,flashing,binarypatch/originalchanges. Newmanualdownload only;
no toolinstallation/core/vendorrefetch. Protectedinputsretainhashes.

**Single best next step:** obtainofflinehistoricalsupport-sourceattachments or
authenticmatchingROMlisting, validatevariant/revision, thenauditSHIexitstate.
Repeatingpacket-format inference cannot supplymissingauthenticROMinstructions.

**TESTED Phase19B-ROM final integrity:**13 canonicalfinal/final-repeat reports
match byte-for-byte. Manifestprovenance/nullunknown/closedgate checks pass;
protectedSYX/BIN andalltenextracthashes unchanged;19A203-file/harness guard passes.
Reproductiontoolct_rom_verify.py; checks/reproducibility.json. No execution
determinism, ROMexitopcode validation or authenticstockcoverage was obtained.

## 2026-10-06 — Phase 19B-SYMBOLIC partial state and dependency frontier

**IMPLEMENTED / TESTED:** new partial_state.py/symbolic_startup.py under harness/
and24 focused tests.24-bit masks/values/provenance represent sets, not guessed
zeros. BCLR13 defines0, BSET13 defines1, unrelated unknowns are preserved, and
carry is oldbit13. Equality can prove false from a known mismatch; undecided
branch/address/count/modifier uses stop. Concrete core/defaults unchanged.

**SYMBOLIC:** qualified GPIO local operations evaluated, not full CPU execution.
Interrupt control fields admit at most32 completions; known absence or ordinary
mask exclusion makes some bits irrelevant. Nonmaskable priority3 still passes
mask3. ICC data/IF/ACK/enable are unknown before sourced publication. A qualified
synthetic enabled transfer writes123456, then pending/read/flag-clear/ACK; no30002
injected. Empty/disabled/overrun behavior remains unqualified and stops.

Bootstrap temporal OMRmask600080/value400080 is retained before second ROM;
final carry is incoming first-ROM OMRbit21, not a proven literal0. No exclusion
of second-ROM clobber was recovered, so these become historical provenance,
not current handoff seeds. Low P entry mapping does not need full OMR; explicit
100..106 does not use R/N/M/stack. Reviewed SP/SC/R0/workerR5 definitions are
recorded separately from inherited IRQ/loop prerequisites.

**BLOCKING true use:** ROM-exit pending/PIC request IPL/SR.I -> interrupt
eligibility -> next original instruction vs ISR before P:0. Both originals stop
with0 instructions; the requested main100 profile also stops. Actual source
bytes/hashes used; no empty queue or concrete stock register seeds. No eligible
interrupt, worker publication or main receipt occurred. User's one-original-
instruction success criterion was NOT MET. Loop/SA/peripheral/full CMP limits
are deferred frontiers, not demands for every incoming register to be exact.

Created dsp-symbolic-handoff.md/dsp-partial-state-model.md; updated requested
handoff/startup/report/validation/log/todo. Exporter ct_symbolic_startup.py writes
blocking traces, partial masks, local transfers, ICC contract, temporal history,
first-use ledger, tests/source/input hashes under phase19b-symbolic final/repeat.
Test duration text is excluded from canonical comparison. No ROM search/network,
hardware/MIDI/SysEx/flashing/patches/original changes/modified DSP execution/Plaits.

**ROM-listing necessity:** a full listing is not uniquely necessary; a weaker
authoritative no-delivery or mask/pending contract can decide the predicate.
Current evidence cannot. No ignore-IRQ mode was used to claim progress.
Best next step: establish that narrow live interrupt contract, then re-evaluate
the loop guard; no controlled startup/scheduler until material gates pass.

**TESTED final symbolic reproducibility:**24 focused tests pass;16 canonical
files in verified/ and verified-repeat/ are byte-identical. Earlier final/
exports precede added field-bound guards and expanded scratch/stack ledger.
The test duration text is explicitly excluded. Original SYX/BIN/allten extracts
retain expected hashes; sealed203-file concrete core/harness guard passes.
`tools/ct_symbolic_verify.py` and checks/reproducibility.json record verification.
No authentic execution count changed and no guessed control state was added.

## Phase 19B-IRQ — 2026-10-06

**UNRESOLVED interrupt-exclusion/convergence contract; original main0 / worker0.**
See `notes/dsp-interrupt-handoff.md` and `builds/phase19b-irq/final/`.

DOCUMENTED: PIC field00 is disabled,01/10/11 select IPL0/1/2; SR.I is bits9:8.
The always-on source at VBA+FC needs no external event when enabled. ICC NMI
and DMA-stall are IPL3 sources; ordinary mask3 alone cannot exclude them.
The SHI mode0 description specifies loading/entry, not a reviewed SR/PIC/FIFO
cleanup or interrupt-pipeline contract. No post-ROM reset value was promoted.

VERIFIED conditional on VBA0: main vector44 JSR156 writes Y2000..2002 and can
write HRX through inherited X10 to X/Y RAM; main vector3E JSR1B4 writes RAM/DMA.
Other nonreserved main vectors and every nonreserved worker vector are NOP/NOP.
Fast NOPs do not prove persistent peripheral requests clear or finite convergence.
VBA0 itself is not established after ROM. Upload order does not prove the exact
cross-core entry/publication interleaving. No 30002 was seeded.

SYMBOLIC source/vector classes are conditional architecture classes, not verified
reachable ROM exits. Exact first fetch also depends on pending/already fetched
interrupts and documented pipeline timing. The abstract field predicate alone
is insufficient. Loop inheritance remains deferred because IRQ resolution failed.
No stock or handler instructions executed; no scheduler replay enabled.

TESTED:16 canonical files match final/final-repeat;24 existing partial-state
checks pass;16 PIC/SR predicate cases pass; protected SYX/BIN and all ten DSP
extraction hashes match; sealed203-file concrete-core/harness guard passes.
Evidence: builds/phase19b-irq/checks/reproducibility.json.

The next prerequisite is a matching authoritative final SHI ROM-exit fragment
or handoff guarantee covering effective interrupt state/pipeline and VBA,
including second ROM entry. A full register dump is not required. Previous
phase gates and X35F/high-X ownership verdicts remain unchanged.

## Phase 19C-CHECKPOINT — 2026-10-06

**TESTED / BOUNDED-PROOF:** original-opcode address-only checkpoint slices are
implemented using the sealed Phase19A interpreter and authoritative memory hooks.
See notes/dsp-checkpoint-replay.md and notes/dsp-checkpoint-state.md.
Canonical traces: builds/phase19c-checkpoint/final/ and final-repeat/.

4164 cases execute24656 original opcodes per invocation:24576 at1F92..1F97,
64 cursor loads at1F89,14 zero-consumer instructions at203A..2040, and2
single204B consumer-calibration instructions. Unknown arithmetic/store data
remains SYMBOLIC/null. Numeric backing encodings are not stock values.
No authentic boot, full1F5C/1F90 DO loop or positive-count consumer loop executes.

The32 initialized cursor cells and each32-address body projection reproduce
X[2CCC,2CEC),[2CEC,2D0C),[2C02,2C22),[2C24,2C44), for M7FFFF/3FF.
There are no cursor-slice writes to X35F, X[340,360) or X[5F00,6000).
Both initialized-zero203A entries read35F0, load the four initial fields and
perform the Y prefetch before DO0 skips204B. One-word204B behavior is calibrated
separately with cleared destination0; no normal positive producer is invented.

These are PROVEN FOR CHECKPOINT DOMAIN address properties, not universal stock
invariants. Isolated slices do not replay inherited loop edges/stack/call paths
or async interference. Cursor/count/record/modifier preservation and parent
reachability remain UNRESOLVED. No family is removed from the universal blocker
set. X35F normal invariant / persistent high-X availability remain
NOT-YET-DETERMINED; service robustness remains NO. No Plaits PoC gate passes.

TESTED:13 canonical files identical;6 schema tests;5 native refusal gates;
protected original SYX/BIN and all ten extraction hashes intact; sealed203-file
core plus existing19A harness guard passes. Linked-library/binary hashes are
exported separately. Evidence: builds/phase19c-checkpoint/final-checks/reproducibility.json.

Next: qualify the complete1F5C nested-loop checkpoint stack/control relation
and symbolic-data interface to join the isolated body slices through original
DO/call instructions. Do not invent stack defaults or turn this into a ROM
search, hardware session, firmware patch or automatic scheduler replay.

## Phase 19C-FULLHELPER — 2026-10-06

**TESTED / BOUNDED-PROOF:** complete original P:[1F5C,1F9B) helper and
P:[C9D,CB8) callee now execute as joined control flow, including the real
caller JSR at1E80/1EE5 and natural return to1E82/1EE7.
See notes/dsp-full-helper-replay.md; canonical exports are
builds/phase19c-fullhelper/final/ and final-repeat/.

The admitted class is explicit: initialized caller pointers/counts/cursors,
retained M0..6FFFF and M7FFFF/3FF; healthy resident SP=SC=d, d3..7 before
caller; inactive LF/FV; opaque prefix and incoming LA/LC. These depths/flags
are SYMBOLIC finite structural class bindings, not recovered actual stock
stack values or normal-runtime invariants. Other/active/extension-dependent
classes refuse; no guessed ROM or reset stack is used.

40 cases per invocation execute385880 original opcodes,9647 per case
(including one caller JSR). Original DO yields16 contexts x32 stores at1F97,
64 initial clears,32 C9D calls and returns,66 DO executions. Complete helper
per case writes1728 X words and160 Y words. Actual LC countdowns, address
ordering, return frames, peak d+6, restored depth/LA/LC and unchanged opaque
prefix all match. Cursor words remain unchanged; all body intervals match
Phase19C-CHECKPOINT. Numeric arithmetic data/results remain SYMBOLIC/null.

PROVEN FOR CHECKPOINT DOMAIN: no read/write to X35F, X[340,360) or
X[5F00,6000). This is not an incoming-zero proof or universal ownership.
No natural helper-to203A chain or positive-count publisher is established.
Actual normal parent entry/stack/loop class, foreign mutations and async
interference remain UNRESOLVED. Universal X35F invariant/high-X persistence
and service robustness verdicts remain unchanged. No persistent Plaits layout
or firmware-implementation gate passes; only explicitly hypothetical design
assumptions remain possible. No Plaits work was performed.

TESTED:11 canonical exports match byte-for-byte, including full traces,
watched accesses and final symbolic CPU/X/Y state. Seven refusal gates pass;
protected SYX/BIN and all ten extraction hashes match; sealed203-file core
and19A harness source guard plus validated19A binary identity pass.
Evidence: builds/phase19c-fullhelper/checks/reproducibility.json.

Single best next step: resolve actual normal reachability and stack/loop entry
of parent1E15 feeding1E80/1EE5, connecting the local structural class to a
specific normal path. Do not artificially join203A or launch broad alias,
ROM-source, hardware, scheduler or Plaits work automatically.
# Phase20B5-SEQUENCE — final static checkpoint association attempt (2026-10-07)

Overall **PARTIAL**; **STATIC STRATEGY EXHAUSTED**. Source evidence and every
bounded consumer discovery recorded in project0-sequencer-ordering.md with
instruction addresses/offsets; event gate in project0-first-note-context.md.
Existing20B4 macro arithmetic/seven-byte and20B3P657 record reused unchanged.

**VERIFIED:** AF46 literal0→1FD34/1FD84→2E2D8/2E35C→3F1F0 child+48
group pointer; separate2D7C4/3CF58 editing object. Eight3240-byte patterns,
32*28-byte step region,40-byte header/gap and12*32*6-byte automation region.
3DC34..56 loads header15/0/3 without proving active length.3F350..384
uses six occupancy bits and compares key/substep;3F856..89C writes encoded
duration(subdivisions),substep andseven-bit level.3F1F0 passes12 parameter
lanes to base while139 initializes a separate note-key state domain.
Vtable805A5B4 resolves note recording/automation methods;2520A is a stub.
1D02A yields source+CA8*pattern+C0*lane+3A8.3FC20 stages pending values;
3FE24 gates on retained sources/state.3FF0E calls400A4 before3FF1A calls
40188 in the same pending branch.400A4 writes mean/third-weight values with
FF handling;40188 writes current record and prior state. These are storage/
recording paths, not proven audible-playback chronology.8059080 pairs0..7
map group0/lane0..7;8/9 mapFF. No inferred callback/lane semantics.

**MEASURED:** step0 mask03, occupiedrecords51/18/0/106 and82/2/0/106;
same encodedsubstep0, not admitted as first audible event. Automation lanes
2/8/9 contain52/53/15 nonFF bytes; othersallFF. First-step lane8=1,4,7,12,18,22;
lane9=127,FF,FF,FF,FF,FF. Full raw record map exported. **HYPOTHESIS:** header15
may mean16 steps; active length staysnull. **UNRESOLVED:** actual first event,
track sound route, active load branch, automation application order/value,
allocator slot andY91/numerical histories. **CONDITIONAL CALCULATED:** previous
stored-context material differences unchanged; event equivalence insufficient.

**VERIFIED reused seam evidence:** selected post9D9 after original32-word
generation, before9DD; groupA82..88 choosesX2DF0 or2E50 according toXCC,
A8E reads previous group accumulation. Snapshot specification includes selected
32 words, guardX2C66, Xpost[Q+30,Q+43),Ypost[S+12,S+1A), actualCPU/AGU/stack
and tables. Q=57B+4A*i andS=59F+28*i differ in stride. This is not an acquired
or admitted checkpoint; unresolved mode/pointer inputs remain explicitly required.

**TESTED:** nine static export/provenance/refusal tests pass; two exports of15
requested artifacts are byte-identical. Disassembly rows match original bytes;
literal/partial-boundary rows are not asserted executable. OriginalSYX/BIN/DSP
payload SHA256 and previous20B4 report hashes unchanged. Evidence:
builds/phase20b-sequence/final/validation.json andchecks-v2/verification.json.
Reproduction:plaits/seam/sequence/README.md. No installed tools, application
launch, hardware, MIDI/SysEx, firmware patch/repack, Plaits or stockCPU execution.

**STATIC CHECKPOINT RECONSTRUCTION EXHAUSTED.** Event/context admissionNO,
checkpointresumeNO. Final broad static attempt ends here. Current single next
step: separately authorize/specify one coherent provenance-qualified original9D9
snapshot; no acquisition performed. Earlier static continuation suggestions
elsewhere in this log are historical. See static-checkpoint-limit.md.

## Phase20B7 TAP qualification — 2026-10-07

**DESIGN/DOCUMENTATION ONLY.** Read pinned RM/FM; inspect primary public board
photos/diagram and official controller documentation/source. No board access,
measurements, JTAG/OnCE/MIDI/SysEx, installed tool, firmware/target-memory write,
hook, stock CPU execution or snapshot. Previous evidence preserved.

**STRONGLY SUPPORTED:** public V3.2 FP002099-01 board has DSPB56724AG144-LQFP;
README+under-shield photo agree. Actual user unit/maskUNRESOLVED. **VERIFIED image
observation:** six through-hole pads beside DSP, no net continuity established.
J3 ten-pad ProgrammingDebug plus author's SWDIO/SWCLK map strongly supports
MCU SWD, not DSP TAP. **PhysicalREADY-FOR-PIN-VERIFICATION, conditionalactualunit;
TAP exposureUNRESOLVED.** No pin map inferred from position/count/hidden layers.

**VERIFIED package/manual:** RM PDF48/49/74:56724 TMS101,TCK102,TDI103,TDO104,
RESET111,PINIT105,SCAN144;56725 equivalent55/56/57/58,63,59,80. Full voltage,
ground/mode/reset/pull table exported. No external packageTRST/DE/selectorpin.
Nominal3.3V I/O; actualVref/ground/loading/controllerunknown. EC limits do not
categorically exclude all5V silicon tolerance or authorize5V board drive.

**VERIFIED RM22:** externalTDI→core1TAP→core0TAP→TDO,4+4IRbits, JTAG0noIDCODE;
JTAG1ID01ED001D. OnCE needs DSP-specific protocol, not ordinary SWD. CHIDR and
originalP100/P9D8..9E0 signatures define conditional future core-ID test; no test
executed. **VERIFIED FM7:**9DCNOP hardware trigger acknowledgesafterexecution,
candidatePABEX9DD/PIL56D800 only under qualified boundary. Capture rawlatches
beforeGO, originalstatus/subaccumulators/AGU/activeindexedstack; no forcedLF/SP0.

**VERIFIED current source audit:** OpenOCD pinned8da0578d7bce3e134821ccf10911182788debc32
plainIR/DR scans omit companionTAPpadding; examine requiresIDCODE. Debug init
changesSR.SA/SC,N0/N1,M0/M1, though originals cached; topSSH/SSL not fullframes.
GlobalOnCEcache percoreisolation unqualified. Hardware comparator route exists
withoutPpatch. **ToolingPLAUSIBLE TOOLCHAIN, qualifiedpairNONE:** exactdevice
Symphony support documented; currentconverterSKU/drivers/rawexportunknown.
TRACE32familyalternative exact56724 supportunknown; defaultsoftwareBP patchesP.
Other genericJTAG/56800/SWD evidence not promoted to DSP56k support.

**VERIFIED RM3 / CONDITIONAL acquisition:** selected100words lowprivateRAM under
capturedvalidOMR; shared[30000,38000)distinct. **UNRESOLVED:** DMA, SHI/forcedGOIRQ,
ARM queues/cache/project/patch epoch; no universalhaltorder. Equal repeated reads
notABAproof. Actualview/model/pointercell/340bytebuffer, independentY7/R4slot,
XCC/bank/track/runtimeproject mustcorrelate; noinventedroot/getter/cachedefaults.

**TESTED:**11 documentary/refusal/range checks, byte-identical repeated exports,
JSON/CSV parse and guarded originals/allfirmware/pinnedmanuals/publicsources/
20B5+20B6exports/source scripts. Reportsfinal-v2/repeat-v2/checks-v2 under
builds/phase20b-tapqual/; source locations and excerpt hashes included. Tests do
not qualify hardware/controller, voltage, capture or replay. Public docs retrieved;
faileddirectNXP404 distinguished from consultedofficialwebcachedtext.

**Decision:** externalOnCEstillpreferredCONDITIONALLY; notshownimpractical, hook
notpromoted. Pin-verificationfuture-sessionjustifiedYES/separateauthorization,
probeattachmentNO, flashNO, snapshotadmissionNO. Bestnextstep: separatelyauthorize
limitedpowered-offactualboardidentity/candidate-netcontinuityverification.
StaticcheckpointstrategyEXHAUSTED; no further broad static event reconstruction.

## Phase20C LIVEPATCH-DESIGN — 2026-10-07

**OFFLINE DESIGN ONLY.** User defers runtime snapshot acquisition. Preserved
prior evidence; no target access/debug/MIDI/SysEx, firmware patch, RAM reservation,
flash-ready artifact, renderer change or CPU execution.

**VERIFIED:** both request/completion passes remain necessary in the current
design; request publishes queue/bitmap/ICC and completion consumes results.
Completion9A5..9B8 produces six ramps/current updates, Y7=Q+30 andR4=S+0C.
Original[9B9,9D9) is32P and its DO32 writes mono plus auxiliary2C02/2C24 streams.
Unconditional removal would lose post-mode inputs. Chosen **CONDITIONAL** design
retains the whole combiner via a relocated clone, then overwrites mono32 only,
restores liveout and JMPs original9D9. Fallback replays displacedMOVE1400,R0 and
continues9BB. No original generator computation is removed.

**VERIFIED selected guard producer:**7F1 iteration16 supplies2C66 in phasepair
scratch; finalmono loop does not write it. Original prefix retained; other classes
may leave older natural word. No universal value/duplicate-last/zero invented.
Original combiner CCR restored before9D9; downstream responds naturally to newmono.

**BOUNDED-PROOF union / CONDITIONAL wrapper:**26 raw words R1..7,N0..7,A/B slices,
data regs,SR. R0 reload at9D9; M/OMR unchanged; balancedDO/helperJSR adds up to3
stack entries. Dispatcher uses numericXCC0/R4=5AB; UI Synth1 name remainshypothesis.
No unresolved project/UI root used. Wrapper legality/modes/IRQ/stack still unqualified.

**VERIFIED lifetime rejections:**Q records/kernel regenerated and consumed each
block; first12 Y sample words remain phases/masks/ramps; output/aux/guard shared.
**UNRESOLVED:** fixed7 persistent X words. Temporary candidateX[2CCC,2CEC),32words,
could fit3 controls+3 spills+26 saves, but later-reader/async ownership not closed.
No candidate calledSAFE; X5F00 tail blockers preserved. Total demand39 data words,
no new output buffer. CurrentY12F preferred over target159/seed15C; centerednote
origin verified, Hz/table calibration and actualconverter/headroom unresolved.

**MEASURED existing encoding/traffic, CALCULATED changed template:**442P becomes
549P for81 long X sites+26 long control sites. Partialmodule713P+2 padding before
unknown glue. Existing7520 blocks give addressing delta587/673.3734/945 cycles;
no relocated execution. Conservative nominaldelta ceiling1964 yields15343 renderer
template envelope;142 known nominal glue gives15485 plus unresolved terms.
Retainedcombiner562 nominal cycles is not subtracted. Complete costs remainnull.

**VERIFIED framing:** count2A5E/load0/6byte header; ARM count+2 andAAword chunks;
nonwrapping transport boundFFFD (UXTH followed by32-bitCMP/BLT, notsigned16). Conditional core0P4000 gives5538 extra words.
Any in-place growth overlaps storedchannel1 at8110; move whole stream rather than
shift absolute ARM code. Maximum appended stream49158bytes, hypotheticalBIN364002
ending08068DE2; nominal512KiB flash fit is conditional, update/recovery not proved.
No code destination selected, no image produced.

**TESTED:**10 design/source/refusal checks,8682 listing rows checked against original
words (data included), repeat exports byte-identical, CSV/JSON parsing and immutable
original/firmware/standalone/previous20B6+20B7 guards. Reportsfinal-v2/repeat-v2/
checks-v2 underbuilds/phase20c-livepatch-design/. CPUexecution0, patchedimage0.
Initial v1 retained as exploratory evidence; v2 corrects sender cutoff toFFFD
and tests the zero-extended32-bit comparison/count-overflow distinction.

**Readiness:** snapshotneededNO for live architecture; technicallyjustified
CONDITIONALYES; codeplacementNO/stateplacementNO; registerunionboundedCONDITIONALLY;
offline executablepatchconstructionNO; flashingNO. Prototype not built because
requested mapping gate failed. Recovery checklist exported; backup/CRC not rollback
proof. Best next step: bounded fixed7-word persistent-state ownership proof; if
none can be established, stop before construction instead of inventing allocation.

## Phase20C2 FIXEDSTATE — 2026-10-07

**OVERALL REFUSED.** Strictly offline bounded inherited-candidate audit; no broad
RAM sweep, high-X search, target/debug/MIDI/SysEx, repack/patch, renderer change,
CPU execution or snapshot work. All previous evidence/originals preserved.

**New VERIFIED slot0 tail data flow:**281..2A2 setsX2B=E+45;70C loadsR1 and
73B emits3 derived update terms at5BF..5C1;36D/374 later reads them in retained
update path. Timestamp5C2=E+48 is written2DD usingR7=E+1,+71decimal, read by
1BDB allocator. Conditional ARM start21A22/54/5E sendszero to5C3+4A*i. All5
tail cells have retained writers; no seven-cell allocation. Extending through
5C5 crosses slot1mailbox5C4/coefficient5C5. Active coefficient/kernel/post/output/
group/high-X regions and unowned2-wordgap excluded, not searched for freedom.

**VERIFIED conditional scratch domains:** paired829/82A or884/885 stores cover
32 weights2CCC..2CEB, consumed833/83F/897 before9B9 but rewritten nextblock.
Phase15 initializedcursor family clears/accumulates bothhalves2CCC..2D0B;
normalparent/foreignpreservation remainsUNRESOLVED. All58 contiguous7 windows
in64-wordspan reject service robustness; representativefirst7/second7/split7
rankREJECTED. No completeglobalreader/writerclosure claimed; fatalwriters or
unclosed relevantdomains suffice to refuse positiveownership.

**VERIFIED service capability:**5E privatewriteoperation0/port0 acceptedunder
Selection0, no candidateprotection, privatewirewordzero. Cache-independent
address arithmetic: ifC!=a starta/count1; else starta-1/count2 forcessetup and
reaches a in serializedtransfer. No packet created/transmitted or invocation
observed. Nominal1500-row endpointprojection has no watchedhits, but omits known
ARM5C3reset; cache/normalbulk/foreign effective domains remainunclosed. SHI19D
maypreemptselected voice. KnownDMA/ring/sharedworker exclude watchedprivate
ranges conditionally, not everyreprogramming/context. Temp32word2CCC workspace
stillNOTPROVEN; localforegroundserialization alone is not exclusion.

**VERIFIED state layout:**phase,next,previous_pw,high,frequency,pw,shape;
no separatepreviousphase/integratorword. Exactbaselineinit0,0,200000,0,A3D7,
200000,0. **CONDITIONAL initialization:**deterministicownedepoch or explicitly
publishedzerofrequency sentinel; legalpositiveinterpolation remains>=1. No extra
flag inherentlyneeded; separatearmedactivationflag would be8total and needown
ownership. ArbitraryactivationRAM neverassumedzero. Currentstockwriters destroy
dormantXstate; one-waytakeover or ownedPobject are separatefallback designs.

**Exactly two DESIGN fallbacks:**A selectedgeneratorrecord[57B,582) takeover
requiresdisablingselected387/77F producers/readers inbothpasses plus actualtarget
service/foreignfilters and newaux/guard/postaccounting. Notcompatible withkeeping
allselectedgeneratorwork unchanged. B extendeduploadedPobject adds7 mutableP
words, notX; conditional5538capacity becomes5531code, partialmodule722P incldata.
FM372/373 MOVEMsupportsallregisters; code/count/layout unchanged inthisphase.
63state transfer sites; existing7520blocks771/833.6467/1037transfers imply nominal
MOVEMdelta3855/4168.23/5185 cycles under6+1vs2familytable. No newnumeric/cache/
pipelinequalification or integratedbound. DirectprivateSHI writesX/Y, notlowP;
P/DMA/mode/tail/container ownership stillunproved. B bestpreservesretainedwork.

**TESTED:**11 source/refusal/arithmeticchecks, targetedoriginalDSP+ARM bytechecks
(274event+1454hostARMrows), repeatidenticalexports, immutable originals/allfirmware/
standalone/20C/Phase11/15/19Chost/P204B guards. Thirteenrequestedartifacts plus
evidence atbuilds/phase20c-fixedstate/final-v1/,repeat-v1/,checks-v1/. No qualified
set, so positive lifetime fixture REFUSED; CPUexecution0. Tests do not qualify
storage or exercise full firmware. Initializationvalues are source data, not
stockmemory seeds. Recovery/flashgates stayclosed.

**Readiness:**persistentXNO/tempNO/crossblockNO/offlinepatchNO/flashNO.
Largestblocker is survivingstock/servicewriter ownership. **Single next step:**
bounded seven-word P-object/MOVEM contract qualification, not another broadX
search or automatic implementation. Snapshotbranch DEFERRED.

## Seven-word P-memory follow-up — 2026-10-07

**SOURCE-DERIVED:** DSP56300FM PDF372/373 permits absolute MOVEM read/write of
P using A/X0/Y0. Manual fields W/EA110000/dddddd and extension are encoded by
a narrow standalone adapter because the pinned assembler rejects absolute
MOVEM and long absolute control transfers. Core/assembler libraries and source
remain sealed. Existing independent Rust decoder verifies all boundaries,
MOVEM addresses/registers and branch targets. JSR source is PDF329 (generated
wrapper's327 comment is a page-reference typo, not an opcode change).

**IMPLEMENTED/TESTED:** seven mutable standalone cells P[2D29,2D30), deliberately
synthetic/unreserved. Only63 state operands change in low-P; all-long high-P/X
fixtures preserve original arithmetic and DIV. Strict callbacks reject other
P writes and old X-state accesses. Code/data/padding do not overlap, mutable
data is never executed. Exactly21 initialized BE24 bytes replace poisoned
seven-cell state once per case:0,0,200000,0,A3D7,200000,0. No eighth flag or
per-block reset, and no authentic Circuit initialization claimed.

**TESTED:**2,176 isolated raw24/CCR/accumulator fixtures pass independent integer
and equivalent long-X models. All43 unchanged cases at both stated rates pass
fresh independent oracle and original samples/state after every block.7,520
blocks/240,640 samples; max/RMS sample and all seven-state differences0.
All34,997,772 issued instructions match original ordinals/targets.2,048-block
continuity passes,65,536 samples after one seed. Low-P runs twice with all files
byte-identical. Existing float/pitch metrics unchanged, max0.9991969348 cents.

**MEASURED:** low-P code505 words; high-P and high-X code549 each. P version
adds seven P data cells, removes seven persistent X cells. Unchanged3 X spills,
3 controls,16 scratch registers,32 Y samples,0 LUT,3 stack frames;2 P padding.
All variants issue3988/4653.9590/8136 opcodes per block. No firmware integration.

**CALCULATED from MEASURED traces:** FM A7 MOVEM6+absolute1=7 vs long-X2.
High-X model6900/7943.5521/13335, high-P10785/12111.7855/18510 cycles/block.
Paired P-state increment3855/4168.2334/5185, average+52.4732%. Architectural
transfers771/833.6467/1037; callback reads additionally include the core's
old-value read for P cache invalidation, not another architectural operation.
Private internal zero-wait/no IRQ/DMA/standalone mode/family timing and inherited
conservative interlocks assumed. Physical cycles, hardware cache behavior,
whole-module costs and all-state WCET UNRESOLVED; old bounds do not transfer.

**VERIFIED bounded ownership facts:** unchanged upload P[0,2A5E) excludes the
candidate; no cold stock seed exists there. Apparent P28DE MOVEP is table data
copied from[28DD,29EC), not an executable writer. Reviewed SHI stores X/Y and
fixed audio DMA/shared aliases miss private candidate under reviewed map.
**UNRESOLVED:** actual endpoint/mode/translation, all DMA destination/reprogramming,
indirect/foreign/ROM/cache/prefetch/IRQ domains and owned loader/init epoch.
Linear absence is not complete reachability proof. Proven stock P cells0.

**VERDICT:** PASS standalone initialized numeric/continuity contract; **REFUSED
safe Circuit storage**. No stock image loaded, hardware/MIDI/SysEx/flash/repack,
original modification, stock RAM reservation or integration. Native DIV,
restoring and REGOPT references preserved.627 input guards unchanged; six
contract tests; reports final-v4/repeat-v4 identical. Reproducible tools:
ct_pstate_prepare.py,ct_pstate_verify.py,ct_pstate_check.py and standalone build
wrapper. Evidence:builds/phase20c-pstate/final-v4/,repeat-v4/,checks-v4/;
note:plaits-p-state-qualification.md. Exploratory source/build/failed runs v1..6
preserved; v7 fixes wrapper types/encoding/decoder capacity without core changes.

**Single next step:** targeted normal DMA destination/reconfiguration closure
for illustrative P[2D29,2D30) under the Selection0 memory map. No automatic
hardware or firmware construction; other ownership/load/cache/workspace gates
remain explicit, snapshot branch DEFERRED.

## Phase20C4-PREGION — exact appended P ownership — 2026-10-07

**Overall REFUSED; candidate CONDITIONAL.** One block only:
P:[0x3FF0,0x3FF7), seven24-bit cells,16-word alignment. No broad P/X search,
renderer redesign, firmware/stock execution, hardware/MIDI/SysEx, repack, flash
or original change. Previous43-case P-state qualification reused, not rerun;
its tested address remains2D29, not this proposed object. Owned stock P words0,
offline patch constructionNO. Snapshot work remains DEFERRED; no hardware-debug
path is recommended under the external-interfaces-only policy.

**CALCULATED / CONDITIONAL layout:** future complete code must end before3FEC,
giving5518 words from2A5E; proposed transfer fence3FEC..3FEE, two preguards,
state3FF0..3FF7, two postguards, load end3FF9. Known549P renderer and713P partial
module fit, but complete glue/fence/guards are not built or declared owned.
Padding is a structural requirement, not an indirect-write/target exclusion or
universal hardware prefetch proof. No whole-appended-range ownership claim.

**VERIFIED loader bytes/control:** ARM29260 resets via23438 and calls29200 for
bootstrap0 at29284, selectedch0 at29294, selectedch1 at292A6. Source table29700
uses4*selection, +8 forch1. One BE24 count/load record; currentch0Selection0
endsP2A5E. All five current streams miss the candidate; ch1 is another transport
endpoint under the recorded isolation premise. In-place extension overlaps
channel1 atARMoffset8110. **SOURCE-DERIVED / CONDITIONAL:** RM103 contiguous
PRAM contract means completedextendedcount3FF9/load0 seeds allseven on EVERY
reload.49137 framedbytes; sendercount+headers3FFB, belowFFFD transportlimit.
No object was emitted; currentstock doesnotseedthese cells. Diagnostics end
the epoch despite shorter stream counts leaving raw tail contents untouched.

**VERIFIED targeted writer inventory:** no executable directP store recovered
in the selected canonical listing; apparentMOVEP28DE is copied data. Not a
complete CFG/ROM/self-modification certificate. All8 DMA channels structurally
supportP DDS2; X registersetsDCR=FFFFEC−4*c, DCO+1,DDR+2,DSR+3. RM115/116
gives channel-specific32 request lines, including6/7. Reviewedcontrols285AC4
and286251 plusDE enables selectY andX, DRS11/12 ESAIRX/TX, DCO2→3 transfers,
DTM5 repeats withoutblock-endDEclear. **BOUNDED-PROOF NO** forprivateP whileDDS
staysY/X, regardless of cursor growth. Directnormal ISR1BC setsDDR0=29;
1BE setsDSR1=21. Remainingdirectreferences are tenINIT setup/enable rows.

**Largest UNRESOLVED normal domain:** P2043 loadsR4 fromX[364+5*k] underlinear
tablewalk;2048 readsX:(R4),204B writesB tosameunmaskedX destination. Prior
positivecount/compiledrecord/value domain remainsUNKNOWN; no normalattained
DMA-register orP collision was found. Thirty-two candidate-specific register
alias equations exported; no records/counts/valueintervals fabricated. Another
normal register obligation is pagedSHI171/175 savedcursor((page<<8)−2)&FFFFFF,
not separateextended3FFFFmask. HypotheticalpageFFFF plusfinitecursoroffset
can reachDMAregisters; actualnormalpage/length/space/cache/order notestablished.
Channels2..7 post-ROMDE/DDS/DDR/count/offset/trigger remainunknown; documented
resetDE0 is not promoted to post-ROM inactivity. Reconfiguration closure fails.

**VERIFIED / BOUNDED-PROOF service narrowing:**5E runs inSelection0 butdirectly
writes X/Y/shared, notprivateP underreviewedmap. Coherentstart/count envelopes
missDMAperipherals; inheritedfirstcachedcursorordering remains separate.
Privatewireword0 andsharedbyte<<8 cannot setDCRDDS2/DE1 evenifaliased. That
doesnot certify everyservice side effect or priorDMA state. Readback changes
cursor/save state. Diagnostic5C/5D/71 andmode-control paths can loadSelection1;
return0 uses1F532→1F554→1F568→29260. Fullproject/patch reload ancestry remains
unresolved. No arbitraryprivateP command recovered; absence is notuniversal.

**ROM/mode/cache UNRESOLVED:** shim changesOMR thenJMPFFFFFE; no directnormal
mainROMedge recovered, but computed dispatch/returns/exception ancestry and
compatibleROMexit residue are notclosed. RM76/77 fixedcore0MS110 giveswritable
P[0,4000), not provennormalmodepreservation. **New primary caveat:** RM95 lists
PCUcache, but RM100Table5-2 reservesSR19, genericFMCE position. Genericcache
control/constructor semantics cannot be transplanted as a chip certificate.
FM153/154 PMOVE/cache behavior and DMA incoherence are conditional family rules.
Standalone MOVEM success is numeric support only, not ownership/hardware proof.

**New BOUNDED-PROOF execution exclusion:** FM101 VBA low8 bits alwayszero;
RM115 interrupt offsetsC0..FAreserved. CandidateF0..F6 cannot be a documented
valid vector start orsecondword for ANY alignedVBA. No VBA/reset value seeded.
No scopeddecoded direct branch/call/loopend hitscandidate; stock2A5D isRTS.
Sevencomputed transfers DB6,DBD,DC5,DCD,DEC,DF9,19AC have unclosed normaltarget
preservation; initial low55tableentries and14descriptor+0values are notuniversal
mutationproof. RTS/RTI andcompleteappendedCFG remainunclosed. No actualnormal
execution of candidate shown. Padding never substitutes for target/DMA proof.

**Deliverables/TESTED:** all13 requested ledgers plus rankedoptions/manual/source
witnesses;8682 originalDSProws (includingdata) and727 ARMrows bytechecked.
12 focusedtests cover7-cell/guard/load math,8 DMAsets,spaces/triggers/lengths,
servicevalues,pagednecessaryequations,any-VBA vector-slot exclusion,tabledata,
unchangedpositivecount uncertainty andrefusal.56 report members repeatidentical;
740 protectedinputs unchanged, overwrite refusalPASS. No stockCPU or numeric
suite execution. Toolsct_pregion_audit.py/ct_pregion_verify.py and12 tests;
canonicalbuilds/phase20c-pregion/final-v1/,repeat-v1/,checks-v1/.
Noteplaits-p-region-ownership.md; state/code/todo/P-state notes updated.

**Ranked remaining designs:** B temporarysoftware-instrumented/enforcedobject
withDMAadmission/writecoverage first; A one-wayselectedgenerator takeover second;
C controlledreplacementpayloadwithexplicitmodule/loader/mode/DMAownership third.
Allconditional, nonebuilt; monitoring alone doesnot prove universalownership.
**Single next step:** specifyB's finite enforcement/coverage contract offline,
using external interfaces only. No new broadmemorysearch or hardware-debug path;
patch construction andflashing remain unjustified.
