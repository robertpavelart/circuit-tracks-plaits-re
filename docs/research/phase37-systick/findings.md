> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase37 — native post-scheduler bootloader SysTick

**PROVEN:** official stock first, then the existing diagnostic control execute the native SysTick path from the exact phase36 checkpoint. The native tick returns normally; two later Thread-generated PendSV requests switch Main→UI→Storage. Execution stops at Storage's first unsupported array-data QSPI read. No firmware image, hardware access, reference/pinned edit, application SDMMC work or additional NOR response model is introduced.

**PROVEN:** authoritative execution evidence is stock.json (local-only reference: `builds/phase37-systick/stock.json`; not distributed), diagnostic.json (local-only reference: `builds/phase37-systick/diagnostic.json`; not distributed), regressions.json (local-only reference: `builds/phase37-systick/regressions.json`; not distributed), minimal observer control (local-only reference: `builds/phase37-systick/stock-minimal-observer.json`; not distributed) and the four clean subprocess exits in `run-log.json`. Early exploratory comparator output is not admission evidence: a cross-Uc context restore produced a native heap error and was removed. The corrected comparison CPU receives explicit architectural register copies; context save/restore is confined to its own Uc owner. All final controls exit0.

## Configuration and timing boundary

**PROVEN:** native configuration `$08002EE8–$08002F08` disables CTRL, clears VAL, reads the core-clock variable at `$200004B4`, computes the reload with `UMULL`/shift/subtract, writes LOAD, then writes CTRL=7. `SysTick_configuration` records intermediate registers: represented core clock120,000,000, intermediate quotient120,000, final reload119,999=`$1D4BF`. 08002ee8.asm (local-only reference: `builds/phase37-systick/08002ee8.asm`; not distributed) and `clock_MMIO` identify the actual native writes.

**PROVEN:** earlier helper `$08001C44` also configures SysTick, writes priority byte `$F0` at `$E000ED23`, clears VAL and enables CTRL=7; see 08001c30.asm (local-only reference: `builds/phase37-systick/08001c30.asm`; not distributed). Native scheduler setup leaves SHPR3=`$F0F00000`, so SysTick and PendSV are both priority `$F0`, PRIGROUP=3. At the captured event PRIMASK/BASEPRI/FAULTMASK are0; observed native critical-section values PRIMASK=1 or BASEPRI=`$C0` block this priority. Mask fixtures prove pending is retained until unmask rather than consumed by an ineligible entry.

