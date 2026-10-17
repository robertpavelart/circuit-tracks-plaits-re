"""Read existing B1.3 bytes only; emit text/JSON, no firmware or transport I/O."""
from pathlib import Path
import sys,json,hashlib,struct
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase42-exact-rdiag-integration'))
from environment import PUBLISHED,STOCK,md,REF
sys.path.insert(0,str(ROOT/'tools'))
from ct_data_decode import decode
from capstone.arm import ARM_OP_MEM,ARM_REG_PC
RANGES=[(0x08023f68,0x290),(0x08026d64,0x44),(0x0803b27c,0x510),
 (0x08057e30,0x1b0),(0x08057fe0,0x80),(0x08038c10,0xa4),
 (0x08036374,0x110),(0x08036460,0x128),(0x08058eb0,0xf0),
 (0x080248b4,0x100),(0x08029ddc,0x84),(0x08038b70,0x30),
 (0x0801f650,0x50),(0x08024130,0x38),(0x08047016,0x84),
 (0x0804709a,0x160),(0x0803542c,0x100),(0x08047cf2,0x100),
 (0x08037ef0,0x70),(0x08026d06,0x2e)]
def main():
    image=PUBLISHED[:];init,_=decode(image)
    assert hashlib.sha256(image).hexdigest()=='2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41'
    for a,n in RANGES:
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
        initialized_table=init[0x3788:0x37b0].hex(),table_pointer=hex(struct.unpack_from('<I',init,0x37ac)[0]),
        initial_mode=init[0x37bc],initial_window_pointer=hex(struct.unpack_from('<I',init,0x37c0)[0]),
        windows=[dict(record=hex(a),base=hex(struct.unpack_from('<I',image,a-0x08010000)[0]),
                      end_inclusive=hex(struct.unpack_from('<I',image,a-0x08010000+4)[0])) for a in (0x08038c3c,0x08038c44,0x08038c4c)],
        inquiry_bytes=image[0x4b6b8:0x4b6b8+36].hex(),
        read_filter_marker=image[0x47fd0:0x47fe0].hex(),
        ranges=[dict(start=hex(a),bytes=n,equal_stock=image[a-0x08010000:a-0x08010000+n]==STOCK[a-0x08010000:a-0x08010000+n]) for a,n in RANGES])
    (OUT/'b13-inspection.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
