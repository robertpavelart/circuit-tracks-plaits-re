"""Read-only preservation/result checks; writes only this audit's manifest."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
prev=R/'builds/phase27-qspi-read';v=read(prev/'validation.json')
assert all(digest(prev/n)==h for n,h in v['evidence_sha256'].items())
assert digest(R/'notes/qspi82000-read-diagnostic.md')==v['report_sha256']
older=R/'builds/phase26-qspi82000';old=read(older/'validation.json')
assert all(digest(older/n)==h for n,h in old['evidence_sha256'].items())
assert digest(R/'notes/p0282-0386-reclaim-qualification.md')==old['qualification_note_sha256']
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
assert all(digest(Path(n))==h for n,h in ref.items())
pin=read(R/'plaits/upstream/source-manifest.json')['files']
assert all(digest(R/'plaits/upstream'/x['path'])==x['sha256'] for x in pin)
f=read(O/'full-handler-failure.json');i=read(O/'irq-context-result.json')
assert f['Main_flag']=='0x0' and f['Storage_flag']=='0x100' and f['controller_flag']=='0x1'
assert f['backend_semaphore']==0 and f['replies']==0 and not f['controller_flag_check_reached']
assert f['stopped_PC']=='0x801cdc8' and f['no_synthetic_wait_success'] and not f['hardware_access']
assert i['Storage_control_returns'] and i['Main_wait_blocks_despite_controller_complete']
s=read(O/'stack-probe-result.json');assert s['cases'][0]['total_observed_from_aligned_top']==852
assert s['cases'][0]['remaining_bytes_to_low_guard']==2212 and s['cases'][1]['status']=='guard detected insufficient headroom'
m=read(O/'midi-schedule-result.json')['cases']
assert [x['ticks'] for x in m]==[34,99,101,2]
assert all(x['USB_transfers']==33 and x['sysex_bytes']==1338 and x['USB_MIDI_bytes']==1784 for x in m[:2])
assert m[2]['sysex_bytes']==0 and m[3]['status']=='router returned after disconnect; no capture'
t=read(O/'storage-effects-result.json')
assert t['modeled_known_mutation_overlaps']==0 and t['whole_install_preservation'].startswith('NOT PROVEN')
assert t['payload_erase_end_exclusive']=='0x6b000' and t['maximum_staging_payload_write_end_exclusive']=='0x6a740'
assert t['metadata_erase_interval']==['0x80000','0x81000']
st=read(O/'static-evidence.json');assert len(st['stock_disassembly_spans'])==53
assert [x['file'] for x in st['stock_disassembly_spans'] if not x['B13_identical']]==['08021000.asm']
assert all(0x08021024<=int(a,16)<0x08021028 for a in st['DIN_changed_bytes'])
assert not any(x.suffix.lower() in ('.bin','.syx','.hex') for x in O.rglob('*') if x.is_file())
note=R/'notes/qspi82000-hardware-readiness.md'
assert note.read_text(encoding='utf8').rstrip().endswith('QSPI82000 HARDWARE READINESS = FAIL')
result=dict(confidence='PROVEN',scope='Offline evidence consistency and preservation',
 verdict='FAIL',installation_target_preservation='NOT PROVEN',first_boot_target_preservation='NOT PROVEN',
 gates={
 'H1':dict(confidence='UNKNOWN',passes=False,reason='Complete install mutation closure unproven'),
 'H2':dict(confidence='UNKNOWN',passes=False,reason='Complete first-boot mutation closure unproven'),
 'H3':dict(confidence='UNKNOWN',passes=False,reason='Bounded model 852 bytes / guard headroom 2212; full maximum unknown'),
 'H4':dict(confidence='PROVEN',passes=False,reason='Actual QSPI IRQ notifies Storage; actual Main handler waits Main'),
 'H5':dict(confidence='UNKNOWN',passes=False,reason='Actual router yields; no audio/deadline bound and stalled USB has no finite wait'),
 'H6':dict(confidence='PROVEN',passes=True,reason='Selected fixed diagnostic transaction read-only; not global runtime/deployment'),
 'H7':dict(confidence='PROVEN',passes=True,reason='Patch-plan bootloader/recovery code unchanged; actual unit recovery unknown')},
 phase27_files_unchanged=len(v['evidence_sha256']),phase27_note_unchanged=True,
 phase26_unchanged=True,range_note_unchanged=True,reference_inputs_unchanged=len(ref),pinned_files_unchanged=len(pin),
 candidate_firmware_generated=False,candidate_SYX_generated=False,hardware_access=False,
 evidence_sha256={str(x.relative_to(O)):digest(x) for x in sorted(O.rglob('*')) if x.is_file() and x.name!='validation.json'},
 report_sha256=digest(note))
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ('evidence_sha256','gates')},indent=2))
