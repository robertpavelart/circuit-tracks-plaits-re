"""Targeted offline ARM asset writer/path bridge; no CPU/device use."""
import argparse,json
from pathlib import Path
from ct_static import ROOT,BASE,engine,sha
from ct_stock_load_audit import verify_inputs
WINDOWS=[(0x8036b1c,0x8036cc8),(0x803c8a0,0x803c950),(0x803c9d0,0x803ca52),
 (0x80367da,0x80367f8),(0x8026610,0x802667e),(0x803b0b4,0x803b0e0),
 (0x8039a0a,0x8039b10),(0x803a100,0x803a252),(0x803a520,0x803a590),
 (0x8039124,0x80391a0),(0x8039b0e,0x8039de0),(0x80393e0,0x803945c),
 (0x8039570,0x80395bc),(0x8039940,0x8039a0a),(0x8039b12,0x8039bde),
 (0x80396d0,0x80397b0),(0x8039d7c,0x8039f00),(0x8036ccc,0x8036d82),
 (0x80397c8,0x8039860),(0x8036d82,0x8036e52),(0x8026680,0x80266d4),
 (0x803a2cc,0x803a3cc),(0x80392fc,0x80393c8),(0x803a47c,0x803a4d0),
 (0x8039e5e,0x8039f9e),(0x803cc34,0x803cc54),(0x803ccfa,0x803cd42),
 (0x8036e5c,0x8036ff6),(0x803676c,0x80367da)]
TARGETS={0x803cbf0,0x803cc54,0x803c9d0,0x8039b0e,0x8039bd0}
def collect(out):
 out=out.resolve();base=(ROOT/'builds/phase19c-packlink').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh PACKLINK child required')
 verify_inputs();b=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes();cs=engine()
 from capstone.arm import ARM_OP_IMM
 spans=[(int(x['source_offset'],16),int(x['source_offset'],16)+x['stream_size'])
  for x in json.loads((ROOT/'firmware/dsp/build-4486/manifest.json').read_text())['blocks']]
 calls=[];ins=[]
 for o in range(0,len(b)-3,2):
  if any(a<=o<c for a,c in spans):continue
  for i in cs.disasm(b[o:o+4],BASE+o,count=1):
   if i.mnemonic.startswith(('b','cb')):
    v=[x.imm for x in i.operands if x.type==ARM_OP_IMM]
    if v and v[-1] in TARGETS:calls.append(dict(PC=i.address,target=v[-1],raw=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str))
 out.mkdir(parents=True)
 with (out/'arm-windows.asm').open('x',encoding='utf8') as f:
  for lo,hi in WINDOWS:
   f.write(f'; reviewed window {lo:08X}..{hi:08X}; decode is not reachability proof\n')
   cs=engine() # independent Thumb IT state for each reviewed window
   for i in cs.disasm(b[lo-BASE:hi-BASE],lo):
    ins.append(dict(PC=i.address,raw=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str))
    f.write(f'{i.address:08X} {i.bytes.hex():10} {i.mnemonic:10} {i.op_str}\n')
 for n,v in [('instructions.json',ins),('calls.json',calls),('provenance.json',dict(offline=True,CPU_instructions_executed=0,source_sha256=sha(Path(__file__).read_bytes()),BIN_sha256=sha(b)))]:
  with (out/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 verify_inputs()
 hashes={p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()}
 with (out/'hashes.json').open('x',encoding='utf8') as f:json.dump(hashes,f,indent=2,sort_keys=True);f.write('\n')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path);collect(p.parse_args().output_dir)
