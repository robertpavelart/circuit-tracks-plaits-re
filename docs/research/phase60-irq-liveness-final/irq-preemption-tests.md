> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase60 — native preemption cases

**PROVEN bounded cases:** all nine injected external events return to normal native flow and then1AE06 withstatus0/type2. Narrow private-write hooks record0 intents; watched write/erase/file-mutation entries record0. Native registration/BPB parsing and kernel/Storage queues are inherited unchanged. Geometry records collected at the final checkpoint are persisted per case. irq-tests.json (local-only reference: `builds/phase60-irq-liveness-final/irq-tests.json`; not distributed), [run_irq_cases.py](<../../../builds/phase60-irq-liveness-final/run_irq_cases.py>).

|IRQ|Injection PC / event|Native instructions|Mount return|Private writes|

|---|---|---:|---:|---:|

|28|0x801d768: first modeled millisecond boundary after at least 3ms elapsed since CEN+DIER; controlled timer event|62735|0|0|

|30|0x801d768: first modeled millisecond boundary after at least 1ms elapsed since CEN+DIER; controlled timer event|59377|0|0|

|37|0x801bd92: one received MIDI active-sensing byte after UE+RXNEIE and at least1 modeled ms; controlled serial completion|59359|0|0|

|38|0x801bd92: one received MIDI active-sensing byte after UE+RXNEIE and at least1 modeled ms; controlled serial completion|59359|0|0|

|40|0x801bbd8: one falling power-button EXTI edge with configured IMR/FTSR; GPIO shadow low|59371|0|0|

|49|0x801c63c: SDMMC command timeout after native command start; absent-card success model|59370|0|0|

|50|0x801d768: first modeled millisecond boundary after at least 1ms elapsed since CEN+DIER; controlled timer event|59343|0|0|

|70|0x8037596: DMA2 stream7 TC after native read transaction started, NDTR reaches zero|59318|0|0|

|92|0x8037596: TCF for an already-issued NOR command with TCIE|59346|0|0|

Entry occurs only withIRQenabled,PRIMASK/FAULTMASKclear, priority aboveBASEPRI and no active handler. Basic hardware frames/unstack are modeled; actual pinned handlers execute. GenericPOP-to-EXC_RETURN is handled for native IRQs as well asBX LR. Early USART entry can precede task creation; the observer no longer incorrectly tries to read aTCB name through null. That observer defect was corrected and its affected cases rerun; it was not a firmware failure. [prepare.py](<../../../builds/phase60-irq-liveness-final/prepare.py>), [instrumented_startup.py](<../../../builds/phase60-irq-liveness-final/instrumented_startup.py>).

**PROVEN modeled source constraints:** serial input waits at least1 logical millisecond afterUE/RXNEIE (longer than a31250-baud byte); DMA70 requires started streamEN/TCIE and an issued NOR command; QSPI92 requiresTCIE and an issued command; SD49 requires busy command and enabled command-timeout mask. Completion/absence timing for NOR/SD remains explicitly supplied, as inPhase59; it is not measured hardware timing. Firing a default/uninitialized USB interrupt was deliberately not used as a test.

**UNKNOWN untested eligible branches/combinations:**TIM2 compare4→1EEB0; an armed RTC alarm223B0→[200069F0] after a held-power sequence; cascaded display DMA59/60 under that compare branch; nested/repeated events and extended FP exception frames. Pending status registers use inherited simple shadows rather than a full peripheral W0C/W1C/clock engine. Thus individual handler results are not universal IRQ closure. Phase59 SysTick tests are preserved, not rerun. early-systick.json (local-only reference: `builds/phase59-scheduler-first-mount-order/early-systick.json`; not distributed).
