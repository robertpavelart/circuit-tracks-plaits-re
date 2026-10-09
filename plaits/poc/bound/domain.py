"""Read-only compact exact branch-state model of the frozen REGOPT program.

No oscillator arithmetic implementation is changed.  Phase/PW/high and integer
interpolation determine all main-program branches; next/shape affect samples but
not the event decisions. Timing imports the pinned existing instruction model.
"""
from pathlib import Path
import sys,itertools
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'plaits/poc/regopt'))
sys.path.insert(0,str(ROOT/'plaits/poc/timing'))
import timing_opt, audit
audit.classify=timing_opt.classify
P,L=audit.program(ROOT/'builds/phase20a-regopt/final')
F=1<<22; Q=1<<21; H=F//4

def helper(k):
 p=[L['ratio'],L['ratio']+1,L['ratio']+2]
 for _ in range(k):p+=list(range(L['ratio_integer'],L['ratio_fraction']))
 p += [L['ratio_integer'],L['ratio_integer']+1]+list(range(L['ratio_fraction'],L['ratio_fraction']+3))
 return p+[L['ratio_fraction']+3]*21+list(range(L['ratio_fraction']+4,L['ratio_zero']))

def path(start,stop,decisions,ks=()):
 pcs=[];pc=start;ki=iter(ks)
 while pc!=stop:
  pcs.append(pc);r=P[pc];s=r['assembly'];fall=pc+r['words']
  if r['family']=='JSR':pcs+=helper(next(ki));pc=fall
  elif r['family']=='JMP':pc=int(s.split()[-1][1:],16)
  elif r['family']=='JCC':pc=int(s.split()[-1][1:],16) if decisions[pc] else fall
  else:pc=fall
 prev=None;cost=0
 for i,pc in enumerate(pcs):
  r=P[pc];nxt=pcs[i+1] if i+1<len(pcs) else stop
  cost+=audit.cycle(r,prev,audit.branch_taken(r,nxt))[1];prev=r
 return cost,tuple(pcs)

@lru_cache(None)
def sample(carries,high,cross,event,upper,ks):
 d={0x25c:not carries[0],0x26c:not carries[1],0x27c:not carries[2],
    0x293:bool(high),0x297:not cross,0x2b8:event!='wrap',0x345:event=='wrap',0x36b:upper}
 return path(L['sample'],L['block_end'],d,ks)

@lru_cache(None)
def setup(cap,lower,upper):
 return path(0x200,L['sample'],{0x203:not cap,0x216:not lower,0x21c:not upper})

def target(f,p,s):
 f=min(f,H);p=F//2 if f==H else min(max(p,2*f),F-2*f)
 return f,p,s

def block(state,controls,trace=False):
 # State: phase,high,frequency,PW,shape. All initial states in searches arise
 # from reset and preceding blocks, never injected into emulator state.
 ph,hi,fi,pw,sh=state; rawf,rawp,raws=controls
 ft,pt,st=target(*controls);old=[fi,pw,sh];tar=[ft,pt,st]
 delta=[t-c for t,c in zip(tar,old)];step=[d//32 for d in delta]
 rem=[d%32 for d in delta];err=[0]*3;cost,pcs=setup(rawf>=H,rawp<2*ft,rawp>F-2*ft)
 full=list(pcs) if trace else None; events=[];ksall=[];samples=[]
 for j in range(32):
  prevpw=pw;carries=[]
  for i in range(3):
   old[i]+=step[i];err[i]+=rem[i];carry=err[i]>=32
   if carry:err[i]-=32;old[i]+=1
   carries.append(carry)
  fi,pw,sh=old;ph+=fi;was_hi=hi;cross=ph>=pw;ev='none';ks=[];ratios=[]
  if not hi and cross:
   ev='pw';ratios.append((ph-pw,prevpw-pw+fi));hi=1
  elif ph>=F:
   ev='wrap';ph-=F;ratios.append((ph,fi));hi=0
  if ev!='none':ratios.extend([(fi,pw),(fi,F-pw)])
  upper=ph>=pw;ratios.append((ph-pw,F-pw) if upper else (ph,pw))
  for n,d in ratios:
   if n<0 or d<=0 or n>=4*d:raise ValueError(('ratio',n,d,state,controls,j))
   ks.append(n//d)
  c,ps=sample(tuple(carries),was_hi,cross,ev,upper,tuple(ks));cost+=c
  if trace:full.extend(ps)
  events.append(ev);ksall.extend(ks);samples.append(dict(j=j,phase=ph,high=hi,f=fi,pw=pw,shape=sh,event=ev,upper=upper,ratio_integer_parts=ks,carries=carries,cycles=c))
 cost+=3
 if trace:full.append(L['block_end'])
 return (ph,hi,fi,pw,sh),cost,dict(events=events,ratio_calls=len(ksall),integer_parts=ksall,samples=samples,remainders=rem,trace=full)

RESET=(0,0,int(.01*F+.5),F//2,0)

def cfg_profiles():
 rows=[]
 for carries in itertools.product([False,True],repeat=3):
  for hi in [0,1]:
   for cross in [False,True]:
    evs=['pw'] if not hi and cross else ['none','wrap']
    for ev in evs:
     for upper in [False,True]:
      # PW implies upper; wrap may be either. Non-wrap/high could be either.
      if ev=='pw' and not upper:continue
      ks=(0,)*(1 if ev=='none' else 4)
      cost,pcs=sample(carries,hi,cross,ev,upper,ks)
      rows.append(dict(carries=carries,high=hi,cross=cross,event=ev,upper=upper,cycles=cost))
 return rows

if __name__=='__main__':
 for ev in ['none','pw','wrap']:
  rr=[r for r in cfg_profiles() if r['event']==ev]
  print(ev,min(r['cycles'] for r in rr),max(r['cycles'] for r in rr))
 print('setups',[(c,l,u,setup(c,l,u)[0]) for c,l,u in itertools.product([False,True],repeat=3)])
 s=RESET
 for _ in range(3):
  s,c,d=block(s,(H,F//2,Q//2));print(s,c,d['ratio_calls'],d['events'])
