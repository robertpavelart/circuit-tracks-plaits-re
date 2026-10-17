"""Phase35 reset runner copied with optional native PendSV adapter.

All new output is local to phase36. No RAM access hooks. Native instruction
stream is unchanged; the adapter handles only architectural exception boundaries.
"""
from pathlib import Path
import sys,json,struct,hashlib
from collections import Counter,deque
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'builds/phase33-preservation-powercycle'))
from cold_boot import Cold
from support import *
# support.O points at phase33; keep new output local.
O=Path(__file__).resolve().parent

def run(entry,variant='stock',hooks='bounded',poison=False,limit=300000,clock_model=False,nor_init=False,nor_identity=False,tick_model=False,seed=None,svc_model=None):
 e=Cold('stock' if variant=='B13' else variant);u=e.uc
 if variant=='B13':
  for at,data in PUBLISHED.parts:u.mem_write(0x08010000+at,data)
 original_code_sha=sha(bytes(u.mem_read(0x08000000,0x80000)))
 if poison:u.mem_write(0x20000000,b'\xa5'*0x50000)
 for address,data in seed or []:
  assert 0x20000000<=address and address+len(data)<=0x20050000
  u.mem_write(address,data)
 counts=Counter();tail=deque(maxlen=40);lastpc=[None];stack=[];call_chain=[];blocks=[];openblocks=[];events=[];lastreads=deque(maxlen=10);why={}
 pending=[];commands=[];IRQs=[];in_irq=[False];fifo=[];lasttick=[0];milestones={};steps=[0]
 def regs():return {f'r{i}':hex(u.reg_read(UC_ARM_REG_R0+i)) for i in range(13)}|dict(sp=hex(u.reg_read(UC_ARM_REG_SP)),lr=hex(u.reg_read(UC_ARM_REG_LR)),xPSR=hex(u.reg_read(UC_ARM_REG_XPSR)))
 def code(u,pc,n,d):
  if svc_model is not None and not in_irq[0]:
   action=svc_model.observe(u,pc,n)
   if action:
    why.update(kind=action,pc=hex(pc));u.emu_stop();return
  if pc in (0x0801ddd4,0x0801d4b0,0x0805767c,0x0801d9ea,0x080031c2,0x0801c634):
   milestones.setdefault(hex(pc),dict(registers=regs(),call_chain=list(call_chain)))
  if tick_model and not in_irq[0] and steps[0]-lasttick[0]>=2000 and int.from_bytes(u.mem_read(0xe000e010,4),'little')&3==3:
   if svc_model is not None and getattr(svc_model,'pendsv_active',False):
    why.update(kind='unsupported nested tick during PendSV',pc=hex(pc));u.emu_stop();return
   if svc_model is not None and getattr(svc_model,'switches',[]):
    why.update(kind='next unsupported post-scheduler SysTick boundary',pc=hex(pc));u.emu_stop();return
   lasttick[0]=steps[0];pending.append(dict(service='SysTick'))
  if not in_irq[0] and pending:
   why.update(kind='service pending',pc=hex(pc));u.emu_stop();return
  counts[pc]+=1;steps[0]+=1;tail.append(hex(pc))
  if counts[pc]>20000:why.update(kind='platform wait',pc=hex(pc));u.emu_stop();return
  # Read instructions through the host API only. Never install RAM access hooks.
  raw=bytes(u.mem_read(pc,n));ins=next(md.disasm(raw,pc),None)
  if ins and ins.mnemonic in ('bl','blx'):
   call_chain.append(dict(pc=hex(pc),instruction=ins.mnemonic+' '+ins.op_str,return_address=hex(pc+n)))
   if len(call_chain)>40:call_chain.pop(0)
  if pc in (0x0800927c,0x080596c4):
   desc=u.reg_read(UC_ARM_REG_R0);data=bytes(u.mem_read(desc,12));rel,encoded,dest=struct.unpack('<III',data)
   src=(desc+rel)&0xffffffff;actualdest=(dest+(u.reg_read(UC_ARM_REG_R9) if encoded&1 else 0))&0xffffffff
   row=dict(entry=hex(pc),caller=hex(u.reg_read(UC_ARM_REG_LR)&~1),registers=regs(),descriptor=hex(desc),descriptor_hex=data.hex(),
    compressed_source=hex(src),compressed_bytes=encoded>>1,destination=hex(actualdest),relative_destination=bool(encoded&1),
    source_sha256=sha(bytes(u.mem_read(src,encoded>>1))),call_chain=list(call_chain),RAM_before=bytes(u.mem_read(actualdest,64)).hex())
   blocks.append(row);openblocks.append((u.reg_read(UC_ARM_REG_LR)&~1,actualdest,row))
  if openblocks and pc in (0x080092ec,0x08059734):
   _,dest,row=openblocks[-1];end=u.reg_read(UC_ARM_REG_R5)
   assert 0<=end-dest<=0x50000
   row.update(end_destination=hex(end),output_bytes=end-dest,output_sha256=sha(bytes(u.mem_read(dest,end-dest))),RAM_after=bytes(u.mem_read(dest,64)).hex())
  if openblocks and pc==openblocks[-1][0]:
   _,dest,row=openblocks.pop();row['returned']=True
  lastpc[0]=pc
 def memory(u,access,a,n,v,d):
  if a<0x40000000 and not 0x08000000<=a<0x08080000:return
  pc=u.reg_read(UC_ARM_REG_PC)
  if access==17: # UC_MEM_WRITE
   events.append(dict(pc=hex(pc),address=hex(a),size=n,value=hex(v)))
   if nor_init and a==0xa0001018:
    ccr=int.from_bytes(u.mem_read(0xa0001014,4),'little');dlr=int.from_bytes(u.mem_read(0xa0001010,4),'little')
    item=dict(opcode=hex(ccr&255),address=hex(v),DLR=dlr,CCR=hex(ccr),issuer_PC=hex(pc));commands.append(item);pending.append(item)
   if nor_init and a==0xa000100c:
    sr=int.from_bytes(u.mem_read(0xa0001008,4),'little');u.mem_write(0xa0001008,struct.pack('<I',sr&~v))
  else:
   lastreads.append(dict(pc=hex(pc),address=hex(a),size=n))
   if nor_identity and a==0xa0001020:
    assert n==1 and fifo,'unmodeled QSPI FIFO data requested'
    u.mem_write(a,bytes([fifo.pop(0)]))
   if clock_model and a==0x40023800:
    value=int.from_bytes(u.mem_read(a,4),'little')
    for on,ready in ((0,1),(16,17),(24,25),(26,27),(28,29)):
     value=(value|(1<<ready)) if value&(1<<on) else (value&~(1<<ready))
    u.mem_write(a,struct.pack('<I',value))
   if clock_model and a==0x40023808:
    value=int.from_bytes(u.mem_read(a,4),'little');selection=value&3
    u.mem_write(a,struct.pack('<I',(value&~12)|(selection<<2)))
 u.hook_add(UC_HOOK_CODE,code)
 if hooks=='bounded':
  # No RAM hooks, even no-op ones: they perturb Thumb IT execution in this DLL.
  for lo,hi in ((0x40000000,0x4002ffff),(0xa0001000,0xa0001fff),(0xe000e000,0xe000ffff),(0xe0042000,0xe0042fff)):
   u.hook_add(UC_HOOK_MEM_READ,memory,begin=lo,end=hi);u.hook_add(UC_HOOK_MEM_WRITE,memory,begin=lo,end=hi)
  u.hook_add(UC_HOOK_MEM_WRITE,memory,begin=0x08000000,end=0x0807ffff)
 if hooks=='legacy':
  u.hook_add(UC_HOOK_MEM_READ,memory);u.hook_add(UC_HOOK_MEM_WRITE,memory)
 base=0x08000000 if entry=='bootloader' else 0x08010000
 sp,pc=struct.unpack('<II',bytes(u.mem_read(base,8)));u.reg_write(UC_ARM_REG_SP,sp)
 try:
  while True:
   u.emu_start(pc,0xffffffff,count=limit)
   if why.get('kind')=='native SVC boundary':
    pc=svc_model.service(u)|1;why.clear();continue
   if why.get('kind')=='native PendSV boundary':
    pc=svc_model.service_pendsv(u)|1;why.clear();continue
   if why.get('kind')!='service pending':break
   resume=u.reg_read(UC_ARM_REG_PC);item=pending.pop(0);is_tick=item.get('service')=='SysTick';op=None if is_tick else int(item['opcode'],16)
   if is_tick:pass
   elif nor_identity and op==0xaf:
    assert item['DLR']==2;fifo.extend(bytes.fromhex('c22019'))
   elif op not in (0xf5,0x35,0xb7):
    why.update(kind='missing authentic QSPI response',required='JEDEC identity bytes' if op==0x9f else 'command-specific NOR data/status',command=item);break
   # Ideal completion only of the observed data-free mode commands. No array
   # bytes, identity, metadata or software controller flag is fabricated.
   if not is_tick:u.mem_write(0xa0001008,struct.pack('<I',2))
   saved=u.context_save();vectorbase=int.from_bytes(u.mem_read(0xe000ed08,4),'little')
   exception=15 if is_tick else 108
   irq=int.from_bytes(u.mem_read(vectorbase+4*exception,4),'little')
   sp=u.reg_read(UC_ARM_REG_SP)
   hwregs=[u.reg_read(UC_ARM_REG_R0+x) for x in range(4)]+[u.reg_read(UC_ARM_REG_R12),u.reg_read(UC_ARM_REG_LR),resume,u.reg_read(UC_ARM_REG_XPSR)]
   u.mem_write(sp-32,struct.pack('<8I',*hwregs))
   in_irq[0]=True;u.reg_write(UC_ARM_REG_SP,sp-32);u.reg_write(UC_ARM_REG_LR,0x0807ff01);u.reg_write(UC_ARM_REG_IPSR,exception)
   u.emu_start(irq,0x0807ff00,count=10000)
   assert u.reg_read(UC_ARM_REG_PC)==0x0807ff00,'native IRQ did not return'
   IRQs.append(dict(vector=hex(irq),service='SysTick' if is_tick else 'QSPI',after_command=item.get('opcode'),software_flags='set by native IRQ, not host fixture'))
   u.context_restore(saved);in_irq[0]=False;why.clear();pc=resume|1
 except Exception as exc:why.update(kind='exception',error=str(exc),pc=hex(u.reg_read(UC_ARM_REG_PC)))
 if not why:why=dict(kind='instruction limit',pc=hex(u.reg_read(UC_ARM_REG_PC)))
 for row in blocks:
  if 'output_bytes' not in row:
   ptr=u.reg_read(UC_ARM_REG_R5);dest=int(row['destination'],16)
   row['partial_RAM_destination']=bytes(u.mem_read(dest,64)).hex()
   if dest<=ptr<=dest+0x50000:row['partial_output_bytes']=ptr-dest
 endcode=sha(bytes(u.mem_read(0x08000000,0x80000)));assert endcode==original_code_sha,'firmware code mutated'
 runtime={hex(a):hex(int.from_bytes(u.mem_read(a,4),'little')) for a in (0x20000378,0x20000380,0x200060d4,0x20006138,0x20006790,0x20006968,0x2000696c,0x400264b8,0x400264bc,0xa0001000,0xa0001008)}
 def r32(address):return int.from_bytes(u.mem_read(address,4),'little')
 wrapper=r32(0x20006968);holder=r32(0x20006790)
 ownership=None
 if 0x20000000<=wrapper<0x2004ffe0 and 0x20000000<=holder<0x2004ffe0:
  backend=r32(wrapper+4)
  ownership=dict(wrapper=hex(wrapper),backend=hex(backend),semaphore=u.mem_read(backend+8,1)[0],
   sync=r32(wrapper+16),pending=u.mem_read(wrapper+12,1)[0],Storage_flags=r32(holder+8),Main_flags=r32(0x20007758),
   parser_owner_initialized='UNKNOWN until Main task entry; payload bytes alone are not ownership',
   old_payload_prefix=bytes(u.mem_read(0x2000a070,16)).hex())
 target_counts=dict(reads=0,writes=0,erase_overlaps=0)
 for item in commands:
  op=int(item['opcode'],16);address=int(item['address'],16)
  if op in (0xeb,0xec,3,0x13,0xb,0xc):
   target_counts['reads']+=int(address<0x82200 and address+item['DLR']+1>0x82000)
  elif op in (2,0x12,0x38):
   target_counts['writes']+=int(address<0x82200 and address+item['DLR']+1>0x82000)
  elif op in (0x20,0x21):
   target_counts['erase_overlaps']+=int((address&~4095)<0x82200 and (address&~4095)+4096>0x82000)
  else:assert op in (0xf5,0x35,0xb7,0xaf),'unclassified NOR command'
 return dict(svc=None if svc_model is None else svc_model.result,entry=entry,variant=variant,hooks=hooks,clock_model=clock_model,poison=poison,stop=why,registers=regs(),instructions=sum(counts.values()),
  blocks=blocks,last_PCs=list(tail),call_chain=call_chain,MMIO_writes=events,last_MMIO_reads=list(lastreads),
  NOR_commands=commands,native_IRQs=IRQs,NOR_mode_completion_model=nor_init,NOR_identity_model=nor_identity,
  tick_model=tick_model,milestones=milestones,
  runtime_fields=runtime,code_unchanged=True,stable_user_state=False,
  initialized_ownership_prefix=ownership,seeded_old_RAM=bool(seed),
  target_counts_observed_prefix=target_counts,target_counts_complete_boot=None,
  RAM_sha256=sha(bytes(u.mem_read(0x20000000,0x50000))),code_sha256=endcode)

if __name__=='__main__':
 rows=[run(entry,variant,hooks) for variant in ('stock','diagnostic') for entry in ('bootloader','application') for hooks in ('none','bounded')]
 (O/'corrected-trace.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(json.dumps([dict(entry=x['entry'],variant=x['variant'],hooks=x['hooks'],stop=x['stop'],blocks=[(b.get('returned'),b.get('output_bytes')) for b in x['blocks']]) for x in rows],indent=2))
