"""Validate evidence and stop-rule compliance, not an unexecuted convergence."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(name,ok):assert ok,name;checks.append(name)
for phase in ('phase26-qspi82000','phase27-qspi-read','phase28-hardware-readiness','phase29-storage-wrapper','phase30-chunked-storage','phase31-storage-error-recovery','phase32-host-containment','phase33-preservation-powercycle','phase34-startup-decompression','phase35-svc-context','phase36-pendsv-context','phase37-systick','phase38-nor81000'):
 p=R/'builds'/phase;v=read(p/'validation.json')
 ck(phase+' evidence unchanged',all(sha(p/n)==h for n,h in v['evidence_sha256'].items()))
prior=read(R/'builds/phase38-nor81000/validation.json')
for label,name,key in (('preservation','qspi82000-preservation-powercycle.md','preservation_report_sha256'),('readiness','qspi82000-hardware-readiness.md','report_sha256')):
 a=O/f'phase38-{label}-before.md';p=R/'notes'/name
 ck(label+' archive exact',sha(a)==prior[key])
 ck(label+' earlier note retained',p.read_bytes().startswith(a.read_bytes()))
 ck(label+' correct final status',p.read_text(encoding='utf8').rstrip().endswith('NOR81000 SYMBOLIC BYTE14 QUALIFICATION = UNQUALIFIED'))
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
ck('451 reference inputs unchanged',len(ref)==451 and all(sha(Path(n))==h for n,h in ref.items()))
pins=read(R/'plaits/upstream/source-manifest.json')['files']
ck('183 pinned sources unchanged',len(pins)==183 and all(sha(R/'plaits/upstream'/p['path'])==p['sha256'] for p in pins))
code=read(O/'instruction-evidence.json');result=read(O/'result.json');order=read(O/'byte14-ordering.json');other=read(O/'other22-provenance.json')
native={x['address']:x for x in code['boot_reader']}
ck('exact native zero pair',native[0x08005dae]['mnemonic']=='movs' and native[0x08005dae]['operands']=='r2, #0' and native[0x08005db0]['mnemonic']=='strb' and native[0x08005db0]['operands']=='r2, [r4, #0xe]')
ck('byte14 address correct',int(order['byte14_address'],16)==0x2000546c+14)
ck('sequential Main proof remains limited',order['zeroing']['classification']=='NOT OBSERVABLE BEFORE ZEROING' and order['zeroing']['confidence']=='PROVEN only for immediate Main instruction pair')
ck('no global absence or actual observer fabricated',order['global_classification'].startswith('UNKNOWN') and order['first_observer'] is None)
ck('other22 is independent stop rule',order['stop_rule'].startswith('User section8'))
ck('two mapped RAM source identities checked',len(other['sources'])==2 and all(sha(Path(x['source_file']))==x['source_sha256'] for x in other['sources']))
for x in other['sources']:
 data=Path(x['source_file']).read_bytes()
 ck(Path(x['source_file']).name+' correct application cache layout',x['application_cache_candidate']=='0x20006868' and x['boot_cache']=='0x2000546c')
 ck(Path(x['source_file']).name+' exact two range observations',[(r['indices'],r['file_offset'],r['bytes']) for r in x['ranges']]==[([0,13],'0x6868',14),([15,22],'0x6877',8)])
 ck(Path(x['source_file']).name+' RAM-only values reproduce',all(data[int(r['file_offset'],16):int(r['file_offset'],16)+r['bytes']].hex()==r['observed_RAM_hex'] and hashlib.sha256(bytes.fromhex(r['observed_RAM_hex'])).hexdigest()==r['observed_RAM_sha256'] for r in x['ranges']))
 ck(Path(x['source_file']).name+' no request history assumed',not x['accepted_observable_NOR_bytes'] and all(r['original_NOR_byte_equivalence']==r['this_exact_cold_boot_request_equivalence']=='UNKNOWN' for r in x['ranges']))
ck('both candidate ranges actually differ',all(other['candidate_range_equality'][str((a,b))] is False for a,b in ((0,13),(15,22))))
ck('no accepted original or read-equivalent bytes',other['accepted_original_NOR_bytes']==other['accepted_post_read_equivalent_bytes']==0)
mut=code['identity_mutator'];ck('native first14 mutator recorded',any(x['address']==0x08005eaa and x['operands']=='r2, #0xe' for x in mut) and any(x['address']==0x08005eac and x['mnemonic']=='bl' and x['operands']=='#0x8001858' for x in mut))
ck('zero exhaustive variants admitted',result['exhaustive_variants_tested']==0 and result['accepted_observable22'] is None and result['original_byte14_value'] is None)
ck('no unsupported semantic statement or reconstruction',result['semantic_unobservability_statement_admitted'] is False and result['reconstructed_original_NOR_record'] is False)
ck('no completion/convergence success invented',result['native_completion'].startswith('UNKNOWN') and result['post_zero_convergence'].startswith('UNKNOWN') and result['verdict']=='UNQUALIFIED')
ck('no new boot execution claimed',result['stock_progression'].startswith('No new execution') and result['diagnostic_progression'].startswith('No new execution'))
ck('target counts explicitly inherited prefix only',result['target_counts']==dict(scope='Inherited executed prefix only; no newly reached post-completion prefix',reads=0,writes=0,erase_overlaps=0,full_boot=None))
ck('no runtime service/injection in prerequisite script','emu_start' not in (O/'audit.py').read_text() and 'mem_write' not in (O/'audit.py').read_text())
ck('no binary/firmware/NOR slice output',not any(p.suffix.lower() in ('.bin','.syx','.hex') for p in O.rglob('*') if p.is_file()))
v=dict(confidence='UNKNOWN',verdict='UNQUALIFIED',scope='Prerequisite ordering and other22 provenance only; no native completion or convergence replay',
 validation_checks=len(checks),checks=checks,exhaustive_variants_tested=0,accepted_observable_bytes=0,
 global_byte14_unobservable='UNKNOWN',first_proven_observer=None,completion_executed=False,new_boot_execution=False,
 gates=dict(H1='UNKNOWN',H2='UNKNOWN',P1='PROVEN within prior diagnostic scope',P2='UNKNOWN',P3='UNKNOWN',P4='PROVEN unchanged code'),
 observed_prefix_target_counts=dict(reads=0,writes=0,erase_overlaps=0),target_counts_scope='inherited executed prefix only',complete_boot_target_counts=None,
 hardware_access=False,firmware_generated=False,target_data_investigated=False,SDMMC_investigated=False,
 reference_inputs_unchanged=451,pinned_sources_unchanged=183,
 report_sha256=sha(R/'notes/qspi82000-hardware-readiness.md'),preservation_report_sha256=sha(R/'notes/qspi82000-preservation-powercycle.md'),
 evidence_sha256={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name!='validation.json'})
(O/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps({k:x for k,x in v.items() if k not in ('checks','evidence_sha256')},indent=2))
