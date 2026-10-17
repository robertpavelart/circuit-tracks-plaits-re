> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# P:$0282–$0386 reclaim qualification

**2026-10-15 follow-up:** the final section below supersedes the earlier diagnosis and next experiment. The old P:$1B44 stop is explained by a suspended-fetch/cache fault in the fixture and an unreachable stop condition while audio is disabled. A continuously resumed four-job initialization prefix now passes with the target guard. The complete initializer still requires the original coefficient-storage service and authenticated payload; reclaim remains **UNQUALIFIED**, with **0** safe words added.

2026-10-15. **UNKNOWN — reclaim remains UNQUALIFIED.** The exact interval contains 261 words. No retained execution, data read, or write into it was observed. That is insufficient for admission: the integrated table-initialization transition does not complete in the unguarded baseline, and the MIDI program-change path waits for an ARM task that this fixture does not run. **Safe additional words admitted: 0.** This is not a demonstrated retained dependency on a particular word in the interval.

The experiment stays on this interval. It neither ports Plaits nor creates firmware, changes pinned/reference sources, or accesses hardware. Its new executable is an instrumented Windows DSP interpreter. Existing BE24 fixture programs are copied unchanged; the pre-existing logical generation disable (`P:$0281 = $00000C`, RTS) is applied in emulator memory to **both** variants before either DSP boots. The only new ownership guard is core0 P:$0282–$0386. Existing high-tail canaries and emulator-only call stubs are common fixture infrastructure; none is counted as reclaimed stock memory.

## Evidence and reproduction

All experiment files are under phase23-p0282-0386 (local-only reference: `builds/phase23-p0282-0386`; not distributed). Primary evidence:

- evidence.json (local-only reference: `builds/phase23-p0282-0386/evidence.json`; not distributed): completed comparisons, unsuccessful prerequisites, observed P-data reader domains, hashes and zero admission.
- classified-references.json (local-only reference: `builds/phase23-p0282-0386/classified-references.json`; not distributed): every decoded incoming/internal edge, all 21 external immediate literals in the numeric interval, all 51 matching raw word values, seven decoded indirect sites, and remaining closure gaps. Raw numeric matches are not automatically P references.
- core0.asm (local-only reference: `builds/phase23-p0282-0386/core0.asm`; not distributed): disassembly of the actual Layout A fixture; addresses below are core0 P unless another space is stated.
- prepare.py (local-only reference: `builds/phase23-p0282-0386/prepare.py`; not distributed), coupled.cpp (local-only reference: `builds/phase23-p0282-0386/coupled.cpp`; not distributed) `targetAccess`, `replayAccess`, `replayFetch`, `STATEWRITE/STATECHECK`; build-provenance.json (local-only reference: `builds/phase23-p0282-0386/build-provenance.json`; not distributed).
- replay.py (local-only reference: `builds/phase23-p0282-0386/replay.py`; not distributed) `Pair.send`, `Pair.block`, `first_three_table_jobs`; probes.py (local-only reference: `builds/phase23-p0282-0386/probes.py`; not distributed) `run`; guard-controls.json (local-only reference: `builds/phase23-p0282-0386/guard-controls.json`; not distributed).

**PROVEN:** baseline and guarded fixture files have the same SHA-256, `e7eee50bc85c995cc9ca00b5bdc55ce279366bfe747bb93b2fc43db3e511f4c0`, before the identical runtime RTS. All 451 previously recorded reference inputs and all 183 pinned Plaits source files match their earlier hashes. The architecture report before this update matches its prior final-validation hash, `2b31aa6f2c0b8ccdeb15795eb2de1afcacf6c012f829c865716ef7d1e361a8be`. evidence.py (local-only reference: `builds/phase23-p0282-0386/evidence.py`; not distributed) performs these checks without changing those sources.

Reproduction uses Python 3.14 with `-B`. Build with `prepare.py`; disassemble/inventory with `static_inventory.py`; run `replay.py <fresh-name> 256`. `probes.py` accepts `kind:fresh-output-name`, with kinds `patch-reload`, `project-restore`, `program-change`, `table-helpers`, and `table-init-serviced-recorded`. The retained replay and main-loop-service probe remain distinct. Do not rerun into existing evidence directories. The original unsuccessful and interrupted directories remain preserved.

## Original ownership and control reachability

**PROVEN:** $0282–$0386 is the body of the stock per-slot synth context/control routine whose entry is $0281. It loads the slot bank from X:(R3), sets X:$CC/$CD and bank offset X:$CB, consumes voice flags, updates oscillator/envelope records, and calls the stock generator helpers. It is not a standalone immutable LUT. Specific boundaries in `core0.asm`:

| Source / reference | Classification | Finding |
|---|---|---|
| $0281 original `move r0,x:$2` → $0282 | REMOVED WITH STOCK SYNTH GENERATION | Sole established entry fallthrough. The common RTS prevents it from boot onward. |
| $0282–$0378 internal branches and DO bodies; $0379 RTS | REMOVED WITH STOCK SYNTH GENERATION | Internal targets and loop endpoints are enumerated in `classified-references.json`; no independent retained entry established. |
| $037A→$04D5, $037C→$0657, $037E→$0387; $0384→$077F; $0386 RTS | REMOVED WITH STOCK SYNTH GENERATION | Outgoing synth helper/worker calls. This experiment does not reclaim the callees. |
| $0280 RTS preceding entry | RETAINED | Previous routine terminates; no ordinary fallthrough from its body. |
| $2881 initializer; $2892 loads R2=$0281; $2898 twelve-iteration loop, $289A stores function word | CONDITIONAL | X:$EB+8*i, i=0…11, points to $0281. Retain these entries as RTS calls. Function-word integrity remains a prerequisite. |
| $19A5 loads R1 from descriptor; $19AC `jsr (r1)` | RETAINED | Shared 14-slot dispatcher. It still calls $0281: 6,540 times in the 256-block case, with zero $0282–$0386 fetches. |
| $28AC/$28BC slot12 initialization; $28C7/$28C9 slot13 initialization | RETAINED | Other descriptor roots are $202B and $1A2B, outside the interval. |
| $0DB6; $0DBD/$0DC5/$0DCD/$0DEC/$0DF9 | RETAINED | Other decoded indirect jump/calls are effects dispatch. X:$9D8/$9DB-related tables are initialized by $29EC/$29F2 from P:$29F6–$2A2C. Their initializer values are outside the target; arbitrary descriptor corruption is not a qualified input. |
| $2706 word `$0FC316`, decoded `jsnr $0316` | RETAINED **data**, not a control reference | See below. This apparent external edge is a false positive from linear disassembly. |
| Complete asynchronous program/preset loader, uncaptured cold ARM reset sequence | UNKNOWN | Runtime coverage does not close these paths. |

