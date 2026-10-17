"""Only observed privileged basic-frame PendSV: native scheduler, fail closed.

No RAM hooks. Instruction operand snapshots plus per-instruction SRAM diffs
cover native handler/scheduler accesses without the known RAM-hook artifact.
"""
from svc import *
from capstone.arm import ARM_OP_MEM
O=Path(__file__).resolve().parent

def changes(before,after):
 out=[]
 for off in range(0,len(before),4096):
  if before[off:off+4096]==after[off:off+4096]:continue
  for j in range(off,min(off+4096,len(before)),4):
   if before[j:j+4]!=after[j:j+4]:out.append(dict(address=0x20000000+j,before=before[j:j+4].hex(),after=after[j:j+4].hex()))
 return out
def regs_no_psr(u):
 return {k:u.reg_read(v) for k,v in SPECIAL.items() if k!='xpsr'}|{f'r{i}':u.reg_read(r) for i,r in enumerate(GENERAL)}
def task(u,tcb):
 ram(tcb,92);sp=r32(u,tcb);ram(sp,68)
 return dict(TCB=tcb,name=bytes(u.mem_read(tcb+0x34,10)).split(b'\0')[0].decode('ascii'),saved_PSP=sp,
  stack_base=r32(u,tcb+0x30),priority=r32(u,tcb+0x2c),TCB_hex=bytes(u.mem_read(tcb,92)).hex(),context_hex=bytes(u.mem_read(sp,68)).hex())
def validate_context(u,address):
 ram(address,68);assert address%8==4,'basic software context must place hardware frame at 8-byte alignment'
 words=struct.unpack('<17I',bytes(u.mem_read(address,68)))
 assert words[8]==0xfffffffd,'invalid / unsupported next EXC_RETURN'
 hw=words[9:];assert hw[7]&(1<<24),'next Thumb bit missing';assert not hw[7]&0x1ff,'next context is not Thread';pc_valid(hw[6])
 return words

