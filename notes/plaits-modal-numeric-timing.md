> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Modal two-word numerical and timing feasibility

2026-10-15. **UNQUALIFIED overall.** The tested two-word filter representation eliminates unintended zero coefficients and closely reproduces the original source over the supplied vectors. The executed implementation fails the existing **conditional** core-0 timing allowance by a large margin. Moving the unchanged work to core 1 cannot fix its aggregate throughput. This is a rejection of this implementation's cost, not a proof that every optimized faithful Modal resonator is impossible.

No remaining ModalEngine implementation was added. No firmware was generated or hardware accessed. Pinned Plaits and CIRCUITS-HACKS files remain unchanged. All new sources/results are under phase21-modal-numeric (local-only reference: `builds/phase21-modal-numeric`; not distributed). Integrity verification (local-only reference: `builds/phase21-modal-numeric/integrity.json`; not distributed) checks all 183 pinned files, 451 protected reference inputs, and exact equality of the original audit vectors. The existing [Modal-port report](<plaits-modal-dsp-port.md>) and Layout A qualification were retained.

## 1. What executed

**PROVEN:** generate.py (local-only reference: `builds/phase21-modal-numeric/generate.py`; not distributed) emits the original un-factored SVF recurrence, with all **24 modes and 48 resonator histories**. wide.cpp (local-only reference: `builds/phase21-modal-numeric/wide.cpp`; not distributed) executes native DSP56300 opcodes, compares every mode's state and output against a separate host integer model, checks canaries, rejects undeclared writes, and counts actual instruction fetches and modeled opcode cycles. The native build uses the installed reference interpreter libraries with a local memory observation adapter and denied peripheral adapter; build_native.py (local-only reference: `builds/phase21-modal-numeric/build_native.py`; not distributed) changes neither checkout. Execution explicitly uses `execInterpreter`.

The program is **496 assembled P words**, executing at isolated analysis origin P:`$200`, ending exclusively at `$3F0`. Addressed opcode/cycle map (local-only reference: `builds/phase21-modal-numeric/program-map.tsv`; not distributed). This is not an integrated Circuit allocation or a complete-engine P charge. BP and LP tests assemble separate variants differing in the selected filter output; integrating both in one shared callable renderer remains outside this numeric experiment.

There are three useful scopes:

1. Resonator: original filtered excitation and original coefficients supplied to the DSP; all 24 modes execute there.
2. Excitation SVF: original **unfiltered** impulse/dust samples and original coefficients supplied to the DSP; original LOW_PASS output executes there.
3. Cascade: DSP excitation output is passed as exact fixed-point integers into the DSP resonator. Original host Voice output processing then permits comparison of final MAIN and AUX int16 samples.

Coefficient derivation, impulse/dust generation, Voice control/envelope processing and MAIN/AUX postprocessing were **not** ported to DSP. Their native DSP costs are not hidden inside a filter-only timing number. This follows the instruction not to implement the rest of ModalEngine yet.

## 2. Exact two-word formats and arithmetic

**PROVEN in the executed implementation:** a signed integer `N` is encoded as:

`N = signed24(high) * 2^23 + low`, with `0 <= low <= 0x7FFFFF`.

The high word is signed 24-bit; the low word's bit 23 is always clear. This gives **47 significant signed bits in two 24-bit storage words**. It makes every limb compatible with the already-qualified signed native `mpy y0,x0,a`, avoiding an unqualified mixed-sign multiplier interpretation.

| Quantity | Representation | Real range / resolution |
|---|---|---|
| `g`, `r+g`, `h`, gain | Q4.43, 47-bit signed | `-8, 8)`, LSB `2^-43` |
| Resonator histories and signals | Q11.36, 47-bit signed | `[-1024, 1024)`, LSB `2^-36` |
| Excitation SVF histories/signals, including raw impulse | Q21.26, 47-bit signed | `[-1048576, 1048576)`, LSB `2^-26` |
| Excitation→resonator transfer | Exact integer left shift by 10 | No float conversion at the DSP-filter boundary |
| Accumulator | Native signed 56-bit, preserving its low portion | Products/carries added before explicit repacking |

