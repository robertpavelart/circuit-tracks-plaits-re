"""Exact paired replay after authentic nonzero output-ring qualification."""
from environment import ROOT,sha
from master_path import OUT
from live_master import EXE
import json,subprocess,shutil
class Peer:
 def __init__(self,name,reduced):
  self.d=OUT/name;self.d.mkdir(exist_ok=True);self.output=[]
  for p in (OUT/'both').glob('*.be24'):shutil.copyfile(p,self.d/p.name)
  if reduced:shutil.copyfile(ROOT/'builds/phase20g-dual-allocation/osc_only.be24',self.d/'core0.be24')
  self.reduced=reduced;self.commands=[]
  self.p=subprocess.Popen([str(EXE),'-'],cwd=self.d,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=(self.d/'error.txt').open('w'),text=True,bufsize=1)
 def send(self,ls):
  if self.reduced:
   ls=[('P 3bba '+' '.join(['5a1234']*(0x4000-0x3bba))) if l.startswith('P 3fed ') else 'FREE 3bba' if l=='FREE 3fed' else l for l in ls]
  self.commands+=ls;self.p.stdin.write('\n'.join(ls+['SYNC'])+'\n');self.p.stdin.flush();out=[]
  while True:
   l=self.p.stdout.readline()
   if not l:raise RuntimeError((self.d/'error.txt').read_text())
   if l.strip()=='SYNC':break
   out.append(l.rstrip());self.output.append(l.rstrip())
  return out
 def close(self):
  self.p.stdin.close();assert self.p.wait()==0
  (self.d/'output.txt').write_text('\n'.join(self.output)+'\n');(self.d/'job.txt').write_text('\n'.join(self.commands)+'\n')
def run(source='both',baseline='paired-baseline',candidate='paired-layout-A'):
 a=Peer(baseline,False);b=Peer(candidate,True)
 ls=(OUT/source/'job.txt').read_text().splitlines();at=ls.index('AUDIT')+1
 a.send(ls[:at]);b.send(ls[:at]);chunk=[];checks=0;differences=[]
 for l in ls[at:]:
  chunk.append(l)
  if l!='SUMMARY':continue
  x=a.send(chunk+['STATEWRITE state.bin']);y=b.send(chunk+[f'STATECHECK ../{baseline}/state.bin']);chunk=[];checks+=1
  diff=[v for v in y if v.startswith('STATE_DIFF')];differences+=diff
  if diff:print('first divergence',checks,diff,flush=True);break
 a.close();b.close()
 result=dict(checks=checks,differences=differences,stage_bytes_equal=(a.d/'stages.txt').read_bytes()==(b.d/'stages.txt').read_bytes(),baseline_program=sha((a.d/'core0.be24').read_bytes()),layout_A_program=sha((b.d/'core0.be24').read_bytes()))
 (OUT/('paired-result.json' if source=='both' else source+'-paired-result.json')).write_text(json.dumps(result,indent=2));print(result)
if __name__=='__main__':run()
