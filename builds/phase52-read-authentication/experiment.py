"""Exhaustive bounded prefix-fault/interleaving experiment; synthetic sectors only."""
from native_sequence import *
def seq(fault_index=None,refresh=4096,outcome='completion'):
    m=Model();values=[]
    for i,lba in enumerate((64,65,64)):
        v=m.read(lba,refresh if i==fault_index else 4096,outcome if i==fault_index else 'completion')
        values.append(v)
        if v is None:break
    while len(values)<3:values.append(None)
    t,c,t2=values
    return dict(fault_index=fault_index,refresh=refresh,outcome=outcome,trace=m.history,
        simple_512=triple(*(None if v is None else v[:512] for v in values)),
        simple_4096=triple(t,c,t2),BPB_gate=structural(t) and structural(t2),
        enhanced_4096=enhanced(t,c,t2))
def main():
    baseline=seq();assert baseline['enhanced_4096']
    failures=[]
    for i in range(3):
        for name,n in [('no-byte-false-completion',0),('partial128',128),('partial512',512),('stale-completion-no-new-DMA',0)]:
            r=seq(i,n,name);failures.append(r)
        r=seq(i,0,'timeout');assert not r['enhanced_4096'] and len(r['trace'])==i+1;failures.append(r)
        r=seq(i,128,'partial-timeout');assert not r['enhanced_4096'] and len(r['trace'])==i+1;failures.append(r)
    exhaustive=[]
    for n in range(513):
        r=seq(2,n,'prefix-completion')
        assert r['enhanced_4096']==(n==512)
        exhaustive.append(dict(refreshed_bytes=n,accepted_512=r['simple_512'] and r['BPB_gate'],
            accepted_4096=r['enhanced_4096'],returned_512_hex=r['trace'][2]['returned_512_hex'],
            returned_4096_sha256=r['trace'][2]['returned_4096_sha256'],trace=r['trace']))
    # Both controls have legitimate zero suffixes; partial refresh can produce
    # exactly their full expected bytes. This is not an incorrect-target proof.
    m=Model();v=[m.read(64),m.read(65,8,'partial-control-A'),m.read(64),m.read(73,27,'partial-control-B'),m.read(64)]
    five=all(x==v[0] for x in (v[2],v[4])) and v[0]!=v[1] and v[0]!=v[3] and v[1]!=v[3] and structural(v[0])
    assert five and v[1]==FAT and v[3]==ROOT_SECTOR
    five_trace=m.history
    m=Model();a0=m.read(64);c0=m.read(65);replayed=m.read(64,source=FAT)
    assert not enhanced(a0,c0,replayed)
    immediate_trace=m.history
    # Logical replay ambiguity: well-formed older target substituted by the DMA
    # outcome seam twice. No claim of a native old-sector replay producer.
    stale=bytearray(TARGET);stale[13]=2;stale[22:24]=(2).to_bytes(2,'little');stale=bytes(stale)
    assert structural(stale)
    m=Model();a=m.read(64,source=stale);b=m.read(65);c=m.read(64,source=stale)
    assert enhanced(a,b,c) and a!=TARGET
    result=dict(confidence='PROVEN',scope='Native host-facing execution; physical outcomes are explicit synthetic seams',
        vectors=dict(target_512=TARGET[:512].hex(),control_A_512=FAT[:512].hex(),control_B_512=ROOT_SECTOR[:512].hex(),
                     target_full_sha256=sha(TARGET),control_A_full_sha256=sha(FAT),control_B_full_sha256=sha(ROOT_SECTOR)),
        baseline=baseline,independent_faults=failures,partial_T2_exhaustive=exhaustive,
        five_read_partial_controls=dict(accepted=five,trace=five_trace,
            refreshed_A=8,refreshed_B=27,all_returned_bytes_equal_full_control=True,
            scope='A five-read sequence cannot certify complete control refresh; target geometry is still correct in this case'),
        older_target_replay=dict(accepted=True,returned_512=a[:512].hex(),trace=m.history,
            scope='Hypothetical repeated old well-formed BPB at physical-data seam; native reachability UNKNOWN'),
        immediate_control_replay=dict(accepted=False,trace=immediate_trace,
            scope='Hypothetical replay of immediately previous control into target response'),
        partial_lengths_tested=513,shorter_than_512_target_prefixes_accepted=0,
        exactly_512_accepted=True,full_4096_completion_authenticated=False,
        hardware_access=False,firmware_generated=False)
    (OUT/'authentication-experiment.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(prefix_lengths=513,short_target_prefixes_accepted=0,
        independent_fault_cases=len(failures),C_zero_failure_simple_accepts=next(c for c in failures if c['fault_index']==1 and c['refresh']==0 and c['outcome']=='no-byte-false-completion')['simple_4096'],
        five_read_partial_controls_pass=five,old_target_replay_passes=True)))
if __name__=='__main__':main()
