"""Exact candidate static inspection; does not import devices or builders."""
import sys,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'final-two-check-closure'))
import byte_audit as A
from capstone.arm import ARM_OP_IMM
O=Path(__file__).resolve().parent
def listing(a,n):
    text=[]
    for i in A.md.disasm(A.read(a,n),a):
        suffix=''
        for op in i.operands:
            if op.type==3 and op.mem.base==11:
                at=((i.address+4)&~3)+op.mem.disp
                try:suffix+=f' ; [{at:08X}]={A.word(at):08X}'
                except ValueError:pass
        text.append(f'{i.address:08X}: {i.mnemonic:10} {i.op_str}{suffix}')
    out='\n'.join(text)+'\n'
    (O/f'{a:08x}.asm').write_text(out)
    return out
def xrefs(target):
    rows=[]
    for at in range(0x8010000,0x8010000+len(A.image)-4,2):
        i=next(A.md.disasm(A.read(at,4),at,count=1),None)
        if i and i.mnemonic in ('bl','blx','b','b.w') and i.operands[0].type==ARM_OP_IMM and i.operands[0].imm==(target&~1):rows.append(dict(at=hex(at),instruction=i.mnemonic))
    needle=(target|1).to_bytes(4,'little')
    pointers=[hex(0x8010000+k) for k in range(len(A.image)-3) if A.image[k:k+4]==needle]
    return dict(target=hex(target),direct_candidates=rows,pointer_candidates=pointers)
if __name__=='__main__':
    for arg in sys.argv[1:]:
        if ':' in arg:
            a,n=arg.split(':');print(listing(int(a,16),int(n,16)))
        else:
            row=xrefs(int(arg,16))
            (O/f'xrefs-{int(arg,16):08x}.json').write_text(json.dumps(row,indent=2)+'\n')
            print(json.dumps(row,indent=2))
