> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Pinned original Plaits ModalEngine DSP port experiment

2026-10-15. **UNQUALIFIED.** The complete DSP56300 ModalEngine/Voice port was **not completed**. This phase established the exact selected source closure, passed the original-source 12→32 scheduler, and assembled/executed a state-pointer resonator arithmetic probe. It did not establish complete-engine fit, qualified Circuit data allocations, MIDI/vpre integration, or two-instance operation. The 91-word probe is not a substitute engine and must not be described as a complete Modal port.

**PROVEN:** the pre-existing Layout A budget remains **1075 new P words**. Its previous [stock/master qualification](<stock-master-signal-path-qualification.md>) was not restarted or altered. No firmware container was generated, no hardware was accessed, and no pinned/reference sources were modified. The current reference verification (local-only reference: `builds/phase21-modal-plaits/reference-verification.json`; not distributed) matches all 451 protected reference inputs. The pinned verification (local-only reference: `builds/phase21-modal-plaits/pinned-verification.json`; not distributed) validates every file against the existing source manifest.

## 1. Exact target and closure

Plaits commit `08460a69a7e1f7a81c5a2abcc7189c9a6b7208d4`; stmlib commit `e3bd7c9cc00e4364166f9905c0509b6ffd0535ec`. Symbol-scoped closure and call graph (local-only reference: `builds/phase21-modal-plaits/closure.json`; not distributed) lists 29 source/header files, their symbols, categories and SHA-256 values. It distinguishes dependencies of the selected renderer from compile-time includes.

**PROVEN:** ModalEngine::Init/Reset/Render (local-only reference: `plaits/upstream/plaits/dsp/engine/modal_engine.cc`; not distributed) allocates 24 float scratch samples, initializes `harmonics_lp_` once, and resets `ModalVoice`. `Reset()` does **not** reset `harmonics_lp_`. Every native render clears MAIN/AUX and applies `ONE_POLE(harmonics_lp_, parameters.harmonics, .01)` before calling ModalVoice.

**PROVEN:** ModalVoice::Render (local-only reference: `plaits/upstream/plaits/dsp/physical_modelling/modal_voice.cc`; not distributed) retains the original two excitation paths:

- Patched trigger: an impulse, scaled by accent, damping, cutoff and the original semitone-ratio lookup. Note-off stops future trigger excitation; it does not erase the ringing histories.
- Unpatched trigger: `Dust(.00005 + .99995 * brightness^4)` with the original random sequence and accent scaling. Density is calculated **before** accent modifies brightness/damping.

The excitation passes through `ResonatorSvf<1>` in LOW_PASS/replace mode. AUX receives this filtered excitation. MAIN receives the 24-mode resonator result. Resonator::Init/Process and NthHarmonicCompensation (local-only reference: `plaits/upstream/plaits/dsp/physical_modelling/resonator.cc`; not distributed) retain all **24 modes**, six batches of four, 48 histories, the `.015` position, third-harmonic compensation, stiffness interpolation, harmonic stretch, and damping/brightness-dependent Q loss. ResonatorSvf::Process (local-only reference: `plaits/upstream/plaits/dsp/physical_modelling/resonator.h`; not distributed) defines the two-state recurrence and four-mode addition order. No modes or internal tails were removed.

**PROVEN:** Voice::Init/Render (local-only reference: `plaits/upstream/plaits/dsp/voice.cc`; not distributed) registers Modal at **model 20**, `already_enveloped=true`, MAIN gain `-1`, AUX gain `.8`. Consequently the original LPG **audio processing is bypassed for Modal**. Voice still executes trigger delay/hysteresis, note smoothing, decay-envelope modulation, accent compression, parameter clamps, engine-entry/reset handling, and `LPGEnvelope::Init()` in the bypass branch. MAIN uses the original limiter; AUX does not. ChannelPostProcessor::Process (local-only reference: `plaits/upstream/plaits/dsp/voice.h`; not distributed) then uses the original negative polarity, truncation, `+1`, and Clip16 conversion. Adding LPG audio filtering would change this target.

