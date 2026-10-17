> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Stock master signal path qualification

2026-10-15. **PROVEN within the stated offline model:** the restored non-silent stock baseline and Layout A match through 8,192 consecutive numbered audio blocks, with no divergence. The three retained 64-block paired regressions also pass. The conservative 1,075-word shared-code budget is qualified for the next offline admission experiment; no Plaits engine was ported.

## Evidence and scope

**PROVEN:** the work uses the existing packed DSP analysis streams, the authentic ARM flash/RAM artifacts, actual ARM control routines, both executing DSP interpreters, and the previously recovered stock wavetable families. No application firmware image was generated. No hardware was accessed. The reference checkout was read-only: integrity audit (local-only reference: `builds/phase20l-master-path/reference-integrity.json`; not distributed) checks 451 previously hashed inputs with no changes.

Principal reproducible sources:

- [Instrumented coupled interpreter](<../plaits/poc/authentic_qualification/coupled.cpp>): `replayFetch`, `stage`, `replayAccess`, `STATEWRITE/STATECHECK`, vpre and core-1 register contracts.
- [ARM/DSP readback bridge](<../plaits/poc/authentic_qualification/live_master.py>): `Bridge`, its actual-ARM `$08029344` read hook, `experiment`.
- [Short paired replay](<../plaits/poc/authentic_qualification/pair_master.py>): `Peer`, `run`.
- [Long paired replay](<../plaits/poc/authentic_qualification/long_master.py>): `Pair`, `main`.
- [Statistics and provenance extractor](<../plaits/poc/authentic_qualification/master_evidence.py>): `stages`, `sources`.
- Actual core-0 listing (local-only reference: `builds/phase20k-stock-wavetable/core0.asm`; not distributed) and controlling ARM paths (local-only reference: `builds/phase20l-master-path/ARM-controlling-paths.asm`; not distributed). Addresses below are DSP P-word addresses or ARM byte addresses, explicitly distinguished.

The baseline core-0 SHA-256 is `64034810b65a6df258333154af8753de09caa8cd4cddb8b7cd8514aab52ddd5b`; Layout A is `e7eee50bc85c995cc9ca00b5bdc55ce279366bfe747bb93b2fc43db3e511f4c0`. These are the pre-existing DSP analysis artifacts, copied without constructing a firmware image. Paired result (local-only reference: `builds/phase20l-master-path/paired-result.json`; not distributed).

## 1. Verified source

**PROVEN:** core 0 finishes the raw mono generator loop with its store at P:`$9D8`; the snapshot at P:`$9D9`, before subsequent processing, contains 32 signed 24-bit fractional samples in X:`$2C46–$2C65` (Q1.23 interpretation). X:`$CC` records bank 0/1. The same scratch buffer is reused sequentially, so bank context is captured at the instruction boundary.

In the unchanged original 64-block stimulus, both banks first become nonzero at block 1:

| Bank | Samples | Min | Max / absolute peak | RMS, integer sample units | Nonzero |
|---|---:|---:|---:|---:|---:|
| Synth1 | 32 | 878 | 27,051 | 17,606.077555 | 32 |
| Synth2 | 32 | 5 | 231 | 131.202610 | 32 |

Across those 64 blocks, raw peaks are 1,488,150 and 1,317,551 respectively; each has 2,016 nonzero samples. Original stage statistics (local-only reference: `builds/phase20l-master-path/before/stage-statistics.csv`; not distributed), summary (local-only reference: `builds/phase20l-master-path/before/stage-summary.json`; not distributed), and instruction-tagged traffic (local-only reference: `builds/phase20l-master-path/before/traffic.txt`; not distributed).

## 2. Downstream graph

**PROVEN control/data flow:** the following graph comes from executed boundaries and the core-0 listing, rather than names of reference modules. The path is serial through each row, except the explicitly described parallel sends and buses.

