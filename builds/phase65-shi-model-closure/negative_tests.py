"""Bounded native SPI wait + SHI framing/count checks; never startup fixtures."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase46-msd-filesystem-closure'));import native_cases as N
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'));from independent_validate import decode
from spi2_model import SPI2
from dsp_peer import BootPeer
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
c=json.loads((R/'builds/phase63-defect-closure/development-identity.json').read_text());image=decode((R/'builds/phase63-defect-closure'/(c['candidate']+'.syx')).read_bytes())[0]
def native_command(name,delay=3,complete=True):
 e=N.Physical();u=e.uc;u.mem_write(0x08010000,image);p=BootPeer();p.command=True;m=SPI2(delay,complete,response=p.byte);m.bind(u);m.write(0,0x44);m.write(4,0x1703)
 e.w32(0x20001000,0x20001004);e.w32(0x20001004,0x40003800);u.mem_write(0x20002000,bytes.fromhex('200100'));u.mem_write(0x20002010,b'LEFT'+bytes(3)+b'RIGHT')
 count=[0]
 def hook(u,pc,n,d):count[0]+=1
 u.hook_add(UC_HOOK_CODE,hook);err=None
 try:e.call(0x08037960,0x20001000,0x20002000,0x20002014,3,sp=0x2004fff8,maxins=5000)
 except Exception as ex:err=str(ex)
 returned=u.reg_read(UC_ARM_REG_PC)==0x0807ff00
 assert bytes(u.mem_read(0x20002010,4))==b'LEFT' and bytes(u.mem_read(0x20002017,5))==b'RIGHT'
 if complete:assert returned and p.width==2 and not p.frame
 else:assert not returned and p.width==3 and not p.frame and u.reg_read(UC_ARM_REG_PC)==0x0803798a
 return dict(case=name,passed=True,native_instructions=count[0],PC=hex(u.reg_read(UC_ARM_REG_PC)),width=p.width,returned=returned,observer_error=err)
def data_peer():
 p=BootPeer();p.width=2;p.pointer=0xc00;p.command=False;return p
def main():
 rows=[native_command('normal command'),native_command('not-ready: no completed SPI receive',complete=False),native_command('delayed readiness',delay=30)]
 assert rows[2]['native_instructions']>rows[0]['native_instructions']
 data=bytes((i*73+11)&255 for i in range(512))
 p=data_peer();p.byte(data[0]);assert p.pointer==0xc00 and p.frame==[data[0]] and 0xc00 not in p.memory['X']
 rows.append(dict(case='incomplete16-bit word: no premature consumption',passed=True,bytes_received=1,words_stored=0))
 p=data_peer()
 for b in data[:-2]:p.byte(b)
 assert p.pointer==0xcff and 0xcff not in p.memory['X'] and len(p.memory['X'])==255
 # The SHI has no descriptor count/CRC; remaining DMA bytes are a separate condition.
 remaining=512-len(data[:-2]);assert remaining==2
 rows.append(dict(case='incomplete512-byte descriptor / wrong255-word count',passed=True,received_bytes=510,DMA_remaining_bytes=remaining,stored_words=255,last_coefficient_absent=True,completion_permitted=False,scope='wire/count invariant, not a native RTOS timeout replay'))
 for b in data[-2:]:p.byte(b)
 assert p.pointer==0xd00 and len(p.memory['X'])==256
 expected=[int.from_bytes(data[i:i+2],'big')<<8 for i in range(0,512,2)]
 assert [p.memory['X'][0xc00+i] for i in range(256)]==expected
 rows.append(dict(case='remaining bytes complete exact256-word transfer',passed=True,stored_words=256,byte_order='big endian16-bit left-justified in24-bit word'))
 # A caller asking for255 words is not magically expanded or rejected by SHI hardware.
 q=data_peer()
 for b in data[:510]:q.byte(b)
 assert not q.frame and q.pointer==0xcff and len(q.memory['X'])==255
 rows.append(dict(case='wrong programmed count has no SHI count-validation status',passed=True,received_bytes=510,stored_words=255,expected_behavior='255 complete words if510 bytes are genuinely requested; native normal producer requests512; no fabricated device count error',scope='SHI word framing, not proof of a native firmware error exit'))
 (O/'negative-tests.json').write_text(json.dumps(dict(confidence='PROVEN',candidate_sha256=c['BIN_sha256'],passed=True,cases=rows,scope='three native37960 command cases plus exact wire invariants; incompleteDMA native task wait covered separately only if explicitly recorded'),indent=2)+'\n')
 print('Bounded SHI checks PASS',len(rows))
if __name__=='__main__':main()
