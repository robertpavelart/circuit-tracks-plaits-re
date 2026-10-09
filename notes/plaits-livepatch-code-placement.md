# Phase20C — code/container and addressing costs

## Current Phase20C5 guarded-object layout - 2026-10-07

**PARTIAL. CALCULATED / CONDITIONAL; no image.** Proposed code[2A5E,3F5C) has5374P capacity;
new save/control/shadow/status objects and numeric P7 occupy explicit appended
intervals. The older5518P code budget below no longer applies to this layout.
Two-word fences/padding cannot establish writer exclusion or control-flow safety.

Known unassembled partial costs:712P voice wrapper +89 guarded204B clone +37
partial SHI clone +28 initializer =866P. Planning allowances add256 validator,
96 startup,128 control-flow checks,64 reply adapter and216 simple Rn veneers,
for1626P. These are budget targets, not bounds or a fit certificate. Caller
adapters, actual indexed/modulo/parallel EAs, converter and full initialization
are extra. Naively inlining24P at344 candidates costs8256P, exceeding capacity.

Retarget the renderer-internal two-word MOVE#>0,R0 to2C46 and change Y output to
X; an outer R0 setup would be overwritten. Width/cycle delta0 under that template.
Converting18 remaining long X sites to P has a calculated35/101.9920/590-cycle
premium from the sealed trace, not new execution. Conditional renderer bound
28708 plus wrapper416 and illustrative Q1/N20 fast guards gives29548+unknown.
Q/N are not stock bounds; whole-runtime cost remains null. Original combiner562
is retained, not subtracted. SHI classifier4..60 includes false-branch penalties;
root admission/cursor/error handling is extra.

Whole-helper guarded204B clone has a five-NOP relocated DO tail. Encoding, ABI,
control-flow and complete coverage remain unqualified. Current details/evidence:
plaits-enforced-state.md and phase20c-enforcedstate/final-v3. Earlier costs below
are historical templates, not the current proposed total.

## Phase20C4 bounded object layout — 2026-10-07

**CALCULATED / CONDITIONAL, not constructed:** candidate seven-word data at
P:[0x3FF0,0x3FF7), two guard words each side, proposed terminal transfer at
[0x3FEC,0x3FEE). Complete appended executable code must end before0x3FEC;
budget from0x2A5E is5,518 words. Existing549-word standalone code and713-word
partial module fit, but unknown full glue is not declared fitted or owned.
Proposed load count0x3FF9/load0 gives49,137 framed bytes and reset of all seven
literals on every reload. In-place extension still overlaps channel1; no enlarged
payload/image was emitted. These layout conditions do not establish tail freedom.
Ownership remains REFUSED: DMA/register, computed targets, ROM/mode/cache and
loader epoch are unclosed. Prior measured renderer counts/cycle models remain
unchanged; no new integrated timing claim. See `plaits-p-region-ownership.md`.

## Current P-state executable cost qualification — 2026-10-07

**MEASURED standalone executable505P shortcontrol/longPstate;549P high all-long
template, each+7persistentP+2padding.** The high longXreference also measures549P.
Allstate transfers/branch targets verified by independentRustdisassembly and
exactoriginalinstruction-ordinal traces. The sealednumericrenderer remainsintact.

**CALCULATED from MEASURED traces:**highX model6900/7943.5521/13335 versushighP
10785/12111.7855/18510 min/mean/max cycles/block. PairedPstorageincrement
3855/4168.2334/5185; average+52.4732%. Allissue3988/4653.9590/8136opcodes.
No hardwarecycle measurement, full-module count orall-stateWCET. Actualstock
Pmode/tail/loader/DMA/cache andworkspace/glue gates remainclosed; noimagebuilt.
The old13379/15485 bounds mustnotbe used forPstate. Full evidence:
plaits-p-state-qualification.md,builds/phase20c-pstate/final-v4/.
The previous20C2 MOVEM cost prediction below is now executed/qualified only
within the standalone numeric/private-memory contract, not Circuit ownership.

## Current Phase20C2 fallback resource update — 2026-10-07

**Seven-X ownership REFUSED; no construction admitted.** All evaluated fixed
or split candidate state addresses exceed3F, so hypothetical X addressing has
zero delta to the549P long template. No small low-X block was discovered/claimed.

