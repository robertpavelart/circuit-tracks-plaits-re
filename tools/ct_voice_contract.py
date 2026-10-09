#!/usr/bin/env python3
"""Reviewed address accounting and loop-count evidence, not a DSP emulator.

Reads only firmware/disassembly. No device APIs, no firmware execution. Paths
and repetitions below are explicit analyst-selected static witnesses; unknown
branch flags and runtime preset contents are never silently simulated.
"""
import argparse, json, re, struct
from pathlib import Path
from ct_static import ROOT, BASE, BIN_HASH, SYX_HASH, sha, save
from ct_phase4_trace import arm_evidence
import ct_fw_tool

RANGES=[(0x100,0x156),(0x1b4,0x281),(0x281,0x4d5),(0x759,0xcb8),
        (0x198d,0x19f3),(0x1c53,0x1dda),(0x2644,0x267b),
        (0x27f8,0x281b),(0x2881,0x28ac),(0x2a2d,0x2a5e)]
ARM=['phase5-arm-patch-level.asm','phase5-arm-pitch-table.asm',
     'phase5-arm-gain-transfer.asm','phase5-arm-wave-pointers.asm',
     'phase5-arm-wave-base.asm','phase4-arm-bank-gain.asm',
     'phase3-arm-transport.asm','phase3-arm-table-upload.asm']

def load_asm(path,payload):
    rows={}; evidence=[]
    for line in path.read_text().splitlines():
        m=re.match(r'P:([0-9A-F]{6})  ([0-9A-F]{6})(?: ([0-9A-F]{6}))?\s+(.*)',line)
        if not m: continue
        pc=int(m[1],16)
        rows[pc]=dict(pc=pc,text=m[4],line=line)
        if any(a<=pc<b for a,b in RANGES):
            raw=bytes.fromhex(m[2]+(m[3] or ''))
            if payload[3*pc:3*pc+len(raw)]!=raw:
                raise ValueError(f'Raw words disagree at P:{pc:X}')
            evidence.append(line)
    return rows,evidence

def increment_sites(rows,lo,hi,register='r7'):
    return [pc for pc,r in rows.items() if lo<=pc<hi and f'x:({register})+' in r['text']]

def account(rows):
    # Both alternatives emit exactly three words between P:0x419..459.
    prefix=increment_sites(rows,0x3a0,0x419)
    suffix=increment_sites(rows,0x459,0x46e)
    paths={name:prefix+increment_sites(rows,a,b)+suffix
           for name,a,b in [('flag0_clear',0x44c,0x459),('flag0_set',0x41c,0x44c)]}
    assert all(len(v)==14 for v in paths.values())
    ptr=0x57b; producers=[]
    for lane in range(3):
        for pc in paths['flag0_clear']:
            producers.append(dict(site=f'P:0x{pc:X}',lane=lane,address=f'X:0x{ptr:X}',instruction=rows[pc]['text']))
            ptr+=1
    # DO #3 at P:0x470 repeats the pair of reads, advancing by six words.
    for repeat in range(3):
        for pc in increment_sites(rows,0x472,0x47c):
            producers.append(dict(site=f'P:0x{pc:X}',address=f'X:0x{ptr:X}',instruction=rows[pc]['text']))
            ptr+=1
    for pc in increment_sites(rows,0x47c,0x4d5):
        producers.append(dict(site=f'P:0x{pc:X}',address=f'X:0x{ptr:X}',instruction=rows[pc]['text']))
        ptr+=1
    assert ptr==0x5bf
    emitted={r['site']:r['address'] for r in producers if 'lane' not in r}
    assert emitted['P:0x4C7']=='X:0x5BB'
    assert emitted['P:0x4D0']=='X:0x5BC'
    assert emitted['P:0x4D1']=='X:0x5BD'
    assert emitted['P:0x4D3']=='X:0x5BE'
    # BDD and AA8 consume seven coefficient words, including its callees.
    reads=increment_sites(rows,0xaa8,0xbdd,'r0')+increment_sites(rows,0xbdd,0xc2d,'r0')
    assert reads==[0xaa8,0xaa9,0xbdf,0xbec,0xbf3,0xc10,0xc1a]
    assert 'r0+8' in rows[0xa1f]['text']
    consumers=[dict(stage='after three records',r0='X:0x5A5'),
               dict(stage='after six coefficient ramps',r0='X:0x5AB'),
               dict(stage='after mode word',r0='X:0x5AC'),
               dict(stage='after BDD seven reads',r0=f'X:0x{0x5ac+len(reads):X}'),
               dict(stage='after A1F +8',r0=f'X:0x{0x5ac+len(reads)+8:X}'),
               dict(stage='A7F n6',address='X:0x5BB'),
               dict(stage='A8A ramp delta',address='X:0x5BC'),
               dict(stage='A8D current gain (updated each sample)',address='X:0x5BD')]
    return producers,consumers,reads

