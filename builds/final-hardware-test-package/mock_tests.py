"""Fake clocks/frames only. Never imports a MIDI transport or emulator."""
from pathlib import Path
import json,sys,tempfile,subprocess,hashlib
import live_host as H
from status_protocol import packet
O=Path(__file__).resolve().parent
class Clock:
 def __init__(self):self.now=0.
 def __call__(self):return self.now
class Fake:
 def __init__(self,c,g,r,mode=''):self.c=c;self.g=g;self.r=r;self.events=[];self.sent=[];self.buffer=b'';self.mode=mode
 def send(self,b):
  self.sent.append(bytes(b))
  if self.mode=='disconnect':raise OSError('fake disconnect')
  if self.mode=='send-timeout' and b[4]==15:self.c.now+=3
  self.events=list(self.g if b[4]==14 else self.r)
 def receive(self,deadline):
  if self.events:
   x=self.events.pop(0)
   if isinstance(x,Exception):raise x
   return x
  if self.mode=='premature':raise TimeoutError('early EOS')
  if self.mode=='partial':self.buffer=b'\xf0'
  self.c.now=deadline;raise TimeoutError('absolute deadline')
 def close(self):pass
def frame(kind,index,address,total,data):
 b=H.C.SIG+bytes((0x4d,37,kind,index))+H.C.n32(address)+H.C.n32(total)+bytes((len(data),))+bytes(x for v in data for x in (v>>4,v&15))
 return b+H.C.n32(H.C.crc(b[4:]))+b'\xf7'
def main():
 geo=next(bytes.fromhex(x) for x in json.loads((O/'geometry-fixture.json').read_text())['frames'] if bytes.fromhex(x)[4]==0x4e)
 payload=bytes((i*73^i>>1^0xa6)&255 for i in range(512))
 raw=[packet(37,6)]+[frame(1,i+1,0x82000+64*i,512,payload[i*64:(i+1)*64]) for i in range(8)]+[frame(2,9,0x82000,512,H.C.crc(payload).to_bytes(4,'big')),packet(37,7)]
 good=[packet(37,4),geo];rows=[]
 # Keep sandbox test IO inside the package; no device/transport handles exist.
 with tempfile.TemporaryDirectory(prefix='phase68-mock-',dir=O) as td:
  root=Path(td)
  assert root.resolve().parent==O.resolve()
  def case(name,g=good,r=raw,expected='SUCCESS',mode='',only=False,approve=True,inventory=(['Circuit Tracks'],['Circuit Tracks']),identity=False):
   d=root/name;d.mkdir();clock=Clock();f=Fake(clock,g,r,mode);marker=d/'attempt.json'
   result=H.run(d/'evidence',marker,lambda:inventory,lambda p:f,clock,geometry_only=only,preflight_pass=True,approve=lambda *a:approve,identity=identity)
   assert result['status']==expected,(name,result)
   assert result['automatic_retries']==0
   if expected=='SUCCESS':assert (d/'evidence/qspi_00082000_000821ff.bin').read_bytes()==payload
   else:assert not (d/'evidence').exists()
   if f.sent:
    assert marker.exists(),name
    again=H.run(d/'other',marker,lambda:(_ for _ in ()).throw(AssertionError('retry inventory')),lambda _:None,clock,preflight_pass=True)
    assert again['diagnostic_messages_attempted']==0
   if expected=='FAILED':assert 'DO NOT RETRY' in result['message'] and result['requires_power_cycle']
   rows.append(dict(case=name,passed=True,status=expected,messages=len(f.sent),marker_retained=marker.exists(),automatic_retries=0,accepted_file=expected=='SUCCESS'))
  case('full exact success')
  ident=bytes(range(23));combined=ident+payload
  both=[packet(37,6),frame(0,0,0x81000,535,ident)]+[frame(1,i+1,0x82000+64*i,535,payload[i*64:(i+1)*64]) for i in range(8)]+[frame(2,9,0x81000,535,H.C.crc(combined).to_bytes(4,'big')),packet(37,7)]
  case('separately selected identity plus coefficients',r=both,identity=True)
  case('geometry only',only=True,expected='READY')
  case('operator declines',approve=False,expected='FAILED')
  for code,label in ((1,'NOT_READY'),(2,'INVALID'),(3,'UNSAFE')):case(label,g=[packet(37,code)],expected=label)
  case('FAILED status',g=[packet(37,5)],expected='FAILED')
  case('silence',g=[],expected='FAILED')
  case('send disconnect',mode='disconnect',expected='FAILED')
  case('input disconnect',r=[OSError('fake input loss')],expected='FAILED')
  case('auth send timeout',mode='send-timeout',expected='FAILED')
  case('premature EOS',mode='premature',expected='FAILED')
  case('trailing partial',mode='partial',expected='FAILED')
  case('corrupt CRC',r=raw[:2]+[raw[2][:-3]+bytes([raw[2][-3]^1])+raw[2][-2:]]+raw[3:],expected='FAILED')
  case('duplicate chunk',r=raw[:3]+raw[2:],expected='FAILED')
  case('missing chunk',r=raw[:3]+raw[4:],expected='FAILED')
  case('reorder',r=raw[:1]+[raw[2],raw[1]]+raw[3:],expected='FAILED')
  case('duplicate completion',r=raw[:-1]+raw[-2:],expected='FAILED')
  case('completion early',r=[raw[0],raw[-2],raw[-1]],expected='FAILED')
  case('duplicate success',r=raw+[raw[-1]],expected='FAILED')
  case('raw before authorized',r=raw[1:],expected='FAILED')
  case('missing success',r=raw[:-1],expected='FAILED')
  case('stale session',g=[packet(38,4)],expected='FAILED')
  case('ambiguous ports',inventory=(['Circuit A','Circuit B'],['Circuit']),expected='FAILED_PRE_SEND')
  for i in (0,4,7):
   case(f'truncated after {i}',r=raw[:i+2],expected='FAILED')
   case(f'error at {i}',r=raw[:i+1]+[packet(37,5)],expected='FAILED')
  locked=H.run(root/'locked',root/'marker',lambda:(_ for _ in ()).throw(AssertionError('locked inventory')),lambda _:None)
  assert locked['diagnostic_messages_attempted']==0
  # The actual CLI list must stop before importing/enumerating a transport.
  cp=subprocess.run([sys.executable,'-B',str(O/'live_host.py'),'list'],capture_output=True,text=True)
  assert cp.returncode==2 and 'no MIDI enumeration/open/send' in cp.stderr
  rows.append(dict(case='default CLI and engine locks',passed=True,status='LOCKED',messages=0))
 result=dict(passed=True,version=H.VERSION,cases=rows,hardware_access=False,MIDI_ports_opened=0,transport_imported='frozen_transport' in sys.modules)
 assert not result['transport_imported'];(O/'host-mock-results.json').write_text(json.dumps(result,indent=2)+'\n');print('Final mock checks PASS',len(rows))
if __name__=='__main__':main()
