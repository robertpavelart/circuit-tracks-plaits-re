"""Bounded Phase20C2 lifetime audit. Offline ledgers/arithmetic only, no CPU/device.

Candidate pool is inherited slot0 tail and two previously identified scratch
halves. Excluded regions are not searched. Known collisions suffice to reject;
unclosed writer/consumer classes never become a qualification by absence.
"""
import argparse,csv,json,re
from pathlib import Path
from pypdf import PdfReader
from ct_livepatch_design import ROOT,DSP,FM,RM,GOLD,original_rows,sha,dump,table

BASE=ROOT/'builds/phase20c-fixedstate'
PREVIOUS=ROOT/'builds/phase20c-livepatch-design/final-v2'
HOST=ROOT/'builds/phase19c-hostwrite/final-v3'
STATE_NAMES=['phase','next','previous_pw','high','frequency','pw','shape']


def regions():
    return [dict(id=i,start=a,end_exclusive=b,words=b-a,original_role=role,
        pool_status=status,source=source) for i,a,b,role,status,source in [
        ('TAIL',0x5BF,0x5C4,'slot0 three update terms, timestamp, ARM start-reset word','REJECTED: five words, all have retained writers','20C state-lifetime;281/657/event/allocator'),
        ('SCRATCH_A',0x2CCC,0x2CEC,'generator phase weights / effect scratch; also temporary candidate','REJECTED persistent','20C state-lifetime;Phase15 cursor-table'),
        ('SCRATCH_B',0x2CEC,0x2D0C,'second initialized effect-scratch half','REJECTED: service writable and unclosed effect reachability','Phase15 cursor-table'),
        ('GAP',0x2C22,0x2C24,'geometric two-word gap between nominal side-stream ranges','EXCLUDED: only two words and boundary ownership not proved','Phase15 interval distinction'),
        ('TAIL_EXTEND',0x5BF,0x5C6,'invalid seven-word tail extension into next slot','EXCLUDED: slot1 mailbox/coefficient collision','D(i)/E(i) stride4A'),
        ('ACTIVE_COEFFICIENTS',0x57B,0x5BF,'active generator/current ramps/post words','EXCLUDED, no search','20C retained prefix'),
        ('ACTIVE_KERNEL',0x1960,0x196C,'active kernel context','EXCLUDED, no search','20C retained preparation'),
        ('HIGH_X',0x5F00,0x6000,'previous unresolved high-X region','EXCLUDED, no new analysis','prior ownership gate')]]


def sets():
    return [dict(id=i,words=words,layout=layout,ranking='REJECTED',reason=reason)
        for i,words,layout,reason in [
        ('FIRST7',list(range(0x2CCC,0x2CD3)),'contiguous','retained lookup completion overwrites every word; service can clear every word'),
        ('SECOND7',list(range(0x2CEC,0x2CF3)),'contiguous','service writable; initialized effect clear/accumulation capable, normal reachability/foreign domains unclosed'),
        ('SPLIT7',[0x5BF,0x5C0,0x5C1,0x2CEC,0x2CED,0x2CEE,0x2CEF],'split','retained per-slot updates overwrite first3; service writable throughout')]]


def target_words():
    return sorted(set(range(0x5BF,0x5C4))|set(range(0x2CCC,0x2D0C)))


