"""Offline targeted asset source/predicate disassembly; no CPU or device use."""
import argparse,json,struct
from pathlib import Path
from ct_static import ROOT,BASE,engine,sha
from ct_stock_load_audit import verify_inputs

WINDOWS=[(0x8051ba0,0x8051c50),(0x803cb70,0x803cd40),
 (0x80499e0,0x8049c54),(0x805bfcc,0x805c00c),(0x8036740,0x80367d8),
 (0x8030c60,0x8030d10),(0x8030da0,0x8030e60),(0x803ca52,0x803cb08),
 (0x8052b8a,0x8052c10),(0x8049c88,0x8049d80),
 (0x8022a20,0x8022e80),(0x80253d0,0x8025440),
 (0x8049cd0,0x8049d20),(0x8036a7e,0x8036b1c),(0x80367da,0x80368d6)]
TARGETS={0x803cc44,0x805bfcc,0x803cbd6,0x8051ba0}
def collect(out):
 out=out.resolve();base=(ROOT/'builds/phase19c-assetbound').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh ASSETBOUND child required')
 verify_inputs();b=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes();cs=engine()
 from capstone.arm import ARM_OP_IMM
 data=json.loads((ROOT/'firmware/dsp/build-4486/manifest.json').read_text())['blocks']
 spans=[(int(x['source_offset'],16),int(x['source_offset'],16)+x['stream_size']) for x in data]
 calls=[];ins=[]
 for o in range(0,len(b)-3,2):
  if any(a<=o<c for a,c in spans):continue
  for i in cs.disasm(b[o:o+4],BASE+o,count=1):
   if i.mnemonic.startswith(('b','cb')):
    imm=[x.imm for x in i.operands if x.type==ARM_OP_IMM]
    if imm and imm[-1] in TARGETS:calls.append(dict(PC=i.address,target=imm[-1],raw=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str))
 out.mkdir(parents=True)
 with (out/'arm-windows.asm').open('x',encoding='utf8') as f:
  for lo,hi in WINDOWS:
   f.write(f'; window {lo:08X}..{hi:08X}; review code/data boundaries\n')
   for i in cs.disasm(b[lo-BASE:hi-BASE],lo):
    x=dict(PC=i.address,raw=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str);ins.append(x)
    f.write(f'{i.address:08X} {i.bytes.hex():10} {i.mnemonic:10} {i.op_str}\n')
 def emit(n,v):
  with (out/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 emit('instructions.json',ins);emit('calls.json',calls)
 emit('literals.json',{hex(a):hex(struct.unpack_from('<I',b,a-BASE)[0]) for a in range(0x8049c18,0x8049c34,4)})
 emit('pointer-references.json',{hex(t):[hex(BASE+o) for o in range(len(b)-3) if b[o:o+4]==struct.pack('<I',t|1)] for t in TARGETS})
 emit('provenance.json',dict(offline=True,CPU_instructions_executed=0,source_sha256=sha(Path(__file__).read_bytes()),BIN_sha256=sha(b)))
 verify_inputs()
 emit('hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path);collect(p.parse_args().output_dir)
