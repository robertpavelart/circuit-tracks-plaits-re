"""Independent oracle, relocation-normalized traces, manual cycle arithmetic.

The output verdict refuses Circuit allocation unless stock ownership is proved;
successful synthetic execution cannot promote that gate.
"""
import argparse, csv, json, re, sys, subprocess
from pathlib import Path
from collections import Counter
import numpy as np
from ct_pstate_prepare import ROOT, BASE, INIT, STATE, fresh, write, sha
sys.path.insert(0, str(ROOT/'plaits/poc'))
from fixed_model import Fixed
sys.path.insert(0, str(ROOT/'plaits/poc/regopt'))
from timing_opt import classify as old_classify
import audit as timing

FIELDS=['phase','next','previous_pw','high','frequency','pw','shape']
def obj(p): return json.loads(p.read_text())
def rows(p):
    with p.open(newline='') as f: return list(csv.DictReader(f))
def dump(out,name,v): write(out/name,json.dumps(v,indent=2,sort_keys=True)+'\n')
def csvout(out,name,rs):
    with (out/name).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)

def program(folder):
    lines=(folder/'program.asm').read_text().splitlines()
    labels=obj(folder/'labels.json'); raw=(folder/'program.be24').read_bytes()
    origin=int(lines[0].split()[0],16); pp={}; ordinal={}
    for i,line in enumerate(lines):
        a,s=line.split(' ',1); pc=int(a,16)
        end=int(lines[i+1].split()[0],16) if i+1<len(lines) else labels['done']
        size=end-pc; ordinal[pc]=i
        if s.startswith('movem '):
            src,dst=s[6:].split(','); read=src.startswith('p:')
            r=old_classify(pc,s.replace('movem ','move ').replace('p:','x:'),size)
            r.update(assembly=s,family='MOVEM_LONG_ABSOLUTE',base=6,ea=1,short_write=False,
                     mem='P_data_read' if read else 'P_data_write',
                     source='DSP56300FM PDF431 A7: T6+lab1; PDF372/373 semantics')
            op=int.from_bytes(raw[(pc-origin)*3:(pc-origin+1)*3],'big')
            ext=int.from_bytes(raw[(pc-origin+1)*3:(pc-origin+2)*3],'big')
            reg=dst if read else src; field={'a':14,'x0':4,'y0':6}[reg]
            assert size==2 and op==((0x07f080 if read else 0x077080)|field)
            assert STATE<=ext<STATE+7
        else:
            r=old_classify(pc,s,size)
            if size==2 and s.startswith(('jmp ','jsr ')):
                r.update(ea=1,source='FM A4/A5 JMP/JSR absolute EA T3+lab1')
        pp[pc]=r
    return pp,labels,ordinal

def normalize(s):
    s=s.replace('movem ','move ')
    s=re.sub(r'p:>\$([0-9a-f]{6})',lambda m:f'x:${int(m[1],16)-STATE+0x20:06x}',s)
    s=s.replace('x:>$','x:$')
    # Branch and DO extension targets are verified against target ordinals.
    return s

def instruction_equivalence(base,variant):
    bp,bl,bi=program(base); vp,vl,vi=program(variant)
    assert len(bp)==len(vp)
    targetb={**bi,bl['done']:len(bi)};targetv={**vi,vl['done']:len(vi)}
    for (_,b),(_,v) in zip(bp.items(),vp.items()):
        bs,vs=normalize(b['assembly']),normalize(v['assembly'])
        if bs.startswith(('j','do ')):
            bm=re.search(r'\$([0-9a-f]{6})$',bs);vm=re.search(r'\$([0-9a-f]{6})$',vs)
            assert bm and vm
            bt,vt=int(bm[1],16),int(vm[1],16)
            # The assembler DO operand denotes the first word after the loop;
            # its serialized extension is that address minus one.
            if bs.startswith('do '):
                assert bt==bl['block_end'] and vt==vl['block_end']
            else: assert targetb[bt]==targetv[vt]
            bs=bs[:bm.start()]+'TARGET';vs=vs[:vm.start()]+'TARGET'
        assert bs==vs,(bs,vs)
    return bp,vp,bi,vi

