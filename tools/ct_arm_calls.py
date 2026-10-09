#!/usr/bin/env python3
"""Offline multi-target direct-call scan; halfword hits require code review."""
import argparse,json,struct
from pathlib import Path
from ct_static import ROOT,BASE,engine,save
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--targets',required=True,nargs='+',type=lambda x:int(x,0))
    p.add_argument('--output',required=True)
    a=p.parse_args()
    data=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    targets=set(a.targets)
    cs=engine()
    from capstone.arm import ARM_OP_IMM
    hits=[]
    for off in range(0,len(data)-3,2):
        for i in cs.disasm(data[off:off+4],BASE+off,count=1):
            if i.mnemonic.startswith(('bl','b')):
                for op in i.operands:
                    if op.type==ARM_OP_IMM and op.imm in targets:
                        hits.append(dict(site=f'0x{i.address:08X}',target=f'0x{op.imm:08X}',instruction=i.mnemonic+' '+i.op_str))
    save(a.output,json.dumps(hits,indent=2)+'\n')
if __name__=='__main__': main()
