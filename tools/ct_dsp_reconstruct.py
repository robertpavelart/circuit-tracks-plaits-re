#!/usr/bin/env python3
"""Export only reviewed P-to-X startup table copies; no firmware execution.

This is a partial initialized-memory reconstruction, not a runtime RAM dump.
Rules below are pinned to explicit MOVEM/store/DO loops in this build.
"""
import argparse,json
from pathlib import Path
from ct_static import ROOT,sha,save
from ct_dsp_boot import parse

COPIES=[
    (0x2620,0x262C,0x1D53,16,'X'),
    (0x2629,0x263C,0x007D,8,'X'),
    (0x271D,0x268C,0x1EDD,0x8B,'X'),
    (0x29F2,0x29F6,0x09DB,0x37,'X'),
]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--streams',default=str(ROOT/'firmware/dsp/build-4486'))
    p.add_argument('--output-dir',required=True)
    a=p.parse_args()
    source=Path(a.streams)
    out=Path(a.output_dir).resolve()
    if out.exists(): raise SystemExit('Choose a fresh output directory')
    if out==(ROOT/'original').resolve() or (ROOT/'original').resolve() in out.parents:
        raise SystemExit('Protected destination')
    raw=(source/'selection0-channel0.boot24.bin').read_bytes()
    description=parse(raw)
    if sha(raw)!='449c347018a7f318f6eede928446a341f2d3d7d41eb7f2e18d6c71a90d42efb4':
        raise SystemExit('Only the verified payload supported')
    payload=raw[6:]
    manifest=dict(status='partial static reconstruction',p_load=description,table_copies=[],
                  zero_init=[dict(space='X',start='0x000000',words=0x6000,evidence='P:0x2786'),
                             dict(space='Y',start='0x000000',words=0x6000,evidence='P:0x2786'),
                             dict(space='X',start='0x030000',words=0x8000,evidence='P:0x278F')],
                  caveat='Zero ranges are subsequently modified; only explicit reviewed table copies are exported')
    files=[('P-000000-002A5E.payload24.bin',payload)]
    for site,src,dst,count,space in COPIES:
        block=payload[src*3:(src+count)*3]
        if len(block)!=count*3: raise ValueError('Copy outside uploaded P space')
        name=f'{space}-{dst:06X}-{dst+count:06X}.table24.bin'
        files.append((name,block))
        manifest['table_copies'].append(dict(instruction=f'P:0x{site:X}',source=f'P:0x{src:X}',
                                            destination=f'{space}:0x{dst:X}',words=count,
                                            end_exclusive=f'{space}:0x{dst+count:X}',file=name,sha256=sha(block)))
    # Resolve the 55-entry table at X:0x9DB copied from P:0x29F6.
    words=[int.from_bytes(payload[i:i+3],'big') for i in range(0,len(payload),3)]
    manifest['indirect_table']=[dict(index=i,target=f'P:0x{words[0x29f6+i]:X}') for i in range(0x37)]
    out.mkdir(parents=True,exist_ok=False)
    for name,content in files: save(out/name,content)
    save(out/'manifest.json',json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__': main()
