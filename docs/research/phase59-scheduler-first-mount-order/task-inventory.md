> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase59 — tasks alive at modeled first mount

**PROVEN for the native fixture:** all five tasks below exist before first mount. Four application tasks are created by1DDD4, IDLE by1CABC. All are initially ready, priority0; Storage and Content later block on notifications. The `80` argument in Main's wrapper is an observer allocation/capacity argument, **not priority128**. 1BDA2 loads the actual priority from stack+20 into the argument to1C91C;1C940 stores it atTCB+2C. app-0801bd9c.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-0801bd9c.asm`; not distributed), app-0801c91c.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-0801c91c.asm`; not distributed), modeled-valid-startup.json (local-only reference: `builds/phase59-scheduler-first-mount-order/modeled-valid-startup.json`; not distributed).

|Task|Entry|Object / TCB|Initial priority|Stack|First run / block|Storage and state capability|

|---|---|---|---:|---|---|---|

|Main|0801D4B0|20007750 / 2000835C|0|768 words /3072 bytes|Identity read2520C via wrapper wait23FD6; yields before and during queue completion|Can later perform FS restore/persistence, updater/identity dispatch; proposed12-byte admission/raw owners live here|

|UI|0801D680|200084D0 / 20008CDC|0|512 words /2048 bytes|1E4BE(20000360),209E4 polling,1BE60 yield; not initially notification-blocked|Indirect input/event callbacks need closure; observed UI timer records inactive|

|Storage|0805767C|20008D38 / 20009244|0|320 words /1280 bytes|Register SD/NOR completion observers, wait1BE1A(flag1), drainSD thenNOR|Can program/erase through queued operations2/3; observed queue traffic is read/control only|

|Content|08022ACC|200092A0 / 200097B8|0|320 words /1280 bytes|1BE1A(flag1) then22AE4 drain until empty|Can open/write/delete files via operation dispatch; no observed pre-mount work in normal case|

|IDLE|0801CD30|kernel-owned / 2000B17C|0|256 words /1024 bytes|Ready-list yield1CD44, watchdog feed1D760, WFI1D766|No array mutation in observed path; generic hook/interrupt closure separate|

Task entries above are normalized even addresses; constructor Thumb pointers have bit0 set. The saved initial context contains task argument, normalized entryPC, EXC_RETURN=FFFFFFFD and XPSR Thumb bit; frames are built by native1D11C rather than hand-filled by the host. Stack sizes are requested capacities, not proved high-water margins. app-0801d11c.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-0801d11c.asm`; not distributed).

**PROVEN synchronization:**1BE1A checks object+8 flags; when absent it uses1CDC8 notification wait, removes current ready node via1CF44, and requests PendSV.1BDE8 ORs flags and invokes1CE60 to notify/unblock actual TCB. Per-task TLS pointer is stored atTCB+50 by1CD54; it is not the current priority. NOR backend's byte+8 semaphore starts1 at22F10 and is decremented/restored by native backend operations. app-0801cdc8.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-0801cdc8.asm`; not distributed), app-0801cd54.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-0801cd54.asm`; not distributed), app-08022f10.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-08022f10.asm`; not distributed).

**UNKNOWN global inventory:** no separate USB task was created in this prefix. That does not exclude USB ISR or deferred callbacks, nor tasks conditionally created by a later callback. Direct access to the12-byte record is covered only by the known old-owner ledger, not every task's indirect callees/DMA. ownership.json (local-only reference: `builds/phase57-first-mount-provenance/ownership.json`; not distributed).
