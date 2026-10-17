> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Seven-word P-state qualification — 2026-10-07

## Phase20C4 ownership follow-up — 2026-10-07

**REFUSED; candidate CONDITIONAL.** The concrete ownership study uses
P:[0x3FF0,0x3FF7), with proposed two-word guards and a hard appended-code budget.
This is not the address of the previous standalone numerical fixture; no renderer
was retargeted or redesigned. Seven owned stock P words remain unproved.
Known DMA0/Y and DMA1/X miss it; normal P204B record-driven register aliases,
paged SHI cursor/order and post-ROM channels2–7 remain unresolved. Documentary
vector slots exclude the candidate for any aligned VBA, but computed targets
and returns are unclosed. RM Table5-2 reserves SR19, so generic cache-enable
assumptions are not qualified. No allocation or patch construction follows.
See `plaits-p-region-ownership.md`; reports `builds/phase20c-pregion/final-v1/`.
Current next step is the bounded software-enforced/instrumented object design,
not another memory search. Numerical results below remain unchanged.

**Overall: REFUSED for Circuit Tracks storage. PASS for the standalone numeric
and initialized P-object contract.** MOVEM is viable; no seven-word stock P
allocation is proved. This is not an impossibility claim about P-backed state.
No hardware, MIDI/SysEx, stock CPU replay, firmware patch/repack/flash, original
file changes, RAM reservation, model switching or polyphony.

Canonical evidence: `builds/phase20c-pstate/final-v4/`. Complete original
43-case inputs reused, not rediscovered. Final executable/source versions are
`core-v7/` and `source-v7/`; fixtures `fixtures-v7/`; traces `low-p-v7/`,
`low-p-repeat-v7/`, `high-p-v7/`, `high-x-v7/`. Earlier exploratory outputs
remain intact and are not canonical certificates. A repeated report export is
`repeat-v4/`. Tools: `ct_pstate_prepare.py`, `ct_pstate_verify.py`, build wrapper
`plaits/poc/pstate/build.ps1`, six tests in `test_pstate_contract.py`.

## Instruction legality and memory semantics

**SOURCE-DERIVED:** pinned DSP56300FM Rev5 PDF372/373 (13-132/133) permits MOVEM
read/write P with all on-chip registers and memory-alterable addressing. Used
form is absolute long EA110000 plus a 24-bit extension. Used data-register
fields: A=0E, X0=04, Y0=06. Read first word is07F080|register; store is077080|register.
All63 sites are pure transfers, with no parallel ALU operation to discard.
MOVEM to SR replaces CCR; SSH has push/pop effects. Neither is used here.
Other destinations have documented sticky growth/limiting effects; MOVEM must
not be assumed to preserve all CCR bits in every numeric mode or overflow state.

**IMPLEMENTED:** only state operands change in the low-P renderer. No arithmetic,
scaling, helper, oracle, interpolation, event decisions or output buffer changes.
Long-X/high-P variants additionally encode the existing X operands long and
relocate control targets, preserving their original instruction ordinals.