def per_word_writers(a):
    facts=[('INIT','BOOT/INIT','2788','X[0,6000) <-0; R0 increments via pairedY store',
        'VERIFIED startup clear; acceptable before owned initialization')]
    if 0x5BF<=a<0x5C2:
        facts.append(('LOOP/INDIRECT','NORMAL AUDIO/PREPARATION','2A2->70C->73B',
            f'X2B=E+45; R1=5BF; DO3 writes word j={a-0x5BF}', 'VERIFIED retained writer under slot0/linear state'))
    elif a==0x5C2:
        facts.append(('INDEXED','NOTE/TRIGGER','2D8/2DD','R7=X29=E+1; (R7+71decimal)=E+48=5C2',
            'VERIFIED retained timestamp publisher; trigger condition'))
    elif a==0x5C3:
        facts.append(('ARM->SHI','NORMAL START/EVENT','08021A22/54/5E ->19D',
            '5C3+4A*slot; zero stagedSP8 and upper24 sent', 'VERIFIED conditional branch writer, not all starts'))
    if 0x2CCC<=a<0x2CEC:
        pc='829/884' if (a-0x2CCC)%2==0 else '82A/885'
        facts.append(('LOOP/INDIRECT','NORMAL COMPLETION GENERATOR',pc,
            f'R2=2CCC; DO X3B=16, paired stores cover32; offset={a-0x2CCC}',
            'VERIFIED conditional lookup-class path; actual preset not assumed'))
        facts.append(('Y-CURSOR / FILL','EFFECT-FAMILY','1F68/1F6E',
            'initializedY1820=2CCC, DO X3A=32 clear first buffer',
            'VERIFIED address arithmetic; normal parent reachability UNRESOLVED'))
    if 0x2CEC<=a<0x2D0C:
        facts.append(('Y-CURSOR / FILL','EFFECT-FAMILY','1F6A/1F6F',
            'initializedY1821=2CEC, DO X3A=32 clear second buffer',
            'VERIFIED address arithmetic; normal parent reachability UNRESOLVED'))
    if 0x2CCC<=a<0x2D0C:
        facts.append(('TABLE-DRIVEN INDIRECT','EFFECT-FAMILY','1F89/1F97',
            '16 initializedY1820+j alternating2CCC/2CEC;32-word accumulation per entry',
            'VERIFIED conditional domain; foreign cursor/modifier and entry unclosed'))
    facts += [('HOST/SERVICE','SERVICE permitted inSelection0','269E4/26A9A->292F8->19D',
        'private X start<8000, no reservation check, private data zero; target-normalized cache-miss witness',
        'VERIFIED request-dependent capability, not observed operation'),
        ('CACHED CONTINUATION','NORMAL/SERVICE transport','292F8/29306/19D',
        'cache hit uses currentDSP X10/X11; nominal requested endpoint not effective target',
        'UNRESOLVED all-normal interleaving/cursor state'),
        ('FOREIGN INDEX/COPY/DMA','normal/foreign state','204B, mailbox/table jobs, reprogrammedDMA',
        'candidate-specific destination/count/context domains not globally closed; known DMA staging excludes candidates',
        'UNRESOLVED; cannot qualify from absent literal'),
        ('ABSOLUTE','syntactic prior ledgers','Phase6B/19C ledgers',
        'known fatal stores use computed pointers; no literal-address absence claim',
        'complete direct/foreign writer proof NOT asserted')]
    return [dict(address=f'X:0x{a:X}',writer_class=kind,entry_mode=mode,PC=pc,formula=formula,
        evidence=status,all_writers_closed=False) for kind,mode,pc,formula,status in facts]


def readers(a):
    rows=[]
    def add(pc,mode,relationship,why,status):
        rows.append(dict(address=f'X:0x{a:X}',PC=pc,mode=mode,relative_to_replacement=relationship,
            requirement=why,evidence=status,all_consumers_closed=False))
    if a<0x5C2:
        add('36D/374','retained inactive/update branch','later invocation / cross-block',
            f'R0=X2B=5BF;DO3 reads offset{a-0x5BF} and adds derived term intoY state',
            'VERIFIED pointer/count under slot0; not all branches active')
    elif a==0x5C2:
        add('1BB7/1BDB','normal allocation/steal','outside selected render / later note',
            'bank0 six-slot timestamp scan R0=5C2 stride4A; allocator remains original', 'VERIFIED retained reader')
    elif a==0x5C3:
        add('foreign/derived readers','UNRESOLVED','UNRESOLVED',
            'full consumer role not recovered; normal reset writer already disqualifies', 'UNRESOLVED, not semantically dead')
    if 0x2CCC<=a<0x2CEC:
        add('833' if a==0x2CCC else '83F','selected lookup completion','before overwrite and again in later block',
            'phase weights used in lane interpolation, retained stock prefix', 'VERIFIED conditional weights path')
        add('897','alternate lookup completion','before overwrite / subsequent block',
            'R2=2CCC linear32 reads', 'VERIFIED conditional alternate path')
    if 0x2CCC<=a<0x2D0C:
        add('1F93','effect-family','later scheduled use possible',
            'read current X cursor before1F97 accumulation', 'VERIFIED initialized domain, normal entry UNRESOLVED')
        add('1F09' if a<0x2CEC else '1F0B','effect-family','later scheduled use possible',
            'R4=2CCC/R5=2CEC, DO32 reads both halves', 'VERIFIED local domain; actual normal parent UNRESOLVED')
    add('188/1A4','generic service read','independent of render',
        'private X readable, including prefetch; no candidate ownership filter', 'VERIFIED capability, not observation')
    add('foreign indirect readers','UNRESOLVED','UNRESOLVED',
        'not globally enumerated; never use no-post-read as ownership', 'UNRESOLVED')
    return rows


