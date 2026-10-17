> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase59 — actual native selections

**PROVEN in the supplied model:** initial priority0 list has count5 and bitmap1; currentTCB2000B17C is IDLE. The list header's index/sentinel is200060DC. Its forward/back links and exact raw header are persisted in `launch`. Equal-priority insertion selects IDLE before SVC; subsequent selection rotates the existing list through the real1CCB0 routine. `CLZ(bitmap)` chooses highest ready priority;1CD14..1CD2C advances the index past sentinel and loads node+0C owner into20006138. This is not a creation-order assumption. modeled-valid-startup.json (local-only reference: `builds/phase59-scheduler-first-mount-order/modeled-valid-startup.json`; not distributed), app-0801ccdc.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-0801ccdc.asm`; not distributed), app-0801cd08.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-0801cd08.asm`; not distributed).

Recorded exception-return sequence:

IDLE → Main → UI → Storage → Content → IDLE → IDLE → Main → UI → IDLE → IDLE → Storage → Main → UI → IDLE → IDLE → Storage → Main

Repeated same-task IDLE entries include **SysTick returns**, not task changes. The JSON field `switches` stores every modeled exception return; its length18 must not be described as18 task changes. First five distinct activations are IDLE, Main, UI, Storage, Content. Later Storage activations service Main's queued identity/control/read requests; Content blocks without consuming a normal pre-mount item. The mount chain begins on Main after identity and display initialization. app-0801d4b0.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-0801d4b0.asm`; not distributed), app-0801ec80.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-0801ec80.asm`; not distributed).

**PROVEN conditional delay result:** delaying NOR completion notification for three SysTick wake events runs the real notification/unblock/list path; it reaches status0 with56 exception returns and62681 instructions. No ready-list node is edited by the host. Notification arrival itself is supplied; external IRQ timing is not proved. delayed-storage.json (local-only reference: `builds/phase59-scheduler-first-mount-order/delayed-storage.json`; not distributed).

**UNKNOWN universal order:** preemption by unmodeled external interrupts, early USB dispatch, different on-storage/input state and extended FP frames. No single fixed total order across all such states is asserted.
