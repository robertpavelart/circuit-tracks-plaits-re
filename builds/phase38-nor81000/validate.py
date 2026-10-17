"""Qualification stays UNQUALIFIED when the required source bytes are absent."""
from pathlib import Path
import json,hashlib,sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(name,ok):assert ok,name;checks.append(name)
for phase in ('phase26-qspi82000','phase27-qspi-read','phase28-hardware-readiness','phase29-storage-wrapper','phase30-chunked-storage','phase31-storage-error-recovery','phase32-host-containment','phase33-preservation-powercycle','phase34-startup-decompression','phase35-svc-context','phase36-pendsv-context','phase37-systick'):
 p=R/'builds'/phase;v=read(p/'validation.json')
 ck(phase+' evidence unchanged',all(sha(p/n)==h for n,h in v['evidence_sha256'].items()))
old=R/'builds/phase37-systick';v37=read(old/'validation.json')
for name in ('trace.py','svc.py','pendsv.py','systick.py'):ck(name+' phase37 support unchanged',sha(O/name)==sha(old/name))
for label,name,key in (('preservation','qspi82000-preservation-powercycle.md','preservation_report_sha256'),('readiness','qspi82000-hardware-readiness.md','report_sha256')):
 before=O/f'phase37-{label}-before.md';note=R/'notes'/name
 ck(label+' archive matches phase37',sha(before)==v37[key])
 ck(label+' prior text preserved',note.read_bytes().startswith(before.read_bytes()))
 ck(label+' unqualified outcome appended',note.read_text(encoding='utf8').rstrip().endswith('NOR81000 STORAGE READ = UNQUALIFIED'))
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
ck('451 reference inputs unchanged',len(ref)==451 and all(sha(Path(n))==h for n,h in ref.items()))
pins=read(R/'plaits/upstream/source-manifest.json')['files']
ck('183 pinned sources unchanged',len(pins)==183 and all(sha(R/'plaits/upstream'/p['path'])==p['sha256'] for p in pins))
cat=read(O/'candidate-catalog.json');admit=read(O/'payload-admission.json')
ck('1858 existing candidates retained',len(cat['candidates'])==cat['reused_prior_candidates']==1858)
ck('all inherited candidates have path/hash/space/provenance',all(x['path'] and len(x['sha256'])==64 and 'documented_base_address' in x and x['documented_address_space'] and x['provenance'] for x in cat['candidates']))
ck('22 relevant candidate files rehashed',len(cat['focused_rehashed'])==22 and all(sha(Path(x['path']))==x['sha256'] for x in cat['focused_rehashed']))
ck('five new generated artifacts have identity but no NOR admission',len(cat['new_existing_artifacts'])==5 and all(len(x['sha256'])==64 and not x['accepted'] and x['physical_NOR_81000_included'] is False for x in cat['new_existing_artifacts']))
ck('33 existing archive records referenced without reinterpreting bytes',cat['prior_archive_containers']==33 and sha(Path(cat['archive_catalog_source']))==cat['archive_catalog_sha256'])
ck('prior installation evidence not substituted',len(cat['modeled_installation_sources'])==2 and all(sha(Path(x['path']))==x['sha256'] and not x['NOR_81000_payload_present'] and not x['accepted'] for x in cat['modeled_installation_sources']))
ck('no candidate admitted by name or semantics',cat['no_filename_base_inference'] and cat['accepted_physical_NOR_sources']==0 and not any(x['accepted'] for x in cat['candidates']))
ck('accepted slice source/offset/hex/hash absent',not admit['accepted'] and all(admit[k] is None for k in ('source_file','source_file_offset','physical_NOR_base','slice_hex','slice_sha256','independent_authenticated_duplicate')))
ck('native payload completion not admitted',admit['native_payload_service_admitted'] is False and admit['requested_bytes']==23 and admit['requested_range']==['0x81000','0x81017'])
a=read(O/'stock-request.json');b=read(O/'diagnostic-request.json')
ck('stock/diagnostic complete request event equality',a['read_events']==b['read_events'])
ck('stock/diagnostic final ownership equality',a['read_final']==b['read_final'])
ck('stock/diagnostic final CPU/SRAM equality',a['final_architecture']==b['final_architecture'] and a['RAM_sha256']==b['RAM_sha256'])
for row in (a,b):
 name=row['variant'];f=row['read_final'];prev=read(old/f'{name}.json')
 ck(name+' observer leaves phase37 stop/SRAM/code unchanged',row['stop']==prev['stop'] and row['RAM_sha256']==prev['RAM_sha256'] and row['code_sha256']==prev['code_sha256'] and row['code_unchanged'])
 ck(name+' final architectural state unchanged',row['final_architecture']==prev['final_architecture'])
 caller=next(x for x in row['read_events'] if x['pc']==0x08005dac)
 ck(name+' exact caller arguments',all(caller['registers'][k]==v for k,v in dict(r0=0x20007a44,r1=0x81000,r2=0x2000546c,r3=23,r6=0x08005881).items()))
 submitted=next(x for x in row['read_events'] if x['pc']==0x080058a4)['request']
 dequeued=next(x for x in row['read_events'] if x['pc']==0x080057b6)['request']
 ck(name+' exact native request fields',submitted['fields']==dequeued['fields']==[1,0,0x81000,0x2000546c,23,0,0])
 ck(name+' correct stack ownership and queue copy',submitted['address']==f['original_request_address']==0x20006410 and dequeued['address']==f['request_address']==0x2000742c and submitted['hex']==dequeued['hex']==f['original_request_hex']==f['request_hex'])
 ck(name+' real Main submit and Storage dequeue owners',caller['objects']['current_TCB']==0x20006488 and f['objects']['current_TCB']==0x20007470 and f['objects']['wrapper']==0x20007a44 and f['objects']['backend']==0x200003dc and f['objects']['queue']==0x20007a60)
 init=bytes.fromhex(caller['objects']['backend_hex']);end=bytes.fromhex(f['objects']['backend_hex']);wrapper=bytes.fromhex(f['objects']['wrapper_hex'])
 ck(name+' semaphore held and sync wait retained',init[8]==1 and end[8]==0 and int.from_bytes(wrapper[16:20],'little')==1)
 ck(name+' DMA is armed but no bytes consumed',f['DMA_registers']['0x400264bc']==23 and f['DMA_registers']['0x400264c0']==0xa0001020 and f['DMA_registers']['0x400264c4']==0x2000546c and f['DMA_registers']['0x400264b8']&1==1)
 ck(name+' exact controller command no fake status',f['controller_registers']['0xa0001010']==22 and f['controller_registers']['0xa0001014']==0x07183fec and f['controller_registers']['0xa0001018']==0x81000 and f['controller_registers']['0xa0001008']==0)
 ck(name+' no backend read completion/caller consumer executed',not any(x['pc'] in (0x08007712,0x08005dae) for x in row['read_events']) and row['stop']['kind']=='missing authentic QSPI response' and row['stop']['pc']=='0x80051c2')
 ck(name+' target observation stays prefix-only',row['target_counts_observed_prefix']==dict(reads=0,writes=0,erase_overlaps=0) and row['target_counts_complete_boot'] is None and not row['stable_user_state'])
