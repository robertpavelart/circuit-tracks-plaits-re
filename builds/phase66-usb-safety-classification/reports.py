from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1]
load=lambda n:json.loads((O/n).read_text());a=load('analysis.json');x=load('continuity.json');u=load('usb-evidence.json')
def link(n):return f'[{n}](<{(O/n).as_posix()}>)'
def write(n,s):(O/n).write_text(s.strip()+'\n',encoding='utf-8')
write('register-sequence.md',f'''
# Exact USB register and local sequence

**PROVEN:** `$40040008` is STM32F745 USB OTG HS `GAHBCFG`, the global AHB configuration register, at base `$40040000` plus8. Bit0 is the global interrupt enable, GINT; bit5 enables the controller's internal DMA. It is an ordinary readable/writable configuration register, not a FIFO or a read-to-pop status. Source: [ST device definitions](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-f7/master/Include/stm32f745xx.h), USB_OTG_HS_PERIPH_BASE, USB_OTG_GlobalTypeDef.GAHBCFG, GAHBCFG_GINT/DMAEN.

**PROVEN exact code:** `080381C8→08048316` loads GAHBCFG, shifts right1 then left1, stores it back at `0804831C`, returns0. It clears bit0 and preserves the other31 bits. No bit is tested for readiness and there is no loop. Normal progress requires only a responding peripheral register. The Phase65 unmapped-read exception was caused by the emulator's missing address range, not by firmware waiting for a USB event. `0804830E` performs the complementary bit0 enable.

**PROVEN next local conditions:** `080381DC→080481D4` configures the PHY interface and calls `08048A8E`. That reset helper waits for GRSTCTL bit31 AHBIDL, sets bit0 CSRST, and waits for it to clear. Its native countdown returns3 on timeout. `08038250→0804834A` initializes device registers and uses the self-clearing TX/RX FIFO flush bits5/4. These are the only finite hardware transitions added; no host reset, descriptor request, enumeration or packet-completion event was invented. Sources: {link('candidate-0804830e.asm')}, {link('candidate-080481d4.asm')}, {link('candidate-08048a8e.asm')}, {link('candidate-0804834a.asm')}, {link('candidate-080381a8.asm')}.

**PROVEN bounded model:** {link('usb_model.py')}, `USBInit`, implements the observed device-initialization register latches, write-one-to-clear interrupt fields, idle-without-transfer status and delayed reset/flush completion. SR-style polling advances completion after three reads in the normal test profile; this is an abstract finite delay, not measured silicon latency. No pending bus events are supplied. Unknown registers, forced host mode, internal-DMA configuration and endpoint activation stop the model. There is no endpoint memory DMA or FIFO packet model.

**STRONG INFERENCE:** this minimal disconnected-device profile represents the successful conditions consumed by the observed startup. It is not a complete USB reset-value/peripheral implementation. Unused/reserved fields, endpoint traffic, bus speed/timing and physical host interoperability remain **UNKNOWN**. The current [ST low-level driver](https://raw.githubusercontent.com/STMicroelectronics/stm32f7xx-hal-driver/master/Src/stm32f7xx_ll_usb.c) supports these reset/flush semantics; it is not asserted to be the exact historical source/ABI of the candidate.

**PROVEN native sanity:** {link('model-tests.json')} has six checks: interrupt-bit clear without a wait, normal reset, delayed reset, AHB never idle, reset never completes, and rejection of unsupported endpoint activation. Actual `08048316/08048A8E` bytes execute in isolated argument fixtures. Both missing-condition cases take the real return3 path. Geometry canaries remain unchanged. These fixtures are never inserted into startup RAM.
''')
write('safety-allocation.md',f'''
# Safety relevance and allocation results

The conclusions below concern the normal offline startup workload, with inherited synthetic storage/ADC/clock inputs. They do not describe arbitrary later USB commands.

| Resource | Observed effect / boundary | Confidence |
|---|---|---|
|Diagnostic-owned RAM|USB init writes its own handle/endpoint metadata and temporary stack. All3,186 observed allocation returns end at or below20044D70 and none intersects the reserved record.|PROVEN within traced prefix|
|12-byte lifecycle/geometry|Remains `110000000180003480908f01`; no USB-driver PC writes it.|PROVEN|
|Raw capture buffer|No raw frame exists yet. USB init's temporary stack use is not concurrent with a live capture frame.|PROVEN absence; future lifetime UNKNOWN here|
|External NOR program/erase|No mutation primitive is entered after USB initialization starts in this workload; local USB init contains register/metadata operations.|PROVEN observed path; arbitrary later commands outside scope|
|Authorization epoch/session|No diagnostic request is injected, no session is authorized, and record11 persists. No USB-init write advances the epoch/session.|PROVEN|
|Bootloader/rollback|Candidate bytes and prior install/rollback evidence are unchanged; the modeled register sequence does not program internal flash.|PROVEN scoped preservation; physical rollback UNKNOWN|

**PROVEN USB initialization state:** the live PCD handle at `$20004D44` has six endpoints and state1 (driver READY). Its native DMA-enable field is0 at handle+`$10`; this offset follows the actual by-value ABI and conditional branch at `08048226`, not an assumed modern struct layout. GAHBCFG ends at1, so GINT is enabled and DMAEN is clear. No endpoint-DMA register is programmed in the observed USB initialization. PCD READY is **not** `USBD_STATE_CONFIGURED=3`; no host configuration event was modeled.

**PROVEN allocation evidence:** {link('allocation-returns.json')} tracks entry size, caller return PC, SP/TCB, pointer and end extent for1,582 generic requests and1,604 underlying bounded bump calls. All3,186 calls return; there are no positive-size failure returns, pending returns, arithmetic-wrap extents or overlaps with `[20044D70,20044D7C)`. The generic/bump counts are two layers of the allocator, not3,186 distinct independent objects. Observation begins at runtime-hook installation after constructors; the constructor reservation evidence remains separately preserved.

The cursor is `$20044D68`, eight bytes below the cap. This is the observed bump frontier, not a physical RAM/stack margin measurement or proof that all future requests can succeed. A large160,784-byte allocation is explicitly recorded at2001183C–20038C4C; no inference about its ownership/free capacity is needed for the overlap check. The earlier concern that the next fault might mean allocation failure is **rejected**: every observed allocator call returned normally and the fault address is DWT, not heap RAM. See {link('analysis.json')} and {link('fault-and-R9.json')}.

**UNKNOWN:** allocations caused by future host enumeration, runtime reconfiguration or actual capture entry have not been executed. No claim is made that zero observed overlap proves the entire future lifetime. The prior Phase63 stack-buffer/DMA fence and host containment tests remain scoped evidence; no prepared fixture replaces this continuous run.
''')
write('continuity-and-stop.md',f'''
# Continuous replay and stop-rule disposition

**PROVEN:** the same ARM instance runs the exact Phase63 candidate through the inherited authenticated starting boundary, constructors, scheduler/NOR/SD, SPI2/SHI table startup, USB initialization, and later Main initialization. No geometry/task-ready fixture is inserted mid-run. Coefficients are synthetic NOR-zero inputs, not authenticated contents of the user's unit. The existing runner requires reconstructing its prefix because it does not serialize all CPU/peripheral/closure state.

The final replay executes **{x['executed_instructions']:,} native ARM instructions** and stops at `0801D5A4`, with R9=`$E0001004`. Passive allocation/register/fault instrumentation reproduces the same PC and instruction count as the pre-instrumentation run. The old349 manifest files remain unchanged. USB initialization has finished; the geometry record remains `{x['record']}`.

**PROVEN next gap:** literal `$0801D6D8` loads `$E0001004` into R9 at `0801D57E`. `0801D5A4` reads that address and `0801D5A8` stores the timestamp at `$20006960`. Later `0801D66A–0801D67E` reads it again, computes the elapsed delta and conditionally prints a loop-overrun message before continuing the same loop. Listing: {link('candidate-0801d57e.asm')}. The exact fault and all live registers are in {link('fault-and-R9.json')}.

**PROVEN vendor identification:** `$E0001004` is DWT.CYCCNT, baseE0001000 plus4, an on-core cycle counter. Source: [Arm Cortex-M7 CMSIS definitions](https://raw.githubusercontent.com/ARM-software/CMSIS_5/develop/CMSIS/Core/Include/core_cm7.h), DWT_BASE and DWT_Type.CYCCNT. The fixture maps SCS atE000E000 but not DWT. This is a missing emulator register, not an invalid heap pointer or a hardware-observed fault.

**STRONG INFERENCE — non-safety-related local dependency:** the observed counter value is used by this Main-loop timing/logging path. It is not an allocation address, DMA ownership indication, geometry field, NOR command, authorization token or rollback control. The diagnostic's timeout source is the separately modeled clock at2000081C. No concrete dependency connecting this particular cycle-counter read to corruption of the protected resources is demonstrated.

**Stop rule applied:** no DWT model, broad USB enumeration/endpoint model, unrelated peripheral investigation or firmware change was added. The residual profiling gap is explicitly **MODEL COVERAGE LIMITATION / HARDWARE-ONLY UNKNOWN** for actual hardware counter/timing behavior. A missing emulator register could be modeled offline, but this phase does not turn that into another mandatory research phase. This classification is not a new software corruption finding.

| Requested continuity answer | Result |
|---|---|
|Can startup reach USB-ready?|PROVEN controller/PCD READY with GINT enabled. Host-enumerated/configured readiness remains UNKNOWN.|
|Does geometry remain intact?|PROVEN through the new Main-loop frontier.|
|Do modeled post-constructor allocations overlap diagnostic RAM?|PROVEN no overlap for every observed returned extent; future lifetime remains UNKNOWN.|
|Can authorization/capture entry be reached without a firmware defect?|No defect is demonstrated; execution of these entries from this continuous state is UNKNOWN. No host SET_CONFIGURATION or diagnostic request was supplied.|

Earlier Phase63 native parser/authorization/capture tests remain valid within their prepared boundary models. They are not relabeled as continuous reset-to-capture evidence. No configured-state byte, session word or ready return was forced merely to complete this table.
''')
v=dict(verdict='UNQUALIFIED',confidence='UNKNOWN',USB_local_safety='PROVEN in observed initialization workload',USB_driver_ready=True,USB_host_configured=False,geometry_unchanged=True,observed_allocation_returns=a['completed_returns'],allocation_overlap=False,positive_size_allocation_failure=False,new_firmware_defect_demonstrated=False,remaining_gap='MODEL COVERAGE LIMITATION / HARDWARE-ONLY UNKNOWN: DWT.CYCCNT Main-loop profiling read',remaining_local_gap_safety_relevance='STRONG INFERENCE non-safety-related timing/logging',authorization_capture_continuity='UNKNOWN: not executed',future_allocation_lifetime='UNKNOWN',firmware_modified=False,hardware_access=False,MIDI_access=False,transmission=False,prior_manifests=a['prior_manifests'])
write('preflight-verdict.json',json.dumps(v,indent=2))
write('findings.md',f'''
# Phase66 — USB gap safety classification

**FINAL PREFLIGHT CLOSURE = UNQUALIFIED.** The USB register gap is closed for the bounded device-initialization path and no firmware defect is demonstrated. Startup reaches PCD READY; the next stop is an unmapped DWT cycle-counter read used for Main-loop timing/logging. The stop rule is applied; no broad USB or unrelated peripheral phase was started.

1. **PROVEN:**40040008 is USB OTG HS GAHBCFG. `08048316` clears bit0; it does not poll readiness. Native reset/flush polling is covered by a finite model and six bounded checks.
2. **PROVEN:** USB initialization completes with PCD state1, global interrupts enabled, internal DMA disabled, and no endpoint-DMA programming. Host enumeration/configuration remains **UNKNOWN**.
3. **PROVEN:** geometry remains `110000000180003480908f01`. All1,582 observed generic requests and1,604 underlying bump calls return; no returned extent overlaps the record or crosses its cap. No allocation failure is observed.
4. **PROVEN:** the next fault is `$E0001004` at `0801D5A4`, DWT.CYCCNT. **STRONG INFERENCE:** this local profiling/logging dependency is not safety-relevant. It is **MODEL COVERAGE LIMITATION / HARDWARE-ONLY UNKNOWN**, not a concrete firmware defect.
5. **UNKNOWN:** actual host configuration and uninterrupted authorization/capture entry, subsequent allocation/lifetime behavior and physical memory/timing margins. These were not forced or silently marked passed. Thus the overall continuous preflight remains UNQUALIFIED even though this USB initialization safety question is resolved within the tested scope.

Reports: {link('register-sequence.md')}, {link('safety-allocation.md')}, {link('continuity-and-stop.md')}. Data: {link('analysis.json')}, {link('allocation-returns.json')}, {link('usb-evidence.json')}, {link('preflight-verdict.json')}.

All199 Phase63,72 Phase64 and78 Phase65 manifest files verify unchanged. No firmware was generated/modified and no reference repository was edited. No hardware, MIDI port or transmission was used. The existing H4 no-retry/quarantine policy and prior scoped regression results remain unchanged.

No new peripheral-research phase is proposed. The distinction to retain is controller-ready versus host-configured, and observed non-overlap versus a complete future capture lifetime.

FINAL PREFLIGHT CLOSURE = UNQUALIFIED
''')
write('CHECKPOINT.md',f'''
# Phase66 completed checkpoint

USB classification/model scope is finished. Do not restart USB/SHI analysis or begin a broad DWT/USB phase automatically.

Current exact-image run:7,071,645 ARM instructions, USB PCD READY/GINT1/DMA0, record110000000180003480908f01, heap20044D68/cap20044D70.1,582 generic allocations +1,604 bump calls,3,186 completed returns, no failures/pending/overlaps. Physical headroom and future request success remain unknown.

Frontier0801D5A4 reads R9=E0001004, DWT.CYCCNT. This is a non-safety-related local profiling/logging dependency, not heap corruption. Exact registers and transitions are saved. DWT was not modeled. No host enumeration or diagnostic input was injected; host-configured/query/auth/raw entry and future lifetime are unexecuted.

Files:startup.py derives the saved Phase65 runner and adds only USBInit plus passive fault/allocation observation. selected-startup.py.txt is the executed source. usb_model.py rejects unsupported host/DMA/endpoint activity; three-poll reset/flush is an abstraction, not hardware timing. model_tests.py records six native/helper guard cases. analyze.py verifies new evidence and349 old manifest entries; reports.py writes reports/manifest; validate.py verifies final consistency.

The field at handle+0x10 is DMA-enable in this candidate's actual by-value ABI; +0x0C is a different field. Do not infer historical struct offsets from current HAL layouts. No firmware changes occurred.

The runner does not serialize all CPU/peripheral state, so a SRAM dump alone cannot resume its machine. The false early device-mask stop and pre-instrumentation DWT stop are retained separately. Passive instrumentation reproduces the same final instructions/frontier; no old scoped suites were rerun.

FINAL PREFLIGHT CLOSURE = UNQUALIFIED
''')
write('README.md',f'Phase66 bounded USB safety classification. Begin with {link("findings.md")}. Overall **UNQUALIFIED**; no hardware action or new peripheral-research phase is proposed.')
rows=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS.txt':rows.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(O).as_posix())
(O/'SHA256SUMS.txt').write_text('\n'.join(rows)+'\n');print('Phase66 reports and manifest saved',len(rows))
