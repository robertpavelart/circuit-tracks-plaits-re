"""Supplemental TX pointer lifetime, timeout and dormancy controls."""
from test_native import *
from unicorn import UC_HOOK_MEM_WRITE

class Observed(Exact):
 def __init__(self,*a,**k):
  self.inflight=None;self.TX=[];self.copy_calls=[];super().__init__(*a,**k)
 def code(self,u,pc,n,d):
  if pc==0x0801aa14 and self.task=='Main':
   dst,src,count=[u.reg_read(UC_ARM_REG_R0+i) for i in range(3)]
   if self.frame and src==self.frame+PACKET:self.copy_calls.append(dict(destination=hex(dst),source=hex(src),bytes=count))
  if pc==0x08024754:
   p=u.reg_read(UC_ARM_REG_R2);ln=u.reg_read(UC_ARM_REG_R3)
   assert p+ln<=self.input_buf or p>=self.input_buf+360
   assert not self.bounds['Main'][0]<=p<self.bounds['Main'][1]
   self.inflight=(p,bytes(u.mem_read(p,ln)));self.TX.append(dict(source=hex(p),bytes=ln,independent_of_parser_and_Main_stack=True))
  return super().code(u,pc,n,d)
 def write(self,u,access,a,n,v,d):
  if self.inflight:
   p,b=self.inflight;assert a+n<=p or a>=p+len(b),'pending USB IN source overwritten'
  return super().write(u,access,a,n,v,d)
 def tick(self,*a,**k):
  if self.inflight:
   p,b=self.inflight;assert bytes(self.u.mem_read(p,len(b)))==b
  if self.usb and self.ticks+1>=self.usb[1]:self.inflight=None
  return super().tick(*a,**k)

def main():
 rows=[]
 for delay in (2,9):
  m=Observed(delay=delay);m.start();finish(m)
  assert len(m.copy_calls)==10 and all(x['source']==hex(m.frame+PACKET) for x in m.copy_calls)
  rows.append(dict(case=f'native router synchronous copy / USB asynchronous source; delay{delay}',confidence='PROVEN',router_copy_calls=m.copy_calls,USB_IN_sources=m.TX,details=m.summary()))
 m=Observed();m.start()
 for _ in range(100):
  m.tick()
  if m.usb:break
 else:raise AssertionError('no USB transfer')
 m.usb=(m.usb[0],10**9);timer(m)
 assert not m.finish(32) and m.e.r8(STATE+4)==3 and m.e.r8(STATE+7)==2 and len(m.reads)==1
 dispatch(m,request(99));assert len(m.reads)==1
 rows.append(dict(case='USB IN completion lost: quarantine, retain frame, no next read',confidence='PROVEN',details=m.summary()))
 # Disconnect while an IN pointer is retained: native router has copied its
 # caller bytes, so returning the Main frame cannot invalidate USB source.
 m=Observed();m.start()
 for _ in range(100):
  m.tick()
  if m.usb:break
 m.u.mem_write(m.dev+0x274,b'\0');assert m.finish(100)
 assert m.e.r8(STATE+4)==3 and len(m.reads)==1
 if m.inflight:
  p,b=m.inflight;assert bytes(m.u.mem_read(p,len(b)))==b
 rows.append(dict(case='disconnect during pending IN; no next read and independent source unchanged',confidence='PROVEN',details=m.summary()))
 # Unsigned deadline subtraction across tick rollover.
 m=Exact('missing',0);m.e.w32(0x2000081c,0xfffffff0);m.start();assert not m.finish()
 timer(m,4998);assert m.e.r8(STATE+4)==1
 timer(m,4999);assert m.e.r8(STATE+4)==3
 rows.append(dict(case='5000 tick deadline across unsigned rollover',confidence='PROVEN'))
 # Execute the real unchanged SysTick handler on exact base and derivative.
 # Compare runtime state and supported registers; extra diagnostic stack
 # writes are expected, so do not assert whole-stack byte equality.
 for label,limit,magic in [('unreserved',0x20044e58,0),('IDLE',STATE,0x4e4f5234),('bad magic',STATE,0)]:
  snapshots=[]
  for candidate in (False,True):
   e=Physical();u=e.uc
   if not candidate:u.mem_write(0x08010000,(O/'rebuilt-sc35d8.bin').read_bytes())
   e.w32(0x20002b44,limit);e.w32(STATE,magic);e.w32(STATE+4,0);e.w32(STATE+8,0x12345678)
   state=bytes(u.mem_read(STATE,12));writes=[]
   def watch(u,access,a,n,v,d):writes.append((a,n,v))
   u.hook_add(UC_HOOK_MEM_WRITE,watch)
   for reg in range(UC_ARM_REG_R0,UC_ARM_REG_R12+1):u.reg_write(reg,0x12340000+reg)
   u.reg_write(UC_ARM_REG_IPSR,15);e.call(0x0805998c,sp=0x2004ff00)
   assert bytes(u.mem_read(STATE,12))==state
   nonstack=[(hex(a),n,v) for a,n,v in writes if not 0x2004f000<=a<0x20050000]
   snapshots.append(dict(supported_registers=[u.reg_read(reg) for reg in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)],sp=u.reg_read(UC_ARM_REG_SP),nonstack_writes=nonstack))
  assert snapshots[0]==snapshots[1],(label,snapshots)
  rows.append(dict(case=f'native SysTick dormancy: {label}',confidence='PROVEN',base_candidate_equal=True,observables=snapshots[1]))
 (O/'ownership-results.json').write_text(json.dumps(dict(confidence='PROVEN',cases=rows,case_count=len(rows),hardware_access=False),indent=2)+'\n')
 print('Ownership cases PASS:',len(rows))
if __name__=='__main__':main()

