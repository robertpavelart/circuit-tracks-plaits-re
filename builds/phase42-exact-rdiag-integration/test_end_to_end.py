"""Native exact candidate USB bytes -> ctremote-compatible framing -> files."""
from test_native import *
from host import OneShot,DeviceLease,FramedTransport,queue
from test_offline import Clock
import ast

class FakeLink:
 def __init__(self,clock,wire):
  self.clock=clock;self.q=self;self.chunks=[];self.sent=[];self.readded=[]
  at=0
  for n in [1,2,17,3,128,5,64]*100:
   if at>=len(wire):break
   self.chunks.append(wire[at:at+n]);at+=n
  assert at>=len(wire)
 def send(self,data):self.sent.append(data)
 def get(self,timeout):
  if self.chunks:
   self.clock.t+=0.001;return self.chunks.pop(0),len(self.chunks)
  self.clock.t+=timeout;raise queue.Empty()
 def _readd(self,h):self.readded.append(h)

def main():
 # Reuse only the pinned reference's pure request/reply helpers. Loading its
 # WinMM module or Link constructor is neither needed nor permitted here.
 tree=ast.parse((O/'source/tools/ctremote.py').read_text());ns={'SIG':(240,125,67,84),'PAD':232}
 funcs=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('build','parse')]
 exec(compile(ast.Module(body=funcs,type_ignores=[]),'pinned_ctremote_protocol','exec'),ns)
 m=Exact();m.start();finish(m);assert ns['build'](13,37)==request(37)
 raw=b''.join(m.usb_bytes);wire=b''.join(raw[i+1:i+1+{4:3,5:1,6:2,7:3}[raw[i]&15]] for i in range(0,len(raw),4))
 assert wire==b''.join(m.frames) and all(ns['parse'](f,13,37) is not None for f in m.frames)
 rows=[]
 for label,data in [('normal',wire),('truncated',wire[:-1]),('duplicate completion',wire+m.frames[-1])]:
  c=Clock();link=FakeLink(c,data);t=FramedTransport(link,c);session=OneShot(DeviceLease(t,c),37);dest=O/('synthetic-capture' if label=='normal' else 'rejected-'+label.replace(' ','-'))
  result=session.run(dest);assert len(link.sent)==1
  if label=='normal':
   assert result['status']=='SUCCESS'
   for name,expect in zip(('nor_00081000_00081016.bin','nor_00082000_000821ff.bin'),(m.payload[:23],m.payload[23:])):assert (dest/name).read_bytes()==expect
  else:assert result['status']=='FAILED' and not dest.exists()
  rows.append(dict(case=label,confidence='PROVEN',result=result,bytes_from_native_USB=True,requests=1,host_input_buffers_returned=len(link.readded)))
 (O/'end-to-end-results.json').write_text(json.dumps(dict(confidence='PROVEN',origin='SYNTHETIC emulator bytes, NOT device evidence',reference_ctremote_build_parse_match=True,cases=rows,hardware_access=False),indent=2)+'\n');print('End-to-end cases PASS:',len(rows))
if __name__=='__main__':main()
