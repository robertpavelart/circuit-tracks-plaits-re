> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Dual-replacement P budget: authentic-reference qualification

2026-10-15. **The installed reference environment is reproducible, but neither layout is qualified under the requested complete-workload standard.** The new evidence is materially stronger: authentic ARM initialization, actual stock generator execution, 4,096 core-0 blocks per layout, and the installed pinned DSP emulator. Important core-1, feedback, external-memory and full-system paths remain modeled or absent. All long-run final master snapshots were zero, so their sample equality cannot qualify a complete non-silent audio workload.

PROVEN means directly established by the stated artifact/execution. STRONG INFERENCE means a source-supported extension beyond that scope. UNKNOWN means the required evidence is missing. A passing partial experiment never promotes an UNKNOWN required gate.

No Plaits engine was produced. No application BIN, SYX, flash package or flash-ready firmware was generated. No hardware was accessed. Reference builders were not invoked, because they generate firmware, even when their output is temporary. Published B1.3 code was loaded for emulation from existing uploader COPY/ADD spans and hash-checked without saving an application image. Raw DSP streams, emulator drivers and audit executables are analysis inputs, not firmware packages. All changes are in CIRCUIT.

## 1. Reference provenance

Reference root: `C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main`.

**PROVEN:** the dump checkout HEAD is `d6aec9fc9d975d65f54ed5ca16c096227e6974ab`, from `userx14/circuittracksreverseengineering`. File bytes match the pinned Git blob IDs, not merely filenames:

| Exact file used | Bytes | SHA-256 | Pinned Git blob |
|---|---:|---|---|
| `C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ctre\Firmware-Analysis\dumpCT_flash_0x08000000.bin` | 524,288 | `f3d85d64c9ead9205e5336dff49bb51f21d270ffa29b47c6f6971125d6d848a8` | `4f8ce3714e366d36ef668334aa92c194e95917b1` |
| `C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ctre\Firmware-Analysis\ram_dump_firmware_0x08037988.bin` | 327,679 | `26a29670c0c1918217b7eadf8f89fe6df97994d3cc6e1c0ed65ac522e161094c` | `303437fcb2117b6d47b34df51409b0721f610db2` |

**PROVEN:** the flash dump's application slice equals the entire official stock 4486 BIN, byte for byte. Stock identity is Circuit Tracks 1.2.1 build 4486, 314,844 bytes, BIN SHA-256 `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da`; official SYX SHA-256 `bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd`. Paths are `stock/circuittracks-firmware-4486-STOCK.bin`, `.syx`, and `stock/SHA256SUMS.txt` under the reference root.

**PROVEN:** the existing published B1.3 spans hash to BIN `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`, size 435,220 (`$6A414`). Its manifest's SYX identity is `6f07376b5983a5e0350d4883ae9ed57a69bc735320afde9f43ca75017b8e8736`. The user's independently reported `verify_builds.py: ALL IDENTICAL` agrees; that firmware-generating command was not rerun here. Evidence: B1.3 manifest (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/firmware/b1.3/manifest.json`; not distributed) and `tools/rc_uploader.html:PATCHES.B1.3`.

**PROVEN:** installed `re/app.asm` text exactly matches fresh in-memory disassembly of verified stock bytes, using Capstone 5.0.7 and the same options as gen_listing.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/gen_listing.py`; not distributed). Installed Unicorn is 2.1.4. Python used: `C:\Users\rober\AppData\Local\Python\pythoncore-3.14-64\python.exe`, always with `-B`.

**PROVEN:** DSP checkout HEAD is `44353be2f0156cac970c6ab4f467ea1998b40605`. Its four working-tree changes match the documented memtrace/MinGW patch areas: `memory.cpp`, `memory.h`, `mmuhelper.cpp`, `threadtools.cpp`. Installed tool: `C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ext\bin\dsptool.exe`, SHA-256 `a8f9988386377a33024c39ccea26722f6699976c9d0d3a0297a42cfde060fc7a`.

**STRONG INFERENCE:** binary-to-source association follows the pinned checkout, CMake build cache, WinLibs compiler path, static libraries and documented `setup_dev.py:step_dsptool` recipe. This run did not rebuild the emulator libraries to establish bit-for-bit independent binary reproducibility. It built a CIRCUIT-only audit wrapper linked to those same installed libraries. Compiler, source, library and executable hashes are in `audit-tool-provenance.json`.

