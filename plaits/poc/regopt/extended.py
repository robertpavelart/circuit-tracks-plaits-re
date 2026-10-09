"""Focused standalone stress: untouched native generator versus optimized code."""
import argparse,csv,json,math,random,subprocess,sys
from pathlib import Path
import numpy as np
from generate_opt import ROOT,GOLD
sys.path.insert(0,str(ROOT/'plaits/poc'))
from fixed_model import Fixed,F
def sha(p):
 import hashlib
 return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
 r=subprocess.run(list(map(str,args)),capture_output=True)
 if r.returncode:raise RuntimeError((args,r.returncode,r.stderr.decode(errors='replace')))
def extended(out,build,assembly):
 out=out.resolve();base=ROOT/'builds/phase20a-regopt'
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh stress output required')
 out.mkdir(parents=True);cases=[];seq=[];rng=random.Random(200020)
 def add(name,fn,rate=48000):
  i=len(cases);cases.append(dict(id=i,name=name,blocks=512,rate=rate,start=len(seq)*32))
  for b in range(512):seq.append((i,b,*fn(b)))
 add('notch_BLEP_quarter',lambda b:(.25,0,0))
 add('triangle_integratedBLEP_quarter',lambda b:(.25,1,1))
 add('simultaneous_notch_triangle_corrections',lambda b:(.25,.5,.5))
 add('near_quarter_extreme_PW_shape',lambda b:(.249999,0 if b%2 else 1,0 if b%2 else 1))
 add('extreme_PW_at_lower_frequency',lambda b:(55/48000,0 if b%2 else 1,.5))
 add('rapid_frequency_PW_shape_ramps',lambda b:(.25 if b%2 else 440*2**(-69/12)/48000,b%2,1-b%2))
 add('eight_step_control_corners',lambda b:([.003,.01,.03125,.125,.249999,.25,.125,.01][b%8],[0,1,0,.5,1,0,1,.5][b%8],[0,.5,1,.5,0,.5,1,.5][b%8]))
 for rate in [48000,48046.875]:
  controls=[(rng.choice([55,440,1760,8000,11000])/rate,rng.choice([0,1,.01,.99,.5]),rng.choice([0,1,.499999,.500001,.5])) for _ in range(512)]
  add('focused_random_'+str(rate),lambda b,controls=controls:controls[b],rate)
 inputs=out/'inputs.tsv';inputs.write_text(''.join(f'{i} {b} {f:.17g} {p:.17g} {s:.17g}\n' for i,b,f,p,s in seq))
 (out/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
 model=None;last=-1;oracle=[];ostates=[]
 for i,b,f,p,s in seq:
  if i!=last:model=Fixed();last=i
  oracle+=model.render32(f,p,s);ostates.append(model.state())
 np.asarray(oracle,dtype='<i4').tofile(out/'oracle.i32')
 for version in ['first','repeat']:
  run([build/'vs_golden.exe',GOLD/'assembly/variablesaw.asm',inputs,out/('golden-'+version),'ac'])
  print('Extended golden '+version+' complete',flush=True)
  run([build/'vs_dsp.exe',assembly/'variablesaw.asm',inputs,out/('optimized-'+version),'3'])
  print('Extended optimized '+version+' complete',flush=True)
 for kind in ['golden','optimized']:
  for p in (out/(kind+'-first')).iterdir():assert sha(p)==sha(out/(kind+'-repeat')/p.name),p.name
 for name in ['output.i32','states.csv']:
  assert (out/'golden-first'/name).read_bytes()==(out/'optimized-first'/name).read_bytes(),name
 assert (out/'oracle.i32').read_bytes()==(out/'optimized-first/output.i32').read_bytes()
 states=list(csv.DictReader((out/'optimized-first/states.csv').open()))
 for r,e in zip(states,ostates):assert [int(r[k]) for k in ['phase','next','previous_pw','high','frequency','pw','shape']]==e
 labels=json.loads((out/'optimized-first/labels.json').read_text());trace=np.memmap(out/'optimized-first/execution-pc.u16',dtype='<u2',mode='r')
 blocks=list(csv.DictReader((out/'optimized-first/blocks.csv').open()));offset=0;events=[]
 for c in cases:
  rs=blocks[c['id']*512:(c['id']+1)*512];n=sum(int(x['instructions']) for x in rs);t=trace[offset:offset+n];offset+=n
  events.append(dict(case=c['id'],name=c['name'],PW_events=int(np.count_nonzero(t==labels['pw_event'])),wrap_events=int(np.count_nonzero(t==labels['wrap_event'])),
   maximum_ratio_calls_per_block=max(int(x['ratio_calls']) for x in rs),mean_issued_per_block=sum(int(x['instructions']) for x in rs)/len(rs)))
 assert events[0]['PW_events']>0 and events[1]['wrap_events']>0 and events[2]['maximum_ratio_calls_per_block']==80
 (out/'events.json').write_text(json.dumps(events,indent=2)+'\n')
 (out/'result.json').write_text(json.dumps(dict(status='TESTED exact',cases=len(cases),blocks=len(seq),samples=len(oracle),samples_golden_exact=True,all_seven_states_golden_exact=True,
  independent_integer_oracle_exact=True,both_implementations_repeat_full_traces=True,saturation_failures=0,helper_register_clobber_failures=0,
  simultaneous='both correction contributions at one admitted event; no change to mutually exclusive PW/wrap branch order',hardware_access=False),indent=2)+'\n')
 (out/'hashes.json').write_text(json.dumps({p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()},indent=2)+'\n')
 print('Extended exact samples/states/oracle/repeat PASS',len(seq),'blocks',flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);a.add_argument('--build-dir',type=Path,required=True);a.add_argument('--assembly-dir',type=Path,required=True)
 ns=a.parse_args();extended(ns.output_dir,ns.build_dir.resolve(),ns.assembly_dir.resolve())
