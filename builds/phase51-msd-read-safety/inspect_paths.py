"""Inspect existing B1.3 paths and initialized callback objects; text only."""
from pathlib import Path
import sys,json,struct,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase50-msd-readonly-geometry'))
from inspect_b13 import PUBLISHED,STOCK,decode,md,ARM_OP_MEM,ARM_REG_PC
RANGES=[(0x08022f94,0x48),(0x08037430,0xa4),(0x08037596,0x2a),(0x08022826,0x64),
 (0x0801a7e4,0x48),(0x08024630,0x38),(0x080246a8,0x1c),(0x0801e624,0xa8),
 (0x08047c88,0x6a),(0x08047cf2,0x4e),(0x08058eb0,0x1c),
 (0x080245c6,0x86),(0x0802464c,0x1c),(0x08037380,0x24),
 (0x0801c072,0x86),(0x0801c4d4,0x20),(0x08057650,0x2c),
 (0x08024d2c,0x30),(0x0802484c,0x58),(0x08038b70,0x30),
 (0x0801eb30,0x7c),(0x0803b6a6,0x132)]
def main():
    b=PUBLISHED[:];init,_=decode(b)
    for a,n in RANGES:
        lines=[]
        for i in md.disasm(b[a-0x8010000:a-0x8010000+n],a):
            tail=''
            for o in i.operands:
                if o.type==ARM_OP_MEM and o.mem.base==ARM_REG_PC:
                    at=((i.address+4)&~3)+o.mem.disp
                    if 0x8010000<=at<=0x8010000+len(b)-4:tail+=f' ; [{at:08X}]={struct.unpack_from("<I",b,at-0x8010000)[0]:08X}'
            lines.append(f'{i.address:08X}: {i.mnemonic:10} {i.op_str}{tail}')
        (OUT/f'b13-{a:08x}.asm').write_text('\n'.join(lines)+'\n',encoding='utf8')
    objects=[]
    for a in [0x200000cc,0x200000ec,0x200000f8]:
        words=struct.unpack_from('<3I',init,a-0x20000000)
        objects.append(dict(address=hex(a),words=[hex(w) for w in words]))
    r=dict(image_sha256=hashlib.sha256(b).hexdigest(),initialized_objects=objects,
           ranges=[dict(start=hex(a),bytes=n,equal_stock=b[a-0x8010000:a-0x8010000+n]==STOCK[a-0x8010000:a-0x8010000+n]) for a,n in RANGES])
    (OUT/'path-inspection.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
