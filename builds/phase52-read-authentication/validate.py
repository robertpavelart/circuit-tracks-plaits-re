"""Validate saved Phase52 coverage, transcripts, scopes and historical integrity."""
from pathlib import Path
import ast,hashlib,json,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    previous=ROOT/'builds/phase51-msd-read-safety';preserved=0
    for line in (previous/'SHA256SUMS.txt').read_text().splitlines():
        h,n=line.split('  ',1);assert sha(previous/n)==h,n;preserved+=1
    sources=load(ROOT/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
    for s in sources:assert sha(Path(s['path']))==s['sha256'],s['path']
    d=load(OUT/'authentication-experiment.json');rows=d['partial_T2_exhaustive']
    assert [r['refreshed_bytes'] for r in rows]==list(range(513))
    target=bytes.fromhex(d['vectors']['target_512'])
    for r in rows:
        n=r['refreshed_bytes'];expected=target[:n]+bytes(512-n)
        assert bytes.fromhex(r['returned_512_hex'])==expected
        assert r['accepted_512']==r['accepted_4096']==(n==512)
        assert len(r['trace'])==3
    faults=d['independent_faults'];assert len(faults)==18
    timeouts=[f for f in faults if f['outcome'] in ('timeout','partial-timeout')]
    assert len(timeouts)==6
    for f in timeouts:
        assert len(f['trace'])==f['fault_index']+1
        assert f['trace'][-1]['USB_bytes']==0 and f['trace'][-1]['returned_512_hex'] is None
    control_failure=next(f for f in faults if f['fault_index']==1 and f['outcome']=='no-byte-false-completion')
    assert control_failure['simple_4096'] and not control_failure['enhanced_4096']
    assert d['five_read_partial_controls']['accepted'] and len(d['five_read_partial_controls']['trace'])==5
    assert d['older_target_replay']['accepted'] and not d['immediate_control_replay']['accepted']
    traces=d['baseline']['trace']+[t for r in rows for t in r['trace']]+[t for f in faults for t in f['trace']]
    traces+=d['five_read_partial_controls']['trace']+d['older_target_replay']['trace']+d['immediate_control_replay']['trace']
    for t in traces:
        if t['USB_bytes']:
            assert t['USB_bytes']==4096 and len(bytes.fromhex(t['returned_512_hex']))==512 and t['CSW_status']==0
    dma=load(OUT/'DMA-setup-cases.json')['cases'];assert len(dma)==2
    assert dma[0]['NDTR']==4096 and dma[1]['NDTR']==123 and all(c['result']==0 for c in dma)
    required=['findings.md','transfer-buffer-lifetime.md','failure-semantics.md','control-sector-strategy.md',
              'partial-dma-exhaustive.md','cross-sector-consistency.md','authenticated-read-plan.md']
    links=0
    for n in required:
        p=OUT/n;assert p.stat().st_size
        for targetpath in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
            assert Path(targetpath).exists() or Path(targetpath)==OUT/'validation.json',(n,targetpath);links+=1
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    assert (OUT/'findings.md').read_text(encoding='utf8').rstrip().endswith('MSD PHYSICAL READ AUTHENTICATION = UNQUALIFIED')
    result=dict(confidence='PROVEN',prior_Phase51_files_unchanged=preserved,pinned_reference_sources_unchanged=len(sources),
        exhaustive_target_prefix_lengths=513,short_target_prefixes_accepted=0,exact_512_prefix_accepted=True,
        independent_fault_placements=18,timeout_sequences_stopped_without_retry=6,
        native_command_traces=len(traces),DMA_setup_native_cases=2,local_links_checked=links,
        physical_outcomes_modeled=True,actual_replay_producer_established=False,
        hardware_access=False,MIDI_ports_opened=0,firmware_generated=False,firmware_modified=False,firmware_transmitted=False,
        authentication_answer='UNKNOWN',verdict='UNQUALIFIED')
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
