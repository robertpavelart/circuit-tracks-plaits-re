"""Evidence closure; complete boot gates stay UNKNOWN when no endpoint exists."""
from pathlib import Path
import json,hashlib,sys,unicorn
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(n,v):assert v,n;checks.append(n)
for phase in ('phase26-qspi82000','phase27-qspi-read','phase28-hardware-readiness','phase29-storage-wrapper','phase30-chunked-storage','phase31-storage-error-recovery','phase32-host-containment','phase33-preservation-powercycle'):
 p=R/'builds'/phase;v=read(p/'validation.json')
 ck(phase+' evidence unchanged',all(sha(p/n)==h for n,h in v['evidence_sha256'].items()))
v33=read(R/'builds/phase33-preservation-powercycle/validation.json')
for label,filename,key in (('preservation','qspi82000-preservation-powercycle.md','preservation_report_sha256'),('readiness','qspi82000-hardware-readiness.md','report_sha256')):
 before=O/f'phase33-{label}-before.md';note=R/'notes'/filename
 ck(label+' archive exact',sha(before)==v33[key])
 ck(label+' prior text retained',note.read_bytes().startswith(before.read_bytes()))
 ck(label+' required final verdict',note.read_text(encoding='utf8').rstrip().endswith('QSPI PRESERVATION / COLD-BOOT MODEL = UNQUALIFIED'))
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
ck('451 reference inputs unchanged',len(ref)==451 and all(sha(Path(n))==h for n,h in ref.items()))
pins=read(R/'plaits/upstream/source-manifest.json')['files']
ck('183 pinned sources unchanged',len(pins)==183 and all(sha(R/'plaits/upstream'/p['path'])==p['sha256'] for p in pins))
isolation=read(O/'isolation.json');fault=read(O/'legacy-fault-detail.json');traces=read(O/'corrected-trace.json');oracle=read(O/'oracle.json');micro=read(O/'instruction-control.json')
poison=read(O/'poison-control.json');nor=read(O/'nor-progress.json');ident=read(O/'reference-identity-progress.json');ticks=read(O/'tick-progress.json');baseline=read(O/'B13-control.json');restart=read(O/'restart-prefix.json')
ck('36 fixture ablations',len(isolation)==36)
ck('all-address read hook alone reproduces same old failures',all(x['error'] is not None and x['end_PC']==('0x800929e' if x['entry']=='0x8000000' else '0x8059706') for x in isolation if x['mode']=='read hook'))
ck('code-only and register-init controls advance',all(x['error'] is None for x in isolation if x['mode'] in ('SP only','SP MSP','SP CONTROL','SP IPSR','all registers','code hook')))
ck('four detailed legacy faults',len(fault)==4 and all(not x['blocks'][0].get('returned',False) for x in fault))
ck('legacy descriptor/call/RAM/register evidence complete',all(x['blocks'][0]['descriptor_hex'] and x['blocks'][0]['call_chain'] and x['blocks'][0]['partial_RAM_destination'] and len(x['registers'])==16 for x in fault))
ck('eight corrected native reset prefixes',len(traces)==8 and all(x['blocks'][0]['returned'] for x in traces))
for entry,size,source_bytes,dest in (('bootloader',11084,885,'0x20000004'),('application',15618,2582,'0x20000000')):
 subset=[x for x in traces if x['entry']==entry]
 ck(entry+' native exact source/output sizes',all(x['blocks'][0]['output_bytes']==size and x['blocks'][0]['compressed_bytes']==source_bytes and x['blocks'][0]['destination']==dest for x in subset))
 for variant in ('stock','diagnostic'):
  pair=[x for x in subset if x['variant']==variant]
  ck(entry+'/'+variant+' bounded observer matches no-memory-hook RAM',len(pair)==2 and pair[0]['RAM_sha256']==pair[1]['RAM_sha256'] and pair[0]['blocks'][0]['output_sha256']==pair[1]['blocks'][0]['output_sha256'])
