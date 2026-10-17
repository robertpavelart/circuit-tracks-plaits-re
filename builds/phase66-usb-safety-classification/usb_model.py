"""Narrow disconnected USB OTG HS initialization model; no bus packets or DMA."""
class USBModelGap(RuntimeError):pass
class USBInit:
 BASE=0x40040000
 def __init__(self,delay=3,idle=True,complete=True):
  self.delay=delay;self.idle=idle;self.complete=complete;self.reg={8:0,12:0,16:0,20:0,24:0};self.pending={};self.polls=0;self.trace=[];self.endpoint_DMA=[]
 def known(self,o):
  return o in(0,4,8,12,16,20,24,0x24,0x28,0x38,0x100,0x800,0x804,0x808,0x810,0x814,0x818,0x81c,0x828,0x82c,0x830,0x834,0x838,0x83c,0xe00) or 0x104<=o<=0x13c and not o%4 or (0x900<=o<0xd00 and o%0x20 in(0,4,8,0x10,0x14,0x18,0x1c))
 def record(self,pc,rw,o,v):
  self.trace.append(dict(PC=hex(pc),access=rw,address=hex(self.BASE+o),value=hex(v)))
 def read(self,o,n=4,pc=0):
  if n!=4 or not self.known(o):raise USBModelGap(f'USB read outside initialization subset: {self.BASE+o:08x},size{n},PC{pc:08x}')
  if o==16:
   self.polls+=1
   if self.complete:
    for flag in list(self.pending):
     if self.polls>=self.pending[flag]:self.reg[16]&=~flag;del self.pending[flag]
   v=(self.reg[16]&0x7fffffff)|(0x80000000 if self.idle else 0)
  else:v=self.reg.get(o,0)
  self.record(pc,'R',o,v);return v
 def write(self,o,v,n=4,pc=0):
  if n!=4 or not self.known(o):raise USBModelGap(f'USB write outside initialization subset: {self.BASE+o:08x},size{n},PC{pc:08x}')
  self.record(pc,'W',o,v)
  if o==8 and v&0x20:raise USBModelGap('USB internal DMA configuration is outside this initialization profile')
  if o==12 and v&0x20000000:raise USBModelGap('forced USB host mode is outside this device initialization profile')
  if o==16:
   self.reg[o]=v&0x7fffffff
   for flag in(1,0x10,0x20):
    if v&flag:self.pending[flag]=self.polls+self.delay
  elif o in(4,20,0x818) or 0x900<=o<0xd00 and o%0x20==8:self.reg[o]=self.reg.get(o,0)&~v
  else:self.reg[o]=v
  if 0x900<=o<0xd00 and o%0x20==0x14:self.endpoint_DMA.append(dict(register=hex(self.BASE+o),buffer=hex(v)))
  if 0x900<=o<0xd00 and o%0x20==0 and v&0x80000000:
   raise USBModelGap('endpoint activation requires USB bus/packet/DMA model; no memory transfer is fabricated')
 def bind(self,u):
  from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
  from unicorn.arm_const import UC_ARM_REG_PC
  u.mem_map(self.BASE,0x10000)
  def rd(u,ac,a,n,v,d):u.mem_write(a,self.read(a-self.BASE,n,u.reg_read(UC_ARM_REG_PC)).to_bytes(n,'little'))
  def wr(u,ac,a,n,v,d):self.write(a-self.BASE,v,n,u.reg_read(UC_ARM_REG_PC))
  u.hook_add(UC_HOOK_MEM_READ,rd,begin=self.BASE,end=self.BASE+0xffff);u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=self.BASE,end=self.BASE+0xffff)
 def summary(self):return dict(registers={hex(self.BASE+k):hex(v) for k,v in self.reg.items()},trace=self.trace,AHB_idle=self.idle,polls=self.polls,delay=self.delay,endpoint_DMA=self.endpoint_DMA,pending_reset_flush=self.pending,scope='disconnected initialization subset; finite reset/flush transitions; no host enumeration/packets/endpoint completion or memory DMA')
