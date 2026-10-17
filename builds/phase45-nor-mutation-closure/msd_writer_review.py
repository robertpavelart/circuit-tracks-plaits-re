"""Newly identified initialized-RAM USB MSD write callback, offline only.

Executes actual mode setter and native callback address/branch arithmetic.
Storage read/write completions, debug output and scratch allocation are explicit
seams. No USB device, filesystem mount, WinMM, firmware output or physical NOR.
"""
from pathlib import Path
import sys,json,struct,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase42-exact-rdiag-integration'))
from environment import *
O=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools'));from ct_data_decode import decode
image=(R/'builds/phase44-preflash-redteam-closure/circuittracks-4486-nor-evidence-atomic-test.bin').read_bytes()
assert sha(image)=='0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738'
def run(mode,block):
 e=Physical();u=e.uc;u.mem_write(0x08010000,image)
 init,desc=decode(image)
 # Only immutable initialized records relevant to mode / callback. Running
 # object fixture remains explicit, not presented as completed cold boot.
 u.mem_write(0x20003780,init[0x3780:0x37c4])
 e.call(0x08038c10,mode)
 selected=e.r32(0x200037c0);base=e.r32(selected)
 ops=[];trace=[]
 def ret(v=0):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
 def hook(u,pc,n,d):
  trace.append(hex(pc))
  if pc in (0x08057fe0,0x08026d34):ret()
  elif pc==0x08026d06:ret(0x20020000)
  elif pc==0x08023fd6:ret()
  elif pc==0x08024130:
   a,b,c=[u.reg_read(UC_ARM_REG_R0+i) for i in (1,2,3)]
   ops.append(dict(kind='READ',start=hex(a),length=c));u.mem_write(b,b'\xff'*c);ret()
  elif pc==0x08024164:
   a,b,c=[u.reg_read(UC_ARM_REG_R0+i) for i in (1,2,3)]
   flag=e.r32(u.reg_read(UC_ARM_REG_SP))
   ops.append(dict(kind='WRITE',start=hex(a),length=c,erase_first=flag,
    identity_overlap=a<0x81017 and a+c>0x81000,coeff_overlap=a<0x82200 and a+c>0x82000));ret()
 u.hook_add(UC_HOOK_CODE,hook)
 u.mem_write(0x20021000,b'\xa5'*4096)
 e.call(0x08057ef4,0,0x20021000,block,1,maxins=100000)
 writes=[x for x in ops if x['kind']=='WRITE']
 assert len(writes)==1 and int(writes[0]['start'],16)==base+(block<<12)
 return dict(mode=mode,record=hex(selected),base=hex(base),block=block,operations=ops,native_trace=trace)
def main():
 init,desc=decode(image);ptrs={}
 for target in (0x08057e89,0x08057ef5,0x08057fb1):
  ptrs[hex(target)]=[hex(0x20000000+k) for k in range(len(init)-3) if init[k:k+4]==struct.pack('<I',target)]
 cases=[run(mode,block) for mode in (0,1,2,3) for block in (0x81,0x82)]
 assert all(not any(o.get('coeff_overlap') or o.get('identity_overlap') for o in c['operations']) for c in cases if c['mode']!=3)
 assert any(o.get('coeff_overlap') for c in cases if c['mode']==3 for o in c['operations'])
 result=dict(confidence='PROVEN',scope='Exact initialized callback pointers and mode/address arithmetic; synthetic read completion, scratch allocation, and debug seams; not boot reachability proof',
  candidate_sha256=sha(image),initialized_data_sha256=sha(init),callback_pointers=ptrs,default_mode=init[0x37bc],default_record=hex(int.from_bytes(init[0x37c0:0x37c4],'little')),
  cases=cases,ordinary_boot_mode_invariant='UNKNOWN pending complete mode-setter/USB timer and callback root closure',hardware_access=False,firmware_generated=False)
 (O/'msd-writer-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 # Add focused byte-derived listings without overwriting any pre-limit files.
 for a,n in ((0x080248b4,0xe0),(0x08038c10,0x94),(0x08057e88,0x118),(0x08025d98,0x60),(0x08019e50,0x190)):
  lines=[f'{i.address:08x}: {i.mnemonic:9} {i.op_str}' for i in md.disasm(image[a-0x08010000:a-0x08010000+n],a)]
  (O/f'additional-{a:08x}.asm').write_text('\n'.join(lines)+'\n')
 print('8 native MSD callback cases: default/window modes exclude targets; whole-NOR mode3 reaches both; boot-mode invariant not assumed.')
if __name__=='__main__':main()
