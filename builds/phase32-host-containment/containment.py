"""Offline-only one-shot host wrapper. No MIDI port creation or device cleanup.

Uses the unchanged phase27 framing transport and independent protocol receiver.
The five-second absolute observation window includes trailing-frame detection.
No file is published until that window ends without another frame/partial byte.
"""
from pathlib import Path
import sys,hashlib,os,tempfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'builds/phase27-qspi-read'))
from protocol import Receiver,request,NAME,SIZE
from receiver import WinMMTransport

TIMEOUT_SECONDS=5.0
FAILURE_MESSAGE='CAPTURE FAILED\nDO NOT RETRY\nPOWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT'

class DeviceLease:
 """One attempt per externally established device session, shared by callers.

 There is deliberately no reset/retry/rearm method. Constructing a new lease
 does not prove a physical power cycle; this module provides no live adapter.
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

class OneShotCapture:
 def __init__(self,lease,token):
  self.lease=lease;self.token=token;self.status='NEW';self.message=''
  self._receiver=None;self.sha256=None;self.error=None;self.final=None
 def run(self,directory):
  if self.status!='NEW':raise RuntimeError('DO NOT RETRY: capture session is terminal')
  # Claim before any send. A second capture using the same lease cannot send.
  self.lease.claim();self.status='ACTIVE'
  transport=self.lease.transport;clock=self.lease.clock
  temporary=None
  try:
   destination=Path(directory);target=destination/NAME
   if target.exists():raise FileExistsError('Existing evidence will not be replaced')
   self._receiver=Receiver(self.token)
   deadline=clock.monotonic()+TIMEOUT_SECONDS
   transport.send(request(self.token))
   while True:
    remaining=deadline-clock.monotonic()
    if remaining<=0:break
    transport.timeout=remaining
    try:frame=transport.receive()
    except TimeoutError:
     # Silence after one completion is acceptable only with no partial frame.
     if transport.buffer:raise ValueError('partial trailing SysEx at deadline')
     if not self._receiver.done:raise
     break
    if clock.monotonic()>=deadline:raise TimeoutError('frame arrived outside absolute deadline')
    self._receiver.accept(frame) # rejects every frame after completion
   payload=self._receiver.result()
   if len(payload)!=SIZE or len(self._receiver.frames)!=9 or self._receiver.next!=9:
    raise ValueError('exact eight chunks plus one completion required')
   # In-memory validation above; same-directory staging, fsync then an atomic
   # no-replace rename on this Windows target. Never progressively write NAME.
   destination.mkdir(parents=True,exist_ok=True)
   fd,temporary=tempfile.mkstemp(prefix='.qspi-staging-',suffix='.tmp',dir=destination)
   with os.fdopen(fd,'wb') as output:
    output.write(payload);output.flush();os.fsync(output.fileno())
   os.rename(temporary,target);temporary=None
   self.sha256=hashlib.sha256(payload).hexdigest();self.final=str(target)
   self.status='SUCCESS';self.lease.device_state='ONE-SHOT COMPLETE'
   self.message='CAPTURE COMPLETE\nSHA-256 = '+self.sha256
  except Exception as exc:
   self.status='FAILED';self.lease.device_state='POWER-CYCLE REQUIRED'
   self.error=type(exc).__name__+': '+str(exc);self.message=FAILURE_MESSAGE
  finally:
   if temporary is not None:Path(temporary).unlink(missing_ok=True)
   # No partial bytes or decoder can be reused by this session.
   self._receiver=None;transport.buffer=b''
  return self.summary()
 def summary(self):
  return dict(status=self.status,device_state=self.lease.device_state,message=self.message,error=self.error,
   sha256=self.sha256,final=self.final,reconstruction_retained=self._receiver is not None,
   session_consumed=self.lease.claimed)
