#!/usr/bin/env python3
"""Phase14 single-word static writer ledger, not an emulator/points-to proof.

Enumerates X and conservatively L stores in byte-checked canonical listings,
retains unknown aliases and candidate data, and records scoped zero-preserving
and finite-address witnesses. Existing reports are inputs, not refetched work.
"""
import argparse,csv,io,json,re,struct
from pathlib import Path
from ct_static import ROOT,BASE,BIN_HASH,SYX_HASH,sha,save
from ct_resource_audit import read_rows
import ct_fw_tool

# These boundaries are established by existing instruction-derived copy/RLE
# reports. They are excluded as DATA, never used as executable writer witnesses.
DATA=[(0x146A,0x14EF),(0x2309,0x2599),(0x262C,0x2644),
      (0x268C,0x2717),(0x2720,0x2779),(0x28DD,0x29EC),(0x29F6,0x2A2D)]

ZERO={0x29E:'A cleared29C; no intervening A definition',
      0x2D2:'B cleared2CA; fixed6 clear loop',
      0x75F:'A cleared759; loop only stores',0x760:'A cleared759; loop only stores',
      0x1F6E:'A cleared1F66;32 clear iterations under stock count',
      0x1F6F:'A cleared1F66;32 clear iterations under stock count',
      0x2030:'X0=0 at202D;38 clear iterations',
      0x20B5:'old B cleared20B3; parallel tfr updates after store',
      0x20CC:'B=0 at20C9; branch to20CC does not alter B',
      **{p:'A cleared208A; only stores in loop' for p in range(0x2092,0x2098)},
      0x25EE:'X0=0 at25EB;8 INIT stores',
      0x2788:'X0=0 at2783; INIT6000-word clear',
      0x2791:'X0=0 at278C; INIT8000-word shared clear',
      **{p:'X0=0 at28B9; no subsequent X0 producer in descriptor initialization'
         for p in [0x28C0,0x28C1,0x28CA,0x28CB,0x28CC,0x28CD,0x28CE,0x28CF]}}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',required=True)
    out=Path(ap.parse_args().output_dir).resolve()
    if out.exists():raise SystemExit('Choose a fresh output directory')
    if out==ROOT/'original' or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    def emit(name,obj):save(out/name,json.dumps(obj,indent=2,sort_keys=True)+'\n')
    inputs={}
    def read(name):
        p=ROOT/name;raw=p.read_bytes();inputs[name]=sha(raw);return raw
    arm=read('firmware/circuittracks-firmware-4486.bin')
    syx=read('original/circuittracks-firmware-4486.syx')
    assert sha(arm)==BIN_HASH and sha(syx)==SYX_HASH
    syxp=ROOT/'original/circuittracks-firmware-4486.syx'
    assert ct_fw_tool.decode_syx(syxp)['firmware']==arm
    assert ct_fw_tool.build_syx(syxp,arm)==syx
    manifest=json.loads(read('firmware/dsp/build-4486/manifest.json'))
    for block in manifest['blocks']:
        for kind in ('stream','payload'):
            raw=read('firmware/dsp/build-4486/'+block[kind+'_file'])
            assert sha(raw)==block[kind+'_sha256']
    payload=read('firmware/dsp/build-4486/selection0-channel0.payload24.bin')
    listing='builds/phase3-selection0-channel0.asm';read(listing)
    rows=read_rows(ROOT/listing,payload)
    def require(pc,t):assert rows[pc]['text']==t,(hex(pc),t)
    for pc,t in {0x29C:'clr a',0x2CA:'clr b x:$0029,r7',
      0x759:'clr a #$002df0,r0',0x1F66:'clr a #$fffffc,n5',
      0x2035:'asr a #$00035f,r0',0x203A:'move x:(r0)+,x1',
      0x2040:'do x1,$204c',0x204B:'move b,x:(r4)',
      0x1F89:'move y:>(r6+32),r7',0x1F97:'move b,x:(r7)+',
      0x198:'move x:$0010,r0',0x19D:'move x0,x:(r0)+',
      0x15C:'movec #$00ffff,m0',0x1B1:'movec y:$2002,m0',
      0x19AC:'jsr (r1)',0x28AC:'move #$00202b,r2',
      0x20B3:'clr b x:(r1),x0',0x20C9:'cmp x0,b #$00,b',
      0x208A:'clr a #$002e70,r0',0x28B9:'move #$00,x0',
    }.items():require(pc,t)
    # Operand positions preserve parallel moves: comma precedes write target;
    # bit RMW operands are writes, too. L is retained conservatively, not silently
    # omitted. No machine-code instruction decoding is invented here.
    transfers=re.compile(r',([xl]):((?:>)?\([^)]*\)(?:[+-](?:n[0-7])?)?|\$[0-9a-f]+)')
    bits=re.compile(r'\b(bset|bclr|bchg)\s+#[0-9]+,([xl]):((?:>)?\([^)]*\)(?:[+-](?:n[0-7])?)?|\$[0-9a-f]+)')
    census=[];excluded=[];direct=[]
    for pc,row in sorted(rows.items()):
        t=row['text'];operands=[(m[1],m[2]) for m in transfers.finditer(t)]
        for m in bits.finditer(t):
            if (m[2],m[3]) not in operands:operands.append((m[2],m[3]))
        for space,operand in operands:
            record={'PC':hex(pc),'space':space.upper(),'operand':operand,'instruction':t}
            if any(a<=pc<b for a,b in DATA):
                excluded.append(dict(record,status='VERIFIED DATA exclusion'));continue
            indirect='(' in operand
            record.update(indirect=indirect,mode='UNRESOLVED normal reachability unless reviewed witness supplied',
                minimum_address='0x0' if indirect else operand.removeprefix('$'),
                maximum_address='0xFFFFFF' if indirect else operand.removeprefix('$'),
                base='UNRESOLVED' if indirect else operand,
                pointer_source='UNRESOLVED' if indirect else 'instruction absolute operand',
                modifier='UNRESOLVED' if indirect else 'unindexed absolute',
                loop_count='UNRESOLVED',domain_status='conservative24-bit envelope, NOT proved attainable extrema' if indirect else 'literal address',
                reaches_35F='UNRESOLVED' if indirect else int(operand[1:],16)==0x35F,
                zero_invariant_effect='UNRESOLVED possible nonzero write' if indirect else 'nonalias' if int(operand[1:],16)!=0x35F else 'UNRESOLVED')
            if pc in ZERO:
                record['zero_invariant_effect']='VERIFIED zero-preserving under reviewed local producer/entry'
                record['value']=0;record['value_proof']=ZERO[pc]
            elif t.startswith('bclr '):
                record['zero_invariant_effect']='VERIFIED bit-clear preserves a zero word, even on alias'
            elif pc==0x204B:
                record['zero_invariant_effect']='conditional cannot be first violator:203A reads35F=0 and DO skips'
            if indirect:
                reg=re.search(r'r[0-7]',operand)[0]
                record['modifier']=reg.replace('r','m')+'; value UNRESOLVED globally'
                # A bounded lexical hint is not promoted to flow-sensitive proof.
                for prior in sorted((p for p in rows if max(0,pc-40)<=p<pc),reverse=True):
                    text=rows[prior]['text']
                    if re.search(r','+reg+r'(?:\s|$)',text):
                        record['lexical_pointer_hint']=hex(prior)+': '+text;break
            census.append(record)
            if not indirect and int(operand[1:],16)==0x35F:direct.append(record)
    assert not direct,'Unexpected absolute count writer; review before updating result'
    # Reviewed address witnesses. Assertions anchor paths; inequalities retain
    # the existing stock-count and AGU premises rather than invent global bounds.
    intervals={
      0x120:(0x60,0x68,'main-loop8 stores; R0=60, legacy linear M0'),
      **{p:(0x39,0x42,'140 setsR0=39;9 sequential stores, legacy linear M0')
         for p in [0x146,0x148,0x149,0x14A,0x14B,0x14E,0x151,0x153,0x154]},
      0x1BC8:(0,1,'1BC2 R3=0, no update; conservative L-store inclusion'),
      0x1BE0:(0,1,'1BC2 R3=0, no update; conservative L-store inclusion'),
      0x1D32:(0x1B16,0x1B21,'1D26 R2=1B16;11-word context save, linear M2'),
      **{p:(0x1B16,0x1B21,'1D26 R2=1B16;11-word context save, linear M2') for p in range(0x1D33,0x1D3D)},
      0x1CD7:(0xC00,0xE00,'1CD0 backup loop512, linear M1'),
      0x1CE4:(0xC00,0xE00,'1CD9 backup transform512, linear M1'),
      0x1CF2:(0xC00,0xE00,'1CE6 backup transform512, linear M1'),
      0x1CC7:(0x1D8D,0x1E8C,'recovered selector7 index0..63;3 stores, legacy linear M1'),
      0x1B90:(0x2FE,0x35E,'ONLY call1A77:20 stores stride5; last35D. Other helper callers separate'),
      0x1BF3:(0x1E,0x20,'recovered normal bank0/1; R0=1E+bank, no postincrement'),
      0x1BFF:(0x20,0x22,'recovered normal bank0/1; R0=20+bank, no postincrement'),
      0x271E:(0x1EDD,0x1F68,'INIT copy139 words; R1=1EDD'),
      0x2622:(0x1D53,0x1D63,'INIT8*2 copied words'),0x2623:(0x1D53,0x1D63,'INIT8*2 copied words'),
      0x262A:(0x7D,0x85,'INIT8 words R1=7D'),
    }
    for item in census:
        pc=int(item['PC'],16)
        if pc in intervals:
            lo,hi,premise=intervals[pc];item['reviewed_witness']={'start':hex(lo),'end_exclusive':hex(hi),
                'contains_35F':lo<=0x35F<hi,'status':'VERIFIED conditional reviewed address witness','premises':premise}
            # Avoid claiming the shared helper's other calls inherit one bound.
            if pc!=0x1B90:
                item.update(minimum_address=hex(lo),maximum_address=hex(hi-1),base=hex(lo),
                    pointer_source=premise,domain_status='VERIFIED conditional witness; global entry/state preservation unresolved',
                    reaches_35F='VERIFIED NO under stated premises')
    emit('DSP-X-L-write-census.json',{'scope':'all recognized write operands in canonical channel0 listing after listed DATA exclusions; code/entry closure unresolved',
          'data_exclusions':[[hex(a),hex(b)] for a,b in DATA],'entries':census,
          'absolute_X35F_writers':direct,'zero_preserving_sites':[hex(p) for p in sorted(ZERO)],
          'indirect_operand_count':sum(r['indirect'] for r in census)})
    emit('excluded-data-writes.json',excluded)
    indirect=[r for r in census if r['indirect']]
    possible=[r for r in indirect if r['reaches_35F']=='UNRESOLVED']
    emit('possible-indirect-aliases.json',{'scope':'possible by unclosed domains, not normal reachability witnesses',
       'entries':possible,'count':len(possible),'zero_preserving_not_counterexamples':True})
    worker_listing='builds/phase3-selection0-channel1.asm';read(worker_listing)
    worker_payload=read('firmware/dsp/build-4486/selection0-channel1.payload24.bin')
    worker_rows=read_rows(ROOT/worker_listing,worker_payload)
    worker_stores=[]
    for pc,row in worker_rows.items():
        operands=[(m[1],m[2]) for m in transfers.finditer(row['text'])]
        operands+=[(m[2],m[3]) for m in bits.finditer(row['text']) if (m[2],m[3]) not in operands]
        for space,operand in operands:
            assert operand!='$035f'
            worker_stores.append({'PC':hex(pc),'space':space.upper(),'operand':operand,'instruction':row['text'],
                'domain':'shared queue cursor R5, initial30002 or loadedX30000; M5FFFF; countA1 from endpoint-cursor difference' if pc==0x126 else 'fixed peripheral/shared address',
                'count_word_alias':'no absolute35F writer; private channel/core and shared mapping premise retained; queue producer/extent closure unresolved'})
    emit('worker-write-census.json',{'program':'Selection0/channel1','entries':worker_stores,
        'private_spaces':'do not merge numerically matching addresses with channel0 privateX without a physical alias proof',
        'scope':'byte-checked separate-program store census; not a worker capacity/persistence proof'})
    # Existing exact normal ARM address map remains the narrow trusted domain.
    pmap='builds/phase9/verified/parameter-writes.csv'
    parameter=list(csv.DictReader(io.StringIO(read(pmap).decode())))
    hits=[r for r in parameter if r['space']=='X' and int(r['address'])==0x35F]
    assert len(hits)==1 and '286BC' in hits[0]['helper']
    record_hits=[r for r in parameter if r['space']=='X' and 0x360<=int(r['address'])<0x3C4]
    assert not record_hits
    arm_evidence=[]
    for directory in sorted((ROOT/'builds/phase14').glob('arm-*')):
        for path in sorted(directory.glob('*.asm')):
            read(str(path.relative_to(ROOT)))
            for line in path.read_text().splitlines():
                m=re.match(r'([0-9A-F]{8})\s+([0-9a-f]+)\s+(.*)',line)
                if m:
                    pc=int(m[1],16);raw=bytes.fromhex(m[2]);assert arm[pc-BASE:pc-BASE+len(raw)]==raw
                    arm_evidence.append(line)
    save(out/'arm-witnesses.asm','\n'.join(arm_evidence)+'\n')
    def u32(a):return struct.unpack_from('<I',arm,a-BASE)[0]
    assert u32(0x8020940)==0x2740C and u32(0x8035670)==0x20006990
    assert u32(0x803A2BC)==0x20006990
    stream_bytes=0x2740C;stream_words=stream_bytes//2
    stream_start=0xE80000;stream_end=stream_start+stream_words
    assert stream_end==0xE93A06 and stream_end<0x1000000
    emit('host-stream-count-proof.json',{
       'initializer':'208F8 buffer pointer;208FA literal20940=2740C bytes;208FC→355E8',
       'record':'20006990;355EC reads literal35670;355F2→47C54',
       'setter':'47C54 tests MINIMUM25800, NOT maximum;47C62 stores pointer;47C64 stores length',
       'consumer':'395E0 literal3A2BC;395E4 reads record+4→r2;395E8 r0=E80000;395EC→48DAA',
       'bytes':stream_bytes,'16_bit_DSP_words':stream_words,
       'initial_pointer_after_page_compensation':'0xE7FFFE','prefill_words':2,
       'payload_start':hex(stream_start),'end_exclusive':hex(stream_end),
       'count_35F_alias_under_premises':False,
       'status':'VERIFIED recovered initializer/consumer chain; conditional preserved record and linear transport',
       'premises':'record+4 remains2740C; initialized pointer, complete even4096-byte chunks; M0FFFF legacy linear; no intervening cursor redirection',
       'unresolved':'all indirect ARM writers to record and cross-transaction SHI cursor/state preservation, not a new oversized-transfer witness'})
    emit('ARM-alias-ledger.json',{'exact_parameter_hit':hits,'compiled_record_hits':record_hits,
       'normal_parameter_value':0,'deferred_banks':[0,1],
       'families':[
        {'path':'286BC/286E4','classification':'NORMAL UI/PARAMETER immediate or deferred','value':0,'aliases_35F':'YES bank0; zero-preserving'},
        {'path':'35E28 fixed staging','classification':'recovered normal table job','range':'X[C00,D00)','aliases_35F':'NO with recorded count/transport premises'},
        {'path':'219E8/21C48','classification':'normal note lifecycle','range':'X57A+4A*slot, slot0..11; Y context fields separate','aliases_35F':'NO recovered slot domain'},
        {'path':'269E4 request5E →26A9A→292F8→P19D','classification':'SERVICE','aliases_35F':'YES accepted private start; transmitted value ZERO for private byte slots; cannot itself introduce nonzero'},
        {'path':'395EC→48DAA→48E26→2968E→P19D','classification':'UNRESOLVED normal/service ancestry and bulk endpoint',
         'pointer':'pageE800 gives initial E7FFFE after DSP compensation',
         'count':'r2 from [20006990+4]; recovered initializer208FA supplies2740C bytes; chunk<=4096',
         'aliases_35F':'VERIFIED NO recovered stream under record/cursor/legacy-modifier preservation; universal state closure unresolved'},
        {'path':'mailbox selector7→1CC7','classification':'recovered normal publisher','maximum':'1E8B','aliases_35F':'NO under index/modifier premises'},
       ]})
    # Exact direct edges and aligned raw pointer candidates for the consumer.
    edges=[]
    for pc,r in rows.items():
        if any(a<=pc<b for a,b in DATA):continue
        if r['text'].split()[0].startswith(('j','b')) and re.search(r'\$(?:0*202b|0*203a)\b',r['text']):
            edges.append({'PC':hex(pc),'instruction':r['text']})
    assert not edges
    word_values=[int.from_bytes(payload[i:i+3],'big') for i in range(0,len(payload),3)]
    occurrences={hex(v):[hex(i) for i,w in enumerate(word_values) if w==v] for v in (0x202B,0x203A,0x35F)}
    assert occurrences['0x202b']==['0x28ad'] and occurrences['0x203a']==[]
    emit('entry-and-dominance.json',{'direct_edges_to_202B_or_203A':edges,'aligned_word_occurrences':occurrences,
       'recovered_entry':{'call':'19AC jsr(R1)','pointer_cell':'X14B','initialized_target':'202B at28AC/28BC',
         'sequence':'init2779 clear → scheduler198D walks14 eight-word descriptors →19AC→202B→203A',
         'value':'0 from INIT and possible later286E4; NOT proved dominating across all foreign writes',
         'domain':'0 on recovered producer paths; universal normal state domain UNRESOLVED'},
       'entry_into_interior_203A':'no direct edge or aligned literal pointer found; arbitrary indirect targets not globally excluded',
       'self_writer_lemma':'with recovered202B entry and zero-skip mode,204B cannot be first nonzero writer to35F: count already zero means loop skipped'})
    transitions=[{'transition':name,'recovered_evidence':evidence,'invariant':'UNRESOLVED globally; no nonzero setter recovered'}
      for name,evidence in [
       ('patch/preset','27A10→2872C→286BC clears35F immediately/deferred; no populated360 table in recovered parameter map'),
       ('synth-bank switching','protected0/1 selector: zero count35F/4D1; consumer202B fixed35F'),
       ('note start/release','219E8/21C48 recovered slots12; X57A+4A*slot mailbox excludes35F'),
       ('effect changes','recovered parameter sinks exclude35F except zero setter; state-loaded effect writers remain open'),
       ('scene/session/project','no dedicated35F nonzero setter recovered; host stream/entry and reset ancestry not fully closed'),
       ('transport start/stop','no literal35F nonzero setter; generic host/control closure incomplete'),
       ('full DSP restart','INIT2788 clears35F; post-init foreign writers still require exclusion'),
       ('DSP soft reset without full boot','no specific nonzero count publisher recovered; universal normal entry not established')]]
    emit('transitions.json',transitions)
    emit('asynchronous-paths.json',[
       {'path':'SHI156→198→19D','class':'normal and service transport','pointer':'X10; X11 selectsX/Y',
        'modifier':'M0=FFFF forced15C, saved/restored15A/1B1','value':'received X0','aliases_35F':'YES capability; normal nonzero publication NOT proved',
        'race':'interrupt can occur before203A; no normal-value exclusion globally established'},
       {'path':'audio ISR1B4..1D8','class':'NORMAL AUDIO','write_domain':'reviewed low Y buffers/fixed X peripherals','aliases_35F':'NO reviewed configuration'},
       {'path':'deferred ARM2139A→286F6→286BC','class':'NORMAL UI/PARAMETER','value':0,'aliases_35F':'YES bank0; zero-preserving'},
       {'path':'mailbox1C53/1D41','class':'normal background jobs','domain':'C00..E00, workspace2400..2800, selector7>=1D8D under recorded premises',
        'aliases_35F':'NO recovered bounded jobs; universal saved-context closure unresolved'},
       {'path':'channel1 ICC worker','class':'separate private memory plus shared protocol','domain':'shared30000..38000 premise',
        'aliases_35F':'no direct channel0 private35F write established; physical alias/context closure not claimed'}])
    emit('invariant-verdict.json',{'invariant':'NOT-YET-DETERMINED','disproof_witness':None,
       'absolute_DSP_writer_found':False,'recovered_ARM_nonzero_writer_found':False,
       '204B_removed_as_high_X_blocker':False,'candidate_reevaluated':False,
       'prior_normal_runtime_safe':'NOT-YET-DETERMINED','prior_service_robust':'NO',
       'specific_open_aliases':['P19D saved X10 host stream: normal endpoint/space/cursor provenance',
           'P1F97 R7=Y[R6+32],16*32 output under stock count: cursor-cell preservation and actual normal entry',
           'other state-loaded nonzero stores explicitly retained in census; no single-only-blocker claim'],
       'next':'close P1F97 cursor provenance/preservation: Y[1820,1830) or Y[1A10,1A20), plus actual normal entry and M7; under stock32/linear mode forbid cursor values[340,360)',
       'static_analysis_exhausted':False,'hardware_or_execution_performed':False})
    emit('effect-cursor-obligation.json',{
       'path':'1E74..80 or corresponding19F0 setup→1F5C→1F89→1F97',
       'pointer_load':'R7=Y[R6+32] at1F89; R6 advanced once per outer iteration',
       'stock_R6_initial':['0x1800','0x19F0'],'stock_outer_iterations':16,'stock_inner_iterations':32,
       'pointer_cell_domains':['Y[1820,1830)','Y[1A10,1A20)'],
       'initialized_cursors':['0x2CCC','0x2CEC','0x2C02','0x2C24'],
       'source_word':'B fromX[R7] at1F93 plus MAC at1F95; not a proved-zero store',
       'linear_forbidden_base_start':'0x340','linear_forbidden_base_end_exclusive':'0x360',
       'formula':'35F in[c,c+32) iff340<=c<=35F in nonwrapping legacy-linear case',
       'factory_count_word_nonalias':'VERIFIED under initialized cursors/stock32/linear M7',
       'universal_normal_count_word_nonalias':'UNRESOLVED: pointer-cell/entry/modifier preservation',
       'not_counterexample':'no recovered normal producer installs a forbidden cursor',
       'not_single_only_unknown':'other possible state-loaded writes retained in full census'})
    windows=[(0x156,0x1B4),(0x198D,0x19BE),(0x202B,0x204C),(0x28AC,0x28D0),
             (0x1F5C,0x1F9B),(0x2779,0x278A),(0x1BC2,0x1BE7),(0x1A70,0x1AB1)]
    save(out/'dsp-witnesses.asm','\n'.join(rows[p]['line'] for p in sorted(rows)
         if any(a<=p<b for a,b in windows))+'\n')
    for name,h in inputs.items():assert sha((ROOT/name).read_bytes())==h
    emit('validation.json',{'inputs_SHA256':inputs,'BIN_SHA256':sha(arm),'SYX_SHA256':sha(syx),
       'decoded_equals_BIN':True,'roundtrip_identical':True,'all_five_extract_pairs_checked':True,
       'canonical_DSP_bytes_checked':True,'selected_ARM_bytes_checked':True,
       'script_SHA256':sha(Path(__file__).read_bytes()),'execution':'STATIC ledger only; no ISA execution',
       'indirect_operands':len(indirect),'possible_alias_operands':len(possible)})

if __name__=='__main__':main()
