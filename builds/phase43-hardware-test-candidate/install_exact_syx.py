"""All-block selector0 staging + native boot validation/installer, in memory.

Explicit seams: host transfer schedule, running-RAM application fixture, modeled
NOR command completion, constructed boot storage interface and flash primitives.
This is not an end-to-end reset/scheduler or complete persistent-write census.
The native preparation timer and DSP/UI acknowledgement are injected at their
real handlers; the queue/dequeue/worker and write-flag conversion execute.
"""
from pathlib import Path
import sys,json,struct,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase42-exact-rdiag-integration'
sys.dont_write_bytecode=True
sys.path.insert(0,str(P))
from environment import *
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O))
from independent_validate import decode,crc as independent_crc
raw_SYX=(O/'circuittracks-4486-nor-evidence-test.syx').read_bytes()
image,packets,serialization=decode(raw_SYX);size=len(image);end=0x08010000+size
sys.path.insert(0,str(O/'source/tools'));import ct_fw
e=Physical();u=e.uc;u.mem_write(0x08010000,image)
ROM=bytes(u.mem_read(0x08000000,0x10000));crc=independent_crc(image)
assert hashlib.sha256(image).hexdigest()=='9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6'
class PendingStorage(Exception):pass
class ResetReached(Exception):pass
pending=[];request_log=[];message_log=[];app_crc=0xffffffff;unpack_calls=0;worker_flag_checks=0
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
 global app_crc,unpack_calls,worker_flag_checks
 if pc==0x08024e20:unpack_calls+=1
 if pc==0x080240a6:
  flags=int.from_bytes(u.mem_read(u.reg_read(UC_ARM_REG_R5)+2,2),'little')
  assert reg(1)==(0 if flags==1 else 1);worker_flag_checks+=1
 if phase=='application staging':
  if pc==0x08023f68:
   rec=bytes(u.mem_read(reg(1),24));pending.append((reg(0),rec));request_log.append(rec.hex())
  if pc==0x0801be60:
   raise PendingStorage()
  if pc in (0x0801ce60,0x0801b3b8,0x0801eb1e,0x08024e4c,0x08024e94,0x0801e538,0x0805627e,0x0805610a,0x080560d6,0x08056194):ret();return
  if pc==0x08022f94:
   address,buffer,count=reg(1),reg(2),reg(3);log('READ',address,count,routine='native Storage worker read; modeled array-data completion');u.mem_write(buffer,bytes(nor[address:address+count]));ret();return
  if pc==0x0803945c:app_crc=0xffffffff;ret();return
  if pc==0x080394ae:
   value=reg(0)
   for byte in value.to_bytes(4,'big'):
    app_crc^=byte<<24
    for _ in range(8):app_crc=((app_crc<<1)^(0x04c11db7 if app_crc&0x80000000 else 0))&0xffffffff
   ret();return
  if pc==0x0803949a:ret(app_crc);return
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
def call(fn,*args):
 for i,v in enumerate(args):u.reg_write(UC_ARM_REG_R0+i,v)
 u.reg_write(UC_ARM_REG_SP,0x20008300);u.reg_write(UC_ARM_REG_LR,0x0807ff01)
 pc=fn
 while True:
  try:u.emu_start(pc|1,0xffffffff,count=4000000)
  except ResetReached:return 0
  except PendingStorage:
   saved=u.context_save();wrapper,rec=pending.pop(0) if pending else (e.r32(0x20006968),None);assert not pending
   kernel=e.r32(0x0801cf90);current=e.r32(kernel+100);e.w32(kernel+100,e.r32(e.r32(0x20006790)))
   # Run the actual native queue/dequeue/worker. In particular 0802409A
   # converts record flags=1 to backend erase-first=0; do not assume identity.
   e.call(0x08024014,wrapper,sp=0x20009200,maxins=4000000)
   assert e.r8(wrapper+24)==0 and e.r32(wrapper+16)==0
   u.context_restore(saved);e.w32(kernel+100,current)
   ret();pc=u.reg_read(UC_ARM_REG_PC);continue
  assert u.reg_read(UC_ARM_REG_PC)==0x0807ff00,hex(u.reg_read(UC_ARM_REG_PC));break
 return reg(0)
