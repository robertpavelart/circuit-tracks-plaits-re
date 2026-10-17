"""Genuine reset entry, fresh volatile maps. Stop honestly at missing platform.

No running-RAM import. Blank SRAM is a deterministic representative power-on
fixture, not a silicon promise that SRAM is physically cleared by power loss.
"""
from support import *
from collections import Counter,deque

class Cold:
 def __init__(self,variant='diagnostic'):
  self.uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u=self.uc
  u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M7)
  for a,n in ((0x08000000,0x80000),(0x20000000,0x50000),(0x40000000,0x30000),(0xa0001000,0x1000),(0xe000e000,0x2000),(0xe0042000,0x1000)):
   u.mem_map(a,n)
  u.mem_write(0x08000000,ROM)
  if variant=='stock':
   u.mem_write(0x08010000,STOCK);self.image=STOCK
  else:
   for at,b in PUBLISHED.parts:u.mem_write(0x08010000+at,b)
   self.image=candidate(self)

def probe(entry,poison=False,variant='diagnostic'):
 e=Cold(variant);u=e.uc;events=[];reads=[];counts=Counter();last=deque(maxlen=24);why={};mutations=[]
 if poison:u.mem_write(0x20000000,b'\xa5'*0x50000)
 def code(u,pc,n,d):
  counts[pc]+=1;last.append(hex(pc))
  if counts[pc]>10000:why.update(kind='unmodeled platform wait/loop',pc=hex(pc));u.emu_stop()
  if pc in (0x08022fdc,0x08023078):
   mutations.append(dict(kind='WRITE' if pc==0x08022fdc else 'ERASE',routine=hex(pc),address=hex(u.reg_read(UC_ARM_REG_R1)),length_or_end=hex(u.reg_read(UC_ARM_REG_R3 if pc==0x08022fdc else UC_ARM_REG_R2))))
  if pc==0x08022f94:events.append(dict(kind='READ',address=hex(u.reg_read(UC_ARM_REG_R1)),length=u.reg_read(UC_ARM_REG_R3)))
 def write(u,access,a,n,v,d):
  if 0x08000000<=a<0x08080000:mutations.append(dict(kind='internal flash CPU store',address=hex(a),size=n))
  if a>=0x40000000 and len(events)<200:events.append(dict(kind='MMIO store',pc=hex(u.reg_read(UC_ARM_REG_PC)),address=hex(a),value=hex(v)))
 def read(u,access,a,n,v,d):
  if a>=0x40000000:
   item=dict(pc=hex(u.reg_read(UC_ARM_REG_PC)),address=hex(a),size=n)
   if not reads or reads[-1]!=item:
    if len(reads)<200:reads.append(item)
 def invalid(u,access,a,n,v,d):why.update(kind='unmapped platform access',address=hex(a),pc=hex(u.reg_read(UC_ARM_REG_PC)));return False
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
 base=0x08000000 if entry=='bootloader' else 0x08010000
 sp,pc=struct.unpack('<II',bytes(u.mem_read(base,8)))
 u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_MSP,sp);u.reg_write(UC_ARM_REG_CONTROL,0);u.reg_write(UC_ARM_REG_IPSR,0)
 try:u.emu_start(pc,0xffffffff,count=1500000)
 except Exception as exc:
  why.setdefault('kind','emulator/platform exception');why['exception']=str(exc);why['pc']=hex(u.reg_read(UC_ARM_REG_PC))
 if not why:why=dict(kind='instruction budget exhausted',pc=hex(u.reg_read(UC_ARM_REG_PC)))
 result=dict(confidence='PROVEN',scope='Actual reset prefix only; NOT stable application first boot',entry=entry,variant=variant,reset_vector=hex(pc),initial_SP=hex(sp),
  SRAM_fixture='A5 poison' if poison else 'zero representative',candidate_sha256=sha(e.image),running_RAM_snapshot_imported=False,
  stop=why,executed_instructions=sum(counts.values()),last_PCs=list(last),MMIO_and_storage_events=events,last_distinct_MMIO_reads=reads,
  stop_registers={str(i):hex(u.reg_read(UC_ARM_REG_R0+i)) for i in range(13)},stop_xPSR=hex(u.reg_read(UC_ARM_REG_XPSR)),
  persistent_mutations_observed=mutations,stable_USB_MIDI_state_reached=False,
  complete_first_boot_target_reads=None,complete_first_boot_target_writes=None,complete_first_boot_target_erase_overlap=None,
  note='Unobserved suffix counts UNKNOWN, never reported as zero; no peripheral-ready flags fabricated')
 dump(int(why.get('pc',hex(u.reg_read(UC_ARM_REG_PC))),16)&~1,64)
 return result

if __name__=='__main__':
 rows=[probe(entry,poison) for entry in ('bootloader','application') for poison in (False,True)]
 rows.extend(probe(entry,variant='stock') for entry in ('bootloader','application'))
 (O/'cold-boot-prefix.json').write_text(json.dumps(dict(confidence='PROVEN',probes=rows,H2='UNKNOWN',P2='UNKNOWN',P3='UNKNOWN'),indent=2)+'\n')
 print(json.dumps([dict(entry=x['entry'],fixture=x['SRAM_fixture'],stop=x['stop'],instructions=x['executed_instructions']) for x in rows],indent=2))
