> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Layout A: coupled offline replay qualification

Date: 2026-10-15. **Decision: UNQUALIFIED.** Layout B was not pursued. No Plaits port, application image, firmware package, hardware access or reference-repository change was made.

The high-address storage defect is repaired in an experimental harness. Actual B1.3 programs now execute together, including stock handshake/wait instructions. However, the strict baseline stops on its first stock wavetable read, before completing one audio block. A separate 8,192-iteration synchronization test also retains a failing immediate-completion assertion. Neither result admits Layout A.

Confidence terms: **PROVEN** means directly observed in the stated offline experiment; **STRONG INFERENCE** means supported interpretation with an explicit remaining assumption; **UNKNOWN** means the qualification evidence is missing. These labels do not establish physical memory ownership.

## 1. Root cause of the old address probes

**PROVEN — HARNESS LIMITATION / MISSING EXTERNAL MEMORY BACKING.** The installed CLI constructs `Memory mem(mv, 0x80000)` in `cmdRun`. All three spaces therefore have only `$80000` words. The non-MMU constructor also sets `m_bridgedMemoryAddress = _memSize`.

In `Memory::memTranslateAddress`, without MMU support:

```cpp
auto o = static_cast<int32_t>(_addr - m_bridgedMemoryAddress);
o >>= 24;
_area = static_cast<EMemArea>(_area & o);
```

For `$340000` and `$E80000`, `o` becomes zero and the area becomes P. `Memory::get` then returns zero because the offset exceeds `size(P)`. `Memory::dspWrite` executes its store only when `_offset < size(_area)` but still returns true afterward. Thus the old write/read probe could appear to succeed while discarding the write.

Exact sources:

