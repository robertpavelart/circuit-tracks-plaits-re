"""Append phase37 result to archived phase36 notes without changing old text."""
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[1]
SECTION='''

## Phase37 — native post-scheduler bootloader SysTick qualified

**PROVEN:** native configuration computes LOAD=`$1D4BF` (119,999) from represented core clock120MHz and writes CTRL=7: processor-clock source, counter and interrupt enabled. SysTick/PendSV priority bytes are both `$F0`. **STRONG INFERENCE:** intended1ms cadence if the clock equals120MHz. **UNKNOWN:** real timing; the existing ideal2000-instruction event source is retained and VAL is not decremented.

**PROVEN:** stock first, diagnostic second reproduce the phase36 CPU/SRAM checkpoint at `$08006EF2`: Main TCB `$20006488`, MSP=`$2004FFE0`, PSP=`$200063C4`, CONTROL=2, masks0. SysTick vector `$0800003C → $08009331` selects actual handler `$08009330`. Architectural entry consumes pending, enters Handler mode on MSP, and stacks the padded hardware frame at PSP `$200063A0`, xPSR=`$01000200`, EXC_RETURN=`$FFFFFFFD`.

**PROVEN:** actual `$0800935C` clock helper updates `$20000008` 7→8 and the handler updates `$20005518` 0→1. Kernel counter `$200053C0`, scheduler lists/bytes and current TCB remain unchanged. SysTick requests no PendSV. Native POP/architectural return consumes the frame once, restores every Thread register, returns to `$08006EF2`, PSP=`$200063C4`, MSP=`$2004FFE0`, CONTROL=2 and xPSR=`$01000000`. No synthetic software tick increment or scheduler-success flag is used.

**PROVEN:** old ideal wrapper matches live registers and scheduler/counter results but differs in10 stack words: omitted4-byte alignment pad and sentinel LR instead of EXC_RETURN. The native exception path is authoritative. Twenty-four new native-evidence/architectural checks pass; masking retains pending until unmask. Stock/diagnostic and minimal-observer controls match full final SRAM and CPU/context boundaries. **UNKNOWN:** tick-produced PendSV/tail chaining and a second post-scheduler tick are unobserved before the next boundary; neither event is fabricated.

**PROVEN:** later Main and UI each request PendSV through native `$08004720`, independently of SysTick. The unchanged phase36 native model switches Main→UI (`$08003048`, PSP `$20006E00`) then UI→Storage (`$08009202`, PSP `$20007468`), using constructor-created frames and checked ownership ranges. Storage stops at `$080051C2` after issuing `$EC`, address `$81000`, DLR22: an unsupported23-byte array-data read. No data/metadata or completion success is supplied. Bootloader has not completed; application SDMMC `$0801C63C` remains untouched.

**PROVEN observed-prefix target counts `$82000–$821FF`:** reads0 / writes0 / erase overlaps0. The pending `$81000–$81016` read is outside the target. **UNKNOWN:** complete-boot counts and H1/H2/P2/P3. P1 remains PROVEN in its prior diagnostic scope; P4 remains PROVEN unchanged bootloader bytes. Host containment remains PASS; H4 remains FAIL in-session. No firmware generation, hardware access, pinned/reference edit or Plaits work occurred.

**UNKNOWN — exactly one next smallest experiment:** qualify native bootloader Storage's23-byte `$EC` read at `$81000–$81016` using provenance-checked existing NOR bytes and native completion; establish byte provenance before replaying data, then stop at the next unsupported boundary. See [phase37 findings](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase37-systick/findings.md>), [stock](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase37-systick/stock.json>), [diagnostic](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase37-systick/diagnostic.json>) and [validation](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase37-systick/validation.json>).

BOOTLOADER SYSTICK MODEL = PASS
'''
if __name__=='__main__':
 for label,name in (('preservation','qspi82000-preservation-powercycle.md'),('readiness','qspi82000-hardware-readiness.md')):
  before=(O/f'phase36-{label}-before.md').read_bytes();p=R/'notes'/name;after=before+SECTION.encode('utf8')
  assert p.read_bytes() in (before,after),'independent note edits would be overwritten'
  p.write_bytes(after)
 print('Both phase36 note archives retained byte-exact before phase37 append')