FallbackB evaluates seven P data words loaded as part of an extended P object.
FM372/373 supports MOVEM with all on-chip registers;63 existing state-transfer
sites would retain2-word long forms in the prescribed template, but use different
opcodes/CCR/pipeline/P-bus behavior. No code changed or numerical equivalence
claimed. Conditional capacity5538 becomes5531 for code after seven data words;
713P+2padding+7data=722 before unknown glue. Illustrative data[2D29,2D30) is not
reserved and full glue affects location.

**MEASURED priortrace counts / CALCULATED model:**7520 blocks contain
771/833.6467/1037 state transfers min/mean/max. FM A7 MOVEM6+long extension1
versus longX2 gives hypothetical extra3855/4168.23/5185 cycles relative to the
long-X design. These are not new execution measurements or a bound. Earlier
15485 partial envelope must not be carried over unchanged to P-backed state.
Loader/container, tail/mode ownership, P/DMA/cache and numeric/CCR/stack/IRQ
qualification remain required. Current reports:builds/phase20c-fixedstate/final-v1/.
Single next step: bounded P-object/MOVEM contract qualification, no repack or flash.

2026-10-07. **CALCULATED conditional templates; no changed code assembled or
executed.** No patched DSP stream, ARM BIN or SYX was produced.

## K. Placement options

**Preferred structural candidate, not proved placement:** append module beyond
P2A5E, retain original generator/fallback and all bank1 algorithms. Bootstrap
sets OMR MS7/MSW1(22) and clearsMSW0(21). Under the DSP56724/core0 map, capacity
is P[0,4000); current single record occupies[0,2A5E). The conditional additional
capacity is **5538 words /16614 bytes**. Exact running endpoint/core/mode and
complete P-tail ownership remain unqualified. No deployable address selected.

The five upload streams are not five same-P segments. Channel1 is another endpoint;
selection1 is an alternative image, bootstrap is replaced atP0. Thus there is no
following record in this selected stream to collide with in P-space. That statement
does not exclude unbounded indirect P references, ROM/memory-mode behavior or other
runtime ownership. Capacity is not SAFE placement.

Reclaiming the original generator is rejected: the fallback and bank1 still use
77F and the combiner. Sacrificing an algorithm can affect bank1/other patches and
has no proved non-test-unused region. No other executable trampoline destination
was proved. Options B/C/D therefore supply zero verified reclaimable words.

## Image extension mechanics

**VERIFIED unchanged bytes:** stream source ARM offset1F0, six-byte BE24
count/load header, count2A5E, load0; exactly10846 payload words. Stream ends8110,
where channel1 starts. No per-stream checksum/type/entry field; P0/reset branch
remain unchanged. Outer firmware uses size and non-reflectedCRC32.

ARM sender08029200 reads count bytes1/2 as16-bit BE, adds the two header words,
sends chunks up toAA words (510 bytes), source+3*index. Positive signed BLT
comparisons use zero-extended32-bit values. Nonwrapping16-bit totals imply payload≤FFFD for the reviewed transport;
the conditional4000-word PRAM capacity is lower and fits. There is no32767
cutoff: UXTH does not sign-extend. Integer sender fixtures exercise8000 andFFFD
payloads and reject FFFE/FFFF, correcting the initial16-bit signed-limit inference. Increasing count alone
would transmit the following stored stream and then unrelated ARM bytes.

**Any positive in-place growth overlaps channel1 immediately.** Larger growth
also overlaps executable ARM code; simply moving channel1 is insufficient.
Do not shift absolute-addressed ARM code. Conditional future alternative: append
the complete enlarged stream while retaining existing addresses, change only
selection0/channel0 pointer-table cell08029700, then update outer size/CRC through
a separately qualified future construction. Other table cells/images remain.

Current BIN end is0805CDDC. Maximum4000-word stream would be49158 bytes; appending
it yields364002-byte BIN ending08068DE2. This fits below nominal08080000 under
the photographed STM32F745VE512KiB model, **CONDITIONALLY**. It does not prove
actual flash layout, bootloader limits, protection, integrity/version rules,
DMA assumptions, update acceptance or recovery. Authentic boot-ROM handoff gaps
remain explicit. No update image generated or acceptance test performed.

## L. Renderer and wrapper word counts

