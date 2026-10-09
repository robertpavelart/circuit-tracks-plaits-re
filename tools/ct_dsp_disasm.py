#!/usr/bin/env python3
"""Offline decode adapter; uses a real upstream decoder, not Capstone.

Linear output includes embedded data; reachability must be reviewed separately.
"""
import argparse
from pathlib import Path
import subprocess
from ct_static import ROOT,save

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input')
    p.add_argument('--origin',type=lambda x:int(x,0),default=0)
    p.add_argument('--start',type=lambda x:int(x,0),default=0)
    p.add_argument('--end',type=lambda x:int(x,0))
    p.add_argument('--decoder',default=str(ROOT/'builds/dsp-tools/dsp_disasm.exe'))
    p.add_argument('--output',required=True)
    a=p.parse_args()
    if Path(a.output).exists():
        raise SystemExit('Choose a fresh output file')
    size=Path(a.input).stat().st_size
    end=a.end if a.end is not None else a.origin+size//3
    result=subprocess.run([a.decoder,a.input,f'{a.origin:X}',f'{a.start:X}',f'{end:X}'],
                          capture_output=True,text=True,check=True)
    save(a.output,result.stdout)

if __name__=='__main__':
    main()
