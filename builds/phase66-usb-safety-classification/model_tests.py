"""Exact candidate USB helpers, isolated register fixtures, no hardware ports."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase46-msd-filesystem-closure'));import native_cases as N
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'));from independent_validate import decode
from usb_model import USBInit,USBModelGap
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
P=R/'builds/phase63-defect-closure';c=json.loads((P/'development-identity.json').read_text());image=decode((P/(c['candidate']+'.syx')).read_bytes())[0]
def run(name,fn,delay=3,idle=True,complete=True):
 e=N.Physical();u=e.uc;u.mem_write(0x08010000,image);m=USBInit(delay,idle,complete);m.bind(u)
 u.mem_write(0x20044d70,b'GEOMETRYTEST');before=bytes(u.mem_read(0x20044d70,12));calls=[0]
 def hook(u,pc,n,d):
  calls[0]+=1
  if pc in(0x08037494,0x080374d4,0x08037648,0x08024164,0x080241b8):raise AssertionError('unexpected NOR mutation call')
 u.hook_add(UC_HOOK_CODE,hook)
 if fn==0x08048316:m.reg[8]=0x11
 result=e.call(fn,m.BASE,sp=0x2004fff8,maxins=3000000)
 assert bytes(u.mem_read(0x20044d70,12))==before
 assert u.reg_read(UC_ARM_REG_SP)==0x2004fff8
 if fn==0x08048316:assert result==0 and m.reg[8]==0x10 and len(m.trace)==2
 elif complete and idle:assert result==0 and not m.pending
 else:assert result!=0
 return dict(case=name,passed=True,return_value=result,instructions=calls[0],PC=hex(u.reg_read(UC_ARM_REG_PC)),USB=m.summary())
def main():
 rows=[run('global interrupt disable: no status wait',0x08048316),run('normal native core reset',0x08048a8e),run('delayed reset',0x08048a8e,delay=30),run('AHB never idle',0x08048a8e,idle=False),run('reset never clears',0x08048a8e,complete=False)]
 assert rows[2]['instructions']>rows[1]['instructions']
 m=USBInit();m.write(0x910,64);m.write(0x914,0x20002000)
 try:m.write(0x900,0x80000000)
 except USBModelGap:rows.append(dict(case='endpoint activation refuses unmodeled memory transfer',passed=True))
 else:raise AssertionError('fabricated endpoint completion')
 (O/'model-tests.json').write_text(json.dumps(dict(confidence='PROVEN',candidate_sha256=c['BIN_sha256'],passed=True,cases=rows,scope='Exact helper bytes with isolated argument/register fixtures, not startup RAM substitution'),indent=2)+'\n');print('USB helper cases PASS',len(rows))
if __name__=='__main__':main()
