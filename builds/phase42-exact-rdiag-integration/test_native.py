"""Exact-image native Main/RX/Storage/TX ownership tests; synthetic data only."""
from coupled import *
from rx_probe import process
from unicorn.arm_const import UC_ARM_REG_PRIMASK

def timer(m, elapsed=5000):
 saved=m.u.context_save();task=m.task
 try:
  m.task='IRQ';m.u.reg_write(UC_ARM_REG_IPSR,15)
  m.e.w32(0x2000081c,(m.e.r32(STATE+8)+elapsed)&0xffffffff)
  m.e.call(0x0805998c,sp=0x2004ff00)
 finally:m.u.context_restore(saved);m.task=task

def dispatch(m,data):
 """Supplementary direct reentry attack: never the normal USB dispatch model."""
 saved=m.u.context_save();task=m.task;state=bytes(m.u.mem_read(STATE,12));n=len(m.reads);q=m.queued()
 # A synthetic request argument, not an ownership claim on this low-SRAM
 # address: preserve its prior bytes and restore them before other tasks run.
 scratch=bytes(m.u.mem_read(0x2000b000,len(data)))
 try:
  m.task='IRQ';m.u.reg_write(UC_ARM_REG_IPSR,108)
  p=0x2004f200;desc=0x2004f400
  p=0x2000b000;m.u.mem_write(p,data)
  m.u.mem_write(desc,struct.pack('<II',p,len(data)))
  m.e.call(0x0801eb30,0,desc,0,sp=0x2004ff00)
 finally:
  m.u.mem_write(0x2000b000,scratch);m.u.context_restore(saved);m.task=task
 assert len(m.reads)==n and m.queued()==q and bytes(m.u.mem_read(STATE,12))==state

def finish(m):
 assert m.finish(1500);m.verify()
 assert m.service_PCs=={'0x8020ea0','0x8020f62','0x8035c58','0x801c894','0x801eb30'}
 assert m.handler_return_verified

def normal_case(name,trigger=None,opts=None,data=None):
 m=Exact(**(opts or {}));m.start();injected=False
 for _ in range(1500):
  if trigger and not injected and trigger(m):
   before=m.raw_snapshot();enqueue(m,data or request(37));assert m.raw_snapshot()==before;injected=True
  if m.done:break
  m.tick()
 else:raise AssertionError('unbounded normal capture')
 m.verify();assert not trigger or injected
 return dict(case=name,confidence='PROVEN',injection=injected,entry_count=m.entry_count,handler_restored_before_parser_reuse=m.handler_return_verified,details=m.summary())

