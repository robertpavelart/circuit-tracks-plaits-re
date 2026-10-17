"""Bounded startup-ready SPI slave contract, instruction-backed by2601.
Unknown readbacks stop instead of silently supplying a successful value.
"""
class UnknownPeerRead(RuntimeError):pass
class BootPeer:
 def __init__(self):
  self.marker=False;self.read=None;self.reply=[0,0,0];self.index=0;self.log=[];self.core=0;self.command=False;self.htx=0;self.pointer=0;self.space='X';self.memory={'X':{},'Y':{0x2c:0x800000}};self.pending=None;self.job2_pending=False;self.jobs=[]
 def arm_write(self,core,value,address):
  if core==0 and address==0xfff:
   self.log.append(dict(event='actual ARM write request to X:FFF; not committed until wire word completes',core=core,value=hex(value),address=hex(address)))
 def arm_read(self,core,address):self.read=(core,address)
 def word(self,a,b,c,lr):
  if self.htx is None and lr==0x08029512:raise UnknownPeerRead(f'consumed unqualified DSP prefetch: {self.read!r}')
  self.reply=list((self.htx or 0).to_bytes(3,'big'));self.index=0;self.pending=((a<<16)|(b<<8)|c,self.command,self.core)
 def read_word(self):
  if self.core!=0 or self.space!='Y' or self.pointer not in (0x2b,0x2c):self.pointer+=1;return None
  value=(1 if self.marker else 0) if self.pointer==0x2b else self.memory['Y'][0x2c]
  if self.pointer==0x2c and self.job2_pending:
   self.memory['Y'][0x2c]=0x800000;self.job2_pending=False
  self.log.append(dict(event='actual SHI read',space=self.space,address=hex(self.pointer),value=hex(value)));self.pointer+=1;return value
 def commit(self):
  word,cmd,core=self.pending
  if core!=0:raise UnknownPeerRead(f'core{core} transfer not modeled')
  if cmd:
   if word&(1<<21):
    self.log.append(dict(event='SHI width command',value=hex(word)))
    if word!=0x200000:raise UnknownPeerRead(f'SHI width transition {word:06x}: 16-bit bulk DMA recipient and generated-table job not modeled')
    return # already-24-bit mode; no invented acknowledgement
   if word&(1<<22):self.htx=self.read_word();return
   if word&(1<<20):self.pointer=((word<<8)-2)&0xffffff;return
   if word&(1<<19):self.pointer=word&0x3ffff
   else:self.pointer=word&0x7fff;self.space='Y' if word&0x8000 else 'X'
   if word&0x800000:self.htx=self.read_word()
  else:
   self.memory[self.space][self.pointer]=word
   if self.space=='X' and self.pointer==0xfff:self.marker=word!=0
   if self.space=='Y' and self.pointer==0x2c:
    self.log.append(dict(event='mailbox job posted',value=hex(word)))
    if word in (0x080002,0x094403,0x0a8804,0x0bcc05):
     # A stuttering busy->complete contract, not a DSP cycle-time assertion.
     # Exact native init plus observed X state reaches800000 for this exact job.
     from pathlib import Path
     import json,hashlib
     root=Path(__file__).parent;proof=json.loads((root/'peer-contract-proof.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
     sequence=[0x080002,0x094403,0x0a8804,0x0bcc05]
     assert self.jobs==sequence[:sequence.index(word)],'exact native job-order proof mismatch'
     assert proof['job_word']=='080002' and proof['first_service_status']=='800000'
     assert f'{word:06x}' in proof['completed_exact_jobs']
     if word==0x094403:assert proof['next_job_qualified'] and proof['next_exact_job']=='094403'
     assert sha((root/'loaded-core0.be24').read_bytes())==proof['program_sha256']
     assert sha((root/'peer-mailbox-observed-output.txt').read_bytes())==proof['native_output_sha256']
     canonical=json.dumps({hex(k):v for k,v in self.memory['X'].items()},sort_keys=True).encode()
     assert sha(canonical)==proof['init_X_sha256'],'native peer initialization proof does not match wire state'
     self.jobs.append(word)
     self.job2_pending=True
    else:raise UnknownPeerRead(f'DSP deferred task completion not qualified for Y:2C={word:06x}')
   self.pointer+=1
 def byte(self,tx):
  assert self.index<3
  value=self.reply[self.index];self.index+=1
  if self.index==3:self.commit()
  return value
