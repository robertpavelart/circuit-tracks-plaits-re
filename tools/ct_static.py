#!/usr/bin/env python3
"""Offline Circuit Tracks evidence collection. Never opens a device.

All output files are exclusive-create. Address scans are candidates, not proof
of code reachability; data and alternate instruction alignments can decode.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'builds/python-deps'))
sys.path.insert(0, str(ROOT / 'tools'))
import ct_fw_tool

BASE = 0x08010000
SYX_HASH = 'bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd'
BIN_HASH = 'b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(path, data):
    p = Path(path).resolve()
    if p == (ROOT/'original').resolve() or (ROOT/'original').resolve() in p.parents:
        raise SystemExit('Protected original/ destination')
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f:
        f.write(data if isinstance(data, bytes) else data.encode('utf-8'))

def engine():
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN, CS_MODE_MCLASS
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN | CS_MODE_MCLASS)
    cs.detail = True
    return cs

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bin', default=str(ROOT / 'firmware/circuittracks-firmware-4486.bin'))
    p.add_argument('--base', type=lambda x: int(x, 0), default=BASE)
    sub = p.add_subparsers(dest='command', required=True)
    b = sub.add_parser('baseline')
    b.add_argument('--syx', default=str(ROOT / 'original/circuittracks-firmware-4486.syx'))
    b.add_argument('--output', required=True)
    s = sub.add_parser('survey')
    s.add_argument('--output', required=True)
    d = sub.add_parser('disasm')
    d.add_argument('--start', required=True, type=lambda x: int(x, 0))
    d.add_argument('--end', required=True, type=lambda x: int(x, 0))
    d.add_argument('--output', required=True)
    x = sub.add_parser('xrefs')
    x.add_argument('--target', required=True, type=lambda x: int(x, 0))
    x.add_argument('--output', required=True)
    e = sub.add_parser('extract')
    e.add_argument('--offset', required=True, type=lambda x: int(x, 0))
    e.add_argument('--size', required=True, type=lambda x: int(x, 0))
    e.add_argument('--output', required=True)
    a = p.parse_args()
    data = Path(a.bin).read_bytes()
    base = a.base
    if a.command == 'baseline':
        info = ct_fw_tool.decode_syx(Path(a.syx))
        rebuilt = ct_fw_tool.build_syx(Path(a.syx), info['firmware'])
        result = dict(syx_size=len(info['raw']), bin_size=len(data), syx_sha256=sha(info['raw']),
                      bin_sha256=sha(data), rebuilt_sha256=sha(rebuilt),
                      crc32=f"0x{info['crc']:08X}", write_chunks=info['write_count'],
                      init_version=info['init_version'], header_version=info['header_version'],
                      target_code=info['target_code'], decoded_equals_bin=info['firmware'] == data,
                      exact_syx_match=rebuilt == info['raw'])
        result['expected_hashes_match'] = result['syx_sha256'] == SYX_HASH and result['bin_sha256'] == BIN_HASH
        save(a.output, json.dumps(result, indent=2) + '\n')
        if not all(result[k] for k in ['decoded_equals_bin', 'exact_syx_match', 'expected_hashes_match']):
            raise SystemExit('Baseline mismatch')
    elif a.command == 'survey':
        core = ['MSP','Reset','NMI','HardFault','MemManage','BusFault','UsageFault','Reserved',
                'Reserved','Reserved','Reserved','SVCall','DebugMonitor','Reserved','PendSV','SysTick']
        vectors = []
        for i in range(min(114, len(data)//4)):
            value = struct.unpack_from('<I', data, i*4)[0]
            vectors.append(dict(index=i, irq=i-16 if i>=16 else None,
                                name=core[i] if i<16 else f'IRQ{i-16}', offset=i*4,
                                vector=value, code=value & ~1,
                                thumb=bool(value & 1), in_image=base <= (value & ~1) < base+len(data)))
        strings = [dict(offset=m.start(), address=base+m.start(), text=m.group().decode('ascii'))
                   for m in re.finditer(rb'[\x20-\x7e]{4,}', data)]
        save(a.output, json.dumps(dict(base=base, end=base+len(data), sha256=sha(data),
                                      vector_count_candidate=114, vectors=vectors, strings=strings), indent=2)+'\n')
    elif a.command == 'disasm':
        if not base <= a.start < a.end <= base+len(data) or a.start & 1:
            raise SystemExit('Invalid address range')
        cs = engine()
        cs.skipdata = True
        lines = []
        for i in cs.disasm(data[a.start-base:a.end-base], a.start):
            annotation = ''
            if i.id:
                from capstone.arm import ARM_OP_MEM, ARM_REG_PC
                for operand in i.operands:
                    if operand.type == ARM_OP_MEM and operand.mem.base == ARM_REG_PC:
                        literal = ((i.address+4)&~3)+operand.mem.disp
                        if base <= literal <= base+len(data)-4:
                            annotation = f' ; [{literal:08X}] = {struct.unpack_from("<I", data, literal-base)[0]:08X}'
                if i.mnemonic == 'adr':
                    annotation = f' ; address = {((i.address+4)&~3)+i.operands[1].imm:08X}'
                if i.mnemonic in ('addw','subw') and i.operands[1].reg == ARM_REG_PC:
                    sign = -1 if i.mnemonic == 'subw' else 1
                    annotation = f' ; address = {((i.address+4)&~3)+sign*i.operands[2].imm:08X}'
            lines.append(f'{i.address:08X}  {i.bytes.hex():10s} {i.mnemonic:9s} {i.op_str}{annotation}')
        save(a.output, '\n'.join(lines)+'\n')
    elif a.command == 'xrefs':
        from capstone.arm import ARM_OP_IMM, ARM_OP_MEM, ARM_REG_PC
        cs = engine()
        hits = []
        needle = struct.pack('<I', a.target)
        hits.extend(dict(kind='raw_pointer', address=base+m.start())
                    for m in re.finditer(re.escape(needle), data))
        # Decode independently at each halfword to avoid losing code after data.
        for off in range(0, len(data)-3, 2):
            seq = list(cs.disasm(data[off:off+4], base+off, count=1))
            if not seq:
                continue
            i = seq[0]
            if i.mnemonic == 'adr' and ((i.address+4)&~3)+i.operands[1].imm == a.target:
                hits.append(dict(kind='adr_candidate', address=i.address, instruction=i.mnemonic+' '+i.op_str))
            if i.mnemonic in ('addw','subw') and i.operands[1].reg == ARM_REG_PC:
                sign = -1 if i.mnemonic == 'subw' else 1
                if ((i.address+4)&~3)+sign*i.operands[2].imm == a.target:
                    hits.append(dict(kind='pc_address_candidate', address=i.address, instruction=i.mnemonic+' '+i.op_str))
            if i.mnemonic.startswith(('bl', 'b')) and any(o.type == ARM_OP_IMM and o.imm == a.target for o in i.operands):
                hits.append(dict(kind='branch_candidate', address=i.address, instruction=i.mnemonic+' '+i.op_str))
            if i.mnemonic.startswith('ldr'):
                for o in i.operands:
                    if o.type == ARM_OP_MEM and o.mem.base == ARM_REG_PC:
                        addr = ((i.address+4)&~3)+o.mem.disp
                        if base <= addr <= base+len(data)-4 and struct.unpack_from('<I',data,addr-base)[0] == a.target:
                            hits.append(dict(kind='literal_load_candidate', address=i.address, literal=addr, instruction=i.mnemonic+' '+i.op_str))
            if i.mnemonic == 'movw' and i.operands[1].imm == a.target & 0xffff:
                reg = i.operands[0].reg
                for j in cs.disasm(data[off+i.size:off+32], i.address+i.size):
                    if j.mnemonic == 'movt' and j.operands[0].reg == reg and j.operands[1].imm == a.target >> 16:
                        hits.append(dict(kind='movw_movt_candidate', address=i.address, upper_address=j.address, register=i.reg_name(reg)))
                        break
                    if reg in j.regs_access()[1]:
                        break
        save(a.output, json.dumps(dict(target=a.target, hits=hits), indent=2)+'\n')
    elif a.command == 'extract':
        if a.offset < 0 or a.size <= 0 or a.offset+a.size > len(data):
            raise SystemExit('Extraction outside image')
        out = Path(a.output).resolve()
        if out == Path(a.bin).resolve() or (ROOT/'original').resolve() in out.parents:
            raise SystemExit('Protected destination')
        block = data[a.offset:a.offset+a.size]
        save(out, block)
        print(json.dumps(dict(source_sha256=sha(data), offset=a.offset, size=a.size, address=base+a.offset,
                              extracted_sha256=sha(block)), indent=2))

if __name__ == '__main__':
    main()
