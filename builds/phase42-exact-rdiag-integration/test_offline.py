"""Synthetic-only ARM/Storage replay and independent one-shot host negatives."""
from pathlib import Path
import json,tempfile,hashlib
from replay import Model
from evidence_protocol import *
from host import OneShot,DeviceLease
from environment import Physical,UC_HOOK_CODE,UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
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
 result=dict(confidence='PROVEN',scope='Host-only fake MIDI streams with controllable clock, independent of exact-image native replay',host_cases=host,synthetic_sha256={NAMES[0]:hashlib.sha256(DATA[:23]).hexdigest(),NAMES[1]:hashlib.sha256(DATA[23:]).hexdigest()},firmware_image_generated=False,hardware_access=False)
 (O/'test-results.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('native_cases','host_cases')},indent=2));print('Host cases',len(host))
if __name__=='__main__':main()
