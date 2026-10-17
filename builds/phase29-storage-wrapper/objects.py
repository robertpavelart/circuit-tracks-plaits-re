from inspect_code import *
s=authentic_session();e=s.e
def rec(a,n):return dict(address=hex(a),words={hex(i):hex(e.r32(a+i)) for i in range(0,n,4)})
wrapper=e.r32(0x20006968);holder=e.r32(0x20006790);tcb=e.r32(holder)
result=dict(wrapper=rec(wrapper,28),queue=rec(e.r32(wrapper+8),12),Storage_holder=rec(holder,12),Storage_TCB=rec(tcb,0x60),Main_TCB=rec(0x2000835c,0x60),heap_before=rec(0x20002b44,8),Main_periodic_service_object=rec(0x20000354,12))
result['heap_remaining_bytes']=e.r32(0x20002b44)-e.r32(0x20002b48)
result['allocation_attempts']=[]
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC
for n in (512,1024):
 try:
  e.call(0x0801cfa4,n,0x08026b22,maxins=10000)
  result['allocation_attempts'].append(dict(bytes=n,returned=hex(e.uc.reg_read(UC_ARM_REG_R0))))
 except Exception as exc:
  result['allocation_attempts'].append(dict(bytes=n,error=str(exc),PC=hex(e.uc.reg_read(UC_ARM_REG_PC)),allocation_returned=False))
result['heap_after']=rec(0x20002b44,8)
(O/'objects.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
