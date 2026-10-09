#!/usr/bin/env python3
"""Offline Phase-8 evidence replay and conservative allocation search.

No firmware execution, hardware, compilation or modification. Reviewed formulas
are explicit analyst inputs, not an automatic whole-program points-to proof.
Unknown reachability/bounds block availability; absence of literals never proves it.
All exports require a fresh output directory and are exclusive-create.
"""
import argparse, csv, io, json, re, struct
from pathlib import Path
from ct_static import ROOT, BASE, BIN_HASH, SYX_HASH, sha, save
from ct_phase4_trace import arm_evidence
from ct_resource_audit import read_rows
from ct_memory_ownership import affine_loop
import ct_fw_tool

CANDIDATES = {'X': (0x4000, 0x6000), 'Y': (0x3000, 0x4000)}

def csv_text(rows):
    s = io.StringIO()
    keys = sorted(set().union(*(r.keys() for r in rows))) if rows else ['status']
    w = csv.DictWriter(s, fieldnames=keys)
    w.writeheader(); w.writerows(rows)
    return s.getvalue()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', required=True)
    out = Path(p.parse_args().output_dir).resolve()
    if out.exists(): raise SystemExit('Choose a fresh output directory')
    if out == ROOT/'original' or ROOT/'original' in out.parents:
        raise SystemExit('Protected original/')
    arm = (ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    syxp = ROOT/'original/circuittracks-firmware-4486.syx'
    syx = syxp.read_bytes()
    assert sha(arm) == BIN_HASH and sha(syx) == SYX_HASH
    decoded = ct_fw_tool.decode_syx(syxp)
    assert decoded['firmware'] == arm
    assert ct_fw_tool.build_syx(syxp, arm) == syx
    inputs = []
    def checked(path):
        data = path.read_bytes()
        inputs.append({'path':path.relative_to(ROOT).as_posix(), 'sha256':sha(data)})
        return data
    checked(Path(__file__).resolve())
    arm_reports = sorted((ROOT/'builds').glob('phase8-*.asm'))
    for path in arm_reports:
        count = arm_evidence(path, arm)
        checked(path); inputs[-1]['byte_checked_instructions'] = count
        save(out/'evidence'/path.name, path.read_bytes())
    for path in sorted((ROOT/'builds').glob('phase8-*.json')):
        checked(path); save(out/'evidence'/path.name, path.read_bytes())
    for name in ['phase3-arm-params.asm','phase3-arm-note-params.asm']:
        path=ROOT/'builds'/name; arm_evidence(path,arm); checked(path)
    manifest = json.loads(checked(ROOT/'firmware/dsp/build-4486/manifest.json'))
    programs = {}
    for b in manifest['blocks']:
        for field, hfield in [('stream_file','stream_sha256'),('payload_file','payload_sha256')]:
            data = checked(ROOT/'firmware/dsp/build-4486'/b[field])
            assert sha(data) == b[hfield]
        start=int(b['source_offset'],16)
        assert arm[start:start+b['stream_size']] == (ROOT/'firmware/dsp/build-4486'/b['stream_file']).read_bytes()
        if b['name'] in ('selection0-channel0','selection0-channel1'):
            path=ROOT/'builds'/('phase3-'+b['name']+'.asm')
            checked(path)
            programs[b['name']]=read_rows(path,data)
    source_manifest=json.loads(checked(ROOT/'plaits/upstream/source-manifest.json'))
    for f in source_manifest['files']:
        data=(ROOT/'plaits/upstream'/f['path']).read_bytes()
        assert len(data)==f['size'] and sha(data)==f['sha256']
    # Zero-fill scatter descriptor: signed callback offset from descriptor address.
    rel, length, dest, terminator=struct.unpack_from('<IIII',arm,0x4b7b4)
    signed=rel if rel<0x80000000 else rel-0x100000000
    assert (0x805b7b4+signed,length,dest,terminator)==(0x801a7eb,0x2d50,0x20003d04,0)
    assert dest<=0x20006800<dest+length
    init={'status':'VERIFIED INIT-ONLY','descriptor':'0x0805B7B4',
          'raw_hex':arm[0x4b7b4:0x4b7c4].hex(),'callback':'0x0801A7EA (Thumb pointer +1)',
          'ARM_zero_interval':['0x20003D04','0x20006A54'],
          'selector_boot_value':0,'secondary_clear':'08021098 STRH zero to parent+4; also clears slot byte',
          'DSP_clear':'P:2786 DO 6000, X/Y stores at 2788/2789: [0,6000); INIT-ONLY, not runtime exclusion'}
    writes=[
        {'site':'08021098','kind':'STRH parent+4','value':'0','mode':'BOOT / reinitialization ancestry unresolved'},
        {'site':'08021496','kind':'STRB parent+4','value':'low byte of incoming r0','mode':'parameter callbacks',
         'bounded_witness':'080214BE calls with 0,1; 0804966E inherits 49634 input'},
        {'site':'0804963A','kind':'STRB direct','value':'low byte of incoming r0',
         'bounded_witness':'0803BE0C/0E and BE16/18 supply 0,1; indirect ancestry unresolved'},
        {'site':'0804978C','kind':'STRB direct','value':'low byte incoming r0; 0x10 returns before store',
         'mode':'channel/event routing; complete normal/service domain UNRESOLVED'},
        {'site':'0804982C','kind':'STRB direct','value':'low byte incoming r0; 0xFF/0x10 special branches bypass store',
         'mode':'channel/event routing; complete normal/service domain UNRESOLVED'}]
    table=[struct.unpack_from('<I',arm,0x4a384+4*i)[0] for i in range(16)]
    assert table[6]==0x8027a11
    callbacks=[{'index':i,'table_address':f'0x{0x805a384+4*i:08X}',
                'Thumb_pointer':f'0x{v:08X}','entry':f'0x{v&~1:08X}'} for i,v in enumerate(table)]
    bank={'status':'VERIFIED partial domain, UNRESOLVED global normal invariant',
          'address':'0x20006800','parent':'0x200067FC +4','distinct_slot':'0x20006801 (+5)',
          'conservative_byte_domain':[0,255],'global_normal_0_1_proved':False,
          'initialization':init,'reviewed_mutations':writes,
          'reviewed_direct_literal_reads':'25 load candidates; raw pointer and alias scans in evidence/',
          'bounded_use_site':'08021D9A AND 1; write at 21DA2 targets X:9D or X:9E',
          'callbacks':'0802148C stores selector before 16-entry indirect dispatch; slot 6 -> 08027A10',
          'caveat':'not an exhaustive alias/indirect-write proof; wider values are abstract possibilities, not proved normal inputs'}
    # Complete destinations of the reviewed 27A10 local loop, not its callees.
    # Twenty records, stride five; words +0,+1,+2,+4 are written, +3 skipped.
    bank_addresses=[]
    for b in range(256):
        locations=[(0x2fb+0x172*b+5*i+j, f'record {i} field +{j}')
                   for i in range(20) for j in (0,1,2,4)]
        locations += [(0x3d0+0x172*b+i, f'tail {i}') for i in range(20)]
        for raw,field in locations:
            encoded=raw&0xffff; sp='Y' if encoded&0x8000 else 'X'; addr=encoded&0x7fff
            lo,hi=CANDIDATES[sp]
            bank_addresses.append({'bank':b,'space':sp,'address':f'0x{addr:X}',
               'encoded_argument':f'0x{encoded:04X}','field':field,
               'candidate_overlap':lo<=addr<hi,
               'status':'VERIFIED formula; abstract byte-domain enumeration, NOT runtime witness',
               'bounded_0_1_witness':b in (0,1)})
    assert next(x for x in bank_addresses if x['bank']==64)['address']=='0x5F7B'
    blockers=[
      {'id':'HOST-BANK','spaces':'X/Y','origin':'20006800; 08049758/497CA -> channel thunks 08029A08/29A12',
       'access':'08027A10 bank*172+2FB, 20*5 records plus tail bank*172+3D0',
       'missing':'normal parameter-callback ancestry and selector invariant; wider writers not classified SERVICE-ONLY',
       'range':'abstract enumeration in bank-destinations.csv; not actual normal occupancy'},
      {'id':'HOST-OTHER','spaces':'X/Y','origin':'Phase6C final host-callers.json and unresolved-host-intervals.csv',
       'access':'computed, cached and bulk helpers including 292F8/29314/29528',
       'missing':'complete normal caller arguments, base/count and mode exclusion', 'range':'unknown; may overlap either entire candidate'},
      {'id':'MAILBOX','spaces':'X/Y','origin':'P:1C53..1C5F r5=((Y:2C & 7FFFF0)<<1)&FFFFFF',
       'access':'normal selectors 0/2/3/4/5; others lack normal reachability proof',
       'missing':'full multistage bounds and retained X:1B16 destination lifetime',
       'range':'reviewed normal external bases do not overlap; complete exclusion unresolved'},
      {'id':'DSP-EFFECT','spaces':'X/Y','origin':'P:CE2..CED ->1157; Y:7FE ->n7; scaled parameter ->X:9B1+n2',
       'access':'variable pointer/index effect processing beyond bounded CC4/CD7 prefixes',
       'missing':'coefficient index bounded separately; remaining retained buffer pointer/modifier/helper bounds', 'range':'may overlap candidates; no actual overlap witness'},
      {'id':'DSP-TABLE','spaces':'X/Y','origin':'P:1E15 saves r6/r7 ->X:1D3A/1D3B; P:1E33/1EC2/1EED reload',
       'access':'table/transform work using retained pointers',
       'missing':'entry mode, pointer origins and all loop extents; not proven normal audio occupancy',
       'range':'unknown; cannot classify SERVICE-ONLY or exclude either candidate'},
      {'id':'QUEUE','spaces':'X','origin':'normal P:7C8 variable repeat count, endpoints 81B/876/8D5/917/954; worker P:114/120/126',
       'access':'queue X:30002 onward; worker queued fetch pointer at P:125',
       'missing':'all producer counts/endpoints, wrap prevention and queued source value bounds',
       'range':'selected profile shared-only; aggregate maximum unresolved; private-core low addresses not aliases'},
      {'id':'DMA','spaces':'X/Y','origin':'P:2A2D..2A3D setup, 1BC/1BE rearm',
       'access':'reviewed DMA staging X:21/Y:29; normal rings [1000,1400)',
       'missing':'complete register-writer census, DCR space/stride decoding and indirect reconfiguration exclusion',
       'range':'no reviewed candidate destination; global asynchronous exclusion not proved'},
      {'id':'SAVE-SCRATCH','spaces':'X/Y','origin':'indirect-origins.csv and stack-register inventory',
       'access':'software save/scratch pointers; hardware return stack is separate architectural storage',
       'missing':'all helper save/scratch footprints and maximum nested call/interrupt depth',
       'range':'hardware-stack terminology alone does not reserve X/Y; software bounds unresolved'}]
    # These are uncertainty envelopes, NOT actual full-space-access claims.
    exclusions=[]
    for b in blockers:
        for sp,(lo,hi) in CANDIDATES.items():
            if sp in b['spaces']:
                exclusions.append({'id':b['id'],'space':sp,'start':lo,'end':hi,
                    'status':'UNRESOLVED exclusion over candidate; NOT verified occupied'})
    # No unknown exclusion is treated as empty. Probe every word-aligned start.
    searches=[]
    for sp,(lo,hi) in CANDIDATES.items():
        for n in (64,128,256,512,1024):
            accepted=[]; blocking=set()
            for start in range(lo,hi-n+1):
                overlap=[e['id'] for e in exclusions if e['space']==sp
                         and start<e['end'] and start+n>e['start']]
                blocking.update(overlap)
                if not overlap: accepted.append(start)
            assert not accepted  # This version cannot close global exclusions.
            searches.append({'space':sp,'words':n,'candidate_starts_considered':hi-lo-n+1,
                'verified_starts':len(accepted),'answer':'NOT-YET-DETERMINED',
                'status':'all starts blocked by unresolved interprocedural exclusions; not proven occupied',
                'blocking_ids':','.join(sorted(blocking))})
    ch0=programs['selection0-channel0']; ch1=programs['selection0-channel1']
    assert ch0[0x1166]['text']=='move #>$000013,y0'
    assert ch0[0x1168]['text']=='mpy +y0,x0,b'
    assert ch0[0x116a]['text']=='move b1,n2'
    index_min=(-(1<<23)*19)//(1<<23)
    index_max=(((1<<23)-1)*19)//(1<<23)
    assert (index_min,index_max)==(-19,18)
    coefficient={'status':'VERIFIED ISA-derived arithmetic; address bounds conditional on linear M2',
       'evidence':'P:1166 y0=19;1168 signed fractional MPY;116A direct B1 ->n2; alternate branch uses3 from1160',
       'formula':'n2=floor(19*signed24(x0)/2^23)', 'n2_min':index_min,'n2_max':index_max,
       'linear_X_interval':['0x99E','0x9C4'],
       'reference':'https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf sections3.1.2/3.1.3',
       'caveat':'B1 direct transfer is unscaled; this does not bound subsequent retained circular buffer pointers'}
    effect=[]
    for row in affine_loop(ch0,0xcc6,0xccf,32,
            {'r0':0x2ef0,'r1':0x1bb2,'r2':0x1bf2,'r4':0x840,'r5':0x880,'r6':0x9c0},
            status='VERIFIED conditional selected N=32 / linear AGU'):
        row['mode']='NORMAL AUDIO selected N=32 / linear AGU'
        row['premise']='P:CB8..CC2 immediate bases; X:3A=32 init-derived; legacy linear AGU; script explicit inputs'
        effect.append(row)
    stack=[{'pc':f'P:{pc:06X}','instruction':r['text'],
            'status':'lexical inventory, may include decoded data; not depth/occupancy proof'}
           for pc,r in ch0.items() if re.search(r'\b(?:ssh|ssl|sp|sc|la|lc)\b',r['text'])]
    dma=[]; direct_candidates=[]
    for pc,r in ch0.items():
        for sp,address in re.findall(r'([xy]):\$([0-9a-fA-F]+)',r['text']):
            a=int(address,16);lo,hi=CANDIDATES[sp.upper()]
            if lo<=a<hi:
                direct_candidates.append({'pc':f'P:{pc:06X}','space':sp.upper(),
                    'address':hex(a),'instruction':r['text'],'status':'decoded operand only; reachability unproved'})
            if sp=='x' and 0xffffd8<=a<0xfffff0:
                dma.append({'pc':f'P:{pc:06X}','register':hex(a),'instruction':r['text'],
                    'status':'canonical decoded DMA-register operand inventory; reachability/reconfiguration not closed'})
    dsp_windows=[(0x1b4,0x1d9),(0x759,0x77f),(0x7a7,0x7ce),(0xcb8,0xcf0),
                 (0x1157,0x1195),(0x1c53,0x1ccc),(0x1e15,0x1e45),(0x1ec2,0x1ef8),
                 (0x2779,0x278b),(0x2a2d,0x2a40)]
    lines=[r['line'] for pc,r in sorted(ch0.items()) if any(a<=pc<b for a,b in dsp_windows)]
    lines += ['','; Selection0/channel1 worker']+[r['line'] for pc,r in sorted(ch1.items()) if 0x100<=pc<0x134]
    inherited={}
    for name in ['normal-host-intervals.csv','normal-dsp-intervals.csv','unresolved-host-intervals.csv','mailbox-witnesses.json']:
        path=ROOT/'builds/phase6c/final'/name; checked(path)
        save(out/'inherited'/name,path.read_bytes()); inherited[name]='unchanged partial evidence; not complete normal ranges'
    gates={k:'NOT-YET-DETERMINED' for k in ['RAM64','RAM128','RAM256','RAM512','RAM1024','host_exclusion','DSP_worker_DMA_exclusion','persistence','coexistence_with_output']}
    gates.update({'persistent_RAM_still_primary_blocker':'YES','implementation_ready':'NO'})
    result={'status':'UNRESOLVED allocation proof; static study only','bank':bank,
      'candidates':[{'space':sp,'start':hex(lo),'end_exclusive':hex(hi),'classification':'POTENTIALLY AVAILABLE / UNRESOLVED after-init exclusions','initialization':'INIT-ONLY clear'} for sp,(lo,hi) in CANDIDATES.items()],
      'largest_VERIFIED_AVAILABLE_AFTER_INIT_words':{'X':0,'Y':0},'chosen_allocation':None,
      'zero_meaning':'zero words proven available, NOT zero words physically available',
      'gates':gates,'worker':{'queue_start':'X:30002','selected_12_voice_endpoint':'X:30902 (192 requests/voice profile only)',
      'modifier':'00FFFF is legacy linear 24-bit addressing when SR.EMA=0; not a shared-RAM modulo ring',
      'architectural_condition':'DSP56300FM 4.5.1; DSP56724RM SR EMA bit18 reset0; actual mode/global SR writes not closed',
      'domain':'shared [30000,38000) P/X/Y aliases under conditional part map; private low X/Y per core separate',
      'maximum_endpoint':None},
      'output':{'stock_scratch':'X:[2C46,2C66)','readable_neighbor':'X:2C66',
      'classification':'VERIFIED RUNTIME OCCUPIED scratch, not persistent',
      'direct_render':'HYPOTHESIS possible within serial completion lifetime; numeric/live-state/guard ABI unresolved',
      'extra_32_word_buffer_required':'not required by primitive source; adapter requirement UNRESOLVED'},
      'resources':{'P_code':'separate; translated word count/placement unresolved','persistent_X_Y':'no allocation proved',
      'tables':'SOURCE-DERIVED primitive has no lookup dependency with validated normalized frequency; pitch conversion separate',
      'scalar_payload':'SOURCE-DERIVED six floats plus bool; 25 payload bytes excluding ABI; 13 word illustration for bit-preserving floats',
      'planning_words':256,'planning_not_requirement':True},
      'integrity':{'SYX':sha(syx),'BIN':sha(arm),'decoded_equals_BIN':True,'roundtrip_identical':True,
      'crc':f"0x{decoded['crc']:08X}",'DSP_streams_checked':len(manifest['blocks']),
      'Plaits_source_files_checked':len(source_manifest['files'])},
      'coefficient_index':coefficient,
      'inventory_counts':{'direct_high_candidate_operands':len(direct_candidates),
       'DMA_register_operands':len(dma),'hardware_stack_register_operands':len(stack)},
      'inventory_caveat':'canonical listing may decode data; no absolute high operand is not a free-memory proof',
      'inherited':inherited}
    save(out/'audit.json',json.dumps(result,indent=2)+'\n')
    save(out/'bank-writes.csv',csv_text(writes))
    save(out/'parameter-callbacks.csv',csv_text(callbacks))
    save(out/'bank-destinations.csv',csv_text(bank_addresses))
    save(out/'bounded-effect-intervals.csv',csv_text(effect))
    save(out/'coefficient-index-bound.json',json.dumps(coefficient,indent=2)+'\n')
    save(out/'allocation-search.csv',csv_text(searches))
    save(out/'candidate-exclusion-envelopes.csv',csv_text(exclusions))
    save(out/'unresolved-exclusions.csv',csv_text(blockers))
    save(out/'stack-register-inventory.csv',csv_text(stack))
    save(out/'DMA-register-inventory.csv',csv_text(dma))
    save(out/'direct-candidate-operands.csv',csv_text(direct_candidates))
    save(out/'reviewed-dsp.asm','\n'.join(lines)+'\n')
    save(out/'input-integrity.json',json.dumps(inputs,indent=2)+'\n')
    print(json.dumps({'output':str(out),'integrity':result['integrity'],'gates':gates},indent=2))

if __name__=='__main__': main()
