> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Four-track Plaits resource architecture

2026-10-15. **UNKNOWN: final safe program/data budgets and complete four-track deadline.** This audit establishes a measured, conservative generation-disabled baseline and identifies exact candidate ranges, but does not qualify their complete deletion closure. It must not be read as a completed stock-synth removal proof or a full-engine admission.

**PROVEN:** the final requested rules are `MAX_TRACKS_PER_MODEL=2`, `MAX_POLY_TRACKS=2`, four tracks with mono default and conceptual per-track requests 1/2/3/4 voices. Four mono Modal tracks are not a required configuration. Two mono Modal filter banks cost **155,394 modeled cycles/block** before the rest of either engine. Two selected Modal tracks may still request more than two Modal voices; model assignment count and voice count are separate limits.

No full ModalEngine, UI, new application/DSP firmware image or bootloader modification was implemented. All program changes in this phase are emulator-memory experiments. The reference repository remains read-only. The previously qualified 1,075-word MIDI-code deletion remains evidence, not the final architecture's capacity limit.

## 1. What executed and what remains unqualified

replay.py (local-only reference: `builds/phase22-four-track-resource/replay.py`; not distributed) runs actual pinned B1.3 ARM code with the authentic RAM/flash artifacts, the existing Layout A core-0 analysis stream, and both native DSP interpreters. Its only synthesis-disable program edit is **P:$0281 = RTS**, applied after boot in emulator memory. The twelve stock synth slot calls still execute that return, but their sound-generation bodies do not execute. The fourteen-slot dispatcher, both remaining slots, ARM note routing/old allocation, bank processing, drums, MIDI processing and effects remain present. No P-memory holes were deleted, relocated or exported as a new program image.

For retained-audio comparison, some cases supply the same explicitly **MODELED** 32-word mono stems into X:$2DF0 and X:$2E50 at P:$020C in both baseline and disabled runs. This is a downstream integration probe, not Plaits execution, stock oscillator equivalence, or proof of four real engine capacity. Idle and drum-only final cases use zero physical input and no stems.

**PROVEN:** nine corrected paired cases × 256 numbered blocks × baseline/disabled = **4,608 numbered block executions**, plus separate ARM-readback service blocks. Each pair has zero differences in the sampled retained stages and final 64-word output blocks. The selected stages span bank processing, stereo strips, mixer/bus, sends/intermediates, master processing and output ring. These are sample comparisons, not a claim that every remaining private word or register matches the original synth-enabled machine. The inherited vpre and core-1 caller checks remain enabled. corrected-replay-results.json (local-only reference: `builds/phase22-four-track-resource/corrected-replay-results.json`; not distributed), analysis.json (local-only reference: `builds/phase22-four-track-resource/analysis.json`; not distributed) and each case's `costs.csv`, `stages.txt`, `job.txt`, `output.txt`, `data0.tsv`, `data1.tsv`, `pc0.txt`, `pc1.txt` and result JSON retain the witnesses.

Three fixture limitations were investigated rather than hidden:

1. Initial exploratory runs restored a MIDI mode before its first-use ARM service initialization; the real initializer subsequently reset it. Those runs remain saved and are not evidence of active retained modes. The corrected runner initializes first, then restores the patch and sends notes. It observes line ACT=$0001, granular ACT=$1002, and FX-sequencer ACT=$0000.
2. Initial drum stimuli 36–39 were ignored by the documented stock route. A separate paired 256-block test uses **60/62/64/65**, reaches actual ARM `$08034460`, `$0801A99A`, `$0803222C`, and still produces **zero drum output**. PCM playback is not qualified. Notes alone do not prove sample audio.
3. Granular reaches source validation, but **core-1 `grain` at P:$04DE executes zero times**. `voice` runs, then `v_off` is taken with the available source state. Thus its control/dispatch overhead is measured, not its active-grain worst case. Conversely, Master FX cases publish GARM=$C0FFEE and execute the retained glitch sample path on the derived external ring; active glitch is exercised in that limited knob configuration. Capture recording/playback and maximum granular/glitch workloads remain UNKNOWN.

Sources: analysis.json (local-only reference: `builds/phase22-four-track-resource/analysis.json`; not distributed); reference granular_dsp.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/granular_dsp.py`; not distributed) `voice`, `v_src`, `v_off`, `grain`, `glitch`; reference NOTAS.md (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md`; not distributed) stock MIDI drum routing; the source/closure and address evidence below. A successful process exit is not used to promote these missing workloads into coverage.

## 2. Stock synthesis closure: callers and retained dependencies

**PROVEN source structure:** boot P:$2881 initializes twelve synth descriptors at X:$00EB–$014A with entry $0281 and record strides: X:$1960 + 12*v, Y:$011F + $60*v, Y:$0131 + $60*v, X:$057A + $4A*v, Y:$059F + $28*v. Init P:$28AC adds slot 12, routine $202B; P:$28C7 adds slot 13, routine $1A2B. These last two descriptors at X:$014B–$015A remain.

The audio call at P:$01FC enters `$198D`; P:$19AC performs **JSR (R1)** using that table. `$19BF` performs the second, flag-selected completion pass and calls `$077F` at `$19E6`. `$0281` normally performs per-voice context/control preparation and reaches `$037A→$04D5/$0657/$0387→$077F`. The wave worker uses the shared gather machinery, then `$09B9` / B1.3 `$2C54` source selection, the raw mono combiner, and `$09D9` onward per-voice processing before summing to the banks.

