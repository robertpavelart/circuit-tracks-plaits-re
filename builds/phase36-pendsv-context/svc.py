"""Narrow basic-frame SVC model. Real native task frames; no scheduler bypass.

Arm DUI0646C 2.1.3/2.4: handler MSP, CCR.STKALIGN fixed 1 on M7,
basic frame and F9/FD returns. Unsupported nesting/FP fail closed.
"""
import sys,struct,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'builds/phase33-preservation-powercycle'))
from support import *

SPECIAL={k:globals()['UC_ARM_REG_'+k.upper()] for k in ('control','primask','basepri','faultmask','msp','psp','lr','xpsr','ipsr','pc','sp')}
GENERAL=[UC_ARM_REG_R0+i for i in range(13)]
FRAME=[UC_ARM_REG_R0+i for i in range(4)]+[UC_ARM_REG_R12,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_XPSR]
NAMES=['r0','r1','r2','r3','r12','lr','pc','xpsr']
def snap(u):return {k:u.reg_read(v) for k,v in SPECIAL.items()}|{f'r{i}':u.reg_read(r) for i,r in enumerate(GENERAL)}
def r32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
def ram(a,n=4):assert a%4==0 and 0x20000000<=a and a+n<=0x20050000, f'invalid RAM {a:08x}+{n}'
def pc_valid(pc):assert pc%2==0 and 0x08000000<=pc<0x08080000,f'invalid PC {pc:08x}'

