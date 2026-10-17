"""Measured source/statistics/provenance, without modifying input artifacts."""
from environment import ROOT,REF,PUBLISHED,authentic_session,sha
from master_path import OUT
import json,csv,math,collections
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PC,UC_ARM_REG_LR
def stats(v):
 if not v:return dict(min=None,max=None,peak=None,RMS=None,nonzero=0,samples=0)
 v=[n-0x1000000 if n&0x800000 else n for n in v]
 return dict(min=min(v),max=max(v),peak=max(map(abs,v)),RMS=math.sqrt(sum(n*n for n in v)/len(v)),nonzero=sum(n!=0 for n in v),samples=len(v))
def stages(name):
 rows=[];first={};totals=collections.defaultdict(list)
 for l in (OUT/name/'stages.txt').open():
  t=l.split()
  if t[0]!='S':continue
  block,group,pc=int(t[1]),int(t[2],16),int(t[4],16);v=[int(n,16) for n in t[9:]]
  r=dict(block=block,bank=group,PC=f'{pc:X}',stage=t[5],space=t[6],base=t[7],**stats(v));rows.append(r)
  k=(group if 0x900<=pc<0xc30 else -1,t[5]);totals[k].extend(v)
  if any(v) and k not in first:first[k]=r
 with (OUT/name/'stage-statistics.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
 result=[]
 for (g,tag),v in totals.items():result.append(dict(bank=g,stage=tag,**stats(v),first_nonzero=first.get((g,tag))))
 # Output ring is interleaved Q1.23, 32 L/R pairs.
 ring=[r for r in rows if r['stage']=='output_ring' and r['nonzero']]
 stereo=[]
 for l in (OUT/name/'stages.txt').open():
  t=l.split()
  if t[0]=='S' and t[5]=='output_ring':stereo.append((int(t[1]),[int(n,16) for n in t[9:]]))
 first_stereo=next(((b,v) for b,v in stereo if any(v)),None)
 result=dict(stages=result,output_first=None if first_stereo is None else dict(block=first_stereo[0],left=stats(first_stereo[1][::2]),right=stats(first_stereo[1][1::2])),output_all=dict(left=stats([n for _,v in stereo for n in v[::2]]),right=stats([n for _,v in stereo for n in v[1::2]])))
 (OUT/name/'stage-summary.json').write_text(json.dumps(result,indent=2));return result
def sources():
 import capstone
 md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB|capstone.CS_MODE_MCLASS)
 ranges=[(0x80213b0,0x80213d4),(0x80214d0,0x8021578),(0x80217b4,0x8021886),(0x8021950,0x8021960),(0x80287c4,0x80287de),(0x8028c9c,0x8028d32),(0x8028d32,0x8028dc8),(0x8028ef2,0x8028f3c),(0x8028f40,0x8028fe2),(0x8036192,0x8036196),(0x803be3e,0x803beac)]
 text=[]
 for a,b in ranges:
  for i in md.disasm(PUBLISHED[a-0x8010000:b-0x8010000],a):text.append(f'{i.address:08x}: {i.mnemonic:<8} {i.op_str}')
 (OUT/'ARM-controlling-paths.asm').write_text('\n'.join(text)+'\n')
 s=authentic_session();records=[];active=None
 def code(uc,a,n,d):
  nonlocal active
  if active and a==active['return_PC']:
   active['result']=uc.reg_read(UC_ARM_REG_R0);active=None
  if a==0x8036192:
   active=dict(bank=uc.reg_read(UC_ARM_REG_R0),index=uc.reg_read(UC_ARM_REG_R1),return_PC=uc.reg_read(UC_ARM_REG_LR)&~1,reads=[]);records.append(active)
 def read(uc,access,a,n,v,d):
  if active:active['reads'].append(dict(PC=uc.reg_read(UC_ARM_REG_PC),address=a,size=n,value=int.from_bytes(uc.mem_read(a,n),'little')))
 s.e.uc.hook_add(UC_HOOK_CODE,code);s.e.uc.hook_add(UC_HOOK_MEM_READ,read)
 s.events=[];s.capture('global',0x8028ef2);s.capture('settings',0x8028fd6)
 (OUT/'ARM-getter-provenance.json').write_text(json.dumps(records,indent=2))
 (OUT/'ARM-provenance-events.json').write_text(json.dumps(s.events,indent=2))
 selected=[r for r in records if (r['bank'],r['index']) in [(32,46),(32,47),(32,50),(32,51),(33,0),(33,1),(33,7)]]
 print(json.dumps(selected,indent=2))
if __name__=='__main__':
 sources()
 for name in ['before','global-restored','synth1','synth2','both','paired-baseline','paired-layout-A']:
  r=stages(name);print(name,r['output_first'],r['output_all'])
