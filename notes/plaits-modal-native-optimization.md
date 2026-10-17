> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Original Plaits Modal: DSP56300 native arithmetic optimization

**Decision: UNQUALIFIED for complete-engine realtime admission; numerical optimization passes the tested fidelity screen.** The best executed filter bank costs **77,697 modeled cycles / worst 32-sample block**, versus 762,600 previously: **9.815× faster**. MAIN max/RMS error is **3 / 0.329192831 int16 counts**; AUX is **2 / 0.281588880**. Four synchronized banks project to **310,788 cycles**, requiring both cores under the conditional 327,680-cycle aggregate allowance. That leaves only **8,446 cycles per core** with two voices on each, before missing engine work and retained jobs. A complete four-track deadline is not established.

The architecture studied is four Plaits tracks, mono by default; seven and ten simultaneous Modal voices represent the requested polyphony stress cases. **The old 1,075-P-word allocation is not applied as the new architecture's limit.** Stock-synth removal was not audited. No firmware image or hardware activity was produced, and no bootloader/recovery changes were made. Changes are confined to this report and the new standalone experiment directory.

## Evidence and scope

**PROVEN:** Four actual assembled DSP candidates execute the unchanged primary **4,096-block corpus**, 131,072 compared MAIN/AUX samples, **10,923 native 12-sample renders**. All four also execute the separate 4,096-block single-strike, fixed-control tail corpus. The native interpreter runs real assembled instructions; a separately evaluated host integer recurrence checks every mode's output samples and both persistent histories after every call. The original pinned floating-point oracle supplies a second, distinct numerical comparison.

The native work comprises the excitation SVF and all **24 resonant modes / 48 resonator histories**. Original control smoothing, coefficient derivation, excitation generation, limiter/postprocessing and the already-verified 12→32 wrapper remain host work. Their behavior is reused, not claimed as newly ported DSP code. MAIN/AUX statistics include the original host ChannelPostProcessor applied to the actual DSP filter output. No mode count, physical resonator topology, decay parameter or engine selection behavior is changed by the selected candidate.

Sources: resonator.h (local-only reference: `plaits/upstream/plaits/dsp/physical_modelling/resonator.h`; not distributed), `ResonatorSvf::Process`, especially the `hp`, `bp`, `lp`, `state_1`, `state_2` recurrence; [plaits-modal-numeric-timing.md](<plaits-modal-numeric-timing.md>); wide.cpp (local-only reference: `builds/phase21-modal-native/wide.cpp`; not distributed), `main`, `product`, `Bus`; postprocess.cpp (local-only reference: `builds/phase21-modal-numeric/postprocess.cpp`; not distributed), `main`; analysis.json (local-only reference: `builds/phase21-modal-native/analysis.json`; not distributed). Original source reconstruction in ranges.py (local-only reference: `builds/phase21-modal-native/ranges.py`; not distributed) matches every recorded resonator final history with **zero error**. Exciter reconstruction in storage_study.py (local-only reference: `builds/phase21-modal-native/storage_study.py`; not distributed) also matches with zero error, validating the observed range extraction against the recorded source states.

The pinned manifests verify **183 original source files** and **451 protected reference inputs** unchanged. Primary vectors retain SHA-256 `ed37638be905baae4b7b6655b03ab475e8cede8190d09f3a1acb1c47cc7809ca`. integrity.json (local-only reference: `builds/phase21-modal-native/integrity.json`; not distributed) records these checks and equality of B, D and the final instrumented D signal streams. Existing investigations and original corpus files were reused.

## 1. Profile established before optimization

The original worst executed path is three native renders × 25 filters: **369,825 instructions / 762,600 modeled cycles**. profile.py (local-only reference: `builds/phase21-modal-native/profile.py`; not distributed) reconstructs hits from the already-qualified fixed loops and addressed instruction-cycle map and asserts those exact totals. baseline-cost-profile.json (local-only reference: `builds/phase21-modal-native/baseline-cost-profile.json`; not distributed) includes every addressed instruction, hit count and classification. These are modeled DSP cycles, not Windows elapsed time.

