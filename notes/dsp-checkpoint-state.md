# Phase 19C-CHECKPOINT: partial snapshot contract

## Phase 19C-PARENT — actual normal checkpoint not admitted

2026-10-06. [dsp-parent-replay.md](dsp-parent-replay.md) records the current
gate. **UNRESOLVED:** no verified normal predecessor publishes a1E15 target,
or actual SP/SC/frame history at parent entry. Do not supply descriptor/table
targets, reset depth, LF0, incoming LA/LC or foreign-actor exclusion by hand.
**VERIFIED conditional:** D99's counted outer DO gives LF1/LA=DAF/LC1..5 if
its algorithm wrapper calls the parent. This differs from the old inactive-loop
class. Parent-local DOs are closed at1E80/1EE5, but inherited LF persists.
Potential occupancy is s+5 through an algorithm wrapper, s+4 through a changed
DB6 direct tail target, or s+2 through descriptor19AC, with s at1D9 entry and
healthy balanced prior frames; actual alternatives/s are not recovered.
**TESTED:** normal replay refuses before output/CPU creation.0 new original
instructions; no concrete normal checkpoint. Old bounded snapshots are retained.

2026-10-06. **VERIFIED static provenance / SYMBOLIC numerical data.** This
contract describes a bounded later-state property experiment. It is not an
authentic ROM exit, startup snapshot, captured device state or universal normal
runtime invariant. No ROM search, installation, hardware, transmission, firmware
patch or Plaits work occurred.

## Selected checkpoint candidates

| Candidate | Minimum local inputs | Disposition |
|---|---|---|
| P1F5C whole helper | X1D40..42, counts, M/N, coefficient/state buffers, stack/call/outer loops and arithmetic modes | UNRESOLVED full replay; not replaced with guessed state |
| P1F89 cursor load | R6=1800+j or19F0+j; M6=FFFF; Y1820+j or1A10+j retained initialized value | TESTED 64 one-instruction slices |
| P1F90 inner DO | X3A=32; current A/X1/R3/R7; inherited outer LA/LC/LF; stack/extension state | UNRESOLVED full loop entry; no stack defaults promoted |
| P1F92 inner body | R3=2C8A+i; R7=c+j-parity+i; M3=FFFF; M7=FFFF or3FF; A/X1 and read data symbolic | TESTED 4096 six-instruction slices through1F97 |
| P203A zero consumer | R0=35F; M0/M5=FFFF; N5=0; X35F..363=0; Y0=0; candidate-device SC0 | TESTED two seven-instruction zero-skip slices |
| P204B single store | R4=0 derived from cleared X364; B symbolic | TESTED two consumer-calibration slices only; positive-count entry unproved |

The selected latest entry before the cursor store is1F92. Index i spans0..31;
outer index j spans0..15 in each family. These indices are static loop-relation
coordinates, not recovered runtime counters. We do not advance PC manually
between instructions in a slice. Each independently supplied snapshot starts a
new CPU. This does not simulate the DO branch or join snapshots into a single
executed block. Inner-loop edge processing, stack restoration and outer-loop
control after1F97 are excluded from the projection. The dispatch PC recorded
at END is not certification of the real inherited-loop next PC.

## Concrete field provenance

VERIFIED bytes and existing Phase13/15 data flow support:

- P260A..261F initializes16 alternating cursor words in each Y family.
  Even/odd A values2CCC/2CEC; B values2C02/2C24. All32 words are individually
  exported in cursor-table.json. Reading them at1F89 is replayed separately.
- Caller setup P1E76/P1ED9 supplies R6 base1800/19F0. Each1F8C advance adds1
  to R6. Hence cursor-load checkpoint R6=base+j.
- P1F8D supplies R3=2C8A;1F92 postincrements it once/iteration.
  P1F89 supplies R7 from the cursor;1F97 postincrements once/iteration.
  Body checkpoint inputs therefore R3=2C8A+i, R7=c+i.
