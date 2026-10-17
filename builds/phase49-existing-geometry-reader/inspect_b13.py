"""Offline exact published B1.3 inspection; never opens transports or emits images."""
from pathlib import Path
import sys, json, hashlib, struct
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase42-exact-rdiag-integration'))
from environment import PUBLISHED, REF, md
from capstone.arm import ARM_OP_MEM, ARM_REG_PC

def main():
    image=PUBLISHED[:]
    assert hashlib.sha256(image).hexdigest()=='2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41'
    ranges=[(0x0801eb30,0x2a8),(0x0802484c,0x4e0),(0x080251a0,0x1c0),
            (0x08039570,0x80),(0x08039f00,0x400),(0x0803a300,0x360),
            (0x0802503c,0x144),(0x08038ba0,0xc0),(0x0802540c,0x1dc),
            (0x080257a0,0x27a),(0x0803a614,0x60),(0x08057e30,0x144)]
    for a,n in ranges:
        lines=[]
        for i in md.disasm(image[a-0x08010000:a-0x08010000+n],a):
            suffix=''
            for o in i.operands:
                if o.type==ARM_OP_MEM and o.mem.base==ARM_REG_PC:
                    at=((i.address+4)&~3)+o.mem.disp
                    if 0x08010000<=at<=0x08010000+len(image)-4:
                        suffix+=f' ; [{at:08X}]={struct.unpack_from("<I",image,at-0x08010000)[0]:08X}'
            lines.append(f'{i.address:08X}: {i.mnemonic:10} {i.op_str}{suffix}')
        (OUT/f'b13-{a:08x}.asm').write_text('\n'.join(lines)+'\n',encoding='utf8')
    result=dict(image_sha256=hashlib.sha256(image).hexdigest(),image_bytes=len(image),
                dispatcher_bytes=image[0xeb30:0xeb38].hex(),
                literal_rdiag_signature_offsets=[hex(0x08010000+i) for i in range(len(image)) if image.startswith(bytes.fromhex('f07d4354'),i)],
                caveat='Signature search is corroboration, not proof of absence of computed or alternate interfaces.',
                ranges=[dict(start=hex(a),bytes=n) for a,n in ranges])
    (OUT/'b13-inspection.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