| Exclusive opcode family | Instructions | Modeled cycles |
|---|---:|---:|
| Memory accesses | 185,475 | 543,225 |
| Normalization/shifting | 59,400 | 59,400 |
| Register reconstruction/copies | 45,450 | 46,200 |
| 56-bit add/subtract | 36,900 | 36,900 |
| Limb masking | 15,300 | 30,600 |
| Loop/control, including calls/returns | 9,300 | 28,275 |
| Native coefficient products | 18,000 | 18,000 |
| Saturation instructions | 0 | 0 |

The first five rows are the five largest contributors. Memory accounts for **71.233%**; the native products themselves account for **2.360%**. Generic scratch copying and limb reconstruction dominate, rather than multiplication throughput.

The following semantic groups overlap the opcode families; do not add them to that table:

| Requested semantic operation | Instructions | Cycles | Exact accounting boundary |
|---|---:|---:|---|
| Coefficient reconstruction | 2,775 | 6,000 | Existing coefficient staging/cache transfer; DSP coefficient derivation absent |
| History reconstruction | 17,700 | 36,900 | Persistent history loads, scratch unpacking, history copies into multiply operands |
| History writes | 9,600 | 19,800 | Scratch re-encoding and persistent stores |
| Output accumulation | 39,600 | 89,100 | Caller-side gain-product staging, sum unpack/add/repack; shared multiply helper counted separately |

All wide-product helper reconstruction/normalization is included in the exclusive families above, with exact PCs available. There was **no native 24-mode outer loop** in the old probe: host dispatch invoked the per-mode kernel. The measured native sample DO loops and call/return overhead are included. The new probe retains that dispatch boundary, so neither result hides a measured full-engine mode scheduler.

## 2. Native representation and multiply

**PROVEN over both corpora:** every supplied nonzero binary32 coefficient is represented **exactly**, using an **unsigned 24-bit mantissa M** and a small signed shift S:

`coefficient = M * 2^(-23-S)`.

For `frexp(f) = m * 2^E`, use `M = m * 2^24`, `S = 1-E`. The exercised shifts fit **−2…23**. No coefficient disappears. An unsigned mantissa is essential: its top bit normally is set, so a signed 24-bit multiply would interpret it incorrectly.

Canonical history encoding is `N = signed24(H) * 2^24 + unsigned24(L)`. Registers A/B retain 56-bit intermediates. The selected resonator uses **36 fractional bits**, excitation **26 fractional bits**. These are 48-bit containers with fewer meaningful occupied bits, not generic 48-bit coefficient multiplication.

For `N=H*2^24+L`, two native partial products form

`T = 2*H*M + floor(2*L*M / 2^24)`, then `product = shift(T,S)`.

Assembly uses explicit **MPYSU** for signed H × unsigned M, **MPYUU** for unsigned L × unsigned M, **ASR #24**, **ADD**, and signed **NORMF**. For S≥0 this equals the ideal floor product. For S<0, dropping the low partial remainder early loses at most `2^(-S)-1` integer units: at most **3 history LSBs** for the exercised exponent range. This is deliberate bounded truncation, not coefficient quantization. The separately evaluated host model includes it and agrees exactly with native execution.

Instruction semantics: dsp_ops_alu.inl (local-only reference: `emulator/upstream/dsp56300/source/dsp56kEmu/dsp_ops_alu.inl`; not distributed), `DSP::alu_mpysuuu` and `DSP::alu_rnd`; dsp_ops.inl (local-only reference: `emulator/upstream/dsp56300/source/dsp56kEmu/dsp_ops.inl`; not distributed), `DSP::op_Normf`; generate.py (local-only reference: `builds/phase21-modal-native/generate.py`; not distributed) and cached.asm (local-only reference: `builds/phase21-modal-native/cached.asm`; not distributed). The old generic four-part coefficient/history multiplication becomes **two partial products**; 9,000 native products replace 18,000 on the worst 25-filter path. No resonance/decay shortcut is used.

Candidate D caches g/r/h mantissas and shifts once per native mode call in N0/N1, N2/N3, N7/X1, and reuses g for its second multiplication. Histories and intermediate hp/bp live in registers; no generic arithmetic scratch buffers are accessed. This changes storage/access scheduling while retaining B's integer output bit for bit.

## 3. Range and precision evidence

**PROVEN for the complete primary corpus, not for arbitrary future controls:** ranges.json (local-only reference: `builds/phase21-modal-native/ranges.json`; not distributed) gives all observed intermediate extrema, reconstructed sample by sample in original binary32 order.

