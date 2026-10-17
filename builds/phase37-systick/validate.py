"""Close phase37 evidence; preserve all earlier evidence and open boot gates."""
from pathlib import Path
import json,hashlib,sys
sys.dont_write_bytecode=True
import unicorn
O=Path(__file__).resolve().parent;R=O.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(name,ok):assert ok,name;checks.append(name)
for phase in ('phase26-qspi82000','phase27-qspi-read','phase28-hardware-readiness','phase29-storage-wrapper','phase30-chunked-storage','phase31-storage-error-recovery','phase32-host-containment','phase33-preservation-powercycle','phase34-startup-decompression','phase35-svc-context','phase36-pendsv-context'):
 p=R/'builds'/phase;v=read(p/'validation.json')
 ck(phase+' evidence unchanged',all(sha(p/n)==h for n,h in v['evidence_sha256'].items()))
old=R/'builds/phase36-pendsv-context';v36=read(old/'validation.json')
for name in ('svc.py','pendsv.py'):ck(name+' qualified implementation byte-exact',sha(O/name)==sha(old/name))
for label,name,key in (('preservation','qspi82000-preservation-powercycle.md','preservation_report_sha256'),('readiness','qspi82000-hardware-readiness.md','report_sha256')):
 archive=O/f'phase36-{label}-before.md';note=R/'notes'/name
 ck(label+' archive matches phase36',sha(archive)==v36[key])
 ck(label+' earlier note retained byte-exact',note.read_bytes().startswith(archive.read_bytes()))
 ck(label+' verdict appended',note.read_text(encoding='utf8').rstrip().endswith('BOOTLOADER SYSTICK MODEL = PASS'))
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
ck('451 reference inputs unchanged',len(ref)==451 and all(sha(Path(n))==h for n,h in ref.items()))
pins=read(R/'plaits/upstream/source-manifest.json')['files']
ck('183 pinned sources unchanged',len(pins)==183 and all(sha(R/'plaits/upstream'/p['path'])==p['sha256'] for p in pins))
a=read(O/'stock.json');b=read(O/'diagnostic.json');minimal=read(O/'stock-minimal-observer.json')
ck('stock/diagnostic complete SysTick evidence matches',a['SysTick']==b['SysTick'])
ck('stock/diagnostic complete PendSV evidence matches',a['PendSV']==b['PendSV'])
ck('stock/diagnostic whole SRAM matches',a['RAM_sha256']==b['RAM_sha256'])
ck('stock/diagnostic final CPU state matches',a['final_architecture']==b['final_architecture'])
ck('minimal observer final SRAM/CPU match',minimal['RAM_sha256']==a['RAM_sha256'] and minimal['final_architecture']==a['final_architecture'])
for k in ('captured','before_return','restored','after','legacy_comparison'):
 ck('minimal SysTick '+k+' matches',minimal['SysTick'][0][k]==a['SysTick'][0][k])
