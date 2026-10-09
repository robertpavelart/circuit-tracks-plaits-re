"""Allocate exact24-bit scratch values using CFG liveness; preserve golden math."""
import argparse,json,re,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'plaits/poc'));sys.path.insert(0,str(ROOT/'plaits/poc/div'))
from generate import Program
from generate_compact import helper
GOLD=ROOT/'builds/phase20a-div/final-compact'
POOL=['y1']+[f'r{i}' for i in range(1,8)]+[f'n{i}' for i in range(8)]
MEM=re.compile(r'x:>?\$([0-9a-f]{6})')
def source():
 p=Program();old=p.build();lines=old[:old.index('ratio:')]+helper()+['done:']
 assert '\n'.join(lines)+'\n'==(GOLD/'assembly/variablesaw.asm').read_text()
 return p,lines
def graph(p,lines):
 nodes=[];labels={};line_ids=[]
 for i,s in enumerate(lines):
  if s.endswith(':'):labels[s[:-1]]=len(nodes)
  else:nodes.append(s);line_ids.append(i)
 count=labels['ratio'];nodes=nodes[:count];line_ids=line_ids[:count]
 inv={v:k for k,v in p.names.items()};scratch=set(p.scratch)
 use=[];defs=[];succ=[]
 for i,s in enumerate(nodes):
  u=set();d=set();match=MEM.search(s)
  if match:
   v=inv[int(match[1],16)]
   if v in scratch:
    (u if s.startswith('move x:') else d).add(v)
  use.append(u);defs.append(d)
  if s.startswith('jmp '):edges={labels[s.split('@')[1]]}
  elif s.startswith(('jlt ','jge ','jle ','jne ','jeq ')):edges={i+1,labels[s.split('@')[1]]}
  else:edges={i+1}
  if i==labels['block_end']-1:edges.add(labels['sample'])
  succ.append({n for n in edges if n<count})
 live_in=[set() for _ in nodes];live_out=[set() for _ in nodes]
 while True:
  change=False
  for i in reversed(range(count)):
   out=set().union(*(live_in[j] for j in succ[i])) if succ[i] else set()
   inside=use[i]|(out-defs[i])
   if out!=live_out[i] or inside!=live_in[i]:change=True;live_out[i]=out;live_in[i]=inside
  if not change:break
 assert not live_in[0],live_in[0]
 interference={v:set() for v in scratch}
 for i in range(count):
  for v in defs[i]:
   for w in live_out[i]-{v}:interference[v].add(w);interference[w].add(v)
 return dict(nodes=nodes,labels=labels,line_ids=line_ids,use=use,defs=defs,succ=succ,live_in=live_in,live_out=live_out,interference=interference)
def allocation(p,g):
 layout=json.loads((GOLD/'assembly/layout.json').read_text())
 asm=(GOLD/'dsp-first/program.asm').read_text().splitlines();pcs=[int(s.split()[0],16) for s in asm][:len(g['nodes'])]
 trace=np.memmap(GOLD/'dsp-first/execution-pc.u16',dtype='<u2',mode='r');counts=np.bincount(trace,minlength=4096)
 weight={v:sum(int(counts[pc]) for pc,u,d in zip(pcs,g['use'],g['defs']) if v in u|d) for v in p.scratch}
 colors={};active={v for v in p.scratch if weight[v]}
 while active:
  v=max(active,key=lambda v:(len({colors[w] for w in g['interference'][v] if w in colors}),weight[v],len(g['interference'][v]),v))
  occupied={colors[w] for w in g['interference'][v] if w in colors};c=0
  while c in occupied:c+=1
  colors[v]=c;active.remove(v)
 assert all(colors[v]!=colors[w] for v in colors for w in g['interference'][v] if w in colors)
 slots={v:POOL[c] if c<len(POOL) else f'x:${c-len(POOL):06x}' for v,c in colors.items()}
 spills=max([c-len(POOL)+1 for c in colors.values() if c>=len(POOL)]+[0])
 assert spills<=0x20,'Scratch must not overlap retained X20..27'
 return slots,colors,spills,pcs,weight