| Input | Executed routine / P address | Output | Controls/state |
|---|---|---|---|
| Raw mono X:`2C46`, 32 | `9DD–A7E`; selected `BDD`, which first calls `AA8` | X:`2C46` or `2C68` | Prepared per-voice X record, normalization history; table pointer Y:`1C` |
| Normalized block | `BDF–BE7`, prescale multiply | X:`2C68`, 32 | X:`5AE` / `76A` in these selected voices |
| X:`2C68` plus preceding histories | `C18 → C9D`; coefficients `C2D/C88` | First-pass scratch X:`2C88` area | Coefficient rows X:`1600–193F`; runtime Y:`F5F–F7F`; voice Y histories |
| First-pass scratch | `C22 → C9D`; branch selection/copy through `A25–A28` | X:`2D2C` area, then X:`2C46` | X:`5B1/5B2` or `76D/76E`, selected coefficient offsets; voice histories |
| Post-filter mono X:`2C46` | `A7F–A94` | Bank sum X:`2DF0` or `2E50`, 32 | Gain increment/current X:`5BC/5BD` or `778/779`; selected envelope Y:`130` or `370`; X:`CC` |
| Bank mono sums | `11E9/11F1 → AA8` | Same bank mono buffers | X:`3F7/569` family, Y:`7D3/7D9` histories |
| Bank mono sums | `1203/1209 → 120F` recursive strip processing | Same bank mono buffers | X:`3FA/56C` family; Y:`7ED/7F5` histories |
| Bank mono | `125D/126A → 1252`, then `FF9` strip processing | Stereo Y:`840` / `880`, 64 | X:`400/572`, X:`96E/972`; Y:`782/790`; related strip histories |
| Envelope/trigger state | `1277/1288/1299/12AA → 12BB` | X:`2028/2048/2068/2088` coefficient ramps | Trigger bits X:`99+N1`; per-strip X parameter records and Y envelope state |
| Global level/pan targets | `1AFC/1B02 → 1B2B`; then `12ED → 13A3` | X:`1B32–1B71`, `1B72–1BB1` | X:`52–55`, X:`407/579`; smoothed stereo gains Y:`57–5A`; sidechain ramps X:`2028/2048` |
| Y:`840/880`, inserted input strip, gain arrays | `23C → vpre 336E`; mixer `242–24E` | Y:`800`, 64 | Stock gains above; input coefficients X:`20C/24C`; vpre caller contract checked |
| Y:`800` and X:`2E70` bus | `24F–25B` | Y:`800`, 64 | Bus accumulation; no forced substitute samples |
| Synth strips, send bus X:`2EF0`, physical input ring | `CB8` onward | Send/intermediate Y:`9C0` and later scratch | X:`1BB2/1BF2`, `1C32/1C72`, retained effect parameters |
| Y:`800`, sends/effects and stereo scratch | `D32–D57 → 13AD–1468` | X:`2E10`, 64 | Master filter X:`CF/D0`, Y:`20A8–20CB`, recursive histories; Y:`7FF` master multiplier |
| X:`2E10` | `26B–273` | X:`2E10`, scaled by 4 | Stock arithmetic, unchanged |
| X:`2E10` | `274 → 2ACE → 3E1F… → 2AD0` | X:`2E10` | Retained capture/glitch wrapper and Master FX selectors/state at X:`3A40` family |
| X:`2E10` | `276 → 21C4`; selected output loop `2247–2251` | X output ring; X:`1000–103F` for this fixed-ring fixture | X:`DE` output level, X:`1EE6` current level; Y:`10D–110` compressor/limiter settings |
| X output ring | Output ISR `1B4–1D8`, reads at `1C8/1CA` | Output staging Y:`21/22`, subsequent peripheral path | Y:`FFE` ring reader, Y:`FFD` producer; actual ESAI interrupt timing is **UNKNOWN** |

Snapshot names `post_eq`, `stereo_strip`, and `sends_return` are measurement labels. The last does **not** assert that the parallel send-return buffer must be nonzero when no send is enabled. The first recursive-pass snapshot is X:`2C8A`, corrected during instrumentation from a premature read of the second destination. Detailed history-prefix operations remain visible in the instruction-tagged trace. No audio-processing instruction was changed.

**UNKNOWN:** a complete independent semantic decomposition of mute/solo and every compressor/limiter branch. Executed level/pan and trigger-dependent gain arithmetic is proven; separate universal “mute” or “solo” stages are not invented. Both enabled and bypassed Master FX control paths were tested as described below.

## 3. Where silence began

**PROVEN:** the earliest nonzero-to-zero transition in the first few blocks is the voice recursive filter. This is a transient startup condition: in the original replay Synth2's filter opens at block 4, Synth1's at block 14. ARM-emitted filter targets are already present, but stock DSP smoothing advances them from initial state. For example, block 2 reads X:`2E9=$0253AF`, Y:`14=$FBA000`; P:`6DF–6ED` clamps the resulting cutoff control to zero. P:`498` publishes X:`5B0=0`, and `C2D/C88` produce the corresponding near-zero feed-forward coefficients. By block 63, X:`2E9=$1CEFF2` and Y:`91=$17C276` are nonzero. This filter latency does not explain the persistent silent master.