The common trigger delay is plaits::DelayLine (local-only reference: `plaits/upstream/plaits/dsp/physical_modelling/delay_line.h`; not distributed), not stmlib's similarly named class. It has eight float entries and a five-native-call read delay. NoteToFrequency (local-only reference: `plaits/upstream/plaits/dsp/engine/engine.h`; not distributed) uses `a0` based on the original corrected **47872.34 Hz** constant; Voice decay (local-only reference: `plaits/upstream/plaits/dsp/dsp.h`; not distributed) uses the original nominal 48000 Hz and native block size 12. These constants were preserved; actual Circuit pitch/rate adaptation was not qualified here.

**PROVEN:** original engine entry calls `LoadUserData` and `Reset`, resets MAIN's postprocessor, and updates the previous-engine index. Modal's `LoadUserData` is a no-op. UserData::ptr (local-only reference: `plaits/upstream/plaits/user_data.h`; not distributed) is compiled under upstream `TEST` in the host oracle; no flash-saving method is called. Returning to Modal would reset its histories while preserving harmonics smoothing. Actual switches through other engines were not exercised; this requirement is established by source, not a runtime switching regression.

Dependency categories, exhaustively enumerated with paths in `closure.json`:

| Category | Selected dependency |
|---|---|
| ENGINE-LOCAL | `modal_engine.{cc,h}`, `modal_voice.{cc,h}`, `resonator.{cc,h}`, `noise/dust.h` |
| VOICE-COMMON | Model-20 portions of `voice.{cc,h}`, `engine.h`, `dsp.h`, `envelope.h`, `physical_modelling/delay_line.h`, LPG initialization in `fx/low_pass_gate.h`, ignored user-data lookup |
| STMLIB-COMMON | `stmlib.h`, DSP helpers, FAST tangent in `filter.h`, limiter, cosine initializer, semitone lookup, hysteresis quantizer, allocator, random implementation; parameter-interpolator header is compile-only on the selected path |
| IMMUTABLE RESOURCE | Two pitch-ratio arrays, stiffness array, fixed-position mode amplitudes, scalar constants |
| MUTABLE STATE | Harmonics smoothing, 50 filter histories, Voice trigger/note/envelope/limiter bookkeeping, trigger-delay storage, RNG; detailed named fields below |

The host executable links the existing complete Voice registry because upstream `Voice::Init` references it. Only model 20 renders. This link requirement does not put other engines into the selected DSP closure or permit charging their memory/code to this port.

## 2. Original memory and two-instance model

**PROVEN on Windows x64:** measured memory (local-only reference: `builds/phase21-modal-plaits/host-result/memory.json`; not distributed) comes from C++ `sizeof` on the original classes. Host object sizes include ABI overhead; they are not Cortex-M measurements.

| Object/storage | Original bytes | DSP representation assessment | Lifetime/sharing |
|---|---:|---|---|
| ModalEngine host object | 344 | No direct byte-to-word conversion: includes vtable/base settings and pointer | Per track, persistent |
| ModalVoice, included above | 300 | 75 scalar fields including resolution and amplitudes | Histories per track; amplitudes shareable |
| Resonator, included above | 292 | Resolution + 24 amplitudes + 48 histories | 48 histories must be independent |
| Resonator histories, included above | 192 | 48 one-word histories tested; precision not admitted; two-word representation would use 96 | Per track, persistent |
| Excitation filter, included above | 8 | Two histories; two-word representation would use four | Per track, persistent |
| Harmonics LP, included above | 4 | One scalar; one/two words depending on numeric design | Per track, persistent |
| RNG | 4 global upstream | **Two** 24-bit words needed to preserve all 32 integer bits | Must become per track for independent streams |
| DecayEnvelope | 4 | One scalar | Per track, persistent |
| LPGEnvelope | 20 | Five logical fields; Modal returns to fixed initialized values each render | Derivable on selected bypass path |
| ChannelPostProcessor | 28 each | Seven floats; MAIN limiter peak is dynamically used, remaining selected-path fields initialize but do not process audio | Per track or derivable constants |
| Trigger delay samples | 32 | Eight scalar entries, plus index and buffer reference in original object | Per track, persistent |
| Modal scratch allocation | 96 | 24 one-word or 48 two-word values | Temporary; serial calls may share after return |
| Voice MAIN/AUX arrays | 192 total | 48 one-word or 96 two-word values at original maximum allocation | Temporary; cannot alias live pending FIFO frames |
| SVF four-mode local arrays | 112 | Seven arrays × four floats; implementation can reuse/register-allocate | Temporary |
| Resonator coefficient local arrays | 48 | Three arrays × four floats, live across nested SVF call | Temporary |
| Pitch-ratio arrays | 2056 | 514 scalar entries; 1028 words for bit-preserving two-word binary32 storage | Shared immutable |
| Stiffness array | 260 | 65 scalar entries; 130 words for two-word binary32 storage | Shared immutable |
| Fixed-position amplitudes | 96 | 24 scalar entries; 48 words for two-word binary32 storage | Shared immutable if initialized to original exact values |
| FIFO remainder | Adapter addition | At most eight MAIN/AUX frame pairs: 16 sample words plus candidate three metadata words | Per track, persistent across Circuit calls |

