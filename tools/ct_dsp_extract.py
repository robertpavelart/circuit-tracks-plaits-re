#!/usr/bin/env python3
"""Extract statically traced upload streams, not a flashable DSP image.

Each stream consists of two big-endian 24-bit header words (count, load
address), followed by count big-endian 24-bit words. Source ranges come from
the uploader at 0x08029260 and pointer table at 0x08029700.
"""
import argparse
import json
from pathlib import Path
import struct
from ct_static import ROOT, BASE, BIN_HASH, sha, save

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bin', default=str(ROOT/'firmware/circuittracks-firmware-4486.bin'))
    p.add_argument('--output-dir', required=True)
    a = p.parse_args()
    data = Path(a.bin).read_bytes()
    if sha(data) != BIN_HASH:
        raise SystemExit('This evidence manifest applies only to the verified build 4486 BIN')
    out = Path(a.output_dir).resolve()
    if out == (ROOT/'original').resolve() or (ROOT/'original').resolve() in out.parents:
        raise SystemExit('Protected destination')
    if out.exists():
        raise SystemExit('Output directory already exists; choose a new directory')
    pointers = struct.unpack_from('<4I', data, 0x19700)
    candidates = [('bootstrap', 0x080296E0, 'first upload; channel argument 0')]
    candidates += [(f'selection{s}-channel{c}', pointers[s+2*c], f'selection {s}; channel argument {c}')
                   for s in range(2) for c in range(2)]
    outputs = []
    entries = []
    for name, address, role in candidates:
        offset = address-BASE
        count = int.from_bytes(data[offset:offset+3], 'big')
        load = int.from_bytes(data[offset+3:offset+6], 'big')
        size = (count+2)*3
        if count > 65533 or offset < 0 or offset+size > len(data):
            raise SystemExit(f'Invalid upload stream {name}')
        raw = data[offset:offset+size]
        words = [int.from_bytes(raw[i:i+3], 'big') for i in range(6, size, 3)]
        words_text = ''.join(f'{load+i:06X} {w:06X}\n' for i,w in enumerate(words))
        stream_name = name+'.boot24.bin'
        payload_name = name+'.payload24.bin'
        outputs.extend([(stream_name, raw), (payload_name, raw[6:]), (name+'.words.txt', words_text)])
        entries.append(dict(name=name, role=role, source_offset=f'0x{offset:X}',
                            source_address=f'0x{address:08X}', end_address=f'0x{address+size:08X}',
                            stream_size=size, payload_size=size-6, word_count=count,
                            load_word_address=f'0x{load:06X}', stream_sha256=sha(raw),
                            payload_sha256=sha(raw[6:]), stream_file=stream_name, payload_file=payload_name,
                            encoding='big-endian 24-bit words; no ARM-side decompression',
                            identity='uploaded DSP program candidate; silicon/core identity not proven'))
    manifest = dict(source_bin=Path(a.bin).name, source_sha256=sha(data), base=f'0x{BASE:08X}',
                    uploader='0x08029260', stream_sender='0x08029200', pointer_table='0x08029700',
                    boot_format_reference='https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf#page=103',
                    blocks=entries)
    # Precompute and validate everything before creating the fresh destination.
    out.mkdir(parents=True, exist_ok=False)
    for name, content in outputs:
        save(out/name, content)
    save(out/'manifest.json', json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
