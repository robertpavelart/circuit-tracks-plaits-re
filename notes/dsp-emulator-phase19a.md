> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 19A — deterministic offline execution substrate

2026-10-06. **IMPLEMENTED / TESTED:** a headless, forced-interpreter harness
executing synthetic fixtures only. No Circuit Tracks program, startup, scheduler,
modified firmware, hardware, MIDI/SysEx, OnCE/JTAG, flashing or Plaits execution.
Final synthetic programs start at P:0x400; fixture handlers use P:0x600.
Earlier exploratory fixtures used synthetic code at0x100; no Circuit image
was loaded into the harness at any stage.

## A. Revision, build and reproducibility

Pinned core:44353be2f0156cac970c6ab4f467ea1998b40605, GPLv3.
Pinned missing source dependency fetched:AsmJit3577608cab0bc509f856ebf6e41b2f9d9f71acc4.
No toolchain installation. Existing MSVC19.44.35228, Windows x64, C++17,
CMake3.31/Ninja, Debug assertions, SDK10.0.26100.0. Definitions:
DSP56K_FORCE_INTERPRETER=1,DSP56300_DEBUGGER=0,ASMJIT_STATIC; harness
static_assert(!g_useJIT). JIT code/dependency remains linked because upstream
classes require it, but DSP execution is interpreter-only; no JIT instrumentation.
No GUI/plugin/device adapter. Upstream Audio is an internal memory-ring class,
not a connected audio-device driver.

Two independent build directories produced executables, replay_core.lib,
asmjit.lib and debugging symbols. Build recipe/source reproduced; Debug binary
hashes differ with build-directory/PDB metadata. **Canonical traces reproduce**,
not a claim of bit-identical executable builds. Full binary hashes are in
builds/phase19a/reproducibility-final.json. Final build logs are build-complete.log and
build-complete-repeat.log; preliminary failures/logs retained for provenance.

Local vendor source remained unchanged. The instrumented copy is under
emulator/upstream/dsp56300. Exact overlays, normalized review diff and source
hash manifests live underemulator/harness. Preparation verifies every original
and overlay hash and refuses an existing destination. The first-build MSVC
template ambiguity was resolved by explicit third template argumentnullptr for
existing readMem/writeMem specializations, not new opcode semantics.

## B–D. Implemented files and memory/trace contract

- emulator/CMakeLists.txt andbuild.ps1: headless build using installed tools.
- emulator/harness/main.cpp: authoritative bus, interpreter driver, fixtures,
  optional read watches, bounds/peripheral faults and register snapshots.
- emulator/harness/prepare.py,overlay/,instrumentation.patch,source-manifest.json:
  reproducible exact local instrumentation, pinned original hashes.
- emulator/tests/fixtures.json andrun.py:37 hand-auditable synthetic programs,
  independent expected writes/register results; programs exported with results.
- emulator/tests/audit_paths.py: source/site coverage guard and fixture assertions.
- emulator/tests/final_audit.py: cross-build trace hashes and protected-input checks.

**IMPLEMENTED:** P/X/Y are distinct vectors with configurable sizes through
`--sizes=P,X,Y` hexadecimal words. Generic fixture defaults each800 words;
these are intentional zero-initialized test memories, not a stock checkpoint.
Explicit toy shared window[30000,30020) aliases only X/Y into a separate shared
vector. Upstream generic bridge is disabled for relevant24-bit addresses.
The conditional Circuit memory map is not activated. Direct fixture verifies
X40=7,Y40=9,P40=0; shared fixture verifies cross-view consistency.

Memory callbacks replace the core's authoritative read/write/fetch path; spare
upstream buffers are not the modeled RAM. CPU, DMA and host/worker toy actor
stores use the same logger. Core/peripheral API surface outside the harness is
not certified merely by being present in the linked library.

JSONL records contain type,sequence,instruction_counter,PC,actor,memory_space,
effective_address,backing,old_value,new_value,instruction_word,address_register,
modifier,write_kind. Equal values are logged. NonCPU PC/opcode are null, not
invented. Parallel Rn attribution is null when ambiguous. Fixture source hints
identify loop/store kind; this is not a general architectural decoder of store
semantics. No wallclock timestamps or host pointers enter canonical traces.
EXEC records cover actual opcode entries including internalDO/REP iterations.

Snapshots recordPC,SR/OMR,SP/SC,LA/LC,R/N/M,rawA/B/X/Y,VBA/SZ/EP and all16
system-stack cells. Generic CLI watches acceptspace:lo:hi, e.g.X:35F:360;
no Circuit address is hardcoded into watch selection. Fault records include
attempted address and PC; invalid CPU reads/writes exit42. Unsupported peripheral
addresses fault; only explicit fixture-control ports are approved. Instruction
budget also applies inside internal loops. Unsupported chip behavior is not
silently modeled as a generic register bank.

## E–J. Store and execution results

