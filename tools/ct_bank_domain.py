#!/usr/bin/env python3
"""Offline ARM bank-domain evidence collector; no device or firmware execution.

Direct-call and pointer scans are candidates, including possible data decodes.
Use reviewed control flow to establish actual callers. Fresh outputs only.
"""
import argparse, json, struct
from pathlib import Path
from ct_static import ROOT, BASE, BIN_HASH, sha, save, engine
from ct_data_decode import decode

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',required=True)
    p.add_argument('--targets',nargs='*',type=lambda x:int(x,0),default=[])
    p.add_argument('--windows',nargs='*',default=[])
    a=p.parse_args(); out=Path(a.output_dir).resolve()
    if out.exists():raise SystemExit('Choose a fresh output directory')
    if out==ROOT/'original' or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    assert sha(arm)==BIN_HASH
    windows=[]
    for window in a.windows:
        lo,hi=(int(x,0) for x in window.split(':'))
        if not BASE<=lo<hi<=BASE+len(arm):raise SystemExit('Window outside verified image')
        windows.append((lo,hi))
    ram,init=decode(arm)
    assert ram==(ROOT/'builds/initialized-data-v2.bin').read_bytes()
    cs=engine(); targets=set(a.targets);calls=[];references=[]
    from capstone.arm import ARM_OP_IMM
    for off in range(0,len(arm)-3,2):
        for i in cs.disasm(arm[off:off+4],BASE+off,count=1):
            if i.mnemonic.startswith(('bl','b')):
                for op in i.operands:
                    if op.type==ARM_OP_IMM and op.imm in targets:
                        calls.append({'site':f'0x{i.address:08X}','target':f'0x{op.imm:08X}',
                          'bytes':i.bytes.hex(),'instruction':i.mnemonic+' '+i.op_str,
                          'status':'halfword candidate; review code reachability'})
    for target in sorted(targets):
        for value in sorted({target,target|1}):
            needle=struct.pack('<I',value)
            for data,base,kind in ((arm,BASE,'flash'),(ram,0x20000000,'decoded ARM init data')):
                pos=0
                while True:
                    hit=data.find(needle,pos)
                    if hit<0:break
                    references.append({'target':f'0x{target:08X}','value':f'0x{value:08X}',
                     'address':f'0x{base+hit:08X}','domain':kind,
                     'status':'exact bytes; not an automatic pointer/reachability proof'})
                    pos=hit+1
    save(out/'calls.json',json.dumps(calls,indent=2)+'\n')
    save(out/'references.json',json.dumps(references,indent=2)+'\n')
    for lo,hi in windows:
        lines=[]
        for i in cs.disasm(arm[lo-BASE:hi-BASE],lo):
            lines.append(f'{i.address:08X}  {i.bytes.hex():10} {i.mnemonic:10} {i.op_str}')
        save(out/f'{lo:08X}-{hi:08X}.asm','\n'.join(lines)+'\n')
    save(out/'provenance.json',json.dumps({'BIN_SHA256':sha(arm),'script_SHA256':sha(Path(__file__).read_bytes()),
     'init_data':init,'targets':[f'0x{x:08X}' for x in sorted(targets)],'windows':a.windows,
     'mode':'static only; no ISA execution'},indent=2)+'\n')

if __name__=='__main__':main()
