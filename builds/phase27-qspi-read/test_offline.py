"""Synthetic transport tests and ARM-on-authenticated-fixture tests. No device I/O."""
from pathlib import Path
import sys,json,struct,hashlib,random
from protocol import *
from build_patch import build,BASE,HOOK,ROUTER,READ,REF,R,O
from environment import authentic_session
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from receiver import WinMMTransport
import queue
plan=build();fragment=(O/'arm-diagnostic.fragment.bin').read_bytes()
checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
def reject(name,fn):
 try:fn()
 except ValueError:checks.append(name);return
 raise AssertionError(name)
check('CRC32 MPEG-2 known answer',crc32(b'123456789')==0x0376e6e7)
for seed in range(8):
 rng=random.Random(seed);data=bytes(rng.randrange(256) for _ in range(512));r=Receiver(seed)
 for p in synthetic_packets(seed,data):r.accept(p)
 check('synthetic exact reassembly '+str(seed),r.result()==data)
frames=synthetic_packets(17,bytes(range(256))*2)
def receive(fs):
 r=Receiver(17)
 for f in fs:r.accept(f)
 return r.result()
reject('reject missing completion',lambda:receive(frames[:-1]))
reject('reject wrong order',lambda:receive([frames[1]]+frames[1:]))
reject('reject duplicate',lambda:receive([frames[0]]+frames))
reject('reject wrong token',lambda:Receiver(16).accept(frames[0]))
for index in (8,24,40,155):
 b=bytearray(frames[0]);b[index]^=1;reject('reject packet mutation '+str(index),lambda b=b:Receiver(17).accept(b))
wrong=frames[:-1]+[packet(17,1,8,bytes(4))]
reject('reject whole-capture CRC',lambda:receive(wrong))
reject('reject trailing transcript junk',lambda:list(split_stream(b''.join(frames)+b'x')))
reject('reject truncated transcript',lambda:list(split_stream(b''.join(frames)[:-1])))
class FakeLink:
 def __init__(self):self.q=queue.Queue();self.readded=[];self.sent=[]
 def _readd(self,h):self.readded.append(h)
 def send(self,b):self.sent.append(b)
f=FakeLink();stream=b''.join(frames)
for i in range(0,len(stream),37):f.q.put((stream[i:i+37],i))
tr=WinMMTransport(f);tr.send(request(17));r=Receiver(17)
for _ in range(9):r.accept(tr.receive())
check('fragmented/coalesced WinMM callback adapter without WinMM',r.result()==bytes(range(256))*2 and f.sent==[request(17)])

