"""Offline, target-specific dispatch/writer audit; no DSP execution or packets.

Reprojects the existing Phase14 writer inventory onto the requested selectors,
effect table and descriptor+0 cells. Conditional target sets are not normal
selector snapshots or proof of normal reachability. Fresh exports only.
"""
import argparse
import csv
import io
import json
from pathlib import Path
import re
from ct_stock_load_audit import ROOT, verify_inputs, rows, sha
import ct_fw_tool

WATCH={'selector95A':{0x95a},'indices95B_95F':set(range(0x95b,0x960)),
       'effect_table':set(range(0x9db,0xa12)),
       'descriptor0':{0xeb+8*i for i in range(14)}}
# Original wrapper control flow, including DDC's fallthrough into DE6.
ROUTES={0xdb7:(0xdbd,[0xdb7,0xdb8,0xdba,0xdbc,0xdbd]),
        0xdbf:(0xdc5,[0xdbf,0xdc0,0xdc2,0xdc4,0xdc5]),
        0xdc7:(0xdcd,[0xdc7,0xdc8,0xdca,0xdcc,0xdcd]),
        0xddc:(0xdec,[0xddc,0xde0,0xde2,0xde5,0xde6,0xdeb,0xdec]),
        0xde6:(0xdec,[0xde6,0xdeb,0xdec]),
        0xdd3:(0xdec,[0xdd3,0xde6,0xdeb,0xdec]),
        0xdcf:(0xdec,[0xdcf,0xddc,0xde0,0xde5,0xde6,0xdeb,0xdec]),
        0xdf3:(0xdf9,[0xdf3,0xdf8,0xdf9])}
SITES=[0xdb6,0xdbd,0xdc5,0xdcd,0xdec,0xdf9]


def overlap(lo,hi):
    return [name for name,cells in WATCH.items() if any(lo<=a<hi for a in cells)]


def enumerate_conditional(words):
    """All nominal-domain combinations, never injected into RAM or a CPU."""
    table=words[0x29f6:0x2a2d]
    if len(table)!=55:raise ValueError('Require55 original table words')
    result=[]
    for q in range(8):
        for i in range(5):
            wi=15+5*q+i;wrapper=table[wi]
            if wrapper not in ROUTES:raise ValueError('Unreviewed original wrapper')
            pc,path=ROUTES[wrapper]
            result.append(dict(site=0xdb6,row_selector=q,stage=i,algorithm_index=None,
                table_address=0x9db+wi,raw_table_value=wrapper,final_target=wrapper,
                scope='CONDITIONAL nominal domain and preserved table; NOT proven normal input'))
            for k in range(15):
                marker=table[k]
                result.append(dict(site=pc,row_selector=q,stage=i,algorithm_index=k,
                    table_address=0x9db+k,raw_table_value=marker,final_target=(marker+1)&0xffffff,
                    wrapper=wrapper,wrapper_path=path,
                    scope='CONDITIONAL nominal domain/table and legacy linear modifiers; NOT proven normal input'))
    return result


