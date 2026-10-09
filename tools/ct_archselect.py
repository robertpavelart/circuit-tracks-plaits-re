"""Phase20C6 architecture comparison: static evidence and planning, no patch/CPU.

Reuses sealed ledgers. Does not scan new universal writer domains or run DSP code.
Per-word role labels are scoped classifications, never ownership certificates.
"""
import argparse,csv,json,re
from pathlib import Path
from ct_livepatch_design import original_rows,save_registers
from ct_pregion_audit import ROOT,sha,write,dump,table
BASE=ROOT/'builds/phase20c-archselect'
PRE='builds/phase20c-enforcedstate/final-v3'
REQUIRED=['comparison-criteria.csv','modification-sites.csv','selected-slot-state-map.csv',
 'takeover-candidate-words.csv','auxiliary-dependencies.csv','request-completion-dependencies.csv',
 'service-impact.csv','save-frame-comparison.csv','code-size-comparison.csv','cycle-comparison.csv',
 'global-risk.csv','failure-containment.csv','offline-testability.json','scalability.json','decision.json','validation.json']

def obj(n):return json.loads((ROOT/n).read_text(encoding='utf8'))
def csvrows(n):
    with (ROOT/n).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
def fresh(out):
    out=out.resolve()
    if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('Fresh archselect child required')
    out.mkdir(parents=True);return out
def guards():
    g=obj(PRE+'/input-guards.json')
    for folder in [PRE,'builds/phase20c-enforcedstate/checks-v3',
        'builds/phase20c-livepatch-design/final-v2','builds/phase20c-fixedstate/final-v1']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file():g[p.relative_to(ROOT).as_posix()]=sha(p)
    for n in ['tools/ct_enforcedstate_design.py','tools/ct_enforcedstate_verify.py',
        'emulator/tests/test_enforcedstate_design.py','builds/phase20c-pstate/final-v4/high-X-block-cycles.csv']:
        g[n]=sha(ROOT/n)
    for n,h in g.items():assert sha(ROOT/n)==h,n
    return dict(sorted(g.items()))

