"""Close phase36 evidence without rerunning historical evidence writers."""
from pathlib import Path
import json,hashlib,sys
sys.dont_write_bytecode=True
import unicorn
O=Path(__file__).resolve().parent;R=O.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(name,ok):assert ok,name;checks.append(name)
for phase in ('phase26-qspi82000','phase27-qspi-read','phase28-hardware-readiness','phase29-storage-wrapper','phase30-chunked-storage','phase31-storage-error-recovery','phase32-host-containment','phase33-preservation-powercycle','phase34-startup-decompression','phase35-svc-context'):
 p=R/'builds'/phase;v=read(p/'validation.json')
 ck(phase+' evidence unchanged',all(sha(p/n)==h for n,h in v['evidence_sha256'].items()))
old=R/'builds/phase35-svc-context';v35=read(old/'validation.json')
ck('phase35 qualified SVC copied without changes',sha(O/'svc.py')==sha(old/'svc.py'))
for label,name,key in (('preservation','qspi82000-preservation-powercycle.md','preservation_report_sha256'),('readiness','qspi82000-hardware-readiness.md','report_sha256')):
 before=O/f'phase35-{label}-before.md';note=R/'notes'/name
 ck(label+' archive matches phase35',sha(before)==v35[key])
 ck(label+' old text byte-exact',note.read_bytes().startswith(before.read_bytes()))
 ck(label+' current result appended',note.read_text(encoding='utf8').rstrip().endswith('BOOTLOADER PENDSV / CONTEXT MODEL = PASS'))
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
ck('451 reference inputs unchanged',len(ref)==451 and all(sha(Path(n))==h for n,h in ref.items()))
pins=read(R/'plaits/upstream/source-manifest.json')['files']
ck('183 pinned sources unchanged',len(pins)==183 and all(sha(R/'plaits/upstream'/p['path'])==p['sha256'] for p in pins))
stock=read(O/'stock.json');diag=read(O/'diagnostic.json');minimal=read(O/'stock-minimal-observer.json')
ck('official stock and diagnostic entire PendSV evidence agrees',stock['PendSV']==diag['PendSV'])
ck('official stock and diagnostic complete SRAM agrees',stock['RAM_sha256']==diag['RAM_sha256'])
ck('post-scheduler checkpoint agrees',stock['stop']==diag['stop']==minimal['stop']==dict(kind='next unsupported post-scheduler SysTick boundary',pc='0x8006ef2'))
ck('observer ablation complete SRAM agreement',minimal['RAM_sha256']==stock['RAM_sha256'])
for k in ('captured','incoming','before_return','restored','outgoing_saved_PSP','outgoing_software_frame_hex','post_return_trace'):
 ck('minimal observer '+k+' agrees',minimal['PendSV'][0][k]==stock['PendSV'][0][k])
