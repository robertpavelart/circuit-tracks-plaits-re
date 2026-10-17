> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase60 — early IRQ inventory

**PROVEN observed normal-success inventory:**20 external NVIC enables plus SVC/PendSV/SysTick. Accumulated W1S/W1C events are used rather than treating the last write to a shadow ISER word as the full enable set. Native enable helper is1BBC4, store1BBD4; priority helper writes1BBAE. Original priority bytes/enable PC/callerLR are persisted. The observed prefix still executes59306 instructions and returns mount status0/type2, matchingPhase59. irq-inventory.json (local-only reference: `builds/phase60-irq-liveness-final/irq-inventory.json`; not distributed), observed-prefix.json (local-only reference: `builds/phase60-irq-liveness-final/observed-prefix.json`; not distributed), [irq_observer.py](<../../../builds/phase60-irq-liveness-final/irq_observer.py>).

|IRQ / vector|Handler|Priority byte|Enable PC / caller return|Source / earliest condition|Callbacks and effect|

|---|---|---:|---|---|---|

|14 / 30 DMA1 stream3|0x8057533|80|0x801bbd4 / 0x801c059|SPI2 RX stream disabled; CR10414 lacksEN before snapshot|No independent storage path in shown handler; completion37852 if stream started|

|15 / 31 DMA1 stream4|0x8057509|80|0x801bbd4 / 0x801c059|SPI2 TX stream disabled; CR10454 lacksEN|Completion3784E; no pre-mount transfer observed|

|18 / 34 ADC shared|0x80574d7|96|0x801bbd4 / 0x804959d|ADC processing source; acquisition DMA not started in observed prefix|1F3F4 RAM/ADC path; acquisition start after mount|

|24 / 40 TIM1 break / TIM9|0x80575a1|160|0x801bbd4 / 0x802441f|TIM9 CR1=8 has CEN0 before snapshot|234C2 toggles GPIO; source inactive|

|28 / 44 TIM2|0x805744b|32|0x801bbd4 / 0x802441f|CEN+DIER; update after ARR1000,PSC170; compare4 separate enabled source|Display1EEB0/25AE8→3AD64; tested update with delayed Storage|

|30 / 46 TIM4|0x80574b5|128|0x801bbd4 / 0x802441f|CEN+CC1IE; PSC5999, CCR1=10|5760C increments service200001D8 pending count|

|36 / 52 SPI2|0x805c30d|240|0x801bbd4 / 0x803793d|CR2=1703; RXNEIE/TXEIE/ERRIE all0|Default loop5C30C; no eligible SPI source asserted|

|37 / 53 USART1|0x80574fd|128|0x801bbd4 / 0x80229ab|UE+RXNEIE; completed incoming serial byte required|1DD86→2214A bounded receive ring; tested FE byte|

|38 / 54 USART2|0x8057503|128|0x801bbd4 / 0x80229ab|UE+RXNEIE; completed incoming serial byte required|Same receive handler for second interface|

|40 / 56 EXTI15_10|0x80573d9|0|0x801bbd4 / 0x801b0a5|IMR bit11 and falling edge enabled; external power-button transition|1DA24→22308 (arm alarm if held) or2238C (disarm); falling/low case tested|

|41 / 57 RTC alarm|0x80573dd|16|0x8022304 / 0x80222ff|Alarm interrupt enabled; ALRAE bit8 clear in normal prefix|223B0→[200069F0]; conditional power hold1DA70→1DAE0 requires separate arm/expiration|

|49 / 65 SDMMC1|0x8057563|192|0x801bbd4 / 0x801c623|Native command busy and MASK.CTIMEOUTIE; absent-card timeout event|C690 status update→57664 notification; tested one command timeout|

|50 / 66 TIM5|0x8057499|128|0x801bbd4 / 0x802441f|CEN+CC1IE; PSC5999, CCR1=10|5760C increments service200001CC pending count|

|56 / 72 DMA2 stream0|0x80574e9|96|0x801bbd4 / 0x801c059|ADC DMA configured, stream EN0 before snapshot|1F3FA RAM ADC queue|

|59 / 75 DMA2 stream3|0x8057431|16|0x801bbd4 / 0x801c059|SPI4 display DMA EN0 in normal prefix|1EFA8 callback only when a display frame/transfer is active|

|60 / 76 DMA2 stream4|0x805740f|16|0x801bbd4 / 0x801c059|SPI4 other stream EN0 in normal prefix|Handler clears DMA flags only|

|69 / 85 DMA2 stream6|0x8057579|80|0x801bbd4 / 0x801c059|SD DMA EN0 in absent-card prefix; command timeout is not data DMA|Clears DMA flags; card-present data transfers not asserted|

|70 / 86 DMA2 stream7|0x80573ef|80|0x801bbd4 / 0x801c059|NOR DMA EN+TCIE only after actual read command setup|22888 no-op completion tail; TC/NDTR0 case tested|

|84 / 100 SPI4|0x805c399|240|0x801bbd4 / 0x803793d|CR2=1703; peripheral RXNE/TXE/error interrupts disabled|Default loop5C398; no eligible SPI source asserted|

|92 / 108 QUADSPI|0x80573e1|192|0x801bbd4 / 0x8022709|Command issued, CR.TCIE set, SR.TCF becomes set|22826 sets controller completion bits;57664 notifies Storage|

**PROVEN system vectors:**SVC11=1D9B0, PendSV14=1D954, SysTick15=5998C. SVC is raised at1D9EA; PendSV requires native ICSR.PENDSVSET; SysTick starts through1D2C8 withCTRL7/LOAD119999 and priority240. BASEPRI/PRIMASK are checked before experimental entry. Native SysTick does not dispatch software timer callbacks. vectors.json (local-only reference: `builds/phase59-scheduler-first-mount-order/vectors.json`; not distributed), app-0801d2c8.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-0801d2c8.asm`; not distributed).

**PROVEN scope of handler statements:** pinned handler bodies are decoded in app-080573d8.asm (local-only reference: `builds/phase60-irq-liveness-final/app-080573d8.asm`; not distributed), including tail calls and constant peripheral/context pointers. None of those immediate handlers contains a direct NOR program/erase or directD70 store; indirect callback descendants require their own path proof. The two default-loop vectors were not injected merely because enabled. USB IRQ77 is absent, as is FS IRQ67; see [usb-startup-order.md](<usb-startup-order.md>).

**STRONG INFERENCE:** inactive stream/peripheral sources in the observed initialization state stay inactive until their post-mount acquisition/display activation. This is narrower than all card-present/input/power-button states. **UNKNOWN exact conditional roots:**TIM2 compare41EEB0/display transfer activation and RTC alarm223B0→[200069F0] following a held-power sequence; not counted as tested solely from an enabled bit. No unobserved IRQ is called harmless by name.