- P2779..2781 initializes modifiersFFFF. Reviewed P265 temporarily selects
  M7=3FF. Both alternatives are examined; neither permits wrapping in the
  initialized32-address windows. Their retention is a checkpoint premise,
  not a closed foreign-writer invariant.
- X3A=32 is the proven stock body count. Enumeration over i0..31 uses that
  static premise; the positive DO at1F90 was not executed in this phase.
- P2035 fixes R0=35F. P2788 clears X35F..363 and P2789 clears Y0.
  Y30 is initialized0 at1BA8/1BA9;2034..2038 then gives N5=0.
  These define the conditioned initialized-zero checkpoint, with no intervening
  relevant mutation. This is not claimed to be the actual final boot snapshot.
- Candidate DSP56724/25 table5-2 reserves SR13, supporting SC0 for zero-skip
  semantics. Exact physical part identification remains conditional.

Every numerical snapshot field has a provenance string in checkpoints.json.
Conditional preservation premises are retained. No positive X35F domain was
invented; adjacent20-record capacity is not a count producer or count bound.
No worker/ICC value is needed for these isolated private-memory slices.

## Schema and symbolic execution boundary

Machine-readable schema: `ct-checkpoint-v1`, with per-instance CPU fields,
X/Y subsets, exact immutable P SHA256, symbolic fields, provenance, selected
entry/stop, scope and parameters. CPU fields use `value:null` for unknowns;
partial SR has known_mask/known_value only for the candidate reserved SC bit.
Full SR/OMR/stack/accumulators are never checkpointed as zero.
Partial OMR additionally carries mask600080/value400080 from the uploaded
shim's memory-mode transformation, explicitly conditioned on retention. Its
actual ROM preservation remains unproved. Other bits stay symbolic.

Native numeric core backing for unknown arithmetic/control data uses two
explicit transport encodings. These are not stock values or additional
legitimate checkpoint states. They are discarded from numerical results.
Arithmetic/store data remains SYMBOLIC_DATA and is logged as null. Paired
encodings must have identical instruction/address/modifier projections.
Two representations are a metamorphic check, **not exhaustive enumeration of
arbitrary 24-bit data or every SR word**.

The soundness boundary is a small audited instruction whitelist executed by
the existing interpreter, not a new DSP decoder. For each accepted instruction,
unknown data cannot feed an address register, branch, loop count or modifier.
Body loads produce X0/B; arithmetic produces A/B/Y0/flags; the store consumes
B only as data. R3/R7 effective-address relations are checked before dispatch
and every actual bus access is checked. No conditional branch consumes flags.
Cursor loads require a known initialized word before accepting R7. In the
record consumer every pointer/count/index source used is known0/35F; DO0 uses
documented SC0 and performs no stack push. All other memory reads, peripheral
accesses, instructions, P writes and out-of-domain modifiers/indexes refuse.

Other SR arithmetic modes only affect symbolic data in the body. They are not
claimed numerically modeled; all output words remain unconstrained. OMR mapping
uses the declared private P/X/Y bus profile, and no stack/extension/cache/port
operation is admitted. The admitted low addresses fit the reviewed candidate
main-core map; this does not implement arbitrary OMR remapping or prove board
memory mode. The backing OMR retains the explicit600080/400080 relation; its
other bits are not checkpoint values. Unknown LF/LA/LC/stack state is not
substituted to run a loop edge.

The experiment has no asynchronous events. This is an explicit isolation of
the property domain, not proof that stock interrupts/worker/mailbox activity
cannot intervene. Prior ROM-authentic startup gates remain closed.

## Unresolved local prerequisites

- Full1F5C/1F90 stack depth, extension mode, saved outer loop and caller entry.
- Actual normal parent1E15 reachability and foreign saved-base/cursor/modifier
  preservation across blocks.
- Positive X35F publisher, valid complete destination records and final-prefetch
  provenance for positive counts.
- Numerical accumulator/coefficient/effect state and all-mode arithmetic output.
- Interrupt, host/SHI, worker and background mutation between snapshots.

None is a hidden default. The runner refuses unsupported control dependencies;
the implemented address projection stops before those obligations arise.

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