The disable experiment stops at entry $0281; it does not prove that deleting every reachable helper is safe. Source and observed evidence are in core0.asm (local-only reference: `builds/phase20k-stock-wavetable/core0.asm`; not distributed), dependency-inventory-observed.json (local-only reference: `builds/phase22-four-track-resource/dependency-inventory-observed.json`; not distributed), direct-edges.tsv (local-only reference: `builds/phase22-four-track-resource/direct-edges.tsv`; not distributed), reference NOTAS.md (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md`; not distributed) “Tabla de voces del DSP”.

| Candidate interval, inclusive | Words | Original role | Remaining-reference / reachability finding |
|---|---:|---|---|
| $0281–$0386 | 262 | stock per-slot synth entry/context and dispatch | 1 decoded external inbound references (may include data); entry RTS remains reachable; body ownership UNKNOWN |
| $0387–$0758 | 978 | stock voice coefficient/envelope/modulation helpers; shared status must be resolved per helper | 9 decoded external inbound references (may include data); 0 observed instructions after disable; full indirect/P-data/ARM closure UNKNOWN |
| $077F–$09B8 | 570 | stock request/completion waveform worker | 7 decoded external inbound references (may include data); 0 observed instructions after disable; full indirect/P-data/ARM closure UNKNOWN |
| $09B9–$09D8 | 32 | stock mono source combiner | 8 decoded external inbound references (may include data); 0 observed instructions after disable; full indirect/P-data/ARM closure UNKNOWN |
| $09D9–$0AA7 | 207 | stock per-voice normalization/filter/gain and completion bookkeeping | 4 decoded external inbound references (may include data); 0 observed instructions after disable; full indirect/P-data/ARM closure UNKNOWN |
| $2C54–$2D58 | 261 | B1.3 stock synth source-selection extension | 1 decoded external inbound references (may include data); 0 observed instructions after disable; full indirect/P-data/ARM closure UNKNOWN |

**UNKNOWN:** a complete caller/reader/writer closure for these intervals. `direct-edges.tsv` inventories decoded direct address references; the original disassembly also decodes embedded table words as instructions, so an apparent edge is not automatically a real caller. `dependency-inventory.json` preserves all such inbound references and numeric literals rather than declaring them removed. P-data reads, init copies and pointer tables must be distinguished from instruction fetches.

Seven stock indirect transfer sites require target-domain closure: **$0DB6, $0DBD, $0DC5, $0DCD, $0DEC, $0DF9, $19AC**. `$19AC` has the observed fourteen-slot table; the others include retained effect dispatch using X pointer tables. Generic SHI access and ARM-driven Y:$2C table jobs remain additional data-writer obligations. The graph is therefore an explicit unresolved dependency worklist, not a falsely complete semantic graph.

**PROVEN retained dependencies:** do not reclaim `$0759–$077E` wholesale: bank clearing and gather reset/progress contracts remain. Do not reclaim `$0AA8–$0BDC` merely because a synth voice calls it: `$0AAC` is also called from retained `$0F64`, `$0F71`, `$11FC`, `$2122`; entry `$0AA8` and interior `$0AAC` share the body. Keep bank EQ/filter/stereo processing `$11E9–$1276`, four-strip envelope/sidechain preparation `$1277–$12EC`, drum/control `$202B–$2089`, drum buses/rendering `$208A–$20B2`, the mailbox/SHI handlers, and the fourteen-slot dispatcher. `$19F3` control/modulation remains conservatively retained; not all of it is proved synth-only.

**ARM closure:** stock `$080219E8` and `$08021C48`, slot selection `$0802161A/$080216C6/$08021706/$080217B4`, and their synth-record writes are replacement candidates only after separating the generic event path. Keep upstream `$08051720` MIDI receive, `$08034460/$080344AA` note dispatch and `$0803222C` routing. Keep shared parameter flush `$080213B0/$0802148C`, global/settings restoration `$08028EF2/$08028FD6`, and SPI read/write/loader `$08029344/$08029492` until their consumers are individually retargeted. The observed original note allocator still runs in this experiment; it is not removed or proven unnecessary. ARM vtables, callbacks, synth-preset restore/table jobs and sequencer sources prevent a complete ARM deletion count today. **No ARM code is claimed reclaimed.** [dsp-command-map.md](<dsp-command-map.md>) and [stock-master-signal-path-qualification.md](<stock-master-signal-path-qualification.md>) provide instruction-backed destinations; reference app.asm (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/re/app.asm`; not distributed) contains the unchanged stock listing.

## 3. Exact P accounting

| Space | Existing occupied words | Unoccupied/candidate range | Qualification |
|---|---:|---|---|
| Original B1.3 core0 | 16,365, ending $3FEC | $3FED–$3FFF: 19 | Existing tail, not newly reclaimed |
| Layout A core0 | 15,290, ending $3BB9 | $3BBA–$3FFF: 1,094 | Prior 1,075-word oscillator deletion + original 19-word tail |
| Retained B1.3 core1 | 2,047, ending $07FE | $07FF–$3FFF: 14,337 arithmetic candidate | Full range ownership/placement not qualified by an oversized emulator allocation |

