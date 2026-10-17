> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 19C-CHECKPOINT: bounded original-opcode replay

2026-10-06. **TESTED / BOUNDED-PROOF for the declared local address domain.**
Universal stock invariants, persistent high-X allocation and authentic boot
remain **UNRESOLVED**. Original firmware and all extracted streams are intact.

Implementation: `emulator/harness/checkpoint/` (native runner, build recipe,
collector). Tests: `emulator/tests/test_checkpoint_state.py` and
`emulator/tests/verify_checkpoint.py`. It links the existing sealed Phase19A
forced-interpreter libraries. That core's authoritative Memory.replayRead /
Memory.replayWrite hooks capture every admitted X/Y access. No core, original
image, legacy19A harness, decoder or protected source manifest was changed.
No hardware APIs, device I/O, transmissions, ROM searches or installation.

Exact original main payload SHA256:
`b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855`.
The native loader independently verifies size/hash before execution. P is an
immutable source array behind the bus; original opcodes are dispatched by the
sealed interpreter. P writes and out-of-scope reads/peripherals are rejected.

## Executed coverage

| Slice | Cases | Original opcode executions | Meaning |
|---|---:|---:|---|
| P1F92..1F97 |4096|24576|32 cursor cells ×32 static iteration coordinates ×2 M7 alternatives ×2 symbolic-data backing checks |
| P1F89 |64|64|All32 initialized cursor values, paired backing checks |
| P203A..2040 |2|14|Initialized zero consumer; DO skips to204C |
| P204B |2|2|Single-store calibration at cleared destination0, not a reachable positive-count scenario |
| Total |4164|24656|Bounded original-opcode dispatches; no authentic boot instructions |

The cursor slices are six instructions, not seven. Count figures are per
invocation. The independent repeat executes the same domain again; it is not
additional distinct state coverage. Unknown numerical words/modes are carried
as an address-only SYMBOLIC projection, not concrete sample values.

See `dsp-checkpoint-state.md` for per-field provenance and projection rules.
Checkpoints.json records all partial CPU/X/Y state, parameters and P identity.
Two numeric backing representations for symbolic operands must agree in
control/address observations; their data are not promoted into evidence.

## Differential validation and address results

TESTED: every original cursor-load instruction reads the correct initialized
Y word. Every body slice dispatches the exact stock words92..97, reads the
expected R3/R7 addresses, performs exactly one X store at1F97 and advances R7
once. Aggregating independently checkpointed i0..31 reproduces each exact
32-address interval:

| Source Y cells | Parity | X store interval, end exclusive |
|---|---|---|
|1820..182F|even|[2CCC,2CEC)|
|1820..182F|odd|[2CEC,2D0C)|
|1A10..1A1F|even|[2C02,2C22)|
|1A10..1A1F|odd|[2C24,2C44)|

Both M7 alternatives match. The B family has a two-word hole; it is not
collapsed into a contiguous exact union. This validates body effective-address
behavior at every static iteration coordinate; **the32-iteration DO itself,
complete helper, foreign preservation and actual caller scheduling were not
executed or proven**.

TESTED zero record consumer:203A reads X35F0;203B..203E reads X360..3630.
203F still reads Y0 before checking the loop. DO at2040 uses latched count0,
skips to204C, performs no204B store and does not need a guessed DO stack.
Both replayed203A entries record X35F0. No positive-count publisher was found
or invented. The twenty adjacent positions are not twenty active records.

TESTED one-store calibration: original204B writes exactly one X word at R4=0,
with no destination postincrement, and symbolic B data. This confirms the
consumer's unindexed store and logger behavior. It **does not validate an
executed multi-record positive-count table walk**; that remains UNRESOLVED.
No calibration store is included as a normal checkpoint counterexample.

