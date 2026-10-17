"""New joint-path cases only. Native candidate; scheduler/USB/DMA seams explicit."""
from pathlib import Path
import sys,json,struct,importlib.util
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase63-defect-closure'))
import dma_regression as prior
from unicorn.arm_const import *
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_INVALID
image=(R/'builds/final-hardware-test-package/circuittracks-nor-defect-closure-development.bin').read_bytes()
class Joint(prior.M):
 def __init__(self,*args,**kwargs):
  self.bot_done=False;self.bot_usb=[];self.joint=[];self.host_reads=[];self.irqs=[]
  super().__init__(*args,**kwargs)
  assert bytes(self.u.mem_read(0x8010000,len(image)))==image
  self.bounds['BOT']=self.bounds['Main'] # One Main task, separate logical invocation.
  self.bounds['UI']=(0x200084dc,0x20008cd8) # saved allocated UI stack; helper-only
  self.out=self.e.r32(0x20006974);self.inp=self.e.r32(0x20006970)
  self.USB_BUF=0x40024000
  def fault(u,access,address,size,value,data):
   print('MODEL BOUNDARY',hex(u.reg_read(UC_ARM_REG_PC)),hex(address),self.task,[hex(u.reg_read(UC_ARM_REG_R0+i)) for i in range(4)],bytes(u.mem_read(0x2000679c,31)).hex());return False
  self.u.hook_add(UC_HOOK_MEM_INVALID,fault)
 def code(self,u,pc,n,d):
  if pc==0x8070cb8:
   assert not (self.e.r32(0x400264b8)&1) and self.e.r32(0x400264bc)==0
   assert self.e.r32(self.wrapper+16)==0 and self.e.r8(self.backend+8)==1
   self.raw_finished=True;self.guards_ready=False # lease ends at native POP, even INVALID
  if pc==0x801a7e4 and self.task=='BOT':
   at=u.reg_read(UC_ARM_REG_R0);size=u.reg_read(UC_ARM_REG_R1)
   assert at==self.USB_BUF and size==4096
   u.mem_write(at,bytes(size));self.ret(at);return # exact bounded clear semantics
  if pc==0x8022f94 and u.reg_read(UC_ARM_REG_R2)==self.USB_BUF:
   a=[u.reg_read(UC_ARM_REG_R0+i) for i in range(4)]
   assert self.task=='Storage' and a==[self.backend,0xd4000,self.USB_BUF,4096]
   assert self.active is None
   self.host_reads.append(dict(address=hex(a[1]),buffer=hex(a[2]),bytes=a[3]))
   self.active=dict(chunk=-1,owner='BOT',due=self.ticks+2,issued=False);return
  if pc==0x8037596 and self.active and self.active.get('owner')=='BOT':
   assert self.e.r32(0xa0001018)==0xd4000 and self.e.r32(0x400264bc)==4096
   assert self.e.r32(0x400264c4)==self.USB_BUF;return
  if pc==0x8024754 and self.task=='BOT':
   at=u.reg_read(UC_ARM_REG_R2);size=u.reg_read(UC_ARM_REG_R3)
   self.bot_usb.append(dict(buffer=hex(at),bytes=size));self.ret();return
  if pc==0x802478c and self.task=='BOT':self.ret(31);return # supplied CBW reception
  if self.task=='IRQ' and pc in (0x8024770,0x80246a8,0x80246c4,0x8024668,0x803b7d4,0x803b7a8,0x8024808):
   self.irqs.append(dict(boundary=hex(pc)));self.ret();return
  return super().code(u,pc,n,d)
 def irq(self,kind='normal'):
  if self.active and self.active.get('owner')=='BOT':
   assert not self.active['issued'];self.active['issued']=True
   if kind=='missing':self.e.w32(0xa0001008,0x20);return
   if kind=='normal':
    self.u.mem_write(self.USB_BUF,b'B'*4096);self.e.w32(0x400264bc,0);self.e.w32(0x400264b8,self.e.r32(0x400264b8)&~1);self.e.w32(0xa0001008,2)
   else:self.e.w32(0xa0001008,1)
   self.run_cpu('IRQ',0x80573e0,SP=0x20050000,LR=0x807ff01);return
  return super().irq(kind)
 def helper(self,pc,*args,role='IRQ'):
  ctx=self.u.context_save();task=self.task
  try:
   self.task=role;self.u.reg_write(UC_ARM_REG_IPSR,77+16 if role=='IRQ' else 0)
   self.e.call(pc,*args,sp=0x2004ff00 if role=='IRQ' else 0x20008c60,maxins=200000)
  finally:self.u.context_restore(ctx);self.task=task
 def post_cbw(self):
  # Native BOT admission consumes the same static CBW as the completed OUT transfer.
  b=bytearray(31);b[:4]=b'USBC';struct.pack_into('<II',b,4,0x504839,4096);b[12]=0x80;b[14]=10;b[15]=0x28;b[17:21]=(64).to_bytes(4,'big');b[22:24]=(1).to_bytes(2,'big')
  self.u.mem_write(0x2000679c,bytes(b));self.u.mem_write(0x200068d4,b'\0')
  self.e.w32(0x2000689c,4096);self.e.w32(0x200068a0,8192)
  self.e.call(0x8038c10,1,sp=0x200082d8) # existing normal base94000 mode, no hardware
  assert self.e.r32(0x200037c0)==0x8038c3c
  self.helper(0x801e6cc,self.out) # real OUT-completion leaf posts endpoint flag
  self.joint.append(dict(event='USB OUT completion posted',QSPI_commands=len(self.commands)))
 def start_bot(self):
  assert not self.frame or self.done,'Main cannot invoke BOT while its diagnostic frame is suspended'
  self.run_cpu('BOT',0x801f37c,SP=0x200082d8,LR=0x807ff01)
  self.bot_done=self.u.reg_read(UC_ARM_REG_PC)==0x807ff00
 def bot_tick(self,kind='normal'):
  self.ticks+=1
  if self.active and not self.active['issued'] and self.ticks>=self.active['due']:self.irq(kind)
  if not self.storage_started:self.start_worker()
  else:self.run_cpu('Storage',resume=True)
  if not self.bot_done:
   self.run_cpu('BOT',resume=True);self.bot_done=self.u.reg_read(UC_ARM_REG_PC)==0x807ff00
  self.check()
 def reset(self,kind):
  before=bytes(self.u.mem_read(0x20044d70,12));owners=(self.e.r32(0x400264b8),self.e.r32(0x400264bc),self.e.r32(self.wrapper+16),self.e.r8(self.backend+8))
  if kind=='BOT reset':
   # Valid class reset packet: type21 requestFF, wValue/index/length zero.
   self.u.mem_write(0x2004ffc0,struct.pack('<BBHHH',0x21,0xff,0,0,0));self.helper(0x8058ecc,self.dev,0x2004ffc0)
  elif kind=='class reset':self.helper(0x8037f46,self.dev,0)
  elif kind=='disconnect':self.u.mem_write(self.dev+0x274,b'\0') # bus-event state boundary
  elif kind=='remount':self.helper(0x806cf00,0x20000ab0,role='UI') # native invalidation; caller scheduling is a seam
  afterowners=(self.e.r32(0x400264b8),self.e.r32(0x400264bc),self.e.r32(self.wrapper+16),self.e.r8(self.backend+8))
  assert owners==afterowners,(kind,owners,afterowners)
  if kind!='remount':assert bytes(self.u.mem_read(0x20044d70,12))==before
  self.joint.append(dict(event=kind,record=bytes(self.u.mem_read(0x20044d70,12)).hex(),owners_unchanged=True))
