"""Existing stock/SC35D8/B1.3 read lifetimes and initialization call sites only."""
from pathlib import Path
import sys,json,struct,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase50-msd-readonly-geometry'))
from inspect_b13 import PUBLISHED,STOCK,md,REF,decode,ARM_OP_MEM,ARM_REG_PC
from capstone.arm import ARM_OP_IMM
RANGES=[(0x08035e28,0x130),(0x0802520c,0x40),(0x0801ec80,0x50),
 (0x08047c6c,0x1c),(0x0801df00,0x200),(0x0801e390,0x60),(0x0801f0a8,0x3c),
 (0x0801f900,0x3a0),(0x0801d3e0,0x190),(0x0802108c,0x48),
 (0x0801f3d0,0x160),(0x0802968e,0x30),(0x0803ba78,0x38),(0x0801f478,0x210),(0x0801d550,0x160),(0x08035df0,0x38)]
def main():
    b=PUBLISHED[:];boot=(REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin').read_bytes()[:0x10000]
    clean=(ROOT/'builds/phase43-hardware-test-candidate/clean-sc35d8.bin').read_bytes()
    corrected=(ROOT/'builds/phase44-preflash-redteam-closure/circuittracks-4486-nor-evidence-atomic-test.bin').read_bytes()
    images={'B1.3':b,'stock':STOCK,'SC35D8':clean,'corrected-diagnostic':corrected}
    targets={0x08035e28,0x0802520c,0x08047c6c,0x0801f0a8,0x08005d98,0x0802108c,0x0801ec80,0x0801f0f0}
    refs=[]
    for name,base,data in [('B1.3',0x08010000,b),('boot',0x08000000,boot)]:
        for off in range(0,len(data)-3,2):
            i=next(md.disasm(data[off:off+4],base+off,count=1),None)
            if i and i.mnemonic.startswith(('bl','b.w')):
                for o in i.operands:
                    if o.type==ARM_OP_IMM and (o.imm&~1) in targets:refs.append(dict(image=name,at=hex(i.address),instruction=i.mnemonic+' '+i.op_str))
    for name,base,data,ranges in [('app',0x08010000,b,RANGES),('boot',0x08000000,boot,[(0x08005d98,0x40),(0x08003a10,0x1c0)])]:
        for a,n in ranges:
            lines=[]
            for i in md.disasm(data[a-base:a-base+n],a):
                tail=''
                for o in i.operands:
                    if o.type==ARM_OP_MEM and o.mem.base==ARM_REG_PC:
                        at=((i.address+4)&~3)+o.mem.disp
                        if base<=at<base+len(data)-4:tail+=f' ; [{at:08X}]={struct.unpack_from("<I",data,at-base)[0]:08X}'
                lines.append(f'{i.address:08X}: {i.mnemonic:10} {i.op_str}{tail}')
            (OUT/f'{name}-{a:08x}.asm').write_text('\n'.join(lines)+'\n',encoding='utf8')
    r=dict(confidence='PROVEN',scope='Exact-image range comparison and direct-call candidates, not full asynchronous CFG',direct_candidates=refs,
        images=[dict(name=name,sha256=hashlib.sha256(data).hexdigest(),ranges=[dict(start=hex(a),bytes=n,equal_stock=data[a-0x08010000:a-0x08010000+n]==STOCK[a-0x08010000:a-0x08010000+n]) for a,n in RANGES]) for name,data in images.items()])
    ram_path=REF/'ctre/Firmware-Analysis/ram_dump_firmware_0x08037988.bin'
    ram=ram_path.read_bytes()
    r['boot']=dict(path=str(REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin'),bytes_hashed=len(boot),sha256=hashlib.sha256(boot).hexdigest())
    r['reference_RAM']=dict(path=str(ram_path),sha256=hashlib.sha256(ram).hexdigest(),bytes=len(ram),
        words={hex(a):hex(struct.unpack_from('<I',ram,a-0x20000000)[0]) for a in (0x2000327c,0x20006a00,0x20002b44,0x20002b48)})
    r['first_resource_descriptor']=dict(address='0x80567ec',raw=b[0x467ec:0x467f8].hex(),
        source=hex(struct.unpack_from('<I',b,0x467ec)[0]),word_count=struct.unpack_from('<H',b,0x467f0)[0],
        identical_all_images=all(data[0x467ec:0x467f8]==b[0x467ec:0x467f8] for data in images.values()))
    (OUT/'read-inspection.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');print(json.dumps(refs,indent=2))
if __name__=='__main__':main()