class Model:
 def __init__(self):
  self.s=authentic_session();self.e=self.s.e;u=self.e.uc
  u.mem_write(BASE,fragment);u.mem_write(HOOK,bytes.fromhex(plan['hook']['after']))
  u.mem_map(0xa0001000,0x1000)
  self.ctx=self.e.r32(self.e.r32(self.e.r32(0x20006968)+4)+4)
  self.controller=self.e.r32(self.ctx);self.backend=self.e.r32(self.e.r32(0x20006968)+4)
  self.router=self.e.r32(struct.unpack('<I',bytes(u.mem_read(0x0801edd0,4)))[0])
  self.calls=[];self.out=[];self.writes=[];self.forward=False;self.minsp=0xffffffff;self.pending=None
  self.synthetic=bytes(((i*73)^ (i>>1)^0xa6)&255 for i in range(512))
  self.events=[];self.complete=True;self.canaries=None
  def ret(v=0):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
  def code(u,pc,n,d):
   self.minsp=min(self.minsp,u.reg_read(UC_ARM_REG_SP))
   if pc==READ:
    args=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    self.calls.append(args);self.pending=args
    assert args[0]==self.backend and args[1]==ADDRESS and args[3]==512
    assert args[2]%4==0
    u.mem_write(args[2]-4,b'HEAD');u.mem_write(args[2]+512,b'TAIL');self.canaries=(args[2]-4,args[2]+512)
    self.events.append('actual backend entry')
   elif pc==0x08037596:
    # Model only the external DMA/IRQ completion boundary. The real stock
    # read wrapper, DMA setup, command builder and wait-loop instructions run.
    regs={x:self.e.r32(0xa0001000+x) for x in (0,0x10,0x14,0x18)}
    assert regs[0x18]==ADDRESS and regs[0x10]==511
    assert regs[0x14]&255 in (0xeb,0xec) and (regs[0x14]>>26)&3==1
    self.events.append(dict(actual_QSPI_registers={hex(k):hex(v) for k,v in regs.items()}))
    if not self.complete:raise RuntimeError('MODELED missing DMA completion: stopped without success')
    u.mem_write(self.pending[2],self.synthetic)
    self.e.w32(self.controller,self.e.r32(self.controller)|1)
    self.events.append('MODELED external DMA bytes and IRQ completion flag')
   elif pc==0x0801be1a:
    self.events.append(dict(MODELED_RTOS_boundary=hex(pc)));ret(0)
   elif pc==ROUTER:
    assert u.reg_read(UC_ARM_REG_R0)==self.router
    msg=u.reg_read(UC_ARM_REG_R2);bp,n=struct.unpack('<II',bytes(u.mem_read(msg,8)))
    self.out.append((u.reg_read(UC_ARM_REG_R1),bytes(u.mem_read(bp,n))))
    self.events.append('MODELED output router captures copied frame');ret(0)
   elif pc==HOOK+4:
    self.forward=True
    # Original prologue already executed; emulate only original continuation.
    sp=u.reg_read(UC_ARM_REG_SP);vals=struct.unpack('<6I',bytes(u.mem_read(sp,24)))
    for reg,val in zip((UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8),vals[:5]):u.reg_write(reg,val)
    u.reg_write(UC_ARM_REG_SP,sp+24);u.reg_write(UC_ARM_REG_PC,vals[-1]|1)
  def write(u,access,a,n,v,d):
   self.writes.append((a,n,v))
   if 0x08000000<=a<0x08080000:raise AssertionError('internal flash write')
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 def run(self,data,port=0):
  self.calls=[];self.out=[];self.forward=False;self.events=[];self.writes=[];self.canaries=None;self.minsp=0xffffffff
  u=self.e.uc;buf=0x20060100;msg=0x20060000
  u.mem_write(buf,bytes(data));u.mem_write(msg,struct.pack('<II',buf,len(data)))
  u.mem_write(buf-4,b'BUFL');u.mem_write(buf+PAD,b'BUFR')
  before={reg:0x12340000+reg for reg in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)}
  for reg,v in before.items():u.reg_write(reg,v)
  sem=self.e.r8(self.backend+8)
  self.e.call(HOOK,port,msg,0,maxins=1000000)
  assert all(u.reg_read(reg)==v for reg,v in before.items())
  assert self.e.r8(self.backend+8)==sem
  assert bytes(u.mem_read(buf-4,4))==b'BUFL' and bytes(u.mem_read(buf+PAD,4))==b'BUFR'
  if self.canaries:
   assert bytes(u.mem_read(self.canaries[0],4))==b'HEAD' and bytes(u.mem_read(self.canaries[1],4))==b'TAIL'
  return dict(calls=self.calls,frames=len(self.out),events=self.events,forwarded=self.forward,
   modeled_fixture_stack_high='0x2006f000',max_stack_observed=0x2006f000-self.minsp,
   actual_MMIO_writes=[(hex(a),n,hex(v)) for a,n,v in self.writes if a>=0x40000000],
   forbidden_flash_writes=0)
m=Model();runs=[]
for port in (0,1):
 result=m.run(request(39+port),port);runs.append(result)
 check('actual backend + 9 compiled ARM frames port '+str(port),len(m.calls)==1 and len(m.out)==9)
 check('same-port mask '+str(port),all(mask==1<<port for mask,_ in m.out))
 r=Receiver(39+port)
 for _,frame in m.out:r.accept(frame)
 check('compiled ARM CRC/framing/reassembly '+str(port),r.result()==m.synthetic)
 check('independent host/ARM frame equality '+str(port),[x for _,x in m.out]==synthetic_packets(39+port,m.synthetic))
 if port==0:
  (O/'synthetic-transcript.syx').write_bytes(b''.join(x for _,x in m.out))
  # Explicitly synthetic transport evidence; never named a real QSPI dump.
  (O/'synthetic-data.bin').write_bytes(m.synthetic)
for offset,value in [(4,6),(9,9),(19,3),(22,2),(23,1),(231,0),(5,128)]:
 req=bytearray(request(1));req[offset]=value;m.run(req)
 check('refuse malformed/write request '+str(offset),not m.calls and not m.out and not m.forward)
