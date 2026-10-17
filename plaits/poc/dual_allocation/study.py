"""DSP-only dual-removal allocation study. Reference checkout is read-only."""
import ast, hashlib, inspect, json, os, subprocess, sys, types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
OUT=ROOT/'builds/phase20g-dual-allocation'
TOOL=OUT/'host/replay.exe'
sys.dont_write_bytecode=True
sys.path[:0]=[str(REF/'tools'),str(ROOT/'builds/python-deps')]
def protect(event,args):
    if event=='open' and isinstance(args[0],(str,bytes)):
        p=os.path.abspath(os.fsdecode(args[0]))
        if p.lower().startswith(str(REF).lower()+os.sep):
            mode=args[1] or '';flags=args[2] or 0
            if any(x in str(mode) for x in ('w','a','+','x')) or flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_APPEND):raise RuntimeError('Reference write rejected: '+p)
sys.addaudithook(protect)
cache=json.loads((REF/'tools/dsp_asm_cache.json').read_text())
missing={}
def assemble(lines):
    todo=list(dict.fromkeys(l for l in lines if l not in cache))
    if todo:
        r=subprocess.run([str(TOOL),'asm'],input='\n'.join(todo)+'\n',text=True,capture_output=True,check=True)
        for l,row in zip(todo,r.stdout.splitlines()):
            assert not row.startswith('ERR'),(l,row)
            cache[l]=missing[l]=[int(x,16) for x in row.split()[1:]]
        assert all(l in cache for l in todo)
    return [cache[l] for l in lines]
shim=types.ModuleType('dspasm_cache');shim.assemble=assemble;shim.dis_listing=lambda *a:[];sys.modules['dspasm_cache']=shim
def setup():
    # Only module import/configuration: never invoke any application builder.
    import build_sc41_3, build_sc16, vcf21_dsp as V, sampler_dsp as S, granular_dsp as GD, dsp56 as D
    return V,S,GD,D,build_sc16
