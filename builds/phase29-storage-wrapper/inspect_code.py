"""Read-only B1.3 instruction/object inspection. Never constructs firmware."""
from pathlib import Path
import sys,json,struct
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'plaits/poc/authentic_qualification'))
from environment import REF,STOCK,PUBLISHED,authentic_session,sha
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True
def code(a,n):
 b=PUBLISHED[a-0x08010000:a-0x08010000+n];lines=[]
 for i in md.disasm(b,a):
  suffix=''
  for op in i.operands:
   if op.type==3 and op.mem.base==11:
    at=((i.address+4)&~3)+op.mem.disp
    if 0x08010000<=at<0x08010000+len(PUBLISHED):suffix=f' ; literal[{at:08x}]={w(at):08x}'
  lines.append(f'{i.address:08x}: {i.mnemonic:9} {i.op_str}'+suffix)
 (O/f'{a:08x}.asm').write_text('\n'.join(lines)+'\n');return '\n'.join(lines)
def w(a):return struct.unpack('<I',PUBLISHED[a-0x08010000:a-0x08010000+4])[0]
if __name__=='__main__':
 for x in sys.argv[1:]:
  a,n=x.split(':');print(code(int(a,16),int(n,16)))
