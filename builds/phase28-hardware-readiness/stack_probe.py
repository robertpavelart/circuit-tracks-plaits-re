"""Reuse phase27's model by AST extraction, without rerunning/modifying it.
Real captured Main stack bounds; static 128-byte input-call prefix is modeled.
OS wait/output are phase27 models: this is not a corrected completion test.
"""
from inspect_code import *
import ast,types
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
P=R/'builds/phase27-qspi-read';plan=json.loads((P/'patch-plan.json').read_text());fragment=(P/'arm-diagnostic.fragment.bin').read_bytes()
BASE=int(plan['append']['start'],16);HOOK=0x0801eb30;ROUTER=0x08020c90;READ=0x08022f94;ADDRESS=0x82000;PAD=232
sys.path.insert(0,str(P));from protocol import request
tree=ast.parse((P/'test_offline.py').read_text());node=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Model')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(P/'test_offline.py'),'exec'),globals())
class Guard(Exception):pass
out=[]
for prefix in (128,2372):
 m=Model();e=m.e;u=e.uc;base=0x2000775c;top=0x20008358;entry=top-prefix
 u.mem_write(base,b'LOW!');u.mem_write(top,b'HIGH')
 def call(self,fn,*args,**kw):
  u.reg_write(UC_ARM_REG_SP,entry)
  for i,x in enumerate(args):u.reg_write(UC_ARM_REG_R0+i,x)
  u.reg_write(UC_ARM_REG_LR,0x0807ff01);u.emu_start(fn|1,0xffffffff,count=1000000)
  assert u.reg_read(UC_ARM_REG_PC)==0x0807ff00
 e.call=types.MethodType(call,e)
 def bound(u,pc,n,d):
  if u.reg_read(UC_ARM_REG_SP)<base+4:raise Guard('modeled stack guard reached')
 u.hook_add(UC_HOOK_CODE,bound)
 try:
  result=m.run(request(1));status='modeled path returned'
  assert bytes(u.mem_read(base,4))==b'LOW!' and bytes(u.mem_read(top,4))==b'HIGH'
 except Guard:status='guard detected insufficient headroom'
 out.append(dict(prefix_bytes=prefix,entry_SP=hex(entry),minimum_SP=hex(m.minsp),status=status,
  additional_observed_bytes=entry-m.minsp,total_observed_from_aligned_top=top-m.minsp,
  remaining_bytes_to_low_guard=m.minsp-(base+4)))
assert out[0]['additional_observed_bytes']==724 and out[1]['status'].startswith('guard detected')
result=dict(confidence='PROVEN',scope='Bounded phase27 model on captured Main stack; not a hardware-safe stack proof',
 source_harness_sha256=sha((P/'test_offline.py').read_bytes()),
 configured_words=0x300,configured_bytes=3072,stack_allocation_base='0x2000775c',stack_allocation_end_exclusive='0x2000835c',
 aligned_initial_top='0x20008358',thread_entry='0x0801d4b0',
 call_prefix=[dict(PC='0x0801d4b0',bytes=40),dict(PC='0x08020e94',bytes=8),dict(PC='0x08020ea0',bytes=56),dict(PC='0x0801c894',bytes=24)],
 cases=out,unbounded=['OS wait/scheduler endpoint','Full output router/USB endpoint','Preemption/FPU exception frames and independent task watermark'],hardware_headroom_verdict='UNKNOWN')
(O/'stack-probe-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
