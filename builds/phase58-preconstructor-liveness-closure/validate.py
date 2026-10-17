"""Check new constructor/frontier evidence and preserve previous phases/sources."""
from pathlib import Path
import ast,json,hashlib,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    preserved={}
    for phase in ('phase57-first-mount-provenance','phase56-geometry-snapshot-lifecycle','phase53-existing-read-final-decision'):
        folder=ROOT/'builds'/phase;count=0
        for line in (folder/'SHA256SUMS.txt').read_text().splitlines():
            h,n=line.split('  ',1);assert sha(folder/n)==h,(phase,n);count+=1
        preserved[phase]=count
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for s in sources:assert sha(Path(s['path']))==s['sha256'],s['path']
    ins=load(OUT/'inspection.json');ct=load(OUT/'constructor-cases.json');cfg=load(OUT/'constructor-cfg.json');front=load(OUT/'startup-frontier.json')
    assert ins['image_sha256']==ct['image_sha256']=='0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738'
    assert ins['boot64k_sha256']=='09fcb71d6583a5714cb96d496ffb423c0d7049754a4cb4413f588d6f54148643'
    assert ins['preconstructor']['classification']=='SAFE' and ins['preconstructor']['relative_word']=='0x185'
    assert len(ct['cases'])==3
    expected=[int(c['target'],16)&~1 for c in load(ROOT/'builds/phase57-first-mount-provenance/ownership.json')['constructor_table']['entries']]
    for c in ct['cases']:
        assert c['returned'] and c['error'] is None and c['instructions']==1300
        assert c['private_record_unchanged'] and not c['private_write_intents']
        assert not c['relevant_operations'] and not c['explicit_MMIO_operands']
        assert len(c['allocations'])==11 and c['heap_cursor_after']=='0x20007750' and c['minimum_SP']=='0x2004ff78'
        assert [int(x['target'],16) for x in c['calls'] if x['pc']=='0x805b986']==expected
    assert ct['cases'][0]['executed_PCs']==ct['cases'][1]['executed_PCs']==ct['cases'][2]['executed_PCs']
    assert ct['cases'][2]['existing_capacity_reserved']
    assert cfg['instructions']==543 and not cfg['relevant_operations']
    assert {r['pc'] for r in cfg['unresolved']}=={'0x801cfaa','0x8037386'}
    assert front['frontier']['pc']=='0x801b266' and not front['first_mount_reached']
    assert front['private_record_unchanged'] and not front['relevant_operations']
    required=['findings.md','preconstructor-0805B958.md','reset-to-first-mount.md','early-storage-mutations.md',
        'async-preemption.md','state12-liveness.md','adapted-ownership.md','first-epoch-proof.md']
    links=0
    for name in required:
        p=OUT/name;assert p.stat().st_size>100
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(target).exists() or Path(target)==OUT/'validation.json',(name,target);links+=1
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('FIRST-MOUNT PROVENANCE FINAL CLOSURE = UNQUALIFIED')
    result=dict(confidence='PROVEN',scope='Authenticated constructor native/static evidence plus bounded startup continuation; not full asynchronous/native-adapter closure',
        prior_files_unchanged=preserved,pinned_sources_unchanged=len(sources),reports=8,local_links_checked=links,
        new_native_constructor_cases=3,instructions_per_constructor_case=1300,constructors_per_case=10,
        constructor_allocations_per_case=11,constructor_private_write_intents=0,constructor_watched_mutation_calls=0,
        conservative_constructor_CFG_instructions=543,optional_failure_callback_sites_with_explicit_premises=2,
        preconstructor_classification='SAFE under authenticated admitted constructor contract',startup_frontier='0x0801b266',
        complete_first_epoch_proven=False,complete_native_adapted_liveness=False,
        historical_suites_rerun=False,Phase53_reopened=False,hardware_access=False,MIDI_ports_opened=0,
        firmware_generated=False,SYX_generated=False,candidate_designated=False,firmware_modified=False,firmware_transmitted=False,
        verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