**PROVEN:** the one apparent decoded external branch into the interval is not executable code in its established boot use. $268B branches over P:$268C–$2716 to $2717. At $2717, R0=$268C and R1=$1EDD; the $8B-word loop at $271B/$271D copies that entire P table to X:$1EDD–$1F67. Thus the numeric curve word at $2706 is copied to **X:$1F57**, not used as a P:$0316 destination. Each completed replay records 139 executions of reader $271D, one read of the $2706 table word, and zero instruction fetches at $2706. See `core0.asm`, each completed case's `data0.tsv` and `pc0.txt`, and `evidence.json` `P_readers`.

**STRONG INFERENCE:** with immutable dispatch roots and the common RTS, this body is synth-generation-only. **UNKNOWN:** complete input/restore reachability closure under every required transition. The table-word correction removes a false incoming edge; it does not establish that closure by itself.

## Data references and numeric collisions

**PROVEN:** the reviewed external immediate values in this numeric interval denote the following spaces or arithmetic, not P data inside the interval. Full instruction text and individual sites appear in `classified-references.json`.

| Instruction site(s) | Classification | Actual meaning |
|---|---|---|
| $01E8 `cmp #$300,a` | RETAINED | Audio-ring-distance threshold. |
| $0389 `#$299,R0`; $04D7 `#$2B5,R0` | REMOVED WITH STOCK SYNTH GENERATION | X voice/control arrays used by $0387/$04D5. These equal-valued X addresses are not P aliases. |
| $1299 `#$28C,R0`; $12AA `#$291,R0` | RETAINED | X descriptors, explicitly read at $12A0/$12B1. |
| $1A70 `#$2FE,R1`; $1A9B/$1AA3/$1AAB/$1AB5/$1AB9/$1ABD/$1AC1/$1AC5/$1AC9 | RETAINED | X control records $2FE, $2E1, $2D5, $2D6, $2D8, $2DC, $2E0, $2E9, $2EE, $2F1. $1B7B/$1B89 read/write X:(R1). |
| $1BC0 `#$362,R4` | RETAINED | Y voice/control record; $1BCE reads Y:(R4+$E). |
| $1CF7 `#$324,X0` | RETAINED | Selector2 table-generation loop count. |
| $2035 `#$35F,R0` | RETAINED | X drum/control descriptor, read at $203A onward. |
| $2A4C `#$2FA` | RETAINED | Peripheral initialization value for X:$FFFFBE. |
| $33C7 `sub #$296,b` | RETAINED | X mailbox/state field-offset arithmetic; store is X:(R7) at $33DC. |
| $3813 `sub #$340,a` | RETAINED | X granular/control record offset; subsequent access X:(R3+1), $381F. |

The raw-word scan additionally exposes X:$2FA in the absolute X read at $1A75 and relative branch displacement `$2BF` at $22EA: the decoded BSR destination is **$25A9**, not $02BF. Internal immediates/branch extensions are part of the removed body. No standalone jump-table entry pointing into $0282–$0386 was established from this scan. The seven indirect sites above, rather than raw numeric equality, are the remaining dispatch mechanisms to constrain.

**PROVEN for exercised paths:** all actual P-data reads are guarded, including initialization before `AUDIT`. Boot readers cover tables at $146A–$14EE, the packed initialization stream beginning $2309, $262C–$2643, $268C–$2716, $2720–$2778, $28DD–$29EB and $29F6–$2A2C. Retained B1.3 readers consume high P LUTs; their exact observed domains are in `evidence.json`. None reads $0282–$0386. Main mailbox table selectors in $1C53–$1DA9 and their generation helpers use X/Y data; the three executed jobs independently pass the guard. **UNKNOWN:** unexercised branches of the loader and integrated initialization; no universal data-ownership claim follows from these observations.

## Guard mechanism and before/after comparisons

**PROVEN:** `TARGET` is armed immediately after loading core0 and applying the identical P:$0281 RTS, before core1 initialization at $0100 and core0 initialization at $0107. Baseline observes target accesses; the candidate exits on the first target access. `targetAccess` checks actual instruction PCs via `Memory::getOpcode`/`replayFetch`, P-data reads via `Memory::get`/`replayAccess`, and writes via `Memory::dspWrite`/`replayAccess`. It is independent of post-boot audit enable. No poison overwrites the interval, so diagnostic prefetch of the unused second word after the one-word RTS is not mistaken for execution or data consumption. Cycle-profiler opcode inspection is excluded from execution counts.

The positive controls detect execution and DSP P-data reads at both $0282 and $0386, and host P writes through the same native write hook at both boundaries. A DSP write-intent instruction is detected on the interpreter's preceding old-value P read; its logged kind is **DATA_READ**, not a claimed observed WRITE. Adjacent $0281/$0387 accesses pass. `negative.py` and `guard-controls.json` preserve all nine cases.

`Pair.send` compares every batch from boot onward. `STATEWRITE/STATECHECK` compares both cores' complete modeled private X/Y backing arrays, shared SRAM, external words/validity bits/canaries, every architectural register supported by `readRegToInt` before `Reg_HIT`, and the ordered shared/external plus private-write transaction stream. This includes boot transactions, not merely terminal hashes. Program backing is intentionally not part of this state serialization; the access guard and identical programs address that separately. Larger emulator backing arrays do not establish hardware RAM ownership.