ck('independent oracle exact eight outputs, no injection',len(oracle)==8 and all(x['native_match'] and not x['output_injected'] for x in oracle))
ck('four poisoned SRAM controls',len(poison)==4 and all(x['blocks'][0]['returned'] and set(bytes.fromhex(x['blocks'][0]['RAM_before']))=={0xa5} for x in poison))
ck('poison does not affect output',all(x['blocks'][0]['output_sha256']==next(y['blocks'][0]['output_sha256'] for y in traces if x['variant']==y['variant'] and x['entry']==y['entry']) for x in poison))
ck('native function controls preserve real code/input',len(micro)==8 and all(x['native_output_matches_oracle'] for x in micro if x['hookmode']!='read') and all(not x['native_output_matches_oracle'] for x in micro if x['hookmode']=='read'))
app_bad=next(x for x in micro if x['entry']=='application' and x['hookmode']=='read')
ck('first real application control-flow divergence captured',app_bad['first_trace_difference']['control']['pc']=='0x80596e4' and app_bad['first_trace_difference']['instrumented']['pc']=='0x80596e8')
ck('native data-free NOR IRQ service only',len(nor)==4 and all([x['opcode'] for x in row['NOR_commands']]==['0xf5','0x35','0xb7','0xaf'] and len(row['native_IRQs'])==3 for row in nor))
ck('identity and timing assumptions separated',len(ident)==4 and all(x['NOR_identity_model'] for x in ident) and len(ticks)==4 and all(x['tick_model'] for x in ticks))
ck('further stock/candidate stops agree',all(x['stop']['pc']==('0x801c63c' if x['entry']=='application' else '0x80031c4') for x in ticks+baseline))
ck('native Main setup is not Main/Storage execution',all('0x801ddd4' in x['milestones'] and '0x801d4b0' not in x['milestones'] and '0x805767c' not in x['milestones'] for x in ticks+baseline if x['entry']=='application'))
for entry in ('application','bootloader'):
 group=[x for x in ticks+baseline if x['entry']==entry]
 ck(entry+' official stock/B13/candidate checkpoint equality',len(group)==3 and len({x['RAM_sha256'] for x in group})==1)
ck('six prior-failure SRAM seed cases',len(restart)==6 and {x['prior_case'] for x in restart}=={'B tef0','C tef4','D tef7','E missing0','F missing4','G missing7'})
ck('native prefix reinitializes semaphore/sync/pending/flags',all(x['initialized_ownership_prefix']['semaphore']==1 and x['initialized_ownership_prefix']['sync']==0 and x['initialized_ownership_prefix']['pending']==0 and x['initialized_ownership_prefix']['Storage_flags']==0 and x['initialized_ownership_prefix']['Main_flags']==0 for x in restart))
ck('native prefix reinitializes DMA runtime',all(int(x['runtime_fields']['0x400264b8'],16)&1==0 and int(x['runtime_fields']['0x400264bc'],16)==0 for x in restart))
ck('complete ownership and preservation not falsely qualified',all(x['full_P2'].startswith('UNKNOWN') and x['full_P3'].startswith('UNKNOWN') and not x['stable_user_state'] for x in restart))
all_rows=traces+poison+nor+ident+ticks+baseline+restart
ck('code unchanged in every final control/replay',all(x['code_unchanged'] for x in all_rows))
ck('observed-prefix target counts zero only in covered prefix',all(x['target_counts_observed_prefix']==dict(reads=0,writes=0,erase_overlaps=0) and x['target_counts_complete_boot'] is None for x in all_rows))
ck('no synthesized array bytes/automatic diagnostic read',all(all(int(c['opcode'],16) in (0xf5,0x35,0xb7,0xaf) for c in x['NOR_commands']) for x in all_rows))
ck('no false stable checkpoint',all(not x['stable_user_state'] for x in all_rows))
log=read(O/'run-log.json');ck('eleven final evidence scripts succeed',len(log)==11 and all(x['exit_code']==0 for x in log))
ck('no firmware/binary/SYX outputs',not any(p.suffix.lower() in ('.bin','.syx','.hex') for p in O.rglob('*') if p.is_file()))
module=Path(unicorn.__file__);dll=module.parent/'lib/unicorn.dll'
result=dict(confidence='PROVEN',scope='Decompression observer fix and native cold-start prefixes; not full cold boot',checks=checks,validation_checks=len(checks),
 startup_decompression='PROVEN repaired with no firmware/output/PC bypass',gates=dict(H1='UNKNOWN',H2='UNKNOWN',P1='PROVEN within prior diagnostic graph',P2='UNKNOWN',P3='UNKNOWN',P4='PROVEN code unchanged'),
 observed_prefix_target_counts=dict(reads=0,writes=0,erase_overlaps=0),complete_boot_target_counts=None,
 native_decompression_controls=8,poison_controls=4,isolated_function_controls=8,restart_prefix_cases=6,
 model_runtime=dict(Python=sys.version,unicorn_version=unicorn.__version__,unicorn_module=str(module),DLL_sha256=sha(dll) if dll.exists() else None),
 reference_inputs_unchanged=451,pinned_sources_unchanged=183,prior_evidence_unchanged=True,hardware_access=False,firmware_generated=False,
 verdict='UNQUALIFIED',report_sha256=sha(R/'notes/qspi82000-hardware-readiness.md'),preservation_report_sha256=sha(R/'notes/qspi82000-preservation-powercycle.md'),
 evidence_sha256={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name!='validation.json'})
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','evidence_sha256','model_runtime')},indent=2))
