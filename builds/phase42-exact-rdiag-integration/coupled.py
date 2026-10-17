"""Exact-image native USB-ring -> Main parser/fanout -> rdiag -> Storage replay.

USB packet arrival and transfer completion are opaque modeled peripheral events;
native ring operations, Main polling, parser, fanout and patched dispatcher run.
"""
from replay import *
Previous=Model
from rx_probe import enqueue
from integrate import STATE
L={k:int(v,16) for k,v in json.loads((O/'integration.json').read_text())['layout'].items()}
class Exact(Previous):
 def __init__(self,*args,**kwargs):
  self.handler_return_verified=False;self.entry_count=0;self.post_return_parser_stores=0;self.service_PCs=set();self.tx_sources=[]
  super().__init__(*args,**kwargs)
  self.image_before=bytes(self.u.mem_read(0x08010000,len((O/'integrated-internal.bin').read_bytes())))
 def code(self,u,pc,n,d):
  if pc==L['entry']:self.entry_count+=1
  if pc in (0x08020ea0,0x08020f62,0x0801c894,0x0801eb30,0x08035c58):self.service_PCs.add(hex(pc))
  if L['entry']<=pc<L['entry']+256:
   i=next(md.disasm(bytes(u.mem_read(pc,n)),pc))
   if self.task=='Main' and i.mnemonic=='pop' and 'pc' in i.op_str and not self.handler_return_verified and self.e.r8(STATE+4) in (2,3) and self.reads and self.active is None:
    assert bytes(u.mem_read(self.input_buf,232))==self.expected_input
    self.handler_return_verified=True
  if pc==0x08020c90:
   p=u.reg_read(UC_ARM_REG_R2);bp,ln=struct.unpack('<II',bytes(u.mem_read(p,8)))
   frame=bytes(u.mem_read(bp,ln))
   if len(frame)>4 and frame[:4]!=b'\xf0\x7dCT':
    self.foreign_output=getattr(self,'foreign_output',[])+[frame.hex()]
    # Execute the native router; omit only the diagnostic-packet assertion.
    return
  return super().code(u,pc,n,d)
 def start(self,token=37,data=None,port=0):
  assert port==0 and self.active is None
  self.done=False;self.token=token;self.frame=None;self.guards_ready=False;self.restoring=False
  self.expected_input=request(token) if data is None else data
  self.task='Main';self.e.w32(self.kernel+100,0x2000835c);self.u.reg_write(UC_ARM_REG_IPSR,0)
  self.enqueue_proof=enqueue(self,self.expected_input)
  self.mainregs={r:0x30ab0000+r for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)}
  for r,v in self.mainregs.items():self.u.reg_write(r,v)
  self.run_cpu('Main',0x08020ea0,SP=0x200082d8,LR=0x0807ff01)
 def verify(self,*a,**k):
  super().verify(*a,**k)
  assert bytes(self.u.mem_read(0x08010000,len(self.image_before)))==self.image_before
  assert self.e.r8(STATE+4)==2 and self.e.r8(STATE+7)==0
 def raw_snapshot(self):
  return dict(state=bytes(self.u.mem_read(STATE,12)).hex(),request=None if self.active is None else bytes(self.u.mem_read(self.wrapper,28)).hex(),reads=len(self.reads),raw=bytes(self.u.mem_read(self.input_buf+RAW,64)).hex(),frame=self.frame,sp=self.u.reg_read(UC_ARM_REG_SP))
if __name__=='__main__':
 m=Exact();m.start();print('active',m.active);print(enqueue(m,request(37)));assert m.finish();m.verify();print(m.entry_count,m.service_PCs,m.handler_return_verified)

