> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# QSPI $82000–$821FF preservation and one-shot power-cycle qualification

**UNKNOWN — overall qualification remains UNQUALIFIED.** The selected all-block updater/NOR algorithms and native boot validator/installer preserve a synthetic target, and the seven diagnostic outcomes issue no persistent mutations in their selected graph. A full cold restart to normal USB/MIDI-ready application state has **not** been executed. H1/H2/P2/P3 therefore cannot be promoted from partial evidence.

**PROVEN:** no hardware access, firmware/SYX export, reference/pinned-source changes or Plaits implementation occurred. The phase30 device architecture and phase32 host containment are unchanged. An application exists only in emulator memory for this experiment; no hardware-test candidate is generated. All evidence is under phase33-preservation-powercycle (local-only reference: `builds/phase33-preservation-powercycle`; not distributed).

## Physical address map

All intervals here are half-open unless written with an inclusive dash. NOR addresses are **chip byte offsets**, not internal STM32 addresses.

| Physical storage | Range | Purpose / evidence | Confidence |
|---|---|---|---|
| STM32 internal flash | `[$08000000,$08010000)` | Existing64KiB bootloader, unchanged | PROVEN |
| STM32 internal flash | `[$08010000,$08080000)` | Application sector allocation; installed payload starts08010000 | PROVEN |
| STM32 internal flash | `$080101E8–$080101EB` | Planned four-byte version marker, inside version block at080101C8 | PROVEN |
| External NOR | `[$0,$80000)` | Application staging bundle selector0 | PROVEN captured descriptors |
| External NOR | `[$80000,$80017)` |23-byte update selector/version/size/CRC metadata; containing erase sector`[$80000,$81000)` | PROVEN selected graph |
| External NOR | `[$81000,$81017)` | Separate identity/settings metadata;4KiB sector`[$81000,$82000)` | PROVEN static path |
| External NOR | `[$82000,$94000)` | Resource bundle selector2; target is first512 bytes`[$82000,$82200)` | PROVEN captured descriptors |
| External NOR | `[$94000,$D4000)` | Selector3 bundle | PROVEN captured descriptors |
| External NOR | `[$D4000,$2000000)` | Selector1 bundle; captured stock storage bindings | PROVEN captured descriptors |
| SD | Separate backend`$20000338` | Complete startup/mount/project writes not enumerated | UNKNOWN |

**PROVEN:** `tools/ct_fw.py:encode` selects0 and sends INIT71, HEADER7C, WRITE72 blocks1..N−1, FINISH73 vector block0 last. Native application header `$08039088–$08039102` selects `[$20003CC8+4*selector]`; selector2 can address the target, whereas selector0 staging cannot reach it with the modeled image size. Application payload ultimately resides in **internal flash**; it is first staged in **external NOR**. Updater metadata is external; the changed version marker is internal/in staged payload. These are different physical objects.

## Installation execution and persistent operations

**PROVEN within the selected model:** [install.py](<../builds/phase33-preservation-powercycle/install.py>) reuses exact B1.3 COPY/ADD spans and unchanged phase30 ARM builders, planned hook and marker in emulator memory. Logical size441,576 (`$6BCE8`), padded to441,600 (`$6BD00`); append ends`$0807BCE8`. In-memory SHA-256`e7c96a5490facee8a4eb7080604500fb2d32f31fa58923eace70b489cd25f110`; CRC`$9865C64A`. These identify an offline memory fixture, not an exported installable artifact.

**PROVEN:** all13,800 blocks pass both the reference Python pack/unpack and actual ARM unpacker `$08024E20`. Every block is programmed via native backend `$08022FDC`; vector block0 is last. Full native erase loop `$08023078` executes. The model then runs boot metadata decoder `$08003B2A/$08005BE8` and native validator `$08003B9A`, which checks product, size, staged CRC and differing38-byte version block before native installer `$08003C24`. The current installed version is kept B1.3 during admission, so the validator must actually enter the installer.

**PROVEN:** the installer executes **110,400 internal word-program calls**, four effective sector erases and one rejected out-of-range erase call. It must produce exact installed bytes; simply preloading an already-matching application is not accepted as installation evidence. Initial fixture verification exposed that version-equality shortcut; the final runner asserts the observed program/erase counts to prevent it.

