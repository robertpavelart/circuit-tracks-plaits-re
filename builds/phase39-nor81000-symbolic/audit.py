"""Prerequisite audit only. Never constructs a NOR payload or services a read.

User stop condition: any missing other-byte provenance prevents 256-way replay.
"""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase33-preservation-powercycle'))
from support import ROM,STOCK,md,REF
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,v):(O/n).write_text(json.dumps(v,indent=2)+'\n')
def code(a,n):
 raw=ROM[a-0x08000000:a-0x08000000+n] if a<0x08010000 else STOCK[a-0x08010000:a-0x08010000+n]
 return [dict(address=i.address,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in md.disasm(raw,a)]
spans={
 'boot_reader':(0x08005d98,0x1c),'app_reader':(0x0802520c,0x1c),
 'sync_wait':(0x08005726,0x3c),'sync_read_return':(0x080058a8,0xc),
 'sync_read_epilogue':(0x08005900,4),'Storage_sync_clear':(0x0800582e,0x20),
 'Main_read_and_publish':(0x08003a3e,0x2c),'identity_mutator':(0x08005ea6,0x18),
 'first_consumer':(0x08005dd8,0x30),'response_consumer':(0x08005e7a,0xc)}
decoded={k:code(a,n) for k,(a,n) in spans.items()}
for name,lines in decoded.items():
 (O/f'{name}.asm').write_text('\n'.join(f"{x['address']:08x}: {x['mnemonic']:8} {x['operands']}" for x in lines)+'\n')
save('instruction-evidence.json',decoded)
old=json.loads((R/'builds/phase38-nor81000/candidate-catalog.json').read_text())
checks=[];rows=[]
for name,loader,line in (('ram_dump_firmware_0x08037988.bin','emu_sc05.py',[9,10,23]),('dumpCT_ram_0x20000000.bin','emu_shared_channels.py',[21,40,41])):
 p=REF/'ctre/Firmware-Analysis'/name;b=p.read_bytes()
 prior=next(x for x in old['focused_rehashed'] if Path(x['path'])==p)
 assert sha(b)==prior['sha256']
 # The application reader's literal names its own destination. Reusing the
 # bootloader's 546c offset in an application RAM dump would be a layout error.
 literal=int.from_bytes(STOCK[0x15248:0x1524c],'little');assert literal==0x20006868
 observed=[]
 for first,last in ((0,13),(15,22)):
  a=literal+first;offset=a-0x20000000;v=b[offset:offset+last-first+1]
  observed.append(dict(indices=[first,last],candidate_RAM_address=hex(a),file_offset=hex(offset),bytes=len(v),
   observed_RAM_hex=v.hex(),observed_RAM_sha256=sha(v),confidence='PROVEN file bytes at loader-assigned SRAM offset',
   original_NOR_byte_equivalence='UNKNOWN',this_exact_cold_boot_request_equivalence='UNKNOWN',
   no_intervening_transformation='UNKNOWN: acquisition timing and identity-edit history not established'))
 rows.append(dict(source_file=str(p),source_sha256=sha(b),loader=str(REF/'tools'/loader),loader_lines=line,
  documented_address_space='ARM SRAM assigned at 20000000 by loader; not NOR capture',
  application_cache_candidate='0x20006868',boot_cache='0x2000546c',
  source_timing='UNKNOWN; no acquisition/register trace establishes cache population and intervening writes',
  ranges=observed,accepted_observable_NOR_bytes=False))
same={str((lo,hi)):rows[0]['ranges'][j]['observed_RAM_hex']==rows[1]['ranges'][j]['observed_RAM_hex'] for j,(lo,hi) in enumerate(((0,13),(15,22)))}
save('other22-provenance.json',dict(confidence='UNKNOWN',sources=rows,candidate_range_equality=same,
 accepted_original_NOR_bytes=0,accepted_post_read_equivalent_bytes=0,
 evidence_limit='A matching or plausible RAM cache is not acquisition history; reader equivalence and unchanged bytes through capture are unproved.',
 first14_mutation_path=dict(entry='08005E88',destination_load='08005EA6 object+8',length=14,copy_call='08005EAC -> 08001858',
  qualification='PROVEN static potential mutator; UNKNOWN whether it ran before either capture'),
 trailing8=dict(indices=[15,22],reader_modifies=False,capture_history_proven=False)))
ordering=dict(confidence='UNKNOWN',byte14_address='0x2000547a',
 zeroing=dict(address='0x08005db0',instruction='strb r2, [r4, #0xe]',preceding='0x08005dae movs r2, #0',
  classification='NOT OBSERVABLE BEFORE ZEROING',confidence='PROVEN only for immediate Main instruction pair'),
 global_classification='UNKNOWN; NOT OBSERVABLE BEFORE ZEROING is not globally qualified',
 first_observer=None,
 findings=[
  dict(scope='Immediate synchronous Main continuation',confidence='PROVEN',result='MOVS zero then STRB; no intervening payload load/copy/compare/checksum/branch/call'),
  dict(scope='Current queued request callback',confidence='PROVEN',result='Both callback/context fields are zero in phase38; no request callback payload read is established'),
  dict(scope='Known identity constructor and pointer publication',confidence='PROVEN static order',result='Main reaches 08003A46 and constructor 08005DD8 only after 08005DB0; formatting pointer publication 08005F9A follows that'),
  dict(scope='Completion to Main return, other tasks, IRQ/DMA/indirect aliases',confidence='UNKNOWN',result='Storage owns execution before Main resumes; prior completion path remains unexecuted. No all-task/all-IRQ observer closure or protected atomic interval is proven.'),
  dict(scope='Full prezero observer enumeration',confidence='UNKNOWN',result='Stopped at independent other22 provenance failure; no claim that absence in Main proves global absence.')],
 stop_rule='User section8: stop if any other22 byte lacks sufficient provenance')
save('byte14-ordering.json',ordering)
result=dict(confidence='UNKNOWN',verdict='UNQUALIFIED',
 reason='Other22 bytes lack request-linked capture history/untransformed-value proof; concurrency-wide byte14 non-observability also unqualified',
 original_byte14_value=None,accepted_observable22=None,exhaustive_variants_tested=0,
 post_zero_convergence='UNKNOWN: prerequisite gate failed, not executed',native_completion='UNKNOWN: not executed',
 stock_progression='No new execution; preserved phase38 boundary 080051C2',diagnostic_progression='No new execution; preserved phase38 boundary 080051C2',
 semantic_unobservability_statement_admitted=False,reconstructed_original_NOR_record=False,
 target_counts=dict(scope='Inherited executed prefix only; no newly reached post-completion prefix',reads=0,writes=0,erase_overlaps=0,full_boot=None),
 next_blocker='Proven values/history for the other22 bytes, plus complete concurrent prezero observer closure',
 no_hardware=True,no_firmware=True,no_payload_constructed=True)
save('result.json',result)
print(json.dumps(dict(verdict=result['verdict'],candidate_range_equality=same,accepted_observable22=0,variants_tested=0),indent=2))
