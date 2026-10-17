"""Offline master-path investigation. Never builds a firmware image."""
from environment import ROOT, REF, authentic_session, sha
from pathlib import Path
import json, shutil, subprocess, math
OUT=ROOT/'builds/phase20l-master-path'
def capture():
    s=authentic_session();s.events=[]
    s.capture('actual global parameter restoration',0x08028ef2)
    r=dict(events=s.events,scope='Actual ARM code, unedited authentic RAM snapshot; no DSP gains supplied by host')
    (OUT/'global-ARM-events.json').write_text(json.dumps(r,indent=2))
    print([(n,len(w)) for n,w in s.events])
    print([w for _,ws in s.events for w in ws if 0x52<=w[2]<=0x59])
    return s.events
def run(name,events):
    src=OUT/'before';d=OUT/name;d.mkdir(exist_ok=True)
    for p in src.glob('*.be24'):shutil.copyfile(p,d/p.name)
    job=(src/'job.txt').read_text()
    ins=[]
    for _,ws in events:
        for c,sp,a,v in ws:ins += [f'CORE {c}',f'{sp.upper()} {a:x} {v:06x}']
    job=job.replace('TRACE traffic.txt','\n'.join(ins)+'\nCORE 0\nTRACE traffic.txt')
    (d/'job.txt').write_text(job)
    r=subprocess.run([str(ROOT/'builds/phase20j-coupled-replay/coupled.exe'),'job.txt'],cwd=d,capture_output=True,text=True)
    (d/'output.txt').write_text(r.stdout+r.stderr)
    print(name,r.returncode,r.stdout[-250:],r.stderr[-250:])
    assert r.returncode==0
if __name__=='__main__':run('global-restored',capture())
