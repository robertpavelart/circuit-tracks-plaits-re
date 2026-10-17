"""8192 consecutive paired audio blocks; actual ARM events and DSP readbacks."""
from environment import ROOT,MAN
from live_master import Bridge
from pair_master import Peer
from master_path import OUT
import json,math,time,filecmp
LV={k:int(v,16) for k,v in MAN['report']['vcf20']['labels'].items()}
class Pair(Bridge):
 def __init__(self):
  for name in ('long-baseline','long-layout-A'):(OUT/name).mkdir(exist_ok=True)
  self.journal_job=(OUT/'long-baseline/journal-job.txt').open('w',buffering=1)
  self.journal_base=(OUT/'long-baseline/journal-output.txt').open('w',buffering=1)
  self.journal_candidate=(OUT/'long-layout-A/journal-output.txt').open('w',buffering=1)
  self.journal_checks=(OUT/'long-checks.jsonl').open('w',buffering=1)
  self.completed_checks=0
  self.peer=Peer('long-layout-A',True);self.blocks=0;self.arm=[]
  super().__init__('long-baseline')
 def send(self,ls):
  ls=[l for l in ls if not l.startswith('TRACE ')]
  x=super().send(ls);y=self.peer.send(ls)
  self.journal_job.write('\n'.join(ls)+'\n')
  if x:self.journal_base.write('\n'.join(x)+'\n')
  if y:self.journal_candidate.write('\n'.join(y)+'\n')
  assert x==y,('command/output divergence',self.blocks,x[-3:],y[-3:])
  return x
 def check(self):
  x=Bridge.send(self,['STATEWRITE SHARED'])
  y=self.peer.send(['STATECHECK SHARED'])
  self.journal_base.write('\n'.join(x)+'\n');self.journal_candidate.write('\n'.join(y)+'\n')
  assert not any(l.startswith('STATE_DIFF') for l in y),(self.blocks,y)
  assert any('differences=0' in l for l in y),y
  self.completed_checks+=1
  self.journal_checks.write(json.dumps(dict(block=self.blocks,completed_checks=self.completed_checks,baseline=x,candidate=y))+'\n')
  if self.completed_checks%64==0:
   tmp=OUT/'long-progress.tmp';tmp.write_text(json.dumps(dict(completed_checks=self.completed_checks,last_block=self.blocks,status='running; journals are not resumable CPU snapshots')))
   tmp.replace(OUT/'long-progress.json')
 def call(self,name,fn,*args):
  self.s.events=[];self.s.capture(name,fn,*args);self.arm.append([self.blocks,name,self.s.events]);self.writes(self.s.events)
 def midi(self,msg):
  super().midi(msg);self.arm.append([self.blocks,'MIDI '+bytes(msg).hex(),self.s.events])
def main(blocks=8192):
 t=time.time();p=Pair()
 # Reference retained line mode and oscillator-disable controls, real mailbox service.
 p.call('MIDI1 line enable',LV['c_vset'],0,1)
 p.call('MIDI1 old oscillator disable',LV['c_vsetosc'],0,0)
 for i in range(blocks):
  p.blocks=i;p.send([f'BLOCK {i}'])
  if i%128==0:
   for tr in (0,1):p.midi([0x90+tr,48+7*tr+(i//128)%12,100])
  if i%128==96:
   for tr in (0,1):p.midi([0x80+tr,48+7*tr+(i//128)%12,0])
  if i%128==32:
   for tr in (0,1):
    for cc,val in [(74,40+(i//128)%64),(7,80+(i//128)%32),(10,48+(i//128)%32)]:p.midi([0xb0+tr,cc,val])
   p.call('current global mixer parameter send',0x08028ef2)
  if i%32==0:p.midi([0x99,36+(i//32)%4,100])
  p.s.e.w32(0x2000081c,2000+2*i//3)
  p.call('retained MIDI/FX/drum service',LV['c_vtick'])
  ring=[int(0x80000*math.sin(2*math.pi*(220+110*tr)*(32*i+n)/48000))&0xffffff for n in range(32) for tr in (0,1)]
  p.send(['CORE 0','Y ffd 001000','Y 1000 '+' '.join(f'{v:06x}' for v in ring),'PC 7000','STOP 7002','COUPLE','DUMPX 2e10 64','DUMPX 1000 64','CHECK','SUMMARY'])
  p.check()
  if i%256==0:print('Exact blocks',i+1,'seconds',round(time.time()-t,1),flush=True)
 p.close();p.peer.close()
 same=filecmp.cmp(p.d/'stages.txt',p.peer.d/'stages.txt',shallow=False);assert same
 result=dict(blocks=blocks,exact_state_checks=blocks,exact_command_outputs=True,exact_stages=same,actual_ARM_DSP_reads=len(p.reads),elapsed_seconds=time.time()-t,
  comparison='Byte equality: both cores full private X/Y, shared RAM, external words/known bits/canaries, supported architectural registers, ordered shared/external accesses and private writes; every measured stage sample',
  scheduling='Actual complete stock blocks serviced before each ARM DSP read; cooperative per-opcode core alternation; hardware timing UNKNOWN')
 (p.d/'ARM-events.json').write_text(json.dumps(p.arm,indent=2));(OUT/'long-result.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
 (OUT/'long-progress.json').write_text(json.dumps(dict(completed_checks=p.completed_checks,last_block=blocks-1,status='complete')))
if __name__=='__main__':main()
