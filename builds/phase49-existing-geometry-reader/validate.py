"""Validate Phase49 local results and preserved prior evidence; no replay or I/O."""
from pathlib import Path
import hashlib,json,ast,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    old=ROOT/'builds/phase48-current-unit-geometry';preserved=0
    for line in (old/'SHA256SUMS.txt').read_text().splitlines():
        h,name=line.split('  ',1);assert sha(old/name)==h,name;preserved+=1
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for row in sources:assert sha(Path(row['path']))==row['sha256'],row['path']
    tests=load(OUT/'parser-tests.json')
    assert len(tests['positive_cases'])==5 and len(tests['rejected_cases'])==24
    assert all(not t['intersects_normal_writable_mapping'] for c in tests['positive_cases'] for t in c['result']['targets'])
    inspect=load(OUT/'b13-inspection.json')
    assert inspect['dispatcher_bytes']=='2de9f04104000d46'
    assert inspect['image_bytes']==435220
    required=['findings.md','live-geometry-structure.md','b13-readonly-interfaces.md','minimum-read-plan.md','readonly-safety.md','geometry_parser.py']
    links=0
    for name in required:
        p=OUT/name;assert p.stat().st_size
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(target).exists() or Path(target)==OUT/'validation.json',(name,target);links+=1
    tree=ast.parse((OUT/'geometry_parser.py').read_text(encoding='utf8'))
    imports=[n.module if isinstance(n,ast.ImportFrom) else a.name for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom)) for a in (n.names if isinstance(n,ast.Import) else [None])]
    assert set(imports)=={'argparse','json','struct','pathlib'}
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('CURRENT-UNIT GEOMETRY READER = UNQUALIFIED')
    result=dict(confidence='PROVEN',prior_Phase48_files_unchanged=preserved,pinned_reference_sources_unchanged=len(sources),
        published_B13_image_sha256=inspect['image_sha256'],disassembly_ranges=len(inspect['ranges']),
        parser_positive_cases=5,parser_rejection_cases=24,parser_imports=imports,local_links_checked=links,
        hardware_access=False,MIDI_ports_opened=0,firmware_generated=False,firmware_modified=False,firmware_transmitted=False,
        current_unit_geometry_authenticated=False,supported_B13_geometry_reader_qualified=False,verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