## 2. Initialization authenticity and real objects

The reference emu_sc05.py:E (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/emu_sc05.py:18`; not distributed) loads the authentic flash/RAM. Published B1.3 application spans replace only application code/data in Unicorn memory. The reference Session (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/dsp_session.py:47`; not distributed) then executes stock post-upload initialization at ARM `$08029492` and the full parameter flush at `$080213B0`. This produces **2,880 core-0 init writes and 388 stock parameter writes**. Every ARM call in the new adapter must actually return; reaching an instruction cap is rejected.

| State source / role | Classification | Evidence and limit |
|---|---|---|
| Existing ARM flash/SRAM, receiver/controller objects and stock parameter backing | AUTHENTIC DUMP | Verified pinned bytes. A stock running snapshot, not a captured B1.3 runtime or every possible execution epoch. |
| Stock coefficient/init tables and flushed DSP controls | DERIVED FROM VERIFIED STOCK/B1.3 CODE | Real ARM initialization/flush on the dump. DSP X/Y were not themselves dumped from hardware. |
| Synth1/Synth2/MIDI1/MIDI2/drum macro-handler pointers | AUTHENTIC DUMP, inspected after reference init | Controller chain `$200069E4` → `$20044CB8` → `$20040B10` → `$20040DB8`; pointers below. |
| Master FX extra state at `$20044D94`; MIDI settings tail `$20039789`; new mode/patch/control bookkeeping | DERIVED FROM VERIFIED STOCK/B1.3 CODE | Actual c_gfst/c_vtick/restore code executes. Old SRAM bytes at those addresses are not automatically authentic B1.3 state. |
| MIDI per-track DSP records X:$3900/$3960/$3B80, stride 48; filters/track FX | DERIVED FROM VERIFIED STOCK/B1.3 CODE | DSP initialization and actual ARM mailbox messages. Immutable source/program layouts match phase20g. |
| Stock mixer/DSP routing/gain state | DERIVED FROM VERIFIED STOCK/B1.3 CODE | Parameter flush and full core-0 block execution. Complete typed ARM mixer-object ownership and every control permutation remain UNKNOWN. |
| Shared X snapshots, MIN, CNT and RDOFS | DERIVED FROM VERIFIED STOCK/B1.3 CODE | Actual core-0 sampler/granular tail. Returned OUT/GOUT are not produced by a concurrent core 1. |
| Callback timing, forced parameter-flush readiness, hardware/semaphore/SPI boundaries and extra emulator stack RAM | MODELED FIXTURE | Inherited reference E/Session/Shi behavior, explicitly retained. One missing SRAM byte is zero-padded; auxiliary mapped SRAM/peripherals are not authentic dump contents. |
| Line input tone, mode patch records, FX latch stimulus, automation callback schedule | MODELED FIXTURE | Deterministic stimuli, transported through real code where stated. Stored patches come from declared buffer delivery, not authentic B1.3 files. |
| Storage locks/save completion | MODELED FIXTURE; real scheduler behavior UNKNOWN | Unstubbed c_mpload did not return after 20,000,000 instructions, stopped at `$0801BE62` in the event/scheduler wait. The later lock/save boundaries are intercepted and reported, not counted as a complete storage test. |
| Authentic DSP CPU state, shared bus/external sample/capture SDRAM and coupled service timing | UNKNOWN | The supplied files contain ARM SRAM/flash, not coherent images of both DSPs and their shared/external memory. |

Measured macro-handler addresses: Synth1 `$20043CC8`, Synth2 `$20043D2C`, MIDI1 `$20043D90`, MIDI2 `$20043DF4`; Drum1–4 `$20043E58`, `$20043EB4`, `$20043F10`, `$20043F6C`. These identify actual objects, not proof of their complete lifecycle. Receiver `$20044CB8`, TX interface `$20011334`, dirty groups `$200067FC`, HAL tick `$2000081C` are also recorded. See `qualification-summary.json:ARM_objects` and `authentic-ARM-workload.json:object_snapshots`.

## 3. Baseline and long workload

Original B1.3, A and B each executed **4,096 consecutive 32-sample core-0 blocks**, 131,072 frames/profile. Total canonical long-run audio blocks: **12,288**. Each run performs the reference two-stage DSP initialization first. A second run with identical stimuli isolated audio-only memory traces from initialization clearing; it reproduces the same sample/state/register results. Repetition is not counted as a longer continuous workload.

