"""Publish scoped preservation results; never upgrade incomplete boot to PASS."""
from support import *
i=json.loads((O/'installation.json').read_text());a=json.loads((O/'address-and-reachability.json').read_text())
p=json.loads((O/'powercycle.json').read_text());b=json.loads((O/'cold-boot-prefix.json').read_text())
old=json.loads((R/'builds/phase32-host-containment/validation.json').read_text())
readiness=R/'notes/qspi82000-hardware-readiness.md';archive=O/'phase32-report-before.md'
if not archive.exists():
 assert sha(readiness.read_bytes())==old['report_sha256'];archive.write_bytes(readiness.read_bytes())
assert sha(archive.read_bytes())==old['report_sha256']
note='''# QSPI $82000–$821FF preservation and one-shot power-cycle qualification

**UNKNOWN — overall qualification remains UNQUALIFIED.** The selected all-block updater/NOR algorithms and native boot validator/installer preserve a synthetic target, and the seven diagnostic outcomes issue no persistent mutations in their selected graph. A full cold restart to normal USB/MIDI-ready application state has **not** been executed. H1/H2/P2/P3 therefore cannot be promoted from partial evidence.

**PROVEN:** no hardware access, firmware/SYX export, reference/pinned-source changes or Plaits implementation occurred. The phase30 device architecture and phase32 host containment are unchanged. An application exists only in emulator memory for this experiment; no hardware-test candidate is generated. All evidence is under [phase33-preservation-powercycle](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase33-preservation-powercycle>).

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

**PROVEN within the selected model:** [install.py](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase33-preservation-powercycle/install.py>) reuses exact B1.3 COPY/ADD spans and unchanged phase30 ARM builders, planned hook and marker in emulator memory. Logical size441,576 (`$6BCE8`), padded to441,600 (`$6BD00`); append ends`$0807BCE8`. In-memory SHA-256`e7c96a5490facee8a4eb7080604500fb2d32f31fa58923eace70b489cd25f110`; CRC`$9865C64A`. These identify an offline memory fixture, not an exported installable artifact.

**PROVEN:** all13,800 blocks pass both the reference Python pack/unpack and actual ARM unpacker `$08024E20`. Every block is programmed via native backend `$08022FDC`; vector block0 is last. Full native erase loop `$08023078` executes. The model then runs boot metadata decoder `$08003B2A/$08005BE8` and native validator `$08003B9A`, which checks product, size, staged CRC and differing38-byte version block before native installer `$08003C24`. The current installed version is kept B1.3 during admission, so the validator must actually enter the installer.

**PROVEN:** the installer executes **110,400 internal word-program calls**, four effective sector erases and one rejected out-of-range erase call. It must produce exact installed bytes; simply preloading an already-matching application is not accepted as installation evidence. Initial fixture verification exposed that version-equality shortcut; the final runner asserts the observed program/erase counts to prevent it.

| Operation | Routine / command | Start / exclusive end | Granularity and purpose | Target overlap | Confidence |
|---|---|---|---|---:|---|
| NOR payload erase,108 operations | `$08023078 → $08037494`,WREN06 then21 (4-byte form of20) | `[$0,$6C000)` |4KiB sectors; prepare selector0 staging |0 | PROVEN model |
| NOR payload program,13,800 operations | `$08022FDC → $080374D4`,WREN06 then12 (4-byte form of02) | `[$0,$6BD00)` |32-byte upload blocks, native256-byte page boundary algorithm |0 | PROVEN model |
| NOR metadata erase,1 operation | Same native erase path,21 | `[$80000,$81000)` |4KiB sector |0 | PROVEN model |
| NOR metadata program,1 operation | Same native program path,12 | `[$80000,$80017)` |23 bytes; selector0/version/size/CRC |0 | PROVEN model |
| Boot staging/metadata reads | `$08003B2A/$08005C10/$08005C68/$08003C24` through modeled storage interface | Staging`[$0,$6BCE8)`/padded32-byte reads to6BD00; metadata80000..80017 | Header/version/CRC/install data | Reads permitted | PROVEN selected model |
| Internal application erase | `$08003C24 → $08006020` | `08010000..08018000`, `08018000..08020000`, `08020000..08040000`, `08040000..08080000` |32KiB/32KiB/128KiB/256KiB effective sectors | Different physical storage | PROVEN model |
| Internal erase request at08080000 | Native wrapper guard offset>=70000 | No erase | Out-of-range no-op | None | PROVEN static guard/model |
| Internal application program | `$08003C24 → $0800605E → $08007FAC` | `[$08010000,$0807BD00)` | Four bytes/call, padded final block | Different physical storage | PROVEN model |
| Identity/settings setter | Boot`$08005DB4`; application`$08025228` | Program`[$81000,$81017)`; erase`[$81000,$82000)` |23 bytes/4KiB; not part of selected normal finalization | No direct overlap; sector ends exactly at target start | PROVEN static path, reachability incomplete |

**PROVEN:** selected modeled totals are **13,801 NOR writes,109 NOR erases; TARGET WRITE COUNT=0; TARGET ERASE OVERLAP=0**. Synthetic target SHA-256 before/after is`3e2a5f93bc6080609236b50b1cbd960f804256b3706be92b55f5a0b25922dbe5`. [installation.json](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase33-preservation-powercycle/installation.json>) logs each operation; [address-and-reachability.json](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase33-preservation-powercycle/address-and-reachability.json>) merges footprints and records caller candidates.

**UNKNOWN — complete H1:** this is not the requested fully coupled host SysEx→RTOS/updater state machine→reset constructors→installer→first boot. Scheduling is replaced by the host block schedule and synchronous NOR completion seam. Boot storage objects are constructed explicitly, CRC endpoints modeled, and internal flash erase/program primitives modeled while native validation/installer control flow runs. All boot constructors, background/storage tasks and SD operations are not closed. Zero overlap in this selected graph cannot certify every persistent operation of installation.

**PROVEN — prior-note correction:** phase31 mislabeled the low helper names. `$08037494` is **erase**, `$080374D4` is **program**, as correctly recorded in phase28 and executed here. Phase31 evidence remains unchanged; its six read-failure findings do not depend on those labels.

## First-boot reachability and genuine reset attempt

**PROVEN:** [cold_boot.py](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase33-preservation-powercycle/cold_boot.py>) starts from actual vectors with MSP`$20050000`, fresh Cortex-M7 CPU, physical SRAM/peripheral mappings and **no running-RAM snapshot**. Diagnostic and unchanged-stock controls execute. Both zero-filled andA5-filled representative SRAM are tried for the diagnostic. No missing ready/completion flag or coefficient data is fabricated to force a completed boot.

| Reset entry | Observed prefix stop | Coverage | Confidence |
|---|---|---|---|
| Bootloader vector`$080098C9` | Unicorn invalid-instruction exception at`$0800929E`, within startup decompression;11,158 instructions | Same for stock control and both diagnostic SRAM fixtures | PROVEN observation; cause UNKNOWN |
| Application vector`$0805C00D` | Decompression load at`$08059706` accesses unmapped`$1FFFFFB0`;11,719 instructions | Same for stock control and both diagnostic SRAM fixtures | PROVEN observation; cause UNKNOWN |

**STRONG INFERENCE:** the matching stock-control stop indicates an incomplete/incorrect cold-start fixture or emulator semantics rather than evidence of a diagnostic-specific defect. No firmware-failure claim is made. [cold-boot-prefix.json](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase33-preservation-powercycle/cold-boot-prefix.json>) records exact PCs/registers/xPSR/accesses. These probes do **not** reach stable normal user state or a USB/MIDI diagnostic command service.

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

**PROVEN:** [powercycle.py](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase33-preservation-powercycle/powercycle.py>) executes the unchanged phase30 native diagnostic for successful capture and TEF/missing completion at0/4/7. **42 assertions** pass. Every exercised diagnostic operation is EC read; no NOR program/erase, SD write or internal-flash write is required for diagnostic state. Existing low-level instruction/write guards reject mutating dispatch/flash stores. This is the selected diagnostic graph, not a claim that unrelated background tasks never write storage.

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

**PROVEN:** bootloader bytes`[$08000000,$08010000)` match the pinned original byte-for-byte before and after selected installation. The installer bounds exclude them. Native recovery button callback`$08003AB0` is replayed for all8 modeled subsets: only scanner IDs18/8/9 all true set the boot-mode flag. Boot main`$08002FDE`, wait`$08003B66` and branch`$08003000` check that mode before normal application handoff; direct handoff uses`$08003D06`. [recovery.json](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase33-preservation-powercycle/recovery.json>) records these predicate tests.

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
'''
(R/'notes/qspi82000-preservation-powercycle.md').write_text(note,encoding='utf8')
section='''

## Phase33 — installation preservation and power-cycle qualification

**UNKNOWN — QSPI one-shot hardware model remains UNQUALIFIED.** See [preservation/power-cycle report](<C:/Proj SSD/CODEX/CIRCUIT/notes/qspi82000-preservation-powercycle.md>) and [phase33 evidence](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase33-preservation-powercycle/validation.json>).

**PROVEN within the selected model:** all13,800 payload blocks pass native ARM SysEx unpacking and native NOR backend staging; the native boot validator enters the native installer from a differing B1.3 version. It executes110,400 modeled internal word-program calls and four effective sector erases. Installed bytes match the emulator-only phase30 prototype. NOR totals:13,801 program operations and109 erases of 4 KiB each. Staging writes`[$0,$6BD00)`, erases`[$0,$6C000)`; metadata program`[$80000,$80017)`, erase`[$80000,$81000)`. **Target writes=0; target erase overlaps=0** in this graph. No application/SYX file is exported. Boot bytes remain unchanged.

**UNKNOWN — H1:** host/RTOS update scheduling, full boot constructors and background/SD persistence are not fully coupled. The selected footprint does not qualify every installation operation. **UNKNOWN — H2:** genuine fresh reset attempts and unchanged-stock controls stop in startup decompression: boot`$0800929E` Unicorn invalid-instruction; app`$08059706` unmapped read`$1FFFFFB0`. Both zero/A5 diagnostic SRAM fixtures have the same boundary. No stable USB/MIDI state is reached; complete first-boot target read/write/erase counts are **UNKNOWN**, not zero. This is a fixture/emulator limit, not a proven firmware failure.

**PROVEN — P1:** success and six TEF/missing-completion native cases issue EC reads only, with no diagnostic-required NOR/SD/internal-flash mutation;42 assertions pass. **UNKNOWN — P2/P3:** fresh CPU/RAM/MMIO maps discard old modeled ownership, but that is not complete normal initialization or a proof SRAM always clears to zero. A full MCU/RTOS/DSP restart and post-reset write closure remain incomplete. The synthetic retained-NOR hash cannot prove the unexecuted suffix preserves target bytes.

**PROVEN — P4:** pinned64KiB bootloader unchanged; all8 modeled recovery-button subsets execute the unchanged native predicate correctly. **UNKNOWN:** unit-specific cold boot, actual power-cycle behavior and recovery installation. **STRONG INFERENCE:** read-only NOR interruption itself should not program/erase array data, and unchanged boot code retains its architectural recovery option. These do not close H2/P2/P3.

**PROVEN — correction:** phase31 prose reversed low helper names: erase is`$08037494`, program is`$080374D4` (phase28 and phase33 are correct). Prior evidence is retained unchanged; read-failure findings are unaffected.

**PROVEN:** phase32 host containment remains PASS; device H4 remains FAIL for in-session recovery. Intended policy is ONE REQUEST PER BOOT, success ends session, failure means no file/no retry and requires full power cycle before any new attempt. **UNKNOWN:** hardware admission remains blocked; no candidate generation follows. Minimum next offline experiment: qualify stock startup scatter decompression at the recorded stop boundaries, then resume real constructors/write tracing to a stable application state.

QSPI ONE-SHOT HARDWARE MODEL = UNQUALIFIED
'''
base=archive.read_bytes();current=readiness.read_bytes()
assert current==base or current==base+section.encode('utf8')
readiness.write_bytes(base+section.encode('utf8'))
print('Wrote preservation report; appended readiness without changing prior text')

