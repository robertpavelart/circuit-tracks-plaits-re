"""Deterministic SPI2 8-bit master subset. No firmware readiness/state edits.

Clock progress is bounded in SR polls, not an assertion of silicon cycle timing.
Slave responses are supplied independently; never equate TXE with RX completion.
"""
from collections import deque
class SPI2:
 BASE=0x40003800
 def __init__(self,delay=3,complete=True,response=None):
  self.cr1=0;self.cr2=0;self.rx=deque();self.tx=deque();self.now=0;self.last_progress=0;self.delay=delay;self.complete=complete;self.response=response or (lambda b:0);self.errors=0;self.trace=[];self.accessors={};self.tx_bytes=[];self.rx_bytes=[]
  self.other={0x10:7,0x14:0,0x18:0,0x1c:0,0x20:2}
 def log(self,pc,rw,offset,value):
  key=(pc,rw,offset);entry=self.accessors.setdefault(key,dict(PC=hex(pc),access=rw,register=hex(self.BASE+offset),count=0,values=[]));entry['count']+=1
  if value not in entry['values'] and len(entry['values'])<16:entry['values'].append(value)
 def read(self,offset,size=4,pc=0):
  if offset==8:
   self.now+=1
   if self.complete and self.tx and self.tx[0][0]<=self.now and self.enabled():
    _,b=self.tx.popleft()
    if len(self.rx)>=4:self.errors|=64
    else:self.rx.append(self.response(b)&255)
   threshold=1 if self.cr2&4096 else 2
   value=(2 if len(self.tx)<=2 else 0)|(1 if len(self.rx)>=threshold else 0)|(128 if self.tx else 0)|self.errors
   value|=min(3,len(self.rx))<<9
   value|=min(3,len(self.tx))<<11
  elif offset==12:
   assert self.rx,'empty DR read outside qualified normal profile'
   value=self.rx.popleft()
   self.rx_bytes.append(value)
   self.last_progress=self.now
  elif offset==0:value=self.cr1
  elif offset==4:value=self.cr2
  elif offset in self.other:value=self.other[offset]
  else:raise AssertionError(('unmodeled SPI2 read',offset))
  self.log(pc,'R',offset,value);return value
 def enabled(self):return self.cr1&0x44==0x44 and not self.other[0x1c]&0x800
 def write(self,offset,value,size=4,pc=0):
  self.log(pc,'W',offset,value)
  if offset==0:self.cr1=value
  elif offset==4:self.cr2=value
  elif offset in (0x10,0x1c,0x20):self.other[offset]=value
  elif offset==12:
   assert size==1,('only observed 8-bit DR accesses qualified',size)
   assert (self.cr2>>8)&15==7 and self.cr2&4096,'only observed 8-bit FRXTH configuration qualified'
   if len(self.tx)>=4:raise AssertionError('TX FIFO overflow')
   self.tx.append((self.now+self.delay,value&255));self.tx_bytes.append(value&255)
   self.last_progress=self.now
  elif offset==8:
   # Hardware status bits are not software-owned; CRCERR clear excluded here.
   raise AssertionError('SPI2 SR write outside qualified normal subset')
  else:raise AssertionError(('unmodeled SPI2 write',offset))
 def bind(self,u):
  from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
  from unicorn.arm_const import UC_ARM_REG_PC
  def rd(u,ac,a,n,v,d):u.mem_write(a,self.read(a-self.BASE,n,u.reg_read(UC_ARM_REG_PC)).to_bytes(n,'little'))
  def wr(u,ac,a,n,v,d):self.write(a-self.BASE,v,n,u.reg_read(UC_ARM_REG_PC))
  u.hook_add(UC_HOOK_MEM_READ,rd,begin=self.BASE,end=self.BASE+0x23);u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=self.BASE,end=self.BASE+0x23)
 def summary(self):return dict(CR1=hex(self.cr1),CR2=hex(self.cr2),SR_polls=self.now,TX_hex=bytes(self.tx_bytes).hex(),RX_hex=bytes(self.rx_bytes).hex(),pending_TX=len(self.tx),pending_RX=len(self.rx),accessors=list(self.accessors.values()),scope='8-bit master subset, deterministic finite clock delay; no full slave/DSP behavior assertion')
