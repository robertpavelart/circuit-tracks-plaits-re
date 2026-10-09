"""Phase20C offline design/evidence export. Never emits a patched program/image.

Reads original instruction bytes and existing standalone traces only. Template
counts are CALCULATED, not assembled or executed changed-code measurements.
"""
import argparse
import array
import csv
import hashlib
import json
import re
import struct
from pathlib import Path
from functools import lru_cache
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'builds/phase20c-livepatch-design'
DSP=ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin'
GOLD=ROOT/'builds/phase20a-regopt/final'
FM=ROOT/'builds/phase19b/documentation/DSP56300FM.pdf'
RM=ROOT/'builds/phase19b/documentation/DSP56724RM.pdf'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def dump(out,name,value):
    with (out/name).open('x',encoding='utf8',newline='\n') as f:
        json.dump(value,f,indent=2,sort_keys=True);f.write('\n')


def table(out,name,rows):
    with (out/name).open('x',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def original_rows():
    payload=DSP.read_bytes();rows={}
    for line in (ROOT/'builds/phase3-selection0-channel0.asm').read_text().splitlines():
        m=re.match(r'P:([0-9A-F]{6})  ([0-9A-F]{6})(?: ([0-9A-F]{6}))?\s+(.*)',line)
        if not m: continue
        pc=int(m[1],16);raw=bytes.fromhex(m[2]+(m[3] or ''))
        if payload[pc*3:pc*3+len(raw)]!=raw: raise AssertionError(f'Original word mismatch {pc:X}')
        rows[pc]=dict(pc=pc,words=len(raw)//3,raw=raw.hex(),instruction=m[4])
    for pc,text in {0x9B9:'move #$001400,r0',0x9C6:'do x:$003a,$09d9',
        0x9D8:'move a,x:(r1)+',0x9D9:'move y:$0007,r0',
        0x9CA:'add b,a a,x:(r3)',0x9CD:'move a,x:(r5)+',
        0x9B8:'move r0,y:$0007',0x19E6:'jsr $077f'}.items():
        assert rows[pc]['instruction']==text,(pc,rows[pc])
    return rows


def generator_map():
    items=[
      (0x281,0x387,'lifecycle / note / parameter preparation','KEEP','consumes event; updates flags, note-follow/envelopes, reset state and calls387/77F'),
      (0x387,0x46E,'three generator records and kernel preparation','KEEP','42 Q words + kernel/sample masks rewritten; cannot borrow persistent storage'),
      (0x46E,0x4D5,'ramp/post/gain coefficient preparation','KEEP','six deltas plus post targets/current gain; downstream live'),
      (0x77F,0x79B,'bank / pass / lane scratch preparation','KEEP','XCC, bitmap OR on request; clear96 Y words on completion'),
      (0x79B,0x99E,'three lanes and inner repeats','KEEP BOTH PASSES','request publishes queue and ICC; completion waits/consumes; phase/coefficient commits; original guard provenance'),
      (0x99E,0x9A5,'pass exit','KEEP','request returns at9A4; only completion reaches9A5'),
      (0x9A5,0x9B9,'six coefficient ramps','KEEP','X[1400,14C0) produced, Q+2A..2F advanced, R4=S+0C, Y7=Q+30'),
      (0x9B9,0x9D9,'complete final mono/aux combiner','RETAIN CLONE ON TEST PATH; ORIGINAL FALLBACK','32 P words, DO32; mono32 plus aux2C02/2C24; no2C66 store'),
      (0x9D9,0x9DD,'natural stock continuation','KEEP IN PLACE','R0<-Y7 +three NOPs, no hook/re-entry at9D9'),
      (0x9DD,0xA95,'post/filter/gain/group mix','KEEP','actual natural coefficients/history/modes/accumulators; no checkpoint fabrication'),
      (0x198D,0x19BF,'descriptor request traversal','KEEP','sets pass bit, consumes descriptor and publishes lookup work'),
      (0x19BF,0x19F3,'completion traversal','KEEP','clears pass bit then consumes bitmap;19E6 invokes77F')]
    return [dict(start=f'P:0x{a:X}',end_exclusive=f'P:0x{b:X}',role=role,decision=decision,
        required_effects=effects,status='VERIFIED original bytes/control flow; CONDITIONAL future replacement')
        for a,b,role,decision,effects in items]


def save_registers():
    # Conservative exact union; R0 is restored by original9D9. M/OMR untouched.
    return [f'R{i}' for i in range(1,8)]+[f'N{i}' for i in range(8)]+['A2','A1','A0','B2','B1','B0','X0','X1','Y0','Y1','SR']


def clobbers():
    rows=[]
    for i in range(8):
        rows.append(dict(field=f'R{i}',classification='REDEFINED BEFORE POST USE' if i==0 else 'MUST PRESERVE',
            evidence='9D9 reload Y7 +three NOPs' if i==0 else 'renderer treats R1..7 as24-bit scratch; conservative restore avoids caller-liveness assumptions'))
        rows.append(dict(field=f'N{i}',classification='MUST PRESERVE',evidence='renderer register scratch; preserve all8 to avoid caller/AGU assumptions'))
        rows.append(dict(field=f'M{i}',classification='MUST PRESERVE',evidence='leave untouched; qualify output M0 linear, do not copy FFFFFF or set harness defaults'))
    for field in ['A','B','X0','X1','Y0','Y1','SR']:
        rows.append(dict(field=field,classification='MUST PRESERVE',evidence='restore original final-combiner boundary raw state, including full accumulator slices and SR'))
    for field in ['OMR','LA/LC/LF/FV','SP/SC/hardware stack']:
        rows.append(dict(field=field,classification='MUST PRESERVE',evidence='OMR unchanged; balanced DO+JSR must restore loop/prefix naturally; do not force SP/SC or standaloneSR/OMR'))
    rows.append(dict(field='A/B during dispatcher before clone/fallback',classification='CAN CLOBBER',
        evidence='final combiner first defines A at9C8,B at9C9 before use; saveSR inB1 while tests useA, restoreSR before original continuation'))
    return dict(status='BOUNDED-PROOF register union; actual wrapper instruction/IRQ/stack qualification UNRESOLVED',
        classifications=rows,raw_save_words=len(save_registers()),raw_save_set=save_registers(),
        M0_qualification='only R0 is used as address register by renderer; N0 changes as data. Qualify legal linear M0 and interlocks.',
        loop_extra_entries=3,extra_entry_reason='rendererDO two frames +native ratioJSR one; entry trampoline/JMP adds zero',
        no_harness_defaults=True,stack_restoration='balanced control flow, not blind SP/SC repair',
        selected_post_early_A_dead=True,conservative_restore_reason='local post liveness is insufficient for whole caller/IRQ equivalence',
        eligibility='arithmetic/memory map/stack/IRQ conditions must qualify or take original fallback')


def lifetime_rows():
    rows=[]
    def add(space,address,category,writers,readers,lifetime,decision):
        rows.append(dict(space=space,address=f'0x{address:X}',classification=category,
            writers=writers,readers=readers,lifetime=lifetime,placement_decision=decision,
            persistent_safe=False,status='VERIFIED local accesses; global/async ownership UNRESOLVED'))
    for j in range(0x4A):
        a=0x57A+j
        if j==0: cat='SHARED';w='ARM event ->29D/29E';r='281 lifecycle'
        elif j<=0x2A: cat='GENERATOR-PRIVATE';w='387 three14-word records; some77F updates';r='77F lane generator and future387 preparation'
        elif j<=0x30: cat='GENERATOR-PRIVATE';w='387 ramp deltas,9A5..9B7 current update';r='next block ramps; final mono/aux combiner'
        elif j<=0x44: cat='POST-PROCESSING-LIVE';w='47E..4D3; post/gain updates';r='9DD..A94 post/gain'
        else: cat='SHARED' if j in (0x47,0x48) else 'UNKNOWN';w='ARM/DSP lifecycle / allocator; complete fields unresolved';r='allocator/time/scratch or unknown'
        add('X',a,cat,w,r,'slot0 context; first42 words and6 ramps overwritten/needed next block',
            'REJECT persistent reuse under retained-stock-prefix design')
    for j in range(12):
        add('X',0x1960+j,'GENERATOR-PRIVATE','387 kernel setup, including dynamic count at3C2',
            'three lane generator / template references','rebuilt/used before every completion; normal dynamic extent must remain intact',
            'REJECT persistent reuse; stride12 is not free capacity')
    for j in range(0x28):
        cat='GENERATOR-PRIVATE' if j<0xC else 'POST-PROCESSING-LIVE'
        writer='387 mask/setup,7F9 or alternate phase stores, event reset' if j<6 else '477/47B deltas;9AF read; next block ramp history' if j<12 else 'post/filter retained history +event reset subsets'
        add('Y',0x59F+j,cat,writer,'retained stock generator/post depending field',
            'same40-word slot; phase/masks and6 ramps remain live because prefix retained',
            'REJECT persistent reuse; changing space alone does not grant ownership')
    for a in range(0x2CCC,0x2D0C):
        add('X',a,'SHARED','822/82D/87D/88B phase absolute weights;1EFA/1F97 effects,260C init',
            'generator weights then effect/scratch consumers','candidate transient interval only between completed combiner and9D9',
            'first32 could fit26 saves+3 controls+3 spills CONDITIONALLY; later reader-before-write/IRQ domains not closed')
    for space,lo,hi,w,r in [
        ('X',0x2C46,0x2C66,'7F1/7F2 phase,9D8 mono; future renderer32','post then scratch reuse'),
        ('X',0x2C66,0x2C67,'phase prefix on selected path, laterC9F history','BE6/BE7 andA93 guard/CCR'),
        ('X',0x2C02,0x2C22,'9CA partial combination','9EB/9FD routing1'),
        ('X',0x2C24,0x2C44,'9CD intermediate','9E1/9FD routing2'),
        ('Y',0xA01,0xA61,'78B..78D clear, lane contributions','9C5..9D6 combo')]:
        for a in range(lo,hi):
            add(space,a,'POST-PROCESSING-LIVE' if lo in (0x2C46,0x2C66,0x2C02,0x2C24) else 'SHARED',
                w,r,'shared per-invocation scratch, not cross-block state',
                'mono32 direct output allowed conditionally; guard/aux untouched; no persistent allocation')
    for space,values in [('X',[0,1,2,4,5,0x2C,0x39,0x3A,0x3B,0x3C,0x3F,0xCC,0x2F30,0x2F31,0x2F32,0x2F34,0x30000]),
                         ('Y',[0,1,4,5,6,7,0x1A,0xFFFFD4])]:
        for a in values:
            add(space,a,'SHARED','stock preparation/generator/protocol','stock generator/post/scheduler',
                'global/current context or peripheral; ownership not surrendered',
                'do not retain standalone literal state/spill/output addresses')
    return rows


def extension():
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    stream=(ROOT/'firmware/dsp/build-4486/selection0-channel0.boot24.bin').read_bytes()
    count=int.from_bytes(stream[:3],'big');load=int.from_bytes(stream[3:6],'big')
    assert count==0x2A5E and load==0 and len(stream)==6+3*count
    assert arm[0x1F0:0x8110]==stream
    assert struct.unpack_from('<I',arm,0x19700)[0]==0x080101F0
    return dict(status='VERIFIED framing/ARM transport; CONDITIONAL PRAM capacity; deployment UNRESOLVED',
        count=count,count_hex='0x2A5E',load=load,header_bytes=6,packed_word_bytes=3,
        checksum='no per-stream checksum observed; outer firmware has size field/nonreflectedCRC32',
        entry='P0 reset branch unchanged; boot entry/load0; no separate entry field',
        uploader='08029260; selection table08029700; sender08029200',
        sender_count='reads bytes1/2 as16bit BE; adds2 header words, stages up toAA words=510bytes; source+3*index',
        sender_limit='payload<=0xFFFD: count+2 must not wrap16bits. CMP/BLT uses zero-extended32bit values, not signed16bit; no0x7FFF cutoff. Core capacity is lower.',
        ROM_contract='one count/load/P record under corroborated SHI boot model; authentic ROM dump still unavailable',
        conditional_core0_mode='bootstrap sets MS7,MSW1 bit22 and clearsMSW0 bit21; P[0,4000),X[0,6000),Y[0,4000)',
        maximum_conditional_payload=0x4000,maximum_conditional_extension=0x4000-count,
        maximum_conditional_extension_bytes=3*(0x4000-count),
        another_loaded_region='channel1/selection1 replace different endpoint or mode, not concatenated same-P loads; no second boot record in selected stream',
        actual_capacity_and_tail_ownership='UNRESOLVED exact endpoint/core/mode/P tail indirect access proof; no deployable address selected',
        source_offset=0x1F0,source_end=0x8110,following_stream_start=0x8110,
        in_place_extension='ANY positive delta overlaps channel1 immediately; larger growth also overwrites absolute-addressed ARM code',
        relocation_design='append whole enlarged stream without shifting existing ARM/DSP addresses; change selected pointer-table cell; outer image size/CRC would need update in a separately authorized later construction',
        appended_start_if_existing_BIN_end_used=0x08010000+len(arm),
        max_new_stream_bytes=6+3*0x4000,max_hypothetical_BIN_bytes=len(arm)+6+3*0x4000,
        max_hypothetical_BIN_end=0x08010000+len(arm)+6+3*0x4000,
        upper_flash_model='STM32F745VE nominal512KiB:08080000 end, CONDITIONAL actual unit; bootloader acceptance not proved',
        acceptance_unknowns=['official updater/bootloader max length','flash layout/protection and recovery independence','all integrity/version fields','P-tail normal indirect ownership','DMA/staging assumptions'],
        flash_ready_image_emitted=False,patched_payload_emitted=False)


def sender_schedule(payload_words):
    """Integer fixture for qualified nonwrapping ARM sender counts, not firmware execution."""
    if not 0<=payload_words<=0xFFFD:raise ValueError('count+2 would wrap the16bit total')
    total=payload_words+2;index=0;chunks=[]
    while index<total:
        count=min(total-index,0xAA)
        chunks.append(dict(source_byte_offset=3*index,word_count=count,byte_count=3*count))
        index=(index+count)&0xFFFF
    assert index==total and sum(c['word_count'] for c in chunks)==total
    return chunks


def renderer_census():
    lines=(GOLD/'dsp-first/program.asm').read_text().splitlines()
    labels=json.loads((GOLD/'dsp-first/labels.json').read_text())
    code=(GOLD/'dsp-first/program.be24').read_bytes()
    assert len(code)==442*3
    rows=[]
    for i,line in enumerate(lines):
        addr,s=line.split(' ',1);pc=int(addr,16)
        end=int(lines[i+1].split()[0],16) if i+1<len(lines) else labels['done']
        mem=bool(re.search(r'x:\$[0-9a-f]{6}',s))
        control=s.split()[0].startswith('j')
        rows.append(dict(pc=pc,instruction=s,original_words=end-pc,
            added_words=int(mem)+int(control),
            added_nominal_cycles=int(s.startswith('move x:'))+int(s.startswith(('jmp ','jsr '))),
            category='absolute X ->long fixed owned block' if mem else 'absolute branch target ->appended module/restore' if control else 'unchanged',
            status='CALCULATED prescribed encoding template; no changed program assembled'))
    assert sum(r['original_words'] for r in rows)==442
    assert sum(bool(re.search(r'x:\$',r['instruction'])) for r in rows)==81
    assert sum(r['instruction'].split()[0].startswith('j') for r in rows)==26
    # Static forward main CFG has no back edge except hardware DO. Bound extra
    # costs with every main read/JMP once per sample, at most80 helper calls,
    # k<=3. This is deliberately looser than the original event DP.
    startup=[r for r in rows if r['pc']<labels['sample']]
    body=[r for r in rows if labels['sample']<=r['pc']<labels['block_end']]
    startup_delta=sum(r['added_nominal_cycles'] for r in startup)
    body_delta=sum(r['added_nominal_cycles'] for r in body if not r['instruction'].startswith('jsr '))
    delta_upper=startup_delta+32*body_delta+80*(1+3)+1
    model=dict(status='CALCULATED conditional encoding/traffic model, not execution measurement',
        baseline_P=442,absolute_X_sites=81,absolute_control_sites=26,
        all_long_renderer_P=442+81+26,terminal='JMP to high restore wrapper, included in26; original arithmetic/nativeDIV unchanged',
        direct_output='single move a,y:(r0)+ ->move a,x:(r0)+; R0 initialized2C46 outside renderer, no extra32-word buffer',
        arithmetic_changes=0,working_registers=16,
        short_block_alternative='would retain442 only if actual13 low X words and low-P placement owned; no such low block proved',
        indirect_base_alternative='would occupy a scratch register or require reallocation/spills; changes ABI/timing, not implemented',
        baseline_bound=13379,baseline_bound_scope='unchanged standalone trace model; cannot quote as integrated bound',
        setup_delta_relaxation=startup_delta,per_sample_delta_relaxation=body_delta,
        ratio_calls_upper=80,ratio_integer_part_upper=3,
        relocation_delta_upper=delta_upper,conditional_relocated_renderer_upper=13379+delta_upper,
        cycle_rules='FM A4/A5 absoluteJMP/JSR add1; longJcc table add0; longabsolute X reads +1 versus short; stores unchanged under retained STRONG2-cycle short-store interpretation',
        assumptions='private zero-wait memory, qualified modes; prior interlocks retained conservatively; encoding/near-DO/fetch boundary audit still required',
        physical_bound=None,firmware_code_emitted=False)
    return rows,model


def trace_address_delta(out,rc):
    # Existing ORIGINAL standalone execution-PC trace; no new CPU execution.
    import numpy as np
    trace=np.memmap(GOLD/'dsp-first/execution-pc.u16',dtype='<u2',mode='r')
    bypc=np.zeros(4096,dtype=np.uint8)
    for r in rc: bypc[r['pc']]=r['added_nominal_cycles']
    with (GOLD/'dsp-first/blocks.csv').open(newline='',encoding='utf8') as f: blocks=list(csv.DictReader(f))
    values=[];pos=0
    for b in blocks:
        n=int(b['instructions']);delta=int(bypc[trace[pos:pos+n]].sum());pos+=n
        values.append(dict(case=b['case'],block=b['block'],original_issued=n,
            nominal_relocation_cycle_delta=delta,status='CALCULATED on existing unchanged trace; no relocated execution'))
    assert pos==len(trace)
    table(out,'addressing-trace-deltas.csv',values)
    ds=[r['nominal_relocation_cycle_delta'] for r in values]
    return dict(blocks=len(ds),minimum=min(ds),mean=sum(ds)/len(ds),maximum=max(ds),
        source_trace_sha256=sha(GOLD/'dsp-first/execution-pc.u16'),status='MEASURED existing address/control event counts; CALCULATED hypothetical cycle delta')


def plans(relocation):
    c=clobbers();regs=save_registers();assert len(regs)==26
    dispatcher=dict(status='CONDITIONAL design, not assembled',interception='P:0x9B9',
        hook='replace complete2-word immediateR0 instruction with2-word absoluteJMP to owned appended module',
        eligibility='normal completion, XCC=0 and R4=0x5AB (slot0 S+0C); arithmetic/AGU/block/ownership conditions qualified or fallback',
        UI_identity='bank0/Synth1 correspondence remains HYPOTHESIS; test identity is numericbank0/slot0',
        template=[['MOVEC SR,B',1],['MOVE R4,A',1],['CMP #>0x5AB,A',2],['JNE >fallback',2],
            ['MOVE X:>CC,A',2],['TST A',1],['JNE >fallback',2],['MOVEC B1,SR',1]],
        template_P=12,fallback_P=4,dispatcher_total_P=16,hook_P=2,
        selected_template_cycles=22,wrong_slot_template_cycles=15,wrong_bank_template_cycles=24,
        costs='CALCULATED FM template, including original-hookJMP; status-read stall2 budgeted. Wrong-slot/bank includes restore/replayedMOVE1400/JMP9BB, subtracts originalMOVE2. No assembled exact claim.',
        template_requires='qualify MOVEC forms and source/control interlocks; optional eligibility/init checks not counted',
        fallback='restoreSR fromB1, replay displaced MOVE1400,R0 andJMP9BB; all other original bytes retained',
        selected='restoreentrySR; run relocated clone9B9..9D8; save natural clone liveout; renderer overwrites mono32 only; restore; JMP original9D9',
        stock_work_removed=0,clone_P=32,clone_changes='only DO end address relocated; raw words copied as evidence, no clone image emitted',
        avoids_9D9_hook='keeps originalR0 reload andNOPs intact; no self-reentering9D9 dispatcher',
        selected_core_instruction_stream='no entryJSR, no new entry return frame; ratiohelperJSR/rendererDO still create up to3 extra frames',
        mode_side_streams='retain complete combiner, so both aux streams remain regardless post selector; changed mono deliberately changes post response',
        cycle_model_qualified=False)
    # Recompute the displayed branch template cycles explicitly under source tables.
    # MOVEC1, MOVE1, CMP2, Jcc4/5, longXread2, TST1. Status read <=2 extra.
    selected=4+1+2+1+2+5+2+1+5+1  # hook +status readstall +all tests +restore
    wrong_slot=4+1+2+1+2+4+1+2+3-2
    wrong_bank=4+1+2+1+2+5+2+1+4+1+2+3-2
    dispatcher.update(selected_template_cycles=selected,wrong_slot_template_cycles=wrong_slot,wrong_bank_template_cycles=wrong_bank)
    state=dict(status='UNRESOLVED persistent placement; no region SAFE/reserved',
        persistent_words=7,persistent_X_base=None,
        fixed_one_voice_block='preferred over relocatable pervoice ABI; absolute address remains null until ownership proof',
        persistent_fields=['phase','next','previous_pw','high','frequency','pw','shape'],
        control_words=3,spill_words=3,save_words=26,total_wrapper_transient_words=32,
        renderer_minimum_words=13,total_data_words_with_conservative_wrapper=39,new_output_words=0,
        transient_candidate=dict(space='X',start=0x2CCC,end_exclusive=0x2CEC,words=32,
            status='CONDITIONAL temporal reuse only; complete later-reader-before-write and async-domain proof missing',
            proposed_layout=dict(controls=[0x2CCC,0x2CCF],spills=[0x2CCF,0x2CD2],save26=[0x2CD2,0x2CEC])),
        persistent_candidates=[dict(region='XQ first42 /kernel12',decision='REJECT',reason='retained preparation and generator use/overwrite every block'),
            dict(region='Y S first12',decision='REJECT',reason='stock phase/masks/ramp history remains required; also not currentX numericABI'),
            dict(region='X2CCC..2D0C',decision='REJECT persistent',reason='generator/effects overwrite; possible temporary wrapper only'),
            dict(region='standaloneX0..2/20..26/30..32',decision='REJECT unqualified',reason='stock globals/protocol/control words; low addresses not free'),
            dict(region='X5F00..6000 or another arbitraryglobaltail',decision='NOT SELECTED',reason='previous ownership blockers retained; no unreferenced-is-free inference')],
        initialization='after proven init/lifetime, frequency=0 sentinel may mean uninitialized because valid retainedfrequency>=1; initialize all7 once before render. Note-retrigger/reset policy separate and unresolved.',
        model_switching=False,polyphony=False,addresses_reserved=False)
    guard=dict(status='VERIFIED selected original data flow; no universal guard value',
        address='X:0x2C66',combiner_writes_guard=False,
        selected_producer='P7F1 first-track store at iteration16 of most-recent applicable lane/repeat; phasepair buffer2C46..2C85',
        selected_formula='pre-add A1 at sample16 = original start+16*prepared increment subject stock arithmetic modes; not a preset constant',
        other_classes='may leave earlier/stale natural word; preserve exact stock prefix rather than create guard default',
        retained_suffix='entire32P combiner retained for aux and natural CCR; it does NOT independently establish2C66',
        replacement_writes='exactly X[2C46,2C66), never2C66',
        no_copy_last_zero_snapshot=True,downstream='BE6/BE7 reads initial guard and executesMPY/CCR; C9F overwrites on selected filter path; A93 laterprefetch',
        future_tail_only_bypass='not proven; requires request/phase/guard/aux state policy beyond current design')
    pitch=dict(status='VERIFIED tracked-note origin; Hz/calibration and DSP converter UNRESOLVED',
        selected_source='Y:0x12F (slot0 current); generalized12F+60*i',
        alternatives=dict(target159='skips glide/smoothing; not preferred',seed15C='initialization seed, not ongoing pitch'),
        evidence='ARM272F2..27308 publishes(note-60)<<16 toY159;5C0..5CB updatesY12F; original preparation657/387 retained',
        note_units='signed24 current centered-index with16 fractional bits; prior parallel5CA scaled old note not interchangeable with12F',
        conditional_formula='q=sign24(Y12F)/65536; fQ=clamp(round(2^22 * f_reference_Hz * 2^(q/12) / Fs),1,2^20)',
        reference_Hz=None,Fs_Hz=None,
        equal_tempered_MIDI_reference='261.625565Hz at index60 only if independent stock index-to-Hz calibration corroborates; not VERIFIED here',
        native_phase_increment='do not copyQ+9; mask/table/modulation-dependent phase units differ',
        converter_architecture='future bounded exponent/fraction converter or proven stock frequency table; no current implementation/P/cycle guarantee',
        fixed_PW_Q2_22=1<<21,fixed_shape_Q3_21=0,
        controls='frequency from tracked current plus fixedPW=.5 andshape=0; no UI/model/knob mapping',
        output_amplitude='signed24 word representation fits; rawQ3.21 identity is only candidate. Stock scale/headroom and any adapter gain/clipping remain unqualified')
    preserve=['Y7 coefficientcursor','R4 post cursor afterstockramps','all original XQ post selectors/targets/gain/rampcurrent',
        'all Y[S+0C,S+28) nonlinear/filter retained state','original lane phase/masks/ramp histories',
        'XCC/bank/context/bitmap/queue/ICC state','both aux streams X2C02/X2C24','natural X2C66 guard',
        'X/Y globals/block counts/modifiers/tables','existing group accumulations2DF0/2E50',
        'SR/OMR/AGU/loop/hardwarestack state via bounded conservativewrapper',
        'stock allocator/note/envelope/velocity/parameter publication']
    live=dict(status='VERIFIED interfaces; future eligibility/lifetime qualification CONDITIONAL',
        at_intercept='after6 ramps: R0=Q+30, R4=S+0C; Y7=R0; no local generatorDO remains',
        stock_setup_required=True,request_work_required=True,snapshot_required=False,
        preserved_downstream_inputs=preserve,
        replacement_boundary='after preserved clone, mono-only change plus owned Plaits state; no reset defaults installed',
        side_effects_kept='ALL original request/completion lane work and full mono/auxcombiner; no stock generator-side-effect deletion')
    cycle=dict(status='CALCULATED conditional templates, not integrated timing measurement',
        unchanged_renderer_bound=13379,relocation_model=relocation,
        dispatcher_cycles=selected,save_nominal_cycles=52,restore_nominal_cycles=52,
        additional_save_restore_interlocks='UNRESOLVED full sequence; SR read stall and AGU/fetch closure needed',
        output_pointer_setup_nominal=2,fixed_controls_and_frequency_store_nominal=9,
        final_JMP9D9_nominal=3,guard_extra_cycles=0,
        retained_combiner_nominal=562,retained_combiner_description='13 setup +DO5 +32*17 one-cyclebody; zero-wait/private modes; no actual execution/walltime',
        retained_combiner_delta=0,preserved_tail='original work retained, so do NOT subtract562 to claim savings',
        known_template_increment=selected+52+52+2+9+3,
        total_incremental_cycles=None,partial_conditional_increment_upper=relocation['conditional_relocated_renderer_upper']+selected+52+52+2+9+3,
        unknown_terms=['numericeligibility checks','pitch converter','persistentinit path','gain/adapter','save/restore/DO-near-end pipeline qualification','IRQ/DMA/waits'],
        complete_deadline_fit=False,voices=1,
        added_P_template=relocation['all_long_renderer_P']+104+9+2+16+32+1,
        prefetch_padding_P=2,added_P_complete=None,
        wrapper_size_rule='26 raw saves +26 restores, longabsolute2 words each =>104P; MOVEC/register legality unassembled',
        cost_scope='increment relative to unchanged stock generation for selectedvoice. All nonselectedpaths paydispatcher only.',
        no_ten_voice_or_polyphony_claim=True)
    contract=dict(status='CONDITIONAL future firstPoC contract; no implementation',
        selected_path='numericbank0/slot0 completion only; UI Synth1 correspondence HYPOTHESIS',
        output='VariableSaw replaces mono32; both original auxiliary streams intentionally retained',
        nonselected='original request/completion/generator/post; wrapper mustrestoredispatchSR; only dispatcher timing overhead',
        Synth2='bank1 always fallback; original arithmetic/state preserved conditionally, full deadline impact unresolved',
        retained_post='natural unchanged9D9->9DD filter/gain/mixer uses actual live state; no reconstructed checkpoint',
        test_scope='single predetermined allocator slot, not monophonic note routing; allocator may place note elsewhere, thus no all-notes claim',
        controls='tracked pitch+fixedPW/shape; no model/knob mapping',
        no_polyphony=True,no_MIDI1_MIDI2_synth_claim=True,
        stock_aux_caveat='routing1/2 subtract/add retained stock components against newmono; may audibly retain stock components. PureVariableSaw success requires routing0 or separate aux semantics qualification.',
        prototype='REFUSED until code/container/state/lifetime/preservation qualified; no separate patched test program constructed',
        readiness=dict(runtime_snapshot_required=False,architecture_technically_justified='CONDITIONAL YES as late monooverwrite, not compute-saving wholesale bypass',
            code_placement_proven=False,state_placement_proven=False,
            register_preservation_bounded='CONDITIONAL26-word union; implemented wrapper/IRQ/stack qualificationNO',
            offline_patched_image_construction_justified=False,flashing_justified=False))
    recovery=dict(status='UNRESOLVED; flashing NOT justified',
        original_backup='hash/roundtrip proven; not recovery independence',
        gates=['official update-entry path and bootloaderbelow08010000 independence fromworkingDSP',
            'ability to recover when DSPboot/handshake/mainloop hangs','acceptedimage size/flash layout/protection/version/integrity rules',
            'official updater handling oflargerrelocatedimage and interruption/powerfailure',
            'exact actualunit identity and currentfirmware; preservedknown-goodofficialimage',
            'restore/rollback procedure supported without unqualified debug or guessedbootpins',
            'ownership/code/preservation/headroom/deadline qualification and separatelyauthorizedfuturetest'],
        recovery_experiment_performed=False,official_tool_launched=False,flash_ready_firmware=False,
        no_assumption='backup existence or encoder success does not prove brokenDSP recovery')
    return {'replacement-liveins.json':live,'replacement-clobbers.json':c,'state-placement.json':state,
        'guard-tail-analysis.json':guard,'dispatcher-design.json':dispatcher,
        'pitch-converter-design.json':pitch,'cycle-budget.json':cycle,
        'poc-contract.json':contract,'recovery-gate.json':recovery}


def placement_rows(ext):
    return [dict(option=option,conditional_capacity_words=capacity,verified_deployable_words=0,
        payload_loader=loader,effect_on_Synth2=effect,effect_on_algorithms=alg,reversibility=rev,status=status)
        for option,capacity,loader,effect,alg,rev,status in [
        ('A append beyondP2A5E',ext['maximum_conditional_extension'],'increasebootcount; relocateentirestream/changeARMselectedpointer; growoutercontainer',
         'samechannel0 containsbothbanks; dispatcherrequired','preserveoriginalcode andconstants','restoreoriginalstream/count/pointer/image only ifrecoveryworks','CONDITIONAL capacity; tail/container notplacementproven'),
        ('B reclaim original generator code',0,'fixedpayloadsize ifa trulyunused region existed',
         'shared77F/combiner used bybank1','fallback andcloned-originalrequire originalgenerator','originalbytes retained separately doesnotprove rollback','REJECT currentcandidate: no non-test-unusedcode proved'),
        ('C sacrifice stock algorithm',0,'requiresproof algorithmunused onallotherpaths orduplicate it',
         'samealgorithm maybeused bybank1','wouldchangeotherstockpatches without furtherdispatch','recoverygate stillneeded','UNRESOLVED; notfirstPoC preservingnonselected paths'),
        ('D other executable region',0,'mustprove mapped writable/loadableP andlifetime',
         'unknownshared/ROM/externalowner','no region identified','unknownloader/recovery','UNRESOLVED; no regionselected')]]


def guards():
    paths=[p for d in ['original','firmware'] for p in (ROOT/d).rglob('*') if p.is_file()]
    paths += [DSP,FM,RM,ROOT/'tools/ct_fw_tool.py',ROOT/'builds/phase3-selection0-channel0.asm',ROOT/'builds/phase3-arm-transport.asm']
    paths += [p for d in [ROOT/'builds/phase20a-bound/final',ROOT/'builds/phase20b-tapqual/final-v2',
        ROOT/'builds/phase20b-snapshot-design/final-v4'] for p in d.rglob('*') if p.is_file()]
    paths += [GOLD/'assembly/variablesaw.asm',GOLD/'assembly/layout.json',GOLD/'dsp-first/program.be24',
        GOLD/'dsp-first/program.asm',GOLD/'dsp-first/labels.json',GOLD/'dsp-first/execution-pc.u16',GOLD/'dsp-first/blocks.csv',
        ROOT/'plaits/poc/regopt/generate_final.py',ROOT/'plaits/poc/regopt/runner_final.cpp',Path(__file__).resolve()]
    for name in ['tools/ct_livepatch_design_verify.py','emulator/tests/test_livepatch_design.py']:
        if (ROOT/name).exists():paths.append(ROOT/name)
    return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}


def build(out):
    out=out.resolve()
    if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('freshPhase20C child required')
    before=guards()
    assert before['original/circuittracks-firmware-4486.syx']=='bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd'
    assert before['firmware/circuittracks-firmware-4486.bin']=='b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da'
    rows=original_rows();rc,model=renderer_census();ex=extension()
    out.mkdir(parents=True);evidence=out/'evidence';evidence.mkdir()
    table(out,'generator-replacement-map.csv',generator_map())
    table(out,'state-lifetime.csv',lifetime_rows())
    table(out,'code-placement-options.csv',placement_rows(ex))
    table(evidence,'original-instructions.csv',[rows[p] for p in sorted(rows) if
        0x281<=p<0x4D5 or 0x5C0<=p<0x5CE or 0x775<=p<0xCB8 or 0x198D<=p<0x19F3])
    operands=[]
    for p,r in rows.items():
        if not 0x387<=p<0x9D9:continue
        for m in re.finditer(r'([xy]):([^ ,]+)',r['instruction']):
            operands.append(dict(pc=f'0x{p:X}',space=m[1].upper(),operand=m[2],instruction=r['instruction'],
                status='VERIFIED encodedoperand; dynamiccount/base/modifier bounds conditional; notcompleteglobalpoints-to proof'))
    table(evidence,'generator-memory-operands.csv',operands)
    table(evidence,'renderer-addressing-sites.csv',rc)
    observed=trace_address_delta(evidence,rc);model['existing_trace_delta']=observed
    dump(out,'image-extension.json',ex)
    dump(evidence,'sender-count-fixtures.json',dict(status='TESTED integer transport arithmetic, no CPU/device',
        fixtures=[dict(payload=n,chunks=len(sender_schedule(n)),total_words=sum(c['word_count'] for c in sender_schedule(n)))
                  for n in [0x2A5E,0x4000,0x7FFD,0x8000,0xFFFD]],
        rejected=[0xFFFE,0xFFFF],reason='zero-extended32bit signedcomparison has no32767 cutoff;16bit count+2 overflow is limit'))
    for n,v in plans(model).items():dump(out,n,v)
    for path,pages in [(FM,[428,429,430,433,434,436,438]),(RM,[75,76,77,78,103])]:
        reader=PdfReader(path)
        for n in pages:(evidence/f'{path.stem}-pdf{n}.txt').write_text(reader.pages[n-1].extract_text(),encoding='utf8',newline='\n')
    assert before==guards(),'guardedsourcechange'
    dump(out,'validation.json',dict(status='TESTED byte/reportconsistency; no patchedprogram execution',
        original_instruction_rows_checked=len(rows),source_hashes=before,
        output_files_requested=14,modified_canonical_firmware=False,hardware_actions=0,
        CPU_execution=0,patch_image_emitted=False,flash_ready_image_emitted=False,
        persistent_RAM_reserved=False,snapshot_branch='DEFERRED',
        report_scope='conditional architecture and static template/oldtrace counts; readinessrefusal retained'))
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True)
    build(p.parse_args().output_dir)
