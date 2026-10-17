"""Mandatory active stock generator probe with authentic reference initialization."""
import json,subprocess
from environment import *
import dsp_session as DS
def run(s,profile='original',blocks=4):
    folder=OUT/('probe-'+profile);folder.mkdir(exist_ok=True)
    program=DS.dsp_program(PUBLISHED) if profile=='original' else (ROOT/f'builds/phase20g-dual-allocation/{profile}.be24').read_bytes()
    prog=bytearray(program)
    for at in DS.SPIN_NOPS:prog[3*at:3*at+3]=bytes(3)
    (folder/'program.be24').write_bytes(prog)
    ls=['LOADP program.be24 0','MAX 20000000','HIST hist.txt','PC 107','STOP 25f3','RUN']
    ls+=DS.Session._mem(s.init_writes);ls+=['PC 25f3','STOP 113','RUN']
    for _,ws in s.events:ls+=DS.Session._mem(ws)
    ls+=['P 7000 0bf080 0001ed 0c7002','WATCHFILE watch.txt','WATCH X 2c46 33','WATCH X 2e10 64','WATCH Y 800 64']
    for _ in range(blocks):ls+=['PC 7000','STOP 7002','RUN','DUMPX 2c46 33','DUMPY 800 64','DUMPX eb 112']
    (folder/'job.txt').write_text('\n'.join(ls)+'\n')
    r=subprocess.run([str(REF/'ext/bin/dsptool.exe'),'run','job.txt'],cwd=folder,capture_output=True,text=True);(folder/'output.txt').write_text(r.stdout+r.stderr)
    print(profile,r.returncode,r.stdout[:200],r.stderr[:200],flush=True)
    return r
if __name__=='__main__':
    s=authentic_session();print('init',len(s.init_writes),'params',len(s.events[0][1]),flush=True)
    s.midi(bytes([0x90,60,100]));s.midi(bytes([0x91,67,100]))
    (OUT/'probe-ARM-writes.json').write_text(json.dumps(dict(init=s.init_writes,events=s.events),indent=2)+'\n')
    for p in ('original','osc_only','osc_va'):run(s,p)