| Resonator quantity | Minimum | Maximum |
|---|---:|---:|
| g | 0.000000230434040 | 4.549587250 |
| r+g | 0.001708322 | 5.549587250 |
| h | 0.038097661 | 0.999999762 |
| gain | 0.000156938 | 0.249999970 |
| Filtered excitation input | −3.888347864 | 17.842651367 |
| (r+g) × s1 | −226.046539307 | 223.591552734 |
| input − (r+g) × s1 − s2 | −228.736907959 | 229.180206299 |
| hp | −62.553295135 | 42.092308044 |
| g × hp | −47.959217072 | 48.050022125 |
| bp | −42.702304840 | 40.523319244 |
| g × bp | −48.021030426 | 48.644168854 |
| lp | −39.111301422 | 48.656127930 |
| s1, including within-block values | −49.683238983 | 49.142974854 |
| s2, including within-block values | −49.144866943 | 49.215911865 |
| gain × bp, per-mode contribution | −10.488918304 | 10.127467155 |

Exciter evidence in storage-study.json (local-only reference: `builds/phase21-modal-native/storage-study.json`; not distributed):

| Excitation quantity | Minimum | Maximum |
|---|---:|---:|
| g | 0.000000217089365 | 4.549587250 |
| r+g | 0.666666925 | 5.978158951 |
| h | 0.035463315 | 0.999999881 |
| gain | 1 | 1 |
| Raw excitation | 0 | 521844.531250 |
| (r+g) × s1 | −27.422378540 | 27.121793747 |
| pre-hp | −26.040615082 | 521831.593750 |
| hp | −22.689355850 | 521831.281250 |
| g × hp | −4.201482773 | 4.561954021 |
| bp | −10.975918770 | 25.881628036 |
| g × bp | −4.118844032 | 3.218790531 |
| lp / filtered output | −3.888347864 | 17.842651367 |
| s1 | −10.987027168 | 25.881645203 |
| s2 | −3.888438225 | 17.842987061 |

Storage, arithmetic and output precision are distinct:

- Coefficients originate with at most 24 binary32 significand bits. Mantissa/exponent preserves all of them; the minimum necessary coefficient significand precision is **UNKNOWN**, because this experiment did not round coefficient mantissas. Coefficient storage is two DSP words but not 48 significant bits.
- Resonator histories need six magnitude bits plus sign over the observed range. F36 therefore occupies at most **43 signed bits** in a 48-bit container; pre-hp needs up to **45**. Excitation hp/input with F26 needs up to **46** occupied signed bits, even though its histories need only about **32**. This does not justify making every quantity a 47-bit significand.
- Actual split-word DSP precision sweeps give the output table below. **F30 is sufficient for the preferred 3/2-count screen over this corpus**, about **37 occupied signed history bits** at the observed peak; it is not a proof that 37 is the mathematical minimum. All formats still cost two storage words, so reducing F alone saves neither cycles nor P words.
- Arithmetic uses the 56-bit accumulator and fractional partial products. A/C's 24-bit stores plus their tested intermediate rounding/truncation are insufficient. Their failure does not prove that every possible 24-bit or block-floating formulation must fail.

| Resonator fractional bits | Storage LSB | MAIN max / RMS counts | AUX max / RMS counts |
|---:|---:|---:|---:|
| 26 | 2^-26 | 5 / 0.536352450 | 2 / 0.281588880 |
| 28 | 2^-28 | 4 / 0.362766352 | 2 / 0.281588880 |
| 30 | 2^-30 | 3 / 0.335619399 | 2 / 0.281588880 |
| 32 | 2^-32 | 3 / 0.330372696 | 2 / 0.281588880 |
| 34 | 2^-34 | 3 / 0.329227593 | 2 / 0.281588880 |
| 36 | 2^-36 | 3 / 0.329192831 | 2 / 0.281588880 |

Excitation is F26 in every row. F28 and F30 were also replayed on the separate full tail corpus: both retain MAIN/AUX max **1/1**. Output precision depends on feedback, cancellation and original postprocessing, so a raw `1/32768` tolerance cannot substitute for these end-to-end int16 measurements. Source binary32 state equality is not claimed: D's primary state error max/RMS is **0.005222457 / 0.000201912**, and tail **0.000021902 / 0.000002412**. Native state equality to the independent integer model is exact.

