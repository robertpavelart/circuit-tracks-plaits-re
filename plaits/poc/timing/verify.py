"""Independent timing-accounting checks; no CPU, hardware or host benchmark."""
import argparse,csv,hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np
from audit import ROOT,BASE,NATIVE,OLD,program,cycle,pipeline,structural,helper_paths,sha,obj,rows,dump,csvout

def verify(first,repeat,out):
 out=out.resolve()
 if out.exists() or not out.is_relative_to(BASE) or out==BASE:raise ValueError('Fresh verification output required')
 for suite in [first,repeat]:
  for n,h in obj(suite/'hashes.json').items():assert sha(suite/n)==h,n
 for p in first.iterdir():
  if p.is_file():assert p.read_bytes()==(repeat/p.name).read_bytes(),p.name
 P,L=program(NATIVE)
 # Independent manual latency examples, not assertions copying full report.
 assert cycle(P[0x4B5])[1]==1                        # DIV iteration
 assert cycle(P[0x4B4])[1]==5                        # REP setup
 assert cycle(P[0x4B3])[1]==3                        # ANDI
 assert cycle(P[0x4AC],taken=False)[1]==5
 assert cycle(P[0x4AC],taken=True)[1]==4
 assert cycle(P[0x4B6],P[0x4B5])[1]==2               # DIV -> moveA0,A
 assert pipeline(P[0x4A6],P[0x4A8])==(0,1)           # memory loadA -> output moveA
 assert cycle(P[0x4B7],P[0x4B6])[1]==1               # ROL+moveB1,X1, not double counted
 assert cycle(P[0x4B8],P[0x4B7])[1]==1               # arithmetic forwarding
 assert cycle(P[0x4B9])[1]==3                        # resident-stack RTS
 assert cycle(P[0x200])[1]==2                       # long absolute memory load
 assert cycle(P[0x4A8],P[0x4A6])[1]==2               # postincrement hidden; transfer stall only
 branches=[r for r in P.values() if r['family']=='JCC']
 assert all(int(r['assembly'].split()[-1][1:],16)!=r['pc']+r['words'] for r in branches)
 assert helper_paths(P,L)==obj(first/'native-helper-paths.json')
 assert [r['cycles'] for r in helper_paths(P,L)]==[49,60,71,82]
 assert structural(P,L,82)['cycles']==30123
 b=rows(first/'block-cycle-estimates.csv');s=obj(first/'cycle-summary.json');census=rows(first/'block-instruction-census.csv')
 assert len(b)==len(census)==7520 and s['issued_total']==38641041
 for r,c in zip(b,census):
  best=int(r['nominal_base_cycles'])+int(r['address_extra_cycles'])+int(r['branch_penalty_cycles'])+int(r['arithmetic_stall_cycles'])+int(r['transfer_stall_cycles'])
  assert best==int(r['best_documented_estimate'])
  assert int(r['lower_bound'])<=best<=int(r['observed_trace_upper_bound'])<=int(r['structural_upper_bound'])
  assert int(r['observed_trace_upper_bound'])==best+12
  assert int(c['DIV'])==21*int(c['JSR']) and int(c['REP'])==int(c['RTS'])==int(c['JSR'])
  assert int(c['AGU_postincrement'])==32 and int(c['DO'])==1
  assert all(int(c[k])==0 for k in ['P_data_read','P_data_write','MAC','MACR','same_space_multiaccess','simultaneous_XY'])
  assert int(r['status_stall_cycles'])==int(r['AGU_stall_cycles'])==int(r['memory_wait_cycles'])==0
 # Independent family accounting from census totals plus emitted transition counts.
 timing=rows(first/'instruction-timing.csv')
 total=sum(int(r['best_total_cycles']) for r in timing)
 assert total==sum(int(r['best_documented_estimate']) for r in b)
 assert sum(int(r['executed']) for r in timing)==s['issued_total']
 ar=sum(int(r['arithmetic_stall_total']) for r in timing);tr=sum(int(r['transfer_stall_total']) for r in timing)
 assert ar==sum(int(r['arithmetic_stall_cycles']) for r in b) and tr==sum(int(r['transfer_stall_cycles']) for r in b)
 hs=rows(first/'hotspots.csv')
 for kind in ['exclusive_family','exclusive_functional_region']:
  assert sum(int(r['cycles_total']) for r in hs if r['kind']==kind)==total
 # The only explicit address register write is far from the first address use.
 first_trace=np.memmap(NATIVE/'dsp-first/execution-pc.u16',dtype='<u2',mode='r')
 at=0;agu_separation=[]
 for r in rows(NATIVE/'dsp-first/blocks.csv'):
  count=int(r['instructions']);pc=first_trace[at:at+count];at+=count
  written=np.flatnonzero(pc==0x280);used=np.flatnonzero(pc==0x4A8)
  assert len(written)==1 and len(used)==32
  assert used[0]-written[0]>3;agu_separation.append(int(used[0]-written[0]-1))
 # Hardware loop boundaries: actual last opcode is output4A8;31 backedges, one exit.
 # Sampling first+last cases suffices to validate relation; counts already all32.
 pos=0;loop_backedges=loop_exits=0
 for r in rows(NATIVE/'dsp-first/blocks.csv'):
  count=int(r['instructions']);pc=first_trace[pos:pos+count];pos+=count
  hits=np.flatnonzero(pc==0x4A8);nexts=pc[hits+1]
  assert np.count_nonzero(nexts==L['sample'])==31 and np.count_nonzero(nexts==L['block_end'])==1
  loop_backedges+=31;loop_exits+=1
 assert obj(NATIVE/'resource-manifest.json')['peak_hardware_stack_entries']==3
 scaling=rows(first/'voice-scaling.csv')
 for r in scaling:
  budget=246000000*32/float(r['rate_Hz']);cycles=float(r['cycles'])
  assert abs(float(r['conditional_budget'])-budget)<1e-9
  assert abs(float(r['conditional_block_percent'])-100*cycles/budget)<1e-10
  assert abs(float(r['remaining_cycles'])-(budget-cycles))<1e-9
 # Invalid output request must refuse without touching the existing evidence.
 refusal=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('audit.py')),'--output-dir',str(first)],capture_output=True)
 assert refusal.returncode and b'Fresh timing output required' in refusal.stderr
 for n,h in obj(first/'hashes.json').items():assert sha(first/n)==h,n
 # Recheck immutable renderer/core/input guards after report generation.
 for suite in [NATIVE,OLD]:
  for n,h in obj(suite/'implementation-provenance.json').items():assert sha(ROOT/n)==h,n
  for n,h in obj(suite/'hashes.json').items():assert sha(suite/n)==h,n
 sys.path.insert(0,str(ROOT/'tools'));from ct_stock_load_audit import verify_inputs
 verify_inputs()
 out.mkdir(parents=True)
 subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),'--results',str(ROOT/'builds/phase19a/validated/results.json'),'--output',str(out/'unchanged-core-audit.json')],check=True,capture_output=True)
 result=dict(status='PASS CONDITIONAL STANDALONE MODEL',success_gates={k:True for k in 'ABCDEFGHI'},
  numerical_renderer_rerun=False,renderer_sources_and_evidence_unchanged=True,all_reports_twice_byte_identical=True,
  trace_opcodes=38641041,blocks=7520,accounted_cycles=total,arithmetic_stalls=ar,transfer_stalls=tr,
  documented_examples_checked=12,AGU_min_intervening_opcodes=min(agu_separation),DO_backedges=loop_backedges,DO_exits=loop_exits,
  overwrite_refusal=True,originals_core_preserved=True,no_hardware_no_firmware_changes=True,
  upper_bound_scope='finite only under private/internal/zero-wait/no-IRQ/no-DMA and same-core timing assumptions',
  unconditional_Circuit_cycle_bound=None,source_SHA256=sha(Path(__file__)))
 dump(out,'verification.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--first',type=Path,required=True);a.add_argument('--repeat',type=Path,required=True);a.add_argument('--output-dir',type=Path,required=True)
 ns=a.parse_args();verify(ns.first,ns.repeat,ns.output_dir)
