> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase36 — native bootloader PendSV context qualification

**PROVEN:** the captured first PendSV completes using architectural exception entry/return and the unchanged native handler/scheduler. Official stock passes first; the existing memory-only diagnostic control passes identically. This qualifies the observed privileged basic-frame IDLE→bootloader Main switch, not complete boot or a general NVIC/RTOS implementation.

**PROVEN:** no firmware image is generated, hardware accessed, reference/pinned sources edited, or SDMMC behavior investigated. Phase26–35 evidence remains byte-exact. `trace.py` derives from phase35; its optional adapter and the new post-scheduler stop are the only execution-model extensions. `svc.py` is an exact copy of the qualified phase35 implementation. Existing ideal RCC/NOR/timing premises remain conditional.

## Captured pending state

**PROVEN:** stock runs from fresh reset through the qualified SVC path. At `$08002A6E`, the full CPU register snapshot and full SRAM SHA match the archived phase35 stock checkpoint **before** PendSV entry. This is not a separately invented scheduler fixture. stock.json (local-only reference: `builds/phase36-pendsv-context/stock.json`; not distributed) `PendSV[0].captured` records CPU registers, both stack windows, scheduler bytes, TCB/context bytes, NVIC pending/active arrays, VTOR, AIRCR, SHPR3, SHCSR and FPCCR/FPCAR.

| Pre-entry field | Exact value |
|---|---|
| PC / LR | `$08002A6E / $08002D65` |
| MSP / PSP | `$2004FFE0 / $20007EA0` |
| CONTROL / IPSR | `$2 / $0`: privileged PSP Thread |
| PRIMASK / BASEPRI / FAULTMASK | `$0 / $0 / $0` |
| xPSR | `$21000000` |
| r0 / r1 / r2 / r3 | `$4 / $A5A5A5A5 / $A5A5A5A5 / $A5A5A5A5` |
| r4 / r5 / r6 | `$E000ED04 / $10000000 / $20005204` |
| r7 / r8 / r9 / r10 / r11 / r12 | each `$A5A5A5A5` |
| ICSR pending / VECTACTIVE | `$10000000` /0 |
| SHCSR / SHPR3 / AIRCR | `$00070000 / $F0F00000 / $05FA0300` |
| PendSV priority / PRIGROUP | `$F0 / 3` |
| current-TCB global / TCB | `$20005268 / $20007EB8` |
| outgoing task / old saved-context pointer | `IDLE / $20007E6C` |
| scheduler base / ready bitmap / ready count | `$20005204 / $1 / 4` |

**PROVEN:** no external NVIC pending/active bits are present in the captured mapped-system state. There is no active preempted exception. The pending request is the native IDLE `STR` at `$08002A6C`, not a host-written scheduling request. `FPCCR=$C0000000`, CONTROL.FPCA=0; no active extended FP frame is required.

**UNKNOWN:** the inherited flat-MMIO capture is not a complete silicon NVIC snapshot. In particular, raw phase35 ICSR omits read-only derived RETTOBASE/VECTPENDING fields. Phase36 preserves that exact pre-entry backing value for comparison, then explicitly derives the fields required for its sole-active PendSV entry/return. This does not establish arbitrary priority arbitration or interrupt timing.

## Architectural entry

**PROVEN within the observed model:** PRIMASK/FAULTMASK/BASEPRI allow PendSV. With Thread priority and no competing pending/active exception, the observed priority grouping does not alter admission. The model rejects unsupported masking, other pending system exceptions, external arbitration and nested entry before changing CPU/SRAM state.

**PROVEN:** VTOR `$08000000`, slot `$08000038`, vector `$0800312D`, executable handler entry `$0800312C`. Asynchronous entry preserves return PC `$08002A6E` without incrementing it. Hardware stacking uses PSP `$20007E80–$20007E9F`, with no pad for this aligned incoming PSP. Words are r0=4, r1/r2/r3/r12=A5 fill, lr=`$08002D65`, pc=`$08002A6E`, xPSR=`$21000000`. Handler mode uses unchanged MSP `$2004FFE0`, CONTROL.SPSEL=0, IPSR=14, LR=`$FFFFFFFD`. Pending is consumed; ICSR=`$0000080E`, SHCSR=`$00070400` while active.