| Completed paired case | Numbered 32-sample blocks | Coupled audio calls, including ARM readback service | Exact checkpoints | Target hits |
|---|---:|---:|---:|---:|
| Initial smoke | 4 | 41 | 123 | 0 |
| Retained transitions | 256 | 545 | 1,851 | 0 |
| Stock patch reloads, both tracks | 8 | 17 | 58 | 0 |
| Project apply from captured record | 8 | 17 | 59 | 0 |
| Isolated original table helpers + subsequent audio | 8 | 17 | 63 | 0 |
| Total | 284 | 637 | 2,154 | 0 |

**PROVEN:** all 2,154 completed checkpoints have zero byte differences. Audio dump lines and complete stage files match. In the 256-block case each of 14 stages has 545 comparisons: both bank seams/EQ/stereo strips, mixer, mixer-plus-bus, send return, pre-master, before/after Master FX, output staging and output ring. Both X:$1000 output dumps and Y:$0800 mixer dumps are compared each numbered block. No first differing sample, state word, supported register or shared/external transaction exists in these completed cases. High-tail P:$3BBA–$3FFF canaries and the existing vpre/core1 register contracts pass. `retained-result.json`, `retained-{baseline,guarded}/output.txt`, `stages.txt`, `costs.csv` and `evidence.json` support these counts.

## Transition coverage and remaining failures

**PROVEN:** the completed retained case executes DSP initialization ($0107→$25F3→$0113), actual B1.3 first-use `c_vtick`, stock Synth1/Synth2 note-on **$080219E8** and note-off **$08021C48**, and both MIDI tracks through line/granular/FX-sequencer/off restore flags 1/11/5/0. It invokes the real `c_mpload` patch-restore code 64 times using the existing modeled CTM1 record source, stock parameter flush $080213B0 32 times, actual mixer/send controls $08034D92 and flush $08028EF2, and Master FX controls via the existing global state. The full note path $08051720→$08034460/$080344AA→$0803222C reaches the stock note handlers. Original sound generation remains disabled in both variants; deterministic equal bank stems exercise downstream processing and are explicitly modeled audio inputs, not stock-generated sound.

**PROVEN, bounded:** `patch-reload` executes original **$0802FC82** for Synth1 and Synth2 from the existing session record and emits 196 DSP writes per call. `project-restore` executes original **$0802EEFE** on manager `$2003D71C` and the captured record, emitting 489 DSP writes. Both then run eight matched blocks. These are available reload/apply cases, not proof of every library patch, alternate bank, filesystem load, or full power-on ARM reset. Source corroboration: reference emu_sc19_4.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/emu_sc19_4.py`; not distributed) `scenario`/`main`, and app.asm (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/re/app.asm`; not distributed) at those ARM addresses. Full project/media restoration remains **UNKNOWN**.

**PROVEN, bounded:** `table-helpers` replays the preserved actual ARM posts from ARM-generator-posts.json (local-only reference: `builds/phase20k-stock-wavetable/ARM-generator-posts.json`; not distributed): `$080002`, `$094403`, `$0A8804` to Y:$2C. Original DSP P:$1C53 completes them in **1 /327 /327 calls**, with **393,259 /985,706 /1,509,226 interpreter steps**, mailbox `$800000`, exact paired state, and no target access. The $173000/$174000 table previews match the previously recovered values. `table-helpers-baseline/output.txt` records completion. These are isolated helper replays, not successful integrated boot scheduling; selectors0/1/5/6/7 and the remainder of the full ARM initializer have not been admitted by this test.

**UNKNOWN — program-change completion:** bank CC0=1 and CC32=1 return, but the following channel1 program1 message enters original `$08022A9C` and waits at `$08022AB6…$08022AC8`. At `$0801BE6C`, LR=`$08022ABB`, SP=`$2006EED8`, R1=`$20006A47`, the original code requests scheduler activity; the completion byte at task object+`$10` has not reached 2. The original 20-million-ARM-instruction run stops there without returning. A separate watchdog probe reproduces the wait after 64 visits. It does not acknowledge the task or fake a successful patch load. No target access is observed before either stop. See `transitions-result.json`, `program-change-result.json`, their partial jobs/readbacks, and reference `app.asm` `$08022A9C/$08022AE4`.

**UNKNOWN — integrated table initialization:** the first attempt advanced only the old bridge's audio entry P:$01ED. It omitted the actual DSP main-loop call at **$0121→$1C53**; 7,001 audio service calls without table-job progress are preserved in `table-init-interrupted.json` and the interrupted directories, and are **excluded** from successful coverage. The corrected fixture schedules the actual **$0113–$0129** prefix before readback audio. In **two baseline attempts** this reaches the **2,000,000 scheduler-step limit at P:$1B44**, before the requested stop at $012A. $1B44 is a `do n0` body whose listing has a direct caller at $1B16; its actual incoming path in this failure, a completed integrated run, and the root cause of its nontermination have not been established. This is a baseline limitation, not a baseline-versus-guarded divergence and not evidence that $0282 is required. The guarded peer has not replayed that failing batch because the baseline stopped first. See `table-init-serviced-recorded-result.json`, its `partial-job.txt`, and baseline `error.txt`.

**UNKNOWN:** full cold ARM boot ordering (the ARM starts from the pinned running-RAM snapshot), asynchronous preset/bank changes through program-change, all table jobs in the complete main loop, active valid granular grains, active sample-drum PCM, capture, and all possible Master FX settings. No hardware timing or bus behavior is inferred. Existing peripheral/ICC and equal-stem models remain explicit. These gaps must not be turned into a claim that all retained features were exercised.

## Allocation decision

**STRONG INFERENCE:** the local control/data evidence favors removal of this routine body once stock Synth1/Synth2 generation is replaced. **UNKNOWN:** the requested complete transition qualification. Consequently:

