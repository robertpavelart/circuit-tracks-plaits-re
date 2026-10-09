#!/usr/bin/env python3
"""Meaningful offline checks for source integrity and extracted evidence."""
import argparse
import json
from pathlib import Path
import struct
import tempfile
from ct_static import ROOT, BASE, BIN_HASH, SYX_HASH, sha, save
from ct_data_decode import decode
import ct_fw_tool

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reports',required=True)
    p.add_argument('--dsp',required=True)
    a=p.parse_args()
    reports=Path(a.reports)
    dsp=Path(a.dsp)
    b=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    syx=ROOT/'original/circuittracks-firmware-4486.syx'
    raw=syx.read_bytes()
    assert sha(b)==BIN_HASH and sha(raw)==SYX_HASH
    info=ct_fw_tool.decode_syx(syx)
    assert info['firmware']==b and ct_fw_tool.build_syx(syx,b)==raw
    assert info['crc']==0x4E74DA9E
    assert struct.unpack_from('<II',b)==(0x20050000,0x0805C00D)
    v=struct.unpack_from('<114I',b)
    assert all(x&1 and BASE <= (x&~1) < BASE+len(b) for x in v[1:] if x)
    assert sum(bool(x) for x in v[1:])==105
    for address,text in [(0x0801F5F0,b'>> DSP Uploading...\n\0'),(0x0801F608,b'<< DSP Uploaded\n\0')]:
        assert b[address-BASE:address-BASE+len(text)]==text
    for file,site in [('xrefs-uploading.json',0x0801F560),('xrefs-uploaded.json',0x0801F56C)]:
        report=json.loads((reports/file).read_text())
        assert any(h['kind']=='adr_candidate' and h['address']==site for h in report['hits'])
    manifest=json.loads((dsp/'manifest.json').read_text())
    repeat=json.loads((reports/'dsp/manifest.json').read_text())
    assert manifest==repeat
    for block in manifest['blocks']:
        off=int(block['source_offset'],0)
        source=b[off:off+block['stream_size']]
        stream=(dsp/block['stream_file']).read_bytes()
        payload=(dsp/block['payload_file']).read_bytes()
        assert source==stream and payload==stream[6:]
        assert sha(stream)==block['stream_sha256'] and sha(payload)==block['payload_sha256']
        assert int.from_bytes(stream[:3],'big')*3==len(payload)
        assert int.from_bytes(stream[3:6],'big')==0
        assert stream==(reports/'dsp'/block['stream_file']).read_bytes()
        words=(dsp/(block['name']+'.words.txt')).read_text().splitlines()
        assert len(words)==block['word_count']
        rebuilt=b''.join(int(line.split()[1],16).to_bytes(3,'big') for line in words)
        assert rebuilt==payload
    data,description=decode(b)
    assert data==(reports/'initialized-data.bin').read_bytes()
    assert description['consumed']==description['compressed_size']==2582
    assert len(data)==15618
    # Follow the reconstructed object pointers to hardware configuration.
    def w(address):
        return struct.unpack_from('<I',data,address-0x20000000)[0]
    assert w(w(w(w(0x20000320)+4)))==0x40003800
    transport=w(0x20000320)
    assert w(w(w(transport+12)))==0x40026058
    assert w(w(w(transport+16)))==0x40026070
    damaged=bytearray(b)
    damaged[0x4C3C4:0x4C3C6]=bytes([0x11,0])
    try:
        decode(damaged)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid zero-distance back reference accepted')
    with tempfile.TemporaryDirectory(prefix='ct-static-') as folder:
        sentinel=Path(folder)/'sentinel'
        sentinel.write_bytes(b'preserve')
        try:
            save(sentinel,b'overwrite')
        except FileExistsError:
            pass
        else:
            raise AssertionError('Overwrite allowed')
        assert sentinel.read_bytes()==b'preserve'
    forbidden=ROOT/'original/static-test-prohibited.txt'
    assert not forbidden.exists()
    try:
        save(forbidden,b'forbidden')
    except SystemExit:
        pass
    else:
        raise AssertionError('original/ destination accepted')
    assert not forbidden.exists()
    print('PASS: source hashes, exact roundtrip, vectors, ADR references, five stream ranges/hashes,')
    print('      extraction reproducibility, 24-bit re-encoding, data decoder, SPI2/DMA pointers,')
    print('      malformed data rejection, overwrite refusal and original/ protection.')

if __name__=='__main__':
    main()
