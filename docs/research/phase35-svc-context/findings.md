> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase35 — native bootloader SVC / PSP qualification

**PROVEN:** unchanged stock passes first, then the existing memory-only diagnostic control passes identically. Scope is the observed privileged, basic-frame first-task SVC, not a general NVIC/RTOS implementation. No firmware file is generated, hardware accessed, pinned/reference input edited, or SDMMC behavior added. Phase26–34 evidence is preserved.

## Exact cause and entry

**PROVEN:** native scheduler startup calls `$080031A4` from `BL` at `$08002E26`. It reloads the vector MSP, executes `MSR CONTROL,0`, enables IRQ/fault exceptions, executes DSB/ISB, then reaches bytes `00 DF` (`SVC #0`) at `$080031C2`. This is synchronous SVC used to start the RTOS first task; it is neither PendSV nor an exception return at that instruction. See disassembly (local-only reference: `builds/phase35-svc-context/08003188.asm`; not distributed), `scheduler_start_trace`, and `call_chain` in stock.json (local-only reference: `builds/phase35-svc-context/stock.json`; not distributed).

| Pre-SVC field | Value in both native controls |
|---|---|
| CONTROL | `$00000000`: privileged Thread, MSP, no active FP frame |
| PRIMASK / BASEPRI / FAULTMASK | `$0 / $C0 / $0` |
| MSP / PSP | `$20050000 / $00000000` |
| LR | `$08002E2B`, ordinary caller return address |
| xPSR / IPSR | `$61000000 / $0` |
| VTOR | `$08000000` |
| SVC vector slot / value | `$0800002C / $08003189` |
| SVC priority byte | `$00`, not masked by BASEPRI `$C0` |
| ICSR / SHCSR before entry | `$00000000 / $00070000` in this mapped-system fixture |

**PROVEN within the architectural model:** entry selects MSP and writes the hardware frame at `$2004FFE0`. Initial LR becomes EXC_RETURN `$FFFFFFF9`. Handler mode uses MSP, IPSR=11, CONTROL.SPSEL=0. Vector execution starts at `$08003188` with Thumb state. The frame's return PC is `$080031C4`, as required for the two-byte SVC; it is not a manually selected task PC. `pre_stack_window` preserves the original 128 stack bytes before stacking.

| Hardware frame offset | Word |
|---|---|
| +00 r0 | `$00000000` |
| +04 r1 | `$C0000000` |
| +08 r2 | `$00F00000` |
| +0C r3 | `$200004B4` |
| +10 r12 | `$20007474` |
| +14 lr | `$08002E2B` |
| +18 pc | `$080031C4` |
| +1C xPSR | `$61000000` |

**PROVEN:** no alignment pad is needed in this actual entry. Fixture alignment cases also verify a four-byte pad and stacked xPSR bit9 when incoming SP is 4 modulo8. M7's fixed STKALIGN=1 is implemented explicitly; `CCR_backing_register=0` records the inherited flat-MMIO reset limitation instead of falsely claiming it is the silicon CCR value.

