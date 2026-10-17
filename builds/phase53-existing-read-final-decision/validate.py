"""Decision evidence consistency and preservation; no previous suite reruns."""
from pathlib import Path
import ast,hashlib,json,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    prior=ROOT/'builds/phase52-read-authentication';preserved=0
    for line in (prior/'SHA256SUMS.txt').read_text().splitlines():
        h,n=line.split('  ',1);assert sha(prior/n)==h,n;preserved+=1
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for s in sources:assert sha(Path(s['path']))==s['sha256'],s['path']
    d=load(OUT/'producer-cases.json');scan=load(OUT/'existing-paths.json')
    assert scan['image_sha256']=='2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41'
    assert all(r['equal_stock'] for r in scan['ranges'])
    assert len(d['commands'])==9 and [c['generated_response_length'] for c in d['commands']]==[36,36,7,18,18,8,8,8,12]
    assert all(c['bytes36_through511_unchanged'] and c['persistent_or_storage_calls']==0 for c in d['commands'])
    assert d['max_non_NOR_generated_response_bytes']==36
    rows=d['mode1_LBAs_00_3F'];assert len(rows)==64 and [r['USB_LBA'] for r in rows]==list(range(64))
    for r in rows:
        assert r['NOR_wrapper_reads']==[dict(address=hex(0x94000+r['USB_LBA']*4096),bytes=4096)]
    assert not scan['initialized_pointer_candidates'] and not scan['immediate_candidates']
    required=['findings.md','buffer-producers.md','synthetic-msd-sectors.md','deterministic-poison-analysis.md',
              'completion-signals.md','existing-b13-final-verdict.md'];links=0
    for n in required:
        p=OUT/n;assert p.stat().st_size
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(target).exists() or Path(target)==OUT/'validation.json',(n,target);links+=1
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('EXISTING B1.3 GEOMETRY AUTHENTICATION = FAIL')
    r=dict(confidence='PROVEN',decision_scope='Inspected supported existing B1.3 interfaces, not arbitrary undocumented/corrupted execution',
        prior_Phase52_files_unchanged=preserved,pinned_reference_sources_unchanged=len(sources),
        exact_image_sha256=scan['image_sha256'],native_data_in_producer_cases=9,native_low_window_bindings=64,
        maximum_generated_non_NOR_response_bytes=36,Phase52_target_control_experiments_repeated=False,
        independent_completion_export_found=False,usable_full_buffer_poison_mechanism_found=False,
        local_links_checked=links,hardware_access=False,MIDI_ports_opened=0,firmware_generated=False,
        firmware_modified=False,firmware_transmitted=False,new_diagnostic_generated=False,
        authentication_answer='PROVEN NO',branch_closed=True,verdict='FAIL')
    (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='utf8')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