def trace_equivalence(base,variant):
    bp,vp,bi,vi=instruction_equivalence(base,variant)
    bt=np.memmap(base/'execution-pc.u16',dtype='<u2',mode='r')
    vt=np.memmap(variant/'execution-pc.u16',dtype='<u2',mode='r')
    assert len(bt)==len(vt)
    bm=np.full(0x4000,-1,dtype=np.int16);vm=bm.copy()
    for pc,i in bi.items(): bm[pc]=i
    for pc,i in vi.items(): vm[pc]=i
    for a in range(0,len(bt),1048576):
        b=bt[a:a+1048576];v=vt[a:a+1048576]
        assert np.all(bm[b]>=0) and np.all(vm[v]>=0)
        assert np.array_equal(bm[b],vm[v]),'Control-flow ordinal mismatch'
    return dict(issued=len(bt),all_instruction_operands_equivalent=True,
                all_branch_and_DO_targets_equivalent=True,all_execution_ordinals_equal=True)

def independent_decode(folder,out,name):
    pp,labels,_=program(folder);origin=min(pp)
    decoder=ROOT/'builds/dsp-tools/dsp_disasm.exe'
    r=subprocess.run([str(decoder),str(folder/'program.be24'),f'{origin:X}',f'{origin:X}',f"{labels['done']:X}"],
                     capture_output=True,text=True,check=True)
    write(out/(name+'-independent-disassembly.asm'),r.stdout)
    decoded={}
    for line in r.stdout.splitlines():
        m=re.match(r'P:([0-9A-F]+)\s+[0-9A-F]{6}(?:\s+[0-9A-F]{6})?\s+(.*)',line)
        assert m,line
        decoded[int(m[1],16)]=m[2]
    assert set(decoded)==set(pp)
    for pc,p in pp.items():
        s=p['assembly'];d=decoded[pc]
        if s.startswith('movem '):
            assert d==s.replace('p:>$00','p:$'),(s,d)
        elif s.startswith('j'):
            sm=re.fullmatch(r'(j\w+) \$([0-9a-f]+)',s);dm=re.fullmatch(r'(j\w+) \$([0-9a-f]+)',d)
            assert sm and dm and sm[1]==dm[1] and int(sm[2],16)==int(dm[2],16),(s,d)
    return dict(decoder_sha256=sha(decoder),instruction_boundaries_exact=True,
                MOVEM_and_control_targets_exact=True,source='Existing independent Rust DSP56300 disassembler')

def cycles(folder,out,name):
    pp,ll,_=program(folder); blocks=rows(folder/'blocks.csv')
    trace=np.memmap(folder/'execution-pc.u16',dtype='<u2',mode='r')
    size=0x4000
    bases=np.zeros(size,dtype=np.int16);low=bases.copy();src=bases.copy();alu=bases.copy();dst=bases.copy()
    conditional=np.zeros(size,dtype=bool);targets=np.zeros(size,dtype=np.uint16)
    pread=bases.copy();pwrite=bases.copy()
    for pc,r in pp.items():
        bases[pc]=r['base']+r['ea'];low[pc]=bases[pc]-int(r['short_write'])
        src[pc]=r['move_src'];alu[pc]=r['alu_dst'];dst[pc]=r['move_dst']
        pread[pc]=r['mem']=='P_data_read';pwrite[pc]=r['mem']=='P_data_write'
        if r['family']=='JCC':
            conditional[pc]=True;targets[pc]=int(r['assembly'].split()[-1][1:],16)
    pos=0; rr=[]; census=Counter()
    for b in blocks:
        n=int(b['instructions']);pc=np.asarray(trace[pos:pos+n]);pos+=n
        prev=np.zeros_like(pc);prev[1:]=pc[:-1]
        nxt=np.empty_like(pc);nxt[:-1]=pc[1:];nxt[-1]=ll['done']
        ar=(src[pc]&alu[prev])!=0;tr=(src[pc]&dst[prev])!=0
        assert not np.any(ar&tr)
        false=conditional[pc]&(nxt!=targets[pc]);extra=ar.astype(np.int16)+tr+false
        cost=int((bases[pc]+extra).sum())
        pr=int(pread[pc].sum());pw=int(pwrite[pc].sum())
        if name!='baseline':
            assert pr+pw==int(b['P_state_reads'])
            assert pw==int(b['P_state_writes'])
        # memWriteP reads the old P word for decode-cache invalidation. Those
        # emulator implementation callbacks are not extra architectural loads.
        counts=np.bincount(pc,minlength=size)
        for p in np.flatnonzero(counts): census[pp[p]['family']]+=int(counts[p])
        rr.append(dict(case=int(b['case']),block=int(b['block']),issued=n,
            nominal_and_interlock_cycles=cost,ambiguity_lower_cycles=int((low[pc]+extra).sum()),
            cold_fill_drain_allowance=12,conditional_trace_ceiling=cost+12,
            architectural_P_reads=pr,architectural_P_writes=pw,
            arithmetic_interlocks=int(ar.sum()),transfer_interlocks=int(tr.sum())))
    assert pos==len(trace)
    csvout(out,name+'-block-cycles.csv',rr)
    vals=[r['nominal_and_interlock_cycles'] for r in rr];ins=[r['issued'] for r in rr]
    return dict(blocks=len(rr),issued_min=min(ins),issued_mean=float(np.mean(ins)),issued_max=max(ins),
        model_cycles_min=min(vals),model_cycles_mean=float(np.mean(vals)),model_cycles_max=max(vals),
        conditional_trace_ceiling_max=max(vals)+12,physical_measured_cycles=None,
        status='MEASURED opcode traces / CALCULATED private-zero-wait cycle model; not stock timing or all-state WCET',
        instruction_census=dict(census)),rr