for cmd in range(128):
 if cmd==CMD:continue
 req=bytearray(request(1));req[4]=cmd;m.run(req)
 check('no read/write dispatch for other command '+str(cmd),not m.calls and not m.out and not m.forward)
for offset in range(6,22):
 req=bytearray(request(1));req[offset]^=1;m.run(req)
 check('hardcoded address/length byte '+str(offset),not m.calls and not m.out)
for data in (request(1)[:-1],request(1)+b'\0',b'\xf0\x7dCT'):
 m.run(data);check('refuse request length '+str(len(data)),not m.calls and not m.out)
m.run(request(1),2);check('refuse unrecognized input port',not m.calls and not m.out)
m.e.uc.reg_write(UC_ARM_REG_IPSR,15);m.run(request(1));check('refuse interrupt context',not m.calls and not m.out);m.e.uc.reg_write(UC_ARM_REG_IPSR,0)
m.run(b'\xf0\x7e\x7f\x06\x01\xf7');check('forward foreign identity with original prologue',m.forward and not m.calls)
m.e.uc.mem_write(m.backend+8,b'\0');m.run(request(1));check('backend busy produces no success',len(m.calls)==1 and not m.out);m.e.uc.mem_write(m.backend+8,b'\1')
cap=m.e.r32(m.backend+12);m.e.w32(m.backend+12,0x80000);m.run(request(1));check('backend bounds error produces no success',len(m.calls)==1 and not m.out);m.e.w32(m.backend+12,cap)
saved=m.e.r32(m.backend);m.e.w32(m.backend,0);m.run(request(1));check('wrong backend type refused',not m.calls and not m.out);m.e.w32(m.backend,saved)
callback=m.e.r32(m.ctx+0x28);m.e.w32(m.ctx+0x28,0);m.run(request(1));check('unknown completion callback refused',not m.calls and not m.out);m.e.w32(m.ctx+0x28,callback)
count=m.e.r8(m.ctx+0x24);m.e.uc.mem_write(m.ctx+0x24,b'\2');m.run(request(1));check('additional completion callback refused',not m.calls and not m.out);m.e.uc.mem_write(m.ctx+0x24,bytes([count]))
for lanes in (0,1):
 for addr_mode in (0,1):
  m.e.uc.mem_write(m.ctx+0x18,bytes([lanes,addr_mode]));result=m.run(request(41));runs.append(result)
  r=Receiver(41)
  for _,frame in m.out:r.accept(frame)
  check('stock read lane/address flags '+str((lanes,addr_mode)),r.result()==m.synthetic)
m.e.uc.mem_write(m.ctx+0x18,b'\1\1')
class SyntheticTransport:
 def send(self,data):m.run(data);self.queue=[f for _,f in m.out]
 def receive(self):return self.queue.pop(0)
r=acquire(SyntheticTransport(),45);check('injected transport request and receiver',r.result()==m.synthetic)
destination=O/'synthetic-host-output'
if not (destination/NAME).exists():meta=r.save(destination,origin='SYNTHETIC TRANSPORT TEST ONLY; not device data')
else:meta=json.loads((destination/(NAME+'.json')).read_text())
check('host writes exact 512 bytes and SHA256', (destination/NAME).read_bytes()==m.synthetic and meta['sha256']==hashlib.sha256(m.synthetic).hexdigest())
m.complete=False
try:m.run(request(1))
except RuntimeError as ex:
 check('missing DMA completion is not reported as success','MODELED missing DMA' in str(ex) and not m.out)
else:raise AssertionError('missing completion accepted')
out=dict(confidence='PROVEN',scope='Offline synthetic transport and authenticated-ARM instruction execution with explicit peripheral/RTOS/router models; not a hardware or authenticated coefficient test',
 checks=checks,runs=runs,hardware_IO=False,original_QSPI_bytes_used=False,
 hardware_stack_headroom='UNKNOWN',real_DMA_IRQ_completion='UNKNOWN',full_router_device_transmission='UNKNOWN')
(O/'offline-test-result.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(checks=len(checks),ARM_runs=len(runs),max_observed_stack=[x['max_stack_observed'] for x in runs],hardware_IO=False),indent=2))