def service_witness(a,cache):
    """Private service-address/cache arithmetic witness; no wire frames/CPU/device."""
    if not 1<=a<0x8000 or not 0<=cache<=0xFFFF:raise ValueError('private model bounds')
    start=a if cache!=a else a-1
    count=1 if cache!=a else 2
    assert cache!=start  # force normal private address setup, X flag clear
    return dict(target=a,initial_cache=cache,start=start,count=count,
        stores=list(range(start,start+count)),stored_value=0,
        condition='valid decodedservice operation0/port0, coherent serializedtransfer; no external ingress observation')


def nominal_host_projection():
    with (HOST/'scalar-endpoints.csv').open(encoding='utf8',newline='') as f:rows=list(csv.DictReader(f))
    hits=[];projected=0
    for r in rows:
        if r['space']!='X':continue
        text=r['address'] or r['start'] or r['destination_start']
        if not text:continue
        try:start=int(text,16) if text.startswith('0x') else int(text)
        except ValueError:continue
        endtext=r['end_exclusive']
        end=int(endtext,16) if endtext.startswith('0x') else int(endtext) if endtext else start+1
        projected+=1
        words=[a for a in target_words() if start<=a<end]
        if words:hits.append(dict(site=r['site'],kind=r['kind'],start=start,end_exclusive=end,hits=words))
    return dict(source='builds/phase19c-hostwrite/final-v3/scalar-endpoints.csv',rows=len(rows),
        X_rows_projected=projected,hits=hits,
        supplement='ARM21A5E start reset5C3 is byte-verified separately; this1500-row ledger omits that writer',
        limitation='nominal endpoints only; no all-normal/cache/cursor/bulk closure')


def layout():
    variables=json.loads((GOLD/'assembly/layout.json').read_text())['variables']
    assert [variables[n] for n in STATE_NAMES]==list(range(0x20,0x27))
    role=['periodic phase; legal deferred-wrap excursions allowed',
        'delayed naive+BLEP/integrated-BLEP contribution consumed as next sample this',
        'previous sample PW used in event denominator',
        'PW-crossed/unwrapped event-state flag, not another previous-phase word',
        'retained current frequency, next block interpolation starts here',
        'retained current PW, next block interpolation starts here',
        'retained current shape, next block interpolation starts here']
    formats=['Q2.22','signedQ3.21','Q2.22','boolean0/1','Q2.22','Q2.22','Q3.21']
    init=[0,0,0x200000,0,41943,0x200000,0]
    rows=[dict(offset=i,name=n,original_X=0x20+i,format=formats[i],meaning=role[i],
        exact_baseline_init=init[i],future_X=None) for i,n in enumerate(STATE_NAMES)]
    return dict(status='VERIFIED unchanged source/layout; no representation change',words=7,fields=rows,
        no_separate_previous_phase=True,no_extra_integrator_word=True,
        sources=['plaits/poc/fixed_model.py Fixed.__init__/render32','REGOPT assembly/layout.json','REGOPT assembly/variablesaw.asm'])