def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    V,S,GD,D,B=setup()
    core=(ROOT/'builds/phase20d-midi-vpre/fixture/reference-core0.be24').read_bytes()
    labels=dict((k,int(v,16)) for k,v in (l.split() for l in (ROOT/'builds/phase20d-midi-vpre/fixture/labels.txt').read_text().splitlines()))
    oldw,oldl=B.dsp_code(0x2a5e)
    oldw[oldl['fx_hook']-0x2a5e:oldl['fx_hook']-0x2a5e+2]=D.jmp(oldl['smp_post'])
    assert D.to_bytes(oldw)==core[3*0x2a5e:], 'Full appended source mismatch'
    tabs={k:labels[k] for k in ('TATK','TDEC','TLFO','TF')};tabs['TDEC']-=64
    original,vl=V.code(labels['vpre'],tabs,0x87,labels['fx_cap'])
    assert D.to_bytes(original)==core[3*labels['vpre']:3*labels['smp_post']]
    class Strip(ast.NodeTransformer):
        def visit_FunctionDef(self,n):
            if n.name=='control':n.body=[ast.Pass() if isinstance(q,ast.If) and isinstance(q.test,ast.Name) and q.test.id=='OSC3' else q for q in n.body]
            if n.name=='channel':
                for q in n.body:
                    if isinstance(q,ast.If) and isinstance(q.test,ast.Name) and q.test.id=='OSC3':
                        i=next(i for i,x in enumerate(q.body) if isinstance(x,ast.If) and isinstance(x.test,ast.Name) and x.test.id=='DUAL')
                        q.body=q.body[:i]+q.body[-1:]
            if n.name=='code':n.body=[ast.Pass() if isinstance(q,ast.If) and isinstance(q.test,ast.Name) and q.test.id=='OSC' and any(isinstance(x,ast.Constant) and x.value=='TINC' for x in ast.walk(q)) else q for q in n.body]
            return self.generic_visit(n)
    tree=Strip().visit(ast.parse((REF/'tools/vcf21_dsp.py').read_text()));ast.fix_missing_locations(tree)
    m=types.ModuleType('dual_reduced');m.__file__=str(REF/'tools/vcf21_dsp.py');exec(compile(tree,m.__file__,'exec'),m.__dict__)
    for k in ('TILT','FB','SLOPES','FXMORE','BISEND','SINEFIX','STGLIDE','GATEFIX','TYPEZONE','CODE7','DUAL','ROUTE','VADRUM','GRAN','GATEREL','GATE_RKC','VFF','OSC','OSC2','OSC3','PLIMIT'):setattr(m,k,getattr(V,k))
    profiles={}
    for name,va in [('osc_only',True),('osc_va',False)]:
        m.VADRUM=va
        w,l=m.code(labels['vpre'],tabs,0x87,labels['fx_cap'])
        # Reassemble the entire sampler/capture/glitch tail at its compacted base.
        tw,tl=S.code(labels['vpre']+len(w),v34=S.V34,pre_ret=labels['fx_hook']+2 if S.PRE else None)
        # Validate sampler generation at original placement before relying on it.
        ow,ol=S.code(labels['smp_post'],v34=S.V34,pre_ret=labels['fx_hook']+2 if S.PRE else None)
        assert D.to_bytes(ow)==core[3*labels['smp_post']:]
        prefix=bytearray(core[:3*labels['vpre']]);prefix[3*labels['fx_hook']:3*(labels['fx_hook']+2)]=D.to_bytes(D.jmp(tl['smp_post']))
        prefix[3*0xd22:3*0xd23]=l['vret'].to_bytes(3,'big')
        new=bytes(prefix)+D.to_bytes(w+tw);nl={**{k:v for k,v in labels.items() if v<labels['vpre']},**l,**tl}
        (OUT/f'{name}.be24').write_bytes(new)
        (OUT/f'{name}-labels.json').write_text(json.dumps(nl,indent=2)+'\n')
        reclaimed=len(core)//3-len(new)//3
        profiles[name]=dict(words=len(new)//3,reclaimed=reclaimed,tail=19,available=19+reclaimed,free_range=[len(new)//3,0x4000],largest_contiguous=0x4000-len(new)//3,sha256=hashlib.sha256(new).hexdigest(),VA_control_retained=va)
    # Graph for every named basic block/table in the reference core0 label set.
    graph=[]
    removals=[(0x36ad,0x3876,'oscillator control'),(0x3999,0x3b82,'single/dual/VA-noise render'),(0x3d9e,0x3e1f,'TINC')]
    ws=[int.from_bytes(core[i:i+3],'big') for i in range(0,len(core),3)]
    sorted_labels=sorted(labels.items(),key=lambda q:(q[1],q[0]));byaddr={a:k for k,a in sorted_labels}
    for i,(name,start) in enumerate(sorted_labels):
        end=next((a for _,a in sorted_labels[i+1:] if a>start),len(ws));reason=next((r for a,b,r in removals if a<=start<b),None)
        cls='REMOVE' if reason else 'SHARED-INFRASTRUCTURE' if name.startswith(('v','pmfb','pf_','sc_init','mixhook','mh','idle','id_')) else 'KEEP'
        edges=[]
        for pc in range(start,end-1):
            op=ws[pc]
            if op==0x0bf080 or op==0x0af080 or 0x0af0a0<=op<=0x0af0af:
                target=ws[pc+1];edges.append(dict(type='static-transfer',target=byaddr.get(target,f'P:{target:04X}'),pc=pc))
        if name.startswith('vc_') or name=='vpre':edges +=[dict(type='indexed-table',target=k) for k in ('TATK','TDEC','TLFO','TF')]
        graph.append(dict(symbol=name,start=start,end=end,classification=cls,reason=reason or 'retained component or shared audio/control path',edges=edges))
    result=dict(original_words=len(core)//3,profiles=profiles,full_appended_source_matches=True,sampler_source_matches=True,
        graph_scope='Every manifest core0 label/table plus source function-level closure. Static-transfer scan is conservative; indexed/indirect stock targets are not falsely classified dead.',
        graph=graph,components=[
          dict(symbol='control/osc_ctrl',classification='REMOVE',calls=['Note/TINC','modterm','shape/morph weights','OSC2 direction/sync']),
          dict(symbol='channel/waves/fold/dual/noise',classification='REMOVE',calls=['OSC1/OSC2 phase','fold','LCG noise']),
          dict(symbol='control/shared',classification='SHARED-INFRASTRUCTURE',calls=['mailbox','ADSR','LFO','TF/TATK/TDEC/TLFO','KEYF/NOTE2','VCA target','FX parameters']),
          dict(symbol='channel/shared',classification='KEEP',calls=['granular OUT','VCA','track FX','filter','ROUTE','RMODE return']),
          dict(symbol='sampler/core0_tail/core0_table',classification='KEEP',calls=['capture/play/replace','SHA/SHB/SHT snapshots','glitch GOUT','CNT/RDOFS','sm_se']),
          dict(symbol='drums2_dsp/tables',classification='KEEP',calls=['drums','shared control tables']),
          dict(symbol='vcf21 ARM framework',classification='SHARED-INFRASTRUCTURE',calls=['MIDI','c_vsend/c_vtick','automation','FX sequencer','step drummer','mpatch','persist19'])],
        original_islands=[dict(start=a,end=b,words=b-a,name=r) for a,b,r in removals],
        generated_assembler_lines=len(missing),reference_written=False,firmware_image_generated=False)
    (OUT/'allocation.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'assembler-supplement.json').write_text(json.dumps(missing,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('graph','components')},indent=2))
if __name__=='__main__':prepare()
