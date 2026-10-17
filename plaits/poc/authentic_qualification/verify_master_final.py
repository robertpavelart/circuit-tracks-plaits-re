"""Verify completed qualification evidence and stream stage statistics."""
from environment import ROOT,REF,sha
from master_path import OUT
import json,filecmp,csv,math,hashlib

def signed(v):return v-0x1000000 if v&0x800000 else v
class Moments:
 def __init__(self):self.n=0;self.nz=0;self.lo=None;self.hi=None;self.sq=0;self.first=None
 def add(self,vs,block):
  if not vs:return
  self.n+=len(vs);self.nz+=sum(v!=0 for v in vs);self.sq+=sum(v*v for v in vs)
  lo=min(vs);hi=max(vs);self.lo=lo if self.lo is None else min(lo,self.lo);self.hi=hi if self.hi is None else max(hi,self.hi)
  if self.first is None and any(vs):self.first=block
 def result(self):return dict(samples=self.n,nonzero=self.nz,min=self.lo,max=self.hi,peak=None if not self.n else max(abs(self.lo),abs(self.hi)),RMS=None if not self.n else math.sqrt(self.sq/self.n),first_nonzero_block=self.first)
def stream_stages():
 d=OUT/'long-baseline';totals={};last={};rows=0
 with (d/'stages.txt').open() as f,(d/'stage-statistics.csv').open('w',newline='') as target:
  writer=csv.DictWriter(target,['block','bank','PC','stage','space','base','samples','min','max','peak','RMS','nonzero']);writer.writeheader()
  for line in f:
   t=line.split()
   if not t or t[0]!='S':continue
   assert len(t)==9+int(t[8]),('incomplete stage row',rows,t[:9])
   b=int(t[1]);bank=int(t[2],16);pc=int(t[4],16);tag=t[5];vs=[signed(int(v,16)) for v in t[9:]]
   m=Moments();m.add(vs,b);r=m.result();r.pop('first_nonzero_block')
   writer.writerow(dict(block=b,bank=bank,PC=f'{pc:X}',stage=tag,space=t[6],base=t[7],**r));rows+=1
   k=f'{bank if 0x900<=pc<0xc30 else "all"}:{tag}'
   totals.setdefault(k,Moments()).add(vs,b)
   if tag in ('bank0_pre_strip','bank1_pre_strip','output_ring'):last[(b,tag)]=vs
 main={};nonzero={};stereo=[Moments(),Moments()]
 for tag in ('bank0_pre_strip','bank1_pre_strip','output_ring'):
  m=Moments();positive=0
  for b in range(8192):
   vs=last[(b,tag)];m.add(vs,b);positive+=bool(any(vs))
   if tag=='output_ring':
    stereo[0].add(vs[::2],b);stereo[1].add(vs[1::2],b)
  main[tag]=m.result();nonzero[tag]=positive
 result=dict(stage_rows=rows,all_observations={k:m.result() for k,m in totals.items()},
  main_blocks=8192,main_last_observation_per_block=main,main_blocks_with_signal=nonzero,
  main_stereo=dict(left=stereo[0].result(),right=stereo[1].result()),
  both_banks_nonzero_main_blocks=sum(bool(any(last[(b,'bank0_pre_strip')])) and bool(any(last[(b,'bank1_pre_strip')])) for b in range(8192)),
  note='All-observation statistics include complete stock audio blocks used to service ARM reads. Main statistics use the final observation for each numbered block, after all its control-service blocks.')
 (d/'stage-summary.json').write_text(json.dumps(result,indent=2));return result
