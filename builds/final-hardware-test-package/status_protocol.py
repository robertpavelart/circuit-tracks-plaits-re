"""Pure explicit status codec; no transport imports."""
from protocol_codec import crc as crc32,n32
NAMES={1:'NOT_READY',2:'INVALID',3:'UNSAFE',4:'READY',5:'FAILED',6:'AUTHORIZED',7:'SUCCESS'}
def packet(session,code,epoch=1):
 body=bytes([0x4f,session,code])+n32(0 if code==1 else epoch)+bytes(15)
 return b'\xf0\x7dCT'+body+n32(crc32(body))+b'\xf7'
def parse(raw,session):
 if len(raw)!=39 or raw[:5]!=b'\xf0\x7dCT\x4f' or raw[-1]!=247 or raw[5]!=session or raw[6] not in NAMES or raw[15:30]!=bytes(15):raise ValueError('malformed/stale status')
 def un(b):
  if any(v>15 for v in b):raise ValueError('status nibble')
  v=0
  for x in b:v=(v<<4)|x
  return v
 if un(raw[30:38])!=crc32(raw[4:30]):raise ValueError('status CRC')
 epoch=un(raw[7:15]);name=NAMES[raw[6]]
 if epoch!=(0 if name=='NOT_READY' else 1):raise ValueError('stale status epoch')
 return dict(status=name,epoch=epoch)
