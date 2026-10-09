#!/usr/bin/env python3
"""Parse exactly one observed SHI count/address/data record per upload stream.

Do not search payload words for imagined nested records. The P-space assignment
is conditional on the corroborated DSP56724-family SHI mode-0 boot format.
DSP addresses are word addresses, unlike source byte offsets.
"""
import argparse
import json
from pathlib import Path
from ct_static import ROOT, sha, save

def parse(raw):
    if len(raw)%3 or len(raw)<6:
        raise ValueError('Incomplete 24-bit header or word alignment')
    words=[int.from_bytes(raw[i:i+3],'big') for i in range(0,len(raw),3)]
    count,load=words[:2]
    if len(words)!=count+2:
        raise ValueError('Count does not cover exactly the observed stream')
    if load+count>0x1000000:
        raise ValueError('Load range exceeds 24-bit address space')
    return dict(record_count=1,record_type='SHI count/address/program-words (no explicit type tag)',
                header_bytes=6,stream_words=len(words),payload_words=count,load_word_address=f'0x{load:06X}',
                load_end_exclusive=f'0x{load+count:06X}',boot_start_word_address=f'0x{load:06X}',
                memory_space='P / PRAM under DSP56724-compatible mode-0 boot contract',
                memory_space_status='corroborated ISA/boot-format interpretation; exact silicon unresolved',
                record_map=[dict(stream_offset=0,size=3,field='24-bit word count',value=count),
                            dict(stream_offset=3,size=3,field='24-bit load/start address',value=load),
                            dict(stream_offset=6,size=count*3,field='program-word payload',
                                 first_word_address=load,end_word_address_exclusive=load+count)],
                payload_sha256=sha(raw[6:]))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--streams',default=str(ROOT/'firmware/dsp/build-4486'))
    p.add_argument('--output',required=True)
    a=p.parse_args()
    source=Path(a.streams)
    manifest=json.loads((source/'manifest.json').read_text())
    blocks=[]
    for block in manifest['blocks']:
        raw=(source/block['stream_file']).read_bytes()
        if sha(raw)!=block['stream_sha256']:
            raise ValueError('Stream differs from verified extraction')
        record=parse(raw)
        record.update(name=block['name'],source_offset=block['source_offset'],source_address=block['source_address'])
        blocks.append(record)
    save(a.output,json.dumps(dict(endianness='24-bit big-endian',blocks=blocks,
                                  reference='https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf#page=103'),indent=2)+'\n')

if __name__=='__main__':
    main()