Stimuli go through actual ARM MIDI receive/parameter-flush, B1.3 mode restore/validation/application, c_vapply and c_vtick. There are 32 stock note-on, 32 note-off, 32 filter-parameter events, 32 mode restores, 128 automation event points, 32 drum triggers and eight requests for simultaneous stock notes. Blocks 0–1023 focus Synth1, 1024–2047 Synth2, and 2048–4095 combine stock notes, drums, FX and retained MIDI modes. MIDI1/2 cycle line, granular, FX-sequencer/off selections using declared patch records. The DSP generator, stock mixer, Master FX and sampler/core-0 shared-memory paths run as part of original P:$1ED blocks; there are no synthetic stock-synth overlays.

The reference runner replaces P:$76A/$76F/$77D wait instructions with NOPs, uses a P:$7000 caller outside the allocation budget, and returns zero-filled SPI read replies. Those models remain explicit. No concurrent core 1 services the gather requests. The workload is **not complete**, irrespective of its duration.

## 4. Active Synth1/Synth2 evidence

**PROVEN:** actual stock generator seams P:$9B9/$9D9 execute after real note stimuli; the long baseline has **937,718 nonzero writes** in the stock mono output/guard region X:$2C46–$2C66. This advances beyond code identity and supplied synth stems. Stock generator/coefficient/history snapshots are compared every 64 blocks and at the end, 65 expanded snapshots/profile. Captured registers and tested state match A/B exactly.

**UNKNOWN:** faithful simultaneous allocation/readback and the complete stock waveform/gather environment. `shi_capture.py:Shi.word` discards read commands; `attach` fills receive buffers with zeros. Both-note requests do not by themselves prove authentic simultaneous active voices. The missing live DSP readback and core-1/external state limit generator admission even though generator instructions and nonzero mono writes are proven.

**PROVEN limitation:** all 4,096 final master snapshots X:$2E10 are zero in baseline as well as both reductions. Therefore final sample equality is not evidence of a complete non-silent mix. The source of that silence was not fully isolated; it must not be attributed exclusively to one modeled boundary without a causal test. Native histogram/watch PC labels identify outer interpreter dispatches; optimized DO bodies can execute internally, so a watch PC is not always the precise inner store instruction.

## 5. Retained MIDI modes and stale flags

The **unchanged original fixture harness** was rerun separately: all 78 transition vectors and all 64 original patch flags remain present, including its rapid zero-time switching. It again records 2,113 calls and 2,646 messages with zero offending ACT messages. These preserved fixtures are not relabeled authentic RAM tests.

An additional replay applies the 78 vectors to the authentic ARM RAM/object environment with explicit storage/view boundaries. All complete. The six Boolean ACT inputs—on, oscillator, VA/velocity-engine bits, route and dual—are exhaustively exercised in **64 combinations on each track**, 128 cases. This replay canonicalizes source mode via validated patch restore and paces accepted ACT messages; it supplements rather than replaces the original rapid-switch fixtures. No offending ACT payload is produced. The 4,096-frame ARM timeline also produces zero offending payloads.

**PROVEN producer invariant within this executed input domain:** actual c_vsend emits neither ACT=1 + DFLAGS VA bit 2, nor ACT=2 + both granular bit 4 and VA bit 2. Actual instructions at `vcf21.py:c_vsend` map line+VA into voice-off for FX-sequencer and move `$0800` to `$1000` only when `$0400` is absent. This is exhaustive payload-input testing of that producer, not merely failure to observe an event. Tag/timestamp bits do not change this payload rule. Real DSP decoding separately masks ACT to two bits and DFLAGS to five.

**STRONG INFERENCE:** the 48 cases are outside normal completed c_vsend transitions. **UNKNOWN:** a complete whole-system proof excluding every initialization/interruption/alternative writer or corrupted state. No global unreachability claim is made from the finite transition tests alone.

All **48 original failing cases were rerun unchanged on the installed pinned DSP tool**, not skipped or normalized:

- Layout A: all 144 differential blocks equal, including those 48.
- Layout B: 96 equal, the same 48 malformed-state blocks fail.

