# Memory and resource status — final pre-hardware review

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

Evidence precedence: [final allocation decision](<research/final-indirect-resolution/findings.md>) controls the remaining software proof boundary; [USB joint-path closure](<research/final-two-check-closure/usb-joint-closure.md>) records 36 passing focused cases. [Phase67](<research/phase67-final-safety-disposition/findings.md>) retains its bounded configuration/query/authorization-to-capture-entry scope. The frozen [package audit](<research/final-hardware-test-package/final-cheap-checks.md>) preserves the earlier two-gap history, with a current supersession notice. No model PASS is physical proof.

## Primary accepted residual SOFTWARE uncertainty

**POST-READY ALLOCATION CENSUS = UNQUALIFIED.** Static analysis did not exhaustively resolve indirect/virtual targets, including **0x0803C91C**, **0x0803C9C4**, and registry/object-method sites. No actual post-READY allocation >8 bytes was found; its absence is NOT proven. The modeled heap cursor is `20044D68`, cap `20044D70`: eight bytes, not physical stack margin or replenished per-request capacity.

The recovered normal-publisher set for `08022E22` has seven targets. Four are allocator-free; three lead to unresolved virtual continuations. The expanded ledger covers 260 encountered indirect sites, 233 unresolved, and 73 target summaries. These are conservative traversal counts, not 233 proven allocation hazards or an exhaustive complete graph.

PROVEN in four isolated allocator ABI cases: rejection reaches BKPT; if execution is artificially continued after BKPT, R0=`FFFFFFFF`, accepted by the generic wrapper as nonzero. Physical exception routing remains UNKNOWN. Safe failure cannot be assumed. These isolated inputs do not prove a post-READY occurrence. See [findings.md](<research/final-indirect-resolution/findings.md>), indirect-ledger.csv (local-only reference: `builds/final-indirect-resolution/indirect-ledger.csv`; not distributed), and [failure-semantics.md](<research/final-indirect-resolution/failure-semantics.md>).

Authentic `$82000` data is not captured. P:`$0282-$0386` remains not finally qualified (261 candidate words, zero newly safe words); final safe DSP P/X/Y budget is UNKNOWN. Physical stack margin is HARDWARE-ONLY UNKNOWN.

# Historical Layout A

**PROVEN within older retained-stock-synth replay:** conservative dual MIDI oscillator replacement reclaimed 1075 P words. Layout A ends at P:`$3BB9` (15290 used), leaving contiguous P:`$3BBA–$3FFF`.

**Arithmetic correction:** that inclusive span is **1094 words = 1075 reclaimed + 19 original tail words** P:`$3FED–$3FFF`. Calling the entire span “1075 words” confuses newly reclaimed capacity with total address span. The historical admission budget remains 1075; this snapshot does not enlarge it to 1094.

THIS IS HISTORICAL EVIDENCE. IT IS NOT THE FINAL FOUR-TRACK PLAITS BUDGET.

Historical qualification includes 8192 exact retained blocks with active Synth1/Synth2, supported state/register/transaction checks, mixer/send automation and separate active Master FX tests. Sample drums/capture/glitch are not universally covered. Layout B's extra 102 shared VA-control words and 1177 total are not substituted for conservative Layout A.

# Final architecture

Final safe **P/X/Y budgets: UNKNOWN**. No additional stock-synth region is admitted. Removal needs retained init/data-reference closure, not simply zero steady-state execution.

# P:$0282–$0386 candidate

261 contiguous words; **UNKNOWN — NOT YET QUALIFIED FOR RECLAIM**, zero newly safe words. P:`$0281` retains RTS in the generation-disabled study. Authentic initialization is blocked on external NOR coefficients. Guarded steady-state/prefix replay cannot qualify initialization it never completed. Adjacency to other unqualified ranges is not safe capacity.

# NOR $82000 role — provenance dependency

Phase65 later completed synthetic coefficient uploads/startup jobs; that mechanical model coverage does not authenticate physical coefficients or qualify P-memory reclaim. The pending authentic-data statements below describe the resource/provenance dependency, not a request for more peripheral emulation.

**PROVEN path:**512 bytes `$82000–$821FF` feed coefficient-storage initialization:

`08035E28 → 08047C6C → 08024130 → 08023F68` (enqueue), wait `08023FD6`, Storage worker `08024014`, backend `08022F94`, reader `08037430`; ARM SRAM destination `0x20005148`.

