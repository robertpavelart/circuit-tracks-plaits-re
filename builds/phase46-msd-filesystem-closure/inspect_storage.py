"""Read-only authenticated storage-code inspection; outputs only Phase46 evidence.

Candidate xrefs include halfword scan false positives. They are not a complete CFG.
No device, MIDI, network, builder or firmware-output imports.
"""
from pathlib import Path
import sys, struct, json, hashlib
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
from capstone.arm import ARM_OP_MEM, ARM_OP_IMM, ARM_REG_PC
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
REF = Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
app = (ROOT/'builds/phase44-preflash-redteam-closure/circuittracks-4486-nor-evidence-atomic-test.bin').read_bytes()
boot = (REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin').read_bytes()[:0x10000]
assert hashlib.sha256(app).hexdigest() == '0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738'
assert hashlib.sha256(boot).hexdigest() == '09fcb71d6583a5714cb96d496ffb423c0d7049754a4cb4413f588d6f54148643'
sys.path.insert(0, str(ROOT/'tools'))
from ct_data_decode import decode
init, descriptor = decode(app)
images = {'app': (0x08010000, app), 'boot': (0x08000000, boot)}
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS); md.detail = True

def listing(name, address, length):
    base, data = images[name]; lines = []
    for i in md.disasm(data[address-base:address-base+length], address):
        suffix = ''
        for op in i.operands:
            if op.type == ARM_OP_MEM and op.mem.base == ARM_REG_PC:
                at = ((i.address+4)&~3)+op.mem.disp
                if base <= at <= base+len(data)-4:
                    suffix += f' ; [{at:08X}]={struct.unpack_from("<I", data, at-base)[0]:08X}'
        lines.append(f'{i.address:08X}: {i.mnemonic:10} {i.op_str}{suffix}')
    return '\n'.join(lines)+'\n'

def xrefs(targets):
    result = {'scope': 'Halfword direct/literal candidates and byte-aligned initialized pointers; not complete computed-flow proof', 'direct': [], 'literal': [], 'pointers': []}
    for name, (base, data) in images.items():
        for off in range(0, len(data)-3, 2):
            i = next(md.disasm(data[off:off+4], base+off, count=1), None)
            if not i: continue
            for op in i.operands:
                if op.type == ARM_OP_IMM and i.mnemonic.startswith(('b', 'cb')) and (op.imm & ~1) in targets:
                    result['direct'].append(dict(image=name, at=hex(i.address), instruction=i.mnemonic+' '+i.op_str))
                if op.type == ARM_OP_MEM and op.mem.base == ARM_REG_PC:
                    at = ((i.address+4)&~3)+op.mem.disp
                    if base <= at <= base+len(data)-4:
                        v = struct.unpack_from('<I', data, at-base)[0]
                        if v in targets or (v & ~1) in targets:
                            result['literal'].append(dict(image=name, at=hex(i.address), value=hex(v)))
        for off in range(len(data)-3):
            v = struct.unpack_from('<I', data, off)[0]
            if v in targets or (v & ~1) in targets:
                result['pointers'].append(dict(image=name, at=hex(base+off), value=hex(v)))
    for off in range(len(init)-3):
        v = struct.unpack_from('<I', init, off)[0]
        if v in targets or (v & ~1) in targets:
            result['pointers'].append(dict(image='initialized-app-RAM', at=hex(0x20000000+off), value=hex(v)))
    return result

if __name__ == '__main__':
    if sys.argv[1] == 'xref':
        result = xrefs({int(s, 16) for s in sys.argv[3:]})
        (OUT/(sys.argv[2]+'.json')).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(result, indent=2))
    else:
        name, address, length = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
        text = listing(name, address, length)
        (OUT/f'{name}-{address:08x}.asm').write_text(text, encoding='utf-8')
        print(text)
