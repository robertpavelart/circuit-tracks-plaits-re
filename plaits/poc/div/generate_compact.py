"""Compact native helper only: qualified parallel register moves, integer count."""
import argparse
from pathlib import Path
import generate_div

def helper():
 return '''ratio:
clr b y0,a
tst a x0,a
jeq @ratio_zero
ratio_integer:
cmp y0,a
jlt @ratio_fraction
sub y0,a
add #$01,b
jmp @ratio_integer
ratio_fraction:
asl #$15,b,b
andi #$fe,ccr
rep #$15
div y0,a
move a0,a
rol a b1,x1
add x1,a
rts
ratio_zero:
clr a
rts'''.splitlines()

def generate(out):
 previous=generate_div.helper
 try:
  generate_div.helper=helper
  generate_div.generate(out)
 finally:generate_div.helper=previous

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',required=True);generate(a.parse_args().output_dir)
