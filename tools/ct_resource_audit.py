#!/usr/bin/env python3
"""Static build-4486 resource inventory, not execution or a free-RAM proof.

Candidate CFG follows decoded direct edges and reviewed indirect-target seeds.
Unknown indirect transfers remain explicit. Literal pointer and absolute-access
inventories are not exhaustive points-to analysis, and unreferenced is not free.
"""
import argparse,csv,io,json,re,struct
from collections import deque
from pathlib import Path
from ct_static import ROOT,BASE,BIN_HASH,SYX_HASH,sha,save
from ct_voice_contract import counts
from ct_phase4_trace import arm_evidence
import ct_fw_tool

REGIONS=[
 ('P',0,0x100,'vector area','VERIFIED loaded; vectors/reserved entries'),
 ('P',0x100,0x2a5e,'mixed code/constants','VERIFIED loaded; candidate CFG separate'),
 ('P',0x262c,0x2644,'copied constants','VERIFIED P-to-X startup copies'),
 ('P',0x268c,0x2717,'copied constants','VERIFIED P-to-X startup copy'),
 ('P',0x2720,0x2779,'templates','VERIFIED startup MOVEM loops'),
 ('P',0x28dd,0x29ec,'wave/filter info constants','VERIFIED P-to-Y startup copy'),
 ('P',0x29f6,0x2a2d,'indirect code pointers','VERIFIED copied to X:9DB'),
 ('P',0x2a5e,0x4000,'unloaded candidate tail','POTENTIALLY AVAILABLE, conditional DSP56724/core0/OMR map'),
 ('X',0,0xeb,'global protocol/control','VERIFIED mixed state, not all fields named'),
 ('X',0xeb,0x15b,'dispatch descriptors','VERIFIED twelve voice and two other entries'),
 ('X',0x15b,0x57a,'parameters and globals','VERIFIED bank bases; full bounds interpretation partial'),
 ('X',0x57a,0x8f2,'twelve voice coefficient/state blocks','VERIFIED 12*0x4A words'),
 ('X',0x8f2,0xc00,'other state/tables','VERIFIED references; detailed ownership partial'),
 ('X',0xc00,0x1000,'host table/mailbox staging','VERIFIED 0x400 startup copy; later table jobs'),
 ('X',0x1000,0x1400,'audio ring','VERIFIED ISR reads and output writes; mirrors Y input ring'),
 ('X',0x1400,0x1600,'shared scratch/table work','VERIFIED overlapping transform/ramp routines'),
 ('X',0x1600,0x1940,'filter coefficients','VERIFIED 832-word ARM upload'),
 ('X',0x1940,0x1960,'global/kernel state','VERIFIED pointer use; full layout partial'),
 ('X',0x1960,0x1a80,'per-voice kernels','VERIFIED 12*0xC words; dynamic transforms'),
 ('X',0x1a80,0x2000,'templates/global sample/output state','VERIFIED multiple routines; detailed boundaries partial'),
 ('X',0x2000,0x2200,'frequency table','VERIFIED 512 ARM-generated words'),
 ('X',0x2200,0x2400,'normalization table','VERIFIED 512 ARM-generated words'),
 ('X',0x2400,0x2800,'table work','VERIFIED mailbox generator accesses'),
 ('X',0x2800,0x2c00,'host table backup','VERIFIED startup copy'),
 ('X',0x2c00,0x2df0,'scratch/audio/filter work','VERIFIED reused by voice and global paths'),
 ('X',0x2c46,0x2c66,'proposed mono seam','VERIFIED scratch lifetime only; not persistent/free'),
 ('X',0x2df0,0x2f30,'group/global audio buffers','VERIFIED bank sums and other mixes'),
 ('X',0x2f30,0x323d,'scheduler/auxiliary/global state','VERIFIED references; computed extent incomplete'),
 ('X',0x4000,0x6000,'state candidate','POTENTIALLY AVAILABLE only; no non-alias proof'),
 ('Y',0,0x11f,'global state','VERIFIED mixed constants, parameters and protocol state'),
 ('Y',0x11f,0x59f,'voice/control regions','VERIFIED 0x60 strides; boundary overlaps require field-level care'),
 ('Y',0x59f,0x77f,'twelve sample contexts','VERIFIED 12*0x28 words, includes retained post state'),
 ('Y',0x77f,0xa01,'group/effects/global state','VERIFIED references'),
 ('Y',0xa01,0xa61,'interleaved voice scratch','VERIFIED 96 words for N=32'),
 ('Y',0xe30,0xf3f,'wave/filter info constants','VERIFIED 0x10F-word P copy'),
 ('Y',0xf3f,0x1000,'ISR/effects/ring state','VERIFIED references, including pointers FFD/FFE'),
 ('Y',0x1000,0x1400,'audio input ring','VERIFIED init/ISR writes'),
 ('Y',0x1400,0x2000,'other scratch/state','UNRESOLVED detailed ownership'),
 ('Y',0x2000,0x2006,'SHI interrupt saved registers','VERIFIED normal SHI ISR'),
 ('Y',0x2006,0x3000,'effects/audio state','VERIFIED references; complete extents unresolved'),
 ('Y',0x3000,0x4000,'state candidate','POTENTIALLY AVAILABLE only; no non-alias proof'),
 ('Y',0x4000,0x6000,'startup-clear addresses outside conditional RAM map','UNRESOLVED/reserved; not free RAM'),
 ('shared',0x30000,0x34000,'worker queue/service work','VERIFIED starts at 30002; upper reservation conservative, not proven capacity'),
 ('shared',0x34000,0x34003,'worker/service metadata','VERIFIED direct normal accesses; broader ownership partial'),
 ('shared',0x34003,0x38000,'shared candidate','POTENTIALLY AVAILABLE only; computed pointers/host writes unresolved'),
 ('external',0x40000,0xf80000,'external sample/table region','VERIFIED EMC accesses; physical size/timing unresolved'),
 ('peripherals',0xfff000,0x1000000,'I/O and ICC','VERIFIED instruction addresses plus conditional device map'),
]

