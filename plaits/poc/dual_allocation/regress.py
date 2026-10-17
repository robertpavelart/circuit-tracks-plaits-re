"""Run retained reference assertions through an offline replay adapter."""
import ast, contextlib, hashlib, io, json, random, subprocess, sys, types
from pathlib import Path
import study
ROOT,REF,OUT,TOOL=study.ROOT,study.REF,study.OUT,study.TOOL
V,S,GD,D,B=study.setup()
stock=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
original=(ROOT/'builds/phase20d-midi-vpre/fixture/reference-core0.be24').read_bytes()
cores={'original':original,'osc_only':(OUT/'osc_only.be24').read_bytes(),'osc_va':(OUT/'osc_va.be24').read_bytes()}
man=json.loads((REF/'firmware/b1.3/manifest.json').read_text())
def stock_core(core=0):
    offset=int.from_bytes(stock[0x19700+8*core:0x19704+8*core],'little')-0x08010000
    n=int.from_bytes(stock[offset:offset+3],'big')
    return stock[offset+6:offset+6+3*n]
def dsp_program(img,core=0):
    if isinstance(img,str):return cores[img] if not core else core1
    assert img==stock,'Only authentic stock bytes or DSP-only profile tokens accepted'
    return stock_core(core)
# Core1 unchanged: produce it from the current source and stock prefix, without
# reconstructing an ARM firmware image or pretending ARM Session is available.
c1w,c1l=GD.core1_code(0x16c);c1stock=[int.from_bytes(stock_core(1)[i:i+3],'big') for i in range(0,len(stock_core(1)),3)]
c1stock[0x12a]=0x0c0000|c1l['c1loop'];core1=D.to_bytes(c1stock+c1w)
assert len(core1)//3==0x7ff
session=types.ModuleType('dsp_session');session.dsp_program=dsp_program;sys.modules['dsp_session']=session
jobs=OUT/'regression-jobs';jobs.mkdir(exist_ok=True);jobcount=0;log=[]
def run(pwords,call,mem=(),dumps=(),maxins=2000000,regs_code=(),pc=None,stop=None):
    global jobcount
    ident=f'{jobcount:05d}';jobcount+=1
    # Reference's out-of-band emulator caller stub, never part of the P budget.
    stub=0x7000
    ls=['P 0 '+' '.join(f'{x:06x}' for x in pwords),'P %x %s'%(stub,' '.join(f'{x:06x}' for x in list(regs_code)+D.jsr(call)+D.jmp(stub+len(regs_code)+2)))]
    for sp,ad,vals in mem:ls.append(f'{sp.upper()} {ad:x} '+' '.join(f'{x&0xffffff:06x}' for x in vals))
    ls +=[f'PC {(stub if pc is None else pc):x}',f'STOP {(stub+len(regs_code)+2 if pc is None else stop):x}',f'MAX {maxins}']
    if jobcount<=8:ls.append('WRITES '+str(jobs/f'{ident}-writes.csv'))
    ls.append('RUN')
    ls +=[f'DUMP{sp.upper()} {ad:x} {n}' for sp,ad,n in dumps]
    path=jobs/f'{ident}.txt';path.write_text('\n'.join(ls)+'\n')
    r=subprocess.run([str(TOOL),str(path)],capture_output=True,text=True)
    (jobs/f'{ident}-output.txt').write_text(r.stdout+r.stderr)
    if r.returncode:raise RuntimeError((ident,r.returncode,r.stderr,r.stdout[-400:]))
    result={};ran=None
    for line in r.stdout.splitlines():
        if line.startswith('RAN'):ran=line
        elif line[:1] in 'PXY' and ':' in line:
            h,vs=line.split(':',1);sp,addr=h.split();result[(sp.lower(),int(addr,16))]=[int(x,16) for x in vs.split()]
    assert ran is not None
    log.append(dict(job=ident,call=call,stop=stop,ran=ran,dumps=[(sp,ad,n) for sp,ad,n in dumps]))
    return result,ran
dspemu=types.ModuleType('dspemu');dspemu.run=run;sys.modules['dspemu']=dspemu
read_bytes=Path.read_bytes
def alias(p):
    if p==REF/'stock/circuittracks-firmware-4486-STOCK.bin':return stock
    return read_bytes(p)