def main():
 rows=[]
 def save(name,m,**extra):
  rows.append(dict(case=name,passed=True,host_reads=m.host_reads,diagnostic_reads=m.reads,joint=m.joint,state=m.state(),BOT_returned=m.bot_done,**extra));persist()
 def persist():(O/'joint-results.json').write_text(json.dumps(dict(candidate_sha256='edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9',cases=rows,passed=all(x['passed'] for x in rows),seams=['prepared exported-geometry fixture','cooperative scheduling of one Main actor and Storage','synthetic CBW/DMA/USB boundaries; no enumeration'],hardware_access=False),indent=2)+'\n')
 # A: BOT service already executing in Main. It must return before parser can run.
 for fault in ('normal','missing','tef'):
  m=Joint();m.post_cbw();m.start_bot()
  for _ in range(30):
   if m.bot_done:break
   m.bot_tick(fault)
  if fault=='normal':
   assert m.bot_done and len(m.host_reads)==1 and not m.reads
   m.start();assert m.finish(1500);assert len(m.commands)==10;save('A BOT then diagnostic normal',m)
  else:
   assert not m.bot_done and m.frame is None and not m.reads and len(m.commands)==1
   save('A BOT '+fault+' blocks Main before diagnostic',m)
   m.active['issued']=False;m.irq('normal')
   for _ in range(30):
    if m.bot_done:break
    m.bot_tick()
   assert m.bot_done and len(m.commands)==1;save('A BOT '+fault+' late completion no diagnostic auto-call',m)
 for event in ('disconnect','timeout','remount','BOT reset','class reset'):
  m=Joint();m.post_cbw();m.start_bot()
  for _ in range(12):m.bot_tick('missing')
  assert not m.bot_done and m.active and not m.frame
  if event=='timeout':prior.timer(m)
  else:m.reset(event)
  assert len(m.commands)==1 and not m.reads and not m.frame
  save('A BOT pending '+event+' no diagnostic entry',m)
  m.active['issued']=False;m.irq('normal')
  for _ in range(30):
   if m.bot_done:break
   m.bot_tick()
  assert m.bot_done and len(m.commands)==1 and not m.reads
  save('A BOT '+event+' late completion does not launch diagnostic',m)
 # B: normal OUT can complete while Main is suspended in diagnostic, but BOT
 # media service is a later call in that SAME Main task.
 for event in ('pending only','disconnect','timeout','missing','tef','remount','BOT reset','class reset'):
  m=Joint('missing',0);m.start();assert not m.finish(12) and m.active
  n=len(m.commands);buf=m.rawbuf;m.post_cbw();assert len(m.commands)==n and not m.host_reads
  if event in ('disconnect','remount','BOT reset','class reset'):m.reset(event)
  if event=='tef':m.active['issued']=False;m.irq('tef')
  if event in ('timeout','missing','tef','disconnect'):prior.timer(m)
  assert not m.finish(8) and not m.done and not m.host_reads and m.rawbuf==buf
  save('B diagnostic pending plus BOT '+event,m)
  m.fail_kind=None;m.active['issued']=False;m.irq('normal')
  assert m.finish(1500) and not m.host_reads
  if event in ('timeout','missing','tef','disconnect','remount'):assert m.e.r32(0x20044d70)!=0x14
  # Deferred endpoint media work has still not been serviced by another task.
  save('B late diagnostic completion plus BOT '+event,m)
  if event in ('pending only','timeout','missing','tef','remount'):
   before=len(m.commands);m.start_bot()
   for _ in range(30):
    if m.bot_done:break
    m.bot_tick()
   assert m.bot_done and len(m.host_reads)==1 and len(m.commands)==before+1
   assert m.e.r32(0x400264bc)==0 and m.e.r8(m.backend+8)==1
   save('B deferred BOT media read only after diagnostic frame return '+event,m)
 print('New joint cases',len(rows))
if __name__=='__main__':main()