**Block-floating investigation:** storage_study.py (local-only reference: `builds/phase21-modal-native/storage_study.py`; not distributed) quantizes every original end-of-render history pair using a shared per-mode exponent and one guard bit, and separately one exponent across all 48 histories. Per-mode storage-only max/RMS error is **7.6294e−6 / 5.3535e−7** on the primary corpus, **1.1921e−7 / 2.4828e−8** on the tail. Shared-across-all-modes RMS is larger: **1.4483e−6 / 4.5291e−8**, respectively. Exponents change **62,181 / 23,676** times across the two corpora. Zero history pairs use an artificial exponent sentinel in the JSON; it is not a required 81-bit fractional implementation.

**STRONG INFERENCE:** dynamic scaling could preserve substantially more tail detail than a fixed global 24-bit grid. **UNKNOWN:** recursive fidelity, causal exponent selection that prevents within-block overflow, native normalization/rescaling cost, and resulting MAIN/AUX errors. This storage-only experiment is explicitly not an implemented fifth DSP candidate or free lookahead. A native block-floating recurrence would have to be measured before claiming an improvement over D.

## 4. Independently executed candidates

A uses unsigned24 coefficient mantissa + exponent, fixed F14 signed24 resonator histories, wide excitation. B uses exact mantissa/exponent coefficients and canonical split-word F36 histories. C uses per-mode F14…F16 histories, with one headroom bit against all observed internal ranges; its 24 scales are in `scales.txt`. D combines native24 coefficients, split48 history containers, 56-bit arithmetic, register-resident intermediate data and per-call coefficient caching. D is the best **implemented** hybrid, not a claim of globally optimal instruction scheduling.

| Candidate | Resonator P / excitation P / body sum | Active history X / allocated X | Instructions/block min / mean / max | Cycles/block min / mean / max |
|---|---:|---:|---:|---:|
| A | 90 / 110 / 200 | 52 / 100 | 38,378 / 51,172.228 / 57,567 | 53,082 / 70,778.16 / 79,623 |
| B | 108 / 110 / 218 | 100 / 100 | 49,898 / 66,532.697 / 74,847 | 62,298 / 83,066.535 / 93,447 |
| C | 90 / 110 / 200 | 52 / 100 | 38,378 / 51,172.228 / 57,567 | 53,082 / 70,778.16 / 79,623 |
| D | 109 / 111 / 220 | 100 / 100 | 48,398 / 64,532.636 / 72,597 | 51,798 / 69,066.108 / 77,697 |

P sums count the two independently assembled bodies, shared across voices. They are **not a linked firmware module**, and exclude dispatch, caller-save and resource-generation code. All candidates use Y:24 output words and X:24 input words. A/C actively use 48 single-word resonator histories plus four excitation words: **52** active words; their exercised four-word-stride records still allocate **100** words including padding. B/D use **100** active history words: 96 resonator + four excitation. Coefficient residency for 25 filters would add **200 X words per voice** (25 × four mantissa/shift pairs), distinct from histories. The isolated probe stages eight coefficient words at a time.

| Candidate | Primary MAIN max / RMS | Primary AUX max / RMS | Tail MAIN max / RMS | Tail AUX max / RMS | Unintended zero coefficients |
|---|---:|---:|---:|---:|---:|
| A | 776 / 36.799969495 | 2 / 0.281588880 | 5177 / 1234.219038530 | 1 / 0.004784160 | 0 |
| B | 3 / 0.329192831 | 2 / 0.281588880 | 1 / 0.241588220 | 1 / 0.004784160 | 0 |
| C | 517 / 44.415472610 | 2 / 0.281588880 | 4393 / 1051.300405143 | 1 / 0.004784160 | 0 |
| D | 3 / 0.329192831 | 2 / 0.281588880 | 1 / 0.241588220 | 1 / 0.004784160 | 0 |

**PROVEN:** B/D pass the preferred fidelity screen on both corpora. A/C fail, especially on long tails; no subjective listening criterion is used. Keeping all coefficients nonzero alone does not qualify A/C. D retains all 24 native mode invocations and 48 histories; none is pruned. Tail claims are limited to the measured approximately 2.73-second horizon, not infinite duration or every possible patch.

