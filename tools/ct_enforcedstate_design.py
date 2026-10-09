"""Phase20C5 design ledger and arithmetic model; no DSP patch/CPU/hardware.

Exactly two storage domains. Enforcement predicates are specifications, not
implemented firmware and not proof that every stock writer reaches a guard.
"""
import argparse,csv,json,re
from pathlib import Path
from collections import Counter
import numpy as np
from pypdf import PdfReader
from ct_pregion_audit import ROOT,protected,sha,write,dump,table,data_pc,decode_dcr
from ct_livepatch_design import original_rows

BASE=ROOT/'builds/phase20c-enforcedstate'
P_STATE=(0x3FF0,0x3FF7);X_STATE=(0x57B,0x582)
TMP=(0x3FC0,0x3FE0);POLICY=(0x3F60,0x3F7E);SHADOW=(0x3F80,0x3FA0)
FAULT=(0x3FE0,0x3FE1);CODE_END=0x3F5C

def fresh(p):
    p=p.resolve()
    if p==BASE or not p.is_relative_to(BASE) or p.exists():raise ValueError('Fresh enforcedstate child required')
    p.mkdir(parents=True);return p
def obj(p):return json.loads((ROOT/p).read_text())
def contains(span,a):return span[0]<=a<span[1]
def cpu_commit_spec(space,address,domain):
    """Range7 guard never confuses equal numeric addresses in P and X."""
    if domain not in ['P','X'] or space not in ['P','X','Y','L'] or not 0<=address<=0xFFFFFF:
        return 'DENY_INVALID_SPEC_INPUT'
    if space=='L':return 'REQUIRE_SPLIT_X_Y_COMPONENTS'
    if domain=='P' and space=='P' and contains(P_STATE,address):return 'DENY_STOCK'
    if domain=='X' and space=='X' and contains(X_STATE,address):return 'DENY_STOCK'
    if space=='X' and address>=0xFFF000:return 'CONTROL_ADMISSION'
    return 'PASS_IN_SPEC'
def dma_spec(dcr,channel):
    if not 0<=channel<8 or not 0<=dcr<=0xFFFFFF:return 'DENY_INVALID_SPEC_INPUT'
    d=decode_dcr(dcr)
    if d['DDS']==3 or d['DSS']==3:return 'DENY_RESERVED_SPACE'
    # Deliberate first-PoC restriction. Unknown P overlays/copies are accounted.
    if d['DDS']==2 or d['DSS']==2:return 'DENY_P_DMA_DURING_EPOCH'
    if channel in [0,1]:
        reference=[0x285AC4,0x286251][channel]
        if dcr&0x7FFFFF != reference:return 'DENY_AUDIO_PROFILE_CHANGE'
    return 'CONDITIONAL_NONP_CONFIG_REVIEW' # endpoints/updates/quiescence still required
def quiescent_spec(de,dtd,dact):
    return len(de)==len(dtd)==8 and all(x==0 for x in de) and all(x==1 for x in dtd) and dact==0
def jclr_classifier_cycles(address):
    """FM A-4/A-13: taken bit branch4, false conditional branch5."""
    if not 0<=address<=0xFFFFFF:raise ValueError('24-bit address required')
    n=0
    for bit in range(23,11,-1):
        if not address&(1<<bit):return n+4
        n+=5
    return n

def traffic(out):
    folder=ROOT/'builds/phase20c-pstate/high-p-v7'
    instructions={int(line.split()[0],16):line.split(' ',1)[1] for line in (folder/'program.asm').read_text().splitlines()}
    feature=np.zeros(16384,dtype=np.uint8)
    for pc,s in instructions.items():
        if s.startswith('move ') and 'x:>' in s:feature[pc]=1
    assert int(feature.sum())==18
    trace=np.memmap(folder/'execution-pc.u16',dtype='<u2',mode='r')
    with (folder/'blocks.csv').open() as f:blocks=list(csv.DictReader(f))
    with (ROOT/'builds/phase20c-pstate/final-v4/high-P-block-cycles.csv').open() as f:cycles=list(csv.DictReader(f))
    pos=0;records=[]
    for b,c in zip(blocks,cycles):
        n=int(b['instructions']);x=int(feature[trace[pos:pos+n]].sum());pos+=n
        records.append(dict(case=int(b['case']),block=int(b['block']),remaining_X_transfers=x,
            inferred_extra_P_cycles=5*x,existing_Pstate_model_cycles=int(c['nominal_and_interlock_cycles']),
            inferred_allP_data_model_cycles=int(c['nominal_and_interlock_cycles'])+5*x))
    assert pos==len(trace)
    table(out,'temporary-P-traffic.csv',records)
    x=[r['remaining_X_transfers'] for r in records];v=[r['inferred_allP_data_model_cycles'] for r in records]
    return dict(status='MEASURED old trace counts / CALCULATED unimplemented all-P-data conversion',sites=18,
        transfers_min=min(x),transfers_mean=float(np.mean(x)),transfers_max=max(x),
        added_cycles_min=5*min(x),added_cycles_mean=5*float(np.mean(x)),added_cycles_max=5*max(x),
        inferred_renderer_min=min(v),inferred_renderer_mean=float(np.mean(v)),inferred_renderer_max=max(v),
        new_renderer_executed=False)

