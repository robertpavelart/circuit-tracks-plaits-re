"""Validate Phase48 evidence without rerunning historical suites or opening I/O."""
from pathlib import Path
import hashlib,json,ast,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    old=ROOT/'builds/phase47-filesystem-state-closure';preserved=0
    for line in (old/'SHA256SUMS.txt').read_text().splitlines():
        h,name=line.split('  ',1);assert sha(old/name)==h,name;preserved+=1
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for row in sources:assert sha(Path(row['path']))==row['sha256'],row['path']
    inv=load(OUT/'existing-evidence-inventory.json')
    assert len((OUT/'project-file-inventory.txt').read_text(encoding='utf8').splitlines())==inv['files']==75892
    assert len(inv['candidates'])==233 and len(inv['archives'])==14
    result=load(OUT/'geometry-review.json')
    versions=result['version_comparison']['images'];assert len(versions)==4
    assert all(all(r['equal_stock'] for r in v['ranges']) for v in versions)
    assert len(result['bounded_normal_mount_cases'])==4
    assert all(c['result']==0 and not c['writes'] and c['total_sectors']==7980 for c in result['bounded_normal_mount_cases'])
    assert result['native_NOR_sector_query']['result']==4096
    required=['findings.md','existing-unit-evidence.md','formatter-layout.md','mount-validation.md',
        'version-geometry-comparison.md','minimum-readonly-evidence.md']
    links=0
    for name in required:
        p=OUT/name;assert p.stat().st_size
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(target).exists() or Path(target)==OUT/'validation.json',(name,target);links+=1
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('CURRENT-UNIT GEOMETRY CLOSURE = UNQUALIFIED')
    r=dict(confidence='PROVEN',scope='Local evidence consistency; no current-unit state acquisition',
        prior_Phase47_files_unchanged=preserved,pinned_reference_sources_unchanged=len(sources),
        project_files_inventoried=inv['files'],candidate_records=len(inv['candidates']),archives_reviewed=len(inv['archives']),
        existing_images_compared=4,ranges_compared_per_image=4,native_bounded_mount_cases=4,native_NOR_sector_queries=1,
        current_unit_geometry_authenticated=False,reports=required,local_links_checked=links,
        hardware_access=False,MIDI_ports_opened=0,firmware_generated=False,firmware_transmitted=False,
        candidate_designated=False,verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='utf8')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
