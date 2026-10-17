"""Read-only static mutation census; raw candidates are NOT proven reachability."""
from pathlib import Path
import json, hashlib, base64, struct
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
O=Path(__file__).resolve().parent
R=O.parents[1]
REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
stock=(REF/'stock/circuittracks-firmware-4486-STOCK.bin').read_bytes()
line=next(x for x in (REF/'tools/rc_uploader.html').read_text(encoding='utf8').splitlines() if x.startswith('const PATCHES = '))
ops=json.loads(line[len('const PATCHES = '):].rstrip(';'))['B1.3']['ops']
b13=b''.join(stock[x[1]:x[1]+x[2]] if x[0]==0 else base64.b64decode(x[1]) for x in ops)
man=json.loads((REF/'firmware/b1.3/manifest.json').read_text())
assert hashlib.sha256(b13).hexdigest()==man['image_sha256']
boot=(REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin').read_bytes()[:0x10000]
assert hashlib.sha256(boot).hexdigest()=='09fcb71d6583a5714cb96d496ffb423c0d7049754a4cb4413f588d6f54148643'
candidate=(R/'builds/phase43-hardware-test-candidate/circuittracks-4486-nor-evidence-test.bin').read_bytes()
assert hashlib.sha256(candidate).hexdigest()=='9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6'
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True
images={'bootloader':(0x08000000,boot),'B13':(0x08010000,b13),'candidate':(0x08010000,candidate)}
targets={0x08005db4:'boot identity setter',0x08025228:'app identity setter',0x08037494:'app sector erase',0x080374d4:'app page program',0x08037648:'app chip erase',0x08023078:'app backend erase',0x08022fdc:'app backend write',0x080058b4:'boot sync write',0x08005380:'boot backend write',0x08005410:'boot backend erase',0x080076cc:'boot read'}
targets.update({0x08007730:'boot sector erase',0x08007770:'boot page program',0x080078e4:'boot chip erase',0x08023f68:'app submit descriptor',0x08024164:'app sync write',0x080241b8:'app sync erase',0x080241f0:'app async erase',0x08005940:'boot async erase'})
result={'scope':'Exhaustive halfword immediate branch candidates and aligned pointer candidates; not exhaustive indirect execution closure','images':{},'targets':{hex(k):v for k,v in targets.items()},'calls':[],'pointers':[]}
result['reviewed_stock_mutator_bodies_equal_B13_candidate']=[]
for start,n in [(0x08022fdc,0x120),(0x08037494,0x290),(0x0802520c,0x160),(0x08024d52,0x110),(0x08024014,0xf0)]:
 before=b13[start-0x08010000:start-0x08010000+n];after=candidate[start-0x08010000:start-0x08010000+n]
 assert before==after
 result['reviewed_stock_mutator_bodies_equal_B13_candidate'].append({'start':hex(start),'length':n,'sha256':hashlib.sha256(before).hexdigest(),'equal':True})
decoded={}
for name,(base,data) in images.items():
 result['images'][name]={'base':hex(base),'length':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 ins=[]
 for off in range(0,len(data)-3,2):
  i=next(md.disasm(data[off:off+4],base+off,count=1),None)
  if not i:continue
  ins.append(i)
  if i.mnemonic in ('bl','b.w','b') and i.operands[0].type==2:
   t=i.operands[0].imm
   if t in targets:result['calls'].append({'image':name,'at':hex(i.address),'kind':i.mnemonic,'target':hex(t),'label':targets[t]})
 for off in range(0,len(data)-3,4):
  value=struct.unpack_from('<I',data,off)[0]
  if (value&~1) in targets:result['pointers'].append({'image':name,'at':hex(base+off),'value':hex(value),'label':targets[value&~1]})
 decoded[name]=ins
# Pin/disassemble exact native mutation helper bodies and caller contexts.
ranges={'bootloader':[(0x08005300,0x190),(0x08005880,0xa0),(0x08005d98,0x40),(0x080075c0,0x450)],'B13':[(0x08022fdc,0x120),(0x08023078,0x88),(0x08024014,0xf0),(0x0802520c,0x40),(0x08037494,0x290),(0x08025160,0x90)],'candidate':[(0x08022fdc,0x120),(0x08023078,0x88),(0x08024014,0xf0),(0x0802520c,0x40),(0x08037494,0x290),(0x08025160,0x90)]}
ranges['bootloader'] += [(0x08003990,0x120),(0x08003b2a,0x2e0),(0x08007e30,0x1c0)]
for key in ('B13','candidate'):ranges[key] += [(0x0801eb40,0x340),(0x08024130,0x150),(0x08038c00,0x400),(0x0802524c,0x120),(0x08026b80,0x110),(0x0802503c,0x100)]
for key in ('B13','candidate'):ranges[key] += [(0x08024d52,0x110)]
ranges['bootloader'] += [(0x08005dd8,0x130),(0x08005908,0x140),(0x080059fa,0x300)]
for name,rr in ranges.items():
 base,data=images[name];out=[]
 for a,n in rr:
  out.append(f'\n; region {a:08X} length {n:X} sha256 '+hashlib.sha256(data[a-base:a-base+n]).hexdigest())
  for i in md.disasm(data[a-base:a-base+n],a):
   suffix=''
   for op in i.operands:
    if op.type==3 and op.mem.base==11:
     at=((i.address+4)&~3)+op.mem.disp
     if base<=at<=base+len(data)-4:suffix=f' ; [{at:08x}]={struct.unpack_from("<I",data,at-base)[0]:08x}'
   out.append(f'{i.address:08x}: {i.mnemonic:10} {i.op_str}'+suffix)
 (O/f'nor-{name}.asm').write_text('\n'.join(out)+'\n',encoding='utf8')
(O/'nor-census.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,indent=2))
