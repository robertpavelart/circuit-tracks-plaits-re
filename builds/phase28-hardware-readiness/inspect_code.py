"""Read-only targeted disassembly/object inspection; no device or firmware output."""
from pathlib import Path
import sys,json,struct
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'plaits/poc/authentic_qualification'))
from environment import REF,STOCK,PUBLISHED,authentic_session,sha
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
FLASH=(REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin').read_bytes()
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True
def code(a,n):
 b=FLASH[a-0x08000000:a-0x08000000+n] if a<0x08010000 else STOCK[a-0x08010000:a-0x08010000+n]
 lines=[]
 for i in md.disasm(b,a):
  suffix=''
  for op in i.operands:
   if op.type==3 and op.mem.base==11:
    at=((i.address+4)&~3)+op.mem.disp
    if 0x08000000<=at<0x08080000:suffix=f' ; literal[{at:08x}]={w(at):08x}'
  lines.append(f'{i.address:08x}: {i.mnemonic:9} {i.op_str}'+suffix)
 (O/f'{a:08x}.asm').write_text('\n'.join(lines)+'\n');return '\n'.join(lines)
def w(a):return struct.unpack_from('<I',FLASH,a-0x08000000)[0]
if __name__=='__main__':
 if len(sys.argv)>1:
  print(code(int(sys.argv[1],16),int(sys.argv[2],16)));raise SystemExit
 s=authentic_session();e=s.e;g=w(0x0801edc4);obj=e.r32(g);vt=e.r32(obj)
 r=dict(global_address=hex(g),object=hex(obj),vtable=hex(vt),methods=[hex(e.r32(vt+i)) for i in range(0,40,4)],fields=[hex(e.r32(obj+i)) for i in range(0,64,4)])
 r['dispatcher_pointer_occurrences']=[hex(0x08010000+i) for i in range(0,len(STOCK)-3,2) if STOCK[i:i+4]==struct.pack('<I',0x0801eb31)]
 (O/'initial-objects.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
