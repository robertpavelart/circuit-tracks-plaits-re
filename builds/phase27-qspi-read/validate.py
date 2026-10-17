"""Final evidence consistency. Does not communicate with devices or build firmware."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((O/'patch-plan.json').read_text());t=json.loads((O/'offline-test-result.json').read_text());a=json.loads((O/'stock-audit.json').read_text())
assert len(t['checks'])==197 and len(t['runs'])==6
assert not t['hardware_IO'] and not t['original_QSPI_bytes_used']
assert all(x['frames']==9 and len(x['calls'])==1 and x['calls'][0][1]==0x82000 and x['calls'][0][3]==512 and x['max_stack_observed']==724 for x in t['runs'])
assert p['append']['bytes']==802 and p['total_patch_bytes']==810
assert sha(O/'arm-diagnostic.fragment.bin')==p['append']['sha256']
assert not p['candidate_image_generated'] and not p['candidate_SYX_generated'] and p['candidate_build_sha256'] is None
assert a['expected_postpackaging_size']==436024 and a['padded_application_end']=='0x807a738'
assert not a['transaction_QSPI_program_commands'] and not a['transaction_QSPI_erase_commands']
assert a['bootloader_size_reject_at']=='0x70001'
sys.path.insert(0,str(O));from protocol import *
r=Receiver(39)
for f in split_stream((O/'synthetic-transcript.syx').read_bytes()):r.accept(f)
assert r.result()==(O/'synthetic-data.bin').read_bytes()
host=O/'synthetic-host-output';assert (host/NAME).read_bytes()==r.result()
assert 'SYNTHETIC' in json.loads((host/(NAME+'.json')).read_text())['origin']
old=json.loads((R/'builds/phase20i-authentic-qualification/provenance.json').read_text())
assert all(sha(Path(n))==h for n,h in old['reference_before'].items())
pin=json.loads((R/'plaits/upstream/source-manifest.json').read_text())
assert all(sha(R/'plaits/upstream'/x['path'])==x['sha256'] for x in pin['files'])
prev=R/'builds/phase26-qspi82000';v=json.loads((prev/'validation.json').read_text())
assert all(sha(prev/n)==h for n,h in v['evidence_sha256'].items())
assert sha(R/'notes/p0282-0386-reclaim-qualification.md')==v['qualification_note_sha256']
note=R/'notes/qspi82000-read-diagnostic.md'
assert note.read_text(encoding='utf8').rstrip().endswith('QSPI82000 READ DIAGNOSTIC = UNQUALIFIED')
closure=dict(confidence='UNKNOWN',scope='Full hardware read-only closure remains unqualified',
 proven_selected_path=['entry/command','0x08022f94','0x08037430','0x0803769c','0x08022746'],
 excluded_mutators=['0x08022fdc','0x08037494','0x080374d4','generic storage queue drain'],
 admitted_indirect_callback=dict(dispatch='0x0801c894',count=1,target='0x08057651',guarded=True),
 open_boundaries=['Real OS wait 0x0801be1a and preemption','Real DMA/IRQ completion and stack/cache accessibility','MIDI port vtable implementations below 0x08020c90','Updater staging/erase footprint and original target preservation'],
 runtime_NOR_read_transaction='PROVEN: EB/EC indirect read only',
 whole_firmware_global_no_write_claim=False,hardware_admitted=False)
(O/'read-only-closure.json').write_text(json.dumps(closure,indent=2)+'\n')
result=dict(confidence='PROVEN',scope='Offline consistency only',checks=197,successful_ARM_cases=6,
 reference_inputs_unchanged=len(old['reference_before']),pinned_files_unchanged=len(pin['files']),
 phase26_unchanged=True,range_qualification_note_unchanged=True,
 evidence_sha256={str(x.relative_to(O)):sha(x) for x in O.rglob('*') if x.is_file() and x.name!='validation.json'},
 report_sha256=sha(note),candidate_firmware_created=False,hardware_access=False,
 diagnostic_verdict='UNQUALIFIED')
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PROVEN: 197 offline checks / 6 ARM cases; reference451 + pinned183 + phase26 unchanged; no hardware/firmware package; diagnostic UNQUALIFIED')