`08035EC8 → 080292DC` selects core0 X:`$0C00`; `08035ECE → 080295E4` selects 16-bit SHI. After read, `08035EEE → 0802968E → 0803BA78` sends 512 bytes as 256 16-bit values to X:`$0C00–$0CFF`, MSB-first into DSP bits 23:8 via P:`$0198`. `08035EF4 → 08029626` restores 24-bit SHI. `08035F04 → 080292F8` posts selector 0/Y:`$002C` (`$0D1000`).

DSP P:`$0121 → $1C53` prepares X:`$2400`/Y:`$1400` basis and continuation X:`$1B15–$1B21`. Selector 0 harmonic-MAC P:`$1DF2` consumes 256 coefficients; first pending Y:`$1A6400` export and completion P:`$1DA2–$1DA9` remain blocked on authentic data.

**STRONG INFERENCE:** stored signed 16 harmonic-amplitude coefficients, not 512 waveform time samples. **UNKNOWN:** exact values/resulting waveform identity. Copies/checkpoints and synthetic data do not establish physical NOR provenance.

# NOR $81000 role

**PROVEN:**23-byte boot read `$81000–$81016`: Main `08003A42 → 08005D98 → 08005880`, queue `0x20007A60`, worker/backend `08005338 → 080076CC`, destination `0x2000546C`. DMA NDTR 23 / DLR 22, address `$81000`. Main `08005DAE / 08005DB0` then zeroes byte 14 at `0x2000547A`.

Application cache `0x20006868` is distinct. Cached zero byte 14 cannot reconstruct its original value. **STRONG INFERENCE:** identity/serial-like record. **UNKNOWN:** authentic original record, unchanged provenance of other 22 bytes and complete asynchronous completion-to-zero observer closure. Phase39 symbolic-byte 14 equivalence did not pass those gates.

# Data-memory candidates, not allocations

| Region | Evidence limit |
|---|---|
| X:`$3B80–$3BEF` | Retained mailbox/save infrastructure |
| X:`$00EB–$015A`, X:`$057A–$08F1`, Y:`$011F–$059E` | Descriptor/voice/ARM parameter users retained |
| X:`$1960–$19EF`, X:`$1400–$15FF`, Y:`$059F–$077E` | Candidates; init/alias/ownership not closed |
| X:`$2C46–$2C65` | Output/scratch, not private persistent state |
| Shared `$30000–$37FFF` | Cross-core work, no whole free allocation qualified |
| Shared granular base `$37000` | Counter/task, voices/grains and exchange buffers retained |
| External `$340000–$37FFFF` | Retained stereo glitch ring |
| Core1 P:`$07FF–$3FFF` | Arithmetic tail only; service/admission unknown |

Use explicitly owned X/Y/data records for mutable state. Code/LUTs may be shared if visibility is proved; phase, histories, envelopes/LPG, RNG, FIFO and delay/resonator state remain independent. Shared scratch requires serialized lifetimes/save contracts.

# Why capture the fixed regions

Required target:512 bytes at$82000. Optional target:23 bytes at$81000, separately authorized. The host must validate actual retained first-mount geometry before same-epoch reads. No authentic target bytes have been acquired. Capture supplies inputs for later initializer replay; it does not itself qualify reclaim, historical pre-install identity or final resource fit. Hash/archive complete accepted bytes with acquisition provenance.

Phase67 scoped preflight is complete; the later operational allocation census remains UNQUALIFIED. Earlier geometry/preservation investigations explain the gate, rather than pending automatic research. The existing B1.3/MSD geometry-authentication branch was exhausted in Phase53. See [findings.md](<research/phase67-final-safety-disposition/findings.md>).

Evidence: [historical master qualification](<../notes/stock-master-signal-path-qualification.md>), 8192-block verification (local-only reference: `builds/phase20l-master-path/final-verification.json`; not distributed), [four-track resource audit](<../notes/four-track-plaits-resource-architecture.md>), [P0282 qualification](<../notes/p0282-0386-reclaim-qualification.md>), [NOR 81000](<research/phase38-nor81000/findings.md>), [symbolic limits](<research/phase39-nor81000-symbolic/findings.md>), [historical Phase43 — SUPERSEDED](<research/phase43-hardware-test-candidate/findings.md>).
