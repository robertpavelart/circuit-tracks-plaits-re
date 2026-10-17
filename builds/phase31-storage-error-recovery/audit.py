"""Static stock caller census with B1.3 byte verification; no binary output."""
from support import *

prior=json.loads((R/'builds/phase30-chunked-storage/validation.json').read_text())
note=R/'notes/qspi82000-hardware-readiness.md';archive=O/'phase30-report-before.md'
if not archive.exists():
 assert sha(note.read_bytes())==prior['report_sha256'];archive.write_bytes(note.read_bytes())
assert sha(archive.read_bytes())==prior['report_sha256']
e=Physical();listing=(REF/'re/app.asm').read_text()
entries={
 0x08022edc:'generic constructor',0x08022f10:'NOR constructor',0x08022f1e:'NOR init',0x08022f5e:'configuration',
 0x08022f94:'read',0x08022fdc:'program',0x08023078:'erase',0x080230f8:'semaphore wait',0x0802310a:'callback registration',
 0x08023f2c:'queue wrapper constructor',0x08023f68:'enqueue',0x08023fd6:'sync wait',0x08024014:'worker',
 0x080240fe:'op0 request',0x08024130:'op1 read request',0x08024164:'op2 write request',0x080241b8:'op3 erase request',0x080241f0:'op3 async request',
 0x08024210:'async enqueue tail',0x080226a2:'QSPI init',0x08022746:'indirect command',0x08022826:'QSPI flags',0x08022888:'DMA callback',
 0x080373bc:'NOR init helper',0x080373ec:'config read',0x08037430:'DMA read',0x08037494:'program helper',0x080374d4:'erase helper',
 0x08037596:'transfer event wait',0x080375c0:'status poll',0x0803769c:'read command descriptor',
 0x080573e0:'QSPI IRQ',0x080573ee:'DMA IRQ',0x08057650:'wait callback',0x08057664:'IRQ callback',0x0805767c:'Storage task',
 0x0801be1a:'flag wait',0x0801bde8:'flag notify',0x0801cdc8:'RTOS wait',0x0801cd30:'idle loop',0x0801d760:'idle callback',
 0x0801eaf8:'watchdog init',0x0801eb1e:'watchdog feed',0x08047c6c:'public read'
}
callers={hex(a):[] for a in entries}
for line in listing.splitlines():
 m=re.match(r'([0-9a-f]{8}):\s+(bl|b\.w|b)\s+#(0x[0-9a-f]+)\s*$',line)
 if not m:continue
 at=int(m[1],16);target=int(m[3],16)
 if target not in entries:continue
 inst=next(md.disasm(PUBLISHED[at-0x08010000:at-0x08010000+4],at),None)
 if inst and inst.mnemonic in ('bl','b.w','b') and inst.operands[0].type==2 and inst.operands[0].imm==target:
  callers[hex(target)].append(dict(address=hex(at),instruction=f'{inst.mnemonic} {inst.op_str}',B13_bytes_verified=True))

values={0x20006968:'NOR wrapper global',0x20000378:'backend object',0x20005550:'controller',0xa0001000:'QSPI MMIO',
 0x400264b8:'DMA2 stream7',0x0805b1ac:'backend vtable',0x0805b1d8:'wrapper vtable',0x08057651:'wait callback pointer',
 0xe000ed0c:'AIRCR',0x40003000:'IWDG',0x40023810:'RCC AHB3RSTR',0x40023800:'RCC base'}
values.update({a|1:label+' function pointer' for a,label in entries.items()})
literals={hex(v):dict(label=label,locations=[]) for v,label in values.items()}
for off in range(0,len(PUBLISHED)-3,2):
 value=w(0x08010000+off)
 if value in values:literals[hex(value)]['locations'].append(hex(0x08010000+off))
# Inventory all B1.3 literal loads to selected values at each halfword boundary.
# These are candidates, not proof that every decoded halfword is reachable code.
loads=[]
for off in range(0,len(PUBLISHED)-3,2):
 a=0x08010000+off;i=next(md.disasm(PUBLISHED[off:off+4],a),None)
 if not i or i.mnemonic not in ('ldr','ldr.w'):continue
 for op in i.operands:
  if op.type==3 and op.mem.base==11:
   at=((a+4)&~3)+op.mem.disp
   if 0x08010000<=at<=0x08010000+len(PUBLISHED)-4 and w(at) in values:
    loads.append(dict(address=hex(a),instruction=i.mnemonic+' '+i.op_str,literal=hex(at),value=hex(w(at)),label=values[w(at)]))
for a,n in [(0x08022edc,0x240),(0x08023f2c,0x350),(0x08022698,0x200),(0x080373bc,0x33c),(0x080573e0,0x5c),(0x08057650,0x90),
 (0x0801be1a,0x46),(0x0801cd30,0x24),(0x0801d760,0xa),(0x0801eaf8,0x38),(0x0801da08,0x1a),(0x08038fdc,0x80)]:code(a,n)
# Retain readable evidence for each discovered wrapper-global load and reset use.
for x in loads:
 if x['label']=='AIRCR':code(int(x['address'],16)-8,0x38)
 if x['label']=='NOR wrapper global':code(int(x['address'],16)-8,0x80)

wrapper=e.r32(0x20006968);backend=e.r32(wrapper+4)
vt=e.r32(backend);wvt=e.r32(wrapper)
ramrefs={hex(v):[] for v in (wrapper,backend,e.r32(backend+4),0x20005550)}
for a in range(0x20000000,0x20050000,4):
 v=e.r32(a)
 if hex(v) in ramrefs:ramrefs[hex(v)].append(hex(a))
result=dict(confidence='PROVEN',scope='Verified direct stock-listing call sites, all halfword-aligned B1.3 literal candidates, initialized RAM pointer census, selected backend/worker/controller control flow',
 completeness='UNKNOWN: arbitrary computed indirect callers or RAM-created aliases outside captured state are not exhaustively proved absent',
 sources=dict(stock_sha256=sha(STOCK),B13_sha256=sha(PUBLISHED[:]),listing_sha256=sha((REF/'re/app.asm').read_bytes())),
 routines={hex(a):n for a,n in entries.items()},verified_direct_callers=callers,literal_candidates=literals,literal_load_candidates=loads,initialized_RAM_aliases=ramrefs,
 backend_vtable=[dict(offset=hex(i),target=hex(e.r32(vt+i))) for i in range(0,36,4)],
 wrapper_vtable=[dict(offset=hex(i),target=hex(e.r32(wvt+i))) for i in range(0,36,4)],
 stock_unwind_found=False,negative_scope='No bounded unwind in inspected same-backend dispatch, callbacks, read completion and init/poll paths; not a universal firmware nonexistence proof',
 watchdog=dict(init='0x0801eaf8',startup_call='0x0801da0a',feed='0x0801eb1e',idle_loop='0x0801cd30 -> 0x0801d760 -> 0x0801eb1e',storage_progress_required=False),
 reset=dict(known_inline='0x08039042..0x0803905a',surrounding_path='Updater writes 23-byte NOR staging metadata before reset; whole function unsuitable',interior_entry='Not a callable stock API; replaying SYSRESETREQ alone cannot qualify complete reboot'),
 hardware_access=False,firmware_generated=False)
(O/'stock-path-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(direct_sites=sum(map(len,callers.values())),literal_load_candidates=len(loads),AIRCR=[x for x in loads if x['label']=='AIRCR'],RAM_aliases=ramrefs),indent=2))
