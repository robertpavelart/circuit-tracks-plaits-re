"""Full exact-image candidate census plus corroborating native ranges. Read-only inputs."""
from pathlib import Path
import sys,struct,json,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import inspect_storage as src
from capstone.arm import ARM_OP_IMM,ARM_OP_MEM,ARM_REG_PC
CODE={0x08019a92,0x080197a0,0x0801addc,0x0801ae1c,0x0801ae3a,0x0801ae90,0x0801aecc,
      0x0801f0a8,0x080248b4,0x08038c54,0x0805dbcc,0x0805767c,0x0801d4b0}
RAM={0x20044d70,0x20044d74,0x20044d78,0x20044d7c,0x20002b44,0x20000aa0,0x20000ab0,
     0x20000a98,0x20005e5c,0x20006968}
def main():
    direct=[];literal=[];movpairs=[];pointers=[];data=src.app
    for off in range(0,len(data)-3,2):
        i=next(src.md.disasm(data[off:off+4],0x08010000+off,count=1),None)
        if not i:continue
        if i.mnemonic.startswith(('bl','b.w')):
            for o in i.operands:
                if o.type==ARM_OP_IMM and (o.imm&~1) in CODE:direct.append(dict(at=hex(i.address),instruction=i.mnemonic+' '+i.op_str))
        for o in i.operands:
            if o.type==ARM_OP_MEM and o.mem.base==ARM_REG_PC:
                a=((i.address+4)&~3)+o.mem.disp
                if 0x08010000<=a<=0x08010000+len(data)-4:
                    v=struct.unpack_from('<I',data,a-0x08010000)[0]
                    if v in RAM:literal.append(dict(at=hex(i.address),value=hex(v)))
        if i.mnemonic=='movw' and len(i.operands)==2 and i.operands[1].type==ARM_OP_IMM:
            j=next(src.md.disasm(data[off+i.size:off+i.size+4],i.address+i.size,count=1),None)
            if j and j.mnemonic=='movt' and j.operands[0].reg==i.operands[0].reg:
                v=i.operands[1].imm|(j.operands[1].imm<<16)
                if v in RAM:movpairs.append(dict(at=hex(i.address),value=hex(v),register=i.reg_name(i.operands[0].reg)))
    ram_path=src.REF/'ctre/Firmware-Analysis/ram_dump_firmware_0x08037988.bin';ram=ram_path.read_bytes()
    for name,base,b in [('flash',0x08010000,data),('initialized_RAM',0x20000000,src.init),('captured_RAM',0x20000000,ram)]:
        for off in range(0,len(b)-3):
            v=struct.unpack_from('<I',b,off)[0]
            if v in RAM or (v&~1) in CODE:pointers.append(dict(image=name,at=hex(base+off),value=hex(v)))
    ranges=[(0x0806b6cc,0x184),(0x0806b850,0x220),(0x0806bc30,0x20),(0x08059970,0x50),
       (0x0801cf50,0x50),(0x0801da00,0xc0),(0x0801d7d8,0x30),(0x0801ae1c,0x28),
       (0x08019a92,0x48),(0x080248b4,0x60),(0x08038c54,0x24),(0x0805767c,0x40),
       (0x080573e0,0x38),(0x0805dbcc,0x6c)]
    for a,n in ranges:(OUT/f'app-{a:08x}.asm').write_text(src.listing('app',a,n),encoding='utf8')
    names=[]
    for name in (b'Main\0',b'UI\0',b'Storage\0',b'IDLE\0',b'USB\0'):
        start=0
        while True:
            off=ram.find(name,start)
            if off<0:break
            names.append(dict(name=name[:-1].decode(),address=hex(0x20000000+off),possible_TCB_if_name_offset34=hex(0x20000000+off-0x34)))
            start=off+1
    r=dict(confidence='PROVEN',scope='Entire exact corrected image and initialized/captured RAM candidate scan; halfword/data decoding and stale captured pointers are NOT a complete indirect alias/writer proof',
        image_sha256=hashlib.sha256(data).hexdigest(),image_bytes=len(data),initialized_bytes=len(src.init),
        direct_candidates=direct,literal_candidates=literal,materialized_RAM_candidates=movpairs,
        pointer_candidates=pointers,task_name_candidates=names,
        RAM_image_sha256=hashlib.sha256(ram).hexdigest(),all_computed_references_closed=False)
    (OUT/'census.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:len(r[k]) for k in ('direct_candidates','literal_candidates','materialized_RAM_candidates','pointer_candidates','task_name_candidates')}))
if __name__=='__main__':main()