- Safe words reclaimed by this experiment: **0**, not 261.
- First required address inside the interval: **none observed; UNKNOWN on uncovered paths**. P:$2706→$0316 is table data, not the missing retained reference.
- A smaller sub-range is not qualified: the coverage gap applies to the entire proposed interval. No second range was tested or admitted.
- The 261-word interval is numerically contiguous but **cannot yet be allocated to Plaits code**. It is separated from the existing high tail by retained/unqualified program; $0281 remains the RTS and $0387 is outside this experiment. No adjacent newly safe interval was established.
- The four-track architecture and final P/data budgets remain **UNQUALIFIED**. Historical Layout A's 1,075-word deletion is unchanged; this experiment adds zero words.

**Smallest next experiment:** make the **unguarded, generation-disabled baseline** complete the original P:$0113→$0121→$1C53 table-initialization transition with authentic ARM initialization ordering, isolating why the attempted prefix reaches the $1B44 loop limit. Then mirror that same transition through the existing target guard. Stay on P:$0282–$0386; do not begin another range or Plaits port. The already reproduced asynchronous program-change gap remains a separate required transition after that prerequisite succeeds.

P0282-0386 RECLAIM = UNQUALIFIED

## Continuous initialization follow-up

**UNKNOWN — the whole 261-word interval remains UNQUALIFIED.** This follow-up resolves the former dispatcher/P:$1B44 failure for the available procedural initialization prefix. It does **not** claim that the whole ARM initializer returned. The procedural prefix completes four real jobs with zero target accesses and 999 exact guarded-versus-baseline checkpoints; the next coefficient-resource read enters a separate unserviced storage-worker wait. Program Change was not investigated or repaired.

All new evidence is under phase24-init-transition (local-only reference: `builds/phase24-init-transition`; not distributed). evidence.json (local-only reference: `builds/phase24-init-transition/evidence.json`; not distributed) records the precise scope, executed PCs, mailbox completions, retained-state comparisons and remaining dependency. continuous.py (local-only reference: `builds/phase24-init-transition/continuous.py`; not distributed) `Native`/`run` executes the actual ARM initializer; paired.py (local-only reference: `builds/phase24-init-transition/paired.py`; not distributed) replays its captured DSP-visible command sequence only after that baseline prefix succeeds. No new reclaim interval or Plaits implementation is involved.

### Exact cause of the previous stop

**PROVEN:** P:$1B44 was not a demonstrated wait for an interrupt, missing table value, or retained use of P:$0282. It was the PC observed when the old scheduler exhausted its step allowance. A shorter trace exhausts its allowance at $011D, and shows $1B44 returning normally. Two independent fixture defects explain that failed experiment:

1. **An unreachable stop condition.** The previous fixture requested STOP $012A while X:$13 was zero. The stock prefix executes $0113→$0121→$1C53, returns through $0123/$0125, and `$0127 jeq $0113` correctly repeats initialization service. It cannot reach $012A until the ARM enables audio. In original ARM `$0802108C`, `$080210BE` calls the table initializer `$08035E28`; only **after that returns** do `$080210C2–$080210CA` publish X:$13=`$00000C`. Setting X:$13 to bypass this ordering would be incorrect. No such write was injected.
2. **A suspended-fetch decoder-cache mismatch.** The old bridge first redirected a fiber paused at DSP $0113 to the artificial $7000 call stub. `DSP::execInterpreter` had already assigned `pcCurrentInstruction=$0113`; the old `replayFetch` changed the physical fetch offset to $7000 without updating that instruction identity. `DSP::op_ResolveCache` consequently cached the $7000 JSR decoder under **$0113**. On later genuine re-entry to $0113, its unchanged BCLR word `$0A1215` was interpreted using that JSR decoder. The trace shows `$0113→$1B16→$1B44`, with R2=`$1B16` and SSH=`$0114`, rather than the expected $0114 continuation. This is harness-induced control flow, not stock initialization behavior.

The minimal cache witness (local-only reference: `builds/phase24-init-transition/cache-witness/result.json`; not distributed) captures `PC=$7000, current-instruction-PC=$0113` on the old transfer and rejects it with `FETCH_ADDRESS_MISMATCH`. The original failed-transfer trace (local-only reference: `builds/phase24-init-transition/old-transfer-trace/init-trace.txt`; not distributed) records the spurious JSR and the normal return from its $1B44 body. Those diagnostic fixtures reproduce the **old** redirect; they are not the successful initialization sequence.

Source mechanism: reference dsp.h (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/ext/dsp56300/source/dsp56kEmu/dsp.h`; not distributed) `DSP::execInterpreter` assigns instruction identity before `fetchPC`; dsp_ops.inl (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/ext/dsp56300/source/dsp56kEmu/dsp_ops.inl`; not distributed) `DSP::op_ResolveCache` indexes by `pcCurrentInstruction`; previous coupled.cpp (local-only reference: `builds/phase23-p0282-0386/coupled.cpp`; not distributed) `replayFetch` rewrites the suspended fetch offset. These pinned/reference sources were read, not changed.

**PROVEN implication for earlier evidence:** the 2,154 earlier equality checks remain preserved observations of two matching fixtures. They are not promoted to authentic continuous-control-flow coverage: equal opcode-cache corruption on both sides can preserve equality. This follow-up does not add those old checks to the new continuous-init qualification count, and does not rerun their unrelated audio workload.

### Authentic service and state restored

**PROVEN:** the new runner executes existing core1 initialization at $0100 and core0 initialization at $0107, pauses at the authentic post-upload wait $25F3, delivers the actual `$08029492` coefficient writes, and resumes naturally to $0113. It applies the common, existing P:$0281 RTS before boot. Those two bootstrap entry selections are the **only** `PC` commands in the successful job files. There is no $7000 stub, direct SERVICE helper call, redirect back to $0113, cache-clearing workaround, or removed stock wait.

`TURN 113` resumes execution for at least one instruction, then observes the next natural return to $0113. It does not assign PC. A fetch-coherence assertion requires physical fetch, architectural PC and interpreter instruction identity to agree throughout both DSPs. This changes scheduling/observation, not firmware instructions. See prepare.py (local-only reference: `builds/phase24-init-transition/prepare.py`; not distributed) and coupled.cpp (local-only reference: `builds/phase24-init-transition/coupled.cpp`; not distributed) `FLOW`, `TURN`, `replayFetch`.

