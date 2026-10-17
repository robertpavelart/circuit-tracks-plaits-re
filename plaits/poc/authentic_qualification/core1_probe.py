"""Actual B1.3 core1 boot/task probe and external-address capability check."""
import json,subprocess
from environment import *
import dsp_session as DS
def main():
    d=OUT/'core1';d.mkdir(exist_ok=True);program=DS.dsp_program(PUBLISHED,1)
    assert program==(ROOT/'builds/phase20g-dual-allocation/retained-core1.be24').read_bytes()
    (d/'program.be24').write_bytes(program)
    c1=int(MAN['report']['granular']['labels']['c1loop'],16)
    cmds=['LOADP program.be24 0','MAX 2000000','HIST hist.txt','PC 107','STOP 10e','RUN','DUMPX 30000 8','DUMPX 37000 32',f'PC {c1:x}','X 37000 000001','STOP 10e','RUN','DUMPX 37000 32','DUMPY 340000 1']
    (d/'job.txt').write_text('\n'.join(cmds)+'\n')
    r=subprocess.run([str(REF/'ext/bin/dsptool.exe'),'run','job.txt'],cwd=d,capture_output=True,text=True);(d/'output.txt').write_text(r.stdout+r.stderr)
    (d/'address-probe.txt').write_text('Y 340000 123456\nDUMPY 340000 1\nY e80000 234567\nDUMPY e80000 1\n')
    a=subprocess.run([str(REF/'ext/bin/dsptool.exe'),'run','address-probe.txt'],cwd=d,capture_output=True,text=True);(d/'address-output.txt').write_text(a.stdout+a.stderr)
    result=dict(core1_words=len(program)//3,core1_sha256=sha(program),published_source_match=True,exit=r.returncode,runs=[l for l in r.stdout.splitlines() if l.startswith('RAN')],address_probe=a.stdout,
        scope='Exact core1 program; fresh emulator reset and zero data memory, not authentic captured DSP state. Counter stimulus modeled. No shared dual-core bus, gather traffic, pack/capture SDRAM data or concurrent core0.',
        confidence='UNKNOWN for authentic/concurrent core1 qualification')
    (OUT/'core1-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
