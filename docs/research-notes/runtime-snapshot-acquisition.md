# Phase20B6 — acquisition design, no acquisition

2026-10-07. **READY-FOR-ACQUISITION-DESIGN**, conditional on board, tool,
boundary and coherence qualification. This is not READY-TO-CONNECT or permission
to flash. Static checkpoint reconstruction remains **EXHAUSTED**. No hardware,
debugger, MIDI/SysEx, firmware/payload modification, stock execution or capture.
Canonical 12 exports: evidence and reports under builds/phase20b-snapshot-design/
final-v4/; repeat-v4/checks-v4. Earlier exports retained.

## A–B. Minimum and trigger

The minimized **CONDITIONAL** numeric profile is actual routing0, nonlinear1,
sequence offsets5/5 and qualified linear/addressing/count conditions at capture.
It is not inferred from the patch file. Mandatory live inputs include SR/OMR,
R4, incoming material modifiersM0/1/2/3/4/6/7, SP/SC/LA/LC and active stack
frames, Y7, selected post X/Y state,32 mono+guard words, selected prior group
accumulations, actual global controls and table provenance. M5 is locally
overwritten from capturedY19/Y1A. LF/FV derive fromSR. Incoming otherR/N/data
registers are redefined or unused for this selected numerical path, but rawR0
is needed for the proposed9DD boundary-normalization proof. Full architectural
comparison/debug save-and-restore requires the otherwise dead register values too.

See runtime-snapshot-schema.md for addresses and omitted fields. Snapshot-live-
fields.csv classifies each register/range A–E with source and conditions.
Prepared targets replace upstreamY8F..91 as *local post-only* inputs. Coefficient
table bytes are not automatically reconstructible from theP payload.

**VERIFIED pinned manual:** DSP56300FM7.2.4 says an executed program-fetch
breakpoint stops after that instruction; a memoryMOVE-access breakpoint stops
after the following instruction. A debugger's address label does not prove
pre-execution state. PipelinePABEX denotes the would-execute instruction.

**Preferred practical trigger:** program comparator on9DC, the last original
NOP, with raw next-execution boundary9DD confirmed from savedPAB/PIL/PDB/flow
state. This avoids placing the trigger at the end of the generatorDO. All32
words and natural guard are complete; no post processing has executed. Incoming
R0 has been replaced by9D9'sY7 reload; other prefix state must be checked.

**CONDITIONAL normalization:** preserve the raw9DD snapshot and proof; future
import may start9D9 only if R0=Y7, original9D9..9DC prefix and memory mapping are
unchanged, and no intervening interrupt/DMA/host/peer mutation occurred. The
reload/threeNOP prefix then has the same local numerical live inputs at9DD.
Replaying that prefix again is not hardware-cycle/pipeline-equivalent; label
the normalization and extra executed prefix. No silent PC edit or forced target
execution. This does not prove real-time scheduler equivalence.

**Exact9D9 alternative:** comparator on the32nd executed9D8 store, confirming
last iteration, store completion, implicitDO exit and raw next boundary9D9.
The first occurrence leaves only one output word complete. A watchpoint on the
last output address acknowledges later and is not assumed pre9D9. Immediately
before9D9 and at its pre-execution boundary are the same architectural cut.
Capture immediately before final-store retirement is too early. No trigger is
implemented or armed in this phase.

## C–E. Debug and stock readback

External DSP **OnCE** is **PLAUSIBLE-BUT-BOARD-UNVERIFIED**: pinned DSP56724RM22
documents two serial 4-bit TAPs and per-core debug. Exact part, DSP pad routing,
voltage, security state, controller compatibility and dual-core halt behavior
remain unresolved. The publicTC2050-compatible header report does not identify
DSP TAP pins. OnCE stops the core and injects instructions for architectural
register/memory access; it is not passive or nonhalting. Details:dsp-debug-access.md.

STM32 SWD/JTAG, conditional on actual silicon/debug permission/header mapping,
can expose ARM registers/RAM and existing SPI transfer buffers. It does not
directly expose DSP-private X/Y, registers or hardware stack; halting ARM does
not halt DSP. Debugger invocation of stock read helper29344 would itself change
ARM control/stack/cache/transport state and needs a future safe call protocol.

