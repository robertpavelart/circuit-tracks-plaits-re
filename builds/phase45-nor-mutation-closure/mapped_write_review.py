"""Native file block mapper address bounds, with queue submission intercepted.

Out-of-range logical blocks are adversarial interface arguments, NOT a claim
that ordinary mounted filesystems actually produce them. They identify the
upstream bound that must be proved for a complete mutation closure.
"""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase42-exact-rdiag-integration'))
from environment import *
O=Path(__file__).resolve().parent
def main():
 rows=[]
 for block in (0,1,0x1f2b,0xfffad,0xfffae):
  e=Physical();u=e.uc;u.mem_write(0x08010000,(R/'builds/phase44-preflash-redteam-closure/circuittracks-4486-nor-evidence-atomic-test.bin').read_bytes())
  obj=0x20000aa0;geometry=e.r32(obj+8)
  assert e.r32(geometry)==0xd4000 and e.r32(geometry+4)==4096
  ops=[]
  def hook(u,pc,n,d):
   if pc==0x08024164:
    a=u.reg_read(UC_ARM_REG_R1);count=u.reg_read(UC_ARM_REG_R3)
    ops.append(dict(address=hex(a),bytes=count,erase_first_requested=e.r32(u.reg_read(UC_ARM_REG_SP)),
     identity_overlap=a<0x81017 and a+count>0x81000,coefficient_overlap=a<0x82200 and a+count>0x82000))
    u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
  u.hook_add(UC_HOOK_CODE,hook)
  e.call(0x0801af1e,obj,0x20022000,block,1)
  assert len(ops)==1 and int(ops[0]['address'],16)==(0xd4000+4096*block)&0xffffffff
  rows.append(dict(logical_block=hex(block),operation=ops[0],upstream_validity='Unproved adversarial LBA' if block>0x1f2b else 'Within initialized partition extent'))
 assert rows[-1]['operation']['coefficient_overlap'] and rows[-2]['operation']['identity_overlap']
 result=dict(confidence='PROVEN',scope='Native block mapper; intercepted before storage request, no array mutation or boot simulation',
  caller='File disk-write abstraction; filesystem upstream logical-block validity not yet exhaustively proved',
  routine='0x0801af1e',geometry_record='0x20000a98',base='0xd4000',sector_size=4096,
  safe_if='0 <= LBA < 0x1f2c and count <= 0x1f2c-LBA; no overflow; stable initialized object binding',
  primitive_has_own_LBA_bound_check=False,cases=rows,hardware_access=False,firmware_generated=False)
 (O/'mapped-write-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print('Mapped write normal partition excludes targets; upstream LBA bound required to exclude 32-bit wrap.')
if __name__=='__main__':main()
