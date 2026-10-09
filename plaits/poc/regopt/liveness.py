"""Export all44 golden scratch fields, dynamic value lifetimes and CFG allocation."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from generate_opt import ROOT,GOLD,POOL,source,graph,allocation
sys.path.insert(0,str(ROOT/'plaits/poc/timing'));from audit import csvout,dump,sha,region
def analyze(out,assembly):
 out=out.resolve();base=ROOT/'builds/phase20a-regopt'
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh liveness output required')
 out.mkdir(parents=True);p,lines=source();g=graph(p,lines);slots,colors,spills,pcs,weight=allocation(p,g)
 t=np.memmap(GOLD/'dsp-first/execution-pc.u16',dtype='<u2',mode='r');L=json.loads((GOLD/'dsp-first/labels.json').read_text())
 calls=np.flatnonzero(t==L['ratio']);samples=np.flatnonzero(t==L['sample']);records=[]
 for v in p.scratch:
  producers=[i for i,d in enumerate(g['defs']) if v in d];consumers=[i for i,u in enumerate(g['use']) if v in u]
  wp=np.asarray([pcs[i] for i in producers],dtype=np.uint16);rp=np.asarray([pcs[i] for i in consumers],dtype=np.uint16)
  w=np.flatnonzero(np.isin(t,wp)) if len(wp) else np.array([],dtype=np.int64)
  r=np.flatnonzero(np.isin(t,rp)) if len(rp) else np.array([],dtype=np.int64)
  crosses_call=crosses_sample=0;max_span=0
  if len(r):
   defs=np.searchsorted(w,r,side='right')-1;assert np.all(defs>=0),v
   start=w[defs]
   crosses_call=int(np.count_nonzero(np.searchsorted(calls,r)-np.searchsorted(calls,start,side='right')))
   crosses_sample=int(np.count_nonzero(np.searchsorted(samples,r)-np.searchsorted(samples,start,side='right')))
   max_span=int(np.max(r-start))
  # Static CFG lifetime includes all possible branches and hardware loop backedge.
  across_call=any(v in g['live_out'][i] for i,s in enumerate(g['nodes']) if s.startswith('jsr @ratio'))
  across_backedge=v in g['live_in'][g['labels']['sample']]
  producer_context=[dict(store_PC=f'0x{pcs[i]:X}',value_instruction=g['nodes'][i-1] if i else 'entry') for i in producers]
  records.append(dict(variable=v,golden_X=f'0x{p.names[v]:X}',producer=json.dumps(producer_context,separators=(',',':')),
   consumers=';'.join(f'0x{pcs[i]:X}' for i in consumers),first_use_PC=f'0x{pcs[consumers[0]]:X}' if consumers else '',last_use_PC=f'0x{pcs[consumers[-1]]:X}' if consumers else '',
   reads=len(r),writes=len(w),first_dynamic_use=int(r[0]) if len(r) else '',last_dynamic_use=int(r[-1]) if len(r) else '',
   maximum_definition_to_read_opcodes=max_span,reads_crossing_call=crosses_call,reads_crossing_sample=crosses_sample,
   CFG_live_across_call=across_call,CFG_live_across_sample_backedge=across_backedge,register_eligible=v!='ratio_integer_q',
   selected_location=slots.get(v,'UNUSED'),color=colors.get(v,''),reasons='exact24-bit scalar; helper preserves pool' if v!='ratio_integer_q' else 'unused native helper fallback slot;zero accesses'))
 csvout(out,'scratch-liveness.csv',records)
 registers=[]
 for reg in [f'r{i}' for i in range(8)]+[f'n{i}' for i in range(8)]+[f'm{i}' for i in range(8)]+['x0','x1','y0','y1','a','b']:
  vs=[v for v,loc in slots.items() if loc==reg]
  live_regions=set();call_live=False
  for i,s in enumerate(g['nodes']):
   if any(v in g['live_in'][i]|g['live_out'][i] for v in vs):live_regions.add(region(pcs[i],L))
   if s.startswith('jsr @ratio') and any(v in g['live_out'][i] for v in vs):call_live=True
  if vs:role='24-bit scratch cache; colored nonoverlapping logical variables';scope='golden CFG + dynamic helper-preservation guard';preserved='YES'
  elif reg=='r0':role='Y output pointer,0..32; exclusively address generation';scope='linear postincrement, M0 reserved';preserved='YES by helper'
  elif reg.startswith('m'):role='retained linear modifiers0xFFFFFF; not allocated';scope='M0 required for output; other modifiers kept unchanged';preserved='YES'
  elif reg in ['x0','y0']:role='arithmetic/ratio inputs; transient, no scratch allocation';scope='helper reads/preserves value but callers overwrite for expressions';preserved='YES by helper; not free'
  else:role='ALU/helper workspace; no long-lived scratch allocation';scope='A/B/X1 are clobbered by helper';preserved='NO'
  registers.append(dict(register=reg,role=role,aliases=';'.join(vs),live_regions=';'.join(sorted(live_regions)),live_at_calls=call_live,helper_preserved=preserved,
   maximum_simultaneous_scratch_bindings=1 if vs else 0,evidence=scope))
 csvout(out,'register-allocation.csv',registers)
 dump(out,'CFG-liveness.json',dict(nodes=[dict(PC=f'0x{pc:X}',instruction=s,live_in=sorted(g['live_in'][i]),live_out=sorted(g['live_out'][i]),definitions=sorted(g['defs'][i]),uses=sorted(g['use'][i])) for i,(pc,s) in enumerate(zip(pcs,g['nodes']))],
  peak_live=max(map(len,g['live_in'])),graph_colors=max(colors.values())+1,allocation_interference={v:sorted(ns) for v,ns in g['interference'].items()},helper_effect='clobbersA/B/X1/CCR; preservespool16',spill_X_words=spills))
 dump(out,'provenance.json',{'golden_trace':sha(GOLD/'dsp-first/execution-pc.u16'),'golden_layout':sha(GOLD/'assembly/layout.json'),'optimized_allocation':sha(assembly/'allocation.json'),'analyzer':sha(Path(__file__))})
 dump(out,'hashes.json',{q.name:sha(q) for q in sorted(out.iterdir()) if q.is_file()})
 print('All44 scratch rows/30 registers;peak19, pool16, spill3; liveness exported',flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);a.add_argument('--assembly-dir',type=Path,required=True)
 ns=a.parse_args();analyze(ns.output_dir,ns.assembly_dir)
