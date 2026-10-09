# Phase 17 — DSP debug and offline observation assessment

## Phase 18 — minimal offline replay specified, not implemented

**DESIGN:** use pinned C++ DSP56300 core in forced-interpreter mode first.
No replay harness, build or DSP execution occurred. Complete CPU/parallel/P/
peripheral/DMA/worker/host store mediation and selected read/203A-entry logging
are required before trusting a trace. **VERIFIED source gaps:** REP iterations
bypass the ordinary opcode callback; DO runs internally; DMA has memcpy/fill
fast paths independent of JIT. Existing generic hooks are insufficient alone.

**UNRESOLVED prerequisites:** post-upload SR/OMR/memory profile, startup Y clear
outside conditional private RAM, EMC initialization, host table contents/order,
material worker behavior and actual normal reachability of parent1E15→1F5C.
Do not invent a full startup checkpoint or a mandatory1F97 scheduler stage.
Separate conditional unit fixtures from integrated normal stock scenarios.

See [dsp-emulator-spec.md](dsp-emulator-spec.md),
[dsp-replay-scenarios.md](dsp-replay-scenarios.md),
[dsp-emulator-validation.md](dsp-emulator-validation.md), and builds/phase18/final/.
**Next:** Phase19A core/memory/every-write tracing plus ISA/AGU/loop/IRQ coverage
tests only after explicit implementation instruction. Planned19B startup,
19C targeted scheduler/models,20 validated stock replay; gates may add work.

X35F invariant/high-X normal availability remain **NOT-YET-DETERMINED**;
service robustness remains **NO**. Hardware stays disconnected,5E rejected,
no firmware patch/allocation/Plaits work. This supersedes historical next steps.

2026-10-06. RESEARCH + STATIC ONLY. No device/port access, JTAG/OnCE connection,
MIDI/SysEx or5E request, firmware/DSP-memory writes, emulator execution/build,
instrumented firmware, installation or Plaits work. Original binaries retained.

**Result: no qualifying passive DSP RAM observation facility established.**
The documented candidate OnCE stops normal execution for register/memory
inspection. Flow history is not effective X/Y write trace. Keep hardware
disconnected,5E rejected, X35F/high-X normal safety NOT-YET-DETERMINED and
service robustnessNO. Absence of a documented facility is not proof that no
unpublished silicon feature exists.

## A. Silicon and debug identity

**VERIFIED firmware:** executable DSP56300-family P words, SHI/ESAI/ICC-like
peripheral accesses, two upload endpoints, normal channel-one shared/ICC worker.
Sources: dsp-memory-map.md, dsp-command-map.md and canonical phase3 listings.
The firmware proves neither a physical package nor endpoint-to-core numbering.

