"""Finalize bounded model evidence without changing any candidate or old verdict."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase63-defect-closure';B=0x08010000
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda n:json.loads((O/n).read_text())
c=json.loads((P/'development-identity.json').read_text());image=(P/(c['candidate']+'.bin')).read_bytes();assert sha(image)==c['BIN_sha256']
assert sha((P/(c['candidate']+'.syx')).read_bytes())==c['SYX_sha256']
preserved=[]
for line in (P/'SHA256SUMS.txt').read_text().splitlines():
 h,n=line.split('  ',1);assert sha((P/n).read_bytes())==h,n;preserved.append(n)
x=load('continuity.json');assert x['candidate_sha256']==c['BIN_sha256']
assert x['frontier']['type']=='UnknownPeerRead' and '200100' in x['frontier']['message']
assert x['record']=='110000000180003480908f01'
assert load('model-tests.json')['passed'] and load('peer-tests.json')['passed']
baseline=(R/'builds/phase43-hardware-test-candidate/clean-sc35d8.bin').read_bytes()
regions=[]
for at,n in [(0x08029190,0x570),(0x08037770,0x298),(0x08048164,0x60),(0x0803b9d8,0x110)]:
 actual=image[at-B:at-B+n];assert actual==baseline[at-B:at-B+n]
 regions.append(dict(start=hex(at),bytes=n,sha256=sha(actual),same_as_clean_SC35D8=True))
(O/'identity-preservation.json').write_text(json.dumps(dict(confidence='PROVEN',BIN_sha256=c['BIN_sha256'],SYX_sha256=c['SYX_sha256'],phase63_manifest_entries_unchanged=len(preserved),new_firmware_images_generated=0,firmware_modified=False,reference_repository_modified=False,SPI2_driver_and_DSP_host_routines=regions),indent=2)+'\n')
alloc=[i for i in x['operations'] if i['kind']=='allocation request'];calls=[i for i in x['calls'] if i['target'] in ('0x801cfa4','0x801d7d8','0x801d808')]
(O/'allocation-prefix.json').write_text(json.dumps(dict(confidence='PROVEN',candidate_sha256=c['BIN_sha256'],observed_requests=len(alloc),requests=alloc,allocation_calls=calls,heap_cursor=x['heap_cursor'],heap_limit=x['heap_limit'],record=x['record'],complete_postboot_coverage=False,diagnostic_raw_buffer_created=False,host_transport_session_started=False,scope='Continuous startup prefix only. No final hardware headroom or all-caller allocation closure is claimed.'),indent=2)+'\n')
(O/'milestones.json').write_text(json.dumps(dict(confidence='PROVEN',candidate_sha256=c['BIN_sha256'],milestones=[i for i in x['events'] if 'milestone' in i or i.get('event')=='first scheduler architectural launch boundary'],final_record=x['record'],USB_ready=False,geometry_query=False,authorization=False,raw_capture_start=False,no_intermediate_fixture_splice=True),indent=2)+'\n')
registers={0:'CR1',4:'CR2',8:'SR',12:'DR',16:'CRCPR',20:'RXCRCR',24:'TXCRCR',28:'I2SCFGR',32:'I2SPR'}
lines=['# Authenticated startup SPI2 accessors','',f"Candidate BIN SHA-256 `{c['BIN_sha256']}`. **PROVEN** observed accesses, not global whole-program or post-frontier completeness.",'','| Instruction | Access | Register | Observed values | Count |','|---|---|---|---|---:|']
for e in x['SPI2']['accessors']:
 off=int(e['register'],16)-0x40003800;lines.append(f"|`{e['PC']}`|{e['access']}|{registers[off]} `{e['register']}`|"+', '.join(f'`{v:X}`' for v in e['values'])+f"|{e['count']}|")
lines+=['','**PROVEN branch semantics:**37970 reads SR,37972 shifts bit1 to sign,37974 BPL skips transmit when TXE=0;3797C STRB enqueues DR.37986 reads SR,37988 shifts bit0 to sign,3798A BPL retries when RXNE=0;3798C LDRB consumes DR.37994/37998 compare byte counters with requested length; only all bytes sent and received permit3799C/3799E return.','', 'CR1 mode/SPE and CR2 DS/FRXTH/DMA configuration are executed at48164 and37858/379A0/379B0. I2SCFGR is read/written by481B6/481BC to keep SPI mode. DMA programming and IRQ helpers are listed separately; modeled DMA transactions are not miscounted as CPU DR instructions.','', 'Relevant authenticated listings: candidate-08037770.asm, candidate-08037960.asm, candidate-08048164.asm, candidate-080291b8.asm, candidate-0803b9d8.asm, candidate-08057532.asm. accessor-audit.json records direct BL/literal candidates. Empty short contexts caused by starting disassembly inside a32-bit instruction are not independently authenticated boundaries; use complete function listings.','', '**UNKNOWN:** accessors reachable only after the deferred DSP task frontier have not executed. The table is complete for instrumented block accesses in this prefix, not a claim that the rest of normal boot has no other accessors.']
(O/'accessors.md').write_text('\n'.join(lines)+'\n')
result=dict(verdict='UNQUALIFIED',confidence='UNKNOWN',candidate_BIN_sha256=c['BIN_sha256'],SPI2_register_subset='PROVEN by four bounded native helper tests and traced startup',startup_continuity='UNKNOWN beyond SHI 16-bit width transition200100 and subsequent bulk-DMA/generated-table service',postboot_allocation_coverage='UNKNOWN',new_firmware_defect_demonstrated=False,frontier_classification='A — missing DSP peer16-bit bulk-transfer and table-job model',frontier=x['frontier'],model_tests=4,peer_contract_tests=len(load('peer-tests.json')['cases']),phase63_preserved_files=len(preserved),hardware_access=False,MIDI_ports_opened=0,firmware_transmitted=False,hardware_test_eligible=False)
(O/'preflight-verdict.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
