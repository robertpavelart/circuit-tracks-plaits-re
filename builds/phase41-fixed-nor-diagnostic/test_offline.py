"""Synthetic-only ARM/Storage replay and independent one-shot host negatives."""
from pathlib import Path
import json,tempfile,hashlib
from replay import Model
from evidence_protocol import *
from host import OneShot,DeviceLease
from environment import Physical,UC_HOOK_CODE,UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
from entry import entry
import struct
O=Path(__file__).resolve().parent
DATA=bytes(((i*73)^(i>>1)^0xa6)&255 for i in range(535))
class Clock:
 def __init__(self):self.t=0.
 def monotonic(self):return self.t
class Fake:
 def __init__(self,clock,frames,partial=False):self.clock=clock;self.frames=list(frames);self.sent=[];self.buffer=b'';self.partial=partial
 def send(self,b):self.sent.append(b)
 def receive(self):
  if self.frames:self.clock.t+=0.02;return self.frames.pop(0)
  self.clock.t+=self.timeout
  if self.partial:self.buffer=b'\xf0\x7d'
  raise TimeoutError('synthetic silence')
def main():
 rows=[]
 # New filter is inert for ordinary traffic: execute its actual forwarding
 # prologue, then stop before the unchanged stock dispatcher continuation.
 for label,data in [('stock identity request',bytes.fromhex('f07e7f0601f7')),('Novation message',bytes.fromhex('f000202901640801f7'))]:
  e=Physical();u=e.uc;u.mem_write(0x0807a414,entry());u.mem_write(0x2000a050,data);u.mem_write(0x200082f0,struct.pack('<II',0x2000a050,len(data)))
  seen=[]
  def forward(uc,pc,n,d):seen.append(pc);uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,forward,begin=0x0801eb34,end=0x0801eb34)
  initial={UC_ARM_REG_R0:0,UC_ARM_REG_R0+1:0x200082f0,UC_ARM_REG_R0+2:123,UC_ARM_REG_SP:0x200082d8,UC_ARM_REG_LR:0x0807ff01}
  for reg,v in initial.items():u.reg_write(reg,v)
  u.emu_start(0x0807a415,0xffffffff,count=10000)
  assert seen==[0x0801eb34] and u.reg_read(UC_ARM_REG_SP)==initial[UC_ARM_REG_SP]-24
  assert all(u.reg_read(reg)==v for reg,v in initial.items() if reg!=UC_ARM_REG_SP)
  rows.append(dict(case=label,confidence='PROVEN',result='original prologue and continuation; no NOR adapter call'))
 for name,opts in [('normal',{}),('MIDI backpressure',{'delay':5}),('preemption after notify',{'interleave':True})]:
  m=Model(**opts);m.start();assert m.finish(1000);m.verify()
  assert bytes(m.payload)==DATA and len(m.reads)==9 and m.payload[14]!=0
  rows.append(dict(case=name,confidence='PROVEN',details=m.summary()))
 for kind in ('tef','missing'):
  for chunk in (0,1,5,8):
   m=Model(kind,chunk);m.start();assert not m.finish()
   assert len(m.reads)==chunk+1 and len(m.frames)==chunk and m.active['chunk']==chunk
   assert m.e.r8(m.backend+8)==0 and m.e.r32(m.wrapper+16)==1
   rows.append(dict(case=f'{kind} identity' if chunk==0 else f'{kind} 82000 chunk{chunk-1}',confidence='PROVEN',details=m.summary()))
 m=Model();m.start();assert m.finish(disconnect_after=4) and len(m.reads)==5 and len(m.frames)==5
 rows.append(dict(case='host disconnect after target chunk3; no next read',confidence='PROVEN',details=m.summary()))
 # Duplicate is only deferred by the old model, not exercised through USB RX.
 m=Model();m.start();assert m.finish(duplicate=True);m.verify()
 assert len(m.reads)==9 and m.deferred_duplicate==1
 rows.append(dict(case='duplicate while active',confidence='UNKNOWN',bounded_nonreentry=True,USB_RX_queue_and_postreturn_dispatch='Not modeled; not a duplicate-command qualification',details=m.summary()))
 for label,mut in [('nonzero host payload',lambda b:b.__setitem__(6,1)),('write command',lambda b:b.__setitem__(4,6)),('bad terminator',lambda b:b.__setitem__(-1,0)),('short request',lambda b:b.__delitem__(6))]:
  m=Model();b=bytearray(request(37));mut(b)
  # A bad terminator never completes the real parser: test decoder rejection
  # separately from calling a handler with a fabricated completed descriptor.
  if label=='bad terminator':
   assert b[-1]!=247;rows.append(dict(case=label,confidence='UNKNOWN',native_entry_replay=False,reason='Does not complete stock parser; no descriptor fabricated'));continue
  m.start(data=bytes(b));assert m.done and not m.reads and not m.frames
  rows.append(dict(case=label,confidence='PROVEN',reads=0))
 normal=synthetic_packets(37,DATA)
 cases={'normal':normal,'silence':[],'failure identity':[],'failure target chunk0':normal[:1], 'failure target chunk4':normal[:5],'failure target chunk7':normal[:8], 'truncated after final data':normal[:-1], 'missing chunk':normal[:4]+normal[5:], 'reordered':[normal[1],normal[0]]+normal[2:], 'duplicate chunk':normal[:3]+[normal[2]]+normal[3:], 'duplicate completion':normal+[normal[-1]], 'early completion':[normal[-1]], 'wrong transaction':synthetic_packets(38,DATA)}
 bad=list(normal);b=bytearray(bad[3]);b[-2]^=1;bad[3]=bytes(b);cases['bad CRC']=bad
 bad=list(normal);b=bytearray(bad[3]);b[8]^=1;b[-9:-1]=n32(crc32(b[4:-9]));bad[3]=bytes(b);cases['wrong address with valid CRC']=bad
 bad=list(normal);bad[-1]=packet(37,2,9,(crc32(DATA)^1).to_bytes(4,'big'));cases['bad whole CRC']=bad
 host=[]
 with tempfile.TemporaryDirectory(dir=O) as d:
  root=Path(d)
  for i,(name,frames) in enumerate(cases.items()):
   clock=Clock();transport=Fake(clock,frames);lease=DeviceLease(transport,clock);c=OneShot(lease,37);dest=root/f'case{i}';result=c.run(dest)
   assert len(transport.sent)==1
   if name=='normal':
    assert c.status=='SUCCESS' and (dest/NAMES[0]).read_bytes()==DATA[:23] and (dest/NAMES[1]).read_bytes()==DATA[23:]
    assert len((dest/NAMES[0]).read_bytes())==23 and len((dest/NAMES[1]).read_bytes())==512
   else:assert c.status=='FAILED' and not dest.exists() and c.hashes is None and result['message']=='CAPTURE FAILED\nDO NOT RETRY\nPOWER-CYCLE REQUIRED'
   try:OneShot(lease,38).run(root/'retry')
   except RuntimeError:pass
   else:raise AssertionError('lease reused')
   assert len(transport.sent)==1 and not list(root.glob('.nor-staging-*'))
   host.append(dict(case=name,confidence='PROVEN',sent=1,result=result,accepted_files=2 if name=='normal' else 0))
  clock=Clock();f=Fake(clock,normal,partial=True);c=OneShot(DeviceLease(f,clock),37);assert c.run(root/'partial')['status']=='FAILED' and not (root/'partial').exists()
  host.append(dict(case='partial trailing packet after completion',confidence='PROVEN',accepted_files=0,sent=len(f.sent)))
 result=dict(confidence='PROVEN',scope='Synthetic prototype on B1.3 running-RAM fixture, not an SC35D8-derived deployable application or complete scheduler/RX replay',native_cases=rows,host_cases=host,synthetic_sha256={NAMES[0]:hashlib.sha256(DATA[:23]).hexdigest(),NAMES[1]:hashlib.sha256(DATA[23:]).hexdigest()},firmware_image_generated=False,hardware_access=False)
 (O/'test-results.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('native_cases','host_cases')},indent=2));print('Native cases',len(rows),'Host cases',len(host))
if __name__=='__main__':main()