for row in (a,b):
 name=row['variant'];t=row['SysTick'][0];prev=read(old/f'{name}.json')
 ck(name+' unchanged code',row['code_unchanged'] and row['code_sha256']==prev['code_sha256'])
 ck(name+' exact old SVC evidence',row['svc']==prev['svc'])
 ck(name+' exact phase36 pre-tick SRAM',t['captured']['RAM_sha256']==prev['RAM_sha256'])
 ck(name+' exact phase36 pre-tick registers',all(t['pre'][k]==int(v,16) for k,v in prev['registers'].items() if k!='xPSR') and t['pre']['xpsr']==int(prev['registers']['xPSR'],16) and t['pre']['pc']==0x08006ef2)
 ck(name+' native configuration recorded',row['SysTick_configuration'][-1]['LOAD']==119999 and row['SysTick_configuration'][-1]['CTRL']==7 and row['SysTick_configuration'][-1]['core_clock']==120000000)
 ck(name+' actual native configuration MMIO',any(x['pc']==0x08002f02 and x['access']=='write' and x['address']==0xe000e014 and x['value']==119999 for x in row['clock_MMIO']) and any(x['pc']==0x08002f04 and x['address']==0xe000e010 and x['value']==7 for x in row['clock_MMIO']))
 ck(name+' native priority setup',any(x['pc']==0x08001c58 and x['address']==0xe000ed23 and x['value']==0xf0 for x in row['clock_MMIO']) and t['captured']['SHPR3']==0xf0f00000)
 ck(name+' correct vector and priority',t['vector_word']==0x0800003c and t['handler']==0x08009331 and t['priority']==0xf0)
 ck(name+' eligible real preconditions',t['pre']['control']==2 and t['pre']['ipsr']==t['pre']['primask']==t['pre']['basepri']==t['pre']['faultmask']==0)
 ck(name+' actual padded hardware entry',t['pre']['psp']==0x200063c4 and t['hardware_frame_address']==0x200063a0 and t['padding']==4 and t['hardware_frame']['xpsr']==0x01000200 and t['hardware_frame']['pc']==0x08006ef2)
 ck(name+' pending consumed active set',t['ICSR_pending']==0x04000800 and t['ICSR_active']==0x80f and t['SHCSR_active']==0x70800 and t['handler_entry']['ipsr']==15 and t['handler_entry']['msp']==0x2004ffe0)
 ck(name+' actual native handler path', [x['pc'] for x in t['native_trace']]==[0x08009330,0x08009332,0x0800935c,0x0800935e,0x08009360,0x08009362,0x08009364,0x08009366,0x08009336,0x08009338,0x0800933a,0x0800933c,0x0800933e])
 ck(name+' native software increments only',t['captured']['clock_counter']==7 and t['after']['clock_counter']==8 and t['captured']['handler_counter']==0 and t['after']['handler_counter']==1)
 ck(name+' scheduler lists/current/kernel untouched by tick',t['captured']['scheduler_hex']==t['after']['scheduler_hex'] and t['captured']['kernel_counter']==t['after']['kernel_counter']==0 and t['after']['current_task']['TCB']==t['captured']['current_task']['TCB']==0x20006488 and not t['PendSV_requested'])
 ck(name+' exact native SRAM write boundaries',not t['unexpected_RAM_writes'] and {x['address'] for x in t['changed_word_writes']}=={0x2004ffd8,0x2004ffdc,0x20000008,0x20005518})
 ck(name+' exact POP and unstack once',t['native_return_pop']==dict(MSP=0x2004ffd8,r0=0x15,EXC_RETURN=0xfffffffd,after_MSP=0x2004ffe0) and t['return_EXC_RETURN']==0xfffffffd and t['frame_consumptions']==1 and t['return_frame_address']==0x200063a0)
 ck(name+' entire Thread context restored',t['restored']==t['pre'] and t['restored']['pc']==0x08006ef2 and t['restored']['psp']==0x200063c4 and t['restored']['control']==2)
 ck(name+' pending/active clear after tick',t['ICSR_return']==0x800 and t['SHCSR_return']==0x70000)
 ck(name+' old/new scheduler observables agree',all(t['legacy_comparison'][k] for k in ('scheduler_hex','clock_counter','handler_counter','kernel_counter','registers','current_TCB')))
 ck(name+' old/new stack discrepancy precisely recorded',not t['legacy_comparison']['full_RAM_equal'] and len(t['legacy_RAM_differences'])==10 and t['legacy_RAM_differences'][0]['address']==0x200063a0 and t['legacy_RAM_differences'][-1]['address']==0x2004ffdc)
 ck(name+' natural native Thread-generated requests only',[x['pc'] for x in row['MMIO_writes'] if x['address']=='0xe000ed04']==['0x8002a6c','0x8004720','0x8004720'])
 ck(name+' all three native task switches',[x['incoming']['name'] for x in row['PendSV']]==['Main','UI','Storage'] and [x['restored']['pc'] for x in row['PendSV']]==[0x08002fde,0x08003048,0x08009202] and [x['restored']['psp'] for x in row['PendSV']]==[0x20006480,0x20006e00,0x20007468])
 initial={x['saved_context']:x for x in row['svc']['task_frame_initializers']}
 ck(name+' every incoming context native constructor-owned',all(initial[x['incoming']['saved_PSP']]['frame_hex']==x['incoming']['context_hex'] for x in row['PendSV']))
 ck(name+' all switch preservation/ownership assertions complete',all(x['frame_consumptions']==1 and not x['unexpected_RAM_writes'] and x['return_EXC_RETURN']==0xfffffffd for x in row['PendSV']))
 ck(name+' observed critical-section masks',any(x['registers']['primask']==1 for x in row['PendSV'][0]['native_trace']) and any(x['registers']['basepri']==0xc0 for x in row['PendSV'][0]['native_trace']))
 ck(name+' stops at exact next NOR boundary',row['stop']['kind']=='missing authentic QSPI response' and row['stop']['pc']=='0x80051c2' and row['stop']['command']==dict(opcode='0xec',address='0x81000',DLR=22,CCR='0x7183fec',issuer_PC='0x80051c0'))
 ck(name+' no second tick invented',len(row['SysTick'])==1 and row['instructions']==77359 and row['instructions']<77689)
 ck(name+' new prefix target counts zero only',[x['opcode'] for x in row['NOR_commands']]==['0xf5','0x35','0xb7','0xaf','0xec'] and row['target_counts_observed_prefix']==dict(reads=0,writes=0,erase_overlaps=0) and row['target_counts_complete_boot'] is None and not row['stable_user_state'])
 ck(name+' no unsupported post-tick CPU CTRL access',not any(x['after_native_tick'] and x['access']=='read' and x['address']==0xe000e010 for x in row['clock_MMIO']))
