"""Reassemble only reference DSP source in RAM. Never run image builders."""
import ast, inspect, json, sys, types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
OUT=ROOT/'builds/phase20e-full-plaits-audit'
sys.dont_write_bytecode=True
sys.path.insert(0,str(REF/'tools'))
# Replace assembler entry point with strict read-only cache. Missing ops fail.
cache=json.loads((REF/'tools/dsp_asm_cache.json').read_text())
shim=types.ModuleType('dspasm_cache')
shim.assemble=lambda lines:[cache[l] for l in lines]
sys.modules['dspasm_cache']=shim
import vcf21_dsp as V
import dsp56 as D
labels=dict((k,int(v,16)) for k,v in (l.split() for l in (ROOT/'builds/phase20d-midi-vpre/fixture/labels.txt').read_text().splitlines()))
def configure(v):
    for k in ('FB','SLOPES','FXMORE','VFF','BISEND','SINEFIX','STGLIDE','GATEFIX','TYPEZONE','CODE7','DUAL','ROUTE','VADRUM','GRAN','OSC','OSC2','OSC3'):
        setattr(v,k,True)
    v.TILT=False
    v.PLIMIT=0x4000
    v.use_gaterel()
configure(V)
tabs={k:labels[k] for k in ('TATK','TDEC','TLFO','TF')}
tabs['TDEC']-=64
words, ls=V.code(labels['vpre'],tabs,0x87,labels['fx_cap'])
core=(ROOT/'builds/phase20d-midi-vpre/fixture/reference-core0.be24').read_bytes()
assert D.to_bytes(words)==core[3*labels['vpre']:3*labels['smp_post']], 'B1.3 reconstruction mismatch'
# Surgery in a separate module AST: strip oscillator-specific control branch,
# waveform/dual/VA-noise body; preserve granular dispatch and entire shared chain.
tree=ast.parse((REF/'tools/vcf21_dsp.py').read_text())
removed=[]
class Remove(ast.NodeTransformer):
    def visit_FunctionDef(self,node):
        if node.name=='control':
            node.body=[ast.Pass() if isinstance(n,ast.If) and isinstance(n.test,ast.Name) and n.test.id=='OSC3' else n for n in node.body]
            removed.append('control: OSC3/OSC2/OSC pitch/shape/morph/dual preparation, including TINC readers')
        if node.name=='channel':
            for n in node.body:
                if isinstance(n,ast.If) and isinstance(n.test,ast.Name) and n.test.id=='OSC3':
                    cut=next(i for i,x in enumerate(n.body) if isinstance(x,ast.If) and isinstance(x.test,ast.Name) and x.test.id=='DUAL')
                    n.body=n.body[:cut]+n.body[-1:]
                    removed.append('channel: oscillator after granular dispatch through vc2_nosc, retains granular path')
        if node.name=='code':
            node.body=[ast.Pass() if isinstance(n,ast.If) and isinstance(n.test,ast.Name) and n.test.id=='OSC' and any(isinstance(x,ast.Constant) and x.value=='TINC' for x in ast.walk(n)) else n for n in node.body]
            removed.append('code: TINC table only')
        return self.generic_visit(node)
tree=Remove().visit(tree)
ast.fix_missing_locations(tree)
mod=types.ModuleType('audit_vcf'); mod.__file__=str(REF/'tools/vcf21_dsp.py')
exec(compile(tree,mod.__file__,'exec'),mod.__dict__)
configure(mod)
w2,l2=mod.code(labels['vpre'],tabs,0x87,labels['fx_cap'])
mod.VADRUM=False
w3,l3=mod.code(labels['vpre'],tabs,0x87,labels['fx_cap'])
mod.VADRUM=True
# Exact source interval for OSC3 control: index first item generated at line 362.
items=[]
original_emit=D.Asm.emit
def trace(self,fn,*args):
    caller=inspect.currentframe().f_back
    while caller and caller.f_code.co_filename!=V.__file__: caller=caller.f_back
    items.append((len(self.items),caller.f_lineno if caller else None))
    return original_emit(self,fn,*args)
D.Asm.emit=trace
captured=[]
original_init=D.Asm.__init__
def init(self,base): original_init(self,base); captured.append(self)
D.Asm.__init__=init
V.code(labels['vpre'],tabs,0x87,labels['fx_cap'])
a=captured[0]; pc=a.base; listing=[]; byitem=dict(items)
for i,it in enumerate(a.items):
    if it[0]=='L': continue
    fn,args=it[1], [ls[x] if isinstance(x,str) and x in ls else x for x in it[2]]
    ws=fn(*args) if callable(fn) else fn
    listing.append(dict(pc=pc,words=len(ws),source_line=byitem.get(i)))
    pc+=len(ws)
# Compare shortening to original known islands; table is 129 words.
osc_render=labels['vc2_nosc']-labels['vc2_ngr']
ctrl=len(words)-len(w2)-osc_render-129
result=dict(original_words=len(words),modified_reference_only_words=len(w2),reclaimed_words=len(words)-len(w2),
    original_matches_manifest_bytes=True,
    removed_sections=removed,oscillator_control_words=ctrl,oscillator_render_words=osc_render,TINC_words=129,
    control_start=f"{labels['vc_oi']-ctrl:04X}",control_end=f"{labels['vc_oi']:04X}",
    render_start=f"{labels['vc2_ngr']:04X}",render_end=f"{labels['vc2_nosc']:04X}",
    table_start=f"{labels['TINC']:04X}",table_end=f"{labels['smp_post']:04X}",
    old_core0_words=0x3fed,shortened_core0_words=0x3fed-(len(words)-len(w2)),
    theoretical_free_P=19+len(words)-len(w2),
    optional_VA_control_removal_words=len(w2)-len(w3),
    total_with_VA_control_removal=len(words)-len(w3),
    theoretical_free_with_VA_control_removal=19+len(words)-len(w3),
    limitations='Assembler-only surgery, not linked B1.3 or functional regression. Retains VA-control, VCF/VCA, FX, routing, mailbox, granular record layout. Needs Plaits code/adapter, relocation of subsequent sampler labels and ARM pointers. No full firmware saved.',
    instruction_source_map=listing,new_labels={k:f'{v:04X}' for k,v in l2.items()})
(OUT/'reclaim.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('instruction_source_map','new_labels')},indent=2))