The ARM executes real **$0802108C**, including controller setup `$0802112E`, metadata setup `$08035DF0`, `$08021196`, and table initializer **$08035E28**. The relevant initializer bodies are byte-identical in pinned B1.3 and the official stock application. Pending SHI-decoded X/Y writes are delivered before the corresponding ARM DSP read. `$08029344` is the existing hardware-read adapter: it returns the actual coupled DSP word left-aligned by eight, and returns to its caller; it does not supply a synthetic ready value or jump past a wait. Instruction-level SPI/SHI peripheral fidelity beyond that modeled interface is **UNKNOWN**.

| Required state/effect | Evidence and conclusion |
|---|---|
| Initial ready state | **PROVEN:** stock DSP $2874/$2875 writes Y:$2C=`$800000`; host does not inject it. |
| Coefficient seed/backup | **PROVEN:** real ARM post-upload coefficients populate X:$C00 onward; stock $25F8–$25FF copies 1,024 words to X:$2800. New job files preserve the original write order. |
| Persistent job continuation | **PROVEN:** P:$1C53 and $1D41 use X:$1B15–$1B21; the DSP itself advances and clears its active continuation. These fields are not replaced with expected final values. |
| Command encoding | **PROVEN:** ARM $08035E66 emits the original word through $080292F8; DSP $1C53 decodes selector and destination. Completion is read back from the DSP, not inferred from a host loop count. |
| Audio gating | **PROVEN:** X:$13 remains zero throughout the successful prefix. ARM audio-enable writes belong after the still-incomplete full initializer. |
| Interrupt/service event | **PROVEN for this prefix:** natural main-loop service advances all four jobs without injected DSP interrupts. Post-enable serial-audio interrupts and real storage-worker service remain outside the completed prefix. |

The intentionally broad **emulator backing** for original generated-table destinations is not a new memory-ownership allocation. No X/Y/P/shared/external words are granted to Plaits by this test.

### Baseline first, then the target guard

**PROVEN:** four-job-baseline-result.json (local-only reference: `builds/phase24-init-transition/four-job-baseline-result.json`; not distributed) was completed before launching the guarded replay. It performs 995 natural main-loop turns, reaches $0113, $0121 and $1C53 **995 times each**, and never executes the old spurious $1B44 path. Original jobs finish as follows:

| Actual Y:$2C post | Destination / selector | DSP-driven reads until ready | Final reply |
|---|---|---:|---|
| `$080002` | Y:$100000 /2 | 1 | `$800000` |
| `$094403` | Y:$128800 /3 | 327 | `$800000` |
| `$0A8804` | Y:$151000 /4 | 327 | `$800000` |
| `$0BCC05` | Y:$179800 /5 | 327 | `$800000` |

The extra reads in the 995-turn total include the stock initial handshake and repeated ready checks while ARM aliases metadata entries. No job is skipped to obtain those completions. The successful prefix pauses observation at **ARM $08035EC0, ordinal14**, immediately before the first coefficient-resource phase. The live ARM frame is not made to return, and its PC is not advanced past that boundary. It is expressly **not a complete `$0802108C` return**.

**PROVEN:** paired-result.json (local-only reference: `builds/phase24-init-transition/paired-result.json`; not distributed) reports **999 exact checkpoints, zero differences, zero target accesses**. The candidate uses the existing $0282–$0386 execution/P-data read/write guard from boot. The comparison includes initialization, each resumed turn and the final boundary: both cores' supported registers, modeled private X/Y state, shared SRAM, external words/validity/canaries, and ordered shared/external/private-write transactions. Indirect entry and P table lookup into the target would trigger the same fetch/data guard. Core0/core1 program hashes remain identical between variants.

Final relevant state is identical: DSP PC/current-instruction-PC=$0113, SP=SC=0, X:$13=0, Y:$2C=$800000, X:$1B15=0, X:$1B16=$000E00, X:$1B21=$002000, Y:$FFD=Y:$FFE=$001000. P:$3BBA–$3FFF canaries pass. The event journals, complete commands, PC/data census and outputs are preserved in `four-job-baseline`, `paired-baseline` and `paired-guarded` under the phase24 directory.

**UNKNOWN — post-full-init retained observables:** audio entry $01ED, bank seam $020C and vpre $336E have **zero executions** in this prefix because audio is correctly disabled. Initialized sample buffers, mixer/send/Master FX/routing storage compare exactly as state, but this is not a rendered-audio test. An empty stage file matching another empty file is not active audio/FX coverage. No full-initializer completion or subsequent sample/mixer/send/Master FX equality is claimed.

### Remaining initializer dependency, separate from Program Change

**PROVEN:** continuing real ARM execution reaches original resource reader **$08047C6C** with source offset **$82000**, destination **$20005148**, length **$200 =512 bytes**. Global `$20006968` selects object `$2000AC94`, vtable `$0805B1D8`; read slot+`$C` is **$08024130**, synchronization slot+`$1C` is **$08023FD6**. The original read routine queues work via `$08023F68`, then waits in `$08023FFC–$0802400E` for its worker to clear bit0 of object+`$10`.

The real resource attempt (local-only reference: `builds/phase24-init-transition/real-resource-attempt-result.json`; not distributed) actually executes that reader. After 64 unchanged scheduler-yield visits, a diagnostic watchdog stops observation at **$0801BE6C, LR=$08024001, R4=$2000AC94**. It supplies neither an acknowledgement nor data. Original worker **$08024014** consumes that queue; its read branch `$0802408A–$08024096` calls the backend's vtable+`$C`. Full completion and the backing coefficient payload are **UNKNOWN**. This is the already documented later resource branch, not a newly investigated reclaim range: [stock-wavetable-provenance-173000.md](<stock-wavetable-provenance-173000.md>) identifies the same ordinal14–29/source-$82000 dependency.

