# Phase 19B — immutable load completed, startup gate blocked

2026-10-06. **IMPLEMENTED / TESTED:** original Selection-0/channel-0 payload
loaded through the pinned core's Memory API and authoritative P bus, read back
word for word. **Stock instructions executed: 0. Stock startup success: NO.**
This is the requested load-first stopping rule applied to an unresolved handoff,
not a claimed failing execution trace. No hardware, transmission, firmware
changes, worker execution, Plaits or scheduler replay.

The final evidence directories are `builds/phase19b/completed/` and
`completed-repeat/`; verification is `checks/reproducibility.json`. `first/`
is an incomplete development run: the constructor-only probe initially rejected
its library reset priority write, after loading but before any execution. It is
not a stock runtime fault. `validated/` and `validated-repeat/` precede the final
explicit reset-profile discrepancy report; use completed directories.

| A–P deliverable | Result |
|---|---|
|A exact artifact|Original `selection0-channel0.payload24.bin`,32538 bytes/10846 BE24 words; SHA256 b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855|
|B load verification|TESTED MATCH: all10846 P words, P[0,2A5E), source/stream/BIN linkage and hashes; six header bytes excluded; 10846 ordered LOADER transactions|
|C initial/handoff state|PC0 derived from boot record; complete post-bootstrap/ROM state UNRESOLVED. Documented chip reset and implementation defaults kept separate|
|D startup entry|P:0→100, verified by loaded-memory decoder; not executed|
|E instruction count|0|
|F first blocker|Pre-execution handoff/live control gate; first anticipated peripheral is P100 YFFFFFA read/modify/write|
|G startup clear|NOT REACHED; no zero-store execution validation|
|H tables/cursors|NOT REACHED; immutable table source hashes MATCH|
|I static/execution matches|16 load-decoded instructions match bytes/lengths; four targets match. Execution differential NOT REACHED|
|J peripherals reached|None by stock execution. Anticipated GPIO100/101,ICC102, then further startup I/O|
|K worker reached|NOT REACHED; required readiness source is statically identified. Adequate model UNRESOLVED; no worker loaded|
|L determinism|Two independent load/probe invocations yield identical exports. Stock execution determinism NOT TESTED|
|M mismatches/unresolved|No stock execution mismatch. Constructor differs from documented SHI reset PC and OMR priority bits; handoff, interrupts, GPIO, ICC and later map/EMC/host tables remain open|
|N19C justified?|Yes for separately requested handoff/peripheral contract work. Startup has not passed; scheduler replay remains gated|
|O original firmware executed?|NO. Loaded and decoded offline, never executed|
|P best next step|Establish a documented minimum post-ROM state/GPIO/ICC contract for P0→100..106 before enabling stock interpreter execution|

`emulator/stock/main.cpp` is a distinct load-only executable. It leaves all
Phase19A source and manifests unchanged, verifies input size/hash before any P
load, opens input read-only, keeps const source bytes separate from mutable
bus P state, and rechecks source identity after load. Output must be fresh and
inside phase19b; no overwrite option exists. Its three unknown-read tests cover
X0,Y0 and the unloaded P tail. Runtime execution/P stores cannot occur in this
executable; a future runtime driver must retain source immutability and log all
architectural P stores rather than reject legitimate self-modification.

P words beyond the original payload and all X/Y values remain unknown. Core host
allocation/zero backing is not silicon initializedness: Memory API reads are
guarded by the authoritative bus. No CPU is attached to the stock-loaded memory.
A wholly separate empty-program constructor probe records implementation reset
values, without executing instructions or providing stock initial values.

Artifacts include immutable/initial-state manifests, native P readback BE24,
native decode witnesses, load transactions, static startup witnesses, expected
initialization assertions, canonical load/gate JSONL, fault/mismatch report,
tagged CPU/P/X/Y unknown-state records and hashes. **The CPU/X/Y hashes describe
canonical partial/unknown state, not actual executed final RAM/register snapshots.**
Empty execution/transaction/watch logs likewise are not passing startup traces.

Reproduce from project root, existing tools/dependencies only:

```powershell
./emulator/stock/build.ps1 -BuildDir builds/phase19b/new-build
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_stock_load_audit.py --exe builds/phase19b/new-build/ct_stock_load.exe --output-dir builds/phase19b/new-load
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_stock_load_audit.py --exe builds/phase19b/new-build/ct_stock_load.exe --output-dir builds/phase19b/new-repeat
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B emulator/stock/verify.py --exe builds/phase19b/new-build/ct_stock_load.exe --first builds/phase19b/new-load --repeat builds/phase19b/new-repeat --output-dir builds/phase19b/new-checks
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_dsp_reset_docs.py --output-dir builds/phase19b/new-doc-evidence
```

Negative gates test a three-byte synthetic non-firmware input (rejected before
loading), existing-output refusal and out-of-phase output refusal. Original
payload/source files are not changed to manufacture a negative test. The 203-file
Phase19A guard and original harness-file hashes pass before each completed load.
Official manuals were archived for new reset/handoff research; no upstream core
refetch or tool installation was performed. See `dsp-boot-handoff.md` and
`dsp-stock-startup.md` for the instruction and primary-document evidence.

## Follow-up Phase19B-HANDOFF — 2026-10-06

New static evidence and minimum contract are in `dsp-rom-handoff.md` and
`builds/phase19b-handoff/final/`. This does not change the19B1 load result or
claim19B2 success. GPIO latch semantics, bootstrap-local effects, ordered ARM
uploads and initial/progress ICC pointer provenance are now explicit. Matching
ROM exit state remains unresolved. A source-attachment discovery lead returned
403 and is not promoted to trusted code.

`emulator/stock/handoff_gate.py` only inspects explicit provenance; it constructs
no CPU and cannot enable execution. Current eligible assignment isPC0 only.
SR/OMR/GPIO/ICC cannot acquire constructor/reset/token defaults. Main/worker
original instructions executed remain0. No automatic19B2 or19C work follows.

## Phase 19B-SYMBOLIC follow-up

Additive partial-state primitives and a narrow startup adapter under harness/
leave the sealed concrete core unchanged.24 focused tests pass: bit operations
preserve unknowns and material uses fail closed. Original attempts remain blocked
by unknown pending/PIC/SR.I recognition before the first instruction. Partial
snapshots describe sets of states, not concrete hardware observations. No stock
execution count or ownership proof was upgraded.

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