**PROVEN architectural basis:** exception entry saves eight core words; Handler mode uses MSP; basic EXC_RETURN selects the return stack; M7 aligns exception frames to eight bytes. The model follows [Arm DUI0646C, §§2.1.3 and 2.3–2.4](https://documentation-service.arm.com/static/61efd8352dd99944d05142d1). It models VECTACTIVE and SVCALLACT transitions for this SVC; a complete NVIC, priority arbitration and tail chaining remain outside its scope.

## Native frame provenance and handler execution

**PROVEN:** all four task contexts are constructed by real boot code `$08002D3C–$08002D60`, called at `$0800270E`. It writes task PC, r0 argument, xPSR `$01000000`, task-return trap LR `$08002D65`, and software EXC_RETURN `$FFFFFFFD`. Task-stack fill is native `$0800266E–$08002676 → $08002D00` with `$A5`; the A5 register words in the saved context are expected fill, not injected host task state. `$08002716` stores the returned context pointer into `[TCB]`. See task creation (local-only reference: `builds/phase35-svc-context/0800263e.asm`; not distributed), frame constructor (local-only reference: `builds/phase35-svc-context/08002d3c.asm`; not distributed), and `task_frame_initializers` / `TCB_store_trace` in stock.json.

**PROVEN:** current-TCB global `$20005268` (scheduler base `$20005204 + $64`) points to TCB `$20007EB8`, name `IDLE` at TCB+$34. Its first word is saved context `$20007E6C`. The complete 68-byte context matches exactly the bytes observed immediately after its native constructor returned; this assertion is required by the replay. No task frame or scheduler-success flag is supplied by the host.

| Native SVC handler instruction | Observed operation |
|---|---|
| `$08003188 LDR r3,[PC,#$48]` | ROM literal `$080031D4 → $20005268` |
| `$0800318A LDR r1,[r3]` | current TCB `$20007EB8` |
| `$0800318C LDR r0,[r1]` | saved context `$20007E6C` |
| `$0800318E LDM r0!,{r4-r11,lr}` | reads36bytes; restores eight software registers and LR=`$FFFFFFFD`; r0 becomes `$20007E90` |
| `$08003192 MSR PSP,r0` | **native instruction** restores PSP=`$20007E90` |
| `$08003196 ISB` | executes unchanged |
| `$0800319A MOV r0,0` / `$0800319E MSR BASEPRI,r0` | clears mask natively |
| `$080031A2 BX lr` | architectural exception return using native LR `$FFFFFFFD` |

**PROVEN:** every instruction up to BX runs natively. BX is recognized at its actual instruction boundary and serviced as architectural exception return. `handler_trace` records every native instruction/register snapshot and exact native-load ranges/bytes, without RAM memory-access hooks. Full SRAM hash is unchanged across the handler, including the TCB, constructor-generated task frame and SVC entry frame: the handler performs no RAM stores in this path. CONTROL remains0 in the handler. No host PSP assignment replaces the native MSR PSP.

## Exact return and first checkpoint

**PROVEN within the architectural model:** `$FFFFFFFD` selects basic unstack from PSP `$20007E90`, using the native task frame, exactly once. Return restores r0=0; r1-r3/r12=`$A5A5A5A5`; lr=`$08002D65`; pc=`$08002A58`; xPSR=`$01000000`. Final PSP/SP=`$20007EB0`, MSP=`$2004FFE0`, CONTROL=2, IPSR=0, BASEPRI=0. The initial MSP SVC frame remains present: scheduler startup intentionally returns into a different frame. It would be incorrect to unstack both frames or restore the original MSP to `$20050000` here.

**PROVEN:** alignment, physical SRAM bounds, restored PC within mapped executable internal flash, Thumb state, Thread IPSR, saved-register values, unchanged frame bytes and single consumption are asserted. The resumed task entry is exactly its native constructor's entry `$08002A59` with the Thumb address bit removed. Host register writes are limited to exception entry/return semantics. The original SVC+2 PC is not used as an arbitrary skip.

**PROVEN:** eight native idle-task instructions execute after return, from `$08002A58` through `$08002A6C`. The idle prologue uses PSP (to `$20007EA0`), reads ready-task count4 at `$20005204`, then writes `$10000000` to ICSR `$E000ED04`, requesting PendSV. Replay stops at the next instruction boundary `$08002A6E`, before executing more code with an unsupported pending exception. `pending_checkpoint` records this state. This is a bounded post-SVC task checkpoint, **not** stable USB/MIDI-ready boot.

**PROVEN:** official stock and diagnostic have identical complete SVC evidence, constructor frames, handler trace, resumed registers, pending checkpoint and full SRAM SHA-256 `2cbbec54dba7cfb0a321ee9fe387c8f0d60170e6058db4366c19adff5667e56b`. Both retain their own unchanged code hashes. The reset runner counts74,751 instruction-hook observations, including the intercepted BX boundary; this is not a hardware cycle measurement.

## Regressions and limits

**PROVEN:** regressions.json (local-only reference: `builds/phase35-svc-context/regressions.json`; not distributed) contains22 passing architectural-fixture checks. They are separate from the two actual native cold-start controls.

| Required case | Evidence / boundary |
|---|---|
| A native bootloader SVC | PROVEN: stock first, diagnostic second, identical constructor-owned context |
| B PSP-selected Thread | PROVEN: privileged architectural entry/unstack fixtures, aligned and padded; native task resumes and runs with PSP |
| C MSP-selected Handler | PROVEN: actual native SVC handler runs on MSP; F9 MSP return separately roundtripped in fixture |
| D nested/pending | PROVEN: native idle requests PendSV; model stops before service. Unsupported nested entry / tail chain rejected without CPU/SRAM mutation. Actual nested scheduling is UNKNOWN |
| E malformed EXC_RETURN | PROVEN: reserved/malformed values, unimplemented Handler/FP return, invalid RAM/alignment, Thumb/PC/IPSR failures rejected; double unstack rejected |
| F stack alignment | PROVEN: four MSP/PSP × aligned/padded privileged roundtrips restore SP, all core registers, xPSR and CONTROL |

**UNKNOWN:** unprivileged-thread support. An exploratory fixture exposed Unicorn's special-register API masking MSP/PSP/mask reads while unprivileged; the model explicitly rejects that unsupported case rather than pretending to qualify it. Both real controls enter and return privileged. Extended/lazy FP frames, nested preemption, arbitrary vectors, tail chaining and PendSV scheduler service are not qualified. No extra scheduler implementation was added.

**STRONG INFERENCE:** this native frame/TCB sequence is the usual first-task restore design of a Cortex-M RTOS port. The architectural interpretation is supported by observed loads, native PSP write and constructor-origin EXC_RETURN, not merely function naming.

**UNKNOWN:** full first boot, installation/target preservation and complete reset ownership. H1/H2/P2/P3 stay UNKNOWN. P1 retains its prior diagnostic-only PROVEN scope; P4 remains PROVEN for unchanged bootloader bytes. Host containment remains PASS; H4 remains FAIL for same-session device recovery. Target observed-prefix counts remain read0/write0/erase-overlap0; full-boot counts are UNKNOWN.

**UNKNOWN — next boundaries:** bootloader now requires pending PendSV service, vector `$08000038 → $0800312D`. The separate application SDMMC wait `$0801C63C` is unchanged from phase34 and was neither rerun nor investigated. These are distinct reset paths; qualifying SVC does not close either one.

**UNKNOWN — exactly one next smallest experiment:** qualify native bootloader PendSV entry/save/scheduler/restore/return beginning with the idle-generated pending state at `$08002A6E`, using the real task frames and stopping at the next unsupported boundary. Do not implement it as part of phase35.

BOOTLOADER SVC / PSP MODEL = PASS
