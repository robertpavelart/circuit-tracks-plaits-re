"""Phase31: reuse unchanged physical phase30 runner; no recovery fabricated."""
from support import *

checks=[]
def ck(name,value):
 assert value,name
 checks.append(name)

def idle_feed(m):
 # Run the actual idle callback on a physical fixture stack. This is not a
 # scheduler/time simulation. Save CPU context; no task ownership edits.
 saved=m.u.context_save();task=m.task;m.task='IRQ'
 writes=[]
 def log(u,access,a,n,v,d):
  if a>=0x40000000:writes.append(dict(address=hex(a),value=hex(v),bytes=n))
 hook=m.u.hook_add(UC_HOOK_MEM_WRITE,log)
 def wake(u,pc,n,d):
  if pc==0x0801d766:u.reg_write(UC_ARM_REG_PC,pc+2|1) # WFI resumes on an explicitly modeled wake
 wake_hook=m.u.hook_add(UC_HOOK_CODE,wake)
 try:m.e.call(0x0801d760,sp=0x2004fff0)
 finally:
  m.u.hook_del(hook);m.u.hook_del(wake_hook);m.u.context_restore(saved);m.task=task
 return writes

cases=[]
for kind in ('tef','missing'):
 for chunk in (0,4,7):
  m=P30.Model(kind,chunk);m.start();ck(f'{kind}/{chunk} initial hang',not m.finish())
  before=m.state();writes=[]
  for i in range(128):
   m.tick();writes.extend(idle_feed(m))
  after=m.state()
  ck(f'{kind}/{chunk} ownership unchanged for 128 more ticks',before==after)
  ck(f'{kind}/{chunk} watchdog feed occurs independently',len(writes)==128 and all(x['address']=='0x40003000' and x['value']=='0xaaaa' for x in writes))
  ck(f'{kind}/{chunk} infinite native wait',m.waits['Storage']['timeout_argument']=='0xffffffff')
  ck(f'{kind}/{chunk} no release or false completion',after['semaphore']==0 and after['sync']==1 and not after['buffer_reusable'] and not after['Main_returned'] and after['frames']==chunk)
  ck(f'{kind}/{chunk} selected requests read-only',m.commands==['0xec']*(chunk+1) and m.raw_cpu_writes==0)
  ck(f'{kind}/{chunk} no forbidden abort',all(not(int(x['value'],16)&2) for x in m.MMIO if x['address']=='0xa0001000'))
  cases.append(dict(kind=kind,chunk=chunk,confidence='PROVEN',before=before,after=after,additional_ticks=128,
   idle_callback_invocations=128,watchdog_writes=writes,second_read='Not admitted: original request remains active; no force release',details=m.summary()))

m=P30.Model();m.start();ck('unchanged normal architecture still completes',m.finish());m.verify()
f=len(m.frames);b=len(m.usb_bytes);m.start(38);ck('second normal request succeeds without reset',m.finish());m.verify(38,f,b)
result=dict(confidence='PROVEN',scope='Fault injections and native idle callback; peripheral effects and task switching explicitly modeled, not hardware elapsed time',
 checks=checks,cases=cases,normal_then_second_normal=m.summary(),stock_unwind_found=False,
 forced_release=False,second_read_after_fault=False,second_read_after_fault_meaning='Not attempted unsafely; live Main prevents admission',
 automatic_watchdog_restart_qualified=False,H4=dict(status='FAIL',confidence='PROVEN',reason='Bounded-failure requirement fails in six selected fault models'),
 safe_reboot='UNKNOWN: not exercised; H1/H2 unchanged and outside scope',verdict='UNQUALIFIED',hardware_access=False,firmware_generated=False)
(O/'fault-replay.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(assertions=len(checks),fault_cases=len(cases),H4=result['H4'],verdict=result['verdict']),indent=2))
