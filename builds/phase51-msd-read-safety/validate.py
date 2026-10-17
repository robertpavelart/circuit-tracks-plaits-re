"""Saved evidence checks, acceptance-gate checks, preservation; no device I/O."""
from pathlib import Path
import ast,hashlib,json,re
from acceptance_gate import assess
from read_cases import bpb
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    old=ROOT/'builds/phase50-msd-readonly-geometry';preserved=0
    for line in (old/'SHA256SUMS.txt').read_text().splitlines():
        h,n=line.split('  ',1);assert sha(old/n)==h,n;preserved+=1
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for s in sources:assert sha(Path(s['path']))==s['sha256'],s['path']
    inspection=load(OUT/'path-inspection.json');assert all(r['equal_stock'] for r in inspection['ranges'])
    reads=load(OUT/'read-cases.json')['cases'];modes=load(OUT/'mode-cases.json')
    assert len(reads)==10 and len(modes['transitions'])==4 and modes['forbidden_calls']==0
    assert [x['internal_mode'] for x in modes['transitions']]==[1,0,1,0]
    zero_hash=hashlib.sha256(bytes(4096)).hexdigest()
    for r in reads:
        assert r['queued_operations']==[1] and r['USB_data_bytes']==4096 and r['CSW_status']==0
        assert bytes.fromhex(r['CSW_hex'])[8:13]==bytes(5)
        assert r['persistent_write_or_FS_flush_calls']==0
        if r['kind'] in ('busy','bounds'):assert not r['parser_accepted'] and r['USB_data_sha256']==zero_hash
        elif r['kind']=='partial128-completion':assert not r['parser_accepted']
        else:assert r['parser_accepted']
        for p in r['physical_read_seam']:assert p['buffer_before_sha256']==zero_hash
    assert {r['USB_data_sha256'] for r in reads if r['kind']=='normal'}=={r['USB_data_sha256'] for r in reads if r['kind']=='partial512-completion'}
    gate_tests=[dict(name=n,result=assess(s)) for n,s in [('zero',{64:bytes(4096)}),('short',{64:bpb()[:-1]}),
         ('missing',{}),('structurally valid but unauthenticated',{64:bpb()})]]
    assert [t['result']['evidence'] for t in gate_tests]==['INVALID','INVALID','INVALID','UNQUALIFIED']
    required=['findings.md','mode1-entry-exit.md','read10-physical-path.md','read-error-propagation.md',
              'stale-buffer-analysis.md','geometry-acceptance-gate.md','minimum-hardware-read-plan.md']
    links=0
    for n in required:
        p=OUT/n;assert p.stat().st_size
        for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(target).exists() or Path(target)==OUT/'validation.json',(n,target);links+=1
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('MSD GEOMETRY READ SAFETY = UNQUALIFIED')
    r=dict(confidence='PROVEN',scope='Local evidence/strict-gate consistency; model seams are not hardware completion',
        prior_Phase50_files_unchanged=preserved,pinned_reference_sources_unchanged=len(sources),
        image_sha256=inspection['image_sha256'],stock_equal_inspected_ranges=len(inspection['ranges']),
        full_dispatcher_deferred_mode_transitions=4,coupled_native_read_cases=10,native_early_error_cases=4,
        hypothetical_partial_cases=4,acceptance_gate_tests=gate_tests,local_links_checked=links,
        hardware_access=False,MIDI_ports_opened=0,firmware_generated=False,firmware_modified=False,firmware_transmitted=False,
        current_unit_geometry_authenticated=False,verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='utf8')
    print(json.dumps({k:v for k,v in r.items() if k!='acceptance_gate_tests'},indent=2))
if __name__=='__main__':main()