def ownership(out):
    asm=ROOT/'builds/phase3-selection0-channel0.asm'
    lines=asm.read_text().splitlines();witness=[]
    payload=(ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin').read_bytes()
    for i,line in enumerate(lines):
        m=re.fullmatch(r'P:([0-9A-F]+)\s+([0-9A-F]{6})(?:\s+([0-9A-F]{6}))?\s+(.*)',line)
        assert m,line
        if 'p:' in m[4].lower():
            a=int(m[1],16)
            for j,word in enumerate([m[2]]+([m[3]] if m[3] else [])):
                assert int(word,16)==int.from_bytes(payload[3*(a+j):3*(a+j+1)],'big')
            if a==0x28de:
                status='VERIFIED DATA: 28D3 seedsR0=28DD,28D7 DO10F,28D9 copiesP[28DD,29EC) toY[E30,F3F); not executable MOVEP'
            else: status='STATIC P reader; boot/table provenance from adjacent instructions; no tail ownership inferred'
            witness.append(dict(pc=f'P:{a:06X}',decode=line,status=status))
            write(out/f'evidence-P{a:04X}.asm','\n'.join(lines[max(0,i-6):i+3])+'\n')
    csvout(out,'stock-P-reference-witnesses.csv',witness)
    boot=(ROOT/'firmware/dsp/build-4486/selection0-channel0.boot24.bin').read_bytes()
    count=int.from_bytes(boot[:3],'big');load=int.from_bytes(boot[3:6],'big')
    assert count==0x2a5e and load==0 and len(boot)==6+3*count
    assert len(witness)==16
    result=dict(candidate=[STATE,STATE+7],candidate_status='ILLUSTRATIVE ONLY / NOT RESERVED',
        operand_reference_count=len(witness),operand_words_byte_verified=True,
        stock_loaded_P=[load,load+count],candidate_in_current_stock_upload=False,
        conditional_core0_MS7_capacity=[0,0x4000],capacity_is_ownership=False,
        normal_core_mode_and_mapping='UNRESOLVED actual mode/endpoint preservation; pinned memory-map interpretation conditional',
        private_host_store='VERIFIED recovered19D/19B write X/Y only; no direct private P store',
        shared_alias='SOURCE-DERIVED sharedPXY[30000,38000) does not include candidate under reviewed map',
        stock_linear_decode_P_stores='One apparent28DE store lies in verified table data; no executable direct P store recovered in this listing',
        completeness='Listing is not CFG coverage, ROM proof, all DMA/channel/indirect/foreign-domain proof, or a global no-writer certificate',
        reviewed_audio_DMA='Recovered fixedY29..2B and XFFFFA4 routes exclude privateP under reviewed map',
        unresolved=['all normal DMA reconfiguration and privateP destination domains',
                    'actual memory mode/translation/endpoint and lifetime across selection/reload',
                    'all indirect P reads/execution and ROM/foreign writer coverage',
                    'hardware P-data/prefetch/cache/wait/IRQ interactions',
                    'owned initialized expanded P object and authentic boot handoff/container'],
        stock_initialization='REFUSED: seven words absent from unchanged upload; arbitrary activation state not seeded',
        proven_owned_stock_P_words=0,stock_lifetime_pass=False,overall='REFUSED')
    dump(out,'P-region-ownership.json',result)
    return result

def verify(source,fixtures,low,repeat,highp,highx,out,exe):
    out=fresh(out);baseline=ROOT/'builds/phase20a-regopt/final';original=baseline/'dsp-first'
    for rel,h in obj(source/'input-guards.json').items(): assert sha(ROOT/rel)==h,rel
    fixture=obj(fixtures/'result.json');assert fixture['fixtures']==2176 and fixture['independent_raw24_model_matches']
    for p in low.iterdir(): assert sha(p)==sha(repeat/p.name),p.name
    cases=obj(baseline/'cases.json');inputs=[]
    for line in (baseline/'inputs.tsv').read_text().splitlines():
        a,b,f,p,s=line.split();inputs.append((int(a),int(b),float(f),float(p),float(s)))
    # Fresh independent oracle. Baseline samples are not the sole authority.
    samples=[];state=[];model=None;last=-1
    for i,b,f,p,s in inputs:
        if i!=last:model=Fixed();last=i
        samples.extend(model.render32(f,p,s));state.append(model.state())
    expected=np.asarray(samples,dtype='<i4'); assert len(expected)==240640
    trace_results={};summaries={};costs={}
    for name,folder in [('low-P',low),('high-P',highp),('high-X',highx)]:
        data=np.fromfile(folder/'output.i32',dtype='<i4')
        assert np.array_equal(data,expected) and sha(folder/'output.i32')==sha(original/'output.i32')
        ss=rows(folder/'states.csv');assert len(ss)==len(state)==7520
        for got,want,(cid,b,*_) in zip(ss,state,inputs):
            assert (int(got['case']),int(got['block']))==(cid,b)
            assert [int(got[k]) for k in FIELDS]==want
        assert sha(folder/'states.csv')==sha(original/'states.csv')
        trace_results[name]=trace_equivalence(original,folder)
        trace_results[name]['independent_decode']=independent_decode(folder,out,name)
        summaries[name],costs[name]=cycles(folder,out,name)
    summaries['baseline'],costs['baseline']=cycles(original,out,'baseline')
    # Per-block delta exact in the conditional manual cycle model. Do not
    # subtract unrelated extrema or call a trace maximum a universal bound.
    deltas=[]
    for i,(b,p,x) in enumerate(zip(costs['baseline'],costs['high-P'],costs['high-X'])):
        d=p['nominal_and_interlock_cycles']-x['nominal_and_interlock_cycles']
        transfers=p['architectural_P_reads']+p['architectural_P_writes']
        assert d==5*transfers
        deltas.append(dict(case=b['case'],block=b['block'],P_vs_long_X_cycles=d,
            high_P_vs_baseline_cycles=p['nominal_and_interlock_cycles']-b['nominal_and_interlock_cycles'],
            P_transfers=transfers))
    csvout(out,'storage-cycle-deltas.csv',deltas)
    rr={n:obj(f/'native-resources.json') for n,f in [('low-P',low),('high-P',highp),('high-X',highx)]}
    assert rr['low-P']['P_words']==505 and rr['high-P']['P_words']==rr['high-X']['P_words']==549
    assert rr['low-P']['persistent_P_words']==rr['high-P']['persistent_P_words']==7
    assert all(v['peak_stack_entries']==3 for v in rr.values())
    continuity=next(c for c in cases if c['name']=='long_continuity');assert continuity['blocks']==2048
    own=ownership(out)
    reg=obj(baseline/'resource-manifest.json');rms=max(m['RMS_difference'] for m in obj(baseline/'metrics.json'))
    result=dict(overall='REFUSED FOR CIRCUIT STORAGE; PASS STANDALONE P-STATE CONTRACT',
        instruction_legality='SOURCE-DERIVED MOVEM_ea + TESTED independent raw24/manual-field fixtures',
        fixtures=fixture,source_renderer='REGOPT final/native DIV unchanged except state addresses; long template changes addressing only',
        cases=43,blocks=7520,samples=240640,independent_integer_oracle_samples=True,all_seven_states_exact=True,
        all_samples_vs_X_exact=True,max_sample_difference=0,RMS_sample_difference=0,
        continuity=dict(blocks=2048,samples=65536,exact=True,initialization_epochs=1,no_per_block_reset=True),
        repeat_files_byte_identical=True,traces=trace_results,initialization=dict(values=INIT,source='21-byte BE24 initialized object read and fully loaded once per case; poison overwritten',
        extra_persistent_flag_words=0,stock_initialization_proved=False),
        resources=rr,scratch_X_words=3,control_X_words=3,register_scratch_words=16,Y_output_words=32,LUT_words=0,
        cost_scope='505/549 executable +7 persistent data +2 decoderpadding; whole module/glue costs not qualified',
        cycles=summaries,P_vs_high_X_cycles=dict(min=min(d['P_vs_long_X_cycles'] for d in deltas),mean=float(np.mean([d['P_vs_long_X_cycles'] for d in deltas])),max=max(d['P_vs_long_X_cycles'] for d in deltas)),
        upstream_reference='Same immutable vectors and controls; exact X equality preserves every previous float comparison result',
        maximum_float_case_RMS_difference=rms,maximum_pitch_cents_error=obj(baseline/'result.json')['maximum_absolute_cents_error'],
        owned_stock_P_words=own['proven_owned_stock_P_words'],firmware_integration_ready=False,
        physical_measured_cycles=None,stock_images_loaded=False,hardware_actions=0,canonical_patch=False)
    dump(out,'qualification.json',result)
    dump(out,'cycle-assumptions.json',dict(memory='private internal zero wait, SR300/OMR0/linearM, no IRQ/DMA; device-family timing assumption',
        model='Frozen REGOPT rules; MOVEM6+absolute1, longJMP/JSR3+1; preserve conservative accumulator interlocks',
        P_cache='Mutable data never executed; sealed interpreter invalidates changed P opcode cache, not a DSP56724 hardware cache proof',
        arithmetic_interlocks='Conservative inherited single-next-transfer charges retained even across multicycle moves; no claim of exact physical cycle timing',
        structural_WCET=None,stock_cycles=None,additional_initialization_cycles='Host fixture loads data object, zero renderer init opcodes; authentic Circuit loader cost not measured'))
    # Export pinned manual evidence without network/refetching anything.
    from pypdf import PdfReader
    manual=ROOT/'builds/phase19b/documentation/DSP56300FM.pdf';pdf=PdfReader(manual)
    ev=out/'evidence';ev.mkdir()
    for page in [320,323,329,372,373,431]: write(ev/f'DSP56300FM-pdf{page}.txt',pdf.pages[page-1].extract_text()+'\n')
    dump(out,'provenance.json',dict(manual_sha256=sha(manual),source_dir=source.relative_to(ROOT).as_posix(),
        guarded_inputs=len(obj(source/'input-guards.json')),all_input_guards_unchanged=True,
        exe_sha256=sha(exe),exe_path=exe.relative_to(ROOT).as_posix(),
        analysis_sha256=sha(Path(__file__)),fixture_sha256=sha(ROOT/'plaits/poc/pstate/fixtures.inl'),
        artifacts='v1-v6 exploratory build/qualification outputs preserved; final v7 uses explicit4000-word decoder capacity; no prior evidence overwritten'))
    dump(out,'hashes.json',{p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()})
    print(json.dumps({k:result[k] for k in ['overall','cases','blocks','samples','P_vs_high_X_cycles']},indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser()
    for key in ['source','fixtures','low','repeat','highp','highx','out','exe']:
        a.add_argument('--'+key,type=Path,required=True)
    ns=a.parse_args();verify(**{k:v.resolve() for k,v in vars(ns).items()})