tests=read(O/'regressions.json')
ck('24 passing checks',len(tests['checks'])==24 and all(x['result']=='PASS' for x in tests['checks']))
ck('unobserved C/H explicit UNKNOWN',tests['C']['confidence']==tests['H']['confidence']=='UNKNOWN' and tests['H']['observed_ticks']==1)
log=read(O/'run-log.json');ck('four clean checked subprocess exits',len(log)==4 and all(x['exit_code']==0 for x in log))
ck('no RAM memory hooks in new service','hook_add(UC_HOOK_MEM' not in (O/'systick.py').read_text())
ck('no firmware files generated',not any(p.suffix.lower() in ('.bin','.syx','.hex') for p in O.rglob('*') if p.is_file()))
module=Path(unicorn.__file__);dll=module.parent/'lib/unicorn.dll'
result=dict(confidence='PROVEN',scope='First post-scheduler privileged basic SysTick and subsequent native Thread-requested PendSV prefix',
 verdict='PASS',checks=checks,validation_checks=len(checks),new_regression_checks=24,checked_native_runs=['official stock first','diagnostic second','stock minimal observer'],
 native_ticks_per_control=1,native_PendSV_per_control=3,SysTick_requested_PendSV=False,second_tick='UNKNOWN beyond next boundary',
 next_boundary=dict(PC='080051C2',task='Storage',NOR_opcode='EC',address='81000',bytes=23,response_modeled=False),
 next_smallest_experiment='Qualify native Storage EC read 81000..81016 using provenance-checked existing NOR source bytes and native completion',
 gates=dict(H1='UNKNOWN',H2='UNKNOWN',P1='PROVEN within prior diagnostic scope',P2='UNKNOWN',P3='UNKNOWN',P4='PROVEN unchanged code'),
 observed_prefix_target_counts=dict(reads=0,writes=0,erase_overlaps=0),complete_boot_target_counts=None,
 SDMMC_investigated=False,hardware_access=False,firmware_generated=False,reference_inputs_unchanged=451,pinned_sources_unchanged=183,
 model_runtime=dict(Python=sys.version,unicorn_version=unicorn.__version__,DLL_sha256=sha(dll) if dll.exists() else None),
 report_sha256=sha(R/'notes/qspi82000-hardware-readiness.md'),preservation_report_sha256=sha(R/'notes/qspi82000-preservation-powercycle.md'),
 evidence_sha256={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name!='validation.json'})
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','evidence_sha256','model_runtime')},indent=2))
