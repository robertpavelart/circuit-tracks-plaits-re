"""Exact-byte static helper; no device/transport or builder imports."""
from pathlib import Path
import struct,hashlib,sys
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
from capstone.arm import ARM_OP_MEM,ARM_REG_PC
O=Path(__file__).resolve().parent;R=O.parents[1]
image=(R/'builds/final-hardware-test-package/circuittracks-nor-defect-closure-development.bin').read_bytes()
assert hashlib.sha256(image).hexdigest()=='edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9'
ram=(R/'builds/phase66-usb-safety-classification/frontier-sram.bin').read_bytes()
def read(a,n=4):
 if 0x8010000<=a<0x8010000+len(image):return image[a-0x8010000:a-0x8010000+n]
 if 0x20000000<=a<0x20050000:return ram[a-0x20000000:a-0x20000000+n]
 raise ValueError(hex(a))
def word(a):return int.from_bytes(read(a),'little')
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True
def listing(a,n):
 rows=[]
 for i in md.disasm(read(a,n),a):
  suffix=''
  for op in i.operands:
   if op.type==ARM_OP_MEM and op.mem.base==ARM_REG_PC:
    p=((i.address+4)&~3)+op.mem.disp
    try:suffix+=f' ; [{p:08X}]={word(p):08X}'
    except ValueError:pass
  rows.append(f'{i.address:08X}: {i.mnemonic:10} {i.op_str}{suffix}')
 text='\n'.join(rows)+'\n';(O/f'{a:08x}.asm').write_text(text);return text
if __name__=='__main__':
 for x in sys.argv[1:]:a,n=x.split(':');print(listing(int(a,16),int(n,16)))
