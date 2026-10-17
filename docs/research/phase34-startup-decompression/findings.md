> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase34 — startup decompression and cold-boot continuation

**PROVEN:** the phase33 decompression stop is caused by an all-address Unicorn RAM-read hook. An entirely empty read callback reproduces both stops with unchanged inputs. Removing that RAM read hook, or restricting it to peripheral addresses, lets the **real unmodified decompressor** return. The fix is in [trace.py](<../../../builds/phase34-startup-decompression/trace.py>), not firmware. No destination bytes, dictionary, decompressed output, instruction changes or PC jump past decompression are used. No missing original QSPI bytes are supplied to repair decompression.

**UNKNOWN — full cold boot:** the corrected execution progresses through startup and native object initialization, but a stable normal USB/MIDI-ready state is not reached. With explicit peripheral models, application startup waits for SDMMC completion at`$0801C63C`; bootloader startup requires SVC/RTOS exception service at`$080031C2` (Unicorn reports exception at the following`$080031C4`). Main/Storage task entry execution is not qualified. H1/H2/P2/P3 remain UNKNOWN; this is not evidence of a hardware/firmware boot failure.

## Exact old stop, authentic input and fixture cause

| Item | Bootloader | Application | Confidence |

|---|---|---|---|

| Real decompressor | `$0800927C` | `$080596C4` | PROVEN |

| Old failure PC | `$0800929E`, nativeBNE, Unicorn invalid instruction | `$08059706`, back-reference LDRB attempts`$1FFFFFB0` | PROVEN |

| Scatter descriptor | `$08009694` | `$0805B7C8` | PROVEN |

| Descriptor bytes | `f0030000ea06000004000020` | `fc0b00002c14000000000020` | PROVEN |

| Compressed input | `[$08009A84,$08009DF9)`;885 bytes | `[$0805C3C4,$0805CDDA)`;2,582 bytes | PROVEN |

| Destination | `$20000004` | `$20000000` | PROVEN |

| Correct output size |11,084 bytes; ends`$20002B50` |15,618 bytes; ends`$20003D02` | PROVEN native/oracle agreement |

| Native return to scatter caller | `$08009620` | `$0805B5A8` | PROVEN |

**PROVEN:** descriptor word0 is a relative source displacement, word1 encodes compressed size and destination-relocation flag, word2 is the destination. Output length is **derived independently from the compressed stream**, not misrepresented as a stored length field. [oracle.py](<../../../builds/phase34-startup-decompression/oracle.py>) implements token/literal/back-reference decoding, including the native pre-decrement literal-length bias. All back-references use bytes already emitted by the same block. It requires no external dictionary or prior RAM contents and never injects output.

**PROVEN:** boot compressed bytes come from the pinned boot flash dump; application compressed bytes come from the verified published/stock flash span. legacy-fault-detail.json (local-only reference: `builds/phase34-startup-decompression/legacy-fault-detail.json`; not distributed) records each variant's complete R0–R12,SP,LR,xPSR, source/destination, source hash, descriptor,64-byte RAM windows, native call history, MMIO state and runtime fields. The recorded call history is a sequence of observed call sites, not an invented symbolic stack unwind. Boot path is reset`$080098C8`→runtime`$0800990C`→scatter`$08009608`→indirect call`$0800927C`; application is reset`$0805C00C`→runtime/scatter`$0805C19C/$0805B590`→indirect call`$080596C4`. These startup stages precede Storage/Main task execution.

**PROVEN — ablation:** isolation.json (local-only reference: `builds/phase34-startup-decompression/isolation.json`; not distributed) contains36 reset experiments covering both variants/entries and SP/MSP/CONTROL/IPSR initialization and no-op hooks. SP/MSP/CONTROL/IPSR changes do not reproduce the stop. Merely registering an all-address read hook does. Code-only and peripheral-bounded traces advance. The all-address write hook is unnecessary for this investigation and is also removed from corrected tracing; isolated decompressor write-only tests return correctly, so this report does not attribute the read-hook defect to every write hook.

**PROVEN — isolated native control:** instruction-control.json (local-only reference: `builds/phase34-startup-decompression/instruction-control.json`; not distributed) calls each exact native function with identical authenticated descriptor/source and physical SRAM. No-hook, write-only and peripheral-bounded controls return and match the independent oracle. A no-op all-address read hook alone reproduces failure. Application first control-flow divergence is trace index19: control executes`$080596E4` (literal-loop pre-decrement); hooked execution goes to`$080596E8`, then derives an invalid history address. Boot failure ends with xPSR`$61000800`, containing residual ThumbIT state, at the BNE reported above. **STRONG INFERENCE:** memory-hook interaction with Thumb conditional execution/state synchronization is the internal Unicorn defect. **UNKNOWN:** the exact C-library implementation defect; no patched DLL or generic engine fix is claimed.