**PROVEN:** Layout A's prior deletion was 457 oscillator-control +489 waveform +129 TINC words, genuinely reassembled/relocated in the earlier study. It preserves VA-dependent shared control. The 102-word extra-control deletion and its failures are not silently counted. This phase reuses that reduced stream; it does not count stock-synth overlays or add the same holes twice. The long resource screens inherit the original final-19-word execution/data guard and the existing $3BBA–$3FFF P-write rejection. A separate post-run audit checks every recorded fetch and P-data address across the full 1,094-word interval: zero accesses. The final focused send probes also poison and runtime-guard the entire interval with `FREE 3bba`, with block-end canary checks. These scopes are not conflated. validation.json (local-only reference: `builds/phase22-four-track-resource/validation.json`; not distributed), allocation.json (local-only reference: `builds/phase20g-dual-allocation/allocation.json`; not distributed), [stock-master-signal-path-qualification.md](<stock-master-signal-path-qualification.md>).

**UNKNOWN:** additional safe stock-synth P reclamation: **zero newly admitted words**, rather than an assertion that hardware has no more capacity. All candidate intervals above remain present in the replay. No fragmented interval was filled with a renderer or qualified as a new executable allocation. Even the entry interval retains a live $0281 return; its remaining 261 words need a separate guarded closure before admission.

**TOTAL SAFE CORE0 P WORDS AVAILABLE FOR PLAITS = UNKNOWN for the final architecture.** Historical qualified reclaimed allowance: 1,075 words; Layout A's contiguous unoccupied tail is 1,094, including its original 19 words. The historical allowance is a lower-bound witness, not a new final limit or a full firmware capacity claim.

**TOTAL SAFE CORE1 P WORDS AVAILABLE FOR PLAITS = UNKNOWN.** Newly reclaimed stock-synth words: 0, because core1 has no demonstrated stock voice generator to delete; it provides general gather service plus retained granular/glitch. Its 14,337-word unloaded tail is a candidate, not an admitted allocation. Core1 P:$016C–$07FE remains retained B1.3 work; deleting it would violate the requested feature preservation.

**STRONG INFERENCE:** absolute long DSP jumps/calls can connect qualified fragments, with measured trampoline/relocation overhead. The old module already demonstrates actual relocation. Fragment capacity must be recomputed after link growth, branch range choices, data references and high-P guards. Immutable LUTs may occupy separately qualified P data holes; initialization copies and P-read references must be preserved. Mutable Plaits state belongs in qualified X/Y/data storage. No linker, all-24-model P fit or code-paging mechanism is established here.

## 4. X/Y/shared/external memory accounting

dependency-inventory-observed.json (local-only reference: `builds/phase22-four-track-resource/dependency-inventory-observed.json`; not distributed) records exact intervals and observed DSP readers/writers, plus host writes from saved jobs, including setup. Each replay's `data*.tsv` records per-address read/write counts and responsible PCs. Absence in these runs does not close future ARM/worker/interrupt aliases.

| Space and inclusive range | Words | Finding |
|---|---:|---|
| Core0 X:$00EB–$015A | 112 | Fourteen descriptors; retain dispatcher and non-synth slots |
| Core0 X:$057A–$08F1 | 888 | Twelve voice records; ARM note writes and an observed retained DSP reader remain |
| Core0 X:$1960–$19EF | 144 | Candidate generator records; no observed post-disable access; ownership UNKNOWN |
| Core0 Y:$011F–$059E | 1,152 | ARM note/parameter writes remain; cannot repurpose wholesale |
| Core0 Y:$059F–$077E | 480 | Candidate per-voice post histories; no observed post-disable access; ownership UNKNOWN |
| Core0 X:$1400–$15FF | 512 | Candidate intermediate workspace; table-job/init closure UNKNOWN |
| Core0 X:$1600–$193F | 832 | 208 words still observed read; 832 host-written including setup; KEEP pending per-table proof |
| Core0 X:$2C02–$2C45 | 68 | Still read/written by retained paths; not persistent-state space |
| Core0 X:$2C46–$2C65 | 32 | Raw seam scratch also used by retained processing; not private persistent state |
| Core0 X:$2DF0–$2E0F / $2E50–$2E6F | 32 each | Retained bank mono strips |
| Core0 X:$3900–$39BF | 192 | CPT_LIST copies all words to granular shadows; KEEP despite oscillator names |
| Core0 X:$3B80–$3BEF | 112 | Two 48-word mailbox/control records plus 16-word save area; KEEP |
| Core1 private X/Y | UNKNOWN | No stock voice-state reclaim proved; unused native backing is not ownership |
| Shared $30000–$37FFF | 32,768 address span | Gather and B1.3 allocations coexist; no newly qualified subrange |
| External $340000–$37FFFF | 262,144 | Retained stereo glitch ring |
| External $E80000–$EA87FF | 165,888 modeled aperture | Capture; not a newly free allocation or proof all words initialized |
| External $100000–$10FFFF | 65,536 | Stock wave family0 candidate; retained aliases/source table use not closed |
| External $128800–$14C7FF | 147,456 | Stock wave family1 candidate; same limitation |
| External $151000–$174FFF | 147,456 | Stock wave family2 candidate; same limitation |

**UNKNOWN:** newly certified reclaimed X/Y/shared/external words on either core; **0 newly allocated/admitted** in this phase. No contiguous stock record is declared free simply because its generator stopped. The 144-X /480-Y /512-X candidates are not summed into an available budget.

