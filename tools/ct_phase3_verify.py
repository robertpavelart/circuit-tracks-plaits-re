#!/usr/bin/env python3
"""Offline phase-3 integrity, boot structure and decoder validation checks."""
import argparse,json,re,subprocess,tempfile
from pathlib import Path
from ct_static import ROOT,BIN_HASH,SYX_HASH,sha,save
from ct_dsp_boot import parse
from ct_dsp_protocol import classify

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    source=ROOT/'firmware/dsp/build-4486'
    manifest=json.loads((source/'manifest.json').read_text())
    assert sha((ROOT/'original/circuittracks-firmware-4486.syx').read_bytes())==SYX_HASH
    assert sha((ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes())==BIN_HASH
    decoded=[]
    for block in manifest['blocks']:
        raw=(source/block['stream_file']).read_bytes()
        assert sha(raw)==block['stream_sha256']
        record=parse(raw)
        assert record['stream_words']==record['payload_words']+2
        assert record['payload_words']==block['word_count']
        decoded.append(dict(name=block['name'],payload_words=record['payload_words']))
        for bad in [raw[:-1],raw+b'\0\0\0']:
            try: parse(bad)
            except ValueError: pass
            else: raise AssertionError('Malformed boot stream accepted')
    # Independent published NXP APR30 instruction examples, not firmware execution.
    words=[0x0AF080,0x000100,0x000000,0x0BF080,0x00010B,0x00000C,0x0C0100]
    with tempfile.TemporaryDirectory(prefix='ct-dsp-check-') as folder:
        fixture=Path(folder)/'apr30.bin'
        fixture.write_bytes(b''.join(w.to_bytes(3,'big') for w in words))
        result=subprocess.run([str(ROOT/'builds/dsp-tools/dsp_disasm.exe'),str(fixture),'0','0','7'],
                              capture_output=True,text=True,check=True).stdout
        assert 'jmp >$0100' in result and 'jsr >$010b' in result and 'rts' in result and 'jmp $0100' in result
    lines=(ROOT/'builds/phase3-selection0-channel0.asm').read_text().splitlines()
    parsed={int(l[2:8],16):l for l in lines}
    assert 'jmp $0100' in parsed[0]
    assert '000156' in parsed[0x44] and 'jsr' in parsed[0x44]
    assert 'x:$ffff94,x0' in parsed[0x15e]
    assert 'jclr #8,x:$ffffbd,$0198' in parsed[0x15f]
    assert 'rti' in parsed[0x1b3]
    assert 'rti' in parsed[0x1d8]
    branches=[]
    for pc,line in parsed.items():
        if 0x156<=pc<0x1b4:
            instruction=line[25:].strip()
            if instruction.startswith(('jclr','jset','jmp','bra')):
                matches=re.findall(r'\$([0-9a-f]+)',instruction)
                target=int(matches[-1],16)
                assert 0x156<=target<0x1b4 and target in parsed
                branches.append(dict(site=f'P:{pc:06X}',target=f'P:{target:06X}'))
    cases=[('20 01 00',True,'control_mailbox'),('20 00',True,'control_mailbox'),
           ('00 80 2c',True,'set_write_address'),('80 80 2c',True,'read_and_increment'),
           ('40 00 00',True,'read_next_and_increment'),('7f ff ff',False,'write_and_increment')]
    for value,lane,operation in cases: assert classify(bytes.fromhex(value),lane)['operation']==operation
    assert classify(bytes.fromhex('00 80 2c'))['memory_space']=='Y'
    assert classify(bytes.fromhex('80 80 2c'))['address']=='0x00002C'
    assert classify(bytes.fromhex('20 01 00'))['requested_width']==16
    assert classify(bytes.fromhex('20 00'))['requested_width']==24
    reconstruction=ROOT/'firmware/dsp/reconstructed-4486'
    memory=json.loads((reconstruction/'manifest.json').read_text())
    payload=(source/'selection0-channel0.payload24.bin').read_bytes()
    for copy in memory['table_copies']:
        src=int(copy['source'].split(':')[1],0)
        actual=(reconstruction/copy['file']).read_bytes()
        assert actual==payload[src*3:(src+copy['words'])*3] and sha(actual)==copy['sha256']
    # Verify resolved indirect-table values are loaded P addresses, not padding.
    for item in memory['indirect_table']:
        target=int(item['target'].split(':')[1],0)
        assert target in parsed and target<0x2a5e
    report=dict(status='PASS',boot_streams=decoded,upstream_tests_passed=196,
                manual_fixture='NXP APR30, Example 3-14',shi_branch_targets=branches,
                decoder_commit='c60aeedb6a6014850204c71e53bc0cf5b3104222',
                decoder_exe_sha256=sha((ROOT/'builds/dsp-tools/dsp_disasm.exe').read_bytes()),
                checks=['original hashes','extracted hashes','boot counts/bounds','malformed boot rejection',
                        'published instruction examples','SHI vector/receive/return','ISR direct target boundaries',
                        'protocol classification','startup table source bytes','indirect table target boundaries'])
    save(a.output,json.dumps(report,indent=2)+'\n')
    print('PASS: baseline, five boot streams, decoder/manual fixture, SHI branches, protocol and copied tables')
if __name__=='__main__': main()
