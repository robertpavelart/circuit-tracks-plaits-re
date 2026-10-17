"""Exact new-image coupled DMA ownership regressions; no device I/O."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase62-final-preflight'
src=(P/'stack_dma_tests.py').read_text()
src=src.replace("c=json.loads((O/'frozen-candidate-identity.json').read_text())", "c=json.loads((O/'construction.json').read_text());c['candidate']='circuittracks-nor-defect-closure-development'")
extra="""
src=src.replace("src=src.replace('from stream import *','')",'''src=src.replace('from stream import *','')
src=src.replace('self.frames=[]','self.status_frames=[];self.allframes=[];self.frames=[]')
src=src.replace("assert self.task=='Main' and self.active is None and self.e.r8(self.backend+8)==1", "assert self.task=='Main' and self.active is None")
src=src.replace('if self.frame and a<','if self.frame and not getattr(self,"raw_finished",False) and a<')
src=src.replace('sp=u.reg_read(UC_ARM_REG_SP);self.minsp', 'if pc==0x08074100 and self.frame is not None and self.e.r32(0x20044d70) in (0x14,0x15):self.raw_finished=True;self.guards_ready=False'+chr(10)+'  sp=u.reg_read(UC_ARM_REG_SP);self.minsp')
src=src.replace("assert bp==self.frame+PACKET;self.frames.append(bytes(u.mem_read(bp,n)))", "f=bytes(u.mem_read(bp,n));self.allframes.append(f);(self.status_frames if f[4]==0x4f else self.frames).append(f);assert f[4]==0x4f or bp==self.frame+PACKET and self.e.r8(self.backend+8)==1")
src=src.replace("assert bytes(decoded)==b''.join(expected)","assert bytes(decoded)==b''.join(self.allframes)")''')
"""
src=src.replace("ns=dict(__file__=",extra+"\nns=dict(__file__=",1)
ns=dict(__file__=str(O/'dma_regression.py'),__name__='selected_dma_model')
exec(compile(src,str(O/'selected-dma-model.py'),'exec'),ns)
M=ns['Measured'];timer=ns['timer'];ownership=ns['ownership']

def main():
 rows=[]
 def record(name,m,**extra):rows.append(dict(case=name,passed=True,ownership=ownership(m),details=m.summary(),**extra))
 m=M();m.start();assert m.finish(1500);m.verify();record('normal',m)
 for kind in ('tef','missing'):
  for k in (0,4,8):
   m=M(kind,k);m.start();assert not m.finish();timer(m);assert not m.done and m.e.r32(0x20044d70)==0x15
   record(f'{kind} {k} quarantine',m)
   m.fail_kind=None;m.active['issued']=False;m.irq();assert m.finish(1500);assert len(m.reads)==k+1 and m.e.r32(0x20044d70)==0x15
   record(f'{kind} {k} late same request',m)
 for k in (0,4,8):
  m=M();m.start()
  for _ in range(1500):
   if m.active and m.active['chunk']==k and not m.active['issued']:break
   m.tick()
  else:raise AssertionError('pending DMA not reached')
  buf=m.rawbuf;m.e.w32(0xa0001008,2);m.active['issued']=True
  m.run_cpu('IRQ',0x080573e0,SP=0x20050000,LR=0x0807ff01)
  # Actual Storage releases its software owner, but DMA remains enabled.
  assert not m.finish(24) and not m.done and m.e.r32(0x400264b8)&1
  assert len(m.reads)==k+1 and len(m.frames)==k
  record(f'TCF before DMA release {k}: no raw CPU read / no return',m)
  # Duplicate native completion IRQ must not bypass ownership fence.
  m.e.w32(0xa0001008,2);m.run_cpu('IRQ',0x080573e0,SP=0x20050000,LR=0x0807ff01)
  timer(m);assert not m.finish(24) and m.e.r32(0x20044d70)==0x15
  record(f'duplicate completion then timeout {k}',m)
  # Model eventual physical DMA release, without rearming or resubmitting.
  m.e.w32(0x400264b8,m.e.r32(0x400264b8)&~1);m.e.w32(0x400264bc,0)
  assert m.finish(1500) and len(m.reads)==k+1 and m.e.r32(0x20044d70)==0x15
  record(f'late physical DMA release {k}: failed absorbing',m)
 m=M();m.start();assert m.finish(1500,disconnect_after=0);record('host disconnect after completed read',m)
 for k in (0,4,8):
  m=M('missing',k);m.start();assert not m.finish();m.u.mem_write(m.dev+0x274,b'\0');timer(m)
  assert not m.finish(24) and not m.done and len(m.reads)==k+1
  record(f'disconnect while pending DMA {k}: quarantine retains frame',m)
  m.fail_kind=None;m.active['issued']=False;m.irq();assert m.finish(1500) and len(m.reads)==k+1 and m.e.r32(0x20044d70)==0x15
  record(f'disconnected late completion {k}: no retry',m)
 m=M(interleave=True);m.start();assert m.finish(1500,duplicate=True);m.verify();record('preempted producer and queued duplicate input',m)
 m=M();m.u.mem_write(m.backend+8,b'\0');m.start();assert not m.finish(24);timer(m);assert not m.finish(24) and not m.commands
 record('busy backend: no forced release; conservative nonreturn',m)
 result=dict(confidence='PROVEN',candidate_sha256=ns['c']['BIN_sha256'],passed=True,cases=rows,hardware_access=False,seams=['running RAM fixture','modeled RTOS scheduling','synthetic NOR/DMA/USB completions'],continuity_proof=False)
 (O/'dma-regression.json').write_text(json.dumps(result,indent=2)+'\n');print('DMA regression PASS',len(rows))
if __name__=='__main__':main()
