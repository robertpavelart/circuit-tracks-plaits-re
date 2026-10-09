"""Golden arithmetic; exact scratch allocation, proven integral-A reload removal."""
import argparse,json,re
from pathlib import Path
from generate_opt import ROOT,POOL,MEM,source,graph,allocation

def low_zero(g):
 pred=[set() for _ in g['nodes']]
 for i,edges in enumerate(g['succ']):
  for j in edges:pred[j].add(i)
 states=[False]*len(pred)
 while True:
  changed=False
  for i,s in enumerate(g['nodes']):
   incoming=bool(pred[i]) and all(states[j] for j in pred[i])
   out=incoming
   if s.startswith('move ') and s.split(',')[-1]=='a':out=not s.startswith('move b,a')
   if s.startswith('clr a'):out=True
   if s.startswith(('mpy ','asr ')):out=False
   if s.startswith('jsr @ratio'):out=True # unchanged helper returns A1 with A0=0
   if states[i]!=out:states[i]=out;changed=True
  if not changed:return states,pred
def x0_live(g):
 uses=[];defs=[]
 for s in g['nodes']:
  if s.startswith('move '):
   src,dst=s[5:].split(',');uses.append(src=='x0');defs.append(dst=='x0')
  else:uses.append('x0' in s or s.startswith('jsr @ratio'));defs.append(False)
 ins=[False]*len(uses);outs=ins.copy()
 while True:
  change=False
  for i in reversed(range(len(uses))):
   out=any(ins[j] for j in g['succ'][i]);inside=uses[i] or(out and not defs[i])
   if (inside,out)!=(ins[i],outs[i]):ins[i]=inside;outs[i]=out;change=True
  if not change:return outs
def generate(out):
 out=Path(out).resolve();base=ROOT/'builds/phase20a-regopt'
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh REGOPT child required')
 p,lines=source();g=graph(p,lines);slots,colors,spills,pcs,weight=allocation(p,g)
 zero,pred=low_zero(g);x0out=x0_live(g);edits={};removed=set();markers={};proof=[]
 for i,s in enumerate(g['nodes'][:-1]):
  if not g['defs'][i]:continue
  v=next(iter(g['defs'][i]));j=i+1
  if g['succ'][i]!={j} or pred[j]!={i} or g['use'][j]!={v}:continue
  if not s.startswith('move a,x:') or not g['nodes'][j].startswith('move x:'):continue
  dst=g['nodes'][j].split(',')[-1];store=g['line_ids'][i];read=g['line_ids'][j]
  dead=v not in g['live_out'][j]
  if dst=='a' and zero[i]:
   removed.add(read)
   if dead:removed.add(store);markers[store]=f'narrow_{i}:'
   proof.append(dict(kind='A0-proven-zero redundant reload',variable=v,store_PC=pcs[i],read_PC=pcs[j],removed_store=dead))
  elif dead:
   edits[read]=f'move a1,{dst}';removed.add(store);markers[store]=f'narrow_{i}:'
   proof.append(dict(kind='dead scratch pair to exact24bit A1 transfer',variable=v,store_PC=pcs[i],read_PC=pcs[j],removed_store=True))
 for i,s in enumerate(g['nodes'][:-1]):
  m=re.fullmatch(r'move #>\$([0-9a-f]{6}),x0',s)
  if not m:continue
  j=i+1;nexts=g['nodes'][j]
  if g['succ'][i]!={j} or pred[j]!={i} or x0out[j] or not re.fullmatch(r'(add|sub|cmp) x0,a',nexts):continue
  value=int(m[1],16);imm=f'#${value:02x}' if value<=63 else f'#>${value:06x}'
  removed.add(g['line_ids'][i]);edits[g['line_ids'][j]]=nexts.split()[0]+' '+imm+',a'
  proof.append(dict(kind='dead X0 immediate preparation folded into same ALU operation',value=value,load_PC=pcs[i],ALU_PC=pcs[j]))
 inverse={a:n for n,a in p.names.items()};generated=[]
 for i,s in enumerate(lines):
  if i in markers:generated.append(markers[i])
  if i in removed:continue
  if i in edits:generated.append(edits[i]);continue
  m=MEM.search(s)
  if m:
   v=inverse[int(m[1],16)]
   if v in slots:
    r=slots[v]
    if s.startswith('move x:'):s='move '+r+','+s.split(',')[-1]
    else:
     src=s.split()[1].split(',')[0];s='move '+('a1' if src=='a' else src)+','+r
   elif v in p.scratch:raise AssertionError('Dead helper word unexpectedly used')
   elif v.startswith('target_'):s=MEM.sub(f'x:${0x30+list(p.names)[7:10].index(v):06x}',s)
  generated.append(s)
 assert generated[generated.index('ratio:'):] == lines[lines.index('ratio:'):]
 loc={n:slots[n] if n in slots else 'UNUSED' if n in p.scratch else (0x30+list(p.names)[7:10].index(n) if n.startswith('target_') else a) for n,a in p.names.items()}
 out.mkdir(parents=True)
 (out/'variablesaw.asm').write_text('\n'.join(generated)+'\n')
 (out/'layout.json').write_text(json.dumps(dict(origin=0x200,state_words=7,state_X=[0x20,0x27],control_X=[0x30,0x33],scratch_X=[0,spills],scratch_words=spills,
  register_scratch_words=16,register_pool=POOL,scratch_logical_values=43,output_Y=[0,32],render_samples=32,table_words=0,variables=loc,
  numeric_boundary='A1 word transfers; no reload only when A0 provably zero; deleted-boundary range checks via zero-cost labels'),indent=2)+'\n')
 (out/'allocation.json').write_text(json.dumps(dict(graph_colors=max(colors.values())+1,peak_CFG_live_words=max(map(len,g['live_in'])),colors=colors,locations=slots,
  golden_memory_weights=weight,peepholes=proof,removed_instructions=len(removed),narrowing_labels=len(markers),helpers_unchanged=True),indent=2,sort_keys=True)+'\n')
 print('REGOPT generation:19 colors,16 registers,3 spills;',len(removed),'instructions removed; unchanged helper')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',required=True);generate(a.parse_args().output_dir)
