"""Phase35 evidence closure; all earlier evidence remains byte-exact."""
import json,hashlib,sys
from pathlib import Path
sys.dont_write_bytecode=True
import unicorn
O=Path(__file__).resolve().parent;R=O.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(name,ok):assert ok,name;checks.append(name)
for phase in ('phase26-qspi82000','phase27-qspi-read','phase28-hardware-readiness','phase29-storage-wrapper','phase30-chunked-storage','phase31-storage-error-recovery','phase32-host-containment','phase33-preservation-powercycle','phase34-startup-decompression'):
 p=R/'builds'/phase;v=read(p/'validation.json')
 ck(phase+' evidence byte-exact',all(sha(p/n)==h for n,h in v['evidence_sha256'].items()))
v34=read(R/'builds/phase34-startup-decompression/validation.json')
for label,name,key in (('preservation','qspi82000-preservation-powercycle.md','preservation_report_sha256'),('readiness','qspi82000-hardware-readiness.md','report_sha256')):
 before=O/f'phase34-{label}-before.md';p=R/'notes'/name
 ck(label+' archive matches phase34',sha(before)==v34[key])
 ck(label+' previous note retained byte-exact',p.read_bytes().startswith(before.read_bytes()))
 ck(label+' result appended',p.read_text(encoding='utf8').rstrip().endswith('BOOTLOADER SVC / PSP MODEL = PASS'))
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
ck('451 reference inputs unchanged',len(ref)==451 and all(sha(Path(n))==h for n,h in ref.items()))
pins=read(R/'plaits/upstream/source-manifest.json')['files']
ck('183 pinned sources unchanged',len(pins)==183 and all(sha(R/'plaits/upstream'/p['path'])==p['sha256'] for p in pins))
stock=read(O/'stock.json');diag=read(O/'diagnostic.json');s=stock['svc'];d=diag['svc']
ck('stock and diagnostic entire SVC trace identical',s==d)
ck('stock and diagnostic entire SRAM identical',stock['RAM_sha256']==diag['RAM_sha256'])
for row in (stock,diag):
 name=row['variant'];m=row['svc']
 ck(name+' unchanged native code',row['code_unchanged'])
 ck(name+' native decompression retained',row['blocks'][0]['returned'] and row['blocks'][0]['output_sha256']=='7e6f9f2ef9ae96a8ab8cf3f0b11b5df1520aad4bc483f559682525540b48bd18')
 ck(name+' exact SVC/vector/priority',m['pre']['pc']==0x080031c2 and m['vector_word']==0x0800002c and m['handler']==0x08003189 and m['SVC_priority']==0)
 ck(name+' actual preconditions',all(m['pre'][k]==v for k,v in dict(control=0,primask=0,basepri=0xc0,faultmask=0,msp=0x20050000,psp=0,lr=0x08002e2b,xpsr=0x61000000,ipsr=0).items()))
 ck(name+' correct hardware entry',m['entry_frame_address']==0x2004ffe0 and m['entry_frame']['pc']==0x080031c4 and m['entry_EXC_RETURN']==0xfffffff9 and m['handler_entry']['ipsr']==11 and m['handler_entry']['pc']==0x08003188 and m['padding']==0)
 ck(name+' active SVC state modeled',m['ICSR_at_entry']==11 and m['SHCSR_at_entry']==m['SHCSR_before_entry']|0x80 and m['ICSR_after_return']==0 and m['SHCSR_after_return']==m['SHCSR_before_entry'])
 ck(name+' authentic four task frames',len(m['task_frame_initializers'])==4 and any(x['saved_context']==m['saved_context'] and x['frame_hex']==m['saved_context_hex'] for x in m['task_frame_initializers']))
 ck(name+' task owns native context',m['current_TCB_global']==0x20005268 and m['current_TCB']==0x20007eb8 and m['task_name']=='IDLE' and m['saved_context']==0x20007e6c)
 ck(name+' actual handler observed', [x['pc'] for x in m['handler_trace']]==[0x08003188,0x0800318a,0x0800318c,0x0800318e,0x08003192,0x08003196,0x0800319a,0x0800319e,0x080031a2])
 ck(name+' native PSP and EXC_RETURN',m['before_return']['psp']==0x20007e90 and m['before_return']['lr']==0xfffffffd and m['before_return']['basepri']==0)
 ck(name+' exact frame restored once',m['return_frame_address']==0x20007e90 and m['return_EXC_RETURN']==0xfffffffd and m['frame_consumptions']==1 and m['restored']['psp']==0x20007eb0 and m['restored']['msp']==0x2004ffe0 and m['restored']['pc']==0x08002a58 and m['restored']['control']==2 and m['restored']['ipsr']==0)
 ck(name+' real PSP task runs to pending boundary',len(m['post_return_trace'])==8 and m['post_return_trace'][0]['pc']==0x08002a58 and row['stop']==dict(kind='next unsupported pending PendSV boundary',pc='0x8002a6e') and m['pending_checkpoint']['ICSR']==0x10000000 and m['pending_checkpoint']['registers']['psp']==0x20007ea0)
 ck(name+' no false complete boot or array traffic',row['target_counts_observed_prefix']==dict(reads=0,writes=0,erase_overlaps=0) and row['target_counts_complete_boot'] is None and not row['stable_user_state'])
tests=read(O/'regressions.json');ck('22 passing architectural fixture checks',len(tests)==22 and all(x['result']=='PASS' for x in tests))
ck('no firmware outputs',not any(p.suffix.lower() in ('.bin','.syx','.hex') for p in O.rglob('*') if p.is_file()))
ck('no RAM memory hooks in new adapter','hook_add(UC_HOOK_MEM' not in (O/'svc.py').read_text())
ck('runner read observer remains bounded',"if hooks=='bounded':" in (O/'trace.py').read_text() and '0x20000000,0x2004ffff' not in (O/'trace.py').read_text())
module=Path(unicorn.__file__);dll=module.parent/'lib/unicorn.dll'
result=dict(confidence='PROVEN',scope='Native privileged basic-frame bootloader SVC and first PSP task checkpoint only',
 checks=checks,validation_checks=len(checks),native_controls=['stock first','diagnostic second'],fixture_checks=len(tests),
 verdict='PASS',next_smallest_experiment='Native pending PendSV from idle at 08002A6E; handler 0800312C',
 complete_boot='UNKNOWN',gates=dict(H1='UNKNOWN',H2='UNKNOWN',P1='PROVEN within prior diagnostic scope',P2='UNKNOWN',P3='UNKNOWN',P4='PROVEN unchanged code'),
 SDMMC_investigated=False,hardware_access=False,firmware_generated=False,reference_inputs_unchanged=451,pinned_sources_unchanged=183,
 model_runtime=dict(Python=sys.version,unicorn_version=unicorn.__version__,DLL_sha256=sha(dll) if dll.exists() else None),
 report_sha256=sha(R/'notes/qspi82000-hardware-readiness.md'),preservation_report_sha256=sha(R/'notes/qspi82000-preservation-powercycle.md'),
 evidence_sha256={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name!='validation.json'})
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','evidence_sha256','model_runtime')},indent=2))