**PROVEN:** after settling, the first persistent zero on Synth1 is the stock mixer. At block 63, P:`242` reads nonzero Y:`840` but X:`1B32=0`; the same is true for the following coefficient words. P:`243–24A` explicitly multiplies these samples by those zeros. The coefficient producer `1B2B` reads X:`52=0`; its output Y:`57/58` and the derived X:`1B32` array stay zero. This closes the causal chain, rather than diagnosing silence from an isolated zero parameter.

**PROVEN:** Synth2 additionally had a closed voice gain. P:`4C6` read Y:`370=$000080`, and P:`4D0/4D1` published zero X:`778/779`, although raw and filtered oscillator samples were nonzero. The old reference SPI adapter returned zero for every read, including voice-allocation feedback. Original reference adapter (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/shi_capture.py`; not distributed), `attach`, `SPI_XFER`; reference session (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/dsp_session.py`; not distributed), `Session.full_dump`, `Session.midi`.

**PROVEN:** restoring the mixer alone makes Y:`800` nonzero but does not establish the final output path. The settings restoration was also missing: X:`CF/D0` remained at startup values in the master filter, and X:`DE=0` closed the final output multiplier. The final-output restoration below supplies all of these through actual ARM code.

## 4. Controlling state and authentic restoration

**PROVEN:** `Session.full_dump` marks patch dirty groups at `200067FC+16`, but does not restore the separate global/settings groups serviced through `20006A0C`. The experiment executes actual ARM `$08028EF2` and `$08028FD6` on the unedited authentic RAM snapshot. The getter `$08036192 → $0803BE3E` reaches the actual bank object and descriptor reader `$0803BD00`; the final byte read is `$0803BD0C`. Executed getter provenance (local-only reference: `builds/phase20l-master-path/ARM-getter-provenance.json`; not distributed), emitted writes (local-only reference: `builds/phase20l-master-path/ARM-provenance-events.json`; not distributed).

| Source bank / index | Actual RAM byte | Value | Actual ARM conversion / destination |
|---|---|---:|---|
| `$20 / 46` | `20010358` | 41 | `28D16`, shift 23 before upper-24 transport → X:`52=$148000` |
| `$20 / 47` | `20010359` | 100 | `28DAC` → X:`54=$320000` |
| `$20 / 50,51` | `2001035C/5D` | 64,64 | `287C4`, center pan → X:`53/55=$400000` |
| `$21 / 0` | `20010364` | 69 | `28F4A` → X:`CF=$450000` |
| `$21 / 1` | `20010365` | 30 | `28F5C` → X:`D0=$1E0000` |
| `$21 / 7` | `20010371` | 127 | `28FBC` → X:`DE=$7F0000` |

The settings call also emits Y:`10D/10E/10F=0`, Y:`110=1`, preserving the dump's actual output processing settings. No VCA or mixer coefficient is manually set to unity. The source values above are **authentic artifact values**, not claimed universal defaults for every project.

For note allocation, the bridge intercepts the actual ARM DSP-read helper `$08029344`, flushes all preceding actual SHI writes in order, executes the unmodified complete DSP audio block, reads the requested X/Y word, and returns it in the helper's original 32-bit format (`word << 8`). The actual ARM allocator `$080217B4` and note preparation continue executing. The isolated Synth2 test reads X:`37=$0080FF`, then its real Y:`36F` voice history; note setup reaches the bank-1 voice instead of accepting fabricated zero feedback. Synth2 readbacks (local-only reference: `builds/phase20l-master-path/synth2/ARM-readback.json`; not distributed), both-bank readbacks (local-only reference: `builds/phase20l-master-path/both/ARM-readback.json`; not distributed).

**STRONG INFERENCE:** these were harness omissions, supported by exact code provenance and restoration from unchanged snapshot values. **UNKNOWN:** whether this particular scheduling/readback sequence matches interrupt timing on a physical device. The bridge deliberately models servicing one complete stock block before each read; peripheral cycle-counter timing is not hardware-qualified. It does not supply assumed free-slot numbers or force envelope state.

## 5. Non-silent master and both-bank isolation

