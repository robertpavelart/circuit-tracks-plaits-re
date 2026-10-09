#!/usr/bin/env python3
"""Export reviewed static voice-path evidence; never execute firmware or open devices.

The address formulas are analyst reconstructions, not a recovered symbol file.
DSP excerpts must match the extracted payload's raw words. Existing reports and
original/ are protected by exclusive-create output handling.
"""
import argparse
import json
import re
from pathlib import Path
from ct_static import ROOT, BASE, BIN_HASH, SYX_HASH, sha, save
import ct_fw_tool

DSP_RANGES = [(0x156,0x1b4),(0x1d9,0x281),(0x281,0x758),
              (0x77f,0xaA8),(0x198d,0x19f3),(0x1bb3,0x1be8),
              (0x2881,0x28ac)]
ARM_REPORTS = ['phase4-arm-events.asm', 'phase4-arm-inputs.asm',
               'phase4-arm-slot-note.asm', 'phase4-arm-scaling.asm',
               'phase4-arm-note-writer.asm', 'phase4-arm-release.asm',
               'phase3-arm-note-params.asm', 'phase3-arm-params.asm',
               'phase4-arm-noteon-tail.asm']

def dsp_evidence(path, payload):
    result=[]
    for line in path.read_text().splitlines():
        m=re.match(r'P:([0-9A-F]{6})  ([0-9A-F]{6})(?: ([0-9A-F]{6}))?\s+(.*)',line)
        if not m: continue
        pc=int(m[1],16)
        if not any(start<=pc<end for start,end in DSP_RANGES): continue
        raw=bytes.fromhex(m[2]+(m[3] or ''))
        if payload[pc*3:pc*3+len(raw)]!=raw:
            raise ValueError(f'Disassembly bytes disagree at P:{pc:06X}')
        result.append(line)
    return result

def arm_evidence(path, binary):
    count=0
    for line in path.read_text().splitlines():
        m=re.match(r'([0-9A-F]{8})  ([0-9a-f]+)\s+',line)
        if not m: continue
        address=int(m[1],16); raw=bytes.fromhex(m[2])
        if binary[address-BASE:address-BASE+len(raw)]!=raw:
            raise ValueError(f'ARM report bytes disagree at {address:08X}')
        count+=1
    return count

