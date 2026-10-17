"""Actual ARM DSP-readback bridge to the offline coupled interpreter."""
from environment import ROOT, authentic_session, sha
from master_path import OUT
import json,shutil,subprocess,sys,math
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PC,UC_ARM_REG_LR
EXE=ROOT/'builds/phase20j-coupled-replay/coupled.exe'
class Bridge:
 def __init__(self,name):
  self.d=OUT/name;self.d.mkdir(exist_ok=True)
  for p in (OUT/'before').glob('*.be24'):shutil.copyfile(p,self.d/p.name)
  self.commands=[];self.output=[];self.reads=[]
  self.proc=subprocess.Popen([str(EXE),'-'],cwd=self.d,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=(self.d/'error.txt').open('w'),text=True,bufsize=1)
  ls=(OUT/'before/job.txt').read_text().splitlines()
  end=next(i for i in range(len(ls)-1) if ls[i]=='STOP 113' and ls[i+1]=='COUPLE')+2
  self.send(ls[:end])
  self.s=authentic_session()
  self.writes(self.s.events);self.s.events=[]
  self.s.capture('global restore',0x08028ef2)
  self.s.capture('actual stock settings restoration',0x08028fd6)
  (self.d/'ARM-global-events.json').write_text(json.dumps(self.s.events,indent=2))
  self.writes(self.s.events);self.s.events=[]
  self.send(['CORE 0','P 7000 0bf080 0001ed 0c7002','P 3fed '+' '.join(['5a1234']*19),'FREE 3fed',
    'LOADY wave0.be24 100000','LOADY wave1.be24 128800','LOADY wave2.be24 151000','STAGES stages.txt','TRACE traffic.txt','AUDIT'])
  def read(uc,a,n,data):
   if a!=0x08029344:return
   core=uc.reg_read(UC_ARM_REG_R0);addr=uc.reg_read(UC_ARM_REG_R1)
   pending=self.s._take();self.writes([('pending',pending)])
   # Let the unmodified complete stock block consume pending mailbox commands.
   # This is an explicit scheduling model, not an invented register response.
   self.send(['CORE 0','PC 7000','STOP 7002','COUPLE'])
   sp='Y' if addr&0x8000 else 'X';addr &=0x7fff
   result=self.send([f'CORE {core}',f'DUMP{sp} {addr:x} 1','CORE 0'])
   value=int(next(l.split(':')[1] for l in result if l.startswith(f'{core} {sp} ')),16)
   self.reads.append(dict(core=core,space=sp,address=addr,value=value,caller=uc.reg_read(UC_ARM_REG_LR),pending=pending))
   uc.reg_write(UC_ARM_REG_R0,(value<<8)&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR)|1)
  self.s.e.uc.hook_add(UC_HOOK_CODE,read)
 def send(self,ls):
  self.commands+=ls
  self.proc.stdin.write('\n'.join(ls+['SYNC'])+'\n');self.proc.stdin.flush()
  result=[]
  while True:
   l=self.proc.stdout.readline()
   if not l:raise RuntimeError('DSP bridge stopped: '+(self.d/'error.txt').read_text())
   if l.strip()=='SYNC':break
   result.append(l.rstrip());self.output.append(l.rstrip())
  return result
 def writes(self,events):
  ls=[]
  for _,ws in events:
   for c,sp,a,v in ws:ls += [f'CORE {c}',f'{sp.upper()} {a:x} {v&0xffffff:06x}']
  if ls:self.send(ls+['CORE 0'])
 def midi(self,msg):
  self.s.events=[];self.s.midi(bytes(msg));self.writes(self.s.events)
 def close(self):
  self.proc.stdin.close();assert self.proc.wait()==0
  (self.d/'job.txt').write_text('\n'.join(self.commands)+'\n')
  (self.d/'output.txt').write_text('\n'.join(self.output)+'\n')
  (self.d/'ARM-readback.json').write_text(json.dumps(self.reads,indent=2))
def experiment(name,tracks,blocks=64):
 b=Bridge(name)
 for t in tracks:b.midi([0x90+t,60+7*t,100])
 for i in range(blocks):
  b.send([f'BLOCK {i}','CORE 0','Y ffd 001000','PC 7000','STOP 7002','COUPLE','DUMPX 2e10 64','DUMPY 800 64','CHECK','SUMMARY'])
 b.close();print(name,'complete',len(b.reads),'actual DSP readbacks',flush=True)
if __name__=='__main__':
 for name,tracks in [('synth1',[0]),('synth2',[1]),('both',[0,1])]:experiment(name,tracks)
