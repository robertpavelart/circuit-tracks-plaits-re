#!/usr/bin/env python3
"""Translate startup decompressor 0x080596C4; creates an offline RAM data view.

No firmware execution or device memory access. Bounds checks intentionally
reject malformed streams. These are ARM initialized data, not DSP compression.
"""
import argparse
import json
from pathlib import Path
import struct
from ct_static import ROOT, BASE, BIN_HASH, sha, save

def decode(data):
    record = 0x4B7C8
    relative, length_flags, destination = struct.unpack_from('<3I', data, record)
    if length_flags & 1:
        raise ValueError('Unsupported sb-relative destination')
    start = record+relative
    end = start+(length_flags>>1)
    if start < 0 or end > len(data):
        raise ValueError('Compressed range outside source')
    pos = start
    out = bytearray()
    def byte():
        nonlocal pos
        if pos >= end:
            raise ValueError('Truncated compressed data')
        value = data[pos]
        pos += 1
        return value
    while pos < end:
        token = byte()
        literals = token & 3
        if not literals:
            literals = byte()+3
        match = token >> 4
        if match == 15:
            match = byte()+15
        for _ in range(literals-1):
            out.append(byte())
        if match:
            distance = byte()
            high = (token>>2)&3
            if high == 3:
                high = byte()
            distance += high<<8
            if distance == 0 or distance > len(out):
                raise ValueError('Invalid back reference')
            for _ in range(match+2):
                out.append(out[-distance])
        if len(out) > 0x3D04:
            raise ValueError('Output exceeds next zero-initialized region')
    return bytes(out), dict(record=f'0x{BASE+record:08X}', source=f'0x{BASE+start:08X}',
                           compressed_size=end-start, consumed=pos-start,
                           destination=f'0x{destination:08X}', output_size=len(out),
                           gap_before_zero_region=0x3D04-len(out), sha256=sha(out))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bin', default=str(ROOT/'firmware/circuittracks-firmware-4486.bin'))
    p.add_argument('--output', required=True)
    p.add_argument('--report', required=True)
    a = p.parse_args()
    data = Path(a.bin).read_bytes()
    if sha(data) != BIN_HASH:
        raise SystemExit('Only verified build 4486 supported')
    if Path(a.output).resolve() == Path(a.report).resolve() or any(Path(x).exists() for x in [a.output,a.report]):
        raise SystemExit('Choose two distinct fresh output files')
    out, report = decode(data)
    def word(address):
        return struct.unpack_from('<I', out, address-0x20000000)[0]
    state = 0x20000314
    transport = word(state+12)
    serial_object = word(transport+4)
    spi_config = word(serial_object)
    rx_config = word(word(transport+12))
    tx_config = word(word(transport+16))
    report['transport'] = dict(state=f'0x{state:08X}', transport=f'0x{transport:08X}',
                               serial_object=f'0x{serial_object:08X}', spi_config=f'0x{spi_config:08X}',
                               spi_base=f'0x{word(spi_config):08X}',
                               rx_dma_stream=f'0x{word(rx_config):08X}', rx_peripheral=f'0x{word(rx_config+4):08X}',
                               tx_dma_stream=f'0x{word(tx_config):08X}', tx_peripheral=f'0x{word(tx_config+4):08X}')
    report['gpio_groups'] = []
    for channel in range(2):
        group = word(state+16+channel*4)
        pins = []
        for index in range(3):
            config = word(word(group+index*4))
            pins.append(dict(index=index, config=f'0x{config:08X}', gpio_base=f'0x{word(config):08X}',
                             pin_mask=f'0x{word(config+4):X}'))
        report['gpio_groups'].append(dict(channel=channel, group=f'0x{group:08X}', pins=pins))
    save(a.output, out)
    save(a.report, json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
