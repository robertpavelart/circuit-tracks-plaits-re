"""Read-only checks of saved evidence and package; writes this folder's receipts only."""
from pathlib import Path
import hashlib,json
O=Path(__file__).resolve().parent
P=O.parent/'final-hardware-test-package'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checked=[]
for line in (P/'HASHES.txt').read_text(encoding='utf-8').splitlines():
    if not line or line.startswith('#'):continue
    digest,name=line.split('  ',1)
    p=(P/name).resolve()
    assert p.is_relative_to(P.resolve()) and p.is_file()
    assert sha(p)==digest,name
    checked.append(name)
candidate=sha(P/'circuittracks-nor-defect-closure-development.bin')
r=json.loads((O/'reachability.json').read_text())
j=json.loads((O/'joint-results.json').read_text())
assert r['candidate_sha256']==j['candidate_sha256']==candidate
assert r['conclusion']=='D' and not r['complete']
assert len(j['cases'])==36 and j['passed'] and all(x['passed'] for x in j['cases'])
assert j['hardware_access'] is False
assert any(int(x['pc'],16)==0x8022e22 and x['classification']=='UNKNOWN' for x in r['indirect_sites'])
for name in ('findings.md','allocation-closure.md','usb-joint-closure.md'):
    assert (O/name).is_file()
result=dict(candidate_sha256=candidate,package_manifest_entries_verified=len(checked),
    package_manifest_sha256=sha(P/'HASHES.txt'),
    frozen_package_unchanged=True,new_joint_cases=36,new_joint_cases_passed=36,
    roots=len(r['roots']),instruction_nodes=r['instruction_nodes'],
    indirect_sites=len(r['indirect_sites']),
    unresolved_indirect_sites=sum(x['classification']=='UNKNOWN' for x in r['indirect_sites']),
    allocation_conclusion='D',allocation_verdict='UNQUALIFIED',
    usb_joint_verdict='PASS within declared initialized normal-host/model scope',
    operational_preflight='UNQUALIFIED',live_tools_unlocked=False,
    verification_scope='Saved results/byte binding/package integrity only; does not rerun closed tests or operate devices')
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
files=sorted(p for p in O.iterdir() if p.is_file() and p.name!='SHA256SUMS.txt')
(O/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files))
print(json.dumps(result,indent=2))