class Model(SVC):
 def __init__(self,audit=True):
  super().__init__();self.svc_result=self.result;self.switches=[];self.pendsv_active=False;self.after_count=0;self.audit=audit
 def observe(self,u,pc,n):
  if self.pendsv_active:return None
  if not self.switches:
   action=super().observe(u,pc,n)
   if action=='next unsupported pending PendSV boundary':return 'native PendSV boundary'
   return action
  if r32(u,0xe000ed04)&(1<<28):return 'native PendSV boundary'
  self.after_count+=1
  if len(self.switches[-1]['post_return_trace'])<96:
   self.switches[-1]['post_return_trace'].append(dict(pc=pc,registers=regs_no_psr(u)))
  if bytes(u.mem_read(pc,n)) in (b'\x30\xbf',b'\x20\xbf'):
   self.switches[-1]['next_boundary']=dict(kind='unsupported task sleep',pc=pc)
   return 'next unsupported task WFI/WFE boundary'
  return None
 def capture(self,u):
  current=r32(u,0x20005268);ram(current,92)
  return dict(registers=snap(u),ICSR=r32(u,0xe000ed04),SHCSR=r32(u,0xe000ed24),
   SHPR3=r32(u,0xe000ed20),AIRCR=r32(u,0xe000ed0c),VTOR=r32(u,0xe000ed08),current_task=task(u,current),
   scheduler_base=0x20005204,scheduler_hex=bytes(u.mem_read(0x20005204,0x1d0)).hex(),
   stack_window_address=u.reg_read(UC_ARM_REG_PSP)-128,stack_window_hex=bytes(u.mem_read(u.reg_read(UC_ARM_REG_PSP)-128,128)).hex(),
   MSP_stack_address=u.reg_read(UC_ARM_REG_MSP)-96,MSP_stack_hex=bytes(u.mem_read(u.reg_read(UC_ARM_REG_MSP)-96,128)).hex(),
   NVIC_active_hex=bytes(u.mem_read(0xe000e300,32)).hex(),NVIC_pending_hex=bytes(u.mem_read(0xe000e200,32)).hex(),
   FPCCR=r32(u,0xe000ef34),FPCAR=r32(u,0xe000ef38),
   RAM_sha256=sha(bytes(u.mem_read(0x20000000,0x50000))))
 def enter_pendsv(self,u,row):
  pre=snap(u);icsr=r32(u,0xe000ed04);shcsr=r32(u,0xe000ed24)
  assert pre['ipsr']==0 and icsr&0x1ff==0,'nested entry unsupported'
  assert pre['control']==2,'only observed privileged PSP Thread entry supported'
  assert pre['xpsr']&(1<<24),'entry is not Thumb state'
  assert pre['primask']==pre['faultmask']==0,'PendSV masked'
  assert not pre['basepri']&15,'unsupported priority granularity'
  assert not any(u.mem_read(0xe000e300,32)) and not any(u.mem_read(0xe000e200,32)),'external pending/active arbitration unsupported'
  priority=u.mem_read(0xe000ed22,1)[0]
  assert not pre['basepri'] or priority<pre['basepri'],'PendSV blocked by BASEPRI'
  assert icsr&(1<<28),'no pending PendSV'
  assert not icsr&((1<<26)|(1<<31)),'other pending system exception unsupported'
  handler=r32(u,r32(u,0xe000ed08)+56);assert handler&1;pc_valid(handler&~1)
  old=pre['psp'];ram(old-32,32);pad=4 if old&4 else 0;new=old-32-pad;ram(new,32+pad);assert new%8==0
  vals=[u.reg_read(x) for x in FRAME];vals[6]=pre['pc'];vals[7]=(vals[7]&~512)|(512 if pad else 0)
  raw=struct.pack('<8I',*vals);u.mem_write(new,raw);u.reg_write(UC_ARM_REG_PSP,new)
  u.reg_write(UC_ARM_REG_CONTROL,pre['control']&~2)
  u.reg_write(UC_ARM_REG_XPSR,(pre['xpsr']&0xf80f0000)|0x0100000e)
  u.reg_write(UC_ARM_REG_LR,0xfffffffd);u.reg_write(UC_ARM_REG_PC,handler)
  # RETTOBASE=1 because this is the sole active exception. Consume pending,
  # update VECTACTIVE/VECTPENDING and native SHCSR.PENDSVACT.
  u.mem_write(0xe000ed04,struct.pack('<I',(icsr&~((1<<28)|0x1ff|0x1ff000))|0x800|14))
  u.mem_write(0xe000ed24,struct.pack('<I',shcsr|(1<<10)))
  row.update(pre=pre,priority=priority,vector_word=r32(u,0xe000ed08)+56,handler=handler,entry_EXC_RETURN=0xfffffffd,
   hardware_frame_address=new,hardware_frame=dict(zip(NAMES,vals)),hardware_frame_hex=raw.hex(),padding=pad,
   handler_entry=snap(u),ICSR_active=r32(u,0xe000ed04),SHCSR_active=r32(u,0xe000ed24))
  self.pendsv_active=True
  return handler
 def leave_pendsv(self,u,row):
  assert self.pendsv_active and u.reg_read(UC_ARM_REG_IPSR)==14,'not active PendSV / double consumption'
  exc=u.reg_read(UC_ARM_REG_LR);assert exc==0xfffffffd,'unsupported EXC_RETURN'
  assert not r32(u,0xe000ed04)&((1<<28)|(1<<26)),'tail chain unsupported'
  address=u.reg_read(UC_ARM_REG_PSP);ram(address,32);assert address%8==0
  raw=bytes(u.mem_read(address,32));vals=struct.unpack('<8I',raw)
  assert vals[7]&(1<<24) and not vals[7]&0x1ff,'invalid hardware frame xPSR';pc_valid(vals[6])
  new=address+32+(4 if vals[7]&512 else 0);ram(new-4,4)
  assert u.reg_read(UC_ARM_REG_CONTROL)==0,'unexpected handler CONTROL'
  for reg,val in zip(FRAME[:6],vals[:6]):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_XPSR,vals[7]&~512);u.reg_write(UC_ARM_REG_PSP,new)
  u.reg_write(UC_ARM_REG_CONTROL,2);u.reg_write(UC_ARM_REG_FAULTMASK,0)
  u.reg_write(UC_ARM_REG_PC,vals[6]|1)
  u.mem_write(0xe000ed04,struct.pack('<I',(r32(u,0xe000ed04)&~0x1ff)|0x800))
  u.mem_write(0xe000ed24,struct.pack('<I',r32(u,0xe000ed24)&~(1<<10)))
  assert bytes(u.mem_read(address,32))==raw and u.reg_read(UC_ARM_REG_SP)==new
  row.update(return_EXC_RETURN=exc,return_frame_address=address,return_frame_hex=raw.hex(),restored=snap(u),
   frame_consumptions=1,ICSR_return=r32(u,0xe000ed04),SHCSR_return=r32(u,0xe000ed24))
  self.pendsv_active=False;self.after_count=0
  return vals[6]
 def service_pendsv(self,u):
  row=dict(captured=self.capture(u),native_trace=[],post_return_trace=[],observer='detailed' if self.audit else 'minimal control');self.switches.append(row)
  if len(self.switches)==1:
   expected=json.loads((O.parent/'phase35-svc-context/stock.json').read_text())
   assert row['captured']['registers']==expected['svc']['pending_checkpoint']['registers'],'phase35 CPU state mismatch'
   assert row['captured']['RAM_sha256']==expected['RAM_sha256'],'phase35 SRAM mismatch'
   assert row['captured']['ICSR']==expected['svc']['pending_checkpoint']['ICSR']
  handler=self.enter_pendsv(u,row);out=row['captured']['current_task'];oldpsp=row['pre']['psp'];msp=row['pre']['msp']
  previous=[bytes(u.mem_read(0x20000000,0x50000))];last=[None];writes=[]
  def observe(uc,pc,n,d):
   if pc==0x08003170:
    nxt=r32(uc,0x20005268);row['incoming']=task(uc,nxt);validate_context(uc,row['incoming']['saved_PSP'])
    if len(self.switches)==1:
     initialized=[x for x in self.svc_result['task_frame_initializers'] if x['saved_context']==row['incoming']['saved_PSP']]
     assert len(initialized)==1 and initialized[0]['frame_hex']==row['incoming']['context_hex'],'incoming frame is not native constructor output'
     row['incoming_native_constructor']=initialized[0]
   if not self.audit:
    if pc==0x08003186:uc.emu_stop()
    return
   current=bytes(uc.mem_read(0x20000000,0x50000));diff=changes(previous[0],current)
   if last[0] is not None:
    last[0]['RAM_writes']=diff;writes.extend(diff)
   previous[0]=current
   ins=next(md.disasm(bytes(uc.mem_read(pc,n)),pc))
   item=dict(pc=pc,instruction=ins.mnemonic+' '+ins.op_str,registers=regs_no_psr(uc),operand_memory=[])
   def val(name):
    if name=='pc':return (pc+4)&~3
    aliases=dict(ip='r12',sb='r9',sl='r10',fp='r11')
    return item['registers'][aliases.get(name,name)]
   for op in ins.operands:
    if op.type==ARM_OP_MEM:
     base=val(ins.reg_name(op.mem.base)) if op.mem.base else 0
     index=val(ins.reg_name(op.mem.index)) if op.mem.index else 0
     assert not op.shift.value,'unmodeled shifted address'
     a=(base+index+op.mem.disp)&0xffffffff
     size=1 if ins.mnemonic.startswith(('ldrb','strb')) else 2 if ins.mnemonic.startswith(('ldrh','strh')) else 4
     item['operand_memory'].append(dict(address=a,size=size,before=bytes(uc.mem_read(a,size)).hex()))
   if ins.mnemonic.startswith(('stm','ldm')):
    base=val(ins.reg_name(ins.operands[0].reg));count=len(ins.operands)-1
    a=base-count*4 if ins.mnemonic.startswith('stmdb') else base
    item['operand_memory'].append(dict(address=a,size=count*4,before=bytes(uc.mem_read(a,count*4)).hex()))
   if ins.mnemonic in ('push','pop'):
    count=len(ins.operands);a=item['registers']['sp']-(count*4 if ins.mnemonic=='push' else 0)
    item['operand_memory'].append(dict(address=a,size=count*4,before=bytes(uc.mem_read(a,count*4)).hex()))
   row['native_trace'].append(item);last[0]=item
   if pc==0x08003186:uc.emu_stop()
  hook=u.hook_add(UC_HOOK_CODE,observe)
  try:u.emu_start(handler,0xffffffff,count=2000)
  finally:u.hook_del(hook)
  assert u.reg_read(UC_ARM_REG_PC)==0x08003186,'native PendSV did not reach return'
  if not self.audit:writes=changes(previous[0],bytes(u.mem_read(0x20000000,0x50000)))
  incoming=row['incoming'];ctx=validate_context(u,incoming['saved_PSP'])
  assert [u.reg_read(UC_ARM_REG_R4+i) for i in range(8)]==list(ctx[:8]),'incoming r4-r11 mismatch'
  assert u.reg_read(UC_ARM_REG_PSP)==incoming['saved_PSP']+36,'native PSP restore mismatch'
  expected_saved=row['hardware_frame_address']-36
  assert r32(u,out['TCB'])==expected_saved,'outgoing saved PSP field mismatch'
  expectedwords=[row['pre'][f'r{i}'] for i in range(4,12)]+[0xfffffffd]
  assert bytes(u.mem_read(expected_saved,36))==struct.pack('<9I',*expectedwords),'outgoing registers not saved'
  assert bytes(u.mem_read(row['hardware_frame_address'],32)).hex()==row['hardware_frame_hex'],'outgoing hardware frame corrupted'
  # Exact ownership for this native switch: outgoing stack, handler scratch,
  # outgoing TCB SP, scheduler yield/current/list-index stores observed in code.
  scheduler=0x20005204
  bitmap=int.from_bytes(bytes.fromhex(row['captured']['scheduler_hex'])[0x74:0x78],'little')
  assert bitmap,'no ready tasks'
  priority=bitmap.bit_length()-1;readylist=scheduler+20*priority
  allowed=[(expected_saved,oldpsp),(msp-24,msp),(out['TCB'],out['TCB']+4),
   (scheduler+0x78,scheduler+0x7c),(0x20005268,0x2000526c),(readylist+4,readylist+8)]
  all_stores=[]
  for ins in row['native_trace']:
   if ins['instruction'].startswith(('str','stm','push')):
    for operand in ins['operand_memory']:
     a,n=operand['address'],operand['size'];assert any(lo<=a and a+n<=hi for lo,hi in allowed),'native store intent outside allowed ranges'
     all_stores.append(dict(pc=ins['pc'],address=a,size=n))
  bad=[x for x in writes if not any(lo<=x['address'] and x['address']+4<=hi for lo,hi in allowed)]
  row.update(outgoing_saved_PSP=expected_saved,outgoing_software_frame_hex=bytes(u.mem_read(expected_saved,36)).hex(),
   native_write_ranges=allowed,unexpected_RAM_writes=bad,native_store_intents=all_stores,changed_word_writes=len(writes),before_return=snap(u),
   ready_list_base=readylist,ready_bitmap=bitmap,selected_priority=priority)
  assert not bad,'native handler wrote unrelated RAM'
  resumed=self.leave_pendsv(u,row)
  return resumed
