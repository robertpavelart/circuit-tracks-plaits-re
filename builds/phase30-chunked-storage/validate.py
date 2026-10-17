"""Evidence consistency/preservation, physical-only addressing, no device I/O."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(n,v):assert v,n;checks.append(n)
for phase in ('phase27-qspi-read','phase28-hardware-readiness','phase29-storage-wrapper'):
 p=R/'builds'/phase;v=read(p/'validation.json')
 check(phase+' evidence unchanged',all(sha(p/n)==h for n,h in v['evidence_sha256'].items()))
v29=read(R/'builds/phase29-storage-wrapper/validation.json')
check('phase29 report archived unchanged',sha(O/'phase29-report-before.md')==v29['report_sha256'])
v27=read(R/'builds/phase27-qspi-read/validation.json')
check('phase27 note unchanged',sha(R/'notes/qspi82000-read-diagnostic.md')==v27['report_sha256'])
v26=read(R/'builds/phase26-qspi82000/validation.json');p=R/'builds/phase26-qspi82000'
check('phase26 unchanged',all(sha(p/n)==h for n,h in v26['evidence_sha256'].items()))
check('reclaim qualification unchanged',sha(R/'notes/p0282-0386-reclaim-qualification.md')==v26['qualification_note_sha256'])
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
check('451 recorded reference inputs unchanged',len(ref)==451 and all(sha(Path(n))==h for n,h in ref.items()))
pins=read(R/'plaits/upstream/source-manifest.json')['files']
check('183 pinned files unchanged',len(pins)==183 and all(sha(R/'plaits/upstream'/p['path'])==p['sha256'] for p in pins))
r=read(O/'replay-result.json');a=read(O/'ownership-and-error-audit.json');cases=r['cases']
check('12 scenario groups / 37 explicit assertions',r['scenario_groups']==12 and len(r['checks'])==37)
normal=cases[0]['details']
check('eight exact addresses and 64-byte lengths',[x['address'] for x in normal['reads']]==[hex(0x82000+i*64) for i in range(8)] and all(x['length']==64 for x in normal['reads']))
check('one physical parser-owned payload',all(x['destination']=='0x2000a070' for x in normal['reads']) and normal['input_capacity']==360)
check('exact synthetic host reconstruction',normal['reconstruction']['exact_concatenation'] and normal['reconstruction']['bytes']==512 and normal['reconstruction']['sha256']==sha(R/'builds/phase27-qspi-read/synthetic-data.bin'))
check('nine frames / 1784 USB bytes',normal['frames']==9 and normal['USB_bytes']==1784 and normal['USB_transfers']==33)
check('normal semaphore/request released',normal['state']['semaphore']==1 and normal['state']['sync']==0 and normal['state']['queue_bytes']==0 and normal['state']['buffer_reusable'])
check('stock synchronous second notification tested',cases[1]['details']['reconstruction']['exact_concatenation'])
faults=[c for c in cases if c['case'].startswith(('tef on','missing on'))]
check('six retained failure regressions',len(faults)==6 and all(not c['bounded_recovery'] for c in faults))
check('errors not falsely unwound',all(c['details']['state']['semaphore']==0 and c['details']['state']['sync']==1 and not c['details']['state']['buffer_reusable'] and c['details']['state']['active_chunk'] in (0,4,7) for c in faults))
check('actual indefinite Storage wait observed',all(c['details']['last_waits']['Storage']['timeout_argument']=='0xffffffff' for c in faults))
busy=next(c['details'] for c in cases if c['case'].startswith('backend busy'))
check('busy owner not force-released by diagnostic',busy['after_failure_before_second_request']['semaphore']==0 and busy['after_failure_before_second_request']['sync']==0 and busy['after_failure_before_second_request']['buffer_reusable'])
disconnect=next(c['details'] for c in cases if c['case'].startswith('host disappears'))
check('disconnect after chunk3 no DMA leak',disconnect['after_failure_before_second_request']['frames']==4 and disconnect['after_failure_before_second_request']['semaphore']==1 and disconnect['after_failure_before_second_request']['sync']==0)
check('second successes after recoverable exits',busy['reconstruction']['exact_concatenation'] and disconnect['reconstruction']['exact_concatenation'])
check('selected QSPI operations read-only',a['QSPI_commands']==['0xec'] and all(v=='0xec' for c in cases for v in c['details']['QSPI_commands']))
check('live Main frame and physical stack margins',normal['Main_frame']=='0x200081e8' and normal['stack_usage']['Main']==524 and normal['headroom_to_guard']['Main']==2540 and normal['stack_usage']['Storage']==204 and normal['headroom_to_guard']['Storage']==1068)
check('no nonphysical memory or hardware access',not r['nonphysical_RAM_used'] and not r['hardware_access'] and all(not c['details']['nonphysical_memory_mapped'] for c in cases))
check('returning exits restore shared stock input',all(c['details']['stock_input_restored'] for c in cases if c['details']['state']['Main_returned']))
check('no early CPU overwrite of raw payload',all(c['details']['raw_CPU_writes']==0 for c in cases))
check('normal native CRC/packet reads cover eight chunks',normal['raw_CPU_reads']==1024 and normal['raw_region_restoration_writes']==64)
check('real B1.3 reservation leaves four bytes',a['heap']['after_B13_reservation']['available']==4 and a['heap']['64_byte_attempt_after_reservation']['PC']=='0x801d7f4' and a['heap']['64_bytes_before_reservation']['retained_feature_state_return']=='0x0')
check('no new persistent heap allocation',a['new_RAM']['new_heap_bytes']==0 and a['new_RAM']['new_persistent_global_bytes']==0 and a['new_RAM']['command_frame_bytes']==188)
check('no firmware/SYX/binary output',not any(p.suffix.lower() in ('.bin','.syx','.hex') for p in O.rglob('*') if p.is_file()))
note=R/'notes/qspi82000-hardware-readiness.md'
check('report ends with required unqualified verdict',note.read_text(encoding='utf8').rstrip().endswith('QSPI CHUNKED READ ARCHITECTURE = UNQUALIFIED'))
result=dict(confidence='PROVEN',scope='Offline consistency, ownership bounds and preservation; not hardware admission',
 validation_checks=len(checks),checks=checks,replay_explicit_assertions=37,scenario_groups=12,
 guard_rounds=sum(c['details']['guard_checks'] for c in cases),callee_saved_comparisons=sum(c['details']['callee_saved_checks'] for c in cases),
 verdict='UNQUALIFIED',gates={
  'B1':dict(confidence='STRONG INFERENCE',finding='Physical stock allocation and serialized lifetime proven in fixture; concurrent hardware workload unqualified'),
  'B2':dict(confidence='PROVEN',finding='Eight fixed 64-byte reads complete normally'),
  'B3':dict(confidence='PROVEN',finding='Exact synthetic reconstruction'),
  'B4':dict(confidence='PROVEN',finding='TEF injection fails to unwind'),
  'B5':dict(confidence='UNKNOWN',finding='No stock-compatible bounded recovery qualified'),
  'B6':dict(confidence='UNKNOWN',finding='Busy/disconnect retries succeed; TEF/missing completion remain active'),
  'B7':dict(confidence='UNKNOWN',finding='Physical RAM and modeled stack depths established; full worst cases not qualified'),
  'B8':dict(confidence='PROVEN',finding='Selected diagnostic read-only'),
  'H3':dict(confidence='UNKNOWN',finding='Complete stack/DMA suitability unqualified'),
  'H4':dict(confidence='UNKNOWN',finding='Normal ownership correct; bounded recovery absent'),
  'H5':dict(confidence='UNKNOWN',finding='Yield/drain tested, but Main held inside handler and ingress/audio workload unqualified'),
  'H6':dict(confidence='PROVEN',finding='Fixed diagnostic path read-only')},
 H1_H2='NOT PROVEN, unchanged; not investigated in phase30',physical_payload='0x2000a070..0x2000a0af',new_heap_bytes=0,
 Main_stack_used=524,Main_guard_headroom=2540,Storage_stack_used=204,Storage_guard_headroom=1068,
 reference_inputs_unchanged=451,pinned_sources_unchanged=183,prior_evidence_unchanged=True,
 hardware_access=False,firmware_generated=False,SYX_generated=False,nonphysical_RAM_used=False,
 prior_report_sha256=sha(O/'phase29-report-before.md'),report_sha256=sha(note),
 evidence_sha256={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name!='validation.json'})
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','gates','evidence_sha256')},indent=2))