**PROVEN:** phase33's apparent missing address`$1FFFFFB0` is an invalid decompression history access under the faulty observer, not a missing firmware ROM region to map. No mapping there was added. ROM/flash input, reset RAM, aliasing, DMA completion, RTOS service, external storage, interrupt and cache state were not missing dependencies of this decompressor: it executes identically with authentic flash input and its own local history once the faulty read observer is removed.

## Correction verification

**PROVEN:** corrected memory hooks cover MCU peripherals`$40000000–$4002FFFF`, QUADSPI`$A0001000–$A0001FFF`, system/debug registers, and internal-flash stores. They do not cover SRAM reads or writes. Host `mem_read` snapshots and code hooks retain descriptor/output/register evidence. Flash code hashes before/after execution must match. No application code, diagnostic path or pinned/reference file is modified. No-PC-skip native returns and decompressed bytes are checked separately.

**PROVEN:** eight corrected full-reset prefix controls (stock/diagnostic×boot/application×no-memory-hook/bounded-hook) return from decompression. Corrected and uninstrumented controls have identical decompressed hashes and complete SRAM checkpoint hashes within each entry/variant. Four A5-poisoned SRAM controls also return with the same output; no dictionary/history initialization is assumed. The independent oracle matches all eight native outputs exactly:

- Boot output SHA-256:`7e6f9f2ef9ae96a8ab8cf3f0b11b5df1520aad4bc483f559682525540b48bd18`.

- Application output SHA-256:`2db584abde65123402067c89720f5a10e12c40650b700d6af2f13ed93743e04f`.

## Subsequent authentic control flow and explicit service models

**PROVEN:** without an oscillator model, native stock and diagnostic next wait at RCC HSE readiness: boot`$080034CE`, app`$0801B266`. clock-progress.json (local-only reference: `builds/phase34-startup-decompression/clock-progress.json`; not distributed) adds a separate **ideal** RCC model: oscillator/PLL ready follows enable, SWS follows SW. It changes peripheral register responses, not firmware branches. Physical startup delays, clock faults and timing are UNKNOWN; this is not the decompression fix or a hardware timing measurement.

**PROVEN within the model:** the next real operations are NOR F5/35/B7 initialization, then AF/QPIID with DLR2. nor-progress.json (local-only reference: `builds/phase34-startup-decompression/nor-progress.json`; not distributed) supplies ideal completion only for those three data-free mode commands and executes native QSPI IRQ vectors`$080090B5` (boot) or`$080573E1` (application). Controller software flags are written by those native handlers, not forced by the host. IRQ execution uses an explicitly modeled basic register frame/return wrapper; it is not a complete Cortex-M interrupt controller, scheduler or FPU exception model. No array bytes or metadata are synthesized.

**PROVEN as manufacturer documentation:** AF returns C2/20/19 for the reference project's MX25L25645G, matching its9F identity. [Macronix identity table](https://www.mxic.com.tw/Lists/Datasheet/Attachments/9234/MX25L25645G%2C%203V%2C%20256Mb%2C%20v1.3.pdf). **UNKNOWN:** identity of the user's unit. reference-identity-progress.json (local-only reference: `builds/phase34-startup-decompression/reference-identity-progress.json`; not distributed) is explicitly conditional on that documented reference-part response. The real firmware reads these three bytes through the modeled FIFO; no final destination structure is injected.

**PROVEN within the conditional model:** tick-progress.json (local-only reference: `builds/phase34-startup-decompression/tick-progress.json`; not distributed) services the **native SysTick handler** when enabled, at an ideal deterministic instruction cadence. Time increments are performed by native handler instructions; no timer/global counter is directly advanced by the fixture. This is not measured MCU timing. Startup progresses beyond the native100-tick delay. B13-control.json (local-only reference: `builds/phase34-startup-decompression/B13-control.json`; not distributed) additionally uses unmodified published B1.3, so the control is not limited to factory stock versus a B1.3-based candidate. Full SRAM hashes at the reached checkpoints match across factory stock, unchanged B1.3 and diagnostic.

| Entry | Furthest checkpoint | What is not yet established | Confidence |

|---|---|---|---|

| Application, stock/B1.3/diagnostic | SD command wait`$0801C63C`, object`$20005548`, busy flag bit1 remains set; native Main setup`$0801DDD4` has run | SDMMC completion/status model and full initialization; Main`$0801D4B0` and Storage`$0805767C` entry execution, normal user state and diagnostic reception | PROVEN prefix; remainder UNKNOWN |

| Bootloader, stock/B1.3/diagnostic | Scheduler start executes SVC`$080031C2`; exception reported at31C4 | Exception entry/return, native SVC handler`$08003188`, PSP/task-frame restoration, PendSV and actual bootloader main task | PROVEN prefix; remainder UNKNOWN |