def fallback_P_traffic(out):
    import numpy as np
    prog=[]
    for line in (GOLD/'dsp-first/program.asm').read_text().splitlines():
        addr,text=line.split(' ',1);m=re.search(r'x:\$([0-9a-f]{6})',text)
        if m and 0x20<=int(m[1],16)<0x27:prog.append((int(addr,16),text))
    assert len(prog)==63
    trace=np.memmap(GOLD/'dsp-first/execution-pc.u16',dtype='<u2',mode='r')
    mask=np.zeros(4096,dtype=np.uint8)
    for p,_ in prog:mask[p]=1
    with (GOLD/'dsp-first/blocks.csv').open(encoding='utf8',newline='') as f:blocks=list(csv.DictReader(f))
    result=[];index=0
    for b in blocks:
        size=int(b['instructions']);n=int(mask[trace[index:index+size]].sum());index+=size
        result.append(dict(case=b['case'],block=b['block'],existing_state_transfer_count=n,
            hypothetical_longMOVEM_increment=5*n,status='CALCULATED source-table delta on unchanged existing trace; no MOVEM execution'))
    assert index==len(trace)
    table(out,'P-state-traffic.csv',result)
    vals=[r['existing_state_transfer_count'] for r in result]
    return dict(status='MEASURED priortraceevents /CALCULATED unimplemented fallback timing',static_state_sites=63,
        blocks=len(vals),state_transfers_min=min(vals),state_transfers_mean=sum(vals)/len(vals),state_transfers_max=max(vals),
        nominal_added_cycles_min=5*min(vals),nominal_added_cycles_mean=5*sum(vals)/len(vals),nominal_added_cycles_max=5*max(vals),
        rule='FM PDF431 MOVEM6+absoluteextension1=7 versus longX2 =>+5, device-family/private-memory assumption',
        complete_cycle_bound=None,new_CPU_execution=False,trace_sha256=sha(GOLD/'dsp-first/execution-pc.u16'))


def fallback_design(traffic):
    return dict(status='DESIGN ONLY; exactly two architectures; neither QUALIFIED',
        A=dict(name='one-way selected-slot generator storage takeover',
            conditional_X_example=[0x57B,0x582],words=7,
            ownership='would repurpose first7 words inside slot0 generatorrecord, NOT currently free or original7 persistent scalars',
            required_disables=['selected387 generator-record writers before any Plaits write; retain/reconstruct post-preparation pointer/accounting',
                'selected77F original lane reads/writes BOTH request andcompletion; preserve globalbitmap/worker machinery for other slots',
                'all selected reset/preparation/table/copy aliases to proposed7',
                'genericSHI/service target stores into ownedrange, including cached/extended continuations; need actual-target filtering'],
            new_obligations=['selected request bitmap without dead lookup jobs','post Q+30/Y7/R4 correct',
                'auxiliary/guard contract: retain needed producer or restrict/enforce routing0 with justified substitute',
                'post/allocator/other slots unaffected; lifecycle initialization explicit'],
            incompatibility='cannot retain all original selectedgenerator/combiner as current20C architecture AND reclaim its inputs',
            fallback='one-way activation: selected stock reentry prohibited; re-enabling387 destroys Plaitsstate. Other slots remainstock.',
            short_state=False,P_cost_delta_to549=0,complete_extra_P_cycles=None,
            conclusion='UNRESOLVED larger redesign; no takeover/writer filter implemented'),
        B=dict(name='extend uploaded P object with7 mutable state words',
            space='P, not X; therefore does NOT satisfy seven persistentX gate',words=7,
            structural_evidence='RM memory map +SHI onecount/load/Ppayload; FM MOVEM supports read/writeP anyregister',
            capacity='conditional currentP[0,4000),5538 extra words;7 data words reduce remainingcodecapacity to5531',
            illustrative_after_module_data=[0x2D29,0x2D30],
            address_status='layout illustration from713P+2padding; not owned/reserved; completegluechangesaddress',
            load='extend whole P stream/count; existingdataobject initialized byprogram upload beforeP0 execution. No inventedX bootrecord.',
            original_X_ownership='no unprovedglobalX claim; privateP mustnot alias stockX/Y under actualOMR/mode',
            memory_switch_alternative='no compatible extraX gained: current24KX alreadymax in reviewedmaps; 8KP maps failloaded2A5E, largerP maps shrinkX belowrequired scratch',
            external_X_alternative='existingEMC assetobject ownership/size/loader not proved; no externaladdress chosen',
            ISA='MOVEM supports all on-chip registers; raw accumulator/CCR/numeric equivalence and pipeline/cache/P-bus hazards need qualification',
            static_state_transfer_sites=63,renderer_P_relative_to549='0 templatechange if63 longX2wordforms become63 longMOVEM2wordforms; +7 P data. Not assembled.',
            partial_module_data_total=722,complete_added_P=None,traffic=traffic,
            protection='private stockSHI19D/19B writeX/Y only, notP; sharedPX/Y alias region30000 distinct. DMA/Pwriters/mode switches stillmustclose.',
            initialization='seed exact7 baselinevalues in owneduploadeddataobject; no8th flag needed for provedcoldload epoch; arbitraryactivation notsolved',
            fallback='dormantPstate plausible duringnumericdispatcherfallback; Selectionreload/endofownership resets/reseeds epoch',
            gates=['proveactualPmode/tailownership/code/container','boundedPwrite/DMA/cache behavior','MOVEM bit-equivalence, originalarithmetic/CCR contract',
                'newcycle/stack/IRQ audit','temporaryworkspace ownership','pitch/headroom/recovery'],
            conclusion='CONDITIONAL structural alternative preserving20C retainedwork; not implemented/qualified'),
        preferred_next='bounded qualification of the7-word P-backedobject/MOVEM contract, rather than another broadXsearch',
        images_or_firmware_modified=False)