def state_map():
    out=[]
    def add(space,a,group,label,role,evidence,retain=True):
        out.append(dict(space=space,address=f'0x{a:X}',group=group,classification=label,
            role=role,evidence=evidence,retain_for_A=retain,
            takeover_ownership_qualified=False,status='VERIFIED scoped interface; complete ownership UNRESOLVED'))
    for j in range(8):
        add('X',0xEB+j,'descriptor','MUST RETAIN',
            ['function281','kernel pointer1960','control pointer11F','secondary pointer131',
             'mailbox pointer57A','sample pointer59F','context6 (general role unresolved)','bank0'][j],
            '2881 initialization;198D/19BF traversals,19AC/19E6')
    lane_roles=['kernel pointer','fraction/control','repeat count','branch selector','flags',
        'product coefficient','phase/correction coefficient','base/correction7','base/correction8',
        'prepared phase increment','interpolation10','interpolation11','interpolation12','interpolation13']
    for j in range(0x4A):
        a=0x57A+j
        if j==0:label='MUST RETAIN';role='event mailbox';ev='29D consume/29E clear; ARM21246'
        elif j<=42:
            k=j-1;label='GENERATOR-ONLY';role=f'lane{k//14} +{k%14} {lane_roles[k%14]}'
            ev='387..46D preparation;79D..99D both passes; generator-only does not mean auxiliary-independent'
        elif j<=48:label='MUST RETAIN';role=f'current mono/aux coefficient {j-43}';ev='472/476 reads;9AF/9B7 current update;9C5..9D6'
        elif j<=68:label='POST-OWNED';role='post selector/coefficients/history/gain inputs';ev='47E..4D3;9DD..A94'
        elif j<=71:label='MUST RETAIN';role='three lifecycle update terms';ev='70C..73B writes;36D/374 reads'
        elif j==72:label='ALLOCATOR-OWNED';role='timestamp';ev='2DD writer;1BB7/1BDB six-slot scan'
        else:label='UNKNOWN';role='ARM start-reset word; not free';ev='08021A22/54/5E; complete consumers unresolved'
        add('X',a,'event/coefficient block',label,role,ev)
    known={3:('ALLOCATOR-OWNED','processed lifecycle flags','2C0/2C5, allocator1BB3'),
        0x10:('MUST RETAIN','current note-follow','5C0/5CB'),
        0x11:('ALLOCATOR-OWNED','primary envelope level, also allocation input','4F3..55B,1BB3'),
        0x16:('MUST RETAIN','scaled current note','5CC,6A7'),
        0x2E:('MUST RETAIN','note-level-sensitive envelope target','ARM2715E,4E7'),
        0x34:('MUST RETAIN','second envelope target','ARM27214,4D5'),
        0x3A:('MUST RETAIN','note-follow target','ARM27308,5C1'),
        0x3B:('MUST RETAIN','note-follow step','ARM27FA4,5C2..5C9'),
        0x3C:('MUST RETAIN','note-follow smoothing','ARM27FA4,5C2..5C9'),
        0x3D:('MUST RETAIN','note-follow seed','ARM27FA4,32A/32B')}
    for j in range(0x60):
        label,role,ev=known.get(j,('UNKNOWN','control/envelope/modulation field; retain by policy','V stride60,281/4D5/657; full scalar meaning unresolved'))
        add('Y',0x11F+j,'control V',label,role,ev)
    for j in range(0x28):
        if j<6:label='GENERATOR-ONLY';role=f'lane{j//2} '+('phase' if j%2 else 'mask/mode');ev='79D,7E4/7F9 and alternate phase stores; event333..335'
        elif j<12:label='MUST RETAIN';role=f'mono/aux ramp delta{j-6}';ev='477/47B preparation;9AF ramp consume'
        else:label='POST-OWNED';role='nonlinear/filter retained sample state';ev='9DD R4=S+C; BDD and alternate post paths'
        add('Y',0x59F+j,'sample S',label,role,ev)
    for j in range(12):
        add('X',0x1960+j,'kernel nominal footprint','GENERATOR-ONLY','nominal selected kernel word',
            'D+1;387 R5/R2 dynamic kernel stores3C2; complete dynamic footprint not bounded')
        add('Y',0x1960+j,'kernel reset mirror','UNKNOWN','selected kernel-associated reset word',
            '332 X2->R5;338 writes12Y; full producer/consumer footprint unresolved')
        add('X',0x19F0+j,'kernel coefficient nominal footprint','GENERATOR-ONLY','kernel base+90hex coefficient word',
            '3B4/3B5/3BB R2=R5+90hex;3C2 dynamic stores;97B X:(R3+144decimal) reads firstword per lane; extent/other-slot alias unresolved')
        add('X',0x1A80+j,'kernel template source footprint','SHARED','kernel base+120hex source coefficient',
            '3BF X:(R2+N2),N2=90hex; no ownership surrendered')
    shared=[('Y',0xA01,0xA61,'three interleaved lane buffers','789..78D clear;lane accumulations;9C8..9D6'),
        ('X',0x2C02,0x2C22,'auxiliary0','9CA pre-add A;9E1..9FD modes1/2'),
        ('X',0x2C24,0x2C44,'auxiliary1','9CD first-two-lane sum;9FD/A09'),
        ('X',0x2C46,0x2C86,'phase/index and mono scratch','7F1/7F2;first32 overwritten9D8;2C66 guard'),
        ('X',0x2F30,0x2F35,'pass/queue globals','198D/19BF;81B/847/975/977'),
        ('X',0x2DF0,0x2E10,'bank0 sample sum','A82..A94;other same-bank slots share'),
        ('X',0,8,'current generator globals','387/77F preparation, not persistent per voice'),
        ('Y',0,8,'current generator globals','77F/9B8 Y7 post cursor, not persistent per voice')]
    for space,lo,hi,role,ev in shared:
        for a in range(lo,hi):
            add(space,a,'shared invocation/protocol','SHARED',role,ev)
    for space,a,role,ev in [('X',0xCC,'bank','77F/780'),('X',0x2C,'slot index','19AD/19E7'),
        ('X',0x28,'control pointer','281 preparation'),('X',0x29,'coefficient pointer','29F/392'),
        ('X',0x2A,'sample-state pointer','296 publication;38B reload'),
        ('X',0x2B,'update-tail pointer','281/70C'),('X',0x9D5,'descriptor traversal cursor','19A3/19CE'),
        ('X',0x30000,'queue publication','81B'),('X',0x30002,'queue start, extent dynamic','worker120/126')]:
        add(space,a,'shared context/queue','SHARED',role,ev)
    assert len({(r['space'],r['address']) for r in out})==len(out)
    return out

