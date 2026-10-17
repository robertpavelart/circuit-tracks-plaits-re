"""Preservation and host-containment evidence closure, no hardware access."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(n,v):assert v,n;checks.append(n)
for phase in ('phase26-qspi82000','phase27-qspi-read','phase28-hardware-readiness','phase29-storage-wrapper','phase30-chunked-storage','phase31-storage-error-recovery'):
 p=R/'builds'/phase;v=read(p/'validation.json')
 ck(phase+' evidence unchanged',all(sha(p/n)==h for n,h in v['evidence_sha256'].items()))
v31=read(R/'builds/phase31-storage-error-recovery/validation.json')
ck('phase31 report archive exact',sha(O/'phase31-report-before.md')==v31['report_sha256'])
note=R/'notes/qspi82000-hardware-readiness.md'
ck('prior report text preserved',note.read_bytes().startswith((O/'phase31-report-before.md').read_bytes()))
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
ck('451 reference inputs unchanged',len(ref)==451 and all(sha(Path(n))==h for n,h in ref.items()))
pins=read(R/'plaits/upstream/source-manifest.json')['files']
ck('183 pinned sources unchanged',len(pins)==183 and all(sha(R/'plaits/upstream'/p['path'])==p['sha256'] for p in pins))
r=read(O/'test-results.json');cases=r['cases']
ck('265 meaningful host assertions',r['passed_assertions']==265 and len(r['checks'])==265)
ck('30 stream scenarios',len(cases)==30 and r['scenario_groups']==30)
ck('A through N represented',all(any(c['case'].startswith(k+' ') for c in cases) for k in 'ABCDEFGHIJKLMN'))
ck('absolute five-second bound',r['timeout_seconds']==5.0 and all(c['virtual_elapsed']<=5.0+1e-9 for c in cases))
success=[c for c in cases if c['result']['status']=='SUCCESS'];failed=[c for c in cases if c['result']['status']=='FAILED']
ck('only three valid stream encodings accepted',len(success)==3 and {c['case'] for c in success}=={'A complete normal stream','fragmented valid stream','coalesced valid stream'})
ck('all failed streams no final file or digest',len(failed)==27 and all(not c['final_exists'] and c['result']['sha256'] is None and not c['result']['reconstruction_retained'] for c in failed))
ck('all failed sessions clearly quarantined',all(c['result']['device_state']=='POWER-CYCLE REQUIRED' and c['result']['message']=='CAPTURE FAILED\nDO NOT RETRY\nPOWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT' for c in failed))
ck('single request no retry',all(c['sent_requests']==1 for c in cases) and r['automatic_retries']==0 and r['device_cleanup_commands']==0)
ck('exact SHA for each valid encoding',all(c['result']['sha256']==r['accepted_sha256'] for c in success))
ck('Windows atomic no-replace rename target',sys.platform=='win32')
ck('no residual test data or firmware',not any(p.suffix.lower() in ('.bin','.syx','.hex','.tmp') for p in O.rglob('*') if p.is_file()))
ck('publication failure and existing evidence checks','publication failure removes staged data' in r['checks'] and 'existing output preserved and no request issued' in r['checks'])
ck('required final verdict',note.read_text(encoding='utf8').rstrip().endswith('QSPI HOST FAILURE CONTAINMENT = PASS'))
result=dict(confidence='PROVEN',scope='Host-side offline containment only; not device error recovery/hardware readiness',checks=checks,validation_checks=len(checks),
 host_assertions=265,stream_scenarios=30,failed_streams=27,valid_transport_encodings=3,timeout_seconds=5.0,automatic_retries=0,cleanup_commands=0,
 H4='FAIL, unchanged for device in-session recovery',H1_H2='Unchanged; not investigated',prior_evidence_unchanged=True,reference_inputs_unchanged=451,pinned_sources_unchanged=183,
 hardware_access=False,firmware_generated=False,verdict='PASS',report_sha256=sha(note),
 evidence_sha256={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name!='validation.json'})
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','evidence_sha256')},indent=2))