| Property | Classification for admitted local checkpoint domain |
|---|---|
| Any X35F write? | **PROVEN FOR CHECKPOINT DOMAIN: NO** |
| Any write into X[340,360)? | **PROVEN FOR CHECKPOINT DOMAIN: NO** |
| Any access into X[340,360)? | **TESTED YES: two zero count reads at35F** |
| Any write into X[5F00,6000)? | **PROVEN FOR CHECKPOINT DOMAIN: NO** |
| Nonzero35F at replayed203A? | **PROVEN FOR CHECKPOINT DOMAIN: NO**, by initialized-zero domain |
| Every normal invocation preserves these properties? | **UNRESOLVED** |

These results validate the earlier conditional address argument. They do not
remove the cursor family from the universal X35F blocker set or establish a
persistent256-word allocation. There is no normal-domain disproof witness.

All X/Y reads and writes are in trace.jsonl, including PC/opcode, checkpoint
identity, dispatch count, space/effective address, relevant AGU modifier,
concrete-or-symbolic data tag and declared slice call path. Actual callers are
not executed and are not presented as dynamic call traces. Watched-accesses.json
separately exports the target interval/high-X events; x35f-entries.json exports
every replayed203A value. No numeric unknown result or backing placeholder is
reported as a concrete firmware value.

## Usefulness and limits

| Gate | Answer |
|---|---|
| A reproduce1F97? | YES for cursor loads/body slices; full helper UNRESOLVED |
| B reproduce203A? | YES initialized zero consumer; positive-count path UNRESOLVED |
| C capture all local effective writes? | YES for admitted slices through authoritative hooks |
| D valid local state hits35F? | NO writes in admitted domain; universal UNRESOLVED |
| E valid local state hits high-X? | NO writes in admitted domain; universal UNRESOLVED |
| F reduce memory-risk argument? | YES local execution checks strengthen scoped proof; persistence remains open |
| G authentic full boot independently unresolved? | YES |

BOUNDED-PROOF means the initialized-cursor/retained-modifier and initialized-zero
relations, private bus mapping, no asynchronous event intervention and audited
data-only symbolic flow. It is not a proof for arbitrary service states or all
normal block transitions. Full-loop edges/stack, mode changes, whole program,
worker/ICC and audio scheduler are not certified. All retained universal
X35F/high-X blockers remain. No Plaits PoC allocation/design gate is passed.

**Single best next step:** qualify a complete P1F5C nested-loop checkpoint's
stack/outer-loop/control relation and symbolic-data interface, then join these
body slices using original DO/call instructions. Keep this offline and scoped;
do not use presumed ROM/reset stack values or seek more ROM in this phase.

## Reproduction and integrity

```powershell
./emulator/harness/checkpoint/build.ps1 -BuildDir builds/phase19c-checkpoint/new-build
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B emulator/harness/checkpoint/collect.py --exe builds/phase19c-checkpoint/new-build/ct_checkpoint.exe --output-dir builds/phase19c-checkpoint/new-audit
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B emulator/harness/checkpoint/collect.py --exe builds/phase19c-checkpoint/new-build/ct_checkpoint.exe --output-dir builds/phase19c-checkpoint/new-repeat
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B emulator/tests/verify_checkpoint.py --exe builds/phase19c-checkpoint/new-build/ct_checkpoint.exe --first builds/phase19c-checkpoint/new-audit --repeat builds/phase19c-checkpoint/new-repeat --output-dir builds/phase19c-checkpoint/new-checks
```

Existing local MSVC/CMake and sealed19A libraries are reused. Fresh output
directories are mandatory; no overwrites. Canonical evidence: final/ and
final-repeat/ (first/repeat predate the explicit partial OMR mask and linked
substrate manifest). **TESTED:**13 files match byte-for-byte,6 checkpoint-schema
tests pass,5 native refusal gates pass (wrong image, overwrite, invalid cursor
index, unqualified modifier, unsupported full-helper control),
protected SYX/BIN and all ten extraction hashes pass,
and the sealed203-file core plus19A harness source guard passes.
See builds/phase19c-checkpoint/final-checks/reproducibility.json. The linked
substrate manifest hashes both libraries and the validated19A fixture binary;
binary provenance is recorded separately from the unchanged source guard.

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