The `coefficient_updates`/`cache_hits` counts in verification JSON describe host-observed coefficient-bit changes. They do not mean DSP coefficient derivation was measured or that D skips whole calls when controls settle. D's cache means six coefficient fields loaded into registers once per call, rather than per sample; all native filter costs remain constant at the measured path.

Evidence: generate.py (local-only reference: `builds/phase21-modal-native/generate.py`; not distributed), run.py (local-only reference: `builds/phase21-modal-native/run.py`; not distributed), tail.py (local-only reference: `builds/phase21-modal-native/tail.py`; not distributed), qualify.py (local-only reference: `builds/phase21-modal-native/qualify.py`; not distributed), blocks.csv (local-only reference: `builds/phase21-modal-native/blocks.csv`; not distributed), each candidate's `verification.json`, `native.csv`, `postprocess.json`, and tail equivalents in phase21-modal-native (local-only reference: `builds/phase21-modal-native`; not distributed).

## 5. Ownership, assembly layout and execution checks

These addresses belong only to a denied-peripheral standalone interpreter. **No ownership in retained Circuit firmware or in the future four-track map is established.**

| Isolated area | Exact addresses | Use / evidence |
|---|---|---|
| Resonator X histories | $0020–$007F | 24 × four-word records, `base = $20 + 4*mode`; s1 high/low at +0/+1, s2 at +2/+3 |
| Exciter X histories, separate invocation/process | $0020–$0023 | Two split histories; overlaps isolated resonator base because probes are separate |
| Coefficient staging X | $0190–$0197 | g, r+g, h, gain mantissa/shift |
| Narrow-only scale metadata X | $0198–$0199 | A/C input/output alignment shifts |
| Input X | $0200–$0217 | Twelve canonical paired samples |
| Output Y | $0300–$0317 | Twelve paired accumulated samples |
| A/C resonator P | $0200–$0259 | 90 words each |
| B resonator P | $0200–$026B | 108 words |
| D resonator P | $0200–$026C | 109 words |
| A/B/C excitation P, separate probe | $0200–$026D | 110 words |
| D excitation P, separate probe | $0200–$026E | 111 words |

Temporary hp/bp, products and additions are held in A/B and R6/N6; there is **no memory arithmetic scratch arena** in D. Caller-preservation workspace remains unallocated and unmeasured, rather than borrowing a live buffer. Mutable P writes: **zero**.

Final D primary replay: **262,152 exact mode checks**, **524,304 history comparisons**, **21,496,464 data reads**, **7,340,256 data writes**. Reads are denied outside declared X/Y windows; writes are denied outside X histories or Y output. Canary addresses X:$001F/$0080, $018F/$019A, $01FF/$0218 and Y:$02FF/$0318 are checked after every mode call. All remain intact. There are zero permitted accesses to shared/external RAM, hardware or retained image buffers. Opcode reads include the explicit zero end/prefetch sentinels; execution outside an instruction boundary fails closed. Tail replay repeats all mode/state checks with one initialization rather than the primary corpus's two.

The native probe assumes SR=$300 and linear M0…M7=$FFFFFF. Its body modifies A/B, X0/X1/Y0/Y1, R0…R7, N0…N7, SR and DO-loop state; it does **not** establish a retained caller ABI or charge saves/restores. Core-1's R5/M5 gather contract therefore needs an explicit wrapper or register reassignment. M registers are initialized by the harness, not newly qualified against a running caller. This is a numerical/timing kernel experiment, not a coupled retained-audio regression or native ARM control integration.

Evidence: wide.cpp (local-only reference: `builds/phase21-modal-native/wide.cpp`; not distributed), `Bus::read`, `Bus::write`, `before`, `main`; verification.json (local-only reference: `builds/phase21-modal-native/D-final/verification.json`; not distributed) and verification.json (local-only reference: `builds/phase21-modal-native/D-tail-final/verification.json`; not distributed); build_native.py (local-only reference: `builds/phase21-modal-native/build_native.py`; not distributed) and `build-provenance.json` for compiler, library hashes and denied-peripheral instrumentation. No stock image is loaded.

## 6. Physical thresholds and new four-track architecture

**STRONG INFERENCE under a conditional clock model:** [plaits-cycle-audit.md](<plaits-cycle-audit.md>) derives 163,840 clocks per 32 samples per core from 246 MHz / 48046.875 Hz. The physical clock assumption remains unverified. At nominal 48 kHz it would be 164,000. Modeled opcode costs omit hardware bus waits and retained task scheduling.