def counts(rows,n=32,repetitions=1):
    # Issued instructions in selected loop BODIES; extension words aren't instructions.
    # No call expansion except the explicit C9D loop body; no wait-time bound.
    assert 'do x:$003c' in rows[0x80e]['text']
    assert 'do x:$003c' in rows[0x83b]['text']
    specifications=[
      ('phase progression, both passes',0x7f1,0x7f3,6*repetitions*n),
      ('first-pass address interpolation loop (X:3C=N-1)',0x810,0x816,3*repetitions*(n-1)),
      ('second-pass absolute-value loop',0x826,0x82b,3*repetitions*(n//2)),
      ('second-pass lookup result arithmetic (X:3C=N-1)',0x83d,0x846,3*repetitions*(n-1)),
      ('six coefficient ramps',0x9b3,0x9b5,6*n),
      ('three-lane numerical combination',0x9c8,0x9d9,n),
      ('AA8 mode-zero ramp table',0xaff,0xb01,n),
      ('AA8 nonzero normalization branch',0xb0c,0xb22,n),
      ('BDD input scaling',0xbe6,0xbe8,n),
      ('two recursive C9D calls',0xca6,0xcb0,2*(n//2)),
      ('group gain accumulation',0xa8d,0xa95,n)]
    result=[]
    for name,lo,hi,times in specifications:
        body=[p for p in rows if lo<=p<hi]
        result.append(dict(loop=name,start=f'P:0x{lo:X}',end_exclusive=f'P:0x{hi:X}',
                           body_instructions=len(body),iterations=times,issued_instructions=len(body)*times))
    return dict(profile='three address-mask >=8 lanes, nonzero Q+3, Q+4=0, one repeat each; post mode=0, AA8 normalization branch active',
                samples=n,loops=result,subtotal=sum(r['issued_instructions'] for r in result),
                worker_fetch_body_per_word=6,queued_words=3*repetitions*2*n,
                worker_fetch_body_instructions=6*3*repetitions*2*n,
                caveat='Selected major-loop subtotal only: excludes setup, calls, control preparation, interrupts, wait repetitions and pipeline/memory cycles. Not a worst-case bound or headroom estimate.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',required=True)
    p.add_argument('--dsp-asm',default=str(ROOT/'builds/phase3-selection0-channel0.asm'))
    a=p.parse_args();out=Path(a.output_dir).resolve()
    if out==ROOT/'original' or ROOT/'original' in out.parents: raise SystemExit('Protected original/')
    if out.exists(): raise SystemExit('Choose a fresh output directory')
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    syx_path=ROOT/'original/circuittracks-firmware-4486.syx';syx=syx_path.read_bytes()
    if sha(arm)!=BIN_HASH or sha(syx)!=SYX_HASH: raise SystemExit('Original integrity failure')
    decoded=ct_fw_tool.decode_syx(syx_path)['firmware']
    assert decoded==arm and ct_fw_tool.build_syx(syx_path,decoded)==syx
    payload=(ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin').read_bytes()
    assert sha(payload)=='b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855'
    rows,evidence=load_asm(Path(a.dsp_asm),payload)
    producers,consumers,reads=account(rows)
    reports=[dict(file=n,instructions_checked=arm_evidence(ROOT/'builds'/n,arm)) for n in ARM]
    # Exact upper-24-bit table upload at ARM 0x08029430, 0x340 entries.
    flash=0x08052bb4; count=0x340
    table=b''.join((struct.unpack_from('<I',arm,flash-BASE+4*i)[0]>>8).to_bytes(3,'big') for i in range(count))
    waveinfo=payload[0x28e4*3:0x28eb*3] # waveform index 1, Y:E37 from startup copy
    assert int.from_bytes(waveinfo[-3:],'big')==0x1fff
    result=dict(status='static reviewed contract and pointer accounting, not firmware execution',
       syx_sha256=sha(syx),bin_sha256=sha(arm),roundtrip_byte_identical=True,
       dsp_instruction_rows_checked=len(evidence),arm_reports=reports,
       selected_slot=0,descriptor_X='0xEB',control_Y='0x11F',secondary_Y='0x131',
       event_X='0x57A',coefficients_X='0x57B',sample_state_Y='0x59F',
       lane_modes_Y=['0x59F','0x5A1','0x5A3'],lane_phase_Y=['0x5A0','0x5A2','0x5A4'],
       bank_parameters_X='0x296',bank_intermediates_Y='0x7C',bank_sum_X='0x2DF0',
       component_word_stride=14,coefficient_producers=producers,gain_consumers=consumers,
       bdd_coefficient_read_sites=[f'P:0x{v:X}' for v in reads],
       block_counts=dict(X38='0x50',X39=5,X3A=32,X3B=16,X3C=31,X3D=15,X3E=64,X3F=96,X40=0),
       budget=counts(rows),
       table_export=dict(arm_source=f'0x{flash:X}',destination='X:[0x1600,0x1940)',words=count,sha256=sha(table)),
       waveform_index_1_info=dict(P='0x28E4',Y='0xE37',words=[int.from_bytes(waveinfo[i:i+3],'big') for i in range(0,21,3)]),
       mono_seam=dict(entry_P='0x9DD',samples_X='[0x2C46,0x2C66)',words=32,r0='0x5AB',r4='0x5AB',
                      note='r0 is X coefficient pointer; r4 is Y state pointer. Other downstream shared state remains required.'),
       unresolved=['Complete concrete runtime preset snapshot','Exact sample rate and DSP clock',
                   'Cycle budget/headroom','Absolute sample normalization','Complete table footprints for arbitrary parameters'])
    out.mkdir(parents=True,exist_ok=False)
    save(out/'contract.json',json.dumps(result,indent=2)+'\n')
    save(out/'dsp-output-path.asm','\n'.join(evidence)+'\n')
    save(out/'X-001600-001940.table24.bin',table)
    save(out/'Y-000E37-000E3E.waveinfo24.bin',waveinfo)
    print(json.dumps(dict(output=str(out),loop_subtotal=result['budget']['subtotal'],dsp_rows=len(evidence)),indent=2))

if __name__=='__main__': main()
