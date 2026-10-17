"""Bounded peripheral-function tests; these fixtures are NOT startup continuity."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(O));from spi2_model import SPI2
sys.path.insert(0,str(R/'builds/phase46-msd-filesystem-closure'));import native_cases as N
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'));from independent_validate import decode
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
P=R/'builds/phase63-defect-closure';c=json.loads((P/'development-identity.json').read_text());image=decode((P/(c['candidate']+'.syx')).read_bytes())[0]
def run(name,delay=3,complete=True,enabled=True):
 e=N.Physical();u=e.uc;u.mem_write(0x08010000,image);m=SPI2(delay,complete,response=lambda b:b^0xa5);m.bind(u)
 assert m.read(8)==2 and not m.rx and not m.tx
 m.write(0,0x44 if enabled else 4);m.write(4,0x1703)
 e.w32(0x20001000,0x20001004);e.w32(0x20001004,0x40003800);u.mem_write(0x20002000,b'\x12\x34\x56');u.mem_write(0x20002010,b'LEFT'+b'\x77'*3+b'RIGHT')
 visits=[]
 def hook(u,pc,n,d):visits.append(pc)
 u.hook_add(UC_HOOK_CODE,hook)
 error=None
 try:e.call(0x08037960,0x20001000,0x20002000,0x20002014,3,sp=0x2004fff8,maxins=5000)
 except Exception as ex:error=repr(ex)
 returned=u.reg_read(UC_ARM_REG_PC)==0x0807ff00
 actual=bytes(u.mem_read(0x20002014,3));expected=bytes(x^0xa5 for x in b'\x12\x34\x56')
 assert bytes(u.mem_read(0x20002010,4))==b'LEFT' and bytes(u.mem_read(0x20002017,5))==b'RIGHT'
 if complete and enabled:assert returned and actual==expected and not m.tx and not m.rx,(returned,actual.hex(),expected.hex(),error,m.summary())
 else:assert not returned and not m.rx_bytes and 0x08037960<=u.reg_read(UC_ARM_REG_PC)<=0x0803799e
 return dict(case=name,passed=True,returned=returned,PC=hex(u.reg_read(UC_ARM_REG_PC)),instructions=len(visits),native_error=error,output=actual.hex(),SPI2=m.summary())
def main():
 rows=[run('normal transfer'),run('delayed shift completion',delay=30),run('no completed receive',complete=False),run('SPI master clock disabled',enabled=False)]
 assert rows[1]['instructions']>rows[0]['instructions']
 # No receive byte may exist just because the transmit FIFO is available.
 m=SPI2();assert m.read(8)==2 and m.read(8)&1==0
 result=dict(confidence='PROVEN',candidate_sha256=c['BIN_sha256'],passed=True,cases=rows,scope='Exact candidate37960 bytes with isolated argument/peripheral fixtures, not reset-to-capture continuity',hardware_access=False)
 (O/'model-tests.json').write_text(json.dumps(result,indent=2)+'\n');print('Native SPI2 model sanity PASS',len(rows))
if __name__=='__main__':main()
