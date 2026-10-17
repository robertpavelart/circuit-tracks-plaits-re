"""Check saved Phase50 results and integrity only; no historical test reruns."""
from pathlib import Path
import ast,hashlib,json,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    prior=ROOT/'builds/phase49-existing-geometry-reader';preserved=0
    for line in (prior/'SHA256SUMS.txt').read_text().splitlines():
        h,name=line.split('  ',1);assert sha(prior/name)==h,name;preserved+=1
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for s in sources:assert sha(Path(s['path']))==s['sha256'],s['path']
    native=load(OUT/'native-reads.json');geometry=load(OUT/'geometry-tests.json');inspection=load(OUT/'b13-inspection.json')
    assert native['image_sha256']==inspection['image_sha256']=='2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41'
    assert len(native['SCSI'])==7 and len(native['modes'])==4
    assert all(r['result']==0 and r['persistent_write_or_FS_flush_calls']==0 for r in native['SCSI'])
    assert native['SCSI'][4]['NOR_reads']==[dict(physical='0xd4000',bytes=4096)]
    assert native['modes'][1]['registered_classes']==['0x200000ec','0x200000f8']
    assert native['modes'][1]['window_record']=='0x8038c3c'
    assert len(geometry['positive'])==5 and len(geometry['rejected'])==15
    assert all(not t['intersects_normal_writable_mapping'] for c in geometry['positive'] for t in c['parser']['targets'])
    required=['findings.md','msd-backing-store.md','scsi-read-path.md','minimum-sector-plan.md',
              'physical-binding.md','readonly-safety.md','mode-entry.md','geometry_from_sector.py']
    links=0
    for name in required:
        p=OUT/name;assert p.stat().st_size
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(target).exists() or Path(target)==OUT/'validation.json',(name,target);links+=1
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('MSD READ-ONLY GEOMETRY PATH = UNQUALIFIED')
    result=dict(confidence='PROVEN',scope='Offline result consistency, not a live USB/geometry admission',
        prior_Phase49_files_unchanged=preserved,pinned_reference_sources_unchanged=len(sources),
        published_B13_image_sha256=inspection['image_sha256'],SCSI_native_slices=7,vendor_deferred_mode_native_slices=4,
        native_BPB_parser_matches=5,decoder_rejections=15,local_links_checked=links,
        hardware_access=False,MIDI_ports_opened=0,firmware_generated=False,firmware_modified=False,firmware_transmitted=False,
        current_unit_geometry_acquired=False,full_mode_USB_driver_worker_closure=False,verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