**PROVEN in this coupled model:** the complete generator → filter → gain → strip → mixer → master filter → Master FX → output-level path reaches the actual output ring. These are separate runs from the same initial artifacts, with only the stated bank receiving a note. The unselected bank's accumulated audio remains zero even though its seeded raw oscillator scratch may oscillate.

| Test | First nonzero output-ring block | First L/R peak | First per-channel RMS | First nonzero L/R | Peak L/R across run |
|---|---:|---:|---:|---:|---:|
| Synth1 alone | 9 | 4 / 4 | 2.345208 / 2.345208 | 11 / 11 | 142,966 / 142,966 |
| Synth2 alone | 7 | 4 / 4 | 0.707107 / 0.707107 | 1 / 1 | 296,847 / 296,847 |
| Both | 15 | 4 / 4 | 2.828427 / 2.828427 | 16 / 16 | 495,943 / 495,943 |

Early tiny values are followed by substantial signal; a lone rounding residue is not the evidence for a working path. RMS is in signed integer sample units; divide by 8,388,608 for Q1.23 full-scale units. Each measured output block contains 32 L/R pairs. Control-read servicing also executes complete blocks before the 64 numbered blocks, so aggregate summaries include those extra blocks; no DSP reset occurs between them.

Per-block **min, max, absolute peak, RMS, and nonzero count for every captured stage** are in Synth1 CSV (local-only reference: `builds/phase20l-master-path/synth1/stage-statistics.csv`; not distributed), Synth2 CSV (local-only reference: `builds/phase20l-master-path/synth2/stage-statistics.csv`; not distributed), and both-bank CSV (local-only reference: `builds/phase20l-master-path/both/stage-statistics.csv`; not distributed). Their neighboring `stage-summary.json` files identify first nonzero blocks and aggregate statistics.

For the both-bank run, peak propagation is raw mono 1,565,340 / 1,754,768 → accumulated banks 335,474 / 1,910,131 → stereo mixer 345,024 → master-filter buffer 124,962 → scaled/post-Master-FX 499,848 → final output ring 495,943. These are maxima across the run, not a claim that all peaks occur in the same block. Both-bank summary (local-only reference: `builds/phase20l-master-path/both/stage-summary.json`; not distributed).

## 6. Layout A comparisons

**PROVEN:** Layout A was not compared until the restored baseline output ring was nonzero. The first 64-block comparison passes with zero differences and byte-identical stage files. A separate 64-block probe enables Master FX with modeled held-key mask `$3B` at authentic object `20044D94+6` for its second half; actual `c_vtick` computes and transports the effect parameters. Its paired replay also passes. Main result (local-only reference: `builds/phase20l-master-path/paired-result.json`; not distributed), active Master FX result (local-only reference: `builds/phase20l-master-path/active-MasterFX-probe-paired-result.json`; not distributed).

At each compared boundary the runner compares bytes for both cores' entire private X/Y backing stores, shared SRAM, all declared external words and initialized/unknown bits, external canaries, and all supported architectural registers before the performance-counter group. It also compares the ordered sequence of shared/external reads and writes and private writes (including address space, core, DSP/host origin, address and value). This is a direct comparison, not a digest-only test. Different program contents and relocated instruction PCs are intentionally not treated as data-state differences. Live vpre caller-register/modifier and core-1 task contracts are independently enforced.

The vpre contract checks X0/X1/Y0/Y1, R0/R1/R2/R3/R4/R6/R7, N0, M0/M2/M4 between actual entry P:`336E` and return P:`23E`. The core-1 task contract independently checks R5/M5. The block-boundary comparison additionally includes supported accumulators, address registers, all N/M modifiers, SR/OMR, loop and stack registers. Unsupported peripheral registers and physical interrupt timing are not silently described as measured hardware state.

**PROVEN:** negative controls detect both a changed final X word and a transient X write restored before the boundary. Thus equal final memory alone cannot conceal different recorded traffic. Comparator negative controls (local-only reference: `builds/phase20l-master-path/comparator-negative-controls/result.json`; not distributed).

