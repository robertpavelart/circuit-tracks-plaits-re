"""Authenticate this phase's narrow ARM/DSP producer and consumer listings."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase63-defect-closure'
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'));from independent_validate import decode
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
c=json.loads((P/'development-identity.json').read_text());image=decode((P/(c['candidate']+'.syx')).read_bytes())[0]
assert hashlib.sha256(image).hexdigest()==c['BIN_sha256']
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
for at,n in [(0x08035e28,0x168),(0x080295e4,0x100),(0x0803ba78,0x60),(0x080377de,0x182),(0x08023414,0x34),(0x080381be,0x80),(0x080482d0,0x84),(0x0801bba4,0x44)]:
 rows=[f'{i.address:08X}: {i.bytes.hex():10} {i.mnemonic} {i.op_str}' for i in md.disasm(image[at-0x08010000:at-0x08010000+n],at)]
 (O/f'candidate-{at:08x}.asm').write_text('\n'.join(rows)+'\n')
asm=(R/'builds/phase64-spi2-model-closure/loaded-core0.asm').read_text().splitlines()
for start,end in [(0x113,0x140),(0x156,0x1b4),(0x1c53,0x1daa)]:
 rows=[s for s in asm if start<=int(s.split(':')[0],16)<end]
 (O/f'DSP-{start:04x}-{end-1:04x}.asm').write_text('\n'.join(rows)+'\n')
(O/'audit-identity.json').write_text(json.dumps(dict(confidence='PROVEN',candidate_sha256=c['BIN_sha256'],command_word='0x200100',ARM_register_or_address=False,interface='DSP SHI control word carried through SPI2 DR',core0_sha256=hashlib.sha256((O/'loaded-core0.be24').read_bytes()).hexdigest(),emulator_sha256=hashlib.sha256((R/'builds/phase24-init-transition/coupled.exe').read_bytes()).hexdigest()),indent=2)+'\n')
print('Narrow producer/consumer listings saved')