Q integer-width notation includes the sign. High/low encoding is identical for coefficients and histories; only the binary-point position differs. The Q11.36 range covers the intermediate `r+g` product before cancellation, which rejected the earlier one-word implementation. Q21.26 admits the measured **521844.53125** excitation impulse.

Four signed 24×24 native products implement a coefficient×signal multiplication. Let `B=2^23`, operands `a=ah*B+al`, `b=bh*B+bl`:

`T = floor(al*bl/B) + ah*bl + al*bh`

`floor(a*b/2^43) = ((ah*bh + floor(T/B))*8) + floor((T mod B)/2^20)`.

The DSP's fractional MPY result is arithmetic-shifted once to obtain the integer product. Cross terms remain in 56-bit accumulators; full-accumulator copies use **TFR**, not the narrowing register MOVE form. The latter was caught by the independent integer check during development and corrected before the passing replay. Final high/low splitting uses an arithmetic shift and low-word mask.

Host vector-to-integer conversion uses `llround`, nearest with halfway cases away from zero. DSP multiplication truncates toward negative infinity; addition/subtraction is exact at the current fixed scale, followed by checked representation packing. There is no intentional saturation, dynamic block exponent, denormal emulation, clipping of coefficients, or mode-count reduction. Accumulator and signal ranges are admitted only for the tested inputs; this is not an all-input proof.

