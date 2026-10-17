"""File-first consistency checks; no peripheral, firmware writer or MIDI APIs."""
from pathlib import Path
import hashlib,json,sys
O=Path(__file__).resolve().parent
load=lambda n:json.loads((O/n).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if '--manifest' in sys.argv:
 rows=(O/'SHA256SUMS.txt').read_text().splitlines()
 for row in rows:
  h,n=row.split('  ',1);assert sha(O/n)==h,n
 print('Phase64 manifest verified',len(rows));raise SystemExit
x=load('continuity.json');proof=load('peer-contract-proof.json');v=load('preflight-verdict.json')
assert v['verdict']=='UNQUALIFIED' and not v['hardware_test_eligible']
assert v['candidate_BIN_sha256']==x['candidate_sha256']
assert sha(O/'loaded-core0.be24')==proof['program_sha256']
assert sha(O/'peer-mailbox-observed-output.txt')==proof['native_output_sha256']
assert proof['completed_exact_jobs']=={'080002':1,'094403':327,'0a8804':327,'0bcc05':327}
assert len(load('model-tests.json')['cases'])==4
assert len(load('peer-tests.json')['cases'])==11
assert x['frontier']['type']=='UnknownPeerRead' and '200100' in x['frontier']['message']
assert x['record']=='110000000180003480908f01'
assert x['heap_limit']=='0x20044d70'
assert len(x['SPI2']['accessors'])==31
assert load('identity-preservation.json')['phase63_manifest_entries_unchanged']==199
assert not load('allocation-prefix.json')['complete_postboot_coverage']
assert not any(load('milestones.json')[k] for k in ('USB_ready','geometry_query','authorization','raw_capture_start'))
result=dict(confidence='PROVEN',saved_file_consistency=True,register_cases=4,peer_cases=11,original_candidate_unchanged=True,accepted_continuity='same-state prefix through four procedural DSP jobs; stops at first unsupported16-bit width transition',complete_startup_and_postboot_allocations='UNKNOWN',verdict='UNQUALIFIED')
(O/'final-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