**PROVEN architectural basis:** PendSV pending and active state are separate; basic-frame exception entry/return selects the stack through EXC_RETURN; RETTOBASE indicates no preempted active exception here. The implementation follows [Arm Cortex-M7 DUI0646C, exception model and ICSR](https://documentation-service.arm.com/static/61efd8352dd99944d05142d1). [pendsv.py](<../../../builds/phase36-pendsv-context/pendsv.py>) `Model.enter_pendsv` performs only these architectural changes; vector lookup determines handler execution. It does not supply a next task, fake scheduler success, or skip native code.

## Native outgoing save and scheduler selection

**PROVEN:** 0800312c.asm (local-only reference: `builds/phase36-pendsv-context/0800312c.asm`; not distributed) and `native_trace` record the actual path:

- `$0800312C MRS r0,PSP` obtains the stacked hardware-frame pointer `$20007E80`.
- `$08003134–$08003136` resolve current TCB through `$20005268`.
- `$08003138` tests EXC_RETURN bit4. FP save `$0800313E` is not executed for the observed basic frame.
- `$08003142 STMDB r0!,{r4-r11,lr}` writes36bytes at `$20007E5C–$20007E7F`; r4/r5/r6 have the nontrivial pre-entry values above, r7-r11 retain native A5 fill, and saved LR=`$FFFFFFFD`.
- `$08003146 STR r0,[r2]` stores `$20007E5C` into IDLE TCB field `$20007EB8+0`. This is the saved PSP/context pointer; the live hardware-frame PSP remains `$20007E80` until incoming restore.
- `$08003148` saves r0/r3 on MSP. `$0800314E` disables interrupts, `$08003150` sets BASEPRI=`$C0`, barriers run, and `$0800315C` re-enables interrupts under that priority mask.
- `$0800315E BL $080029D8` executes the real scheduler. No generic FreeRTOS scheduler substitute is used.

**PROVEN:** 080029d8.asm (local-only reference: `builds/phase36-pendsv-context/080029d8.asm`; not distributed) identifies the native decision:

| Native access / instruction | Observed role |
|---|---|
| scheduler+$80 (`$20005284`) | suspension state0; ordinary selection branch taken |
| `$080029EA`, scheduler+$78 (`$2000527C`) | yield-pending field written0 |
| `$080029EC–$08002A0E` | outgoing stack-base lookup via TCB+$30 and four native `$A5A5A5A5` stack-guard checks |
| `$08002A1C–$08002A2A` | ready bitmap1; CLZ/RSB derives priority0, list stride20bytes |
| ready list `$20005204` | list count4, old index `$2000520C` |
| `$08002A42–$08002A46` | follows next node `$2000648C`; writes new list index to `$20005208` |
| `$08002A50–$08002A54` | node owner at `$20006498` is TCB `$20006488`; stores this into current-TCB global `$20005268` |

**PROVEN:** selected TCB `$20006488` contains name `Main`, saved context `$2000643C`, stack base `$20005888`, priority0. Its68-byte context exactly equals the earlier native `$08002D3C` constructor output, captured during reset. Constructor entry argument is `$2000587C`, task entry `$08002FDF` (Thumb address), restored PC `$08002FDE`. That code and the subsequent executed trace identify the **bootloader Main** entry, distinct from application Main `$0801D4B0`; task identity is not based on the name alone. This switch is IDLE→Main, not IDLE→Storage.

**STRONG INFERENCE:** the observed ready-list traversal implements round-robin selection among the four priority0 tasks. The exact first choice above is PROVEN; later scheduling order is UNKNOWN beyond this bounded run.

## Native incoming restore and exception return

**PROVEN:** scheduler returns to `$08003162`. Native `$08003166` clears BASEPRI; `$0800316A` restores MSP scratch; `$0800316C–$0800316E` load the new TCB and its saved context. `$08003170 LDM r0!,{r4-r11,lr}` restores all eight callee-saved registers as `$A5A5A5A5` and LR=`$FFFFFFFD` from the actual constructor frame. FP restore `$0800317A` is not executed. **Native** `$0800317E MSR PSP,r0` installs `$20006460` before return; the host does not replace that instruction.

**PROVEN within the architectural model:** `$08003186 BX LR` triggers basic PSP exception return. `Model.leave_pendsv` validates the actual native frame and consumes it exactly once:

| Restored field | Value |
|---|---|
| hardware-frame source | `$20006460–$2000647F` |
| EXC_RETURN | `$FFFFFFFD` |
| r0 | `$2000587C` |
| r1-r3 / r12 | each `$A5A5A5A5` |
| r4-r11 | each `$A5A5A5A5`, loaded by native handler |
| LR / PC / xPSR | `$08002D65 / $08002FDE / $01000000` |
| PSP / MSP | `$20006480 / $2004FFE0` |
| CONTROL / IPSR | `$2 / $0`: privileged PSP Thread |
| PRIMASK / BASEPRI / FAULTMASK | `$0 / $0 / $0` |
| ICSR / SHCSR | `$00000800 / $00070000`: no PendSV pending/active |

**PROVEN:** no per-task CONTROL, BASEPRI or PRIMASK value is stored/restored by this native software frame. Masking is managed by the handler instructions; Thread stack selection/privilege are architectural return semantics. The native path saves r4-r11 plus EXC_RETURN, while hardware saves r0-r3/r12/lr/pc/xPSR. No FP context is touched in this path. Extended/lazy FP and unprivileged variants remain UNKNOWN and fail closed in the model.

## RAM access and observer qualification

**PROVEN:** all64 handler/scheduler instruction-boundary observations, including the intercepted BX, are recorded. Memory operands and bulk push/pop/LDM/STM ranges are decoded from actual native instructions and sampled through host reads. No RAM read/write hooks are installed. Per-instruction xPSR sampling is deliberately avoided in IT blocks.

**PROVEN:** each native instruction is followed by a full-SRAM comparison. In addition, all seven decoded native store intents are checked even when they write the value already present. Allowed writes are restricted to:

| Half-open range | Ownership in this switch |
|---|---|
| `$20007E5C,$20007EA0)` | IDLE software save plus architectural hardware frame |
| `[$2004FFC8,$2004FFE0)` | handler and scheduler MSP scratch24bytes |
| `[$20007EB8,$20007EBC)` | IDLE TCB saved-context field |
| `[$2000527C,$20005280)` | scheduler yield-pending field |
| `[$20005268,$2000526C)` | current-TCB pointer |
| `[$20005208,$2000520C)` | selected priority0 ready-list index |

**PROVEN:** ready-list ownership is derived independently from the captured bitmap and the native20-byte stride, not accepted from an arbitrary observed write address. Thirteen changed-word write events occur; no write intent or observed SRAM modification falls outside the declared ranges. The outgoing hardware frame, incoming constructor frame and old SVC MSP frame remain intact. Handler/scheduler scratch writes are not presented as newly available memory.

**PROVEN:** a separate stock control removes the detailed register/memory-difference observer while executing the same native handler/scheduler. [stock-minimal-observer.json (local-only reference: `builds/phase36-pendsv-context/stock-minimal-observer.json`; not distributed) matches detailed stock on complete SRAM, captured state, incoming context, pre-return/restored registers and post-return trace. This checks the new observer against the prior RAM-hook failure mode.

## Regressions and bounded progression

**PROVEN:** regressions.json (local-only reference: `builds/phase36-pendsv-context/regressions.json`; not distributed) contains32 passing checks. Native evidence asserts A/B/C/D/H: exact captured first PendSV, outgoing PSP/register save, incoming PSP/register restore and pending consumption. Separate architectural fixtures test G aligned/padded PSP entry/return, unchanged Thread CPU state on a round trip, single consumption, E malformed next-context bounds/alignment/PC/Thumb, F invalid or unsupported EXC_RETURN, and rejection of masked/nested/FP/competing-pending cases without CPU/SRAM/system-register mutation. Fixture mutations never enter the authentic boot controls.

**UNKNOWN — I, second PendSV:** exactly one native switch occurs before the next due post-scheduler SysTick boundary. No second PendSV is fabricated or skipped; later behavior is unexecuted. This qualification is limited to the first observed switch.

**PROVEN:** diagnostic.json (local-only reference: `builds/phase36-pendsv-context/diagnostic.json`; not distributed) and stock have identical entire PendSV records, scheduler selection, constructor frames, exception return and full SRAM at the final checkpoint: SHA-256 `d43fb528fee5661d5e520c69cc2dc480587a5e0437f46ce0ed86fc306ee4e0b5`. Each run retains its unchanged code hash. Both execute Main beyond `$08002FDE`; the first96 post-return instruction snapshots are retained.

**PROVEN within the inherited ideal cadence:** both stop at PC `$08006EF2` before delivering the first due **post-scheduler SysTick**. The prefix's native-instruction observation count is75,689, not a hardware cycle/time measurement. `$08006EF2` is an ordinary ring-buffer store in Main's startup work, not an SDMMC wait or a newly established firmware fault. The stop is the new required RTOS exception-service boundary under the existing2000-instruction tick premise. The old pre-scheduler save/restore IRQ wrapper is intentionally not reused after task scheduling begins. No additional peripheral or timer service is implemented here.

**UNKNOWN:** actual time-to-interrupt, complete boot, later PendSV switches and stable USB/MIDI readiness. The separate application SDMMC wait `$0801C63C` remains exactly the prior phase34 evidence and was not rerun or investigated. It is not the next boundary reached by this bootloader control.

**UNKNOWN:** H1/H2/P2/P3 and complete-boot target counts remain open. Observed-prefix target counts are reads0 / writes0 / erase-overlap0 only. P1 retains its prior diagnostic-scope PROVEN status; P4 remains PROVEN for unchanged bootloader code. H4 remains FAIL for same-session recovery; host containment remains PASS.

**UNKNOWN — exactly one next smallest experiment:** qualify the first native **post-scheduler bootloader SysTick** at the captured `$08006EF2` boundary, including its scheduling effects and any resulting PendSV, using the real Main PSP context. Do not solve SDMMC or any later peripheral boundary as part of that prerequisite.

BOOTLOADER PENDSV / CONTEXT MODEL = PASS
