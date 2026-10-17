"""Phase44 F tests. Loads lazy transport; all WinMM entry points are mocks."""
from pathlib import Path
import sys,json,ctypes,tempfile,io,contextlib
from unittest.mock import patch
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
import capture_nor_evidence as C
import ctremote_transport as T
from test_capture_tool import Clock,Fake
class MM:
 def __init__(self,fail=None,ins=None,outs=None):
  self.fail=fail;self.ins=['Circuit Tracks'] if ins is None else ins;self.outs=['Circuit Tracks'] if outs is None else outs;self.calls=[]
 def __getattr__(self,name):
  def call(*a):
   self.calls.append(name)
   if name=='midiInGetNumDevs':return len(self.ins)
   if name=='midiOutGetNumDevs':return len(self.outs)
   if name in ('midiInGetDevCapsW','midiOutGetDevCapsW'):
    cls=T.MIDIINCAPSW if name.startswith('midiIn') else T.MIDIOUTCAPSW
    names=self.ins if name.startswith('midiIn') else self.outs
    ctypes.cast(a[1],ctypes.POINTER(cls)).contents.szPname=names[a[0]]
   if name=='midiOutLongMsg':ctypes.cast(a[1],ctypes.POINTER(T.MIDIHDR)).contents.dwFlags=1
   return 5 if self.fail==name else 0
  return call
rows=[]
def record(name,**kw):rows.append(dict(case=name,confidence='PROVEN',**kw))
def no_send(mm):assert not any(n in mm.calls for n in ('midiOutLongMsg','midiOutShortMsg'))
with tempfile.TemporaryDirectory(dir=O) as tmp:
 root=Path(tmp)
 # Never call real _api: inject mock before any transport inventory/construction.
 mm=MM();T.winmm=mm
 with contextlib.redirect_stdout(io.StringIO()) as out:assert C.main(['ports'])==0
 assert 'Circuit Tracks' in out.getvalue();assert all('Get' in n for n in mm.calls);no_send(mm)
 record('ports CLI mocked enumeration',calls=mm.calls,port_opens=0,diagnostic_requests=0)
 for name,mm in [('no match',MM(ins=['Other'])),('ambiguous input',MM(ins=['Circuit A','Circuit B'])),('ambiguous output',MM(outs=['Circuit A','Circuit B']))]+[(n,MM(fail=n)) for n in ('midiInGetDevCapsW','midiOutGetDevCapsW','midiInOpen','midiOutOpen','midiInPrepareHeader','midiInAddBuffer','midiInStart')]:
  T.winmm=mm;claim=root/(name+'.attempt');dest=root/(name+'.output')
  result=C.run_capture(dest,lambda:T.Link(),Clock(),claim)
  assert result['status']=='PRE-SEND FAILED' and result['device_state']=='NOT REQUESTED'
  assert result['message']==C.PRE_SEND_FAILURE and not claim.exists() and not dest.exists();no_send(mm)
  if 'midiOutOpen' in mm.calls:assert 'midiInClose' in mm.calls
  if 'midiInPrepareHeader' in mm.calls:assert 'midiOutClose' in mm.calls
  record(name,requests=0,marker=False,power_cycle_required=False,resource_calls=mm.calls)
 # Successful opening and idempotent close release all prepared input resources.
 mm=MM();T.winmm=mm;link=T.Link();link.close();calls=list(mm.calls);link.close()
 assert mm.calls==calls and mm.calls.count('midiInUnprepareHeader')==8
 assert mm.calls.count('midiInClose')==1 and mm.calls.count('midiOutClose')==1;no_send(mm)
 record('successful setup close idempotence',requests=0,input_buffers_unprepared=8)
 normal=C.synthetic_packets(37,bytes(i%256 for i in range(535)))
 # Marker absent during opening; fully flushed/durable before send starts.
 clock=Clock();link=Fake(clock,b''.join(normal));claim=root/'barrier.attempt';events=[]
 original_send=link.send
 def checked_send(data):
  assert claim.exists() and json.loads(claim.read_text())['attempt']=='SEND MAY BEGIN';events.append('send');original_send(data)
 link.send=checked_send
 def opened():assert not claim.exists();events.append('open');return link
 result=C.run_capture(root/'barrier.output',opened,clock,claim)
 assert result['status']=='SUCCESS' and events==['open','send'] and claim.exists() and link.closed
 record('commit barrier before request',events=events,requests=1,marker=True)
 # Two processes both pass initial check: loser must close and never transmit.
 clock=Clock();link=Fake(clock,b'');claim=root/'race.attempt'
 def racing_open():claim.write_text('other process committed');return link
 result=C.run_capture(root/'race.output',racing_open,clock,claim)
 assert result['status']=='FAILED' and not link.sent and link.closed and claim.read_text()=='other process committed'
 record('exclusive marker race',requests=0,other_marker_preserved=True,closed=True)
 # Disk persistence failure before send leaves no owned marker and sends nothing.
 clock=Clock();link=Fake(clock,b'');claim=root/'fsync.attempt'
 with patch.object(C.os,'fsync',side_effect=OSError('mock disk failure')):result=C.run_capture(root/'fsync.output',lambda:link,clock,claim)
 assert result['status']=='PRE-SEND FAILED' and not claim.exists() and not link.sent and link.closed
 record('marker fsync pre-send failure',requests=0,marker=False,closed=True)
 # Ambiguous submission errors remain conservative: entered send, do not retry.
 clock=Clock();link=Fake(clock,b'',send_error=True);claim=root/'ambiguous.attempt'
 result=C.run_capture(root/'ambiguous.output',lambda:link,clock,claim)
 assert result['status']=='FAILED' and result['send_may_have_begun'] and claim.exists() and len(link.sent)==1 and link.closed
 assert 'FULL POWER CYCLE REQUIRED' in result['message']
 record('ambiguous send failure',requests=1,marker=True,power_cycle_required=True)
 # Existing output is local validation: no port and no permanent claim.
 claim=root/'existing.attempt';dest=root/'existing.output';dest.mkdir();opened=[]
 result=C.run_capture(dest,lambda:opened.append(1),Clock(),claim)
 assert result['status']=='PRE-SEND FAILED' and not opened and not claim.exists()
 record('existing output rejected before port open',requests=0,marker=False)
assert T.winmm is not None
report=dict(confidence='PROVEN',case_count=len(rows),cases=rows,hardware_access=False,real_WinMM_loaded=False,MIDI_ports_opened=0)
(O/'host-presend-tests.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Phase44 pre-send and mock WinMM tests PASS:',len(rows))
