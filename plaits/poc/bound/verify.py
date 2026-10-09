"""Verify search witnesses with the unchanged sealed standalone executable."""
import argparse,json,csv,subprocess,hashlib
import numpy as np
from domain import *
sys.path.insert(0,str(ROOT/'plaits/poc'))
from fixed_model import Fixed
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(out,search):
 if out.exists() or not out.resolve().is_relative_to(ROOT/'builds/phase20a-bound'):raise ValueError('Fresh proof output required')
 out.mkdir(parents=True)
 witnesses=json.loads((search/'witnesses.json').read_text())
 witnesses.append(dict(id=len(witnesses),controls=[1,F//2,0],preparation=[],cycles=block(RESET,(1,F//2,0))[1],ratio_calls=32))
 seq=[];expect=[];states=[];samples=[];modeltraces=[];summary=[]
 for w in witnesses:
  state=RESET;oracle=Fixed();case=w['id']
  controls=w['preparation']+[w['controls']]
  for b,c in enumerate(controls):
   seq.append((case,b,*c));state,cost,d=block(state,c,True)
   samples+=oracle.render32(c[0]/F,c[1]/F,c[2]/Q);states.append(oracle.state());modeltraces+=d['trace']
   assert [state[0],state[1],state[2],state[3],state[4]]==[oracle.phase,oracle.high,oracle.frequency,oracle.pw,oracle.shape]
   expect.append(dict(case=case,block=b,cycles=cost,ratio_calls=d['ratio_calls'],wrap=d['events'].count('wrap'),PW=d['events'].count('pw'),state=list(state),controls=c))
  assert expect[-1]['cycles']==w['cycles'] and expect[-1]['ratio_calls']==w['ratio_calls']
  summary.append(dict(case=case,target_block=len(controls)-1,cycles=cost,ratio_calls=d['ratio_calls'],wrap=d['events'].count('wrap'),PW=d['events'].count('pw'),preparation_blocks=len(controls)-1))
 inputs=out/'inputs.tsv';inputs.write_text(''.join(f'{i} {b} {f/F:.17g} {p/F:.17g} {s/Q:.17g}\n' for i,b,f,p,s in seq))
 (out/'cases.json').write_text(json.dumps([dict(id=w['id'],name='bound_witness_'+str(w['id']),rate=48046.875,blocks=len(w['preparation'])+1) for w in witnesses],indent=2)+'\n')
 np.array(samples,dtype='<i4').tofile(out/'oracle.i32')
 np.array(modeltraces,dtype='<u2').tofile(out/'model-pc.u16')
 assembly=ROOT/'builds/phase20a-regopt/final/assembly/variablesaw.asm'
 exe=ROOT/'builds/phase20a-regopt/core-final/vs_dsp.exe'
 # Existing wrapper restricts destinations to phase20a-regopt. Preserve it;
 # choose fresh children, then copy the generated evidence into this phase.
 import shutil
 runs=[]
 for repeat in ['first','repeat']:
  runout=ROOT/'builds/phase20a-regopt'/('bound-'+out.name+'-'+repeat)
  if runout.exists():raise ValueError('Fresh emulator output required')
  r=subprocess.run([str(exe),str(assembly),str(inputs),str(runout),'3'],capture_output=True)
  if r.returncode:raise RuntimeError(r.stderr.decode())
  shutil.copytree(runout,out/('dsp-'+repeat));runs.append(runout)
  print('unchanged emulator',repeat,'complete',len(seq),'blocks',flush=True)
 for p in runs[0].iterdir():assert sha(p)==sha(runs[1]/p.name),p.name
 assert sha(runs[0]/'program.be24')==sha(ROOT/'builds/phase20a-regopt/final/dsp-first/program.be24')
 assert (out/'oracle.i32').read_bytes()==(runs[0]/'output.i32').read_bytes()
 assert (out/'model-pc.u16').read_bytes()==(runs[0]/'execution-pc.u16').read_bytes()
 rr=audit.rows(runs[0]/'states.csv')
 for r,s in zip(rr,states):assert [int(r[k]) for k in ['phase','next','previous_pw','high','frequency','pw','shape']]==s
 # Independent existing cycle classification applied to actual emulator trace.
 projection=out/'timing-input';projection.mkdir()
 shutil.copytree(runs[0],projection/'dsp-first')
 shutil.copyfile(out/'cases.json',projection/'cases.json')
 timed=audit.suite_counts(projection,None)
 trace=np.memmap(runs[0]/'execution-pc.u16',dtype='<u2',mode='r');pos=0
 for b,e in zip(audit.rows(runs[0]/'blocks.csv'),expect):
  n=int(b['instructions']);pcs=trace[pos:pos+n];pos+=n;prev=None;cost=0
  for i,pc in enumerate(pcs):
   r=P[int(pc)];nxt=int(pcs[i+1]) if i+1<n else L['done']
   cost+=audit.cycle(r,prev,audit.branch_taken(r,nxt))[1];prev=r
  assert cost==e['cycles'];assert int(b['ratio_calls'])==e['ratio_calls'];assert int(b['wrap_events'])==e['wrap']
 assert pos==len(trace)
 (out/'validated-blocks.json').write_text(json.dumps(expect,indent=2)+'\n')
 (out/'validated-targets.json').write_text(json.dumps(summary,indent=2)+'\n')
 (out/'verification.json').write_text(json.dumps(dict(status='TESTED',blocks=len(seq),samples=len(samples),witnesses=len(witnesses),sample_max_difference=0,sample_RMS_difference=0,all_seven_states_exact=True,
   full_PC_trace_matches_branch_model=True,repeat_trace_and_artifacts_exact=True,unchanged_program_hash=sha(runs[0]/'program.be24'),timing=timed),indent=2)+'\n')
 (out/'provenance.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in [exe,assembly,ROOT/'plaits/poc/fixed_model.py',Path(__file__),Path(__file__).with_name('domain.py')]},indent=2)+'\n')
 print('exact samples/state/PC/cycles PASS',flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);a.add_argument('--search-dir',type=Path,required=True);ns=a.parse_args();verify(ns.output_dir,ns.search_dir)