**PROVEN:** `$40012C00` is **SDMMC1**, as defined by the exact [STM32F745 header](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-f7/master/Include/stm32f745xx.h). The wait writes ICR`+$38` and MASK`+$3C` through`$0801C646`, then polls its software command-completion flag. This corrects the temporary commentary identification as I2C. The missing service is not a table/decompressor dictionary. No SD card response, absent-card timeout, successful mount or project contents are invented to advance it.

**UNKNOWN:** no stable Main/Storage/USB-ready application checkpoint was reached. Task object creation is not task execution. Diagnostic hook bytes exist unchanged in the memory candidate; installation/registration of a live callable diagnostic service after full boot remains unqualified. No automatic diagnostic read occurs in the observed prefix; absence over the unexecuted suffix is UNKNOWN.

## Persistent tracing, installation and restart gates

**PROVEN observed-prefix counts:** target QSPI reads0, writes0, erase overlaps0. Observed NOR commands are mode setup and identification, not array reads/program/erase. MMIO and native-command logs are retained. **UNKNOWN complete-boot counts:** reads UNKNOWN, writes UNKNOWN, erase overlaps UNKNOWN. The unexecuted SD/storage/project/background suffix is not assigned zero counts.

**PROVEN carried-forward selected install evidence:** phase33 still logs13,801 NOR writes,109 sector erases and zero target write/erase overlaps;110,400 internal word-program calls produce exact installed bytes. Its installer uses code hooks rather than the failing global RAM-read hook. Evidence files remain unchanged. **UNKNOWN H1:** repaired decompression alone does not supply native SVC/PendSV boot scheduling, full host/updater/worker coupling, boot constructors/background/SD closure or complete reset transition. The coupled installation path therefore remains incomplete; no broader zero-write assertion replaces the scoped phase33 result.

**PROVEN partial reset:** restart-prefix.json (local-only reference: `builds/phase34-startup-decompression/restart-prefix.json`; not distributed) starts six fresh MCU instances with adverse SRAM seeds derived from the recorded TEF0/4/7 and missing0/4/7 states. Old CPU/peripheral/task contexts are not restored. Actual startup decompression, zero-initialization and constructors execute; no failed-session cleanup is called. Each prefix reconstructs wrapper`$2000AC94`, backend`$20000378`, Storage holder`$20008D38`: semaphore1, sync0, pending0, Storage flags0, Main flags0, DMA EN0 and NDTR0. This is stronger than merely clearing emulator maps. Raw-buffer bytes clear in these tested runs, but bytes alone are not an ownership contract.

**UNKNOWN P2/P3:** these restarts stop at the same SDMMC boundary. Live parser ownership, complete diagnostic state, Main/Storage task operation, DSP startup and post-ready controller use are not established. No second diagnostic request is attempted in a failed boot. Full restart target-byte preservation cannot be concluded before the unexecuted persistent operations are traced.

| Gate | Result | Reason |

|---|---|---|

| H1 complete installation preserves target | UNKNOWN | Selected model unchanged and zero-overlap; full boot/scheduling/update closure incomplete |

| H2 complete first boot preserves target | UNKNOWN | Decompression repaired; no normal user-ready endpoint |

| P1 diagnostic causes no persistent mutation | PROVEN within previously tested diagnostic graph | Prior seven-case evidence preserved; scope unchanged |

| P2 cold restart clears all ownership | UNKNOWN | Native prefix now reconstructs key fields; full state/task/parser contract incomplete |

| P3 target survives complete failure/restart | UNKNOWN | Prefix has no target mutations; complete boot suffix missing |

| P4 bootloader/recovery code unchanged | PROVEN | Code immutable in all new runs; prior recovery predicate evidence preserved |

**UNKNOWN remaining offline prerequisites:** faithful basic Cortex-M SVC/EXC_RETURN/PSP/PendSV context transitions, SDMMC status/IRQ/card responses, then actual persistent-storage inputs and background/task coverage. These are model/input gaps, not hardware-only unknowns. **UNKNOWN hardware-only limits:** unit identity, real timing/cache/bus behavior, power-domain removal/reset and unit-specific recovery remain untested. Host containment stays PASS and device H4 stays FAIL for in-session recovery.

**UNKNOWN — smallest next experiment:** isolate the **native bootloader SVC start** at`$080031C2 → $08003188`, using its already natively created task frame to validate architectural exception entry/EXC_RETURN and PSP restoration. Do not force task-ready flags or jump directly to a task. That would enable authentic bootloader task execution and is the prerequisite for closing the install/reset path; it is not a firmware or diagnostic redesign.

QSPI PRESERVATION / COLD-BOOT MODEL = UNQUALIFIED