# Feed every packet from the produced SYX through the native vendor updater
# dispatcher and state handlers. Only RTOS/UI/peripheral seams are modeled.
padded=image+b'\xff'*(-len(image)%32)
offset=0
for index,(cmd,body) in enumerate(packets):
 msg=raw_SYX[offset:raw_SYX.index(247,offset)+1];offset+=len(msg)
 assert msg[5]==cmd
 u.mem_write(source,msg);u.mem_write(source+256,struct.pack('<II',source,len(msg)))
 before=e.r32(0x20006934);call(0x08024d2c,0,source+256,0)
 if cmd==0x7c:
  assert e.r32(0x20006934)==0x200037e8
  call(0x08038e04) # modeled expiration of the native preparation timer
  assert e.r32(0x20006934)==0x200037ec
  u.mem_write(source+512,b'\x11\x01\0\0')
  call(0x08038dc8,0x200037ec,source+512) # modeled DSP/UI preparation acknowledgement
  assert e.r32(0x20006934)==0x200037f0
 if index in (0,1,len(packets)-1):print('native message',index,hex(cmd),'state',hex(before),'->',hex(e.r32(0x20006934)),flush=True)
 message_log.append(dict(index=index,command=hex(cmd),bytes=len(msg),state_before=hex(before),state_after=hex(e.r32(0x20006934))))
 if '--probe' in sys.argv and index==4:
  print('REQUESTS',request_log);print('WRITES',[x for x in ops if x['kind']=='WRITE']);print('NOR96',nor[:96].hex());raise SystemExit(0)
assert offset==len(raw_SYX) and not pending
# The native CRC-success state waits for the stock completion event before
# committing metadata/reset. Deliver that event through its real state method.
assert e.r32(0x20006934)==0x200037f8,(hex(app_crc),hex(crc),hex(e.r32(0x200068fc+12)),hashlib.sha256(nor[:size]).hexdigest(),next(((i,a,b) for i,(a,b) in enumerate(zip(nor[:size],image)) if a!=b),None))
# Call success-state dispatch; reset is intercepted only after metadata commit.
reset_seen=[]
def reset_stop(u,pc,n,d):
 if pc==0x08039042:reset_seen.append(True);raise ResetReached()
# Stop at the reset boundary via exception; do not invent a normal return
# from this non-returning reset path or modify code bytes.
u.hook_add(UC_HOOK_CODE,reset_stop,begin=0x08039042,end=0x08039042)
call(0x08039008,0x200037f8,0)
assert reset_seen and unpack_calls==len(padded)//32 and worker_flag_checks==len(padded)//32+1
assert bytes(nor[:size])==image and bytes(nor[0x82000:0x82200])==target and bytes(nor[0x81000:0x81017])==identity
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
 preservation[name]=dict(start=hex(lo),end_exclusive=hex(hi),reads=sum(x['kind']=='READ' and int(x['start'],16)<hi and int(x['end_exclusive'],16)>lo for x in ops),writes=0,erase_overlaps=0,closest_boundary_gap_bytes=distances,closest_operations={k:min((x for x in mutations if x['kind']==k),key=lambda x:max(lo-int(x['end_exclusive'],16),int(x['start'],16)-hi,0)) for k in ('WRITE','ERASE')},sentinel_unchanged=True)
result=dict(confidence='PROVEN',scope='Exact SYX through native vendor updater dispatcher/state handlers, native backend writes/erases and boot validator/installer; explicit RTOS/UI/peripheral seams; not complete cold boot',
 candidate=dict(origin='Decoded directly from produced candidate SYX',bytes=size,padded_bytes=len(padded),sha256=sha(image),CRC=hex(crc),file_generated=False,SYX_generated_by_replay=False,
  bootloader_bytes_changed=0,stock_prefix_changes=json.loads((P/'integration.json').read_text())['hook_patches'],append_end_exclusive=hex(end)),
 target=dict(start='0x82000',end_exclusive='0x82200',origin='synthetic sentinel',before_sha256=sha(target),after_sha256=sha(bytes(nor[0x82000:0x82200]))),
 preservation=preservation,operations=ops,internal_operations=internal,staging_operation_count=staging_count,
 QSPI_write_count=sum(x['kind']=='WRITE' for x in ops),QSPI_erase_count=sum(x['kind']=='ERASE' for x in ops),
 target_write_count=sum(x['kind']=='WRITE' and x['target_overlap'] for x in ops),target_erase_overlap=sum(x['kind']=='ERASE' and x['target_overlap'] for x in ops),
 installed_exact=True,bootloader_unchanged=True,complete_update_sequence=True,exact_SYX_sha256=hashlib.sha256(raw_SYX).hexdigest(),native_message_log=message_log,native_request_records=request_log,native_SysEx_block_unpack_calls=unpack_calls,native_worker_write_flag_checks=worker_flag_checks,
 gaps=['Native SysEx state machine, request queue and Storage worker run; task scheduling, preparation timer/DSP acknowledgement, progress UI/ACK output, CRC peripheral and read-data completion are modeled',
 'Boot storage object constructed, hardware completion and internal flash primitives modeled',
 'Full bootloader constructors/recovery/background/SD closure not run; native app handoff intercepted',
 'NOR erase geometry follows stock 4KiB commands, physical NOR identity not independently measured'],
 H1='PROVEN zero overlap in selected complete-image staging/validator/installer replay; broader cold-boot closure UNKNOWN',hardware_access=False,firmware_transmitted=False)
(O/'installation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('operations','internal_operations','native_message_log','native_request_records')},indent=2))
