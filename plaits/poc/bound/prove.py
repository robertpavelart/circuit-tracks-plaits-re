"""Finite branch/event relaxation, exact ramp proof and unchanged-trace checks.

The DP is an upper-bound relaxation, NOT a claim that its maximizing ordering
is a reachable oscillator trajectory. The 44-cycle search gap stays unresolved.
"""
import argparse,json,itertools
from functools import lru_cache
import numpy as np
from domain import *

def automaton(pmax,wmax):
 @lru_cache(None)
 def go(n,hi,p,w,cooldown):
  if n==32:return (0,())
  cd=max(0,cooldown-1)
  options=[(204 if hi else 200,'none',hi,p,w,cd)]
  if not hi and p<pmax:options.append((581,'pw',1,p+1,w,cd))
  if hi and w<wmax and not cooldown:options.append((552,'wrap',0,p,w+1,3))
  vals=[]
  for cost,event,h,pp,ww,cc in options:
   tail,events=go(n+1,h,pp,ww,cc);vals.append((cost+tail,(event,)+events))
  return max(vals)
 result=max(((*go(0,h,0,0,0),h) for h in [0,1]))
 return dict(base_cycles=result[0],maximizing_relaxed_events=result[1],initial_high=result[2],states=go.cache_info().currsize,
             reachability='aggregate-event relaxation only; maximizing sample ordering not proved reachable')

def qualify(out):
 if out.exists() or not out.resolve().is_relative_to(ROOT/'builds/phase20a-bound'):raise ValueError('Fresh proof output required')
 out.mkdir(parents=True)
 profiles=cfg_profiles()
 for r in profiles:
  base=sample((False,)*3,r['high'],r['cross'],r['event'],r['upper'],(0,)*(1 if r['event']=='none' else 4))[0]
  assert r['cycles']==base+10*sum(r['carries'])
 normal=automaton(8,8);exception=automaton(6,5)
 normal_bound=normal['base_cycles']+930+106+3+12
 exceptional_bound=exception['base_cycles']+930+106+3+12+22
 assert normal_bound==13379 and exceptional_bound<normal_bound
 # Exact floor interpolation identities for all remainders; algebra handles
 # the unbounded quotient. No full 24-bit state brute force or sampled proof.
 for d in range(-63,64):
  a=d//32;r=d%32;cur=0;err=0;carries=0
  for j in range(1,33):
   cur+=a;err+=r
   if err>=32:err-=32;cur+=1;carries+=1
   assert cur==(j*d)//32
  assert cur==d and carries==r
 # Qualify every compact branch transition against existing full traces, no
 # renderer re-execution and no repeat of the completed liveness work.
 qualifications=[]
 for suite,run,timing in [
  (ROOT/'builds/phase20a-regopt/final','dsp-first',ROOT/'builds/phase20a-regopt/timing/block-cycle-estimates.csv'),
  (ROOT/'builds/phase20a-regopt/extended','optimized-first',ROOT/'builds/phase20a-regopt/extended-timing/block-cycle-estimates.csv')]:
  inputs=[line.split() for line in (suite/'inputs.tsv').read_text().splitlines()]
  bs=audit.rows(suite/run/'blocks.csv');ss=audit.rows(suite/run/'states.csv');ts=audit.rows(timing)
  trace=np.memmap(suite/run/'execution-pc.u16',dtype='<u2',mode='r');pos=0;last=None;ks=[0,0,0,0];eventmax=0
  for inp,b,s,t in zip(inputs,bs,ss,ts):
   i,j,f,p,sh=inp;i=int(i)
   if i!=last:state=RESET;last=i
   control=[int(float(f)*F+.5),int(float(p)*F+.5),int(float(sh)*Q+.5)]
   state,cost,d=block(state,control,True)
   n=int(b['instructions']);assert np.array_equal(np.array(d['trace'],dtype='<u2'),trace[pos:pos+n]);pos+=n
   assert cost==int(t['best_documented_estimate'])
   assert list(state)==[int(s[k]) for k in ['phase','high','frequency','pw','shape']]
   assert d['ratio_calls']==int(b['ratio_calls']) and 32<=d['ratio_calls']<=80
   assert d['events'].count('pw')<=8 and d['events'].count('wrap')<=8
   for v in d['samples']:assert 2*v['f']<=v['pw']<=F-2*v['f']
   for k in d['integer_parts']:ks[k]+=1
   eventmax=max(eventmax,sum(x!='none' for x in d['events']))
  assert pos==len(trace) and len(inputs)==len(bs)==len(ss)==len(ts)
  qualifications.append(dict(suite=suite.relative_to(ROOT).as_posix(),blocks=len(bs),samples=32*len(bs),full_PC_trace_exact=True,cycle_model_exact=True,branch_state_exact=True,maximum_events=eventmax,ratio_integer_parts=ks))
  print('existing exact transition qualification',suite.name,len(bs),'blocks',flush=True)
 (out/'proof.json').write_text(json.dumps(dict(status='PROVEN-BOUND / CONDITIONAL',normal=normal,first_sample_deferred_wrap=exception,
  normal_upper=normal_bound,exception_upper=exceptional_bound,carry_cost_per_occurrence=10,maximum_total_carries=93,
  startup_upper=106,exit=3,boundary=12,helper_extra_per_integer_part=11,global_upper=max(normal_bound,exceptional_bound),
  quotient_remainder_identity_exhaustive=True,branch_cost_profiles=len(profiles),qualifications=qualifications),indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);qualify(p.parse_args().output_dir)