**MEASURED existing immutable layout:**442P renderer,81 short absolute X sites,
26 absolute control-transfer sites. Arithmetic/native DIV remain unchanged.
At high appended P with fixed data addresses above3F, a prescribed all-long
template adds81 data-extension words and26 branch-extension words:
**549P renderer**. Its terminal JMP reaches high restore code; a low direct9D9
exit would alter that count but bypass the required restoration. Direct output
changes the single Y:(R0)+ store to X:(R0)+, with separate R0=2C46 setup; no copy32
or new output allocation. These are static template counts, not new executable
size measurements. PC-relative alternatives could differ and are not assumed.

|Conditional module component|P words|
|---|---:|
|Long-address renderer/native helper|549|
|26 saves +26 restores, long absolute2-word forms|104|
|Fixed PW/shape setup +frequency store, excluding converter|9|
|Output pointer setup|2|
|Dispatcher selected prefix +fallback|16|
|Entire original combiner clone|32|
|Final short JMP9D9|1|
|Subtotal|**713**|
|Conservative prefetch padding|2|
|Pitch converter, initialization, extra eligibility, amplitude adapter|**UNRESOLVED**|

The original hook replaces two words with two words, so adds no container length
by itself. **715P is a template allowance, not the complete added code**. Conditional
5538-word capacity leaves4823 after that allowance, before unknown terms. Complete
added P remainsnull. MOVEC forms, raw save/restore legality, DO endpoint relocation
and pipeline restrictions must be assembled/audited only after placement/state gate.

A hypothetical715-word extension needs a34689-byte relocated complete stream;
existing BIN plus that stream is349533 bytes. This is arithmetic, not an emitted
image. No flash-ready artifact is present.

## M. Cycle impact

**Existing baseline only:** tightened13,379-cycle bound belongs to unchanged
standalone short addressing and its stated private-memory/mode/no-IRQ model.
It is not the integrated patch cost.

Under pinned FM timing tables/retained STRONG short-store interpretation: changing
short X reads to long adds one nominal cycle per execution; short stores modeled
as2 remain2 for long; long absolute JMP/JSR adds one; long Jcc has no table
increment. Previous interlocks are retained conservatively. New sequence legality,
boundary, cache/waits and IRQ behavior remain unqualified.

**MEASURED existing trace events / CALCULATED hypothetical delta:** census of
7520 unchanged standalone blocks yields nominal addressing deltas
**587 /673.3734 /945 cycles min/mean/max**. This is not relocated-code execution,
and the maximum is not an all-state bound. Exact per-block rows are exported.

Conservative finite relaxation: setup≤11 extra, main sample≤51 extra once per
forward path ×32; ≤80 helper calls ×(one longJSR plus up to3 long helper-loopJMPs),
plus one exitJMP increment = **1964 cycles**. Thus a conditional relocation
template ceiling is **15,343**, retaining the standalone13,379 algebraic bound.
This is deliberately loose and still conditional on valid unchanged integer
contract, modes, memory and encoding; no physical/integrated bound claim.

Dispatcher selected template24; nominal saves52, restores52; output pointer2;
fixed controls/frequency store9; finalJMP3. Sum **142** additional nominal cycles
besides renderer. Partial conditional increment: **15,485 plus unknown terms**.
Unknowns are converter, initialization, eligibility/adapter, preservation
interlocks/DO/fetch qualification, IRQ/DMA/wait states. Complete delta remainsnull.

Original combiner subtotal **CALCULATED 562**:13 setup, DO5,32×17 body under
private zero-wait stock conditions. It is retained, so its incremental delta is
zero: do not subtract562 or other stock generator work to advertise savings.
Guard receives no additional store. Wrong-slot/bank dispatcher overhead is
18/26 nominal cycles; all non-selected paths retain original arithmetic/state
subject to qualified flag restoration and timing impact. No total audio deadline,
multi-voice or Synth2 timing fit proved.

## Reproduction

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B tools/ct_livepatch_design.py --output-dir builds/phase20c-livepatch-design/reproduce-new
& $taskPython -B tools/ct_livepatch_design.py --output-dir builds/phase20c-livepatch-design/repeat-new
& $taskPython -B tools/ct_livepatch_design_verify.py --suite-dir builds/phase20c-livepatch-design/reproduce-new --repeat-dir builds/phase20c-livepatch-design/repeat-new --output-dir builds/phase20c-livepatch-design/checks-new
```

Fresh outputs only. Ten design/source/refusal tests, JSON/CSV parsing, repeated
report equality and immutable original/firmware/standalone/previous-evidence guards.
Existing PC traces are read; no CPU instantiated or changed numerical suite run.
No prototype is admitted under unproved placement or state.
