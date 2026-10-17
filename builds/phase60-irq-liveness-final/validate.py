"""Integrity/ABI/result validation; historical evidence is hash-checked, not rerun."""
from pathlib import Path
import json,hashlib,ast,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def main():
    preserved={}
    for phase in ('phase59-scheduler-first-mount-order','phase58-preconstructor-liveness-closure','phase57-first-mount-provenance','phase56-geometry-snapshot-lifecycle','phase53-existing-read-final-decision'):
        folder=ROOT/'builds'/phase;count=0
        for line in (folder/'SHA256SUMS.txt').read_text().splitlines():
            h,n=line.split('  ',1);assert sha(folder/n)==h,(phase,n);count+=1
        preserved[phase]=count
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for s in sources:assert sha(Path(s['path']))==s['sha256'],s['path']
    inv=load(OUT/'irq-inventory.json');base=load(OUT/'observed-prefix.json');tests=load(OUT/'irq-tests.json');owners=load(OUT/'owner-model-tests.json')
    assert base['executed_instructions']==59306 and base['mount_return_status']==0 and base['fs_type']==2
    expected={14,15,18,24,28,30,36,37,38,40,41,49,50,56,59,60,69,70,84,92}
    assert {r['irq'] for r in inv['snapshots'][0]['enabled']}==expected
    assert 77 not in expected and len(tests['cases'])==9
    mut={'wrapper program','wrapper erase','backend program','backend erase','NOR program','NOR erase','NOR chip erase','identity write','filesystem write','unlink','MSD write callback','file write','mapped filesystem write'}
    for c in tests['cases']:
        r=load(OUT/f"irq{c['irq']}.json");trace=load(OUT/f"irq-{c['irq']}-trace.json")
        assert r['mount_return_status']==0 and r['fs_type']==2 and r['private_unchanged'] and not r['private_writes']
        assert len(trace['injected'])==1 and c['geometry_hex']==inv['snapshots'][-1]['geometry_record_hex']
        assert not [x for x in r['operations'] if x['kind'] in mut]
    assert owners['all_cases_passed'] and len(owners['cases'])==11 and len(owners['oracle_comparisons'])==22
    assert all(x['independent_oracle_equal'] for x in owners['oracle_comparisons'])
    assert owners['native_mount_record_hex']==inv['snapshots'][-1]['geometry_record_hex']
    assert not owners['actual_old_owner_call_sites_replaced'] and not owners['full_lifetime_closed']
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    reports=['findings.md','early-irq-inventory.md','usb-startup-order.md','timer-systick-order.md','irq-preemption-tests.md','state12-full-liveness.md','adapted-owner-model.md','final-first-epoch-verdict.md'];links=0
    for name in reports:
        p=OUT/name;assert p.stat().st_size>100
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text()):assert Path(target).exists(),target;links+=1
    assert (OUT/'findings.md').read_text().rstrip().endswith('FINAL PREFLASH PROVENANCE CLOSURE = UNQUALIFIED')
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    app=ROOT/'builds/phase44-preflash-redteam-closure/circuittracks-4486-nor-evidence-atomic-test.bin'
    assert sha(app)=='0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738'
    r=dict(confidence='PROVEN',scope='Persisted native handler/owner model tests and artifact integrity, not universal IRQ/native-adapter closure',prior_files_unchanged=preserved,pinned_sources_unchanged=len(sources),baseline_native_instructions=59306,enabled_external_IRQs=20,external_IRQ_cases=9,native_owner_boundary_cases=11,independent_oracle_transition_comparisons=22,reports=8,local_links_checked=links,private_write_intents_in_IRQ_cases=0,watched_mutation_entries_in_IRQ_cases=0,all_native_old_owner_adapters_installed=False,all_early_IRQ_branches_qualified=False,first_epoch_verdict='UNKNOWN',target82000_presnapshot_mutation='UNKNOWN',target81000_presnapshot_mutation='UNKNOWN',hardware_access=False,MIDI_ports_opened=0,firmware_generated=False,SYX_generated=False,firmware_transmitted=False,historical_suites_rerun=False,verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'))
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