**PROVEN additional coverage:** a third 64-block paired replay exercises actual project-parameter listener `$08034D92`, resolved listener object `20044BD8`, followed by the real global sender and retained FX service. X:`52/54` alternate between `$148000/$320000`; X:`53/55` between `$200000/$60820F`. These are deliberate runtime level/pan automation inputs after baseline restoration, not manual DSP gain patches. Final left/right peaks are 700,717 / 894,997; all compared samples, state, registers and recorded traffic agree. [Probe implementation](<../plaits/poc/authentic_qualification/optional_master.py>), actual ARM events (local-only reference: `builds/phase20l-master-path/mixer-send-FX-probe/actual-ARM-events.json`; not distributed), paired result (local-only reference: `builds/phase20l-master-path/mixer-send-FX-probe-paired-result.json`; not distributed).

Send targets X:`E7/E8` become `$0A4000/$190000`. At block 63, P:`CCD/CCE` actually write nonzero Y:`9C0` send samples, with left/right peaks 242,897 / 320,043; P:`CE0/CE1` preserve nonzero send-plus-input samples. Later P:`11E2/11E3` replace that scratch with zero wet-delay output. The end-of-chain snapshot named `sends_return` therefore cannot measure the earlier send input. This is a parallel wet branch; the direct master remains nonzero. Store-site statistics (local-only reference: `builds/phase20l-master-path/mixer-send-FX-probe/store-stage-statistics.csv`; not distributed), [extractor](<../plaits/poc/authentic_qualification/master_write_stats.py>). These CSVs also measure bank normalization, master-filter inputs/outputs, and final ring stores at their actual instructions.

The active Master FX probe executes P:`2ADA` and each of `2AE7/2B0C/2B62/2BD6/2C32` 64 times, with 2,048 fetches at active effect-loop P:`2AF9`; the ordinary both-bank test executes none of those active dispatches. Its final output peak is 1,370,880. This establishes active DSP effect execution, not only a nonzero ARM selector. Active-effect histogram (local-only reference: `builds/phase20l-master-path/active-MasterFX-probe/pc0.txt`; not distributed), stage summary (local-only reference: `builds/phase20l-master-path/active-MasterFX-probe/stage-summary.json`; not distributed).

The guard covers P:`3BBA–3FFF` at every opcode boundary, including interpreted DO bodies, with block-end canary checks and P-write rejection. The arithmetic is important: `3BBA–3FEC` comprises the **1,075 deleted words**; `3FED–3FFF` is the existing 19-word tail. The full guarded interval contains 1,094 words. This experiment does not increase the requested shared-code budget by adding that pre-existing tail.

## 7. Long replay and remaining limits

The interrupted attempt is preserved under `builds/phase20l-master-path/long-baseline-interrupted-20261015` and `long-layout-A-interrupted-20261015`. Their common stage-file prefix is byte-identical; complete output-stage records extend through label 7,949. However, neither interpreter process survived, and the old runner saved commands/results only at normal close. Those traces are not a resumable CPU checkpoint or a substitute for the final state/transaction comparison. Only the long replay therefore had to restart; the completed source investigation, isolated synth tests, and three short paired regressions were retained. The workload and native interpreter were unchanged. The rerun adds incremental command/output journals and per-block comparison records, explicitly not claiming resumable suspended fibers. Preservation record (local-only reference: `builds/phase20l-master-path/interrupted-replay-preservation.json`; not distributed).

**PROVEN:** the completed long replay contains 8,192 consecutive numbered blocks with both synth note/retrigger/release paths, actual CC74 parameter updates, actual global mixer parameter sends, deterministic input, retained MIDI line selection and oscillator disable, and actual retained-mode service ticks. Drum-channel messages are attempted. Unsupported MIDI CC7/10 attempts do not emit DSP parameter writes and are not counted as successful mixer parameter changes.

**UNKNOWN unless separately measured:** audible sample drums and their external sample payloads; active granular/capture/glitch content; all compressor/limiter branches; all project-load modes; physical interrupt/ESAI timing. Entry to retained service or bypass code alone does not qualify audible operation of those subsystems. The stock Master FX active probe is separately proven above. No claim of global memory ownership, physical CPU headroom, firmware recovery, or readiness to flash follows from these offline tests.

## 8. Final verification and admission decision

**PROVEN:** all 8,192 consecutive numbered blocks (0–8,191) completed in one uninterrupted rerun, without resetting either DSP. Every block has an exact native state/transaction comparison and an intact guard check in both layouts. There are 18,476 complete stock audio-block/vpre calls in total because actual ARM readback servicing also executes complete blocks. Those additional calls are included in sample-file and traffic comparisons; they are not substituted for the 8,192 required numbered blocks. The run issued 10,284 actual-model DSP readbacks to the executing ARM code and checked the core-1 R5/M5 task contract 65,441,166 times.

