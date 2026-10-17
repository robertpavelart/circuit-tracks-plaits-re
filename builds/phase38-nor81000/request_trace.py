"""Observe the existing blocked read only; no NOR payload or completion model."""
import sys,json
sys.dont_write_bytecode=True
from trace import run
from systick import *
class ReadTrace(TickModel):
 def __init__(self):
  super().__init__();self.read_events=[];self.wrapper=None;self.request=None;self.original_request=None
 def objects(self,u):
  if self.wrapper is None:return None
  w=self.wrapper;b=r32(u,w+4);q=r32(u,w+8)
  return dict(wrapper=w,wrapper_hex=bytes(u.mem_read(w,32)).hex(),backend=b,backend_hex=bytes(u.mem_read(b,32)).hex(),
   queue=q,queue_hex=bytes(u.mem_read(q,48)).hex(),backend_vtable=r32(u,b),
   backend_vtable_hex=bytes(u.mem_read(r32(u,b),32)).hex(),current_TCB=r32(u,0x20005268))
 def observe(self,u,pc,n):
  if pc==0x08005dac:self.wrapper=u.reg_read(UC_ARM_REG_R0)
  if pc==0x080057b6:
   self.request=u.reg_read(UC_ARM_REG_R5)
  if pc==0x080058a4:self.original_request=u.reg_read(UC_ARM_REG_R1)
  if pc in (0x08005d98,0x08005dac,0x080058a4,0x080057b6,0x080057e6,0x080076cc,0x08007704,0x0800770c,0x08007938,0x080050e6,0x080051c0,0x080051c2) or (0x08005300<=pc<0x08005840 and self.wrapper is not None):
   ins=next(md.disasm(bytes(u.mem_read(pc,n)),pc))
   row=dict(pc=pc,instruction=ins.mnemonic+' '+ins.op_str,registers=regs_no_psr(u))
   if pc in (0x08005dac,0x080057b6,0x080057e6,0x080076cc,0x08007704,0x0800770c,0x080051c2):row['objects']=self.objects(u)
   if pc in (0x080057b6,0x080058a4):
    address=self.request if pc==0x080057b6 else self.original_request
    raw=bytes(u.mem_read(address,24));row['request']=dict(address=address,hex=raw.hex(),fields=list(struct.unpack('<HH5I',raw)))
   if pc==0x0800770c:
    p=u.reg_read(UC_ARM_REG_R1);row['controller_descriptor']=dict(address=p,hex=bytes(u.mem_read(p,16)).hex())
   self.read_events.append(row)
  return super().observe(u,pc,n)
 def finalize(self,u,stop):
  super().finalize(u,stop)
  self.read_final=dict(objects=self.objects(u),request_address=self.request,
   request_hex=bytes(u.mem_read(self.request,24)).hex() if self.request else None,
   original_request_address=self.original_request,original_request_hex=bytes(u.mem_read(self.original_request,24)).hex(),
   destination=0x2000546c,destination_hex=bytes(u.mem_read(0x2000546c,23)).hex(),
   DMA_registers={hex(a):r32(u,a) for a in (0x400264b8,0x400264bc,0x400264c0,0x400264c4)},
   controller_registers={hex(a):r32(u,a) for a in (0xa0001000,0xa0001008,0xa0001010,0xa0001014,0xa0001018)})
if __name__=='__main__':
 for variant in sys.argv[1:] or ['stock','diagnostic']:
  m=ReadTrace();row=run('bootloader',variant,clock_model=True,nor_init=True,nor_identity=True,tick_model=True,limit=600000,svc_model=m)
  row.update(read_events=m.read_events,read_final=m.read_final,final_architecture=m.final_state)
  (O/f'{variant}-request.json').write_text(json.dumps(row,indent=2)+'\n')
  old=json.loads((O.parent/f'phase37-systick/{variant}.json').read_text())
  assert row['stop']==old['stop'] and row['RAM_sha256']==old['RAM_sha256'],'observer changed existing prefix'
  print(variant,row['stop'],m.read_final,flush=True)