def design(out):
    out=fresh(out);(out/'evidence').mkdir();guards=protected()
    for p in (ROOT/'builds/phase20c-pregion/final-v1').rglob('*'):
        if p.is_file():guards[p.relative_to(ROOT).as_posix()]=sha(p)
    dump(out,'input-guards.json',dict(sorted(guards.items())))
    rows=original_rows()
    require={0x202B:'move #$000967,r1',0x2043:'mpy +y1,y0,a x:(r0)+,r4',
             0x2048:'move x:(r4),b a,y1',0x2049:'mac +x0,y1,b x:(r0)+,x0',
             0x204A:'move y:(r5+n5),y0',0x204B:'move b,x:(r4)',0x2055:'move x:(r0)+,b y:(r4),y0',
             0x2057:'tfr y0,a x:$0015,y1',0x2070:'rts',0x198:'move x:$0010,r0',
             0x19D:'move x0,x:(r0)+',0x19E:'move r0,x:$0010',0x9D9:'move y:$0007,r0',
             0x9DD:'move x:(r0)+,a'}
    for pc,s in require.items():assert rows[pc]['instruction']==s
    for a,b in [(0x202B,0x2071),(0x156,0x1B4),(0x9D9,0xA20),(0x387,0x3C0),(0x70C,0x742),(0x198D,0x19B1)]:
        write(out/'evidence'/f'P{a:04X}-P{b:04X}.asm','\n'.join(f"P:{pc:06X} {r['raw']} {r['instruction']}" for pc,r in rows.items() if a<=pc<b)+'\n')
    fm=PdfReader(ROOT/'builds/phase19b/documentation/DSP56300FM.pdf')
    for page in [99,100,101,195,200,201,203,204,205,372,373,426,427,428,429,430,431,437,438,439]:
        write(out/'evidence'/f'FM-pdf{page:03d}.txt',fm.pages[page-1].extract_text()+'\n')
    rm=PdfReader(ROOT/'builds/phase19b/documentation/DSP56724RM.pdf')
    write(out/'evidence'/'RM-pdf115.txt',rm.pages[114].extract_text()+'\n')

    coverage=[]
    for pc,r in rows.items():
        s=r['instruction'];mn=s.split()[0]
        if data_pc(pc) or mn.startswith('j') or mn=='btst':continue
        if re.search(r',[xl]:>?\(',s):
            dest=re.findall(r',([xl]:[^\s]+)',s)
            coverage.append(dict(pc=hex(pc),instruction=s,components=';'.join(dest),
                status='DECODED store candidate, not established all-normal reachability',
                obligation='Prove actualEA excludes policy roots or mediate commit; Rn alone inadequate for indexed/predecrement/modulo/parallel cases'))
    assert len(coverage)==344
    table(out,'writer-coverage-obligations.csv',coverage)
    t=traffic(out)

    compare=[dict(domain='A appended P (CHOSEN)',seven_words='P:[3FF0,3FF7)',
        required_changes='Reserve initialized object; immutable code and typed owner P stores; DMA/control admission; SHI/204B and other-store mediation; control-flow/ROM epoch gate',
        writer_exclusions='All stock P accesses to owned data; all P DMA prohibited whileactive; CPU DMA register writes mediated; mode fixed',
        execution_risks='Complete store/control-flow coverage, initialquiescence and trustedstartup, privatePRAM/cacheprofile notyetproved',
        renderer_words=549,renderer_model_mean=12111.7855,renderer_model_max=18510,
        temporary_storage='Chosen P32 rendererworkspace +P30 serializedpolicyframe +P32 provisionaltypedshadow +P1diagnostic, not numericstate',
        stock_impact='Retain original selectedrequest/lookup/combiner/aux; selected mono overwritten; DMA overlays/reconfigs conditionallydenied',
        classification='PARTIAL design; no ownership certificate'),
        dict(domain='B deliberately reclaimed selectedgenerator X',seven_words='X:[57B,582)',
        required_changes='Permanentselected takeover before387/77F reads/writes; replace selectedrequest/completion obligation; newaux/guardcontract; actualX7 commit/read guard',
        writer_exclusions='Selected preparation, lane updates andall host/foreign X writers; DMA X orbit mustexclude7; commonguardcode protection stillneeded',
        execution_risks='Replacement of entire selectedgenerator semantics, auxiliary streams/2C66guard andpublication path unresolved',
        renderer_words=549,renderer_model_mean=7943.5521,renderer_model_max=13335,
        temporary_storage='Same Pframe/spill/control strategy possible;7numericstate inownedX; no separate naturallyfreeXclaim',
        stock_impact='Selected originalgenerator DISABLED; othernumericbank/slots intendedstock; selectedpostmodes1/2 andguard behavior notqualified',
        classification='CONDITIONAL moreinvasive fallback, NOT SELECTED')]
    table(out,'storage-domain-comparison.csv',compare)

    guard_options=[
        dict(rank=1,option='A skip only conflicting destination commit',site='Relocate whole70P helper202B..2070 via existing2-word entry202B/C; preserve/retargetDO endpoint',
            P_domain_action='X3FF0 isnot P3FF0. RouteDMA/control destinations throughadmission;ordinaryX passed. Retain all prefetches.',
            X_domain_action='Guard before2048read; matchingX57B..581 skipsread/MAC/write but advancesnextcoefficient/sourceprefetch andloop.',
            invasiveness='Only offending record sideeffect denied; value semantics notnamed',
            cycle_cost='P-domain fast+21/record,+4/entry; slow+19+unqualifiedvalidator/record',
            P_cost='89P proposed guardedclone incl5NOPs, notassembled',stock_effect='CONDITIONALLY CHANGED conflictingrecord/registerwrite only',
            reversibility='Only reload restoresoriginal epoch; no live selectedswitchback'),
        dict(rank=2,option='B redirect to explicit owned discard sink',site='Same relocated helper; guardsbeforeRMW ifXtakeover',
            P_domain_action='No fictional harmlessXaddress; extraownedP sink requires changed commit andknownseed',
            X_domain_action='Need explicit ownedXsink or differentPread/write primitive; neveruseoneof7numericfields',
            invasiveness='Extraobject pluschangedRMW semantics',cycle_cost='Extra read/write/mode costUNRESOLVED',P_cost='Extra >=1data word pluscode, notallocated',
            stock_effect='DISABLED outputofconflictingrecord; neighboringrecords retained',reversibility='Reload; no implicitstate restoration'),
        dict(rank=3,option='D rewrite destination at preparation',site='Producer ofX[364+5*k] UNKNOWN',
            P_domain_action='Can complementcommitguard onlyonceproducer/orderproved',X_domain_action='Cannotprevent laterSHI/foreigntablemutation',
            invasiveness='Lower steadycost butunrecoveredpublicationpoint',cycle_cost='UNRESOLVED',P_cost='UNRESOLVED',stock_effect='UNRESOLVED',reversibility='Unqualifiedtablelifecycle'),
        dict(rank=4,option='C zero count for conflictingrecord',site='X35F isONE countlatched intoLC, no perrecordcount exists',
            P_domain_action='Settingglobalcount0 disablesallrecords orfutureinvocations, notonecurrentrecord',
            X_domain_action='Cannot editlatchedLC bywritingX35F; cannotjumpoutDOwithoutlegaltermination',invasiveness='Broad/global effect',
            cycle_cost='Not rankedasminimalvalidmechanism',P_cost='UNRESOLVED',stock_effect='DISABLED entireloop, unrelatedrecordsemanticsUNKNOWN',reversibility='Not acceptable first design')]
    table(out,'p204b-guard-options.csv',guard_options)
    write(out/'evidence'/'guard-template.txt',
        'DESIGN ONLY, NOT ASSEMBLED\nP204B P-domain replacement in relocated202B helper:\n'
        'save SR into Y1 (dead afterMAC untilnextdefinition);copy R4 to A (deaduntilnextdefinition);\n'
        'AND/CMP rawtop12 withFFF000;branch tocontroladmission ifperipheral;restoreSR;\n'
        'otherwise original MOVE B,X:(R4). Slowmediator mustreproduce56-to24limiting/CCR.\n'
        'Five NOP words commonloop-tail;retarget DO LA tolastNOP. Neverhookone-wordLA204B withlongJMP.\n'
        'Y1/A scratchdeadness islocal; X1 isnotdestroyed. ExactglobalCCR/ABI/encoding needsqualification.\n')
    costs=[('Save SR in Y1',1,1,1),('Copy R4 into A',1,1,1),
        ('AND long immediate FFF000,A',2,2,2),('CMP long immediate FFF000,A',2,2,2),
        ('Long JEQ slow; false adds1',2,5,4),('Fast restore SR',1,1,0),
        ('Original MOVE B,X:(R4)',1,1,0),('Long JMP common tail',2,4,0),
        ('Slow restore SR',1,0,1),('Long JSR validator (body excluded)',2,0,4),
        ('Five common NOPs',5,5,5)]
    table(out,'guard-cost-template.csv',[dict(operation=s,proposed_words=w,
        fast_nominal_cycles=f,slow_nominal_cycles=c,classification='CALCULATED unassembled; interlocks/ABI excluded') for s,w,f,c in costs])
    assert sum(w for s,w,f,c in costs)==20
    assert sum(f for s,w,f,c in costs)-1==21 and sum(c for s,w,f,c in costs)-1==19

    admission=dict(status='DESIGN ONLY / PARTIAL',stock_central_point_exists=False,
        proposed_point='One serialized nonblocking control-commit validator with distributed store adapters',
        protected_roots='X DMA32registers+DOR4, PIC/mode/loader/control-flow; immutableloadedP code+allownedP data',
        policy='Duringactiveepoch no stockDMA P source orP destination. Reserveall8channels; do notdeclare2..7 harmless.',
        prohibited_DMA_control_writes='FM205 restrictsDMAperipheralaccess toTX/RXdataregisters; DMA->DMAcontrol isnot a supportedgeneral path undercompatibleprofile. Defensiveadmission stillrejectscontrol/peripheralunknowns.',
        channel0='Pin DCR285AC4(+DE),DSRFFFFA8,DCO2,DDSY/DRS11; DDR0 ISRreset29 preserved',
        channel1='Pin DCR286251(+DE),DDRFFFFA4,DCO2,DSSY/DDSX/DRS12;DSR1 ISRreset21 preserved',
        channels2to7='Inspect complete configuration; admit documented safeX/Y endpoints/modes, notblanket disable. Unknown/unsafeactiveconfig preventsPlaitsactivation.',
        runtime_update='Enabledconfiguration immutable except certifiedaudio rearm andclearDE. Reconfigure onlyafter DE0+DTD1 certification; otherwise returnNOT_READY withno change. No runtimepoll loop.',
        startup_quiescence='ClearDEall8; maskmaskable writerIRQs; await allDE0,allDTD0..7=1,DACT0; budgettimeoutrefusesactivation; reinitialize7 AFTER lastoldword completes.',
        eight_channel_status_evidence='RM PDF115 explicitly adds DTD6 at DSTR6 and DTD7 at DSTR7. Its DCH[10:9]/DCH[2:0] text is inconsistent; policy does not use the active-channel field as a quiescence witness.',
        quiescence_caveats='FM195 clearingDE mayfinishword;FM204DACTchannel0artifact;FM205DTDwordmode pendingtrigger caveat. Device/handoff barrier behaviorstillneedsproof.',
        startup_trust='Loadedentry/enforcementstub mustsurvive untilquiescence. UnknownoldP-DMA couldmodifycodebeforeguard; no software-onlytrust assumption silently made.',
        reentrancy='One P30 policyframe onlyif maskablecommitwriters serialized;NMIhandlers mustnotuseit; knownNOPvectors/stability requireclosure. Do notshare rendererP26frame.',
        coverage=dict(P204B='Identified entry/clone design',SHI='Identifieddata-laneclone198..19F',
            audio_literals='Only certifiedpinnedprofileexceptions',other_CPU_stores='344 decodedX/L candidates: actualEA/parallel/RMW coverageand exemptionsunproved',
            direct_P_stores='No recoveredexecutablenormalstore; typednewowner sites requireCFIcapabilities',
            mode_ROM='Guard allmode/control/returns; INIT/ROMnotvalidnormalcomputedentries;reloadendsownership'),
        all_known_classes_can_be_enforced_now=False,no_generic_MMUs_or_store_trap_assumed=True)
    dump(out,'dma-admission-design.json',admission)

    service=dict(status='CONDITIONAL design, notimplemented',preferred='Actualdestination commit AFTERloadingR0 andselectingX/Y, notrequestedARMaddress orcache',
        clone='P198..19F eightoriginalwords, entry198/199whole3wordwindow; preservecursor/save/RTI behavior; displacedbranchandhighlocaltargetsneedrelocation',
        P_domain='PrivateX/Y cannotdirectlyaliasprivateP in fixedmap. Xperipheral DMA/control writes routedtoadmission, notnumericX3FF0block.',
        X_domain='OnlyXeffective[57B,582) denied, Ysameintegernotblocked;checkEAbeforeeachword, notstartonly',
        fast_guard='Twelve JCLR bit-tests onactualunindexed R0 bits23..12 canclassifyFFF000pagewithoutclobberingA/B; classifier4..60modelcycles (falseadds1), normal lowRAMfirsttest4. Instructionformsunassembled.',
        cumulative='Testeveryactualpostincrementdestination; handlewrap/width/cached/pagedwrites. Blockedword stillconsumed; emulateexactoriginalAGUadvance onceandstoreX10.',
        bank='Do nottreatport/selection/spaceasinterchangeable; testbackingspaceandactualselector',
        error_reporting='Existing5Ereturnstatus2 cannotlieaboutdenials. Addsymbolicguard-status query/replyadapter, numericopcodeUNASSIGNED; P1faultlatchownedseparately, nohardwarepackets.',
        frame='Fastbitpath noA/Bclobber;slowvalidatorneedsABIpreservation andseparateserializedframe; data-laneoriginaldoesNOTsaveA becausebranches198bypasses168..16C',
        entire_service_disabled=False,existing_nonconflicting_service='IntendedUNCHANGEDvalues/protocol,cost/backpressureUNRESOLVED',
        external_ingress_semantics='No new arbitraryPwrite; diagnostic/reload invalidateepoch thenreseed; no live ownerread access admitted except statusadapter')
    dump(out,'service-write-guard.json',service)

    epoch=dict(status='CONDITIONAL one-way contract',domain='A appended P',seven_state=P_STATE,
        stages=['Modifiedpayloadload doesnotitselfpublishvalidstate',
                'Trustedstartup masks/restrictswriters,quiescesallDMA,validatesmemory/numeric/stack/profile andguardcoverage',
                'Finish original INIT; split/reorder earlyDMAarm2A3D/3E untiladmission; preserveboot/ICC/host prerequisites',
                'Write exact7state values afterquiescence; initializeframe/status; arm onlyadmittedDMA',
                'Publish selectedbank0/slot0 one-way gateway; otherbank/slots original',
                'Stayowned evenwhilevoiceidle; neverallowselectedstocktakeback ofnumericobject',
                'Payloadreload/reset/diagnostic transition ends epoch; reenteronlythroughfullstartup'],
        mode='Fixed compatibleMS110/Harvardmapping; no implicitOMR/M/SR constructortransplant. Rejectincompatibleactivation, notforceunaccountedmode.',
        no_eighth_numeric_or_activation_flag=True,
        why='Compile-timeone-wayimage plusdominatingstartup gateway; illegal INIT/ROMcomputedentries blocked. This flowproofisnot yet established.',
        diagnostic_word='P3FE0 distinctP1faultstatus, optionalfornumericstate butrequiredforlatcheddenialreporting; explicitlycounted, notconcealed8thphaseword',
        seed=[0,0,0x200000,0,41943,0x200000,0],initializer='7unrolled2wordimmediate +2wordMOVEM:28P /63nominalstartupcycles; nofieldsreadbeforeinit',
        boot_literals_only_not_sufficient=True,initialization_executed=False)
    dump(out,'ownership-epoch.json',epoch)

    writers=[dict(domain='A selectedstockpreparation387',removed='NONE',reason='It writesoldX/Yobjects, notnewP7; retainforlookup/aux/post',control='TypedPowner/immutablemodeguard preventsalias'),
        dict(domain='A selected77F request/completion',removed='NONE',reason='Retainworkpublication,bitmap/lookup,phaseandguard provenance',control='9B9completionmonooverwriteonly'),
        dict(domain='A oldmono32combiner',removed='Monooutputsubsequentlyoverwritten, not producerdeleted',reason='Aux2C02/2C24 andguard2C66retainstockcontract',control='Returnoriginal9D9with26liveouts'),
        dict(domain='B selected387 producer',removed='Selectedrecord reads/writes reachingQ57B..581 mustbe bypassedBEFOREuse',reason='First7of42fields areactivegeneratorinputs, notspare',control='Entry-context gate, preservedpostprefix46E..4D3 obligations unqualified'),
        dict(domain='B selected77F lanes',removed='Selected stocklane bodies BOTHpasses',reason='Theywouldinterpret/overwritePlaitsphase/pw asstockdescriptorfields',control='Replacementrequest/completion protocol needed, notsimplyskippublication'),
        dict(domain='B reset/host/table/foreignstores',removed='Onlycommits toownedX7denied unlessowner initializer/renderer',reason='Scalar/cache/bulk resets/servicecanotherwiseclobber',control='ActualEA+spaceguard; otherdestinationspassed')]
    readers=[dict(domain='A stockgenerator',suppression='NONE foroldstockdata; no newP7access allowed',reason='Preservealllookup/aux work',unresolved='AllstockPsource/CFIcapabilitycoverage'),
        dict(domain='A post/filter/mixer',suppression='NONE;original9D9 onward consumeschangedmonoandoriginalaux',reason='Naturalvoicegain/envelope/post retained',unresolved='Pitch/headroom, routing1/2 includeoldaux; purePlaits-onlyaudio notasserted'),
        dict(domain='B selectedQ generatorrecord',suppression='Bypass everyselectedstock read of57B..581',reason='Differentfield representation; cannotpartiallyreuseoldlane',unresolved='Complete42field/lane/post/aux replacement'),
        dict(domain='B lookup/auxcombiner',suppression='Selectedoldlanes/combiner cannotconsumeclaimedrecord',reason='Requestresultsand2auxstreams dependoldgeneration',unresolved='Newaux/guard2C66; do notzero/duplicatearbitraryguard'),
        dict(domain='B othercontexts',suppression='NONE intended',reason='Stride4A geometricallyseparates slots; doesnotexclude globalwriter aliases',unresolved='Allshared/globaldescriptor andservicebehavior')]
    table(out,'selected-path-writers.csv',writers);table(out,'selected-path-readers.csv',readers)

    save=[dict(strategy='A protected appendedPframe (CHOSEN)',frame='P[3FC0,3FDA),26raw24words',P_words=104,nominal_cycles=364,
        advantage='No borrowedXregion; separatefrompersistentstateandpolicyframe',limitation='FullrawMOVEM/PCR/CCR/restore/IRQABIunqualified; R0excludedbecause9D9reloads',qualification='CONDITIONAL'),
        dict(strategy='B hardwarestack',frame='Atleast13paired48bitframes for26words',P_words='>=52plusstaging',nominal_cycles='>=52plusstaging/restrictions',
        advantage='No new dataRAM ifheadroom existed',limitation='16hardwareentries;13+renderer3=16BEFORE existingcaller/IRQ. Doesnotfit; X/Ystackextension revivesownershipproblem.',qualification='REJECT firstPoC hardware-only'),
        dict(strategy='C block-local Xscratch',frame='ProposedX[2CCC,2CEC),32-wordloan, NOTselected',P_words=104,nominal_cycles=104,
        advantage='FasterlongXmoves',limitation='Borrow/lifetime/SHI/DMA/latereaders needexplicittemporaryguard; local lastread isnotownership. Loanflag/coverageextra.',qualification='UNRESOLVED'),
        dict(strategy='D reduce26 bydeadness',frame='A2/A1/A0 foregroundcandidate;R0alreadyomitted',P_words='potential-12',nominal_cycles='potential-42',
        advantage='9DD definesfullA beforeforegrounduse',limitation='IRQbefore9DD savesincomingA toY2003..2005; observability/otherpostpathsnotclosed. Keep26.',qualification='CONDITIONAL only, NOTselected')]
    table(out,'save-strategy.csv',save)
    dump(out,'temporary-workspace.json',dict(status='CONDITIONAL proposedownedobjects,notallocated',
        persistent7=P_STATE,renderer_frame26=(0x3FC0,0x3FDA),spills3=(0x3FDA,0x3FDD),controls3=(0x3FDD,0x3FE0),
        policy_frame30=POLICY,policy_R0_readonly_ABI=True,
        typed_control_shadow32=SHADOW,shadow_scope='Provisional16hardwareframesx2; typedDO/IRQ/call/data protocol,headroom/coverage UNQUALIFIED',
        fault_status1=FAULT,total_proposed_P_data_words=102,
        no_new_output_words=True,renderer_register_scratch16=True,
        register_spills='Existing19peakvs16helper-preserved registers leaves3spills. UsingM1..3 needs3extraM saves/restores+mode/IRQproof; wouldexpand26 to29. Notselected.',
        P_spills_controls='Convertremaining18longXsites tolongP MOVEM; samewordwidth, numeric/ABIqualificationpending, notexecuted',
        X_loan_selected=False))

    features=[]
    labels=['Synth1 selectednumericbank0/slot0','OtherSynth1slots','Synth2/bank1','MIDItracks','Drums','FX',
            'Service/update','Pack/projectload']
    for mechanism in ['A retainedstock+monooverwrite','DMAadmission/immutableepoch','204B/servicecommitdenial','B selectedtakeover alternative']:
        for feature in labels:
            if mechanism=='A retainedstock+monooverwrite':
                state='CONDITIONALLY CHANGED' if feature in [labels[0],'FX'] else 'UNCHANGED'
                scope='Intended arithmetic/data paths unchanged exceptselectedmono; sharedtimingnotqualified. UIbank-toSynthlabelremainsconditional.'
            elif mechanism=='DMAadmission/immutableepoch':
                state='CONDITIONALLY CHANGED' if feature in ['Service/update','Pack/projectload'] else 'UNRESOLVED'
                scope='Pin knownaudio0/1; admitsafeX/Y2..7, denyP-DMA/unsupportedliveconfig. Unknownlegitimateuser ofsuchDMA mustbeaccounted; noblanketclaimallfeaturesunchanged.'
            elif mechanism=='204B/servicecommitdenial':
                state='CONDITIONALLY CHANGED'
                scope='Only deniedrecord/write affected; unrelatedrecordsemantics notguessed, errorsnotreportedassuccess. Timing/ingressrate remainsunknown.'
            else:
                state='DISABLED' if feature==labels[0] else 'UNRESOLVED' if feature in ['FX','Service/update','Pack/projectload'] else 'UNCHANGED'
                scope='DISABLED meansselectedoriginalgenerator, replacedbyPlaitsintent; no globalother-bank suppression. Aux/guard/post andsharedtiming unqualified.'
            features.append(dict(mechanism=mechanism,feature=feature,status=state,scope=scope))
    table(out,'feature-impact.csv',features)

    renderer_bound=13379+1964+5*81*33
    cycles=dict(status='CALCULATED conditional model,nothardwaretiming/integratedWCET',
        current_Pstate_renderer=obj('builds/phase20c-pstate/final-v4/qualification.json')['cycles']['high-P'],
        state_transfer_vs_long_X=dict(min=3855,mean=4168.233377659574,max=5185),
        temporary_P_conversion=t,
        conservative_renderer_relaxation=dict(old_validcontrol_bound=13379,longaddress_relaxation=1964,
            maximum_81_static_memory_sites_times33_visits=2673,extraP_cycles_per_longXsite=5,conditional_allP_bound=renderer_bound,
            scope='Oneblock validoldnumericcontract,internalprivatezerowait,noIRQ; helperhasnoXmemory; eachforwardmainmemorysite atmost32samples+setup. Newsemantics/sequence notyetqualified.'),
        save_restore_nominal=364,dispatcher_nominal=24,fixed_controls_setup_nominal=25,return9D9_nominal=3,
        output_pointer_extra_cycles=0,output_pointer_reason='Retargetexisting2-wordMOVE#>0,R0 INSIDErenderer. Outsidepointersetupalone isoverwritten.',
        known_wrapper_nominal=416,retained_combiner_delta=0,retained_combiner_nominal=562,
        p204b=dict(clone_entry=4,fast_extra_per_record=21,slow_extra_per_record='19+U_validator',
            record_count_normal_bound=None,helper_calls_per_block_bound=None,
            q1_n20_partial_example=renderer_bound+416+4+21*20,
            cap20='IllustrativefuturePoCadmissioncap,NOTprovedstockrecordcount. RejectinglargerN changeswholeloop andmustbeaccounted, no capimplemented.'),
        service_fast_guard_cycles='4..60 perunindexedXword classifier (bit-testtemplate, falseadds1); rootrequests add U_validator/context',
        other_X_components='G actualEAguards, 4..60 forsimpleunindexedclassifieronly; indexed/modulo/parallelEA costUNRESOLVED',
        DMA_guard='No runtimepoll: NOT_READY onunquiescedconfig; completevalidatorboundUNRESOLVED. Knownaudio rearm bypass onlyunderpinnedprofile.',
        selected_writer_suppression=0,
        init_seven_nominal=63,startup_quiescence='T_start budget/timeout policy,oneepochcost; barrier/progress boundUNRESOLVED',
        one_voice_partial_formula='28708+416+Q*(4+21*Nfast+(19+U_validator)*Nslow)+serviceguards+otherEAguards+CFI+converter+interlocks+IRQ/DMAwaits',
        complete_one_voice_upper=None,deadline_fit_proved=False,no_saved_stock_work_subtracted=True)
    dump(out,'cycle-budget.json',cycles)
    known=712+89+37+28
    size=dict(status='CALCULATED designtemplates/allocations,notassembledcompleteimage',
        renderer_and_helper=549,state_load_store_additional_words=0,remaining18Psites_width_change=0,
        renderer_output_retarget_delta=0,save_restore26=104,fixed_controls_setup=10,
        dispatcher=16,retained_combiner_clone=32,return_original9D9=1,base_voice_wrapper=712,
        p204b_guarded_clone=89,p204b_extra_to70=19,SHI_data_clone_partial=37,
        initializer7=28,known_partial_subtotal=known,
        planning_allowances=dict(central_validator=256,startup_quiescence=96,CFI_registry_guard=128,status_reply_adapter=64,
            eight_simple_Rn_guard_veneers=216),
        planning_subtotal=known+256+96+128+64+216,
        allowance_status='Budgettargets only, no proofactualimplementationfits; calleradapters/displacedinstructions/modechecks/converter notincluded',
        proposed_data_words=102,state7=P_STATE,temporary32=TMP,policy30=POLICY,CFI32=SHADOW,diagnostic1=FAULT,
        code_limit=CODE_END,conditional_code_budget=CODE_END-0x2A5E,
        existing_conditional_appended_capacity=0x4000-0x2A5E,
        naive_24word_inline_per344_sites=344*24,
        naive_inline_does_not_fit=True,centralization_needs_proved_caller_exemptions=True,
        complete_added_P=None,all_template_encoding_ABI_and_DO_hazards_closed=False,
        no_patch_or_extended_stream_emitted=True)
    dump(out,'code-size.json',size)

    failure=dict(status='CONDITIONALdesignonly; reporting/muteABIunqualified',
        startup='Iftrust/mode/quiescence/stack/coveragecannotbeadmitted, doNOTpublishPlaitsownedepoch. No unknownstatezeroassumption.',
        conflicting_cpu_record='Rejectsinglecommit; forXtakeover skipreservedread+MACwhilepreservingnextprefetch andDOcount. No globalNreset.',
        service='Consumeexactoneword/advanceexactoriginalcursor once; denyactualcommit, latchP1faultstatus, replydenial notstatus2success; querynumericIDunassigned.',
        DMA='RejectPsource/destinationorunsafeupdate; oldadmittedconfiguration unchanged. DE0maystillhaveoldword: neverinitializeuntilquiescence.',
        fault_latch='Separateinitialized P3FE0, notpartofsevennumericwords/activationflag. No runtimecounter/flag hidden inphase/frequency.',
        epoch_loss='Onmapping/code/CFI guarantee loss invalidateowner andstopselectedrenderinguntilreload; selectedmute/postaux protocolmustbequalified, notassumedtofollowfrommono0.',
        silent_corruption_allowed=False,harmless_scratch_redirect_assumed=False,global_services_disabled=False,
        interrupt_masking='Serializesslowpolicyframe only; maskabledelivery delayed, NMIcoverage/IRQheadroom/FIFOlatency notqualified',
        recovery='Separateofficialexternal-interfaceacceptance/rollbackgate; noJTAG/OnCE/SWDdependency,recommendationoruse')
    dump(out,'failure-containment.json',failure)
    qualification=dict(overall='PARTIAL',chosen_domain='A appended protected P',seven_object=P_STATE,
        state_ownership_guaranteed_by_implemented_runtime=False,offline_patched_image_technically_justified=False,hardware_flashing_justified=False,
        stock_features_all_unchanged=False,one_way_epoch_and_init_defined=True,
        bounded_control_points=['Whole helper entry202B/C;70P clone plus five-word DO-tail proposal, unassembled','SHIDataentry198/199 completewindow','AudioDMAsetup/rearm underpinnedprofiles',
            'One proposedcentralcommitvalidator, notastocktrap'],
        missing=['All344decodedstorecandidates/exemptions andactualEA/parallel/RMW coverage',
                 'Completeindirectcall/return/ROM/stack capability andimmutable-codeclosure',
                 'Trustedstartup +eightchannelquiescence underrealhandoff/memoryprofile',
                 'Concretevalidator/reportadapter/saveABIencoding andreentrancy/IRQ latency qualification',
                 'Wholeone-voice/scheduler/service eventcounts andcompletecostbound',
                 'Selectedcontrols/pitch/headroom/recovery stillseparategates'],
        largest_remaining_blocker='No centralizedstockstore trap: distributed actualEA/commit+CFI coverage unclosed. Two hookedwriters arenota guarantee.',
        next_step='Finite source/ISA coverage certificate for everyX/Lstorecomponent capableofDMA/control writes andevery P/read/indirect-control boundary; selectprovedexemptionsor exactadapters beforeany patchedimage.',
        no_broad_free_memory_search=True,exactly_two_storage_domains=True,third_domain_introduced=False,
        stock_CPU_execution=0,new_renderer_execution=0,firmware_repacked=False,hardware_actions=0)
    dump(out,'qualification.json',qualification)
    validation=dict(status='VERIFIED input/source / CALCULATED design,qualificationPARTIAL',required_artifacts=14,
        original_DSP_rows_byte_checked=len(rows),original202B_helper_words=70,p204b_template_extra_words=19,
        store_candidates=344,not_complete_reachable_store_registry=True,known_X_memory_sites=81,
        reused_43case_trace=True,trace_instructions_read=34997772,numeric_suite_rerun=False,
        new_enforcement_tests_are_spec_arithmetic_only=True,native_guard_code_assembled=False,
        new_P7_candidate_executed=False,data_objects_reserved=False,guard_inputs=len(guards),
        source_sha256=sha(Path(__file__)),stock_bytes_or_renderer_modified=False)
    dump(out,'validation.json',validation)
    for name,h in guards.items():assert sha(ROOT/name)==h,name
    dump(out,'hashes.json',{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    print(json.dumps(dict(overall='PARTIAL',domain='P',state=P_STATE,known_partial_P=known,
        complete_cycles=None,store_candidates=len(coverage),guards=len(guards)),indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);design(a.parse_args().output_dir)