| Simultaneous Modal voices | Arrangement | Maximum cycles/voice on one core | Both cores: integer split, maximum/voice | Measured D projected total / busiest core |
|---:|---|---:|---:|---:|
| 1 | One Modal | 163,840 | 1+0: 163,840 | 77,697 / 77,697 |
| 4 | Four mono tracks | 40,960 | 2+2: 81,920 | 310,788 / 155,394 |
| 7 | One poly4 + three mono | 23,405.714 | 4+3: 40,960 | 543,879 / 310,788 |
| 10 | Two poly4 + two mono | 16,384 | 5+5: 32,768 | 776,970 / 388,485 |

These are zero-other-work thresholds; actual allowances must subtract retained workload, full engine work, wrappers and transport. Seven voices cannot use the more optimistic aggregate `327680/7` as a per-voice bound if voices stay on one core: the 4-voice core is the deadline bottleneck. Costs assume all voices encounter the measured three-native-render worst block together, not a pooled mean.

The old mean baseline of 73,435.634 cycles includes stock Synth1/Synth2, which the new architecture will remove. **It is not subtracted here as if it were the final retained baseline.** No invented saving is credited for their removal. New retained drums/FX/mixer and core-1 worst-block costs are **UNKNOWN**, pending the separately requested future removal/scheduling study.

For the current bank alone, at most **two voices/core, four total** pass the raw screen. Four mono Modal tracks therefore require core1; seven or ten Modal voices fail even before other work. There is no evidence here for enabling Modal poly4 while three other Modal mono tracks remain active. Polyphony policies involving cheaper other models require those models' measured costs.

## 7. Core-1 reconsideration using D only

The selected optimized bank, not the old 762,600-cycle prototype, underlies all projections above. **STRONG INFERENCE:** independent voices can be assigned two per core with independent X states; the 109-word resonator body plus 111-word excitation body can be installed on each core if program ownership is separately established. Code is shared by voices **within each core**. Executing on two private P spaces requires a code copy on each: nominal body sum **440 P words across both cores**, before scheduler/ABI code. No new P or X ownership is claimed.

