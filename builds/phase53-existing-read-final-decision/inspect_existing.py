"""Exact B1.3 buffer constants/registered SCSI producers; no firmware output."""
from pathlib import Path
import sys,json,struct,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase50-msd-readonly-geometry'))
from inspect_b13 import PUBLISHED,STOCK,decode,md,ARM_OP_MEM,ARM_REG_PC
from capstone.arm import ARM_OP_IMM
def main():
    b=PUBLISHED[:];init,_=decode(b)
    def inrange(v):return 0x40024000<=v<0x40025000
    literals=[];ram=[];loads=[];immediates=[]
    for off in range(len(b)-3):
        v=struct.unpack_from('<I',b,off)[0]
        if inrange(v):literals.append(dict(at=hex(0x08010000+off),value=hex(v)))
    for off in range(len(init)-3):
        v=struct.unpack_from('<I',init,off)[0]
        if inrange(v):ram.append(dict(at=hex(0x20000000+off),value=hex(v)))
    # Halfword candidates are checked against saved function listings, not
    # automatically labeled reachable instructions.
    for off in range(0,len(b)-3,2):
        i=next(md.disasm(b[off:off+4],0x08010000+off,count=1),None)
        if not i:continue
        for o in i.operands:
            if o.type==ARM_OP_MEM and o.mem.base==ARM_REG_PC:
                at=((i.address+4)&~3)+o.mem.disp
                if 0x08010000<=at<=0x08010000+len(b)-4:
                    v=struct.unpack_from('<I',b,at-0x08010000)[0]
                    if inrange(v):loads.append(dict(at=hex(i.address),instruction=i.mnemonic+' '+i.op_str,literal=hex(at),value=hex(v)))
            if o.type==ARM_OP_IMM and inrange(o.imm):immediates.append(dict(at=hex(i.address),instruction=i.mnemonic+' '+i.op_str))
    ranges=[(0x0803b27c,0x52c),(0x08026d64,0x174),(0x08057e30,0x1b0),
            (0x0803b7f8,0x60),(0x0804862a,0x18c)]
    for a,n in ranges:
        lines=[]
        for i in md.disasm(b[a-0x08010000:a-0x08010000+n],a):
            tail=''
            for o in i.operands:
                if o.type==ARM_OP_MEM and o.mem.base==ARM_REG_PC:
                    at=((i.address+4)&~3)+o.mem.disp
                    if 0x08010000<=at<0x08010000+len(b)-4:tail+=f' ; [{at:08X}]={struct.unpack_from("<I",b,at-0x08010000)[0]:08X}'
            lines.append(f'{i.address:08X}: {i.mnemonic:10} {i.op_str}{tail}')
        (OUT/f'b13-{a:08x}.asm').write_text('\n'.join(lines)+'\n',encoding='utf8')
    constants={hex(a):b[a-0x08010000:a-0x08010000+n].hex() for a,n in [(0x0805b6b8,36),(0x0805c1fc,7),(0x0805c204,8),(0x0805c20c,8)]}
    result=dict(image_sha256=hashlib.sha256(b).hexdigest(),literal_candidates=literals,
        initialized_pointer_candidates=ram,PC_relative_load_candidates=loads,immediate_candidates=immediates,
        constants=constants,scope='Whole-byte literal and halfword instruction candidate census plus registered-path inspection; not an arbitrary computed-alias theorem',
        ranges=[dict(start=hex(a),bytes=n,equal_stock=b[a-0x08010000:a-0x08010000+n]==STOCK[a-0x08010000:a-0x08010000+n]) for a,n in ranges])
    (OUT/'existing-paths.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