The ARM has entered `$080295E4`'s 16-bit SHI setup in that exploratory continuation, but no resource payload is admitted or uploaded. A complete native acknowledgement/upload model for that subsequent phase remains **UNKNOWN**. The successful **paired** prefix ends before this setup, avoiding any claim about unqualified width-control effects. Source/control evidence is the reference app.asm (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/re/app.asm`; not distributed) at $08035EC0–$08035F04, $08047C6C, $08024130, $08023FD6 and $08024014.

**PROVEN:** this required initialization storage wait differs from the prior Program Change wait at LR=$08022ABB. No Program Change task was executed, bypassed or declared repaired. Its qualification gap remains separate.

### Decision and one current next experiment

**PROVEN:** the old P:$1B44/dispatcher failure is resolved for four genuine procedural jobs; the guarded prefix has zero target fetches, P-data reads or writes and zero divergence across 999 checkpoints. **UNKNOWN:** the complete resource-backed initializer, subsequent continuous retained audio processing, and the separate Program Change path. The interval therefore remains unavailable for Plaits: **safe reclaimed words =0**. No first retained use inside it is established. No smaller or adjacent range is qualified. The architecture budget is unchanged, so the architecture report was not modified in this follow-up. All 451 recorded reference inputs and 183 pinned source files still match their hashes.

**Exactly one smallest next experiment:** qualify **one original `$08024014` storage-worker read for offset `$82000`, length512**, using authenticated **existing offline** backing bytes, then carry that single result through the actual 16-bit SHI upload and its first selector0 job. Establish payload provenance and completion from code/execution; do not fabricate data or clear the wait flag. This is the first unfinished dependency in the live initializer, and remains confined to completing the $0282–$0386 qualification fixture.

P0282-0386 RECLAIM = UNQUALIFIED

## First coefficient-storage provenance gate — 2026-10-15

**UNKNOWN:** this exact storage-backed sequence remains unqualified. The request's address space is now identified from the stock code and authenticated RAM object chain, but no existing payload has PROVEN provenance for that location. The user requires PROVEN byte provenance before executing the worker/upload/selector0 qualification. This follow-up therefore stops at that gate. It does not substitute RAM contents, synthesized coefficients, zeroes, completion flags, or a directly loaded DSP table. It does not repeat the already completed four-job/999-checkpoint experiment.

Evidence: study.py (local-only reference: `builds/phase25-first-coefficient/study.py`; not distributed), result.json (local-only reference: `builds/phase25-first-coefficient/result.json`; not distributed), storage-chain.json (local-only reference: `builds/phase25-first-coefficient/storage-chain.json`; not distributed), and the focused ARM-request-path.asm (local-only reference: `builds/phase25-first-coefficient/ARM-request-path.asm`; not distributed). These are local analysis artifacts, not a firmware image. The script verifies each examined instruction span against both official 4486 and pinned B1.3 bytes, inspects the existing `authentic_session()` object graph, and inventories existing source assets. It does not invoke `$0802108C` again, complete a storage request, or start a DSP job.

### Request identity and address semantics

**PROVEN:** requesting stock ARM routine `$08035E28`, called by `$0802108C`, reaches the ordinal14 branch at `$08035E94`. The first 12-byte descriptor at **`$080567EC`** is `00 20 08 00 00 01 00 00 00 00 DE 03`. Its source field is `$00082000`; its halfword count at +4 is `$0100`. The ordinal-derived additional offset at `$08035EAE` is zero for this first request. `$08035ED4` doubles the count to **512 bytes**, `$08035ED6` obtains buffer **`$20005148`**, and `$08035EE2` calls **`$08047C6C`** with those arguments. The prior live-frame trace observed exactly those values; this study decodes their original descriptor rather than rerunning that prefix.

**PROVEN:** the selected source is an asynchronous wrapper over the external QSPI backend, not an SD filename or an offset in the official BIN. The authenticated running-RAM object chain is:

| Link | Address / value |
|---|---|
| Global storage pointer | `$20006968` → `$2000AC94` |
| Wrapper vtable | `$0805B1D8`; read +`$C` → `$08024130` |
| Wrapper backend +4 | `$20000378`; vtable `$0805B1AC` |
| Backend read +`$C` | `$08022F94` |
| Backend context +4 / capacity +`$C` | `$20000000` / `$02000000` bytes |
| Context → controller → device | `$20005550` → `$200033EC` |
| Device register base | **`$A0001000`**, QSPI controller |

**PROVEN:** `$08022F94` checks the offset against capacity, takes its semaphore, and calls `$08037430` with the same offset. `$0803744A` stores that offset in command+8. `$0803769C` adjusts command flags/lanes but does not rebase its address. Finally **`$0802281C–$08022820` copies command+8 unchanged to controller register base+`$18`**, the address register. Thus **`$82000–$821FF` is the absolute byte-addressed external-QSPI interval selected by this backend**; there is no file/partition offset addition on this path. The command template at `$080376F4` is `EB EC 0F 00 00 00 00 00 00 00 00 00 06 00 00 00`; the hardware-read command and length are configured by `$08037430/$08022746`. Physical contents and actual hardware execution are **UNKNOWN**. This read-only experiment makes no physical access.

### Actual worker/completion contract

**PROVEN by code:** `$08047C6C` calls wrapper read `$08024130`. Its template at `$0802422C` starts with operation 1 and otherwise zeroes; it sets request+4=source, +8=destination, +`$C`=length, and explicitly zeroes callback +`$10` and userdata +`$14`. `$08023F68` enqueues the 24-byte request through `$08036708`, updates pending state and signals the service event. `$0802415E` calls synchronization slot +`$1C`, **`$08023FD6`**, which waits for wrapper+`$10` bit0 to clear. These routines and request-field order are preserved in the focused listing.

