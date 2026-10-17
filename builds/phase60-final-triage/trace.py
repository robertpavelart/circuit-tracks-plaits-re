"""Focused read-only byte inspection of the three requested categories."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import inspect_storage as s
def main():
    for arg in sys.argv[1:]:
        a,n=arg.split(':');a=int(a,16);n=int(n,16)
        t=s.listing('app',a,n);(OUT/f'app-{a:08x}.asm').write_text(t);print(t)
if __name__=='__main__':main()
