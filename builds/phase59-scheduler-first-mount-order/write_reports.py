"""Write Phase59 reports from persisted evidence; never execute historical suites."""
from pathlib import Path
import json,struct
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def link(name,label=None):
    p=OUT/name
    return f'[{label or name}](<{p.as_posix()}>)'
def old(phase,name,label=None):
    p=ROOT/'builds'/phase/name
    return f'[{label or name}](<{p.as_posix()}>)'
def save(name,text):(OUT/name).write_text(text.strip()+'\n',encoding='utf8')
def main():
    rows=json.loads((OUT/'case-summary.json').read_text())['cases']
    valid=json.loads((OUT/'modeled-valid-startup.json').read_text())
    evidence=link('native_startup.py')+', '+link('modeled-valid-startup.json')+', '+link('case-summary.json')
    table='|Case|Native instructions after constructors|Mount status|Private write intents|\n|---|---:|---:|---:|\n'
    for r in rows:table+=f"|{r['case']}|{r['instructions']}|{r['status'] if r['status'] is not None else 'not reached'}|{r['writes']}|\n"
    save('findings.md',f'''# Phase59 — scheduler to first mount

**UNKNOWN — final qualification.** The clock frontier has been crossed and the native application scheduler/queues now reach the first NOR mount return at `0801AE06`. This is substantial new conditional execution evidence, not complete asynchronous producer exclusion or adapted native state liveness.

**PROVEN in the recorded fixtures:** native reset clock/vector prefix `0801BC78`, the previously qualified constructor invocation, startup `0801D3C8`, task constructors, scheduler, SVC/PendSV handlers and native Storage worker execute. First five task selections are **IDLE → Main → UI → Storage → Content**; priorities are all zero. Synthetic FAT16 input returns status0/type2; invalid BPB returns13/type0. No watched mutation entry and no narrow private-record write intent occurs in the nine bounded cases. {evidence}.

{table}
**PROVEN scope limits:** a clock-only shadow run stops at `0803759A`. Advancing past that uses explicitly supplied NOR completion status; successful-array-read cases additionally supply completion notification and synthetic JEDEC/BPB data. SD absence is modeled by command status5. Pre-scheduler time advances one millisecond per counter poll. These are environmental models, not physical data, a native IRQ replay, or authenticated completion. The eight mount-reaching cases include six successful mount cases and two failed mount cases. Source/observation details: {link('postclock-controlflow.md')}.

**UNKNOWN required gaps:** complete early USB interrupt/callback ordering; native earliest timer IRQ producer/arbitration; native adapted 12-byte initialization/getter/timeout/export/admission/raw/terminal integration through authorization; transitive indirect writer/DMA exclusion. The early-USB adversarial case is not claimed passed. The queued-query case tests a well-formed queue state but does not claim a normal boot producer enqueues it before scheduler start. {link('timer-callback-order.md')}, {link('state12-liveness.md')}, {link('first-epoch-verdict.md')}.

The first-epoch answer is **UNKNOWN**. Scheduler-to-snapshot mutation answers are separately **UNKNOWN** for82000..821FF and **UNKNOWN** for81000..81016. Neither is promoted to PROVEN NO from a no-write replay. Historical Phase58 constructor results and Phase53's exhausted interface branch are preserved, not rerun. No hardware/MIDI access or firmware/SYX output occurred.

Smallest next experiment: qualify the early USB interrupt-to-deferred-dispatch boundary against the actual pre-mount ready-list checkpoint, including the native timer notification producer. Then join a concrete emulator-only native lifecycle adaptation to export/authorization; marker survival is insufficient. No new peripheral-wide cold-boot investigation is necessary to name these exact missing boundaries.

SCHEDULER FIRST-MOUNT ORDER = UNQUALIFIED''')
    save('postclock-controlflow.md',f'''# Phase59 — postclock native path

**PROVEN byte predicates:** `0801B266` reads `[r4]`, with runtime `r4=40023800`; `LSLS #14; BPL` waits for bit17. `0801B274` waits for bit29 through `LSLS #2`; `0801B282` waits for bit25 through `LSLS #6`. Native code sets bits16,28,24 respectively before waiting. At `0801B2A0` it requests `RCC_CFGR.SW=2`; the model supplies `SWS=2` before native `0801BCB4` computes SystemCoreClock at20003570. Release iterations2 and8 both reach the same successful mount. No board clock lock timing is asserted. {link('app-0801b1a8.asm')}, {link('app-0801bcb4.asm')}, {link('delayed-clock.json')}.

**PROVEN native continuation:** clock function returns at1B362 → startup1D3EC GPIO1DCDE → two1DD44 interfaces →1DDD4 task creation →1DFEE/1E062 controller/peripheral setup →1E134/1E3A8 wrappers →1D3A0 →1AAD8 SD initialization →1E4B6 on20000354/360 timer activation →1DE78 sets20006A47=1 →1CABC. Exact call events, including indirect destinations, are recorded in each JSON; they are observed edges, not a complete CFG. {link('app-0801d3c8.asm')}, {link('app-0801ddd4.asm')}, {link('app-0801dfee.asm')}, {link('app-0801e3a8.asm')}.

**PROVEN kernel mechanics:** task creator1C91C allocates word-count stack and5C-byte TCB, fills stackA5, stores priority+2C, builds a native basic frame at1D11C, inserts ready nodeTCB+4 using1D312. Ready bitmap is20006148, ready lists start200060D4, current TCB is20006138. New equal-priority task replaces current before scheduling at1CA56..1CA68. Scheduler1CABC creates IDLE last, sets200066E8=1 and20006A28=0, then1D16C configures priorities/SysTick and1D9CC executes SVC at1D9EA. Native handler1D9B0 restores actual current TCB frame, PSP and BASEPRI. {link('app-0801c91c.asm')}, {link('app-0801cabc.asm')}, {link('app-0801d16c.asm')}, {link('app-0801d9cc.asm')}, {link('app-0801d9ac.asm')}.

**PROVEN modeling boundary:** SVC11/PendSV14/SysTick15 basic-frame entry/unstack is supplied by the harness; handlers execute pinned image bytes. Nested exceptions, FP extended frames, NVIC priority truncation/readback, arbitrary external IRQ arbitration and actual time scheduling are not qualified by this harness. SysTick is delivered at eligible idle WFI, plus one explicit early pending case. At first SVC, BASEPRI masks the early tick, so delivery waits for the native SVC handler to clear BASEPRI. This corrected a preliminary invalid injection assumption; the persisted final early-tick run is valid for this narrow model. {link('early-systick.json')}, {link('vectors.json')}.

**PROVEN explicit peripheral seams:** status bit0 at20005550 is supplied for NOR completion. Valid-device cases synthesize EF4019/32MiB JEDEC identity, zeros at81000 and a coherent4096-byte FAT16 BPB atD4000; DMA destinations are filled at3748E after native command setup/wait. Immediate completion flag100 is supplied to the actual Storage object, or delivered later via native1BDE8 in the delayed case. No forced semaphore release is performed. SD status5 models absent-card timeout. Poll-time increments2000081C are a controlled time source, not native timer IRQ execution. {link('native_startup.py')}, {link('delayed-storage.json')}.

**UNKNOWN:** actual peripheral completion/IRQ ownership and all possible callbacks between these boundaries. Thus this path cannot alone authorize capture.''')
    tasks=[('Main','0801D4B0','20007750','2000835C','768 words /3072 bytes','Identity read2520C via wrapper wait23FD6; yields before and during queue completion','Can later perform FS restore/persistence, updater/identity dispatch; proposed12-byte admission/raw owners live here'),('UI','0801D680','200084D0','20008CDC','512 words /2048 bytes','1E4BE(20000360),209E4 polling,1BE60 yield; not initially notification-blocked','Indirect input/event callbacks need closure; observed UI timer records inactive'),('Storage','0805767C','20008D38','20009244','320 words /1280 bytes','Register SD/NOR completion observers, wait1BE1A(flag1), drainSD thenNOR','Can program/erase through queued operations2/3; observed queue traffic is read/control only'),('Content','08022ACC','200092A0','200097B8','320 words /1280 bytes','1BE1A(flag1) then22AE4 drain until empty','Can open/write/delete files via operation dispatch; no observed pre-mount work in normal case'),('IDLE','0801CD30','kernel-owned','2000B17C','256 words /1024 bytes','Ready-list yield1CD44, watchdog feed1D760, WFI1D766','No array mutation in observed path; generic hook/interrupt closure separate')]
    t='|Task|Entry|Object / TCB|Initial priority|Stack|First run / block|Storage and state capability|\n|---|---|---|---:|---|---|---|\n'
    for name,entry,obj,tcb,stack,block,cap in tasks:t+=f'|{name}|{entry}|{obj} / {tcb}|0|{stack}|{block}|{cap}|\n'
    save('task-inventory.md',f'''# Phase59 — tasks alive at modeled first mount

**PROVEN for the native fixture:** all five tasks below exist before first mount. Four application tasks are created by1DDD4, IDLE by1CABC. All are initially ready, priority0; Storage and Content later block on notifications. The `80` argument in Main's wrapper is an observer allocation/capacity argument, **not priority128**. 1BDA2 loads the actual priority from stack+20 into the argument to1C91C;1C940 stores it atTCB+2C. {link('app-0801bd9c.asm')}, {link('app-0801c91c.asm')}, {link('modeled-valid-startup.json')}.

{t}
Task entries above are normalized even addresses; constructor Thumb pointers have bit0 set. The saved initial context contains task argument, normalized entryPC, EXC_RETURN=FFFFFFFD and XPSR Thumb bit; frames are built by native1D11C rather than hand-filled by the host. Stack sizes are requested capacities, not proved high-water margins. {link('app-0801d11c.asm')}.

**PROVEN synchronization:**1BE1A checks object+8 flags; when absent it uses1CDC8 notification wait, removes current ready node via1CF44, and requests PendSV.1BDE8 ORs flags and invokes1CE60 to notify/unblock actual TCB. Per-task TLS pointer is stored atTCB+50 by1CD54; it is not the current priority. NOR backend's byte+8 semaphore starts1 at22F10 and is decremented/restored by native backend operations. {link('app-0801cdc8.asm')}, {link('app-0801cd54.asm')}, {link('app-08022f10.asm')}.

**UNKNOWN global inventory:** no separate USB task was created in this prefix. That does not exclude USB ISR or deferred callbacks, nor tasks conditionally created by a later callback. Direct access to the12-byte record is covered only by the known old-owner ledger, not every task's indirect callees/DMA. {old('phase57-first-mount-provenance','ownership.json')}.''')
    sequence=' → '.join(r['name'] for r in valid['switches'])
    save('first-schedule-order.md',f'''# Phase59 — actual native selections

**PROVEN in the supplied model:** initial priority0 list has count5 and bitmap1; currentTCB2000B17C is IDLE. The list header's index/sentinel is200060DC. Its forward/back links and exact raw header are persisted in `launch`. Equal-priority insertion selects IDLE before SVC; subsequent selection rotates the existing list through the real1CCB0 routine. `CLZ(bitmap)` chooses highest ready priority;1CD14..1CD2C advances the index past sentinel and loads node+0C owner into20006138. This is not a creation-order assumption. {link('modeled-valid-startup.json')}, {link('app-0801ccdc.asm')}, {link('app-0801cd08.asm')}.

Recorded exception-return sequence:

{sequence}

Repeated same-task IDLE entries include **SysTick returns**, not task changes. The JSON field `switches` stores every modeled exception return; its length18 must not be described as18 task changes. First five distinct activations are IDLE, Main, UI, Storage, Content. Later Storage activations service Main's queued identity/control/read requests; Content blocks without consuming a normal pre-mount item. The mount chain begins on Main after identity and display initialization. {link('app-0801d4b0.asm')}, {link('app-0801ec80.asm')}.

**PROVEN conditional delay result:** delaying NOR completion notification for three SysTick wake events runs the real notification/unblock/list path; it reaches status0 with56 exception returns and62681 instructions. No ready-list node is edited by the host. Notification arrival itself is supplied; external IRQ timing is not proved. {link('delayed-storage.json')}.

**UNKNOWN universal order:** preemption by unmodeled external interrupts, early USB dispatch, different on-storage/input state and extended FP frames. No single fixed total order across all such states is asserted.''')
    q='|Enqueue instruction index|Producer TCB|Record opcode / arguments|\n|---:|---|---|\n'
    for x in valid['operations']:
        if x['kind']=='storage enqueue':q+=f"|{x['instruction_index']}|{x['TCB']}|{' / '.join(x['request_words'])}|\n"
    save('queue-order.md',f'''# Phase59 — queue/work ordering

**PROVEN native allocation:**1E3A8 creates two1C-byte wrappers. NOR2000AC94 points to backend20000378; SD2000AD08 points to20000338. Each uses a3-record ring, record size18 hex /24 bytes, created by366E0. Wrapper+8 is ring object,+C pending count,+10 drain/sync flags,+14 Storage task object,+18 completion result. Content has its own2-record ring of48 hex /72-byte work items. These are ARM RAM queues, unrelated to DSP SDRAM. {link('app-0801e3a8.asm')}, {link('app-08023f2c.asm')}, {link('app-08022a0c.asm')}.

**PROVEN observed normal producer chain:**Main1EC80→2520C submits identity read81000/23 bytes; the pre-mount ioctl obtains stride4096; filesystem BPB read becomes physicalD4000/4096. Native enqueue23F68→ring36708 precedes notify1BDE8(Storage,flag1). Storage registers completion observers before draining SD first, NOR second, via24014. Native36732 dequeues,24070 dispatches op0control/op1read/op2program/op3erase/op4sync;240D8 invokes optional completion callback. Each enqueue/dequeue/Storage drain and native ordinal is in the JSON.

{q}
**PROVEN tested scope:** no program/erase enqueue appears in the baseline or injected status-query case. Queue injection allocates32 bytes via the real allocator then invokes real23F68 before SVC with a well-formed read-only control record, rather than editing a queue link. It tests a valid queue state, **not a demonstrated normal pre-scheduler producer**. Normal constructor/startup observed queues are empty at scheduler launch. {link('queued-query.json')}, {link('app-08023f2c.asm')}.

**UNKNOWN complete producer exclusion:** Content operation dispatch22B24 (eleven cases), queued completion callback240D8, indirect UI/USB producers and future binding/remount changes still require transitive reachability/argument proof. A blank queue in a replay does not prove all producer predicates false. Existing preserved producer graph remains scoped: {old('phase45-nor-mutation-closure','nor-mutation-callgraph.md')}. No later B1.3 persistence feature is imported into the SC35D8-derived image by name.''')
    save('timer-callback-order.md',f'''# Phase59 — timers and callbacks

**PROVEN native implementation:**1E480 allocates28-byte software timer records and initializes them through37AAC. At offsets0/+4 are period/current countdown,+8 mode flag,+C callback,+10 argument.1E4BE consumes pending ticks from `[service+4]+A`, decrements armed records, handles one-shot/periodic reload and executes callback at1E51E. Thus a hardware pending tick and a user callback execution are distinct events. {link('app-0801e4b0.asm')}, {link('app-08037aac.asm')}, {old('phase58-preconstructor-liveness-closure','app-0801e480.asm')}.

**PROVEN fixture record state at first mount:** service20000354 has12 slots; slot5 period/countdown1000, inactive, callback080253BD; slot6 period/countdown1000, mode2, callback08025669; slot7 inactive, callback080258C9; slot11 period/countdown1, mode2, callback080234ED. Other slots inactive/zero. Service20000360 has2 zero/inactive records. Complete28-byte records are saved in each run. Main initializes slots5/6/7 during1EC80 before mount; constructor-established slot11 is already present. Exact registration calls appear in `calls`. {link('modeled-valid-startup.json')}, {link('app-0801ec80.asm')}.

**STRONG INFERENCE:** Main's software timer dispatcher is not reached before Main's own synchronous first mount returns; UI's pre-mount dispatcher sees inactive slots. Timer pending accumulation alone therefore does not execute these Main callbacks while Main is blocked on Storage. This does not exclude direct interrupt callbacks or all earlier/alternative epoch roots.

**PROVEN narrow adversarial case:** one pending service tick for both services is supplied at the first UI poll; native UI1E4BE executes and does not call any armed user callback before the mount. Main retains its pending tick. This tests consumer behavior at a valid pending count, **not the native timer IRQ producer or the earliest physical tick/arbitration**. {link('earliest-timer.json')}.

**UNKNOWN:** exhaustive earliest external timer IRQ delivery and callbacks under all valid scheduling states; delayed USB reconfiguration callback248B4 (150-tick scheduling by248CE), its registration predicate and all storage-producing descendants before snapshot. The existing image's implementation must determine reachability; later B1.3 guard timers are not assumed present. No timer-specific PROVEN NO is asserted for settings/flush/delete/NOR/reformat/updater cleanup globally. {old('phase45-nor-mutation-closure','background-write-analysis.md')}.

**PROVEN SysTick consumer:** vector15=0805998D→6B748→599B8 increments2000081C and returns;59992 increments20006A28. This handler does not itself execute the Main software timer callbacks. Early tick is masked at first SVC byBASEPRI, delivered after native unmask, then mount still returns0. {link('app-08059924.asm')}, {link('app-0806b6cc.asm')}, {link('early-systick.json')}.''')
    save('storage-task-startup.md',f'''# Phase59 — Storage startup

**PROVEN native path:** Storage entry5767C runs after Main/UI in the modeled ready-list schedule. It binds SD completion waiter5765A and NOR waiter57650 via each wrapper's vtable+20. It then waits flag1 at576A0, drainsSD at576A6, drainsNOR at576B0, repeats. Waiter57650 consumes notification100; notifier57664 uses100/101. The worker does not invent a read until a producer supplies a record. {link('app-08057650.asm')}, {link('app-08023f2c.asm')}.

**PROVEN observed requests before snapshot:** identity read81000..81016; geometry control query returning4096-byte stride; BPB readD4000..D4FFF for the successful synthetic case. No request to82000..821FF is made. The identity read occurs before first mount. A queue item can precede Storage's first activation: Main's identity submission is processed once Storage registers/waits; preserved object notification flags carry the wake. {link('modeled-valid-startup.json')}.

**PROVEN capability:** op2 and op3 worker branches can program/erase the NOR through22FDC/23078 and374D4/37494/37648; optional callbacks can reach other code. The worker alone supplies no address-range protection that proves upstream producers safe. Normal replay exercising only op0/1 is not a complete mutation proof.

**PROVEN delay test:** delayed completion leaves the read/wait active until a modeled completion notification is delivered using native1BDE8. Native ready-list removal/reinsertion and semaphore restoration execute; no host forced semaphore release is used. This is successful-completion scheduling evidence, not an error-unwind test and does not supersede H4. {link('delayed-storage.json')}, {old('phase31-storage-error-recovery','findings.md')}.

**UNKNOWN:** full earliest USB/timer/Content producer closure and actual controller ISR arbitration, so target preservation remains unqualified separately for both NOR regions.''')
    save('filesystem-to-snapshot.md',f'''# Phase59 — filesystem to snapshot

**PROVEN native chain:** Main1D4B4→1EC80 (identity) →1D4BC→1EEAA (display) →1D4C0→1F0A8→1AE3A (bind NOR backend) →disk vtable→1ADDC→1AE02→19A92→197A0→BPB parse→19A4C→1AE06. Disk20000AA0, filesystem20000AB0, registered pointer20005E5C; geometry20000A98 holdsD4000 base/1000 stride. Native scatter/static constructor1F050 only constructs disk objects. {link('app-0801d4b0.asm')}, {link('app-0801f050.asm')}, {link('app-0801f0a8.asm')}, {link('app-0801addc.asm')}.

|Stage|Context / execution|Preemption and side effects|
|---|---|---|
|Bind1AE3A / register19A92|Synchronous Main|Updates RAM binding/type; scheduling interrupts possible unless masked|
|197A0 mount / status/ioctl|Synchronous Main API with queued worker work|Main may yield/block; Storage executes requests asynchronously|
|Physical read22F94→37430|Storage|Command/DMA setup; modeled completion notification; no array program requested|
|BPB parse / mount commit19A32..19A4A|Main|Updates RAM FS/type/mount ID; exact body preserved fromPhase55|
|Return at1AE06|Main|Native status0/type2 for valid fixture;13/type0 for invalidBPB; no new snapshot hook emitted|

**PROVEN fixture result:** successful input physically readsD4000/4096 through the actual wrapper/worker/backend; it does not bypass diskio or fabricate a ready-list/FS type. The host fills the DMA destination with an explicitly synthetic coherent BPB; this does not authenticate current-unit geometry. Bad BPB reaches the same return PC with failure and must not be accepted as geometry. {link('modeled-valid-startup.json')}, {link('invalid-bpb.json')}.

**PROVEN retained prior analysis:** mount type clear/rebuild, alternate197A0 remount clients, cached fast path, mount ID wrap and snapshot's exact pre-IT boundary were already inspected inPhase55–58; those results are reused without rerunning old suites. {old('phase55-precleanup-geometry-snapshot','mount-cases.json')}, {old('phase58-preconstructor-liveness-closure','first-epoch-proof.md')}.

**UNKNOWN:** all external interrupt/callback producers during Main's waits, complete prior epoch proof, adapted native snapshot commit and later interlock. Native1AE06 currently has no new geometry-commit hook in this historical image. Consequently checkpoint arrival alone is not a valid first-epoch attestation.''')
    save('state12-liveness.md',f'''# Phase59 — 12-byte ownership

**PROVEN new bounded evidence:** marker0123456789ABCDEF55AA55AA at20044D70..20044D7B remains byte-identical with zero narrow write intents in all9 new runs. Reservation uses existing allocator limit20002B44=D70, before constructors. No new RAM capacity is allocated for lifecycle state. Tests exercise native startup/task creation/selected SysTick/queue/mount paths. They do **not** contain a committed geometry record or execute adapted export/authorization/raw capture. {link('case-summary.json')}, {link('native_startup.py')}.

|Known owner|Native access / lifetime obligation|
|---|---|
|Getter6B6CC|6B708 clears+4;6B70A clears+8;6B714 writes oldNOR4magic;6B722 later checksmagic. Under earlyD70 reservation with new control format, mismatch returns0 at6B744 rather than admitting export. Merely preventing clears does not make the diagnostic usable.|
|SysTick6B748|Reads old magic/state/start,6B794 writes quarantine byte+4 only if old schema ACTIVE and elapsed>=5000; new schema must replace interpretation. Marker test takes magic-mismatch path, not every old state branch.|
|Admission6B798|6B820 writes state+4;6B824 session+5;6B830 tick+8. These collide with geometry until atomic schema handover is implemented.|
|Raw6B850|6B8DA chunk+6;6B8DE/6B924/6BA02 owner+7;6B9FE failure+4; required postauthorization overlay only.|
|Corrected terminal|6BC46 success+4 underPRIMASK; old6B9EC bypassed by6B9DC, not counted as live.|
|Allocator / task stacks|Native allocations below reserved limit in bounded runs; stack/dma/global aliases through USB/export/authorization are not globally closed.|

Per-byte source of truth: {old('phase57-first-mount-provenance','ownership.json')}; native getter/timeout bytes: {link('app-0806b6cc.asm')}. Existing collision tests: {old('phase56-geometry-snapshot-lifecycle','liveness-tests.json')}.

**UNKNOWN adapted native liveness:** no coordinated native BOOT→MOUNTING→VALID→EXPORTED→ACTIVE initializer, mount commit, getter, timeout, authorization and raw/terminal adaptation exists in the tested image. Geometry must remain immutable through authorization, then payload+4..11 may become transport fields; control epoch/failure must not be overwritten by late completion. Existing abstract lifecycle/isolated commit helpers are not a substitute. {old('phase58-preconstructor-liveness-closure','adapted-ownership.md')}.

**UNKNOWN global unexpected writers:** all indirect range copies, task/IRQ stack high water and DMA descriptors after snapshot remain unclosed. No earlier phase is superseded by a marker-only run. This required gate remains open even if pre-mount producer exclusion is later closed.''')
    save('first-epoch-verdict.md',f'''# Phase59 — first epoch and separate region verdicts

From scheduler start through the geometry snapshot at0801AE06, can any reachable task, queue item, timer or callback write/erase82000..821FF?

**UNKNOWN**

Separately, can one write/erase81000..81016?

**UNKNOWN**

Is0801AE06 reached in the first relevant filesystem epoch before any reachable mutation of82000?

**UNKNOWN**

**PROVEN in bounded modeled executions:** first native19A92/197A0 call is Main's NOR mount; preceding Main identity operation is a read, Storage queue operations are control/read, Content has no normal work, no watched mutation entry occurs and all tested private markers survive. Valid/invalid mount outcomes are distinguished. This narrows scheduling hypotheses beyondPhase58 but does not prove universal reachability. {evidence}.

**STRONG INFERENCE normal-input ordering:** same-task sequencing delays Main restore1F0F0 and its timer polling until after1AE06; empty Content/SD work and inactive UI timer slots explain the observed absence of earlier filesystem activity. Interrupt-deferred USB/control work and native timer event arrival are not completely excluded.

|Gate|Result / reason|
|---|---|
|Clock native normal predicate|PROVEN in explicit ready-bit model, not physical lock timing|
|First selections / real frames / queue worker|PROVEN within native scheduler/basic-frame model|
|Delayed Storage / earlySysTick|PROVEN bounded successful-completion cases; actual peripheral IRQ arbitration UNKNOWN|
|Earliest timer callback|PROVEN pending-tick consumer case only; native earliest producer/arbitration UNKNOWN|
|Queue present|PROVEN injected well-formed control item; normal prestart producer not established|
|Early USB runnable|UNKNOWN; no separate USB task exists in observed inventory; IRQ/callback path not tested to closure|
|Mount success/failure|PROVEN native parse/return with synthetic device data|
|82000 no earlier mutation|UNKNOWN complete producer exclusion; no counterexample asserted|
|81000 preservation|UNKNOWN independently; explicit identity writer25228 erases[81000,82000), never infer82000 damage from that edge|
|Adapted12-byte liveness through authorization|UNKNOWN; adapters not implemented/tested|

**PROVEN restrictions:** only current-phase evidence text/scripts/JSON were written; historical candidate and pinned sources remain hash-checked. No image/SYX/device transaction was produced. H4 remains failure for device-side in-session recovery; successful completion models do not qualify failure unwinding. Phase53 is not reopened.

Smallest next work is the early USB ISR→deferred-dispatch and native timer-producer ordering at this actual scheduler checkpoint, then concrete emulator-only owner-adapter replay. Do not substitute another quiet replay for those closures.

SCHEDULER FIRST-MOUNT ORDER = UNQUALIFIED''')
    print('Wrote 10 Phase59 reports')
if __name__=='__main__':main()
