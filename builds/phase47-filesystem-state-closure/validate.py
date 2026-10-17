"""Consistency checks only; no old runner invocation or firmware output."""
from pathlib import Path
import json,hashlib,ast,re,struct
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    preserved=0
    prior=ROOT/'builds/phase46-msd-filesystem-closure'
    for line in (prior/'SHA256SUMS.txt').read_text().splitlines():
        h,name=line.split('  ',1);assert sha(prior/name)==h,name;preserved+=1
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for row in sources:assert sha(Path(row['path']))==row['sha256'],row['path']
    provenance=load(OUT/'geometry-provenance.json');ram=Path(provenance['RAM_path']).read_bytes()
    assert hashlib.sha256(ram).hexdigest()==provenance['RAM_sha256']
    f=0xab0
    assert ram[f]==2 and struct.unpack_from('<H',ram,f+12)[0]==4096
    assert struct.unpack_from('<I',ram,f+32)[0]==0x1f21
    assert struct.unpack_from('<I',ram,f+52)[0]==13
    r=load(OUT/'normal-states.json')
    assert r['cluster_mapping_count']==7967 and r['min_lba']==13 and r['max_lba']==0x1f2b
    assert len(r['cases'])==4 and len(r['startup'])==3
    for case in r['cases']+r['startup']:
        assert not case['identity_touched'] and not case['coefficients_touched']
        for w in case['writes']:
            assert 0xd4000<=int(w['start'],16)<int(w['end'],16)<=0x2000000
    assert r['startup'][0]['startup']['events']==['SIZE','READ']
    assert r['startup'][1]['startup']['events']==['SIZE']
    required=['findings.md','real-filesystem-geometry.md','countermodel-comparison.md',
        'target-address-equations.md','startup-persistence.md','realistic-startup-states.md',
        'initialized-ram-callback.md','target-preservation.md']
    links=0
    for name in required:
        p=OUT/name;assert p.stat().st_size
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(target).exists() or Path(target)==OUT/'validation.json',(name,target);links+=1
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('PREFLASH FILESYSTEM STATE CLOSURE = UNQUALIFIED')
    result=dict(confidence='PROVEN',scope='Saved result/provenance consistency; no actual-unit qualification',
        prior_phase46_files_unchanged=preserved,pinned_reference_files_unchanged=len(sources),
        native_cluster_conversions=7967,normal_file_operation_cases=4,startup_cases=3,
        reference_geometry_authenticated=True,current_unit_geometry_authenticated=False,
        reports=required,links_checked=links,hardware_access=False,MIDI_ports_opened=0,
        firmware_generated=False,firmware_transmitted=False,candidate_designated=False,
        verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
