"""Compare all saved core0 samples/state/registers, with explicit dead-field exclusions."""
import collections,json
from environment import *
def read(profile):
    blocks=[];current=None;pwords=0
    for l in (OUT/f'long-{profile}/output.txt').read_text().splitlines():
        if l.startswith('RAN'):
            current=dict(ran=l,dumps={},regs={});blocks.append(current)
        elif l.startswith('REG:'):current['regs']={k:int(v,16) for k,v in (a.split('=') for a in l[4:].split())}
        elif l[:1] in 'XYP' and ':' in l:
            key,vals=l.split(':',1);current['dumps'][key]=[int(a,16) for a in vals.split()]
        elif l.startswith('PWRITES'):pwords=int(l.split()[1])
    return blocks[2:],pwords
def main():
    base,pw=read('original');result={};dead=set()
    for t in range(2):
        dead|={48*t+i for i in list(range(10,19))+list(range(22,48))}
        dead|={96+48*t+i for i in range(9,48)}
    for p in ('osc_only','osc_va'):
        rows,pw=read(p);assert len(rows)==len(base)==4096
        bad=[];cpu=collections.Counter();raw=collections.Counter();explained=[]
        for i,(a,b) in enumerate(zip(base,rows)):
            dif=[]
            for key,xs in a['dumps'].items():
                if key.startswith('P '):continue
                ys=b['dumps'][key]
                diff=[j for j,(x,y) in enumerate(zip(xs,ys)) if x!=y]
                if diff:raw[key]+=1
                excluded=dead if key=='X 003900' else {0x400+j for j in dead} if key=='X 037000' else set()
                # Source-defined sampler temporary register slots only.
                if key=='X 003d00':excluded|={16,17,23,28,29}
                remaining=[j for j in diff if j not in excluded]
                if remaining:dif.append(dict(key=key,indices=remaining[:16],values=[(xs[j],ys[j]) for j in remaining[:16]]))
            regs=[k for k,v in a['regs'].items() if b['regs'][k]!=v]
            for k in regs:cpu[k]+=1
            # LA can retain a relocated finished-loop address. No automatic
            # blanket normalization: all other CPU differences stay failures.
            regs_live=[k for k in regs if k!='la']
            if dif or regs_live:bad.append(dict(block=i,memory=dif,registers={k:[a['regs'][k],b['regs'][k]] for k in regs_live}))
            if 'la' in regs and len(explained)<8:explained.append(dict(block=i,LA=[a['regs']['la'],b['regs']['la']],SR=[a['regs']['sr'],b['regs']['sr']]))
        hist=dict((int(pc,16),int(n)) for pc,n in (l.split() for l in (OUT/f'long-{p}/hist.txt').read_text().splitlines()))
        start=0x3bba if p=='osc_only' else 0x3b54
        assert not any(start<=pc<0x4000 for pc in hist)
        result[p]=dict(blocks=len(rows),runtime_P_writes=pw,retained_mismatches=bad,raw_snapshot_difference_counts=dict(raw),CPU_difference_counts=dict(cpu),finished_loop_LA_examples=explained,outer_dispatch_histogram_free_tail_entries=0)
    watch=[]
    for l in (OUT/'long-original/watch.txt').read_text().splitlines():
        pc,ad,rw,v=l.split()
        if rw=='W' and ad.startswith('X:002c') and int(v,16):watch.append((pc,ad,int(v,16)))
    result['baseline_stock_mono_nonzero_writes']=len(watch)
    result['baseline_stock_mono_nonzero_examples']=watch[:8]
    result['scope']='Reference-style core0 with actual ARM dump initialization; no coupled core1, zero-filled SPI replies. Histogram PCs are outer interpreter dispatches; fast DO bodies can be executed inside a dispatch.'
    (OUT/'long-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({p:{k:v if k not in ('retained_mismatches',) else len(v) for k,v in d.items() if k not in ('finished_loop_LA_examples',)} for p,d in result.items() if isinstance(d,dict)},indent=2));print('Nonzero stock mono writes',len(watch))
if __name__=='__main__':main()
