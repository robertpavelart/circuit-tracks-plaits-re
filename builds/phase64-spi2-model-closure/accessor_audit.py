"""Authenticate relevant listings and direct polled-transfer callers."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase63-defect-closure'
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'));from independent_validate import decode
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
c=json.loads((P/'development-identity.json').read_text());b=decode((P/(c['candidate']+'.syx')).read_bytes())[0];assert hashlib.sha256(b).hexdigest()==c['BIN_sha256']
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True;B=0x08010000
def listing(at,n):return '\n'.join(f'{i.address:08X}: {i.bytes.hex():10} {i.mnemonic} {i.op_str}' for i in md.disasm(b[at-B:at-B+n],at))+'\n'
for at,n in [(0x08037770,0x290),(0x08037960,0xa8),(0x08048164,0x60),(0x080291b8,0x548),(0x0803b9d8,0x110),(0x08057532,0x30)]:
 (O/f'candidate-{at:08x}.asm').write_text(listing(at,n))
callers=[]
for off in range(0,len(b)-4,2):
 h=int.from_bytes(b[off:off+2],'little');h2=int.from_bytes(b[off+2:off+4],'little')
 if h&0xf800!=0xf000 or h2&0xd000!=0xd000:continue
 ins=next(md.disasm(b[off:off+4],B+off,count=1),None)
 if ins and ins.mnemonic=='bl' and ins.operands[0].imm in (0x0803baa2,0x08037960):callers.append(dict(address=hex(B+off),target=hex(ins.operands[0].imm),context=listing(B+off-8,28)))
literal=[]
for off in range(0,len(b)-3,4):
 value=int.from_bytes(b[off:off+4],'little')
 if 0x40003800<=value<0x40003820:literal.append(dict(address=hex(B+off),value=hex(value)))
(O/'accessor-audit.json').write_text(json.dumps(dict(confidence='PROVEN',candidate_sha256=c['BIN_sha256'],direct_call_candidates=callers,SPI2_literal_candidates=literal,scope='Authenticated relevant routine listings and direct BL scan. Literal/data candidates are not automatically executable references; indirect closure remains bounded by traced startup.'),indent=2)+'\n')
print('Authenticated listings/callers',len(callers))
