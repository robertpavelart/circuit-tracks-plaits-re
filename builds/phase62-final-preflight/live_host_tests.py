"""Fake inventory, link and monotonic time. Never invokes WinMM/list CLI."""
from pathlib import Path
import sys,json,tempfile
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];sys.path.insert(0,str(O));import live_host as H
sys.path.insert(0,str(R/'builds/phase61-final-geometry-gated-candidate'));import native_tests as T
c=json.loads((O/'frozen-candidate-identity.json').read_text());T.image=T.decode((O/(c['candidate']+'.syx')).read_bytes())[0]
class Clock:
 def __init__(self):self.now=0.
 def __call__(self):return self.now
class Fake:
 def __init__(self,clock,geometry,raw,mode='normal'):self.clock=clock;self.geometry=geometry;self.raw=list(raw);self.events=[];self.buffer=b'';self.mode=mode;self.sent=[];self.closed=False
 def send(self,b):
  self.sent.append(b)
  if self.mode=='send-disconnect':raise OSError('driver disconnected')
  self.events=[self.geometry] if b[4]==14 else list(self.raw)
  if self.mode=='malformed-auth-rejected' and b[4]==15:self.events=[]
  if self.mode=='auth-send-timeout' and b[4]==15:self.clock.now+=3
 def receive(self,deadline):
  if self.mode=='geometry-silence' and len(self.sent)==1:self.clock.now=deadline;raise TimeoutError('silence')
  if self.events:
   b=self.events.pop(0)
   if isinstance(b,Exception):raise b
   return b
  if self.mode=='premature-boundary':raise TimeoutError('premature EOS timeout')
  if self.mode=='trailing-partial':self.buffer=b'\xf0'
  self.clock.now=deadline;raise TimeoutError('absolute quiet boundary')
 def close(self):self.closed=True
def main():
 n=T.N().mounted().export();geom=n.frames[0];n.authorize();frames=n.frames[1:]
 root=Path(tempfile.mkdtemp(prefix='live-host-mocks-',dir=O));rows=[]
 def case(name,*,mode='normal',geo=geom,raw=frames,ports=(['Circuit'],['Circuit']),open_error=False,preparation_timeout=False,geometry_only=False,validator=H.C.geometry_response,expected='SUCCESS',count=2,identity=False):
  d=root/name;d.mkdir();clock=Clock();f=Fake(clock,geo,raw,mode);calls=[]
  def inventory():calls.append('inventory');return ports
  def opener(port):
   calls.append('open')
   if open_error:raise OSError('injected open failure')
   if preparation_timeout:clock.now=11
   return f
  result=H.run(d/'evidence',d/'ATTEMPT.json',inventory,opener,clock,geometry_only=geometry_only,identity=identity,preflight_pass=True,validator=validator)
  assert result['status']==expected,(name,result)
  assert len(f.sent)==result['diagnostic_messages_attempted']==count
  assert result['marker_exists']==(count>0)
  if expected!='SUCCESS':assert not (d/'evidence').exists()
  else:assert (d/'evidence/qspi_00082000_000821ff.bin').read_bytes()==T.payload[23:]
  if expected=='FAILED_POST_SEND':assert result['requires_power_cycle'] and result['automatic_retries']==0
  rows.append(dict(case=name,result=result,port_calls=calls,passed=True))
  if count:
   second=H.run(d/'second',d/'ATTEMPT.json',lambda:(_ for _ in ()).throw(AssertionError('second launch accessed MIDI')),opener,clock,preflight_pass=True)
   assert second['diagnostic_messages_attempted']==0 and second['marker_exists']
 case('no-device',ports=([],[]),expected='FAILED_PRE_SEND',count=0)
 case('ambiguous-device',ports=(['Circuit1','Circuit2'],['Circuit']),expected='FAILED_PRE_SEND',count=0)
 case('open-failure',open_error=True,expected='FAILED_PRE_SEND',count=0)
 case('timeout-before-send',preparation_timeout=True,expected='FAILED_PRE_SEND',count=0)
 case('timeout-after-send',mode='geometry-silence',expected='FAILED_POST_SEND',count=1)
 case('malformed-geometry',geo=b'bad',expected='FAILED_POST_SEND',count=1)
 bad=bytearray(geom);bad[13]=2;bad[-9:-1]=H.C.n32(H.C.crc(bad[4:-9]))
 case('stale-epoch',geo=bytes(bad),expected='FAILED_POST_SEND',count=1)
 def unsafe(b,s):
  e,g,d=H.C.geometry_response(b,s);d['targets_reachable']['0x82000']=True;return e,g,d
 case('geometry-policy-unsafe',validator=unsafe,expected='UNSAFE',count=1)
 case('safe-geometry-only-stop',geometry_only=True,expected='GEOMETRY_SAFE',count=1)
 case('safe-full-capture')
 case('duplicate-packet',raw=frames[:1]+frames,expected='FAILED_POST_SEND')
 case('missing-packet',raw=frames[:3]+frames[4:],expected='FAILED_POST_SEND')
 case('out-of-order',raw=[frames[1],frames[0]]+frames[2:],expected='FAILED_POST_SEND')
 case('duplicate-completion',raw=frames+[frames[-1]],expected='FAILED_POST_SEND')
 case('MIDI-disconnect',mode='send-disconnect',expected='FAILED_POST_SEND',count=1)
 case('USB-input-disconnect',raw=[OSError('USB disconnected')],expected='FAILED_POST_SEND')
 case('end-boundary-premature-timeout',mode='premature-boundary',expected='FAILED_POST_SEND')
 case('end-boundary-trailing-partial',mode='trailing-partial',expected='FAILED_POST_SEND')
 case('authorization-driver-timeout',mode='auth-send-timeout',expected='FAILED_POST_SEND')
 case('malformed-authorization-rejected-no-reply',mode='malformed-auth-rejected',expected='FAILED_POST_SEND')
 nn=T.N().mounted().export();gg=nn.frames[0];nn.authorize(True);case('optional-identity',geo=gg,raw=nn.frames[1:],identity=True)
 # Actual native non-VALID states have NO wire status. They are tested as
 # silence, not replaced by fictional NOT_READY/INVALID/FAILED packets.
 for state in ('NOT_READY','INVALID','FAILED'):case('actual-device-'+state+'-is-silence',mode='geometry-silence',expected='FAILED_POST_SEND',count=1)
 locked=H.run(root/'locked-output',root/'locked-marker',lambda:(_ for _ in ()).throw(AssertionError('locked path touched MIDI')),lambda _:None)
 assert locked['status']=='FAILED_PRE_SEND' and not locked['marker_exists'] and locked['diagnostic_messages_attempted']==0
 rows.append(dict(case='unqualified-CLI-core-lock',result=locked,passed=True))
 result=dict(confidence='PROVEN',candidate_sha256=c['BIN_sha256'],host_cases_passed=True,cases=rows,protocol_state_distinction_gate='FAIL: actual device has no NOT_READY/INVALID/FAILED reply; no mock can close that firmware gap',unsafe_case_scope='Injected independent policy veto, not a claim compact valid D4000 geometry can overlap lower targets',live_hardware_tool_qualified=False,hardware_access=False,MIDI_ports_opened=0)
 (O/'live-host-tests.json').write_text(json.dumps(result,indent=2)+'\n');print('Host mock assertions PASS',len(rows),'; actual status protocol gate FAIL')
if __name__=='__main__':main()