def candidates():
    rows=[]
    for s,lo,hi,kind in [('X',0x57B,0x5A5,'Q'),('X',0x1960,0x196C,'kernel'),
        ('X',0x19F0,0x19FC,'kernel coefficients'),
        ('Y',0x59F,0x5A5,'phase/mask'),('Y',0x1960,0x196C,'kernel mirror')]:
        for a in range(lo,hi):
            k=a-0x57B if kind=='Q' else None
            thin=k is not None and k//14==2 and k%14 in [0,1,10,11,12,13]
            rows.append(dict(space=s,address=f'0x{a:X}',family=kind,
                proposed_takeover='last-lane six-field thinning possibility' if thin else 'selected-generator candidate only',
                stock_producers='387 preparation/reset/host/foreign classes need exclusions',
                stock_consumers='phase-only slice may omit these reads; alternate classes/entry/reset still unclosed' if thin else 'retained lane/aux/guard or unresolved dynamic kernel dependence',
                other_voice_scope='nominal slot stride separates; dynamic/foreign coverage unresolved',
                service='arbitrary writes cannot be ignored across blocks; local actual-EA protection needed',
                qualified=False,classification='CONDITIONAL six-field hypothesis' if thin else 'UNRESOLVED / not reclaimable under retained work'))
    assert len(rows)==84 and sum(r['proposed_takeover'].startswith('last-lane') for r in rows)==6
    return rows

def liveness(rows):
    # Explicit selected boundary observations, not an unvalidated general DSP
    # use/def decoder. Unknown caller/IRQ observability retains conservative set.
    assert rows[0x9D9]['instruction']=='move y:$0007,r0'
    assert rows[0x9DD]['instruction']=='move x:(r0)+,a'
    assert rows[0x168]['instruction']=='move a0,y:$2003'
    assert rows[0x16A]['instruction']=='move a1,y:$2004'
    assert rows[0x16C]['instruction']=='move a2,y:$2005'
    observations={
        'R0':('REDEFINED','9D9 replaces R0 before9DD; excluded from save'),
        'R4':('LIVE','9D9 does not redefine;post BDD readsY:(R4) atBED'),
        'A':('FOREGROUND DEAD / IRQ OBSERVABLE','9DD full A definition;168/16A/16C IRQ snapshot prevents universal dropping'),
        'B':('MODE-DEPENDENT DEFINED / CALLER UNKNOWN','AA8 defines B on selectedBDD; all other post/caller/IRQ paths not closed'),
        'Y7':('LIVE MEMORY','9D9 loads post X pointer from Y7; cannot use as persistent flag')}
    out=[]
    for reg in ['R0']+save_registers()+[f'M{i}' for i in range(8)]+['OMR','LA/LC/stack','Y7']:
        base='A' if reg.startswith('A') and len(reg)==2 else 'B' if reg.startswith('B') and len(reg)==2 else reg
        cls,ev=observations.get(base,('UNRESOLVED caller/IRQ liveness','no bounded all-mode deadness proof; selected memory takeover does not waive caller/IRQ ABI'))
        out.append(dict(field=reg,A_classification=cls,B_classification=cls,evidence=ev,
            saved_in_both=reg in save_registers(),reason='Same natural9D9/post boundary; speculative earlier B entry can only add live-ins until designed'))
    return out

