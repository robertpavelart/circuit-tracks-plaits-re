"""Only replace the fallback's ratio-helper suffix. No algorithm/oracle edit."""
import sys,json,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from generate import Program

def helper():
 # n>=0, 0<d<=0x7fffff, n<=0x7fffff, n<4*d.
 # Zero denominator gets explicit safe zero, outside the valid ratio contract.
 # Fractional remainder < divisor:21 DIVs form20 stored bits + last bit in C.
 # Move A0 to A1, then ROL inserts C into A1: floor(remainder*2^21/divisor).
 return '''ratio:
move y0,a
tst a
jeq @ratio_zero
move x0,a
clr b
ratio_integer:
cmp y0,a
jlt @ratio_fraction
sub y0,a
move #>$200000,x1
add x1,b
jmp @ratio_integer
ratio_fraction:
andi #$fe,ccr
rep #$15
div y0,a
move a0,a
rol a
move b1,x1
add x1,a
rts
ratio_zero:
clr a
rts'''.splitlines()

def build():
 p=Program();old=p.build();start=old.index('ratio:')
 lines=old[:start]+helper()+['done:']
 assert p.scratch[-1]=='ratio_integer_q'
 # No algorithm or layout change in this phase. Former helper slot is unused.
 return p,lines

def generate(out):
 out=Path(out).resolve();base=Path(__file__).resolve().parents[3]/'builds/phase20a-div'
 if out.exists() or not out.is_relative_to(base) or out==base:raise ValueError('Fresh DIV child required')
 p,lines=build();out.mkdir(parents=True)
 (out/'variablesaw.asm').write_text('\n'.join(lines)+'\n')
 (out/'layout.json').write_text(json.dumps(dict(origin=0x200,state_words=7,scratch_words=len(p.scratch),
  state_X=[0x20,0x27],control_X=[0x40,0x43],scratch_X=[0x80,0x80+len(p.scratch)],output_Y=[0,32],
  table_words=0,variables=p.names,unused_scratch=['ratio_integer_q'],render_samples=32),indent=2)+'\n')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',required=True);generate(a.parse_args().output_dir)
