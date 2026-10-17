"""ARM-message driven retained component timeline, not a full-device checkpoint."""
import json,random,subprocess
import regress as R
OUT=R.ROOT/'builds/phase20h-budget-qualification';OUT.mkdir(exist_ok=True)
REGS=['x0','x1','y0','y1','r0','r1','r6','r7','n0','m0','r2','r3','r4','m2','m4']
def asm(ls):return sum(R.study.assemble(ls),[])
def run_profile(profile):
    timeline=json.loads((OUT/'arm-retained-timeline.json').read_text());frames=timeline['initial_frames']+timeline['frames']
    p=R.words(R.cores[profile]);lab=R.labs[profile];base=0x6000
    ls=['move #>$000300,sr']+[f'move #>$ffffff,m{i}' for i in range(8)]+[f'move #>${0x123000+i:06x},{r}' for i,r in enumerate(REGS) if not r.startswith('m')]
    seed=asm(ls);before=asm([f'move {r},x:>${0x6000+i:06x}' for i,r in enumerate(REGS)])
    after=asm([f'move {r},x:>${0x6020+i:06x}' for i,r in enumerate(REGS)])
    code=seed+before+R.D.jsr(lab['vpre'])+after+R.D.jsr(lab['vret'])
    # Stock mixer consumes supplied stock synth stems and the processed ring.
    code+=asm([f'move #>${ad:06x},{reg}' for reg,ad in [('r0',0x200),('r1',0x240),('r2',0x280),('r3',0x2c0),('r5',0x1000),('r6',0x1100),('r7',0x1140)]])
    # Execute original P23E..24E then continue at 24F via an emulator-only
    # branch. No synthetic stock synthesis overlay or allocation contribution.
    mixat=base+len(code)+2;code+=R.D.jmp(0x23e)
    # Explicit fixture wiring replaces unqualified stock downstream stages.
    for i in range(64):code+=asm([f'move y:>${0x800+i:06x},a',f'move a,x:>${0x2e10+i:06x}'])
    code+=R.D.jsr(lab['fx_hook']);stop=base+len(code)
    p[0x24f:0x251]=R.D.jmp(mixat)
    p += [0]*(stop+1-len(p));p[base:stop]=code
    def mem(sp,ad,vals):return f'{sp} {ad:x} '+' '.join(f'{v&0xffffff:06x}' for v in vals)
    lines=[mem('P',0,p),'MAX 300000','WRITES '+str(OUT/f'{profile}-timeline-writes.csv')]
    # Declared synthetic initial state; no authentic boot checkpoint implied.
    lines += [mem('X',0x3a,[32]),mem('Y',0xffd,[0x1000]),mem('X',0x200,[0x100000]*256),mem('X',R.S.MAGIC_AT,[R.S.MAGIC]),mem('X',R.S.SMB,[0]*0x28)]
    import masterfx_dsp as G
    lines += [mem('X',G.G_TGT,[0x500000,0x7fffff,0x080000]),mem('X',G.AF_F,[0x180000,0x500000]),mem('X',G.DG_N,[3,0xffc000,1,0,0]),mem('X',G.PH_A,[0xd00000,0x200000,0x400000]),mem('X',G.VN_T,[0x680000,0x300000,0x040000,0x500000,0x008000])]
    rng=random.Random(211)
    dumps=[('X',R.V.VB0,96),('X',R.V.OSB0,192),('X',0x3800,0xa0),('Y',0x1000,64),('Y',0x800,64),('Y',0x880,64),('Y',0x9c0,64),('Y',0x3400,0x600),('X',G.BUF,64),('X',0x3a40,0x40),('X',R.S.SMB,0x28),('X',R.GD.GB,0x621),('X',0x6000,15),('X',0x6020,15)]
    free=R.study.OUT/'allocation.json';allocation=json.loads(free.read_text());freeat=allocation['profiles'].get(profile,{}).get('words',0x3fed)
    # Canary every word of the candidate P tail, no runtime writes allowed.
    lines += [mem('P',freeat,[0x5a1234]*(0x4000-freeat)),f'FREETAIL {freeat:x}']
    for index,frame in enumerate(frames):
        for w in frame['mail']:lines.append(mem('X',w['address'],[w['word']]))
        for sp,ad,n in [('Y',0x1000,64),('Y',0x1100,64),('Y',0x1140,64),('Y',0x880,64),('Y',0x9c0,64)]:lines.append(mem(sp,ad,[rng.randrange(-0x100000,0x100000) for _ in range(n)]))
        lines += [mem('Y',G.NOISE,[rng.randrange(-0x700000,0x700000) for _ in range(128)]),mem('X',G.FX_ON,[0x1f if index%3 else 0]),mem('X',R.GD.OUT,[rng.randrange(-0x100000,0x100000) for _ in range(128)]),mem('X',R.GD.GOUT,[rng.randrange(-0x100000,0x100000) for _ in range(128)]),mem('X',R.GD.GARM,[R.GD.GMAGIC if index%4==0 else 0,127,127,0,0])]
        # Exercise recording start/stop in existing sampler code.
        lines.append(mem('X',R.S.STATE,[1 if index%32<8 else 0]))
        lines += [f'PC {base:x}',f'STOP {stop:x}','RUN']+[f'DUMP{sp} {ad:x} {n}' for sp,ad,n in dumps]+[f'DUMPP {freeat:x} {0x4000-freeat}']
    path=OUT/f'{profile}-timeline-job.txt';path.write_text('\n'.join(lines)+'\n')
    res=subprocess.run([str(OUT/'host/replay.exe'),str(path)],capture_output=True,text=True)
    (OUT/f'{profile}-timeline-output.txt').write_text(res.stdout+res.stderr)
    if res.returncode:raise RuntimeError((profile,res.returncode,res.stderr,res.stdout[-500:]))
    blocks=[];current=None
    for l in res.stdout.splitlines():
        if l.startswith('RAN'):current=dict(ran=l,dumps={});blocks.append(current)
        elif l[:1] in 'XYP' and ':' in l:
            h,v=l.split(':');current['dumps'][h]=[int(s,16) for s in v.split()]
    assert len(blocks)==len(frames),(len(blocks),len(frames))
    for b in blocks:
        assert b['dumps']['X 006000']==b['dumps']['X 006020'],(profile,'caller register preservation')
        assert b['dumps'][f'P {freeat:06x}']==[0x5a1234]*(0x4000-freeat),(profile,'P canary')
    return blocks
