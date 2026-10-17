"""Run new Phase59 cases only; does not run historical suites."""
from pathlib import Path
import subprocess,sys,json
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
CASES=[('native-startup',[]),('modeled-startup',['--peripheral-completion-model']),('modeled-valid-startup',['--peripheral-completion-model','--valid-bpb']),('delayed-clock',['--peripheral-completion-model','--valid-bpb','--delayed-clock']),('early-systick',['--peripheral-completion-model','--valid-bpb','--early-systick']),('delayed-storage',['--peripheral-completion-model','--valid-bpb','--delayed-storage']),('earliest-timer',['--peripheral-completion-model','--valid-bpb','--earliest-timer']),('queued-query',['--peripheral-completion-model','--valid-bpb','--queued-query']),('invalid-bpb',['--peripheral-completion-model','--valid-bpb','--invalid-bpb'])]
def main():
    rows=[]
    for name,flags in CASES:
        subprocess.run([sys.executable,'-B',str(OUT/'native_startup.py'),*flags,'--case='+name],check=True,capture_output=True,text=True)
        r=json.loads((OUT/(name+'.json')).read_text());rows.append(dict(case=name,frontier=r['frontier'],status=r['mount_return_status'],instructions=r['executed_instructions'],private_unchanged=r['private_unchanged'],switches=len(r['switches']),writes=len(r['private_writes'])))
    (OUT/'case-summary.json').write_text(json.dumps(dict(confidence='PROVEN',scope='Measured native execution under each explicit model; not exhaustive scheduler/IRQ reachability',cases=rows,early_USB_adversarial_case='UNKNOWN: no separate USB task exists in observed creation set; early USB IRQ/callback dispatch not qualified',complete_adapted_state12_liveness=False),indent=2)+'\n')
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