def sites(rows):
    out=[]
    def add(arch,role,address,kind,action,status='CONDITIONAL design'):
        out.append(dict(architecture=arch,role=role,address=address,count_kind=kind,action=action,status=status))
    for pc,role in [(0x9B9,'dispatcher'),(0x202B,'P204B whole helper entry'),(0x198,'SHI actual data commit clone'),
        (0x2A3D,'DMA0 enable gateway'),(0x2A3E,'DMA1 enable gateway')]:
        assert pc in rows
        add('A',role,f'P:0x{pc:X}','KNOWN_ORIGIN_PROPOSED_EDIT','Guard/redirect complete instruction window; encoding/ABI pending')
    for r in csvrows('builds/phase20c-pregion/final-v1/dma-reconfiguration.csv'):
        if r['pc'].startswith('0x') and int(r['pc'],16) not in [0x2A3D,0x2A3E]:
            add('A','pinned safe audio setup/rearm',f"P:{r['pc']}",'KNOWN_REVIEW_NO_EDIT',r['instruction'],'VERIFIED literal; exemption conditional on immutable profile')
    for role in ['new state transfer63 operands','save/restore52 MOVEMs','startup/initializer gateway',
                 'central DMA/control validator','typed control shadow','denial/status adapter']:
        add('A',role,'APPENDED, exact placement unassigned','NEW_COMPONENT_NOT_STOCK_SITE','Explicit module; count not an origin instruction count')
    for role in ['remaining actual-EA adapters/exemptions (reuse344-candidate ledger)',
        'mode/ROM/indirect-control/return boundaries','reload/reset/diagnostic boundary','trusted pre-quiescence entry',
        'IRQ serialization/FIFO and safe failure transition','converter/headroom and workspace initialization']:
        add('A',role,'UNRESOLVED','UNRESOLVED_SITE_SET','Finite proof/implementation obligations, not counted as one code site','UNRESOLVED')
    for pc,role in [(0x387,'selected preparation entry'),(0x79D,'selected lane consumer entry'),(0x9B9,'selected completion/combiner gateway')]:
        add('B',role,f'P:0x{pc:X}','KNOWN_ANCHOR_NOT_FINITE_EDIT','Anchor only; exact selected discriminator, displaced effects and continuation unqualified')
    for role,address in [('phase reset','P:0x333..339'),('guard phase producer','P:0x7E4..7F9'),
        ('lane cursor/loop exit','P:0x979..99D'),('request bitmap','P:0x791..799'),
        ('worker publish/consume','P:0x81B/847/975/977'),('six ramps','P:0x9A5..9B8'),
        ('SHI commit protection','P:0x198..19F'),('table RMW protection','P:0x2048/204B')]:
        add('B',role,address,'KNOWN_OBLIGATION_EDIT_SET_UNKNOWN','Retain/rewrite/protect as required; no exact patch set claimed')
    for role in ['seven-word ownership transition','remaining X/DMA writers to chosen object',
        'safe P code/save workspace','selected early-boundary save/restore and ABI','reload/error/control boundaries']:
        add('B',role,'UNRESOLVED','UNRESOLVED_SITE_SET','Not proved eliminable by local selected suppression','UNRESOLVED')
    return out

def projections(out):
    a=csvrows(PRE+'/temporary-P-traffic.csv')
    b=csvrows('builds/phase20c-pstate/final-v4/high-X-block-cycles.csv')
    assert len(a)==len(b)==7520
    outrows=[]
    for ra,rb in zip(a,b):
        assert (ra['case'],ra['block'])==(rb['case'],rb['block'])
        outrows.append(dict(case=ra['case'],block=ra['block'],A_renderer=int(ra['inferred_allP_data_model_cycles']),
            B_renderer=int(rb['nominal_and_interlock_cycles'])+int(ra['inferred_extra_P_cycles']),
            status='CALCULATED hypothetical all-P temporary conversion on existing traces; no new execution'))
    table(out,'paired-cost-projections.csv',outrows)
    result={}
    for arch in ['A','B']:
        vals=[r[arch+'_renderer'] for r in outrows]
        result[arch]=dict(renderer_min=min(vals),renderer_mean=sum(vals)/len(vals),renderer_max=max(vals),
            partial_wrapper_mean=sum(vals)/len(vals)+416,partial_wrapper_max=max(vals)+416)
    return result