| Operation | Routine / command | Start / exclusive end | Granularity and purpose | Target overlap | Confidence |
|---|---|---|---|---:|---|
| NOR payload erase,108 operations | `$08023078 → $08037494`,WREN06 then21 (4-byte form of20) | `$0,$6C000)` |4KiB sectors; prepare selector0 staging |0 | PROVEN model |
| NOR payload program,13,800 operations | `$08022FDC → $080374D4`,WREN06 then12 (4-byte form of02) | `[$0,$6BD00)` |32-byte upload blocks, native256-byte page boundary algorithm |0 | PROVEN model |
| NOR metadata erase,1 operation | Same native erase path,21 | `[$80000,$81000)` |4KiB sector |0 | PROVEN model |
| NOR metadata program,1 operation | Same native program path,12 | `[$80000,$80017)` |23 bytes; selector0/version/size/CRC |0 | PROVEN model |
| Boot staging/metadata reads | `$08003B2A/$08005C10/$08005C68/$08003C24` through modeled storage interface | Staging`[$0,$6BCE8)`/padded32-byte reads to6BD00; metadata80000..80017 | Header/version/CRC/install data | Reads permitted | PROVEN selected model |
| Internal application erase | `$08003C24 → $08006020` | `08010000..08018000`, `08018000..08020000`, `08020000..08040000`, `08040000..08080000` |32KiB/32KiB/128KiB/256KiB effective sectors | Different physical storage | PROVEN model |
| Internal erase request at08080000 | Native wrapper guard offset>=70000 | No erase | Out-of-range no-op | None | PROVEN static guard/model |
| Internal application program | `$08003C24 → $0800605E → $08007FAC` | `[$08010000,$0807BD00)` | Four bytes/call, padded final block | Different physical storage | PROVEN model |
| Identity/settings setter | Boot`$08005DB4`; application`$08025228` | Program`[$81000,$81017)`; erase`[$81000,$82000)` |23 bytes/4KiB; not part of selected normal finalization | No direct overlap; sector ends exactly at target start | PROVEN static path, reachability incomplete |