Path.read_bytes=alias
def words(data):return [int.from_bytes(data[i:i+3],'big') for i in range(0,len(data),3)]
labs={'original':{k:int(v,16) for k,v in man['report']['sc16']['dsp_labels'].items()}}
for name in ('osc_only','osc_va'):labs[name]=json.loads((OUT/f'{name}-labels.json').read_text())
results=[]
def suite(name,fn):
    start=jobcount;s=io.StringIO()
    with contextlib.redirect_stdout(s):
        try:fail=fn();error=None
        except Exception as e:fail=None;error=repr(e)
    (OUT/f'{name}.log').write_text(s.getvalue()+(error or '')+'\n')
    results.append(dict(name=name,failures=fail,error=error,jobs=jobcount-start))
    print(json.dumps(results[-1]),flush=True)
def differential(profile):
    rnd=random.Random(207);bad=[];comparable=0
    # Parameter/flags are valid retained-mode and deliberately stale flag cases.
    for mode,act,df in [('line',1,0),('gran',2,16),('gran-route',2,17),('line-dualflag',1,2),('line-stale-VA',1,4),('gran-stale-VA',2,20)]:
        for variant in range(6):
            blocks=[0]*96;osb=[0]*96;os2=[0]*96
            for t in range(2):
                b=t*48
                for off in range(2,18):blocks[b+off]=rnd.randrange(0,128)
                blocks[b+2]=64;blocks[b+3]=80;blocks[b+4]=7;blocks[b+5]=3;blocks[b+16]=variant%7;blocks[b+13]=variant%7;blocks[b+11]=64
                blocks[b+18]=1;blocks[b+19]=48+12*t;blocks[b+20]=act;blocks[b+21]=100;blocks[b+22]=1;osb[b+21]=df;osb[b+19]=32;osb[b+20]=65
            states={p:(list(blocks),list(osb),list(os2)) for p in ('original',profile)}
            carry={p:[] for p in states}
            for step in range(4):
                ring=[rnd.randrange(-0x200000,0x200000)&0xffffff for _ in range(64)]
                gr=[rnd.randrange(-0x100000,0x100000)&0xffffff for _ in range(128)]
                outs={}
                for p in states:
                    vb,ob,o2=states[p];vb[18]=vb[66]=int(step!=2);vb[22]=vb[70]=int(step==3)
                    code,value=[(19,act|(df<<8)),(18,67),(17,0),(21,1)][step]
                    vb[0]=vb[48]=((1-(step&1))<<23)|(code<<16)|value
                    mem=[('x',0x3a,[32]),('x',V.VB0,vb),('x',V.OSB0,ob),('x',V.OS2B0,o2),('y',0xffd,[0x1000]),('y',0x1000,ring),('x',V.FLAGS,[0]),('x',GD.RDOFS,[64]),('x',GD.OUT,gr)]+carry[p]
                    dumps=[('x',V.VB0,96),('x',V.OSB0,96),('x',V.OS2B0,96),('x',0x3800,0xc0),('x',GD.VS0,96),('y',0x1000,64),('y',0x3400,0x600)]
                    r,_=run(words(cores[p]),labs[p]['vpre'],mem=mem,dumps=dumps)
                    states[p]=(r[('x',V.VB0)],r[('x',V.OSB0)],r[('x',V.OS2B0)]);outs[p]=r
                    carry[p]=[(sp,ad,vs) for (sp,ad),vs in r.items() if (sp,ad) in [('x',0x3800),('x',GD.VS0),('y',0x3400)]]
                a,b=outs['original'],outs[profile]
                # Compare all audio/filter/envelope/FX/granular-counter state.
                keys=[('x',V.VB0),('x',0x3800),('x',GD.VS0),('y',0x1000),('y',0x3400)]
                # Saved register area contains relocated internal R3/R4 values;
                # its 0x38C0+ scratch words are not persistent filter/FX state.
                params_equal=all(a[('x',V.OSB0)][48*t+o]==b[('x',V.OSB0)][48*t+o] for t in range(2) for o in list(range(10))+[19,20,21]) and all(a[('x',V.OS2B0)][48*t+o]==b[('x',V.OS2B0)][48*t+o] for t in range(2) for o in range(9))
                if all(a[k]==b[k] for k in keys) and params_equal:comparable+=1
                else:
                    diffs=[dict(space=k[0],base=k[1],index=i,a=x,b=y) for k in keys for i,(x,y) in enumerate(zip(a[k],b[k])) if x!=y]
                    bad.append(dict(mode=mode,variant=variant,step=step,diffs=diffs[:16]))
    (OUT/f'{profile}-differential.json').write_text(json.dumps(dict(comparable_blocks=comparable,failures=bad),indent=2)+'\n')
    return len(bad)