def read_rows(path,payload):
    rows={}
    for l in path.read_text().splitlines():
        m=re.match(r'P:([0-9A-F]{6})  ([0-9A-F]{6})(?: ([0-9A-F]{6}))?\s+(.*)',l)
        if not m:continue
        pc=int(m[1],16);raw=bytes.fromhex(m[2]+(m[3] or ''))
        if payload[3*pc:3*pc+len(raw)]!=raw:raise ValueError(f'Bad disassembly bytes {pc:X}')
        rows[pc]=dict(pc=pc,words=len(raw)//3,text=m[4],line=l)
    return rows

def candidate_cfg(rows,seeds):
    todo=deque(seeds);visited=set();unresolved=[]
    while todo:
        pc=todo.popleft()
        if pc in visited:continue
        if pc not in rows:
            unresolved.append(dict(pc=f'P:{pc:06X}',reason='no canonical instruction boundary'));continue
        visited.add(pc);r=rows[pc];op=r['text'].split()[0];nxt=pc+r['words']
        if op in ('rts','rti','stop','wait','illegal','dc'):continue
        call=op in ('jsr','bsr','jscs','jscc') or op.startswith(('bscc','bsne','bseq'))
        branch=op.startswith('j') or (op.startswith('b') and op not in ('bset','bclr','bchg','btst'))
        unconditional=op in ('jmp','bra')
        if branch:
            targets=re.findall(r'\$([0-9a-fA-F]+)',r['text'])
            if targets:todo.append(int(targets[-1],16))
            else:unresolved.append(dict(pc=f'P:{pc:06X}',reason='indirect branch/call',instruction=r['text']))
        if not unconditional or call:todo.append(nxt)
    return visited,unresolved

def inventory(rows,visited,program):
    out=[]
    for pc,r in rows.items():
        for m in re.finditer(r'([xyp]):\$([0-9a-fA-F]+)',r['text']):
            out.append(dict(program=program,pc=f'P:{pc:06X}',kind='absolute_operand',space=m[1].upper(),
                            address=int(m[2],16),candidate_reachable=pc in visited,instruction=r['text']))
        for m in re.finditer(r'#(?:>)?\$([0-9a-fA-F]+),(r[0-7])',r['text']):
            out.append(dict(program=program,pc=f'P:{pc:06X}',kind='register_immediate_not_necessarily_pointer',
                            space='unknown',address=int(m[1],16),register=m[2],candidate_reachable=pc in visited,instruction=r['text']))
        if re.search(r'[xy]:[^ ]*\(r[0-7]',r['text']):
            out.append(dict(program=program,pc=f'P:{pc:06X}',kind='indirect_memory_operand',space='unresolved',
                            address=None,candidate_reachable=pc in visited,instruction=r['text']))
    return out

def esai_fields(clock,control):
    return dict(PM=clock&255,PSR=(clock>>8)&1,DC=(clock>>9)&31,FP=(clock>>14)&15,
                CKD=(clock>>21)&1,FSD=(clock>>22)&1,HCKD=(clock>>23)&1,
                SW=(control>>10)&31,MOD=(control>>8)&3,enabled_lines=control&63)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True);a=p.parse_args()
    out=Path(a.output_dir).resolve()
    if out==ROOT/'original' or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    if out.exists():raise SystemExit('Choose a fresh output directory')
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes();syx_path=ROOT/'original/circuittracks-firmware-4486.syx';syx=syx_path.read_bytes()
    assert sha(arm)==BIN_HASH and sha(syx)==SYX_HASH
    decoded=ct_fw_tool.decode_syx(syx_path)['firmware'];assert decoded==arm and ct_fw_tool.build_syx(syx_path,decoded)==syx
    source=ROOT/'firmware/dsp/build-4486'
    payload=(source/'selection0-channel0.payload24.bin').read_bytes()
    assert sha(payload)=='b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855'
    rows=read_rows(ROOT/'builds/phase3-selection0-channel0.asm',payload)
    table=json.loads((ROOT/'firmware/dsp/reconstructed-4486/manifest.json').read_text())['indirect_table']
    seeds=[0,0x156,0x1b4,0x281,0x202b,0x1a2b,0x19be]+[int(t['target'].split('0x')[1],16) for t in table]
    visited,unknown=candidate_cfg(rows,seeds)
    worker_payload=(source/'selection0-channel1.payload24.bin').read_bytes()
    worker=read_rows(ROOT/'builds/phase3-selection0-channel1.asm',worker_payload)
    wvisit,wunknown=candidate_cfg(worker,[0,0x12b])
    inv=inventory(rows,visited,'normal-channel0')+inventory(worker,wvisit,'normal-channel1')
    # Evidence constants are pinned to raw payload words as well as decoded text.
    word=lambda pc:int.from_bytes(payload[pc*3:pc*3+3],'big')
    assert word(0x10c)==0x2028 and 'ffff7d' in rows[0x10d]['text']
    assert word(0x2a40)==0xecc309 and word(0x2a51)==0x817d10
    assert word(0x2a44)==0x0cc30a and word(0x2a53)==0x017d01
    tx=esai_fields(0xecc309,0x817d10);rx=esai_fields(0x0cc30a,0x017d01)
    divider=2*(tx['PM']+1)*(1 if tx['PSR'] else 8)*(tx['FP']+1)*32*(tx['DC']+1)
    assert tx['SW']==31 and tx['MOD']==1 and divider==5120
    rate_constant=struct.unpack_from('<H',arm,0x805bcd0-BASE)[0];assert rate_constant==48047
    budget=counts(rows);assert budget['subtotal']==4355
    references=[r for r in inv if r['address']==0x2c46]
    bootstrap=(source/'bootstrap.payload24.bin').read_bytes()
    assert bootstrap.hex().startswith('0444ba0ac4670ac4760ac45504c4ba')
    audited_arm=[]
    for name in ['phase6-arm-system-init.asm','phase6-arm-rcc-init.asm','phase6-arm-clock-functions.asm','phase3-arm-transport.asm']:
        audited_arm.append(dict(file=name,rows_checked=arm_evidence(ROOT/'builds'/name,arm)))
    program_words=len(payload)//3
    result=dict(status='static audit; no execution; hardware identity/source wiring conditional',
      syx_sha256=sha(syx),bin_sha256=sha(arm),roundtrip_identical=True,arm_reports=audited_arm,
      program_words=program_words,program_end_exclusive=f'P:0x{program_words:X}',
      conditional_internal_capacity=dict(model='DSP56724 core0 with MS=1/MSW1=1/MSW0=0',P=0x4000,X=0x6000,Y=0x4000),
      candidate_program_tail=dict(start=f'P:0x{program_words:X}',end_exclusive='P:0x4000',words=0x4000-program_words,
                                 status='POTENTIALLY AVAILABLE, not a proven deployable extension'),
      pll=dict(value='0x002028',PEN=1,NR=1,NF=41,NO=1,DF=0,ratio=41,actual_Hz=None),
      esai=dict(TCCR='0xECC309',TCR='0x817D10',RCCR='0x0CC30A',RCR='0x017D01',SAICR='0x40',TX=tx,RX=rx,
                slot_bits=32,data_bits=24,slots_per_frame=2,nominal_Fsys_cycles_per_frame=divider,
                source_assumption='documented reset ETI0/ETO0=0; normal program has no direct PDRH change',actual_rate_Hz=None),
      arm_clock_assumption=dict(HSE_Hz=24000000,MCO1_source='HSE',MCO1_divider=4,MCO1_Hz=6000000,
                                DSP_connection='HYPOTHESIS; board wiring not verified'),
      corroborating_rate_constant=dict(address='0x0805BCD0',value=rate_constant,status='VERIFIED value; sample-rate interpretation supported, not physical measurement'),
      conditional_clock_model=dict(core_Hz=246000000,sample_rate_Hz=246000000/divider,cycles_per_32_frame_period=32*divider,
                                   block_seconds=32/(246000000/divider),status='conditional nominal model, not measured or board-verified'),
      buffer_reference_candidates=references,
      cfg=dict(candidate_instruction_rows=len(visited),unresolved_transfers=unknown,worker_rows=len(wvisit),worker_unresolved=wunknown,
               caveat='not proof of dead code; candidate disassembly/indirect seeds; unexplored data-derived targets remain'),
      regions=[dict(space=s,start=f'0x{lo:X}',end_exclusive=f'0x{hi:X}',words=hi-lo,role=role,status=status) for s,lo,hi,role,status in REGIONS],
      candidates=[dict(space=s,start=f'0x{lo:X}',end_exclusive=f'0x{hi:X}',words=hi-lo,status=status)
                  for s,lo,hi,role,status in REGIONS if 'candidate' in role],
      verified_available_RAM_words=0,
      corrected_budget=budget,voice_scaling=[dict(voices=v,major_loop_instructions=4355*v,worker_body_instructions=1152*v,
                estimated_voice_generation_post_instructions=[5000*v,7000*v],estimate_status='HYPOTHESIS, excludes control/global/IRQ/stalls') for v in [1,6,12]],
      worker_queue=dict(start='shared:0x30002',known_profile_requests_per_voice=192,
                        upper_bound='UNRESOLVED; no capacity/backpressure proof',stock_no_lookup_branch='P:0x7A7..7C2 mode<8'),
      feasibility=dict(program='NOT-YET-DETERMINED',RAM='NOT-YET-DETERMINED',voice_cycle_headroom='NOT-YET-DETERMINED',
                       worker_bypass='stock request-free voice path exists; replacement invariants still required',
                       writable_buffer='VERIFIED DSP scratch writes; full replacement side effects unresolved',comparison='NOT-YET-DETERMINED for hard resource fit'))
    memory=io.StringIO();writer=csv.DictWriter(memory,fieldnames=['space','start','end_exclusive','words','role','status']);writer.writeheader();writer.writerows(result['regions'])
    accesses=io.StringIO();writer=csv.DictWriter(accesses,fieldnames=['program','pc','kind','space','address','register','candidate_reachable','instruction']);writer.writeheader();writer.writerows(inv)
    out.mkdir(parents=True,exist_ok=False)
    save(out/'audit.json',json.dumps(result,indent=2)+'\n');save(out/'memory-map.csv',memory.getvalue());save(out/'access-inventory.csv',accesses.getvalue())
    save(out/'candidate-code.asm','\n'.join(rows[p]['line'] for p in sorted(visited))+'\n')
    print(json.dumps(dict(output=str(out),candidate_code_rows=len(visited),references_to_buffer=len(references),corrected_subtotal=4355),indent=2))

if __name__=='__main__':main()
