"""Exact candidate terminal-store race and isolated fix, emulator only.

No candidate image is written. The fix is a 32-byte-or-smaller code fragment
placed in unused candidate pool RAM in the emulator, plus a local branch patch.
"""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase42-exact-rdiag-integration'))
from environment import *
O=Path(__file__).resolve().parent
from unicorn.arm_const import UC_ARM_REG_PRIMASK
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate/source/tools'))
from thumb import Asm,h,raw,movw,movt,ldrb_imm,cmp_imm,b_cond,movs_imm,strb_imm,b_w
STATE=0x20044d70;START=0x0806b9dc;END=0x0806b9ee;FIX=0x0806bc30
class Boundary(Exception):pass
def fixed_fragment():
 a=Asm(FIX)
 a.emit(raw,h(0xf3ef)+h(0x8210)) # MRS r2,PRIMASK
 a.emit(raw,h(0xb672)) # CPSID i
 a.emit(movw,0,STATE&65535);a.emit(movt,0,STATE>>16)
 a.emit(ldrb_imm,1,0,4);a.emit(cmp_imm,1,1);a.emit(b_cond,'restore','ne')
 a.emit(movs_imm,1,2);a.emit(strb_imm,1,0,4)
 a.label('restore');a.emit(raw,h(0xf382)+h(0x8810)) # MSR PRIMASK,r2
 a.emit(b_w,END)
 return a.assemble()[0]
def prepare(patched=False,primask=0):
 e=Physical();u=e.uc;e.call(0x0805dbcc)
 e.w32(STATE+8,0);e.w32(0x2000081c,5000);u.mem_write(STATE+4,b'\1')
 if patched:
  blob=fixed_fragment();assert len(blob)<=92
  assert bytes(u.mem_read(FIX,len(blob)))==b'\xff'*len(blob)
  u.mem_write(FIX,blob);u.mem_write(START,b_w(START,FIX))
 u.reg_write(UC_ARM_REG_PRIMASK,primask)
 return e
def irq(e):
 u=e.uc;s=u.context_save()
 u.reg_write(UC_ARM_REG_IPSR,15)
 e.call(0x0805998c,sp=0x2004ff00)
 value=e.r8(STATE+4);u.context_restore(s)
 return value
def execute_boundary(patched,site,primask=0):
 e=prepare(patched,primask);u=e.uc;seen=[]
 def pause(u,pc,n,d):
  if pc==site and not seen:
   seen.append(True);raise Boundary()
 hook=u.hook_add(UC_HOOK_CODE,pause)
 before=None;pending=False
 try:u.emu_start(START|1,END,count=100)
 except Boundary:
  before=e.r8(STATE+4)
  if u.reg_read(UC_ARM_REG_PRIMASK)==0:
   interrupt_state=irq(e)
  else:
   pending=True;interrupt_state=None
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,END,count=100)
 assert u.reg_read(UC_ARM_REG_PC)==END
 if pending and primask==0:interrupt_state=irq(e)
 return dict(site=hex(site),boundary_hit=bool(seen),state_before_irq=before,
  irq_deferred=pending,state_after_irq=interrupt_state,
  terminal_state=e.r8(STATE+4),final_PRIMASK=u.reg_read(UC_ARM_REG_PRIMASK))
def main():
 original=[execute_boundary(False,pc) for pc in (0x0806b9dc,0x0806b9e4,0x0806b9e6,0x0806b9e8,0x0806b9ea,0x0806b9ec)]
 assert any(x['state_after_irq']==3 and x['terminal_state']==2 for x in original)
 blob=fixed_fragment();ins=list(md.disasm(blob,FIX))
 # Before/after every emitted instruction, including masks/restoration.
 sites=[START]+[i.address for i in ins]
 fixed=[execute_boundary(True,pc) for pc in sites]
 assert all(not(x['state_after_irq']==3 and x['terminal_state']!=3) for x in fixed)
 assert all(x['final_PRIMASK']==0 for x in fixed)
 masked=[execute_boundary(True,pc,1) for pc in sites]
 assert all(x['final_PRIMASK']==1 for x in masked)
 # Quarantined state can never be promoted even without a new interrupt.
 e=prepare(True);e.uc.mem_write(STATE+4,b'\3');e.uc.emu_start(START|1,END,count=100);assert e.r8(STATE+4)==3
 result=dict(confidence='PROVEN',scope='Native exact candidate instructions and native SysTick watchdog; instruction-boundary interrupt injection, not physical timing',
  original_atomic=False,original=original,quarantine_overwrite_reproduced=True,
  fix=dict(address=hex(FIX),bytes=len(blob),hex=blob.hex(),sha256=sha(blob),patch_address=hex(START),branch_hex=b_w(START,FIX).hex(),in_memory_only=True),
  fixed_boundary_cases=fixed,preexisting_PRIMASK_cases=masked,already_quarantined_preserved=True,
  candidate_file_modified=False,new_firmware_image_generated=False,new_SYX_generated=False,
  limitation='Isolated commit fix only; full native coupled regression and final-image serialization of an amended candidate are not performed here.')
 (O/'success-atomicity.json').write_text(json.dumps(result,indent=2)+'\n')
 (O/'success-atomicity-fix.asm').write_text('\n'.join(f'{i.address:08x}: {i.mnemonic:9} {i.op_str}' for i in ins)+'\n')
 print('Original quarantine overwrite reproduced; isolated critical-section fix passes',len(fixed)+len(masked)+1,'checks; no image generated.')
if __name__=='__main__':main()
