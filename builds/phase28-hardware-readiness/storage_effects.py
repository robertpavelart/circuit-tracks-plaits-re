"""Execute stock NOR erase/program address generation, with modeled peripheral
completion/WIP. No actual firmware payload, NOR capture or device is involved.
"""
from inspect_code import *
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
import math
s=authentic_session();e=s.e;u=e.uc;u.mem_map(0xa0001000,0x1000)
backend=e.r32(e.r32(0x20006968)+4);ctx=e.r32(backend+4);controller=e.r32(ctx)
k=w(0x0801cf90);holder=e.r32(0x20006790);e.w32(k+0x64,e.r32(holder))
ops=[];calls=[]
def hook(u,pc,n,d):
 if pc==0x0801b3b8:
  u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
 elif pc==0x0803769c:
  p=u.reg_read(UC_ARM_REG_R1);b=bytes(u.mem_read(p,16));flags=int.from_bytes(b[2:4],'little')
  op=b[1] if flags&2 and e.r8(ctx+0x19)==1 and b[1] else b[0]
  addr=int.from_bytes(b[8:12],'little');length=int.from_bytes(b[4:8],'little')
  item=dict(opcode=hex(op),address=hex(addr),length=length,caller=hex(u.reg_read(UC_ARM_REG_LR)))
  if op in (0x20,0x21):item['erased_interval']=[hex(addr&~0xfff),hex((addr&~0xfff)+0x1000)]
  elif op in (2,0x12):item['written_interval']=[hex(addr),hex(addr+length)]
  elif op not in (6,5):raise AssertionError(('unexpected command',item))
  ops.append(item)
 elif pc==0x08037596:
  # Explicit peripheral model; storage/address algorithms execute unchanged.
  e.w32(controller,e.r32(controller)|1);e.w32(holder+8,e.r32(holder+8)|0x100)
 elif pc==0x080375c0:
  # WIP polling endpoint: already-completed modeled program/erase, no NOR bytes.
  u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
u.hook_add(UC_HOOK_CODE,hook)
size=json.loads((R/'builds/phase27-qspi-read/stock-audit.json').read_text())['expected_postpackaging_size']
start=len(ops);e.call(0x08023078,backend,0,size,maxins=2000000);calls.append(dict(name='application payload erase',ops=ops[start:]))
buf=0x2006d000;u.mem_write(buf,bytes(256)) # dummy program source, not coefficients/firmware
for name,address,length,erase in [('first payload block',32,32,0),('last payload block',((size+31)//32-1)*32,32,0),('vector payload block',0,32,0),('metadata finalization',0x80000,23,1)]:
 e.w32(0x2006f000,erase);start=len(ops);e.call(0x08022fdc,backend,address,buf,length,maxins=100000)
 calls.append(dict(name=name,ops=ops[start:]))
for op in ops:
 for key in ('erased_interval','written_interval'):
  if key in op:
   lo,hi=map(lambda x:int(x,16),op[key]);assert not (lo<0x82200 and hi>0x82000),op
bundles=[]
for i in range(4):
 p=e.r32(0x20003cc8+4*i);bundles.append(dict(selector=i,object=hex(p),base=hex(e.r32(p+8)),capacity=hex(e.r32(p+12))))
result=dict(confidence='PROVEN',scope='Selected normal-app staging algorithms; not complete install/first-boot preservation',
 planned_image_size=size,normal_selector=0,bundles=bundles,
 maximum_staging_payload_write_end_exclusive=hex((size+31)//32*32),
 payload_erase_end_exclusive=hex((size+4095)//4096*4096),
 metadata_write_interval=['0x80000','0x80017'],metadata_erase_interval=['0x80000','0x81000'],
 target=['0x82000','0x82200'],modeled_known_mutation_overlaps=0,calls=calls,
 peripheral_completion='MODELED; WIP wait endpoint modeled completed; no real storage bytes',
 whole_install_preservation='NOT PROVEN: complete bootloader/first-boot mutation closure not executed',hardware_access=False)
(O/'storage-effects-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({x:v for x,v in result.items() if x!='calls'},indent=2))
