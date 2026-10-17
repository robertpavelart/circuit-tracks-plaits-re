"""Validate this static-analysis evidence and immutable package binding only."""
from pathlib import Path
import hashlib,json,csv
O=Path(__file__).resolve().parent
P=O.parent/'final-hardware-test-package'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
candidate=sha(P/'circuittracks-nor-defect-closure-development.bin')
expected='edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9'
assert candidate==expected
count=0
for line in (P/'HASHES.txt').read_text(encoding='utf-8').splitlines():
    if not line or line.startswith('#'):continue
    digest,name=line.split('  ',1);p=(P/name).resolve()
    assert p.is_relative_to(P.resolve()) and sha(p)==digest,name
    count+=1
r=json.loads((O/'resolution.json').read_text())
f=json.loads((O/'allocator-failure.json').read_text())
assert r['candidate_sha256']==f['candidate_sha256']==candidate
assert r['verdict']=='UNQUALIFIED' and not r['complete']
assert len(r['content_targets'])==7 and len(r['secondary_timer_publishers'])==17
assert all(x['callback']!='UNKNOWN' for x in r['secondary_timer_publishers'])
assert len(f['cases'])==4 and f['passed']
assert not r['allocator_endpoints']
assert len(r['indirect_sites'])==260
assert sum(x['status']=='UNKNOWN' for x in r['indirect_sites'])==233
assert len(r['target_summaries'])==73
for t in ('0x803c90c','0x803c968','0x803c9a8'):
    assert r['content_summaries'][t]['classification']=='UNKNOWN'
with (O/'indirect-ledger.csv').open(newline='') as h:assert len(list(csv.DictReader(h)))==260
assert (O/'findings.md').read_text().rstrip().endswith('POST-READY ALLOCATION CENSUS = UNQUALIFIED')
result=dict(candidate_sha256=candidate,package_hash_entries_verified=count,
    package_unchanged=True,firmware_modified=False,
    content_publisher_targets=r['content_targets'],content_global_alias_closure='not universal; normal publisher types only',
    secondary_timer_publishers=17,summarized_callback_targets=73,
    indirect_sites=260,unresolved_indirect_sites=233,
    resolved_edge_allocator_endpoints=0,complete_allocator_absence_proof=False,
    allocator_ABI_cases=4,allocator_ABI_cases_passed=4,
    physical_BKPT_routing='UNKNOWN; not emulated',
    allocation_verdict='UNQUALIFIED',USB_joint_path='prior PASS preserved; not rerun',
    hardware_access=False,MIDI_access=False,transmission=False)
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
files=sorted(x for x in O.iterdir() if x.is_file() and x.name!='SHA256SUMS.txt')
(O/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files))
print(json.dumps(result,indent=2))