def main():
 r=json.loads((OUT/'long-result.json').read_text());assert r['blocks']==r['exact_state_checks']==8192 and r['exact_command_outputs'] and r['exact_stages']
 checks=[json.loads(l) for l in (OUT/'long-checks.jsonl').read_text().splitlines()]
 assert len(checks)==8192
 for i,c in enumerate(checks):
  assert c['block']==i and c['completed_checks']==i+1
  assert c['baseline']==c['candidate'] and all('differences=0' in s for s in c['candidate'])
 a=OUT/'long-baseline';b=OUT/'long-layout-A'
 assert filecmp.cmp(a/'journal-output.txt',b/'journal-output.txt',shallow=False)
 assert filecmp.cmp(a/'stages.txt',b/'stages.txt',shallow=False)
 preserved=json.loads((OUT/'interrupted-replay-preservation.json').read_text())
 prefix_bytes=preserved['common_stage_prefix']['bytes'];left=prefix_bytes
 with (OUT/'long-baseline-interrupted-20261015/stages.txt').open('rb') as old,(a/'stages.txt').open('rb') as fresh:
  while left:
   n=min(left,1024*1024);assert old.read(n)==fresh.read(n),'Rerun differs from preserved completed stage prefix';left-=n
 summary=None
 for name in ('long-baseline','long-layout-A'):
  d=OUT/name;assert not (d/'error.txt').read_text()
  out=(d/'output.txt').read_text();assert 'STATE_DIFF' not in out and 'FAIL' not in out
  cc=[l for l in out.splitlines() if l.startswith('CHECK ')]
  assert cc==[f'CHECK {i} OK' for i in range(8192)]
  ss=[l for l in out.splitlines() if l.startswith('SUMMARY ')]
  assert len(ss)==8192 and all('pwrite=0 ' in l for l in ss)
  summary=ss[-1]
 assert 'FREE 3bba' in (b/'job.txt').read_text().splitlines()
 stats=stream_stages()
 assert all(stats['main_blocks_with_signal'][k]>0 for k in ('bank0_pre_strip','bank1_pre_strip','output_ring')) and stats['both_banks_nonzero_main_blocks']>0
 short={}
 for fn in ('paired-result.json','active-MasterFX-probe-paired-result.json','mixer-send-FX-probe-paired-result.json'):
  q=json.loads((OUT/fn).read_text());assert q['checks']==64 and not q['differences'] and q['stage_bytes_equal'];short[fn]=q
 for name,selected in [('synth1',0),('synth2',1)]:
  q=json.loads((OUT/name/'stage-summary.json').read_text())
  banks={v['bank']:v['peak'] for v in q['stages'] if v['stage']=='voice_bank_sum'}
  assert banks[selected]>0 and banks[1-selected]==0 and q['output_all']['left']['nonzero'] and q['output_all']['right']['nonzero']
 negatives=json.loads((OUT/'comparator-negative-controls/result.json').read_text());assert all(v['detected'] for v in negatives.values())
 fxhist={int(l.split()[0],16):int(l.split()[1]) for l in (OUT/'active-MasterFX-probe/pc0.txt').read_text().splitlines()}
 assert fxhist[0x2ada]>0 and fxhist[0x2af9]>0
 automation=json.loads((OUT/'mixer-send-FX-probe/actual-ARM-events.json').read_text());mix={a:set() for a in (0x52,0x53,0x54,0x55)}
 for _,events in automation['events']:
  for _,ws in events:
   for core,space,addr,value in ws:
    if core==0 and space=='x' and addr in mix:mix[addr].add(value)
 assert all(len(values)>=2 for values in mix.values())
 sends=json.loads((OUT/'mixer-send-FX-probe/store-stage-summary.json').read_text());assert all(next(v for v in sends if v['stage']==tag)['nonzero']>0 for tag in ('send_left','send_right'))
 old=json.loads((ROOT/'builds/phase20i-authentic-qualification/provenance.json').read_text())['reference_before']
 from pathlib import Path
 changed=[p for p,h in old.items() if not Path(p).is_file() or sha(Path(p).read_bytes())!=h];assert not changed
 build=json.loads((ROOT/'builds/phase20j-coupled-replay/build-provenance.json').read_text());assert sha((ROOT/'builds/phase20j-coupled-replay/coupled.exe').read_bytes())==build['exe']
 files=[a/'stages.txt',b/'stages.txt',a/'journal-output.txt',b/'journal-output.txt',a/'job.txt',b/'job.txt',a/'ARM-events.json',a/'ARM-readback.json',OUT/'long-checks.jsonl',OUT/'long-result.json',ROOT/'plaits/poc/authentic_qualification/long_master.py',ROOT/'plaits/poc/authentic_qualification/coupled.cpp']
 hashes={}
 for p in files:
  h=hashlib.sha256()
  with p.open('rb') as f:
   while chunk:=f.read(1024*1024):h.update(chunk)
  hashes[str(p)]=dict(size=p.stat().st_size,sha256=h.hexdigest())
 result=dict(confidence='PROVEN within the stated offline model',qualified_shared_code_words=1075,main_blocks=8192,exact_native_state_and_transaction_checks=len(checks),exact_stage_files=True,exact_output_journals=True,guards=dict(range='P:3BBA-3FFF',checks_per_layout=8192,P_writes=0),last_summary=summary,
  short_regressions=short,isolated_bank_regressions_verified=True,negative_controls_verified=True,active_MasterFX_dispatches=fxhist[0x2ada],active_MasterFX_loop_fetches=fxhist[0x2af9],real_mixer_automation_distinct_values={f'{a:X}':sorted(v) for a,v in mix.items()},nonzero_send_stores_verified=True,reference_inputs_verified=len(old),reference_inputs_changed=changed,native_runner_sha256=build['exe'],preserved_stage_prefix_reproduced_bytes=prefix_bytes,main_stereo=stats['main_stereo'],main_blocks_with_signal=stats['main_blocks_with_signal'],both_banks_nonzero_main_blocks=stats['both_banks_nonzero_main_blocks'],artifacts=hashes)
 (OUT/'final-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ('short_regressions','artifacts')},indent=2))
if __name__=='__main__':main()