**STRONG HYPOTHESIS:** DSPB56724AG. First-party board research lists this part
under the RF shield with SDRAM and latch. A teardown discussion instead reports
DSPB56725AG; the conflict is unresolved without a readable marking/package
photo tied to the relevant board. No public photograph was inspected this phase.
[Board research](https://github.com/userx14/CircuitTracksReverseEngineering),
[teardown report](https://www.reddit.com/r/novationcircuit/comments/1g6r35j/).

**SOURCE-DERIVED, conditional:**56724 has144-pin20×20mm LQFP;56725 has80-pin
14×14mm LQFP. Both use two24-bit DSP56300 cores. Datasheet Table19 lists
DSPB56724AG and DSPB56725AF, not the reported56725AG. Exact unit, revision,
mask and package remain **UNRESOLVED**. External-memory firmware use supports
the56724 interpretation but is not an independently verified board netlist.
[DSP56724EC, overview/Table19/package figures](https://www.nxp.com/docs/en/data-sheet/DSP56724EC.pdf).

**SOURCE-DERIVED:** OnCE per core, not SC140 EOnCE. Candidate parts have two
serially chained4-bit TAP instruction registers; debug entry may be coupled
between cores. JTAG-0 and JTAG-1 capabilities differ. CHIDR values distinguish
724/725 and cores, but no chip-ID read occurred. Manufacturer pin functions
do not establish Circuit Tracks pads.
[DSP56724RM, sections4.3.5/6.2.1 and chapter22](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf).

## B–C. Feature and state-effects matrix

**SOURCE-DERIVED:** DSP56300 OnCE access requires Debug mode, stopping normal
operation. SC140 EOnCE real-time transfer features are inapplicable to the
candidate architecture. No arbitrary background X/Y/P read facility satisfying
the full gate was found. This is a documented-procedure conclusion, qualified
by the unresolved physical part.
[AN2073, sections4/5](https://www.nxp.com/docs/en/application-note/AN2073.pdf).

| Feature | Core continues? | Debug state changes? | Program/data RAM changes? | Registers/stack/flow | Safe during normal audio? |
|---|---|---|---|---|---|
|Arbitrary X/Y/P inspection|NO, documented procedure|YES|Target store unnecessary for a simple read; debugger scratch/peripheral effects unresolved|Injected instruction/pipeline; example incrementsR0; stack save is tool-dependent|NO strict gate|
|Architectural register inspection|NO, documented procedure|YES|No RAM store required by primitive; save strategy unresolved|Forced transfer/debug context, register-specific|NO strict gate|
|Background arbitrary RAM access|None documented|UNRESOLVED|UNRESOLVED|UNRESOLVED|Not established|
|Internal flow-history capture|YES during running execution|History updates|No program/data logging buffer required|No injected capture instruction|Capture alone does not supply requested data|
|Flow-history retrieval|NO, documented sequence|YES pointer/OCR|No target RAM store required|Debug/pipeline interaction|NO strict gate|
|Instruction trace counter/stepping|RunsN instructions then stops|YES|No software patch required|Debug entry/execution control|NO|
|P/X/Y read/write watchpoints|Stops on configured trigger|YES comparators/counter/status|No software patch required|Debug entry; possible other-core halt|NO|
|Continuous effective X/Y address+data trace|None documented|UNRESOLVED|UNRESOLVED|UNRESOLVED|Not established|
|Boundary pin sampling|Potentially normal pin operation|YES TAP/BSR|Not private-memory inspection|Mode-specific; no board safety proof|UNRESOLVED|

The simple memory-read example uses a forced MOVEP intoOGDB and postincrements
R0. Other instruction choices may avoid that particular AGU change, but cannot
remove documented Debug mode/instruction injection. No monitor firmware is
required for that primitive; this does not make it passive. Do not claim all
reads inherently write program/data RAM or stack. Conversely, debugger save/
restore strategies are not state-free merely because final values are restored.
[AN1839, sections1.4/4.4/4.7](https://www.nxp.com/docs/en/application-note/AN1839.pdf).

Full requirement test: nonhalting **NO**; no debug instructions **NO**; unchanged
program flow **NO**; no AGU change **not guaranteed**; no RAM write **depends on
debugger/target**; unchanged interrupt state/timing **not established**; no monitor
**possible but insufficient**. No safe audio window or wall-time guarantee.

## D. Trace versus breakpoint detection

**SOURCE-DERIVED:**12×25-bit circular flow-history entries hold program-address
history; retrieval advances its pointer and requires a full12-read sequence
for coherence. Pipeline address registers supplement it. Memory comparators
support P/X/Y read/write conditions, combined events and an occurrence counter;
triggering enters Debug mode. Trace counter means stepping, not streaming data
trace. Configuring filters changes debug state. Passive internal capture is
distinct from intrusive retrieval.
[AN1839, sections1.2/1.3/1.5/4.5](https://www.nxp.com/docs/en/application-note/AN1839.pdf).

**Assessment:** recent branch flow nearP203A/P1F97 may be reconstructible from
history, but neither effective cursor addresses nor written values are logged.
A write watchpoint may detect an address event, including a same-value store,
but halts on the trigger and cannot report the count value at every203A entry.
No lossless continuous X35F/high-X access stream or independent trace port was
documented. The inherited DSP56300FM chapter7 evidence agrees; full PDF fetch
failed this phase, so use the successfully read application notes for the new
gate, rather than claiming a fresh complete family-manual review.

## E–F. Board access and passive electrical observations

See [board-debug-access.md](board-debug-access.md). Public research reports a
TC2050-compatible debug header and references J3 photograph/diagram files.
Exact numbered pins and DSP TAP pads are **UNRESOLVED**. STM32 debug access
would not expose DSP private RAM without interacting with the DSP.

| Signal/mechanism | What future input-only capture could show | Cannot establish |
|---|---|---|
|SPI2/SHI|Existing host address/data words, reads, width changes, boot/runtime separation and timing; decode with recovered command-lane/chip-select GPIOs|DSP-only stores, every203A value, absence of high-X writes; incomplete/lost capture further weakens it|
|ESAI/audio|Clock/frame/slot behavior, sample output and correlation with host events|Private RAM ownership or count invariant; silent audio is not no-write evidence|
|ICC/shared communication|On-chip for candidate56724/25; no external bus route established|External SDRAM/EMC sniffing cannot reveal private X/Y or internalICC/shared accesses|
|GPIO handshakes|Selection/lane/ready/reset timing where actually routed and identified|Internal addresses/data/lifecycle without correlation|
|JTAG boundary SAMPLE|Pin snapshots, not a high-bandwidth private memory bus trace|Same limits as external pins; JTAG remains active TAP manipulation|

**Explicit limit:** SPI sniffing shows host traffic and cannot prove absence of
internal DSP-only writes. Electrically input-only does not mean zero loading;
probe capacitance, voltage domain and access points require validation in a
separately authorized future scope. No analyzer/pin assignment or capture now.
Boundary EXTEST/CLAMP/HIZ may alter pin behavior; not an observation substitute.
[AN2074](https://www.nxp.com/docs/en/application-note/AN2074.pdf).

## G. Offline emulator feasibility

**VERIFIED local sources, no emulator run:**

| Candidate/pinned commit | Available basis | Missing validation |
|---|---|---|
|C++ dsp56300,44353be2f0156cac970c6ab4f467ea1998b40605|56362 SHI exchange/status/IRQ, ESAI, DMA; memory debugger callbacks and configurable JIT write routing|56724-specific maps/dual-coreICC/EMC, complete write-hook coverage, bus/interrupt timing and attribution|
|Rust mborgerson,c60aeedb6a6014850204c71e53bc0cf5b3104222|DSP56300 core/interrupt state, callback memory regions, AGU/modulo implementation|Circuit peripheral model; inline JIT RAM stores bypasswrite_memory; dependency/build footprint and semantic fidelity|

Sources already exist locally. Read only, no refetch/build/run/install.
[C++ project](https://github.com/dsp56300/dsp56300),
[Rust project](https://github.com/mborgerson/dsp56300).

**VERIFIED source details:** C++ jitconfig.h defaults memoryWritesCallCpp=false;
jitmem.cpp routes reviewed single and parallel X:Y writes throughC++ when enabled.
memory.cpp offers onMemoryWrite but its commented change-history block records
only value changes, so it cannot prove no same-value stores. Rust emit/mem.rs
uses direct buffer stores for constant/dynamic X/Y addresses; a hook solely in
core.rs write_memory is insufficient. Callback regions or emitter interception
are plausible alternatives, requiring full coverage validation. No instrumentation
implemented, and no guarantee that every access path already invokes a hook.
Line-numbered source witnesses and hashes are exported underphase17.

**Available inputs:** P payloads/load map, reviewed startup clear/copies, cursor
tables, descriptor/state fragments, handler entryPCs and host command format.
**UNRESOLVED:** complete registers/X/Y state, ROM/external tables, pending work,
IRQ priorities/timing, shared aliases, ICC worker/event ordering, DMA activity,
host parameter transitions. These are sufficient for specifying conditional
isolated routine tests, not a faithful complete stock board execution.

**HYPOTHESIS:** offline replay can close selected computed-address cases more
cleanly than halted hardware snapshots. First specify a minimal1F97/203A
state-transition model, exact inputs and deterministic events; fail on missing
peripherals/undefined memory rather than silently zeroing or ignoring them.
Future instrumentation needsPC/space/effective address/old+new value, entry loads,
modifiers/caller context, same-value stores, parallelL writes, CPU/JIT/DMA/ICC/
host stores and translation aliases. ISA, AGU and interrupt fixtures must precede
trust in a trace. Decoder tests alone do not validate execution semantics.

An emulator trace can prove a property for its modeled execution. Finite clean
runs are not universal stock proof. Universal closure requires justified complete
initial/event domains plus exhaustive or invariant reasoning. No full emulator
or existing hardware-facing upstream difftest CLI was executed this phase.

## H. Instrumented firmware — concept only

**HYPOTHESIS future option**, prohibited now: log X35F/high-X effective stores
and count loads using a modified copy. Placement/relocation/overlays must first
be proved. Added code consumes cycles and may change registers/interrupt latency;
no persistent logging RAM allocation is established. SHI/mailbox logging alters
the same traffic/state being investigated. External logging bandwidth, overflow,
atomicity and recovery/bootloader/rollback are unresolved. Instrumenting only
someCPU stores misses parallel writes, DMA and cross-core aliases. Heisenberg
effects can both introduce and suppress a violation. Altered-firmware evidence
must never be presented as unchanged stock proof. No patch/copy build performed.

## I. Method ranking and sufficiency

Ranking combines usefulness with safety; it is not hardware authorization.

| Rank | Option | Safety / effort / behavior risk | X35F | High-X ownership |
|---:|---|---|---|---|
|1|E offline emulator coverage/readiness audit|No hardware risk; moderate targeted/high complete model; model-error risk|SUFFICIENT for fully captured model traces; stock closure unresolved|STRONG EMPIRICAL EVIDENCE for validated scenarios; PROOF only exhaustive justified model|
|2|A targeted static premises|Safest; low/moderate; no behavior changes|PARTIAL EVIDENCE ONLY currently; PROOF possible if global preservation closes|PARTIAL EVIDENCE currently; PROOF needs all writers/domains|
|3|D passiveSPI, conditional future|Electrical risk/access unresolved; moderate; no commands conceptually|PARTIAL EVIDENCE ONLY|PARTIAL EVIDENCE only|
|4|C documented hardware flow history|Retrieval stops execution; high effort; shallow history|PARTIAL EVIDENCE forPC only, not countvalue|NOT USEFUL for write ownership alone|
|5|B OnCE memory/watchpoints|Fails nohalt gate; high access/context effort; debug disturbance|PARTIAL EVIDENCE ONLY|PARTIAL EVIDENCE snapshots/access events|
|6|F instrumented custom firmware|Prohibited; high effort/timing/RAM/recovery risk|PARTIAL EVIDENCE for altered runs|Potential strong empirical evidence for altered runs, no stockPROOF|

Audio/ESAI alone: **NOT USEFUL** for either private-memory claim. GPIO timing:
**PARTIAL EVIDENCE ONLY** for context, no invariant proof. ICC capture externally:
**NOT USEFUL** under documented internal topology. No method currently proves
the normal stock invariant or a256-word allocation.

## J–L. Safety gate and next step

| Gate | Answer | Qualification |
|---|---|---|
|A nonhalting state-preserving memory read documented?|NO|reviewed candidateOnCE requiresDebug mode; exact unit remainsunresolved|
|B sufficient nonhalting X/Y write trace documented?|NO|flow history and halting watchpoints do not qualify|
|C board access to qualifying facility established?|NOT-YET-DETERMINED|no such facility/pad assignment established|
|D passiveSPI can close remaining invariant?|NO|internal stores/entryload invisible|
|E offline emulator plausibly can close it?|YES, conditional|modeled causal trace possible; faithful/exhaustive stock proof stillunresolved|
|F hardware remain disconnected?|YES|no justified live method under current constraints|

**Single best next step:** a static coverage/readiness specification for targeted
offline1F97/203A replay, using existing pinned sources, enumerating initial-state,
event-source and complete effective-write-hook obligations. Do not build/run
an emulator or change firmware as part of this phase. Another broad alias
census or JTAG connection is not justified by these findings.

## Reproduction and integrity

Offline ledger exporter `tools/ct_debug_facility_audit.py` reads existing files,
checks source witnesses/hashes and exports citations, matrices, gaps and gates.
It does not access network/devices or execute firmware/emulators. Public source
URLs are mutable; retrieval date/failed retrieval limits are recorded. Claims
are source-derived with locators, not universally machine-verified hardware facts.

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_debug_facility_audit.py --output-dir builds/phase17/final
```

Fresh output required; existing paths/original rejected. Independent repeat and
input-integrity results are recorded in builds/phase17/reproducibility.json.

**VERIFIED final checks:**9 reports in final/ and repeat/ are byte-identical.
Both supplied SYX/BIN SHA256 values, all five DSP extraction pairs,
decoded-BIN equality and exact SYX roundtrip passed. Exported source-witness
needles/line locations and before/after input hashes passed. No execution
coverage or hardware fidelity is implied by these integrity checks.