**PROVEN by code:** worker **`$08024014`** consumes pending queue entries using `$0803675C/$08036732`. Its read branch **`$0802408A–$08024096`** calls backend `$08022F94` with the original offset/buffer/length. The backend calls `$08037430`, which prepares the destination transfer through `$0801C4D4/$0801C072`, issues the QSPI command through `$0803769C→$08022746`, and waits through `$08037596`. After return it releases the backend semaphore via `$0801BA12`. The worker then stores the return status byte at wrapper+`$18` (`$080240C4`), conditionally calls request+`$10` (`$080240D0–$080240D8`; **null for this request**), drains work, and atomically clears wrapper+`$10` bit0 at `$080240DE–$080240F6`. The waiting read returns the status byte at `$08024160`.

**UNKNOWN:** completed transfer bytes, interrupt/cache/DMA effects and completion ordering under an executed request. The earlier real-reader attempt remains preserved at real-resource-attempt-result.json (local-only reference: `builds/phase24-init-transition/real-resource-attempt-result.json`; not distributed): it stopped after 64 unchanged yields at PC=`$0801BE6C`, LR=`$08024001`, R4=`$2000AC94`. This study supplies neither backing bytes nor a successful status. Static worker analysis is not reported as a completed worker test.

### Existing offline payload search

**PROVEN, bounded search:** corpus-census.json (local-only reference: `builds/phase25-first-coefficient/corpus-census.json`; not distributed) records **11,302 existing files** in the reference/dependency, original backup-SD, project firmware and prior documentation roots; **46 BIN/SYX/DAT/raw-image/dump-name candidates**. All 46 have freshly recorded hashes; 43 had prior inventory hashes and all 43 matched (the other three had no earlier hash to compare). The installed reference archive is separately enumerated in archive-census.json (local-only reference: `builds/phase25-first-coefficient/archive-census.json`; not distributed). address-provenance-search.json (local-only reference: `builds/phase25-first-coefficient/address-provenance-search.json`; not distributed) records explicit address references in the bounded source/document corpus: its six matches are unrelated DSP bitfield unit-test operands, not storage mappings. This is a corpus-scoped search, not a claim that no other file exists anywhere on this machine.

| Existing source | Evidence / admission |
|---|---|
| Official 4486 application | **PROVEN:** 314,844 bytes; authenticated source of the request code/descriptors. Its internal-flash file offset is not the external-QSPI address. It does not furnish an authenticated mapping of these 512 storage bytes. |
| Pinned full internal-flash dumps | **PROVEN:** 524,288 bytes, representing ARM `$08000000` space. They are not a QSPI image; treating their file position `$82000` as this request would also exceed their length. |
| Existing RAM dumps | **PROVEN:** buffer-position slices and source-file SHA-256 values are recorded in `RAM_buffer_candidates`. **UNKNOWN:** which storage transaction, if any, produced those slices. The captured staging buffer is reusable; its address alone cannot identify the first read's contents. |
| Authenticated running-RAM slice | **PROVEN:** `ram_dump_firmware_0x08037988.bin` source SHA-256 `26a29670c0c1918217b7eadf8f89fe6df97994d3cc6e1c0ed65ac522e161094c`; file offset `$5148`, length512 has SHA-256 `47d976b3c828a2f607465aa88321010f4c6366aa2932c2e8dee9a6bc72f67c90`. **UNKNOWN:** association with QSPI `$82000`. The filename's saved PC is not proof of this read's source or completion. This slice was not admitted. |
| Previously recovered stock tables/coefficients | **PROVEN:** the earlier reciprocal constructor and selectors2–5 are distinct from this storage-backed branch. `existing-constructor-assets.json` rechecks original artifact hashes. Generated `$173000` waveform output or the 1,024-word reciprocal seed cannot substitute for this 256-value storage payload. |
| Reference fixtures, backup packs/PCM, source archive | **UNKNOWN:** no authenticated file-to-QSPI-`$82000` correspondence was established. A patch or WAV containing plausible numbers is not byte provenance. No candidate was promoted by filename, similarity, or later DSP behavior. |

**UNKNOWN — selected payload provenance:** source file **none admitted**; source hash/offset **not established**; required length **512 bytes**. No existing QSPI dump or request-associated capture in this scoped corpus establishes the requested physical interval. Authentication of a RAM dump's file identity is distinct from authentication of the staging buffer's transaction history.

### Upload and selector0 contract, not executed coverage

**PROVEN by code:** before the read, `$08035EC8→$080292DC` selects DSP core0 **X:`$C00`**, then `$08035ECE→$080295E4` requests 16-bit SHI words. After a successful read, `$08035EEE→$0802968E→$0803BA78` would send **512 bytes from ARM `$20005148`**, i.e. **256 two-byte DSP values to X:`$C00–$CFF`**. `$08035EF4→$08029626` restores 24-bit SHI transport. Existing [dsp-command-map.md](<dsp-command-map.md>) documents the two-byte, MSB-first SHI word in bits23:8 and the DSP P:$0198 data writer. No byte swapping or coefficient reconstruction occurs in this ARM read/upload branch.

**STRONG INFERENCE:** these 512 bytes are a stored, signed 16-bit harmonic-amplitude coefficient record for the first storage-backed waveform family's first level, rather than 512 time-domain audio samples. The stock descriptor counts 256 values; selector0 sets N0=16, and the existing coefficient-stage analysis consumes 256 X coefficients through P:$1DF2's harmonic MAC path. The signed fractional DSP interpretation follows the SHI left alignment and MAC operation. Exact coefficient values, waveform identity/name, and authoring format remain **UNKNOWN** without the payload. See core0.asm (local-only reference: `builds/phase20k-stock-wavetable/core0.asm`; not distributed) P:$1C53/$1C64/$1CFE/$1DF2 and [dsp-high-x-audit.md](<dsp-high-x-audit.md>) coefficient-stage bounds.

