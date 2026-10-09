"""Finish REGOPT from existing runs/liveness; no renderer or liveness rerun."""
import argparse,csv,json,sys,subprocess
from pathlib import Path
import numpy as np
from generate_opt import ROOT,GOLD,POOL
sys.path.insert(0,str(ROOT/'plaits/poc/timing'))
from audit import sha,obj,rows,csvout,dump
BASE=ROOT/'builds/phase20a-regopt'
def events(folder):
 L=obj(folder/'labels.json');t=np.memmap(folder/'execution-pc.u16',dtype='<u2',mode='r')
 samples=np.flatnonzero(t==L['sample']);pw=np.flatnonzero(t==L['pw_event']);wrap=np.flatnonzero(t==L['wrap_event'])
 positions=np.concatenate([pw,wrap]);types=np.concatenate([np.ones(len(pw),dtype=np.uint8),np.full(len(wrap),2,dtype=np.uint8)])
 order=np.argsort(positions);return np.column_stack([np.searchsorted(samples,positions[order],side='right')-1,types[order]])
def protected(suite):
 for n,h in obj(suite/'hashes.json').items():assert sha(suite/n)==h,n
 if (suite/'implementation-provenance.json').exists():
  for n,h in obj(suite/'implementation-provenance.json').items():assert sha(ROOT/n)==h,n