**STRONG INFERENCE:** ordinary 32-bit ARM C++ layout would make ModalEngine 324 bytes (16-byte Engine base, 300-byte ModalVoice, 4-byte pointer, 4-byte harmonics value), plus 96 allocated scratch bytes. This is a source/ABI derivation, not a measured STM32 object image.

The 112 named tracked fields (local-only reference: `builds/phase21-modal-plaits/state-fields.json`; not distributed) include initialized/bypassed fields and 24 mode amplitudes. After sharing those amplitudes and representing the 32-bit RNG in two words, a one-word-scalar *logical* mirror has **89 words per instance**, before FIFO and control storage. This is not an admitted precision or memory allocation.

**STRONG INFERENCE:** a model-20 specialization could derive bypassed constant fields and represent the dynamic semantic state as 62 numeric scalars plus six integer/flag/RNG words: **68 logical words**, or **130 words** if each numeric scalar is two words. Adding the candidate 19-word FIFO gives **87 / 149 words per track**, **174 / 298 for two tracks**, before canaries, controls and shared scratch. Neither final representation was qualified. The 48 resonator histories and two excitation histories cannot be shared between instances.

**PROVEN:** the two pitch arrays declare 257 entries each but have 256 explicit initializers; the last element is zero-initialized. Counting literals alone would understate original storage. `closure.json` records both counts. All 256 explicit high-ratio binary32 values reconstruct exactly from twelve base entries plus exponent increments of twelve semitones. This tested table compression could reduce high-table storage; DSP reconstruction instructions and placement are still **UNKNOWN**. The low table's 256 usable entries and stiffness interpolation were not approximated away.

All three original arrays total **579 scalar entries**, or **603 including mode amplitudes**. A two-word binary32 mirror is 1206 words; the exponent reconstruction could reduce it to 714 words including amplitudes. These are data-representation counts, not qualified X/Y/P allocations. Putting all uncompressed two-word tables in P would alone exceed 1075; that does not prove the engine cannot fit with data elsewhere.

## 3. Original-source scheduler oracle

**PROVEN:** oracle.cpp (local-only reference: `builds/phase21-modal-plaits/oracle.cpp`; not distributed), generated by prepare.py (local-only reference: `builds/phase21-modal-plaits/prepare.py`; not distributed), runs two independently initialized original Voice objects: one continuous native-12 reference, and one FIFO adapter requested in 32-sample blocks. Both use pinned arithmetic compiled with MSVC `/fp:strict`. Random seed `0x12345678` is explicitly saved/restored per host instance through upstream `Random` accessors.

Controls are sampled at the native render's start sample (`generated / 32`). A render crossing a Circuit boundary retains that native call's controls. The schedule is **3, 3, 2 native calls**, repeating; FIFO remainders are **4, 8, 0** frames. The last call produces four lookahead frames. No native-32 call is substituted.

controls.txt (local-only reference: `builds/phase21-modal-plaits/controls.txt`; not distributed) covers low/high pitches, patched/unpatched excitation, note-on/off, two-block rapid retriggers, no-trigger ringing intervals, level patch/unpatch, accent endpoints, harmonics/timbre/morph boundary controls and sweeps, modulation changes while ringing, and full Voice reinitialization at the first native call using Circuit block 2048's controls. RNG is not implicitly reset by Modal reset.

