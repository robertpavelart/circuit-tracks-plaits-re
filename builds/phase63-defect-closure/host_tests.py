"""Deterministic fake transport only; replies include actual native packets."""
from pathlib import Path
import sys,json,tempfile
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
import live_host as H
import native_regression as T
from status_protocol import packet
class Clock:
 def __init__(self):self.now=0.
 def __call__(self):return self.now
class Fake:
 def __init__(self,clock,geo,raw,mode='normal'):self.clock=clock;self.geo=geo;self.raw=raw;self.buffer=b'';self.events=[];self.sent=[];self.mode=mode
 def send(self,b):
  self.sent.append(b)
  if self.mode=='disconnect':raise OSError('disconnect')
  self.events=list(self.geo if b[4]==14 else self.raw)
  if self.mode=='auth-send-timeout' and b[4]==15:self.clock.now+=3
 def receive(self,deadline):
  if self.events:
   b=self.events.pop(0)
   if isinstance(b,Exception):raise b
   return b
  if self.mode=='premature':raise TimeoutError('premature')
  if self.mode=='partial':self.buffer=b'\xf0'
  self.clock.now=deadline;raise TimeoutError('quiet deadline')
 def close(self):pass
def main():
 n=T.N().mounted().export();geom=n.frames[0];n.authorize();geo=[n.status_frames[0],geom];raw=[n.status_frames[1]]+n.frames[1:]+[n.status_frames[2]]
 root=Path(tempfile.mkdtemp(prefix='host-mocks-',dir=O));rows=[]
 def case(name,g=geo,r=raw,expected='SUCCESS',count=2,mode='normal',only=False,validator=H.C.geometry_response,ports=(['Circuit'],['Circuit']),identity=False):
  d=root/name;d.mkdir();c=Clock();f=Fake(c,g,r,mode);marker=d/'ATTEMPT.json'
  result=H.run(d/'evidence',marker,lambda:ports,lambda p:f,c,geometry_only=only,validator=validator,identity=identity,preflight_pass=True)
  assert result['status']==expected,(name,result)
  assert len(f.sent)==count and result['automatic_retries']==0
  if expected=='SUCCESS':assert (d/'evidence/qspi_00082000_000821ff.bin').read_bytes()==T.ns['payload'][23:]
  else:assert not (d/'evidence').exists()
  if expected=='FAILED':assert marker.exists() and result['requires_power_cycle']
  if count and expected!='NOT_READY':
   second=H.run(d/'second',marker,lambda:(_ for _ in ()).throw(AssertionError('retry inventory')),lambda p:f,c,preflight_pass=True)
   assert second['diagnostic_messages_attempted']==0
  if expected=='NOT_READY':
   assert not marker.exists() and not result['raw_authorization_attempted']
   f.geo=geo;f.raw=raw
   second=H.run(d/'second',marker,lambda:ports,lambda p:f,c,preflight_pass=True)
   assert second['status']=='SUCCESS' and len(f.sent)==3
  rows.append(dict(case=name,passed=True,result=result))
 case('full native READY AUTHORIZED SUCCESS')
 case('NOT_READY can query again',[packet(37,1)],expected='NOT_READY',count=1)
 for code,name in [(2,'INVALID'),(3,'UNSAFE'),(5,'FAILED')]:case(name,[packet(37,code)],expected=name,count=1)
 case('READY geometry only',expected='READY',count=1,only=True)
 case('missing initial status',[geom],expected='FAILED',count=1)
 case('malformed status',[b'bad'],expected='FAILED',count=1)
 bad=bytearray(packet(37,4));bad[37]^=1;case('corrupt status CRC',[bytes(bad)],expected='FAILED',count=1)
 case('stale session',[packet(38,4)],expected='FAILED',count=1)
 case('stale epoch',[packet(37,4,2)],expected='FAILED',count=1)
 case('silence',[],expected='FAILED',count=1)
 case('disconnect',expected='FAILED',count=1,mode='disconnect')
 case('input disconnect',r=[OSError('input disconnect')],expected='FAILED')
 case('duplicate NOT_READY',[packet(37,1)]*2,expected='FAILED',count=1)
 case('duplicate AUTHORIZED',r=raw[:1]+raw,expected='FAILED')
 case('duplicate SUCCESS',r=raw+raw[-1:],expected='FAILED')
 case('duplicate completion',r=raw[:-1]+raw[-2:],expected='FAILED')
 case('missing chunk',r=raw[:3]+raw[4:],expected='FAILED')
 case('reorder',r=raw[:1]+[raw[2],raw[1]]+raw[3:],expected='FAILED')
 case('raw before AUTHORIZED',r=raw[1:],expected='FAILED')
 case('SUCCESS before completion',r=raw[:1]+raw[-1:],expected='FAILED')
 case('missing SUCCESS',r=raw[:-1],expected='FAILED')
 case('FAILED after authorization',r=raw[:1]+[packet(37,5)],expected='FAILED')
 case('premature EOS',mode='premature',expected='FAILED')
 case('partial trailing frame',mode='partial',expected='FAILED')
 case('auth send timeout',mode='auth-send-timeout',expected='FAILED')
 def unsafe(b,s):
  e,g,d=H.C.geometry_response(b,s);d['targets_reachable']['0x82000']=True;return e,g,d
 case('host mapping veto',validator=unsafe,expected='UNSAFE',count=1)
 case('no ports',ports=([],[]),expected='FAILED_PRE_SEND',count=0)
 case('ambiguous ports',ports=(['Circuit A','Circuit B'],['Circuit']),expected='FAILED_PRE_SEND',count=0)
 nn=T.N().mounted().export();nn.authorize(True);case('optional identity',[nn.status_frames[0],nn.frames[0]],[nn.status_frames[1]]+nn.frames[1:]+[nn.status_frames[2]],identity=True)
 locked=H.run(root/'locked',root/'locked-marker',lambda:(_ for _ in ()).throw(AssertionError('locked inventory')),lambda _:None)
 assert locked['status']=='FAILED_PRE_SEND' and locked['diagnostic_messages_attempted']==0
 rows.append(dict(case='live lock',passed=True,result=locked))
 (O/'host-tests.json').write_text(json.dumps(dict(confidence='PROVEN',passed=True,cases=rows,hardware_access=False,MIDI_ports_opened=0,candidate_sha256=T.ns['meta']['BIN_sha256']),indent=2)+'\n');print('Host mocks PASS',len(rows))
if __name__=='__main__':main()
