"""Offline authenticated-byte xref inventory. Candidate xrefs are not CFG proofs."""
from pathlib import Path
import json,hashlib,struct,sys
from capstone import *
from capstone.arm import *
O=Path(__file__).resolve().parent
R=O.parents[1]
REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
app=(R/'builds/phase44-preflash-redteam-closure/circuittracks-4486-nor-evidence-atomic-test.bin').read_bytes()
boot=(REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin').read_bytes()[:0x10000]
assert hashlib.sha256(boot).hexdigest()=='09fcb71d6583a5714cb96d496ffb423c0d7049754a4cb4413f588d6f54148643'
identity=json.loads((R/'builds/phase44-preflash-redteam-closure/atomic-candidate-identity.json').read_text())
assert hashlib.sha256(app).hexdigest()=='0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738'
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True
images={'app':(0x8010000,app),'boot':(0x8000000,boot)}
def listing(name,a,n):
 base,data=images[name];out=[]
 for i in md.disasm(data[a-base:a-base+n],a):
  suffix=''
  for op in i.operands:
   if op.type==ARM_OP_MEM and op.mem.base==ARM_REG_PC:
    at=((i.address+4)&~3)+op.mem.disp
    if base<=at<=base+len(data)-4:suffix+=f' ; [{at:08x}]={struct.unpack_from("<I",data,at-base)[0]:08x}'
  out.append(f'{i.address:08x}: {i.mnemonic:10} {i.op_str}{suffix}')
 return '\n'.join(out)
if len(sys.argv)>1:
 print(listing(sys.argv[1],int(sys.argv[2],16),int(sys.argv[3],16)));raise SystemExit
targets=[0x8023f68,0x80240e8,0x8024130,0x8024164,0x80241a8,0x80241b8,0x80241f0,0x8026bd4,0x8026bd8,0x8022fdc,0x8023078,0x8037494,0x80374d4,0x8037648,0x80373a8,0x80373b4,0x803769c,0x8022776,0x8022746,0x8022818,0x8025228,0x80056b8,0x80058b4,0x8005908,0x8005940,0x8005380,0x8005410,0x8007730,0x8007770,0x80078e4,0x8005db4]
res={'scope':'All halfword immediate branch candidates, all aligned pointer candidates and PC-relative references to target words; each requires code/data review. Not exhaustive computed-target reachability.','images':{},'direct':[],'pointers':[],'literal_xrefs':[]}
for name,(base,data) in images.items():
 res['images'][name]={'base':hex(base),'length':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 ins=[]
 for off in range(0,len(data)-3,2):
  i=next(md.disasm(data[off:off+4],base+off,count=1),None)
  if not i:continue
  ins.append(i)
  if i.mnemonic in ('bl','b','b.w') and i.operands[0].type==ARM_OP_IMM and i.operands[0].imm in targets:
   res['direct'].append({'image':name,'at':hex(i.address),'target':hex(i.operands[0].imm),'kind':i.mnemonic})
 ptrs={}
 for off in range(0,len(data)-3,4):
  v=struct.unpack_from('<I',data,off)[0]
  if v&~1 in targets:ptrs[base+off]=v;res['pointers'].append({'image':name,'at':hex(base+off),'value':hex(v)})
 for i in ins:
  for op in i.operands:
   if op.type==ARM_OP_MEM and op.mem.base==ARM_REG_PC:
    at=((i.address+4)&~3)+op.mem.disp
    if at in ptrs:res['literal_xrefs'].append({'image':name,'at':hex(i.address),'literal':hex(at),'value':hex(ptrs[at]),'instruction':i.mnemonic+' '+i.op_str})
(O/'mutation-graph.json').write_text(json.dumps(res,indent=2)+'\n',encoding='utf8')
rr={'app':[(0x8023f68,0x330),(0x8026b80,0x120),(0x8025228,0x130),(0x8037350,0x3f0),(0x8022700,0x2b0),(0x8047c40,0x120)],'boot':[(0x80056b8,0x360),(0x80075e0,0x370),(0x80053f0,0xc0),(0x8005d98,0x150)]}
for name,ranges in rr.items():
 text='\n\n'.join(f'; {a:08x}+{n:x}\n'+listing(name,a,n) for a,n in ranges)
 (O/f'mutation-{name}.asm').write_text(text+'\n',encoding='utf8')
print(json.dumps(res,indent=2))

