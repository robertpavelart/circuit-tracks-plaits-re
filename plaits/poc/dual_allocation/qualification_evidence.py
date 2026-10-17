"""Summarize ordered ARM stores, DSP access traces and missing full-session inputs."""
import collections,hashlib,importlib,json,sys
from pathlib import Path
import study
ROOT,REF=study.ROOT,study.REF;OUT=ROOT/'builds/phase20h-budget-qualification'
study.setup();import vcf21 as V
def main():
    arm=json.loads((OUT/'arm-transitions.json').read_text());timeline=json.loads((OUT/'arm-retained-timeline.json').read_text())
    offsets={'O_FLAGS':V.O_FLAGS,'O_SIG':V.O_SIG,'O_SD':V.O_SD,'O_SAVED':V.O_SAVED}
    for t in (0,1):
        for n in ('RT_NOTE','RT_VEL','RT_CNT','RT_AUX','RT_TAG','RT_DLO','RT_DHI','RT_DX'):offsets[f't{t}/{n}']=V.O_RT+8*t+getattr(V,n)
    trace=[]
    for c in arm['calls']:
        if c['symbol'] not in ('vp_tri','c_mpload','c_vapply','c_vnon','c_vnoff'):continue
        a=bytes.fromhex(c['before']['tail']);b=bytes.fromhex(c['after']['tail'])
        events=[dict(order=i,**e,field=next((k for k,v in offsets.items() if e.get('address')==V.TAIL+v),None)) for i,e in enumerate(c['ordered_events']) if e['type']!='write' or not 0x2006d000<=e['address']<0x2006f000]
        trace.append(dict(call=c['id'],symbol=c['symbol'],args=c['args'],fields={k:dict(before=a[v],after=b[v]) for k,v in offsets.items()},ordered_events=events))
    (OUT/'ordered-field-transitions.json').write_text(json.dumps(dict(offsets=offsets,tail=V.TAIL,calls=trace),indent=2)+'\n')
    access={}
    for p in ('original','osc_only','osc_va'):
        counts=collections.Counter();addresses=collections.defaultdict(set);dead=[]
        reclaimed=[(0x390a,0x3913),(0x393a,0x3943),(0x3969,0x3990),(0x3999,0x39c0)]
        if p=='osc_va':reclaimed +=[(0x3916,0x3930),(0x3946,0x3960)]
        for line in (OUT/f'{p}-timeline-writes.csv').read_text().splitlines():
            pc,sp,ad,value=line.split(',');pc,ad,value=int(pc,16),int(ad,16),int(value,16);counts[sp]+=1;addresses[sp].add(ad)
            if p!='original' and sp=='X' and any(a<=ad<b for a,b in reclaimed):dead.append(dict(pc=pc,space=sp,address=ad,value=value))
        assert not dead,(p,dead[:10])
        ranges={}
        for sp,ads in addresses.items():
            rs=[]
            for ad in sorted(ads):
                if rs and rs[-1][1]==ad:rs[-1][1]=ad+1
                else:rs.append([ad,ad+1])
            ranges[sp]=rs
        access[p]=dict(write_counts=dict(counts),unique_write_ranges_half_open=ranges,reclaimed_X_write_violations=dead,reclaimed_X_ranges_checked=reclaimed if p!='original' else [],runtime_P_writes=0,scope='Observed finite timeline only; fixture witness X6000/X6020 and external capture storage are explicit test allocations, not ownership claims')
    prereq={}
    for p in [REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin',REF/'ctre/Firmware-Analysis/ram_dump_firmware_0x08037988.bin']:
        prereq[str(p)]=p.exists()
    try:importlib.import_module('dsp_session');session_error=None
    except Exception as e:session_error=repr(e)
    result=dict(ARM_calls=len(arm['calls']),ARM_mailbox_messages=len(arm['mail']),mode_transitions=len(arm['transitions']),checksum_valid_patch_flag_cases=len(arm['patch_flag_cases']),ARM_stale_ACT_messages=[w for w in arm['mail'] if w['code']==19 and (((w['value']&3)==1 and w['value']&0x400) or ((w['value']&3)==2 and w['value']&0x1000 and w['value']&0x400))],
        timeline_calls=len(timeline['calls']),timeline_frames=len(timeline['initial_frames'])+len(timeline['frames']),timeline_no_mail_frames=sum(not f['mail'] for f in timeline['frames']),write_access=access,
        reference_session_prerequisites=prereq,reference_Session_import_error=session_error,full_retained_workload_executed=False,
        missing_workloads=['Authentic ARM boot/session heap and parameter initialization','Active stock Synth1/Synth2 generator execution','Concurrent drums/audio and complete sequencer scheduling','Concurrent core1 granular/glitch production and stock gather service','Whole-device pan/sends/sidechain and project apply/save/restore'])
    (OUT/'qualification-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
    inventory=json.loads((ROOT/'builds/phase20e-full-plaits-audit/source-inventory.json').read_text())['reference_before']
    assert all(hashlib.sha256((REF/p).read_bytes()).hexdigest()==h for p,h in inventory.items())
    current={str(p.relative_to(REF)).replace('\\','/') for p in REF.rglob('*') if p.is_file()};assert current==set(inventory)
    source=json.loads((ROOT/'plaits/upstream/source-manifest.json').read_text())['files'];assert all(hashlib.sha256((ROOT/'plaits/upstream'/p['path']).read_bytes()).hexdigest()==p['sha256'] for p in source)
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file() and p.name!='verification.json'}
    (OUT/'verification.json').write_text(json.dumps(dict(reference_files_unchanged=len(inventory),reference_files_added=0,pinned_source_files_unchanged=len(source),artifacts=hashes),indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('write_access',)},indent=2))
if __name__=='__main__':main()