**VERIFIED stock readback:**1F30A→269E4 operation1→29344(private)/295BA(shared)
→SPI2→SHI156→HTX→ARM reply scratch→37B0C/20C90 logical MIDI response. Private
X/Y reads and bounded shared reads exist; they do not read architectural register
files or stack, and have no seam trigger/freeze. They overwriteX10/X11 and ISR
scratchY2000..2005, prefetch an extra word and can leave a stale ARM address
cache. Y2000 save RAM is not a simultaneous complete seam snapshot.

Only32 words fit the reviewed small scratch path locally; no firmware-enforced
safe maximum established. Padding/error/extra-access hazards remain. Physical
USB-versusDIN routing is unresolved. No new packet encoder, service request or
endpoint is invented. **Sequential5E reads alone are rejected for this snapshot**.
Selection1 tests5C/5D/71 switch to a different diagnostic payload, so they are
also rejected as evidence of naturally running selection0 at9D9.

## F–G. Temporary hook and self-capture

**DESIGN HYPOTHESIS:** a future inline redirect at9D9 could save live state
before copying bounded memory into a sealed diagnostic buffer. No hook assembled,
no P address placement, no freeRAM address or reservation, no patched payload.
A new commit marker in that buffer could be polled after capture; no existing
stock completion mailbox/notification is claimed.

Conceptual order: inline transfer withoutJSR/DO; absolute rawSR/OMR first;
accumulator subfieldsA2/A1/A0/B2/B1/B0 if complete capture is needed; R/N/M
before pointer setup; SP/SC/LA/LC/extension context; SSL-beforeSSH stack walk;
remaining data registers; bounded memory copy; metadata and commit marker last.
Only then may any copier use saved registers, counters or loops. Interrupt
masking, if a future design permits it, follows originalSR capture and is a
documented perturbation, not silently omitted. Any first operation that changes
uncaptured state invalidates that record.

**VERIFIED limitation:** full accumulator moves may limit/change sticky status;
save raw subfields. SSH reads popSP/SC and may invoke stack extension; a complete
walk/restoration proof is required. Self-capture changes pipeline, cache, elapsed
cycles and interrupt timing; no raw original pipeline visibility is established.
It cannot provide an unqualified exact untouched-stock snapshot. External OnCE
raw-latch capture is preferred for that fidelity, with its own inspection hazards.

**CALCULATED inventory / ESTIMATE:** selected core memory100 words, conservative
full-register archive43 words, active stack2*s words (s≤15 onlySEN0), metadata/
workspace24..48:167..221 words before tables;1511..1565 with832 coefficient+
512 normalization words. Rough hook160..320P words, not assembled/measured.
No claim of a proven smallest program, verified cycle cost or available capacity.
The stack algorithm/extension and race protection could increase both estimates.

## H–J. Extraction, perturbation and recovery

OnCE route: raw TAP/controller transaction log and register/memory dump on the
observer computer → canonical sparse bundle. Pipeline/status and registers must
be saved before inspection uses them; only memory reads from a quiescent epoch.
Architectural debug reads still execute injected instructions. Peer cores, DMA,
ARM traffic, audio clocks and peripheral queues are not assumed frozen by a
single-core halt. Qualify exact writer exclusion/ownership or refuse coherence.

DSP-only OnCE cannot recover the full ARM patch from noninvertible DSP control
words. Additional coherent ARM observation or a qualified correlated log is
required for exact patch/event provenance. Reused original 3BE60 selects the
bank model at view+344+4*bank; 3BBE8/3BC06 shows model+0C points to a pointer
cell whose value is the patch byte buffer, with length at model+10. Capture
the actual 340 bytes and hash. Runtime view-root discovery and cross-debug
coherence remain unresolved; do not execute getters or guess a root address.
Slot can be checked independently from captured Y7 and R4 using the differing
Q/S strides. A numeric post snapshot can exist while audible event identity
remains unqualified; the bundle must retain that distinction.

