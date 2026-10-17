"""Offline host protocol and deterministic containment. No device imports.

This module intentionally has no CLI that opens a transport. An operator-facing
hardware tool must be separately authorized; tests inject a callable transport.
"""
from pathlib import Path
import sys,hashlib,os,tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'phase56-geometry-snapshot-lifecycle'))
from compact import decode as geometry_decode
SIG=b'\xf0\x7dCT'
TIMEOUT=10.0
def crc(b):
 c=0xffffffff
 for x in b:
  c^=x<<24
  for _ in range(8):c=((c<<1)^(0x04c11db7 if c&0x80000000 else 0))&0xffffffff
 return c
def n32(v):return bytes(int(x,16) for x in f'{v:08x}')
def number(b):
 if len(b)!=8 or any(x>15 for x in b):raise ValueError('nibbles')
 return int(''.join(f'{x:x}' for x in b),16)
def un(b):
 if len(b)%2 or any(x>15 for x in b):raise ValueError('nibbles')
 return bytes((b[i]<<4)|b[i+1] for i in range(0,len(b),2))
def request(session,op=14,epoch=None,geometry=None,identity=False):
 if not 1<=session<=127:raise ValueError('session')
 b=SIG+bytes((op,session))
 if op==15:
  if epoch!=1 or len(geometry)!=8:raise ValueError('epoch/geometry')
  b+=bytes((3 if identity else 2,))+n32(epoch)+n32(int.from_bytes(geometry[:4],'little'))+n32(int.from_bytes(geometry[4:],'little'))
 elif op!=14:raise ValueError('no other command')
 return b+bytes(231-len(b))+b'\xf7'
def geometry_response(b,session):
 if len(b)!=39 or b[:6]!=SIG+bytes((0x4e,session)) or b[-1]!=247 or any(x>=128 for x in b[1:-1]):raise ValueError('geometry framing')
 if number(b[-9:-1])!=crc(b[4:-9]):raise ValueError('geometry CRC')
 epoch=number(b[6:14]);g=number(b[14:22]).to_bytes(4,'little')+number(b[22:30]).to_bytes(4,'little')
 if epoch!=1:raise ValueError('unexpected epoch')
 domains=geometry_decode(g)
 return epoch,g,domains
class Receiver:
 def __init__(self,session,identity=False):self.session=session;self.identity=identity;self.index=0 if identity else 1;self.parts=[];self.done=False
 def accept(self,b):
  if self.done:raise ValueError('duplicate/after completion')
  if len(b)<34 or b[:6]!=SIG+bytes((0x4d,self.session)) or b[-1]!=247 or any(x>=128 for x in b[1:-1]):raise ValueError('framing')
  kind,index=b[6:8];address=number(b[8:16]);total=number(b[16:24]);count=b[24]
  if index!=self.index or total!=(535 if self.identity else 512) or len(b)!=34+2*count:raise ValueError('order/total/size')
  if number(b[-9:-1])!=crc(b[4:-9]):raise ValueError('CRC')
  data=un(b[25:-9])
  if index<9:
   expected=(0x81000,23,0) if index==0 else (0x82000+64*(index-1),64,1)
   if (address,count,kind)!=expected:raise ValueError('fixed region')
   self.parts.append(data)
  else:
   if index!=9 or kind!=2 or count!=4 or address!=(0x81000 if self.identity else 0x82000) or int.from_bytes(data,'big')!=crc(b''.join(self.parts)):raise ValueError('completion')
   self.done=True
  self.index+=1
 def result(self):
  b=b''.join(self.parts)
  if not self.done or len(b)!=(535 if self.identity else 512):raise ValueError('incomplete')
  return b
class Session:
 def __init__(self,send,clock,session=37,identity=False):
  self.send=send;self.clock=clock;self.session=session;self.identity=identity;self.state='NEW';self.deadline=None;self.receiver=None;self.message='';self.device='UNASSESSED'
 def fail(self):
  self.state='FAILED';self.device='POWER-CYCLE REQUIRED';self.receiver=None;self.message='CAPTURE FAILED\nDO NOT RETRY\nPOWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT'
 def start(self):
  if self.state!='NEW':raise ValueError('one shot')
  self.state='GEOMETRY';self.deadline=self.clock()+TIMEOUT;self.send(request(self.session))
 def poll(self):
  if self.state in ('GEOMETRY','ACTIVE') and self.clock()>=self.deadline:self.fail()
 def accept(self,b):
  self.poll()
  if self.state=='FAILED':return
  try:
   if self.state=='GEOMETRY':
    epoch,g,domains=geometry_response(b,self.session)
    if domains['targets_reachable']['0x82000'] or self.identity and domains['targets_reachable']['0x81000']:raise ValueError('reachable')
    self.receiver=Receiver(self.session,self.identity);self.state='ACTIVE';self.deadline=self.clock()+TIMEOUT
    self.send(request(self.session,15,epoch,g,self.identity))
   elif self.state=='ACTIVE':self.receiver.accept(b)
   else:raise ValueError('out of session')
  except (ValueError,IndexError):self.fail()
 def finish(self,directory):
  # Explicit end-of-stream validation precedes any output. A later duplicate
  # received before this boundary invalidates the entire in-memory reconstruction.
  self.poll();staging=None
  try:
   if self.state!='ACTIVE':raise ValueError('not active')
   b=self.receiver.result();coeff=b[23:] if self.identity else b
   d=Path(directory)
   if d.exists():raise FileExistsError('existing capture is never replaced')
   d.parent.mkdir(parents=True,exist_ok=True);staging=Path(tempfile.mkdtemp(prefix='.capture-',dir=d.parent))
   captures={'qspi_00082000_000821ff.bin':coeff}
   if self.identity:captures['nor_00081000_00081016.bin']=b[:23]
   for name,data in captures.items():
    with (staging/name).open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
   # One directory publication makes optional identity and coefficients atomic
   # together. No final filename is exposed if either file fails to be written.
   os.rename(staging,d);staging=None
   self.state='SUCCESS';return hashlib.sha256(coeff).hexdigest()
  except (ValueError,OSError):self.fail();return None
  finally:
   if staging is not None:
    # Delete only exact files owned by this freshly created staging directory.
    for name in ('qspi_00082000_000821ff.bin','nor_00081000_00081016.bin'):
     p=staging/name
     if p.exists():p.unlink()
    staging.rmdir()
