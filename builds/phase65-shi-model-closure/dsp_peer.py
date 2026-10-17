"""Specific startup SHI wire abstraction. Native DSP, not constant idle replies."""
import hashlib
from native_dsp import NativeDSP
class UnknownPeerRead(RuntimeError):pass
class BootPeer:
 def __init__(self,native_factory=NativeDSP):
  self.marker=False;self.read=None;self.log=[];self.core=0;self.command=False;self.htx=0;self.pointer=0;self.space='X';self.memory={'X':{},'Y':{0x2c:0x800000}};self.width=3;self.frame=[];self.reply=[];self.lr=0;self.native=None;self.factory=native_factory;self.jobs=[];self.dmas=[];self.polls=0
 def arm_write(self,core,value,address):pass # observation of intent never commits a transfer
 def arm_read(self,core,address):self.read=(core,address)
 def word(self,a,b,c,lr):self.lr=lr # actual clocked bytes, not arguments, form the word
 def read_word(self):
  if self.core!=0:raise UnknownPeerRead('core1 SHI read outside startup subset')
  if self.native:
   if self.space=='Y' and self.pointer==0x2c:
    self.native.turn();self.polls+=1
    if self.polls>2000:raise UnknownPeerRead('native DSP mailbox has not completed within2000 observed polls')
   value=self.native.read(self.space,self.pointer)
  elif self.space=='Y' and self.pointer in(0x2b,0x2c):value=int(self.marker) if self.pointer==0x2b else 0x800000
  else:value=None
  self.log.append(dict(event='SHI read',space=self.space,address=hex(self.pointer),value=None if value is None else hex(value)))
  self.pointer+=1;return value
 def commit(self,word,cmd):
  if self.core!=0:raise UnknownPeerRead('core1 SHI transfer outside startup subset')
  if cmd:
   if word&(1<<21):
    assert word in(0x200000,0x200100),hex(word)
    self.log.append(dict(event='SHI width',word=hex(word),old_bytes=self.width,new_bytes=2 if word&256 else 3))
    if self.native:
     self.native.write('X',0x12,word);self.native.turn()
     assert self.native.read('X',0x12)==word&~(1<<21),'width command pending bit not consumed by native main loop'
    self.width=2 if word&256 else 3;return
   if word&(1<<22):self.htx=self.read_word();return
   if word&(1<<20):self.pointer=((word<<8)-2)&0xffffff;return
   if word&(1<<19):self.pointer=word&0x3ffff
   else:self.pointer=word&0x7fff;self.space='Y' if word&0x8000 else 'X'
   if word&0x800000:self.htx=self.read_word()
  else:
   self.memory[self.space][self.pointer]=word
   if self.space=='X' and self.pointer==0xfff:self.marker=word!=0
   if self.native:self.native.write(self.space,self.pointer,word)
   if self.space=='Y' and self.pointer==0x2c:
    if not self.native:
     self.native=self.factory(self.memory);self.native.write('Y',0x2c,word)
    self.jobs.append(word);self.polls=0;self.log.append(dict(event='mailbox job',word=hex(word)))
   self.pointer+=1
 def byte(self,tx):
  if not self.frame:
   if self.htx is None and self.lr==0x08029512:raise UnknownPeerRead('unknown consumed SHI read')
   self.reply=list((self.htx or 0).to_bytes(3,'big'))[:self.width]
   self.frame_cmd=self.command;self.frame_width=self.width
  value=self.reply[len(self.frame)];self.frame.append(tx)
  if len(self.frame)==self.frame_width:
   word=int.from_bytes(bytes(self.frame),'big')<<(8 if self.frame_width==2 else 0)
   self.frame=[];self.commit(word,self.frame_cmd)
  return value
 def dma(self,data):
  row=dict(core=self.core,command=self.command,width=self.width,bytes=len(data),pointer=hex(self.pointer),space=self.space,sha256=hashlib.sha256(data).hexdigest())
  self.dmas.append(row)
  if self.native is None:
   row['scope']='inherited bootstrap DMA; loaded DSP programs independently extracted from exact candidate'
   return bytes(len(data))
  assert self.width==2 and not self.frame,'only observed coefficient DMA subset admitted'
  if self.command:assert data==bytes.fromhex('2000'),'only observed return-to24-bit DMA command admitted'
  start=self.pointer;response=bytes(self.byte(b) for b in data)
  row['words']=self.pointer-start;row['end']=hex(self.pointer)
  assert not self.frame,'incomplete SHI word after DMA'
  self.native.flush();return response
 def close(self):
  if self.native:self.native.close()
