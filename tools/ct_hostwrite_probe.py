"""Offline targeted ARM helper/cache call scan using the existing Capstone copy.
No devices, firmware writes, CPU execution, packets, installation or network.
Candidate halfword edges are not automatically NORMAL-reachable instructions.
"""
import argparse,json,struct
from pathlib import Path
from ct_static import ROOT,BASE,engine,sha
from ct_stock_load_audit import verify_inputs

TARGETS={0x80292f8,0x8029314,0x802933a,0x80291e0,0x80292dc,0x80294ca,
         0x80294ac,0x802968e,0x80296b0,0x80295e4,0x8029626,0x8029344,
         0x8029528,0x80295ba,0x803baa2,0x803ba78,0x803ba96,
         0x8048daa,0x8049a66,0x8049a80,0x8051b54,0x8049a1c,
         0x80395bc,0x8051b80,0x8049c34}
WINDOWS=[(0x8029190,0x8029200),(0x80292dc,0x8029626),(0x8029626,0x802966e),
         (0x8029680,0x80296de),(0x803b9d4,0x803bae2),(0x80233de,0x802343a),
         (0x8051b54,0x8051b80),(0x8048d68,0x8048e60),(0x8049a1c,0x8049c16),
         (0x8049c34,0x8049c52),(0x8051b80,0x8051b9e),(0x80395e0,0x80395fe),
         (0x80395bc,0x803960a),(0x803cc20,0x803cc58),(0x805bfc0,0x805bfe0),
         (0x80219e8,0x8021a90),(0x802191c,0x8021964),(0x80217b4,0x8021872),
         (0x8021be4,0x8021c48),(0x8021c48,0x8021d04),(0x8021de0,0x8021e98),
         (0x805c00c,0x805c014),(0x801a79c,0x801a7fa),
         (0x805b590,0x805b5b0),(0x80596c4,0x805973c),(0x805b990,0x805b9bc)]


def collect(out):
    out=out.resolve();base=(ROOT/'builds/phase19c-hostwrite').resolve()
    if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh phase19c-hostwrite child required')
    _,protected=verify_inputs();b=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    manifest=json.loads((ROOT/'firmware/dsp/build-4486/manifest.json').read_text())
    data=[(int(x['source_offset'],16),int(x['source_offset'],16)+x['stream_size']) for x in manifest['blocks']]
    cs=engine();from capstone.arm import ARM_OP_IMM
    calls=[]
    for off in range(0,len(b)-3,2):
        if any(a<=off<c for a,c in data):continue
        for i in cs.disasm(b[off:off+4],BASE+off,count=1):
            if i.mnemonic.startswith(('b','cb')):
                imm=[x.imm for x in i.operands if x.type==ARM_OP_IMM]
                if imm and imm[-1] in TARGETS:
                    calls.append(dict(PC=i.address,target=imm[-1],raw=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str,
                        scope='Targeted canonical-halfword edge candidate; inbound/ancestry/data classification required'))
    out.mkdir(parents=True)
    def emit(n,v):
        with (out/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
    emit('targeted-calls.json',calls)
    emit('literal-references.json',{hex(a):[BASE+i for i in range(len(b)-3) if b[i:i+4]==struct.pack('<I',a)]
        for a in [0x20003d00,0x20003cfc,0x20003d04,0x20000314,0x20000000]})
    instructions=[]
    with (out/'arm-windows.asm').open('x',encoding='utf-8',newline='\n') as f:
        for lo,hi in WINDOWS:
            f.write(f'; reviewed boundary/window {lo:08X}..{hi:08X}; linear decode may include data\n')
            for i in cs.disasm(b[lo-BASE:hi-BASE],lo):
                x=dict(PC=i.address,raw=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str)
                instructions.append(x);f.write(f'{i.address:08X}  {i.bytes.hex():10} {i.mnemonic:10} {i.op_str}\n')
    emit('instructions.json',instructions)
    import capstone
    emit('provenance.json',dict(ARM_BIN_SHA256=sha(b),Capstone_version=capstone.__version__,DSP_boot_data_excluded=data,
        decoder='ARM little endian CortexM Thumb2',scope='Targeted direct-helper/cursor investigation, not broad alias census',
        source_sha256=sha(Path(__file__).read_bytes()),offline=True,firmware_modified=False))
    verify_inputs()
    emit('hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
    print('Targeted edges',len(calls),'windows',len(instructions))
    print('New low-level/special direct edges:',[(hex(x['PC']),hex(x['target'])) for x in calls if x['target'] in [0x80291e0,0x802933a,0x8049a66,0x8049a80,0x8048daa,0x8051b54]])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path)
    collect(p.parse_args().output_dir)