**PROVEN reference allocations:** granular/glitch GB=$37000; CNT=GB, task=GB+6; per-voice states GB+$20 with stride $30; grains GB+$240, 12 words ×16 grains ×2 tracks; MIN=GB+$100; ping-pong OUT=GB+$140, GOUT=GB+$1C0; SHA=GB+$400, SHB=SHA+$C0, SHT=SHA+$120, SHLEN=SHA+$220. CPT_LIST copies oscillator/voice records, capture length, master input and GARM; a quarter sample table is copied each block. These obligations survive stock-synth removal. reference granular_dsp.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/granular_dsp.py`; not distributed) `core0_tail`, `core1_code`, `CPT_LIST`.

**STRONG INFERENCE:** use variable-sized, model-aware voice arenas with explicit owner/core/generation, alignment, capacity, guards and block-safe lifetime. Reserve actual requested voices for the four selected models, with at most two poly tracks, not ten worst-case Modal objects. Modal's 100 history words/voice are a lower bound only; two mono instances need at least 200 history words, plus coefficient caches, complete Voice/LPG/exciter/RNG state, FIFO and workspaces. Delay/resonator histories, envelopes, RNG and trigger state cannot be shared between voices. Code and immutable LUT/wavetables can share only under proven address visibility/precision contracts. Original RNG32 needs preservation, not replacement by the reference's 24-bit LCG.

Pinned `Voice::Init` already reuses the engine arena (`allocator->Free()` before each engine Init); it does not justify sharing mutable arenas between simultaneously running voices. StringEngine has three internal string voices; each String has 1024+256 delay sample cells: **3,840 delay cells per original StringEngine** before other state. These are source-level cells, not qualified DSP word counts. External data has 16 useful bits in the coupled model; 37+-bit Modal histories require packing/multiword storage and new numerical/timing proof. voice.cc (local-only reference: `plaits/upstream/plaits/dsp/voice.cc`; not distributed), string_engine.cc (local-only reference: `plaits/upstream/plaits/dsp/engine/string_engine.cc`; not distributed), string.h (local-only reference: `plaits/upstream/plaits/dsp/physical_modelling/string.h`; not distributed), [plaits-modal-native-optimization.md](<plaits-modal-native-optimization.md>).

## 5. Measured retained CPU baseline

**PROVEN within the model:** final initialized, cycle-weighted runs below execute the retained program with all twelve stock synth entries returned immediately. Every row has 256 numbered main blocks. The mean/p95/max are empirical; p95 uses nearest rank and is not a future workload bound. Columns include the host call stub and final stop prefetch. ARM readbacks cause separate complete service blocks; their statistics and instructions are stored separately in analysis JSON. They are not blindly added to one physical audio period.

| Workload | Core0 cycles mean / p95 / max | Core1 executed cycles mean / p95 / max | Coverage limit |
|---|---:|---:|---|
| idle | 47,405.102 /47,452 /47,452 | 47,403.508 /47,449 /47,451 | silent input; melodic generation disabled |
| drums | 47,405.102 /47,452 /47,452 | 47,403.508 /47,449 /47,451 | 36–39 ignored; superseded by separate valid-note attempt |
| mixer | 47,406.156 /47,452 /47,452 | 47,404.527 /47,449 /47,451 | nonzero declared bank stems; real level/pan automation |
| sends | 47,406.156 /47,452 /47,452 | 47,404.527 /47,449 /47,451 | same stems; real parameter automation; not every send/return condition |
| MasterFX | 49,936.297 /52,509 /52,509 | 49,935.258 /52,509 /52,509 | mask0 then $3B; active retained glitch included |
| line | 49,666.828 /49,741 /49,749 | 49,665.371 /49,738 /49,746 | both MIDI tracks ACT1 and note on/off |
| granular | 49,881.547 /49,947 /49,959 | 49,879.898 /49,946 /49,958 | ACT$1002; zero grain renders; source validation only |
| FXseq | 47,400.109 /47,452 /47,452 | 47,397.883 /47,449 /47,451 | ACT0 transport; populated pattern playback UNKNOWN |
| combined | 52,199.617 /54,716 /54,734 | 52,198.133 /54,715 /54,732 | line + mixer/sends/FX/glitch; drum PCM unqualified |

| Workload | Core0 instructions mean / max | Core1 instructions mean / max |
|---|---:|---:|
| idle | 40,866.367 /40,882 | 17,492.676 /17,510 |
| drums | 40,866.367 /40,882 | 17,492.676 /17,510 |
| mixer | 40,866.719 /40,882 | 17,493.051 /17,510 |
| sends | 40,866.719 /40,882 | 17,493.051 /17,510 |
| MasterFX | 43,089.266 /45,326 | 18,531.285 /19,585 |
| line | 41,961.984 /41,995 | 18,314.996 /18,345 |
| granular | 42,104.891 /42,135 | 18,400.008 /18,428 |
| FXseq | 40,864.703 /40,882 | 17,490.645 /17,510 |
| combined | 44,185.414 /46,407 | 19,353.949 /20,393 |

The separate **valid drum-note control attempt** measures core0 47,418.219 /47,490 /47,502, core1 47,416.766 /47,490 /47,499, but its output is identically zero and matches idle. It cannot supply the requested active PCM baseline. The nine corrected paired cases have 32256 retained stage comparisons with **zero differences**. Synth generation worker/preparation/combiner/post/source-selection intervals record zero instructions in disabled runs; $0281 remains the live RTS. Mean core0 generation-disable savings range 18,576.344–20,024.520 cycles/block across final cases; this is executed-cost evidence, not a code-size estimate or an extrapolation to twelve fully sounding original voices.

**UNKNOWN:** complete retained worst case for active sample drums, active granular grains, capture recording/playback, full FX-sequencer pattern playback and independent step-drummer sequencing. Line and granular ACT transitions and MIDI-note handling are exercised; granular's source is insufficient for grains. FX-sequencer mode's correct voice-off transport is exercised, not a real populated pattern's full automation workload. Nonzero total output in a stem-fed case does not establish sound from every subsystem.

Send-setting automation passes through the real parameter listener and flush. A final 8-numbered-block focused pair measures the actual transient stores: **704/704 nonzero writes** at P:$0CCD and $0CCE, peaks **11,916 /6,926**, exactly equal between baseline and generation-disabled runs. Send-plus-input writes at $0CE0/$0CE1 also match. Later $11E2/$11E3 overwrite that scratch with zero wet-delay output, so the end-of-chain `sends_return` snapshot is zero and cannot diagnose whether the earlier send input was active. **PROVEN:** active tested send input; **UNKNOWN:** nonzero long-delay/reverb wet-tail worst case. send-store-evidence.json (local-only reference: `builds/phase22-four-track-resource/send-store-evidence.json`; not distributed). Retained bank filters, stereo strips, level/pan, four-strip mixer, Master FX and limited active glitch execute. Full sidechain/mute/solo interaction coverage and arbitrary project/scene/transport scheduling remain UNKNOWN.

### Two scheduler models and cycle-count limits

prepare.py (local-only reference: `builds/phase22-four-track-resource/prepare.py`; not distributed) instruments actual opcode fetches including recursive DO bodies, addressed cycles, private/shared/external accesses and existing contracts. Its first model preserves the old one-instruction-per-core alternation. That model can give core1 many more modeled cycles than core0 because its polling instructions cost more; those counts are witnesses, not physical simultaneous deadlines.

weighted.py (local-only reference: `builds/phase22-four-track-resource/weighted.py`; not distributed) is a separate model: within each coupled call, step the core with the lower accumulated modeled cycles. No stock wait is removed, and core states persist. The final table uses it. Its core1 totals approximately match elapsed core0 clocks because the stock loop polls while idle. **Those totals are not an irreducible core1 workload reservation.** `core1_task_dispatch_cycles` also contains empty polling/dispatch work, not just audio work. No idle-loop percentage is promoted to safe rendering capacity.

Memory/peripheral behavior remains the established coupled model: declared external regions, initialization-validity guards, modeled ICC, no actual ESAI/interrupt or SDRAM wait-state timing. Private backing is larger than demonstrated hardware SRAM. The previously preserved immediate-gather primitive failure is not resolved or skipped by this new screen. `smoke-disabled` also retains an instrumentation recursion failure; the cycle-reader recursion guard fixed the profiler, not the firmware. [plaits-layout-a-coupled-replay.md](<plaits-layout-a-coupled-replay.md>) and the final build/source witnesses document these limits.

The conditional physical allowance remains **163,840 clocks/core/32-sample block** (246 MHz /48046.875 Hz), 327,680 across two cores. Physical clock/bus timing is unverified. The old 73,435.634 mean retaining stock synthesis is not reused as the new baseline. For the tested conservative program, core0's largest numbered main block is **54,734 cycles**, leaving **109,106** before renderers; subtracting one Modal filter bank leaves **31,409** for missing Modal work and other rendering. This is an arithmetic screen for this fixture, not a qualified complete-engine budget. Including separate service calls, the combined case's maxima are **54,904 core0 /54,903 core1**; those calls are not silently excluded from the evidence. Their per-call statistics remain separately visible in analysis.json (local-only reference: `builds/phase22-four-track-resource/analysis.json`; not distributed).

## 6. Four track output seams

**STRONG INFERENCE:** use distinct low-level adapters, converging on retained strips.

| Track | Event/control path to preserve | Candidate output seam | Retained downstream path |
|---|---|---|---|
| 1, original Synth1 | Generic sequencer/MIDI/automation → new Plaits voice assignment; retarget synth-specific ARM allocation/sinks | X:$2DF0–$2E0F immediately before P:$020C, after `$19BF` completion | $11E9→$1203→$125D; Y:$0840; level/pan, sends, sidechain and stock mixer |
| 2, original Synth2 | Same generic front end, independent track/voice state | X:$2E50–$2E6F at same bank boundary | $11F1→$1209→$126A; Y:$0880; same shared strip infrastructure |
| 3, original MIDI1 | Existing B1.3 `c_vnon/c_vnoff→c_vsend/c_vtick` mailbox, VB=$3B80 | Layout A `vpre=$336E`, `vchan=$37A7`, `vc2_nosc=$37D0`: private renderer output adapter before retained chain | Retained VCA/FX/filter and input-strip mixer $023E–$024E |
| 4, original MIDI2 | Same framework, VB=$3BB0, independent record and routing | Same shared code, selected by track state; distinct output/state ownership | Second input strip through same retained stock mixer |

The earlier B1.3 oscillator hook at $3999 was relocated/removed by Layout A; it is **not** the current hook. In Layout A `vc2_ngr` and `vc2_nosc` coincide at $37D0. The new adapter must explicitly supply a Plaits source; merely jumping there does not create one. The earlier VariableSaw test's input-ring insertion is reusable architecture, not newly qualified full-Voice integration. osc_only-labels.json (local-only reference: `builds/phase20g-dual-allocation/osc_only-labels.json`; not distributed), [plaits-midi-vpre-offline.md](<plaits-midi-vpre-offline.md>), reference vcf21_dsp.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21_dsp.py`; not distributed) `vpre`, `channel`, `control`.

