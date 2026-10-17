"""Physical SRAM only: live-frame eight-chunk stock-wrapper experiment.
Peripherals/RTOS switches modeled explicitly; never supplies original bytes.
"""
from stream import *
from unicorn import UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
# Phase42 imports its local fixed-evidence protocol.
from evidence_protocol import request,Receiver,synthetic_packets,crc32,n32,packet
class Pause(Exception):pass
class Model:
 def __init__(self,fail_kind=None,fail_chunk=None,delay=2,interleave=False):
  self.e=Physical();self.u=u=self.e.uc;self.shims=load(u)
  self.task='Main';self.contexts={};self.waits={};self.done=False;self.storage_started=False
  self.fail_kind=fail_kind;self.fail_chunk=fail_chunk;self.delay=delay;self.ticks=0;self.active=None;self.injected=False
  self.interleave=interleave
  self.minsp={};self.events=[];self.reads=[];self.frames=[];self.usb_bytes=[];self.usb=None;self.frame=None;self.guards_ready=False
  self.commands=[];self.MMIO=[];self.guardchecks=0;self.regchecks=0;self.yields={};self.deferred_duplicate=0
  self.payload=bytes(((i*73)^(i>>1)^0xa6)&255 for i in range(535));self.token=37
  self.bounds={'Main':(0x2000775c,0x20008358),'Storage':(0x20008d44,0x20009240),'IRQ':(0x2004f000,0x20050000)}
  self.kernel=w(0x0801cf90);self.wrapper=self.e.r32(0x20006968);self.backend=self.e.r32(self.wrapper+4)
  self.holder=self.e.r32(0x20006790);self.storage=self.e.r32(self.holder);self.queue=self.e.r32(self.wrapper+8)
  self.router=self.e.r32(w(0x0801edd0));self.port=self.e.r32(self.e.r32(self.router+20));self.pipe=self.e.r32(self.port+20)
  self.stream=self.e.r32(self.e.r32(self.pipe+4)+4);self.dev=self.e.r32(self.stream+16)
  self.parser=self.e.r32(self.e.r32(0x200068b0+12));self.input_desc=self.e.r32(self.parser+36);self.input_buf=self.e.r32(self.input_desc+4)
  self.unused_input=bytes(u.mem_read(self.input_buf+232,128))
  assert self.e.r32(self.parser+16)==360 and 0x20000000<=self.input_buf<0x20050000-360
  u.mem_write(self.dev+0x274,b'\3');u.mem_write(self.stream+12,b'\0')
  ctx=self.e.r32(self.backend+4)
  self.e.call(0x080226a2,self.e.r32(ctx))
  self.e.call(0x0801beb0,self.e.r32(ctx+20))
  self.peripheral_setup=dict(QSPI_CR=hex(self.e.r32(0xa0001000)),QSPI_DCR=hex(self.e.r32(0xa0001004)),DMA_CR=hex(self.e.r32(0x400264b8)),DMA_PAR=hex(self.e.r32(0x400264c0)),
   routines=['0x080226a2','0x0801beb0'])
  # Execute retained B1.3 lazy reservation, not an artificial heap-limit edit.
  self.retained_state=self.e.call(0x0805dbcc)
  assert self.retained_state==0x20044d7c and self.e.r32(0x20002b44)-self.e.r32(0x20002b48)==8
  self.retained_bytes=bytes(u.mem_read(self.retained_state,220));self.IRQ_bytes=bytes(u.mem_read(0x080573e0,14))
  for name in ('Main','Storage'):
   lo,hi=self.bounds[name];u.mem_write(lo,b'LOW!');u.mem_write(hi,b'HIGH')
  self.visited=set();self.edges=set();self.notification=[];self.read_ownership=[];self.pending_owner=None
  self.raw_cpu_reads=0;self.raw_cpu_writes=0;self.status_after_failure=None;self.restoration_writes=0
  self.reconstruction=None
  u.hook_add(UC_HOOK_CODE,self.code);u.hook_add(UC_HOOK_MEM_WRITE,self.write);u.hook_add(UC_HOOK_MEM_READ,self.read,begin=self.input_buf+RAW,end=self.input_buf+RAW+63)
 def ret(self,v=0):self.u.reg_write(UC_ARM_REG_R0,v);self.u.reg_write(UC_ARM_REG_PC,self.u.reg_read(UC_ARM_REG_LR)|1)
 def queued(self):
  q=self.queue;n=int.from_bytes(self.u.mem_read(q+4,2),'little');a=int.from_bytes(self.u.mem_read(q+6,2),'little');b=int.from_bytes(self.u.mem_read(q+8,2),'little');return (a-b)%n
 def left(self):
  p=self.e.r32(self.port+16);return (int.from_bytes(self.u.mem_read(p+2,2),'little')-int.from_bytes(self.u.mem_read(p,2),'little'))&65535
 def state(self):
  return dict(Main_returned=self.done,semaphore=self.e.r8(self.backend+8),queue_bytes=self.queued(),pending=self.e.r8(self.wrapper+12),sync=self.e.r32(self.wrapper+16),
   Main_flags=hex(self.e.r32(0x20007758)),Storage_flags=hex(self.e.r32(self.holder+8)),controller=hex(self.e.r32(0x20005550)),
   QSPI_SR=hex(self.e.r32(0xa0001008)),QSPI_CR=hex(self.e.r32(0xa0001000)),DMA_CR=hex(self.e.r32(0x400264b8)),DMA_NDTR=self.e.r32(0x400264bc),
   active_chunk=self.active['chunk'] if self.active else None,frames=len(self.frames),buffer_reusable=self.done and self.active is None)
 def check(self):
  if self.guards_ready and not self.done:
   for off in GUARDS:assert self.e.r32(self.frame+off)==0x30ca0000+off,('guard',off)
   for off in (-4,64):assert self.e.r32(self.input_buf+RAW+off)==0x30ca0000+RAW+off,('raw guard',off)
  for name in ('Main','Storage'):
   lo,hi=self.bounds[name];assert bytes(self.u.mem_read(lo,4))==b'LOW!' and bytes(self.u.mem_read(hi,4))==b'HIGH'
  assert bytes(self.u.mem_read(self.retained_state,220))==self.retained_bytes
  assert bytes(self.u.mem_read(self.input_buf+232,128))==self.unused_input,'outside serialized request ownership'
  assert bytes(self.u.mem_read(0x080573e0,14))==self.IRQ_bytes and self.e.r32(0x20006790)==self.holder
  self.guardchecks+=1
 def read(self,u,access,a,n,v,d):
  assert not 0x20050000<=a<0x40000000,('nonphysical SRAM read',hex(a))
  if self.frame and a<self.input_buf+RAW+64 and a+n>self.input_buf+RAW:
   assert self.active is None and self.task=='Main','raw CPU read before DMA completion'
   self.raw_cpu_reads+=1
 def write(self,u,access,a,n,v,d):
  assert not 0x20050000<=a<0x40000000,('nonphysical SRAM write',hex(a))
  assert not 0x08000000<=a<0x08080000,('CPU flash write',hex(a))
  if self.frame and a<self.input_buf+RAW+64 and a+n>self.input_buf+RAW:
   if self.restoring:self.restoration_writes+=1;return
   self.raw_cpu_writes+=1;raise AssertionError('CPU overwrite of live raw payload')
  if a==0xa0001014:
   assert v&255 in (0xeb,0xec) and (v>>26)&3==1
   self.commands.append(hex(v&255))
  if a==0xa000100c:
   self.e.w32(0xa0001008,self.e.r32(0xa0001008)&~v) # modeled W1C peripheral response
  if a in (0xa0001000,0xa000100c,0x400264b8,0x400264bc,0x400264c4):self.MMIO.append(dict(task=self.task,address=hex(a),value=hex(v)))
 def code(self,u,pc,n,d):
  sp=u.reg_read(UC_ARM_REG_SP);self.minsp[self.task]=min(sp,self.minsp.get(self.task,sp))
  lo,hi=self.bounds[self.task];assert lo+4<=sp<=hi,('stack',self.task,hex(pc),hex(sp))
  if pc not in self.visited:
   self.visited.add(pc);i=next(md.disasm(bytes(u.mem_read(pc,n)),pc),None)
   if i and i.mnemonic in ('bl','blx','b.w'):self.edges.add((hex(pc),i.mnemonic,i.op_str))
  if pc in (0x08022fdc,0x08023078,0x08037494,0x080374d4,0x0802407a,0x0802409a,0x080240b6,0x080240c8):raise AssertionError(('mutator/nonread dispatch',hex(pc)))
  if pc==0x08023fa0 and self.task=='Main' and self.interleave:
   self.interleave=False;self.waits['Main']=dict(kind='forced preemption after first notify');raise Pause()
  if pc==0x08047c6c and self.task=='Main':
   self.frame=u.reg_read(UC_ARM_REG_R7)
   assert self.bounds['Main'][0]+4<self.frame and self.frame+FRAME<self.bounds['Main'][1]-128
  if COMMAND<=pc<COMMAND+0x300 and self.task=='Main' and u.reg_read(UC_ARM_REG_R1)==TEMPLATE:
   assert self.active is None;self.restoring=True
  if pc==0x0801ce60:
   self.notification.append((self.task,hex(u.reg_read(UC_ARM_REG_R0)),hex(u.reg_read(UC_ARM_REG_R1))));self.ret()
  elif pc==0x0801cdc8:
   mask=u.reg_read(UC_ARM_REG_R1);fp=u.reg_read(UC_ARM_REG_R2)
   if not self.e.r32(fp)&mask:self.waits[self.task]=dict(kind='task flag',mask=hex(mask),flag_pointer=hex(fp),timeout_argument=hex(u.reg_read(UC_ARM_REG_R3)));raise Pause()
   self.ret() # only when actual IRQ/event flag store already occurred
  elif pc==0x0801be60:
   self.waits[self.task]=dict(kind='stock scheduler yield');raise Pause()
  elif pc==0x08022f94:
   args=[u.reg_read(UC_ARM_REG_R0+i) for i in range(4)];chunk=len(self.reads)
   assert self.task=='Storage' and 0<=chunk<9 and args==[self.backend,0x81000 if chunk==0 else 0x82000+(chunk-1)*64,self.input_buf+RAW,23 if chunk==0 else 64]
   assert self.active is None and self.left()==0 and self.usb is None,'reuse before prior packet release'
   self.guards_ready=True;self.check()
   self.reads.append(dict(chunk=chunk,address=hex(args[1]),destination=hex(args[2]),length=23 if chunk==0 else 64))
   self.active=dict(chunk=chunk,due=self.ticks+self.delay,issued=False)
  elif pc==0x08022fcc:
   self.active=None # busy return never acquired semaphore / started DMA
  elif pc==0x08022fd4:
   assert self.task=='Storage';self.read_ownership.append(dict(stage='actual backend release',state=self.state()));self.active=None
  elif pc==0x08037596:
   assert self.task=='Storage'
   assert self.e.r32(0xa0001018)==(0x81000 if self.active['chunk']==0 else 0x82000+(self.active['chunk']-1)*64) and self.e.r32(0xa0001010)==(22 if self.active['chunk']==0 else 63)
   assert self.e.r32(0x400264c4)==self.input_buf+RAW and self.e.r32(0x400264bc)==(23 if self.active['chunk']==0 else 64)
  elif pc==0x08020c90:
   assert self.task=='Main' and self.active is None and self.e.r8(self.backend+8)==1
   p=u.reg_read(UC_ARM_REG_R2);bp,n=struct.unpack('<II',bytes(u.mem_read(p,8)))
   assert bp==self.frame+PACKET;self.frames.append(bytes(u.mem_read(bp,n)))
  elif pc==0x08024754:
   p=u.reg_read(UC_ARM_REG_R2);n=u.reg_read(UC_ARM_REG_R3)
   assert self.usb is None and 0<n<=64 and n%4==0
   self.usb=(bytes(u.mem_read(p,n)),self.ticks+self.delay);self.ret()
  elif pc==0x0801be78:
   raise AssertionError('unexpected blocking router sleep; pre-drain should prevent it')
  elif pc==0x0801b3b8:self.ret()
 def run_cpu(self,task,pc=None,resume=False,**regs):
  self.task=task
  if task!='IRQ':self.e.w32(self.kernel+100,self.storage if task=='Storage' else 0x2000835c)
  self.u.reg_write(UC_ARM_REG_IPSR,108 if task=='IRQ' else 0)
  if resume:
   self.u.context_restore(self.contexts[task]);self.u.reg_write(UC_ARM_REG_IPSR,0)
   pc=self.u.reg_read(UC_ARM_REG_PC)|1
   if self.waits[task]['kind']=='stock scheduler yield':
    self.ret();pc=self.u.reg_read(UC_ARM_REG_PC)|1
  else:
   for name,v in regs.items():self.u.reg_write(globals()['UC_ARM_REG_'+name],v)
  try:self.u.emu_start(pc|1,0xffffffff,count=2000000)
  except Pause:
   self.contexts[task]=self.u.context_save();self.yields[task]=self.yields.get(task,0)+1;self.check();return
  assert self.u.reg_read(UC_ARM_REG_PC)==0x0807ff00,hex(self.u.reg_read(UC_ARM_REG_PC))
  if task=='Main':
   self.done=True
   if self.frame is not None:assert getattr(self,'handler_return_verified',False),'handler restoration was not witnessed before parser reuse'
   assert self.u.reg_read(UC_ARM_REG_SP)==0x200082d8
   assert all(self.u.reg_read(r)==v for r,v in self.mainregs.items());self.regchecks+=len(self.mainregs)
  self.check()
 def start(self,token=37,data=None,port=0):
  assert self.active is None;self.done=False;self.token=token;self.frame=None;self.guards_ready=False;self.restoring=False
  self.expected_input=request(token) if data is None else data
  self.task='Main';self.e.w32(self.kernel+100,0x2000835c);self.u.reg_write(UC_ARM_REG_IPSR,0)
  for byte in self.expected_input:parsed=self.e.call(0x08035c58,self.parser,byte,sp=0x200082f0)
  assert parsed==2,'stock parser did not complete the request'
  self.input_desc=self.e.r32(self.parser+36);assert self.e.r32(self.input_desc+4)==self.input_buf
  assert int.from_bytes(self.u.mem_read(self.input_desc,2),'little')==len(self.expected_input)
  assert bytes(self.u.mem_read(self.input_buf,len(self.expected_input)))==self.expected_input
  # This is the actual input-service frame descriptor location above callback SP.
  self.message=0x200082f0;self.u.mem_write(self.message,struct.pack('<II',self.input_buf,len(self.expected_input)))
  self.mainregs={r:0x30ab0000+r for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)}
  for r,v in self.mainregs.items():self.u.reg_write(r,v)
  self.run_cpu('Main',0x0801eb30,R0=port,R1=self.message,R2=0,SP=0x200082d8,LR=0x0807ff01)
 def start_worker(self):
  self.storage_started=True
  self.run_cpu('Storage',0x0805769c,R4=self.holder,R5=0x2000696c,R6=0x20006968,SP=0x20009240-24,LR=0x0807ff01)
 def irq(self,kind='normal'):
  assert self.active and not self.active['issued'];self.active['issued']=True
  k=self.active['chunk']
  if kind=='normal':
   assert self.e.r32(0xa0001000)&1 and self.e.r32(0x400264b8)&1 and not self.e.r32(0x400264b8)&0x100
   begin=0 if k==0 else 23+(k-1)*64;length=23 if k==0 else 64
   self.u.mem_write(self.input_buf+RAW,self.payload[begin:begin+length]);self.e.w32(0x400264bc,0)
   self.e.w32(0x400264b8,self.e.r32(0x400264b8)&~1) # normal-mode DMA auto-disables on completion
   self.e.w32(0xa0001008,2) # TCF; opaque DMA supplied exactly 64 bytes
  elif kind=='tef':self.e.w32(0xa0001008,1)
  elif kind=='missing':self.e.w32(0xa0001008,0x20);return
  self.run_cpu('IRQ',0x080573e0,SP=0x20050000,LR=0x0807ff01)
  self.events.append(dict(stage=kind+' IRQ',chunk=k,state=self.state()))
 def tick(self,disconnect_after=None,duplicate=False):
  self.ticks+=1
  if duplicate:
   # Main is parked inside its handler; normal Main dispatcher cannot re-enter.
   # Record host-side pending input, do not overwrite its live parser buffer.
   self.deferred_duplicate+=1
  if self.usb is not None and self.ticks>=self.usb[1]:
   b=self.usb[0];self.usb=None;self.usb_bytes.append(b)
   self.run_cpu('IRQ',0x0801e624,R0=self.stream,SP=0x20050000,LR=0x0807ff01)
  if disconnect_after is not None and len(self.frames)==disconnect_after+1 and self.left()==0 and self.usb is None:
   self.u.mem_write(self.dev+0x274,b'\0')
  if self.active and not self.active['issued'] and self.ticks>=self.active['due']:
   k=self.active['chunk'];kind=self.fail_kind if k==self.fail_chunk else 'normal';self.irq(kind or 'normal')
  if not self.storage_started:self.start_worker()
  else:self.run_cpu('Storage',resume=True)
  if not self.done:self.run_cpu('Main',resume=True)
  self.check()
 def finish(self,max_ticks=500,disconnect_after=None,duplicate=False):
  for _ in range(max_ticks):
   if self.done:return True
   self.tick(disconnect_after=disconnect_after,duplicate=duplicate and self.ticks==1)
   if self.injected:pass
   if self.fail_kind and self.active and self.active['issued'] and self.active['chunk']==self.fail_chunk:
    # bounded observer only; it never cancels/unwinds a live request
    for _ in range(16):self.tick()
    return False
  return self.done
 def verify(self,token=37,fs=0,us=0):
  expected=synthetic_packets(token,self.payload);assert self.frames[fs:]==expected
  receiver=Receiver(token)
  for f in self.frames[fs:]:receiver.accept(f)
  assert receiver.result()==self.payload
  raw=b''.join(self.usb_bytes[us:]);decoded=bytearray()
  for i in range(0,len(raw),4):
   p=raw[i:i+4];decoded+=p[1:1+{4:3,5:1,6:2,7:3}[p[0]&15]]
  assert bytes(decoded)==b''.join(expected)
  assert self.e.r8(self.backend+8)==1 and self.queued()==0 and self.e.r32(self.wrapper+16)==0 and self.active is None
  self.reconstruction=dict(confidence='PROVEN',origin='SYNTHETIC test bytes, not device evidence',bytes=535,sha256=sha(receiver.result()),
   packet_crc_and_whole_crc=True,exact_concatenation=True,target_filename='535-byte synthetic transaction',file_written=False)
 def summary(self):
  return dict(state=self.state(),reads=self.reads,QSPI_commands=self.commands,frames=len(self.frames),USB_transfers=len(self.usb_bytes),
   USB_bytes=sum(map(len,self.usb_bytes)),ticks=self.ticks,yields=self.yields,guard_checks=self.guardchecks,callee_saved_checks=self.regchecks,
   minimum_SP={k:hex(v) for k,v in self.minsp.items()},stack_usage={k:self.bounds[k][1]-v for k,v in self.minsp.items()},
   headroom_to_guard={k:v-self.bounds[k][0]-4 for k,v in self.minsp.items()},Main_frame=hex(self.frame) if self.frame else None,
   payload=hex(self.input_buf+RAW),input_parser=hex(self.parser),input_allocation=hex(self.input_buf),input_capacity=360,packet=hex(self.frame+PACKET) if self.frame else None,
   deferred_host_duplicates=self.deferred_duplicate,events=self.events,MMIO_trace=self.MMIO,notification_targets=self.notification,
   raw_CPU_reads=self.raw_cpu_reads,raw_CPU_writes=self.raw_cpu_writes,last_waits=self.waits,after_failure_before_second_request=self.status_after_failure,
   raw_region_restoration_writes=self.restoration_writes,stock_input_restored=self.done,
   reconstruction=self.reconstruction,
   constrained_call_edges=sorted(self.edges),retained_B13_heap_state_unchanged=True,
   actual_stock_peripheral_setup=self.peripheral_setup,
   nonphysical_memory_mapped=False,original_QSPI_bytes_used=False)


