"""Actual stock queue/Storage/IRQ/wait + emulator-only submit/completion/service.
No firmware image, original coefficient bytes, WinMM or hardware access.
The test arena is deliberately outside physical STM32 SRAM. No ownership claim.
"""
from shims import *
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
sys.path.insert(0,str(R/'builds/phase27-qspi-read'))
from protocol import request,Receiver,synthetic_packets
class Blocked(Exception):pass
class SubmitPaused(Exception):pass
class Model:
 def __init__(self):
  self.s=authentic_session();self.e=self.s.e;self.u=u=self.e.uc;self.shims=load(u)
  u.mem_map(0xa0001000,0x1000)
  self.wrapper=self.e.r32(0x20006968);self.backend=self.e.r32(self.wrapper+4);self.queue=self.e.r32(self.wrapper+8)
  self.holder=self.e.r32(0x20006790);self.storage=self.e.r32(self.holder);self.kernel=w(0x0801cf90)
  self.router=self.e.r32(w(0x0801edd0));self.port=self.e.r32(self.e.r32(self.router+0x14));self.pipe=self.e.r32(self.port+0x14)
  self.iface=self.e.r32(self.pipe+4);self.stream=self.e.r32(self.iface+4);self.dev=self.e.r32(self.stream+0x10)
  u.mem_write(self.dev+0x274,b'\3');u.mem_write(self.stream+0xc,b'\0')
  self.task='Main';self.minsp={};self.events=[];self.reads=[];self.commands=[];self.ctx=None;self.wait=None
  self.ticks=0;self.usb=None;self.usb_delay=2;self.usb_bytes=[];self.frames=[];self.callback_count=0;self.sleeps=0
  self.payload=bytes(((i*73)^(i>>1)^0xa6)&255 for i in range(512))
  self.regchecks=0;self.guardchecks=0;self.retchecks=0;self.background_ticks=0;self.submission_returns=0;self.busy_rejections=0
  self.stagesp={};self.stage='setup';self.visited=set();self.edges=set();self.payload_cpu_writes=0;self.Storage_return_checks=0
  self.pause_submit=False;self.mainctx=None
  self.guards={}
  for a,n in ((STATE,32),(REQ,24),(PAYLOAD,512),(PACKET,232),(DESC,8)):
   u.mem_write(a,bytes(n))
   for at in (a-8,a+n):
    val=struct.pack('<II',0xdead0000|(at&65535),0xcafe0129);u.mem_write(at,val);self.guards[at]=val
  self.stack_bounds={'Main':(0x2000775c,0x20008358),'Storage':(0x20008d44,0x20009240),'IRQ':(0x2004f000,0x20050000)}
  for name in ('Main','Storage'):
   lo,hi=self.stack_bounds[name];u.mem_write(lo,b'LOW!');u.mem_write(hi,b'HIGH')
  self.original_IRQ=bytes(u.mem_read(0x080573e0,14));self.notification_targets=[]
  u.hook_add(UC_HOOK_CODE,self.code);u.hook_add(UC_HOOK_MEM_WRITE,self.write)
 def ret(self,v=0):self.u.reg_write(UC_ARM_REG_R0,v);self.u.reg_write(UC_ARM_REG_PC,self.u.reg_read(UC_ARM_REG_LR)|1)
 def flags(self):return dict(phase=self.e.r32(STATE),status=self.e.r32(STATE+4),semaphore=self.e.r8(self.backend+8),
  Main_flags=hex(self.e.r32(0x20007758)),Storage_flags=hex(self.e.r32(self.holder+8)),controller=hex(self.e.r32(0x20005550)),
  queued_bytes=self.queued(),wrapper_pending_byte=self.e.r8(self.wrapper+12),wrapper_sync_word=self.e.r32(self.wrapper+16))
 def queued(self):
  q=self.queue;cap=int.from_bytes(self.u.mem_read(q+4,2),'little');h=int.from_bytes(self.u.mem_read(q+6,2),'little');t=int.from_bytes(self.u.mem_read(q+8,2),'little')
  return (h-t)%cap
 def check(self):
  for at,v in self.guards.items():assert bytes(self.u.mem_read(at,8))==v,('arena guard',hex(at))
  for name in ('Main','Storage'):
   lo,hi=self.stack_bounds[name];assert bytes(self.u.mem_read(lo,4))==b'LOW!' and bytes(self.u.mem_read(hi,4))==b'HIGH',name
  assert bytes(self.u.mem_read(0x080573e0,14))==self.original_IRQ
  assert self.e.r32(0x20006790)==self.holder
  self.guardchecks+=1
 def code(self,u,pc,n,d):
  sp=u.reg_read(UC_ARM_REG_SP);self.minsp[self.task]=min(self.minsp.get(self.task,sp),sp)
  self.stagesp[self.stage]=min(self.stagesp.get(self.stage,sp),sp)
  if pc not in self.visited:
   self.visited.add(pc)
   ins=next(md.disasm(bytes(u.mem_read(pc,n)),pc),None)
   if ins and ins.mnemonic in ('bl','blx','b.w'):
    target=ins.op_str
    if ins.mnemonic=='blx' and ins.operands[0].type==1:
     target=hex(u.reg_read(globals()['UC_ARM_REG_'+ins.op_str.upper()]))
    self.edges.add((hex(pc),ins.mnemonic,target))
  lo,hi=self.stack_bounds[self.task];assert lo+4<=sp<=hi,('stack',self.task,hex(pc),hex(sp))
  if pc in (0x08022fdc,0x08023078,0x08037494,0x080374d4,0x0802407a,0x0802409a,0x080240b6,0x080240c8):
   raise AssertionError(('reachable mutator/non-read request',hex(pc)))
  if pc==0x08023fa0 and self.task=='Main' and self.pause_submit:raise SubmitPaused()
  if pc==0x0801ce60:
   self.notification_targets.append((self.task,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)));self.ret()
  elif pc==0x0801cdc8:
   mask=u.reg_read(UC_ARM_REG_R1);fp=u.reg_read(UC_ARM_REG_R2)
   if not self.e.r32(fp)&mask:
    self.wait=dict(mask=hex(mask),flag_pointer=hex(fp));raise Blocked()
   self.ret() # OS endpoint only; actual holder flag is consumed by stock BE1A
  elif pc==0x08022f94:
   args=[u.reg_read(UC_ARM_REG_R0+i) for i in range(4)]
   assert self.task=='Storage' and args==[self.backend,0x82000,PAYLOAD,512],args
   self.reads.append(args)
  elif pc==CALLBACK:
   assert self.task=='Storage';rp=u.reg_read(UC_ARM_REG_R0);ud=u.reg_read(UC_ARM_REG_R1)
   assert bytes(u.mem_read(rp,24))==bytes(u.mem_read(REQ,24)) and ud==STATE
   assert self.e.r8(self.backend+8)==1 or self.e.r8(self.wrapper+24)==2
   self.callback_count+=1
  elif pc==0x080576b4:
   assert all(u.reg_read(r)==v for r,v in self.storage_registers.items())
   self.Storage_return_checks+=len(self.storage_registers)
  elif pc==0x08020c90:
   assert self.task=='Main';d=u.reg_read(UC_ARM_REG_R2);p,n=struct.unpack('<II',bytes(u.mem_read(d,8)))
   self.frames.append(bytes(u.mem_read(p,n)))
  elif pc==0x08024754:
   p=u.reg_read(UC_ARM_REG_R2);n=u.reg_read(UC_ARM_REG_R3)
   assert self.usb is None and 0<n<=64 and n%4==0
   self.usb=(bytes(u.mem_read(p,n)),self.ticks+self.usb_delay);self.ret()
  elif pc==0x0801be78:
   self.sleeps+=1;raise AssertionError('output called without adequate preflight; would block Main')
  elif pc==0x0801b3b8:self.ret()
 def write(self,u,access,a,n,v,d):
  assert not (0x08000000<=a<0x08080000),('flash write',hex(a))
  if a<PAYLOAD+512 and a+n>PAYLOAD:self.payload_cpu_writes+=1;raise AssertionError('CPU overwrite of DMA payload')
  if a==0xa0001014:
   assert v&255 in (0xeb,0xec) and (v>>26)&3==1,hex(v)
   self.commands.append(hex(v&255))
 def invoke(self,fn,*args,task='Main',prefix=128,registers=None):
  self.task=task
  if task!='IRQ':self.e.w32(self.kernel+0x64,self.storage if task=='Storage' else 0x2000835c)
  self.stage=task+'-'+hex(fn)
  self.u.reg_write(UC_ARM_REG_IPSR,108 if task=='IRQ' else 0)
  top=self.stack_bounds[task][1];self.u.reg_write(UC_ARM_REG_SP,top-prefix)
  before={r:0x12900000+r for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)}
  for r,v in before.items():self.u.reg_write(r,v)
  for r,v in (registers or {}).items():self.u.reg_write(r,v)
  if registers:before.update({r:v for r,v in registers.items() if r in before})
  if task=='Storage':self.storage_registers=before.copy()
  for i,v in enumerate(args):self.u.reg_write(UC_ARM_REG_R0+i,v)
  self.u.reg_write(UC_ARM_REG_LR,0x0807ff01)
  try:self.u.emu_start(fn|1,0xffffffff,count=2000000)
  except Blocked:
   assert task=='Storage';self.ctx=self.u.context_save();self.check();return 'blocked'
  except SubmitPaused:
   self.mainctx=self.u.context_save();self.check();return 'paused before pending increment'
  assert self.u.reg_read(UC_ARM_REG_PC)==0x0807ff00,hex(self.u.reg_read(UC_ARM_REG_PC))
  assert self.u.reg_read(UC_ARM_REG_SP)==top-prefix
  assert all(self.u.reg_read(r)==v for r,v in before.items())
  self.regchecks+=len(before);self.retchecks+=1;self.check();return self.u.reg_read(UC_ARM_REG_R0)
 def submit(self,token=37,data=None,port=0):
  b=request(token) if data is None else data;self.u.mem_write(0x20061100,b)
  self.u.mem_write(0x20061000,struct.pack('<II',0x20061100,len(b)))
  old=len(self.reads);result=self.invoke(0x0807a414,port,0x20061000,0)
  assert len(self.reads)==old,'Main must not enter backend'
  if self.mainctx is None:self.submission_returns+=1
  self.events.append(dict(stage='Main paused before pending increment' if self.mainctx else 'Main submit returned',state=self.flags()));return result
 def start_storage(self):
  # Captured callbacks already installed. Start at original event-loop boundary
  # with registers set exactly as the unchanged task prologue establishes.
  result=self.invoke(0x0805769c,task='Storage',prefix=24,registers={UC_ARM_REG_R4:self.holder,UC_ARM_REG_R5:0x2000696c,UC_ARM_REG_R6:0x20006968})
  self.events.append(dict(stage='Storage initial wait',wait=self.wait,state=self.flags()));return result
 def resume_storage(self):
  assert self.ctx is not None;self.task='Storage';self.stage='Storage-resume';self.u.context_restore(self.ctx)
  self.e.w32(self.kernel+0x64,self.storage);self.u.reg_write(UC_ARM_REG_IPSR,0)
  try:self.u.emu_start(self.u.reg_read(UC_ARM_REG_PC)|1,0xffffffff,count=2000000)
  except Blocked:self.ctx=self.u.context_save();self.events.append(dict(stage='Storage blocked',wait=self.wait,state=self.flags()));self.check();return
  raise AssertionError('Storage loop must reach original event wait')
 def irq(self,error=False):
  assert self.reads and self.e.r8(self.backend+8)==0
  assert self.e.r32(0xa0001018)==0x82000 and self.e.r32(0xa0001010)==511
  if not error:self.u.mem_write(PAYLOAD,self.payload) # opaque DMA model after real command setup
  self.e.w32(0xa0001008,1 if error else 2) # TEF-only versus TCF
  self.invoke(0x080573e0,task='IRQ',prefix=0)
  self.events.append(dict(stage='actual QSPI IRQ',error=error,state=self.flags()));self.resume_storage()
 def port_left(self):
  p=self.e.r32(self.port+16);return (int.from_bytes(self.u.mem_read(p+2,2),'little')-int.from_bytes(self.u.mem_read(p,2),'little'))&65535
 def tick(self,disconnect=False):
  self.ticks+=1;self.background_ticks+=1 # modeled runnable unrelated task opportunity, not audio execution
  if disconnect:self.u.mem_write(self.dev+0x274,b'\0');self.usb=None
  if self.usb is not None and self.ticks>=self.usb[1]:
   b=self.usb[0];self.usb=None;self.usb_bytes.append(b);self.invoke(0x0801e624,self.stream,task='IRQ',prefix=0)
  self.invoke(0x08035a50,self.port,prefix=40)
  phase=self.e.r32(STATE)
  # Host model of a future Main periodic callback. Not installed or ownership-qualified.
  if phase==2:
   if not self.e.r8(self.dev+0x274):
    self.e.w32(STATE,0);self.events.append(dict(stage='Main disconnected; cancel completed reply'))
   elif self.port_left()==0 and self.usb is None:self.invoke(SERVICE,prefix=56)
   else:self.busy_rejections+=1
  elif phase==3 and self.port_left()==0 and self.usb is None:self.e.w32(STATE,0)
  self.check()
 def finish(self,limit=300):
  for _ in range(limit):
   if self.e.r32(STATE)==0 and self.usb is None and not self.port_left():break
   self.tick()
  return self.e.r32(STATE)==0
 def verify(self,token=37,frame_start=0,usb_start=0):
  frames=self.frames[frame_start:];expected=synthetic_packets(token,self.payload);assert frames==expected
  rec=Receiver(token)
  for f in frames:rec.accept(f)
  assert rec.result()==self.payload
  raw=b''.join(self.usb_bytes[usb_start:]);decoded=bytearray()
  for i in range(0,len(raw),4):
   p=raw[i:i+4];n={4:3,5:1,6:2,7:3}[p[0]&15];decoded+=p[1:1+n]
  assert bytes(decoded)==b''.join(expected)
  assert self.e.r8(self.backend+8)==1 and self.queued()==0 and self.e.r8(self.wrapper+12)==0
  assert self.e.r32(self.holder+8)==0 and self.e.r32(0x20007758)==0
 def summary(self):
  return dict(state=self.flags(),reads=len(self.reads),QSPI_commands=self.commands,callbacks=self.callback_count,
   frames=len(self.frames),USB_transfers=len(self.usb_bytes),USB_bytes=sum(map(len,self.usb_bytes)),ticks=self.ticks,
   modeled_other_task_opportunities=self.background_ticks,output_backpressure_deferrals=self.busy_rejections,
   unexpected_sleep_calls=self.sleeps,canary_checks=self.guardchecks,callee_saved_register_checks=self.regchecks,
   minimum_SP={k:hex(v) for k,v in self.minsp.items()},
   remaining_bytes_to_low_guard={k:v-(self.stack_bounds[k][0]+4) for k,v in self.minsp.items()},
   modeled_usage_from_aligned_top={k:self.stack_bounds[k][1]-v for k,v in self.minsp.items()},
   stage_minimum_SP={k:hex(v) for k,v in self.stagesp.items()},Storage_worker_callee_saved_checks=self.Storage_return_checks,
   payload_CPU_writes=self.payload_cpu_writes,selected_call_edges=sorted(self.edges),visited_instruction_count=len(self.visited),
   notifications=[dict(context=t,TCB=hex(p),mask=hex(v)) for t,p,v in self.notification_targets],events=self.events)

