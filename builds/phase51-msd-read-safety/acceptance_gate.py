"""Offline gate: structural BPB validity alone never authenticates physical completion."""
from pathlib import Path
import sys,json,argparse
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'phase50-msd-readonly-geometry'))
from geometry_from_sector import decode
def assess(sectors):
    try:candidate=decode(sectors)
    except ValueError as e:return dict(evidence='INVALID',reason=str(e))
    return dict(evidence='UNQUALIFIED',physical_read_completion='UNKNOWN',
        reason='BPB structure passes; existing MSD success/length does not attest lower NOR status or DMA completeness',
        candidate_geometry=candidate)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sector',action='append',required=True,metavar='USB_LBA=LOCAL_FILE')
    args=p.parse_args();sectors={}
    try:
        for arg in args.sector:
            left,right=arg.split('=',1);lba=int(left,0)
            if lba in sectors:raise ValueError('duplicate sector')
            sectors[lba]=Path(right).read_bytes()
        result=assess(sectors)
    except (ValueError,OSError) as e:result=dict(evidence='INVALID',reason=str(e))
    print(json.dumps(result,indent=2));raise SystemExit(2 if result['evidence']=='INVALID' else 3)
if __name__=='__main__':main()
