"""Native decompressor with identical authenticated inputs; first divergence.
No output writes or decompressor instruction patches from the host fixture.
"""
from trace import *
from oracle import decode
results=[]
for entry,fn,descriptor in (('bootloader',0x0800927c,0x08009694),('application',0x080596c4,0x0805b7c8)):
 group=[]
 for hookmode in ('none','read','write','bounded'):
  e=Cold('stock');u=e.uc;steps=[]
  def snapshot(u,pc,n,d):
   if len(steps)<1200:
    steps.append(dict(pc=hex(pc),r0=hex(u.reg_read(UC_ARM_REG_R0)),r1=hex(u.reg_read(UC_ARM_REG_R1)),r3=hex(u.reg_read(UC_ARM_REG_R3)),r5=hex(u.reg_read(UC_ARM_REG_R5)),r6=hex(u.reg_read(UC_ARM_REG_R6))))
  def noop(*args):pass
  u.hook_add(UC_HOOK_CODE,snapshot)
  if hookmode=='read':u.hook_add(UC_HOOK_MEM_READ,noop)
  if hookmode=='write':u.hook_add(UC_HOOK_MEM_WRITE,noop)
  if hookmode=='bounded':
   u.hook_add(UC_HOOK_MEM_READ,noop,begin=0x40000000,end=0x4002ffff)
   u.hook_add(UC_HOOK_MEM_WRITE,noop,begin=0x40000000,end=0x4002ffff)
  rel,encoded,dest=struct.unpack('<III',u.mem_read(descriptor,12))
  source=bytes(u.mem_read(descriptor+rel,encoded>>1));expected,stats=decode(source)
  u.reg_write(UC_ARM_REG_SP,0x2004fff0);u.reg_write(UC_ARM_REG_R0,descriptor);u.reg_write(UC_ARM_REG_LR,0x0807ff01)
  try:u.emu_start(fn|1,0x0807ff00,count=200000);error=None
  except Exception as exc:error=str(exc)
  output=bytes(u.mem_read(dest,len(expected)))
  row=dict(entry=entry,hookmode=hookmode,error=error,end_PC=hex(u.reg_read(UC_ARM_REG_PC)),final_xPSR=hex(u.reg_read(UC_ARM_REG_XPSR)),native_output_matches_oracle=output==expected,trace=steps)
  group.append(row)
 base=group[0]
 assert base['native_output_matches_oracle'] and group[-1]['native_output_matches_oracle']
 for row in group[1:]:
  difference=next((index for index,(x,y) in enumerate(zip(base['trace'],row['trace'])) if x!=y),None)
  row['first_trace_difference']=None if difference is None else dict(index=difference,control=base['trace'][difference],instrumented=row['trace'][difference])
 results.extend(group)
(O/'instruction-control.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps([{k:v for k,v in x.items() if k!='trace'} for x in results],indent=1))
