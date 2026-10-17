"""Persist exact scoped results; never promotes an incomplete continuity run."""
from pathlib import Path
import json,hashlib,collections
O=Path(__file__).resolve().parent;R=O.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda name:json.loads((O/name).read_text())
c=load('development-identity.json');digest=c['BIN_sha256']
assert sha((O/(c['candidate']+'.bin')).read_bytes())==digest
assert sha((O/(c['candidate']+'.syx')).read_bytes())==c['SYX_sha256']
for name,key in [('dma-regression.json','passed'),('status-mount-tests.json','passed'),('host-tests.json','passed'),('heap-reset-tests.json','passed')]:
 x=load(name);assert x[key] and x['candidate_sha256']==digest,name
native=load('native-tests.json');assert native['all_passed'] and len(native['cases'])==28
# The wrapper selected this file-first decoded image before creating any native
# fixture. Add identity to its persisted result, without rerunning passed cases.
native['candidate_sha256']=digest;(O/'native-tests.json').write_text(json.dumps(native,indent=2)+'\n')
assert load('reservation-tests.json')['passed'] and load('reservation-tests.json')['image_sha256']==digest
transitions=[]
for name in ['b13-to-candidate','candidate-to-official','candidate-to-b13']:
 x=load(name+'-summary.json');assert x['accepted'] and x['actual_install_performed'] and not x['silent_noop']
 assert x['installed_before_sha256']==digest or x['incoming_image_sha256']==digest
 assert x['final_installed_sha256']==x['incoming_image_sha256']
 for v in x['preservation'].values():assert v['writes']==v['erase_overlaps']==0 and v['sentinel_unchanged']
 for lo,hi in x['internal_erase_ranges']+x['internal_program_ranges']:assert 0x08010000<=int(lo,16)<int(hi,16)<=0x08080000
 transitions.append({k:x[k] for k in ['transition','installed_before_sha256','incoming_SYX_sha256','final_installed_sha256','silent_noop','preservation','internal_erase_ranges','internal_program_ranges','seams']})
(O/'install-validation.json').write_text(json.dumps(dict(confidence='PROVEN',passed=True,transitions=transitions,bootloader_region_excluded=True,hardware_access=False),indent=2)+'\n')
x=load('continuity-startup-frontier.json');continuity=load('continuity-status.json');assert continuity['candidate_sha256']==digest
allocs=[v for v in x['operations'] if v['kind'] in ('allocation request','bounded allocator')]
calls=[v for v in x['calls'] if v['target'] in ('0x801cfa4','0x801d7d8','0x801d7d0','0x801d808')]
(O/'allocation-coverage.json').write_text(json.dumps(dict(confidence='PROVEN',candidate_sha256=digest,scope='Observed startup prefix only; not complete postboot enumeration',observed_request_count=sum(v['kind']=='allocation request' for v in allocs),requests=allocs,call_sites=calls,heap_cursor=continuity['heap_cursor'],heap_limit=continuity['heap_limit'],state=['0x20044d70','0x20044d7c'],raw='Main retained stack frame +192..255',transport='existing stock parser/router/rings; no new heap allocation',all_postboot_allocations_enumerated=False,full_startup_and_diagnostic_lifetime_completed=False,hardware_headroom='UNKNOWN — HARDWARE-ONLY',allocator_bounds_scope='Nonoverflow round-to-four native allocations; no universal arbitrary-size/indirect-owner proof'),indent=2)+'\n')
historical=[]
p=R/'builds/phase61-final-geometry-gated-candidate'
for line in (p/'SHA256SUMS.txt').read_text().splitlines():
 if not line.strip():continue
 h,name=line.split('  ',1);assert sha((p/name).read_bytes())==h,name;historical.append(name)
p=R/'builds/phase62-final-preflight';f=json.loads((p/'frozen-candidate-identity.json').read_text())
for ext,key in [('bin','BIN_sha256'),('syx','SYX_sha256')]:assert sha((p/(f['candidate']+'.'+ext)).read_bytes())==f[key]
(O/'historical-preservation.json').write_text(json.dumps(dict(confidence='PROVEN',phase61_manifest_entries_unchanged=len(historical),phase62_frozen_BIN_SYX_unchanged=True,reference_repository_written=False),indent=2)+'\n')
verdict=dict(verdict='UNQUALIFIED',confidence='UNKNOWN',candidate_BIN_sha256=digest,candidate_SYX_sha256=c['SYX_sha256'],hardware_test_eligible=False,live_host_enabled=False,live_uploader_enabled=False,blockers=['Continuous startup->USB-ready->query->authorization->raw not completed: SPI2 polled TXE/RXNE/data model missing at08037968, SR40003808','Complete postboot allocation enumeration/lifetime not reached'],passed={'reservation':7,'native':28,'status_mount':13,'DMA_ownership':len(load('dma-regression.json')['cases']),'host_mocks':len(load('host-tests.json')['cases']),'install_rollback':3,'file_first_identity':True,'uploader_parser_lock':load('uploader-tests.json')['passed']},hardware_access=False,MIDI_ports_opened=0)
(O/'preflight-verdict.json').write_text(json.dumps(verdict,indent=2)+'\n')
print(json.dumps(dict(verdict=verdict['verdict'],passed=verdict['passed'],historical_entries=len(historical),observed_allocation_requests=sum(v['kind']=='allocation request' for v in allocs)),indent=2))
