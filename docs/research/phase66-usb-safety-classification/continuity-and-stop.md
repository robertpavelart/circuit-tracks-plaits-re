> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Continuous replay and stop-rule disposition

**PROVEN:** the same ARM instance runs the exact Phase63 candidate through the inherited authenticated starting boundary, constructors, scheduler/NOR/SD, SPI2/SHI table startup, USB initialization, and later Main initialization. No geometry/task-ready fixture is inserted mid-run. Coefficients are synthetic NOR-zero inputs, not authenticated contents of the user's unit. The existing runner requires reconstructing its prefix because it does not serialize all CPU/peripheral/closure state.

The final replay executes **7,071,645 native ARM instructions** and stops at `0801D5A4`, with R9=`$E0001004`. Passive allocation/register/fault instrumentation reproduces the same PC and instruction count as the pre-instrumentation run. The old349 manifest files remain unchanged. USB initialization has finished; the geometry record remains `110000000180003480908f01`.

**PROVEN next gap:** literal `$0801D6D8` loads `$E0001004` into R9 at `0801D57E`. `0801D5A4` reads that address and `0801D5A8` stores the timestamp at `$20006960`. Later `0801D66A–0801D67E` reads it again, computes the elapsed delta and conditionally prints a loop-overrun message before continuing the same loop. Listing: candidate-0801d57e.asm (local-only reference: `builds/phase66-usb-safety-classification/candidate-0801d57e.asm`; not distributed). The exact fault and all live registers are in fault-and-R9.json (local-only reference: `builds/phase66-usb-safety-classification/fault-and-R9.json`; not distributed).

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