def core0_suite(profile):
    # Retain all original SC36 assertions for core0 tail/granular integration.
    # Exclude only calls to the unrelated combined EC oscillator/VA suite and
    # independently run the core1 suite. No assertion is rewritten.
    path=REF/'tools/emu_sc36_dsp.py';tree=ast.parse(path.read_text())
    class Select(ast.NodeTransformer):
        def visit_Assign(self,n):
            if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and isinstance(n.value.func.value,ast.Name) and n.value.func.value.id=='C1':n.value=ast.Constant(0)
            return n
        def visit_AugAssign(self,n):
            if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and isinstance(n.value.func.value,ast.Name) and n.value.func.value.id=='EC':return ast.Pass()
            return n
    tree=Select().visit(tree);ast.fix_missing_locations(tree);m=types.ModuleType('retained_sc36');m.__file__=str(path);exec(compile(tree,str(path),'exec'),m.__dict__)
    mm=json.loads(json.dumps(man));mm['report']['sc16']['dsp_labels']={k:f'{v:x}' for k,v in labs[profile].items()}
    return m.main(profile,mm,'original',man)
def tail_differential(profile):
    bad=0
    for magic in (0,GD.GMAGIC):
        mem=[('x',0x3a,[32]),('x',S.MAGIC_AT,[S.MAGIC]),('x',0x3900,list(range(192))),('x',0x3b80,list(range(96))),('x',0x1d8d,list(range(256))),('x',0x3d09,[12345]),('x',0x2e10,[0x50000+3*i for i in range(64)]),('x',GD.GARM,[magic,10,20,30,40]),('x',GD.CNT,[7]),('x',GD.RDOFS,[64]),('x',GD.GOUT+64,[0x70000+5*i for i in range(64)])]
        dumps=[('x',GD.SHA,0x221),('x',GD.MIN,64),('x',GD.GIN,5),('x',GD.CNT,6),('x',0x2e10,64),('x',S.SMB,0x28)]
        r=[run(words(cores[p]),labs[p]['smp_post'],mem=mem,dumps=dumps)[0] for p in ('original',profile)]
        if r[0]!=r[1]:bad+=1
    return bad
def return_differential(profile):
    rnd=random.Random(209);bad=0
    for route in (0,1):
        for filt in range(7):
            vb=[0]*96;ob=[0]*96
            for t in range(2):
                q=48*t;vb[q+2]=64;vb[q+3]=80;vb[q+8]=127;vb[q+11]=64;vb[q+16]=filt;vb[q+18]=1;vb[q+19]=60;vb[q+20]=1;vb[q+21]=100;vb[q+22]=1;ob[q+21]=route
            mem=[('x',0x3a,[32]),('x',V.VB0,vb),('x',V.OSB0,ob),('x',V.FLAGS,[3]),('y',0xffd,[0x1000]),('y',0x1000,[0]*64),('y',0x880,[rnd.randrange(-0x200000,0x200000)&0xffffff for _ in range(64)]),('y',0x9c0,[rnd.randrange(-0x200000,0x200000)&0xffffff for _ in range(64)])]
            rs=[]
            for p in ('original',profile):
                # Original vpre prepares controls; vret processes both stereo returns.
                drv=list(D.jsr(labs[p]['vpre'])+D.jsr(labs[p]['vret'])+D.RTS);pw=words(cores[p]);pw +=[0]*(0x6000+len(drv)-len(pw));pw[0x6000:0x6000+len(drv)]=drv
                r,_=run(pw,0x6000,mem=mem,dumps=[('x',V.VB0,96),('x',0x3800,0xc0),('y',0x880,64),('y',0x9c0,64),('y',0x1000,64)])
                rs.append(r)
            bad+=rs[0]!=rs[1]
    return bad
