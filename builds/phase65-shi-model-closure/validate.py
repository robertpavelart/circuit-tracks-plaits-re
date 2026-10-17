"""File-first result consistency and immutable input identity checks."""
from pathlib import Path
import hashlib,json,sys
O=Path(__file__).resolve().parent;R=O.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
if '--manifest' in sys.argv:
 rows=(O/'SHA256SUMS.txt').read_text().splitlines()
 for row in rows:
  h,n=row.split('  ',1);assert sha(O/n)==h,n
 print('Phase65 manifest verified',len(rows));raise SystemExit
for n in ('loaded-core0.be24','loaded-core1.be24'):
 assert sha(O/n)==sha(R/'builds/phase64-spi2-model-closure'/n)
x=load(O/'continuity.json');a=load(O/'allocation-prefix.json');v=load(O/'preflight-verdict.json');t=load(O/'transfer-summary.json')
assert v['verdict']=='UNQUALIFIED' and not v['full_postboot_safety_proof']
assert x['frontier']['pc']=='0x8048316' and x['registers']['r0']=='0x40040000'
assert x['record']==a['record']=='110000000180003480908f01'
assert a['total_requests']==298 and a['new_requests']==122 and not a['complete_postboot_coverage']
assert a['heap_cursor']=='0x20011334' and a['heap_limit']=='0x20044d70'
assert len(t['coefficient_DMAs'])==144 and t['restore_commands']==144
assert len(t['posted_jobs'])==148 and len(t['observed_completed_jobs'])==147 and t['last_completion_unknown']=='0x212c00'
inc=load(O/'incomplete-transfer/negative-result.json')
assert inc['passed'] and inc['native_wait_visits']==256 and inc['TX_remaining']==inc['RX_remaining']==2
assert inc['TX_EN']==inc['RX_EN']==1 and not inc['completion_delivered']
assert load(O/'negative-tests.json')['passed']
assert not (O/'native-dsp-error.txt').read_text().strip()
script=(O/'native-dsp-job.txt').read_text().splitlines()
assert [s for s in script if s.startswith('PC ')]==['PC 100','PC 107']
assert not any(s.startswith('P ') for s in script),'host program patch in native DSP transcript'
assert 'FLOW 1' in script
output=(O/'native-dsp-output.txt').read_text()
assert '0 X 000012: 000100' in output and '0 X 000012: 000000' in output
assert not any(p.suffix.lower() in ('.syx',) for p in O.rglob('*'))
result=dict(confidence='PROVEN',saved_evidence_consistent=True,unchanged_DSP_programs=True,normal_observer_corrected=True,coefficient_uploads=144,job_posts=148,observed_completions=147,negative_checks=8,new_allocation_requests=122,continuous_startup_complete=False,postboot_allocations_complete=False,firmware_change=False,verdict='UNQUALIFIED')
(O/'final-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