def suite():
 results=[];assertions=0
 def check(name,condition):
  nonlocal assertions
  assert condition,name;assertions+=1
 m=Model();m.submit();check('one queued request and Main returned without acquiring backend',m.queued()==24 and not m.reads and m.e.r8(m.backend+8)==1)
 before=bytes(m.u.mem_read(STATE,0x380));m.submit(98);check('duplicate while queued does not replace request/token',m.queued()==24 and bytes(m.u.mem_read(STATE,0x380))==before)
 m.start_storage();check('Storage actual wait owns semaphore',m.wait['mask']=='0x100' and m.e.r8(m.backend+8)==0)
 m.irq();check('actual worker callback marks ready',m.e.r32(STATE)==2 and m.callback_count==1)
 before=bytes(m.u.mem_read(STATE,0x380));m.submit(97);check('duplicate after completion before output cannot reuse buffer',bytes(m.u.mem_read(STATE,0x380))==before)
 check('normal output drains',m.finish());m.verify();results.append(dict(case='normal',result='PROVEN',details=m.summary()))
 # Delayed IRQ, task switches, duplicate command, output backpressure, second request.
 m=Model();m.submit();m.start_storage();snapshot=bytes(m.u.mem_read(STATE,0x380));
 for _ in range(8):m.tick();m.resume_storage()
 m.submit(99);check('pending duplicate preserves owned record/payload',bytes(m.u.mem_read(STATE,0x380))==snapshot and len(m.reads)==1 and m.queued()==0)
 check('Main flag untouched during delayed DMA',m.e.r32(0x20007758)==0)
 m.irq();m.usb_delay=5;check('backpressured first request finishes',m.finish());m.verify()
 check('backpressure defers rather than sleeps in Main',m.busy_rejections>0 and m.sleeps==0)
 f=len(m.frames);b=len(m.usb_bytes);m.submit(38);m.resume_storage();m.irq();check('second request drains',m.finish());m.verify(38,f,b)
 check('two independent callbacks and reads',m.callback_count==2 and len(m.reads)==2)
 results.append(dict(case='delayed IRQ / switching / duplicate / MIDI backpressure / second request',result='PROVEN',details=m.summary()))
 m=Model();m.u.mem_write(m.backend+8,b'\0');m.submit();m.start_storage()
 check('busy backend rejected with status2 and no DMA',m.e.r32(STATE+4)==2 and not m.commands)
 m.tick();check('busy request no longer active; other owner semaphore preserved',m.e.r32(STATE)==0 and m.queued()==0 and m.e.r8(m.backend+8)==0 and m.callback_count==1)
 results.append(dict(case='backend busy',result='PROVEN',details=m.summary()))
 m=Model();m.submit();m.start_storage();m.tick(disconnect=True);check('disconnect does not reuse pending DMA buffer',m.e.r32(STATE)==1)
 m.irq();m.tick(disconnect=True);check('completed request canceled without output',m.e.r32(STATE)==0 and not m.frames and m.e.r8(m.backend+8)==1 and m.queued()==0)
 results.append(dict(case='host disappears while read active',result='PROVEN',details=m.summary()))
 m=Model();m.submit();m.start_storage();m.irq(error=True)
 check('TEF-only wakes Storage but no controller TCF; waits again',m.e.r32(STATE)==1 and m.wait['mask']=='0x100' and m.e.r32(0x20005550)&1==0 and m.e.r8(m.backend+8)==0 and m.callback_count==0)
 for _ in range(8):m.tick();m.resume_storage()
 check('error retains in-flight request and semaphore; no false reply',m.e.r32(STATE)==1 and m.e.r8(m.backend+8)==0 and not m.frames)
 results.append(dict(case='QSPI TEF-only completion error',result='PROVEN',required_no_deadlock_gate=False,details=m.summary()))
 m=Model();m.submit();m.start_storage()
 for _ in range(8):m.tick();m.resume_storage()
 check('missing IRQ has no added firmware timeout',m.e.r32(STATE)==1 and m.e.r8(m.backend+8)==0 and not m.frames)
 results.append(dict(case='missing IRQ observation',result='PROVEN',required_no_deadlock_gate=False,details=m.summary()))
 # Explicitly exercise the stock submit ordering: notification precedes pending
 # byte increment. Whether real scheduling permits this interleaving is UNKNOWN.
 m=Model();m.pause_submit=True;m.submit();check('notification occurs before pending increment',m.mainctx is not None and m.queued()==24 and m.e.r8(m.wrapper+12)==0)
 m.start_storage();check('early worker observes zero pending and returns to event wait',not m.reads and m.queued()==24 and m.e.r32(m.holder+8)==0)
 m.pause_submit=False;m.task='Main';m.stage='Main-resume-submit';m.u.context_restore(m.mainctx);m.e.w32(m.kernel+0x64,0x2000835c)
 m.u.emu_start(m.u.reg_read(UC_ARM_REG_PC)|1,0xffffffff,count=2000000)
 check('Main returns after late pending increment without second signal',m.u.reg_read(UC_ARM_REG_PC)==0x0807ff00 and m.e.r8(m.wrapper+12)==1 and m.e.r32(m.holder+8)==0)
 m.check();results.append(dict(case='preemption after submit notification before pending increment',result='STRONG INFERENCE',
  real_scheduler_permits_this_interleaving='UNKNOWN',details=m.summary()))
 m=Model();invalid=[]
 for at in list(range(6,23))+[23,230,231]:
  b=bytearray(request(37));b[at]^=1;invalid.append(bytes(b))
 invalid.extend([request(37)[:-1],request(37)+b'\0'])
 for cmd in range(128):
  if cmd==13:continue
  b=bytearray(request(37));b[4]=cmd;invalid.append(bytes(b))
 for b in invalid:
  m.submit(data=b);check('fixed-request validator refuses mutation',m.queued()==0 and m.e.r32(STATE)==0 and not m.reads)
 m.submit(port=1);check('focused fixture rejects non-USB input',m.queued()==0)
 results.append(dict(case='fixed-request negative mutations',result='PROVEN',negative_cases=len(invalid)+1,details=m.summary()))
 result=dict(confidence='PROVEN',scope='Actual stock storage/IRQ instructions with explicit emulator scheduler/peripheral and unqualified arena/service attachment',
  independent_scenarios=len(results),explicit_gate_assertions=assertions,cases=results,shims=m.shims,
  allocation='UNKNOWN on hardware; model 0x20060000 arena is outside physical SRAM',
  verdict='FAIL',reason='Normal queued completion corrected; TEF-only error and missing IRQ retain semaphore/request; buffer/service ownership unqualified',
  hardware_access=False,firmware_generated=False)
 (O/'replay-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
if __name__=='__main__':suite()
