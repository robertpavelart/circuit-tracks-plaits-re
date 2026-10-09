#!/usr/bin/env python3
"""Offline Phase19B-HANDOFF evidence. Decodes stock files; NEVER executes DSP.
Fresh phase output required. No network, device, patch, CPU constructor or stub.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from pypdf import PdfReader
from ct_stock_load_audit import rows, state_manifest, verify_inputs

ROOT=Path(__file__).resolve().parents[1]
DOC='https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf'
FORUM='https://community.nxp.com/t5/Other-NXP-Products/DSP56725-bootloader/td-p/217563'

def sha(data):return hashlib.sha256(data).hexdigest()
def save(out,name,obj):
    b=obj if isinstance(obj,bytes) else (json.dumps(obj,indent=2,sort_keys=True)+'\n').encode()
    with (out/name).open('xb') as f:f.write(b)

def annotations(rs):
    spec=[
        (0x100,['Y:PCRG'],['Y:PCRG','SR.C'],[],['SR.C'],
         'old=PCRG; C=(old>>13)&1; PCRG=old&~0x2000',None),
        (0x101,['Y:PRRG'],['Y:PRRG','SR.C'],[],['SR.C'],
         'old=PRRG; C=(old>>13)&1; PRRG=old|0x2000',None),
        (0x102,['Y:ICDR4'],['A','ICC flags/ACK side effects'],[],['A'],
         'A receives peer ICDR3 via ICDR4; ICC read acknowledges and clears interrupt flag',None),
        (0x104,['A'],['CCR compare flags'],['A'],['CCR compare flags'],
         'Compare transferred A against immediate 0x030002; A retained; Z determines next branch',None),
        (0x106,['SR.Z'],['PC'],['SR.Z'],['PC'],
         'Z=0 -> PC=0x102; Z=1 -> PC=0x107','Z == 0'),
    ]
    return [dict(**rs[pc],reads=read,writes=write,registers_consumed=used,registers_defined=defined,
         effects=effect,branch_condition=cond,
         addressing='direct short peripheral' if pc<0x102 else 'direct absolute Y' if pc==0x102 else 'immediate compare' if pc==0x104 else 'absolute conditional branch',
         AGU_R_N_M_used=False,stack_used=False,
         prior_state='Live loop/interrupt/mode state must be justified for all; GPIO handoff words for100/101, peer ICC state for102')
         for pc,read,write,used,defined,effect,cond in spec]

def run(out):
    out=out.resolve()
    if out.exists() or not out.is_relative_to((ROOT/'builds/phase19b-handoff').resolve()):
        raise ValueError('Fresh output under builds/phase19b-handoff required')
    main,protected=verify_inputs()
    sources=ROOT/'firmware/dsp/build-4486';manifest=json.loads((sources/'manifest.json').read_text())
    loaded={}
    for name in ['bootstrap','selection0-channel0','selection0-channel1']:
        b=next(b for b in manifest['blocks'] if b['name']==name)
        payload=(sources/b['payload_file']).read_bytes();stream=(sources/b['stream_file']).read_bytes()
        assert sha(payload)==b['payload_sha256'] and sha(stream)==b['stream_sha256']
        assert stream[6:]==payload and len(payload)//3==b['word_count']
        assert int.from_bytes(stream[:3],'big')==b['word_count'] and int.from_bytes(stream[3:6],'big')==0
        loaded[name]=(b,payload)
    static=rows(ROOT/'builds/phase3-selection0-channel0.asm',main)
    worker=rows(ROOT/'builds/phase3-selection0-channel1.asm',loaded['selection0-channel1'][1])
    bootstrap=rows(ROOT/'builds/phase3-bootstrap.asm',loaded['bootstrap'][1])
    # Verify existing ARM disassembly against source bytes, without regenerating it.
    binary=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    arm=[]
    for filename,lo,hi in [('phase3-arm-transport.asm',0x08029190,0x080292d0),('dsp-init.txt',0x08023438,0x08023470)]:
        for line in (ROOT/'builds'/filename).read_text().splitlines():
            m=re.match(r'([0-9A-Fa-f]{8})\s+([0-9A-Fa-f]+)\s+(.*)',line)
            if m and lo<=int(m[1],16)<hi:
                address=int(m[1],16);raw=bytes.fromhex(m[2]);offset=address-0x08010000
                assert binary[offset:offset+len(raw)]==raw
                arm.append(dict(address=address,bytes=m[2],text=m[3],line=line))
    assert any(r['address']==0x08029284 for r in arm)
    out.mkdir(parents=True)
    decoded={}
    for name,lo,hi in [('bootstrap',0,8),('selection0-channel0',0x100,0x107),('selection0-channel1',0x100,0x12b)]:
        p=subprocess.run([str(ROOT/'builds/dsp-tools/dsp_disasm.exe'),str(sources/(name+'.payload24.bin')),'0',f'{lo:X}',f'{hi:X}'],
                         capture_output=True,text=True,check=True)
        save(out,name+'.asm',p.stdout.encode())
        rr=rows(out/(name+'.asm'),loaded[name][1]);old=bootstrap if name=='bootstrap' else static if name=='selection0-channel0' else worker
        for pc,r in rr.items():assert r['raw']==old[pc]['raw'] and r['text']==old[pc]['text']
        decoded[name]=len(rr)
    save(out,'startup-instructions.json',annotations(static))
    boot_effects=[
        dict(PC=0,defines=['X0'],reads=['OMR'],effect='X0=OMR_in',SR='unchanged'),
        dict(PC=1,defines=['X0','SR.C'],effect='C=old X0.bit7; X0.bit7=1'),
        dict(PC=2,defines=['X0','SR.C'],effect='C=old X0.bit22; X0.bit22=1'),
        dict(PC=3,defines=['X0','SR.C'],effect='C=old X0.bit21; X0.bit21=0'),
        dict(PC=4,defines=['OMR'],reads=['X0'],effect='OMR=X0'),
        dict(PC=5,defines=[],effect='NOP'),
        dict(PC=6,defines=['PC'],effect='PC=0xFFFFFE; P:7 is extension operand, not separate instruction')]
    save(out,'bootstrap-analysis.json',dict(status='VERIFIED static bytes and decoding',stream_bytes=30,header_bytes=6,
       program_bytes=24,words=8,instructions=7,load=0,entry=0,effects=boot_effects,
       OMR_formula='(OMR_in | 0x400080) & ~0x200000',SR_formula='SR out unchanged except C=OMR_in.bit21',
       untouched=['SP','SC','SSH/SSL','R0-R7','N0-N7','M0-M7','A','B','LA','LC','VBA','peripherals','ICC','shared RAM'],
       untouched_scope='Decoded bootstrap body only, excludes ROM loader/reset/implicit pending interrupts',
       post_second_ROM_preservation='UNRESOLVED; no authentic matching ROM source/binary established'))
    mask=sum(1<<b for b in [21,20,19,18,15,14,13,12,11,10,9,8,7,6,5,3,2,1,0])
    save(out,'gpio-contract.json',dict(profile='Conditional DSP56724/DSP56725 compatible device',
       PCRG=dict(space='Y',address=0xfffffa,reset=0x1e1,documented_RW_bits_mask=mask,
         reset_bit13=0,read='control latch, not sampled pin data; no read-clear side effect documented',
         write='changes GPIO function together with PRRG',external_pin_value=False,handoff_value=None),
       PRRG=dict(space='Y',address=0xfffff9,reset=0x1e1,documented_RW_bits_mask=mask,reset_bit13=0,handoff_value=None),
       PDRG=dict(space='Y',address=0xfffff8,reset=0,role='pin/latch data; NOT READ by100..106'),
       configuration_table=[dict(PRRG=0,PCRG=0,function='disconnected'),dict(PRRG=0,PCRG=1,function='input'),
                            dict(PRRG=1,PCRG=0,function='output'),dict(PRRG=1,PCRG=1,function='alternate function')],
       prefix_result='After100/101 bit13 is output regardless of original bit13; output latch/pin level remains unknown',
       ROM_can_have_modified='UNRESOLVED: no proven write exclusion for this ROM',
       board_pin_level_needed_for_prefix=False,board_G13_to_ARM_poll_signal='UNRESOLVED',
       reserved_bits='Blank register-diagram fields excluded from RW mask; do not infer writable storage',
       implemented_model=False,manual=dict(URL=DOC,pages=[143,144],section='8.2.5, tables8-10/8-11')))
    save(out,'icc-contract.json',dict(status='VERIFIED static producer/consumer; DOCUMENTED conditional register pairing',
       producer=dict(image='selection0-channel1',PC=0x109,space='Y',address=0xffffd7,register='ICDR3',value=0x030002),
       consumer=dict(image='selection0-channel0',PC=0x102,space='Y',address=0xffffd4,register='ICDR4',compare_PC=0x104,branch_PC=0x106),
       initial_at_hardware_reset=0,initial_at_application_handoff=None,
       worker_shared_queue=dict(first_word=0x30000,initial_tail_and_cursor=0x30002,PC_tail_write=0x107,
          cursor_register='R5',progress_publications=[0x109,0x121,0x128]),
       value_role='Initial queue cursor / consumed-result progress pointer; initial equality also gates main readiness',
       ordering=['worker105 initializesR5','worker107 writes sharedX30000','worker109 writesICDR3','main102 reads peerICDR3 viaICDR4'],
       read_side_effects=['read clears corresponding interrupt flag','when acknowledging a maskable transfer, ACK is set to inform producer'],
       empty_or_disabled_read_ACK_behavior='Not fully specified by reviewed text; do not invent flag transitions for these cases',
       IRQ_behavior='Do not assume none: ICCR3.MIE, PIC priority and SR masks govern delivery; post-ROM states unresolved',
       acknowledgement=dict(explicit_consumer_instruction=False,implicit_on_ICDR4_read=True,
          producer_register='ICAR3',address=0xffffd5,ACK_bit=0,RACK_bit=1),
       shared_alias='Explicit common word store across private cores at X30000; not private X/Y equal-address aliasing',
       repeated_reads='Do not replace with one-shot command dequeue; ICDR4 reflects peer data. Implement read ACK/flag effects.',
       publication_time='UNRESOLVED until justified original worker execution/event contract',
       implementation='SPECIFICATION ONLY; no fake publication or broad worker model',
       evidence=[worker[pc] for pc in [0x105,0x107,0x109,0x120,0x121,0x125,0x126,0x128]],
       manual=dict(URL=DOC,pages=[250,251,255,256,257,258],sections=['13.1.2','13.2.2.5','13.2.2.8'])))
    save(out,'arm-ordering.json',dict(status='VERIFIED upload call order; DOCUMENTED application starts at load address',
       classification='B: channel0 upload/start contract precedes channel1; explicit ICC synchronization',
       calls=[dict(address=0x08029284,image='bootstrap',channel=0),dict(address=0x08029294,image='selection0-channel0',channel=0),
              dict(address=0x080292a6,image='selection0-channel1',channel=1)],
       delay_calls=[0x0802928a,0x0802929a],
       core0_PC102_relative_to_worker109='UNRESOLVED: cannot assert token already exists on first read',
       physical_endpoint_to_core_numbers='UNRESOLVED exact board assignment; complementary ICC program roles corroborated',
       final_transfer='ROM starts at P0; original main JMP100 / worker JMP100 performs last transfer',
       ARM_witnesses=arm))
    prior=state_manifest()['fields'];fields=[]
    for name,old in prior.items():
        classification='BLOCKING UNKNOWN' if name in ['SR','OMR','LA','LC','VBA'] else 'UNKNOWN BUT UNUSED BEFORE INITIALIZATION'
        if name in ['SP','SC','R0-R7','M0-M7']:classification='FIRMWARE INITIALIZES BEFORE USE (reviewed uses only)'
        if name=='PC':classification='DOCUMENTED HANDOFF VALUE'
        fields.append(dict(field=name,value=0 if name=='PC' else None,classification=classification,
           provenance=[dict(kind='boot manual' if name=='PC' else 'unknown',detail=old['evidence'])],
           documented_reset=old['documented_reset'],firmware_init=old['firmware_initializes_before_use'],
           scope='Prefix100..106: R/N/M/stack not explicit operands; do not claim all later uses dominated'))
    fields.extend([
       dict(field='Y:PCRG',value=None,classification='BLOCKING UNKNOWN',provenance=[dict(kind='reset manual',detail='reset1E1 is not a handoff guarantee')]),
       dict(field='Y:PRRG',value=None,classification='BLOCKING UNKNOWN',provenance=[dict(kind='reset manual',detail='reset1E1 is not a handoff guarantee')]),
       dict(field='Y:ICDR4',value=None,classification='BLOCKING UNKNOWN',provenance=[dict(kind='worker publication',detail='worker109 later writes30002; first-read timing unresolved')]),
       dict(field='IRQ/ICCR3/PIC/SHI handoff',value=None,classification='BLOCKING UNKNOWN',provenance=[dict(kind='unknown',detail='SPI-slave24 boot format documented, full register/mask residue not specified')])])
    save(out,'handoff-manifest.json',dict(status='BLOCKED',execution_allowed=False,profile='candidate DSP56724-compatible only',
       fields=fields,explicit_assignments=[dict(field='PC',value=0,provenance='DSP56724RM table5-5 + boot header; post-load entry only')],
       derived_entry=dict(PC=0x100,provenance='Original mainP0 JMP100',executed=False),
       requirements=[dict(field='SR.LF / loop control',value=None,requirement='No active inherited hardware loop; no assumed zero LA/LC'),
          dict(field='IRQ boundary',value=None,requirement='No uncontrolled delivery before safe point; derive masks/priorities/pending events'),
          dict(field='24-bit compatible transfer/compare modes and mapping',value=None,requirement='Explicit compatible live modes, not whole SR/OMR zero'),
          dict(field='PCRG/PRRG',value=None,requirement='Prove post-ROM latch words or supported symbolic state; no pin-value substitution')],
       instruction_limit=0,worker_execution_allowed=False,stock_CPU_defaults_used=False))
    gates={
       'A P100 entry defensible':'NOT-YET-DETERMINED','B GPIO sufficiently modeled':'NO',
       'C 30002 provenance proven':'YES',
       'D channel ordering proven':'YES',
       'E SR/OMR sufficient':'NOT-YET-DETERMINED',
       'F stack/AGU sufficient':'NOT-YET-DETERMINED',
       'G at least one instruction may execute without guess':'NO',
       'H reach known clear':'NO'}
    save(out,'execution-gate.json',dict(answers=gates,execution_allowed=False,
       answer_scope=dict(C='Conditional documented device profile + verified stock producer/consumer bytes',
          D='Upload order only; first-PC102/worker109 interleaving NOT-YET-DETERMINED',
          F='Explicit100..106 operands do not use stack/AGU; inherited loop/interrupt uses remain unproved',
          G='No execution authorized under the current incomplete contract; not a proof that no future prefix can be established'),
       longest_defensible_prefix_instructions=0,stop_before=0,requested_P100_prefix_stop_before=0x100,
       stock_instructions_actually_executed=0,worker_instructions_actually_executed=0,
       resume19B2=False,first_blocker='Authentic live post-ROM control state and GPIO latch handoff; no safe first-instruction profile',
       next_step='Acquire matching DSP56724/56725 ROM loader source/listing and validate reset-through-SHI exits for live SR/OMR/IRQ and PCRG/PRRG',
       worker_gate='Closed: worker100/102..104 uses unmodeled peripherals before publication and inherited control state is unresolved'))
    device=PdfReader(ROOT/'builds/phase19b/documentation/DSP56724RM.pdf')
    pages=[96,97,98,99,100,101,102,142,143,248,249,250,253,254,255,256,257,258]
    text='\n'.join(f'PDF PAGE {i+1}\n'+device.pages[i].extract_text() for i in pages)
    save(out,'device-document-witnesses.txt',text.encode())
    save(out,'primary-sources.json',dict(manuals=[dict(URL=DOC,
          local='builds/phase19b/documentation/DSP56724RM.pdf',SHA256=sha((ROOT/'builds/phase19b/documentation/DSP56724RM.pdf').read_bytes()),pages=[i+1 for i in pages]),
          dict(URL='https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf',
          local='builds/phase19b/documentation/DSP56300FM.pdf',SHA256=sha((ROOT/'builds/phase19b/documentation/DSP56300FM.pdf').read_bytes()))],
          discovery_lead=dict(URL=FORUM,status='UNRESOLVED non-authoritative forum report of support-supplied source; attachments not retrieved',
             retrieval='Web open cache misses; direct public page HTTP403. No access bypass, login or support message attempted.'),
          handoff_guarantees='Mode0 documents SPI slave24, image load and entry; reviewed manual does not supply a complete ROM exit register contract'))
    verify_inputs()
    for name,(block,payload) in loaded.items():assert sha((sources/block['payload_file']).read_bytes())==sha(payload)
    save(out,'validation.json',dict(status='TESTED static evidence PASS; EXECUTION BLOCKED',decoder_instruction_counts=decoded,
        protected_source_hashes_match=True,main_worker_bootstrap_hashes_match=True,ARM_witness_bytes_match=True,
        original_instructions_executed=0,worker_emulator_loaded=False,
        worker_static_load=dict(words=364,bytes=1092,load=0,end=0x16c,entry=0,startup=0x100),
        audit_script_SHA256=sha(Path(__file__).read_bytes())))
    save(out,'hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
    print('Static handoff audit PASS; stock/worker execution gate CLOSED; 0 instructions')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',required=True,type=Path)
    run(ap.parse_args().output_dir)
