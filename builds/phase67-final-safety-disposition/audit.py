from pathlib import Path
import sys,struct,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase63-defect-closure'
sys.path.insert(0,str(R/'builds/phase42-exact-rdiag-integration'))
from environment import Physical
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
image=(P/'circuittracks-nor-defect-closure-development.bin').read_bytes()
assert hashlib.sha256(image).hexdigest()=='edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9'
ram=(R/'builds/phase66-usb-safety-classification/frontier-sram.bin').read_bytes()
def fresh():
 e=Physical();e.uc.mem_write(0x08010000,image);e.uc.mem_write(0x20000000,ram);return e
e=fresh();router=e.r32(0x200069f4);port=e.r32(e.r32(router+20));pipe=e.r32(port+20);stream=e.r32(e.r32(pipe+4)+4);dev=e.r32(stream+16);table=e.r32(dev+0x28c)
pointers=dict(router=router,port=port,pipe=pipe,stream=stream,dev=dev,class_table=table,class_functions=[e.r32(table+i*4) for i in range(10)])
(O/'pointers.json').write_text(json.dumps(pointers,indent=2))
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
def listing(at,n):
 (O/f'{at:08x}.asm').write_text('\n'.join(f'{i.address:08X}: {i.mnemonic:8} {i.op_str}' for i in md.disasm(image[at-0x8010000:at-0x8010000+n],at))+'\n')
for at,n in [(0x8037ef8,0x248),(0x803a784,0x300),(0x801cfa4,0x180),(0x801d7d8,0x30),(0x803649e,0x142),(0x8047c88,0x194),(0x801e614,0x110),(0x803803c,0x10c),(0x8070b00,0x180),(0x8070500,0x200),(0x8058eb0,0x110),(0x805b568,0x28),(0x801d82c,0x70),(0x801eb30,0x2a0),(0x803b7d4,0x30),(0x8024668,0x70),(0x8026d64,0x70),(0x8020b98,0x100),(0x8020e88,0x20)]+[(a&~1,0x180) for a in pointers['class_functions'] if 0x8010000<=a<0x8075100]:listing(at,n)
if __name__=='__main__':print(json.dumps(pointers,indent=2))
