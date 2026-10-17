"""Evidence ledger for the incomplete Layout A coupled qualification."""
import json,re
from environment import ROOT,REF,sha
OUT=ROOT/'builds/phase20j-coupled-replay'
old=json.loads((ROOT/'builds/phase20i-authentic-qualification/provenance.json').read_text())
changed=[p for p,h in old['reference_before'].items() if sha(__import__('pathlib').Path(p).read_bytes())!=h]
assert not changed,changed
checks={}
for name in ['address-probe','modulo-probe','reject-unknown','reject-unbacked','reject-branch','reject-inner-do','reject-pwrite','reject-deadlock']:
 t=(OUT/name/'output.txt').read_text();checks[name]=dict(output_sha256=sha(t.encode()),output=t)
sync=json.loads((OUT/'sync-primitives/result.json').read_text())
base=(OUT/'original-8/output.txt').read_text()
assert 'UNKNOWN_EXTERNAL_READ' in base and 'addr=173000' in base
assert sync['passed'] is False and sync['exact_gather_at_stock_wait_return']==1
assert sync['exact_gather_after_additional_service']==8192 and sync['exact_ring_blocks']==8192
gates={
 'L1':('STRONG INFERENCE','Pinned AGU tests and implemented 16-bit external model work at tested addresses; complete DSP56724 physical decoding remains unqualified.'),
 'L2':('UNKNOWN','Actual dual programs run; synthetic rapid publication exposes stale progress. Full workload blocked at first unknown wavetable read.'),
 'L3':('UNKNOWN','Zero complete audio blocks; first block aborts before final master output.'),
 'L4':('UNKNOWN','No new coupled active Synth1 comparison.'),
 'L5':('UNKNOWN','No new coupled active Synth2 comparison.'),
 'L6':('UNKNOWN','No new coupled drum comparison.'),
 'L7':('UNKNOWN','No new coupled retained MIDI comparison.'),
 'L8':('UNKNOWN','No new coupled mixer/Master FX comparison.'),
 'L9':('UNKNOWN','Eventual primitive data and ring outputs exact, but immediate-completion regression fails.'),
 'L10':('UNKNOWN','Guard tests pass, including inside recursive DO. No complete Layout A audio replay.'),
 'L11':('UNKNOWN','8192 primitive iterations, not 8192 complete audio blocks.'),
 'L12':('UNKNOWN','Authentic external stock synth lookup payload absent; delay zero initialization is derived from executed boot.')}
r=dict(reference_files_verified_unchanged=len(old['reference_before']),checks=checks,synchronization=sync,baseline=dict(output=base,complete_audio_blocks=0,attempted_block=0,peak=None,RMS=None,nonzero_sample_count=None,first_nonzero_block=None,final_master=None),gates=gates,budget='UNQUALIFIED',next_required_artifact='Authenticated external DSP lookup fixture for the stock patch, beginning with X:173000..174FFF, with original address/width/loading provenance; rerun first real stock block before expanding.')
(OUT/'qualification.json').write_text(json.dumps(r,indent=2)+'\n')
inventory={}
for p in OUT.rglob('*'):
 if p.is_file() and p.name!='artifact-hashes.json':inventory[str(p.relative_to(OUT))]=dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
(OUT/'artifact-hashes.json').write_text(json.dumps(inventory,indent=2)+'\n')
print(json.dumps(dict(reference_unchanged=r['reference_files_verified_unchanged'],synchronization=sync,baseline=r['baseline'],budget=r['budget']),indent=2))