The pinned assembler lacks absolute MOVEM EA encoding and long absolute
JMP/JSR/Jcc encoding. A narrow wrapper encodes just these documented forms;
the sealed interpreter/core and assembler sources/libraries are unchanged.
Long-branch fields are supported by FM PDF320/323/**329** (the generated v7
source comment says327 for JSR;329 is the correct page). The existing independent
Rust disassembler confirms all instruction boundaries, every MOVEM register/
address and all control-transfer destinations. No Capstone DSP decoding or
invented opcode is used.

**TESTED:**2,176 isolated fixtures:136 raw24 values (zero, one, signed extremes,
all ones, actual initializer values, deterministic random values) ×4 initial
CCR settings ×4 operations (P→A/X0/Y0 and A→P). Compare an independent raw24
integer model and equivalent long-X instructions. A reads sign-extend A1 into
A2 and clear A0; stores preserve bounded raw24 values. A/B raw accumulators,
X0/Y0, SR, SP/SC match. The fixture domain has zero scaling, no overflow,
interrupts or peripherals. It does not qualify arbitrary stock SR/OMR modes.

## Seven-word object and initialization

**IMPLEMENTED/TESTED, standalone only:** synthetic private P[2D29,2D30), exactly
seven24-bit cells. Its address was inherited as a layout illustration, not found
as free stock memory. Strict bus admits mutable writes only inside these seven
cells; all executable P words are immutable. The PC must be an instruction
boundary outside the object. Old X[20,27) reads/writes are forbidden in P mode.
Y[0,20) is the independent32-sample output, not state. Decoder capacity is4000
P words so the high-address code/data object is representable; this is a
synthetic harness parameter, not proof of the running Circuit memory map.

|Offset|Retained field|Exact initial raw24|
|---:|---|---:|
|0|phase|000000|
|1|next|000000|
|2|previous_pw|200000|
|3|high|000000|
|4|frequency|00A3D7|
|5|pw|200000|
|6|shape|000000|

All21 seed bytes are validated and loaded once per test case, replacing an
explicit A5A5A5 poison in all seven cells. No eighth flag, arbitrary zero-RAM
assumption or per-block reset. State persists through every render in the case.
This proves an explicit standalone load epoch, not authentic stock boot-ROM
execution, Circuit upload growth or arbitrary live activation initialization.

The sealed `memWriteP` also reads the old word to invalidate its decode cache.
Consequently `blocks.csv` P_state_reads includes architectural MOVEM reads
**plus one emulator old-value read per store**. The report reconciles this
exactly, and charges only architectural operations. Mutation never executes
the data object. Interpreter cache behavior is not hardware prefetch/cache
coherence qualification.

## Exact equivalence and continuity

**TESTED:** all43 existing cases,7,520 blocks,240,640 samples, both rates48kHz
and conditional48.046875kHz, pitch cases, sweeps, abrupt seeded stress and
frequency-cap case. Each of the three variants independently matches a fresh
unchanged integer oracle and the sealed REGOPT samples and seven state fields
after every block. Maximum sample/state difference=0; sample RMS difference=0.
All34,997,772 issued opcodes are compared by instruction ordinal,
including branch/DO destinations; address relocation changes PCs, not the path.

The2,048-block case has65,536 consecutive samples and one initialization epoch.
Exact oracle state continuity passes. The low-P suite runs twice; all output,
state, block, code, label, resource and complete PC-trace files are byte-identical.
Native DIV and restoring fallbacks remain available and unchanged. Since the
new sample vectors equal the sealed vectors, every prior float-reference and
pitch comparison remains unchanged: max tested pitch error0.9991969348 cents;
largest float-reference case RMS difference0.02197305172. These are inherited
comparison results, not claims of floating-point equality or sample-rate proof.

## Measured words and trace-derived timing

**MEASURED:** executable words and actual issued opcodes. **CALCULATED:** cycles
from those measured traces and the pinned manual timing model. Physical hardware
cycles are UNRESOLVED; no hardware timing measurement was performed.

|Standalone variant|Executable P|Persistent P|Persistent X|Model cycles/block min / mean / max|
|---|---:|---:|---:|---|
|Sealed REGOPT short-X|442|0|7|6278 /7270.1787 /12390|
|Only state changed to long MOVEM|505|7|0|10713 /12039.7528 /18320|
|High-address all-long X reference|549|0|7|6900 /7943.5521 /13335|
|High-address all-long P state|549|7|0|10785 /12111.7855 /18510|

All variants issue **3,988 /4,653.9590 /8,136** opcodes/block,
exactly **34,997,772** total. MOVEM changes latency and extensions, not opcode count.
Every P variant still uses3 X spills,3 X controls,16 retained scratch registers,
32 Y output cells,0 LUT cells, peak3 stack frames. Add two decoder padding words
to each executable count; low-P total code+padding+state=514P, high-P=558P.
High-P vs high-X executable delta=0, persistent storage delta=+7P/−7X.
This is a standalone renderer count, not a complete Circuit module/glue count.

**SOURCE-DERIVED/CALCULATED:** FM PDF431 A7: MOVEM6+long absolute extension1=7
nominal cycles versus long-X2. **MEASURED:**771 /833.6466755 /1037 state transfers
per block. Exact paired model delta **3855 /4168.2333777 /5185 cycles**, not
the difference of unrelated extrema. Average +52.4732% against high-X renderer;
stock budget fit remains UNRESOLVED. Branch extension costs and inherited
conservative accumulator interlock charges are included. The model assumes
private internal zero-wait memory, standalone SR300/OMR0, linear modifiers,
no DMA/interrupts, and family-compatible timing. It retains the inherited
short-store ambiguity and a separate12-cycle fill/drain allowance.
Observed high-P ceiling=18522; this is **not an all-state WCET**. Neither the
old13379 standalone bound nor15485 partial integration allowance transfers.

## Stock ownership and verdict

**VERIFIED bytes:** Selection0/channel0 upload loads P[0,2A5E),10846 words.
The seven candidate cells are outside it. The unchanged stock upload does not
initialize them. Conditional core0/MS7 capacity P[0,4000) includes the candidate,
but capacity does not establish owner, backing, preservation or initialization.

Sixteen actual P-operand references are exported and byte-checked against the
original payload; the listing's P-address prefix is excluded. Older report v3
had an overly broad export filter and is superseded. Numerical results did not
change. The apparent MOVEP at
P28DE is **table data**, copied by28D3/28D7/28D9 from[28DD,29EC); do not treat
its linear decode as a normal P writer. The selected listing recovers no
executable direct P store; this is not complete CFG/ROM/foreign/DMA closure.
Known private host19D/19B stores target X/Y; reviewed fixed audio DMA paths and
shared PXY[30000,38000) miss the candidate under the reviewed map. These narrow
exclusions do not close all P destination, mode-switch or reload domains.

**UNRESOLVED ownership blockers:** actual normal endpoint/mode/translation and
lifetime; complete DMA destination/reconfiguration and indirect P/foreign/ROM
coverage; hardware P-data/cache/prefetch/wait/IRQ behavior; and a proven owned
expanded P load/initialization epoch. Prior temporary32-word workspace,
preservation/stack/IRQ ABI, pitch/headroom and recovery gates also stay closed.

**Verdict: REFUSED for safe Circuit P storage. Proven owned stock P words:0.**
Standalone instruction/numeric/continuity gates pass. No firmware construction,
stock RAM reservation or integration is justified. The original firmware and
reference implementations are hash-guarded and unchanged.

**Single best next step:** a candidate-specific static closure of normal DMA
destination/reconfiguration domains for P[2D29,2D30) under the Selection0 memory
map. Keep mode/ROM/loader residuals explicit; do not promote capacity to ownership.

## Reproduction

Use fresh child paths; all tools refuse existing output destinations. Existing
small local compiler, sealed interpreter libraries and decoder suffice; no
download or tool installation.

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B tools/ct_pstate_prepare.py --output-dir builds/phase20c-pstate/source-new
& ./plaits/poc/pstate/build.ps1 -SourceDir builds/phase20c-pstate/source-new -BuildDir builds/phase20c-pstate/core-new
& ./builds/phase20c-pstate/core-new/pstate.exe --fixtures builds/phase20c-pstate/fixtures-new
& ./builds/phase20c-pstate/core-new/pstate.exe builds/phase20c-pstate/source-new/low-p/variablesaw.asm builds/phase20a-regopt/final/inputs.tsv builds/phase20c-pstate/low-new 3 200 p
& ./builds/phase20c-pstate/core-new/pstate.exe builds/phase20c-pstate/source-new/low-p/variablesaw.asm builds/phase20a-regopt/final/inputs.tsv builds/phase20c-pstate/repeat-new 3 200 p
& ./builds/phase20c-pstate/core-new/pstate.exe builds/phase20c-pstate/source-new/high-p/variablesaw.asm builds/phase20a-regopt/final/inputs.tsv builds/phase20c-pstate/high-p-new 3 2a5e p
& ./builds/phase20c-pstate/core-new/pstate.exe builds/phase20c-pstate/source-new/high-x/variablesaw.asm builds/phase20a-regopt/final/inputs.tsv builds/phase20c-pstate/high-x-new 3 2a5e x
& $taskPython -B tools/ct_pstate_verify.py --source builds/phase20c-pstate/source-new --fixtures builds/phase20c-pstate/fixtures-new --low builds/phase20c-pstate/low-new --repeat builds/phase20c-pstate/repeat-new --highp builds/phase20c-pstate/high-p-new --highx builds/phase20c-pstate/high-x-new --out builds/phase20c-pstate/report-new --exe builds/phase20c-pstate/core-new/pstate.exe
& $taskPython -B -m unittest discover -s emulator/tests -p test_pstate_contract.py -v
```

The verifier records the explicitly supplied executable hash; reproduction
does not overwrite core-v7. The report preserves the original frozen-suite
comparisons; filenames containing "new" are explicit isolated output choices.
