"""HARDWARE-TEST ONLY: standalone one-shot capture. Importing opens no ports."""
"""Fixed experimental command in rdiag framing; no hardware or I/O imports."""
import hashlib
SIG=b'\xf0\x7dCT';CMD=13;SIZE=535;PAD=232
REGIONS=((0x81000,23),)+tuple((0x82000+i*64,64) for i in range(8))
NAMES=('nor_00081000_00081016.bin','nor_00082000_000821ff.bin')
def crc32(data):
 c=0xffffffff
 for b in data:
  c^=b<<24
  for _ in range(8):c=((c<<1)^(0x04c11db7 if c&0x80000000 else 0))&0xffffffff
 return c
def nib(b):return bytes(v for x in b for v in (x>>4,x&15))
def un(b):
 if len(b)%2 or any(v>15 for v in b):raise ValueError('invalid nibbles')
 return bytes((b[i]<<4)|b[i+1] for i in range(0,len(b),2))
def n32(v):return nib(v.to_bytes(4,'big'))
def request(token):
 if not 0<=token<128:raise ValueError('transaction id')
 return SIG+bytes((CMD,token))+bytes(225)+b'\xf7'
def packet(token,kind,index,payload):
 addr=REGIONS[index][0] if index<9 else 0x81000
 b=SIG+bytes((CMD|64,token,kind,index))+n32(addr)+n32(SIZE)+bytes((len(payload),))+nib(payload)
 return b+n32(crc32(b[4:]))+b'\xf7'
def synthetic_packets(token,data):
 assert len(data)==535
 return [packet(token,0,0,data[:23])]+[packet(token,1,i+1,data[23+64*i:23+64*(i+1)]) for i in range(8)]+[packet(token,2,9,crc32(data).to_bytes(4,'big'))]
class Receiver:
 def __init__(self,token):self.token=token;self.next=0;self.frames=[];self.parts=[];self.done=False
 def accept(self,msg):
  if self.done:raise ValueError('packet after completion')
  if len(msg)<34 or msg[:6]!=SIG+bytes((CMD|64,self.token)) or msg[-1]!=247 or any(v>=128 for v in msg[1:-1]):raise ValueError('framing/session')
  kind,index=msg[6:8];addr=int.from_bytes(un(msg[8:16]),'big');total=int.from_bytes(un(msg[16:24]),'big');n=msg[24]
  if len(msg)!=34+2*n or total!=SIZE or index!=self.next:raise ValueError('length/total/order')
  if crc32(msg[4:-9])!=int.from_bytes(un(msg[-9:-1]),'big'):raise ValueError('packet CRC')
  data=un(msg[25:-9])
  if index<9:
   if (addr,n)!=REGIONS[index] or kind!=(0 if index==0 else 1):raise ValueError('region/address/size')
   self.parts.append(data)
  else:
   if index!=9 or kind!=2 or addr!=0x81000 or n!=4 or int.from_bytes(data,'big')!=crc32(b''.join(self.parts)):raise ValueError('completion')
   self.done=True
  self.next+=1;self.frames.append(msg)
 def result(self):
  if not self.done or len(self.frames)!=10 or sum(map(len,self.parts))!=535:raise ValueError('incomplete capture')
  return b''.join(self.parts)
 def captures(self):
  b=self.result();return dict(zip(NAMES,(b[:23],b[23:])))

"""Qualified one-shot receiver with an explicit capture-only CLI below.

Both captures publish in one atomic directory rename after full validation.
"""
from pathlib import Path
import ast,os,json,hashlib,shutil,tempfile,queue
# Receiver and request are embedded above.
class DeviceLease:
 """One attempt per externally established device session, shared by callers.

 There is deliberately no reset/retry/rearm method. Constructing a new lease
 does not prove a physical power cycle; the CLI adds a durable attempt marker.
 """
 def __init__(self,transport,clock):
  if getattr(transport,'_one_shot_lease_created',False):
   raise RuntimeError('DO NOT RETRY: transport already belongs to a device session')
  transport._one_shot_lease_created=True
  self.transport=transport;self.clock=clock;self.claimed=False
  self.device_state='UNATTEMPTED'
 def claim(self):
  if self.claimed:raise RuntimeError('DO NOT RETRY: device session already consumed')
  self.claimed=True;self.device_state='CAPTURE ACTIVE'
TIMEOUT_SECONDS=5.0
FAILURE='CAPTURE FAILED\nDO NOT RETRY\nFULL POWER CYCLE REQUIRED'
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
   os.rename(staging,final);staging=None
   self.hashes=hashes;self.status='SUCCESS';self.lease.device_state='ONE-SHOT COMPLETE'
   self.message='CAPTURE COMPLETE\n'+'\n'.join(n+' LENGTH = '+str(len(captures[n]))+' SHA-256 = '+h for n,h in hashes.items())
  except (Exception,KeyboardInterrupt) as exc:
   self.status='FAILED';self.lease.device_state='POWER-CYCLE REQUIRED';self.error=type(exc).__name__+': '+str(exc);self.message=FAILURE
  finally:
   if staging is not None:
    assert staging.resolve().parent==final.parent.resolve() and staging.name.startswith('.nor-staging-')
    shutil.rmtree(staging)
   transport.buffer=b''
  return dict(status=self.status,device_state=self.lease.device_state,message=self.message,sha256=self.hashes,error=self.error)


# Live access exists only behind the explicit `capture` subcommand. This module
# is importable for offline fake-Link tests without importing WinMM.
import time,argparse

def run_capture(destination, link_factory, clock=time, attempt_path=None):
 link=None
 try:
  final=Path(destination)
  if final.exists():raise FileExistsError('existing output is never replaced')
  claim=Path(attempt_path) if attempt_path is not None else Path(__file__).resolve().with_name('NOR-CAPTURE-ATTEMPT.json')
  # Durable one-attempt marker BEFORE opening a port or sending anything.
  # No reset/retry/rearm command is provided. Do not delete/bypass this marker.
  with claim.open('x') as f:
   json.dump({'policy':'ONE SHOT; no retry; full power cycle required after failure','output':str(final),'attempt':'CLAIMED'},f);f.flush();os.fsync(f.fileno())
  link=link_factory()
  transport=FramedTransport(link,clock);lease=DeviceLease(transport,clock)
  result=OneShot(lease,37).run(final)
 except (Exception,KeyboardInterrupt,SystemExit) as exc:
  result={'status':'FAILED','device_state':'POWER-CYCLE REQUIRED','message':FAILURE,'sha256':None,'error':type(exc).__name__+': '+str(exc)}
 finally:
  if link is not None:
   try:link.close() # WinMM host-resource teardown only; no device/storage command.
   except Exception:pass
 return result

def main(argv=None):
 ap=argparse.ArgumentParser(description='ONE-SHOT fixed NOR evidence capture. H4 FAIL. No retry; full power cycle after failure.')
 sub=ap.add_subparsers(dest='action',required=True)
 capture=sub.add_parser('capture',help='one explicit capture; opens MIDI only when this command is run')
 capture.add_argument('--out',required=True,type=Path,help='new directory; receives exactly the two validated evidence BIN files')
 capture.add_argument('--port-name',default='Circuit',help='unique Windows MIDI name substring')
 args=ap.parse_args(argv)
 def live_link():
  from ctremote_transport import Link
  return Link(args.port_name)
 result=run_capture(args.out,live_link)
 print(result['message'])
 print('TRANSACTION STATUS = '+result['status'])
 if result.get('error'):print('DETAIL: '+result['error'])
 return 0 if result['status']=='SUCCESS' else 1
if __name__=='__main__':raise SystemExit(main())