| Requested gate | Confidence / result | Evidence |
|---|---|---|
| Rendered samples, every captured stage and final stereo ring | **PROVEN — exact** | Complete baseline/Layout A stage files compare byte-for-byte; all 8,192 main-block output observations are present. |
| DSP data state | **PROVEN — exact, 8,192 comparisons** | Both cores' complete private X/Y backing, shared SRAM and declared external words/known bits/canaries. |
| Supported architectural registers | **PROVEN — exact** | Native boundary comparisons plus 18,476 vpre caller contracts and 65,441,166 core-1 task contracts. |
| Shared/external transactions | **PROVEN — exact** | Ordered value/address/core/space/read-write/origin records, compared as bytes; private writes included. Negative transient-write control also passes. |
| P:`3BBA–3FFF` | **PROVEN — intact** | 8,192 block-end checks per layout; opcode-time execution/data guards throughout; zero P writes. |
| Active stock Synth1 and Synth2 | **PROVEN** | Isolated-bank tests plus 8,185 main blocks with both accumulated banks nonzero. |
| Mixer, level/pan automation and sends | **PROVEN for exercised cases** | Long mixer path/global sends, plus retained 64-block real ARM parameter-listener automation with distinct L/R output and measured nonzero send stores. |
| Active Master FX | **PROVEN for exercised selectors** | Both retained 64-block active-effect comparisons pass, including actual DSP effect-loop execution. This is separate from the long run's ordinary FX service/bypass coverage. |

The final main-block stereo output has L/R peaks **3,179,481 / 3,179,481**, L/R RMS **1058233.182568 / 1058233.182568** in signed integer sample units, and L/R nonzero sample counts **262,012 / 262,012** out of 262,144 samples per channel. Main-block observations with nonzero signal: Synth1 bank **8,185**, Synth2 bank **8,192**, final ring **8,189**. Idle/released blocks are retained rather than removed from the comparison.

The rerun also reproduces **348,041,998 bytes** of the interrupted run's preserved common stage prefix exactly. Thus the necessary reconstruction of continuous execution did not alter the earlier measured sample path. The independent verifier rechecks all 8,192 sequential comparison records, byte-compares complete output journals and sample files, verifies the P-guard logs and zero P-write counts, verifies the native executable against its existing build provenance, and confirms **451 reference inputs unchanged**.

Primary final evidence: independent verification (local-only reference: `builds/phase20l-master-path/final-verification.json`; not distributed), long-run result (local-only reference: `builds/phase20l-master-path/long-result.json`; not distributed), per-block native comparison records (local-only reference: `builds/phase20l-master-path/long-checks.jsonl`; not distributed), baseline complete output (local-only reference: `builds/phase20l-master-path/long-baseline/output.txt`; not distributed), Layout A complete output (local-only reference: `builds/phase20l-master-path/long-layout-A/output.txt`; not distributed), streamed per-stage statistics (local-only reference: `builds/phase20l-master-path/long-baseline/stage-statistics.csv`; not distributed), main/all-observation summaries (local-only reference: `builds/phase20l-master-path/long-baseline/stage-summary.json`; not distributed), [verifier implementation](<../plaits/poc/authentic_qualification/verify_master_final.py>).

**STRONG INFERENCE:** Layout A's conservative deletion/relocation preserves the tested non-silent stock signal path and exercised retained control/effect paths, making its 1,075 reclaimed program words suitable for the next offline shared-code admission experiment. The original program has 16,365 words and Layout A has 15,290: the difference is exactly 1,075. The additional 19-word original tail remains excluded from this budget.

**UNKNOWN / not qualified by this replay:** audible sample drums or their sample payloads; isolated retained MIDI line audibility; active granular/capture/glitch content; delayed wet-tail return beyond the measured cases; every compressor/limiter mode; every project/restore mode; physical interrupt/ESAI timing and CPU headroom. Drum-message attempts and retained service/bypass execution do not prove those subsystems' audible operation. None of these is silently promoted to a passing full-feature hardware regression.

The qualified result is limited to this offline experiment and its exercised allocation/paths. No new DSP data-memory ownership, hardware recovery guarantee, firmware-image readiness or Plaits implementation is claimed. No firmware was generated or flashed, and no reference files were modified.

QUALIFIED PLAITS SHARED-CODE P BUDGET = 1075 words