def drums_suite(profile):
    # Execute the original emu_compact drum-control sweep/assertions against
    # the real B1.3 and reduced DSP programs. Its older table-length comparison
    # and removed oscillator/VA tests are not applicable to this replacement.
    path=REF/'tools/emu_compact.py';tree=ast.parse(path.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    start=next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='common' for t in n.targets))
    end=next(i for i,n in enumerate(fn.body) if isinstance(n,ast.FunctionDef) and n.name=='vpre')
    pre=ast.parse('fails=0\ndef check(c,m):\n global fails\n print(("ok: " if c else "FAIL: ")+m)\n fails += int(not c)\n').body
    # Keep the reference check closure with nonlocal fails, then exact drum body.
    checks=[n for n in fn.body if isinstance(n,ast.FunctionDef) and n.name=='check']
    fn.body=[ast.Assign(targets=[ast.Name(id='fails',ctx=ast.Store())],value=ast.Constant(0))]+checks+ast.parse('P0=prog_reduced\nPR=prog_original\ndl=labels_reduced\ndr=labels_original').body+fn.body[start:end]+[ast.Return(ast.Name(id='fails',ctx=ast.Load()))]
    ast.fix_missing_locations(tree);m=types.ModuleType('retained_drums');m.__file__=str(path);m.prog_reduced=words(cores[profile]);m.prog_original=words(original);m.labels_reduced=labs[profile];m.labels_original=labs['original'];exec(compile(tree,str(path),'exec'),m.__dict__)
    return m.main(None,None,None,None)
def sender_contract():
    rows=[]
    for active in (0,1):
        for osc in (0,1):
            for va in (0,1):
                for velocity in (0,1):
                    for route in (0,1):
                        for dual in (0,1):
                            w=active+active*osc+(route<<8)+(dual<<9)+(va<<10)+(velocity<<11)
                            if w&3==1 and w&0x400:w=0 # exact FXSEQ sd_nf branch
                            if w&0x800 and not w&0x400:w^=0x1800 # exact GRAN sd_ng
                            act=w&3;df=(w>>8)&31
                            assert not(act==1 and df&4)
                            assert not(act==2 and df&16 and df&4)
                            rows.append(dict(active=active,osc=osc,VA=va,velocity=velocity,route=route,dual=dual,ACT=act,DFLAGS=df))
    (OUT/'ARM-sender-contract.json').write_text(json.dumps(dict(scope='Source-derived c_vsend truth table, not ARM execution',cases=rows,line_VA_combination_reachable=False,gran_VA_combination_reachable=False),indent=2)+'\n')
def main():
    sender_contract()
    for p in ('osc_only','osc_va'):
        suite(p+'-retained-differential',lambda p=p:differential(p))
        suite(p+'-SC36-core0',lambda p=p:core0_suite(p))
        suite(p+'-tail-differential',lambda p=p:tail_differential(p))
        suite(p+'-FX-return-differential',lambda p=p:return_differential(p))
        suite(p+'-reference-drums',lambda p=p:drums_suite(p))
    # Unmodified reference component suites on their original test fixtures.
    import emu_masterfx_dsp
    suite('reference-masterfx',lambda:emu_masterfx_dsp.main(stock))
    S.V34=S.HIGH=S.HOLD=S.CLIP=S.CLIP2=S.PRE=False;S.TAIL=S.TAIL_TABLE=None
    import emu_sc33_dsp,emu_sc34_dsp
    suite('reference-capture',emu_sc33_dsp.main)
    suite('reference-capture-replacement',emu_sc34_dsp.main)
    GD.OVERLOAD=False
    import emu_gran_core1
    suite('reference-granular-glitch-core1',emu_gran_core1.main)
    (OUT/'regressions.json').write_text(json.dumps(dict(suites=results,jobs=log,limitations=['No ARM/Unicorn Session or authentic live RAM snapshots','Reference test drivers at P7000/core1 P3800 are emulator-only and excluded from allocation budget','Retained stock synth code identity is checked separately; no full active stock-synth workload replay']),indent=2)+'\n')
    (OUT/'assembler-supplement-tests.json').write_text(json.dumps(study.missing,indent=2)+'\n')
if __name__=='__main__':main()