**PROVEN:** selected modeled totals are **13,801 NOR writes,109 NOR erases; TARGET WRITE COUNT=0; TARGET ERASE OVERLAP=0**. Synthetic target SHA-256 before/after is`3e2a5f93bc6080609236b50b1cbd960f804256b3706be92b55f5a0b25922dbe5`. [installation.json (local-only reference: `builds/phase33-preservation-powercycle/installation.json`; not distributed) logs each operation; address-and-reachability.json (local-only reference: `builds/phase33-preservation-powercycle/address-and-reachability.json`; not distributed) merges footprints and records caller candidates.

**UNKNOWN — complete H1:** this is not the requested fully coupled host SysEx→RTOS/updater state machine→reset constructors→installer→first boot. Scheduling is replaced by the host block schedule and synchronous NOR completion seam. Boot storage objects are constructed explicitly, CRC endpoints modeled, and internal flash erase/program primitives modeled while native validation/installer control flow runs. All boot constructors, background/storage tasks and SD operations are not closed. Zero overlap in this selected graph cannot certify every persistent operation of installation.

**PROVEN — prior-note correction:** phase31 mislabeled the low helper names. `$08037494` is **erase**, `$080374D4` is **program**, as correctly recorded in phase28 and executed here. Phase31 evidence remains unchanged; its six read-failure findings do not depend on those labels.

## First-boot reachability and genuine reset attempt

**PROVEN:** [cold_boot.py](<../builds/phase33-preservation-powercycle/cold_boot.py>) starts from actual vectors with MSP`$20050000`, fresh Cortex-M7 CPU, physical SRAM/peripheral mappings and **no running-RAM snapshot**. Diagnostic and unchanged-stock controls execute. Both zero-filled andA5-filled representative SRAM are tried for the diagnostic. No missing ready/completion flag or coefficient data is fabricated to force a completed boot.

| Reset entry | Observed prefix stop | Coverage | Confidence |
|---|---|---|---|
| Bootloader vector`$080098C9` | Unicorn invalid-instruction exception at`$0800929E`, within startup decompression;11,158 instructions | Same for stock control and both diagnostic SRAM fixtures | PROVEN observation; cause UNKNOWN |
| Application vector`$0805C00D` | Decompression load at`$08059706` accesses unmapped`$1FFFFFB0`;11,719 instructions | Same for stock control and both diagnostic SRAM fixtures | PROVEN observation; cause UNKNOWN |

**STRONG INFERENCE:** the matching stock-control stop indicates an incomplete/incorrect cold-start fixture or emulator semantics rather than evidence of a diagnostic-specific defect. No firmware-failure claim is made. cold-boot-prefix.json (local-only reference: `builds/phase33-preservation-powercycle/cold-boot-prefix.json`; not distributed) records exact PCs/registers/xPSR/accesses. These probes do **not** reach stable normal user state or a USB/MIDI diagnostic command service.

**UNKNOWN — complete first-boot target counts:** READS=UNKNOWN, WRITES=UNKNOWN, ERASE OVERLAP=UNKNOWN. Zero persistent stores observed before these prefix stops is not a zero count for the unexecuted suffix. No post-boot result is fabricated from the captured running-RAM model.

| Required subsystem | What is established | Remaining target-write reachability | Confidence |
|---|---|---|---|
| Reset/initialization | Actual reset prefix above | Constructors and full startup suffix incomplete | UNKNOWN |
| DSP/table initialization | Known coefficient/table initializer`$08035E28` includes stock read path to`$08047C6C`; prior authenticated procedural prefix exists | Full original coefficient/resource service still required; no complete first-boot write closure | UNKNOWN |
| Pack/storage mounting | Captured generic NOR bindings and separate SD backend | Mount/repair/format predicates and producer address domains not fully traced | UNKNOWN |
| Settings restoration | Setter81000 sector does not include82000 | Invocation predicates and any other setters not closed | UNKNOWN |
| Projects/patches | Generic save/program and erase framework remains available | Startup autosave/restore/background behavior not exhaustively executed | UNKNOWN |
| Background Storage | `$08024014` dispatch supports program/erase and read | Cannot assert no queued unrelated write solely from diagnostic read-only behavior | UNKNOWN |
| B1.3 first use | Earlier native`$0805DBDC` private allocation test remains valid | That allocation is not a census of every B1.3 first-use persistent path | UNKNOWN |

## Seven failure/power-cycle cases

**PROVEN:** [powercycle.py](<../builds/phase33-preservation-powercycle/powercycle.py>) executes the unchanged phase30 native diagnostic for successful capture and TEF/missing completion at0/4/7. **42 assertions** pass. Every exercised diagnostic operation is EC read; no NOR program/erase, SD write or internal-flash write is required for diagnostic state. Existing low-level instruction/write guards reject mutating dispatch/flash stores. This is the selected diagnostic graph, not a claim that unrelated background tasks never write storage.

| Case | Native reads issued | State before power removal | Diagnostic persistent writes/erases | Cold restart result | Confidence |
|---|---:|---|---:|---|---|
| A success |8 | Semaphore released; Main returned; exact synthetic result |0 | Fresh reset prefix stops as above | PROVEN bounded model |
| B TEF0 |1 | Semaphore0/sync1/active request retained |0 | Same | PROVEN bounded model |
| C TEF4 |5 | Same |0 | Same | PROVEN bounded model |
| D TEF7 |8 | Same |0 | Same | PROVEN bounded model |
| E missing0 |1 | Same |0 | Same | PROVEN bounded model |
| F missing4 |5 | Same |0 | Same | PROVEN bounded model |
| G missing7 |8 | Same |0 | Same | PROVEN bounded model |

**PROVEN about the abstraction:** each new MCU instance drops the old CPU context, task contexts, Main live frame, DMA/runtime register maps and host transaction object. Initial old-location flags and DMA/QSPI runtime words are zero in the chosen reset fixture. No application cleanup or cross-task release is used. The external synthetic NOR array is retained separately and unchanged in that read-only/reset abstraction.

**UNKNOWN — P2/P3:** making fresh maps is a reset **premise**, not proof that real startup correctly recreates semaphores, queues, task notifications, SysEx ownership, DMA and QSPI state. SRAM need not physically power up as zero; theA5 control does not complete initialization either. Full DSP reset/bootstrap is not executed. The retained synthetic hash cannot certify the unexecuted post-reset storage operations. A second read after a failed request is never attempted in the same boot or falsely admitted through a running-RAM snapshot.

**STRONG INFERENCE:** interrupting an actual read-only EC transaction should not program or erase the NOR array: read commands are distinct from WREN/program/erase, and the exercised diagnostic never issues those. Reference `ctre/README.md:7` identifies MX25L25645G; its official sector-erase section specifies4KiB sectors and requires WREN. MCU controller and DMA state are volatile/resettable. [Macronix MX25L25645G datasheet](https://www.mxic.com.tw/Lists/Datasheet/Attachments/8906/MX25L25645G%2C%203V%2C%20256Mb%2C%20v2.0.pdf), [ST STM32F745 register definitions](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-f7/master/Include/stm32f745xx.h).

**UNKNOWN:** actual unit NOR identity/configuration, analog power-down/up behavior and sufficient power removal for all relevant domains. Manufacturer documentation and a fresh-map model cannot prove those for this unit. More critically, the first-boot suffix might issue unrelated program/erase commands; read-only interruption by itself does not prove P3. No hardware failure probability is invented.

## Recovery application path and gates

**PROVEN:** bootloader bytes`$08000000,$08010000)` match the pinned original byte-for-byte before and after selected installation. The installer bounds exclude them. Native recovery button callback`$08003AB0` is replayed for all8 modeled subsets: only scanner IDs18/8/9 all true set the boot-mode flag. Boot main`$08002FDE`, wait`$08003B66` and branch`$08003000` check that mode before normal application handoff; direct handoff uses`$08003D06`. [recovery.json (local-only reference: `builds/phase33-preservation-powercycle/recovery.json`; not distributed) records these predicate tests.

**STRONG INFERENCE:** an unchanged independently entered bootloader retains the architectural option to accept official application firmware without relying on the diagnostic handler. Reference `docs/NOTAS.md:29` reports the Scales + Preset + Note entry and uploader hardware tests; those are reported reference evidence, not an observation on this unit. **UNKNOWN:** full cold entry, recovery updater installation, button timing/mapping and successful normal diagnostic-app boot after the modeled stuck case. Neither option is an absolute recovery guarantee.

| Gate | Result | Evidence boundary |
|---|---|---|
| H1 installation preserves target | UNKNOWN | Selected all-block native algorithms have0 write/erase overlaps; complete updater/boot constructor/SD closure incomplete |
| H2 first boot preserves target | UNKNOWN | No stable first boot; total target R/W/E counts unknown |
| P1 failed diagnostic issues no persistent mutation | PROVEN | Seven selected native diagnostic cases; excludes unrelated background tasks |
| P2 cold restart clears all stuck ownership | UNKNOWN | Fresh-map premise tested; full native MCU/RTOS/DSP initialization not complete |
| P3 target survives complete restart | UNKNOWN | Read-only interruption consistent with preservation; unexecuted boot suffix remains open |
| P4 bootloader/recovery code unchanged | PROVEN | Pinned64KiB boot bytes unchanged; actual recovery operation remains unknown |

**PROVEN:** H4 remains FAIL for in-session device error recovery; phase32 host containment remains PASS. The intended conditional policy is **ONE REQUEST PER BOOT**. Success preserves validated file/hash and ends the session. Failure produces no evidence file, no retry or cleanup, and requires a full power cycle before another attempt. **UNKNOWN:** this policy is not hardware-qualified until H1/H2/P2/P3 close; a new process or host lease is not proof of a power cycle. No hardware-test candidate generation follows this result.

**UNKNOWN — minimum next offline experiment:** qualify the startup scatter-decompression/reset prefix in isolation against the unchanged stock control, reproducing the current`$0800929E`/`$08059706` stops with the recorded registers and exact source descriptors. Resolve that fixture/emulator boundary without fabricated SRAM or coefficient contents, then resume authentic constructors and persistent-write logging to stable USB/MIDI state. This is a prerequisite to the requested full install/first-boot and post-power-cycle qualification, not a new diagnostic architecture.

QSPI ONE-SHOT HARDWARE MODEL = UNQUALIFIED

## Phase34 — startup observer repaired; complete cold boot still open

**PROVEN:** the phase33 decompression failure is caused by an **all-address Unicorn RAM-read hook**, reproduced even with an empty callback. Restricting memory hooks to peripheral/register and internal-flash-store ranges makes the real, unchanged decompressor return. No firmware patch, PC skip, fabricated dictionary or decompressed-output injection is used. Corrected stock controls pass before diagnostic comparisons.

**PROVEN:** boot descriptor`$08009694`, source`$08009A84`/885bytes, destination`$20000004` produces11,084bytes. Application descriptor`$0805B7C8`, source`$0805C3C4`/2,582bytes, destination`$20000000` produces15,618bytes. Eight native controls match an independent byte-level oracle; four A5-SRAM controls also return. Old stops at`$0800929E`/`$08059706` are observer artifacts, not missing ROM/history/storage inputs. [Phase34 findings](<../docs/research/phase34-startup-decompression/findings.md>) provides registers, call chains, descriptors, hashes, RAM windows and the controlled hook ablation.

**PROVEN within explicit peripheral models:** ideal RCC readiness, native QSPI completion handlers for F5/35/B7, documented reference-part AF identity C22019 and native periodic SysTick advance the prefix further. These assumptions are recorded separately from the proven hook correction. Stock, unchanged B1.3 and diagnostic SRAM checkpoints agree. Application startup reaches an **SDMMC1 command wait at`$0801C63C`**, object`$20005548`, not a decompressor wait. Bootloader reaches SVC scheduler startup`$080031C2`, where architectural exception/context-switch service is missing. Main task setup has executed; Main/Storage task entry execution and normal USB/MIDI-ready state remain UNKNOWN.

**PROVEN observed-prefix target counts:** reads0 / writes0 / erase-overlaps0. **UNKNOWN full-boot counts:** reads UNKNOWN / writes UNKNOWN / erase-overlaps UNKNOWN. No automatic diagnostic array read occurs in the observed prefix. Unexecuted storage mounting/project/background paths are not silently counted as zero.

**PROVEN partial reset:** all six recorded stale-failure SRAM seeds are overwritten/reconstructed by native startup and constructors: semaphore1, sync/pending0, task flags0, DMA EN0/NDTR0. No application cleanup or same-boot retry is used. **UNKNOWN:** complete parser/diagnostic/task/DSP ownership and target preservation beyond the SDMMC stop. Partial native reset evidence does not qualify P2/P3.

**UNKNOWN H1/H2/P2/P3:** complete install/first-boot/reset closure is still missing SVC/PendSV and SDMMC/storage services. Phase33's selected13,801 NOR writes /109 erases still have zero target overlap; that unchanged evidence is not upgraded to a full-install claim. **PROVEN within prior scope:** P1 remains read-only diagnostic behavior; P4 remains unchanged bootloader code. Host containment stays PASS; H4 remains FAIL for in-session device recovery. No firmware generation, hardware access, reference/pinned-source edit or Plaits work occurred.

**UNKNOWN — smallest next offline experiment:** qualify native bootloader SVC entry/EXC_RETURN/PSP restoration from the actual initialized task frame at`$080031C2 → $08003188`, without forcing PC or task-ready flags. See validation (local-only reference: `builds/phase34-startup-decompression/validation.json`; not distributed) and [complete phase34 evidence](<../docs/research/phase34-startup-decompression/findings.md>).

QSPI PRESERVATION / COLD-BOOT MODEL = UNQUALIFIED

## Phase35 — native bootloader SVC and PSP restoration qualified

**PROVEN within the observed privileged basic-frame path:** stock first, then diagnostic execute the same native scheduler-start SVC `$080031C2`. Before entry: MSP=`$20050000`, PSP=0, CONTROL=0, LR=`$08002E2B`, PRIMASK/FAULTMASK=0, BASEPRI=`$C0`, xPSR=`$61000000`. SVC priority0 is unmasked. VTOR `$08000000`, vector `$0800002C → $08003189`. Architectural entry stacks eight words at MSP `$2004FFE0`, LR=`$FFFFFFF9`, IPSR=11; the actual handler executes unchanged.

**PROVEN:** native frame constructor `$08002D3C` creates the first task context; no host task frame is injected. Current-TCB global `$20005268` points to IDLE TCB `$20007EB8`, whose saved context is `$20007E6C`. Native `$0800318E` loads r4-r11/LR, and native `$08003192` restores PSP=`$20007E90`. BX LR uses the task's `$FFFFFFFD`; architectural unstack consumes the native frame once, restoring PC=`$08002A58`, PSP/SP=`$20007EB0`, CONTROL=2, privileged Thread mode. Original MSP SVC frame remains at `$2004FFE0`, as required when starting another context. No handler RAM writes or saved-frame corruption occur.

**PROVEN:** stock/diagnostic SVC records and complete SRAM match. Eight native idle instructions run with PSP, then request PendSV via ICSR. Both stop at `$08002A6E`, before executing further with unsupported pending service. This is a post-SVC task checkpoint, not stable USB/MIDI readiness. Twenty-two architectural fixtures pass, including PSP/MSP selection, padded/aligned frames, invalid EXC_RETURN/PC/Thumb/RAM rejection and single consumption. Unsupported nesting, FP return and unprivileged fixtures fail closed. **UNKNOWN:** full NVIC/PendSV and unprivileged/FP behavior; the inherited earlier IRQ/timing/NOR assumptions remain conditional. M7 STKALIGN=1 is explicitly modeled despite the flat CCR backing register.

**UNKNOWN:** H1/H2/P2/P3 and full-boot target counts. Observed-prefix target counts are0 reads/0 writes/0 erase overlaps only. P1 remains PROVEN in its prior diagnostic scope; P4 remains PROVEN for unchanged code. Host containment remains PASS; H4 remains FAIL in-session. Application SDMMC wait `$0801C63C` remains the separate, untouched phase34 boundary. No firmware generation, hardware access, reference/pinned edits or Plaits work occurred.

**UNKNOWN — exactly one next smallest experiment:** qualify native bootloader PendSV `$0800312C` from the real idle-generated pending state `$08002A6E`, including native task save/scheduler/restore and architectural return. It is not implemented here. See [phase35 findings](<../docs/research/phase35-svc-context/findings.md>), native stock trace (local-only reference: `builds/phase35-svc-context/stock.json`; not distributed), diagnostic trace (local-only reference: `builds/phase35-svc-context/diagnostic.json`; not distributed) and validation (local-only reference: `builds/phase35-svc-context/validation.json`; not distributed).

BOOTLOADER SVC / PSP MODEL = PASS

## Phase36 — first native PendSV context switch qualified

**PROVEN:** stock first, then diagnostic replay exactly the phase35 pending CPU/SRAM state at `$08002A6E`. Pre-entry MSP=`$2004FFE0`, PSP=`$20007EA0`, CONTROL=2, xPSR=`$21000000`, PRIMASK/BASEPRI/FAULTMASK=0, LR=`$08002D65`; native IDLE has set PendSV pending. VTOR vector `$08000038 → $0800312D` selects native entry `$0800312C`. Architectural entry stacks the actual Thread context on PSP `$20007E80`, consumes pending, enters Handler mode on MSP and installs EXC_RETURN `$FFFFFFFD`.

**PROVEN:** native `$08003142` saves r4-r11/LR at `$20007E5C`; `$08003146` writes that context pointer to IDLE TCB `$20007EB8`. Native scheduler `$080029D8` uses ready bitmap1 and priority0 list `$20005204` (count4), moves list index `$20005208` to node `$2000648C`, and selects owner TCB `$20006488`. Its native constructor frame at `$2000643C` belongs to bootloader Main by both recorded entry `$08002FDF` and name. No generic scheduler, task-ready flag or host-created task frame is substituted.

**PROVEN:** native handler restores r4-r11 and EXC_RETURN, then native `$0800317E` writes PSP=`$20006460`. Architectural BX/return consumes the hardware frame once, restoring PC=`$08002FDE`, PSP=`$20006480`, CONTROL=2, privileged Thread mode; MSP remains `$2004FFE0`. All seven native store intents, including unchanged-value stores, and per-instruction full-SRAM differences remain within the declared outgoing stack/MSP scratch/TCB/scheduler ranges. No unrelated RAM modification occurs in the switch. No FP save/restore instruction executes in the observed basic-frame path.

**PROVEN:** stock/diagnostic entire PendSV records and complete SRAM agree;32 new native-evidence/architectural-fixture checks pass. A minimal-observer stock control matches the detailed trace, avoiding the prior RAM-hook artifact. Malformed context/EXC_RETURN, alignment, pending consumption and single unstack are tested separately from native boot. **UNKNOWN:** a second PendSV does not occur before the first due post-scheduler tick; nested/FP/unprivileged and later scheduling remain unqualified.

**PROVEN within the inherited ideal2000-instruction cadence:** both execute Main and stop at `$08006EF2`, before delivering the first post-scheduler SysTick. This is an RTOS service boundary during ordinary ring-buffer work, not an SDMMC wait or a firmware-fault conclusion. The earlier pre-scheduler IRQ wrapper is not used for the scheduled context. **UNKNOWN:** real interrupt timing, full boot and stable USB/MIDI state. Application SDMMC `$0801C63C` remains the separate unchanged prior boundary and was not investigated.

**UNKNOWN:** H1/H2/P2/P3 and full-boot target counts. Observed-prefix target counts remain0 reads/0 writes/0 erase overlaps only. P1 remains PROVEN within prior diagnostic scope; P4 remains PROVEN unchanged boot code. H4 remains FAIL in-session; host containment remains PASS. No firmware generation, hardware access, reference/pinned edit or Plaits work occurred.

**UNKNOWN — exactly one next smallest experiment:** qualify native post-scheduler bootloader SysTick from the captured Main-context boundary `$08006EF2`, including any naturally requested PendSV; stop at the next unsupported boundary. See [phase36 findings](<../docs/research/phase36-pendsv-context/findings.md>), stock (local-only reference: `builds/phase36-pendsv-context/stock.json`; not distributed), diagnostic (local-only reference: `builds/phase36-pendsv-context/diagnostic.json`; not distributed) and validation (local-only reference: `builds/phase36-pendsv-context/validation.json`; not distributed).

BOOTLOADER PENDSV / CONTEXT MODEL = PASS

## Phase37 — native post-scheduler bootloader SysTick qualified

**PROVEN:** native configuration computes LOAD=`$1D4BF` (119,999) from represented core clock120MHz and writes CTRL=7: processor-clock source, counter and interrupt enabled. SysTick/PendSV priority bytes are both `$F0`. **STRONG INFERENCE:** intended1ms cadence if the clock equals120MHz. **UNKNOWN:** real timing; the existing ideal2000-instruction event source is retained and VAL is not decremented.

**PROVEN:** stock first, diagnostic second reproduce the phase36 CPU/SRAM checkpoint at `$08006EF2`: Main TCB `$20006488`, MSP=`$2004FFE0`, PSP=`$200063C4`, CONTROL=2, masks0. SysTick vector `$0800003C → $08009331` selects actual handler `$08009330`. Architectural entry consumes pending, enters Handler mode on MSP, and stacks the padded hardware frame at PSP `$200063A0`, xPSR=`$01000200`, EXC_RETURN=`$FFFFFFFD`.

**PROVEN:** actual `$0800935C` clock helper updates `$20000008` 7→8 and the handler updates `$20005518` 0→1. Kernel counter `$200053C0`, scheduler lists/bytes and current TCB remain unchanged. SysTick requests no PendSV. Native POP/architectural return consumes the frame once, restores every Thread register, returns to `$08006EF2`, PSP=`$200063C4`, MSP=`$2004FFE0`, CONTROL=2 and xPSR=`$01000000`. No synthetic software tick increment or scheduler-success flag is used.

**PROVEN:** old ideal wrapper matches live registers and scheduler/counter results but differs in10 stack words: omitted4-byte alignment pad and sentinel LR instead of EXC_RETURN. The native exception path is authoritative. Twenty-four new native-evidence/architectural checks pass; masking retains pending until unmask. Stock/diagnostic and minimal-observer controls match full final SRAM and CPU/context boundaries. **UNKNOWN:** tick-produced PendSV/tail chaining and a second post-scheduler tick are unobserved before the next boundary; neither event is fabricated.

**PROVEN:** later Main and UI each request PendSV through native `$08004720`, independently of SysTick. The unchanged phase36 native model switches Main→UI (`$08003048`, PSP `$20006E00`) then UI→Storage (`$08009202`, PSP `$20007468`), using constructor-created frames and checked ownership ranges. Storage stops at `$080051C2` after issuing `$EC`, address `$81000`, DLR22: an unsupported23-byte array-data read. No data/metadata or completion success is supplied. Bootloader has not completed; application SDMMC `$0801C63C` remains untouched.

**PROVEN observed-prefix target counts `$82000–$821FF`:** reads0 / writes0 / erase overlaps0. The pending `$81000–$81016` read is outside the target. **UNKNOWN:** complete-boot counts and H1/H2/P2/P3. P1 remains PROVEN in its prior diagnostic scope; P4 remains PROVEN unchanged bootloader bytes. Host containment remains PASS; H4 remains FAIL in-session. No firmware generation, hardware access, pinned/reference edit or Plaits work occurred.

**UNKNOWN — exactly one next smallest experiment:** qualify native bootloader Storage's23-byte `$EC` read at `$81000–$81016` using provenance-checked existing NOR bytes and native completion; establish byte provenance before replaying data, then stop at the next unsupported boundary. See [phase37 findings](<../docs/research/phase37-systick/findings.md>), stock (local-only reference: `builds/phase37-systick/stock.json`; not distributed), diagnostic (local-only reference: `builds/phase37-systick/diagnostic.json`; not distributed) and validation (local-only reference: `builds/phase37-systick/validation.json`; not distributed).

BOOTLOADER SYSTICK MODEL = PASS

## Phase38 — NOR81000 read identified; original payload not qualified

**PROVEN:** Main `$08003A42 → $08005D98` requests exactly23 bytes at external NOR `$81000–$81016`, destination `$2000546C`. Native synchronous wrapper `$08005880` submits a24-byte operation1 record through queue `$20007A60`; Storage TCB `$20007470` dequeues the copy at `$2000742C` and dispatches backend `$08005338 → $080076CC`. DMA has NDTR23, PAR `$A0001020`, M0AR `$2000546C`; native command is `$EC`, AR `$81000`, DLR22. Stock/diagnostic prefix observers preserve the phase37 CPU/SRAM endpoint exactly.

**PROVEN static consumer:** after return, `$08005DB0` overwrites identity-cache byte14 with zero. The later constructor/protocol paths inspect/copy14 alphanumeric identity bytes and register the record pointer for string formatting. **STRONG INFERENCE:** the first14 bytes are a serial/identity string. **UNKNOWN:** exact trailing bytes15–22 semantics and original record contents. Post-read RAM cannot establish the destroyed original byte14.

**PROVEN census; UNKNOWN NOR provenance:** reused1858 existing candidates and33 archive-container records, rehashed22 relevant capture/update files and checked the current project/reference file delta. No candidate proves file offset→physical NOR `$81000` mapping for all23 original bytes. Internal flash/application images, SRAM snapshots, generated reset/diagnostic data and updater metadata at `$80000` are not admitted substitutes. Full source paths, SHA-256 values, address spaces and rejections are recorded in [candidate sources](<../docs/research/phase38-nor81000/candidate-sources.md>) and catalog (local-only reference: `builds/phase38-nor81000/candidate-catalog.json`; not distributed).

**UNKNOWN:** no accepted source/offset/23-byte hex/slice SHA exists. No payload is extracted or injected, no IRQ/completion success is asserted, and no post-consumption checkpoint is claimed. The native DMA/QSPI completion, semaphore release, sync clear and caller-return paths are documented statically but remain unexecuted for this read. The semaphore remains held and Main/request ownership remains retained at the original `$080051C2` boundary.

**PROVEN observed-prefix target `$82000–$821FF` counts:**0 reads /0 writes /0 erase overlaps. **UNKNOWN:** post-read/full-boot counts and H1/H2/P2/P3. P1 remains PROVEN in its previous scope; P4 remains PROVEN unchanged code. H4 remains FAIL in-session; host containment remains PASS. No target data investigation, SDMMC work, firmware generation, hardware access or reference/pinned-source edit occurred.

**UNKNOWN — minimum missing prerequisite:** existing original bytes and acquisition metadata proving exact file-offset mapping to `$81000–$81016`, including byte14. Only then can the native Storage completion experiment proceed. See [phase38 findings](<../docs/research/phase38-nor81000/findings.md>), payload admission (local-only reference: `builds/phase38-nor81000/payload-admission.json`; not distributed) and validation (local-only reference: `builds/phase38-nor81000/validation.json`; not distributed).

NOR81000 STORAGE READ = UNQUALIFIED

## Phase39 — symbolic byte14 equivalence remains unqualified

**PROVEN static normal-return order:** `$08005DAE MOVS r2,0` then `$08005DB0 STRB r2,[r4,#$E]` zero `$2000547A`, byte14 of the boot record. Main performs no payload read/copy/compare/call/branch/yield between that read return and the store. The identity constructor and formatting-pointer publication occur afterward. **UNKNOWN:** full non-observability from DMA visibility across Storage/task/IRQ/indirect-reader activity; the immediate Main pair is not an all-task/all-IRQ proof, and no first observer is established.

**PROVEN focused provenance facts:** application reader `$0802520C` uses cache `$20006868`, distinct from bootloader `$2000546C`. The two previously authenticated-file RAM snapshots map to SRAM by loader code, but their candidate bytes0–13 and15–22 differ in both ranges. **UNKNOWN:** capture timing/population, intervening identity edits and equality to the22 original or unchanged post-read bytes for this exact request. Native edit helper `$08005E88 → $08005EAC` can replace the first14 bytes; whether it ran before a capture is unknown. The other22-byte gate therefore independently fails.

**PROVEN:** followed the user's section8 stop condition. Exhaustive native variants tested=0; no concrete23-byte NOR record, guessed byte14, completion signal, convergence result or boot advancement is fabricated. **UNKNOWN:** post-zero convergence, completed-read behavior and global semantic unobservability. Unknown byte14 alone is not the rejection reason:22 proved values plus a complete concurrency proof could admit the proposed equivalence without reconstructing original byte14.

**PROVEN inherited prefix counts for `$82000–$821FF`:**0 reads /0 writes /0 erase overlaps; no new prefix reached. **UNKNOWN:** full-boot/post-read counts, H1/H2/P2/P3. Stock and diagnostic retain the prior `$080051C2` boundary; no new emulation is claimed. Earlier P1/P4 scopes, H4 FAIL and host-containment PASS remain unchanged. No firmware generation, hardware access, pinned/reference edits, target-data investigation or SDMMC work occurred.

**UNKNOWN — next blocker:** request-linked unchanged provenance for the22 observable bytes, followed by complete completion-to-zero observer closure. See [phase39 findings](<../docs/research/phase39-nor81000-symbolic/findings.md>), other22 provenance (local-only reference: `builds/phase39-nor81000-symbolic/other22-provenance.json`; not distributed), ordering (local-only reference: `builds/phase39-nor81000-symbolic/byte14-ordering.json`; not distributed) and validation (local-only reference: `builds/phase39-nor81000-symbolic/validation.json`; not distributed).

NOR81000 SYMBOLIC BYTE14 QUALIFICATION = UNQUALIFIED