def build(out):
    out=fresh(out);(out/'evidence').mkdir();g=guards();dump(out,'input-guards.json',g)
    r=original_rows();m=state_map();c=candidates();live=liveness(r);mods=sites(r);cost=projections(out)
    require={0x9CA:'add b,a a,x:(r3)',0x9CD:'move a,x:(r5)+',0x7F1:'add y0,a a1,x:(r2)+',
        0x7F7:'jcs >$07fa',0x7F9:'move a1,y:(r4)',0x79B:'do #$0003,$099e',0x7C8:'do x:(r0)+,$099a',
        0x19E6:'jsr $077f',0x9B8:'move r0,y:$0007',0x9D8:'move a,x:(r1)+'}
    for pc,s in require.items():assert r[pc]['instruction']==s,(pc,s)
    for lo,hi in [(0x156,0x1B4),(0x281,0x342),(0x37A,0x4D5),(0x77F,0x851),
        (0x979,0xA95),(0xAA8,0xABF),(0xBDD,0xC02),(0x198D,0x19F3)]:
        write(out/'evidence'/f'P{lo:04X}-P{hi:04X}.asm',
            '\n'.join(f"P:{pc:06X} {v['raw']} {v['instruction']}" for pc,v in r.items() if lo<=pc<hi)+'\n')
    table(out,'selected-slot-state-map.csv',m);table(out,'takeover-candidate-words.csv',c)
    table(out,'modification-sites.csv',mods);table(out,'register-liveness.csv',live)
    criteria=[
        ('stock edit count','5 identified origins/4 windows plus unclosed sets','3 anchors, not a finite rewrite; at least8 dependency classes','A known anchors; total both unknown'),
        ('global/local behavior','global DMA/control/service restriction','local intent; foreign/service/DMA and P-code protection survive','B locality advantage conditional'),
        ('memory ownership','explicit P7 plus extra P objects unqualified','0 qualified reclaimed words;84 candidates examined','A clearer layout, neither owned'),
        ('writer exclusion','complete mediation unclosed','bypassed selected producer is not foreign-writer exclusion','no demonstrated B scope collapse'),
        ('register preservation','bounded union26, exact minimum unproved','same26 at retained9D9; earlier boundary unqualified','tie at comparable boundary'),
        ('code growth','866 partial /1626 target; complete null','740 comparable-boundary constituent subtotal plus unknown bypass/protection','B smaller subtotal is not proven complete cost'),
        ('cycles','P-state +global guards; partial costs','X-state cheaper but retained/removed work and guards unknown','B numerical advantage conditional'),
        ('initialization','trusted DMA quiescence and exact once-only seed','activation/reset producer collisions; exact transition unproved','B reset is not automatically simpler'),
        ('failure modes','missed guard can corrupt state/code/global config','bad bypass can corrupt queues/post or other paths as well as selected audio','local B containment not demonstrated'),
        ('recoverability','normal external rollback unqualified','same normal external rollback unqualified','tie; no board/debug option'),
        ('preserve bank1/unrelated','stock arithmetic retained; policy/timing risks','shared routines require selected guards and original fallback','A original data path better specified'),
        ('auditability','known policy obligation ledger and retained stock tail','unknown seven-word subset and auxiliary slice contract','A currently more auditable'),
        ('offline fixture','bounded standalone renderer yes, protected patch no','renderer yes, full local takeover fixture no','neither patch finite now'),
        ('later polyphony','larger protected per-voice P objects/relocation/cost','per-slot contexts could scale after full takeover proof','neither demonstrated dead end'),
        ('final controls','calibrated note conversion/controls/gain unqualified','same plus retained-subgenerator control compatibility','no controls promise')]
    table(out,'comparison-criteria.csv',[dict(criterion=k,A=a,B=b,assessment=s) for k,a,b,s in criteria])
    aux=[
        ('mono','9C8..9D8','all three YA01+lane+3*k and six ramp coefficients','overwrite only X[2C46,2C66)','B must keep or explicitly replace selected third-lane contribution'),
        ('aux0','9C8/9CA','lane0*c0, pre-add A storedX2C02','retain original lane0 sample generation','cannot derive it from final mono alone'),
        ('aux1','9C9/9CD','lane0*c0 +lane1*c1 storedX2C24','retain original lanes0/1','zeroing/duplicating mono is not equivalent'),
        ('guard','7EF/7F1..7F2','pre-add phase track at sample16 of latest applicable lane/repeat','retain natural phase producer and leave2C66 unchanged','combiner has no independent guard store'),
        ('ramps','470..47C/9A5..9B8','six currentX and six deltaY words;post cursors','retain all six in comparable A/B','cannot treat tail as surrendered'),
        ('post','9D9/9DD..A94','X5AB..5BE/Y5AB..5C6 and gain/envelope','leave original post/allocator state','full selected object cannot be reclaimed')]
    table(out,'auxiliary-dependencies.csv',[dict(output=k,producer=p,dependency=d,A_action=a,B_obligation=b,
        classification='VERIFIED data flow; B replacement UNRESOLVED') for k,p,d,a,b in aux])
    dump(out,'last-lane-thinning.json',dict(status='CONDITIONAL scoped alternative, not a takeover certificate',
        lane2_Q=0x597,phase_guard_slice_fields=list(range(2,10)),
        phase_guard_slice_evidence='7C8 repeat;7D0..7D2 branch/flags/coefficient;7DE..7E9 phase/base/correction/increment',
        six_possible_record_fields=[0,1,10,11,12,13],
        six_possible_addresses=[0x597,0x598,0x5A1,0x5A2,0x5A3,0x5A4],
        additional_kernel_words='No free claim:3C2 dynamic coefficient writes at19F0+4*lane and97B current-coefficient read;source1A80; global/other-slot extent unclosed',
        original_first_two_lanes_required_for_exact_aux=True,
        alternative_new_aux_from_Plaits='Could be a redesigned selected auxiliary contract, but not exact original auxiliary values; no validated producer/post/guard proof',
        maximum_reclaimable_words_proved=False,seven_reclaimable_words_proved=False,
        phase_only_variant_implemented=False))
    req=[('entry','384/19E6','request R0Q/R4S and completion reload Q/S','preserve two distinct entries'),
        ('pass/bitmap','1998..1999/791..799/19BF','bit23 pass and pending-context bits','no forced request omission without scheduling rewrite'),
        ('lookup','806..81B/832..84B','record phase/mask/coefficient ->shared queue ->lane samples','lanes0/1 aux require their results'),
        ('worker','channel1 120/125/126','address in queue replaced with fetched word','queue cursor/publication and counts must match'),
        ('phase commit','7F5/7F7/7F9,alternate8D2/913','selected request skips commit;completion writes, other classes differ','cannot initialize/reclaim every pass'),
        ('lane progression','979..99D','R4 phase pair, R0 record step, R7 lane cursor, hardwareDO state','skipping body needs exact equivalent cursor/loop tail'),
        ('exit','99E..9A4','request1BE8 publication/return;completion entersramps','same return obligation, not direct9D9 on request'),
        ('continuation','9B8/9D9','Y7=Q+30 and R4=S+C','selected mono must not change these cursors')]
    table(out,'request-completion-dependencies.csv',[dict(stage=k,PC=p,dependency=d,B_obligation=b,
        status='VERIFIED original path; B rewrite UNRESOLVED') for k,p,d,b in req])
    service=[]
    for arch in ['A','B']:
        for path in ['SHI scalar/cached/paged','P204B RMW','DMA/foreign','note reset/activation','reload/diagnostic']:
            service.append(dict(architecture=arch,path=path,
                scope='P object/code admission plus actual control commits' if arch=='A' else 'actual selected X7 commits/read-RMW plus safe appended code/workspace',
                tolerable='NO arbitrary post-init numeric state writes',
                reason='phase/next/pw/frequency retained across blocks; overwrite-before-use/reset changes continuity',
                reduction='Direct numeric X7 check is narrower, but complete foreign domains not proved absent' if arch=='B' else 'Fixed-map X/Y data stores do not directly alias privateP',
                classification='CONDITIONAL design / coverage UNRESOLVED'))
    table(out,'service-impact.csv',service)
    saves=[dict(architecture=a,boundary='after retained combiner ->9D9',registers=';'.join(save_registers()),
        saved_words=26,storage='protected appended P26 proposed; ownership unqualified',P_words=104,nominal_cycles=364,
        minimum_all_mode_save_words=None,earlier_boundary='not selected' if a=='A' else 'UNRESOLVED, cannot import deadness',
        verdict='same conservative bound; no qualified B reduction') for a in ['A','B']]
    table(out,'save-frame-comparison.csv',saves)
    sz=obj(PRE+'/code-size.json')
    sizes=[('A','renderer',549),('A','save26',104),('A','controls+dispatcher+combiner+return',59),
        ('A','204B+SHI+init partial',154),('A','known partial subtotal',866),('A','planning subtotal',1626),
        ('A','proposed data',102),('B','renderer highX',549),('B','save26 same-boundary P',104),
        ('B','controls+dispatcher+combiner+return',59),('B','longX init7',28),
        ('B','comparable-boundary constituent subtotal',740),('B','minimum explicit data X7+P32',39)]
    table(out,'code-size-comparison.csv',[dict(architecture=a,component=k,P_words=v,
        total_complete_P=None,conditional_code_capacity=sz['conditional_code_budget'] if a=='A' else 'depends on workspace/policy layout',
        unknown_glue='actual-EA/CFI/trust/reply/converter' if a=='A' else 'producer/consumer/phase-only/aux/request/reset/service/DMA/code-workspace ownership',
        status='CALCULATED constituent/template, not assembled or total bound') for a,k,v in sizes])
    cy=[]
    q=obj('builds/phase20c-pstate/final-v4/qualification.json')
    for a,key in [('A','high-P'),('B','high-X')]:
        b=q['cycles'][key]
        cy.append(dict(architecture=a,component='sealed renderer (state handling included)',mean=b['model_cycles_mean'],max_style=b['model_cycles_max'],
            conditional_upper=15343 if a=='B' else 28708,scope='existing model; upper column is loose renderer relaxation only',classification='MEASURED traces / CALCULATED cycles'))
        premium=q['P_vs_high_X_cycles']
        per_transfer=7 if a=='A' else 2
        cy.append(dict(architecture=a,component='state handling nominal (ALREADY included in renderer)',
            mean=per_transfer*premium['mean']/5,max_style=per_transfer*premium['max']/5,conditional_upper=None,
            scope='Existing trace transfer counts derived from five-cycle P-vs-X premium; do not add twice; interlocks separate',classification='CALCULATED from MEASURED counts'))
        for component,n in [('P26 save/restore',364),('selected dispatcher',24),('fixed controls plus return',28)]:
            cy.append(dict(architecture=a,component=component,mean=n,max_style=n,conditional_upper=None,
                scope='same-boundary unassembled nominal template; ABI/IRQ/interlocks not certified',classification='CALCULATED CONDITIONAL'))
        cy.append(dict(architecture=a,component='guard/enforcement',mean=None,max_style=None,conditional_upper=None,
            scope='A: helperentry4,fast21/record,SHI4..60+validator; B: exactX7+foreign/DMA/Pworkspace protection cost unqualified',classification='UNRESOLVED total event counts'))
        cy.append(dict(architecture=a,component='retained/removed stock work',mean=None,max_style=None,conditional_upper=None,
            scope='A retains full original generator,combiner562; stock_work_removed=0' if a=='A' else 'B proposed aux/guard slice extent unqualified; subtract only subsequently proved removed work, no fabricated saving',classification='VERIFIED A retention / UNRESOLVED B extent'))
        cy.append(dict(architecture=a,component='hypothetical P temporary conversion +same wrapper',
            mean=cost[a]['partial_wrapper_mean'],max_style=cost[a]['partial_wrapper_max'],
            conditional_upper=28708+416 if a=='A' else 15343+5*18*33+416,
            scope='conversion unexecuted; includes save364+dispatcher24+controls25+return3; guards/converter/stock omitted',classification='CALCULATED CONDITIONAL partial'))
        cy.append(dict(architecture=a,component='whole one-voice additional/total cost',mean=None,max_style=None,conditional_upper=None,
            scope='A addsQ*(4+21Nfast+(19+U)Nslow)+allguards; B retained/removed generator work and allbypass/guard counts unclosed',classification='UNRESOLVED'))
    table(out,'cycle-comparison.csv',cy)
    risks=[]
    for feature in ['bank1 (UI Synth2 HYPOTHESIS)','other bank0 voices','MIDI1/MIDI2','drums','FX','project/pack','service','firmware update']:
        for a in ['A','B']:
            risks.append(dict(architecture=a,feature=feature,
                impact='global policy/latency can deny unrelated config, arithmetic retained' if a=='A' else 'local selected intent; shared loops/queue/service/code/DMA remain potential global failures',
                relative_rank='HIGH global-policy surface' if a=='A' else 'LOWER intent, UNRESOLVED actual isolation',
                classification='HYPOTHESIS risk ranking / UNRESOLVED whole runtime',
                recovery='normal external only, unopened device; no recovery certificate'))
    table(out,'global-risk.csv',risks)
    fail=[('A','missed writer guard','state corruption; DMA/code overwrite can affect wholeDSP','no proved containment'),
        ('A','startup trust failure','guard code corrupted before admission','refuse activation, trust certificate required'),
        ('B','missed selected producer/read','numeric phase fields interpreted as stock pointers/counts','can escape selected path through huge loops/queue/cursors'),
        ('B','wrong selected discriminator','shared routines suppress bank1/other slots','not inherently local'),
        ('B','aux/guard omission','post values/CCR/memory contract corrupted','selected audio likely first symptom, global exception/deadline unbounded'),
        ('B','service overwrites retainedstate','continuity/state corruption or invalid arithmetic inputs','local guard still required')]
    table(out,'failure-containment.csv',[dict(architecture=a,failure=f,consequence=c,containment=s,
        classification='HYPOTHESIS consequence / no observed fault',hardware_or_debug_dependency=False) for a,f,c,s in fail])
    finite=dict(A=False,B=False)
    dump(out,'offline-testability.json',dict(status='CONDITIONAL plan; no patch or emulator execution',
        finite_patch_candidate=finite,authentic_full_boot_required=False,
        finite_definition='All required edits at known addresses with known complete branch/continuation semantics; not merely hooks known',
        A='Original body/combiner/post and renderer are bounded fixtures; missing writer/control adapters preclude protected patched fixture',
        B='No seven-word subset plus producer/consumer/aux/guard/request/reset contract qualified;3 anchors do not form finite patch',
        allowed_harness='Explicit constrained memory/register/IRQ/DMA profile, not claimed authentic stock checkpoint; poisoned objects and forbidden writes; no unit access',
        future_tests=['instruction windows and fallback bytes','exact samples/state versus sealed oracle','aux/guard/post boundary comparison',
            'two passes/cursors/bitmap/worker counts','negative writer/control tests','save/IRQ/stack boundaries','continuity/reload/error and timing'],
        no_fixture_constructed=True))
    dump(out,'scalability.json',dict(status='CONDITIONAL, no promise or implementation',
        A='More typed P state objects/ownership, per-voice addressing and budgets needed; no inherent mathematical dead end shown',
        B='Per-slot contexts could be reclaimed only with proved per-slot producer/consumer/aux and service rules; fixed one-voice addresses do not scale automatically',
        synth1_synth2='UI mapping remains HYPOTHESIS;2 independent mono paths require separate state and admitted timing',
        MIDI1_MIDI2_three_voices='No stock internal synth hosting/routing proven for MIDI tracks; six additional render paths not implied by12 existing contexts',
        controls='pitch calibration/gain and PW/shape control mapping unqualified in both; preserved bank/event flow is useful, not finished ABI',
        polyphony_implemented=False,VariableSaw_math_changed=False,dead_end_proved=False))
    decision=dict(result='SELECT-A',readiness='PARTIAL design; protected offline patch construction NOT justified',
        preference_status='CONDITIONAL architecture ranking, not proof of fastest elapsed implementation',
        reason='A preserves verified full lookup/aux/guard/post contract. B has zero qualified seven-word subsets and no bounded replacement for required auxiliary/guard work; locality/cost advantage remains hypothetical.',
        A_known_origin_instruction_addresses=5,A_known_origin_windows=4,A_profile_review_unchanged_sites=10,
        B_known_anchors=3,B_finite_producer_consumer_patches=0,site_totals_complete=False,
        generator_candidate_words=len(c),qualified_reclaimed_words=0,thin_last_lane_possible_words=6,
        six_word_caveat='Conditional common-path thinning, not an ownership certificate or exhaustive impossibility proof;kernel/other fields andalternate modes stayunresolved',
        aux_first_two_lanes_required=True,guard_producer_independent_of_combiner=True,
        register_bound_both=26,qualified_save_reduction_B=0,
        runtime_policy_global_impact_minimized=False,service_scope_reduction_B_proved=False,
        no_new_universal_writer_audit=True,ownership_certificate=False,
        offline_patch_now=False,flashing_now=False,
        biggest_blocker='Finite actual-EA/commit and control boundaries; existing344 candidate obligations unresolved. Authentic boot is NOT required for an explicit constrained offline fixture; runtime pre-quiescence trust remains a separate gate.',
        exact_next_phase='20C7-A-COVERAGE: certify only required A control-store/actual-EA exemptions/adapters and typed P/control boundaries, with exact origins/continuations/costs; no new memory census or patched fixture until finite.',
        post_selection_phase_started=False,unopened_device_policy=True,
        future_external_interfaces_only=['USB-C','normal MIDI','normal microSD/pack mechanisms where applicable'],
        hardware_actions=0,DSP_execution=0,original_modified=False)
    dump(out,'decision.json',decision)
    dump(out,'validation.json',dict(status='VERIFIED bytes/reused ledgers / CALCULATED planning',
        original_rows_byte_checked=len(r),selected_map_words=len(m),candidate_words=len(c),
        explicit_register_liveness_rows=len(live),liveness_scope='same natural9D9 boundary, foreground witnesses plus IRQ/caller residual; no claimed minimal whole-runtime save set',
        required_reports=REQUIRED,old_trace_blocks_read=7520,trace_rerun=False,numeric_suite_rerun=False,
        universal_writer_census_rerun=False,complete_patch_sites=False,complete_ownership=False,
        source_sha256=sha(Path(__file__)),guards=len(g),immutable_runtime_bytes_modified=False,
        no_image_or_packets_emitted=True,stock_or_new_DSP_execution=0))
    for n,h in g.items():assert sha(ROOT/n)==h,n
    dump(out,'hashes.json',{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    print(json.dumps(dict(result='SELECT-A',map_words=len(m),candidates=len(c),guards=len(g),cost_projections=cost,patch_justified=False),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);build(p.parse_args().output_dir)