def initialization():
    return dict(status='CONDITIONAL bounded design; actualownership/activation gate NOT qualified',
        exact_source_init=layout()['fields'],arbitrary_RAM_zero_assumption=False,
        preferred='deterministically initialize all7 exactly once after proven ownership transition, before firstrender; bootloadedPobject is fallbackB possibility',
        baseline_values=[0,0,0x200000,0,41943,0x200000,0],
        startup_X_clear='acceptable before init but not proof of arbitraryfirstentry values or laterpersistence',
        zero_frequency_sentinel='validfrequency>=1 throughout validramp; may markuninitialized only if ownership/startup explicitly publishes0 and wrapper initializes before renderer',
        positive_frequency_proof='f(k)=c+floor(k*(t-c)/32), 0<=k<=32,c/t>=1 =>f(k)>=min(c,t)>=1; existingpositiveinputdomain required',
        extra_persistent_flag_preferred=0,
        extra_flag_condition='one separateflag (=8 total) if independently armeddynamicactivation required; thatflagneeds itsowninit/ownership. It doesnotfixunknownRAM.',
        note_lifecycle='retain oscillator dormant acrossinactiveblocks unless explicitnewresetpolicy adopted; no invented stocktrigger reset',
        fallback_current_X_candidates='stock writers destroy/corruptstate; no dormancy guarantee',
        fallback_A='selectedpath one-way only whilestock producersdisabled; no returningstock over ownedfields',
        fallback_B='ownedPobject dormant whiledispatcherfallsback, only withinprovedno-reload/no-mode-change epoch',
        actual_first_init_PC=None,initialized_stock_or_Plaits_memory=False,implemented=False)


def transient():
    return dict(status='NOT PROVEN / unqualified',start=0x2CCC,end_exclusive=0x2CEC,words=32,
        partition=dict(controls=[0x2CCC,0x2CCF],spills=[0x2CCF,0x2CD2],save26=[0x2CD2,0x2CEC]),
        local_last_read='833/83F or897 laneweightconsumption before9B9; entirecombiner doesnotread2CCC',
        foreground_serialization='ordinarysame-core effect1E15/1F5C cannot preemptnormalvoice byitself; mailboxjobs servicedforeground113..123. No instantboundary ownership fromthisalone.',
        post_readers='knownpostpath references otherscratch; fullcomputedtable/mode/foreignstate readerbeforewrite closureUNRESOLVED',
        asynchronous_blocker='SHIISR19D can writeevery candidatecell duringrender; service5E acceptedSelection0; all-normalcached/bulk endpoints notclosed',
        DMA_worker='knownstaging/ring andsharedworker writes missprivateinterval conditionally; runtime reprogramming/foreignstate notclosed',
        required_new_proof='exclude/disable relevantasynchronouswriters and laterreader-before-write, notmerely restoreCPUregs',
        persistent_qualification=False,allocated=False)


