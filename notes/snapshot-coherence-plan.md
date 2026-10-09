# Phase20B7 — Seam snapshot coherence and provenance plan

2026-10-07. **CONDITIONAL design; no coherent snapshot acquired.** Static checkpoint
reconstruction remains EXHAUSTED. Numeric admission/replay remains refused.
Canonical evidence: `builds/phase20b-tapqual/final-v2/`; eleven documentary design
tests plus byte-identical repeated reports, not device/controller measurements.

## H. Exact breakpoint contract

**VERIFIED FM7.2.4, PDF136:** program-fetch breakpoint acknowledgement follows
execution of the matching instruction. Hardware comparator at original P9DC
(`000000`, NOP) therefore gives candidate **raw next-execution P9DD**, provided
no interrupt/exception or other delay changes that boundary. Original9DD is
`56D800`, `move x:(r0)+,a`; it must not have retired. All32 mono words
X:[2C46,2C66) and natural guardX2C66 are complete.

**CONDITIONAL expected:** PABEX=9DD (would-execute address), PIL contains the
9DD opcode56D800. PABFR, PABDR, PDB and flow history must be observed, not filled
with fabricated fixed values. FM7.2.5, PDF137 defines the distinct pipeline
addresses. GUI/GDB PC is a tool-derived interpretation, not sufficient evidence.
Original listing signatures are reproduced in evidence/program-signatures.json.

The local generator DO completed at9D8 before the NOPs. **UNRESOLVED inherited
state:** outer loop LF/FV, stacked SR/LA/LC and active frames may remain. NOP
itself changes neither SR nor stack; this does not prove debug entry or an
intervening interrupt leaves everything untouched. Do not setLF/SP/SC to defaults.

**Required acquisition order within a future qualified halt:** raw OnCE
status/configuration and PIL/PDB before injected GO; PABFR/PABDR/PABEX and all12
circular flow entries; original SR/OMR/SP/SC/LA/LC and conditionalEP/SZ; raw
A2:A1:A0/B2:B1:B0 and R/N/M/data registers before clobbering them; then a qualified
full active indexed stack walk. Save initial stack controls and readSSL beforeSSH
per frame because SSH reads pop SP/SC (FM5.4.3). Preserve raw accumulator slices
before any limiting/scaling full-accumulator transfer. Complete walk/restoration,
injected-instruction IRQ behavior and exact controller export remain unqualified.

FM7.2.7 and RM6 show forced-instruction memory inspection, not passive peeking.
RM Table6-1 XFFFFFC versus Table6-2 YFFFFFC OGDB-label inconsistency remains
explicit; choose no injection solely from the conflicting figure. Controller
implementation/device applicability must resolve it.

Preserve raw9DD bundle. Numeric normalization to replay9D9 is allowed only under
the existing Phase20B6 explicit proof rule: original prefix unchanged, R0=Y7,
no intervening IRQ or mutation. This is not a cycle/pipeline-equivalence claim.
No normalizer/importer implemented and no replay started.

## I. Physical core identification design

**VERIFIED device RM:** CHIDR XFFFFF5 yields core0=000724/core1=010724 for56724
(000725/010725 for56725). Future access itself needs qualified forced-instruction
handling. The two-TAP chain must allow JTAG0 without IDCODE. Preserve raw state
before injection; compare unchanged P100 and P9D8..9E0 words against the original
payload/listing; correlate natural halt pipeline state and actual slot cursors.
Record TAP/core/coupled-debug association. No reset, forced PC, P writes, guessed
channel-to-core mapping, or execution of identification tests in this phase.

## J. Writers and coherence

**VERIFIED RM3, PDF75–78:** internal low P/X/Y RAM is per core; shared physical
RAM is [30000,38000), aliased across P/X/Y and both cores. Required ranges are
low internal RAM **CONDITIONALLY** under actual captured OMR/MS/MSW mapping.
Peer-core CPU access is therefore not automatically an alias to this snapshot.
That does not prove either core's DMA, peripheral/ownership routing, mailbox
jobs or debug-injected interrupts cannot mutate it.

For actual observed slot i, Q=57B+4A*i; S=59F+28*i. Table values are DSP words,
half-open endpoints. Two independent slot formulas must agree in0..11.

|Range|Words|Established ordinary writer / exclusion needed|
|---|---:|---|
|X[2C46,2C67)|33|same-core generator9C6..9D8; natural guard included; exclude DMA|
|X[Q+30,Q+38)|8|post/parameter fields, same-core ARM→SHI ISR path; exclude queued/injected ISR and DMA|
|X[Q+40,Q+43)|3|same-core ramp/state plus parameter path; same exclusions|
|Y[S+0C,S+1A)|14|retained post state; same-core loop, indirect SHI possibilities require exclusion|
|X[2DF0,2E10) or[2E50,2E70)|32|prior same-core voice accumulations selected by XCC; exclude DMA|
|X CC/39/3A/3B/40|5|runtime/init/parameter/IRQ publishers; same epoch required|
|Y7/10/19/1A/1C|5|cursor/masks/modifiers/table pointer; same epoch required|
|Total selected numeric memory|**100**|not a complete CPU/stack/table/provenance dump|

