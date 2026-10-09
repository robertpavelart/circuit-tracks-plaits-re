"""Offline targeted backend disassembly; source bytes unchanged, fresh outputs."""
import argparse,json,struct
from pathlib import Path
from ct_static import ROOT,BASE,engine,sha
from ct_stock_load_audit import verify_inputs
WINDOWS=[(0x802658a,0x8026764),(0x803b04c,0x803b218),
 (0x8036650,0x803676c),(0x8036e00,0x8036e60),(0x80370e0,0x80372a0),
 (0x801f060,0x801f1d0),(0x803b1f0,0x803b27c),
 (0x80263f8,0x802658a),(0x8025c98,0x8025ebc),(0x8026064,0x80261e8),
 (0x8025ebc,0x8025f80),(0x8025e08,0x8025e4c),(0x805c274,0x805c290),
 (0x8019cc6,0x8019e50),(0x803adf0,0x803ae80),(0x803afc4,0x803b04c),
 (0x8048e84,0x8048f70),(0x801a12c,0x801a27c),
 (0x801a9f6,0x801aa34),(0x805c16c,0x805c1c0),(0x805c24a,0x805c274),
 (0x803ae80,0x803af00),(0x8025e4c,0x8025e58),(0x80297d6,0x802983c),
 (0x801eb1e,0x801eb88),(0x801aade,0x801ab00),(0x8026494,0x802658a),
 (0x801f1c0,0x801f22c),(0x8019ae4,0x8019cc6)]
TARGETS={0x8026610,0x803b084,0x803b08c,0x80263f8,0x8026064,0x801f0f0}
LITERALS={0x20006914,0x2000691c,0x20006910,0x2000690c,0x20006794}
def collect(out):
 out=out.resolve();base=(ROOT/'builds/phase19c-backendbound').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh BACKENDBOUND child required')
 verify_inputs();b=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes();cs=engine()
 from capstone.arm import ARM_OP_IMM,ARM_OP_MEM,ARM_REG_PC
 data=json.loads((ROOT/'firmware/dsp/build-4486/manifest.json').read_text())['blocks']
 spans=[(int(x['source_offset'],16),int(x['source_offset'],16)+x['stream_size']) for x in data]
 calls=[];refs=[];ins=[]
 for o in range(0,len(b)-3,2):
  if any(a<=o<c for a,c in spans):continue
  for i in cs.disasm(b[o:o+4],BASE+o,count=1):
   if i.mnemonic.startswith(('b','cb')):
    imm=[x.imm for x in i.operands if x.type==ARM_OP_IMM]
    if imm and imm[-1] in TARGETS:calls.append(dict(PC=i.address,target=imm[-1],raw=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str))
   if i.mnemonic.startswith('ldr'):
    for op in i.operands:
     if op.type==ARM_OP_MEM and op.mem.base==ARM_REG_PC:
      p=((i.address+4)&~3)+op.mem.disp
      if BASE<=p<=BASE+len(b)-4 and struct.unpack_from('<I',b,p-BASE)[0] in LITERALS:
       refs.append(dict(PC=i.address,literal=p,value=struct.unpack_from('<I',b,p-BASE)[0],raw=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str))
 out.mkdir(parents=True)
 with (out/'arm-windows.asm').open('x',encoding='utf8') as f:
  for lo,hi in WINDOWS:
   f.write(f'; window {lo:08X}..{hi:08X}; code/data boundaries require review\n')
   for i in cs.disasm(b[lo-BASE:hi-BASE],lo):
    x=dict(PC=i.address,raw=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str);ins.append(x)
    f.write(f'{i.address:08X} {i.bytes.hex():10} {i.mnemonic:10} {i.op_str}\n')
 def emit(n,v):
  with (out/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 emit('instructions.json',ins);emit('calls.json',calls);emit('literal-read-candidates.json',refs)
 emit('provenance.json',dict(offline=True,CPU_instructions_executed=0,source_sha256=sha(Path(__file__).read_bytes()),BIN_sha256=sha(b)))
 verify_inputs();emit('hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path);collect(p.parse_args().output_dir)