def validate_original_evidence(out):
    r=original_rows()
    expected={0x2A2:'move r7,x:$002b',0x36D:'move x:$002b,r0',0x374:'move x:(r0)+,a y:(r4),y0',
        0x70C:'move x:$002b,r1',0x73B:'move b,x:(r1)+',0x2DD:'move a1,x:(r7+71)',
        0x1BDB:'move x:(r0),a0',0x829:'move a,x:(r2)+',0x82A:'move b,x:(r2)+',
        0x1F97:'move b,x:(r7)+',0x19D:'move x0,x:(r0)+'}
    for pc,text in expected.items():assert r[pc]['instruction']==text,(pc,r[pc])
    windows=[(0x281,0x2A3),(0x2C7,0x2DF),(0x36D,0x379),(0x70C,0x73F),(0x822,0x846),(0x87D,0x89E),
        (0x156,0x1D9),(0x1BB3,0x1BE8),(0x1EFA,0x1F10),(0x1F5C,0x1F9B),(0x260A,0x2622),(0x2779,0x278A)]
    table(out,'original-DSP-witnesses.csv',[r[p] for p in sorted(r) if any(a<=p<b for a,b in windows)])
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    paths=[ROOT/'builds/phase4-arm-events.asm',HOST/'arm-witnesses.asm',
        ROOT/'builds/phase11/replay/arm-initial/080269E4-08026B1E.asm']
    checks=[]
    for path in paths:
        if not path.is_file():continue
        n=0
        for line in path.read_text().splitlines():
            m=re.match(r'([0-9A-Fa-f]{8})\s+([0-9A-Fa-f]{4,8})\s+',line)
            if not m:continue
            a=int(m[1],16);raw=bytes.fromhex(m[2]);off=a-0x08010000
            assert off>=0 and arm[off:off+len(raw)]==raw,(path,a)
            n+=1
        checks.append(dict(file=path.relative_to(ROOT).as_posix(),byte_checked_rows=n,sha256=sha(path)))
    dump(out,'ARM-byte-checks.json',checks)
    dump(out,'nominal-host-projection.json',nominal_host_projection())
    for path,pages in [(FM,[372,373,431]),(RM,[75,76,77,78,103])]:
        reader=PdfReader(path)
        for p in pages:(out/f'{path.stem}-pdf{p}.txt').write_text(reader.pages[p-1].extract_text(),encoding='utf8',newline='\n')


def guards():
    paths=[p for d in ['original','firmware'] for p in (ROOT/d).rglob('*') if p.is_file()]
    paths += [DSP,FM,RM,Path(__file__).resolve(),ROOT/'tools/ct_livepatch_design.py',ROOT/'builds/phase3-selection0-channel0.asm',
        ROOT/'builds/phase4-arm-events.asm',GOLD/'assembly/layout.json',GOLD/'assembly/variablesaw.asm',
        GOLD/'dsp-first/program.asm',GOLD/'dsp-first/execution-pc.u16',GOLD/'dsp-first/blocks.csv',ROOT/'plaits/poc/fixed_model.py']
    for d in [PREVIOUS,HOST,ROOT/'builds/phase15/verified',ROOT/'builds/phase19c-p204b/final-v4',ROOT/'builds/phase11/replay']:
        paths += sorted(p for p in d.rglob('*') if p.is_file())
    for name in ['tools/ct_fixedstate_verify.py','emulator/tests/test_fixedstate_ownership.py']:
        if (ROOT/name).exists():paths.append(ROOT/name)
    return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}


