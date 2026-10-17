"""Finalize hashes and validate saved evidence. No rebuild or hardware access."""
from pathlib import Path
import sys,json,hashlib,re,ast,importlib.metadata
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase42-exact-rdiag-integration'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 b=read(O/'build-results.json');iv=read(O/'independent-validation.json');install=read(O/'installation.json');native=read(O/'native-regression.json');heap=read(O/'heap-preflight.json');host=read(O/'capture-tool-tests.json');end=read(O/'final-host-roundtrip.json')
 syx=O/'circuittracks-4486-nor-evidence-test.syx';bin=syx.with_suffix('.bin')
 assert sha(syx)==b['inputs']['candidate_SYX']['sha256']==iv['SYX_sha256']==install['exact_SYX_sha256']
 assert sha(bin)==b['inputs']['candidate_BIN']['sha256']==iv['BIN_sha256']==install['candidate']['sha256']
 assert bin.read_bytes()==(O/'independently-decoded.bin').read_bytes()
 assert iv['details']['CRC']==b['inputs']['candidate_BIN']['CRC']==install['candidate']['CRC']=='0xac9987ba'
 assert heap['gate']=='PASS' and heap['fresh_boot_allocator_demand_delta_bytes']==0 and heap['fixed_reservation_capacity_delta_bytes']==-12
 assert b['roundtrip_BIN_equal'] and b['roundtrip_SYX_equal'] and iv['verdict']=='PASS'
 assert b['application_end_exclusive']=='0x806bc8c' and b['remaining_bytes']==82804
 assert install['installed_exact'] and install['bootloader_unchanged'] and install['complete_update_sequence']
 assert len(install['native_message_log'])==11751 and install['native_SysEx_block_unpack_calls']==11749 and install['native_worker_write_flag_checks']==11750
 assert all(x['reads']==x['writes']==x['erase_overlaps']==0 for x in install['preservation'].values())
 assert host['case_count']==25 and host['MIDI_ports_opened']==0
 assert end['result']['status']=='SUCCESS' and end['requests']==1 and sorted(end['lengths'].values())==[23,512]
 assert native['precommand']['latch']=='IDLE' and native['precommand']['diagnostic_Storage_requests']==0
 assert sum(x['opcodes_tested'] for x in native['opcode_sweeps'])==512
 assert not (O/'NOR-CAPTURE-ATTEMPT.json').exists(),'Live capture attempt marker must not exist in this phase'
 # Phase42 (including its notes) and all earlier pinned inputs remain immutable.
 prev=read(P/'validation.json')
 for name,h in prev['evidence_sha256'].items():assert sha(P/name)==h,('phase42 changed',name)
 for path,h in prev['notes_sha256'].items():assert sha(Path(path))==h,('prior note changed',path)
 pins=read(P/'inputs.json')['sources']
 for x in pins:
  original=Path(x['local']);copy=O/'source'/original.relative_to(P/'source')
  assert sha(Path(x['path']))==sha(original)==sha(copy)==x['sha256']
 ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before'];assert len(ref)==451
 assert all(sha(Path(p))==h for p,h in ref.items())
 upstream=read(R/'plaits/upstream/source-manifest.json')['files'];assert len(upstream)==183
 assert all(sha(R/'plaits/upstream'/x['path'])==x['sha256'] for x in upstream)
 earlier=[]
 for n in range(26,42):
  for p in (R/'builds').glob(f'phase{n}-*/validation.json'):
   assert all(sha(p.parent/name)==h for name,h in read(p)['evidence_sha256'].items());earlier.append(str(p.parent))
 # Write standard portable checksum lines, excluding checksum/self-validation
 # files to avoid recursive hash dependencies. Include all root artifacts and
 # the exact rollback file; source-tree pins are checked separately above.
 files=sorted([p for p in O.iterdir() if p.is_file() and p.name not in ('SHA256SUMS.txt','validation.json')]+list((O/'rollback').iterdir()),key=lambda p:p.relative_to(O).as_posix())
 (O/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.relative_to(O).as_posix()+'\n' for p in files))
 for line in (O/'SHA256SUMS.txt').read_text().splitlines():
  h,name=line.split('  ',1);assert sha(O/name)==h
 for p in O.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 links=[]
 for value in re.findall(r'\]\(<([^>]+)>\)',(O/'findings.md').read_text()):
  value=re.sub(r':\d+$','',value);target=Path(value)
  assert target.exists() or target==O/'validation.json',value;links.append(value)
 assert (O/'findings.md').read_text().rstrip().endswith('HARDWARE-TEST CANDIDATE = PASS')
 erases=[x for x in install['internal_operations'] if x['kind']=='ERASE'];writes=[x for x in install['internal_operations'] if x['kind']=='WRITE']
 assert [x['start'] for x in erases]==['0x8010000','0x8018000','0x8020000','0x8040000'] and len(writes)==93992
 assert all(int(x['start'],16)>=0x08010000 for x in writes+erases)
 result=dict(confidence='PROVEN',verdict='PASS',candidate_SYX=dict(bytes=syx.stat().st_size,sha256=sha(syx)),candidate_BIN=dict(bytes=bin.stat().st_size,sha256=sha(bin),CRC='0xAC9987BA'),application_end_exclusive='0x0806BC8C',image_headroom_bytes=82804,fresh_boot_allocation_demand_delta=0,heap_capacity_delta=-12,diff_changed_bytes_vs_SC35D8=1450,external_target_overlaps=install['preservation'],native_opcode_port_cases=512,host_cases=25,final_native_USB_to_final_host_roundtrip='PASS',exact_SYX_messages_replayed=11751,reference_files_unchanged=451,Plaits_sources_unchanged=183,phase43_pinned_source_copies=439,prior_validated_phases_unchanged=earlier,phase42_notes_unchanged=True,report_links_checked=len(links),SHA256SUMS_entries=len(files),hardware_access=False,MIDI_ports_opened=0,uploader_launched=False,firmware_transmitted=False,hardware_action_requires_separate_user_decision=True,remaining_unknowns=['Real boot/USB/DMA/WinMM timing','Actual fresh-boot headroom (allocation demand unchanged; capacity cost 12 bytes)','Complete cold-boot NOR preservation','Actual original NOR evidence bytes','Recovery of this candidate on this unit'],H4='FAIL; no in-session recovery; no retry; full power cycle after failure',toolchain=dict(python=sys.version,capstone=importlib.metadata.version('capstone'),unicorn=importlib.metadata.version('unicorn')),evidence_sha256={p.relative_to(O).as_posix():sha(p) for p in files},SHA256SUMS_sha256=sha(O/'SHA256SUMS.txt'))
 (O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('evidence_sha256','prior_validated_phases_unchanged','external_target_overlaps')},indent=2))
if __name__=='__main__':main()
