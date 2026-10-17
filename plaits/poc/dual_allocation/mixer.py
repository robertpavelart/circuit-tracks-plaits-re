"""Actual stock four-strip mixer replay; supplied stems are not synth engines."""
import json, random
import regress as R
R.jobs=R.OUT/'mixer-jobs';R.jobs.mkdir(exist_ok=True)
def main():
    results=[];rnd=random.Random(210)
    lines=['move #>$000300,sr','move #>$000000,omr']
    lines += [f'move #>${v:06x},{reg}' for reg,v in [('r0',0x200),('r1',0x240),('r2',0x280),('r3',0x2c0),('r5',0x1000),('r6',0x1100),('r7',0x1140)]]
    lines += [f'move #>$ffffff,m{i}' for i in range(8)]
    drv=sum(R.study.assemble(lines),[])+R.D.jmp(0x23e)
    for case in range(16):
        mem=[('x',0x3a32,[32]),('x',0x3a,[32]),('x',0x200,[0x100000]*256)]
        for ad,n in [(0x1000,64),(0x1100,64),(0x1140,64)]:
            mem.append(('y',ad,[rnd.randrange(-0x100000,0x100000)&0xffffff for _ in range(n)]))
        outs=[]
        for p in ('original','osc_only','osc_va'):
            pw=R.words(R.cores[p]);pw += [0]*(0x6000+len(drv)-len(pw));pw[0x6000:0x6000+len(drv)]=drv
            out,ran=R.run(pw,0x23e,mem=mem,dumps=[('y',0x800,64)],pc=0x6000,stop=0x24f)
            outs.append(out)
        assert outs[0]==outs[1]==outs[2],case
        results.append(dict(case=case,identical=True))
    (R.OUT/'mixer-regressions.json').write_text(json.dumps(dict(cases=results,jobs=R.log,scope='Actual stock P23E..24E, nonzero supplied Synth1/Synth2 and MIDI stems. No stock synth generator execution.'),indent=2)+'\n')
    print('PASS: 16 four-strip mixer fixtures, 48 native jobs')
if __name__=='__main__':main()