Hook+stock transport route: immutable sealedDSP buffer → stock29344/SHI → ARM
269E4 scratch →37B0C/20C90 logical reply → future authorized host decode.
This is a proven logical *memory transfer* composition, with unknown physical
endpoint and unallocated hook buffer. A later read can avoid racing the captured
data only if no writer changes that buffer; it still perturbs running protocol
state. Hook+MCU debug alternative: sealed buffer → future qualified debugger-
assisted existing read helpers → allocatedARM scratch → ARM RAM dump. Neither
bridge is implemented or currently safe to invoke.

Emulator seeding is useful *after* the minimized observed inputs exist; it cannot
recover unobserved retained histories from audio/host traffic. PassiveSPI/ESAI/
GPIO logs can supplement event provenance, not replace registers/stack/private
memory. No externalICC data trace or serial/debug output endpoint established.

OnCE needs no firmware patch but creates a halt/audio discontinuity, debug-state
writes and injection timing. Hook routes add instructions, register/CCR/stack
work, memory occupation and IRQ latency; they capture instrumented execution.
No quantitative wall-time or glitch-free claim. Risk-comparison.csv records all
methods. Pre-trigger debug configuration and any prior halt must be logged too.

**Recovery UNRESOLVED:** original files/round-trip tool exist, but they do not
prove unit rollback. ARM bootloader below08010000 and update-mode independence
from a workingDSP are not established. A brokenDSP could prevent ordinary
startup/handshakes; whether independent update mode remains usable is unknown.
DSP-only hook concept may avoidARM code changes, but its distribution/restoration
path remains unqualified. **Flashing justified now: NO.** No destructive procedure.

## K–S. Ranking and decision

|Rank/method|Fidelity|Complexity/risk|Firmware patch/board|DSP registers/stack/X-Y|
|---|---|---|---|---|
|1 DSP OnCE|Highest conditional architecture/pipeline evidence|High; electrical/tool/coherence unknown, audio halt|No patch / DSP access unknown|Conditional / conditional / documented|
|2 DSP hook+stock readback|Conditional instrumented-state capture|Very high; placement/stack/IRQ/restore/endpoint unknown|DSP patch / not inherent|Conditional / unresolved / sealed-buffer design|
|3 DSP hook+MCU debugger bridge|Same hook fidelity|Very high; addsARM debug and call-state hazards|DSP patch / MCU access required|Hook only / hook only / bridge conditional|

The complete eight-method table with field-by-field acquisition/extraction paths
isacquisition-methods.csv. No candidate is classified AVAILABLE on this unit.

Further broad static event-association RE useful? **NO**. Runtime snapshot needed
for stock checkpoint? **YES**. Electrically non-modifying hardware debug plausible?
**CONDITIONAL YES**, behaviorally non-invasive/nonhalting? **NO**. Temporary
diagnostic firmware necessary? **UNRESOLVED**, not if OnCE can qualify. Hardware
acquisition **design** justified? **YES**. Connection/capture/flash authorized now?
**NO**. Existing replay gate remains closed; importer is a design contract only.

**Single best next step:** qualify actual boardDSP TAP exposure/silicon/core mapping
and a controller's pipeline, raw-register, stack and writer-exclusion capabilities
from existing documentation. Any physical inspection, connection or experiment
requires separate authorization. Do not start another broad static provenance phase.

Reproduce with fresh paths:

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B tools/ct_snapshot_design.py --output-dir builds/phase20b-snapshot-design/reproduce-new
& $taskPython -B tools/ct_snapshot_design.py --output-dir builds/phase20b-snapshot-design/repeat-new
& $taskPython -B tools/ct_snapshot_design_verify.py --suite-dir builds/phase20b-snapshot-design/reproduce-new --repeat-dir builds/phase20b-snapshot-design/repeat-new --output-dir builds/phase20b-snapshot-design/checks-new
```

**TESTED:** eight design invariant tests; repeat reports/text/PNG evidence identical;
source and previous20B5 report hashes unchanged. Tests check export consistency,
range arithmetic and refusal/schema structure, not acquisition, hardware fidelity,
formal JSON-Schema meta-validation or replay. No dependency installed.