**PROVEN from reference source:** granular_dsp.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/granular_dsp.py`; not distributed), `core1_code`, documents stock P:$10E–$12A, the R5/M5 gather pointer, and short cooperative tasks to maintain core-0 read service. Shared GB=$37000, CNT=GB, input MIN=GB+$100, granular OUT=GB+$140, glitch GOUT=GB+$1C0 already serve retained work. The glitch ring is external **$340000–$37FFFF**. These buffers are not available merely because this arithmetic probe does not touch them. Its documented core-0 consumer at block k uses core-1 output for c=k−2: **two blocks of latency** in the demonstrated reference path.

A D per-mode task is **967 instructions / 1,035 modeled cycles** per native render; excitation is **991 / 1,059**. Such mode boundaries make histories explicit and offer task-yield points, but they do not prove gather-service latency or sufficient slack under granular/glitch/FX load. Two complete banks per core consume **155,394 cycles** on a worst block, leaving 8,446 cycles for everything missing. Context switching many small tasks consumes some of that margin.

One concrete **unimplemented** diagnostic packet design offloads an entire filter bank while leaving coefficient/excitation generation and original output postprocessing on core0:

- Four header words, 200 mantissa/shift coefficient words (25 filters × 8), and 24 paired raw-excitation words: **228 input words/native render**.
- Paired MAIN and AUX outputs: 48 words plus completion tag, **49 return words**.
- Total **277 shared words/native render/remote voice**; two remote voices × three renders require **1,662 words worst block**, before synchronization reads and task overhead. With coefficients already resident and unchanged, payload would be **77 words**, or 462 for that block.
- Double-buffering three native packets for each of two remote voices would require **3,324 shared words**, plus histories, resident coefficients and metadata. No free range for these packets has been qualified. No external SDRAM is inherently needed for the 100-word history bank; retained rings must not be reused.

**UNKNOWN:** physical bus time, safe new shared allocations, scheduler worst case, full engine distribution and deterministic end-to-end latency. A one-block mailbox pipeline might be designed, but is not required by the arithmetic and is not proven by the existing two-block implementation. Following the demonstrated scheduling pattern would add **two Circuit blocks**; that timing change requires an explicit product decision and sample-sequence qualification. Moving coefficient generation to core1 might reduce packet size, but adds unmeasured native work. Retained granular, capture/glitch and stock read service can conflict with the proposed jobs; no idle-loop count is used as spare CPU evidence.

## 8. Decision and remaining experiment

| Proposed capability | Confidence | Conclusion |
|---|---|---|
| Four-track mono Modal | STRONG INFERENCE | Numerically plausible with D and both cores at filter-only level; very tight remaining margin; full admission UNKNOWN |
| Restricted polyphony | UNKNOWN | Raw limit four concurrent Modal banks across both cores; no extra Modal voices above four-mono baseline are admitted |
| Mono heavy engine | STRONG INFERENCE | One bank costs 77,697 cycles and passes a single-core raw screen; complete engine plus retained deadline remains unqualified |
| Not realtime-feasible on this hardware | UNKNOWN | Not established universally; selected seven-/ten-Modal cases fail the conditional screen, but one/four-bank screens improve materially |

**PROVEN:** the previous arithmetic bottleneck was mostly generic data movement. Exact original coefficient storage, two-part native products and register-resident state/intermediates achieve a **9.815×** worst-path speedup without mode reduction. Preferred int16 fidelity and tested tail behavior survive. Fixed 24-bit A/C recurrences are rejected quantitatively. The F30 sweep demonstrates that source-wide precision was excessive without saving native storage words.

**UNKNOWN / largest blocker:** complete per-voice native cost and retained per-core deadline headroom. The four-track screen has only 8,446 cycles/core left, and coefficient derivation, excitation generation, output processing, caller saves, mailbox work and retained drums/FX/core1 jobs are absent. This report therefore does not authorize the rest of ModalEngine implementation or a full stock-synth removal audit.

The next smallest arithmetic experiment is instruction scheduling of the same D kernel with native parallel transfers/MAC opportunities, keeping these exact vectors and tail test. Its present largest remaining opcode family is register copying: **34,572 instructions / 34,872 cycles** on the worst bank, followed by memory **8,250 / 12,750**, add/sub/negate **11,700 / 11,700**, native products **9,000 / 9,000**, shifts **9,000 / 9,000**, control **75 / 375**. A useful further saving must survive the same independent model and cannot be assumed from peak MAC throughput. This is a proposed experiment only.

## Compact result

| Measure | Result |
|---|---|
| Best implemented representation | D: unsigned24 coefficient mantissa + signed shift; split48 F36 resonator / F26 excitation; 56-bit intermediates |
| P words | **109 resonator + 111 excitation = 220 isolated body words**; linking/ABI overhead unknown |
| State words/voice | **100 X history words**; plus up to 200 resident coefficient words and X24/Y24 sample buffers; caller workspace unknown |
| MAIN max/RMS | **3 / 0.329192831 counts** |
| AUX max/RMS | **2 / 0.281588880 counts** |
| One-voice worst cycles/block | **77,697**, measured filter-only |
| Four-mono worst cycles/block | **310,788**, projected synchronized filter-only sum |
| Maximum plausible Modal polyphony | **Four simultaneous banks raw across two cores; full-engine limit UNKNOWN; no extra poly voices admitted above four Modal mono tracks** |
| Core1 required? | **Yes for the four-mono filter screen**; not required by one isolated bank |
| Largest blocker | Unmeasured full-engine + retained per-core worst-block headroom, with only 8,446 modeled cycles/core left in the four-bank screen |

Reproduction: run `profile.py`, `ranges.py`, `storage_study.py`, `generate.py`, `adapt.py`, `build_native.py`; run the fresh-directory candidate/qualification scripts; then `analyze.py` and `report.py`. Scripts fail on existing replay directories to preserve results. `run.py` expects the separately produced `exciter` replay as documented in its arguments; `tail.py` produces its own tail excitation. `qualify.py` produces the checked primary excitation. Final instrumented repetitions and F28/F30 tail sweeps use `qualify.check` with fresh names. The saved `*.log`, addressed `program-map.tsv`, native/block CSVs, verification JSON and build provenance are the execution witnesses, not standalone firmware payloads.

MODAL NATIVE OPTIMIZATION = UNQUALIFIED
