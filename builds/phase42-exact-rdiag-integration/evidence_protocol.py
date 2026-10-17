"""Fixed experimental command in rdiag framing; no hardware or I/O imports."""
import hashlib
SIG=b'\xf0\x7dCT';CMD=13;SIZE=535;PAD=232
REGIONS=((0x81000,23),)+tuple((0x82000+i*64,64) for i in range(8))
NAMES=('nor_00081000_00081016.bin','nor_00082000_000821ff.bin')
def crc32(data):
 c=0xffffffff
 for b in data:
  c^=b<<24
  for _ in range(8):c=((c<<1)^(0x04c11db7 if c&0x80000000 else 0))&0xffffffff
 return c
def nib(b):return bytes(v for x in b for v in (x>>4,x&15))
def un(b):
 if len(b)%2 or any(v>15 for v in b):raise ValueError('invalid nibbles')
 return bytes((b[i]<<4)|b[i+1] for i in range(0,len(b),2))
def n32(v):return nib(v.to_bytes(4,'big'))
def request(token):
 if not 0<=token<128:raise ValueError('transaction id')
 return SIG+bytes((CMD,token))+bytes(225)+b'\xf7'
def packet(token,kind,index,payload):
 addr=REGIONS[index][0] if index<9 else 0x81000
 b=SIG+bytes((CMD|64,token,kind,index))+n32(addr)+n32(SIZE)+bytes((len(payload),))+nib(payload)
 return b+n32(crc32(b[4:]))+b'\xf7'
def synthetic_packets(token,data):
 assert len(data)==535
 return [packet(token,0,0,data[:23])]+[packet(token,1,i+1,data[23+64*i:23+64*(i+1)]) for i in range(8)]+[packet(token,2,9,crc32(data).to_bytes(4,'big'))]
class Receiver:
 def __init__(self,token):self.token=token;self.next=0;self.frames=[];self.parts=[];self.done=False
 def accept(self,msg):
  if self.done:raise ValueError('packet after completion')
  if len(msg)<34 or msg[:6]!=SIG+bytes((CMD|64,self.token)) or msg[-1]!=247 or any(v>=128 for v in msg[1:-1]):raise ValueError('framing/session')
  kind,index=msg[6:8];addr=int.from_bytes(un(msg[8:16]),'big');total=int.from_bytes(un(msg[16:24]),'big');n=msg[24]
  if len(msg)!=34+2*n or total!=SIZE or index!=self.next:raise ValueError('length/total/order')
  if crc32(msg[4:-9])!=int.from_bytes(un(msg[-9:-1]),'big'):raise ValueError('packet CRC')
  data=un(msg[25:-9])
  if index<9:
   if (addr,n)!=REGIONS[index] or kind!=(0 if index==0 else 1):raise ValueError('region/address/size')
   self.parts.append(data)
  else:
   if index!=9 or kind!=2 or addr!=0x81000 or n!=4 or int.from_bytes(data,'big')!=crc32(b''.join(self.parts)):raise ValueError('completion')
   self.done=True
  self.next+=1;self.frames.append(msg)
 def result(self):
  if not self.done or len(self.frames)!=10 or sum(map(len,self.parts))!=535:raise ValueError('incomplete capture')
  return b''.join(self.parts)
 def captures(self):
  b=self.result();return dict(zip(NAMES,(b[:23],b[23:])))