**PROVEN by code:** `$08035F04→$080292F8` would post the first **selector0** command to **Y:`$2C`** after the upload. The prior four jobs leave the next output base at **Y:`$1A2000`**, encoded mailbox word **`$0D1000`**. ARM advances its next-slot base by `$4800`. DSP main-loop **P:$0121→$1C53** decodes selector0, selects N0=`$10`, X0=`$400`, Y1=`$733333`, Y0=0, and calls `$1CFE`; it prepares X:`$2400` workspace, Y:`$1400` basis, X:`$42/$43`, and X:`$1B15–$1B21` continuation. Its first computed export start is base+17×`$400` = **Y:`$1A6400`**, inside the ARM-assigned `$4800`-word slot. `$1D26–$1D32` publishes pending state and saves continuation; later calls enter `$1CCD/$1D41`. `$1DA2–$1DA9` clears continuation, restores modifiers and publishes Y:`$2C=$800000`; the main-loop call returns through P:$0123. These are decoded expected paths, not observations that this job completed. Actual output words, touched-address census and first-job completion remain **UNKNOWN**.

### Qualification observables and decision

| Requested observable | Result for this exact new sequence |
|---|---|
| Authentic storage read / upload / selector0 completion | **UNKNOWN:** not executed after provenance gate. |
| Target instruction/branch/P-data/table accesses | **UNKNOWN:** not measured for this sequence; not reported as zero. |
| Guarded-versus-baseline divergence count | **UNKNOWN / not applicable:** no admitted baseline, so no paired replay or comparison count. |
| DSP state, supported registers, ARM completion, ordered shared/external traffic | **UNKNOWN:** no new executed completion checkpoints. Static contracts above do not establish equality. |
| Uploaded coefficients and resulting selector0 tables | **UNKNOWN:** no admitted bytes or output. |
| Active samples, mixer/send/Master FX | **UNKNOWN:** still not reached beyond this initializer dependency. |
| Complete initializer proceeds further | **UNKNOWN:** no new advancement; `$0802108C` has not returned. |
| Earlier four-job prefix | **PROVEN, unchanged:** 999 exact checkpoints, zero target accesses/divergences, only within that earlier scope. |
| Safe reclaimed words | **PROVEN:** **0** added; P:$0282–$0386 remains unavailable for Plaits. |

**PROVEN:** 451 recorded reference inputs and 183 pinned Plaits source files still match their existing hashes. No reference/pinned source, hardware, firmware image, architecture budget or other reclaim interval was changed. Program Change remains separate and was not investigated.

**Exactly one smallest next experiment:** a bounded **offline provenance test of one existing storage-associated capture**, requiring an explicit mapping of its 512 bytes to QSPI **`$82000–$821FF`** (or a request-associated `$20005148` capture immediately after this exact read). Verify source identity/hash and address mapping before admitting that slice to the existing actual-worker/upload/selector0 runner. No such mapped capture has been identified in the searched corpus; with the present inputs this experiment cannot yet execute. This calls for an existing offline artifact, not hardware access or another reclaim-range investigation.

P0282-0386 RECLAIM = UNQUALIFIED

## Expanded offline-capture inventory — phase26

**UNKNOWN:** no existing capture was admitted for physical external QSPI `$82000–$821FF`. The broader, capture-focused search and source-backed mapping checks still do not establish the required 512 original bytes. No storage response, upload, selector0 completion or new guarded comparison was executed. **PROVEN:** safe reclaimed words remain **0**; the existing 999-checkpoint result remains confined to its original four-job prefix.

The full phase26 report (local-only reference: `builds/phase26-qspi82000/report.md`; not distributed) and result.json (local-only reference: `builds/phase26-qspi82000/result.json`; not distributed) provide the requested decision fields. capture-inventory.json (local-only reference: `builds/phase26-qspi82000/capture-inventory.json`; not distributed) and its readable table (local-only reference: `builds/phase26-qspi82000/capture-inventory.md`; not distributed) report every candidate's full path, size, SHA-256, provenance, capture type, documented base/address space and target-inclusion status. **PROVEN:** 85,521 files visited; 1,858 candidate paths recorded across the entire existing project/build tree, reference/dependencies, explicitly followed `ctre` alias, original backup SD and distribution archive. Paths/copies are not counted as independent acquisitions.

**PROVEN:** reference `tools/emu_sc05.py:E.__init__` and `tools/emu_shared_channels.py:Emu.__init__` explicitly map the recognized full-flash and SRAM snapshots to ARM `$08000000` / `$20000000`. Exact excerpts and hashes are in mapping-evidence.json (local-only reference: `builds/phase26-qspi82000/mapping-evidence.json`; not distributed). These address assignments are established from code, not filenames. None maps to external QSPI. Other RAM-named files retain **UNKNOWN** bases where no explicit mapping source was established.

**PROVEN:** large saved `state.bin`, `trace.bin` and `iterations.bin` files have identified producers, preserved in fixture-producer-evidence.json (local-only reference: `builds/phase26-qspi82000/fixture-producer-evidence.json`; not distributed). They contain generated DSP checkpoint records, X/Y access flags, or DIV accumulator/status records respectively. A numerical file position `$82000` inside one of those files cannot be treated as physical QSPI `$82000`. No coefficient reconstruction from later state was attempted. Archive enumeration and duplicate grouping are preserved separately; duplicated files and the `ctre` alias do not establish independent capture provenance.

**UNKNOWN:** accepted capture path/hash, physical-QSPI base mapping, target file offset, 512-byte hash, first/last32 bytes and signed16 statistics. No slice was selected or extracted. **UNKNOWN:** QSPI→ARM→DSP equality, selector0 completion, all target access categories including address calculations, and guarded divergence count. These unexecuted observables are null in `result.json`, not zero-access/zero-divergence successes. The exact missing evidence remains **file offset N ↔ physical external QSPI `$82000`**, plus the 512 original bytes. Worker/upload code expectations from phase25 remain unchanged. Complete initialization, active subsequent audio and Program Change remain uncovered.

**Exactly one smallest next experiment:** authenticate **one existing offline capture/metadata pair** explicitly mapping its 512 original bytes to physical QSPI `$82000–$821FF`, as a single admission test. No such pair is identified in the available corpus; the dependent execution cannot proceed with the present inputs. No hardware step, synthetic bytes, new reclaim range or Plaits port is proposed.

P0282-0386 RECLAIM = UNQUALIFIED