Classification: PROVEN direct malformed-state counterexamples; PROVEN impossible outputs of the tested complete six-bit c_vsend domain; STRONG INFERENCE normal-path unreachability beyond that producer; UNKNOWN global system reachability. They are not proven artifacts of missing ARM RAM, and no implementation fix was applied. They remain valid negative/robustness regression tests even if a future complete proof establishes normal-path unreachability.

## 6. Drums / FX / mixer / capture results

**PROVEN within captured core-0 scope:** both layouts have zero retained semantic memory/sample/register mismatches in the long comparison. Macro controls, shared snapshots/counters and audio processing are exercised together, not only as isolated functions. However the silent final master, absent concurrent core1 and modeled scheduler prevent complete admission of pan/sends/sidechain, active granular/glitch and project-controlled sequencing.

The unchanged applicable retained assertions were also rerun on the installed `ext/bin/dsptool.exe`: **1,811 native component/replay jobs**. Both layouts pass SC36 core-0, relocated tail, FX-return and drum-control suites. Master FX 64, capture 15, capture replacement 20 and core1 granular/glitch 28 component jobs pass. Only B's preserved 48 stale cases fail. Historical component tests use their documented remapped/synthetic fixtures; those passes do not qualify native external-memory concurrency. Independent step-drummer routing and actual patch filesystem/scheduler remain partial or UNKNOWN.

## 7. Core 1 and memory backend

**PROVEN program identity:** actual published B1.3 core1 is 2,047 words, SHA-256 `b93a959b0793578385dd46e482fde16501771c0793180a0350dfd2c3a87466bf`, identical to the previously retained core1 slice. Native boot probe reaches P:$10E in four dispatched instructions. A modeled CNT increment exercises the actual c1loop first task and returns to $10E, 57 dispatches / 833 reported instructions. No claim of authentic task state or coupled scheduling follows.

**PROVEN backend limitation:** the installed tool constructs `Memory(...,$80000)`. Writing sentinels at native glitch Y:$340000 and capture Y:$E80000 and reading them back returns zero, not the sentinel. Native external-memory behavior is therefore not represented by this backend. Merely having the program/dumps installed does not fix that model. No native-address concurrent granular/glitch/capture pass is claimed.

Important UNKNOWN paths: core1 stock gather requests/results, actual sample/pack/capture data, inter-core request ordering/acknowledgements, shared-memory coherence under simultaneous execution and native external-memory accesses. Core1 component fixtures with remapped addresses cannot fill these gaps.

## 8. P ownership and exact layouts

| Quantity | A — conservative | B — extended |
|---|---:|---:|
| Original core0 | 16,365 | 16,365 |
| Reduced core0 | 15,290 ($3BBA) | 15,188 ($3B54) |
| Reclaimed words | 1,075 | 1,177 |
| Existing tail, separate | 19 | 19 |
| Candidate inclusive range | $3BBA–$3FFF | $3B54–$3FFF |
| Contiguous size including old tail | 1,094 | 1,196 |

**PROVEN finite evidence:** every candidate P word is canaried after initialization and checked after every long-run block. Both layouts retain all canaries, with zero recorded runtime P writes and no recorded outer-dispatch entry into the free tail. Static placement and repaired P:$D22/$2ACF operands remain those of the exact phase20g assembly/relocation ledger; no preserved synth code is reclaimed.

**UNKNOWN complete ownership:** the reference run loads P directly, not through a newly reduced firmware bootstrap image; loader lifecycle/reupload and asynchronous interrupt/service paths are not completely exercised. Histogram/entry guards surround interpreter dispatch and do not provide complete per-instruction PC coverage of internal fast DO execution. Static indirect reachability is conservative, not an independently complete recovered whole-program CFG. These limits prevent calling this a complete dynamic/static P ownership proof.

## 9. X/Y/shared/external side effects

Audio-only access bitmaps are reset after initialization; otherwise bulk clears conceal removed writes. A removes writes only at X:$390B–$3912 and $393B–$3942 (16 addresses). B additionally removes writes at $3916/$3917/$3919 and $3946/$3947/$3949 (22 total). These are the old oscillator derived fields and VA envelope/noise-level fields. All change from read+write to read-only because retained snapshot copying still reads them. No other observed audio access-bit address changes occur; Y access bitmaps are unchanged.

