"""Report only persisted Phase60 native observations and explicit proof gaps."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def L(name,label=None):return f'[{label or name}](<{(OUT/name).as_posix()}>)'
def P(phase,name,label=None):return f'[{label or name}](<{(ROOT/"builds"/phase/name).as_posix()}>)'
def save(name,s):(OUT/name).write_text(s.strip()+'\n',encoding='utf8')
def main():
    inv=json.loads((OUT/'irq-inventory.json').read_text());test=json.loads((OUT/'irq-tests.json').read_text());model=json.loads((OUT/'owner-model-tests.json').read_text())
    rows=inv['snapshots'][0]['enabled'];enable={r['irq']:r for r in inv['transitions'] if r['enable']}
    kinds={14:('DMA1 stream3','SPI2 RX stream disabled; CR10414 lacksEN before snapshot','No independent storage path in shown handler; completion37852 if stream started'),15:('DMA1 stream4','SPI2 TX stream disabled; CR10454 lacksEN','Completion3784E; no pre-mount transfer observed'),18:('ADC shared','ADC processing source; acquisition DMA not started in observed prefix','1F3F4 RAM/ADC path; acquisition start after mount'),24:('TIM1 break / TIM9','TIM9 CR1=8 has CEN0 before snapshot','234C2 toggles GPIO; source inactive'),28:('TIM2','CEN+DIER; update after ARR1000,PSC170; compare4 separate enabled source','Display1EEB0/25AE8→3AD64; tested update with delayed Storage'),30:('TIM4','CEN+CC1IE; PSC5999, CCR1=10','5760C increments service200001D8 pending count'),36:('SPI2','CR2=1703; RXNEIE/TXEIE/ERRIE all0','Default loop5C30C; no eligible SPI source asserted'),37:('USART1','UE+RXNEIE; completed incoming serial byte required','1DD86→2214A bounded receive ring; tested FE byte'),38:('USART2','UE+RXNEIE; completed incoming serial byte required','Same receive handler for second interface'),40:('EXTI15_10','IMR bit11 and falling edge enabled; external power-button transition','1DA24→22308 (arm alarm if held) or2238C (disarm); falling/low case tested'),41:('RTC alarm','Alarm interrupt enabled; ALRAE bit8 clear in normal prefix','223B0→[200069F0]; conditional power hold1DA70→1DAE0 requires separate arm/expiration'),49:('SDMMC1','Native command busy and MASK.CTIMEOUTIE; absent-card timeout event','C690 status update→57664 notification; tested one command timeout'),50:('TIM5','CEN+CC1IE; PSC5999, CCR1=10','5760C increments service200001CC pending count'),56:('DMA2 stream0','ADC DMA configured, stream EN0 before snapshot','1F3FA RAM ADC queue'),59:('DMA2 stream3','SPI4 display DMA EN0 in normal prefix','1EFA8 callback only when a display frame/transfer is active'),60:('DMA2 stream4','SPI4 other stream EN0 in normal prefix','Handler clears DMA flags only'),69:('DMA2 stream6','SD DMA EN0 in absent-card prefix; command timeout is not data DMA','Clears DMA flags; card-present data transfers not asserted'),70:('DMA2 stream7','NOR DMA EN+TCIE only after actual read command setup','22888 no-op completion tail; TC/NDTR0 case tested'),84:('SPI4','CR2=1703; peripheral RXNE/TXE/error interrupts disabled','Default loop5C398; no eligible SPI source asserted'),92:('QUADSPI','Command issued, CR.TCIE set, SR.TCF becomes set','22826 sets controller completion bits;57664 notifies Storage')}
    table='|IRQ / vector|Handler|Priority byte|Enable PC / caller return|Source / earliest condition|Callbacks and effect|\n|---|---|---:|---|---|---|\n'
    for r in rows:
        i=r['irq'];k,c,e=kinds[i];x=enable[i]
        table+=f"|{i} / {r['vector_number']} {k}|{r['handler']}|{r['priority']}|{x['pc']} / {x.get('caller_return','recorded in per-case trace')}|{c}|{e}|\n"
    save('early-irq-inventory.md',f'''# Phase60 — early IRQ inventory

**PROVEN observed normal-success inventory:**20 external NVIC enables plus SVC/PendSV/SysTick. Accumulated W1S/W1C events are used rather than treating the last write to a shadow ISER word as the full enable set. Native enable helper is1BBC4, store1BBD4; priority helper writes1BBAE. Original priority bytes/enable PC/callerLR are persisted. The observed prefix still executes59306 instructions and returns mount status0/type2, matchingPhase59. {L('irq-inventory.json')}, {L('observed-prefix.json')}, {L('irq_observer.py')}.

{table}
**PROVEN system vectors:**SVC11=1D9B0, PendSV14=1D954, SysTick15=5998C. SVC is raised at1D9EA; PendSV requires native ICSR.PENDSVSET; SysTick starts through1D2C8 withCTRL7/LOAD119999 and priority240. BASEPRI/PRIMASK are checked before experimental entry. Native SysTick does not dispatch software timer callbacks. {P('phase59-scheduler-first-mount-order','vectors.json')}, {P('phase59-scheduler-first-mount-order','app-0801d2c8.asm')}.

**PROVEN scope of handler statements:** pinned handler bodies are decoded in {L('app-080573d8.asm')}, including tail calls and constant peripheral/context pointers. None of those immediate handlers contains a direct NOR program/erase or directD70 store; indirect callback descendants require their own path proof. The two default-loop vectors were not injected merely because enabled. USB IRQ77 is absent, as is FS IRQ67; see {L('usb-startup-order.md')}.

**STRONG INFERENCE:** inactive stream/peripheral sources in the observed initialization state stay inactive until their post-mount acquisition/display activation. This is narrower than all card-present/input/power-button states. **UNKNOWN exact conditional roots:**TIM2 compare41EEB0/display transfer activation and RTC alarm223B0→[200069F0] following a held-power sequence; not counted as tested solely from an enabled bit. No unobserved IRQ is called harmless by name.''')
    save('usb-startup-order.md',f'''# Phase60 — USB early-start boundary

**PROVEN native handoff cleanup:** boot03D06 clears external NVIC enable wordsE000E180/+4/+8 and pending wordsE000E280/+4/+8, pulses AHB/APB reset registers40023810/+4/+10/+14, then installs application VTOR/MSP and branches to reset. A retained USB clock-enable bit alone therefore does not imply a live application USB interrupt after handoff. {P('phase58-preconstructor-liveness-closure','boot-08003d06.asm')}.

**PROVEN exact USB chain:**37F0E→245C6→245FE→381A8→381BE→244D4.244D4 requires peripheral40040000, enables its GPIO/clock (AHB1 bit29), setsIRQ77 priority12<<4=192 at24500 and enablesIRQ77 at2450A.245C6 builds the controller context20004D44 and endpoint/FIFO fields. Device start subsequently uses36460→37F26. The actual OTG handler is574D0→382EA, not a fabricated USB task. {L('app-080244b8.asm')}, {L('app-080381a8.asm')}, {L('app-08036442.asm')}, {L('usb-init-xrefs.json')}, {L('app-080382ea.asm')}.

**PROVEN in the observed normal prefix:** no244D4/245C6/381A8 call, noIRQ77 enable, no40040000 controller access and noUSB callback precedes1AE06. The initialized context/registration of a vendor callback by24D56→38CE8 is not peripheral initialization. Main's settings/USB-mode observer path1F9A4→29DDC→29E30→38C54 belongs to1F0F0 work after Main1D4C0 returns from first mount. The preservedPhase46 observer/class-dispatch evidence is reused. {L('observed-prefix.json')}, {P('phase59-scheduler-first-mount-order','app-0801d4b0.asm')}, {P('phase59-scheduler-first-mount-order','app-08038ce8.asm')}, {P('phase46-msd-filesystem-closure','msd-reachability.md')}.

**STRONG INFERENCE normal-start ordering:** host enumeration and USB diagnostic/vendor/MSD callbacks cannot meaningfully execute before controller initialization/start and unmaskedIRQ77; the ordinary Main initialization path reaches snapshot first. No USB IRQ was injected into an uninitialized controller. This removes the generic early-USB-task hypothesis under the supplied normal-start contract.

**UNKNOWN beyond this boundary:** actual post-mount native geometry-export/authorization integration through vendor dispatcher24D2C and the6B798/6B850 owners. USB readiness after mount does not establish byte ownership. No enumeration, MIDI port or device access was performed.''')
    save('timer-systick-order.md',f'''# Phase60 — timer sources and consumer ordering

**PROVEN native sources:**TIM4IRQ30 andTIM5IRQ50 requireSR.CC1IF andDIER.CC1IE. Handlers574B4/57498 clear that flag then5760C advancesCCR1 and increments pending count at200001D8/+A or200001CC/+A, bounded by byte+B. They do not directly call the software record's callback. Native1E4BE later consumes counts in UI or Main context. {L('app-080573d8.asm')}, {L('app-0805760c.asm')}, {P('phase59-scheduler-first-mount-order','app-0801e4b0.asm')}.

**PROVEN modeled earliest timing:** timer injection requiresCEN+DIER, eligible masks and elapsed logical time after enable. TIM4/5PSC5999,CCR1=10 give1ms at the inherited60MHz APB timer clock. TIM2PSC170/ARR999 gives2.85ms; the test waits3 modeled milliseconds and deliberately uses delayed Storage completion so this update can validly precede snapshot. An earlier preliminary immediate-after-CEN experiment was replaced, not counted as earliest-period evidence. The millisecond counter source is the inheritedPhase59 controlled model; no CPU-cycle-exact peripheral clock claim is made. {L('irq-tests.json')}, {L('irq_observer.py')}.

**PROVEN normal record order:**Main20000354 has slot6 mode2/1000 ticks and slot11 mode2/1 tick;5 and7 inactive at snapshot. UI20000360 slots are inactive. The Main dispatcher is after synchronous first mount; a pending hardware tick does not preempt into that dispatcher. TIM9's clock/IRQ is configured butCR1.CEN remains0 until explicit activation. SysTick5998C→6B748 calls599B8 to advance2000081C, then increments20006A28; only the old timeout guard can touchD70, and only for old schema ACTIVE/magic. {P('phase59-scheduler-first-mount-order','timer-callback-order.md')}, {P('phase59-scheduler-first-mount-order','early-systick.json')}.

**PROVEN tested handlers:**IRQ28 update reaches25AE8;IRQ30/50 reach5760C and return; first mount remains valid. **UNKNOWN separate timer branches:**TIM2 channel4→1EEB0 and resulting display/DMA callbacks under accumulated frame state; RTC alarm223B0→[200069F0] after22308 arms it in a held-power sequence. These exact paths are not promoted to exhaustive exclusion from update-only tests. RTC alarm is initially disarmed (CR1000 lacksALRAE); the falling/low power-edge test disarms it again.

**PROVEN adapted model:** native owner tick touches only control32 whenACTIVE, never geometry inVALID/EXPORTED;5000-tick wrap deadline and lateSUCCESS absorption are checked. This is not the still-unadapted native6B748 call site. {L('owner-tick.asm')}, {L('owner-model-tests.json')}.''')
    table='|IRQ|Injection PC / event|Native instructions|Mount return|Private writes|\n|---|---|---:|---:|---:|\n'
    for r in test['cases']:table+=f"|{r['irq']}|{r['injection']['pc']}: {r['injection']['event']}|{r['instructions']}|{r['mount_status']}|0|\n"
    save('irq-preemption-tests.md',f'''# Phase60 — native preemption cases

**PROVEN bounded cases:** all nine injected external events return to normal native flow and then1AE06 withstatus0/type2. Narrow private-write hooks record0 intents; watched write/erase/file-mutation entries record0. Native registration/BPB parsing and kernel/Storage queues are inherited unchanged. Geometry records collected at the final checkpoint are persisted per case. {L('irq-tests.json')}, {L('run_irq_cases.py')}.

{table}
Entry occurs only withIRQenabled,PRIMASK/FAULTMASKclear, priority aboveBASEPRI and no active handler. Basic hardware frames/unstack are modeled; actual pinned handlers execute. GenericPOP-to-EXC_RETURN is handled for native IRQs as well asBX LR. Early USART entry can precede task creation; the observer no longer incorrectly tries to read aTCB name through null. That observer defect was corrected and its affected cases rerun; it was not a firmware failure. {L('prepare.py')}, {L('instrumented_startup.py')}.

**PROVEN modeled source constraints:** serial input waits at least1 logical millisecond afterUE/RXNEIE (longer than a31250-baud byte); DMA70 requires started streamEN/TCIE and an issued NOR command; QSPI92 requiresTCIE and an issued command; SD49 requires busy command and enabled command-timeout mask. Completion/absence timing for NOR/SD remains explicitly supplied, as inPhase59; it is not measured hardware timing. Firing a default/uninitialized USB interrupt was deliberately not used as a test.

**UNKNOWN untested eligible branches/combinations:**TIM2 compare4→1EEB0; an armed RTC alarm223B0→[200069F0] after a held-power sequence; cascaded display DMA59/60 under that compare branch; nested/repeated events and extended FP exception frames. Pending status registers use inherited simple shadows rather than a full peripheral W0C/W1C/clock engine. Thus individual handler results are not universal IRQ closure. Phase59 SysTick tests are preserved, not rerun. {P('phase59-scheduler-first-mount-order','early-systick.json')}.''')
    save('state12-full-liveness.md',f'''# Phase60 — full-lifetime writer census

**PROVEN known owner ledger:** the existing12-byte record is20044D70..D7B. The saved per-bytePhase57 ledger contains23 known direct accesses; it is preserved and referenced rather than rescanned as if new. Phase60 adds native owner semantics and actual first-mount scalar collection, but does not claim a globally complete alias/range proof. {P('phase57-first-mount-provenance','ownership.json')}, {L('owner-model-tests.json')}.

|Lifetime / writer|Exact old path|Adapted obligation / evidence|
|---|---|---|
|Early initialization|6B708 clears+4;6B70A clears+8;6B714 old magic|Native init fragment clears all12 before publishing allocator limit; later idempotent invocation preserves geometry|
|Getter / USB ready|5DBCC→6B6CC;6B722 reads magic|Getter model never writes12; real getter currently rejects new control rather than implementing export|
|SysTick / timeout|5998C→6B748;6B794 writes+4|Native new tick readsACTIVE/start tick and changes only control toFAILED|
|Parser/SysEx admission|24D2C→6B798;6B820/+4,6B824/+5,6B830/+8|Compare same epoch and all8 geometry bytes before transport overlay; native fragment tested, call-site wiring not installed|
|Raw transaction|6B850;6B8DA/+6;6B8DE/6B924/6BA02/+7|OnlyACTIVE overlay; actual chunk/USB/Storage callbacks still require adapter integration|
|Failure/quarantine|6B9FE/+4|Control FAILED absorbs late completion; owner retained|
|Corrected completion|6B9DC bypasses6B9EC;6BC46 stores+4|New complete fragment checksACTIVE and updates control; old byte store must be redirected|
|Mount snapshot/epoch|1AE06;197A0/19A92;1AE3A/1AEDE|Actual record collected; begin/commit/invalidate fragments tested; native invalidator/commit hooks not wired|
|Range-based init/copy|Scatter source[20000000,20003D02),zero[20003D04,20006A54)|ExcludesD70, previously qualified; unchanged|
|Heap / stack / DMA|1D7D0 allocator; active task stacks; DMA destinations|Early limitD70 honored in existing fixtures; new native helper stack36 bytes; tested reads excludeD70. Post-mount USB/range-copy aliases are not fully traced through old raw/parser callbacks|

**PROVEN geometry liveness in the adapted native model:** actual first-mount46-byte scalars are collected from20000A98,20000AB0 and20000AD0, packed losslessly with the preservedPhase56 codec, copied into the private payload by native commit, exported byte-for-byte and compared again by native authorization. NonACTIVE tick, getter, parser-reset model and host wait preserve them. The model's parser-reset is an explicit no-write owner operation, **not execution of every real parser-reset callback**. {L('adapted_owner.py')}, {L('owner-export.asm')}, {L('owner-authorize.asm')}.

**UNKNOWN full native lifetime:** the actual24D2C→6B798/6B850 paths and their reset/range-copy/late completion descendants have not been redirected and replayed with this union. No whole-image USB-ready→geometry-export→host-decision→raw pipeline is claimed. Existing collision evidence remains relevant, not superseded: {P('phase56-geometry-snapshot-lifecycle','liveness-tests.json')}.

The record's8 geometry bytes become dead only after successful atomic authorization, not on export. The later8-byte transport overlay is intentional lifetime reuse, not simultaneous independent authorization storage.''')
    save('adapted-owner-model.md',f'''# Phase60 — native adapted ownership model

**PROVEN model implementation:**12 native Thumb fragments execute solely in emulator memory0807D000 plus180-hex slots. They are stored only as disassembly/evidence hashes; no binary/SYX/candidate is produced. Private record staysD70..D7B, with control32 (phase3/unexpected1/epoch28) plus8-byte geometry until authorization. Host stimulus/return buffers at2004F000 are test-only caller parameters, not new persistent device storage. {L('adapted_owner.py')}, {L('owner-model-tests.json')}.

**PROVEN native rules:**init clears before publishingD70 reservation and preserves later calls; begin acceptsBOOT0→MOUNTING16 only; commit accepts16, copies8 bytes, DMB publishesVALID11; export accepts11/12, copies8 and publishesEXPORTED12; authorization requirescontrol12,epoch1 and exact two32-bit geometry words plus session1..127, then initializes fixed coefficient-mask2/session/chunk0/owner1/starttick and publishesACTIVE13 underPRIMASK. Timeout changes control only; wrap deadline5000 is unsigned. Invalidation setsunexpected+FAILED; complete accepts onlyACTIVE and cannot overwriteFAILED. Raw-start guard requires exactACTIVE/epoch1/mask2. Getter/parser-reset model has no record write. {L('owner-init.asm')}, {L('owner-commit.asm')}, {L('owner-authorize.asm')}, {L('owner-tick.asm')}, {L('owner-complete.asm')}.

**PROVEN tests:**11 native boundary cases plus22 event-by-event12-byte comparisons to the independentPhase57 State oracle. Cases include idempotent init/getter, parser reset model, nonACTIVE tick, exact export, wrong epoch/geometry low/high/session, invalidation before/after export and after admission, wrap4999/5000, late completion, terminal one-shot. Every fragment preservesR0..R12, supportedAPSR and incomingPRIMASK0/1; neighboring canaries survive. The native epoch/byte comparison is stronger than accepting aCRC alone; a host command carrying these exact proof fields is not implemented here.

**PROVEN contract limits:** source scalar validation/packing uses the existing checked Python codec before native commit; no native source collector/packer is installed at1AE06. Geometry liveness is proved only inside these adapted owners. Raw-start records guarded admission in a test counter; it is not a full chunk engine or an independently proved duplicate-request interlock. Coefficient-only mask2 is modeled; identity mask1/3 remains gated independently. A complete versioned host token/session protocol and old call-site/return ABI integration are not inferred.

**UNKNOWN integration:**actual5DBCC/6B6CC,6B748,6B798,6B850 and6BC46 still implement the historical schema in the pinned image. The fragments demonstrate coherent native semantics, not that those old paths cannot still write the geometry. No candidate qualification follows from this isolated model.''')
    save('final-first-epoch-verdict.md',f'''# Phase60 — exact final gates

Can any valid early IRQ/timer/USB callback mutate82000..821FF before geometry snapshot1AE06?

**UNKNOWN**

Separately for81000..81016:

**UNKNOWN**

Is the first accepted geometry snapshot proven to occur before any reachable mutation of82000 and remain valid through raw-capture authorization?

**UNKNOWN**

**PROVEN narrowed results:** normal USB initialization/IRQ77 is after the observed first mount; nine eligible individual external IRQ cases return to valid mount with no watched mutation/private write; native adapted owner rules preserve captured/exported geometry and reject invalid epoch/terminal completion in their own model. Existing constructor/scheduler/filesystem/queue evidence remains qualified only in its already stated scopes.

The remaining paths are exactly:

|Path|Unresolved obligation|
|---|---|
|TIM2IRQ28 channel4→1EEB0→display transfer/DMA59/60|Compare branch and callback cascade, beyond tested update branch|
|RTCIRQ41→223B0→[200069F0]=1DA70→1DAE0 after1DA24→22308|Held-power arm/expiration branch, beyond tested falling/low disarm|
|1AE06 plus197A0/19A92/1AE3A/1AEDE|Wire native capture/commit and invalidate all later epoch/binding changes|
|5DBCC→6B6CC;5998C→6B748;24D2C→6B798/6B850;6BC46|Install emulator-only owner adapters and replay actual parser reset/range-copy/Storage+USB completion paths through host authorization, rather than only fragments|

No new generic early-USB-task blocker is retained. No architecture phase, candidate designation, firmware/SYX generation or hardware/MIDI action is authorized by these results.

FINAL PREFLASH PROVENANCE CLOSURE = UNQUALIFIED''')
    save('findings.md',f'''# Phase60 — IRQ/liveness final assessment

**UNKNOWN — final admission.** Phase60 narrows IRQ ordering and implements/tests a native12-byte ownership model; it does not establish complete native first-epoch/lifetime closure.

**PROVEN new evidence:**20 enabled external IRQs are inventoried with vectors/priority/enable points and source conditions. Nine individual eligible source events return to1AE06/status0 with no watched mutation/private write. USBIRQ77 is not enabled in the normal prefix; boot handoff clears its old enable/pending state, and the exact init→IRQ path is identified. {L('early-irq-inventory.md')}, {L('usb-startup-order.md')}, {L('irq-preemption-tests.md')}.

**PROVEN native owner model:**11 boundary cases and22 independent oracle comparisons pass. Geometry collected at the native modeled first mount survives native commit/export/host wait and exact-byte epoch1 authorization. Timeout, invalidation and late completion obey the new control-word semantics; registers/flags/masks and canaries are checked. These are emulator-only fragments, not a wired diagnostic image. {L('state12-full-liveness.md')}, {L('adapted-owner-model.md')}.

**UNKNOWN exact remaining paths:**TIM2 channel4→1EEB0/display DMA; RTC223B0→[200069F0] following power-hold arm; native1AE06/197A0/19A92/1AE3A/1AEDE hooks; actual6B6CC/6B748/6B798/6B850/6BC46 owner adaptation and parser/range-copy/completion replay. The final report lists each obligation without restarting constructor, scheduler, filesystem or queue research. {L('final-first-epoch-verdict.md')}.

Pre-snapshot mutation answer is **UNKNOWN** separately for82000 and81000. The combined first-epoch-through-authorization answer is **UNKNOWN**. No destructive counterexample is newly asserted; absence in these tests is not complete exclusion. H4 remains unchanged; no forced semaphore release or retry is introduced. Phase53 is not reopened.

All work is offline. Historical images/reference sources and savedPhase59 evidence remain unchanged. No device/MIDI access, binary firmware/SYX output or transmission occurred.

FINAL PREFLASH PROVENANCE CLOSURE = UNQUALIFIED''')
    print('Eight Phase60 reports written')
if __name__=='__main__':main()
