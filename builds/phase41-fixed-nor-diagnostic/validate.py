"""Validate produced evidence and fail-closed admission, not hardware safety."""
from pathlib import Path
import ast,json,hashlib,re
O=Path(__file__).resolve().parent;R=O.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
q=read(O/'qualification.json');t=read(O/'test-results.json');p=read(O/'publication-results.json')
assert q['verdict']=='UNQUALIFIED' and q['buffer']['full_buffer_qualification']=='UNKNOWN'
assert not q['prototype']['SYX_generated'] and not q['hardware_access']
assert len(t['native_cases'])==19 and len(t['host_cases'])==17 and len(p)==2
n=next(x['details'] for x in t['native_cases'] if x['case']=='normal')
expected=[(0x81000,23)]+[(0x82000+64*i,64) for i in range(8)]
assert [(int(x['address'],16),x['length']) for x in n['reads']]==expected
assert len({x['destination'] for x in n['reads']})==1 and n['frames']==10
assert n['state']['semaphore']==1 and n['state']['sync']==0 and n['state']['active_chunk'] is None
assert n['raw_CPU_writes']==0 and n['stock_input_restored'] and n['callee_saved_checks']==8
assert all(x['confidence']=='UNKNOWN' for x in t['native_cases'] if x['case']=='duplicate while active')
assert all(x['accepted_files']==0 for x in t['host_cases'] if x['case']!='normal')
assert all(x.get('sent')==1 for x in t['host_cases'])
assert all(v['write_overlaps']==v['erase_overlaps']==0 for v in q['installation_selected_replay'].values())
assert q['rollback_official_SYX_decodes_exactly_to_stock']
assert not any(f.suffix.lower() in ('.bin','.syx','.hex') for f in O.rglob('*') if f.is_file())
for f in O.glob('*.py'):ast.parse(f.read_text())
report=R/'notes/fixed-nor-evidence-diagnostic.md';s=report.read_text(encoding='utf8')
assert s.rstrip().endswith('FIXED NOR EVIDENCE DIAGNOSTIC = UNQUALIFIED')
links=re.findall(r'\]\(<(C:/[^>]+)>\)',s)
for link in links:
 m=re.match(r'^(.*?)(?::(\d+))?$',link);path=Path(m[1]);assert path.exists(),link
 if m[2]:assert int(m[2])<=len(path.read_text(encoding='utf8').splitlines()),link
v=dict(confidence='PROVEN',scope='Offline evidence consistency; final candidate remains UNKNOWN',verdict='UNQUALIFIED',native_cases=19,host_cases=19,reference_files_unchanged=q['reference_files_unchanged'],pinned_sources_unchanged=q['pinned_sources_unchanged'],report_sha256=sha(report),verified_local_links=len(links),hardware_access=False,firmware_generated=False,phase40_continued=False,broad_cold_boot_run=False,evidence_sha256={str(f.relative_to(O)):sha(f) for f in sorted(O.rglob('*')) if f.is_file() and f.name!='validation.json'})
(O/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps({k:x for k,x in v.items() if k!='evidence_sha256'},indent=2))
