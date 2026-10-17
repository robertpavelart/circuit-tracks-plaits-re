> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase59 — scheduler to first mount

**UNKNOWN — final qualification.** The clock frontier has been crossed and the native application scheduler/queues now reach the first NOR mount return at `0801AE06`. This is substantial new conditional execution evidence, not complete asynchronous producer exclusion or adapted native state liveness.

**PROVEN in the recorded fixtures:** native reset clock/vector prefix `0801BC78`, the previously qualified constructor invocation, startup `0801D3C8`, task constructors, scheduler, SVC/PendSV handlers and native Storage worker execute. First five task selections are **IDLE → Main → UI → Storage → Content**; priorities are all zero. Synthetic FAT16 input returns status0/type2; invalid BPB returns13/type0. No watched mutation entry and no narrow private-record write intent occurs in the nine bounded cases. [native_startup.py](<../../../builds/phase59-scheduler-first-mount-order/native_startup.py>), modeled-valid-startup.json (local-only reference: `builds/phase59-scheduler-first-mount-order/modeled-valid-startup.json`; not distributed), case-summary.json (local-only reference: `builds/phase59-scheduler-first-mount-order/case-summary.json`; not distributed).

|Case|Native instructions after constructors|Mount status|Private write intents|

|---|---:|---:|---:|

|native-startup|343229|not reached|0|

|modeled-startup|58423|1|0|

|modeled-valid-startup|59306|0|0|

|delayed-clock|59360|0|0|

|early-systick|59335|0|0|

|delayed-storage|62681|0|0|

|earliest-timer|59340|0|0|

|queued-query|61171|0|0|

|invalid-bpb|59163|13|0|

**PROVEN scope limits:** a clock-only shadow run stops at `0803759A`. Advancing past that uses explicitly supplied NOR completion status; successful-array-read cases additionally supply completion notification and synthetic JEDEC/BPB data. SD absence is modeled by command status5. Pre-scheduler time advances one millisecond per counter poll. These are environmental models, not physical data, a native IRQ replay, or authenticated completion. The eight mount-reaching cases include six successful mount cases and two failed mount cases. Source/observation details: [postclock-controlflow.md](<postclock-controlflow.md>).

**UNKNOWN required gaps:** complete early USB interrupt/callback ordering; native earliest timer IRQ producer/arbitration; native adapted 12-byte initialization/getter/timeout/export/admission/raw/terminal integration through authorization; transitive indirect writer/DMA exclusion. The early-USB adversarial case is not claimed passed. The queued-query case tests a well-formed queue state but does not claim a normal boot producer enqueues it before scheduler start. [timer-callback-order.md](<timer-callback-order.md>), [state12-liveness.md](<state12-liveness.md>), [first-epoch-verdict.md](<first-epoch-verdict.md>).

The first-epoch answer is **UNKNOWN**. Scheduler-to-snapshot mutation answers are separately **UNKNOWN** for82000..821FF and **UNKNOWN** for81000..81016. Neither is promoted to PROVEN NO from a no-write replay. Historical Phase58 constructor results and Phase53's exhausted interface branch are preserved, not rerun. No hardware/MIDI access or firmware/SYX output occurred.

Smallest next experiment: qualify the early USB interrupt-to-deferred-dispatch boundary against the actual pre-mount ready-list checkpoint, including the native timer notification producer. Then join a concrete emulator-only native lifecycle adaptation to export/authorization; marker survival is insufficient. No new peripheral-wide cold-boot investigation is necessary to name these exact missing boundaries.

SCHEDULER FIRST-MOUNT ORDER = UNQUALIFIED
