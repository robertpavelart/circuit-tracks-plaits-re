"""Append phase36 findings to exact archived notes, preserving earlier work."""
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[1]
SECTION='''

## Phase36 — first native PendSV context switch qualified

**PROVEN:** stock first, then diagnostic replay exactly the phase35 pending CPU/SRAM state at `$08002A6E`. Pre-entry MSP=`$2004FFE0`, PSP=`$20007EA0`, CONTROL=2, xPSR=`$21000000`, PRIMASK/BASEPRI/FAULTMASK=0, LR=`$08002D65`; native IDLE has set PendSV pending. VTOR vector `$08000038 → $0800312D` selects native entry `$0800312C`. Architectural entry stacks the actual Thread context on PSP `$20007E80`, consumes pending, enters Handler mode on MSP and installs EXC_RETURN `$FFFFFFFD`.

**PROVEN:** native `$08003142` saves r4-r11/LR at `$20007E5C`; `$08003146` writes that context pointer to IDLE TCB `$20007EB8`. Native scheduler `$080029D8` uses ready bitmap1 and priority0 list `$20005204` (count4), moves list index `$20005208` to node `$2000648C`, and selects owner TCB `$20006488`. Its native constructor frame at `$2000643C` belongs to bootloader Main by both recorded entry `$08002FDF` and name. No generic scheduler, task-ready flag or host-created task frame is substituted.

**PROVEN:** native handler restores r4-r11 and EXC_RETURN, then native `$0800317E` writes PSP=`$20006460`. Architectural BX/return consumes the hardware frame once, restoring PC=`$08002FDE`, PSP=`$20006480`, CONTROL=2, privileged Thread mode; MSP remains `$2004FFE0`. All seven native store intents, including unchanged-value stores, and per-instruction full-SRAM differences remain within the declared outgoing stack/MSP scratch/TCB/scheduler ranges. No unrelated RAM modification occurs in the switch. No FP save/restore instruction executes in the observed basic-frame path.

**PROVEN:** stock/diagnostic entire PendSV records and complete SRAM agree;32 new native-evidence/architectural-fixture checks pass. A minimal-observer stock control matches the detailed trace, avoiding the prior RAM-hook artifact. Malformed context/EXC_RETURN, alignment, pending consumption and single unstack are tested separately from native boot. **UNKNOWN:** a second PendSV does not occur before the first due post-scheduler tick; nested/FP/unprivileged and later scheduling remain unqualified.

**PROVEN within the inherited ideal2000-instruction cadence:** both execute Main and stop at `$08006EF2`, before delivering the first post-scheduler SysTick. This is an RTOS service boundary during ordinary ring-buffer work, not an SDMMC wait or a firmware-fault conclusion. The earlier pre-scheduler IRQ wrapper is not used for the scheduled context. **UNKNOWN:** real interrupt timing, full boot and stable USB/MIDI state. Application SDMMC `$0801C63C` remains the separate unchanged prior boundary and was not investigated.

**UNKNOWN:** H1/H2/P2/P3 and full-boot target counts. Observed-prefix target counts remain0 reads/0 writes/0 erase overlaps only. P1 remains PROVEN within prior diagnostic scope; P4 remains PROVEN unchanged boot code. H4 remains FAIL in-session; host containment remains PASS. No firmware generation, hardware access, reference/pinned edit or Plaits work occurred.

**UNKNOWN — exactly one next smallest experiment:** qualify native post-scheduler bootloader SysTick from the captured Main-context boundary `$08006EF2`, including any naturally requested PendSV; stop at the next unsupported boundary. See [phase36 findings](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase36-pendsv-context/findings.md>), [stock](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase36-pendsv-context/stock.json>), [diagnostic](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase36-pendsv-context/diagnostic.json>) and [validation](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase36-pendsv-context/validation.json>).

BOOTLOADER PENDSV / CONTEXT MODEL = PASS
'''
if __name__=='__main__':
 for label,name in (('preservation','qspi82000-preservation-powercycle.md'),('readiness','qspi82000-hardware-readiness.md')):
  before=(O/f'phase35-{label}-before.md').read_bytes();note=R/'notes'/name;after=before+SECTION.encode('utf8')
  assert note.read_bytes() in (before,after),'unexpected independent note change'
  note.write_bytes(after)
 print('Both phase35 note archives retained byte-exact before phase36 append')
