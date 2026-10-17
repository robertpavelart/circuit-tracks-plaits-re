"""Controlled fixture ablation. Stock first, no firmware/source mutation."""
from pathlib import Path
import sys,json,struct
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'builds/phase33-preservation-powercycle'))
from cold_boot import Cold
from support import UC_ARM_REG_SP,UC_ARM_REG_MSP,UC_ARM_REG_CONTROL,UC_ARM_REG_IPSR,UC_ARM_REG_PC,UC_ARM_REG_XPSR,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
rows=[]
for entry in (0x08000000,0x08010000):
 for variant in ('stock','diagnostic'):
  for mode in ('SP only','SP MSP','SP CONTROL','SP IPSR','all registers','code hook','read hook','write hook','all hooks'):
   e=Cold(variant);u=e.uc;sp,pc=struct.unpack('<II',u.mem_read(entry,8));u.reg_write(UC_ARM_REG_SP,sp)
   if mode in ('SP MSP','all registers'):u.reg_write(UC_ARM_REG_MSP,sp)
   if mode in ('SP CONTROL','all registers'):u.reg_write(UC_ARM_REG_CONTROL,0)
   if mode in ('SP IPSR','all registers'):u.reg_write(UC_ARM_REG_IPSR,0)
   def code(u,a,n,d):pass
   def mem(u,access,a,n,v,d):pass
   if mode in ('code hook','all hooks'):u.hook_add(UC_HOOK_CODE,code)
   if mode in ('read hook','all hooks'):u.hook_add(UC_HOOK_MEM_READ,mem)
   if mode in ('write hook','all hooks'):u.hook_add(UC_HOOK_MEM_WRITE,mem)
   try:u.emu_start(pc,0xffffffff,count=100000);error=None
   except Exception as exc:error=str(exc)
   rows.append(dict(entry=hex(entry),variant=variant,mode=mode,end_PC=hex(u.reg_read(UC_ARM_REG_PC)),error=error,xPSR=hex(u.reg_read(UC_ARM_REG_XPSR))))
(O/'isolation.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=1))
