"""Decode the instruction-established ARM initialized-data record for cache provenance.
This is a byte-codec reconstruction, not ARM/DSP CPU boot execution. No hardware.
"""
import argparse,json,struct
from pathlib import Path
from ct_stock_load_audit import ROOT,verify_inputs,sha


def expand(data):
    src=0;dest=bytearray();records=[]
    def take():
        nonlocal src
        if src>=len(data):raise ValueError('Truncated compressed ARM initialization')
        v=data[src];src+=1;return v
    while src<len(data):
        begin=src;token=take();n=token&3
        if not n:n=take()+3
        length=token>>4
        if length==15:length=take()+15
        # Branch972A/9732 goes to96E4: decrement precedes first literal load.
        literals=n-1;out_begin=len(dest)
        for _ in range(literals):dest.append(take())
        distance=None
        if length:
            low=take();high=(token>>2)&3
            if high==3:high=take()
            distance=low+(high<<8)
            if distance<=0 or distance>len(dest):raise ValueError('Unproven/out-of-output back-reference')
            for _ in range(length+2):dest.append(dest[-distance])
        records.append(dict(source_start=begin,source_end=src,token=token,literals=literals,
            copy_bytes=0 if not length else length+2,distance=distance,dest_start=out_begin,dest_end=len(dest)))
        if len(dest)>0x100000:raise ValueError('Unexpected ARM init output extent')
    return bytes(dest),records


def recover():
    verify_inputs();b=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes();base=0x8010000
    def u32(a):return struct.unpack_from('<I',b,a-base)[0]
    assert u32(0x805b5b0)==0x204 and u32(0x805b5b4)==0x224
    assert 0x805b598+u32(0x805b5b0)+0x18==0x805b7b4
    assert 0x805b59e+u32(0x805b5b4)+0x16==0x805b7d8
    # The second walker record invokes Thumb80596C5, passing805B7C8.
    rel=u32(0x805b7c4);signed=rel-(1<<32) if rel>>31 else rel
    assert 0x805b7c4+signed==0x80596c5
    rec=0x805b7c8;src=rec+u32(rec);flagged_size=u32(rec+4);dest=u32(rec+8)
    assert (src,flagged_size,dest)==(0x805c3c4,0x142c,0x20000000)
    raw=b[src-base:src-base+(flagged_size>>1)]
    result,tokens=expand(raw)
    assert len(result)==0x3d02
    cache=result[0x3d00:0x3d02]
    return result,tokens,dict(status='VERIFIED INIT-ONLY codec/output relation; no authentic DSP boot execution',
        descriptor=0x805b7c4,callback=0x80596c4,source_start=src,source_end=src+len(raw),
        source_bytes=len(raw),destination_start=dest,destination_end=dest+len(result),
        walker_start=0x805b7b4,walker_end=0x805b7d8,decoded_bytes=len(result),
        cache_address=0x20003d00,cache_hex=cache.hex(),cache_value=int.from_bytes(cache,'little'),
        cache_provenance_token=[x for x in tokens if x['dest_start']<=0x3d00<x['dest_end']],
        decoded_sha256=sha(result),BIN_sha256=sha(b),CPU_instructions_executed=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path)
    out=p.parse_args().output_dir.resolve();allowed=(ROOT/'builds/phase19c-hostwrite').resolve()
    if out.exists() or out==allowed or not out.is_relative_to(allowed):raise ValueError('Fresh HOSTWRITE child required')
    data,tokens,report=recover();out.mkdir(parents=True)
    with (out/'arm-initialized-data.bin').open('xb') as f:f.write(data)
    for n,v in [('arm-cache-init.json',report),('init-codec-records.json',tokens)]:
        with (out/n).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(report,indent=2))
