from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase63-defect-closure'
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'));from independent_validate import decode
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
c=json.loads((P/'development-identity.json').read_text());image=decode((P/(c['candidate']+'.syx')).read_bytes())[0];assert hashlib.sha256(image).hexdigest()==c['BIN_sha256']
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
for at,n in [(0x080481d4,0x6e),(0x0804830e,0x3c),(0x0804834a,0x1d0),(0x08048560,0x130),(0x080381a8,0xce),(0x0801d7d8,0x40),(0x08048a8e,0x60),(0x0801d57e,0x102)]:
 (O/f'candidate-{at:08x}.asm').write_text('\n'.join(f'{i.address:08X}: {i.bytes.hex():10} {i.mnemonic} {i.op_str}' for i in md.disasm(image[at-0x08010000:at-0x08010000+n],at))+'\n')
(O/'audit-identity.json').write_text(json.dumps(dict(confidence='PROVEN',BIN_sha256=c['BIN_sha256'],SYX_sha256=c['SYX_sha256'],register='USB_OTG_HS.GAHBCFG',address='0x40040008',bit_cleared=0,firmware_function='0x08048316',conditional_wait_in_this_function=False),indent=2)+'\n')
print('Exact USB initialization listings saved')