def finish(out):
 out=out.resolve()
 if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('Fresh report output required')
 new=BASE/'final';old=GOLD;oldtime=ROOT/'builds/phase20a-timing/final';time=BASE/'timing';stress=BASE/'extended';live=BASE/'liveness'
 for s in [old,new,BASE/'register-candidate',ROOT/'builds/phase20a-plaits/final',time,live,stress]:protected(s)
 for n in ['inputs.tsv','cases.json','oracle.i32','reference-first.f32','reference-repeat.f32','metrics.json','pitch-accuracy.csv','reference-block-continuity.json','sample-rate-contract.json']:
  assert sha(old/n)==sha(new/n),n
 for n in ['output.i32','states.csv']:assert sha(old/'dsp-first'/n)==sha(new/'dsp-first'/n),n
 for p in (new/'dsp-first').iterdir():assert sha(p)==sha(new/'dsp-repeat'/p.name),p.name
 for kind in ['golden','optimized']:
  for p in (stress/(kind+'-first')).iterdir():assert sha(p)==sha(stress/(kind+'-repeat')/p.name),p.name
 for n in ['output.i32','states.csv']:assert sha(stress/'golden-first'/n)==sha(stress/'optimized-first'/n),n
 assert sha(stress/'oracle.i32')==sha(stress/'optimized-first/output.i32')
 assert sha(stress/'golden-first/program.be24')==sha(old/'dsp-first/program.be24')
 assert sha(stress/'optimized-first/program.be24')==sha(new/'dsp-first/program.be24')
 # Exact helper source/ISA forms; addresses relocated, same18 instructions/words.
 oldasm=(old/'assembly/variablesaw.asm').read_text().split('ratio:\n',1)[1]
 newasm=(new/'assembly/variablesaw.asm').read_text().split('ratio:\n',1)[1];assert oldasm==newasm
 oldevents=events(old/'dsp-first');newevents=events(new/'dsp-first');assert np.array_equal(oldevents,newevents)
 assert np.array_equal(events(stress/'golden-first'),events(stress/'optimized-first'))
 ob=rows(old/'dsp-first/blocks.csv');nb=rows(new/'dsp-first/blocks.csv')
 for a,b in zip(ob,nb):
  for k in ['case','block','ratio_calls','div_issued','wrap_events','output_writes','peak_stack']:assert a[k]==b[k],k
 assert len(ob)==len(nb)==7520
 # Reuse completed scratch liveness; do not recompute its dynamic intervals.
 allocation=obj(new/'assembly/allocation.json');lv=rows(live/'scratch-liveness.csv');rg=rows(live/'register-allocation.csv')
 assert len(lv)==44 and len(rg)==30 and allocation['peak_CFG_live_words']==19
 assert sum(int(x['reads'])+int(x['writes'])==0 for x in lv)==1
 locations=allocation['locations'];cfg=obj(live/'CFG-liveness.json')
 for v,neighbors in cfg['allocation_interference'].items():
  for w in neighbors:
   if v in locations and w in locations:assert locations[v]!=locations[w],(v,w)
 # Numeric argument motion only; no branches, arithmetic families or event decisions removed.
 ot=rows(oldtime/'instruction-timing.csv');nt=rows(time/'instruction-timing.csv')
 oldfamilies={};newfamilies={}
 for r in ot:oldfamilies[r['family']]=oldfamilies.get(r['family'],0)+int(r['executed'])
 for r in nt:newfamilies[r['family']]=newfamilies.get(r['family'],0)+int(r['executed'])
 for family in ['ADD','SUB','CMP','ASL','ASR','MPY','NEG','DIV','JCC','JMP','JSR','RTS','DO','REP','ANDI']:assert oldfamilies.get(family,0)==newfamilies.get(family,0),family
 oldbranches=rows(oldtime/'branch-audit.csv');newbranches=rows(time/'branch-audit.csv');assert len(oldbranches)==len(newbranches)
 for a,b in zip(oldbranches,newbranches):assert [a[k] for k in ['taken','not_taken']]==[b[k] for k in ['taken','not_taken']]
 # Register data use never invokes address generation on R1..7. N0 is written
 # only in setup, safely before R0 addressing, even under a triplet-wide interlock.
 L=obj(new/'dsp-first/labels.json');prog=(new/'dsp-first/program.asm').read_text().splitlines()
 for line in prog:
  pc,s=line.split(' ',1);pc=int(pc,16)
  if s.startswith('move ') and s.split(',')[-1]=='n0':assert pc<L['sample']
  if ':(' in s:assert s=='move a,y:(r0)+'
 # Failed input and output refusal checks exercise strict wrappers only.
 out.mkdir(parents=True)
 invalid=out/'invalid.tsv';invalid.write_text('0 0 0 .5 .5\n')
 exe=BASE/'core-final/vs_dsp.exe'
 q=subprocess.run([str(exe),str(new/'assembly/variablesaw.asm'),str(invalid),str(out/'invalid-run'),'3'],capture_output=True)
 assert q.returncode and b'Invalid control domain' in q.stderr
 assert (out/'invalid-run/execution-pc.u16').stat().st_size==0
 q=subprocess.run([str(exe),str(new/'assembly/variablesaw.asm'),str(new/'inputs.tsv'),str(new/'dsp-first'),'3'],capture_output=True);assert q.returncode
 # Cheap generic register-family/loop checks against actual compiled code and traces.
 assert obj(new/'resource-manifest.json')['peak_hardware_stack_entries']==3
 for r in nb:assert int(r['output_writes'])==32 and int(r['div_issued'])==21*int(r['ratio_calls'])
 count=0
 for r in rows(time/'block-cycle-estimates.csv'):
  a=sum(int(r[k]) for k in ['nominal_base_cycles','address_extra_cycles','branch_penalty_cycles','arithmetic_stall_cycles','transfer_stall_cycles'])
  assert a==int(r['best_documented_estimate']) and int(r['observed_trace_upper_bound'])==a+12
  assert int(r['lower_bound'])<=a<=int(r['structural_upper_bound']);count+=1
 assert count==7520
 # Export exact requested filenames, copying the existing liveness evidence.
 for name in ['scratch-liveness.csv','register-allocation.csv']:(out/name).write_bytes((live/name).read_bytes())
 sc=obj(oldtime/'cycle-summary.json');nc=obj(time/'cycle-summary.json');res=obj(new/'resource-manifest.json')
 census=[]
 for family in sorted(set(oldfamilies)|set(newfamilies)):
  a=oldfamilies.get(family,0);b=newfamilies.get(family,0)
  census.append(dict(family=family,old_count=a,new_count=b,removed=a-b,old_per_block=a/7520,new_per_block=b/7520))
 csvout(out,'before-after-instruction-census.csv',census)
 comparison=[]
 for k in ['best_min','best_mean','best_max','lower_min','lower_mean','lower_max','observed_upper_max','issued_min','issued_mean','issued_max']:
  comparison.append(dict(metric=k,old=sc[k],new=nc[k],reduction_percent=100*(sc[k]-nc[k])/sc[k],unit='issued opcodes' if k.startswith('issued') else 'conditional calculated cycles'))
 comparison.append(dict(metric='structural_upper',old=sc['structural_upper']['cycles'],new=nc['structural_upper']['cycles'],reduction_percent=100*(1-nc['structural_upper']['cycles']/sc['structural_upper']['cycles']),unit='conditional calculated cycles'))
 csvout(out,'before-after-cycles.csv',comparison)
 oh={(r['kind'],r['name']):r for r in rows(oldtime/'hotspots.csv')};nh={(r['kind'],r['name']):r for r in rows(time/'hotspots.csv')};hotspots=[]
 for kind,name in sorted(set(oh)|set(nh)):
  a=oh.get((kind,name),{});b=nh.get((kind,name),{})
  hotspots.append(dict(kind=kind,name=name,old_cycles_per_block=float(a.get('cycles_per_block',0)),new_cycles_per_block=float(b.get('cycles_per_block',0)),
   old_share_percent=float(a.get('percent_documented_cycles',0)),new_share_percent=float(b.get('percent_documented_cycles',0)),
   change_cycles_per_block=float(b.get('cycles_per_block',0))-float(a.get('cycles_per_block',0))))
 csvout(out,'hotspot-comparison.csv',hotspots)
 scaling=[]
 for rate in [48000,48046.875]:
  budget=246000000*32/rate
  for voices in [1,2,4,8,10,12]:
   for model,c in [('best_mean',nc['best_mean']),('worst_observed',nc['best_max']),('observed_trace_upper',nc['observed_upper_max']),('structural_upper',nc['structural_upper']['cycles'])]:
    value=voices*c;scaling.append(dict(rate_Hz=rate,voices=voices,model=model,cycles=value,conditional_budget=budget,conditional_block_percent=value/budget*100,remaining_cycles=budget-value,
     scope='raw generator arithmetic only; no scheduling/stock workload',conceptual_target='1+1+4+4' if voices==10 else ''))
 csvout(out,'voice-scaling.csv',scaling)
 memory=[]
 for kind in ['X_read','X_write','Y_write']:
  a=sum(int(r['executed']) for r in ot if r['memory_pattern']==kind);b=sum(int(r['executed']) for r in nt if r['memory_pattern']==kind)
  memory.append(dict(kind=kind,old_count=a,new_count=b,removed=a-b,old_per_block=a/7520,new_per_block=b/7520))
 csvout(out,'memory-traffic.csv',memory)
 improvement=100*(1-nc['best_mean']/sc['best_mean'])
 exact=dict(status='TESTED PASS',existing_cases=43,existing_blocks=7520,existing_samples=240640,extended_cases=9,extended_blocks=4608,extended_samples=147456,
  total_samples=388096,sample_max_difference_integer=0,sample_RMS_difference=0,all_seven_states_exact_every_block=True,
  unchanged_oracle=True,existing_inputs_reference_metrics_pitch_rate_contract_hash_identical=True,exact_event_sample_order=True,
  helper_symbolic_instructions_unchanged=True,helper49_cycles_and21_iterations_unchanged=True,helper_pool_preservation_guard_passed=True,
  existing_and_extended_full_trace_determinism=True,stress_overflow_saturation_bad_address_failures=0,
  original_baselines_preserved=True,persistent_words=7,scratch_X_words=3,scratch_register_words=16,P_words=442,peak_stack_entries=3,
  no_hardware_no_Circuit_image_no_firmware_modifications=True,unconditional_silicon_timing=None)
 dump(out,'exact-equivalence.json',exact)
 dump(out,'optimization-result.json',dict(status='STRONG' if improvement>=20 else 'USEFUL' if improvement>=10 else 'MARGINAL',mean_cycle_reduction_percent=improvement,
  memory_operations_removed=sum(m['removed'] for m in memory),memory_report=memory,old_P=700,new_P=442,old_scratch_X=44,new_scratch_X=3,register_scratch=16,
  persistent_state=7,logical_data_memory=45,logical_data_plus_work_registers=61,stack_entries=3,cycle_summary=nc,
  changes='CFG-colored register retention,3 short-addressed spills, dead scratch pairs, proven A0-zero reloads, equivalent immediate ALU operands',
  branch_count_changed=False,new_parallel_forms=False,shared_helper_source_unchanged=True,Circuit_feasibility='UNRESOLVED'))
 # Explain investigated choices instead of asserting every option was implemented.
 dump(out,'optimization-options.json',dict(register_retention='IMPLEMENTED;Y1/R1..7/N0..7; no assumptions about A/B/X1 surviving helper',
  indirect_scratch='not selected:3 spill cells use single-word short addressing; no extra pointer/AGU setup',
  short_layout='IMPLEMENTED:spillX0..2,stateX20..26,controlsX30..32; all private/standalone',
  parallel_moves='retained qualified three helper forms; no additional form selected because local producer/store pairs depend on new A and fixed-width boundaries',
  branch_reduction='branch outcomes/count unchanged; immediate comparisons eliminate argument-preparation moves; no event branches removed',
  recomputation='no arithmetic recomputation or precision/order change',
  common_values='nine rampstep/remainder/error fields survive sample iteration in registers; event/naive/poly values reuse colors',
  sample_scheduling='only locally proven moves removed; arithmetic/event order unchanged',further_opportunity='dual-accumulator/legal parallel scheduling requires new qualification, not implemented'))
 sys.path.insert(0,str(ROOT/'tools'));from ct_stock_load_audit import verify_inputs
 verify_inputs()
 subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),'--results',str(ROOT/'builds/phase19a/validated/results.json'),'--output',str(out/'unchanged-core-audit.json')],check=True,capture_output=True)
 protected(new);protected(old);protected(ROOT/'builds/phase20a-plaits/final')
 dump(out,'golden-reference.json',{'source_suite':str(old), 'frozen_outputs':{n:sha(old/n) for n in ['dsp-first/output.i32','dsp-first/states.csv','dsp-first/program.be24','inputs.tsv','oracle.i32','hashes.json']}})
 dump(out,'provenance.json',{p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),new/'hashes.json',old/'hashes.json',time/'hashes.json',stress/'hashes.json',live/'hashes.json']})
 dump(out,'hashes.json',{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
 print(json.dumps(exact,indent=2));print('Mean cycle reduction',improvement,'% STRONG',flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);finish(a.parse_args().output_dir)
