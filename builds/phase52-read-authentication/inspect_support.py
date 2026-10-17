"""Exact existing B1.3 USB transmit, DMA and native semaphore release listings."""
from native_sequence import OUT,ROOT,fresh
import sys,struct,json
sys.path.insert(0,str(ROOT/'builds/phase50-msd-readonly-geometry'))
from inspect_b13 import PUBLISHED,md,ARM_OP_MEM,ARM_REG_PC
def main():
    for a,n in [(0x08024754,0x1c),(0x0801c100,0xb0),(0x0801ba12,0x2a),(0x080389c6,0xae)]:
        lines=[]
        for i in md.disasm(PUBLISHED[a-0x08010000:a-0x08010000+n],a):
            tail=''
            for o in i.operands:
                if o.type==ARM_OP_MEM and o.mem.base==ARM_REG_PC:
                    at=((i.address+4)&~3)+o.mem.disp
                    if 0x08010000<=at<0x08010000+len(PUBLISHED)-4:tail+=f' ; [{at:08X}]={struct.unpack("<I",PUBLISHED[at-0x08010000:at-0x08010000+4])[0]:08X}'
            lines.append(f'{i.address:08X}: {i.mnemonic:10} {i.op_str}{tail}')
        (OUT/f'b13-{a:08x}.asm').write_text('\n'.join(lines)+'\n',encoding='utf8')
    cases=[]
    for enabled in (0,1):
        e=fresh();e.w32(0x20023000,0x20023040);e.w32(0x20023040,0x400264b8)
        e.w32(0x400264b8,enabled);e.w32(0x400264bc,123);e.w32(0x400264c4,0x20025000)
        result=e.call(0x0801c072,0x20023000,0x40024000,4096,0)
        row=dict(initial_EN=enabled,result=result,NDTR=e.r32(0x400264bc),M0AR=hex(e.r32(0x400264c4)))
        assert result==0
        assert (row['NDTR'],row['M0AR'])==((123,'0x20025000') if enabled else (4096,'0x40024000'))
        cases.append(row)
    (OUT/'DMA-setup-cases.json').write_text(json.dumps(dict(confidence='PROVEN',scope='Native DMA setup helper with modeled register memory; no actual DMA',cases=cases),indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
