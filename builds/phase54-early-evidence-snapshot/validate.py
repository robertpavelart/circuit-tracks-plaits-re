"""Check Phase54 evidence, reports and unchanged inputs without running earlier suites."""
from pathlib import Path
import ast,hashlib,json,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    prior=ROOT/'builds/phase53-existing-read-final-decision';preserved=0
    for line in (prior/'SHA256SUMS.txt').read_text().splitlines():
        h,n=line.split('  ',1);assert sha(prior/n)==h,n;preserved+=1
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for s in sources:assert sha(Path(s['path']))==s['sha256'],s['path']
    scan=load(OUT/'read-inspection.json');native=load(OUT/'reader-boundaries.json')
    expected={'B1.3':'2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41',
              'stock':'b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da',
              'SC35D8':'1525c6662bbff9ced7e6055bb54e864615c30013f1b4dec4be6c404f8c750c05',
              'corrected-diagnostic':'0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738'}
    for i in scan['images']:
        assert i['sha256']==expected[i['name']]
        assert all(row['equal_stock'] for row in i['ranges'])
    assert scan['boot']['sha256']=='09fcb71d6583a5714cb96d496ffb423c0d7049754a4cb4413f588d6f54148643'
    assert scan['reference_RAM']['sha256']=='26a29670c0c1918217b7eadf8f89fe6df97994d3cc6e1c0ed65ac522e161094c'
    assert scan['reference_RAM']['words']['0x20006a00']=='0x20005148'
    assert scan['first_resource_descriptor']['source']=='0x82000'
    assert scan['first_resource_descriptor']['word_count']==256
    assert scan['first_resource_descriptor']['identical_all_images']
    assert native['passed'] and len(native['cases'])==6
    required=['findings.md','stock-read-lifetimes.md','writer-ordering.md','snapshot-hooks.md',
              'snapshot-ram-liveness.md','completion-authentication.md','late-export-design.md','architecture-comparison.md']
    links=0
    for name in required:
        p=OUT/name;assert p.stat().st_size>100
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(target).exists() or Path(target)==OUT/'validation.json',(name,target);links+=1
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('EARLY EVIDENCE SNAPSHOT = UNQUALIFIED')
    r=dict(confidence='PROVEN',scope='Saved exact-image identity, six native boundary cases and architecture-document consistency; not full boot or hardware qualification',
        prior_Phase53_files_unchanged=preserved,pinned_reference_sources_unchanged=len(sources),
        compared_application_images=len(scan['images']),compared_ranges_per_image=len(scan['images'][0]['ranges']),
        native_boundary_cases=6,required_reports=len(required),local_links_checked=links,
        previous_suites_rerun=False,Phase53_branch_reopened=False,hardware_access=False,MIDI_ports_opened=0,
        firmware_generated=False,firmware_modified=False,firmware_transmitted=False,candidate_designated=False,
        code_hook_implemented=False,retention_address_qualified=False,completion_fence_qualified=False,
        pre_read_source_preservation_qualified=False,verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='utf8')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
