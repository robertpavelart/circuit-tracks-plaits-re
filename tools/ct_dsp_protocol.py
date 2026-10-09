#!/usr/bin/env python3
"""Offline interpretation of normal-selection SHI ISR P:0x156.

Classifies a provided word, never sends it. Does not model firmware execution.
GPIO command/data qualification and saved X:0x11 space flag are explicit inputs.
"""
import argparse,json

def classify(raw, command_lane=True, saved_space='X'):
    if len(raw) not in (2,3):
        raise ValueError('Observed word must contain two or three bytes')
    word=int.from_bytes(raw.ljust(3,b'\0'),'big')
    result=dict(word=f'0x{word:06X}',wire_bytes=len(raw),status='VERIFIED ISR-derived interpretation')
    if not command_lane:
        result.update(operation='write_and_increment',handler='P:0x198',memory_space=saved_space,
                      address='saved X:0x10',data=f'0x{word:06X}')
    elif word & (1<<21):
        result.update(operation='control_mailbox',handler='P:0x163',destination='X:0x12',
                      requested_width=16 if word&0x100 else 24,consumer='P:0x12D')
    elif word & (1<<22):
        result.update(operation='read_next_and_increment',handler='P:0x1A0',memory_space=saved_space,
                      address='saved X:0x10')
    else:
        if word & (1<<20):
            address=((word<<8)-2)&0xffffff
            selector='paged address, subtract two words'
            handler='P:0x171'
        elif word & (1<<19):
            address=word&0x3ffff
            selector='18-bit address'
            handler='P:0x17B'
        else:
            address=word&0x7fff
            selector='15-bit address plus X/Y flag'
            handler='P:0x181'
        read=bool(word&(1<<23))
        space='Y' if word&0x8000 else 'X'
        if not read and (word&0x180000):
            space=saved_space
        result.update(operation='read_and_increment' if read else 'set_write_address',handler=handler,
                      read_handler='P:0x188' if read else None,address=f'0x{address:06X}',
                      memory_space=space,format=selector,
                      caveat='Extended write-address branches retain the prior X:0x11 space selector')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('hex_bytes')
    p.add_argument('--data-lane',action='store_true')
    p.add_argument('--saved-space',choices=['X','Y'],default='X')
    a=p.parse_args()
    print(json.dumps(classify(bytes.fromhex(a.hex_bytes),not a.data_lane,a.saved_space),indent=2))
if __name__=='__main__': main()
