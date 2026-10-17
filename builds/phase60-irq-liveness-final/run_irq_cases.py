"""Only new Phase60 IRQ cases. Existing Phase59 regression results are not rewritten."""
from pathlib import Path
import subprocess,sys,json
OUT=Path(__file__).resolve().parent
def main():
    rows=[]
    for irq in (28,30,37,38,40,49,50,70,92):
        extra=['--delayed-storage'] if irq==28 else []
        subprocess.run([sys.executable,'-B',str(OUT/'instrumented_startup.py'),'--peripheral-completion-model','--valid-bpb',*extra,f'--irq={irq}',f'--case=irq{irq}'],capture_output=True,text=True,check=True)
        r=json.loads((OUT/f'irq{irq}.json').read_text());t=json.loads((OUT/f'irq-{irq}-trace.json').read_text())
        assert len(t['injected'])==1 and r['mount_return_status']==0 and r['fs_type']==2 and r['private_unchanged'] and not r['private_writes']
        assert not [x for x in r['operations'] if x['kind'] in ('wrapper program','wrapper erase','backend program','backend erase','NOR program','NOR erase','NOR chip erase','identity write','filesystem write','unlink','MSD write callback','file write','mapped filesystem write')]
        rows.append(dict(irq=irq,injection=t['injected'][0],frontier=r['frontier'],mount_status=r['mount_return_status'],instructions=r['executed_instructions'],private_write_intents=0,watched_target_mutations=0,geometry_hex=t['snapshots'][-1]['geometry_record_hex']))
    result=dict(confidence='PROVEN',scope='Nine individual eligible source-event injections into inherited normal-success model; not all combinations, repeated events, power-hold shutdown, nested FP frames or actual controller timing',cases=rows,passed=True)
    (OUT/'irq-tests.json').write_text(json.dumps(result,indent=2)+'\n');print('Nine Phase60 IRQ cases passed')
if __name__=='__main__':main()
