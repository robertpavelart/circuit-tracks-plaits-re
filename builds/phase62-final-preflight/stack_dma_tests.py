"""New measurements from frozen corrected bytes, explicit running-RAM fixture.
This is NOT the startup continuity test and never claims that fixture seam closed.
"""
from pathlib import Path
import sys,json
import importlib.util
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase61-final-geometry-gated-candidate'
sys.path.insert(0,str(P))
spec=importlib.util.spec_from_file_location('host',P/'host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host);sys.modules['host']=host
c=json.loads((O/'frozen-candidate-identity.json').read_text());src=(P/'coupled_test.py').read_text()
src=src.replace("O/'circuittracks-final-geometry-gated-nor-test.syx'",f"O/'{c['candidate']}.syx'")
src=src.replace("O/'construction.json'",repr(str(P/'construction.json'))).replace("json.loads(("+repr(str(P/'construction.json'))+").read_text())","json.loads(Path("+repr(str(P/'construction.json'))+").read_text())")
src=src.replace("O/'candidate-startup.json'",repr(str(P/'candidate-startup.json'))).replace("json.loads(("+repr(str(P/'candidate-startup.json'))+").read_text())","json.loads(Path("+repr(str(P/'candidate-startup.json'))+").read_text())")
ns=dict(__file__=str(O/'stack_dma_tests.py'),__name__='selected_corrected_model')
exec(compile(src,str(O/'selected-stack-model.py'),'exec'),ns)
from unicorn.arm_const import *
Old=ns['Model']
class Measured(Old):
 def __init__(self,*a,**kw):self.deepest={};self.recent={};super().__init__(*a,**kw)
 def code(self,u,pc,n,d):
  task=self.task;sp=u.reg_read(UC_ARM_REG_SP);self.recent.setdefault(task,[]).append(hex(pc));self.recent[task]=self.recent[task][-32:]
  if task not in self.deepest or sp<int(self.deepest[task]['SP'],16):self.deepest[task]=dict(SP=hex(sp),PC=hex(pc),LR=hex(u.reg_read(UC_ARM_REG_LR)),recent_instruction_path=list(self.recent[task]))
  return super().code(u,pc,n,d)
def timer(m,delta=5000):
 saved=m.u.context_save();task=m.task
 try:
  m.task='IRQ';m.u.reg_write(UC_ARM_REG_IPSR,15);m.e.w32(0x2000081c,(m.e.r32(0x20044d78)+delta)&0xffffffff);m.e.call(0x0805998c,sp=0x2004ff00)
 finally:m.u.context_restore(saved);m.task=task
def ownership(m):
 buf=m.frame+192 if m.frame else None;dma=m.e.r32(0x400264b8)&1;dest=m.e.r32(0x400264c4)
 own=bool(buf is not None and dma and buf<=dest<buf+64)
 assert not (m.done and own),'Main returned while raw stack buffer is DMA destination'
 return dict(Main_returned=m.done,raw_stack_DMA_active=own,record=bytes(m.u.mem_read(0x20044d70,12)).hex(),backend_semaphore=m.e.r8(m.backend+8),request_active=m.e.r32(m.wrapper+16),state=m.state())
def main():
 rows=[]
 def save(name,m):rows.append(dict(case=name,passed=True,ownership=ownership(m),deepest=m.deepest,details=m.summary()))
 m=Measured();m.start();assert m.finish(1500);m.verify();save('normal full transfer',m)
 for kind in ('tef','missing'):
  for k in (0,4,8):
   m=Measured(kind,k);m.start();assert not m.finish();assert not m.done and m.e.r32(m.wrapper+16)==1
   timer(m);assert m.e.r32(0x20044d70)==0x15 and not m.done
   assert len(m.reads)==k+1;ownership(m);save(kind+' chunk'+str(k)+' timeout retains Main/request',m)
   # Deliver completion for that SAME outstanding request. The modeled normal
   # DMA completion clears stream EN before real native IRQ/backend release.
   m.fail_kind=None;m.active['issued']=False;m.irq('normal');assert m.finish(1500)
   assert m.e.r32(0x20044d70)==0x15 and len(m.reads)==k+1;save(kind+' late same-request completion chunk'+str(k),m)
 m=Measured();m.start();assert m.finish(1500,disconnect_after=0);assert m.e.r32(0x20044d70)==0x15;save('disconnect after completed first read',m)
 m=Measured();m.u.mem_write(m.backend+8,b'\0');m.start();assert m.finish(1500);assert m.e.r32(0x20044d70)==0x15 and not m.commands;save('actual backend busy error before DMA submission',m)
 result=dict(confidence='PROVEN',candidate_sha256=c['BIN_sha256'],scope='Fresh corrected-image Main/Storage/IRQ measurements using prior running-RAM model, NOT startup continuity; synthetic DMA/USB completions explicit',cases=rows,passed=True,raw_frame_bytes=260,raw_buffer_bytes=64,raw_buffer_offset=192,raw_saved_register_bytes=20,Main_stack=['0x2000775c','0x20008358'],Storage_stack=['0x20008d44','0x20009240'],in_session_recovery=False)
 (O/'stack-dma-tests.json').write_text(json.dumps(result,indent=2)+'\n');print('New corrected-image stack/DMA cases PASS',len(rows))
if __name__=='__main__':main()