def collect(out):
    out=out.resolve();base=(ROOT/'builds/phase19c-targetbridge').resolve()
    if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh child of builds/phase19c-targetbridge required')
    payload,protected=verify_inputs();inputs={}
    def read(n):
        raw=(ROOT/n).read_bytes();inputs[n]=sha(raw);return raw
    def old(n):return json.loads(read(n))
    def csvread(n):return list(csv.DictReader(io.StringIO(read(n).decode())))
    def emit(n,v):
        with (out/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
    manifest=old('firmware/dsp/build-4486/manifest.json')
    for b in manifest['blocks']:
        for k in ['stream','payload']:
            assert sha(read('firmware/dsp/build-4486/'+b[k+'_file']))==b[k+'_sha256']
    arm=read('firmware/circuittracks-firmware-4486.bin');syx=ROOT/'original/circuittracks-firmware-4486.syx'
    read('original/circuittracks-firmware-4486.syx')
    assert ct_fw_tool.decode_syx(syx)['firmware']==arm and ct_fw_tool.build_syx(syx,arm)==syx.read_bytes()
    listing='builds/phase3-selection0-channel0.asm';read(listing);r=rows(ROOT/listing,payload)
    def req(pc,text):assert r[pc]['text']==text,(hex(pc),text)
    anchors={0xd87:'move x:$095a,x0',0xd89:'move #>$000005,x1',0xd8b:'mpy +x1,x0,a',
        0xd8c:'asr a',0xd8d:'move #$0009ea,r2',0xd8f:'clr a a0,n2',
        0xd90:'move #$00095b,r0',0xd96:'move (r2)+n2,r2',0xd99:'do #$0005,$0db0',
        0xda3:'move x:(r0)+,n1',0xda8:'add x0,a (r2)+n2,r2',0xdad:'move x:(r1+n1),r0',
        0xdb2:'move x:(r3)+,r1',0xdb6:'jmp (r1)',0xdbc:'move (r0)+,r0',0xdbd:'jsr (r0)',
        0xdc4:'move (r0)+,r0',0xdc5:'jsr (r0)',0xdcc:'move (r0)+,r0',0xdcd:'jsr (r0)',
        0xdcf:'jsr >$0ddc',0xdd1:'jmp >$0dd5',0xdd3:'jsr >$0de6',
        0xde0:'do x:$003a,$0de6',0xde5:'move y1,y:(r7)+',0xde6:'move #$000880,r6',
        0xdeb:'move x:(r0)+,a',0xdec:'jsr (r0)',0xdf8:'move x:(r0)+,a',0xdf9:'jsr (r0)',
        0x29ec:'move #$0029f6,r0',0x29ee:'move #$0009db,r1',0x29f0:'do #$0037,$29f5',
        0x29f3:'move x0,x:(r1)+',0x2788:'move x0,x:(r0)',
        0x198:'move x:$0010,r0',0x199:'jclr #15,x:$0011,$019d',0x19d:'move x0,x:(r0)+',
        0x15c:'movec #$00ffff,m0',0x2030:'move x0,x:(r1)+',0x204b:'move b,x:(r4)',
        0x19a5:'move x:(r3)+,r1',0x19ac:'jsr (r1)',0x28c7:'move #$001a2b,r2'}
    for pc,t in anchors.items():req(pc,t)
    words=[int.from_bytes(payload[i:i+3],'big') for i in range(0,len(payload),3)]
    prior=old('builds/phase12/final/effect-dispatch.json')
    assert [int(x['P_value'],16) for x in prior['table']]==words[0x29f6:0x2a2d]
    census=old('builds/phase14/current/DSP-X-L-write-census.json')
    params=csvread('builds/phase9/verified/parameter-writes.csv')
    special=csvread('builds/phase9/verified/special-destinations.csv')
    normalhost=csvread('builds/phase6c/final/normal-host-intervals.csv')
    unclosedhost=csvread('builds/phase6c/final/unresolved-host-intervals.csv')
    hostcallers=old('builds/phase6c/final/host-callers.json')
    staging=old('builds/phase12/final/mailbox-staging.json')
    stream=old('builds/phase14/current/host-stream-count-proof.json')
    dma=old('builds/phase10/replay/DMA-reviewed-bounds.json')
    worker=old('builds/phase14/current/worker-write-census.json')
    utility=old('builds/phase11/replay/utility-domains.json')
    parent=old('builds/phase19c-parent/final-v3/result.json')
    assert parent['original_parent_opcodes']==0
    read('builds/phase3-arm-transport.asm')
    # Byte-check exact ARM transport witnesses; no new ARM/DSP disassembler.
    armw=[]
    for line in (ROOT/'builds/phase3-arm-transport.asm').read_text().splitlines():
        m=re.match(r'([0-9A-F]{8})\s+([0-9a-f]+)\s+(.*)',line)
        if not m:continue
        pc=int(m[1],16);raw=bytes.fromhex(m[2]);assert arm[pc-0x8010000:pc-0x8010000+len(raw)]==raw
        if 0x80291e0<=pc<0x8029200 or 0x80292dc<=pc<0x8029344:armw.append(line)
    out.mkdir(parents=True)
    projected=[];direct_hits=[]
    for e in census['entries']:
        pc=int(e['PC'],16);req(pc,e['instruction'])
        x={k:v for k,v in e.items() if k not in ['reaches_35F','zero_invariant_effect']}
        lo=int(e['minimum_address'],16);hi=int(e['maximum_address'],16)+1
        scope='canonical absolute address' if not e['indirect'] else 'CONDITIONAL existing witness' if 'reviewed_witness' in e else 'UNRESOLVED reused indirect address envelope; not actual normal alias'
        if pc==0x2030:lo,hi,scope=0x967,0x98d,'VERIFIED local38-word clear with legacy linear M1; normal global context UNRESOLVED'
        if pc==0x29f3:lo,hi,scope=0x9db,0xa12,'INIT-ONLY55-word copy, linear initialization'
        if pc==0x2788:lo,hi,scope=0,0x6000,'INIT-ONLY boot clear'
        #1B90 is a shared callee: its one-path finite witness cannot cover all callers.
        if pc==0x1b90:lo,hi,scope=0,0x1000000,'UNRESOLVED other callers; existing1A77-path witness excludes requested cells'
        x.update(target_watch_groups=overlap(lo,hi),target_domain=[lo,hi],target_scope=scope)
        projected.append(x)
        if not e['indirect'] and x['target_watch_groups']:direct_hits.append(x)
    assert direct_hits==[]
    param_hits=[x for x in params if x['space']=='X' and overlap(int(x['address']),int(x['address'])+int(x['words']))]
    # Same parameter map does include descriptor+7, not descriptor+0; exact cells matter.
    assert param_hits==[]
    special_hits=[x for x in special if x['space']=='X' and overlap(int(x['start'],16),int(x['end_exclusive'],16))]
    assert special_hits==[]
    normal_hits=[x for x in normalhost if x['operation']=='write' and x['space']=='X' and overlap(int(x['start'],16),int(x['end_exclusive'],16))]
    assert normal_hits==[]
    emit('writer-ledger.json',dict(status='All recovered canonical X/L operands reprojected; complete actual normal writer set UNRESOLVED',
        watched={k:sorted(v) for k,v in WATCH.items()},entries=projected,direct_absolute_writers=direct_hits,
        source='Existing Phase14 canonical census, data exclusions retained; no new broad alias census',
        unknown_entries=sum(bool(x['target_watch_groups']) and x['target_scope'].startswith('UNRESOLVED') for x in projected)))
    emit('host-and-jobs.json',dict(status='VERIFIED recovered-family exclusions; universal normal endpoints/cursor state UNRESOLVED',
        parameter_hits=param_hits,special_hits=special_hits,normal_constant_suffix_hits=normal_hits,
        largest_recovered_parameter_X=max(int(x['address'])+int(x['words'])-1 for x in params if x['space']=='X'),
        unclosed_callers=unclosedhost,host_argument_records=hostcallers,
        normal_staging=staging,selected_external_stream=stream,reviewed_DMA=dma,worker=worker,
        SHI=dict(writer=0x19d,source='received24-bitX0',destination='X10 viaR0; X11.bit15 clear',
            address_headers=['181..186 private address&7FFF','179..17D18-bit address&3FFFF','171..175 page shifted8 then minus2'],
            count='No DSP-side transfer clamp; X10 incremented after each data word; complete normal endpoint/wrap/cursor retention UNRESOLVED',
            ARM24='292F8→2933A→291E0 sends(r1>>8)&FFFFFF',ARM16='29314→29336 shifts source8, emits(value16<<8)&FFFFFF',
            raw16_can_equal_1E14_or_1E15=False,
            limitation='16-bit exclusion applies to raw target-word publication only, not selector corruption/out-of-domain lookups'),
        service=dict(classification='SERVICE-ONLY recovered request5E',entry='269E4→26A9A→292F8→19D',
            accepted_private_starts=[0,0x8000],value=0,requested_fields_accepted=True,
            mutation='Can replace original nonzero table/descriptor targets with0; no operation performed; no normal target publisher established',
            domain_evidence=utility)))
    emitted=enumerate_conditional(words)
    assert len(emitted)==640 and all(e['final_target']!=0x1e15 for e in emitted)
    fields=['site','row_selector','stage','algorithm_index','table_address','raw_table_value','final_target','wrapper','wrapper_path','scope']
    with (out/'conditional-targets.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(emitted)
    emit('conditional-targets.json',emitted)
    sets={hex(s):sorted({e['final_target'] for e in emitted if e['site']==s}) for s in SITES}
    emit('target-sets.json',dict(status='CONDITIONAL ENUMERATION ONLY; actual normal domains/persistence UNRESOLVED',
        required_domains=dict(X95A=[0,7],X95B_95F=[0,14]),normal_domains=None,normal_targets=None,
        table_persistence='UNRESOLVED',conditional_sets=sets,
        initialized_rows=[dict(row=q,wrappers=words[0x2a05+5*q:0x2a0a+5*q]) for q in range(8)],
        initialized_zero_case=dict(wrapper=0xdf3,call_site=0xdf9,target=0xe19,
            status='INIT-derived0 selector calculation if retained, not executed or proven normal invariant'),
        DC5_DCD='Absent from initialized wrapper rows; no canonical direct entry toDBF/DC7 found; modified/out-of-domain entry not excluded globally'))
    emit('dispatch-formulas.json',dict(status='VERIFIED instructions; closed algebra under legacy linear addressing and reviewed ALU relation',
        wrapper='N2=low24(5*signed24(X95A)); b=(9EA+N2)&FFFFFF; R3=b+i; JMP target=X[b+i]',
        index='k=X[95B+i]; R1=9DB; DAD loadsR0=X[(9DB+signed24(k))&FFFFFF]',
        algorithm='DBD/DC5/DCD: AGU incrementsR0; DEC/DF9: parallel X read postincrementsR0; target=(raw_marker+1)&FFFFFF when legacy linear M0',
        modifiers='M2 row selection, M0 selector-source iteration/marker advance, M1 indexed marker address, M3 wrapper read; actual retained addressing context UNRESOLVED',
        iteration='D99 immediate5; independent stage selectors reloaded via savedX9D9, wrapper pointer viaX9D8 each iteration',
        wrappers=[dict(entry=entry,algorithm_call=pc,path=path) for entry,(pc,path) in ROUTES.items()],
        dataflow_anchors=anchors,
        descriptor='R3=EB+8*i, i0..13 in linear retained descriptor walk; R1=X[R3] at19A5;19AC callsR1; no marker+1'))
    emit('selector-state.json',dict(status='UNRESOLVED exact normal domains; no fabricated selector values',
        cells=[dict(X=a,init_writer=0x2788,init_value=0,
            direct_DSP_writer=None,recovered_ARM_parameter_writer=None,
            normal_value_formula=None,normal_domain=None,normal_trigger=None,
            normal_lifetime='UNRESOLVED foreign/host alias preservation',
            readers=[0xd87] if a==0x95a else [0xda3]) for a in range(0x95a,0x960)],
        required_vs_proven='0..7 and0..14 are table-valid domains, not recovered masks or all-normal producer bounds',
        known_normal_type_macro_patch_source=None))
    emit('table-persistence.json',dict(classification='UNRESOLVED',
        INIT_ONLY=dict(clear=0x2788,copy=[0x29ec,0x29ee,0x29f0,0x29f2,0x29f3],
            P_start=0x29f6,X_start=0x9db,words=55,values=words[0x29f6:0x2a2d]),
        SERVICE_mutation_capability_verified=True,normal_mutation_witness=None,immutable_after_init_proved=False,
        reason='Service zero-write capability established; normal aliases/endpoints remain unclosed, so neither IMMUTABLE nor SERVICE-ONLY MUTABLE is justified',
        normal_known_exclusions=['Recovered bank0/1 parameter destinations max959','fixed mailbox stagingC00..D00, backupC00..E00',
            'workspace2400..2800 and selector7>=1D8D','reviewed audio/DMA/worker mappings, under their preserved-state premises'],
        blocks=['SHI19D normal destination/cursor/endpoint retention','204B positive-count/record destination publication',
            'reused remaining indirect X/L writer context domains'],
        all_actual_writers_closed=False))
    emit('specific-producers.json',[
        dict(PC=0x2788,classification='INIT-ONLY',value=0,destination='X[0,6000)',
            caller='25DE initialization',trigger='DSP initialization/reinitialization',
            lifetime='Replaced by subsequent INIT copies; normal reentry/persistence separate'),
        dict(PC=0x29f3,classification='INIT-ONLY',value='P29F6+j, j0..54',destination='X[9DB,A12)',
            caller='INIT table-copy routine29EC',trigger='Completed initialization',
            lifetime='Mutable RAM; all-normal retention UNRESOLVED'),
        dict(PC=0x19d,classification='NORMAL-PATH/SERVICE transport; actual normal requested-cell endpoint UNRESOLVED',
            value='Received24-bitX0',destination='R0=X10, X11.bit15=0; M0FFFF forced15C; X10 increments',
            callers='ARM292F8 scalar,29314 width, bulk/cached helpers; recovered5E utility SERVICE-ONLY',
            bounds='Header private mask7FFF includes requested cells; full normal cursor/bulk bound UNRESOLVED',
            lifetime='Persistent RAM write until another producer; can interrupt dispatch',
            target_raw16_exclusion='Received low8bits0 excludes1E14/1E15 raw target values only; selectors may exceed nominal domains'),
        dict(PC=0x204b,classification='NORMAL-PATH descriptor202B, positive loop eligibility UNRESOLVED',
            value='B from read/modify/write arithmetic',destination='R4=X[364+5*k]',
            caller='19AC→202B',count='X35F, no positive publisher recovered',
            alias_condition='R4 equals any requested cell; no local destination clamp',
            lifetime='One unindexed X word per record; no supported normal target-producing record'),
        dict(PC=[0x1f6e,0x1f6f,0x1f97],classification='UNRESOLVED normal parent reachability',
            value='0 for initial clears; SYMBOLIC accumulated B at1F97',destination='Y-held cursors; countX3A',
            bounds='Initialized cursor32-word buffers2C02/2C24/2CCC/2CEC exclude requested cells under retained32/linear state',
            selector_alias_base_interval=[0x93b,0x960],table_alias_base_interval=[0x9bc,0xa12],
            alias_premise='32 consecutive X addresses,24-bit linear; intervals are forbidden alias bases, NOT recovered normal values',
            lifecycle='No cursor writeback in qualified helper; foreign cursor/base/count/modifier closure UNRESOLVED'),
        dict(PC=0x2030,classification='NORMAL-PATH descriptor202B',value=0,
            destination='X[967,98D),38-word fixed clear under legacy linearM1',
            requested_cells_overlap=False,lifetime='Per descriptor invocation; context/modifier retention premise explicit'),
        dict(PC=[0x289a,0x28bc,0x28c9],classification='INIT-ONLY',
            destination='Descriptor+0 EB+8*i, i0..13',value='12×281,202B,1A2B',
            requested_effect_fields_overlap=False,lifetime='All-normal descriptor+0 retention UNRESOLVED')])
    emit('descriptor0.json',dict(status='UNRESOLVED all-normal retention; VERIFIED INIT/default and recovered event exclusion',
        cells=[dict(X=0xeb+8*i,init=0x281 if i<12 else 0x202b if i==12 else 0x1a2b,
            INIT_writer=0x289a if i<12 else 0x28bc if i==12 else 0x28c9) for i in range(14)],
        normal_event='ARM21A08 updatesF2+8*i (+7), notEB+8*i (+0), i0..11; interval hulls would give false overlap',
        raw_target_increment=False,target_1E15='NOT-YET-DETERMINED',normal_value_1E15_producer=None,
        remaining='Generic host/DSP indirect aliases and descriptor addressing retention; not whole descriptor reanalysis'))
    emit('patch-preset-relation.json',dict(status='UNRESOLVED universal transition closure',
        recovered_patch_parameter=dict(effect_state_hit=False,source='Phase9 bank0/1 parameter map and deferred special destinations'),
        recovered_table_jobs=dict(effect_state_hit=False,source='Phase12 staging/backup/workspace/selector7 footprints'),
        INIT_reentry='2788 clear then29F3 table copy would reestablish defaults if completed; not a normal patch mutation witness',
        project_session='No exact normal selector/target rewrite established; complete indirect ancestry and cached/bulk retention not closed',
        UI_macro_effect_type='No recovered publisher to requested cells; semantic names not assigned from proximity',
        service='5E private zero writes are SERVICE-ONLY, not an ordinary effect preset publisher'))
    conclusions=[dict(site=s,normal_select_1E15='NOT-YET-DETERMINED',
        conditional_valid_table_select_1E15='VERIFIED NO',conditional_targets=sets[hex(s)]) for s in SITES]
    emit('result.json',dict(status='C: normal reachability remains UNRESOLVED',site_results=conclusions,
        descriptor_19AC='NOT-YET-DETERMINED',normal_target_producer=None,parent_executed_instructions=0,
        table_classification='UNRESOLVED',single_remaining_producer=None,
        single_producer_not_established='Multiple independent open obligations remain: SHI19D and204B plus reused generic X/L address contexts; no honest single-producer reduction',
        priority_producer='P19D normal SHI write destination/cursor state',effect_chain_removed_from_normal_hypothesis=False,
        active_D99_replay_justified=False,authentic_boot=False,Plaits_implementation=False,
        best_next_step='Close normal ARM scalar/width/bulk endpoint and cursor-retention provenance into SHI19D for requested selector/table/descriptor0 cells; preserve independent204B obligation'))
    windows=[(0xd87,0xe80),(0x156,0x1b4),(0x202b,0x204c),(0x2779,0x278a),(0x2881,0x28d3),(0x29ec,0x29f6)]
    with (out/'dsp-witnesses.asm').open('x',encoding='utf-8',newline='\n') as f:
        for pc,e in r.items():
            if any(a<=pc<b for a,b in windows):f.write(e['line']+'\n')
    with (out/'arm-witnesses.asm').open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(armw)+'\n')
    for p in protected:inputs[p.relative_to(ROOT).as_posix()]=sha(p.read_bytes())
    for n in ['tools/ct_effect_target_bridge.py','emulator/tests/test_target_bridge.py','emulator/tests/verify_target_bridge.py']:read(n)
    verify_inputs()
    for n,h in inputs.items():assert sha((ROOT/n).read_bytes())==h,n
    emit('provenance.json',dict(inputs=inputs,offline=True,codec_roundtrip=True,all_ten_extract_hashes=True,
        no_CPU_or_packets=True,all_actual_writers_closed=False))
    emit('hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
    print('640 conditional target records; normal bridge UNRESOLVED;0 DSP instructions; '+str(out))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',required=True,type=Path)
    collect(ap.parse_args().output_dir)
