"""Validate phase29 evidence and earlier inputs. No builds or device access."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
checks=[]
def check(name,value):assert value,name;checks.append(name)
v28=read(R/'builds/phase28-hardware-readiness/validation.json')
check('phase28 evidence unchanged',all(digest(R/'builds/phase28-hardware-readiness'/n)==h for n,h in v28['evidence_sha256'].items()))
check('phase28 report preimage preserved',digest(O/'phase28-report-before.md')==v28['report_sha256'])
v27=read(R/'builds/phase27-qspi-read/validation.json')
check('phase27 evidence unchanged',all(digest(R/'builds/phase27-qspi-read'/n)==h for n,h in v27['evidence_sha256'].items()))
check('phase27 report unchanged',digest(R/'notes/qspi82000-read-diagnostic.md')==v27['report_sha256'])
v26=read(R/'builds/phase26-qspi82000/validation.json')
check('phase26 evidence unchanged',all(digest(R/'builds/phase26-qspi82000'/n)==h for n,h in v26['evidence_sha256'].items()))
check('range qualification unchanged',digest(R/'notes/p0282-0386-reclaim-qualification.md')==v26['qualification_note_sha256'])
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
check('451 recorded reference inputs unchanged',len(ref)==451 and all(digest(Path(n))==h for n,h in ref.items()))
pin=read(R/'plaits/upstream/source-manifest.json')['files']
check('183 pinned sources unchanged',len(pin)==183 and all(digest(R/'plaits/upstream'/x['path'])==x['sha256'] for x in pin))
r=read(O/'replay-result.json');c=r['cases'];a=read(O/'closure.json');obj=read(O/'objects.json')
check('eight scenario groups and explicit assertions',len(c)==8 and r['explicit_gate_assertions']==172)
check('normal queued path returns semaphore and exact output',c[0]['details']['state']['semaphore']==1 and c[0]['details']['frames']==9 and c[0]['details']['USB_bytes']==1784)
check('second request accepted only after first completes',c[1]['details']['callbacks']==2 and c[1]['details']['frames']==18)
check('busy semaphore belongs to prior owner',c[2]['details']['state']['status']==2 and c[2]['details']['state']['semaphore']==0 and not c[2]['details']['QSPI_commands'])
check('disconnected host does not cancel active DMA early',c[3]['details']['state']['phase']==0 and c[3]['details']['state']['semaphore']==1 and not c[3]['details']['frames'])
check('error failure retained',c[4]['details']['state']['phase']==1 and c[4]['details']['state']['semaphore']==0 and not c[4]['required_no_deadlock_gate'])
check('missing IRQ failure retained',c[5]['details']['state']['phase']==1 and c[5]['details']['state']['semaphore']==0 and not c[5]['required_no_deadlock_gate'])
check('preemption uncertainty not silenced',c[6]['real_scheduler_permits_this_interleaving']=='UNKNOWN' and c[6]['details']['state']['queued_bytes']==24)
check('negative fixed requests',c[7]['negative_cases']==150 and not c[7]['details']['reads'])
check('separate stack models',c[0]['details']['modeled_usage_from_aligned_top']['Main']==260 and c[0]['details']['modeled_usage_from_aligned_top']['Storage']==204)
check('separate guarded stack margins',c[0]['details']['remaining_bytes_to_low_guard']['Main']==2804 and c[0]['details']['remaining_bytes_to_low_guard']['Storage']==1068)
check('no output sleep or payload CPU overwrite',all(not x['details']['unexpected_sleep_calls'] and not x['details']['payload_CPU_writes'] for x in c))
check('heap cannot allocate payload',obj['heap_remaining_bytes']==240 and all(x['PC']=='0x801d7f4' and not x['allocation_returned'] for x in obj['allocation_attempts']))
check('selected call graph is bounded',len(a['selected_call_edges'])==92 and a['only_observed_QSPI_commands']==['0xec'])
check('no firmware/SYX/binary generated',not any(p.suffix.lower() in ('.bin','.syx','.hex') for p in O.rglob('*') if p.is_file()))
note=R/'notes/qspi82000-hardware-readiness.md'
check('report states rejected result',note.read_text(encoding='utf8').rstrip().endswith('QSPI STORAGE-WRAPPER CORRECTION = FAIL'))
result=dict(confidence='PROVEN',scope='Offline preservation and result consistency',checks=checks,
 replay_scenario_groups=8,replay_explicit_gate_assertions=172,validation_checks=len(checks),
 aggregate_canary_checks=sum(x['details']['canary_checks'] for x in c),
 aggregate_callee_saved_register_checks=sum(x['details']['callee_saved_register_checks']+x['details']['Storage_worker_callee_saved_checks'] for x in c),
 correction_verdict='FAIL',hardware_readiness='FAIL',
 gates={
  'H1':dict(confidence='UNKNOWN',decision='NOT PROVEN, unchanged'),
  'H2':dict(confidence='UNKNOWN',decision='NOT PROVEN, unchanged'),
  'H3':dict(confidence='UNKNOWN',decision='Both task bounds identified; complete maximum and physical payload allocation not qualified'),
  'H4':dict(confidence='PROVEN',decision='Normal task ownership corrected; required error/no-completion gate fails; real submission scheduling UNKNOWN'),
  'H5':dict(confidence='UNKNOWN',decision='Paced output passes bounded model; actual service registration/deadlines/audio unknown'),
  'H6':dict(confidence='PROVEN',decision='Selected fixed-request fixture read-only; no hardware/deployment claim')},
 physical_payload_buffer_qualified=False,reference_inputs_unchanged=451,pinned_files_unchanged=183,
 phase28_evidence_unchanged=True,phase28_report_before_sha256=digest(O/'phase28-report-before.md'),
 authorized_report_change='Append phase29 findings; original phase28 bytes archived unchanged',
 hardware_access=False,firmware_generated=False,SYX_generated=False,
 evidence_sha256={str(p.relative_to(O)):digest(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name!='validation.json'},report_sha256=digest(note))
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','evidence_sha256','gates')},indent=2))
