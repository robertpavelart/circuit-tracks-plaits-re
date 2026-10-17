"""Append phase35 result without rewriting or re-running earlier evidence."""
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[1]
section='''

## Phase35 — native bootloader SVC and PSP restoration qualified

**PROVEN within the observed privileged basic-frame path:** stock first, then diagnostic execute the same native scheduler-start SVC `$080031C2`. Before entry: MSP=`$20050000`, PSP=0, CONTROL=0, LR=`$08002E2B`, PRIMASK/FAULTMASK=0, BASEPRI=`$C0`, xPSR=`$61000000`. SVC priority0 is unmasked. VTOR `$08000000`, vector `$0800002C → $08003189`. Architectural entry stacks eight words at MSP `$2004FFE0`, LR=`$FFFFFFF9`, IPSR=11; the actual handler executes unchanged.

**PROVEN:** native frame constructor `$08002D3C` creates the first task context; no host task frame is injected. Current-TCB global `$20005268` points to IDLE TCB `$20007EB8`, whose saved context is `$20007E6C`. Native `$0800318E` loads r4-r11/LR, and native `$08003192` restores PSP=`$20007E90`. BX LR uses the task's `$FFFFFFFD`; architectural unstack consumes the native frame once, restoring PC=`$08002A58`, PSP/SP=`$20007EB0`, CONTROL=2, privileged Thread mode. Original MSP SVC frame remains at `$2004FFE0`, as required when starting another context. No handler RAM writes or saved-frame corruption occur.

**PROVEN:** stock/diagnostic SVC records and complete SRAM match. Eight native idle instructions run with PSP, then request PendSV via ICSR. Both stop at `$08002A6E`, before executing further with unsupported pending service. This is a post-SVC task checkpoint, not stable USB/MIDI readiness. Twenty-two architectural fixtures pass, including PSP/MSP selection, padded/aligned frames, invalid EXC_RETURN/PC/Thumb/RAM rejection and single consumption. Unsupported nesting, FP return and unprivileged fixtures fail closed. **UNKNOWN:** full NVIC/PendSV and unprivileged/FP behavior; the inherited earlier IRQ/timing/NOR assumptions remain conditional. M7 STKALIGN=1 is explicitly modeled despite the flat CCR backing register.

**UNKNOWN:** H1/H2/P2/P3 and full-boot target counts. Observed-prefix target counts are0 reads/0 writes/0 erase overlaps only. P1 remains PROVEN in its prior diagnostic scope; P4 remains PROVEN for unchanged code. Host containment remains PASS; H4 remains FAIL in-session. Application SDMMC wait `$0801C63C` remains the separate, untouched phase34 boundary. No firmware generation, hardware access, reference/pinned edits or Plaits work occurred.

**UNKNOWN — exactly one next smallest experiment:** qualify native bootloader PendSV `$0800312C` from the real idle-generated pending state `$08002A6E`, including native task save/scheduler/restore and architectural return. It is not implemented here. See [phase35 findings](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase35-svc-context/findings.md>), [native stock trace](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase35-svc-context/stock.json>), [diagnostic trace](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase35-svc-context/diagnostic.json>) and [validation](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase35-svc-context/validation.json>).

BOOTLOADER SVC / PSP MODEL = PASS
'''
if __name__=='__main__':
 for label,name in (('preservation','qspi82000-preservation-powercycle.md'),('readiness','qspi82000-hardware-readiness.md')):
  before=(O/f'phase34-{label}-before.md').read_bytes();p=R/'notes'/name
  expected=before+section.encode('utf8')
  assert p.read_bytes() in (before,expected),'notes changed outside this append'
  p.write_bytes(expected)
 print('Both notes retain exact phase34 bytes, followed by phase35 result')
