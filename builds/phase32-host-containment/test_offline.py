"""Deterministic fake WinMM queue/clock. Never imports/opens a device library."""
from containment import *
import json,queue,types,importlib
from unittest.mock import patch
from protocol import synthetic_packets,packet,crc32,n32

O=Path(__file__).resolve().parent
class Clock:
 def __init__(self):self.now=0.0
 def monotonic(self):return self.now
class FakeQueue:
 def __init__(self,clock,events):self.clock=clock;self.events=list(events)
 def get(self,timeout):
  until=self.clock.now+timeout
  if self.events and self.events[0][0]<=until:
   at,data=self.events.pop(0);self.clock.now=max(self.clock.now,at);return data,object()
  self.clock.now=until;raise queue.Empty
class FakeLink:
 def __init__(self,clock,events):self.q=FakeQueue(clock,events);self.sent=[];self.readds=0
 def send(self,data):self.sent.append(bytes(data))
 def _readd(self,header):self.readds+=1 # receive-buffer acknowledgement only, not a device command

checks=[]
def ck(name,ok):assert ok,name;checks.append(name)
token=37;payload=bytes(((i*73)^(i>>1)^0xa6)&255 for i in range(512))
good=synthetic_packets(token,payload)
def events(frames):return [(0.1*(i+1),f) for i,f in enumerate(frames)]
cases=[('A complete normal stream',good)]
for label,c in (('B',0),('C',4),('D',7)):
 cases.append((f'{label} truncated after completed chunk {c}',good[:c+1]))
for label,c in (('E',0),('F',4),('G',7)):
 # Explicitly synthetic error kind2: phase31 found no real device error packet.
 cases.append((f'{label} synthetic TEF indication at chunk {c}',good[:c]+[packet(token,2,c,b'TEF')]))
bad=bytearray(good[3]);bad[25]^=1
cases.extend([
 ('H corrupted packet CRC',good[:3]+[bytes(bad)]+good[4:]),
 ('I duplicate chunk',good[:3]+[good[2]]+good[3:]),
 ('J missing chunk',good[:4]+good[5:]),
 ('K reordered chunk',good[:2]+[good[3],good[2]]+good[4:]),
 ('L duplicate completion packet',good+[good[-1]]),
 ('M completion before all chunks',good[:4]+[good[-1]]),
 ('N total silence',[]),
 ('whole capture CRC incorrect',good[:-1]+[packet(token,1,8,(crc32(payload)^1).to_bytes(4,'big'))]),
 ('completion missing',good[:-1]),
 ('wrong token',synthetic_packets(38,payload)),
 ('partial trailing SysEx after valid completion',good+[b'\xf0\x7dCT\x4d']),
])
for c in (0,4,7):cases.append((f'actual TEF is silent at failed chunk {c}',good[:c]))
for field,offset in (('absolute address',8),('total size',16)):
 value=bytearray(good[0]);value[offset]^=1;value[-9:-1]=n32(crc32(value[4:-9]))
 cases.append((f'wrong {field} with valid packet CRC',[bytes(value)]+good[1:]))
cases.append(('63-byte chunk with valid CRC',[packet(token,0,0,payload[:63])]+good[1:]))

results=[]
receiver_module=importlib.import_module('receiver')
for name,frames in cases:
 clock=Clock();schedule=events(frames)
 link=FakeLink(clock,schedule);transport=WinMMTransport(link)
 lease=DeviceLease(transport,clock);session=OneShotCapture(lease,token)
 with tempfile.TemporaryDirectory(dir=O,prefix='phase32-') as td:
  directory=Path(td);target=directory/NAME;publication=[]
  real_rename=os.rename
  def record_rename(source,dest):
   ck(name+' no final before atomic rename',not target.exists())
   ck(name+' staging already complete',Path(source).read_bytes()==payload)
   publication.append(dict(at=clock.now,bytes=Path(source).stat().st_size))
   return real_rename(source,dest)
  with patch.object(receiver_module,'time',clock),patch('containment.os.rename',record_rename):
   result=session.run(directory)
  success=name.startswith('A ')
  ck(name+' expected terminal state',(result['status']=='SUCCESS')==success)
  ck(name+' bounded virtual time',clock.now<=TIMEOUT_SECONDS+1e-9)
  ck(name+' exactly one fixed request',link.sent==[request(token)])
  ck(name+' final exists only on success',target.exists()==success)
  ck(name+' atomic publication only on success',len(publication)==int(success))
  ck(name+' no staging residue',not list(directory.glob('.qspi-staging-*')))
  ck(name+' decoder/buffer discarded',session._receiver is None and transport.buffer==b'')
  if success:
   ck(name+' exact 512 and SHA',target.read_bytes()==payload and result['sha256']==hashlib.sha256(payload).hexdigest())
   ck(name+' full trailing observation window',clock.now==TIMEOUT_SECONDS)
  else:
   ck(name+' quarantine and clear message',result['device_state']=='POWER-CYCLE REQUIRED' and result['message']==FAILURE_MESSAGE)
   ck(name+' no accepted digest',result['sha256'] is None)
  for candidate in (session,OneShotCapture(lease,38)):
   try:candidate.run(directory)
   except RuntimeError:pass
   else:raise AssertionError(name+' reuse was accepted')
  try:DeviceLease(transport,clock)
  except RuntimeError:pass
  else:raise AssertionError(name+' same transport re-leased')
  ck(name+' both same-session retry paths suppressed',link.sent==[request(token)])
  results.append(dict(case=name,confidence='PROVEN',result=result,virtual_elapsed=clock.now,sent_requests=len(link.sent),
   wire_bytes_sent=sum(map(len,link.sent)),final_exists=target.exists(),accepted_bytes=target.stat().st_size if target.exists() else 0,
   published=publication,remaining_input_events=len(link.q.events),output_origin='SYNTHETIC, not device evidence'))