Bank insertion retains original track processing and avoids requiring the retired voice-specific post chain. Raw $09D9 insertion would retain much of that voice closure and is a different architecture. Direct Y:$0840/$0880 insertion is later still and would skip bank processing; it is not chosen here. Initial MAIN-as-mono routing into each strip is the minimal candidate; AUX policy, original Plaits LPG versus B1.3 VCA behavior, note-to-sidechain triggers and new four-track parameter mappings need explicit adapters and fidelity tests. The equal-stem replay does not prove those note/envelope semantics.

## 7. Two-core scheduling models

| Model | Code/state and transfers | Latency/synchronization | Evaluation |
|---|---|---|---|
| A: tracks1/2 core0, tracks3/4 core1 | One renderer copy/model/core used; remote per-voice private state; remote strips delivered to core0 | Tagged ping-pong packets, consumer deadline before bank/vpre seam | Simple but symmetry is unsafe: allowed Modal pair on tracks1/2 costs 155,394 plus retained core0 processing, exceeding one-core screen |
| B: dynamic voice placement | May require code on both cores; independent home-core state; per-voice packets/mixing | Admission and allocation at synchronized boundaries; active migration would need serialization | Better CPU packing, but allocation/state migration and task deadline proofs remain UNKNOWN |
| C: heavy models on less-loaded core, split identical heavy pair | Choose home core using qualified per-model and retained worst profiles; code deduplicated per core | Keep each active voice on its home core initially; generation/sequence/ready tags; commit at audited native/Circuit boundaries | Preferred provisional architecture, with one mono Modal per core when two are selected; actual admission remains UNKNOWN |