- dsptool.cpp:cmdRun (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/dsptool/dsptool.cpp:55`; not distributed).
- memory.cpp:constructors, dspWrite, get, memTranslateAddress (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/ext/dsp56300/source/dsp56kEmu/memory.cpp:24`; not distributed), especially lines 125, 159–165, 181–195 and 397 onward.
- memory.h:Memory, calcXYMemSize, calcPMemSize (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/ext/dsp56300/source/dsp56kEmu/memory.h:102`; not distributed).

This is not evidence that either hardware address is invalid. It is not an address-register truncation failure. The emulator retains 24-bit register/address machinery: types.h:RegType (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/ext/dsp56300/source/dsp56kEmu/types.h:32`; not distributed) and agu.h:updateAddressRegister (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/ext/dsp56300/source/dsp56kEmu/agu.h:29`; not distributed). Its existing AGU implementation was not changed.

**PROVEN:** the experimental DSP instruction test writes `$5A1234/$AB5678` through Y:`$340000/$340001`, reads `$5A1200/$AB5600`, and observes those values from core 1's X view. Y:`$E80000` also stores/reads `$AB5600`. A separate `M0=3, R0=$340003` test wraps post-increment to `$340000`, preserving the high address. These prove the implemented contract, not every physical decoder mode. Evidence: address probe (local-only reference: `builds/phase20j-coupled-replay/address-probe/output.txt`; not distributed) and modulo probe (local-only reference: `builds/phase20j-coupled-replay/modulo-probe/output.txt`; not distributed).

## 2. Harness changes and their limits

Source: [build_coupled.py](<../plaits/poc/authentic_qualification/build_coupled.py>), [coupled.cpp](<../plaits/poc/authentic_qualification/coupled.cpp>) and [coupled_replay.py](<../plaits/poc/authentic_qualification/coupled_replay.py>).

The builder creates CIRCUIT-only copies of the pinned `memory.cpp` and `dsp.cpp`. Other implementation objects come from the installed pinned static libraries. It retains the `Memory` class layout and changes these boundaries:

1. `Memory::get/dspWrite` consult a declared-range bus before the original fallback translation. Private low memory remains separate for each DSP. Shared X and declared external data use shared backing.
2. External words have individual initialization-validity bits. An uninitialized read or an undeclared address terminates the run; neither returns a fabricated zero.
3. `Memory::getOpcode` yields through Windows fibers at every interpreter fetch. This includes instructions inside the interpreter's recursively executed DO loops. Each core resumes its own interpreter call stack. No stock or B1.3 wait instruction is removed.
4. The copied `DSP::findExecPeripheralsFunc` admits the experimental synchronous ICC adapter by returning `dspExecNop` for its periodic peripheral callback. It does not install a real DSP56724 peripheral implementation. ESAI/DMA/interrupt timing remains modeled or absent.
5. Runtime P reads/writes/fetches are guarded; region/shared canaries are checked. The vpre 15-register contract and core-1 R5/M5 task contract have explicit checks.

**PROVEN:** branch-to-free-P and branch-to-free-P from inside a DO body both terminate with `FREE_P_EXECUTION`; a post-audit P write terminates with `CANDIDATE_P_WRITE`. Unknown/unbacked external reads and an instruction-limit/deadlock case also terminate. Exact negative fixtures remain under `builds/phase20j-coupled-replay/reject-{branch,inner-do,pwrite,unknown,unbacked,deadlock}/`.

**UNKNOWN:** complete physical address decoding, all low-peripheral behavior, interrupt delivery and hardware bus timing. This is not a complete DSP56724 machine emulator. The native low allocation is still larger than demonstrated physical private SRAM; its unused addresses are not newly claimed as usable memory.

The experimental wrappers at P:`$7000` are host-controlled call fixtures, as in the reference runner. They are not included in any physical P budget, firmware layout or ownership claim.

## 3. Memory map and initialization provenance

Ranges below are inclusive. External values are represented as 24-bit DSP words with mask `$FFFF00`: sixteen useful bits in bits 23:8. The physical-width interpretation is a **STRONG INFERENCE** from the reference's recorded readbacks and capture format, not a new hardware measurement. X/Y aliasing of the modeled external bus is also an explicit model assumption awaiting complete decoder qualification.

| Range / role | Width / visibility | Initialization classification | Reader/writer and persistence |
|---|---|---|---|
| Core-private low X/Y | Native emulator 24-bit, separate per core | DERIVED where boot/init writes execute; reset zeros elsewhere MODELED | Native DSP instructions and actual ARM-emitted controls; persists across calls. Not a hardware ownership allocation. |
| X:`$30000–$37FFF`, shared communication | 24-bit, common to both cores | DERIVED from core-0 boot clearing the entire bank | Core 0 publishes requests/state; core 1 replaces gather addresses with values and publishes task results; survives blocks. |
| External `$80000–$FFFFF`, stock delay region | 16 useful bits; modeled shared X/Y bus | DERIVED: actual stock boot writes every word to zero | Stock retained DSP paths; persists across blocks. Physical purpose beyond observed boot/use remains an inference. |
| External `$173000–$174FFF`, first requested wave pair | 16 useful bits in model; shared X/Y bus | **UNKNOWN**, all validity bits initially false | Core 1 stock gather reads; first read aborts. Nothing invents table payload. |
| Y:`$340000–$37FFFF`, granular/glitch ring | 16 useful bits; shared bus | Written data DERIVED from executed core-1 writer; its test MIN input is MODELED | Core 1 writes 32 stereo frames per CNT event; ring persists and wraps. Unwritten words remain unknown. |
| Y:`$E80000–$EA87FF`, capture candidate | 16 useful bits; shared bus | UNKNOWN until a write, except explicit MODELED probe word | Probe exercises storage. Complete capture workload has not executed. Other replacement slots are not backed or claimed. |
| X:`$FFFE00–$FFFF7F`, low peripheral bank | Core-private 24-bit latch model | Executed boot writes DERIVED; behavioral semantics **UNKNOWN** | Includes observed stock stores at `$FFFF7D`, `$FFFE00`, `$FFFE6B`, `$FFFE4B`, etc. Unwritten reads reject. |
| Y:`$FFFFD0/$FFFFD1/$FFFFD4/$FFFFD7` | 24-bit modeled ICC registers | MODELED reset/register behavior | Request/acknowledge and peer gather progress, described below. |

Each allocated external vector and the shared-X vector has two host guard words `$5A1234`. Unknown/unmapped address guards supplement those canaries. There is no flat zero-filled 24-bit address array. Region content and validity persist across every primitive iteration.

**PROVEN:** stock boot's short immediate `move #$8,y0` produces `$080000`, not integer 8. The `do y0` at P:`$25EC` clears **524,288 words**, starting X:`$80000`. The initial experimental eight-word region correctly failed on its ninth write; this exposed the actual required span. The expanded span follows executed stock semantics rather than hiding the overrun. The program bytes are in reference-core0.be24 (local-only reference: `builds/phase20d-midi-vpre/fixture/reference-core0.be24`; not distributed), P:`$25E8–$25EE`.

Initialization evidence: granular_dsp.py:GB, RL, RN, SHA, SHB, SHT, CAP_BASE (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/granular_dsp.py:38`; not distributed); NOTAS.md:external memory readbacks (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md:1499`; not distributed); NOTAS.md:capture file format (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md:1557`; not distributed).

The ARM flash and SRAM dumps contain authentic ARM bytes, not an external DSP SDRAM image. Searching the pinned reference assets did not locate the requested stock wave payload. The reference independently states that the application lacks these tables: NOTAS.md:stock wavetable study (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md:868`; not distributed). The existing MIDI/granular regression fixtures use synthetic audio buffers; they are not authentic replacements for these tables. A local SD backup contains session/pack files, but no address-provenanced stock synth wave fixture was established from it; it was not substituted.

## 4. Coupled execution and synchronization evidence

Actual program inputs, copied byte-for-byte into the experiment:

- Core 0: 16,365 words, SHA-256 `64034810b65a6df258333154af8753de09caa8cd4cddb8b7cd8514aab52ddd5b`.
- Core 1: 2,047 words, SHA-256 `b93a959b0793578385dd46e482fde16501771c0793180a0350dfd2c3a87466bf`.

They match the previous verified B1.3 analysis streams. Source/input/build hashes are recorded in build-provenance.json (local-only reference: `builds/phase20j-coupled-replay/build-provenance.json`; not distributed) and artifact-hashes.json (local-only reference: `builds/phase20j-coupled-replay/artifact-hashes.json`; not distributed).

The scheduler alternates opcode fetches one-for-one during coupled calls. The fibers preserve DO call stacks and do not reset either core between events. `ICC::read/write` currently models peer D0 as local D1 and peer D7 as local D4. Other peripheral registers are latches. This mapping is an execution-supported model, not a complete peripheral specification.

**PROVEN:** actual stock handshake executes:

- Core 0 P:`$768–$76F`: raise bit 23, wait for peer acknowledgment, publish/reset list pointer, clear request, wait for peer acknowledgment to clear.
- Core 1 P:`$10E–$116`: observe request, acknowledge, wait for request clear, reload R5, clear acknowledgment.
- Core 1 P:`$117–$128`: calculate pending list length, fetch X:`(R5)` as an address, read X:`(R0)`, replace the shared request with its value, publish R5 progress.
- Core 0 P:`$775–$77D`: compare peer progress with its requested sample count.
- Core 1 P:`$12A → $16C`: dispatch real B1.3 tasks and return to the stock loop.

Evidence: retained-core1.be24 (local-only reference: `builds/phase20g-dual-allocation/retained-core1.be24`; not distributed), first primitive traffic (local-only reference: `builds/phase20j-coupled-replay/sync-primitives/first-traffic.txt`; not distributed) and baseline traffic (local-only reference: `builds/phase20j-coupled-replay/original-8/traffic.txt`; not distributed). Trace instruction PCs identify the executed instruction; fault PCs in stderr can show the incremented PC.

### Preserved failing synchronization regression

The separate primitive test publishes two explicitly MODELED, nonzero external words, calls the actual stock reset/wait routines and runs actual core-1 tasks. It repeats 8,192 times without a core reset. An additional 2,048 core-1 instructions per iteration are a diagnostic drain, not an equivalent replacement for the stock wait.

| Observation | Result |
|---|---:|
| Immediate gather equality when the stock wait returns | **1 / 8,192** |
| Eventual gather equality after the additional diagnostic service | 8,192 / 8,192 |
| Exact 32-frame stereo ring blocks from modeled MIN input | 8,192 / 8,192 |
| Region/shared canary checks | 8,192 / 8,192 |
| Core-1 R5/M5 task contract checks | 581,594, no mismatch |
| Post-audit P writes in this primitive test | 0 |

**PROVEN:** this test fails. `coupled_replay.py synchronization()` still asserts immediate equality; its process exits with an assertion failure. result.json (local-only reference: `builds/phase20j-coupled-replay/sync-primitives/result.json`; not distributed) explicitly records `passed: false`. The full stdout is preserved.

**STRONG INFERENCE:** the modeled progress register retains the preceding list's end value across reset, allowing the very short synthetic producer to return before core 1 updates progress for the new list. The first/last traffic logs demonstrate that sequence. **UNKNOWN:** whether missing ICC side effects, missing bus timing, or a synthetic publication schedule unlike stock audio is the decisive cause. No forced progress clear, extra delay, wait NOP or skipped assertion was introduced to declare success. Eventual equality does not resolve this regression.

## 5. Strict baseline audio attempt

The baseline executes real core-1 startup at P:`$100`, core-0 boot at `$107`, and real post-init continuation through `$25F3` to `$113`. Actual ARM-derived initialization/control writes from the prior verified fixture are replayed. Additional authentic-snapshot ARM calls request Synth1 note 60, Synth2 note 67, drum note 36, and retained MIDI1 line selection. Their emitted commands are preserved in additional-ARM-stimulus.json (local-only reference: `builds/phase20j-coupled-replay/original-8/additional-ARM-stimulus.json`; not distributed). Requested notes are not proof of completed audio or distinct voice allocation.

The input stimulus is a declared MODELED stereo sine signal, 220/330 Hz, amplitude `$80000`, at the reference input-ring address. The scheduled longer fixture retains its ARM mode/restore/automation events, but none after block 0 is claimed executed.

**PROVEN:** core-0 initialization completed after 758,789 fetch steps while core 1 also ran; post-init continuation completed after another 5,464. During audio block 0, core 0 published `$173000` into shared X:`$30002`. Core 1 loaded it at P:`$120` and attempted X:`(R0)` at `$125`. The range exists but its first word is uninitialized, so the runner terminates with:

```text
FAIL UNKNOWN_EXTERNAL_READ block=0 core=1 pc=000126 space=1 addr=173000
```

Evidence: baseline output (local-only reference: `builds/phase20j-coupled-replay/original-8/output.txt`; not distributed) and its traffic log. The reference's independent stock-wave analysis identifies `$173000` and `$174000` as two 4,096-word tables requested by a stock Synth1 note, with table format/mipmap mapping not fully established.

| Required baseline statistic | Result |
|---|---|
| Completed core-0 audio blocks | **0** |
| First attempted block | 0, aborted |
| Peak / RMS / nonzero sample count | Not measurable from a completed master buffer |
| First nonzero master block | UNKNOWN |
| Final completed master buffer/state | Unavailable |

This is not a silent baseline pass. No Layout A audio comparison was launched. A guessed sine, random table or zero wave payload was not substituted. The old all-zero master snapshots therefore remain invalid qualification evidence; this run exposes a concrete missing input instead of reproducing their silence.

## 6. Comparison, long run, P ownership and retained state

**UNKNOWN:** all requested coupled retained-audio comparisons, including Synth1, Synth2, drums, MIDI retained modes, mixer/sends, Master FX, capture/glitch and vpre caller preservation in an actual completed audio block. The first block stops before these claims can be established. Reference ARM SPI replies still use the previous zero-response adapter, and storage/RTOS boundaries retain the earlier explicit models. These are additional authenticity limits.

The 8,192-iteration test is a bus/service/ring diagnostic, **not 8,192 consecutive core-0 audio blocks**. It does not satisfy the long-run audio gate. It retains its failure rather than promoting loop completion to regression success.

Trace support records private/shared/external/P reads and writes while enabled, labels HOST versus DSP accesses, and covers instruction fetches inside DO. The failed baseline's audio prefix is fully logged. The long primitive run retains first/last full traffic, cumulative access/traffic hashes and counters; it does not retain a per-access log of every middle iteration. No full-workload trace or equality claim is made from those aggregates.

Program ownership remains unchanged from the allocation study:

| Quantity | Value |
|---|---:|
| Original B1.3 core-0 words | 16,365 (`$3FED`) |
| Layout A words | 15,290 (`$3BBA`) |
| Conservative deletion | 1,075 words |
| Original existing tail | 19 words |
| Candidate contiguous range | P:`$3BBA–$3FFF`, 1,094 addresses |
| Newly qualified Plaits shared-code budget | **None** |

The candidate span includes the original 19-word tail; that arithmetic does not qualify either its use or the 1,075-word deletion. Guard negative tests demonstrate detection, not absence of every loader/interrupt/service/indirect access in an unexecuted workload. No synthetic stock-synth overlay was counted.

## 7. Final gates

| Gate | Confidence | Finding |
|---|---|---|
| L1 — external Y addressing semantics | STRONG INFERENCE | High-address linear/modulo storage tests work; width and shared external decoder model still have physical assumptions. |
| L2 — coupled programs for tested workload | UNKNOWN | Actual boot/handshake runs; complete audio blocked; synthetic immediate-completion regression fails. |
| L3 — non-silent retained master baseline | UNKNOWN | No complete master block. |
| L4 — active Synth1 equality | UNKNOWN | No coupled baseline/A comparison. |
| L5 — active Synth2 equality | UNKNOWN | No coupled baseline/A comparison. |
| L6 — drums equality | UNKNOWN | No coupled baseline/A comparison. |
| L7 — retained MIDI equality | UNKNOWN | No coupled baseline/A comparison. |
| L8 — mixer/Master FX equality | UNKNOWN | No completed coupled audio path. |
| L9 — shared/core-1 equality | UNKNOWN | Eventual primitive/ring data exact; immediate completion fails; no full regression. |
| L10 — candidate P untouched/stable | UNKNOWN | Guard tests work; complete reduced-layout replay not performed. |
| L11 — long replay without divergence | UNKNOWN | Only primitive iterations completed; their immediate-completion assertion fails. |
| L12 — external initialization authentic enough | UNKNOWN | Stock wave payload missing; modeled probes are not authentic audio assets. |

Machine-readable evidence: qualification.json (local-only reference: `builds/phase20j-coupled-replay/qualification.json`; not distributed). Verification rehashed all **451 previously protected reference inputs**, with no changes. This is a scoped input verification, not a claim about every file in the reference tree. All experimental source, executable, scripts, raw DSP copies and logs are under CIRCUIT.

The next prerequisite is authentic external lookup data for the actual stock patch, beginning with addressed words `$173000–$174FFF`, together with original word packing/loading provenance. First rerun one actual stock audio block with that fixture and inspect both gather completion and the master output. More tables or sample payload may then be requested; this first pair is the smallest demonstrated missing artifact, not a promise that it alone qualifies the complete workload.

QUALIFIED PLAITS SHARED-CODE P BUDGET = UNQUALIFIED

Smallest demonstrated missing artifact: an authenticated, address-provenanced payload for the stock `$173000/$174000` lookup-table pair; use it for the first strict coupled audio block before expanding the replay.
