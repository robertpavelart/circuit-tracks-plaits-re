"""Offline tests of final CLI/runtime and mock WinMM send. No ports opened."""
from pathlib import Path
import sys,ast,json,tempfile,queue,ctypes
from ctypes import wintypes
from unittest.mock import patch
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
import capture_nor_evidence as C
class Clock:
 def __init__(self):self.t=0.
 def monotonic(self):return self.t
 def time(self):return self.t
 def sleep(self,n):self.t+=n
class Fake:
 def __init__(self,clock,wire,disconnect=False,send_error=False):
  self.clock=clock;self.q=self;self.chunks=[wire[i:i+17] for i in range(0,len(wire),17)];self.sent=[];self.readded=[];self.closed=False;self.disconnect=disconnect;self.send_error=send_error
 def send(self,b):
  self.sent.append(b)
  if self.send_error:raise TimeoutError('synthetic output failure')
 def get(self,timeout):
  if self.chunks:self.clock.t+=0.001;return self.chunks.pop(0),1
  if self.disconnect:raise OSError('synthetic disconnect')
  self.clock.t+=timeout;raise queue.Empty()
 def _readd(self,h):self.readded.append(h)
 def close(self):self.closed=True
def main():
 data=bytes(((i*73)^(i>>1)^0xa6)&255 for i in range(535));normal=C.synthetic_packets(37,data)
 cases={'normal':normal,'silence':[],'TEF identity no completion':[],'TEF target0':normal[:1],'TEF target4':normal[:5],'TEF target7':normal[:8],'missing chunk':normal[:3]+normal[4:],'duplicate chunk':normal[:2]+normal[1:],'reordered chunk':[normal[1],normal[0]]+normal[2:],'duplicate completion':normal+[normal[-1]],'early completion':[normal[-1]],'unexpected sequence':C.synthetic_packets(38,data),'disconnect':normal[:2],'send timeout':[]}
 bad=list(normal);b=bytearray(bad[3]);b[-2]^=1;bad[3]=bytes(b);cases['bad checksum']=bad
 bad=list(normal);b=bytearray(bad[3]);b[8]^=1;b[-9:-1]=C.n32(C.crc32(b[4:-9]));bad[3]=bytes(b);cases['wrong address valid CRC']=bad
 bad=list(normal);bad[-1]=C.packet(37,2,9,(C.crc32(data)^1).to_bytes(4,'big'));cases['whole checksum mismatch']=bad
 rows=[]
 with tempfile.TemporaryDirectory(dir=O) as d:
  root=Path(d)
  for index,(label,frames) in enumerate(cases.items()):
   clock=Clock();link=Fake(clock,b''.join(frames),disconnect=label=='disconnect',send_error=label=='send timeout');created=[]
   def factory():created.append(True);return link
   dest=root/str(index);claim=root/(str(index)+'.attempt')
   result=C.run_capture(dest,factory,clock,claim)
   assert len(link.sent)==1 and link.sent[0]==C.request(37) and link.closed
   if label=='normal':
    assert result['status']=='SUCCESS' and {p.name for p in dest.iterdir()}==set(C.NAMES)
    assert (dest/C.NAMES[0]).read_bytes()==data[:23] and (dest/C.NAMES[1]).read_bytes()==data[23:]
    assert 'LENGTH = 23' in result['message'] and 'LENGTH = 512' in result['message']
   else:assert result['status']=='FAILED' and not dest.exists() and result['message']==C.FAILURE and result['sha256'] is None
   repeat=C.run_capture(root/('retry'+str(index)),factory,clock,claim)
   assert repeat['status']=='FAILED' and len(created)==1 and len(link.sent)==1
   assert not list(root.glob('.nor-staging-*'))
   rows.append(dict(case=label,confidence='PROVEN',result=result,requests=1,second_process_style_attempt_blocked_before_Link_construction=True))
  # Truncated final frame must not publish even though all data chunks arrived.
  clock=Clock();link=Fake(clock,b''.join(normal)[:-1]);dest=root/'truncated'
  assert C.run_capture(dest,lambda:link,clock,root/'truncated.attempt')['status']=='FAILED' and not dest.exists()
  rows.append(dict(case='truncated final frame',confidence='PROVEN',requests=1,accepted_files=0))
  clock=Clock();link=Fake(clock,b''.join(normal));dest=root/'rename'
  with patch.object(C.os,'rename',side_effect=OSError('synthetic rename failure')):r=C.run_capture(dest,lambda:link,clock,root/'rename.attempt')
  assert r['status']=='FAILED' and not dest.exists() and not list(root.glob('.nor-staging-*'))
  rows.append(dict(case='publication failure',confidence='PROVEN',accepted_files=0,requests=1))
  dest=root/'existing';dest.mkdir();(dest/C.NAMES[0]).write_bytes(b'previous evidence');opened=[]
  assert C.run_capture(dest,lambda:opened.append(True),Clock(),root/'existing.attempt')['status']=='FAILED' and not opened
  assert (dest/C.NAMES[0]).read_bytes()==b'previous evidence'
  rows.append(dict(case='existing output',confidence='PROVEN',requests=0,previous_evidence_unchanged=True))
  def unavailable():raise SystemExit('synthetic busy/missing ports')
  assert C.run_capture(root/'unavailable',unavailable,Clock(),root/'unavailable.attempt')['message']==C.FAILURE
  rows.append(dict(case='Link initialization failure',confidence='PROVEN',requests=0))
 # Extract only definitions; never execute WinDLL loading, ports(), or __init__.
 tree=ast.parse((O/'ctremote_transport.py').read_text());nodes=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name in ('MIDIHDR','Link')]
 ns=dict(ctypes=ctypes,wintypes=wintypes,MHDR_DONE=1,_NOR_PENDING_SENDS=[])
 exec(compile(ast.Module(body=nodes,type_ignores=[]),'mock_Link_definitions','exec'),ns)
 class MM:
  def __init__(self,kind):self.kind=kind;self.long=0;self.prepared=0;self.unprepared=0
  def midiOutPrepareHeader(self,*a):self.prepared+=1;return 1 if self.kind=='prepare error' else 0
  def midiOutLongMsg(self,handle,header,n):
   self.long+=1
   if self.kind=='normal':ctypes.cast(header,ctypes.POINTER(ns['MIDIHDR'])).contents.dwFlags=1
   return 1 if self.kind=='send error' else 0
  def midiOutUnprepareHeader(self,*a):self.unprepared+=1;return 0
 for kind in ('normal','prepare error','send error','timeout'):
  clock=Clock();mm=MM(kind);ns['time']=clock;ns['winmm']=mm;ns['_NOR_PENDING_SENDS']=[]
  link=object.__new__(ns['Link']);link.hout=1
  try:link.send(C.request(37));assert kind=='normal'
  except (OSError,TimeoutError):assert kind!='normal'
  assert mm.long<2
  if kind=='timeout':assert len(ns['_NOR_PENDING_SENDS'])==1 and mm.unprepared==0
  rows.append(dict(case='mock WinMM '+kind,confidence='PROVEN',LongMsg_calls=mm.long,buffer_retained=bool(ns['_NOR_PENDING_SENDS']),unprepare_calls=mm.unprepared))
 assert 'ctremote_transport' not in sys.modules,'live transport module imported during tests'
 result=dict(confidence='PROVEN',case_count=len(rows),cases=rows,timeout_seconds=5.0,success_output_files=2,hardware_access=False,MIDI_ports_opened=0,WinMM_functions_called='mock objects only')
 (O/'capture-tool-tests.json').write_text(json.dumps(result,indent=2)+'\n');print('Final capture tool tests PASS:',len(rows))
if __name__=='__main__':main()
