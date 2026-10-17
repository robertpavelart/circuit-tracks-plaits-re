"""Physical-address-only ARM fixture; no Session/E.call artificial stack.
Imports pinned byte sources read-only. No image or device output.
"""
from pathlib import Path
import sys,json,struct
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'plaits/poc/authentic_qualification'))
# Avoid this file's own module name when loading the earlier provenance module.
import importlib.util
spec=importlib.util.spec_from_file_location('qualified_byte_sources',R/'plaits/poc/authentic_qualification/environment.py')
src=importlib.util.module_from_spec(spec);spec.loader.exec_module(src)
REF,STOCK,PUBLISHED,sha=src.REF,src.STOCK,src.PUBLISHED,src.sha
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True
class Physical:
 def __init__(self):
  self.uc=u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  u.mem_map(0x08000000,0x80000)
  u.mem_write(0x08000000,(REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin').read_bytes())
  for at,b in PUBLISHED.parts:u.mem_write(0x08010000+at,b)
  u.mem_map(0x20000000,0x50000)
  ram=(REF/'ctre/Firmware-Analysis/ram_dump_firmware_0x08037988.bin').read_bytes()
  u.mem_write(0x20000000,ram.ljust(0x50000,b'\0'))
  exact=(O/'integrated-internal.bin').read_bytes();u.mem_write(0x08010000,b'\xff'*0x70000);u.mem_write(0x08010000,exact)
  u.mem_map(0x40000000,0x30000);u.mem_map(0xa0001000,0x1000);u.mem_map(0xe000e000,0x2000)
  def stop(u,pc,n,d):
   if pc==0x0807ff00:u.emu_stop()
  u.hook_add(UC_HOOK_CODE,stop)
 def r32(self,a):return struct.unpack('<I',self.uc.mem_read(a,4))[0]
 def w32(self,a,v):self.uc.mem_write(a,struct.pack('<I',v))
 def r8(self,a):return self.uc.mem_read(a,1)[0]
 def call(self,fn,*args,sp=0x20008330,maxins=100000):
  u=self.uc;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x0807ff01)
  for i,v in enumerate(args):u.reg_write(UC_ARM_REG_R0+i,v)
  u.emu_start(fn|1,0xffffffff,count=maxins)
  assert u.reg_read(UC_ARM_REG_PC)==0x0807ff00
  return u.reg_read(UC_ARM_REG_R0)
def w(a):return struct.unpack('<I',PUBLISHED[a-0x08010000:a-0x08010000+4])[0]
def code(a,n):
 lines=[]
 for i in md.disasm(PUBLISHED[a-0x08010000:a-0x08010000+n],a):
  suffix=''
  for op in i.operands:
   if op.type==3 and op.mem.base==11:
    at=((i.address+4)&~3)+op.mem.disp
    if 0x08010000<=at<0x08010000+len(PUBLISHED):suffix=f' ; [{at:08x}]={w(at):08x}'
  lines.append(f'{i.address:08x}: {i.mnemonic:9} {i.op_str}'+suffix)
 (O/f'{a:08x}.asm').write_text('\n'.join(lines)+'\n');return '\n'.join(lines)
if __name__=='__main__':
 for arg in sys.argv[1:]:
  a,n=arg.split(':');print(code(int(a,16),int(n,16)))