def main():
    results={p:run_profile(p) for p in ('original','osc_only','osc_va')}
    summary={}
    for p in ('osc_only','osc_va'):
        dif=[];raw=0
        for i,(a,b) in enumerate(zip(results['original'],results[p])):
            da,db=a['dumps'],b['dumps'];keys=[k for k in da if k in db and not k.startswith('P ') and k not in ('X 003900','X 037000','X 003d00')]
            # Sampler saved R registers contain relocated table/code addresses;
            # compare semantic sampler fields separately in component suite.
            params=list(range(10))+[19,20,21]
            controls=all(da['X 003900'][48*t+o]==db['X 003900'][48*t+o] for t in range(2) for o in params) and all(da['X 003900'][96+48*t+o]==db['X 003900'][96+48*t+o] for t in range(2) for o in range(9))
            raw+=da['X 003900']!=db['X 003900']
            saved={R.S.SAVM4-R.S.SMB,R.S.SAVR6-R.S.SMB,R.S.SAVM5-R.S.SMB,R.S.SAVR2-R.S.SMB,R.S.SAVM2-R.S.SMB}
            sampler_equal=all(x==y for j,(x,y) in enumerate(zip(da['X 003d00'],db['X 003d00'])) if j not in saved)
            # Compare the entire shared region except copied old oscillator
            # derived cells; those are deliberately removed from both engines.
            dead={R.GD.SHA-R.GD.GB+48*t+o for t in range(2) for o in list(range(10,19))+list(range(22,48))} | {R.GD.SHA-R.GD.GB+96+48*t+o for t in range(2) for o in range(9,48)}
            shared_equal=all(x==y for j,(x,y) in enumerate(zip(da['X 037000'],db['X 037000'])) if j not in dead)
            failures=[k for k in keys if da[k]!=db[k]]
            if failures or not controls or not sampler_equal or not shared_equal:dif.append(dict(block=i,dump_mismatches=failures,controls_equal=controls,sampler_equal=sampler_equal,shared_equal=shared_equal))
        summary[p]=dict(blocks=len(results[p]),mismatches=dif,raw_old_derived_state_differences=raw,caller_15_registers_preserved=True,P_tail_canaries_stable=True)
    (OUT/'retained-timeline-results.json').write_text(json.dumps(dict(profiles=summary,scope='Bounded vpre/vret + actual stock mixer + actual B1.3 sampler/MasterFX/core0 granular/glitch chain; supplied synth/granular/glitch stems; synthetic initialization and downstream fixture wiring. Not complete stock synth/drum/core1 workload.'),indent=2)+'\n')
    print(json.dumps({p:{k:v if k!='mismatches' else len(v) for k,v in row.items()} for p,row in summary.items()}))
if __name__=='__main__':main()
