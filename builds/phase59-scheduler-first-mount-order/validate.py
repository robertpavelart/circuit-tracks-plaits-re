"""Validate persisted Phase59 evidence and historical/source hashes only."""
from pathlib import Path
import json,hashlib,ast,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    preserved={}
    for phase in ('phase58-preconstructor-liveness-closure','phase57-first-mount-provenance','phase56-geometry-snapshot-lifecycle','phase53-existing-read-final-decision'):
        folder=ROOT/'builds'/phase;count=0
        for line in (folder/'SHA256SUMS.txt').read_text().splitlines():
            h,n=line.split('  ',1);assert sha(folder/n)==h,(phase,n);count+=1
        preserved[phase]=count
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for s in sources:assert sha(Path(s['path']))==s['sha256'],s['path']
    summary=load(OUT/'case-summary.json');assert len(summary['cases'])==9
    mutations={'wrapper program','wrapper erase','backend program','backend erase','NOR program','NOR erase','NOR chip erase','identity write','filesystem write','unlink','MSD write callback','file write','mapped filesystem write'}
    for case in summary['cases']:
        r=load(OUT/(case['case']+'.json'))
        assert r['private_unchanged'] and not r['private_writes']
        assert not [x for x in r['operations'] if x['kind'] in mutations]
        if case['case']=='native-startup':
            assert r['frontier']['pc']=='0x803759a' and not r['switches']
        else:
            assert r['frontier']['pc']=='0x801ae06' and r['frontier']['type']=='checkpoint'
            expected=1 if case['case']=='modeled-startup' else 13 if case['case']=='invalid-bpb' else 0
            assert r['mount_return_status']==expected
            assert r['fs_type']==(2 if expected==0 else 0)
            names=[x['name'] for x in r['switches']]
            if case['case']!='early-systick':assert names[:5]==['IDLE','Main','UI','Storage','Content']
            assert all(t['priority']==0 for t in r['tasks'])
        for rd in r['physical_reads']:
            assert rd['buffer']+rd['length']<=0x20044d70 or rd['buffer']>=0x20044d7c
        assert len(r['tasks'])==4
    v=load(OUT/'modeled-valid-startup.json')
    assert [(x['address'],x['length']) for x in v['physical_reads']]==[(0x81000,23),(0xd4000,4096)]
    assert not any(x['kind']=='timer callback' for x in load(OUT/'earliest-timer.json')['operations'])
    assert any(x.get('event')=='deferred completion delivered through native 1BDE8' for x in load(OUT/'delayed-storage.json')['events'])
    assert any(x.get('event')=='early pending SysTick serviced at first eligible Thread instruction' for x in load(OUT/'early-systick.json')['events'])
    reports=['findings.md','postclock-controlflow.md','task-inventory.md','first-schedule-order.md','queue-order.md','timer-callback-order.md','storage-task-startup.md','filesystem-to-snapshot.md','state12-liveness.md','first-epoch-verdict.md']
    links=0
    for name in reports:
        p=OUT/name;assert p.stat().st_size>100
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(target).exists(),(name,target);links+=1
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text().rstrip().endswith('SCHEDULER FIRST-MOUNT ORDER = UNQUALIFIED')
    app=ROOT/'builds/phase44-preflash-redteam-closure/circuittracks-4486-nor-evidence-atomic-test.bin'
    assert sha(app)=='0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738'
    result=dict(confidence='PROVEN',scope='Saved native conditional cases and evidence integrity, not complete asynchronous/adapted ownership closure',prior_files_unchanged=preserved,pinned_sources_unchanged=len(sources),historical_image_sha256=sha(app),new_cases=9,mount_checkpoint_cases=8,successful_mount_cases=6,reports=len(reports),local_links_checked=links,private_write_intents=0,watched_mutation_entries=0,early_USB_case_qualified=False,earliest_native_timer_IRQ_qualified=False,complete_adapted_state12_liveness=False,first_epoch_verdict='UNKNOWN',target82000_mutation_verdict='UNKNOWN',target81000_mutation_verdict='UNKNOWN',historical_suites_rerun=False,hardware_access=False,MIDI_ports_opened=0,firmware_generated=False,SYX_generated=False,firmware_transmitted=False,verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