for row in (stock,diag):
 name=row['variant'];p=row['PendSV'][0];before=read(old/f'{name}.json')
 ck(name+' SVC evidence unchanged',row['svc']==before['svc'])
 ck(name+' unchanged code',row['code_unchanged'] and row['code_sha256']==before['code_sha256'])
 ck(name+' exact old pending entry CPU',p['captured']['registers']==before['svc']['pending_checkpoint']['registers'])
 ck(name+' exact old pending entry SRAM',p['captured']['RAM_sha256']==before['RAM_sha256'])
 ck(name+' correct vector/priority',p['vector_word']==0x08000038 and p['handler']==0x0800312d and p['priority']==0xf0 and p['captured']['AIRCR']>>8&7==3)
 ck(name+' correct hardware entry',p['pre']['psp']==0x20007ea0 and p['hardware_frame_address']==0x20007e80 and p['hardware_frame']['pc']==0x08002a6e and p['hardware_frame']['xpsr']==0x21000000 and p['padding']==0 and p['handler_entry']['msp']==0x2004ffe0 and p['handler_entry']['ipsr']==14 and p['handler_entry']['control']==0)
 ck(name+' pending consumed and active set',p['captured']['ICSR']==0x10000000 and p['ICSR_active']==0x80e and p['SHCSR_active']==0x70400)
 ck(name+' exact outgoing IDLE save',p['captured']['current_task']['TCB']==0x20007eb8 and p['outgoing_saved_PSP']==0x20007e5c and p['captured']['current_task']['name']=='IDLE')
 ck(name+' actual scheduler and ready-list',any(x['pc']==0x080029d8 for x in p['native_trace']) and p['ready_list_base']==0x20005204 and p['ready_bitmap']==1 and p['selected_priority']==0)
 ck(name+' incoming Main has native constructor frame',p['incoming']['TCB']==0x20006488 and p['incoming']['saved_PSP']==0x2000643c and p['incoming']['name']=='Main' and p['incoming_native_constructor']['frame_hex']==p['incoming']['context_hex'] and p['incoming_native_constructor']['task_entry']==0x08002fdf)
 ck(name+' native incoming PSP/r4-r11',p['before_return']['psp']==0x20006460 and all(p['before_return'][f'r{i}']==0xa5a5a5a5 for i in range(4,12)))
 ck(name+' exact return once',p['return_EXC_RETURN']==0xfffffffd and p['return_frame_address']==0x20006460 and p['frame_consumptions']==1 and p['restored']['pc']==0x08002fde and p['restored']['psp']==0x20006480 and p['restored']['msp']==0x2004ffe0 and p['restored']['control']==2 and p['restored']['ipsr']==0)
 ck(name+' no pending/active after return',p['ICSR_return']==0x800 and p['SHCSR_return']==0x70000)
 ck(name+' no FP save/restore executed',not {0x0800313e,0x0800317a}&{x['pc'] for x in p['native_trace']})
 ck(name+' native instruction and store coverage',len(p['native_trace'])==64 and len(p['native_store_intents'])==7 and p['changed_word_writes']==13 and not p['unexpected_RAM_writes'])
 ck(name+' genuine post-return progression',len(p['post_return_trace'])==96 and p['post_return_trace'][0]['pc']==0x08002fde)
 ck(name+' no fabricated second switch',len(row['PendSV'])==1)
 ck(name+' incomplete boot remains explicit',not row['stable_user_state'] and row['target_counts_complete_boot'] is None and row['target_counts_observed_prefix']==dict(reads=0,writes=0,erase_overlaps=0))
tests=read(O/'regressions.json')
ck('32 passing new regression checks',len(tests['checks'])==32 and all(x['result']=='PASS' for x in tests['checks']))
ck('second switch unobserved stated UNKNOWN',tests['native_second_PendSV']['confidence']=='UNKNOWN')
ck('adapter has no RAM memory hooks','hook_add(UC_HOOK_MEM' not in (O/'pendsv.py').read_text())
ck('no firmware output',not any(p.suffix.lower() in ('.bin','.syx','.hex') for p in O.rglob('*') if p.is_file()))
module=Path(unicorn.__file__);dll=module.parent/'lib/unicorn.dll'
result=dict(confidence='PROVEN',scope='First privileged basic-frame native bootloader IDLE-to-Main PendSV only',
 verdict='PASS',validation_checks=len(checks),checks=checks,new_regression_checks=32,native_controls=['official stock first','diagnostic second','stock minimal observer control'],
 observed_switches_per_control=1,second_switch='UNKNOWN beyond checkpoint',next_blocker='First post-scheduler native SysTick due at 08006EF2 under inherited ideal cadence',
 next_smallest_experiment='Qualify native post-scheduler bootloader SysTick and resulting scheduler effects from captured Main PSP context',
 gates=dict(H1='UNKNOWN',H2='UNKNOWN',P1='PROVEN within prior diagnostic scope',P2='UNKNOWN',P3='UNKNOWN',P4='PROVEN unchanged code'),
 complete_boot='UNKNOWN',full_target_counts=None,observed_prefix_counts=dict(reads=0,writes=0,erase_overlaps=0),
 SDMMC_investigated=False,hardware_access=False,firmware_generated=False,reference_inputs_unchanged=451,pinned_sources_unchanged=183,
 model_runtime=dict(Python=sys.version,unicorn_version=unicorn.__version__,DLL_sha256=sha(dll) if dll.exists() else None),
 report_sha256=sha(R/'notes/qspi82000-hardware-readiness.md'),preservation_report_sha256=sha(R/'notes/qspi82000-preservation-powercycle.md'),
 evidence_sha256={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name!='validation.json'})
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','evidence_sha256','model_runtime')},indent=2))
