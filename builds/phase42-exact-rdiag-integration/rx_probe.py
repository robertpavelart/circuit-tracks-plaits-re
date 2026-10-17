"""Execute native USB-ring enqueue and Main USB input service on exact image."""
from replay import *
from evidence_protocol import request
from unicorn.arm_const import UC_ARM_REG_PRIMASK
def usb_events(data):
 out=bytearray()
 for i in range(0,len(data),3):
  part=data[i:i+3];last=i+3>=len(data);cin=4 if not last else {1:5,2:6,3:7}[len(part)]
  out+=bytes((cin,))+part+bytes(3-len(part))
 return bytes(out)
def enqueue(m,data):
 u=m.u;e=m.e;iface=e.r32(e.r32(0x200068b4));ring=e.r32(iface+24);events=usb_events(data);payload=b"".join(struct.pack("<H",len(events[i:i+64]))+events[i:i+64] for i in range(0,len(events),64))
 state=bytes(u.mem_read(0x20044d70,12));raw=bytes(u.mem_read(m.input_buf+RAW,64));requests=len(m.reads)
 saved=u.context_save();oldtask=m.task
 try:
  m.task='IRQ';u.reg_write(UC_ARM_REG_IPSR,108);u.mem_write(0x2004f100,payload)
  n=e.call(0x08022190,ring,0x2004f100,len(payload),sp=0x2004ff00)
  assert n==len(payload),(n,len(payload))
 finally:u.context_restore(saved);m.task=oldtask
 assert bytes(u.mem_read(0x20044d70,12))==state and bytes(u.mem_read(m.input_buf+RAW,64))==raw and len(m.reads)==requests
 return dict(interface=hex(iface),ring=hex(ring),ring_buffer=hex(e.r32(ring)),event_bytes=len(payload),native_enqueue='08022190',raw_unchanged=True,state_unchanged=True)
def process(m):
 m.task='Main';m.u.reg_write(UC_ARM_REG_IPSR,0)
 before=bytes(m.u.mem_read(0x20044d70,12));n=len(m.reads)
 m.e.call(0x08020ea0,sp=0x200082d8,maxins=2000000)
 assert len(m.reads)==n and bytes(m.u.mem_read(0x20044d70,12))==before
 return dict(native_input_service='08020EA0',new_NOR_reads=0,state_unchanged=True)
if __name__=='__main__':
 m=Model();m.start();m.tick();print('active',m.active)
 print(enqueue(m,request(37)));assert m.finish();m.verify();print(process(m));print('native RX duplicate safely rejected')

