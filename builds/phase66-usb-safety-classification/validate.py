from pathlib import Path
import json,hashlib,sys
from usb_model import USBInit
O=Path(__file__).resolve().parent;R=O.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda n:json.loads((O/n).read_text())
if '--manifest' in sys.argv:
 rows=(O/'SHA256SUMS.txt').read_text().splitlines()
 for row in rows:
  h,n=row.split('  ',1);assert sha(O/n)==h,n
 print('Phase66 manifest verified',len(rows));raise SystemExit
x=load('continuity.json');a=load('analysis.json');v=load('preflight-verdict.json');u=load('usb-evidence.json')
assert v['verdict']=='UNQUALIFIED' and not v['firmware_modified']
assert x['frontier']['pc']=='0x801d5a4' and a['new_frontier']['address']=='0xe0001004'
assert x['record']=='110000000180003480908f01' and x['executed_instructions']==7071645
prior=load('pre-instrumentation-frontier.json');assert prior['frontier']==x['frontier'] and prior['executed_instructions']==x['executed_instructions']
assert a['generic_requests']==1582 and a['completed_returns']==3186 and a['pending_returns']==0
assert not a['positive_request_failures'] and not a['diagnostic_record_overlapping_returns']
assert a['USB_handle']['PCD_state']==1 and a['USB_handle']['DMA_enable']==0
assert not a['NOR_mutation_entries_after_USB'] and not a['USB_host_configured']
tests=load('model-tests.json');assert tests['passed'] and len(tests['cases'])==6
m=USBInit()
for row in u['trace']:
 off=int(row['address'],16)-m.BASE;value=int(row['value'],16);pc=int(row['PC'],16)
 if row['access']=='R':assert m.read(off,pc=pc)==value,row
 else:m.write(off,value,pc=pc)
assert m.summary()['registers']==u['registers']
for name in ('loaded-core0.be24','loaded-core1.be24'):
 assert sha(O/name)==sha(R/'builds/phase65-shi-model-closure'/name)
assert not list(O.glob('*.syx'))
result=dict(confidence='PROVEN',saved_result_consistency=True,passive_replay_reproducible=True,USB_trace_accesses_replayed=len(u['trace']),native_helper_checks=6,allocation_returns=3186,allocation_overlaps=0,USB_PCD_READY=True,USB_host_configured=False,remaining_gap='DWT.CYCCNT profiling',firmware_changed=False,overall_verdict='UNQUALIFIED')
(O/'final-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
