"""Preserve prior retained assertions; change only transport to installed dsptool."""
import json,subprocess,sys
from environment import ROOT,REF,OUT
sys.path.insert(0,str(ROOT/'plaits/poc/dual_allocation'))
import regress as R
R.OUT=OUT;R.jobs=OUT/'native-regression-jobs';R.jobs.mkdir(exist_ok=True)
def run(pwords,call,mem=(),dumps=(),maxins=2000000,regs_code=(),pc=None,stop=None):
    ident=f'{R.jobcount:05d}';R.jobcount+=1;stub=0x7000
    ls=['P 0 '+' '.join(f'{x:06x}' for x in pwords),'P %x %s'%(stub,' '.join(f'{x:06x}' for x in list(regs_code)+R.D.jsr(call)+R.D.jmp(stub+len(regs_code)+2)))]
    for sp,ad,vals in mem:ls.append(f'{sp.upper()} {ad:x} '+' '.join(f'{x&0xffffff:06x}' for x in vals))
    ls += [f'PC {(stub if pc is None else pc):x}',f'STOP {(stub+len(regs_code)+2 if pc is None else stop):x}',f'MAX {maxins}','RUN']+[f'DUMP{sp.upper()} {ad:x} {n}' for sp,ad,n in dumps]
    path=R.jobs/f'{ident}.txt';path.write_text('\n'.join(ls)+'\n')
    r=subprocess.run([str(REF/'ext/bin/dsptool.exe'),'run',str(path)],capture_output=True,text=True);(R.jobs/f'{ident}-output.txt').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(ident,r.stderr[-500:]);result={};ran=None
    for line in r.stdout.splitlines():
        if line.startswith('RAN'):ran=line
        elif line[:1] in 'PXY' and ':' in line:
            h,vs=line.split(':',1);sp,addr=h.split();result[(sp.lower(),int(addr,16))]=[int(x,16) for x in vs.split()]
    target=stub+len(regs_code)+2 if pc is None else stop
    assert ran is not None and f'pc={target:06x}' in ran,(ident,ran,target)
    R.log.append(dict(job=ident,call=call,stop=target,ran=ran));return result,ran
R.run=run;R.dspemu.run=run
if __name__=='__main__':
    R.main()
    (OUT/'native-regression-tool.json').write_text(json.dumps(dict(tool=str(REF/'ext/bin/dsptool.exe'),scope='Unchanged phase20g/20h retained assertions and preserved 48 negative cases, executed on installed pinned DSP emulator. Component fixtures remain modeled, not authentic coupled workloads.'),indent=2)+'\n')