def main():
 rows=[]
 rows.append(normal_case('A normal'))
 rows.append(normal_case('B duplicate immediately after accept',lambda m:len(m.reads)==0))
 # Full ring/parser/fanout replay after the callback has returned.
 for label,data in [('C duplicate after handler return',request(37)),('N new session after SUCCESS',request(99))]:
  m=Exact();m.start();finish(m);before=bytes(m.u.mem_read(STATE,12));enqueue(m,data);process(m)
  assert m.entry_count==2 and len(m.reads)==9 and bytes(m.u.mem_read(STATE,12))==before
  rows.append(dict(case=label,confidence='PROVEN',entries=2,NOR_reads=9,terminal_state_preserved=True))
 m=Exact();m.start();finish(m);before=bytes(m.u.mem_read(STATE,12));snap=m.state()
 m.u.mem_write(m.input_buf,bytes((i*19+3)&255 for i in range(232)))
 assert bytes(m.u.mem_read(STATE,12))==before and m.state()==snap
 enqueue(m,request(99));process(m)
 assert bytes(m.u.mem_read(STATE,12))==before and len(m.reads)==9 and m.entry_count==2
 rows.append(dict(case='D adversarial overwrite of all 232 parser bytes after return',confidence='PROVEN',bytes_overwritten=232,persistent_state_unchanged=True,NOR_reads=9))
 for letter,k in [('E',0),('F',1),('G',5),('H',8)]:
  rows.append(normal_case(f'{letter} queued duplicate during read global{k}',lambda m,k=k:m.active is not None and m.active['chunk']==k))
 other=bytearray(request(37));other[4]=6
 rows.append(normal_case('I other rdiag while ACTIVE',lambda m:m.active is not None,data=bytes(other)))
 rows.append(normal_case('J stock SysEx while ACTIVE',lambda m:m.active is not None,data=bytes.fromhex('f00020297f7ff7')))
 rows.append(normal_case('K TX backpressure',opts={'delay':9}))
 # Forced nested dispatch supplements natural queued dispatch at the exact
 # command entry: ACTIVE already stored but no Storage request yet exists.
 m=Exact();attack=[]
 def immediate(u,pc,n,d):
  if pc==L['command'] and not attack:
   attack.append(True);m.waits['Main']={'kind':'adversarial admission boundary'};raise Pause()
 m.u.hook_add(UC_HOOK_CODE,immediate);m.start();dispatch(m,m.expected_input);m.run_cpu('Main',resume=True);finish(m)
 assert len(attack)==1 and m.entry_count==2
 rows.append(dict(case='B supplemental direct reentry at first command instruction',confidence='PROVEN',zero_extra_requests=True,details=m.summary()))
 m=Exact();m.start();assert m.finish(1500,disconnect_after=4)
 assert len(m.reads)==5 and len(m.frames)==5 and m.e.r8(STATE+4)==3 and m.e.r8(STATE+7)==0
 enqueue(m,request(99));process(m);assert len(m.reads)==5
 rows.append(dict(case='L disconnect after target chunk3; O command after failure',confidence='PROVEN',details=m.summary()))
 for kind in ('tef','missing'):
  for k in (0,1,5,8):
   m=Exact(kind,k);m.start();assert not m.finish()
   assert m.e.r8(STATE+4)==1 and m.e.r8(STATE+7)==1
   timer(m,4998);assert m.e.r8(STATE+4)==1
   timer(m,4999);assert m.e.r8(STATE+4)==3 and m.e.r8(STATE+7)==1
   before=m.raw_snapshot();dispatch(m,m.expected_input);assert m.raw_snapshot()==before
   enqueue(m,request(99));assert len(m.reads)==k+1 and m.e.r8(m.backend+8)==0 and m.e.r32(m.wrapper+16)==1
   rows.append(dict(case=f'M {kind} global{k}; O direct command after FAILED_QUARANTINED',confidence='PROVEN',deadline_ticks=5000,retained_live_request=True,details=m.summary()))
 # Late normal completion after quarantine can finish the existing wait but
 # must never create the next read or promote FAILED to SUCCESS.
 m=Exact('missing',1);m.start();assert not m.finish();timer(m)
 m.active['issued']=False;m.irq('normal');assert m.finish()
 assert len(m.reads)==2 and len(m.frames)==1 and m.e.r8(STATE+4)==3 and m.e.r8(STATE+7)==0
 enqueue(m,request(99));process(m);assert len(m.reads)==2
 rows.append(dict(case='late completion after quarantine; queued retry rejected after return',confidence='PROVEN',details=m.summary()))
 # Quarantine while the final completion is in flight must stay terminal.
 m=Exact();m.start()
 for _ in range(1500):
  if len(m.frames)==10 and m.usb is not None:break
  m.tick()
 else:raise AssertionError('completion not observed')
 timer(m);assert m.finish() and m.e.r8(STATE+4)==3
 rows.append(dict(case='deadline during final TX cannot overwrite quarantine with SUCCESS',confidence='PROVEN',details=m.summary()))
 # Lazy state reservation failure closes admission and never alters heap/state.
 reservation=[]
 for cursor in (STATE,STATE+4,0x20044d7c):
  e=Physical();e.w32(0x20002b44,0x20044e58);e.w32(0x20002b48,cursor);before=bytes(e.uc.mem_read(STATE,232));r=e.call(0x0805dbcc)
  if cursor==STATE:
   assert r==0x20044d7c and e.r32(0x20002b44)==STATE
   e.uc.mem_write(STATE+4,b'\x03');e.uc.mem_write(0x20044d7c,b'\0'*4)
   assert e.call(0x0805dbcc)==0x20044d7c and e.r8(STATE+4)==3
  else:assert r==0 and e.r32(0x20002b44)==0x20044e58 and bytes(e.uc.mem_read(STATE,232))==before
  reservation.append(dict(cursor=hex(cursor),accepted=cursor==STATE))
 rows.append(dict(case='reservation boundary and MasterFX reinitialization',confidence='PROVEN',tests=reservation,terminal_latch_survives_MasterFX_reinit=True))
 result=dict(confidence='PROVEN',scope='Exact integrated image; physical running-RAM fixture, native USB length-prefixed RX ring/Main/parser/fanout and Storage/TX paths; modeled RTOS scheduling and peripheral completion. No cold boot or hardware.',cases=rows,case_count=len(rows),hardware_access=False,SYX_generated=False)
 (O/'native-results.json').write_text(json.dumps(result,indent=2)+'\n');print('Native cases PASS:',len(rows))
if __name__=='__main__':main()