Host result (local-only reference: `builds/phase21-modal-plaits/host-result/verification.json`; not distributed): **4096 Circuit blocks**, **131072 MAIN/AUX frame pairs**, **10923 native calls**, exact comparison of all 112 listed fields after every native call, arena canaries intact. MAIN has 130794 nonzero samples; AUX has 130348.

| Original-host comparison | Maximum error | RMS error | DC error | First divergence |
|---|---:|---:|---:|---|
| MAIN int16 | 0 | 0 | 0 | None |
| AUX int16 | 0 | 0 | 0 | None |
| Listed persistent/initialized state fields | Exact bits | — | — | None |

This establishes scheduler equivalence between two original host executions. It is **not** ARM-float versus DSP fidelity or two-track isolation. Dynamic model switches and real ARM mailbox timing are outside this host test.

## 4. Numeric range experiment and actual DSP code

trace_numeric.py (local-only reference: `builds/phase21-modal-plaits/trace_numeric.py`; not distributed) creates a separate header overlay that observes the pinned SVF's coefficients, inputs and histories without changing its arithmetic expressions. ModalEngine, ModalVoice and Resonator are rebuilt against that overlay. The instrumented original output is byte-identical to the uninstrumented host output. Observed ranges (local-only reference: `builds/phase21-modal-plaits/numeric-vectors/numeric-ranges.csv`; not distributed) are test-domain observations, not global mathematical bounds:

| Quantity | Observed range |
|---|---|
| Frequency | `6.91017e-8 .. .499000013` cycles/sample |
| FAST tangent `g` | `2.17089e-7 .. 4.54958725` |
| Q | `.7 .. 1850643.5` |
| Reciprocal Q | `5.40353e-7 .. 1.42857146` |
| `r + g` | `.00170832 .. 5.97815895` |
| `h` | `.0354633 .. .999999881` |
| Input across excitation and resonator filters | `-3.88835 .. 521844.53125` |
| Filter histories | Approximately `-49.684 .. 49.216` |

**PROVEN:** blindly reusing VariableSaw's Q3.21 audio/state format cannot represent this observed domain. A single-word resonator-only candidate used signed Q7.17 input/history, Q4.20 `g`/`r+g`, and Q1.23 `h`/gain. These Q names count the sign in the integer-width total; the fractional-bit counts are authoritative. Signed DSP MPY uses the previously qualified `mpy y0,x0,a` opcode and 56-bit accumulator. Every explicit narrowing was checked; products truncate by arithmetic shift, while host coefficient/input conversion rounds to nearest using `llround`.

The first 82-word assembly (local-only reference: `builds/phase21-modal-plaits/plain-assembly/program-map.txt`; not distributed) rejected its independent-integer overflow check at vector record **19789**, native render **3298**, batch 1. Diagnostic log (local-only reference: `builds/phase21-modal-plaits/probe-diagnostic.log`; not distributed): operands `4770641 × 1854020 >> 20` produced `8435119`, above signed 24-bit maximum `8388607`. This was a narrowed `r+g` product before cancellation, not evidence that the original algorithm was unstable. The failed candidate remains recorded; it was not skipped or converted to a passing test.

The second DSP assembly (local-only reference: `builds/phase21-modal-plaits/resonator_fused_probe.asm`; not distributed) factors only that real-number equation:

`hp = h*input - (h*(r+g))*state1 - h*state2`.

`h*(r+g)` uses Q2.22; `g` remains Q4.20 and `h`/gain Q1.23. Products are narrowed independently as modeled in probe.cpp (local-only reference: `builds/phase21-modal-plaits/probe.cpp`; not distributed). There is no silent saturation or discarded mode. This reassociation changes floating/fixed rounding and is explicitly not bit-exact to upstream floating arithmetic.

**PROVEN:** this **91-word four-mode kernel** accepts a state pointer in R7 and is called six times per native render by the test harness, covering all 24 modes. It completed **65538 four-mode calls / 10923 native renders**, with two reset events, zero independent-integer-model mismatches, zero detected accumulator-narrowing overflows, intact state/scratch/output canaries, zero P writes and zero writes outside the declared synthetic ranges. Native verification (local-only reference: `builds/phase21-modal-plaits/fused-probe-result2/verification.json`; not distributed).