The only raw expanded-snapshot differences are the old derived oscillator records and their copied shared-X shadows, at all 65 expanded snapshots. `compare.py` excludes exactly declared dead cells, not arbitrary retained state; sampler temporary save slots are separately identified, and show no raw mismatch in this long run. Captured full-block registers have zero differences, including modifiers; phase20h's separate 15-register vpre contract test remains supporting evidence rather than being substituted for full register equality.

Access bitmaps prove touched addresses, not every numerical transient write. Watched numerical ranges and 65 state snapshots provide additional finite comparisons; unobserved numerical writes and unsupported high external addresses remain UNKNOWN. No new data-state ownership is admitted.

## 10. Separate layout decisions and final gates

| Required gate | Layout A | Layout B |
|---|---|---|
| Q1 active Synth1 | PROVEN executed/captured conditional comparison; UNKNOWN complete faithful workload | Same |
| Q2 active Synth2 | PROVEN executed/captured conditional comparison; UNKNOWN complete faithful workload | Same |
| Q3 retained MIDI modes | PROVEN tested controls/core0 equality; UNKNOWN active granular/FX-sequencer/full scheduler | Same |
| Q4 drums | PROVEN component/control and trigger-path checks; UNKNOWN complete native sample/concurrent workload | Same |
| Q5 Master FX | PROVEN component checks; UNKNOWN non-silent complete master workload | Same |
| Q6 mixer | PROVEN captured equality; UNKNOWN complete non-silent level/pan/send/sidechain permutations | Same |
| Q7 core1/shared interaction | UNKNOWN | UNKNOWN |
| Q8 stale state | PROVEN all preserved stale fixtures pass; UNKNOWN whole-system transition coverage | PROVEN producer-domain invariant; STRONG INFERENCE normal-path unreachability; UNKNOWN whole-system exclusion. All 48 negative failures remain. |
| Q9 tail stable | PROVEN finite canary/write/dispatch evidence; UNKNOWN full loader/interrupt/internal-execution proof | Same |
| Q10 initialization sufficient | PROVEN ARM provenance and executed initialization; UNKNOWN complete dual-DSP/external/session initialization | Same |

Neither layout meets the rule that every required active workload be qualified. B is not rejected merely because unsupported malformed states differ, but those tests remain visible and global reachability is not overclaimed. A's stronger robustness does not waive its core1/system gaps. No new Plaits port is admitted.

## 11. Evidence files and reproducibility

All results live under phase20i-authentic-qualification (local-only reference: `builds/phase20i-authentic-qualification`; not distributed). Key machine-readable files: `provenance.json`, `authentic-ARM-workload.json`, `authentic-transitions.json`, `long-comparison.json`, `qualification-summary.json`, `core1-results.json`, `regressions.json`, `audit-tool-provenance.json`, `verification.json`; subdirectories `long-original`, `long-osc_only`, `long-osc_va`, `core1`, `preserved-fixture-arm`, `native-regression-jobs` retain actual inputs/outputs/traces.

Source: [environment.py](<../plaits/poc/authentic_qualification/environment.py>), [workload.py](<../plaits/poc/authentic_qualification/workload.py>), [transitions.py](<../plaits/poc/authentic_qualification/transitions.py>), [native_regress.py](<../plaits/poc/authentic_qualification/native_regress.py>), [core1_probe.py](<../plaits/poc/authentic_qualification/core1_probe.py>), [compare.py](<../plaits/poc/authentic_qualification/compare.py>), [finalize.py](<../plaits/poc/authentic_qualification/finalize.py>). `instrument_tool.py` builds the CIRCUIT-only wrapper against pinned installed libraries. Run with the pinned-package Python and `-B`. Read-only guards reject reference writes; 451 protected reference inputs and all 183 pinned Plaits source files verify unchanged.

Exact remaining artifact gap: no coherent DSP X/Y/shared/external-memory image, or equivalent verified initialization stream, aligned to this ARM session. The installed ARM dumps alone do not supply it, and the single-core tool does not implement the missing coupled feedback. A further static identity check cannot close that gap.

QUALIFIED PLAITS SHARED-CODE P BUDGET = UNQUALIFIED
Smallest missing experiment: one offline coupled core-0/core-1 baseline replay with real DSP/SPI readback and provenance-qualified shared/external data that produces non-silent retained master audio, followed by the same A/B comparisons.
