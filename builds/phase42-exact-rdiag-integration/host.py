"""Offline-capable one-shot receiver; no live CLI and no MIDI port creation.

Accepts the existing ctremote.Link-compatible framing transport by injection.
Both captures publish in ONE atomic directory rename, after the full deadline.
"""
from pathlib import Path
import ast,os,json,hashlib,shutil,tempfile,queue
from evidence_protocol import Receiver,request
ROOT=Path(__file__).resolve().parents[2]
# Reuse the exact previously qualified lease implementation, without importing
# any transport or unrelated codec module. This module never opens a port.
source=ROOT/'builds/phase32-host-containment/containment.py'
tree=ast.parse(source.read_text())
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='DeviceLease'],type_ignores=[]),str(source),'exec'))
TIMEOUT_SECONDS=5.0
FAILURE='CAPTURE FAILED\nDO NOT RETRY\nPOWER-CYCLE REQUIRED'
class FramedTransport:
 """Injected ctremote.Link send/q/_readd interface; never opens a MIDI port.

 receive consumes existing WinMM callback byte chunks with a bounded timeout.
 No ask()/retry command is used. _readd only returns a host input buffer.
 """
 def __init__(self,link,clock):
  if getattr(link,'_fixed_nor_transport_created',False):raise RuntimeError('DO NOT RETRY: link session already used')
  link._fixed_nor_transport_created=True
  self.link=link;self.clock=clock;self.timeout=TIMEOUT_SECONDS;self.buffer=b''
 def send(self,data):self.link.send(data)
 def receive(self):
  deadline=self.clock.monotonic()+self.timeout
  while True:
   if self.buffer:
    if self.buffer[0]!=0xf0:raise ValueError('unexpected MIDI bytes')
    end=self.buffer.find(b'\xf7')
    if end>=0:
     result,self.buffer=self.buffer[:end+1],self.buffer[end+1:];return result
    if len(self.buffer)>232:raise ValueError('oversized SysEx')
   left=deadline-self.clock.monotonic()
   if left<=0:raise TimeoutError('MIDI input deadline')
   try:data,handle=self.link.q.get(timeout=left)
   except queue.Empty:raise TimeoutError('MIDI input silence') from None
   self.link._readd(handle)
   self.buffer+=data

class OneShot:
 def __init__(self,lease,token):self.lease=lease;self.token=token;self.status='NEW';self.hashes=None;self.error=None
 def run(self,destination):
  if self.status!='NEW':raise RuntimeError('DO NOT RETRY')
  self.lease.claim();self.status='ACTIVE';transport=self.lease.transport;clock=self.lease.clock;staging=None
  try:
   final=Path(destination)
   if final.exists():raise FileExistsError('Existing capture is never replaced')
   r=Receiver(self.token);deadline=clock.monotonic()+TIMEOUT_SECONDS
   transport.send(request(self.token))
   while clock.monotonic()<deadline:
    transport.timeout=deadline-clock.monotonic()
    try:frame=transport.receive()
    except TimeoutError:
     if transport.buffer or not r.done:raise
     # A transport timeout is not proof that the absolute deadline elapsed.
     if clock.monotonic()<deadline:raise TimeoutError('premature transport timeout')
     break
    if clock.monotonic()>=deadline:raise TimeoutError('outside absolute deadline')
    r.accept(frame)
   if transport.buffer:raise ValueError('truncated trailing frame')
   captures=r.captures()
   final.parent.mkdir(parents=True,exist_ok=True)
   staging=Path(tempfile.mkdtemp(prefix='.nor-staging-',dir=final.parent))
   hashes={n:hashlib.sha256(b).hexdigest() for n,b in captures.items()}
   for n,b in captures.items():
    with (staging/n).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
   with (staging/'capture.json').open('x') as f:
    json.dump(dict(origin='Transport bytes; device authenticity not inferred by host',transaction=self.token,sha256=hashes),f,indent=2)
    f.flush();os.fsync(f.fileno())
   os.rename(staging,final);staging=None
   self.hashes=hashes;self.status='SUCCESS';self.lease.device_state='ONE-SHOT COMPLETE'
   self.message='CAPTURE COMPLETE\n'+'\n'.join(n+' SHA-256 = '+h for n,h in hashes.items())
  except Exception as exc:
   self.status='FAILED';self.lease.device_state='POWER-CYCLE REQUIRED';self.error=type(exc).__name__+': '+str(exc);self.message=FAILURE
  finally:
   if staging is not None:
    assert staging.resolve().parent==final.parent.resolve() and staging.name.startswith('.nor-staging-')
    shutil.rmtree(staging)
   transport.buffer=b''
  return dict(status=self.status,device_state=self.lease.device_state,message=self.message,sha256=self.hashes,error=self.error)
