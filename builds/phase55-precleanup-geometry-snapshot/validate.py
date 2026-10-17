"""Phase55 consistency/preservation checks; no earlier experiments rerun."""
from pathlib import Path
import json,hashlib,ast,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    preserved={}
    for phase in ('phase54-early-evidence-snapshot','phase53-existing-read-final-decision'):
        folder=ROOT/'builds'/phase;count=0
        for line in (folder/'SHA256SUMS.txt').read_text().splitlines():
            h,n=line.split('  ',1);assert sha(folder/n)==h,(phase,n);count+=1
        preserved[phase]=count
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for s in sources:assert sha(Path(s['path']))==s['sha256'],s['path']
    scan=load(OUT/'inspection.json');cases=load(OUT/'mount-cases.json');host=load(OUT/'host-gate-cases.json')
    assert len(scan['images'])==4 and all(all(r['equal_stock'] for r in i['ranges']) for i in scan['images'])
    expected={i['name']:i['sha256'] for i in load(ROOT/'builds/phase54-early-evidence-snapshot/read-inspection.json')['images']}
    for i in scan['images']:assert i['sha256']==expected[i['name']]
    assert cases['passed'] and len(cases['cases'])==8
    for c in cases['cases']:
        assert not c['persistent_calls'] and c['supported_native_callee_registers_preserved']
        b=c['boundary'];assert b['registered_fs']=='0x20000ab0'
        assert b['geometry_pointer']=='0x20000a98' and b['wrapper']=='0x2000ac94'
        assert b['status']==0 or b['fs_type']==0
    assert cases['cases'][5]['boundary']['status']==0
    assert cases['cases'][5]['boundary']['record'][28:32]=='0000'
    assert not cases['cases'][5]['boundary']['legacy_parser_accepts']
    assert host['passed'] and len(host['cases'])==9
    assert sum(c['result']['allow_raw_evidence'] for c in host['cases'])==3
    assert scan['RAM_candidate']['cursor_above_proposed_limit']==44
    required=['findings.md','mount-to-persistence-ordering.md','geometry-record.md','geometry-authenticity.md',
              'snapshot-ram-liveness.md','snapshot-hook.md','host-gating.md','architecture-comparison.md']
    links=0
    for n in required:
        p=OUT/n;assert p.stat().st_size>100
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(target).exists() or Path(target)==OUT/'validation.json',(n,target);links+=1
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('PRECLEANUP GEOMETRY SNAPSHOT = UNQUALIFIED')
    r=dict(confidence='PROVEN',scope='Architecture evidence consistency and explicitly modeled native mounts/host gates, not full cold boot or current-unit acquisition',
        prior_files_unchanged=preserved,pinned_sources_unchanged=len(sources),images_compared=4,native_mount_cases=8,
        supplied_record_host_gate_cases=9,required_reports=8,local_links_checked=links,
        earlier_suites_rerun=False,Phase53_branch_reopened=False,hardware_access=False,MIDI_ports_opened=0,
        firmware_generated=False,firmware_modified=False,SYX_generated=False,firmware_transmitted=False,candidate_designated=False,
        fixed_RAM_qualified=False,complete_boot_queue_exclusion_qualified=False,snapshot_hook_emitted=False,
        actual_current_unit_record_obtained=False,verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='utf8')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
