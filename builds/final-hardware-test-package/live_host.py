"""Windows one-shot host; import/help never access MIDI.

Every live CLI operation is LOCKED by the operational gate. No unlock flag.
Phase67 scoped preflight passed; this frozen package is not a live release. Tests inject clocks/transports;
no command retries or arbitrary addresses are implemented.
"""
from pathlib import Path
import sys,json,time,queue,os,argparse,importlib.util,secrets
O=Path(__file__).resolve().parent;R=O.parents[1]
spec=importlib.util.spec_from_file_location('phase61_codec',O/'protocol_codec.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
from status_protocol import parse as status_response
GEOMETRY_SECONDS=10.;AUTH_SEND_SECONDS=2.;RAW_SECONDS=10.
class Frames:
 def __init__(self,link,clock):self.link=link;self.clock=clock;self.buffer=b''
 def send(self,b):self.link.send(b)
 def receive(self,deadline):
  while True:
   if self.buffer:
    if self.buffer[0]!=240:raise ValueError('invalid MIDI stream')
    end=self.buffer.find(b'\xf7')
    if end>=0:
     if end+1>232:raise ValueError('oversized SysEx')
     out=self.buffer[:end+1];self.buffer=self.buffer[end+1:];return out
    if len(self.buffer)>232:raise ValueError('oversized MIDI stream')
   left=deadline-self.clock()
   if left<=0:raise TimeoutError('absolute stage deadline')
   try:b,handle=self.link.q.get(timeout=left)
   except queue.Empty:raise TimeoutError('input silence') from None
   self.link._readd(handle) # Host buffer return only; no diagnostic/storage send.
   self.buffer+=b
 def close(self):self.link.close()
def run(output,marker,inventory,opener,clock=time.monotonic,port='Circuit',geometry_only=False,identity=False,preflight_pass=False,session=37,validator=C.geometry_response,approve=None):
 marker=Path(marker);sent=[];tx=None;begun=False;raw_sent=False;state='PRE_SEND';result={}
 def emit(b):
  nonlocal begun,raw_sent
  if not begun:
   owned=False
   try:
    with marker.open('x') as f:owned=True;json.dump(dict(state='FIRST SEND MAY BEGIN',session=session,output=str(output)),f);f.flush();os.fsync(f.fileno())
   except BaseException:
    if owned:marker.unlink()
    raise
   begun=True
  if b[4]==15:raw_sent=True
  sent.append(b.hex()) # Record attempted transmission before driver call.
  tx.send(b)
 def quiet(deadline):
  try:tx.receive(deadline)
  except TimeoutError:
   if clock()<deadline or tx.buffer:raise
  else:raise ValueError('unexpected trailing response')
 try:
  if not preflight_pass:raise RuntimeError('UNQUALIFIED: live query/capture is locked')
  if marker.exists():raise RuntimeError('DO NOT RETRY: existing durable attempt marker')
  if Path(output).exists():raise FileExistsError('output must be a new directory')
  before=clock();ins,outs=inventory();ii=[x for x in ins if port.casefold() in x.casefold()];oo=[x for x in outs if port.casefold() in x.casefold()]
  if len(ii)!=1 or len(oo)!=1:raise RuntimeError('one unambiguous input and output required')
  tx=opener(port)
  if clock()-before>=GEOMETRY_SECONDS:raise TimeoutError('pre-send preparation deadline')
  gd=clock()+GEOMETRY_SECONDS;emit(C.request(session));state='GEOMETRY_PENDING'
  frame=tx.receive(gd)
  if clock()>=gd:raise TimeoutError('status deadline')
  status=status_response(frame,session)['status'];state=status
  if status=='FAILED':raise RuntimeError('device FAILED: full power cycle required')
  if status in ('NOT_READY','INVALID','UNSAFE'):
   # Observe the whole query window; reject duplicates/trailing replies.
   try:tx.receive(gd)
   except TimeoutError:
    if clock()<gd or tx.buffer:raise
   else:raise ValueError('duplicate/unexpected status')
   # Operational freeze: retain marker even for NOT_READY; no in-session retry.
   result=dict(message=(status+': no authorization or raw request; session ended; attempt marker retained, no retry'))
  elif status!='READY':raise ValueError('unexpected initial status')
  else:
   frame=tx.receive(gd)
   if clock()>=gd:raise TimeoutError('geometry deadline')
   epoch,g,domains=validator(frame,session)
   if domains['targets_reachable']['0x82000'] or identity and domains['targets_reachable']['0x81000']:
    state='UNSAFE';quiet(gd);result=dict(message='UNSAFE: no authorization or raw request')
   elif geometry_only:
    state='READY';quiet(gd);result=dict(epoch=epoch,geometry=g.hex(),domains=domains)
   else:
    if approve is None or approve(epoch,g,domains) is not True:raise RuntimeError('authorization not explicitly approved')
    start=clock();deadline=start+RAW_SECONDS;emit(C.request(session,15,epoch,g,identity))
    if clock()-start>=AUTH_SEND_SECONDS:raise TimeoutError('authorization transmission deadline')
    state='AUTHORIZATION_SENT';receiver=C.Receiver(session,identity);authorized=False;success=False
    while True:
     try:frame=tx.receive(deadline)
     except TimeoutError:
      if clock()<deadline or tx.buffer or not receiver.done or not success:raise
      break
     if clock()>=deadline:raise TimeoutError('packet outside stage deadline')
     if frame[4]==0x4f:
      code=status_response(frame,session)['status']
      if code=='FAILED':raise RuntimeError('device FAILED: full power cycle required')
      if code=='AUTHORIZED' and not authorized and not receiver.parts and not success:authorized=True;state=code
      elif code=='SUCCESS' and authorized and receiver.done and not success:success=True
      else:raise ValueError('duplicate/out-of-order status')
     else:
      if not authorized or success:raise ValueError('raw before authorization / after success')
      receiver.accept(frame)
    h=C.Session(lambda b:(_ for _ in ()).throw(AssertionError('no send during publication')),clock,session,identity)
    h.state='ACTIVE';h.deadline=clock()+1;h.receiver=receiver;digest=h.finish(output)
    if digest is None:raise OSError('atomic publication failed')
    state='SUCCESS';result=dict(SHA256=digest,bytes=512)
 except (Exception,KeyboardInterrupt) as ex:
  state='FAILED' if begun else 'FAILED_PRE_SEND'
  result=dict(error=type(ex).__name__+': '+str(ex),message=('CAPTURE FAILED\nDO NOT RETRY\nPOWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT' if begun else 'CAPTURE NOT SENT; no power cycle required by this attempt'))
 finally:
  if tx is not None:
   try:tx.close()
   except Exception as ex:
    result['close_error']=repr(ex)
    if state!='SUCCESS':state='FAILED' if begun else 'FAILED_PRE_SEND'
 result.update(status=state,diagnostic_messages_attempted=len(sent),messages=sent,marker_exists=marker.exists(),raw_authorization_attempted=raw_sent,automatic_retries=0,requires_power_cycle=state=='FAILED')
 return result
VERSION='1.0.0-phase68-locked'
def main():
 p=argparse.ArgumentParser(description='Frozen one-shot diagnostic host; every live operation is locked by default.')
 p.add_argument('mode',choices=['list','geometry','capture','mock']);p.add_argument('--port',default='Circuit');p.add_argument('--output',type=Path);p.add_argument('--identity',action='store_true');a=p.parse_args()
 if a.mode=='mock':
  import mock_tests
  mock_tests.main();return
 gate=O/'operational-gate.json'
 if not gate.exists() or json.loads(gate.read_text()).get('live_enabled') is not True:p.exit(2,'LOCKED: no MIDI enumeration/open/send. Explicit user decision and separately reviewed release required.\n')
 # No CLI unlock option. The frozen gate is false. No transport import occurs above it.
 spec=importlib.util.spec_from_file_location('frozen_transport',O/'ctremote_transport.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 if a.mode=='list':print(json.dumps(dict(zip(('inputs','outputs'),m.ports())),indent=2));return
 if a.output is None:p.error('--output required')
 def approve(epoch,g,domains):
  print(json.dumps(dict(epoch=epoch,geometry=g.hex(),domains=domains),indent=2))
  return input('Geometry validated locally. Type AUTHORIZE ONE CAPTURE to proceed: ')=='AUTHORIZE ONE CAPTURE'
 result=run(a.output,O/'HARDWARE-ATTEMPT.json',m.ports,lambda name:Frames(m.Link(name),time.monotonic),port=a.port,geometry_only=a.mode=='geometry',identity=a.identity,preflight_pass=True,session=secrets.randbelow(127)+1,approve=approve)
 print(json.dumps(result,indent=2));p.exit(0 if result['status'] in ('SUCCESS','READY','NOT_READY','INVALID','UNSAFE') else 1)
if __name__=='__main__':main()
