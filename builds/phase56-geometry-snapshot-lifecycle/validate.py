"""Preservation and Phase56 evidence consistency; no previous experiment reruns."""
from pathlib import Path
import ast,json,re,hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    preserved={}
    for phase in ('phase55-precleanup-geometry-snapshot','phase54-early-evidence-snapshot','phase53-existing-read-final-decision'):
        d=ROOT/'builds'/phase;n=0
        for line in (d/'SHA256SUMS.txt').read_text().splitlines():
            h,name=line.split('  ',1);assert sha(d/name)==h,(phase,name);n+=1
        preserved[phase]=n
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for s in sources:assert sha(Path(s['path']))==s['sha256'],s['path']
    compact=load(OUT/'compact-tests.json');model=load(OUT/'lifecycle-tests.json')
    commit=load(OUT/'commit-tests.json');live=load(OUT/'liveness-tests.json');census=load(OUT/'census.json')
    assert compact['passed'] and compact['bytes']==8 and len(compact['round_trips'])==5
    assert len(compact['rejections'])==7 and compact['factor_cases']==16
    assert model['passed'] and model['bytes']==12 and len(model['cases'])==7 and len(model['interleavings'])==4
    assert commit['passed'] and commit['helper_bytes']==46 and commit['static_instructions']==16 and len(commit['cases'])==12
    assert {r['instructions'] for r in commit['cases']}=={10,16}
    assert all(r['stack_delta']==24 and r['registers_flags_mask_preserved'] for r in commit['cases'])
    assert {r['mask_set_entry_instructions'] for r in commit['cases'] if r['initial_mask']==0}=={4,10}
    assert live['passed'] and live['initialization_overwrites_record'] and live['legacy_timeout_corrupts_compact_record']
    assert census['image_sha256']=='0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738'
    assert census['image_bytes']==375948 and not census['all_computed_references_closed']
    required=['findings.md','minimal-snapshot-layout.md','ram-ownership.md','snapshot-liveness.md',
        'async-startup-exclusion.md','remount-invalidation.md','generation-gating.md','toctou-review.md','revised-architecture.md']
    links=0
    for name in required:
        p=OUT/name;assert p.stat().st_size>100
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(target).exists() or Path(target)==OUT/'validation.json',(name,target);links+=1
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('GEOMETRY SNAPSHOT LIFECYCLE = UNQUALIFIED')
    r=dict(confidence='PROVEN',scope='Preservation, native local collisions/commit helper and abstract models; not complete startup or corrected-owner qualification',
        prior_files_unchanged=preserved,pinned_sources_unchanged=len(sources),reports=len(required),local_links_checked=links,
        compact_record_bytes=8,proposed_union_bytes=12,native_liveness_collisions=2,native_commit_cases=12,
        compact_round_trips=5,compact_rejections=7,compact_factor_cases=16,lifecycle_scenarios=7,event_interleavings=4,
        previous_suites_rerun=False,Phase53_branch_reopened=False,hardware_access=False,MIDI_ports_opened=0,
        firmware_generated=False,SYX_generated=False,firmware_modified=False,firmware_transmitted=False,candidate_designated=False,
        isolated_commit_emulator_fragment=True,complete_owner_liveness_qualified=False,
        complete_async_startup_exclusion=False,complete_native_invalidator_coverage=False,
        native_queue_admission_interlock_qualified=False,verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='utf8')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
