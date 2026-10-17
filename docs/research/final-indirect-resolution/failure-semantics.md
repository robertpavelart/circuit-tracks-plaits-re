> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Allocator exhaustion control flow

**PROVEN:** isolated native execution of the frozen candidate allocator, with cap `20044D70`, cursor `20044D68`, admits one 8-byte request and advances cursor to the cap. A 12-byte request reaches `0801D7F4` with cursor unchanged. `allocator_failure.py` stops before that BKPT instruction; it does not emulate exception routing or touch a peripheral.

**PROVEN exact control flow:**

1. `0801D7D8..0801D7EA` reads cap/cursor from `20002B44/20002B48` and rounds size to four bytes.
2. `0801D7EC` calculates proposed end; `0801D7F0/0801D7F2` compares and branches on admission.
3. Rejection reaches `0801D7F4: BKPT #1`. Cursor publication at `0801D7F8` is bypassed.
4. If execution resumes after BKPT, `0801D7F6` branches to `0801D800`, which sets R0=`FFFFFFFF`, then `0801D804` returns.
5. Generic wrapper `0801CFA4` receives that value through `0801CFAE`; `0801CFB2 CBNZ` takes the nonzero return at `0801CFBC`. The hook through `[20006A38]` is only considered for zero; it cannot repair this exhaustion result.

`allocator-failure.json` preserves four isolated cases: bounded allocator size8; size12 stop at rejection; size12 with explicitly counterfactual post-BKPT continuation; generic wrapper size12 with the same continuation. The last two return `FFFFFFFF`. This is verification of the failure branch ABI, not a claim that the physical processor resumes a breakpoint automatically.

| Question | Evidence result |
|---|---|
| Is BKPT on the rejection branch? | PROVEN: yes; isolated native execution reaches its PC |
| Does HardFault occur on the user's unit? | UNKNOWN: no unit exception/debug configuration was accessed or modeled |
| What if this becomes a HardFault? | PROVEN by vector/handler bytes: vector at `0801000C` is `08059961`; handler `08059960` branches to itself. It does not return an allocation failure to the caller |
| What if execution continues after BKPT? | PROVEN for that explicitly imposed continuation: R0=`FFFFFFFF`, cursor unchanged |
| Does the generic wrapper reject `FFFFFFFF`? | PROVEN: no; it accepts nonzero |
| Do all callers safely handle failure? | UNKNOWN globally; the concrete constructor example at `0801CFDC` requests12 and tests only zero at `0801CFE0`, so it does not provide safe handling of this ABI |
| Is that constructor proven reachable after READY? | UNKNOWN; the isolated tests do not establish reachability |

There is no basis for labeling an unresolved >8-byte path SAFE-FAIL. Neither unconditional physical HardFault nor successful continued execution is inferred from the opcode name. There is no firmware modification. Even repeated individually small allocations would consume cumulative bump capacity; the eight-byte gap is not replenished per callback.
