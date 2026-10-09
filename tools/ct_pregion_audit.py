"""Phase20C4: one exact P object, static ownership/closure ledger only.

No CPU, firmware builder, packets, hardware, downloads or renderer changes.
Capacity, scanned instructions and conditional layout never imply ownership.
"""
import argparse, csv, hashlib, json, re
from pathlib import Path
from pypdf import PdfReader
from ct_livepatch_design import original_rows

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'builds/phase20c-pregion'
LO,HI=0x3FF0,0x3FF7
LOAD_END=0x3FF9
CODE_LIMIT=0x3FEC
DATA=[(0x146A,0x14EF),(0x2309,0x2599),(0x262C,0x2644),
      (0x268C,0x2717),(0x2720,0x2779),(0x28DD,0x29EC),(0x29F6,0x2A2D)]

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def obj(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
def fresh(path):
    path=path.resolve()
    if path==BASE or not path.is_relative_to(BASE) or path.exists():raise ValueError('Fresh child of builds/phase20c-pregion required')
    path.mkdir(parents=True);return path
def write(p,text):
    with p.open('x',encoding='utf8',newline='\n') as f:f.write(text)
def dump(out,n,v):write(out/n,json.dumps(v,sort_keys=True,indent=2)+'\n')
def table(out,n,rr):
    with (out/n).open('x',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
def data_pc(pc):return any(a<=pc<b for a,b in DATA)
def dma_registers():
    return {0xFFFFEC-4*c+i:(c,k) for c in range(8) for i,k in enumerate(['DCR','DCO','DDR','DSR'])}
def decode_dcr(v):
    return dict(DE=(v>>23)&1,DIE=(v>>22)&1,DTM=(v>>19)&7,DPR=(v>>17)&3,
                DRS=(v>>11)&31,D3D=(v>>10)&1,DAM_destination=(v>>7)&7,
                DAM_source=(v>>4)&7,DDS=(v>>2)&3,DSS=v&3)
def overlap(a,b):return max(a,LO)<min(b,HI)
def counter_a_interval(start,dco,mode):
    if not 0<=dco<=0xFFFFFF:raise ValueError('24-bit DCO required')
    if mode==4:return [(start,start+1)]
    if mode!=5:raise ValueError('Unknown/offset mode not silently linearized')
    end=start+dco+1
    if end<=0x1000000:return [(start,end)]
    return [(start,0x1000000),(0,end-0x1000000)]

def protected():
    g=obj('builds/phase20c-pstate/source-v7/input-guards.json')
    # Keep preceding numeric qualification sealed; it is reused, never rerun.
    paths=['builds/phase20c-pstate/final-v4','builds/phase20c-pstate/checks-v4',
           'builds/phase19c-p204b/final-v4','builds/phase12/final',
           'builds/phase11/replay','builds/phase19b-handoff/final']
    for name in paths:
        for p in (ROOT/name).rglob('*'):
            if p.is_file():g[p.relative_to(ROOT).as_posix()]=sha(p)
    extra=['builds/phase3-selection0-channel0.asm','builds/phase3-selection0-channel1.asm',
           'builds/phase19b/documentation/DSP56300FM.pdf','builds/phase19b/documentation/DSP56724RM.pdf',
           'builds/phase11/arm-ingress/0801F51E-0801F554.asm',
           'builds/phase11/arm-publishers/0801F554-0801F5E0.asm',
           'builds/phase11/arm-initial/080269E4-08026B1E.asm',
           'builds/phase3-arm-mode.asm','builds/phase3-arm-selection.asm','builds/phase3-arm-callers.json',
           'tools/ct_pstate_prepare.py','tools/ct_pstate_verify.py',
           'tools/ct_pstate_check.py','plaits/poc/pstate/fixtures.inl']
    for name in extra:g[name]=sha(ROOT/name)
    for name,h in g.items():assert sha(ROOT/name)==h,name
    return dict(sorted(g.items()))

def arm_evidence(out):
    # Reuse already decoded, byte-proven witnesses; no fresh ARM disassembler.
    raw=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes();n=0
    source=obj('builds/phase19b-handoff/final/arm-ordering.json')['ARM_witnesses']
    selected=[]
    for r in source:
        b=bytes.fromhex(r['bytes']);a=r['address']
        assert raw[a-0x08010000:a-0x08010000+len(b)]==b;n+=1
        if 0x08029200<=a<0x080292B8:selected.append(r['line'])
    for name in ['builds/phase11/arm-ingress/0801F51E-0801F554.asm',
                 'builds/phase11/arm-publishers/0801F554-0801F5E0.asm',
                 'builds/phase11/arm-initial/080269E4-08026B1E.asm',
                 'builds/phase3-arm-mode.asm','builds/phase3-arm-selection.asm']:
        lines=[]
        for line in (ROOT/name).read_text().splitlines():
            m=re.match(r'(080[0-9A-Fa-f]{5})\s+([0-9a-fA-F]{4}(?:[0-9a-fA-F]{4})?)\s+',line)
            if m:
                a=int(m[1],16);b=bytes.fromhex(m[2]);assert raw[a-0x08010000:a-0x08010000+len(b)]==b;n+=1;lines.append(line)
        write(out/'evidence'/Path(name).name,'\n'.join(lines)+'\n')
    write(out/'evidence'/'ARM-upload.asm','\n'.join(selected)+'\n')
    return n

def build(out):
    out=fresh(out);(out/'evidence').mkdir();guard=protected();dump(out,'input-guards.json',guard)
    rows=original_rows();arm_count=arm_evidence(out)
    def require(pc,text):assert rows[pc]['instruction']==text,(hex(pc),text)
    for pc,text in [(0x2043,'mpy +y1,y0,a x:(r0)+,r4'),(0x204B,'move b,x:(r4)'),
                    (0x19D,'move x0,x:(r0)+'),(0x19B,'move x0,y:(r0)+'),
                    (0x1BC,'movep #$000029,x:$ffffee'),(0x1BE,'movep #$000021,x:$ffffeb'),
                    (0xDB6,'jmp (r1)'),(0x19AC,'jsr (r1)'),(0x2A5D,'rts')]:require(pc,text)
    windows=[(0x156,0x1DA),(0xDA0,0xDFB),(0x198D,0x19BD),(0x202B,0x204D),
             (0x25DB,0x25F8),(0x22F8,0x2309),(0x28D3,0x28DF),(0x2A2D,0x2A5E)]
    for a,b in windows:write(out/'evidence'/f'P{a:04X}-P{b:04X}.asm',
        '\n'.join(f"P:{pc:06X} {r['raw']} {r['instruction']}" for pc,r in rows.items() if a<=pc<b)+'\n')
    fm=PdfReader(ROOT/'builds/phase19b/documentation/DSP56300FM.pdf')
    rm=PdfReader(ROOT/'builds/phase19b/documentation/DSP56724RM.pdf')
    for prefix,pdf,pages in [('FM',fm,[101,147,150,151,153,154,189,190,195,196,200,201,372,373]),
                             ('RM',rm,[75,76,77,79,80,95,98,100,102,103,104,115,116])]:
        for p in pages:write(out/'evidence'/f'{prefix}-pdf{p:03d}.txt',pdf.pages[p-1].extract_text()+'\n')

    candidate=dict(range=[LO,HI],hex_range='P:[0x3FF0,0x3FF7)',words=7,word_bits=24,
        status='CONDITIONAL layout candidate, not reserved, initialized or qualified',
        selection=0,transport_channel=0,physical_core0_assignment='CONDITIONAL documented-profile assumption',
        prior_tested_state=[0x2D29,0x2D30],new_region_executed=False,renderer_redesigned=False,
        why='Single 16-word-aligned block above all known code; room for explicit two-word guards inside conditional4000 limit',
        maximum_future_code_end=CODE_LIMIT,code_budget_words=CODE_LIMIT-0x2A5E,
        measured_standalone_high_code=[0x2A5E,0x2C83],partial_old_module_end=0x2D27,
        complete_module_end='UNRESOLVED; must obey hard layout contract, no full module emitted',
        alignment='One24-bit word required for absolute MOVEM;16-word alignment is layout preference, not hardware requirement',
        seed_values=[0,0,0x200000,0,41943,0x200000,0],extra_flag_words=0,
        current_stock_upload_covers=False,whole_appended_range_ownership_claimed=False)
    dump(out,'candidate-region.json',candidate)

    streams=[];manifest=obj('firmware/dsp/build-4486/manifest.json')
    # All five immutable streams retained. Header counts are words, not bytes.
    for name,sel,ch in [('bootstrap',None,0),('selection0-channel0',0,0),('selection0-channel1',0,1),
                        ('selection1-channel0',1,0),('selection1-channel1',1,1)]:
        data=(ROOT/f'firmware/dsp/build-4486/{name}.boot24.bin').read_bytes()
        count=int.from_bytes(data[:3],'big');load=int.from_bytes(data[3:6],'big')
        assert len(data)==6+3*count
        same=ch==0;hit=same and overlap(load,load+count)
        streams.append(dict(stream=name,selection=sel,channel=ch,start=hex(load),count=hex(count),
            end_exclusive=hex(load+count),header_bytes=6,framing='BE24 count,BE24 load,then BE24 words; no separate entry',
            candidate_overlap=hit,status='VERIFIED bytes; physical endpoint isolation conditional',
            effect='Alternative channel0 image; reload ends epoch, untouched tail contents not reliable' if same else
                   'Different transport endpoint; not a following same-P record under endpoint-isolation premise'))
    assert not any(r['candidate_overlap'] for r in streams)
    assert next(r for r in streams if r['stream']=='selection0-channel0')['end_exclusive']=='0x2a5e'
    streams.append(dict(stream='Proposed extendedSelection0/ch0 object (not emitted)',selection=0,channel=0,
        start='0x0',count=hex(LOAD_END),end_exclusive=hex(LOAD_END),header_bytes=6,
        framing='Same single count/load object; total bytes49137',candidate_overlap=True,status='CALCULATED / CONDITIONAL documented boot contract',
        effect='All seven literal cells loaded on every completed reload; initialization once per epoch, not once forever'))
    table(out,'loader-coverage.csv',streams)

    dma=[];regs=dma_registers();direct=[]
    for pc,r in rows.items():
        if data_pc(pc):continue
        for m in re.finditer(r'x:\$([0-9a-f]+)',r['instruction']):
            a=int(m[1],16)
            if a in regs:
                c,k=regs[a];direct.append(dict(pc=hex(pc),channel=c,register=k,address=hex(a),
                    instruction=r['instruction'],classification='NORMAL AUDIO ISR rearm' if pc in [0x1BC,0x1BE] else 'BOOT/INIT direct configuration',
                    destination_provenance='Literal/bit23enable',P_candidate_result='BOUNDED-PROOF NO for reviewed configuration; not universal DMA preservation'))
    assert {int(r['pc'],16) for r in direct}=={0x1BC,0x1BE,0x2A2D,0x2A2F,0x2A31,0x2A33,0x2A35,0x2A37,0x2A39,0x2A3B,0x2A3D,0x2A3E}
    reviewed={0:(0x285AC4,0xFFFFA8,0x29),1:(0x286251,0x21,0xFFFFA4)}
    for c in range(8):
        dcr_addr=0xFFFFEC-4*c
        if c in reviewed:
            v,source,dest=reviewed[c];f=decode_dcr(v)
            require(0x2A2D+8*c,f'movep #${v:06x},x:${dcr_addr:06x}')
            assert f['DDS']==(1 if c==0 else 0) and f['DRS']==11+c and f['DTM']==5 and f['D3D']==0
            dr=counter_a_interval(dest,2,f['DAM_destination'])
            dma.append(dict(channel=c,DCR_address=hex(dcr_addr),DDR_address=hex(dcr_addr+2),DSR_address=hex(dcr_addr+3),
                initial_control=hex(v),enabled_control=hex(v|0x800000),enable_source=hex(0x2A3D+c)+' bset23',
                DDS=f['DDS'],destination_space='Y' if c==0 else 'X',destination_source='INIT literal;ISR1BC reset' if c==0 else 'INIT literal',
                destination_interval=str([(hex(a),hex(b)) for a,b in dr]),source_address=hex(source),
                DCO=2,transfers_per_counter_block=3,destination_mode=f['DAM_destination'],
                DRS=f['DRS'],trigger='ESAI/ESAI_2 receiveRDF' if c==0 else 'ESAI/ESAI_2 transmitTDE',
                transfer_mode='DTM5: peripheral request perword,repeat; DE not cleared at block end',
                reconfiguration='DirectISR resets DDR0 /DSR1 only; indirect register writes unresolved',
                normal_reachability='VERIFIED structural normal audio setup/rearm',can_architecturally_target_P=True,
                candidate_result='BOUNDED-PROOF NO while DDS remains Y/X, independent of subsequent cursor growth',
                complete_normal_exclusion=False))
        else:
            dma.append(dict(channel=c,DCR_address=hex(dcr_addr),DDR_address=hex(dcr_addr+2),DSR_address=hex(dcr_addr+3),
                initial_control=None,enabled_control=None,enable_source='UNRESOLVED post-ROM/indirect; no recovered executable direct enable',
                DDS=None,destination_space='UNRESOLVED (DDS2=P is legal)',destination_source='Unknown DDR'+str(c),
                destination_interval='UNKNOWN, not a fabricated normal interval',source_address=None,
                DCO=None,transfers_per_counter_block=None,destination_mode=None,DRS=None,
                trigger='RM5-10:32 request lines; ch6/7 differ at0/1 and excludeexternalpins; actualselectorUNKNOWN',
                transfer_mode='UNRESOLVED',reconfiguration='Unknown post-ROM initial state plus indirect-X-to-register domains',
                normal_reachability='UNRESOLVED; resetDE0 is not post-ROM state',can_architecturally_target_P=True,
                candidate_result='UNRESOLVED',complete_normal_exclusion=False))
    table(out,'dma-destinations.csv',dma)
    reconfig=list(direct)
    # One row per targeted register, not a broad indirect-memory census.
    for a,(c,k) in sorted(regs.items()):
        reconfig.append(dict(pc='P2043->2048/204B',channel=c,register=k,address=hex(a),
            instruction='R4=X[364+5*k] (linear table premise);readX:(R4),writeB toX:(R4)',
            classification='NORMAL AUDIO indirect register-alias obligation / UNRESOLVED',
            destination_provenance=f'Necessary:positiveX35F and compiled destination exactly{a:06X}; no attained record or normal value domain recovered',
            P_candidate_result='DCR DDS/DE,DDR/count/DSR preservation not proved; hypothetical capability is not normal witness'))
    reconfig += [dict(pc='P171/175->198/19D',channel='all',register='DCR/DCO/DDR/DSR/DOR',address='X:FFFFD0..FFFFF3',
        instruction='Paged savedcursor=((page<<8)-2)&FFFFFF then postincrement; inherited X/Y selector',
        classification='NORMAL PARAMETER/HOST endpoint-order obligation / UNRESOLVED',
        destination_provenance='Necessary e.g.pageFFFF givesFFFEFE and a bounded offset can reach register; no normalpageFFFF/length/context witness recovered',
        P_candidate_result='Cannot promote extended3FFFFmask to pagedpath exclusion; normal source/cursor/order not universally bounded'),
        dict(pc='ROM exit; hardware auto-update',channel='all',register='DCR/DCO/DDR/DSR/DOR',address='device DMA registers',
        instruction='ROM implementation unknown; DDR/DSR/count auto-update follows DCR',classification='BOOT/ROM residue / UNRESOLVED',
        destination_provenance='Reset DE0 documented, no compatible post-ROM all-channel snapshot/cleanup guarantee',
        P_candidate_result='No invented inactive channel2..7; DOR only matters if unknown mode selects offsets')]
    table(out,'dma-reconfiguration.csv',reconfig)

    pw=[]
    for pc,r in rows.items():
        s=r['instruction']
        if re.search(r',p:',s):
            pw.append(dict(mechanism='Explicit decoded P store',producer=hex(pc),normal_class='VERIFIED DATA,not code' if data_pc(pc) else 'UNRESOLVED decoded candidate',
                domain=s,candidate_result='EXCLUDED table decode' if data_pc(pc) else 'UNRESOLVED',evidence='Original bytes + P28D3/28D7/28D9 copy'))
    assert len(pw)==1 and pw[0]['producer']=='0x28de'
    pw += [dict(mechanism='SHI19B/19D direct data stores',producer='P156->198->19B/19D',normal_class='NORMAL PARAMETER +SERVICE',
        domain='Y:(R0)+ or X:(R0)+; noP selector',candidate_result='BOUNDED-PROOF NO directprivateP under compatible map; DMA registerindirection remainsopen',evidence='P199 branch15 and exact19B/19D opcodes'),
        dict(mechanism='DMA all8',producer='DCRn DDS2,DDRn,DCO/DOR',normal_class='NORMAL AUDIO /otherchannelsUNRESOLVED',
        domain='Reviewedch0Y/ch1X; othersunknown; reconfigurationunclosed',candidate_result='UNRESOLVED',evidence='dma-destinations.csv;dma-reconfiguration.csv'),
        dict(mechanism='Normal computed X writers',producer='P204B plussavedcursorSHI',normal_class='NORMAL AUDIO /NORMAL PARAMETER',
        domain='DirectX store, potentiallyDMA/memoryconfigurationeffects ifregisteralias domain admits them',candidate_result='UNRESOLVED indirectP influence; no recoveredPcollision',evidence='PriorfinalP204B compiledrecords/count remainUNKNOWN'),
        dict(mechanism='ARMprogram loader /bootstrap /ROM',producer='ARM29260->29200,bootstrapJMPFFFFFE',normal_class='BOOT/RELOAD, not ordinaryblockwork',
        domain='Onecount/loadPRAMrecord; laterROMresidueunknown',candidate_result='CONDITIONAL seed/reset percompletedextendedreload; ROM closureopen',evidence='loader-coverage.csv;rom-bootstrap-writers.json'),
        dict(mechanism='Selection switch /reset',producer='ARM1F51E/1F554;23438',normal_class='SERVICE/DIAGNOSTIC +BOOT/INIT',
        domain='Alternativechannel0upload andmemorymode/resetepoch',candidate_result='Ownership epoch ends; tailpersistence forbidden; noarbitraryPwriteproved',evidence='reload-semantics.json'),
        dict(mechanism='Peerworker/sharedalias',producer='channel1ICC writes',normal_class='NORMAL WORKER',
        domain='OwnprivateP; sharedPXY30000..38000 separate underRMmap',candidate_result='BOUNDED-PROOF NO via documentedsharedalias; exactendpoint/mapconditional',evidence='RM75/77;different transportargument')]
    table(out,'p-writers.csv',pw)

    service=[dict(path='5E addressedutility',ARM='1F308->269E4',DSP='19B/19D',activeSelection0='VERIFIED staticentry beforeenableguard; noSelection1required',
        destination='PrivateX/Y starts<8000, shared[30000,38000);nocountfinalendpointcheck',
        P_result='BOUNDED-PROOF NO directprivateP underreviewedmap',DMA_result='Coherent accepted start/count envelopes excludeDMA regs; cachedfirststoreorderopen, depositeddata cannotsetDDS2 orDE',
        value_constraint='private24bitword0;sharedbyte<<8 haslow8zero,DE0,DDS0; noarbitrary24bitwrite',status='VERIFIED code +BOUNDED-PROOF valuefacts; globalsideeffectsUNRESOLVED'),
        dict(path='X/Yreadback',ARM='29344/29528;5Eop1',DSP='188/1A0',activeSelection0='VERIFIED routineavailable',
        destination='X/Yread pluscursor/saveRAM; extraqueuedword',P_result='No directPstore',DMA_result='Read/cache/cursor sideeffects mayredirectlaternormalwrite; orderingunclosed',
        value_constraint='Read doesnotitselfdepositarbitraryPword',status='BOUNDED-PROOF localstores,notstatefree'),
        dict(path='DiagnosticSelection1',ARM='1F53C..548->29260(r0=1)',DSP='bootstrapROM +diagnosticprogram',activeSelection0='TransitionendsnormalSelection0epoch',
        destination='Channel0P[0,328),channel1P[0,168);rawtailnotreseeded',P_result='No directcountoverlapcandidate butnormalownershipends',DMA_result='Newprogram/ROM reconfiguresDMA; nobootresiduepromoted',
        value_constraint='Fixedimmutableprogrambytes,norecoveredarbitraryPdatapayload',status='VERIFIEDselectionbranch/streamcounts; compatibilityconditional'),
        dict(path='ReturnSelection0 /fullreset',ARM='1F532->1F554->1F568->29260(r0=0)',DSP='sameextendedload only iffuturepointer/objectchanged',activeSelection0='New epoch afterreload',
        destination='Currentstockcount2A5E excludesstate;futureexplicit3FF9countincludesall7',P_result='CONDITIONAL resetall7 literals onlyinproposedownedobject',DMA_result='Allchannels/mode/IRQ cleanup atROMexit notqualified',
        value_constraint='No enlargedobject orpacketconstructed',status='VERIFIED call chain /CALCULATED proposedcoverage'),
        dict(path='Arbitraryprogram-memorydebugwrite',ARM='No recoveredexternalcommand maps directlytoprivateP',DSP='No recoveredexecutablenormalMOVEMstore',activeSelection0='UNRESOLVED unseencomputed/ROMpathclosure',
        destination='Unknown',P_result='No positivewitness; absenceofdecodedcommandnotuniversalproof',DMA_result='Not aDMAexclusion',value_constraint='No inventedserviceopcode',status='UNRESOLVED; noOnCE/JTAG/SWDrecommendation')]
    service.append(dict(path='Other recovered diagnostic commands5C/5D/71',
        ARM='26962/2698A/269AA->1F51E with26B20 literal; guardedoncurrentmode!=1',
        DSP='FixedSelection1 program via29260; no arbitraryP literal setter',activeSelection0='Can request transition fromSelection0; endsownedepoch',
        destination='Same shortdiagnosticchannel0stream[0,328); ch1[0,168)',
        P_result='No directcandidatecountoverlap; cannotclaimtailpersistenceacrossmode/ROMchange',
        DMA_result='Selection transition changesactiveprogram/ROMstate; oldnormalDMAassumptionsend',
        value_constraint='Fixedtable-selectedpayload,notuserarbitraryprogramimage inrecoveredbranch',
        status='VERIFIED selectioncode bytes / CONDITIONAL endpointmap'))
    table(out,'service-p-writers.csv',service)

    rom=dict(status='UNRESOLVED authenticnormalpost-ROMwrite/executionclosure',
        bootstrap=[0,8],bootstrap_local_OMR='(incoming|0x400080)&~0x200000',return_ROM_entry='P:FFFFFE',
        main_direct_ROM_edges=[],direct_ROM_edge_scope='Byte-checkedmainlisting excludesknowncopieddata; notcomputedfloworhiddenROMcertificate',
        loader_contract='RM103:contiguousPRAMcount/load; startsatloadaddressafterallwords',
        application_late_ROM='No recovereddirectnormalROMcall; computeddispatch/return/exception andROMstate notclosed',
        normal_channels2to7_afterROM='UNKNOWN; resetDE0 notpromoted',
        reload='Documentedwriteatload/bootstrap; newepoch. NounobservableROMpathdeclaredsafe',
        firmware_execution=0,authentic_ROM_available=False)
    dump(out,'rom-bootstrap-writers.json',rom)
    omr=[r for pc,r in rows.items() if not data_pc(pc) and re.search(r',omr\b|(?:andi|ori).*\bomr\b',r['instruction'])]
    mode=dict(status='CONDITIONAL writableinternalPRAM profile, normalpreservationUNRESOLVED',
        requested_profile=dict(part='DSP56724/25',core=0,MS=1,MSW1=1,MSW0=0,P=[0,0x4000],X=[0,0x6000],Y=[0,0x4000]),
        candidate_is_private_internal_PRAM_in_profile=True,shared_range=[0x30000,0x38000],
        alternative_maps='RM76/77:core0P4K/8K/16K/24K/40K; modecanremapphysicalRAMbanks; core1allocationsdiffer',
        main_decoded_OMR_destinations=omr,zero_main_direct_writers_is_global_proof=False,
        actual_entry_OMR_and_runtime_preservation='UNRESOLVED ROMexit/endpoint/indirectexecutionandmodeepochs',
        MOVEM='RMPRAM+FM372/373 legalmutable24bitread/write; coherentread-after-write underfixedprofile andnootherwriter',
        TESTED_support='Reuse2,176fixturesand43casesatoldsynthetic2D29; candidate3FF0notexecuted, nopromotiontostockownership',
        cache_manual_caveat='RM95listsPCUcachefeature,butRM100Table5-2 marksSR19reserved. Do nottransplantgenericFMCEbitcontrol/constructorcachemodel.',
        generic_cache_transfer='FM153/154 PMOVEW hitupdatescache+backing,missbackingonly; PMOVERhitcache/missbacking;DMAPcachecoherencenotmaintained',
        cache_mode_requirement='Treatdevice-specificimplementation/control asUNRESOLVED. NoCEtransitionin3instructionsbeforePMOVE(FM154) wheregenericruleapplies.',
        prefetch='RM95seven-stagepipeline;FM150/151externalburst1..4reads. PrefetchreadsnotPstoresbutcannotproveallnoexecutionfrompadding.',
        padding_is_hardware_coherence_proof=False,actual_hardware_cycles=None)
    dump(out,'memory-mode.json',mode)

    edges=[];direct_hits=[];indirect=[]
    for pc,r in rows.items():
        s=r['instruction'];mn=s.split()[0]
        if data_pc(pc):continue
        if mn.startswith(('j','b')) and not mn in ['bset','bclr','btst','brk']:
            # A bit-test source may use(Rn) while its branch target is literal.
            # Only the control-target operand itself makes this an indirect edge.
            if re.search(r'\(r[0-7]\)$',s):
                indirect.append((pc,s));continue
            m=re.search(r'\$([0-9a-f]+)$',s)
            if m:
                a=int(m[1],16)
                if LO<=a<HI:direct_hits.append((pc,a,s))
        if mn in ['do','dor']:
            m=re.search(r'\$([0-9a-f]+)$',s)
            if m and LO<=int(m[1],16)<HI:direct_hits.append((pc,int(m[1],16),s))
    assert not direct_hits
    edges.append(dict(kind='Directbranch/call/loopendcandidate projection',producer='Originalbyte-checkedlisting excludingknowncopieddata',
        targets='No decodedtargetinsidecandidate',normal_result='BOUNDED-PROOF listingnonhit ONLY',proof_scope='NotCFG/ROM/selfmodification/indirectexecutionclosure'))
    assert {p for p,s in indirect}=={0xDB6,0xDBD,0xDC5,0xDCD,0xDEC,0xDF9,0x19AC}
    for pc,s in indirect:
        scheduler=pc==0x19AC
        edges.append(dict(kind='Computedcontroltransfer',producer=f'P:{pc:04X} {s}',
            targets='Initial14descriptor+0 entries281x12,202B,1A2B' if scheduler else 'Dispatchwrapper/actionpointers throughXtable/loadedR0/R1',
            normal_result='UNRESOLVED targetpreservation; nopositivecandidateentry',
            proof_scope='19A5 R1=Xdescriptor+0; producer/foreignmutationstillopen' if scheduler else
                        'Static55tablevaluescopiedP29F6..2A2D toX9DB..A12 arelow; dynamicindex/table/functionpointerclosure notproved'))
    for kind,producer,targets,result,scope in [
        ('Vectors/interrupts','FM101 VBA[7:0]alwayszero;RM115 C0..FAreserved','CandidateF0..F6 cannotbeavaliddocumentedvectorstart orsecondword for ANY alignedVBA','BOUNDED-PROOF NO directdocumentedvectorfetch underdeviceprofile', 'IndependentofactualVBA value; handlercomputedtargets/RTI/ROM/controlcorruptionremainunclosed'),
        ('Returns/stack','RTS/RTI;hardware/softwarestackextension','SavedPCunknown forallnormalcontexts','UNRESOLVED','Balancedsynthetichelperstackdoesnotqualifystockstack/IRQreturns'),
        ('Stocktailfallthrough','P2A5D RTS','Lastuploadedinstructionreturns','BOUNDED-PROOF localRTSdoesnotfallthrough2A5E','Other computed/exception/corruptedstack entriesnotexcluded'),
        ('Appendedmodulecontrol','Futurecompletecode mustendbefore3FEC','Alllegalexitsrestorecontext andJMP9D9;separateguardfence','CONDITIONAL noentrytodata underlayoutcontract','No completewrapperassembled; syntheticdonehaltsarenotstockcontinuations'),
        ('Decoder/cacheprefetch','Existingdecoderreadsnextword;externalburst1..4','Twoexplicitguardwordsperside; readsarenotexecution','CONDITIONAL structuralguardonly','No hardwarespecclaimthat2paddingboundseverypipeline/loop/exception')]:
        edges.append(dict(kind=kind,producer=producer,targets=targets,normal_result=result,proof_scope=scope))
    table(out,'execution-targets.csv',edges)

    band=dict(status='CALCULATED /CONDITIONAL layoutcontract,notconstructed',
        candidate=[LO,HI],code_budget=[0x2A5E,CODE_LIMIT],exit_fence=[0x3FEC,0x3FEE],
        fence_semantics='Terminalunconditionaltransfer torestorednaturalcontinuation9D9; actualwrappernotbuilt',
        before_padding=[0x3FEE,LO],after_padding=[HI,LOAD_END],explicit_NOP_words_each_side=2,
        leftover_to_conditional_RAM_end=[LOAD_END,0x4000],stock_tail_RTS=0x2A5D,
        hard_layout_requirements=['Noexecutableinstruction/extension overlapsguardsorstate','No branch/call/DOend/dispatchentry pointsatstate',
          'Everycopylengthbounded;initialloaderwritesentireobjectincludingseedandguards','Allnormalexitsrestoreandtransferbeforedata',
          'Completecodeplusunknownglue mustfit5518-wordbudget; nooverruninferredabsentfromold713template'],
        architectural_MOVEM_address_wrap='Absolute24bitaddress, noRn/modifier/postincrement; sevenfields individuallybounded',
        two_words_is_minimum_for_existing_decoder_only=True,universal_hardware_minimum_padding=None,
        recommendation='Atleast2explicitwordsoneachside plus terminaltransfer; extra padding doesnotcloseindirectwrites/execution',
        image_relocation='Do notextendstreaminplace:channel1 startsARMoffset8110;newwholeobjectrelocationneededinfutureauthorizedconstruction')
    dump(out,'guard-band.json',band)
    selection_callers=[r for r in obj('builds/phase3-arm-callers.json') if r['target'].lower()=='0x0801f51e']
    assert {int(r['site'],16) for r in selection_callers}=={0x0801D582,0x0801F302,0x08026962,0x0802698A,0x080269AA}
    reload=dict(status='CONDITIONAL futureownedextendedobject; currentstockhasnostateepoch',
        recovered_selection_callers=selection_callers,
        caller_scope='Existinghalfwordedgecensus plusreviewedboot/servicewindows; notcompletecomputedcallgraph; absenceofproject/patchreloadnotproved',
        bootstrap_and_payload_order=['29284bootstrapch0','29294selectedch0','292A6selectedch1'],
        loader_source_table='ARM08029700+4*selection forchannel0; +8 forchannel1; sender29200',
        source_cursor_count='Low16BEcount +2headerwords;AA-wordchunks,3bytes/word; sourcepointerdoesnotcontiguouslycontinueintoch1 asarecord',
        events=[
        dict(event='Normalaudioblock',desired='Retainall7',proved='UNRESOLVED forallnormalwriters/DMA/context; standalonecontinuityTESTEDonly'),
        dict(event='Projectload',desired='Noresetunless explicitDSPreload',proved='UNRESOLVED completecallancestry/cache/DMA/modepreservation; noeveryprojectloaderedge asserted'),
        dict(event='Patchload',desired='Retainoscillatorstate or explicitdocumentedreseed',proved='NoPuploadinreviewedparameterpath; universalP/modepreservationUNRESOLVED'),
        dict(event='Selection0payloadreload',desired='Resetall7 exactseedvalues oncepercompletedreload',proved='CONDITIONAL count3FF9/load0includesstate; resetacceptable,noextraflag'),
        dict(event='DiagnosticSelections switch',desired='Suspendownership; cannotrenderstateinotherselection',proved='VERIFIED Selection1branch; shorterloadleavestailcontentsbutnoownership/preservationguarantee'),
        dict(event='ReturnSelection0',desired='Completeextendedreloadandreseedbeforerender',proved='VERIFIED1F532->1F554->29260selection0; extendedobjectnotimplemented'),
        dict(event='FullDSPrestart',desired='Newseedepochaftercompleteownedload',proved='CONDITIONAL only; do notinferpower/resetRAMzero')],
        no_extra_flag_only_if_epoch_enforced=True,object_or_seed_emitted=False)
    dump(out,'reload-semantics.json',reload)

    ranked=[dict(rank=1,option='B. temporaryinstrumentedfirmwarestateobject',status='CONDITIONAL design-only,notauthorizedconstruction',
        why='Finiteobject+explicitmode/DMAadmission policy andsoftwarestorecoverage couldmakelifetimeenforceable; externalinterfacesonly',
        residual='All-write/DMAmediationcoverage,observereffects,cycles/recovery needproof; monitoringaloneisnotownershipcertificate'),
        dict(rank=2,option='A. selected-generatortakeover',status='CONDITIONAL largerone-wayredesign',
        why='Transfersownershipofexactselectedgeneratorrecordinstead ofassumingfreeRAM; prior7X takeoverdesignretained',
        residual='Disable selected387/77F producers bothpasses,protectagainstSHI/foreignwriters,newaux/guard/lifecycle/otherbankproof'),
        dict(rank=3,option='C. software-onlycontrolledreplacementpayloadwithexplicitwholemoduleownership',status='CONDITIONAL highest scope/cost; nocurrentimplementation',
        why='Explicitloader/mode/DMA/dispatchcontract removesopaqueownershipinheritance',
        residual='StockSynth2/processingpreservationandrecovery muchharder; notminimalcurrentPoC, no automaticrendererredesign')]
    dump(out,'ranked-options.json',ranked)
    qualification=dict(overall='REFUSED',ownership_classification='CONDITIONAL',candidate=[LO,HI],
        safe_seven_word_P_state_qualified=False,proven_owned_stock_P_words=0,offline_patch_construction_justified=False,
        known_normal_candidate_collision=False,all_normal_noninterference_proved=False,
        largest_remaining_blocker='NormalDMAregisterpreservation: P204B destination X[364+5*k]/count/recordvalue remainsUNKNOWN; pagedSHI cursor/order pluspost-ROMch2..7alsoopen',
        gates=dict(loader_seed='CONDITIONAL exactcount/loadcoverage',normal_stock_P_writers='PARTIALdirectexclusion; indirectDMAinfluenceopen',
          DMA='UNRESOLVED universal; knownch0/1BOUNDED-PROOF NO',service='BOUNDEDlocaldirectP/DDSexclusions,transitionsemanticsexplicit,universalclosureopen',
          ROM='UNRESOLVED',memory_mode='CONDITIONAL map,actualpreservationUNRESOLVED',cache='Devicecontrolambiguity/reservedSR19; nostockcertificate',
          execution='UNRESOLVED computeddispatch/stack/ROM/fullappendedCFG',guards='CONDITIONAL structurallayout'),
        next_step='Specify B temporarysoftware-enforcedobject plusDMAconfigurationadmission/coveragecontract; offline/externalinterfacesonly; no broadmemorysearch orpatchconstruction',
        hardware_debug_recommended=False,hardware_actions=0,firmware_or_renderer_modified=False,stock_CPU_execution=0,
        phase20A_suite_rerun=False,explanation='REFUSED means insufficientpositiveownershipproof,notprovenP-memoryimpossibility. Capacityandpartialnonhits do notqualifyoneblock.')
    dump(out,'qualification.json',qualification)
    validation=dict(status='VERIFIED source bytes /TESTED arithmetic; ownershipREFUSED',requested_reports=13,
        original_DSP_rows_byte_verified=len(rows),ARM_rows_byte_verified=arm_count,
        DMA_channels=8,known_DMA_configurations=2,targeted_registers=32,executable_direct_DMA_reference_rows=len(direct),
        direct_target_candidate_hits=len(direct_hits),decoded_indirect_transfers=len(indirect),
        apparent_P_store28DE_is_data=True,raw_postROM_register_values_invented=False,
        initial_seed_as_runtime_witness=False,complete_CFG_or_alias_closure=False,
        prior_numeric_result_reused=obj('builds/phase20c-pstate/final-v4/qualification.json')['overall'],
        preservation_guard_files=len(guard),all_guard_hashes_unchanged=True,firmware_builder_invoked=False,
        no_broad_X_or_P_free_memory_search=True,script_sha256=sha(Path(__file__)))
    dump(out,'validation.json',validation)
    for name,h in guard.items():assert sha(ROOT/name)==h,name
    dump(out,'hashes.json',{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    print(json.dumps(dict(overall=qualification['overall'],candidate=qualification['candidate'],classification='CONDITIONAL',
        DSP_rows=len(rows),ARM_rows=arm_count,DMA_channels=8,guard_files=len(guard)),indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True)
    build(a.parse_args().output_dir)