The harness supplies **original host-generated coefficients and filtered excitation**. The DSP does not yet execute pitch/lookup/division/coefficient generation, the noise/impulse excitation filter, full Voice processing, the 12→32 FIFO or vpre. Repeating six kernel calls in a host harness does not charge or qualify the missing DSP caller code.

| Arithmetic group | Fidelity assessment |
|---|---|
| Host original versus host FIFO | **BIT-EXACT**, for tested samples and named state fields |
| DSP recurrence versus separate integer model | **BIT-EXACT**, for this defined fixed representation |
| Factored recurrence over real numbers | **ALGORITHMICALLY EQUIVALENT** algebra; rounding differs |
| Full-domain frequency/history representation | **UNQUALIFIED**: 609 observed `g` coefficient instances round to zero |
| Pitch conversion, interpolation, division/reciprocal on DSP | **UNQUALIFIED**: remain original host operations in this probe |
| Noise/RNG on DSP | **UNQUALIFIED**: exact original LCG needs full modulo-2^32 state, not B1.3's unrelated modulo-2^24 LCG |
| MAIN limiter and AUX conversion on DSP | **UNQUALIFIED**: original host postprocessing only |
| Phase | Modal has resonator histories, not an oscillator phase accumulator; no replacement phase algorithm was introduced |
| Perceptual equivalence | **UNQUALIFIED**; no listening-based claim |

## 5. Quantitative comparison and timing

Consolidated results (local-only reference: `builds/phase21-modal-plaits/result.json`; not distributed) restrict the raw resonator comparison to the requested 131072 frames; native verification also reports all 131076 generated frames including lookahead.

| DSP diagnostic versus original float | Maximum absolute | RMS | DC | Correlation | First divergent sample |
|---|---:|---:|---:|---:|---:|
| Raw resonator sum, 131072 samples | .0673418045 | .0099818732 | -.00103764535 | .999998542728 | 48 |
| Resonator histories, 524304 observations including lookahead | .0659589767 | .00629908879 | -.00104346804 | .999998714667 | 192th flattened observation |
| Hybrid MAIN int16, 131072 samples | 996 | 68.4982250 | 4.74188995 | .999966983908 | 694 |
| Complete DSP MAIN/AUX | **UNKNOWN** | **UNKNOWN** | **UNKNOWN** | **UNKNOWN** | **UNKNOWN** |

The hybrid MAIN test (local-only reference: `builds/phase21-modal-plaits/hybrid-main.json`; not distributed) runs the DSP resonator output through the **actual original host ChannelPostProcessor**, with original resets. postprocess.cpp (local-only reference: `builds/phase21-modal-plaits/postprocess.cpp`; not distributed) is diagnostic: coefficients, excitation and postprocessing remain on the host. AUX has not been implemented on DSP. High correlation does not qualify complete ModalEngine fidelity or justify eliminating low-frequency modes.

**PROVEN within the interpreter cycle model:** actual instruction counts and the sealed interpreter's `calcOpcodeCycles` sum are recorded for every native render. These are modeled cycles, not physical DSP measurements. Counting is from executed DSP instructions, not host elapsed time. The kernel has a fixed path, so events do not change these counts.

| Measured scope | Instructions min / mean / max | Modeled cycles min / mean / max |
|---|---|---|
| Six kernel calls, one native 12-sample render | 14640 / 14640 / 14640 | 27072 / 27072 / 27072 |
| Same kernel work reblocked by verified 32-sample schedule | 29280 / 39041.19140625 / 43920 | 54144 / 72194.203125 / 81216 |
| Full renderer, wrapper/control overhead, one complete instance | **UNKNOWN** | **UNKNOWN** |
| Two complete instances, including simultaneous triggers/tails | **UNKNOWN** | **UNKNOWN** |
| Retained baseline + one/two complete Modal instances | **UNKNOWN** | **UNKNOWN** |