def generate(out,peephole=True):
 out=Path(out).resolve();base=ROOT/'builds/phase20a-regopt'
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh REGOPT output required')
 p,lines=source();g=graph(p,lines);slots,colors,spills,pcs,weight=allocation(p,g)
 inverse={v:k for k,v in p.names.items()};edits={};removed=set();proof=[]
 # Dead single-use store->reload: preserve24-bit truncation with A1, not full A.
 pred=[set() for _ in g['nodes']]
 for i,ss in enumerate(g['succ']):
  for j in ss:pred[j].add(i)
 if peephole:
  for i,s in enumerate(g['nodes'][:-1]):
   if i in removed or not g['defs'][i]:continue
   v=next(iter(g['defs'][i]));j=i+1
   if g['succ'][i]!={j} or pred[j]!={i} or g['use'][j]!={v} or v in g['live_out'][j]:continue
   if not s.startswith('move a,x:') or not g['nodes'][j].startswith('move x:'):continue
   dst=g['nodes'][j].split(',')[-1]
   edits[g['line_ids'][j]]=f'move a1,{dst}';removed.add(g['line_ids'][i])
   proof.append(dict(kind='dead scratch store/reload replaced by exactA1 transfer',variable=v,store_PC=pcs[i],read_PC=pcs[j],destination=dst))
 generated=[]
 for i,s in enumerate(lines):
  if i in removed:continue
  if i in edits:generated.append(edits[i]);continue
  m=MEM.search(s)
  if m:
   v=inverse[int(m[1],16)]
   if v in slots:
    r=slots[v]
    if s.startswith('move x:'):s='move '+r+','+s.split(',')[-1]
    else:
     src=s.split()[1].split(',')[0]
     if src=='a':src='a1' # Explicit24-bit word; don't retain accumulator low bits.
     s='move '+src+','+r
   elif v=='ratio_integer_q':raise AssertionError('Unused helper word unexpectedly accessed')
   elif v.startswith('target_'):
    s=MEM.sub(f'x:${0x30+list(p.names)[7:10].index(v):06x}',s)
  generated.append(s)
 out.mkdir(parents=True)
 (out/'variablesaw.asm').write_text('\n'.join(generated)+'\n')
 loc={n:(slots[n] if n in slots else 'UNUSED' if n in p.scratch else (0x30+list(p.names)[7:10].index(n) if n.startswith('target_') else a)) for n,a in p.names.items()}
 layout=dict(origin=0x200,state_words=7,state_X=[0x20,0x27],control_X=[0x30,0x33],scratch_X=[0,spills],scratch_words=spills,
  register_pool=POOL,register_scratch_words=len(set(r for r in slots.values() if not r.startswith('x:'))),
  scratch_logical_values=43,output_Y=[0,32],render_samples=32,table_words=0,variables=loc,
  numeric_boundary='Every scratch store reads A1; single-use folding explicitly moves A1 (24bits)',helper='golden compact helper instructions unchanged')
 (out/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
 summary=dict(graph_colors=max(colors.values())+1,peak_CFG_live_words=max(map(len,g['live_in'])),registers=layout['register_scratch_words'],spills=spills,
  colors=colors,locations=slots,golden_memory_weights=weight,peepholes=proof,
  preservation='helper preservesY1,R1..7,N0..7; M0..7 remain linear; R0 solely output',main_instruction_count_before=len(g['nodes']),main_instruction_count_after=sum(not s.endswith(':') for s in generated[:generated.index('ratio:')]))
 (out/'allocation.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in summary.items() if k not in ['colors','locations','golden_memory_weights','peepholes']},indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',required=True);a.add_argument('--no-peephole',action='store_true');ns=a.parse_args();generate(ns.output_dir,not ns.no_peephole)
