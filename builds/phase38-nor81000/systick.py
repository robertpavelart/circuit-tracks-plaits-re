"""Observed bootloader basic SysTick; native counter code, no scheduler stand-in."""
from pendsv import *
from cold_boot import Cold
class TickModel(Model):
 def __init__(self,audit=True):
  super().__init__(audit);self.tick_active=False;self.ticks=[];self.tick_result=None;self.config=[];self.core_clock=[];self.clock_mmio=[]
 def observe_mmio(self,u,access,a,n,v):
  if a in (0xe000e010,0xe000e014,0xe000e018,0xe000ed20,0xe000ed23):
   self.clock_mmio.append(dict(pc=u.reg_read(UC_ARM_REG_PC),access='write' if access==17 else 'read',address=a,size=n,value=v if access==17 else int.from_bytes(u.mem_read(a,n),'little'),after_scheduler=bool(self.switches),after_native_tick=bool(self.ticks)))
   assert not (a==0xe000e010 and access!=17 and self.ticks),'unimplemented post-tick COUNTFLAG read-to-clear required'
 def observe(self,u,pc,n):
  if pc in (0x08002ee8,0x08002ef4,0x08002efa,0x08002f00,0x08002f04,0x08002f06):
   self.config.append(dict(pc=pc,registers=regs_no_psr(u),core_clock=r32(u,0x200004b4),CTRL=r32(u,0xe000e010),LOAD=r32(u,0xe000e014),VAL=r32(u,0xe000e018)))
  if self.tick_active:return None
  return super().observe(u,pc,n)
 def capture_tick(self,u):
  p=super().capture(u)
  p.update(CTRL=r32(u,0xe000e010),LOAD=r32(u,0xe000e014),VAL_backing=r32(u,0xe000e018),VAL_model='not decremented; ideal 2000-instruction event source only',
   core_clock=r32(u,0x200004b4),clock_increment_byte=u.mem_read(0x20000004,1)[0],
   clock_counter=r32(u,0x20000008),handler_counter=r32(u,0x20005518),kernel_counter=r32(u,0x200053c0))
  return p
 def tick_eligible(self,u):
  priority=u.mem_read(0xe000ed23,1)[0];basepri=u.reg_read(UC_ARM_REG_BASEPRI)
  return (u.reg_read(UC_ARM_REG_PRIMASK)==0 and u.reg_read(UC_ARM_REG_FAULTMASK)==0
   and (not basepri or priority<basepri) and u.reg_read(UC_ARM_REG_IPSR)==0)
 def enter_tick(self,u,row):
  pre=snap(u);icsr=r32(u,0xe000ed04);shcsr=r32(u,0xe000ed24)
  assert pre['ipsr']==0 and pre['control']==2 and pre['xpsr']&(1<<24),'unsupported SysTick entry context'
  assert self.tick_eligible(u),'SysTick masked / not eligible: pending must remain latched'
  priority=u.mem_read(0xe000ed23,1)[0]
  assert not pre['basepri'] or priority<pre['basepri'],'SysTick blocked by BASEPRI'
  assert icsr&(1<<26) and not icsr&((1<<28)|(1<<31)|0x1ff),'pending/active exception conflict'
  assert not any(u.mem_read(0xe000e300,32)) and not any(u.mem_read(0xe000e200,32)),'external arbitration unsupported'
  assert r32(u,0xe000e010)&3==3,'SysTick not enabled / interrupt disabled'
  vector=r32(u,0xe000ed08)+60;handler=r32(u,vector);assert handler&1;pc_valid(handler&~1)
  old=pre['psp'];pad=4 if old&4 else 0;address=old-32-pad;ram(address,32+pad);assert address%8==0
  vals=[u.reg_read(r) for r in FRAME];vals[6]=pre['pc'];vals[7]=(vals[7]&~512)|(512 if pad else 0)
  raw=struct.pack('<8I',*vals);u.mem_write(address,raw);u.reg_write(UC_ARM_REG_PSP,address)
  u.reg_write(UC_ARM_REG_CONTROL,0);u.reg_write(UC_ARM_REG_XPSR,(pre['xpsr']&0xf80f0000)|0x0100000f)
  u.reg_write(UC_ARM_REG_LR,0xfffffffd);u.reg_write(UC_ARM_REG_PC,handler)
  u.mem_write(0xe000ed04,struct.pack('<I',(icsr&~((1<<26)|0x1ff|0x1ff000))|0x800|15))
  u.mem_write(0xe000ed24,struct.pack('<I',shcsr|(1<<11)))
  row.update(pre=pre,priority=priority,vector_word=vector,handler=handler,entry_EXC_RETURN=0xfffffffd,hardware_frame_address=address,
   hardware_frame_hex=raw.hex(),hardware_frame=dict(zip(NAMES,vals)),padding=pad,handler_entry=snap(u),
   ICSR_active=r32(u,0xe000ed04),SHCSR_active=r32(u,0xe000ed24))
  self.tick_active=True;return handler
 def leave_tick(self,u,row):
  assert self.tick_active and u.reg_read(UC_ARM_REG_IPSR)==15,'not active SysTick / double consumption'
  # Actual native return opcode POP {r0,pc}: decode its two live MSP words.
  assert bytes(u.mem_read(u.reg_read(UC_ARM_REG_PC),2))==b'\x01\xbd','unexpected native SysTick return'
  msp=u.reg_read(UC_ARM_REG_MSP);ram(msp,8);temp,exc=struct.unpack('<2I',bytes(u.mem_read(msp,8)))
  assert exc==0xfffffffd,'invalid / unsupported SysTick EXC_RETURN'
  assert not r32(u,0xe000ed04)&((1<<28)|(1<<26)),'unimplemented natural tail chain required'
  a=u.reg_read(UC_ARM_REG_PSP);ram(a,32);assert a%8==0
  raw=bytes(u.mem_read(a,32));vals=struct.unpack('<8I',raw)
  assert vals[7]&(1<<24) and not vals[7]&0x1ff,'invalid SysTick frame';pc_valid(vals[6])
  new=a+32+(4 if vals[7]&512 else 0);ram(new-4,4)
  row['native_return_pop']=dict(MSP=msp,r0=temp,EXC_RETURN=exc,after_MSP=msp+8)
  u.reg_write(UC_ARM_REG_R0,temp);u.reg_write(UC_ARM_REG_MSP,msp+8)
  for reg,val in zip(FRAME[:6],vals[:6]):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_XPSR,vals[7]&~512);u.reg_write(UC_ARM_REG_PSP,new);u.reg_write(UC_ARM_REG_CONTROL,2)
  u.reg_write(UC_ARM_REG_FAULTMASK,0);u.reg_write(UC_ARM_REG_PC,vals[6]|1)
  u.mem_write(0xe000ed04,struct.pack('<I',(r32(u,0xe000ed04)&~0x1ff)|0x800))
  u.mem_write(0xe000ed24,struct.pack('<I',r32(u,0xe000ed24)&~(1<<11)))
  assert bytes(u.mem_read(a,32))==raw and u.reg_read(UC_ARM_REG_SP)==new
  row.update(return_EXC_RETURN=exc,return_frame_address=a,return_frame_hex=raw.hex(),restored=snap(u),frame_consumptions=1,
   ICSR_return=r32(u,0xe000ed04),SHCSR_return=r32(u,0xe000ed24))
  self.tick_active=False;return vals[6]
 def legacy_control(self,u):
  # Comparison-only fork of the exact live checkpoint. Never supplies RAM or
  # scheduler state to the authoritative cold boot.
  e=Cold('stock');v=e.uc;v.mem_write(0x20000000,bytes(u.mem_read(0x20000000,0x50000)))
  v.mem_write(0xe000e000,bytes(u.mem_read(0xe000e000,0x2000)))
  # Unicorn contexts must not cross Uc owners (native heap corruption on this
  # DLL). Copy exposed architectural registers into the comparison-only CPU.
  pre=snap(u)
  for i,reg in enumerate(GENERAL):v.reg_write(reg,pre[f'r{i}'])
  for name in ('msp','psp','lr','control','basepri','primask','faultmask','xpsr'):v.reg_write(SPECIAL[name],pre[name])
  v.reg_write(UC_ARM_REG_PC,pre['pc']|1);assert snap(v)==pre
  resume=v.reg_read(UC_ARM_REG_PC);sp=v.reg_read(UC_ARM_REG_SP);saved=v.context_save()
  hw=[v.reg_read(x) for x in FRAME];hw[6]=resume
  v.mem_write(sp-32,struct.pack('<8I',*hw));v.reg_write(UC_ARM_REG_SP,sp-32)
  v.reg_write(UC_ARM_REG_LR,0x0807ff01);v.reg_write(UC_ARM_REG_IPSR,15)
  handler=r32(v,r32(v,0xe000ed08)+60);v.emu_start(handler,0x0807ff00,count=1000)
  assert v.reg_read(UC_ARM_REG_PC)==0x0807ff00,'legacy handler did not return'
  v.context_restore(saved)
  return dict(registers=snap(v),scheduler_hex=bytes(v.mem_read(0x20005204,0x1d0)).hex(),
   current_TCB=r32(v,0x20005268),clock_counter=r32(v,0x20000008),handler_counter=r32(v,0x20005518),kernel_counter=r32(v,0x200053c0),
   RAM_sha256=sha(bytes(v.mem_read(0x20000000,0x50000)))),bytes(v.mem_read(0x20000000,0x50000))
 def service_tick(self,u):
  row=dict(captured=self.capture_tick(u),native_trace=[]);self.ticks.append(row)
  if len(self.ticks)==1:
   old=json.loads((O.parent/'phase36-pendsv-context/stock.json').read_text())
   assert row['captured']['registers']['pc']==int(old['stop']['pc'],16)
   assert row['captured']['RAM_sha256']==old['RAM_sha256'],'phase36 checkpoint SRAM mismatch'
   assert all(row['captured']['registers'][k]==int(v,16) for k,v in old['registers'].items() if k!='xPSR')
   assert row['captured']['registers']['xpsr']==int(old['registers']['xPSR'],16)
   row['legacy_ideal_wrapper'],legacy_RAM=self.legacy_control(u)
  # Ideal timer event requests SysTick/COUNTFLAG only; both software counter
  # increments must be made by real handler instructions below.
  u.mem_write(0xe000ed04,struct.pack('<I',r32(u,0xe000ed04)|(1<<26)))
  u.mem_write(0xe000e010,struct.pack('<I',r32(u,0xe000e010)|(1<<16)))
  row['ICSR_pending']=r32(u,0xe000ed04)
  handler=self.enter_tick(u,row);before=bytes(u.mem_read(0x20000000,0x50000));previous=[before];last=[None];writes=[]
  def observe(uc,pc,n,d):
   if not self.audit:
    if pc==0x0800933e:uc.emu_stop()
    return
   data=bytes(uc.mem_read(0x20000000,0x50000));diff=changes(previous[0],data)
   if last[0] is not None:last[0]['RAM_writes']=diff;writes.extend(diff)
   previous[0]=data;ins=next(md.disasm(bytes(uc.mem_read(pc,n)),pc))
   item=dict(pc=pc,instruction=ins.mnemonic+' '+ins.op_str,registers=regs_no_psr(uc))
   row['native_trace'].append(item);last[0]=item
   if pc==0x0800933e:uc.emu_stop()
  h=u.hook_add(UC_HOOK_CODE,observe)
  try:u.emu_start(handler,0xffffffff,count=1000)
  finally:u.hook_del(h)
  assert u.reg_read(UC_ARM_REG_PC)==0x0800933e,'native SysTick did not reach exception return'
  if not self.audit:writes=changes(before,bytes(u.mem_read(0x20000000,0x50000)))
  allowed=[(row['pre']['msp']-8,row['pre']['msp']),(0x20000008,0x2000000c),(0x20005518,0x2000551c)]
  unexpected=[x for x in writes if not any(lo<=x['address'] and x['address']+4<=hi for lo,hi in allowed)]
  assert not unexpected,'SysTick modified unrelated RAM'
  assert bytes(u.mem_read(row['hardware_frame_address'],32)).hex()==row['hardware_frame_hex'],'SysTick hardware frame corrupted'
  row.update(before_return=snap(u),native_write_ranges=allowed,unexpected_RAM_writes=unexpected,changed_word_writes=writes,
   PendSV_requested=bool(r32(u,0xe000ed04)&(1<<28)))
  resumed=self.leave_tick(u,row);after=self.capture_tick(u);row['after']=after
  assert row['restored']==row['pre'],'SysTick failed exact Thread register restoration'
  assert u.reg_read(UC_ARM_REG_MSP)==row['pre']['msp'],'native POP failed MSP restoration'
  assert after['clock_counter']==(row['captured']['clock_counter']+row['captured']['clock_increment_byte'])&0xffffffff
  assert after['handler_counter']==(row['captured']['handler_counter']+1)&0xffffffff
  assert after['scheduler_hex']==row['captured']['scheduler_hex'],'unexpected scheduler change'
  if 'legacy_ideal_wrapper' in row:
   legacy=row['legacy_ideal_wrapper'];keys=('scheduler_hex','clock_counter','handler_counter','kernel_counter')
   row['legacy_comparison']={k:legacy[k]==after[k] for k in keys}
   row['legacy_comparison']['registers']=legacy['registers']==row['restored']
   row['legacy_comparison']['current_TCB']=legacy['current_TCB']==after['current_task']['TCB']
   row['legacy_comparison']['full_RAM_equal']=legacy['RAM_sha256']==after['RAM_sha256']
   row['legacy_RAM_differences']=changes(legacy_RAM,bytes(u.mem_read(0x20000000,0x50000)))
  return resumed
 def finalize(self,u,stop):
  self.final_state=dict(registers=snap(u),ICSR=r32(u,0xe000ed04),SHCSR=r32(u,0xe000ed24),
   tick_count=len(self.ticks),switch_count=len(self.switches),current_TCB=r32(u,0x20005268),
   clock_counter=r32(u,0x20000008),handler_counter=r32(u,0x20005518),kernel_counter=r32(u,0x200053c0))