**Correct Y offset remains S+0C, twelve decimal words; not S+12 hexadecimal.**
Slot0Y[5AB,5B9),14 words. X skipped[Q+38,Q+40) remains omitted only under verified
routing0/nonlinear1/offsets5/5. Other profiles refuse this minimal contract.

Coefficient tableX[1600,1940),832 words, and the512-word normalization domain
derived fromY1C/modifier require same-epoch capture or independently proven exact
immutable source/transformation. They are outside the100-word minimum. No table
contents or stock defaults are invented. Registers/stack/pipeline add fields.

**UNRESOLVED coherence:** ordinary selected-core halt stops its normal CPU/ISR
execution. The second core, DMA, SHI/SPI clock/FIFO, ESAI/timers and ARM can
continue. Forced debug GO's interrupt eligibility must be qualified. ARM has no
direct MMIO mapping to DSP private RAM, but it can continue SPI/DMA transfers and
publish queued updates. ARM halt does not cancel in-flight DMA or flush M7 cache.
Coupled DSP halt does not imply ARM/peripheral/DMA halt. CIMDMAS is a stall-
interrupt threshold, **not a DMA-freeze bit**. DMA address/count/modulo domains
must be excluded from each required range; no guessed freeze writes proposed.

## Writer exclusion: no universal halt ordering

**BOUNDED reasoning, not a complete exclusion proof:** DSP-first captures the seam
but ARM patch/publication/queues can change before ARM halt. ARM-first perturbs
host timing, leaves in-flight traffic and lets the DSP advance. Dual-DSP coupled
halt can stop peer CPU execution but not all external writers. None is recommended
as a race-free ordering without new ownership/epoch evidence.

Conditional minimum: qualified hardware seam halt; raw state first; actual OMR
private mapping; all relevant DMA domains excluded; no ISR during debug injection;
pending SHI/host jobs and publication/cache epoch qualified; then sparse reads and
correlated ARM provenance. If required writer exclusion or epoch cannot be proved,
**refuse snapshot**. Repeated equal reads are useful consistency checks, not proof
against ABA or unobserved intervening writes. No firmware getter, queue drain or
unrecorded cache clean/invalidate call is proposed. An extra halt/freeze is justified
only for a proven relevant writer and qualified effect, not as a generic solution.

## K. Correlated patch/event provenance

**VERIFIED prior ARM source formulas, CONDITIONAL runtime observation:** at
0803BE60, model=[view+344+4*bank]. The actual view root is unknown and must be
observed; no root address invented. Model+0C points to a pointer cell that yields
the actual byte buffer; model+10 contains length. Confirm340 bytes (3BBE8/3BC06),
capture raw bytes/SHA256, chain addresses/bytes and publication state. Optional
active correction data: ARM20005C28+8C*bank,140 bytes. No getter invocation.

Correlate independently: Y7=57B+4A*i+30, R4=59F+28*i+0C; actual XCC group,
logical bank, slot/event/track and actual runtime project identity. XCC alone or
cached project0 does not establish audible synth/patch identity. Capture ARM
registers, queues, observed roots and cache-view qualification in the same epoch.
If root/project/event cannot be established, retain UNRESOLVED provenance instead
of filling from cached data. Numeric snapshot alone is not audible patch proof.

## Future sequence and aborts

future-session-plan.json specifies stages, each conditional and separately
authorized: actual board identification/continuity; electrical reference/power
qualification; controller bench qualification; qualified normal-power attachment;
two-TAP/core/P signature verification; hardware-only9DC breakpoint/natural run;
raw state first; previously proven writer exclusion; sparse state/tables/ARM
provenance export; offline validation and qualified debug-state restoration/
disconnect. No attachment, reset, OnCE command, diagnostic hook or flash here.

Connection refused while voltage, ground, TAP identity, electrical compatibility,
reset effects or auto-init/target-memory writes are unknown. Capture refused while
raw-state fidelity, required writers or epoch remain unknown. “Disconnect without
writes” cannot mean skipping necessary qualified restoration of debugger-clobbered
registers; no firmware/memory patch is allowed and all transient changes are logged.

**Preferred: external OnCE, conditional.** Hook not promoted; flashNO. **Best next
step:** separately authorize limited powered-off actual-board identification and
candidate-net continuity, then close controller gates before any attachment.

## Reproduction and test scope

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B tools/ct_tapqual.py --output-dir builds/phase20b-tapqual/reproduce-new
& $taskPython -B tools/ct_tapqual.py --output-dir builds/phase20b-tapqual/repeat-new
& $taskPython -B tools/ct_tapqual_verify.py --suite-dir builds/phase20b-tapqual/reproduce-new --repeat-dir builds/phase20b-tapqual/repeat-new --output-dir builds/phase20b-tapqual/checks-new
```

**TESTED:**11 documentary/refusal/range invariants, byte-identical repeated export,
CSV/JSON parse checks and guarded originals/all firmware/manual/public sources/
previous20B5+20B6 reports. This does not test hardware, electrical measurements,
debugger execution, coherent capture or stock replay. Generator refuses existing
paths and writes only fresh children; first exploratory final-v1 retained,
canonical final-v2 includes completed source/test guards. No dependency installed.
