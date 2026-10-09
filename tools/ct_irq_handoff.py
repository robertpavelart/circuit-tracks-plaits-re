"""Offline, fail-closed interrupt handoff audit. No CPU or device execution.
Fresh output paths only. Conditional architectural classes are not ROM traces.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'emulator/harness'))
from partial_state import Partial, interrupt_eligibility
from symbolic_startup import Startup
from ct_stock_load_audit import verify_inputs, rows

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(out, name, value):
    data = value if isinstance(value, bytes) else (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    with (out / name).open('xb') as f:
        f.write(data)

def source(name, pending, enable, priority, reset, pages, boot):
    return dict(name=name, pending=pending, enable=enable, priority=priority,
                hardware_reset=reset, device_pdf_pages=pages, ROM_relevance=boot,
                application_handoff='UNRESOLVED: reset preservation/ROM writes and pipeline not established')

def sources():
    return [
        source('SHI / SHI_1: six request types', 'X:FFFF91 HCSR: HTDE15, HTUE14, HRNE17, HRFF19, HROE20, HBER21',
               'HCSR HTIE11, HRIE13:12 (00 disabled,01 nonempty,10 reserved,11 full), HBIE10; HEN0 controls individual reset',
               'IPRP bits3:2 SHL', 'Interrupt enables=0; HTDE=1; HTUE/HRNE/HRFF/HROE/HBER=0', [202,203,212,213,214,215],
               'DIRECT: boot consumes HRX. Final FIFO read is not proof of FIFO-empty/error/enable/mask cleanup'),
        source('ICC receive maskable', 'Y:FFFFD3 ICCR4.MIF1 reflects peer ICCR3', 'Peer Y:FFFFD6 ICCR3.MIE0',
               'IPRP bits19:18 ICIL', 'ICCR3/4=0, ICDR3/4=0', [251,256,257,258,260],
               'Worker original P109 writes ICDR3 later in ARM upload order; exact core interleaving/ROM peer behavior unknown'),
        source('ICC acknowledgement maskable', 'Y:FFFFD5 ICAR3.ACK0 (clear via RACK1)',
               'No separate ACK enable specified in reviewed ICAR3; PIC gates source', 'IPRP bits21:20 ICAL',
               'ICAR3/4=0 (table13-1 authoritative; figure13-9 reset drawing inconsistent)', [251,256,257,260],
               'Requires prior publication/read; reset is not handoff provenance'),
        source('ICC nonmaskable', 'Y:FFFFD8 ICCR2.IF1 reflects peer ICCR1.IF1',
               'Peer ICDR1 write when DRE2=1; no MIE/SR mask', 'Fixed IPL3, VBA+28',
               'ICCR1/2=4 (DRE1,IF0); ICDR1/2=0', [251,254,255,261], 'Peer ROM ICDR1 writes not recovered'),
        source('ESAI / ESAI_2', 'X:FFFFB3 SAISR RDF/REDF/ROE/TDE/TEDE/TUE and last-slot events',
               'X:FFFFB7 RCR REIE20,REDIE21,RIE22,RLIE23; X:FFFFB5 TCR TEIE20,TEDIE21,TIE22,TLIE23',
               'IPRP bits1:0 ESL', 'Listed enables/status cleared by reset; no post-ROM guarantee', [158,172,181,182,190,191],
               'Not required by SHI boot description; absence of ROM configuration not proved'),
        source('ESAI_1 / ESAI_3', 'Y:FFFF93 SAISR; same eight event types',
               'Y:FFFF97 RCR, Y:FFFF95 TCR; same interrupt-enable fields', 'IPRP bits11:10 ESL1/ESL3',
               'Same documented ESAI reset semantics', [89,167,175,190,191], 'Shared audio inputs/ROM initialization unbounded'),
        source('DMA channels0..7', 'Core pending latch on block completion; X:FFFFF4 DSTR DTD0..7 are completion status, not assumed identical pending latch',
               'DCRn.DIE22; DE23 and transfer mode govern operation. DCR0..7 X:FFFFEC,E8,E4,E0,DC,D8,D4,D0',
               'IPRC bits12+2n for n0..5; IPRC1 bits0/2 for n6/7',
               'DCR bits cleared (family manual); device adds channels6/7', [80,115],
               'SHI may be read by DMA in architecture; matching ROM implementation unknown'),
        source('TEC / TEC_1 timers0..2', 'X:FFFF8F/8B/87 TCSRn TCF21,TOF20', 'TCSR TCIE2,TOIE1,TE0',
               'IPRP bits9:8 TAL', 'TCSR=0', [238,239,240], 'No timer requirement in SHI boot; ROM use unproved'),
        source('External IRQA/B/C/D (GPIO alternate functions)', 'Synchronized internal pending latch / external level; no readable X/Y flag documented',
               'IPRC IxL1:0 !=00; IxL2 selects level/negative-edge; GPIO mux additionally relevant',
               'IPRC bitfields [2:0],[5:3],[8:6],[11:9]', 'IPRC=0, detection latch held reset while disabled', [105,106,112],
               'Board levels and ROM mux/priority writes unresolved; GPIO data is not an independent PIC source'),
        source('External NMI', 'Latched falling edge on NMI', 'Nonmaskable', 'Fixed IPL3 VBA+0A',
               'Reset does not prove later edge absence', [108,111], 'Board signal history unavailable; never sampled'),
        source('S/PDIF', 'X:FFFF64 SIS/SIC event bits', 'X:FFFF63 SIE matching enables',
               'IPRP SPRL13:12 (Rx),SPTL15:14 (Tx)', 'SIE=0; SIS=2, not all status bits reset0', [114,287],
               'Shared peripheral; no boot exclusion guarantee'),
        source('ASRC', 'Y:FFFC08 ASRSTR + documented data-input/output and FP events',
               'Y:FFFC01 ASRIER bits0..7; Y:FFFC02 ASRIEM routes core', 'IPRP ASL17:16',
               'ASRIER=0,ASRIEM=0', [315,316,324], 'Shared peripheral; no boot exclusion guarantee'),
        source('EMC/ICC access error', 'Y:FFFFC8 source discriminator; ICC EF2; EMC X:FFFE59 TESR',
               'ICC EIE3 and EMC X:FFFE5D TEIR / X:FFFE5B TEDR controls', 'IPRP LIEL23:22',
               'ICC EF/EIE=0; EMC exact reset fields retained in manual, not generalized to0', [262,263,391,392,393],
               'Wrong/simultaneous ICC access or EMC fault; ROM use unresolved'),
        source('Always-on maskable', 'Constant request (no pending flag register)', 'IPRP1 bits23:22 !=00',
               'IPRP1 STIL23:22', 'Priority-register reset clear; no ROM preservation proof', [107,108,115],
               'No external event needed if enabled; defeats empty-event-queue argument'),
        source('DMA stall nonmaskable', 'Internal contention counter exceeds DMAS threshold; level remains until contention ends/DMAS=0',
               'X:FFFFF8 DMAS nonzero; active DMA contention required', 'Fixed IPL3 VBA+0E', 'DMAS=0', [118,120,121],
               'ROM DMA configuration/threshold unknown'),
        source('Core stack error, illegal instruction, TRAP/TRAPcc, debug request',
               'Core internal exception state; no generic readable peripheral flag', 'Exception-specific trigger, fixed IPL3',
               'VBA+02/04/08/06 respectively', 'Hardware reset initializes control but does not establish post-ROM exceptions', [108,111],
               'No original app illegal/TRAP event yet; prior ROM exception/pipeline and debug-request absence not established'),
        source('Reset / watchdog reset', 'RESET input or watchdog expiry; changes boot flow rather than ordinary handler prefix',
               'WCR.WEN0 at Y:FFFFC0; reset input external', 'Reset processing; boot-mode selected entry',
               'WCR text says F, figure says allzeros: conflicting primary documentation', [245,246,247],
               'Separate restart class, not an invented maskable timer IRQ'),
    ]

def vectors():
    v={2:'Stack error',4:'Illegal instruction',6:'Debug request',8:'TRAP',10:'External NMI',14:'DMA stall'}
    v.update({16+2*i:f'IRQ{chr(65+i)}' for i in range(4)})
    v.update({24+2*i:f'DMA{i}' for i in range(8)})
    v.update({40:'ICC NMI',42:'ICC maskable',44:'ICC ACK'})
    es=['Rx data','Rx even','Rx exception','Rx last','Tx data','Tx even','Tx exception','Tx last']
    v.update({48+2*i:'ESAI/2 '+n for i,n in enumerate(es)})
    v.update({112+2*i:'ESAI1/3 '+n for i,n in enumerate(es)})
    v.update({64:'SHI transmit',66:'SHI underrun',68:'SHI nonempty',72:'SHI full',74:'SHI overrun',76:'SHI bus error'})
    for i in range(3):v[84+4*i]=f'Timer{i} compare';v[86+4*i]=f'Timer{i} overflow'
    sp=['Rx C new','Rx validity','Rx illegal','Rx parity','Rx U full','Rx U over','Rx Q full','Rx Q over','Rx UQ sync','Rx UQ frame','Rx over/under','Rx resync','Lock loss','Rx FIFO full','Lock interrupt','Tx under/over','Tx resync']
    v.update({128+2*i:'SPDIF '+n for i,n in enumerate(sp)});v[170]='SPDIF Tx FIFO empty'
    v.update({176+2*i:'ASRC '+n for i,n in enumerate(['Input A','Input B','Input C','Output A','Output B','Output C','Overload','FP wait'])})
    v[252]='Always-on';v[254]='EMC/ICC error'
    return v

def run(out):
    out=out.resolve()
    if out.exists() or not out.is_relative_to((ROOT/'builds/phase19b-irq').resolve()):
        raise ValueError('Fresh phase19b-irq output directory required')
    main,_=verify_inputs(); dsp=ROOT/'firmware/dsp/build-4486'
    manifest=json.loads((dsp/'manifest.json').read_text()); identities={}
    for block in manifest['blocks']:
        for key,hashkey in [('stream_file','stream_sha256'),('payload_file','payload_sha256')]:
            identities[block[key]]=sha((dsp/block[key]).read_bytes())
            assert identities[block[key]]==block[hashkey]
    out.mkdir(parents=True)
    docs={}
    page_sets={'DSP56724RM.pdf':[78,79,80,81,82,83,84,88,89,103,104,105,106,107,108,109,110,111,112,113,114,115,118,120,121,167,175,181,182,190,191,202,203,204,211,212,213,214,215,225,226,238,239,240,245,246,247,251,254,255,256,257,258,260,261,262,263,287,315,316,324,391,392,393],
               'DSP56300FM.pdf':[35,36,37,38,39,40,41,42,43,44,45,95,101,195,196]}
    page_sets['DSP56724RM.pdf']=sorted(set(page_sets['DSP56724RM.pdf']+[158,172]))
    expected_docs={'DSP56724RM.pdf':'3b9876887ca7ecfec99d6e331ce1587e13955d0ecb4d0e8643dafd1df689370f',
                   'DSP56300FM.pdf':'b2e8e346fe55b05d20ad0e6bc03d45fd1e080d46d9a9cd9540271c0c37f5a31e'}
    for name,pages in page_sets.items():
        path=ROOT/'builds/phase19b/documentation'/name
        assert sha(path.read_bytes())==expected_docs[name], 'Primary document identity mismatch'
        reader=PdfReader(path)
        text='\n'.join(f'=== PDF PAGE {n} ===\n'+reader.pages[n-1].extract_text() for n in pages)
        save(out,name+'.witnesses.txt',text.encode())
        docs[name]=dict(sha256=sha(path.read_bytes()),pdf_pages=pages)
    save(out,'documents.json',docs);save(out,'interrupt-sources.json',sources())
    vector_map=[]; listings={}
    for role in ['main','worker']:
        channel=0 if role=='main' else 1
        payload=(dsp/f'selection0-channel{channel}.payload24.bin').read_bytes()
        listing=rows(ROOT/f'builds/phase3-selection0-channel{channel}.asm',payload);listings[role]=listing
        for offset,name in sorted(vectors().items()):
            words=payload[offset*3:(offset+2)*3]
            vector_map.append(dict(role=role,source=name,offset=offset,raw=words.hex(),
                IPL='3' if offset in [2,4,6,8,10,14,40] else '0..2',
                qualification='VERIFIED bytes; DOCUMENTED vector offset; conditional on actual VBA=0 and mapped P',
                first_fetch='P:(VBA | 0x%02X)'%offset,
                local_effect='Two fast NOP words; core pending acknowledgement is not peripheral flag clear' if words==bytes(6) else
                'Long JSR1B4' if role=='main' and offset==62 else 'Long JSR156' if role=='main' and offset==68 else 'UNRESOLVED'))
    assert all(v['raw']=='000000000000' for v in vector_map if v['role']=='worker')
    assert [v['offset'] for v in vector_map if v['role']=='main' and v['raw']!='000000000000']==[62,68]
    save(out,'conditional-vectors.json',vector_map)
    witnesses={}
    for role,lo,hi,label in [('main',0x156,0x1b3,'SHI-handler'),('main',0x1b4,0x1d8,'ESAI-handler'),('main',0x100,0x10f,'main-prefix'),('worker',0x100,0x10d,'worker-prefix'),('main',0x25db,0x25f2,'later-init')]:
        witnesses[label]=[r for pc,r in listings[role].items() if lo<=pc<=hi]
    save(out,'instruction-witnesses.json',witnesses)
    save(out,'handler-effects.json',dict(
        qualification='VERIFIED original bytes/static data flow; exact live handler selection UNRESOLVED; no handler executed',
        SHI=dict(vector='VBA+44; P44 only if VBA0',target='P156',
            effects=['P156/158/15A save X0/R0/M0 into Y2000..2002 before application init',
                     'P15C M0=FFFF; P15E reads HRX to X0; FIFO occupancy changes, overrun-clear requires preceding HCSR read',
                     'P15F branches on GPIO PDRC8; P198 loads R0 from X10; P199 selects X/Y via X11.bit15',
                     'P19B/19D writes HRX word to Y/X:(R0)+; P19E writes updated R0 to X10',
                     'Other branches write X10/X11/X12 and GPIO PDRC9, send HTX; A save/restore Y2003..2005',
                     'P1AD..1B1 restore X0/R0/M0; P1B3 RTI requires valid stacked PC/SR'],
            dependencies=['VBA','interrupt-entry stack/modes','incoming X0/R0/M0','HRX/FIFO','GPIO8','X10/X11','mapping'],
            convergence='Not proved: persistent RAM and peripheral side effects occur; unknown pointer can select material destination'),
        ESAI=dict(vector='VBA+3E; P3E only if VBA0',target='P1B4',
            effects=['P1B4/1B5/1B9 manipulate SSH/SSL for R0/M0/N0 saves',
                     'P1BA/1BB writes Y0/Y1 to Y:(R0) using Y1A-derived modifier',
                     'P1BC/1BE writes DMA DDR0=XFFFFEE and DSR1=XFFFFEB',
                     'P1C1 M0=3FF; P1C3 loads YFFE cursor; P1C7..1CA writes Y/reads X with increment',
                     'P1CB..1CD updates Y21/Y22/YFFE; P1CF..1D6 restores state; P1D8 RTI'],
            convergence='Not proved; requires initialized Y1A/YFFE/ring/stack and alters RAM/DMA'),
        NOP_pairs=dict(effects='Two fast NOP words; no explicit register/RAM stores; core pending clear on second vector fetch',
                       convergence='Conditional one-shot may resume interrupted PC; persistent peripheral level/always-on request can recur; timing and next arbitration unproved')))
    classes=[
        dict(name='No admitted request / pending requests disabled or masked',first='Normal stream nominal PC0; pipeline/loop guard still needed',condition='All maskable sources disabled/masked/inactive AND no IPL3 request AND no already fetched ISR'),
        dict(name='SHI nonempty admitted',first='Vector VBA+44 -> JSR156 only if VBA0',condition='HRIE01,HRNE1,HROE0, SHL!=00, decoded IPL>=SR.I; no higher source; admission timing established'),
        dict(name='SHI other admitted',first='VBA+40/42/48/4A/4C',condition='Documented HCSR event/enable and SHL/SR.I predicate, highest admitted source'),
        dict(name='ICC maskable/ACK admitted',first='VBA+2A/2C',condition='Peer MIF/MIE or ACK plus PIC ICIL/ICAL enabled and IPL>=SR.I'),
        dict(name='Other maskable admitted',first='Documented source vector, including always-on VBA+FC',condition='Source-specific enable/event and PIC field enabled, IPL>=SR.I'),
        dict(name='IPL3 admitted',first='VBA+02/04/06/08/0A/0E/28',condition='Actual exception/NMI/stall/peer write trigger; ordinary SR.I does not exclude'),
        dict(name='Reset/restart',first='Boot mode reset vector; not application prefix',condition='Actual reset/watchdog event; outside controlled application handoff assumption'),
    ]
    for c in classes:
        c['status']='SYMBOLIC conditional architectural class, NOT a verified reachable ROM-exit state'
        c['actual_feasibility']='UNRESOLVED; exact legitimate stock class set cannot be recovered from present contract'
    save(out,'conditional-classes.json',classes)
    # Tiny control-field tests, not full-register brute force and not CPU forks.
    truth=[]
    for field in range(4):
        for mask in range(4):
            admitted=field!=0 and field-1>=mask
            if field:
                p=Partial.concrete(1,'synthetic pending',1);l=Partial.concrete(field-1,'PIC field decode',2);m=Partial.concrete(mask,'synthetic SR.I',2)
                assert interrupt_eligibility(p,l,m).require('fixture')==int(admitted)
            truth.append(dict(PIC_field=field,enabled=bool(field),IPL=None if field==0 else field-1,SR_I=mask,admitted=admitted))
    assert not any(r['admitted'] for r in truth if r['PIC_field']==0 or r['SR_I']==3)
    save(out,'pic-sr-truth-table.json',truth)
    save(out,'tests.json',dict(status='TESTED PASS',PIC_SR_combinations=16,
         image_vector_checks='Both byte-checked tables; all worker entries NOP/NOP; only main3E/44 nonzero',
         scope='Static contracts and symbolic field predicates, no authentic CPU interrupt delivery tested'))
    save(out,'pic-sr-contract.json',dict(
         registers={'IPRC':'X:FFFFFF','IPRP':'X:FFFFFE','IPRC1':'X:FFFFFB','IPRP1':'X:FFFFFA'},
         reset='DOCUMENTED architecture priority registers clear; device extends PIC with C1/P1 (extension interpretation, no separate reviewed reset table)',
         fields={'SHL':'IPRP3:2','ICC':'IPRP19:18','ICC_ACK':'IPRP21:20','Always_on':'IPRP1 23:22'},
         PIC_domain='Each defined two-bit maskable priority field00 disabled,01 IPL0,10 IPL1,11 IPL2; handoff field value UNKNOWN',
         SR_I='SR bits9:8: hardware reset11; actual post-ROM domain00/01/10/11 unresolved',
         bootstrap='No SR.I/PIC/VBA write in eight original shim words; second ROM intervenes, not a reset',
         application='Main109 ORI03,MR masks ordinary IPL0..2 after readiness; main25EF writes IPRP9 (ESAI IPL0,SHI IPL1),25F1 clears SR.I; no reviewed direct IPRC/C1/P1/VBA writes',
         pipeline='FM2.3.2.4/.6/.7/.9: fetched ISR is not cancelled by later disable; SR mask changes need timing. Instantaneous predicate alone is insufficient',
         SHI_exit='Mode0 specifies count/load/entry only; no reviewed exit cleanup/enable/PIC/SR guarantee',
         ICC_order='ARM uploads shim,main,worker; source order is not cross-core clock schedule. Known worker publication cannot precede its own load, but exclusion at main execution boundary unproved',
         VBA='Hardware reset0; actual post-ROM upper16 bits unknown; low8 always0; no exact handler address without provenance'))
    traces={}
    for role in ['main','worker']:
        data=main if role=='main' else (dsp/'selection0-channel1.payload24.bin').read_bytes()
        cpu=Startup(role,data); result=cpu.run(16)
        assert cpu.count==0 and cpu.transaction_log==[]
        traces[role]=dict(result=result,trace=cpu.trace,transactions=cpu.transaction_log)
    save(out,'blocked-original-attempts.json',traces)
    save(out,'gate.json',dict(A='NOT-YET-DETERMINED',B='NO',C='NO',D='NOT-YET-DETERMINED',E='NOT-YET-DETERMINED',F='NOT-YET-DETERMINED',G='NOT-YET-DETERMINED',
        interrupt_contract='UNRESOLVED',execution_authorized_by_gate=False,original_main_instructions=0,original_worker_instructions=0,
        loop_analysis='Deferred as requested; interrupt/pipeline boundary not resolved',
        convergence='Not proved; conditional main SHI/ESAI handlers materially write RAM; NOP vectors do not clear persistent peripheral levels',
        first_blocker='Unknown effective admitted request/pipeline at final ROM branch; SR.I/PIC/peripheral masks/pending and VBA lack exit provenance',
        best_next_step='Obtain a matching authoritative final SHI ROM exit fragment/contract covering effective interrupt arbitration, pending/fetched state and VBA; preserve reset versus second-entry distinction'))
    save(out,'input-integrity.json',identities);verify_inputs()
    save(out,'source-manifest.json',{str(p.relative_to(ROOT)).replace('\\','/'):sha(p.read_bytes()) for p in [Path(__file__),ROOT/'emulator/harness/partial_state.py',ROOT/'emulator/harness/symbolic_startup.py']})
    save(out,'hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
    print('Static IRQ audit PASS; original main=0 worker=0; exclusion/convergence UNRESOLVED')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir',required=True,type=Path)
    run(ap.parse_args().output_dir)