Code cannot execute remotely from the other core's private P by assumption. D's partial Modal bodies total **220 P/core**, shared between its voices; putting them on both cores costs **440 P across cores**, not 220 per voice. Full engines/dispatch/resources are additional and unmeasured. Logical models sharing an implementation (the three six-op variants in pinned Voice registration) can share immutable code, but still have separate logical model quotas and voice state.

A control-local whole-voice renderer on core1 could return 32 final 24-bit mono samples per voice per Circuit block: **64 audio words/block for two remote mono tracks**, or 128 if retaining both MAIN/AUX outputs, plus sequence/completion/control words and actual bus accesses. This is a proposed payload, not measured transfer cycles. A diagnostic offload retaining host coefficient/excitation generation uses the previous **277 shared words/native render/voice**, worst **1,662 words/block for two remote voices**; its much larger coefficient traffic must not be confused with the whole-engine control-packet design. No shared packet addresses are assigned.

The renderer must not stall the stock gather service. Core1 retains P:$010E–$012A, R5/M5 gather contract, granular/glitch tasks, external ring writes and output publication. It may yield at mode/native-render boundaries, charging saves/restores and synchronization. The reference consumes core1 output for c=k−2 in core0 block k: **two blocks of latency**. One-block delivery is a new design target, not a proven property. Phase-aligned 12→32 FIFOs, generation-safe stale packet rejection and actual render deadlines need qualification. Existing granular OUT/GOUT/MIN cannot be reused as private Plaits packets.

## 8. Model restrictions and polyphony admission

architecture-requirements.json (local-only reference: `builds/phase22-four-track-resource/architecture-requirements.json`; not distributed) records the resource schema and policy-checks.json (local-only reference: `builds/phase22-four-track-resource/policy-checks.json`; not distributed) checks the offline assignment predicates. No UI was implemented. A future profile needs `{max_tracks:2, max_polyphony, full_state_words, worst_cycles_per_voice, code/resource ownership, complete_cpu_qualified}`. Modal currently has only `filter_cycles_lower_bound=77697`, history lower bound100 and body P lower bound220; complete cost, full state and admitted polyphony remain UNKNOWN. String and every so-called light engine have no native complete cost here. The sealed VariableSaw oscillator cost is not silently substituted for an entire original Plaits model.

| Required/stress assignment | Evidence and admission |
|---|---|
| Modal + Modal + light A + light A, all mono | Valid assignment. Two measured filter banks =155,394; other voices, retained work and complete Modal costs unpriced. UNKNOWN admission |
| String + String + light A + light A | Valid; original StringEngine internally renders three strings. Native complete CPU/P/state UNKNOWN |
| Four different heavy/light models | Valid; four different resident code/resource sets may be needed. UNKNOWN total |
| Two distinct model pairs | Valid; sum both measured complete profiles when available. UNKNOWN today |
| Two Modal poly2 tracks + two other mono tracks | Valid quotas but four Modal banks alone =310,788; with this measured retained baseline exceeds the conditional aggregate screen before other engines |
| Two Modal poly4 tracks + two other mono tracks | Valid quotas, eight Modal filter banks =621,576; reject this implementation under 327,680 raw two-core allowance even with retained work zero |

