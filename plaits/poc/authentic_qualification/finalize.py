"""Summarize provenance, access changes, object sources and protected-input hashes."""
import collections,json
from environment import *
def main():
    old=json.loads((OUT/'provenance.json').read_text());changed_inputs=[p for p,h in old['reference_before'].items() if sha(Path(p).read_bytes())!=h];assert not changed_inputs,changed_inputs
    w=json.loads((OUT/'authentic-ARM-workload.json').read_text());compar=json.loads((OUT/'long-comparison.json').read_text())
    trace0=(OUT/'long-original/trace.bin').read_bytes();access={}
    for p in ('osc_only','osc_va'):
        t=(OUT/f'long-{p}/trace.bin').read_bytes();assert len(t)==len(trace0)==0x100000
        changed=[]
        for off,(a,b) in enumerate(zip(trace0,t)):
            if a!=b:changed.append(dict(space='X' if off<0x80000 else 'Y',address=off%0x80000,before=a,after=b))
        access[p]=dict(changed_access_bit_addresses=changed,meaning='1 read, 2 write; finite core0 trace, not full numerical write equivalence or external coverage')
    # Authentic root chain used by c_vtrack, measured independently on a new
    # reference-initialized session. No arbitrary object pointer substitution.
    s=authentic_session();chain=[];a=0x200069e4
    for delta in (0,0x40,0x2c):
        a=s.e.r32(a+delta);chain.append(a)
    handlers={name:s.e.r32(a+0x148+4*i) for i,name in enumerate(['Synth1','Synth2','MIDI1','MIDI2','Drum1','Drum2','Drum3','Drum4'])}
    snapshots={name:bytes(s.e.uc.mem_read(ptr,32)).hex() for name,ptr in handlers.items() if 0x20000000<=ptr<0x2004ffe0}
    invalidflags=[]
    for f in w['frames']:
        for _,ws in f['events']:
            for core,sp,ad,value in ws:
                if sp=='x' and ad in (0x3b80,0x3bb0) and value>>16&127==19:
                    act=value&3;df=value>>8&31
                    if act==1 and df&4 or act==2 and df&16 and df&4:invalidflags.append(dict(block=f['block'],address=ad,value=value))
    from compare import read
    blocks,_=read('original');nonzero=sum(any(b['dumps']['X 002e10']) for b in blocks)
    summary=dict(protected_reference_files_unchanged=len(old['reference_before']),reference_changes=changed_inputs,ARM_objects=dict(chain=chain,handlers=handlers,handler_bytes=snapshots,scope='Authentic receiver/controller chain; B1.3 extra state initialized by executed code, not present as B1.3 state in the stock dump'),
        access_changes=access,invalid_ACT_messages_in_long_workload=invalidflags,master_nonzero_blocks=nonzero,master_zero_blocks=len(blocks)-nonzero,
        long_blocks_per_profile=4096,long_audio_blocks_total=12288,expanded_state_snapshots_per_profile=65,reference_whole_core_spin_patches=[0x76a,0x76f,0x77d],
        unresolved=['No coupled core1/gather service or real SPI/DSP read responses','No authenticated DSP X/Y/external SDRAM checkpoint or verified external-data initializer for the captured session','Installed dsptool cannot retain values at Y340000/YE80000; its 0x80000-word backend silently returns zero','Unstubbed patch load does not return under captured scheduler/lock state','All long-run post-Master-FX snapshots zero; this does not qualify a non-silent complete mix','Histogram/entry guard is at outer interpreter dispatch; optimized DO bodies do not have complete per-instruction PC tracing','Full project filesystem, scheduler/interrupt/preemption and numerical writes outside captured ranges not qualified'])
    (OUT/'qualification-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    pinned=json.loads((ROOT/'plaits/upstream/source-manifest.json').read_text())['files'];assert all(sha((ROOT/'plaits/upstream'/row['path']).read_bytes())==row['sha256'] for row in pinned)
    artifacts={str(p.relative_to(ROOT)).replace('\\','/'):sha(p.read_bytes()) for folder in (OUT,ROOT/'plaits/poc/authentic_qualification') for p in folder.rglob('*') if p.is_file() and p.name!='verification.json'}
    (OUT/'verification.json').write_text(json.dumps(dict(reference_files_verified=len(old['reference_before']),pinned_Plaits_files_verified=len(pinned),artifacts=artifacts),indent=2)+'\n')
    print(json.dumps(dict(objects=handlers,access_change_counts={k:len(v['changed_access_bit_addresses']) for k,v in access.items()},invalid_ACT_messages=len(invalidflags),reference_changes=changed_inputs),indent=2))
if __name__=='__main__':main()
