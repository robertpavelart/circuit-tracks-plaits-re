"""Phase19B-ROM: reproducible document comparison and honest unresolved exit state.
Does not reconstruct guessed ROM instructions or execute any DSP image.
"""
import argparse,hashlib,json
from pathlib import Path
from pypdf import PdfReader
from ct_stock_load_audit import verify_inputs,rows
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def save(out,name,obj):
    b=obj if isinstance(obj,bytes) else (json.dumps(obj,indent=2,sort_keys=True)+'\n').encode()
    with (out/name).open('xb') as f:f.write(b)
def run(out):
    out=out.resolve()
    if out.exists() or not out.is_relative_to((ROOT/'builds/phase19b-rom').resolve()):raise ValueError('Fresh phase output required')
    main,_=verify_inputs();stock=ROOT/'firmware/dsp/build-4486'
    extraction=json.loads((stock/'manifest.json').read_text());identity={}
    for b in extraction['blocks']:
        for k,h in [('stream_file','stream_sha256'),('payload_file','payload_sha256')]:
            identity[b[k]]=sha((stock/b[k]).read_bytes());assert identity[b[k]]==b[h]
    mainrows=rows(ROOT/'builds/phase3-selection0-channel0.asm',main)
    workerbytes=(stock/'selection0-channel1.payload24.bin').read_bytes()
    workerrows=rows(ROOT/'builds/phase3-selection0-channel1.asm',workerbytes)
    bootbytes=(stock/'bootstrap.payload24.bin').read_bytes()
    bootrows=rows(ROOT/'builds/phase3-bootstrap.asm',bootbytes)
    old=ROOT/'builds/phase19b-handoff/final'
    # Verified previous contracts are inputs, not rerun stock/emulator code.
    for name in ['arm-ordering.json','icc-contract.json','gpio-contract.json']:
        assert sha((old/name).read_bytes())==json.loads((old/'hashes.json').read_text())[name]
    out.mkdir(parents=True)
    docs=[('DSP56720RM.pdf',ROOT/'builds/phase19b-rom/historical-fetch/DSP56720RM.pdf',
           [0,72,73,79,80,96,97,98,99,100,101,102,103,104,146,147,298,299,300,303,304,305]),
          ('DSP56724RM.pdf',ROOT/'builds/phase19b/documentation/DSP56724RM.pdf',
           [0,75,76,79,80,96,97,98,99,100,101,102,142,143,248,249,250,254,255,256,257])]
    sources=[]
    for name,path,pages in docs:
        reader=PdfReader(path)
        text='\n'.join(f'PDF PAGE {i+1}\n'+reader.pages[i].extract_text() for i in pages)
        save(out,name+'.witnesses.txt',text.encode())
        sources.append(dict(filename=name,URL='https://www.nxp.com/docs/en/reference-manual/'+name,
            SHA256=sha(path.read_bytes()),target='DSP56720/21' if '720' in name else 'DSP56724/25',
            revision='1.1' if '720' in name else '1',date='02/2008' if '720' in name else '02/2009',
            kind='Official reference manual, NOT ROM source',pages=[i+1 for i in pages]))
    recovery=[]
    for p in [ROOT/'builds/phase19b-rom/public-fetch/public-retrieval.json',
              ROOT/'builds/phase19b-rom/historical-fetch/retrieval.json']:
        recovery.extend(json.loads(p.read_text()))
    save(out,'source-catalog.json',dict(status='ROM SOURCE NOT RECOVERED',official_manuals=sources,
         recovered_ROM_sources=[],reported_source=dict(URL='https://community.nxp.com/t5/Other-NXP-Products/DSP56725-bootloader/td-p/217563',
         poster='rocco',post_date='2011-06-25',reported_target='DSP56721',reported_parts=2,
         source_filenames=None,source_revision=None,source_date=None,source_SHA256=None,
         compatibility_report='Nikko 2011-06-29 reports support-supplied56725 file essentially identical; unverified forum report'),
         browser_observation=dict(page_accessible=True,attachment_links_exposed=0,sign_in_performed=False,
           public_attachment_API='Browser ERR_BLOCKED_BY_CLIENT; CLI HTTP403',
           note='Read-only DOM inspection found no attachment/download/asm/txt/zip links; no private-state inspection'),
         public_retrieval=recovery,
         absence_scope='These attempts did not recover source; not proof no source exists elsewhere'))
    comparison=[
       dict(portion='Core ISA',classification='COMPATIBLE',evidence='Both manuals describe DSP56300 cores; not identical silicon/ROM'),
       dict(portion='SHI register addresses',classification='IDENTICAL',scope='Reviewed mapping only',
            addresses=dict(HCKR='X:FFFF90',HCSR='X:FFFF91',HSAR='X:FFFF92',HTX='X:FFFF93',HRX='X:FFFF94')),
       dict(portion='ICC register pairing',classification='COMPATIBLE',evidence='Peer ICDR3 YFFFFD7 -> localICDR4 YFFFFD4, flags/ACK documented in both'),
       dict(portion='PCRG/PRRG mapping/reset',classification='IDENTICAL',scope='Reviewed register diagrams only',
            addresses=['Y:FFFFFA','Y:FFFFF9'],documented_reset=0x1e1),
       dict(portion='OMR bit names/mode0 protocol',classification='COMPATIBLE',evidence='MS/MSW controls; SPI slave24 count/load/program words; start at load'),
       dict(portion='RAM map',classification='DEVICE-SPECIFIC',
            DSP56721_mode110=dict(P_end=0x6000,X_end=0x9000,Y_end=0x8000),
            DSP56724_core0_mode110=dict(P_end=0x4000,X_end=0x6000,Y_end=0x4000),
            DSP56724_core1_mode110=dict(P_end=0x2000,X_end=0x2000,Y_end=0x2000)),
       dict(portion='Additional host interfaces/boot modes',classification='DEVICE-SPECIFIC',
            evidence='56720/21 includes HDI24 and associatedC-F boot modes; do not transplant those paths'),
       dict(portion='ROM SHI implementation/exit instructions',classification='UNRESOLVED',evidence='No matching source/binary obtained'),
       dict(portion='Conditional assembly/device variants',classification='UNRESOLVED',evidence='Cannot inspect missing source directives'),
    ]
    save(out,'applicability.json',comparison)
    timeline=json.loads((old/'arm-ordering.json').read_text())
    timeline.update(dict(status='VERIFIED ARM order + DOCUMENTED abstract boot contract; instruction timing UNRESOLVED',
         main_ROM_passes=2,worker_ROM_passes=1,worker_receives_uploaded_bootstrap=False,
         events=['ARM reset/control sequence','ROM main pass1 receives8-wordshim','shim modifiesOMR and reentersFFFFFE',
                 'ARM main upload; last program word consumed byROMpass2','unknown exactROMexit block -> mainP0 ->100',
                 'ARM worker upload; last program word consumed byworkerROM','unknown exactworkerROMexit -> workerP0 ->100',
                 'worker105/107/109 publishescursor; main102/104/106 observes peer'],
         first_main_poll_relative_to_peer_publication='UNRESOLVED; no preseeded30002',
         concurrency_decision='Staged two-original-core execution is potentially sufficient for a bounded rendezvous; not certified clock timing; no execution justified now',
         stage_obligations=['Keep logical ordering, private memories and shared alias','Model actual worker write and ICC flags/ACK',
                            'No elapsed-time/event claims without timing profile','Stop at unmodeled peripheral']))
    save(out,'two-core-timeline.json',timeline)
    save(out,'ROM-exit-flow.json',dict(status='UNRESOLVED actual instructions',ROM_PC=None,opcodes=None,
         documentary_flow=['consume count','consume load/start address','consume count Pwords, store contiguously',
                           'after last word, enter application at supplied load address'],
         exact_exit_basic_blocks=None,known_application_PC=0,
         register_or_peripheral_clobber_list=None,
         why_not_reconstructed='The input/output boot-format contract permits differing register/peripheral residues; it does not identify internal opcodes or exit state',
         no_speculative_ROM_code_generated=True))
    all_regs=['SR','OMR','SP','SC','SSH','SSL']+[f'{r}{i}' for r in ['R','N','M'] for i in range(8)]+[
              'LC','LA','X0','X1','Y0','Y1','A','B','CCR','interrupt masks/priorities/pending',
              'Y:PCRG','Y:PRRG','SHI configuration/status/FIFO','ICC data/flags/ACK']
    for role,blockname in [('main','selection0-channel0'),('worker','selection0-channel1')]:
        block=next(b for b in extraction['blocks'] if b['name']==blockname)
        fields=[dict(field='PC',value=0,classification='KNOWN EXACT',provenance=dict(kind='boot manual + verified boot header',
                  source='DSP56724RM table5-5',detail='Application post-load entry; not resetPC'),set_explicitly=True)]
        for register in all_regs:
            classification='BLOCKING UNKNOWN' if register in ['SR','OMR','interrupt masks/priorities/pending','Y:PCRG','Y:PRRG','SHI configuration/status/FIFO','ICC data/flags/ACK'] else 'CLOBBERED/UNSPECIFIED'
            detail='Matching ROM path not obtained; no constructor/reset substitution'
            if role=='main' and register in ['SP','SC','R0']:
                classification='INITIALIZED BY APPLICATION BEFORE FIRST USE'
                detail={'SP':'107 before first explicitJSR','SC':'108 before first explicitJSR','R0':'10B before10D'}[register]+'; inheritedIRQ/loop uses still gated'
            if role=='worker' and register=='R5':
                classification='INITIALIZED BY APPLICATION BEFORE FIRST USE';detail='105 before107/109 scalar publication'
            fields.append(dict(field=register,value=None,classification=classification,set_explicitly=False,
                 provenance=dict(kind='unknown' if classification=='BLOCKING UNKNOWN' else 'stock instruction' if classification.startswith('INITIALIZED') else 'unknown',detail=detail)))
        save(out,role+'-handoff.json',dict(status='BLOCKED',execution_allowed=False,role=role,image=block['payload_file'],
             image_SHA256=block['payload_sha256'],load_end=block['word_count'],fields=fields,
             explicit_assignments=[dict(field='PC',value=0,provenance='Verified boot header + documented start-address contract')],
             known_pre_second_ROM_OMR=dict(set_bits=[7,22],clear_bits=[21],provenance='Original uploadedshim',
                  scope='PRE-ROM only, not application handoff') if role=='main' else None,
             worker_bootstrap_OMR_state='No uploaded shim; cannot reuse main pre-ROM state' if role=='worker' else None,
             instruction_limit=0,guessed_zero_initialization=False))
    save(out,'peripheral-exit.json',dict(status='UNRESOLVED handoff values',
         PCRG=dict(address='Y:FFFFFA',documented_reset=0x1e1,ROM_writes=None,shim_writes=False,handoff=None),
         PRRG=dict(address='Y:FFFFF9',documented_reset=0x1e1,ROM_writes=None,shim_writes=False,handoff=None),
         SHI=dict(mode_during_boot='DOCUMENTED SPI slave24',application_config=None,status=None,FIFO=None,pending_IRQ=None),
         ICC=dict(reset_data=0,reset_provenance='device manual, hardware reset boundary only',handoff_data=None,flags=None,ACK=None,
              later_worker_publication='VERIFIED worker109 -> main102; not a ROM exit value'),
         worker_first_write=dict(PC=0x100,address='X:FFFF91',value=0,role='HCSR control write; HEN=0 disablesSHI',
              scope='Stock explicit write, not proof complete statusword becomeszero'),
         main_first_effects=['100 clearsPCRGbit13, setsCfromoldbit','101 setsPRRGbit13, setsCfromoldbit'],
         substitute_reset_values=False))
    save(out,'stock-witnesses.json',dict(bootstrap=list(bootrows.values()),
         main=[mainrows[p] for p in [0,0x100,0x101,0x102,0x104,0x106]],
         worker=[workerrows[p] for p in [0,0x100,0x102,0x103,0x104,0x105,0x107,0x109]],
         bootstrap_role='VERIFIED OMR mode setter + ROM re-entry shim; not SHI loader implementation',
         candidate_capacity_fact='Main2A5E words exceeds56724/core0 defaultP1000; mode110P4000 fits. Does not prove post-ROM mode preservation or actualpart.'))
    save(out,'execution-gates.json',dict(main_entry='NOT-YET-DETERMINED',worker_entry='NOT-YET-DETERMINED',
         faithful_BCLR_BSET='NO: reset semantics known, ROM handoff latches unknown',
         ICC_real_polling_publication='NO qualified execution model; static source provenance is VERIFIED',
         early_unknowns_resolved='NO',first_execution_justified=False,
         original_main_instructions_executed=0,original_worker_instructions_executed=0,
         resume19B2=False,first_blocker='Matching ROM implementation and exit state unavailable',
         next_step='Obtain offline copies of the two historical support-supplied source attachments (or authentic matching ROM listing), then validate variant/revision and SHI exit'))
    save(out,'validation.json',dict(status='TESTED static evidence integrity; ROM recovery/execution BLOCKED',
         all_ten_extracted_hashes=identity,stock_hashes_unchanged=True,
         official_documents_archived=True,no_ROM_source_or_binary_recovered=True,
         exact_exit_instruction_validation='NOT POSSIBLE with current sources',
         runtime_branch_token_ACK_validation='NOT REACHED',
         script_SHA256=sha(Path(__file__).read_bytes())))
    verify_inputs()
    save(out,'hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
    print('Static comparison PASS; ROM source unrecovered; both original execution gates CLOSED')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',required=True,type=Path)
    run(ap.parse_args().output_dir)
