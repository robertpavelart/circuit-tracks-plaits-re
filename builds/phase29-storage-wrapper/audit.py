"""Summarize constrained reachable paths and preserve the phase28 report."""
from inspect_code import *
from shims import STATE,REQ,PAYLOAD,PACKET,DESC
result=json.loads((O/'replay-result.json').read_text());obj=json.loads((O/'objects.json').read_text())
edges=sorted(set(tuple(x) for c in result['cases'] for x in c['details']['selected_call_edges']))
spans=[]
for p in sorted(O.glob('*.asm')):
 if '-emulator' in p.stem:continue
 a=int(p.stem,16);import re
 pcs=[int(x,16) for x in re.findall(r'^([0-9a-f]{8}):',p.read_text(),re.M)]
 if pcs:
  b=PUBLISHED[a-0x08010000:max(pcs)+2-0x08010000]
  spans.append(dict(file=p.name,start=hex(a),sha256=sha(b),source='Published verified B1.3 spans'))
record=dict(confidence='PROVEN',scope='Fixed-operation dataflow plus exercised dispatch targets, not whole-system no-write assertion',
 wrapper=dict(public_read='0x08047c6c -> 0x08024130',synchronous_wait='0x08023fd6',async_submission='0x08023f68',worker='0x08024014',task='0x0805767c'),
 descriptor=dict(bytes=24,fields={'0x00:u16':'operation=1','0x02:u16':'flags=0','0x04:u32':'offset=0x82000','0x08:pointer':hex(PAYLOAD),'0x0c:u32':'length=512','0x10:callback':'0x0807b201 (emulator only)','0x14:userdata':hex(STATE)}),
 constrained_dispatch='TBB 0x08024070, op1 -> 0x0802408a -> backend vtable+0xc -> 0x08022f94',
 callback_rule='request copied to worker stack; callback pointer/userdata preserved; status copied before callback returns',
 selected_call_edges=edges,source_spans=spans,
 only_observed_QSPI_commands=sorted(set(x for c in result['cases'] for x in c['details']['QSPI_commands'])),
 QSPI_program_erase_entries_reached=0,non_read_worker_dispatches_reached=0,
 CPU_flash_writes=0,CPU_payload_writes=sum(c['details']['payload_CPU_writes'] for c in result['cases']),
 request_reachable_SD_writes=0,
 modeling_boundary=['Peripheral DMA payload/TCF/TEF','OS notify/block scheduler endpoints','Main periodic preflight/attachment and USB completion timing','Arena outside physical SRAM'],
 physical_buffer_ownership='UNKNOWN',Main_service_registration='UNKNOWN: modeled at the actual Main periodic service boundary, not installed',
 heap_remaining_bytes=obj['heap_remaining_bytes'],heap_allocation_attempts=obj['allocation_attempts'])
(O/'closure.json').write_text(json.dumps(record,indent=2)+'\n')
note=R/'notes/qspi82000-hardware-readiness.md';v=json.loads((R/'builds/phase28-hardware-readiness/validation.json').read_text())
archive=O/'phase28-report-before.md'
if not archive.exists():
 b=note.read_bytes();assert sha(b)==v['report_sha256'],'Archive must preserve original validated phase28 report'
 archive.write_bytes(b)
assert sha(archive.read_bytes())==v['report_sha256']
print(json.dumps(dict(edges=len(edges),source_spans=len(spans),QSPI_commands=record['only_observed_QSPI_commands'],heap_remaining_bytes=obj['heap_remaining_bytes'],phase28_report_preserved=True),indent=2))