The final recurrence is upstream [ResonatorSvf::Process (local-only reference: `plaits/upstream/plaits/dsp/physical_modelling/resonator.h`; not distributed): `hp=(in-(r+g)*s1-s2)*h`, `bp=g*hp+s1`, `s1=g*hp+bp`, `lp=g*bp+s2`, `s2=g*bp+lp`. Reusing the identical `g*hp` / `g*bp` product does not remove behavior. Original floating-point rounding is not reproduced bit for bit; the fixed integer model is bit-exact to the DSP on the exercised vectors.

Synthetic ownership: X:`$20–$7F` holds 96 history words, X:`$100–$121` holds 34 dedicated working words, X:`$170–$172` holds three carry/unpack temporaries, X:`$190–$197` holds coefficient input, X:`$200–$217` holds 12 paired input samples, X:`$500–$5BF` holds 24 paired coefficient records, and Y:`$300–$317` holds 12 paired output samples. The DSP writes only declared history, working, coefficient-cache and output ranges. Canaries flank history, working, carry, cache and output allocations; input/coefficient-staging writes by DSP are rejected. These addresses establish **no** ownership in retained Circuit memory.

One resonator's 48 persistent histories consume 96 words; its excitation filter adds four. Two instances need **200 history words**. Independent cached coefficients need another **400 words** for two complete 25-filter banks if all four paired coefficients are retained. Code, constants and serialized temporary scratch can be shared; histories and per-instance cache validity cannot. No final Circuit address allocation is claimed.

## 3. Oracle results and long tails

**PROVEN:** the original 4096-block control sequence and `resonator-vectors.f32` are unchanged byte for byte. The observational host build reproduces the previous original MAIN/AUX bytes exactly. Plaits commit `08460a69a7e1f7a81c5a2abcc7189c9a6b7208d4`, stmlib commit `e3bd7c9cc00e4364166f9905c0509b6ffd0535ec` remain pinned.

excitation_vectors.py (local-only reference: `builds/phase21-modal-numeric/excitation_vectors.py`; not distributed) adds observations around the **original** excitation SVF without modifying its arithmetic expressions or pinned files. The replay covers the same low/high notes, smallest coefficients, impulse peak, dust excitation, rapid retrigger, harmonics/timbre/morph sweeps, ringing intervals and original reset events. The native-12 FIFO schedule stays **3,3,2** per Circuit call, with **4,8,0** pending frames. The 10923 native calls generate 131076 samples, including four final lookahead samples.

**PROVEN:** the combined replay (local-only reference: `builds/phase21-modal-numeric/combined-q36/verification.json`; not distributed) performs **262152 exact mode-state/output checks** across 10923 native renders. The excitation replay (local-only reference: `builds/phase21-modal-numeric/exciter-replay/verification.json`; not distributed) performs 10923 exact filter checks. Canaries pass; no undeclared data writes or P writes occur. The original impulse peak is represented and processed without a range rejection.

**COEFFICIENTS QUANTIZED TO ZERO = 0**

The original audit filter bank checks 1092300 coefficient values in total. Maximum coefficient error is **5.6843418860808015e-14**, with no unintended zero coefficient. The additional steady-tail test also has zero unintended zero coefficients.

Final output comparison uses the **actual pinned host ChannelPostProcessor**, not a rewritten approximation. postprocess.cpp (local-only reference: `builds/phase21-modal-numeric/postprocess.cpp`; not distributed), MAIN/AUX result (local-only reference: `builds/phase21-modal-numeric/main-aux.json`; not distributed), **131072 compared samples per channel**:

| Channel | Maximum absolute error, int16 counts | RMS error | DC error | First divergence, zero-based sample |
|---|---:|---:|---:|---:|
| MAIN | 3 | .330822708638 | .0182876586914 | 694 |
| AUX | 2 | .280448619577 | .0751876831055 | 154 |

These numbers qualify the stated **DSP-filter/original-host-control-and-postprocessing hybrid**, not a complete Modal DSP port. They do not establish perceptual equivalence or a universal error bound. The strongest passing exact criterion is DSP versus its independently computed integer recurrence; original float output is close but not exact. Whether this bounded deviation is the final project's accepted fidelity remains **UNKNOWN**.

Internal comparisons, including native lookahead:

| Comparison | Maximum absolute error | RMS error | Scope |
|---|---:|---:|---|
| Direct Q11.36 resonator versus original float | .001880645752 | .000233478955 | Original filtered excitation |
| Cascaded DSP filters, resonator histories | .005228414724 | .000201870861 | 524304 history observations |
| Excitation SVF output versus original float | .000047683716 | .000007973831 | Includes largest impulse |
| Excitation SVF histories | .000089496374 | .000008203888 | Two histories, 21846 observations |

The preliminary two-word Q21.26 resonator test is retained in `replay2`: zeroed coefficients also vanish there, but its maximum raw output error is .001926422119. Increasing resonator history precision to Q11.36 gives only a modest further reduction against float32, consistent with differences in repeated floating-point versus fixed-point rounding. No bit-exact original-float claim follows.

**PROVEN for the tested horizon:** steady_fixture.py (local-only reference: `builds/phase21-modal-numeric/steady_fixture.py`; not distributed) adds a second **4096-block** original-source fixture: fixed note 48, harmonics .5, timbre .3, morph .999, one strike, no reset at block 2048, no subsequent excitation, and zero modulation amounts. It retains all 24 modes. Tail verification (local-only reference: `builds/phase21-modal-numeric/tail-q36/verification.json`; not distributed) has maximum raw audio error **9.4547868e-6**, maximum history error **2.1304266e-5**, and no integer-model/canary failure over approximately 2.73 nominal seconds.

The original output RMS falls from **.2698501060** in samples 4096–12287 to **.1528555572** in samples 122880–131071; DSP RMS is **.2698503215 → .1528564911**. The corresponding decay-ratio error is **3.0086657e-6**. This is a measured two-window decay comparison, not a fitted T60 or an infinite-duration stability proof. The tail remains active rather than being discarded.

## 4. What may legally run at control rate

**PROVEN from original source:** ModalEngine::Render (local-only reference: `plaits/upstream/plaits/dsp/engine/modal_engine.cc`; not distributed) updates `harmonics_lp_` every native render. Voice::Render (local-only reference: `plaits/upstream/plaits/dsp/voice.cc`; not distributed) advances delayed trigger state, note smoothing and decay modulation every native call. Unchanged MIDI/knob values therefore do **not** imply unchanged effective Modal coefficients.

| Rate | Original work and legal caching condition |
|---|---|
| Per sample | Dust RNG where enabled; excitation/filter histories; all 24 resonator recurrences; output accumulation; MAIN limiter after the renderer. These cannot simply run at MIDI control rate. |
| Per native 12-sample render | Harmonics LP, Voice note/trigger/envelope processing, excitation setup, resonator structure/Q/frequency derivation, and coefficients for the whole native call. |
| Only when exact effective inputs change | Pure coefficient calculations and immutable lookups may be cached if their **effective** frequency/structure/brightness/damping inputs are bit-identical, including evolving harmonics LP and internal modulation. Initialization/reset must invalidate the appropriate cache. |
| Shared immutable | Original mode amplitudes, lookup tables and constants; sharing these does not share history updates or audio computation. |

The implemented cache skips coefficient **staging/copy** only when all four original coefficient bit patterns for that mode match the previous native call. It then executes the same recurrence and state evolution. A complete DSP coefficient-derivation cache is **not** implemented; original derivation still runs in the host oracle. No saving from omitted DSP divisions/tangents/lookups is claimed.

**PROVEN:** forced-refresh and cached DSP cascade replays have identical fixed output integers and history-error records for all 4096 audit blocks: `combined-no-cache` versus `combined-q36`. The audit yields 7776 resonator cache hits and 4952 excitation-filter hits. The added steady fixture yields 234518 resonator hits; 3626 Circuit blocks have no coefficient changes in any of the 25 filters.

A copy-cache hit saves **19 instructions / 25 modeled cycles per mode/native call**. Even a completely unchanged 25-filter native call saves only **475 instructions / 625 cycles**. This optimization is valid for the measured numeric representation but does not address the dominant multiply/unpack cost. Raw hardware mailbox values alone are not a valid future coefficient-cache key.

## 5. Measured timing and breakdown

**PROVEN within the interpreter model:** instruction fetches are observed, including hardware-loop bodies and multiply subroutine calls. Opcode cycles use the installed interpreter's `calcOpcodeCycles`; program-map.tsv (local-only reference: `builds/phase21-modal-numeric/program-map.tsv`; not distributed) records weights. No wall-clock runtime is used as a DSP cycle count. External/shared transfer penalties and physical clock validation are outside this isolated model.

One mode over a native 12-sample call costs **4912–4931 instructions / 10143–10168 cycles**, depending on coefficient staging. All 24 resonator modes cost **117888–118344 instructions / 243432–244032 cycles per native render**. The excitation SVF costs one more mode-equivalent call. The 32-sample FIFO consumes two or three native renders; it is not approximated as 32/12 for the worst block.

| One 25-filter bank, per Circuit block | Instructions min / mean / max | Modeled cycles min / mean / max |
|---|---|---|
| A: unchanged coefficients after steady-fixture settling, 3626 blocks | 245600 / 327455.378 / 368400 | 507150 / 676176.689 / 760725 |
| B: at least one effective coefficient changes, 4096 audit blocks | 246056 / 328684.324 / 369825 | 507750 / 677809.668 / 762600 |
| C: actual patched-trigger impulse, 288 audit blocks | 246208 / 328701.007 / 369825 | 507950 / 677824.132 / 762600 |

B and C overlap: a retrigger can coincide with changed effective parameters. Trigger classification observes the original unfiltered patched impulse, not an assumed undelayed host event. The filter inner loop itself has no trigger-specific shortcut. Original trigger/impulse generation cost is excluded, not declared zero.

The following is an **additive 25-filter-bank** breakdown from measured fetch totals and fixed executed loop counts. Repacking has been separated from recurrence/history/output arithmetic; subroutine returns stay with multiplication. A pack executes five instructions / ten modeled cycles, checked against the addressed opcode map.

| Component | Instructions/block min / mean / max | Modeled cycles/block min / mean / max |
|---|---|---|
| setup | 700 / 933.362 / 1,050 | 2,200 / 2,933.423 / 3,300 |
| coefficient_update | 1,356 / 2,407.701 / 2,775 | 3,350 / 5,255.811 / 6,000 |
| excitation_input | 2,400 / 3,200.098 / 3,600 | 4,800 / 6,400.195 / 7,200 |
| recurrence | 69,600 / 92,802.832 / 104,400 | 170,400 / 227,206.934 / 255,600 |
| history_update | 19,600 / 26,134.131 / 29,400 | 39,600 / 52,801.611 / 59,400 |
| output_accumulation | 23,400 / 31,200.952 / 35,100 | 53,400 / 71,202.173 / 80,100 |
| multiplication | 93,000 / 124,003.784 / 139,500 | 162,000 / 216,006.592 / 243,000 |
| normalization | 36,000 / 48,001.465 / 54,000 | 72,000 / 96,002.930 / 108,000 |

`coefficient_update` means input staging and loading only. Original coefficient **recalculation** cost on DSP is **UNKNOWN**. `excitation_input` means reading supplied excitation samples; the full excitation SVF's total cost is already included across the 25 filters, while generating the impulse/dust remains host work. MAIN limiter and AUX conversion are also absent from these DSP totals. Thus **762600 is filter-only worst cost, not a complete ModalEngine upper bound**.

## 6. Two instances, retained baseline and headroom

**PROVEN:** the existing Layout A PC histogram (local-only reference: `builds/phase20l-master-path/long-layout-A/pc0.txt`; not distributed) covers 18476 audited complete audio calls: 8192 main calls plus 10284 ARM-readback service calls. profile.cpp (local-only reference: `builds/phase21-modal-numeric/profile.cpp`; not distributed) weights those executed addresses using the actual retained code and explicit `$7000` call stub. It does not rerun the completed qualification.

Baseline profile (local-only reference: `builds/phase21-modal-numeric/baseline-profile.json`; not distributed): **1136694301 instructions / 1356796779 modeled cycles**, mean **61522.748 instructions / 73435.634 cycles per audited audio call**. Pre-AUDIT boot is excluded. The original 8192 main-call instruction witnesses have min/mean/max **56569 / 61533.653 / 91017**. An exact **per-main-block cycle distribution** was not retained; its maximum is **UNKNOWN**. A mean must not be substituted for a deadline bound.

**STRONG INFERENCE, conditional timing projections:** two independent filter states execute one shared code copy. There is no shared history arithmetic. Projections sum measured per-block paths with the actual 3,3,2 cadence aligned for simultaneous worst cases; they do not double a pooled average and call it a worst case. No cross-instance coefficient-generation saving is assumed. Immutable code/tables are shared, but different pitches/controls still require their own coefficient/state work. The settled track in the mixed case uses the measured zero-update path.

| Two-instance scenario, excluding retained baseline and missing engine work | Instructions min / mean / max | Modeled cycles min / mean / max |
|---|---|---|
| two_steady | 491,200 / 654,910.756 / 736,800 | 1,014,300 / 1,352,353.378 / 1,521,450 |
| two_trigger | 492,416 / 657,402.014 / 739,650 | 1,015,900 / 1,355,648.264 / 1,525,200 |
| two_parameter_change | 492,112 / 657,368.649 / 739,650 | 1,015,500 / 1,355,619.336 / 1,525,200 |
| one_changing_one_steady | 491,656 / 656,160.985 / 738,225 | 1,014,900 / 1,354,030.304 / 1,523,325 |

These are arithmetic projections of isolated measured paths, not a real dual-state Circuit integration test. Sharing an occasional identical coefficient cache across tracks would save only staging work in this implementation; it cannot remove their separate recurrences. Neither private-X ownership nor a complete two-instance caller wrapper is qualified here.

The pre-existing [clock/timing audit](<plaits-cycle-audit.md>) derives a **conditional 246 MHz / 48046.875 Hz** allowance of **163840 clocks per 32-sample block**. The physical oscillator/routing is unverified. At nominal 48 kHz the corresponding allowance is 164000; this difference does not rescue the measured implementation.

- One filter bank worst: **762600 cycles**, already **598760 over** the conditional whole-core allowance before any retained baseline.
- Two filter banks worst: **1525200 cycles**. Remaining core-0 headroom is at most **−1361360 cycles**, even assuming retained work costs zero. Actual retained work makes this worse.
- As a descriptive mean-workload projection only, adding the measured baseline mean to two audit-bank means gives **1429054.970 cycles/block**. This is not a worst-case deadline claim.
- Exact retained worst-block headroom for a future optimized kernel remains **UNKNOWN**. Complete coefficient generation, Voice work, transport, memory waits and caller saves would add cost, not create headroom.

The measured implementation therefore cannot be admitted for two real-time instances under this conditional clock model. This is not an architecture-independent lower bound: the prototype spends heavily on generic two-word unpack/repack and calls. It does not prove that a much more efficient faithful representation cannot work.

## 7. Concrete core-1 scheduling option and its rejection for this kernel

**PROVEN from reference source:** granular_dsp.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/granular_dsp.py`; not distributed), `core1_code`, uses:

- Shared `GB=$37000`, `CNT=GB`, task state `GB+6`, input `MIN=GB+$100`, ping-pong voice outputs `OUT=GB+$140`, glitch outputs `GOUT=GB+$1C0`.
- Stock core-1 P:`$10E–$12A`, preserving the gather-loop R5/M5 contract; work is divided into short tasks so core-0 read service continues.
- External glitch ring `RL=$340000`, `RN=$20000`, stereo extent `$340000–$37FFFF`; granular/glitch states and shadow control blocks already occupy shared allocations.
- Core 0 consumes in block `k` what core 1 produced for `c=k−2`: the documented path has **two Circuit blocks of latency**.

The [coupled runner](<../plaits/poc/authentic_qualification/coupled.cpp>), `replayAccess/replayFetch`, demonstrates the modeled common shared address space and the stock R5/M5 task-boundary contract. This does not grant new packet/state ownership or establish physical bus latency. The present arithmetic probe uses R5 for a coefficient pointer; a core-1 implementation must rename or preserve it before joining that stock scheduler.

A concrete **unimplemented** split to evaluate is:

1. Core 0 keeps original Voice controls, excitation generation/filter and MAIN/AUX postprocessing.
2. Each original native-12 render publishes filtered excitation and correctly timestamped resonator coefficients. Core 1 owns each track's 48 resonator histories.
3. Core 1 processes all 24 modes, using resumable sample/mode tasks interleaved with stock gather service and retained granular/glitch tasks; completed native outputs are tagged and consumed strictly in sequence.
4. A two-Circuit-block packet pipeline matches the existing scheduling pattern. The original 12-sample control cadence and output sample sequence can be preserved **after a fixed extra delay**, but that adds 64 samples relative to a core-0 renderer. It changes observable timing and is not automatically an acceptable transparent implementation.

An explicit full-update packet could contain four 24-bit header words (sequence, native sample origin, flags, dirty-mode mask), 24 excitation words (12 paired samples), and 192 coefficient words. Response: 24 MAIN words (12 paired samples) plus one completion tag. That is **220 input + 25 output = 245 shared words per native render per track**. Worst two-track/three-native-call block: **1470 bidirectional words**. With all coefficients resident and unchanged: **318 words**. Double-buffering three native packets for two tracks requires **2940 shared words**, plus state/control metadata; no free shared address range for that proposal was qualified. AUX remains on core 0 in this split.

Moving coefficient derivation too could replace the 192 coefficients with effective controls and reduce traffic, but would add the currently unmeasured derivation work on core 1. No external SDRAM is required merely for these histories, and the retained glitch ring must not be borrowed.

**STRONG INFERENCE under the same clock model:** offloading the unchanged resonator costs up to **732096 cycles per track/Circuit block**, before packet transfers or task-switch overhead. One such job exceeds a core's 163840-cycle period. Two cores together offer 327680 conditional cycles/block, while two complete measured filter banks require 1525200. Extra buffering can delay a deadline but cannot cure this sustained throughput deficit. The proposed split therefore has **no feasible real-time schedule for this implementation**, even with retained granular/glitch work assumed zero.

Retained granular/glitch scheduling and its maximum load are not newly qualified here. Adding that work, core-0 read service, context saves and bus waits only tightens the bound. Core 1 is **not a sufficient fix** for this kernel. Whether an optimized implementation requires core 1 remains **UNKNOWN**; no core-1 feasibility is claimed from unused address space or an idle-loop count.

## 8. Gates, decision and next experiment

| Gate | Confidence | Finding |
|---|---|---|
| N1 — eliminate unintended zero coefficients | PROVEN | **Yes**, zero remaining across the original vectors and added steady-tail test. |
| N2 — stable long tails | PROVEN | **Yes for the tested 4096-block horizons**, including the additional fixed-control, no-reset ringing test; no infinite-duration proof. |
| N3 — declared oracle fidelity acceptable | UNKNOWN | DSP/integer model exact; final hybrid MAIN/AUX within 3/2 int16 counts. Final project acceptance/perceptual equivalence is not established. |
| N4 — bounded complete resonator cost | UNKNOWN | Recurrence and excitation SVF costs measured and bounded; complete DSP coefficient derivation remains unimplemented/unmeasured. The partial measured cost alone already rejects this candidate under the conditional allowance. |
| N5 — two instances have core-0 headroom | STRONG INFERENCE | **No for this implementation under the documented conditional clock model**, before retained work. This is not a universal optimized-port impossibility proof. |
| N6 — a feasible concrete core-1 split exists | UNKNOWN | A packet/task model is explicit, but rejected for current throughput; extra latency and retained-feature scheduling also remain unresolved. |

The audit is complete as an evidence-based **UNQUALIFIED** feasibility decision. It establishes a workable numerical representation over the tested domain and rejects the measured implementation's cost. The rest of ModalEngine was not implemented or silently approximated.

**Single smallest next experiment:** optimize only the same state-pointer resonator kernel, keeping all 24 modes. Use a canonical accumulator-compatible two-word state layout and qualify a coefficient mantissa/exponent multiply using fewer native partial products; eliminate repeated generic unpack/repack where exact. Replay these unchanged vectors and the long-tail case, measure the same output/state errors and executed costs, and stop if the optimized numeric kernel still misses its timing screen. Do not start the rest of ModalEngine.

The baseline mean leaves an optimistic screening target of roughly **45202 cycles per track/block** for two tracks under 163840 total. This is **not qualified worst-case headroom**; any successful screen still needs retained per-block cycle maxima and missing engine costs. The current 762600-cycle filter path is far above it. A successful next experiment would justify measuring those remaining costs; this audit does not assume that speedup is achievable.

Reproduction sources: `generate.py`, `build_native.py`, `wide.cpp`, `excitation_vectors.py`, `steady_fixture.py`, `profile.cpp`, `postprocess.cpp`, and `analyze.py`, all in the experiment directory. analysis.json (local-only reference: `builds/phase21-modal-numeric/analysis.json`; not distributed) and blocks.csv (local-only reference: `builds/phase21-modal-numeric/blocks.csv`; not distributed) contain full statistics and classifications. Cached and forced-refresh replays are retained separately. Output directories must be fresh.

| Requested final measure | Result |
|---|---|
| Coefficient format | Two-word signed47 Q4.43, signed24 high + unsigned23 low |
| History format | Resonator Q11.36; excitation Q21.26, same paired encoding |
| Zeroed coefficients remaining | **0** |
| One-instance worst modeled cycles/block | **762600 filter-only**; complete engine unknown |
| Two-instance worst projected cycles/block | **1525200 filter-only**; complete engine unknown |
| Retained core-0 headroom | At most **−1361360** under the conditional allowance even before baseline; exact retained worst profile unknown |
| Core 1 required? | Unknown for an optimized design; moving this unchanged kernel is insufficient |
| Next smallest experiment | Optimize the paired-state recurrence/multiply representation and replay the same complete vectors; no rest-of-engine port |

MODAL NUMERIC/TIMING FEASIBILITY = UNQUALIFIED
