"""Read-only phase30 reuse. All new outputs stay in phase31."""
from pathlib import Path
import sys,json,struct,re
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'builds/phase30-chunked-storage'))
import replay as P30
from environment import Physical,REF,STOCK,PUBLISHED,sha,md,w
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
def code(a,n):
 lines=[]
 for i in md.disasm(PUBLISHED[a-0x08010000:a-0x08010000+n],a):
  tail=''
  for op in i.operands:
   if op.type==3 and op.mem.base==11:
    at=((i.address+4)&~3)+op.mem.disp
    if 0x08010000<=at<0x08010000+len(PUBLISHED):tail=f' ; [{at:08x}]={w(at):08x}'
  lines.append(f'{i.address:08x}: {i.mnemonic:9} {i.op_str}'+tail)
 (O/f'{a:08x}.asm').write_text('\n'.join(lines)+'\n');return '\n'.join(lines)
if __name__=='__main__':
 for x in sys.argv[1:]:
  a,n=x.split(':');print(code(int(a,16),int(n,16)))
