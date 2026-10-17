"""Offline request writer / saved-transcript receiver; explicit future live mode.
NOT YET HARDWARE-APPROVED. No I/O at import; live is never used in offline tests.
"""
import argparse,json,sys,time,queue
from pathlib import Path
from protocol import request,Receiver,split_stream,acquire,SIG,CMD
class WinMMTransport:
 """Reuse ctremote.Link's existing USB-MIDI implementation, without its commands."""
 def __init__(self,link,timeout=5):self.link=link;self.buffer=b'';self.timeout=timeout
 def send(self,data):self.link.send(data)
 def receive(self):
  until=time.monotonic()+self.timeout
  while time.monotonic()<until:
   if b'\xf7' in self.buffer:
    end=self.buffer.index(b'\xf7');frame,self.buffer=self.buffer[:end+1],self.buffer[end+1:]
    if frame.startswith(SIG) and len(frame)>5 and frame[4]==CMD|64:return frame
    raise ValueError('unexpected SysEx frame; capture not saved')
   try:chunk,header=self.link.q.get(timeout=min(.05,max(0,until-time.monotonic())))
   except queue.Empty:continue
   self.link._readd(header);self.buffer+=chunk
   if len(self.buffer)>4096:raise ValueError('oversized MIDI response')
  raise TimeoutError('diagnostic incomplete; no capture saved; no automatic retry')
def main():
 p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
 a=s.add_parser('request');a.add_argument('output',type=Path);a.add_argument('--token',type=int,default=1)
 a=s.add_parser('receive');a.add_argument('transcript',type=Path);a.add_argument('--outdir',type=Path,required=True);a.add_argument('--token',type=int,required=True);a.add_argument('--origin',required=True)
 a=s.add_parser('live',help='FUTURE APPROVED USE ONLY; opens MIDI ports');a.add_argument('--port',required=True);a.add_argument('--outdir',type=Path,required=True);a.add_argument('--token',type=int,required=True)
 a=p.parse_args()
 if a.command=='request':
  with a.output.open('xb') as f:f.write(request(a.token))
  print('Offline diagnostic request only; no firmware or MIDI transmission')
 elif a.command=='receive':
  r=Receiver(a.token)
  for msg in split_stream(a.transcript.read_bytes()):r.accept(msg)
  print(json.dumps(r.save(a.outdir,origin=a.origin),indent=2))
 else:
  # Deliberately lazy: no device library or port enumeration in any offline mode.
  ref=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
  sys.path.insert(0,str(ref/'tools'));from ctremote import Link,ports
  print('NOT YET HARDWARE-APPROVED: explicit live mode requested')
  ins,outs=ports()
  if any(sum(a.port.lower() in n.lower() for n in names)!=1 for names in (ins,outs)):
   raise SystemExit('Port selector must match exactly one input and one output; no ports opened')
  link=Link(a.port)
  try:r=acquire(WinMMTransport(link),a.token)
  finally:link.close()
  print(json.dumps(r.save(a.outdir,origin='USB MIDI diagnostic capture; firmware/hardware identity requires independent verification'),indent=2))
if __name__=='__main__':main()
