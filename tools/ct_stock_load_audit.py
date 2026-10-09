#!/usr/bin/env python3
"""Phase 19B1 collector. Exact stock P load; explicitly blocked startup, no CPU exec.

Fresh outputs only, within builds/phase19b. No hardware or network APIs. The
native loader independently checks the payload hash before loading core Memory.
Unknown CPU/RAM state is serialized as unknown, never supplied as zero to DSP.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_HASH = 'b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855'
STREAM_HASH = '449c347018a7f318f6eede928446a341f2d3d7d41eb7f2e18d6c71a90d42efb4'
BIN_HASH = 'b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da'
SYX_HASH = 'bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def canonical(obj):
    return (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=True)+'\n').encode()

def save(d, name, obj):
    with (d/name).open('xb') as f:
        f.write(canonical(obj))

def rows(path, payload):
    result = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        m = re.match(r'P:([0-9A-Fa-f]{6})\s+([0-9A-Fa-f]{6})(?: ([0-9A-Fa-f]{6}))?\s+(.*)', line)
        if not m:
            continue
        pc = int(m[1], 16)
        raw = bytes.fromhex(m[2]+(m[3] or ''))
        if payload[pc*3:pc*3+len(raw)] != raw:
            raise ValueError(f'Static witness byte mismatch at P:{pc:X}')
        result[pc] = dict(PC=pc, words=len(raw)//3, raw=raw.hex(), text=m[4], line=line)
    if not result:
        raise ValueError('No verified disassembly rows')
    return result

def verify_inputs():
    d = ROOT/'firmware/dsp/build-4486'
    paths = {d/'selection0-channel0.payload24.bin':PAYLOAD_HASH,
             d/'selection0-channel0.boot24.bin':STREAM_HASH,
             ROOT/'firmware/circuittracks-firmware-4486.bin':BIN_HASH,
             ROOT/'original/circuittracks-firmware-4486.syx':SYX_HASH}
    for p, expected in paths.items():
        if sha(p.read_bytes()) != expected:
            raise ValueError(f'Input identity mismatch: {p}')
    payload = (d/'selection0-channel0.payload24.bin').read_bytes()
    stream = (d/'selection0-channel0.boot24.bin').read_bytes()
    manifest = json.loads((d/'manifest.json').read_text())
    block = next(b for b in manifest['blocks'] if b['name']=='selection0-channel0')
    assert block['payload_sha256']==PAYLOAD_HASH and block['stream_sha256']==STREAM_HASH
    assert block['word_count']==10846 and block['load_word_address']=='0x000000'
    assert len(payload)==32538 and len(stream)==32544
    assert int.from_bytes(stream[:3],'big')==10846 and int.from_bytes(stream[3:6],'big')==0
    assert stream[6:]==payload
    assert (ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()[0x1f0:0x8110]==stream
    return payload, paths

def state_manifest():
    fields = {}
    def field(name, reset, emu, handoff, evidence, initializes=None):
        fields[name] = dict(documented_reset=reset, emulator_constructor=emu,
                            stock_handoff=handoff, evidence=evidence,
                            firmware_initializes_before_use=initializes)
    field('PC','0xFFFFFE for device SHI reset vector','0x000000',0,
          'DSP56724RM tables 5-3/5-5; stock P:0 JMP 0x100. Post-load entry, not reset entry.')
    field('SR','0xC00300 (DSP56724RM figure 5-2)','0xC00300',None,
          'Reset is documented; ROM handoff preservation and pending interrupts are UNRESOLVED.',
          'CCR updated by P:100/101; compare 104. P:109 ORI MR sets mask; 10A sets RM. LF/FV not cleared here.')
    field('OMR','0x000300 | mode-pin nibble (DSP56724RM figure 5-1)','0x000000',None,
          'DSP56724RM figure 5-1/table 5-1. Bootstrap changes bits 7/22/21 BEFORE ROM re-entry; complete post-ROM value unproved.')
    field('SP','0',0,None,'DSP56300FM 2.3.3 / 5.4.3.1','P:107 = 0 before JSR 10F')
    field('SC','0',0,None,'DSP56300FM 2.3.3 / 5.4.3.2','P:108 = 0 before JSR 10F')
    field('SSH/SSL','UNRESOLVED contents; empty stack does not imply zero cells','16 zero implementation stack cells',None,
          'DSP56300FM 5.4.2/5.4.3; no documented reset data value established.')
    field('R0-R7','UNRESOLVED; not specified by cited reset sequence',[0]*8,None,
          'AGU chapter 4; library resetHW explicitly sets zero.', 'R0 loaded at P:10B before 10D; other first uses require audit if reached.')
    field('N0-N7','UNRESOLVED; not specified by cited reset sequence',[0]*8,None,
          'AGU 4.3.3; library resetHW explicitly sets zero.')
    field('M0-M7','0xFFFFFF each',['0xFFFFFF']*8,None,
          'DSP56300FM 2.3.3 and 4.3.4','P:2779..2781 sets all to 0x00FFFF before clear, if reached.')
    for n in ['A','B','X0/X1','Y0/Y1','LA','LC']:
        field(n,'UNRESOLVED; no reset numeric value established',0,None,
              'Implementation constructor zero; not stock provenance.',
              'A fully loaded at P:102 before 104; live LA/LC use requires SR loop state.' if n=='A' else None)
    field('VBA','0',0,None,'DSP56300FM 2.3.3/5.4.4.4; post-ROM persistence unproved')
    field('SZ','Not initialized','0xBADBAD sentinel',None,'DSP56300FM 5.4.3.3')
    field('EP','Not initialized',0,None,'DSP56300FM 4.3.2')
    return dict(status='UNRESOLVED handoff; execution gate CLOSED', fields=fields,
                stock_CPU_instantiated=False, executed_instructions=0,
                entry=0, startup_branch_target=0x100,
                pending_interrupts=None, peripheral_state=None,
                bootstrap_pre_ROM_OMR=dict(set_bits=[7,22],clear_bits=[21],
                    formula='(OMR_before | 0x400080) & ~0x200000',
                    post_ROM_preservation='UNRESOLVED'),
                instruction_limit=0, instruction_limit_reason='Closed handoff gate; no execution API in load-only tool',
                conditional_hardware_profile=dict(P_end=0x4000,X_end=0x6000,Y_end=0x4000,
                    status='SOURCE-DERIVED conditional DSP56724/core0 mode; not a verified board map'),
                watches=[dict(space='X',start=0x35f,end=0x360),
                         dict(space='X',start=0x340,end=0x360),
                         dict(space='X',start=0x5f00,end=0x6000)])

def run(exe, out):
    payload, protected = verify_inputs()
    out = out.resolve()
    if not out.is_relative_to((ROOT/'builds/phase19b').resolve()) or out.exists():
        raise ValueError('Fresh output under builds/phase19b required')
    # Check the unchanged Phase 19A source boundary before using its Memory API.
    audit = subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
        '--results',str(ROOT/'builds/phase19a/validated/results.json'),
        '--output',str(out.parent/(out.name+'-source-audit.json'))],capture_output=True,text=True)
    if audit.returncode:
        raise ValueError(audit.stderr+audit.stdout)
    p = subprocess.run([str(exe),str(ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin'),str(out)],
                       capture_output=True,text=True)
    if p.returncode:
        raise ValueError(p.stderr+p.stdout)
    native = json.loads((out/'native-load-report.json').read_text())
    assert native['stock_instructions_executed']==0 and native['words']==10846
    assert (out/'P.loaded24.bin').read_bytes()==payload
    transactions = [json.loads(l) for l in (out/'load-transactions.jsonl').read_text().splitlines()]
    assert len(transactions)==10846
    for i,t in enumerate(transactions):
        assert t==dict(actor='LOADER',space='P',address=i,old=None,
                       value=int.from_bytes(payload[3*i:3*i+3],'big'),seq=i)
    static = rows(ROOT/'builds/phase3-selection0-channel0.asm',payload)
    # The native decoder reads actual bus-loaded P words. No interpreter trace.
    loaded = rows(out/'loaded-vectors-startup.asm',payload)
    expected_pcs={0,0x3e,0x44,0x100,0x101,0x102,0x104,0x106,0x107,0x108,0x109,0x10a,0x10b,0x10d,0x10f,0x111}
    assert set(loaded)==expected_pcs
    for pc,r in loaded.items():
        assert r['raw']==static[pc]['raw'] and r['words']==static[pc]['words'], (pc,r,static[pc])
    for pc,target in [(0,0x100),(0x3e,0x1b4),(0x44,0x156),(0x106,0x102)]:
        assert f'func_{target:06x}' in loaded[pc]['text'], (pc,loaded[pc])
    assert payload[:3].hex()=='0c0100'
    assert payload[0x3e*3:0x40*3].hex()=='0bf0800001b4'
    assert payload[0x44*3:0x46*3].hex()=='0bf080000156'
    save(out,'immutable-load-manifest.json',dict(status='TESTED MATCH',artifact='firmware/dsp/build-4486/selection0-channel0.payload24.bin',
         payload_bytes=len(payload),payload_words=10846,stream_header_words=2,load_start=0,load_end=0x2a5e,
         encoding='BE24',source_SHA256=PAYLOAD_HASH,stream_SHA256=STREAM_HASH,
         source_BIN_offset=0x1f6,source_header_offset=0x1f0,emulator_loaded_SHA256=sha((out/'P.loaded24.bin').read_bytes()),
         immutable_source='const input bytes; read-only file stream; source pre/post hashes',
         runtime_P_writes=0,runtime_P_logging='NOT REACHED; executable exposes loading only, not runtime',
         load_transactions=10846,header_excluded=True,core_memory_API_readback_equal=True,
         stock_CPU_constructed=False,worker_loaded=False))
    state=state_manifest(); save(out,'initial-state-manifest.json',state)
    cpu=dict(status='NOT EXECUTED; partially specified stock entry, not a real final CPU snapshot',
             PC=0,stock_instructions_executed=0,
             registers={n:None for n in state['fields'] if n!='PC'},pending_interrupts=None)
    save(out,'CPU.final.tagged.json',cpu)
    for space,end in [('P',0x4000),('X',0x6000),('Y',0x4000)]:
        save(out,space+'.state.tagged.json',dict(space=space,
             status='Load-only initializedness representation; not a concrete final stock RAM image',
             profile_end_conditional=end,
             known_ranges=([dict(start=0,end=0x2a5e,BE24_file='P.loaded24.bin',SHA256=PAYLOAD_HASH)] if space=='P' else []),
             unknown_ranges=[dict(start=0x2a5e if space=='P' else 0,end=end)],
             unknown_reads='DENIED',extra_Y_clear_addresses='UNRESOLVED, not provisioned as RAM' if space=='Y' else None))
    gate=dict(status='BLOCKED BEFORE EXECUTION',actual_PC=None,attempted_instructions=0,executed_instructions=0,
              runtime_faults=[],anticipated_first_peripheral=dict(PC=0x100,space='Y',address=0xfffffa,operation='BCLR read/modify/write'),
              reason='Post-ROM SR/OMR/live control state and GPIO/interrupt handoff not defensible; no guessed reset profile applied',
              anticipated_worker=dict(PC=0x102,space='Y',address=0xffffd4,expected=0x030002,
                 status='UNRESOLVED required model, NOT REACHED',source='Other-core ICDR3; worker static P:109 writes Y:FFFFD7'),
              later_blockers=['Y:[0x4000,0x6000) clear vs conditional RAM map','EMC setup/external reads',
                              'Host-table readiness X:FFF and X:193F','Interrupt peripheral/event fidelity'],
              stock_execution_mismatches=[],
              reset_profile_differences=[
                  dict(register='PC',documented_SHI_reset=0xfffffe,emulator_constructor=0,status='MISMATCH if constructor reused as chip reset'),
                  dict(register='OMR CDP[1:0]',documented_reset=3,emulator_constructor=0,status='MISMATCH for DSP56724-compatible reset profile')],
              execution_differential='NOT REACHED',phase19c='Justified as separately authorized handoff/peripheral contract work; not automatically started')
    save(out,'mismatch-fault-report.json',gate)
    save(out,'decode-validation.json',dict(status='MATCH opcode bytes, instruction lengths and four direct targets',
         count=len(loaded),rows=list(loaded.values()),execution_comparison='NOT REACHED'))
    facts=[]
    for name,pcs,expect in [
        ('private X/Y clear',[0x2779,0x2786,0x2788,0x2789],'24576 writes each, X[i] then Y[i], R0 advanced by Y store; INIT'),
        ('shared X clear',[0x278f,0x2791],'32768 words X:[0x30000,0x38000); INIT'),
        ('modifiers',[0x2779,0x277b,0x2781],'M0..7 = 0x00FFFF'),
        ('cursor families',[0x260a,0x260c,0x260e,0x2610,0x2614,0x2616,0x2618,0x261a],
         'Y:1820..182F alternating 2CCC/2CEC; Y:1A10..1A1F alternating 2C02/2C24'),
        ('descriptors',[0x27f8,0x2644],'Existing static descriptor initialization, exact runtime validation pending'),
        ('SHI setup',[0x25dd,0x25f2],'X:FFFFBD bit 9 before/after initialization; chip semantics not modeled'),
        ('interrupt unmask',[0x25f1],'ANDI FC,MR after init; pending event/state must be justified before replay'),
    ]:
        facts.append(dict(name=name,expected=expect,result='NOT REACHED',
                          byte_verified_witnesses=[static[pc] for pc in pcs]))
    copies=json.loads((ROOT/'firmware/dsp/reconstructed-4486/manifest.json').read_text())['table_copies']
    for copy in copies:
        src=int(copy['source'].split('0x')[1],16)
        b=payload[src*3:(src+copy['words'])*3]
        assert sha(b)==copy['sha256']
        facts.append(dict(name='P-to-X table copy',expected=copy,result='NOT REACHED',source_table_hash_checked=True))
    save(out,'startup-expectations.json',facts)
    ranges=[(0,1),(0x3e,0x40),(0x44,0x46),(0x100,0x113),(0x25db,0x262c),(0x2644,0x264a),
            (0x2779,0x27af),(0x27f8,0x2808)]
    witness='\n'.join(r['line'] for pc,r in static.items() if any(lo<=pc<hi for lo,hi in ranges))+'\n'
    with (out/'static-startup-witnesses.asm').open('xb') as f:f.write(witness.encode())
    probe=json.loads((out/'emulator-reset-probe.json').read_text())
    assert probe['PC']==probe['OMR']==probe['SP']==probe['SC']==0
    assert probe['SR']==0xc00300 and probe['M']==[0xffffff]*8
    assert probe['R']==probe['N']==[0]*8
    trace=[dict(type='LOAD_VERIFIED',stock_instructions_executed=0,words=10846,SHA256=PAYLOAD_HASH),
           dict(type='STARTUP_GATE_BLOCKED',stock_instructions_executed=0,entry=0,reason=gate['reason'])]
    with (out/'canonical-trace.jsonl').open('xb') as f:
        for event in trace:f.write((json.dumps(event,sort_keys=True,separators=(',',':'))+'\n').encode())
    for name in ['execution-trace.jsonl','runtime-transactions.jsonl','runtime-watch.jsonl']:
        (out/name).open('xb').close()
    # No generated manifest hashes itself. Metadata changes do not alter RAM provenance.
    files={p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()}
    save(out,'hashes.json',dict(scope='Load reports/readback plus tagged unknown state. Empty execution != passing startup replay.',files=files))
    verify_inputs()
    save(out,'validation.json',dict(status='TESTED PASS load-only; STARTUP BLOCKED',load_equal=True,
         hashes_unchanged={p.relative_to(ROOT).as_posix():h for p,h in protected.items()},
         core_guard_passed=True,load_transactions_verified=True,decode_matches=16,
         unknown_read_guards=3,stock_instructions=0,stock_execution_success=False,
         loaded_memory_determinism='Compare with independent repeat; not execution determinism',
         executable_SHA256=sha(exe.read_bytes()),
         source_hashes={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in
             [ROOT/'emulator/stock/main.cpp',ROOT/'emulator/stock/build.ps1',ROOT/'emulator/stock/CMakeLists.txt',Path(__file__)]}))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--exe',required=True,type=Path)
    ap.add_argument('--output-dir',required=True,type=Path)
    a=ap.parse_args()
    run(a.exe.resolve(),a.output_dir)
    print('TESTED load-only PASS; stock startup BLOCKED; 0 stock instructions')
