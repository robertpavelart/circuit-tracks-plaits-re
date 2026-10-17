"""Persist bounded Phase65 evidence; no images or external connections."""
from pathlib import Path
import json,hashlib,struct,collections
O=Path(__file__).resolve().parent;R=O.parents[1]
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
preserved={}
for name in ('phase63-defect-closure','phase64-spi2-model-closure'):
 d=R/'builds'/name;rows=(d/'SHA256SUMS.txt').read_text().splitlines()
 for row in rows:
  h,n=row.split('  ',1);assert sha(d/n)==h,(name,n)
 preserved[name]=len(rows)
x=load(O/'continuity.json');s=load(O/'shi-evidence.json');a=load(O/'audit-identity.json')
assert x['candidate_sha256']==a['candidate_sha256']
assert x['frontier']['pc']=='0x8048316' and x['frontier']['type']=='UcError'
assert x['registers']['r0']=='0x40040000'
assert x['record']=='110000000180003480908f01'
dm=[r for r in s['DMAs'] if r.get('words')==256 and not r['command']]
assert len(dm)==144 and all(r['bytes']==512 and r['width']==2 and r['pointer']=='0xc00' and r['end']=='0xd00' for r in dm)
assert all(r['sha256']==hashlib.sha256(bytes(512)).hexdigest() for r in dm)
restores=[r for r in s['DMAs'] if r['command'] and r['bytes']==2]
assert len(restores)==144
posted=[];completed=[];active=None
for row in s['log']:
 if row['event']=='mailbox job':
  if active is not None:raise AssertionError('new job before preceding observed idle')
  posted.append(row['word']);active=row['word']
 if row['event']=='SHI read' and row['space']=='Y' and row['address']=='0x2c' and row['value']=='0x800000' and active is not None:
  completed.append(active);active=None
assert len(posted)==148 and len(completed)==147 and active=='0x212c00'
neg=load(O/'negative-tests.json');assert neg['passed'] and len(neg['cases'])==7
inc=load(O/'incomplete-transfer/negative-result.json')
assert inc['passed'] and inc['TX_remaining']==inc['RX_remaining']==2 and inc['TX_EN']==inc['RX_EN']==1 and len(inc['mailbox_jobs'])==4
prefixalloc=[r for r in x['operations'] if r['kind']=='allocation request']
old=load(R/'builds/phase64-spi2-model-closure/continuity.json')
oldalloc=[r for r in old['operations'] if r['kind']=='allocation request']
assert prefixalloc[:len(oldalloc)]==oldalloc
later=prefixalloc[len(oldalloc):]
ram=(O/'frontier-sram.bin').read_bytes()
word=lambda at:struct.unpack_from('<I',ram,at-0x20000000)[0]
assert word(0x20002b44)==0x20044d70 and word(0x20002b48)==int(x['heap_cursor'],16)
(O/'allocation-prefix.json').write_text(json.dumps(dict(confidence='PROVEN',candidate_sha256=x['candidate_sha256'],total_requests=len(prefixalloc),previous_requests=len(oldalloc),new_requests=len(later),new_request_details=later,all_request_details=prefixalloc,heap_cursor=x['heap_cursor'],heap_limit=x['heap_limit'],complete_postboot_coverage=False,raw_buffer_live=False,transport_session_started=False,record=x['record'],scope='Observed requests through USB initialization only; prior bounded allocator/stack ownership tests remain scoped evidence, not full lifetime enumeration'),indent=2)+'\n')
milestones=[r for r in x['events'] if 'milestone' in r or r.get('event')=='first scheduler architectural launch boundary']
(O/'milestones.json').write_text(json.dumps(dict(confidence='PROVEN',milestones=milestones,SHI_uploads=144,mailbox_posts=148,observed_mailbox_idle_completions=147,final_unobserved_job=active,at_USB_init_record=x['record'],USB_ready=False,geometry_query=False,authorization=False,raw_capture_start=False,no_intermediate_ARM_fixture_splice=True),indent=2)+'\n')
result=dict(confidence='UNKNOWN',verdict='UNQUALIFIED',SHI_specific_subset='PROVEN in stated model:144 actual512-byte transfers,24-bit restore,native DSP service',native_job_posts=len(posted),native_idle_completions_observed=len(completed),final_job_completion='UNKNOWN before USB frontier',continuous_path='PROVEN prefix; UNKNOWN USB-ready through raw capture',postboot_allocations='UNKNOWN beyond USB initialization',stop_category='B — new USB peripheral-model gap',USB_access=dict(instruction='0x08048316',base='0x40040000',offset=8,read_address='0x40040008',operation='read GAHBCFG then clear bit0/globalinterrupt enable',MMIO_in_emulator_map=False),new_firmware_defect_demonstrated=False,candidate_modified=False,firmware_generated=False,hardware_access=False,MIDI_access=False,transmission=False,prior_manifest_files_verified=preserved,negative_checks=8,full_postboot_safety_proof=False)
(O/'preflight-verdict.json').write_text(json.dumps(result,indent=2)+'\n')
(O/'preservation.json').write_text(json.dumps(dict(confidence='PROVEN',prior_manifests=preserved,candidate_BIN_sha256=x['candidate_sha256'],candidate_SYX_sha256=sha(R/'builds/phase63-defect-closure/circuittracks-nor-defect-closure-development.syx'),reference_repository_modified=False,candidate_modified=False),indent=2)+'\n')
(O/'transfer-summary.json').write_text(json.dumps(dict(confidence='PROVEN',coefficient_DMAs=dm,restore_commands=len(restores),posted_jobs=posted,observed_completed_jobs=completed,last_completion_unknown=active,native_turns=s['native_turns'],input_provenance='synthetic zero NOR payloads; not current-unit authenticated bytes',normal_instructions=x['executed_instructions'],new_allocation_requests=len(later)),indent=2)+'\n')
print(json.dumps(dict(verdict=result['verdict'],uploads=len(dm),posts=len(posted),observed_completed=len(completed),allocations=len(prefixalloc),new_allocations=len(later),heap=x['heap_cursor'],preserved=preserved),indent=2))
