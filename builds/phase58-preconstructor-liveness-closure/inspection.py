"""Authenticated listings/caller inventory; no image modifications."""
from pathlib import Path
import sys,json,hashlib,struct
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import inspect_storage as src
from capstone.arm import ARM_OP_IMM,ARM_INS_BL,ARM_INS_BLX,ARM_INS_B
def main():
    ranges=[(0x0805b958,0x38),(0x0801eaf8,0x34),(0x0801d3c8,0x60),(0x0801ddd4,0xb0),
        (0x08022acc,0x28),(0x0801b250,0x30),(0x0801b1a8,0x20),(0x0801d7d0,0x30),
        (0x0805c00c,0x10),(0x0805b590,0x20),(0x0801cfa4,0x1c),(0x08037380,0x24),
        (0x0801e480,0x2c),(0x08024274,0x2c),(0x08037aac,0x10),(0x080584c4,0x22)]
    for a,n in ranges:(OUT/f'app-{a:08x}.asm').write_text(src.listing('app',a,n))
    (OUT/'boot-08003d06.asm').write_text(src.listing('boot',0x08003d06,0x40))
    direct=[]
    for off in range(0,len(src.app)-3,2):
        i=next(src.md.disasm(src.app[off:off+4],0x08010000+off,count=1),None)
        if i and i.id in (ARM_INS_BL,ARM_INS_BLX,ARM_INS_B):
            if i.operands[0].type==ARM_OP_IMM and i.operands[0].imm&~1==0x0805b958:direct.append(hex(i.address))
    r=dict(confidence='PROVEN',image_sha256=hashlib.sha256(src.app).hexdigest(),boot64k_sha256=hashlib.sha256(src.boot).hexdigest(),
        preconstructor=dict(entry='0x0805b958',iterator='0x0805b978',normal_caller='0x0805b5a6 BLX r1',
            scatter_relative_record='0x0805b7d4',relative_word=hex(struct.unpack_from('<I',src.app,0x4b7d4)[0]),
            argument_and_return='0x0805b7d8',direct_call_candidates=direct,constructor_table=['0x0805b5b8','0x0805b5e0'],
            classification='SAFE',classification_scope='Authenticated normal post-scatter constructor invocation with successful admitted allocations, not full boot/IRQ or safe-hook qualification'),
        first_epoch_final='UNKNOWN',range_hashes=[dict(start=hex(a),bytes=n,sha256=hashlib.sha256(src.app[a-0x08010000:a-0x08010000+n]).hexdigest()) for a,n in ranges])
    (OUT/'inspection.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['preconstructor'],indent=2))
if __name__=='__main__':main()
