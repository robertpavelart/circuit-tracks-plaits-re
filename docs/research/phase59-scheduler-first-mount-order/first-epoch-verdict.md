> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase59 — first epoch and separate region verdicts

From scheduler start through the geometry snapshot at0801AE06, can any reachable task, queue item, timer or callback write/erase82000..821FF?

**UNKNOWN**

Separately, can one write/erase81000..81016?

**UNKNOWN**

Is0801AE06 reached in the first relevant filesystem epoch before any reachable mutation of82000?

**UNKNOWN**

**PROVEN in bounded modeled executions:** first native19A92/197A0 call is Main's NOR mount; preceding Main identity operation is a read, Storage queue operations are control/read, Content has no normal work, no watched mutation entry occurs and all tested private markers survive. Valid/invalid mount outcomes are distinguished. This narrows scheduling hypotheses beyondPhase58 but does not prove universal reachability. [native_startup.py](<../../../builds/phase59-scheduler-first-mount-order/native_startup.py>), modeled-valid-startup.json (local-only reference: `builds/phase59-scheduler-first-mount-order/modeled-valid-startup.json`; not distributed), case-summary.json (local-only reference: `builds/phase59-scheduler-first-mount-order/case-summary.json`; not distributed).

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

SCHEDULER FIRST-MOUNT ORDER = UNQUALIFIED