def velocity_scale(event_level, depth, tracking=0xffff):
    """Reviewed integer expressions at ARM 0x0802192C and 0x08027D9A.

    depth is the unsigned parameter byte; positive depth-64 scales the envelope
    target upward with event level. tracking is helper 0x080284DE's result.
    This evaluates a formula only, not DSP/ARM firmware instructions.
    """
    if not 0<=event_level<=127 or not 0<=depth<=127:
        raise ValueError('Seven-bit event/parameter inputs required')
    q=(event_level*event_level)>>7
    d=depth-64
    v=q if d>=0 else q^127
    product=abs(d)*(v-127)
    factor=0x7f00+(0xff if product==0 else product*4)
    return dict(event_level=event_level, squared_level=q, sensitivity=depth,
                tracking=tracking, factor=factor,
                dsp_envelope_target=(tracking*factor & 0xffffffff)>>8)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',required=True)
    p.add_argument('--dsp-asm',default=str(ROOT/'builds/phase3-selection0-channel0.asm'))
    a=p.parse_args()
    out=Path(a.output_dir).resolve()
    if out.exists(): raise SystemExit('Choose a fresh output directory')
    if out==ROOT/'original' or ROOT/'original' in out.parents:
        raise SystemExit('Protected original/ destination')
    binary=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    syx=(ROOT/'original/circuittracks-firmware-4486.syx').read_bytes()
    if sha(binary)!=BIN_HASH or sha(syx)!=SYX_HASH:
        raise SystemExit('Source integrity failure')
    # Established codec baseline, all in memory.
    syx_path=ROOT/'original/circuittracks-firmware-4486.syx'
    decoded=ct_fw_tool.decode_syx(syx_path)
    raw=decoded['firmware']
    if raw!=binary: raise ValueError('Decoded image differs')
    if ct_fw_tool.build_syx(syx_path,raw)!=syx:
        raise ValueError('Roundtrip differs')
    payload=(ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin').read_bytes()
    if sha(payload)!='b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855':
        raise SystemExit('DSP payload integrity failure')
    lines=dsp_evidence(Path(a.dsp_asm),payload)
    pc_lines={int(l[2:8],16):l for l in lines}
    for pc,fragment in [(0x282,'x:(r3),x1'),(0x29d,'x:(r7),y1'),
                        (0x2c7,'jclr #7,y1'),(0x5c1,'y:(r6)+,x0'),
                        (0x5cb,'a,y:(r4)'),(0x6a7,'y:(r5+4),y0'),
                        (0x7e9,'x:(r0)+,y0'),(0x7f1,'add y0,a'),
                        (0xa91,'mac +y0,x0,a'),(0x19ac,'jsr (r1)')]:
        if fragment not in pc_lines.get(pc,''): raise ValueError(f'Missing reviewed DSP anchor {pc:X}')
    reports=[]
    for name in ARM_REPORTS:
        path=ROOT/'builds'/name
        reports.append(dict(file=name,sha256=sha(path.read_bytes()),
                            raw_instruction_rows_checked=arm_evidence(path,binary)))
    slots=[]
    for i in range(12):
        slots.append(dict(slot=i, arm_state=f'0x{0x20005f64+16*i:08X}',
            descriptor_X=f'0x{0xeb+8*i:X}',entry_words=8,
            initialized_pointers=dict(function_P='0x281',kernel_X=f'0x{0x1960+12*i:X}',
                control_Y=f'0x{0x11f+0x60*i:X}',envelope_Y=f'0x{0x131+0x60*i:X}',
                event_X=f'0x{0x57a+0x4a*i:X}',sample_state_Y=f'0x{0x59f+0x28*i:X}'),
            arm_normal_allocation_bank=0 if i<6 else 1,
            bank_field_X=f'0x{0xf2+8*i:X}',
            processed_flags_Y=f'0x{0x122+0x60*i:X}',
            primary_level_Y=f'0x{0x130+0x60*i:X}',
            current_note_Y=f'0x{0x12f+0x60*i:X}',
            note_target_Y=f'0x{0x159+0x60*i:X}',
            level_target_Y=f'0x{0x14d+0x60*i:X}'))
    examples=[velocity_scale(v,127) for v in (0,32,64,96,127)]
    assert [r['dsp_envelope_target'] for r in examples]==sorted(r['dsp_envelope_target'] for r in examples)
    assert velocity_scale(0,64)['factor']==velocity_scale(127,64)['factor']==0x7fff
    manifest=dict(status='reviewed static evidence; not runtime execution',
        original_syx_sha256=sha(syx),arm_bin_sha256=sha(binary),dsp_payload_sha256=sha(payload),
        decoded_syx_equals_bin=True,roundtrip_byte_identical=True,
        checked_dsp_instruction_rows=len(lines),arm_reports=reports,
        slots=slots,velocity_formula_examples=examples,
        unresolved=['Exact external MIDI event classification',
                    'Branch-dependent final gain coefficient offset and complete effects topology',
                    'Physical assignment of ARM transport channels to DSP cores',
                    'Runtime observation and exact Hz/sample rate calibration'])
    # No outputs exist until every evidence check succeeds.
    out.mkdir(parents=True,exist_ok=False)
    save(out/'trace.json',json.dumps(manifest,indent=2)+'\n')
    save(out/'dsp-voice-path.asm','\n'.join(lines)+'\n')
    print(json.dumps(dict(output=str(out),slots=len(slots),dsp_rows=len(lines),
                          arm_rows=sum(r['raw_instruction_rows_checked'] for r in reports)),indent=2))

if __name__=='__main__': main()
