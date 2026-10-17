"""Source/byte evidence for selected read transaction and recovery limits."""
from pathlib import Path
import json,struct
from build_patch import O,R,REF,PUBLISHED,STOCK,sha,BASE
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
spans=[('selected_read',0x08022f94,0x08022fdc),('low_read',0x08037430,0x08037494),
 ('command_adapter',0x0803769c,0x080376e4),('command_registers',0x08022746,0x08022826),
 ('DMA_clear',0x0801c4d4,0x0801c554),('DMA_setup',0x0801c072,0x0801c142),
 ('completion_wait',0x08037596,0x080375c0),('semaphore_release',0x0801ba12,0x0801ba38),
 ('thread_query',0x0801cdb8,0x0801cdc2),('thread_context',0x0801cd82,0x0801cd9a),
 ('callback_dispatch',0x0801c894,0x0801c8bc),('selected_callback',0x08057650,0x0805765a),
 ('thread_flags_wait',0x0801be1a,0x0801be6c),('router_copy',0x08020c90,0x08020dbc),
 ('stock_program_entry',0x08022fdc,0x08023078),('stock_low_erase_entry',0x08037494,0x080374d4),
 ('stock_low_program_entry',0x080374d4,0x0803755a)]
rows=[];text=[]
for name,a,b in spans:
 raw=STOCK[a-0x08010000:b-0x08010000]
 same=raw==PUBLISHED[a-0x08010000:b-0x08010000]
 assert same,(name,'B1.3 differs; re-audit required')
 ins=list(md.disasm(raw,a));calls=[dict(pc=hex(i.address),op=i.mnemonic,target=i.op_str) for i in ins if i.mnemonic in ('bl','blx')]
 rows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),sha256=sha(raw),B13_identical=True,calls=calls))
 text+=['\n; '+name]+[f'{i.address:08x}: {i.mnemonic:9} {i.op_str}' for i in ins]
(O/'stock-read-and-router.asm').write_text('\n'.join(text)+'\n')
from environment import authentic_session
s=authentic_session();e=s.e;backend=e.r32(e.r32(0x20006968)+4);ctx=e.r32(backend+4)
count=e.r8(ctx+0x24);cb=e.r32(ctx+0x28);assert count==1 and cb==0x08057651
dump=REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin';flash=dump.read_bytes()
assert struct.unpack_from('<I',flash,0x3d68)[0]==0x70001
boot=[]
for name,a,b in [('main',0x08002fde,0x080030a0),('buttons',0x08003ab0,0x08003b00),
 ('button_poll',0x08003b66,0x08003b9a),('apply_and_verify',0x08003b9a,0x08003c98),
 ('staging_header_read',0x08003b2a,0x08003b66),('version_and_CRC_read',0x08005c10,0x08005cdc)]:
 boot+=['\n; '+name]+[f'{i.address:08x}: {i.mnemonic:9} {i.op_str}' for i in md.disasm(flash[a-0x08000000:b-0x08000000],a)]
(O/'bootloader-evidence.asm').write_text('\n'.join(boot)+'\n')
patch=json.loads((O/'patch-plan.json').read_text())
size=patch['base_B13_size']+patch['append']['bytes'];pad=(-size)%4
report=dict(confidence='PROVEN',scope='Admitted fixed-range transaction; not all other stock commands/tasks',
 source_spans=rows,selected_backend=hex(backend),context=hex(ctx),
 callback_guard=dict(count=count,entry=hex(cb),dispatch='0x0801c894',target='0x08057650',RTOS_boundary='0x0801be1a'),
 transaction_read_commands=['0xeb','0xec'],transaction_QSPI_program_commands=[],transaction_QSPI_erase_commands=[],
 worker_queue_not_called=True,stock_program_entry_not_called='0x08022fdc',stock_low_erase_not_called='0x08037494',stock_low_program_not_called='0x080374d4',
 expected_postpackaging_size=(size+pad),padding_bytes_needed=pad,padded_application_end=hex(0x08010000+size+pad),
 bootloader_size_reject_at='0x70001',original_initial_SP=hex(struct.unpack('<I',PUBLISHED[0:4])[0]),
 bootloader_dump_sha256=sha(flash),bootloader_64K_sha256=sha(flash[:0x10000]),
 application_patch_addresses_above_bootloader=True,
 full_runtime_scheduler_and_callbacks='UNKNOWN beyond admitted callback/RTOS endpoint; no global whole-firmware no-write assertion',
 hardware_recovery='UNKNOWN; code and local reported tests are not a unit-specific recovery guarantee')
(O/'stock-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='source_spans'},indent=2))
