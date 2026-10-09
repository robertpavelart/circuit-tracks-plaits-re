"""Deterministic adversarial search; all states evolve from the stock PoC reset."""
import argparse,json,random,csv
from pathlib import Path
from domain import *

def search(out,n):
 if out.exists() or not out.resolve().is_relative_to(ROOT/'builds/phase20a-bound'):raise ValueError('Fresh phase output required')
 out.mkdir(parents=True);rng=random.Random(20002001);best=-1;maxcalls=-1;records=[];pool=[]
 # Endpoint corners, nonzero interpolation remainders, low-frequency delayed
 # wraps, near-quarter shifts, and continuous targets. No state is injected.
 freqs=[1,2,3,31,32,33,32767,32768,32769,65535,F//32,F//8,H-33,H-32,H-31,H-2,H-1,H,H+1,F//2]
 widths=[0,1,2,F//4,F//2-33,F//2-1,F//2,F//2+1,F//2+33,3*F//4,F-2,F-1,F]
 shapes=[0,1,31,32,Q//2,Q-33,Q-1,Q]
 def control():
  return (rng.choice(freqs) if rng.random()<.85 else rng.randrange(1,H+1),
          rng.choice(widths) if rng.random()<.8 else rng.randrange(F+1),
          rng.choice(shapes) if rng.random()<.8 else rng.randrange(Q+1))
 for trial in range(n):
  if pool and trial%3:
   prior=list(rng.choice(pool)[1]);prior=prior[:rng.randrange(len(prior)+1)]
  else:prior=[]
  for _ in range(rng.randrange(1,9)):prior.append(control())
  state=RESET
  for c in prior:state,_,_=block(state,c)
  candidates=[control() for _ in range(6)]
  if trial%4==0:candidates += [(f,p,s) for f in [H-1,H-31,H] for p in [0,F] for s in [Q-1]]
  for c in candidates:
   st,cost,d=block(state,c)
   if cost>best or d['ratio_calls']>maxcalls:
    best=max(best,cost);maxcalls=max(maxcalls,d['ratio_calls'])
    records.append(dict(id=len(records),trial=trial,cycles=cost,ratio_calls=d['ratio_calls'],PW=d['events'].count('pw'),wrap=d['events'].count('wrap'),
                        initial_state=list(state),controls=list(c),preparation=[list(x) for x in prior],details=d))
    print('witness',trial,cost,'calls',d['ratio_calls'],'best',best,flush=True)
   pool.append((cost,prior+[c]))
  pool.sort(key=lambda x:-x[0]);pool=pool[:24]
 (out/'witnesses.json').write_text(json.dumps(records,indent=2)+'\n')
 (out/'search.json').write_text(json.dumps(dict(seed=20002001,trials=n,best=best,maximum_calls=maxcalls,witnesses=len(records),all_from_reset=True,complete_search=False),indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--trials',type=int,default=6000);a=p.parse_args();search(a.output_dir,a.trials)