# One absolute deadline: a continuing trickle cannot extend the session.
clock=Clock();link=FakeLink(clock,[(1.0+i*.9,f) for i,f in enumerate(good)])
lease=DeviceLease(WinMMTransport(link),clock)
with tempfile.TemporaryDirectory(dir=O,prefix='phase32-slow-') as td,patch.object(receiver_module,'time',clock):
 result=OneShotCapture(lease,token).run(td)
 ck('trickle cannot extend absolute deadline',result['status']=='FAILED' and clock.now==5.0 and not (Path(td)/NAME).exists() and len(link.sent)==1)
results.append(dict(case='absolute deadline despite trickle',confidence='PROVEN',result=result,virtual_elapsed=clock.now,sent_requests=1,final_exists=False))

for label,schedule,expected in [
 ('fragmented valid stream',[(.01*(j+1),data) for j,data in enumerate([f[k:k+13] for f in good for k in range(0,len(f),13)])],True),
 ('coalesced valid stream',[(.1,b''.join(good))],True),
 ('coalesced duplicate completion',[(.1,b''.join(good+[good[-1]]))],False),
 ('late duplicate completion inside deadline',events(good)+[(4.99,good[-1])],False),
 ('partial frame total silence thereafter',[(.1,good[0][:19])],False),
]:
 clock=Clock();link=FakeLink(clock,schedule);lease=DeviceLease(WinMMTransport(link),clock)
 with tempfile.TemporaryDirectory(dir=O,prefix='phase32-framing-') as td,patch.object(receiver_module,'time',clock):
  session=OneShotCapture(lease,token);result=session.run(td);target=Path(td)/NAME
  ck(label+' terminal outcome',(result['status']=='SUCCESS')==expected)
  ck(label+' file acceptance',target.exists()==expected and (not expected or target.read_bytes()==payload))
  ck(label+' one request and bounded',link.sent==[request(token)] and clock.now<=5.0+1e-9)
  ck(label+' no decoder or staging',session._receiver is None and not list(Path(td).glob('.qspi-staging-*')))
  results.append(dict(case=label,confidence='PROVEN',result=result,virtual_elapsed=clock.now,sent_requests=1,final_exists=target.exists(),output_origin='SYNTHETIC, not device evidence'))

# Existing accepted captures must never be deleted/overwritten on a failed run.
clock=Clock();link=FakeLink(clock,[]);lease=DeviceLease(WinMMTransport(link),clock)
with tempfile.TemporaryDirectory(dir=O,prefix='phase32-existing-') as td:
 target=Path(td)/NAME;target.write_bytes(b'existing capture')
 result=OneShotCapture(lease,token).run(td)
 ck('existing output preserved and no request issued',result['status']=='FAILED' and target.read_bytes()==b'existing capture' and not link.sent)

# Publication failure must not leave a partial final file or reusable session.
clock=Clock();link=FakeLink(clock,events(good));lease=DeviceLease(WinMMTransport(link),clock)
with tempfile.TemporaryDirectory(dir=O,prefix='phase32-io-') as td,patch.object(receiver_module,'time',clock),patch('containment.os.rename',side_effect=OSError('injected publication failure')):
 session=OneShotCapture(lease,token);result=session.run(td)
 ck('publication failure removes staged data',result['status']=='FAILED' and not (Path(td)/NAME).exists() and not list(Path(td).iterdir()) and len(link.sent)==1)

result=dict(confidence='PROVEN',scope='Offline fake transport/clock; unchanged phase27 Receiver and WinMM framing; no hardware I/O',
 timeout_seconds=TIMEOUT_SECONDS,timeout_model='Absolute whole-attempt observation deadline including trailing frames; deadline never renewed',
 checks=checks,cases=results,stream_cases=len(cases),passed_assertions=len(checks),only_valid_stream_published=True,
 scenario_groups=len(results),filesystem_checks=2,
 accepted_sha256=hashlib.sha256(payload).hexdigest(),synthetic_origin=True,test_outputs='Isolated temporary directories removed after assertions; no authentic evidence captured',
 automatic_retries=0,device_cleanup_commands=0,hardware_access=False,firmware_generated=False,verdict='PASS')
(O/'test-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','cases')},indent=2))
