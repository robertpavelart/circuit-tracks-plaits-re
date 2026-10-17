"""Phase57 consistency and unchanged historical evidence; no hardware/suite calls."""
from pathlib import Path
import ast,json,re,hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    preserved={}
    for phase in ('phase56-geometry-snapshot-lifecycle','phase55-precleanup-geometry-snapshot','phase53-existing-read-final-decision'):
        d=ROOT/'builds'/phase;count=0
        for line in (d/'SHA256SUMS.txt').read_text().splitlines():
            h,n=line.split('  ',1);assert sha(d/n)==h,(phase,n);count+=1
        preserved[phase]=count
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for s in sources:assert sha(Path(s['path']))==s['sha256'],s['path']
    own=load(OUT/'ownership.json');model=load(OUT/'epoch-model-tests.json')
    assert own['image_sha256']=='0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738'
    assert len(own['byte_ledger'])==12 and len(own['accesses'])==23
    assert any(a['pc']=='0x806b794' and a['access']=='write' for a in own['accesses'])
    assert len(own['constructor_table']['entries'])==10
    assert own['constructor_table']['entries'][3]['target']=='0x801f051'
    assert own['scatter_zero']['end_exclusive']=='0x20006a54' and not own['scatter_zero']['overlaps_private_state']
    assert model['passed'] and model['state_bytes']==12 and len(model['cases'])==13
    assert not model['native_old_owner_adaptation'] and not model['full_boot_first_epoch_proven']
    required=['findings.md','existing-12byte-ownership.md','coalesced-state-layout.md','first-mount-provenance.md',
        'pre-first-mount-mutations.md','install-to-first-mount.md','async-exclusion.md','state-liveness.md','epoch-invariant.md']
    links=0
    for n in required:
        p=OUT/n;assert p.stat().st_size>100
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(target).exists() or Path(target)==OUT/'validation.json',(n,target);links+=1
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('FIRST-MOUNT GEOMETRY PROVENANCE = UNQUALIFIED')
    r=dict(confidence='PROVEN',scope='Original-owner instruction evidence, reset/constructor table analysis and conceptual 12-byte policy, not completed native boot or adapted owners',
        prior_files_unchanged=preserved,pinned_reference_sources_unchanged=len(sources),reports=9,local_links_checked=links,
        byte_ownership_rows=12,known_owner_access_candidates=23,enumerated_constructor_entries=10,strict_epoch_model_cases=13,
        previous_suites_rerun=False,Phase53_branch_reopened=False,hardware_access=False,MIDI_ports_opened=0,
        firmware_generated=False,SYX_generated=False,firmware_modified=False,firmware_transmitted=False,candidate_designated=False,
        complete_first_epoch_provenance=False,complete_async_exclusion=False,complete_native_state_liveness=False,
        critical_82000_pre_snapshot_preservation='UNKNOWN',identity_81000_pre_snapshot_preservation='UNKNOWN',
        verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='utf8')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