The first three-native-call worst block is Circuit block 0; every block with three calls ties it. This is the measured candidate implementation, not a lower bound for an optimized full port. It cannot be compared as a complete integration cost to the earlier VariableSaw bounds or used to assert two-instance feasibility.

## 6. Exact P placement and incomplete full-engine charge

**PROVEN:** Layout A ends at exclusive P:`$3BBA`. P:`$3BBA–$3FFF` contains **1094 physical tail words**, consisting of **1075 reclaimed words plus the original 19-word tail**. This experiment charges only **P:`$3BBA–$3FEC`**, 1075 words. P:`$3FED–$3FFF` is reserved and was not silently added to the budget.

The assembler allocation (local-only reference: `builds/phase21-modal-plaits/fused-assembly/allocation.json`; not distributed) and addressed instruction map (local-only reference: `builds/phase21-modal-plaits/fused-assembly/program-map.txt`; not distributed) place the kernel at **P:`$3BBA–$3C14`**, 91 words; **P:`$3C15–$3FEC`**, 984 words, remains after this *partial kernel charge*. The assembled analysis bytes match the executed probe bytes.

| Required component | Assembled P charge |
|---|---:|
| Four-mode recurrence probe including local loop/entry setup | 91 |
| Complete 24-mode renderer, coefficient generation, initialization and excitation | **UNKNOWN** |
| Voice common control/limiter/conversion | **UNKNOWN** |
| Native-12 FIFO adapter | **UNKNOWN** |
| Mailbox/control mapping | **UNKNOWN** |
| Caller saves, return/trampolines | **UNKNOWN** |
| Final immutable P tables | **UNKNOWN**; none are in the probe |
| **Complete required total / remaining** | **UNKNOWN / UNKNOWN** |

The raw `.be24` files are isolated DSP analysis streams, not a firmware image. No stock-synth overlay, Layout B region, mutable P state or firmware builder was used. Complete-engine P1 (`<=1075`) is **UNKNOWN**. Neither “fits” nor “cannot fit” follows from the probe. Table sharing, exact high-ratio exponent reconstruction and X/Y table placement are avenues to measure, not unearned budget credits.

## 7. Data ownership, two instances and caller contract

The following addresses are **synthetic probe ownership only**. No stock Circuit DSP image is loaded into this interpreter instance. Their successful use establishes no CIRCUIT memory ownership.

| Range, inclusive | Words | Owner / lifetime | Readers / writers / guards |
|---|---:|---|---|
| X:`$20–$4F` | 48 | All 24 resonator histories, persistent | DSP recurrence; harness zeroes on two original resets; guards X:`$1F/$50` |
| X:`$80–$8F` | 16 | Four-mode coefficients, each call | Harness writes, DSP reads; DSP writes rejected |
| X:`$100–$109` | 10 | Dedicated numeric scratch, each call | DSP only; guards X:`$FF/$10A` |
| X:`$200–$20B` | 12 | Filtered excitation input, each call | Harness writes, DSP reads; DSP writes rejected |
| Y:`$300–$30B` | 12 | Native resonator accumulation, six calls | Harness clears per native render, DSP adds; guards Y:`$2FF/$30C` |
| P:`$3BBA–$3C14` | 91 | Probe instructions | Assembler/host initializes, DSP fetches; all DSP P writes rejected |

All six canaries are checked after every four-mode call. The bus rejects every write except the listed history, scratch and output ranges. Reads use the synthetic backing; this is not a complete retained-memory access audit. No shared or external-memory transactions are involved.

**UNKNOWN:** final addresses for complete instance #1, instance #2, shared tables and full scratch have **not** been qualified. No unrelated live buffer was borrowed. No external memory was used or cross-core ownership assumed.