**PROVEN architectural interpretation:** CTRL=7 enables counting, interrupt request and processor-clock selection. Reload+1 is120,000 processor clocks. [Arm Cortex-M7 guide, SysTick and exception model](https://documentation-service.arm.com/static/61efd8352dd99944d05142d1) defines these fields and exception stacking. **STRONG INFERENCE:** the intended period is1ms/1kHz if the processor clock equals the represented120MHz. **UNKNOWN:** actual hardware timing/frequency. This experiment retains the earlier ideal event cadence of2000 observed instructions; it does not equate2000 instructions with1ms. VAL's flat backing value is0 and is not decremented. COUNTFLAG is set by the modeled timer event; no post-tick CPU CTRL read requiring read-to-clear is observed, and that unimplemented case fails closed.

## Exact entry fixture

**PROVEN:** `SysTick[0].captured` retains all CPU registers, PSP/MSP stack windows, TCB, scheduler/list/counter bytes, NVIC active/pending arrays, SysTick registers, VTOR/SHPR3/AIRCR and FPU control state. Its full SRAM hash equals phase36's final stock SRAM hash before any timer-event changes. Stock and diagnostic capture the same complete state.

| Pre-entry field | Value |
|---|---|
| PC / LR | `$08006EF2 / $08006F15` |
| MSP / PSP / SP | `$2004FFE0 / $200063C4 / $200063C4` |
| CONTROL / IPSR / xPSR | `$2 / $0 / $01000000` |
| PRIMASK / BASEPRI / FAULTMASK | `$0 / $0 / $0` |
| current task / TCB | bootloader Main / `$20006488` |
| r0 / r1 / r2 / r3 | `$20007A60 / $16 / $49 / $15` |
| r4 / r5 / r6 / r7 | `$33 / $49 / $48 / $15` |
| r8 / r9 / r10 / r11 / r12 | `$0 / $0 / $0 / $0 / $A5A5A5A5` |
| CTRL / LOAD / VAL backing | `$7 / $1D4BF / $0` |
| ICSR before event / SHCSR | `$00000800 / $00070000` |
| clock `$20000008` / increment byte `$20000004` | 7 /1 |
| handler counter `$20005518` / kernel counter `$200053C0` | 0 /0 |

**PROVEN within the architectural model:** the ideal timer event sets PENDSTSET and COUNTFLAG, not software tick counters or scheduler flags. ICSR becomes `$04000800`. Eligible entry resolves VTOR `$08000000` slot `$0800003C → $08009331`, executable entry `$08009330`. Pending is consumed, IPSR=15, ICSR=`$0000080F`, SHCSR=`$00070800`, LR=`$FFFFFFFD`, Handler CONTROL.SPSEL=0 and MSP remains `$2004FFE0`.

**PROVEN:** this actual incoming PSP is4 modulo8. Entry aligns the hardware frame to `$200063A0–$200063BF`, leaves the pad word `$200063C0–$200063C3` untouched, and records stacked xPSR bit9. The frame is:

| Offset | Word |
|---|---|
| +00 r0 | `$20007A60` |
| +04 r1 | `$00000016` |
| +08 r2 | `$00000049` |
| +0C r3 | `$00000015` |
| +10 r12 | `$A5A5A5A5` |
| +14 LR | `$08006F15` |
| +18 PC | `$08006EF2` |
| +1C xPSR | `$01000200` |

The asynchronous return PC is unchanged; no instruction at the old boundary is skipped. [systick.py](<../../../builds/phase37-systick/systick.py>) `TickModel.enter_tick` implements the entry. Unsupported nested/FP/external arbitration and simultaneous pending exceptions fail closed.

## Real handler and return

**PROVEN:** 08009330.asm (local-only reference: `builds/phase37-systick/08009330.asm`; not distributed) / 0800935c.asm (local-only reference: `builds/phase37-systick/0800935c.asm`; not distributed) and `native_trace` show13 instruction boundaries including the return:

- `$08009330 PUSH {r7,lr}` writes Main's r7=`$15` and architectural EXC_RETURN=`$FFFFFFFD` to MSP `$2004FFD8–$2004FFDF`.
- `$08009332 BL $0800935C` executes the actual clock helper. `$08009364 STR` writes `$20000008`: 7→8, adding the native increment byte1.
- `$08009336–$0800933C` natively increment `$20005518`: 0→1.
- `$0800933E POP {r0,pc}` is the actual exception-return instruction. Its ordinary two-word MSP loads/advance and the resulting EXC_RETURN unstack are modeled together in `TickModel.leave_tick`. The temporary r0 from the POP is overwritten by the architectural hardware-frame restore, as required.

**PROVEN:** no generic RTOS tick routine, synthetic counter increment or scheduler-success flag replaces these instructions. Native SysTick does not call kernel tick routine `$08002920`, change scheduler bytes/lists/kernel counter, change current task, or request PendSV in this prefix. The four changed native SRAM words are the two MSP scratch words and the two counter words. Per-instruction full-SRAM differences remain inside exactly those ranges; the handler hardware frame stays intact. No RAM memory-access hooks are used.

**PROVEN:** `$FFFFFFFD` restores the actual hardware frame once, including the alignment pad adjustment. Final PC=`$08006EF2`, PSP/SP=`$200063C4`, MSP=`$2004FFE0`, CONTROL=2, IPSR=0, xPSR=`$01000000`; every r0-r12 and LR matches the captured pre-entry value. Pending/active SysTick clear to ICSR=`$800`, SHCSR=`$70000`. Native software increments are the only lasting application-state changes. The returned Main instruction then executes naturally.

## Old ideal service versus native exception service

**PROVEN:** `legacy_ideal_wrapper` executes the old native-handler wrapper on a comparison-only CPU cloned from the exact pre-tick architectural/SRAM state. It supplies nothing to the authoritative cold boot. `legacy_comparison` proves identical live registers, current TCB, scheduler bytes/lists, kernel counter and both software counter results after the tick.

**PROVEN:** full SRAM differs in exactly10 words. The first difference is `$200063A0`: old wrapper retains `$A5A5A5A5`; native entry stores r0=`$20007A60`. The old wrapper placed its frame at unaligned `$200063A4`, omitting the four-byte pad and stacked alignment marker. Nine differing PSP words cover `$200063A0–$200063C0`. The tenth difference is MSP `$2004FFDC`: old sentinel `$0807FF01` versus architectural `$FFFFFFFD`. See `legacy_RAM_differences` for every old/new word. Native entry/return is authoritative; identical scheduler observables do not make the old stack mechanics correct. The old wrapper remains only in the unchanged pre-scheduler prefix, an explicit limit on complete-reset qualification.

## Natural later switches and next boundary

**PROVEN:** SysTick requests no PendSV, so no SysTick→PendSV tail chain is required or fabricated. Later native Thread helper 08004714.asm (local-only reference: `builds/phase37-systick/08004714.asm`; not distributed) tests byte `$20005522` and writes PENDSVSET at `$08004720`. Both later switches originate at that native instruction, not the tick handler. The unchanged qualified phase36 PendSV implementation executes all three observed switches:

| Switch | Native pending boundary | Incoming TCB | Resumed PC | Restored PSP |
|---|---|---|---|---|
| IDLE→Main | `$08002A6E` | `$20006488` | `$08002FDE` | `$20006480` |
| Main→UI | `$08004722` | `$20006E08` | `$08003048` | `$20006E00` |
| UI→Storage | `$08004722` | `$20007470` | `$08009202` | `$20007468` |

**PROVEN:** each incoming frame matches its real native constructor output, each outgoing save and incoming r4-r11/PSP restore passes, each hardware frame is consumed once, and native writes stay in the qualified per-switch ranges. Task identity is supported by TCB/name, constructor entry/argument and executed PC, not name alone. All returns use `$FFFFFFFD` to privileged PSP Thread mode. No later task state is supplied by a host scheduler.

**PROVEN:** Storage issues opcode `$EC`, address `$00081000`, DLR=22 (23bytes), CCR=`$07183FEC`, from native `$080051C0`. The runner stops at `$080051C2` requiring authentic NOR data/completion; no array bytes or storage-success state are invented. It does not model or solve that read. Bootloader has not completed or handed off to application startup. The independent application SDMMC boundary `$0801C63C` remains untouched.

**PROVEN:** only one post-scheduler tick becomes due before this boundary. The next ideal tick would be at observation count77,689; the run stops at77,359. A second tick and a tick-produced PendSV are not fabricated. Native/tail-chained behavior for those unobserved cases is UNKNOWN.

## Controls, regression scope and preservation gates

**PROVEN:** stock and diagnostic have identical complete SysTick and PendSV records, captured/pre-return/restored states, scheduler/counter results and final full SRAM SHA-256 `80bf97caae16ca3b2b031dc22e794a6a9b3f1a3e0c0404e8bfc98e591dd70287`. Their respective code hashes remain unchanged. The minimal-observer stock control matches detailed execution on full SRAM, exception boundaries, task choices and final CPU state, checking for observer-induced behavior.

**PROVEN:**24 checks in `regressions.json` cover native captured A/B/E, real padded entry plus aligned/padded native-handler fixtures F, observed critical-section masking D with retained pending until unmask, malformed/unimplemented returns G and double-unstack rejection. Cases C (tick-generated switch) and H (second naturally due tick) are explicitly UNKNOWN beyond this prefix. No regression is silently skipped or converted to a fabricated successful event.

**PROVEN observed-prefix target counts for `$82000–$821FF`:** reads0, writes0, erase overlaps0. The newly issued `$81000–$81016` request is outside the target and remains incomplete. No new program/erase command occurs. **UNKNOWN full-boot counts:** reads/writes/erase overlaps UNKNOWN; this prefix cannot qualify later storage behavior.

**UNKNOWN:** complete boot/H1/H2/P2/P3 remain open. P1 remains PROVEN within its prior diagnostic-only scope; P4 remains PROVEN unchanged bootloader code. Host containment remains PASS; H4 remains FAIL for same-session device recovery. Timing, unmodeled IRQ sources, pre-scheduler exception architecture and later storage are not silently upgraded by this result.

**UNKNOWN — exactly one next smallest experiment:** qualify the native bootloader Storage `$EC` read of23bytes at `$81000–$81016`, using provenance-checked existing NOR data and authentic native completion behavior; stop at the next unsupported boundary. Establish the source of those bytes before replaying them. Do not substitute application firmware bytes, zeros or invented metadata, and do not investigate SDMMC as part of that experiment.

BOOTLOADER SYSTICK MODEL = PASS
