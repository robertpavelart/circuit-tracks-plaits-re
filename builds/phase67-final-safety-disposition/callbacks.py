import audit as a
import json,struct,traceback
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
O=a.O;S=0x20044d70
def run():
 e=a.fresh();u=e.uc;u.mem_map(0x40040000,0x20000);events=[];alloc=[];writes=[];pcs=set();frames=[]
 def ret(v=0):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
 def code(u,pc,n,d):
  pcs.add(pc)
  if pc in (0x801cfa4,0x801d7d8):alloc.append(dict(pc=hex(pc),size=u.reg_read(UC_ARM_REG_R0)));raise AssertionError('New allocation class')
  if pc in (0x8024164,0x80241b8,0x8022fdc,0x8023078,0x8037494,0x80374d4,0x8037648):raise AssertionError('NOR mutation')
  if pc in (0x8024738,0x803b7d4,0x8024668,0x80246a8,0x80246c4):
   events.append(dict(leaf=hex(pc),args=[hex(u.reg_read(UC_ARM_REG_R0+i)) for i in range(4)]));ret()
  if pc==0x8020c90:
   bp,ln=struct.unpack('<II',bytes(u.mem_read(u.reg_read(UC_ARM_REG_R2),8)));frames.append(bytes(u.mem_read(bp,ln)).hex());ret()
  if pc in (0x8071d00,0x8074700):events.append(dict(leaf=hex(pc),boundary='USB delivery/drain success'));ret()
  if pc==0x8070b00:
   events.append(dict(capture_entry=True,record=bytes(u.mem_read(S,12)).hex()));u.emu_stop()
 def write(u,access,at,n,v,d):writes.append(dict(pc=hex(u.reg_read(UC_ARM_REG_PC)),address=hex(at),size=n,value=hex(v)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=S,end=S+231)
 before=bytes(u.mem_read(S,232));rows=[]
 def setup(req,value):
  u.mem_write(0x200082b0,struct.pack('<BBHHH',0,req,value,0,0));e.call(0x803a784,a.dev,0x200082b0,sp=0x20008230,maxins=100000)
  rows.append(dict(request=req,value=value,state=e.r8(a.dev+0x274),record=bytes(u.mem_read(S,12)).hex()))
 try:
  setup(5,1);assert e.r8(a.dev+0x274)==2
  for val in (1,1,0,1):setup(9,val);assert e.r8(a.dev+0x274)==(3 if val else 2)
  assert bytes(u.mem_read(S,232))==before
  import sys
  sys.path.insert(0,str(a.R/'builds/phase61-final-geometry-gated-candidate'));import host
  parser=e.r32(e.r32(0x200068bc));desc=e.r32(parser+36);buf=e.r32(desc+4)
  # Real receive allocation is already present; descriptor lives in caller stack.
  assert e.r32(parser+16)>=232
  geom=before[4:12]
  for name,packet in [('query',host.request(37)),('wrong-session authorization',host.request(38,15,1,geom,False)),('wrong-geometry authorization',host.request(37,15,1,bytes([geom[0]^1])+geom[1:],False)),('authorization',host.request(37,15,1,geom,False))]:
   u.mem_write(buf,packet);u.mem_write(0x200082f0,struct.pack('<II',buf,len(packet)))
   try:e.call(0x801eb30,0,0x200082f0,sp=0x200082d8,maxins=300000)
   except AssertionError:
    if u.reg_read(UC_ARM_REG_PC)!=0x8070b00:raise
   rows.append(dict(operation=name,record=bytes(u.mem_read(S,12)).hex(),pc=hex(u.reg_read(UC_ARM_REG_PC))))
   if name!='authorization':assert e.r32(S)==0x4a000012
  assert any(x.get('capture_entry') for x in events)
  assert bytes(u.mem_read(S+12,220))==before[12:]
  result=dict(passed=True,rows=rows,allocation_entries=alloc,protected_writes=writes,events=events,frames=frames,executed_pcs=[hex(p) for p in sorted(pcs)],heap_cursor=hex(e.r32(0x20002b48)),seams='Bus address/status/endpoint operations and successful USB frame delivery/drain only; capture stopped before executing raw function. Not a resumed machine or enumeration replay.')
 except Exception as ex:result=dict(passed=False,error=str(ex),traceback=traceback.format_exc(),pc=hex(u.reg_read(UC_ARM_REG_PC)),rows=rows,events=events,allocation_entries=alloc,protected_writes=writes)
 (O/'callback-results.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ('executed_pcs','frames','protected_writes')},indent=2))
 if not result['passed']:raise SystemExit(1)
if __name__=='__main__':run()
