"""All-block selector0 staging + native boot validation/installer, in memory.

Explicit seams: host transfer schedule, running-RAM application fixture, modeled
NOR command completion, constructed boot storage interface and flash primitives.
This is not an end-to-end reset/scheduler or complete persistent-write census.
"""
from environment import *
from unicorn.arm_const import *
import hashlib
ROM=(REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin').read_bytes()
sys.path.insert(0,str(O/'source/tools'));import ct_fw
e=Physical();u=e.uc
image=(O/'integrated-internal.bin').read_bytes();size=len(image);end=0x08010000+size
assert bytes(u.mem_read(0x08010000,size))==image
crc=ct_fw.crc32_mpeg2(image)
assert image[:8]==PUBLISHED[:8] and size%4==0 and size<0x70001
assert bytes(u.mem_read(0x08000000,0x10000))==ROM[:0x10000]
nor=bytearray(b'\xff'*0x2000000)
identity=bytes((i*37+11)&255 for i in range(23));nor[0x81000:0x81017]=identity
target=bytes(((i*113)^(i>>2)^0x5a)&255 for i in range(512));nor[0x82000:0x82200]=target
ops=[];internal=[];phase='application staging';backend=e.r32(e.r32(0x20006968)+4);ctx=e.r32(backend+4)
source=0x20040000;bootobj=0x20041000;bootvt=0x20041040
def ret(v=0):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
def reg(i):return u.reg_read(UC_ARM_REG_R0+i)
def log(kind,a,n,**extra):
 ops.append(dict(phase=phase,kind=kind,start=hex(a),end_exclusive=hex(a+n),length=n,target_overlap=a<0x82200 and a+n>0x82000,**extra))
def hook(u,pc,n,d):
 if pc==0x0803769c:
  descriptor=bytes(u.mem_read(reg(1),16));flags=int.from_bytes(descriptor[2:4],'little')
  op=descriptor[1] if flags&2 and e.r8(ctx+0x19)==1 and descriptor[1] else descriptor[0]
  a=int.from_bytes(descriptor[8:12],'little');count=int.from_bytes(descriptor[4:8],'little')
  if op in (0x20,0x21):
   a&=~4095;log('ERASE',a,4096,command=hex(op),routine='0x08037494',erase_unit=4096)
   nor[a:a+4096]=b'\xff'*4096
  elif op in (2,0x12):
   # Program source is passed to 0x080374d4 and is remembered below.
   data=bytes(u.mem_read(program['buffer'],count));a=program['address']
   log('WRITE',a,count,command=hex(op),routine='0x080374d4',page_limit=256)
   assert all((old&new)==new for old,new in zip(nor[a:a+count],data))
   nor[a:a+count]=data
  elif op not in (6,5):raise AssertionError(('unexpected command',hex(op)))
  ret() # hardware command issue/completion seam; address construction executed
 elif pc==0x080374d4:
  program.update(buffer=reg(2),address=reg(1))
 elif pc in (0x08037596,0x080375c0):ret()
 elif phase=='bootloader validation/install':
  if pc==0x0807f010:
   a,b,count=reg(1),reg(2),reg(3);log('READ',a,count,routine='constructed boot storage read interface')
   u.mem_write(b,bytes(nor[a:a+count]));ret()
  elif pc in (0x0807f020,0x08005d74,0x08005ff8,0x08004ae2,0x0800600e,0x08006006):ret(1)
  elif pc==0x08006020:
   a=reg(0);bounds=[0x08010000,0x08018000,0x08020000,0x08040000,0x08080000]
   if a<0x08080000:
    hi=bounds[bounds.index(a)+1];u.mem_write(a,b'\xff'*(hi-a));internal.append(dict(kind='ERASE',start=hex(a),end_exclusive=hex(hi)))
   else:internal.append(dict(kind='NOOP',start=hex(a),reason='native wrapper rejects offset >=0x70000'))
   ret(1)
  elif pc==0x0800605e:
   a,v=reg(0),reg(1);assert 0x08010000<=a<0x08080000
   u.mem_write(a,struct.pack('<I',v));internal.append(dict(kind='WRITE',start=hex(a),end_exclusive=hex(a+4)));ret(1)
  elif pc==0x08005c68:
   a,n=reg(0),reg(1);log('READ',a,n,routine='boot CRC endpoint model')
   ret(ct_fw.crc32_mpeg2(bytes(nor[a:a+n])))
  elif pc==0x08005c3c:ret(ct_fw.crc32_mpeg2(bytes(u.mem_read(reg(0),reg(1)))))
  elif pc==0x08003d06:
   reached['application_jump']=True;ret() # do not misrepresent this as cold boot
program={};reached={}
u.hook_add(UC_HOOK_CODE,hook)
def call(fn,*args):return e.call(fn,*args,sp=0x20008300,maxins=4000000)
calls=[]
# Execute all native NOR erase and page-program address algorithms, every block.
call(0x08023078,backend,0,size)
padded=image+b'\xff'*(-len(image)%32)
for block in list(range(1,len(padded)//32))+[0]:
 raw=padded[block*32:(block+1)*32]
 # Exercise the actual reference host block codec without encoding a SYX.
 encoded=ct_fw.pack_block(raw);decoded=ct_fw.unpack_block(encoded);assert decoded==raw
 u.mem_write(source+128,encoded);call(0x08024e20,source,source+128)
 assert bytes(u.mem_read(source,32))==raw # actual ARM SysEx block unpacker
 e.w32(0x20008300,0)
 call(0x08022fdc,backend,block*32,source,32)
header=b'\0'+ct_fw.nibbles(0x572,6)+ct_fw.nibbles(size,8)+ct_fw.nibbles(crc,8)
u.mem_write(source,header);e.w32(0x20008300,1);call(0x08022fdc,backend,0x80000,source,23)
assert bytes(nor[:size])==image and bytes(nor[0x82000:0x82200])==target
staging_count=len(ops)
phase='bootloader validation/install'
# Current installed application must remain B1.3, or version equality correctly
# skips installation and a preloaded destination could mask a broken fixture.
u.mem_write(0x08010000,PUBLISHED[:])
# Construct only the known boot storage interface; do not import app RTOS RAM
# as boot objects or claim constructors ran. Native validator/installer use it.
e.w32(bootobj,bootvt)
for slot in range(0,32,4):e.w32(bootvt+slot,0x0807f021)
e.w32(bootvt+12,0x0807f011)
for g in (0x200054c8,0x200054dc):e.w32(g,bootobj)
call(0x08003b2a)
assert e.r32(0x20005384)==size and e.r32(0x20005388)==crc
call(0x08003b9a)
assert sum(x['kind']=='WRITE' for x in internal)==len(padded)//4,'installer must actually program every word'
assert sum(x['kind']=='ERASE' for x in internal)==4,'installer must actually erase four effective sectors'
assert reached.get('application_jump') and bytes(u.mem_read(0x08010000,size))==image
assert bytes(u.mem_read(0x08000000,0x10000))==ROM[:0x10000]
assert bytes(nor[0x82000:0x82200])==target and bytes(nor[0x81000:0x81017])==identity
preservation={}
for name,lo,hi in [('identity',0x81000,0x81017),('wavetable',0x82000,0x82200)]:
 mutations=[x for x in ops if x['kind'] in ('WRITE','ERASE')]
 overlaps=[x for x in mutations if int(x['start'],16)<hi and int(x['end_exclusive'],16)>lo]
 assert not overlaps
 distances={k:min(max(lo-int(x['end_exclusive'],16),int(x['start'],16)-hi,0) for x in mutations if x['kind']==k) for k in ('WRITE','ERASE')}
 preservation[name]=dict(start=hex(lo),end_exclusive=hex(hi),writes=0,erase_overlaps=0,closest_boundary_gap_bytes=distances,sentinel_unchanged=True)
result=dict(confidence='PROVEN',scope='Selected all-block storage algorithms and native boot validator/installer with explicit modeled interfaces; NOT complete host-to-cold-boot execution',
 candidate=dict(origin='exact integrated-internal.bin, hash pinned by integration.json',bytes=size,padded_bytes=len(padded),sha256=sha(image),CRC=hex(crc),file_generated=False,SYX_generated=False,
  bootloader_bytes_changed=0,stock_prefix_changes=json.loads((O/'integration.json').read_text())['hook_patches'],append_end_exclusive=hex(end)),
 target=dict(start='0x82000',end_exclusive='0x82200',origin='synthetic sentinel',before_sha256=sha(target),after_sha256=sha(bytes(nor[0x82000:0x82200]))),
 preservation=preservation,operations=ops,internal_operations=internal,staging_operation_count=staging_count,
 QSPI_write_count=sum(x['kind']=='WRITE' for x in ops),QSPI_erase_count=sum(x['kind']=='ERASE' for x in ops),
 target_write_count=sum(x['kind']=='WRITE' and x['target_overlap'] for x in ops),target_erase_overlap=sum(x['kind']=='ERASE' and x['target_overlap'] for x in ops),
 installed_exact=True,bootloader_unchanged=True,complete_update_sequence=False,native_SysEx_block_unpack_calls=len(padded)//32,
 gaps=['Application SysEx state machine/RTOS queue bypassed at scheduling seam; native NOR backend used for all blocks',
 'Boot storage object constructed, hardware completion and internal flash primitives modeled',
 'Full bootloader constructors/recovery/background/SD closure not run; native app handoff intercepted',
 'NOR erase geometry follows stock 4KiB commands, physical NOR identity not independently measured'],
 H1='PROVEN zero overlap in selected complete-image staging/validator/installer replay; broader cold-boot closure UNKNOWN',hardware_access=False,firmware_exported=False)
(O/'installation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('operations','internal_operations')},indent=2))
