"""Offline timing arithmetic on immutable standalone PC traces; never runs CPU."""
import argparse,csv,hashlib,json,re,sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'builds/phase20a-timing'
NATIVE=ROOT/'builds/phase20a-div/final-compact'
OLD=ROOT/'builds/phase20a-plaits/final'
def obj(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 with p.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
def dump(out,n,v):
 with (out/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def csvout(out,n,records):
 with (out/n).open('x',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
def acc(reg):
 reg=reg.strip().lower()
 return 1 if reg in ['a','a0','a1','a2'] else 2 if reg in ['b','b0','b1','b2'] else 0
def classify(pc,s,size):
 m=s.split()[0];r=dict(pc=pc,assembly=s,words=size,family=m.upper(),base=1,ea=0,
  short_write=False,mem='none',parallel=False,move_src=0,move_dst=0,alu_dst=0,
  acc_transfer=False,agu_update=False,agu_explicit_write=False,source='FM A-6 default DALU/no parallel move; RM4-4',
  rule_class='DOCUMENTED EXACT',applicability='DEVICE-FAMILY ASSUMPTION: same DSP56300 core timing')
 if m=='move':
  src,dst=s[5:].split(',');r['move_src']=acc(src);r['move_dst']=acc(dst)
  r['acc_transfer']=bool(r['move_src'] or r['move_dst'])
  if 'x:' in s or 'y:' in s:
   space='X' if 'x:' in s else 'Y';read=src.startswith(('x:','y:'));r['mem']=space+('_read' if read else '_write')
   if ':>$' in s:r.update(family='MOVE_LONG_ABSOLUTE',ea=1,source='FM A-6 MOVE ea T1+lab1')
   elif ':(r0)+' in s:r.update(family='MOVE_POSTINCREMENT',agu_update=True,source='FM A-1/A-6; RM4-4 AGU')
   else:
    assert ':$' in s and size==1,s
    r.update(family='MOVE_SHORT_ABSOLUTE',source='FM A-6 short read1; second short row2 has missing source operand')
    if not read:r.update(base=2,short_write=True,rule_class='DEVICE-FAMILY ASSUMPTION: garbled short row interpreted as store')
  elif src.startswith('#>'):
   r.update(family='MOVE_LONG_IMMEDIATE',ea=1,source='FM A-6 (A-7 MOVEC for R0) T1+lim1')
   assert size==2,s
   r['agu_explicit_write']=dst=='r0'
  else:r.update(family='MOVE_REGISTER',source='FM A-6 MOVE S,D T1')
 elif m in ['jsr','jmp','rts']:
  r.update(base=3,source='FM A-4 JMP / A-5 JSR / A-8 RTS')
 elif m.startswith('j'):
  assert m in ['jlt','jge','jle','jne','jeq'],s
  r.update(family='JCC',base=4,source='FM A-4 Jcc xxx T4; A-13 false adds1')
 elif m in ['do','rep']:r.update(base=5,source='FM A-4 DO / A-8 REP;12-10 zero loop overhead')
 elif m=='andi':r.update(base=3,source='FM A-2 ANDI T3')
 elif m=='div':r.update(alu_dst=acc(s.split(',')[-1]),source='FM A-4 DIV T1;13-52..54 iteration')
 elif m in ['add','sub','cmp','mpy','asl','asr','neg','clr','tst','rol']:
  a=s.split(' ',1)[1]
  parallel=a.split(' ',1)[1] if ' ' in a else None
  alu=a.split(' ',1)[0];r['alu_dst']=acc(alu.split(',')[-1]) if m not in ['cmp','tst'] else 0
  if parallel:
   assert parallel in ['y0,a','x0,a','b1,x1'],s
   x,y=parallel.split(',');r.update(parallel=True,move_src=acc(x),move_dst=acc(y),acc_transfer=bool(acc(x) or acc(y)))
   r['source']='FM A-6 register MOVE T1 overlaps DALU; RM4-4 forwarding'
  if m in ['asl','asr']:r['source']='FM A-2 multibit shift T1 / A-6 default single-bit DALU'
  if m in ['add','sub'] and alu.startswith('#'):
   r['base']=2 if alu.startswith('#>') else 1;r['source']='FM A-2 ADD or A-8 SUB immediate'
 else:assert m=='nop',s
 # Validate extension-word surcharge once, never count it as a second opcode.
 if r['ea']:assert size==2,s
 return r
def program(suite):
 lines=(suite/'dsp-first/program.asm').read_text().splitlines();labels=obj(suite/'dsp-first/labels.json')
 code=(suite/'dsp-first/program.be24').read_bytes();rr={}
 for i,line in enumerate(lines):
  address,s=line.split(' ',1);pc=int(address,16)
  end=int(lines[i+1].split()[0],16) if i+1<len(lines) else labels['done']
  rr[pc]=classify(pc,s,end-pc)
  rr[pc]['opcode']=code[(pc-0x200)*3:(pc-0x200+1)*3].hex()
 return rr,labels
def pipeline(prev,cur):
 if prev is None:return 0,0
 ar=int(bool(cur['move_src'] & prev['alu_dst']))
 tr=int(bool(cur['move_src'] & prev['move_dst']))
 assert not(ar and tr),'Overlapping hazard requires separate qualification'
 return ar,tr
def branch_taken(r,next_pc):
 return r['family']=='JCC' and next_pc==int(r['assembly'].split()[-1][1:],16)
def cycle(r,prev=None,taken=True):
 ar,tr=pipeline(prev,r)
 branch=int(r['family']=='JCC' and not taken)
 best=r['base']+r['ea']+branch+ar+tr
 return best-int(r['short_write']),best,ar,tr,branch
def region(pc,L):
 if pc>=L['ratio']:return 'ratio_helper'
 if pc<L['sample']:return 'block_setup_clamp_ramp_setup'
 if pc<L['ramp_6']:return 'per_sample_parameter_ramps'
 if L['event']<=pc<L['after_9']:return 'BLEP_corrections_event_math'
 if L['pw_event']<=pc<L['wrap_8'] or L['wrap_event']<=pc<L['event']:return 'event_ratio_argument_setup'
 if pc>=L['after_9']:return 'naive_waveform_blend_output'
 return 'phase_update_event_decisions'
def helper_paths(P,L,old=False):
 # Static trace construction, no CPU: native k=0..3; validated stock API n<4d.
 if old:return None
 result=[]
 for k in range(4):
  pcs=[L['ratio'],L['ratio']+1,L['ratio']+2]
  for _ in range(k):pcs+=list(range(L['ratio_integer'],L['ratio_fraction']))
  pcs += [L['ratio_integer'],L['ratio_integer']+1]+list(range(L['ratio_fraction'],L['ratio_fraction']+3))
  pcs += [L['ratio_fraction']+3]*21+list(range(L['ratio_fraction']+4,L['ratio_zero']))
  prev=None;cost=0
  for i,pc in enumerate(pcs):
   r=P[pc];nxt=pcs[i+1] if i+1<len(pcs) else None
   cost+=cycle(r,prev,branch_taken(r,nxt))[1];prev=r
  result.append(dict(integer_part=k,issued=len(pcs),cycles=cost,includes_RTS=True,excludes_JSR=True))
 assert [r['issued'] for r in result]==[33,38,43,48]
 return result
def structural(P,L,helper_max):
 # Longest paths in acyclic main body. JSR abstracts exact bounded helper.
 # Previous instruction retained for actual arithmetic/transfer interlocks.
 normal_rts=L['ratio_zero']-1
 def longest(start,stop):
  @lru_cache(None)
  def visit(pc,previous):
   if pc==stop:return 0
   r=P[pc];prev=P.get(previous);fall=pc+r['words'];s=r['assembly'];family=r['family']
   if family=='JSR':return cycle(r,prev)[1]+helper_max+visit(fall,normal_rts)
   if family=='JMP':edges=[(int(s.split()[-1][1:],16),True)]
   elif family=='JCC':edges=[(int(s.split()[-1][1:],16),True),(fall,False)]
   else:edges=[(fall,True)]
   assert all(n>pc or n==stop for n,_ in edges),'Main-body cycle unexpectedly found'
   return max(cycle(r,prev,t)[1]+visit(n,pc) for n,t in edges)
  return visit(start,-1)
 startup=longest(0x200,L['sample']);body=longest(L['sample'],L['block_end'])
 exit_cost=cycle(P[L['block_end']])[1]
 return dict(startup_bound=startup,sample_path_bound=body,samples=32,helper_general_bound=helper_max,
  final_JMP=exit_cost,pipeline_boundary_allowance=12,cycles=startup+32*body+exit_cost+12,
  scope='CALCULATED conservative CFG bound; valid ratio API n<4d; internal private memory; no interrupts/DMA; all branch alternatives retained',
  control_paths_overapproximated=True,global_invalid_input_bound=False)
def suite_counts(suite,out=None):
 P,L=program(suite);families=sorted(set(r['family'] for r in P.values()))
 t=np.memmap(suite/'dsp-first/execution-pc.u16',dtype='<u2',mode='r');bs=rows(suite/'dsp-first/blocks.csv')
 sources=obj(suite/'cases.json');case={r['id']:r for r in sources}
 assert set(np.unique(t))<=set(P)
 size=4096
 ardest=np.zeros(size,dtype=np.uint8);movdest=ardest.copy();movsrc=ardest.copy()
 bases=np.zeros(size,dtype=np.int16);lowbase=bases.copy();ea=bases.copy();conditional=np.zeros(size,dtype=bool);targets=np.zeros(size,dtype=np.uint16)
 feature_names=['parallel_register_move','X_read','X_write','Y_read','Y_write','P_data_read','P_data_write','simultaneous_XY','same_space_multiaccess','accumulator_transfer','AGU_postincrement','AGU_explicit_write','MAC','MACR','MPY','DIV','DO','REP','JSR','RTS','JCC_taken','JCC_not_taken']
 features={n:np.zeros(size,dtype=np.uint8) for n in feature_names}
 for pc,r in P.items():
  ardest[pc]=r['alu_dst'];movdest[pc]=r['move_dst'];movsrc[pc]=r['move_src'];bases[pc]=r['base'];lowbase[pc]=r['base']-int(r['short_write']);ea[pc]=r['ea']
  if r['family']=='JCC':conditional[pc]=True;targets[pc]=int(r['assembly'].split()[-1][1:],16)
  for n,v in [('parallel_register_move',r['parallel']),('accumulator_transfer',r['acc_transfer']),('AGU_postincrement',r['agu_update']),('AGU_explicit_write',r['agu_explicit_write'])]:features[n][pc]=v
  if r['mem']!='none':features[r['mem']][pc]=1
  if r['family'] in features:features[r['family']][pc]=1
 region_totals=defaultdict(lambda:np.zeros(6,dtype=np.int64));family_totals=defaultdict(lambda:np.zeros(6,dtype=np.int64));pc_totals=defaultdict(lambda:np.zeros(6,dtype=np.int64))
 block_census=[];est=[];position=0;calls=[];helper_cycles=[];helper_issued=[]
 for block_index,b in enumerate(bs):
  n=int(b['instructions']);pcs=np.asarray(t[position:position+n]);position+=n
  prev=np.empty_like(pcs);prev[0]=0;prev[1:]=pcs[:-1]
  nxt=np.empty_like(pcs);nxt[:-1]=pcs[1:];nxt[-1]=L['done']
  taken=conditional[pcs]&(nxt==targets[pcs]);false=conditional[pcs]&~taken
  ar=((movsrc[pcs]&ardest[prev])!=0).astype(np.int16);tr=((movsrc[pcs]&movdest[prev])!=0).astype(np.int16)
  assert not np.any(ar&tr)
  branch=false.astype(np.int16);best=bases[pcs]+ea[pcs]+branch+ar+tr;lower=lowbase[pcs]+ea[pcs]+branch+ar+tr
  counts=np.bincount(pcs,minlength=size);best_pc=np.bincount(pcs,weights=best,minlength=size)
  lower_pc=np.bincount(pcs,weights=lower,minlength=size);ar_pc=np.bincount(pcs,weights=ar,minlength=size);tr_pc=np.bincount(pcs,weights=tr,minlength=size);br_pc=np.bincount(pcs,weights=branch,minlength=size)
  census={k:int(counts[[pc for pc,r in P.items() if r['family']==k]].sum()) for k in families}
  assert sum(census.values())==n
  census.update({k:int(np.dot(counts,ft)) for k,ft in features.items() if k not in ['JCC_taken','JCC_not_taken']})
  census['JCC_taken']=int(taken.sum());census['JCC_not_taken']=int(false.sum())
  entry=dict(index=block_index,case=int(b['case']),name=case[int(b['case'])]['name'],block=int(b['block']),sample_rate=case[int(b['case'])]['rate'],issued=n,
   lower_bound=int(lower.sum()),best_documented_estimate=int(best.sum()),observed_trace_upper_bound=int(best.sum())+12,
   nominal_base_cycles=int(bases[pcs].sum()),address_extra_cycles=int(ea[pcs].sum()),branch_penalty_cycles=int(branch.sum()),
   arithmetic_stall_cycles=int(ar.sum()),transfer_stall_cycles=int(tr.sum()),memory_wait_cycles=0,status_stall_cycles=0,AGU_stall_cycles=0,
   cold_fill_drain_allowance=12,conditional_utilization_percent=100*int(best.sum())/163840)
  est.append(entry);block_census.append(dict(index=block_index,case=entry['case'],block=entry['block'],**census))
  for pc in np.flatnonzero(counts):
   r=P[pc];stats=np.array([counts[pc],lower_pc[pc],best_pc[pc],ar_pc[pc],tr_pc[pc],br_pc[pc]],dtype=np.int64)
   region_totals[region(pc,L)]+=stats;family_totals[r['family']]+=stats;pc_totals[int(pc)]+=stats
  hmask=pcs>=L['ratio'];h=int(best[hmask].sum());c=int(counts[L['ratio']]);calls.append(c);helper_cycles.append(h);helper_issued.append(int(hmask.sum()))
  if out:
   assert census['DIV']==21*c and census['REP']==c and census['DO']==1 and census['JSR']==census['RTS']==c
   assert census['AGU_postincrement']==32 and census['P_data_read']==census['P_data_write']==0
   assert h==49*c and helper_issued[-1]==33*c
   assert int(b['ratio_calls'])==c
 assert position==len(t)
 result=dict(blocks=len(bs),issued_total=len(t),issued_min=min(x['issued'] for x in est),issued_mean=float(np.mean([x['issued'] for x in est])),issued_max=max(x['issued'] for x in est),
  lower_min=min(x['lower_bound'] for x in est),lower_mean=float(np.mean([x['lower_bound'] for x in est])),lower_max=max(x['lower_bound'] for x in est),
  best_min=min(x['best_documented_estimate'] for x in est),best_mean=float(np.mean([x['best_documented_estimate'] for x in est])),best_max=max(x['best_documented_estimate'] for x in est),
  observed_upper_max=max(x['observed_trace_upper_bound'] for x in est),helper_calls=sum(calls),helper_issued_total=sum(helper_issued),helper_cycles_total=sum(helper_cycles),
  helper_cycles_mean=sum(helper_cycles)/sum(calls),helper_calls_per_block_min=min(calls),helper_calls_per_block_max=max(calls),helper_calls_per_block_mean=float(np.mean(calls)))
 if out:
  bound=structural(P,L,max(x['cycles'] for x in helper_paths(P,L)));result['structural_upper']=bound
  for entry in est:entry['structural_upper_bound']=bound['cycles']
  csvout(out,'block-cycle-estimates.csv',est);csvout(out,'block-instruction-census.csv',block_census)
  minimum=min(range(len(est)),key=lambda i:est[i]['best_documented_estimate']);maximum=max(range(len(est)),key=lambda i:est[i]['best_documented_estimate'])
  scopes={'minimum_cycle_block':[minimum],'mean_all_blocks':list(range(len(bs))),'maximum_cycle_block':[maximum],
   'minimum_issued_block':[min(range(len(bs)),key=lambda i:est[i]['issued'])],'maximum_issued_block':[max(range(len(bs)),key=lambda i:est[i]['issued'])]}
  for name in ['bounded_stress','joint_sweep','long_continuity','frequency_cap']:
   indices=[i for i,x in enumerate(est) if x['name']==name];scopes[name+'_mean']=indices;scopes[name+'_max']=[max(indices,key=lambda i:est[i]['best_documented_estimate'])]
  records=[]
  for scope,indices in scopes.items():
   for family in families+[n for n in feature_names if n not in families]:
    values=[block_census[i][family] for i in indices]
    records.append(dict(scope=scope,blocks=len(indices),count_kind='exclusive_family' if family in families else 'overlapping_feature',family=family,
     total_count=sum(values),mean_count_per_block=sum(values)/len(indices),minimum_count=min(values),maximum_count=max(values),
     block_indices=';'.join(map(str,indices)) if len(indices)==1 else 'see block-instruction-census.csv'))
  csvout(out,'instruction-census.csv',records)
  timings=[]
  for pc,r in P.items():
   st=pc_totals[pc]
   timings.append(dict(pc=f'0x{pc:04X}',opcode=r['opcode'],assembly=r['assembly'],words=r['words'],family=r['family'],executed=int(st[0]),
    base_cycles=r['base'],address_extra_cycles=r['ea'],lower_base_cycles=r['base']-int(r['short_write']),branch_false_extra=1 if r['family']=='JCC' else 0,
    arithmetic_stall_total=int(st[3]),transfer_stall_total=int(st[4]),branch_false_penalty_total=int(st[5]),best_total_cycles=int(st[2]),
    memory_wait_cycles=0,parallel_register_move=r['parallel'],memory_pattern=r['mem'],source=r['source'],rule_class=r['rule_class'],applicability=r['applicability']))
  csvout(out,'instruction-timing.csv',timings)
  hotspots=[]
  for kind,totals in [('exclusive_family',family_totals),('exclusive_functional_region',region_totals)]:
   for rank,(name,st) in enumerate(sorted(totals.items(),key=lambda x:-x[1][2]),1):
    hotspots.append(dict(kind=kind,rank=rank,name=name,issued_total=int(st[0]),cycles_total=int(st[2]),cycles_per_block=float(st[2]/len(bs)),
     percent_documented_cycles=float(100*st[2]/sum(x['best_documented_estimate'] for x in est)),arithmetic_stall_cycles=int(st[3]),transfer_stall_cycles=int(st[4]),branch_false_extra_cycles=int(st[5])))
  csvout(out,'hotspots.csv',hotspots)
  branch_rows=[]
  for pc,r in P.items():
   if r['family']!='JCC':continue
   st=pc_totals[pc];false=int(st[5]);target=int(r['assembly'].split()[-1][1:],16)
   branch_rows.append(dict(pc=f'0x{pc:X}',assembly=r['assembly'],region=region(pc,L),taken=int(st[0])-false,not_taken=false,
    taken_cycles=4,not_taken_cycles=5,extra_pipeline_penalty_added=False,target_is_loop_LA_or_LA_minus1=target in [L['block_end']-1,L['block_end']-2]))
  assert not any(x['target_is_loop_LA_or_LA_minus1'] for x in branch_rows)
  csvout(out,'branch-audit.csv',branch_rows)
  dump(out,'representative-blocks.json',{scope:[est[i] for i in idx] for scope,idx in scopes.items() if len(idx)==1})
  dump(out,'native-helper-paths.json',helper_paths(P,L))
  dump(out,'structural-upper-bound.json',bound)
 return result
def audit(out):
 out=out.resolve()
 if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('Fresh timing output required')
 for suite in [NATIVE,OLD]:
  for n,h in obj(suite/'hashes.json').items():assert sha(suite/n)==h,n
  for n,h in obj(suite/'implementation-provenance.json').items():assert sha(ROOT/n)==h,n
 for n,h in obj(ROOT/'builds/phase20a-div/fixtures-compact/hashes.json').items():assert sha(ROOT/'builds/phase20a-div/fixtures-compact'/n)==h,n
 for n,h in [('DSP56300FM','b2e8e346fe55b05d20ad0e6bc03d45fd1e080d46d9a9cd9540271c0c37f5a31e'),('DSP56724RM','3b9876887ca7ecfec99d6e331ce1587e13955d0ecb4d0e8643dafd1df689370f')]:assert sha(ROOT/f'builds/phase19b/documentation/{n}.pdf')==h
 out.mkdir(parents=True);new=suite_counts(NATIVE,out);old=suite_counts(OLD)
 dump(out,'cycle-summary.json',new);dump(out,'restoring-static-comparison.json',old)
 assumptions=dict(status='CALCULATED / CONDITIONAL',rules={'instruction_base':'DOCUMENTED EXACT within DSP56300 full-pipeline/internal-memory premise',
  'arithmetic_transfer_stall':'DOCUMENTED EXACT: FM3-19..21, A-9 one clock when preceding instruction conflicts',
  'short_absolute_store':'DEVICE-FAMILY ASSUMPTION: second A-6 short MOVE row2 interpreted as store; lower uses1',
  'DSP56724_applicability':'DEVICE-FAMILY ASSUMPTION for exact timing tables; device RM4-4..6 explicitly corroborates same core/pipeline/forwarding',
  'pipeline_boundary':'CALCULATED conservative12-clock allowance from seven stages:6 fill+6 drain',
  'physical_Circuit_timing':'UNRESOLVED'},
  domain=dict(P='private internal [0x200,0x4BC), decoder padding internal',X='private internal state/control/scratch below0xAC',Y='private internal [0,0x20)',
   stack='SEN0, initialized empty, peak3 resident entries; no spill',addressing='linear M0..M7=0xFFFFFF; output(R0)+; no modulo/preupdate',
   interrupts=False,DMA=False,shared_bus=False,external_memory=False,program_data_access=False,host_wallclock_used=False),
  lower_bound='known timing/interlocks, short stores1, full pipeline, no boundary allowance',
  best_documented_estimate='table timing plus EA/false-Jcc/arithmetic/transfer stalls; short stores2; steady full pipeline',
  observed_trace_upper='best+12; applies only to existing paths and admitted private-memory model',
  structural_upper=new['structural_upper'],unconditional_Circuit_upper_bound=None,
  clock_Hz=246000000,clock_status='CONDITIONAL; prior PCTL/MCO wiring model, not physical measurement',
  rate_Hz=[48000,48046.875],conditional_budget_48000=164000,conditional_budget_48046_875=163840,
  stock_cycles_added=False,unknown_stock=['generators','filters/effects','worker activity','DMA/interrupts','scheduling margin','real placement/waits'])
 dump(out,'timing-assumptions.json',assumptions)
 scaling=[]
 for rate in assumptions['rate_Hz']:
  budget=246000000*32/rate
  for voices in [1,2,4,8,10,12]:
   for model,cycles in [('lower_mean',new['lower_mean']),('best_mean',new['best_mean']),('best_worst_observed',new['best_max']),('observed_trace_upper',new['observed_upper_max']),('conservative_structural_upper',new['structural_upper']['cycles'])]:
    total=voices*cycles;scaling.append(dict(rate_Hz=rate,voices=voices,model=model,cycles=total,conditional_budget=budget,conditional_block_percent=100*total/budget,remaining_cycles=budget-total,
     scheduling_feasibility='UNRESOLVED; arithmetic only',target10='Synth1mono+Synth2mono+MIDI1four+MIDI2four conceptual only' if voices==10 else ''))
 csvout(out,'voice-scaling.csv',scaling)
 provenance={p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),NATIVE/'hashes.json',OLD/'hashes.json',NATIVE/'dsp-first/execution-pc.u16',OLD/'dsp-first/execution-pc.u16',ROOT/'builds/phase19b/documentation/DSP56300FM.pdf',ROOT/'builds/phase19b/documentation/DSP56724RM.pdf']}
 dump(out,'provenance.json',provenance)
 dump(out,'hashes.json',{p.relative_to(out).as_posix():sha(p) for p in sorted(out.iterdir()) if p.is_file()})
 print(json.dumps(new,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--output-dir',type=Path,required=True);audit(a.parse_args().output_dir)