def build(out):
    out=out.resolve()
    if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('fresh fixedstate reportchild required')
    before=guards()
    assert before['original/circuittracks-firmware-4486.syx']=='bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd'
    assert before['firmware/circuittracks-firmware-4486.bin']=='b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da'
    out.mkdir(parents=True);ev=out/'evidence';ev.mkdir()
    validate_original_evidence(ev)
    traffic=fallback_P_traffic(ev)
    table(out,'candidate-regions.csv',regions())
    table(out,'candidate-writers.csv',[r for a in target_words() for r in per_word_writers(a)])
    table(out,'candidate-readers.csv',[r for a in target_words() for r in readers(a)])
    lifetimes=[];sharing=[];service=[];irq=[]
    for a in target_words():
        tail=a<0x600;first=0x2CCC<=a<0x2CEC
        lifetimes.append(dict(address=f'X:0x{a:X}',last_read='36D/374 orallocator, repeated later' if tail else '833/83F/897 conditional' if first else 'effect/foreigndomainUNRESOLVED',
            proposed_transfer='afterselectedcombiner',transfer_proved=False,
            next_foreign_write='73B/2DD/ARMstartreset' if tail else 'nextretainedlookupcompletion pairedstore' if first else 'servicezero/effectconditionalstore',
            persistence='REJECTED or UNRESOLVED; no proven cross-blockowner',
            reset_modes='startupclears; event/steal/patch/project/mode/service continuation is NOT disabled by20C dispatcher',all_readers_writers_closed=False))
        sharing.append(dict(address=f'X:0x{a:X}',scope='slot0' if tail else 'global sharedscratch',
            others='allocatorreads timestamp; extendingtail entersslot1 at5C4' if tail else 'otherstockvoices usegeneratorweights/effects; unchangedpaths remain',
            can_sacrifice_under_current_design=False))
        service.append(dict(address=f'X:0x{a:X}',normal_parameter='1500 nominalrows projected, supplementaryeventreset; cache/bulkclosureUNKNOWN',
            generic='19D addressedX writes, not candidateprotected',service='5E operation0/port0 acceptsprivateaddress<8000; writeszero',
            cached='forceprivateMISS bystarta ifcache!=a; elsea-1,count2; serializedwitness reachesa',
            table_generated='1F97 initialized scratchdomains;204B/mailboxforeigntargets UNRESOLVED',
            result='SERVICE-ROBUST NO; all-normalhostclosureUNRESOLVED',observed=False))
        irq.append(dict(address=f'X:0x{a:X}',SHI='19D targetwrite maypreemptvoice, plus cursor/datahandling; no rangeguard',
            ESAI_DMA='reviewedISR/ring/staging missesunderretainedmapping; reprogrammingdomainsUNRESOLVED',
            worker='sharedX30002 queue writes/privatecorestate; no provenlowprivatealiasunderdocumentedmap; exactmappingconditional',
            foreground='generator/allocator/effect/tablejob scheduling; onlyknownforegroundno-preemption is not fullproof',
            result='not excluded; reject qualification'))
    table(out,'candidate-lifetimes.csv',lifetimes);table(out,'voice-sharing.csv',sharing)
    table(out,'service-collisions.csv',service);table(out,'irq-worker-collisions.csv',irq)
    ranks=[]
    for s in sets():
        ranks.append(dict(id=s['id'],addresses=' '.join(f'X:{a:X}' for a in s['words']),layout=s['layout'],words=7,
            original_role='selectedtail/globalweights/effectscratch',last_stock_reader='seeper-wordledger; no terminalcross-blockconsumer',
            writers='seeper-wordledger; completeclosureNO',cross_block='NOT PROVEN, retainedwrites/servicecapability',
            host_service='VERIFIED capability; all-normalcursorstatesUNKNOWN',IRQ_worker='SHI store notexcluded',
            other_voice='global scratch shared; slot0tail retainsallocator/lifecycle',short_absolute=False,
            relative_P_delta_to549=0,relative_nominal_cycle_delta_to549=0,
            cost_status='CALCULATED addressing only, allstateaddresses>3F; no newindirection forsplit',
            confidence='VERIFIED knowncollisions /UNRESOLVED residualdomains',ranking=s['ranking'],reason=s['reason']))
    table(out,'seven-word-ranking.csv',ranks)
    dump(out,'temporary-workspace.json',transient());dump(out,'state-layout.json',layout())
    dump(out,'initialization-contract.json',initialization());dump(out,'fallback-architectures.json',fallback_design(traffic))
    dump(ev,'service-address-fixtures.json',dict(status='TESTED integercounterexamplecapability model; no packets/device',
        examples=[service_witness(a,c) for a in [0x5BF,0x5C3,0x2CCC,0x2CEC] for c in [0xFFFF,a]],
        physical_ingress='UNRESOLVED; witness is static protocol reachability, not runtime event'))
    assert before==guards(),'guardedsourcechange'
    dump(out,'validation.json',dict(overall_result='REFUSED',qualified_seven_word_sets=0,
        qualified_fixed_X_words=0,temporary_proven=False,initialization_bounded='CONDITIONAL7-wordcontract; no provenstockowner',
        cross_block_persistence=False,other_paths_preserved='no patchmade; futurefallbackA mustrequalify',
        addressing_cost='boundedonlyconditionalhighfixed/splittemplate; no qualifiedcandidate',
        offline_patch_construction_justified=False,flashing_justified=False,
        lifetime_fixture='REFUSED: no QUALIFIED set; onlyarithmetic/refusal checks',source_hashes=before,
        candidate_pool='inherited5wordslot0tail +64wordstock scratch;2wordgap/active/highregions excluded',
        complete_writer_or_consumer_sets=False,negative_result='knowncollisionsandunclosedsets suffice; no falseabsenceproof',
        retained_stock_generator_work_removed=0,broad_RAM_sweep=False,
        CPU_execution=0,hardware_actions=0,firmware_or_renderer_modified=False,snapshot_branch='DEFERRED'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path)
    build(p.parse_args().output_dir)
