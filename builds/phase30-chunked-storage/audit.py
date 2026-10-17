"""Physical allocation, stock-interface and source evidence; no firmware output."""
from environment import *
import re
e=Physical()
heap=dict(before=dict(limit=hex(e.r32(0x20002b44)),cursor=hex(e.r32(0x20002b48))))
heap['retained_state_return']=hex(e.call(0x0805dbdc))
heap['after_B13_reservation']=dict(limit=hex(e.r32(0x20002b44)),cursor=hex(e.r32(0x20002b48)),available=e.r32(0x20002b44)-e.r32(0x20002b48))
try:e.call(0x0801cfa4,64,0x08026b22)
except Exception as exc:heap['64_byte_attempt_after_reservation']=dict(error=str(exc),PC=hex(e.uc.reg_read(UC_ARM_REG_PC)),returned=False)
else:raise AssertionError('64 bytes unexpectedly available')
e2=Physical();p=e2.call(0x0801cfa4,64,0x08026b22);r=e2.call(0x0805dbdc)
heap['64_bytes_before_reservation']=dict(pointer=hex(p),cursor_after=hex(e2.r32(0x20002b48)),retained_feature_state_return=hex(r),effect='Retained feature disabled by its guard, not an acceptable free-heap claim')
e=Physical();parser=e.r32(e.r32(0x200068bc));desc=e.r32(parser+36);buf=e.r32(desc+4)
wrapper=e.r32(0x20006968);backend=e.r32(wrapper+4);vt=e.r32(backend)
listing=(REF/'re/app.asm').read_text()
refs={x:[l for l in listing.splitlines() if re.search(r'\bbl\s+#'+x+r'\b',l)] for x in ('0x8035c58','0x8037596','0x801cdc8','0x8022746')}
replay=json.loads((O/'replay-result.json').read_text());edges=sorted(set(tuple(x) for c in replay['cases'] for x in c['details']['constrained_call_edges']))
result=dict(confidence='PROVEN',scope='Physical fixture ownership and selected stock-driver closure; not a deployment admission',heap=heap,
 buffer=dict(parser=hex(parser),descriptor=hex(desc),allocation=hex(buf),capacity=e.r32(parser+16),payload=hex(buf+32),payload_bytes=64,
  raw_guards=[hex(buf+28),hex(buf+96)],owner='Stock Main SysEx parser; exclusively lent while its callback frame remains alive',
  lifetime='Main callback remains suspended, never returns until read and output drain; restores all 232 request bytes on every returning exit',
  original_writers='0x08035c58; direct callers 0x08020f62 and 0x08020ffc',
  diagnostic_writers='DMA modeled after real stock command; local guards; request restoration after no DMA active',
  alignment=(buf+32)%32,alignment_bytes=16,physical_domain='DTCM within 0x20000000..0x2000ffff',
  async_returning_Main_supported=False,full_concurrent_input_IRQ_workload='UNKNOWN'),
 new_RAM=dict(new_heap_bytes=0,borrowed_payload_bytes=64,command_frame_bytes=188,command_saved_register_bytes=20,validator_saved_bytes=32,
  command_frame=dict(output_descriptor=8,stream_crc_state=4,packet_with_padding=164,canaries=8,padding=4),
  request_bytes=24,request_lifetime='Existing stock read-wrapper stack -> queue copy -> worker copy',new_persistent_global_bytes=0),
 backend_methods=[dict(offset=hex(i),target=hex(e.r32(vt+i))) for i in range(0,36,4)],
 timeout=dict(callback='0x08057650 -> 0x0801be1a',wait='0x0801cdc8',actual_timeout='0xffffffff',
  synchronous_Main_wait='0x08023fd6: yields while wrapper+0x10==1',
  bounded_unwind_found=False,scope='Selected QSPI controller, backend/vtable, worker, completion callback and same RTOS wait primitive',
  safe_owner='Storage task; cancellation must quiesce DMA/peripheral before releasing semaphore and clearing request',
  cross_task_release_implemented=False),
 references=refs,constrained_call_edges=edges,
 QSPI_commands=sorted(set(v for c in replay['cases'] for v in c['details']['QSPI_commands'])),
 forbidden_nonread_dispatches=0,request_reachable_SD_writes=0,CPU_flash_writes=0,
 external_primary_sources=[
  dict(url='https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-f7/master/Include/stm32f745xx.h',symbols=['QUADSPI_SR_TEF','QUADSPI_CR_TEIE','QUADSPI_FCR_CTEF','DMA_SxCR_CIRC'],purpose='Manufacturer bit definitions, distinct QSPI/DMA errors'),
  dict(url='https://www.st.com/resource/en/reference_manual/dm00124865-stm32f7-series-advanced-armbased-32bit-mcus-stmicroelectronics.pdf',sections=['2.1.1','14.4','14.5.13'],purpose='DTCM DMA accessibility; IRQ enables; memory-mapped low-power timeout is not indirect-read watchdog')],
 no_nonphysical_RAM=True,hardware_access=False,firmware_generated=False)
(O/'ownership-and-error-audit.json').write_text(json.dumps(result,indent=2)+'\n')
prior=json.loads((R/'builds/phase29-storage-wrapper/validation.json').read_text());archive=O/'phase29-report-before.md';note=R/'notes/qspi82000-hardware-readiness.md'
if not archive.exists():
 b=note.read_bytes();assert sha(b)==prior['report_sha256'];archive.write_bytes(b)
assert sha(archive.read_bytes())==prior['report_sha256']
print(json.dumps(dict(heap=heap,buffer=result['buffer'],edges=len(edges),QSPI_commands=result['QSPI_commands']),indent=2))