Four mono Modal tracks violate the final assignment rule and are not a required support case. Two Modal tracks do not imply two Modal voices when polyphony is requested. A single Modal poly2 track plus one Modal mono track costs at least 233,091 filter cycles; final admission remains UNKNOWN, rather than inventing a poly2 guarantee.

**STRONG INFERENCE:** dynamically disable poly pads unless the transaction fits both per-core complete CPU ceilings, state/workspace arenas, resident code/LUTs, transfer deadlines and `MAX_POLY_TRACKS`. Budget reserved/releasing voices and FIFO/history lifetimes, not just held keys. Repeated notes must steal within reserved capacity or await a safe release, avoiding temporary over-allocation. Engine changes, scene/project restore and external controls use the same runtime validator as the UI; failure retains the previous valid configuration. Select a core at admission; active state migration is not required initially. Every track reserves at least one model-appropriate voice, with no ten-Modal blanket allocation.

## 9. Preset-view contract, recorded only

| Pads, one-based | Page1 | Page2 |
|---|---|---|
| 1–8 | Original models1–8, green | Additional models17–24, yellow |
| 9–16 | Original models9–16, pink | Reserved/unassigned |
| 17–24 | Eight patch/preset slots | Same slots |
| 25–27 | Engine-specific extra/control pages | Same pages |
| 28 | Model bank toggle | Toggle back |
| 29–32 | Mono / poly2 / poly3 / poly4 | Same controls |

**PROVEN source mapping:** pinned `Voice::Init` registers eight additional models first, then the original sixteen. Page1 must map to internal indices **8…23**, Page2 to **0…7**. Modal internal20 is Page1 pad13; String internal19 is Page1 pad12. These model IDs must be stable in project storage rather than confusing page order with source registry index. A model already selected on two *other* tracks is unavailable; the currently selected track does not disable its own model pad merely because one other track shares it. Patch/scene loads revalidate the same global constraints. Colors/order are requirements, not a new renderer or UI implementation. voice.cc (local-only reference: `plaits/upstream/plaits/dsp/voice.cc`; not distributed) and architecture-requirements.json (local-only reference: `builds/phase22-four-track-resource/architecture-requirements.json`; not distributed).

## 10. Rollback boundary

**PROVEN offline:** rollback-evidence.json (local-only reference: `builds/phase22-four-track-resource/rollback-evidence.json`; not distributed) decodes the existing official SYX in memory and matches the preserved 314,844-byte official application, SHA-256 `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da`, against the application slice of the full flash dump. It extracts the existing official core0 program (10,846 words) in memory and verifies the original synth entry at P:$0281 and combiner at $09B9. Thus the official application contains the original sound generators; they are not permanently deleted from some separate immutable boot component by this proposal.

**STRONG INFERENCE:** application-only replacement requires no changes to the Novation bootloader at `$08000000–$0800FFFF`, bootloader flash sectors, option bytes or recovery-key handling. The reference codec links updates at `$08010000` and excludes the first 64 KiB; its application header/block/CRC protocol does not itself prove bootloader recovery independence. Successful official application reinstallation would restore stock Synth1/Synth2 because their ARM/DSP code is inside that official application.

**UNKNOWN:** whether the documented Scales+Preset+Note path recovers every failure to boot the application/DSP. This phase does not execute the bootloader or change the earlier recovery gate. No hardware recovery success is claimed from SYX decoding, hashes, application boundaries or documentation of keys. reference ct_fw.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/ct_fw.py`; not distributed), reference rc_uploader.html (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/rc_uploader.html`; not distributed), [firmware-recovery-gate.md](<firmware-recovery-gate.md>).

**STRONG INFERENCE, design requirement:** no persistent format change may be required for stock boot. Keep calibration/settings/boot configuration independent of custom model selection; use versioned, optional custom project/patch data with safe missing/invalid defaults and no dependence on pool addresses. Four-track custom preset metadata must not silently overwrite original stock patch interpretation. Official firmware restoration and compatibility of custom patches/projects are separate questions. No persistent format was changed in this phase.

## 11. Compact audit and next experiment

| Resource/gate | Finding |
|---|---|
| Core0 safe additional stock P reclaim | UNKNOWN; 0 newly admitted; prior Layout A deletion1,075 retained as historical evidence |
| Core0 usable P ranges | $3BBA–$3FFF is existing 1,094-word unoccupied tail including19 original words; new fragmented stock regions unqualified |
| Core0 reclaimed X / Y | UNKNOWN; 0 newly admitted; 144-X/512-X/480-Y candidates require writer closure |
| Core0 retained mean / worst main cycles | Combined measured **52,199.617 /54,734**, with the stated incomplete workload coverage |
| Core1 safe P available / usable range | UNKNOWN; unloaded $07FF–$3FFF candidate14,337; retain stock gather and B1.3 code |
| Core1 safe X/Y/shared/external state | UNKNOWN; no allocation granted; preserve GB/ring/capture/gather regions |
| Core1 retained mean / worst executed cycles | Combined **52,198.133 /54,732** under cycle-weighted scheduling, including idle polling; not useful-work worst case |
| Track→core model | Provisional heavy-aware home-core assignment; split two Modal mono voices; local bank/vpre adapters remain distinct |
| Transfers | Proposed final mono payload32 words/remote voice/block + protocol; no address/cycle/latency qualification |
| Model / poly-track maxima | Exactly2 tracks/model; exactly2 tracks may request polyphony; actual voice caps depend on qualified complete profiles |
| Modal required same-model mono count | 2; preliminary filter cost155,394, complete engine UNKNOWN |
| Rollback | Bootloader/recovery code unchanged by design and this phase; official app contains stock synths; broken-app recovery guarantee UNKNOWN |

