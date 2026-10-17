"""Pinned-byte IRQ handler and immediate source listing, evidence only."""
from pathlib import Path
import sys,json,struct
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import inspect_storage as source
def main():
    ranges={0x080573d8:0x280,0x0805c30c:0x98,0x0805c398:0x24,0x080227f0:0x100,0x0801e174:0x1d0,0x0801ee34:0x76,0x0801d914:0x3c}
    for arg in sys.argv[1:]:
        if arg.startswith('--'):continue
        a,n=arg.split(':');ranges[int(a,16)]=int(n,16)
    for a,n in ranges.items():(OUT/f'app-{a:08x}.asm').write_text(source.listing('app',a,n))
    if '--xrefs' in sys.argv:
        (OUT/'usb-literal-xrefs.json').write_text(json.dumps(source.xrefs({0x40040000,0x50000000,0x40023834,0x080382ea}),indent=2)+'\n')
    if '--usb-calls' in sys.argv:
        (OUT/'usb-init-xrefs.json').write_text(json.dumps(source.xrefs({0x080244d4,0x080245c6,0x080381a8,0x08036442,0x08036460}),indent=2)+'\n')
    print('Saved',len(ranges),'listings')
if __name__=='__main__':main()