The retained vcf21_dsp.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/vcf21_dsp.py`; not distributed) allocation methodology is explicit named blocks and offsets, not zero scans. Its existing blocks remain relevant constraints:

- `VB0=$3B80`, stride 48, two mailbox/control/state records through X:`$3BDF`.
- `SAVX=$38C0`, 32 words; `FXS=$3840`, stride 48; second filter state at `S2BASE=$3800`.
- `OSB0=$3900`, stride 48; `KEYF_OFF=19`, `NOTE2_OFF=20`, `DFLAGS_OFF=21`, VA-envelope fields 22–25. This is not a wholly free 96-word allocation merely because oscillator code was removed.
- `OS2B0=$3960`, records X:`$3960–$398F` and `$3990–$39BF`. These are potential reclamation *investigation* targets, not admitted Modal records: the retained mailbox still has oscillator parameter destinations and must be audited/remapped before histories occupy them.
- Y comb buffers at `$3400` and chorus buffers at `$3600` remain retained FX resources.

**STRONG INFERENCE:** code and immutable resources can be shared by two Modal instances; histories, harmonics smoothing, trigger/note/envelope/limiter state, RNG and pending FIFO samples must be independent. The tested kernel's R7 state-pointer interface demonstrates this programming mechanism for one resonator's batches. It is not a two-instance isolation test. Shared temporary storage is only plausible for serialized non-overlapping calls, with lifetime/save contracts proven separately.

**UNKNOWN:** full vpre register/modifier preservation. The standalone kernel changes arithmetic registers, address pointers and loop/status state and has no vpre save/return wrapper. The existing contract requires preserving X0/X1/Y0/Y1, R0/R1/R2/R3/R4/R6/R7, N0, M0/M2/M4, plus the independently tested core-1 R5/M5 contract. No existing dedicated save area is overwritten by this experiment; a complete wrapper and its P/data charge remain to implement and test.

## 8. Mailbox/vpre mapping status

**PROVEN from reference source:** `GATE=18`, `NOTE=19`, `ACT=20`, `VEL=21`, `GNEW=22` are X-record **offsets**, corresponding to mailbox **codes 17,18,19,20,21**. `MB=0`, last tag `MBL=1`; the packet is `tag<<23 | code<<16 | value16`. The vpre path is called from P:`$23C`, processes input/return sources, then tail-calls the stock premix. Reference `FLAGS=$3A00`, `RING_PTR=Y:$FFD`, return buffers Y:`$880/$9C0` and stock level/pan/send/sidechain stages are preserved by the earlier Layout A study.

**UNKNOWN / not implemented here:** actual ARM note/parameter hooks bound to Modal, parameter publication/coalescing semantics, fixed model-20 selection, and complete vpre insertion. A source-level mapping requirement is:

| Modal input | Required B1.3 binding |
|---|---|
| Pitch | NOTE code 18 and deliberately specified tune/fine policy, feeding original Voice smoothing and pitch conversion |
| Trigger | GATE code 17 plus GNEW/TRIG code 21 retrigger handling, retaining original native-call delay/hysteresis |
| Level/accent | VEL code 20 with explicit normalization and original level-patched compression; strip LEVEL stays distinct |
| Harmonics/timbre/morph | Three documented parameter slots and ARM/UI publication rules, normalized/clamped before original Voice modulation |
| Model | Fixed 20; no multi-model UI in this phase |
| Audio | Original MAIN converted to the stock input-strip representation; AUX must still be computed and oracle-tested |

This table is a requirement, not a traced implemented control path. Mapping three controls onto arbitrary legacy oscillator slots without changing all retained writers would invalidate state ownership. There is no claim of tested ARM→DSP Modal transport or mailbox rate-limit behavior.

## 9. Retained regression and gates

**PROVEN:** earlier Layout A results remain unchanged: 8192-block exact retained sample/state/transaction comparison, active stock Synth1/Synth2, mixer/send automation and separate active Master FX tests. Final qualification evidence (local-only reference: `builds/phase20l-master-path/final-verification.json`; not distributed). This experiment did not load a Modal-integrated retained module. Those prior results cannot be relabeled as a new integrated regression.

Sample drums and active capture/glitch remain **UNKNOWN** as complete coverage. No new claim was added for them. Two full instances were not attempted because a complete single-instance oracle and allocation have not passed.

| Gate | Confidence | Outcome |
|---|---|---|
| M1 — exact pinned selected closure | PROVEN | Identified; complete symbol/path/table inventory provided |
| M2 — 12→32 wrapper | PROVEN | Passed 4096 original-host blocks, exact MAIN/AUX and 112 state fields |
| M3 — complete DSP Modal implementation exists | PROVEN | **Not met**: only a recurrence probe exists |
| M4 — complete code fits 1075 | UNKNOWN | 91-word kernel is not the full charge |
| M5 — complete state allocation, one instance | UNKNOWN | Synthetic histories tested; no admitted full Circuit record |
| M6 — complete state allocation, two instances | UNKNOWN | Not allocated/tested |
| M7 — complete single-instance MAIN/AUX oracle | UNKNOWN | Partial numeric metrics provided; complete DSP output unavailable |
| M8 — two-instance isolation | UNKNOWN | Single-complete-instance prerequisite unmet |
| M9 — two-instance timing acceptable | UNKNOWN | Kernel counts cannot establish full/coupled timing |
| M10 — integrated stock Synth1/Synth2 regression | UNKNOWN | Prior Layout A pass retained; no integrated test |
| M11 — integrated mixer/send/Master FX regression | UNKNOWN | Prior pass retained; no integrated test |
| M12 — integrated P guards | UNKNOWN | Synthetic probe forbids P writes; integrated guards not tested |

## 10. Reproduction, remaining blocker and next experiment

All new experimental sources, generated overlays, executables, raw analysis streams and results reside under phase21-modal-plaits (local-only reference: `builds/phase21-modal-plaits`; not distributed). artifact-manifest.json (local-only reference: `builds/phase21-modal-plaits/artifact-manifest.json`; not distributed) records artifact/dependency hashes. `prepare.py` verifies pinned sources and generates controls/oracle; `build_oracle.ps1` compiles it. `trace_numeric.py`/`build_numeric.ps1` generate the observational oracle. `make_kernel.py`, `build_probe.ps1` and `build_fused_probe.ps1` generate/build the native arithmetic probes. `build_assemble.ps1` produces addressed maps. `build_postprocess.ps1` compiles the hybrid diagnostic. `inventory.py` and `evidence.py` consolidate evidence without rerunning completed renders. Oracle/probe output directories must be fresh.

The failed ordinary kernel and passing integer-model fused kernel are separate outcomes, not merged. Initial assembler jump-syntax trials and the CMake `/Zi` database-manager failure are not algorithm tests; the successful native build uses direct MSVC `/MDd /O2` with the existing sealed interpreter libraries. Neither issue required modifying the reference toolchain.

The immediate numeric blocker is the unqualified single-word low-frequency/history representation, including 609 zeroed coefficient instances. Complete exciter, coefficient/reciprocal/table logic, Voice wrapper, qualified data allocation and retained integration are also still absent. This is **not** a proven size failure; no smallest hardware/P-budget enlargement is justified from these results.

**Single smallest next experiment:** replace the recurrence probe's frequency coefficients and histories with a two-word representation and replay the **same original 24-mode vectors and 4096-block schedule**, keeping all modes, controls and reset cases. Require nonzero original coefficients to remain representable, preserve strict narrowing/canary checks, and report output/state error, exact assembled size and modeled cycles against this measured single-word candidate. This resolves the numeric choice before charging or admitting complete-engine integration. It does not require firmware or hardware.

| Final requested measure | Result |
|---|---|
| Complete P words used / 1075 | **UNKNOWN**; partial kernel **91 / 1075** |
| P words remaining | Complete **UNKNOWN**; **984 after partial kernel only** |
| Per-instance state words | **UNQUALIFIED**; 68 or 130 semantic-state candidate words, plus 19 FIFO words, before other ownership needs |
| Shared immutable data words | **UNQUALIFIED**; 603 scalar entries uncompressed; two-word mirror 1206, exact high-table reconstruction candidate 714 |
| Worst measured instructions per Circuit block | **43920, recurrence work only** |
| Worst modeled cycles per Circuit block | **81216, recurrence work only** |
| One-instance full DSP oracle fidelity | **UNQUALIFIED**; original-host wrapper is bit-exact |
| Two-instance isolation | **UNKNOWN**, not attempted |
| Remaining blockers | Numeric admission; complete DSP implementation/size; data ownership; ARM/vpre/save integration; full single-instance oracle; two-instance and retained regression |

PLAITS MODAL DSP PORT = UNQUALIFIED
