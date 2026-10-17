"""Fixed-range diagnostic protocol. Pure offline code; never opens MIDI ports."""
from pathlib import Path
import hashlib,json
SIG=b'\xf0\x7dCT'; CMD=13; ADDRESS=0x82000; SIZE=512; PAD=232
NAME='qspi_00082000_000821ff.bin'
def crc32(data):
 c=0xffffffff
 for v in data:
  c^=v<<24
  for _ in range(8):c=((c<<1)^ (0x04c11db7 if c&0x80000000 else 0))&0xffffffff
 return c
def nib(v):return bytes(x for b in v for x in (b>>4,b&15))
def un(v):
 if len(v)%2 or any(x>15 for x in v):raise ValueError('invalid nibbles')
 return bytes((v[i]<<4)|v[i+1] for i in range(0,len(v),2))
def n32(v):return nib(v.to_bytes(4,'big'))
def request(token):
 if not 0<=token<128:raise ValueError('token')
 b=SIG+bytes([CMD,token])+n32(ADDRESS)+n32(SIZE)+b'\x01'
 return b+bytes(PAD-len(b)-1)+b'\xf7'
def packet(token,kind,index,payload):
 """Synthetic test encoder; device implementation is independent ARM code."""
 addr=ADDRESS+64*index if kind==0 else ADDRESS
 b=SIG+bytes([CMD|64,token,kind,index])+n32(addr)+n32(SIZE)+bytes([len(payload)])+nib(payload)
 return b+n32(crc32(b[4:]))+b'\xf7'
def synthetic_packets(token,data):
 if len(data)!=SIZE:raise ValueError('512 required')
 return [packet(token,0,i,data[64*i:64*(i+1)]) for i in range(8)]+[packet(token,1,8,crc32(data).to_bytes(4,'big'))]
class Receiver:
 def __init__(self,token):self.token=token;self.next=0;self.parts=[];self.done=False;self.frames=[]
 def accept(self,msg):
  if self.done:raise ValueError('packet after completion')
  if len(msg)<34 or msg[:4]!=SIG or msg[4:6]!=bytes([CMD|64,self.token]) or msg[-1]!=247 or any(v>=128 for v in msg[1:-1]):raise ValueError('framing/token')
  kind,index=msg[6:8];addr=int.from_bytes(un(msg[8:16]),'big');total=int.from_bytes(un(msg[16:24]),'big');n=msg[24]
  if len(msg)!=34+2*n or total!=SIZE:raise ValueError('length/total')
  body=un(msg[25:25+2*n]);expected=int.from_bytes(un(msg[-9:-1]),'big')
  if crc32(msg[4:-9])!=expected:raise ValueError('packet CRC')
  if index!=self.next:raise ValueError('order/duplicate/missing')
  if kind==0 and index<8 and n==64 and addr==ADDRESS+64*index:
   self.parts.append(body);self.next+=1
  elif kind==1 and index==8 and n==4 and addr==ADDRESS and self.next==8:
   if int.from_bytes(body,'big')!=crc32(b''.join(self.parts)):raise ValueError('whole capture CRC')
   self.done=True;self.next+=1
  else:raise ValueError('kind/index/address/payload size')
  self.frames.append(bytes(msg))
 def result(self):
  if not self.done:raise ValueError('incomplete capture')
  b=b''.join(self.parts)
  if len(b)!=SIZE:raise ValueError('capture size')
  return b
 def save(self,directory,*,origin):
  b=self.result();p=Path(directory);p.mkdir(parents=True,exist_ok=True);target=p/NAME
  if target.exists():raise FileExistsError(target)
  target.write_bytes(b)
  meta=dict(origin=origin,address=hex(ADDRESS),length=SIZE,sha256=hashlib.sha256(b).hexdigest(),
   protocol='QSPI82000-v1',token=self.token,packets=len(self.frames),payload_crc32_mpeg2=hex(crc32(b)),
   confidence='UNKNOWN',note='Protocol integrity alone does not prove hardware/source authenticity')
  (p/(NAME+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
  (p/'received.syx').write_bytes(b''.join(self.frames));return meta
def split_stream(data):
 """Strict saved transcript; rejects junk, truncation and nested framing."""
 at=0
 while at<len(data):
  if data[at]!=240:raise ValueError('transcript junk')
  end=data.find(b'\xf7',at+1)
  if end<0:raise ValueError('truncated transcript')
  yield data[at:end+1];at=end+1
def acquire(transport,token):
 """Transport dependency injection. No platform device adapter is provided."""
 r=Receiver(token);transport.send(request(token))
 for _ in range(9):r.accept(transport.receive())
 r.result();return r
