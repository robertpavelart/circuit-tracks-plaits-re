"""Read-only prior-evidence checks; writes Phase46 consistency evidence only."""
from pathlib import Path
import ast, hashlib, json, re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    prior=ROOT/'builds/phase45-nor-mutation-closure';count=0
    for line in (prior/'SHA256SUMS.txt').read_text().splitlines():
        h,name=line.split('  ',1);assert sha(prior/name)==h,('Phase45 changed',name);count+=1
    older=0
    for name in ('phase43-hardware-test-candidate','phase44-preflash-redteam-closure'):
        base=ROOT/'builds'/name
        for filename,h in load(base/'validation.json')['evidence_sha256'].items():
            assert sha(base/filename)==h,('Historical evidence changed',name,filename);older+=1
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for row in sources:assert sha(Path(row['path']))==row['sha256'],row['path']
    data=load(OUT/'native-cases.json')
    assert len(data['scsi'])==18 and all(c['result']=='0xffffffff' and not c['write_calls'] for c in data['scsi'])
    assert all(c['table_equal'] for c in data['provenance']['applications'])
    assert len(data['settings_load'])==3
    assert all(c['status']==0 and c['bytes_written']==4096 for c in data['fat']['native_file_writes'])
    assert [m['native_sector'] for m in data['fat']['mappings']]==['0xfffad','0xfffae']
    assert data['fat']['mount_result']==0
    required=['findings.md','msd-reachability.md','filesystem-lba-binding.md',
        'address-bounds-audit.md','initialized-ram-callback.md','persistence-routes.md',
        'boot-to-capture-mutation-timeline.md','target-preservation-matrix.md']
    for name in required:assert (OUT/name).stat().st_size>0
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('PREFLASH STORAGE CLOSURE = UNQUALIFIED')
    for path in OUT.glob('*.py'):ast.parse(path.read_text(encoding='utf8'),filename=str(path))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    links=0
    for path in OUT.glob('*.md'):
        for target in re.findall(r'\]\(<([^>]+)>\)',path.read_text(encoding='utf8')):
            assert Path(target).exists() or Path(target)==OUT/'check-evidence.json',(path,target)
            links+=1
    result=dict(confidence='PROVEN',scope='Persisted results, report links and unchanged historical evidence; not final candidate qualification',
        verdict='UNQUALIFIED',phase45_files_verified_unchanged=count,historical_evidence_files_verified_unchanged=older,
        pinned_reference_sources_verified_unchanged=len(sources),reports=required,links_checked=links,
        native_application_decompressions=3,native_boot_decompressions=1,native_scsi_rejections=18,
        native_setting_mode_cases=2,native_startup_settings_producer_cases=3,
        synthetic_accepted_FAT_mounts=1,native_cluster_mappings=2,native_f_write_cases=2,
        cold_boot_completed=False,unit_filesystem_metadata_authenticated=False,final_candidate_designated=False,
        hardware_access=False,MIDI_ports_opened=0,firmware_generated=False,firmware_transmitted=False,
        reused_atomicity_and_update_tests=True)
    (OUT/'check-evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    files={p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS.txt'}
    (OUT/'SHA256SUMS.txt').write_text(''.join(h+'  '+n+'\n' for n,h in sorted(files.items())),encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
