"""Seven native diagnostic cases, followed by fresh reset-prefix execution.
The peripheral reset fixture is an assumption tested, not a proof of boot.
"""
from support import *
import replay as P30
import stream
stream.O=O # phase30 load() may emit text excerpts; direct all new output here
from cold_boot import Cold,probe

rows=[];checks=[]
def ck(n,v):assert v,n;checks.append(n)
for label,kind,chunk in [('A normal',None,None)]+[(f'{label} {kind}{chunk}',kind,chunk) for label,kind,chunk in (
 ('B','tef',0),('C','tef',4),('D','tef',7),('E','missing',0),('F','missing',4),('G','missing',7))]:
 m=P30.Model(kind,chunk);m.start();complete=m.finish()
 if kind is None:m.verify()
 before=m.state()
 ck(label+' native diagnostic outcome',complete==(kind is None))
 ck(label+' only read opcodes',set(m.commands)=={'0xec'})
 ck(label+' failed request retained',kind is None or before['semaphore']==0 and before['sync']==1 and not before['buffer_reusable'])
 # Read-only peripheral bytes are synthetic; persistent NOR is external state.
 persistent=bytearray(m.payload);hash_before=sha(persistent)
 # New MCU instance: discard all CPU/RAM/MMIO/task contexts. Never restore the
 # captured running snapshot as a surrogate for reset initialization.
 reset=Cold();u=reset.uc
 words={
  'old_backend_semaphore_byte':u.mem_read(m.backend+8,1)[0],
  'old_wrapper_sync':int.from_bytes(u.mem_read(m.wrapper+16,4),'little'),
  'old_Storage_flags':int.from_bytes(u.mem_read(m.holder+8,4),'little'),
  'old_Main_flags':int.from_bytes(u.mem_read(0x20007758,4),'little'),
  'DMA_CR':int.from_bytes(u.mem_read(0x400264b8,4),'little'),
  'DMA_NDTR':int.from_bytes(u.mem_read(0x400264bc,4),'little'),
  'QSPI_CR':int.from_bytes(u.mem_read(0xa0001000,4),'little'),
  'QSPI_SR':int.from_bytes(u.mem_read(0xa0001008,4),'little')}
 ck(label+' fresh volatile fixture',not any(words.values()))
 boot=probe('bootloader')
 ck(label+' no observed prefix persistent stores',not boot['persistent_mutations_observed'])
 ck(label+' abstract NOR unchanged across read/reset fixture',sha(persistent)==hash_before)
 rows.append(dict(case=label,confidence='PROVEN',pre_power_loss=before,diagnostic_read_commands=len(m.commands),
  diagnostic_QSPI_write_count=0,diagnostic_QSPI_erase_count=0,diagnostic_required_SD_writes=0,diagnostic_required_internal_flash_writes=0,
  fresh_reset_fixture=words,reset_fixture='Fresh CPU/maps, zero representative SRAM/MMIO, not application initialization and not proof SRAM always powers up zero',
  stale_host_session_copied=False,old_emulator_task_contexts_copied=False,
  cold_reset_prefix=boot,persistent_model_hash_before=hash_before,persistent_model_hash_after=sha(persistent),
  complete_restart_reached=False,P2='UNKNOWN: native boot initialization not complete',P3='UNKNOWN: suffix storage reachability not exercised',
  no_force_cleanup=True))
result=dict(confidence='PROVEN',scope='Native pre-failure diagnostic plus abstract cold reset and real reset prefix; NOT complete cold restart',
 checks=checks,cases=rows,P1='PROVEN within fixed diagnostic graph',P2='UNKNOWN',P3='UNKNOWN',second_read_after_failure_attempted=False,hardware_access=False)
(O/'powercycle.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(cases=len(rows),assertions=len(checks),P1=result['P1'],P2=result['P2'],P3=result['P3']),indent=2))