**UNKNOWN final admission:** final program/data ownership, full active retained CPU worst case, complete model costs, packet placement and deadlines remain open. Successful equal-stem replay demonstrates a useful sound-generation boundary; it does not turn nonexecuted bytes or unobserved RAM into safe allocations.

**Single smallest next experiment:** qualify one new interval, **P:$0282–$0386 (261 words)**. Keep the tested RTS at $0281, establish the complete incoming code/data/ARM table-job target domain for this interval, poison/guard its fetches and P-data reads/writes in a separate interpreter clone **from boot onward**, and replay actual **stock-synth** note-on/off, preset restore and parameter/table-job transitions against the same equal-stem retained baseline. Boot/data-copy consumers must be checked, not merely post-boot absence. A caller, data read or writer rejects that interval; a bounded pass must retain its precise domain. This directly advances the missing P allocation proof without porting another engine or assuming the rest of the 2,310-word candidate worklist is free. The active PCM/grain CPU gap remains separately documented rather than silently solved by that test.

Reproduction and provenance: `prepare.py` builds the separate instrumented runner, `weighted.py` its second scheduler model; `corrected_batch.py` runs the initialized 256-block pairs with `RESOURCE_WEIGHTED=1`; the separate real-drum pair uses the documented notes. `closure.py`, `analyze.py`, `architecture.py` and `report.py` derive the inventories and report. Fresh replay directories are required; original/incorrect/failed explorations are preserved. The build scripts write only in this CIRCUIT experiment directory, and use installed pinned emulator libraries. No reference builder or uploader is invoked.

FOUR-TRACK PLAITS ARCHITECTURE = UNQUALIFIED

## 12. Exact P:$0282–$0386 qualification follow-up, 2026-10-15

**UNKNOWN — P0282-0386 RECLAIM = UNQUALIFIED.** The requested 261-word experiment is now recorded in [p0282-0386-reclaim-qualification.md](<p0282-0386-reclaim-qualification.md>) and phase23 evidence.json (local-only reference: `builds/phase23-p0282-0386/evidence.json`; not distributed). It admits **0 additional P words**. The final four-track code/data budgets remain unknown. No second interval, Plaits port, firmware generation or hardware operation followed.

**PROVEN:** this is the stock synth slot routine body entered through $0281. The new paired interpreter puts the existing RTS at $0281 in **both** variants before DSP boot, then observes/traps actual fetches and P-data reads/writes only in the proposed interval. Both variants retain identical program bytes. A 256-block mode/automation/note replay plus bounded reload/restore/helper cases yields **2,154 exact state checkpoints**, **637 coupled audio calls** including ARM readbacks, identical stage/output samples, supported registers and shared/external transaction streams, and zero target access. The real stock note handlers $080219E8/$08021C48, both-track $0802FC82 reloads and the available $0802EEFE captured-record project apply execute. Equal bank stems remain modeled downstream input; this is not stock sound-generator equivalence or an active-grain/PCM guarantee.

**PROVEN:** the apparent external branch P:$2706→$0316 is a linear-disassembly false positive. P:$2706 contains curve word `$0FC316` inside the $268C–$2716 boot table, copied at $271D into X:$1F57. It is read as table data, with zero $2706 instruction fetches. The exact literal/indirect inventories are in classified-references.json (local-only reference: `builds/phase23-p0282-0386/classified-references.json`; not distributed). **STRONG INFERENCE:** the interval body is removable behind the retained RTS and intact descriptor function words; complete transition closure is still **UNKNOWN**.

**UNKNOWN — the decisive gaps:** MIDI bank-select messages return but program change waits for an unserviced original ARM task at $08022AB6…$08022AC8. Separately, the old readback bridge advances audio at P:$01ED but omits the real main-loop table-job dispatcher $0121→$1C53. Its interrupted audio-only polling run is preserved and excluded from successful table-initialization coverage. Adding the original $0113–$0129 service prefix causes the **baseline** to reach its instruction limit at P:$1B44, before $012A, in two attempts. No completed integrated table-initialization comparison exists. Isolated original DSP helper replays of the preserved actual ARM posts (selectors2/3/4) complete exactly and never access the target; those do not repair the integrated scheduling/initialization gap. No fake ready sentinel or task completion was supplied.

The smallest next experiment in section11 is therefore superseded by this result: **first make the unguarded, generation-disabled baseline complete the original P:$0113→$0121→$1C53 initialization transition with authentic ARM ordering, isolating the $1B44 limit; then mirror that same transition through the existing interval guard.** Remain on this range. The reproduced asynchronous program-change case must also complete before full admission. No first retained reference inside $0282–$0386 has been established, and no smaller sub-range or adjacent range has been qualified. The interval cannot yet be allocated to Plaits. All 451 previously recorded reference inputs and 183 pinned source files remain unchanged.

FOUR-TRACK PLAITS ARCHITECTURE = UNQUALIFIED
