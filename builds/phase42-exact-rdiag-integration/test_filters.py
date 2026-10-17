"""Native malformed/retired commands and exact forwarding boundaries."""
from test_native import *

def main():
 rows=[]
 cases=[]
 for label,mut in [('nonzero payload',lambda b:b.__setitem__(6,1)),('retired write command6',lambda b:b.__setitem__(4,6)),('retired read command1',lambda b:b.__setitem__(4,1)),('unterminated',lambda b:b.__setitem__(-1,0)),('short request',lambda b:b.__delitem__(6))]:
  b=bytearray(request(37));mut(b);cases.append((label,bytes(b)))
 for label,b in cases:
  m=Exact();m.start(data=b)
  assert m.done and not m.reads and not m.frames and m.e.r8(STATE+4)==0 and m.frame is None
  rows.append(dict(case=label,confidence='PROVEN',native_Main_parser=True,entry_count=m.entry_count,reads=0,state='IDLE'))
 # Observe the real forwarding prologue; do not fabricate a completed parser
 # message for malformed requests above. This is a separate call-boundary test.
 for label,data in [('stock identity',bytes.fromhex('f07e7f0601f7')),('Novation',bytes.fromhex('f000202901640801f7'))]:
  e=Physical();u=e.uc;p=0x2000a050;desc=0x200082f0
  u.mem_write(p,data);u.mem_write(desc,struct.pack('<II',p,len(data)));seen=[]
  def stop(u,pc,n,d):seen.append(pc);u.emu_stop()
  u.hook_add(UC_HOOK_CODE,stop,begin=0x0801eb34,end=0x0801eb34)
  initial={UC_ARM_REG_R0:0,UC_ARM_REG_R1:desc,UC_ARM_REG_R2:123,UC_ARM_REG_SP:0x200082d8,UC_ARM_REG_LR:0x0807ff01}
  for r,v in initial.items():u.reg_write(r,v)
  u.emu_start(0x0801eb31,0xffffffff,count=100000)
  assert seen==[0x0801eb34] and u.reg_read(UC_ARM_REG_SP)==initial[UC_ARM_REG_SP]-24
  assert all(u.reg_read(r)==v for r,v in initial.items() if r!=UC_ARM_REG_SP)
  rows.append(dict(case=label,confidence='PROVEN',unchanged_original_prologue=True,forwarded_to='0801EB34'))
 m=Exact(interleave=True);m.start();finish(m)
 rows.append(dict(case='forced preemption after first Storage notify',confidence='PROVEN',details=m.summary()))
 bad=bytearray(request(37));bad[6]=1
 rows.append(normal_case('malformed SysEx queued while ACTIVE',lambda m:m.active is not None,data=bytes(bad)))
 # Silent terminal rejection must restore the incoming interrupt mask.
 m=Exact();m.start();finish(m)
 for mask in (0,1):
  m.u.reg_write(UC_ARM_REG_PRIMASK,mask);dispatch(m,request(99));assert m.u.reg_read(UC_ARM_REG_PRIMASK)==mask
 rows.append(dict(case='terminal rejection preserves incoming PRIMASK 0 and 1',confidence='PROVEN',NOR_reads=9))
 (O/'filter-results.json').write_text(json.dumps(dict(confidence='PROVEN',cases=rows,case_count=len(rows)),indent=2)+'\n')
 print('Filter cases PASS:',len(rows))
if __name__=='__main__':main()
