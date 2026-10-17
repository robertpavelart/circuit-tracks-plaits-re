"""Windows one-shot host; import/help never access MIDI.

Live query/capture is LOCKED unless preflight-verdict.json says PASS. The frozen
firmware currently fails readiness/status gates. Tests inject clocks/transports;
no command retries or arbitrary addresses are implemented.
"""
from pathlib import Path
import sys,json,time,queue,os,argparse,importlib.util,secrets
O=Path(__file__).resolve().parent;R=O.parents[1]
spec=importlib.util.spec_from_file_location('phase61_codec',R/'builds/phase61-final-geometry-gated-candidate/host.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
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
def run(output,marker,inventory,opener,clock=time.monotonic,port='Circuit',geometry_only=False,identity=False,preflight_pass=False,session=37,validator=C.geometry_response):
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
  if clock()>=gd:raise TimeoutError('geometry deadline')
  epoch,g,domains=validator(frame,session)
  if domains['targets_reachable']['0x82000'] or identity and domains['targets_reachable']['0x81000']:
   state='UNSAFE';result=dict(message='Do not authorize; no raw read; restore normal firmware through separately planned flow')
  elif geometry_only:
   state='GEOMETRY_SAFE';result=dict(epoch=epoch,geometry=g.hex(),domains=domains)
  else:
   start=clock();deadline=start+RAW_SECONDS;emit(C.request(session,15,epoch,g,identity))
   if clock()-start>=AUTH_SEND_SECONDS:raise TimeoutError('authorization transmission deadline')
   state='AUTHORIZATION_SENT';receiver=C.Receiver(session,identity)
   while True:
    try:frame=tx.receive(deadline)
    except TimeoutError:
     if clock()<deadline or tx.buffer or not receiver.done:raise
     break # Full absolute end-of-stream observation window completed.
    if clock()>=deadline:raise TimeoutError('packet outside stage deadline')
    receiver.accept(frame);state='AUTHORIZED' # Proven by validated first raw reply, not invented ACK.
   h=C.Session(lambda b:(_ for _ in ()).throw(AssertionError('no send during publication')),clock,session,identity)
   h.state='ACTIVE';h.deadline=clock()+1;h.receiver=receiver;digest=h.finish(output)
   if digest is None:raise OSError('atomic publication failed')
   state='SUCCESS';result=dict(SHA256=digest,bytes=512)
 except (Exception,KeyboardInterrupt) as ex:
  state='FAILED_POST_SEND' if begun else 'FAILED_PRE_SEND'
  result=dict(error=type(ex).__name__+': '+str(ex),message=('CAPTURE FAILED\nDO NOT RETRY\nPOWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT' if begun else 'CAPTURE NOT SENT; no power cycle required by this attempt'))
 finally:
  if tx is not None:
   try:tx.close()
   except Exception as ex:
    result['close_error']=repr(ex)
    if state!='SUCCESS':state='FAILED_POST_SEND' if begun else 'FAILED_PRE_SEND'
 result.update(status=state,diagnostic_messages_attempted=len(sent),messages=sent,marker_exists=marker.exists(),raw_authorization_attempted=raw_sent,automatic_retries=0,requires_power_cycle=state=='FAILED_POST_SEND')
 return result
def main():
 p=argparse.ArgumentParser(description='Phase62 one-shot host. UNQUALIFIED live operations are locked.');p.add_argument('mode',choices=['list','geometry','capture']);p.add_argument('--port',default='Circuit');p.add_argument('--output',type=Path);p.add_argument('--identity',action='store_true');a=p.parse_args()
 # No WinMM DLL load/enumeration occurs until an explicit live CLI operation.
 path=O/'ctremote_transport.py'
 def transport():
  s=importlib.util.spec_from_file_location('pinned_transport',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 if a.mode=='list':
  print(json.dumps(dict(zip(('inputs','outputs'),transport().ports())),indent=2));return
 gate=O/'preflight-verdict.json';passed=gate.exists() and json.loads(gate.read_text()).get('verdict')=='PASS'
 if not passed:p.exit(2,'UNQUALIFIED: no MIDI access; query/capture locked.\n')
 if a.output is None:p.error('--output is required')
 m=transport();result=run(a.output,O/'HARDWARE-ATTEMPT.json',m.ports,lambda name:Frames(m.Link(name),time.monotonic),port=a.port,geometry_only=a.mode=='geometry',identity=a.identity,preflight_pass=passed,session=secrets.randbelow(127)+1)
 print(json.dumps(result,indent=2));p.exit(0 if result['status'] in ('SUCCESS','GEOMETRY_SAFE','UNSAFE') else 1)
if __name__=='__main__':main()