**TESTED:**37 fixtures ×4 runs, across2 independent builds; all expected
results pass and every corresponding canonical trace is byte-identical.

| Mechanism | Tested result |
|---|---|
|Absolute/indirect|X/Y direct, Rn,postinc/postdec,predec,indexedN andoffset updates match expected addresses/values|
|P write|MOVEM fixture writesP40=7; raw077084000040 independently decoded by the existing Rust disassembler|
|Parallel|One instruction logs distinct X40/Y50 writes; both register advances checked|
|Arithmetic/bit store|Address update changes store destination; bit read/modify/write logged|
|REP|4 stores at40..43, distinct instruction ordinals, R0=44|
|DO|3 stores at40..42;offset2 variant40/42/44; nested2×3 captures6 writes|
|Modulo|M0=3,size4:increment43→40 wrap anddecrement40→43 wrap; five accesses/finalR0 match|
|Linear modifiers|FFFFFF andtested00FFFF fixture advance correctly; not a claim about all stockSR modes|
|DMA|Actual upstream copy/fill/fixed-destination/P/shared paths log each destination; peripheral-source repeated-read fill and peripheral destination copy also tested; DE-trigger controller fixture logs fourY writes|
|Same value|Two zero-over-zero writes both recorded|
|Faults|Invalid CPUread/write, unsupportedMOVEP andsmallerY configuration fault deterministically|
|IRQ/call|Syntheticvector20→handler600→RTI resumes interrupted code;PC sequence,SP/SC/SR checked;JSR/RTS also passes|
|Read watches|SelectedX40 read logged once; others remain unlogged|
|Actor bus|HOST/WORKER/PERIPHERAL toy events logged; no realICC worker claimed|

Modulo expectations follow Mn=buffer_length−1 and aligned-base wrap rules in
[NXP DSP56300FM, sections4.4/4.5](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf).
Synthetic fixture formulas/expected addresses are declared independently of
the observed trace. Final traces and results.json are under `validated/` and `validated-repeat/`.

**Source completeness test:**203 local upstream files registered, plus harness/
build/fixture hashes. Unknown/new/changed source fails mandatory review. Static
checks require the RAM overrides and REP hook and reject restoredDMA memcpy,
directfill or new raw-pointer call sites. Required store-form fixtures must pass.
A separate negative source copy withanunregisteredstore.cpp was rejected before
producing a passing audit. This prevents unnoticed source evolution; it is not
a formal proof about all conceivable emulator APIs/ISA forms.

## K–N. Gates, scope and next step

| Gate | Result in supported fixture configuration |
|---|---|
|A reproducible interpreter build|TESTED PASS: two independent builds, same recipe/source|
|B distinct spaces|TESTED PASS|
|C ordinary stores|TESTED PASS|
|D AGU stores|TESTED PASS|
|E REP coverage|TESTED PASS|
|F DO coverage|TESTED PASS|
|G modulo addresses|TESTED PASS for documented tested modes|
|H DMA copy|TESTED PASS|
|I DMA fill|TESTED PASS|
|J same-value stores|TESTED PASS|
|K invalid-memory faults|TESTED PASS|
|L interrupt fixture|TESTED PASS|
|M canonical determinism|TESTED PASS:37×4 runs|

**UNRESOLVED future scope:** complete ISA/mode validation, unknown-state tracking,
stock OMR/map/ROM handoff, Y clear outside conditionalRAM,EMC/hosttables,worker/
ICC/Circuit DMA/ESAI timing, other external/peripheral/raw-pointer APIs. DMA data
movement instrumentation is validated; real-time arbitration/overlap semantics
are not certified. JIT store paths remain unqualified and disabled. Full logging
metadata and stock source provenance need later expansion; fixture classification
must not be reused as an invented stock semantic label.

**Phase19B decision:** substrate gates support proceeding to separately requested
stock loading/provenance work. Full stock startup execution remains gated by19B
state/map/table resolution and unsupported accesses. No19B action occurred or
automatically follows. X35F/high-X ownership remains NOT-YET-DETERMINED; no
allocation or Plaits work.

**Single best next step:** Phase19B immutable load and startup-entry prerequisites,
only when explicitly requested; retain fail-closed mapping/state gates.

## Reproduction

```powershell
./emulator/build.ps1 -BuildDir builds/phase19a/new-build
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B emulator/tests/run.py --exe builds/phase19a/new-build/ct_replay_fixture.exe --output-dir builds/phase19a/new-tests
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B emulator/tests/audit_paths.py --results builds/phase19a/new-tests/results.json --output builds/phase19a/new-audit.json
```

Fresh tests/trace/audit/source outputs required. Installed tool paths are pinned
inbuild.ps1; no downloads during build. Dependency source must already exist at
its recordedrevision. OriginalSYX/BIN andallfive extraction-pair hashes passed;
unmodified vendor/overlay reproduction passed. Canonical evidence:
builds/phase19a/reproducibility-final.json and validated/complete-source-audit.json.