class SVC:
 def __init__(self):
  self.result=dict(confidence='PROVEN',handler_trace=[],task_frame_initializers=[],post_return_trace=[],scheduler_start_trace=[],TCB_store_trace=[])
  self.active=False;self.returned=False;self.count=0;self.initializers={}
 def observe(self,u,pc,n):
  if 0x080031a4<=pc<=0x080031c2:self.result['scheduler_start_trace'].append(dict(pc=pc,registers=snap(u)))
  if pc==0x080031c2 and not self.active and not self.returned:return 'native SVC boundary'
  if pc in (0x08002716,0x0800272c,0x08002790):
   self.result['TCB_store_trace'].append(dict(pc=pc,registers=snap(u)))
  # Capture the native task-frame construction routine, including allocator
  # inputs. Observer uses only instruction hooks / host RAM snapshots.
  if pc==0x08002d3c:
   regs=snap(u);self.initializers[regs['lr']&~1]=dict(pc=pc,registers=regs,
    input_stack_top=regs['r0'],task_entry=regs['r1'],task_argument=regs['r2'])
  if pc in self.initializers:
   row=self.initializers.pop(pc);saved=u.reg_read(UC_ARM_REG_R0);ram(saved,68)
   row.update(return_pc=pc,saved_context=saved,frame_hex=bytes(u.mem_read(saved,68)).hex())
   self.result['task_frame_initializers'].append(row)
  if self.returned:
   if r32(u,0xe000ed04)&(1<<28):
    self.result['pending_checkpoint']=dict(registers=snap(u),ICSR=r32(u,0xe000ed04),
     SHCSR=r32(u,0xe000ed24),cause='native idle task requested PendSV; no tail-chain service fabricated')
    return 'next unsupported pending PendSV boundary'
   self.count+=1
   if len(self.result['post_return_trace'])<96:self.result['post_return_trace'].append(dict(pc=pc,registers=snap(u)))
   if pc==0x0800312c:return 'next unsupported PendSV boundary'
   if self.count>=128:return 'post-SVC 128-native-instruction checkpoint'
  return None
 def enter(self,u,site):
  pre=snap(u);self.result['pre']=pre;assert pre['ipsr']==0,'nested SVC unsupported'
  assert not pre['control']&1,'unprivileged fixture unsupported: Unicorn special-register API masks banked registers'
  svc_priority=u.mem_read(0xe000ed1f,1)[0];self.result['SVC_priority']=svc_priority
  assert pre['primask']==pre['faultmask']==0,'masked SVC unsupported'
  assert not pre['basepri'] or svc_priority<pre['basepri'],'SVC blocked by BASEPRI'
  assert pre['control']&4==0,'FP frame unsupported'
  icsr=r32(u,0xe000ed04);shcsr=r32(u,0xe000ed24)
  assert icsr&0x1ff==0 and shcsr&0x80==0,'active system exception unsupported'
  assert not icsr&((1<<28)|(1<<26)),'pending exception at SVC entry unsupported'
  assert bytes(u.mem_read(site,2))==b'\x00\xdf'
  selected='psp' if pre['control']&2 else 'msp';old=pre[selected];ram(old-32,32)
  self.result['pre_stack_window']=dict(address=old-128,hex=bytes(u.mem_read(old-128,128)).hex())
  padding=4 if old&4 else 0;new=old-32-padding;ram(new,32+padding);assert new%8==0
  values=[u.reg_read(x) for x in FRAME];values[6]=site+2;values[7]=(values[7]&~512)|(512 if padding else 0)
  raw=struct.pack('<8I',*values);u.mem_write(new,raw)
  u.reg_write(SPECIAL[selected],new)
  exc_return=0xfffffffd if selected=='psp' else 0xfffffff9
  vectorbase=r32(u,0xe000ed08);handler=r32(u,vectorbase+44);assert handler&1;pc_valid(handler&~1)
  u.reg_write(UC_ARM_REG_CONTROL,pre['control']&~2)
  u.reg_write(UC_ARM_REG_XPSR,(pre['xpsr']&0xf80f0000)|0x0100000b)
  u.reg_write(UC_ARM_REG_LR,exc_return)
  u.reg_write(UC_ARM_REG_PC,handler)
  u.mem_write(0xe000ed04,struct.pack('<I',(icsr&~0x1ff)|11))
  u.mem_write(0xe000ed24,struct.pack('<I',shcsr|0x80))
  self.active=True
  self.result.update(pre=pre,vector_base=vectorbase,vector_word=vectorbase+44,handler=handler,entry_EXC_RETURN=exc_return,
   entry_stack=selected,entry_frame_address=new,entry_frame=dict(zip(NAMES,values)),entry_frame_hex=raw.hex(),padding=padding,handler_entry=snap(u),
   ICSR_before_entry=icsr,SHCSR_before_entry=shcsr,ICSR_at_entry=r32(u,0xe000ed04),SHCSR_at_entry=r32(u,0xe000ed24),
   CCR_backing_register=r32(u,0xe000ed14),effective_M7_STKALIGN=1)
  return handler
 def leave(self,u,exc):
  assert self.active,'frame already consumed / no active SVC'
  assert u.reg_read(UC_ARM_REG_IPSR)==11,'not in SVC handler'
  assert exc in (0xfffffff9,0xfffffffd),'malformed / unsupported EXC_RETURN'
  assert not r32(u,0xe000ed04)&((1<<28)|(1<<26)),'tail-chain unsupported'
  selected='psp' if exc&4 else 'msp';address=u.reg_read(SPECIAL[selected]);ram(address,32);assert address%8==0,'unaligned frame'
  raw=bytes(u.mem_read(address,32));values=list(struct.unpack('<8I',raw));xpsr=values[7]
  assert xpsr&(1<<24),'missing Thumb bit';assert xpsr&0x1ff==0,'nested return unsupported';pc_valid(values[6])
  new=address+32+(4 if xpsr&512 else 0);ram(new-4,4)
  control=u.reg_read(UC_ARM_REG_CONTROL);self.result['before_return']=snap(u)
  # Exception unstack changes IPSR before selecting the Thread SP.
  for reg,value in zip(FRAME[:6],values[:6]):u.reg_write(reg,value)
  u.reg_write(UC_ARM_REG_XPSR,xpsr&~512)
  u.reg_write(SPECIAL[selected],new)
  u.reg_write(UC_ARM_REG_CONTROL,(control&~6)|(2 if selected=='psp' else 0))
  u.reg_write(UC_ARM_REG_FAULTMASK,0)
  u.reg_write(UC_ARM_REG_PC,values[6]|1)
  u.mem_write(0xe000ed04,struct.pack('<I',r32(u,0xe000ed04)&~0x1ff))
  u.mem_write(0xe000ed24,struct.pack('<I',r32(u,0xe000ed24)&~0x80))
  assert bytes(u.mem_read(address,32))==raw,'unstack changed frame contents'
  assert u.reg_read(UC_ARM_REG_SP)==new
  assert u.reg_read(UC_ARM_REG_IPSR)==0
  assert u.reg_read(UC_ARM_REG_CONTROL)&1==control&1
  self.active=False;self.returned=True
  self.result.update(return_EXC_RETURN=exc,return_stack=selected,return_frame_address=address,return_frame=dict(zip(NAMES,values)),
   return_frame_hex=raw.hex(),restored=snap(u),frame_consumptions=1)
  self.result['ICSR_after_return']=r32(u,0xe000ed04);self.result['SHCSR_after_return']=r32(u,0xe000ed24)
  return values[6]
 def service(self,u):
  handler=self.enter(u,0x080031c2)
  owner=r32(u,0x20005268);ram(owner,4);saved=r32(u,owner);ram(saved,68)
  original=bytes(u.mem_read(saved,68));entry_raw=bytes(u.mem_read(self.result['entry_frame_address'],32))
  native_initializers=[x for x in self.result['task_frame_initializers'] if x['saved_context']==saved]
  assert len(native_initializers)==1 and native_initializers[0]['frame_hex']==original.hex(),'task frame not native constructor output'
  self.result.update(current_TCB_global=0x20005268,current_TCB=owner,saved_context=saved,saved_context_hex=original.hex(),
   TCB_hex=bytes(u.mem_read(owner,92)).hex(),task_name=bytes(u.mem_read(owner+0x34,10)).split(b'\0')[0].decode('ascii'),
   RAM_before_handler_sha256=sha(bytes(u.mem_read(0x20000000,0x50000))))
  def observe(uc,pc,n,d):
   if not self.active:return
   row=dict(pc=pc,instruction=next(md.disasm(bytes(uc.mem_read(pc,n)),pc)).mnemonic,registers=snap(uc))
   accesses={0x08003188:(0x080031d4,4),0x0800318a:(0x20005268,4),0x0800318c:(owner,4),0x0800318e:(saved,36)}
   if pc in accesses:
    address,size=accesses[pc];row['native_load']=dict(address=address,size=size,hex=bytes(uc.mem_read(address,size)).hex())
   self.result['handler_trace'].append(row)
   if pc==0x080031a2:uc.emu_stop()
  handle=u.hook_add(UC_HOOK_CODE,observe)
  try:u.emu_start(handler,0xffffffff,count=64)
  finally:u.hook_del(handle)
  assert u.reg_read(UC_ARM_REG_PC)==0x080031a2,'native handler did not reach BX LR'
  assert u.reg_read(UC_ARM_REG_PSP)==saved+36,'native MSR PSP mismatch'
  assert bytes(u.mem_read(saved,68))==original,'native handler corrupted saved task frame'
  assert bytes(u.mem_read(self.result['entry_frame_address'],32))==entry_raw,'SVC entry frame corrupted'
  assert self.result['RAM_before_handler_sha256']==sha(bytes(u.mem_read(0x20000000,0x50000))),'unexpected handler RAM write'
  expected=struct.unpack('<9I',original[:36]);actual=[u.reg_read(UC_ARM_REG_R4+i) for i in range(8)]+[u.reg_read(UC_ARM_REG_LR)]
  assert actual==list(expected),'software-saved registers not restored'
  return self.leave(u,u.reg_read(UC_ARM_REG_LR))
