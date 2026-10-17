"""Unchanged boot button predicate only; not a hardware recovery simulation."""
from support import *
rows=[]
for bits in range(8):
 e=Physical();u=e.uc;seen=[]
 def hook(u,pc,n,d):
  if pc==0x0800489c:
   button=u.reg_read(UC_ARM_REG_R1);seen.append(button)
   index=(0x12,8,9).index(button);u.reg_write(UC_ARM_REG_R0,(bits>>index)&1)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
 u.hook_add(UC_HOOK_CODE,hook)
 e.w32(0x20005378,0);u.mem_write(0x20040000,b'\x02')
 e.call(0x08003ab0,0,0x20040000,sp=0x2004fff0)
 assert e.r8(0x20005378)==int(bits==7) and seen==[0x12,8,9]
 rows.append(dict(pressed_bits=bits,boot_mode_flag=e.r8(0x20005378),button_IDs=seen))
result=dict(confidence='PROVEN',scope='Actual boot callback with modeled scanner return values; constructors, timing, button mapping and recovery installation not executed',
 cases=rows,bootloader_sha256=sha(ROM[:0x10000]),recovery_available_on_hardware='UNKNOWN',
 evidence='0x08002fde calls boot initialization/metadata/buttons before application handoff; 0x08003ab0 sets mode flag iff IDs18,8,9 all return1; 0x08003000 skips normal install/application branch when mode detected',
 physical_button_names='Reference docs/NOTAS.md reports Scales + Preset + Note; no independent hardware observation here',
 no_new_recovery_code=True,hardware_access=False)
(O/'recovery.json').write_text(json.dumps(result,indent=2)+'\n')
print('8 native boot-button predicate cases passed; hardware recovery UNKNOWN')