ck('observer does not write RAM or MMIO','.mem_write(' not in (O/'request_trace.py').read_text())
ck('observer adds no RAM memory hook','hook_add(UC_HOOK_MEM' not in (O/'request_trace.py').read_text())
ck('no binary/firmware/slice outputs',not any(p.suffix.lower() in ('.bin','.syx','.hex') for p in O.rglob('*') if p.is_file()))
# Decode authoritative pinned instructions; do not run any historical writer.
sys.path.insert(0,str(R/'builds/phase33-preservation-powercycle'))
from support import ROM,md
def ins(a,n=4):return next(md.disasm(ROM[a-0x08000000:a-0x08000000+n],a))
ck('native reader forces zero at byte14',ins(0x08005dae).mnemonic=='movs' and ins(0x08005dae).op_str=='r2, #0' and ins(0x08005db0).mnemonic=='strb' and ins(0x08005db0).op_str=='r2, [r4, #0xe]')
ck('reader length and address literals exact',ins(0x08005d9c).op_str=='r3, #0x17' and ins(0x08005da4).op_str=='r1, #0x81000')
ck('static consumer copies fourteen bytes',ins(0x08005e7c).op_str=='r2, #0xe')
result=dict(confidence='UNKNOWN',scope='Exact native request and source inventory; no original NOR payload or completed-read qualification',verdict='UNQUALIFIED',
 checks=checks,validation_checks=len(checks),proven_prefix_controls=['stock','diagnostic'],accepted_sources=0,accepted_slice_sha256=None,accepted_slice_hex=None,
 native_completion_executed=False,post_consumption_checkpoint=None,next_blocker='Missing proven original NOR 81000..81016 source bytes/address mapping, including byte14',
 gates=dict(H1='UNKNOWN',H2='UNKNOWN',P1='PROVEN within prior diagnostic scope',P2='UNKNOWN',P3='UNKNOWN',P4='PROVEN unchanged code'),
 observed_prefix_target_counts=dict(reads=0,writes=0,erase_overlaps=0),complete_boot_target_counts=None,
 hardware_access=False,firmware_generated=False,SDMMC_investigated=False,target_data_investigated=False,
 reference_inputs_unchanged=451,pinned_sources_unchanged=183,
 report_sha256=sha(R/'notes/qspi82000-hardware-readiness.md'),preservation_report_sha256=sha(R/'notes/qspi82000-preservation-powercycle.md'),
 evidence_sha256={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name!='validation.json'})
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','evidence_sha256')},indent=2))
