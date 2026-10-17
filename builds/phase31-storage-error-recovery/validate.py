"""Phase31 evidence assertions plus prior/reference/pinned preservation."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(n,v):assert v,n;checks.append(n)
for phase in ('phase26-qspi82000','phase27-qspi-read','phase28-hardware-readiness','phase29-storage-wrapper','phase30-chunked-storage'):
 p=R/'builds'/phase;v=read(p/'validation.json')
 ck(phase+' evidence unchanged',all(sha(p/n)==h for n,h in v['evidence_sha256'].items()))
v30=read(R/'builds/phase30-chunked-storage/validation.json')
ck('phase30 report archive exact',sha(O/'phase30-report-before.md')==v30['report_sha256'])
ck('earlier report text unchanged',(R/'notes/qspi82000-hardware-readiness.md').read_bytes().startswith((O/'phase30-report-before.md').read_bytes()))
v27=read(R/'builds/phase27-qspi-read/validation.json')
ck('phase27 note unchanged',sha(R/'notes/qspi82000-read-diagnostic.md')==v27['report_sha256'])
v26=read(R/'builds/phase26-qspi82000/validation.json')
ck('reclaim qualification unchanged',sha(R/'notes/p0282-0386-reclaim-qualification.md')==v26['qualification_note_sha256'])
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
ck('451 reference inputs unchanged',len(ref)==451 and all(sha(Path(n))==h for n,h in ref.items()))
pins=read(R/'plaits/upstream/source-manifest.json')['files']
ck('183 pinned files unchanged',len(pins)==183 and all(sha(R/'plaits/upstream'/p['path'])==p['sha256'] for p in pins))
r=read(O/'fault-replay.json');a=read(O/'stock-path-audit.json')
ck('44 replay assertions',len(r['checks'])==44)
ck('six exact fault cases',{(x['kind'],x['chunk']) for x in r['cases']}=={(k,c) for k in ('tef','missing') for c in (0,4,7)})
ck('128 more ticks and native feeds each',all(x['additional_ticks']==128 and x['idle_callback_invocations']==128 and len(x['watchdog_writes'])==128 for x in r['cases']))
ck('no resource state changed',all(x['before']==x['after'] for x in r['cases']))
ck('semaphore and buffer remain owned',all(x['after']['semaphore']==0 and x['after']['sync']==1 and not x['after']['buffer_reusable'] and not x['after']['Main_returned'] for x in r['cases']))
ck('actual infinite wait in every fault',all(x['details']['last_waits']['Storage']['timeout_argument']=='0xffffffff' for x in r['cases']))
ck('no unsafe release or second read',not r['forced_release'] and not r['second_read_after_fault'])
normal=r['normal_then_second_normal']
ck('two normal requests / 16 reads / 18 frames',len(normal['reads'])==16 and normal['frames']==18 and normal['reconstruction']['exact_concatenation'])
ck('all selected commands are reads',all(v=='0xec' for x in r['cases'] for v in x['details']['QSPI_commands']) and set(normal['QSPI_commands'])=={'0xec'})
ck('no CPU overwrite',all(x['details']['raw_CPU_writes']==0 for x in r['cases']))
ck('75 verified selected direct sites',sum(map(len,a['verified_direct_callers'].values()))==75)
ck('38 literal load candidates',len(a['literal_load_candidates'])==38)
ck('no firmware/binary/SYX output',not any(p.suffix.lower() in ('.bin','.hex','.syx') for p in O.rglob('*') if p.is_file()))
ck('H4 fails bounded failure gate',r['H4']['status']=='FAIL' and r['H4']['confidence']=='PROVEN')
note=R/'notes/qspi82000-hardware-readiness.md'
ck('required final verdict',note.read_text(encoding='utf8').rstrip().endswith('QSPI STORAGE ERROR RECOVERY = UNQUALIFIED'))
result=dict(confidence='PROVEN',scope='Offline assertions and scoped negative recovery search; no hardware/reboot admission',checks=checks,validation_checks=len(checks),
 replay_assertions=len(r['checks']),fault_cases=6,additional_fault_ticks=768,native_idle_feed_invocations=768,
 guard_rounds=sum(x['details']['guard_checks'] for x in r['cases'])+normal['guard_checks'],H4=r['H4'],
 verdict='UNQUALIFIED',H1_H2='Unchanged; not re-investigated',prior_evidence_unchanged=True,reference_inputs_unchanged=451,pinned_sources_unchanged=183,
 hardware_access=False,firmware_generated=False,report_sha256=sha(note),
 evidence_sha256={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name!='validation.json'})
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','evidence_sha256')},indent=2))
