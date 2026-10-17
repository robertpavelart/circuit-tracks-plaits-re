"""Independent consistency/overlap/preservation assertions; no hardware I/O."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(n,v):assert v,n;checks.append(n)
for phase in ('phase26-qspi82000','phase27-qspi-read','phase28-hardware-readiness','phase29-storage-wrapper','phase30-chunked-storage','phase31-storage-error-recovery','phase32-host-containment'):
 p=R/'builds'/phase;v=read(p/'validation.json')
 ck(phase+' evidence unchanged',all(sha(p/n)==h for n,h in v['evidence_sha256'].items()))
v32=read(R/'builds/phase32-host-containment/validation.json')
ck('phase32 report archive exact',sha(O/'phase32-report-before.md')==v32['report_sha256'])
note=R/'notes/qspi82000-hardware-readiness.md';focused=R/'notes/qspi82000-preservation-powercycle.md'
ck('prior readiness text unchanged',note.read_bytes().startswith((O/'phase32-report-before.md').read_bytes()))
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
ck('451 reference inputs unchanged',len(ref)==451 and all(sha(Path(n))==h for n,h in ref.items()))
pins=read(R/'plaits/upstream/source-manifest.json')['files']
ck('183 pinned files unchanged',len(pins)==183 and all(sha(R/'plaits/upstream'/p['path'])==p['sha256'] for p in pins))
i=read(O/'installation.json');p=read(O/'powercycle.json');b=read(O/'cold-boot-prefix.json');a=read(O/'address-and-reachability.json');rec=read(O/'recovery.json')
ops=i['operations'];internal=i['internal_operations']
ck('current phase30 memory-only prototype size',i['candidate']['bytes']==441576 and i['candidate']['padded_bytes']==441600 and not i['candidate']['file_generated'] and not i['candidate']['SYX_generated'])
ck('13800 actual ARM packet decodes',i['native_SysEx_block_unpack_calls']==13800)
writes=[x for x in ops if x['kind']=='WRITE'];erases=[x for x in ops if x['kind']=='ERASE']
ck('13801 NOR programs / 109 erases',len(writes)==13801 and len(erases)==109)
def overlap(x):return int(x['start'],16)<0x82200 and int(x['end_exclusive'],16)>0x82000
ck('independent zero write overlaps',sum(map(overlap,writes))==0 and i['target_write_count']==0)
ck('independent zero erase overlaps',sum(map(overlap,erases))==0 and i['target_erase_overlap']==0)
blocks=writes[:-1]
ck('every staged block once, vector last',[int(x['start'],16) for x in blocks]==list(range(32,441600,32))+[0] and all(x['length']==32 for x in blocks))
ck('native 4KiB erase loop plus metadata',[int(x['start'],16) for x in erases]==list(range(0,0x6c000,4096))+[0x80000] and all(x['length']==4096 for x in erases))
ck('23-byte metadata exact range',writes[-1]['start']=='0x80000' and writes[-1]['end_exclusive']=='0x80017')
iw=[x for x in internal if x['kind']=='WRITE'];ie=[x for x in internal if x['kind']=='ERASE']
ck('installer actually programmed 110400 consecutive words',len(iw)==110400 and [int(x['start'],16) for x in iw]==list(range(0x08010000,0x0807bd00,4)))
ck('installer erased four exact sectors',[(int(x['start'],16),int(x['end_exclusive'],16)) for x in ie]==[(0x08010000,0x08018000),(0x08018000,0x08020000),(0x08020000,0x08040000),(0x08040000,0x08080000)])
ck('out-of-range internal erase does nothing',len([x for x in internal if x['kind']=='NOOP'])==1)
ck('selected install byte exact / boot immutable',i['installed_exact'] and i['bootloader_unchanged'])
ck('synthetic target survives selected installation',i['target']['before_sha256']==i['target']['after_sha256'])
ck('complete install not falsely claimed',not i['complete_update_sequence'] and i['H1'].startswith('UNKNOWN'))
ck('seven actual diagnostic cases / 42 assertions',len(p['cases'])==7 and len(p['checks'])==42)
ck('pre-power-loss only EC reads',[(x['diagnostic_read_commands']) for x in p['cases']]==[8,1,5,8,1,5,8] and all(x['diagnostic_QSPI_write_count']==x['diagnostic_QSPI_erase_count']==x['diagnostic_required_SD_writes']==x['diagnostic_required_internal_flash_writes']==0 for x in p['cases']))
ck('failed native transactions still quarantined',all(x['pre_power_loss']['semaphore']==0 and x['pre_power_loss']['sync']==1 and not x['pre_power_loss']['buffer_reusable'] for x in p['cases'][1:]))
ck('no cleanup or same-boot second request',not p['second_read_after_failure_attempted'] and all(x['no_force_cleanup'] for x in p['cases']))
ck('fresh reset maps not a running RAM snapshot',all(not x['old_emulator_task_contexts_copied'] and not x['cold_reset_prefix']['running_RAM_snapshot_imported'] for x in p['cases']))
ck('complete reset explicitly unknown',p['P2']=='UNKNOWN' and p['P3']=='UNKNOWN' and all(not x['complete_restart_reached'] for x in p['cases']))
ck('six reset probes including stock controls',len(b['probes'])==6 and len([x for x in b['probes'] if x['variant']=='stock'])==2)
ck('no false stable application state',all(not x['stable_USB_MIDI_state_reached'] and x['complete_first_boot_target_writes'] is None and x['complete_first_boot_target_erase_overlap'] is None for x in b['probes']))
ck('stock and diagnostic prefix stops match',len({x['stop']['pc'] for x in b['probes'] if x['entry']=='bootloader'})==1 and len({x['stop']['pc'] for x in b['probes'] if x['entry']=='application'})==1)
ck('all eight native recovery predicates',len(rec['cases'])==8 and all(x['boot_mode_flag']==int(x['pressed_bits']==7) for x in rec['cases']))
ck('no hardware/firmware artifact files',not any(x.suffix.lower() in ('.bin','.syx','.hex') for x in O.rglob('*') if x.is_file()))
ck('both reports end with required verdict',all(x.read_text(encoding='utf8').rstrip().endswith('QSPI ONE-SHOT HARDWARE MODEL = UNQUALIFIED') for x in (note,focused)))
result=dict(confidence='PROVEN',scope='Scoped offline storage/installer evidence and honest cold-start coverage limits',checks=checks,validation_checks=len(checks),
 gates=dict(H1='UNKNOWN',H2='UNKNOWN',P1='PROVEN within selected diagnostic graph',P2='UNKNOWN',P3='UNKNOWN',P4='PROVEN code unchanged; recovery operation UNKNOWN'),
 install_target_write_count=0,install_target_erase_overlap=0,first_boot_target_reads=None,first_boot_target_writes=None,first_boot_target_erase_overlap=None,
 powercycle_cases=7,powercycle_assertions=42,cold_prefix_probes=6,recovery_predicates=8,verdict='UNQUALIFIED',
 reference_inputs_unchanged=451,pinned_sources_unchanged=183,prior_evidence_unchanged=True,
 hardware_access=False,firmware_exported=False,SYX_generated=False,
 report_sha256=sha(note),preservation_report_sha256=sha(focused),
 evidence_sha256={str(x.relative_to(O)):sha(x) for x in sorted(O.rglob('*')) if x.is_file() and x.name!='validation.json'})
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','evidence_sha256')},indent=2))
