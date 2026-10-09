"""Phase20B6 design ledger/schema exporter. No device or firmware execution APIs."""
import argparse, csv, hashlib, json, re
from pathlib import Path
from pypdf import PdfReader
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'builds/phase20b-snapshot-design'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(out,name,data):
    with (out/name).open('x',encoding='utf8',newline='\n') as f:
        json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
def table(out,name,rows):
    with (out/name).open('x',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def live_fields():
    rows=[]
    def add(field,cat,why,evidence,condition='selected routing0/nonlinear1 and offsets5/5, verified at capture'):
        rows.append(dict(field=field,classification=cat,reason=why,evidence=evidence,condition=condition,
          status='BOUNDED-PROOF local input liveness' if cat=='D' else 'VERIFIED source / CONDITIONAL acquisition'))
    add('PC','A','raw next-execution PC and normalized replay PC, with pipeline proof','FM7.2.4/7.2.5; P9D9..DD','all profiles')
    for f in ['SR','OMR']:
        add(f,'A','arithmetic, sticky flags, memory mapping, loop/interrupt/stack extension state','FM5.4; RM5','all profiles')
    for i in range(8):
        add(f'R{i}','A' if i==4 else 'D',
          'live Y post-state cursor' if i==4 else 'overwritten before material local use, or unused; full-state profile still captures it',
          {0:'9D9 Y7 reload',1:'A19; C2D local pointer producers',2:'C09/C21',3:'A1B; AD9/C4B',4:'ACC/BED/C9D',5:'ADF/C17/A80',6:'AAD/BE0/A82',7:'C06'}[i])
        add(f'N{i}','D','locally defined before selected-path use, or unused; retain only for full register comparison',
          {0:'unused in bounded selected path',1:'AAA/C0E/C52',2:'AAF/C72',3:'AD8/C0F/C53',4:'AAC/BE8',5:'AD1/BEA',6:'A7F',7:'unused in bounded selected path'}[i])
        add(f'M{i}','E' if i==5 else 'A','M5 overwritten from Y19 then Y1A on selected path; other modifiers remain material',
          'ADC/B24' if i==5 else 'indirect memory and postincrements9DD..CB7')
    for f in ['X0','X1','Y0','Y1','A','B']:
        add(f,'D','no material incoming numerical read on selected path; full-state/debug preservation capture still recommended',
          dict(A='9DD full overwrite before9DE',B='AA8 overwrite; downstream arithmetic redefines',X0='ACD',X1='ACC',Y0='AE2/BDF',Y1='AD7/BEC')[f])
    for f in ['SP','SC','LA','LC']:
        add(f,'A','active prefix and inherited loop state, not reset defaults','FM5.4.3; local DO/JSR nesting')
    for f,bit in [('LF',15),('FV',16)]: add(f,'C',f'derive from captured SR bit{bit}; reject inconsistent duplicates','FM5.4.1.2')
    add('hardware stack active indexed48-bit entries','A','preserve frame ordering/physical slots; SSH reads pop, not passive access','FM5.4.3; dsp.h ssh()/ssl()')
    add('EP/SZ/stack extension words','E','required if OMR.SEN or push/pop crosses extension boundary; reject unsupported profile','FM5.4.2/5.4.3; RM5')
    add('P original image','B','load exact unchanged original words after hash verification','selection0-channel0.payload24.bin','all profiles; reject patched image')
    add('X:[2C46,2C67)','A','32 original mono words plus natural guard','9C6..9D8; BE6/BE7/A93','all profiles')
    add('Y:7','A','coefficient cursor supplying R0 at9D9','9B8/9D9','raw9D9; at9DD derive consistency from R0 before changes')
    add('X coefficient/post base','C','derive Q+30 from captured coefficient cursor Y7 and independently correlated slot','9D9/9DD; Q=57B+4A*i','all profiles; do not assume slot0')
    add('Y post base','C','capture R4; correlate S+0C=59F+28*i+0C separately (12 decimal words)','R4 state cursor','all profiles; X/Y strides differ')
    add('X:[Q+30,Q+38)','A','post selectors/targets/sequence offsets, slot0:[5AB,5B3)','9DD/AA8/BDF/BEC/C10/C1A')
    add('X:[Q+40,Q+43)','A','header/gain delta/current, slot0:[5BB,5BE)','A7F/A8A/A8D/A91')
    add('X:[Q+38,Q+40)','D','eight skipped coefficients, slot0:[5B3,5BB); not read by selected path','A1F lua(r0+8)','selected routing0/nonlinear1 only')
    add('Y:[S+0C,S+1A)','A','14 retained words, slot0:[5AB,5B9)','ACC/AF5/BED/C04/C2D/C9D')
    add('Y:[8F,92)','D','P657 upstream results already materialized into X post targets','47F..498 precede seam','post-only replay; separately capture for event provenance')
    add('XCC','A','selects group accumulation buffer','A84..88','all profiles')
    add('selected X group:[2DF0,2E10) or[2E50,2E70)','C','derive addresses from XCC, but contents MUST be captured;32 prior accumulations','A82..94','all profiles')
    add('X39/X3A/X40','A','ramp shift/block count/coefficient shift; do not use startup defaults','AEB/AFD/A8B/BF0/C01')
    add('X3B','A','recursive pair-loop count remains input even routing0','CA4')
    add('X3C','E','used by nonlinear2/4 branches; unnecessary for selected nonlinear1','B41/B88','other nonlinear modes require independent liveness validation')
    add('X0 memory word','D','BDD stores R3 before later C1F load; not a captured scratch pointer input','BDD/C1F','selected routing0 path')
    add('Y10/Y19/Y1A/Y1C','A','sign mask, temporary/restore modifier words and nonlinear-table pointer','AD7/ADC/B24/ADF')
    add('X normalization table','C','addresses derive from Y1C and qualified modifier; table CONTENTS require capture or exact independently proven blob','B1C; M5<-Y19','512 words only if stock base/modifier/domain corroborated; otherwise fail narrow profile')
    add('X:[1600,1940)','E','832 words of ARM-uploaded coefficient table data; original P image does not contain runtime table epoch','C42..C8C','capture or hash-proven reconstruction from known upload source/transforms, never assume identical')
    add('Y:[F64,F69)','D','selected5/5 sequence overwritten by original C2D before C9D reads','C65/C78/C7C..7E beforeC18/C22','require linear modifier proof, correct offsets, unchanged C2D and no intervening asynchronous write')
    add('other Y coefficient sequences','E','non5/5 selectors require actual pointed contents unless overwrite-before-read proof exists','C10..22','fail closed outside selected profile')
    add('alternate X:[2C02,2C22) or[2C24,2C44)','E','routing1/2 subtraction/addition inputs; neither live for routing0','9E1..9F9','capture only if actual routing1/2; no universal profile admitted')
    add('output scratch X2C68/2C88/2D2E/2DB0 and transient X/Y2','D','selected path writes before dependent reads; memory must be mapped but initial contents omitted','AA8/BDD/C9F/C2D','selected path plus validated modifiers/block counts; out-of-range/undefined read refuses')
    add('pending IRQ/DMA/peer/ARM writers','E','freeze or exclude material mutations throughout acquisition; snapshot alone does not specify later IRQ timing','RM22/CIM; SHI44; prior19B-IRQ','local replay may use documented IRQ-excluded scope, not an invented no-IRQ stock claim')
    add('slot/active bank/patch/event provenance','A','correlate actual pointers, descriptor bank XCC, patch bytes/hash and event epoch','20B5 missing event chain','metadata live for provenance, not P657 numerical recomputation')
    return rows
def mechanisms():
    fields=['method','rank','fidelity','complexity','device_risk','firmware_patch','board_access','DSP_registers','hardware_stack','XY_memory','evidence','field_acquisition','host_extraction','blocker']
    rows=[
      ('external DSP OnCE hardware breakpoint',1,'highest potential; halted architectural snapshot, pipeline/injection and other writers need qualification','high: board+TAP+tool save sequence','electrical unknown; audio stops; no flash inherent','NO','YES; DSP signals unverified','CONDITIONAL forced transfers/subregister reads','CONDITIONAL save SP/SC and indexed frames; read effects qualified','YES architecturally via forced transfers','PLAUSIBLE-BUT-BOARD-UNVERIFIED; pinned FM7/RM22',
       'P comparator -> retire boundary -> direct pipeline latches first -> saved SR/registers -> stack -> selected memory while writers frozen','JTAG shifts to controller/PC -> raw binary and register logs -> offline bundle','unit part/pads/security/controller support; coordinated peer/DMA state; exact boundary'),
      ('temporary DSP inline capture + stock5E readback',2,'conditional architectural snapshot of instrumented execution; not untouched stock pipeline','very high: placement/save/stack/coherence+service endpoint','firmware and recovery unknown; timing changed','DSP YES; ARM maybe NO','not inherent; service physical mapping unresolved','CONDITIONAL save before clobber','UNRESOLVED exact walk/restore; raw pipeline not available','YES into immutable diagnostic buffer if placement proven','HYPOTHESIS design composed with VERIFIED logical stock read path',
       'inline branch at seam -> status/subfields/AGU/stack save -> bounded copies -> commit sealed buffer -> return normal -> later stock read','sealed DSP buffer ->29344/SPI2 ->269E4 ARM scratch ->37B0C/20C90 logical MIDI sender -> future authorized host decoder','no RAM allocation or hook assembled; stack/IRQ capture proof, transport endpoint and rollback unresolved'),
      ('temporary DSP inline capture + MCU debug extraction',3,'same hook fidelity; avoids unproven external service endpoint','very high: hook plus verified ARM-debug access/procedure','DSP patch recovery + ARM debug/control disturbance','DSP YES; ARM patch optional','YES STM32; reported header only','CONDITIONAL hook supplies values; SWD alone NO','CONDITIONAL hook supplies frames; SWD alone NO','CONDITIONAL invoke existing read helpers after sealing','HYPOTHESIS bridge; VERIFIED SPI read helper functions',
       'hook-sealed DSP words -> future debugger-assisted existing29344 calls -> allocated ARM scratch -> debugger ARM RAM dump','MCU debugger raw file export -> offline bundle; no invented USB endpoint','function invocation changes ARM state/stack/cache; buffer ownership/helper safety/STM access unresolved'),
      ('MCU SWD/JTAG alone',None,'ARM context only; cannot freeze or read private DSP architectural state','moderate/high board validation','halt ARM affects host/peripherals; electrical unknown','NO','YES','NO','NO','NO direct; existing SHI helpers only','CONDITIONAL candidate STM32; public header report',
       'ARM registers/RAM/SPI buffers are inspectable if debug permitted; DSP-private state not mapped into ARM address space','ARM debugger dump of RAM/regs only','not sufficient snapshot; halting ARM does not halt DSP'),
      ('stock5E read service alone',None,'sequential incoherent memory reads, no exact seam trigger','moderate transport validation','protocol/cache/scheduler perturbation; count/prefetch limits','NO','not inherently','NO except stale incidental ISR saves','NO','YES supported private range locally','VERIFIED offline ARM/DSP instructions; physical endpoint UNRESOLVED',
       '269E4 READ ->29344 ->SHI156 ->HTX ->ARM reply; no seam stop or register-read command','37B0C/20C90 logical framed MIDI reply, exact physical endpoint unknown','no freeze, no PC/AGU/stack; cannot treat Y2000 save RAM as simultaneous full snapshot'),
      ('emulator seeded from smaller observation',None,'conditional model, not natural stock state without complete seed','high complete model; lower post-only after qualified seed','none on device','NO','only if obtaining seed','model only','model only','model only','VERIFIED local execution substrate; unresolved hardware inputs',
       'smaller observed live subset + proven immutable tables -> original local replay; cannot reconstruct unobserved long-lived histories','offline files/traces','not an acquisition substitute; static exhaustion persists; board/IRQ/core fidelity conditional'),
      ('passive SPI/ESAI/GPIO or external-memory trace',None,'supplementary event/audio correlation only','moderate/high probe qualification','loading/voltage/access unknown; no command required','NO','YES','NO','NO private state','NO complete private X/Y','VERIFIED logical buses; external access unverified',
       'observe host transfers/audio; cannot see DSP-private writes, registers or stack','analyzer trace offline','insufficient snapshot; ICC internal; no proven complete address+data trace'),
      ('selection1 diagnostic commands5C/5D/71',None,'different diagnostic payload/context','moderate known logical routes','switches active image; destroys target context','NO new patch, but changes selection','not inherently','NO','NO','limited test results','VERIFIED original diagnostic branches',
       'switch selection ->tests at selection1 ->Y3..8 results','existing logical service responses where recovered','not normal selection0 P9D9; reject for seam capture')]
    return [dict(zip(fields,r)) for r in rows]
def format_schema():
    word=dict(type='string',pattern='^[0-9A-F]{6}$')
    h=dict(type='string',pattern='^[0-9a-f]{64}$')
    fragment=dict(type='object',additionalProperties=False,required=['space','start_word','count_words','file_byte_offset','sha256','role','coherence_epoch'],properties={
      'space':dict(enum=['X','Y']), 'start_word':word,'count_words':dict(type='integer',minimum=1),
      'file_byte_offset':dict(type='integer',minimum=0),'sha256':h,'role':dict(type='string'),'coherence_epoch':dict(type='string')})
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema',
      'title':'ct-original-stock-post-snapshot-v1 DESIGN; no sample values', 'type':'object','additionalProperties':False,
      'required':['format','profile','normalized_entry_pc','stop_before_pc','files','fragments','source_hashes','boundary_proof','coherence_proof','admission'],
      'properties':{'format':dict(const='ct-original-stock-post-snapshot-v1'),
       'profile':dict(enum=['routing0-nonlinear1-offset5-linear-qualified','other-mode-not-admitted']),
       'normalized_entry_pc':dict(const='0009D9'),'stop_before_pc':dict(const='000A95'),
       'files':dict(type='object',required=['x','y','registers','stack','metadata'],properties={k:dict(type='string',const=v) for k,v in dict(x='x-memory.bin',y='y-memory.bin',registers='registers.json',stack='stack.json',metadata='metadata.json').items()},additionalProperties=False),
       'fragments':dict(type='array',items=fragment,minItems=1),
       'source_hashes':dict(type='object',required=['ARM','SYX','DSP_P','table_epoch'],properties={k:h for k in ['ARM','SYX','DSP_P','table_epoch']},additionalProperties=False),
       'boundary_proof':dict(type='object',required=['raw_next_pc','last_retired_pc','pipeline_file','normalization_rule','no_post_instructions_retired','no_intervening_mutation'],
           properties={'raw_next_pc':word,'last_retired_pc':word,'pipeline_file':dict(type='string'),
             'normalization_rule':dict(enum=['exact9D9','9DD-after9DC-qualified-idempotent-prefix']),
             'no_post_instructions_retired':dict(const=True),'no_intervening_mutation':dict(const=True)},additionalProperties=False),
       'coherence_proof':dict(type='object',required=['epoch','writers_excluded','transport_log','sealed_hashes'],properties={
         'epoch':dict(type='string'),'writers_excluded':dict(type='array',items=dict(type='string'),minItems=1),
         'transport_log':dict(type='string'),'sealed_hashes':dict(type='array',items=h,minItems=1)},additionalProperties=False),
       'admission':dict(type='object',required=['values_are_observed','unknown_material_fields','firmware_modified','approved_scope'],properties={
          'values_are_observed':dict(const=True),'unknown_material_fields':dict(type='array',maxItems=0),
          'firmware_modified':dict(type='boolean'),'approved_scope':dict(type='string')},additionalProperties=False)}}
    schema['$defs']={
      'registers':dict(type='object',additionalProperties=False,required=['raw_pc','SR','OMR','R','N','M','A','B','X0','X1','Y0','Y1','SP','SC','LA','LC','LF','FV','omissions'],
        properties={**{k:word for k in ['raw_pc','SR','OMR','SP','SC','LA','LC']},
          **{k:{'anyOf':[word,dict(type='null')]} for k in ['X0','X1','Y0','Y1']},
          **{k:dict(type='array',minItems=8,maxItems=8,items={'anyOf':[word,dict(type='null')]}) for k in ['R','N','M']},
          **{k:dict(anyOf=[dict(type='string',pattern='^[0-9A-F]{14}$'),dict(type='null')]) for k in ['A','B']},
          **{k:dict(type='integer',enum=[0,1]) for k in ['LF','FV']},
          'omissions':dict(type='array',items=dict(type='object',required=['field','proof','scope'],properties={k:dict(type='string') for k in ['field','proof','scope']},additionalProperties=False))}),
      'stack':dict(type='object',additionalProperties=False,required=['initial_SP','initial_SC','entries','extension','capture_effects'],properties={
        'initial_SP':word,'initial_SC':word,'entries':dict(type='array',maxItems=16,items=dict(type='object',additionalProperties=False,
          required=['physical_index','high24','low24','frame_provenance'],properties={'physical_index':dict(type='integer',minimum=0,maximum=15),'high24':word,'low24':word,'frame_provenance':dict(type='string')})),
        'extension':dict(type='object',required=['enabled','EP','SZ','fragments'],properties={'enabled':dict(type='boolean'),'EP':{'anyOf':[word,dict(type='null')]},'SZ':{'anyOf':[word,dict(type='null')]},'fragments':dict(type='array',items=fragment)},additionalProperties=False),
        'capture_effects':dict(type='array',items=dict(type='string'))}),
      'metadata':dict(type='object',required=['capture_id','coherence_epoch','method','trigger','cpu_halted','capture_instructions','original_instructions_after_trigger','logical_track','voice_slot','active_bank','patch_sha256','patch_file','board_evidence','core_mapping_evidence','timestamp','block_index','raw_transport_sha256','modified_execution'],
        properties={'capture_id':dict(type='string'),'coherence_epoch':dict(type='string'),'method':dict(type='string'),'trigger':dict(type='string'),
          'cpu_halted':dict(type='boolean'),'capture_instructions':dict(type='array',items=dict(type='string')),
          'original_instructions_after_trigger':dict(type='integer',minimum=0),'logical_track':dict(type='integer',minimum=0),
          'voice_slot':dict(type='integer',minimum=0,maximum=11),'active_bank':dict(type='integer',enum=[0,1]),
          'patch_sha256':h,'patch_file':dict(type='string'),'board_evidence':dict(type='string'),'core_mapping_evidence':dict(type='string'),
          'timestamp':dict(type=['string','null']),'block_index':dict(type=['integer','null']),
          'raw_transport_sha256':h,'modified_execution':dict(type='boolean')},additionalProperties=False)}
    return schema
def run(out):
    out=out.resolve()
    if out.exists() or out==BASE or not out.is_relative_to(BASE): raise ValueError('Fresh design child required')
    sources=['original/circuittracks-firmware-4486.syx','firmware/circuittracks-firmware-4486.bin',
      'firmware/dsp/build-4486/selection0-channel0.payload24.bin','builds/phase3-selection0-channel0.asm',
      'builds/phase16/final/read-side-effects.json','builds/phase16/final/safety-gate.json',
      'builds/phase17/final/silicon-and-board.json','builds/phase17/final/citations.json',
      'builds/phase20b-sequence/final/runtime-snapshot-minimum.json','builds/phase20b-sequence/final/qualification.json',
      'builds/phase20b-seam/final/seam-map.json','builds/phase20b-seam/final/seam-instructions.csv',
      'emulator/harness/source-manifest.json','emulator/upstream/dsp56300/source/dsp56kEmu/dsp.h',
      'emulator/upstream/dsp56300/source/dsp56kEmu/dsp.cpp','emulator/upstream/dsp56300/source/dsp56kEmu/dspregs.h',
      'plaits/seam/contract.py','emulator/harness/checkpoint/replay.cpp',
      'builds/phase9/routing/0803BB38-0803BCA0.asm','builds/phase9/routing/0803BE20-0803BF20.asm',
      'builds/phase19b/documentation/DSP56300FM.pdf','builds/phase19b/documentation/DSP56724RM.pdf']
    sources+=['tools/ct_snapshot_design.py']
    sources += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'builds/phase20b-sequence/final').glob('*')) if p.is_file() and p.relative_to(ROOT).as_posix() not in sources]
    hashes={p:sha(ROOT/p) for p in sources}
    assert hashes[sources[0]]=='bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd'
    assert hashes[sources[1]]=='b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da'
    assert hashes[sources[2]]=='b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855'
    assert json.loads((ROOT/sources[9]).read_text())['static_strategy']=='EXHAUSTED'
    payload=(ROOT/sources[2]).read_bytes();listing=(ROOT/sources[3]).read_text()
    checked=0
    for line in listing.splitlines():
        m=re.match(r'P:([0-9A-F]{6})  ([0-9A-F]{6})(?: ([0-9A-F]{6}))?\s+',line)
        if m and 0x9c6<=int(m[1],16)<0xcb8:
            at=int(m[1],16)*3;raw=bytes.fromhex(m[2]+(m[3] or ''));assert payload[at:at+len(raw)]==raw;checked+=1
    out.mkdir(parents=True);(out/'evidence').mkdir()
    docs=[]
    for name,pages in [('DSP56300FM.pdf',[90,95,96,97,126,129,130,132,135,136,137,140,141,142,143,144]),
                       ('DSP56724RM.pdf',[74,75,76,97,98,99,118,119,120,121,457,458,459,460])]:
        r=PdfReader(ROOT/'builds/phase19b/documentation'/name)
        text='\n'.join(f'PDF PAGE {i} (one-based)\n'+r.pages[i-1].extract_text() for i in pages)
        with (out/'evidence'/(name+'.txt')).open('x',encoding='utf8') as f:f.write(text)
        docs.append(dict(path='builds/phase19b/documentation/'+name,sha256=hashes['builds/phase19b/documentation/'+name],pages=pages,
          URL='https://www.nxp.com/docs/en/reference-manual/'+name,note='VERIFIED pinned primary text; no network retrieval or hardware check'))
    with pdfplumber.open(ROOT/'builds/phase19b/documentation/DSP56724RM.pdf') as pdf:
        for page in [118,119]:
            pdf.pages[page-1].to_image(resolution=110).save(str(out/'evidence'/f'CIM-page{page}.png'))
    table(out,'snapshot-live-fields.csv',live_fields())
    points=[
      dict(candidate='A immediately before9D9',rank=2,raw_next_pc='9D9',mono_complete='YES only final9D8 and DO exit retired',guard='natural',destroyed='owned DO loop frame exits; incomingR0 not reloaded',post_mutation='NO',mechanism='32nd executed-P9D8 comparator hit; DO exit/pipeline semantics must be established',perturbation='halts after instruction; peripheral writers may continue'),
      dict(candidate='B at9D9 pre-execution',rank=2,raw_next_pc='9D9',mono_complete='YES',guard='natural',destroyed='same asA; no reload yet',post_mutation='NO',mechanism='software debugger PC display insufficient; breakpoint9D9 itself retires reload ->9DA',perturbation='exact point needs boundary verification, not force-PC'),
      dict(candidate='C after reload before9DD',rank=1,raw_next_pc='9DD after program breakpoint9DC',mono_complete='YES',guard='natural',destroyed='original incomingR0 overwritten; no other intended prefix mutation',post_mutation='NO if no9DD instruction retired',mechanism='executed program fetch9DC NOP -> debug entry; save PABEX/PABDR/PABFR/PIL/PDB before injection',perturbation='halt; normalize to replay9D9 only if prefix idempotence and no intervening IRQ/DMA/writes proved'),
      dict(candidate='D final store boundary',rank=4,raw_next_pc='depends on occurrence and trigger type',mono_complete='NO on first9D8 hit; YES on32nd completed iteration',guard='natural once generation finished',destroyed='R1 increments; DO exit state matters',post_mutation='NO if still before9DD',mechanism='X-store watchpoint acknowledge after following instruction; not assumed pre9D9',perturbation='DO/loop acknowledgement more difficult; program comparator preferable')]
    table(out,'capture-point-comparison.csv',points)
    methods=mechanisms();table(out,'acquisition-methods.csv',methods)
    dump(out,'debug-interface-evidence.json',dict(status='PLAUSIBLE-BUT-BOARD-UNVERIFIED',primary_sources=docs,
      facility='OnCE per DSP56300 core via two serial4-bit TAPs; not SC140 EOnCE',
      signals=['TCK','TMS','TDI','TDO','reference voltage/ground; no board assignment'],TRST='RM22 figure/table has controllerTRST; RM2.21 lists only four external signals. No separate physical TRST pad assumed',
      board=json.loads((ROOT/'builds/phase17/final/silicon-and-board.json').read_text()),
      visibility={'registers':'FM7.2.7.5 forced instruction toOGDB; accumulator subfields needed to avoid limiter',
       'memory':'FM7.2.7.6 injected memory transfer throughOGDB; preserve pointer/modifier/status first',
       'stack':'architectural16x48 stack; SSH reads pop. Tool must save initialSP/SC/SR and frame ordering and extension state before destructive walk',
       'loops':'LA/LC registers and LF/FV inSR plus saved outer frames; not just debugger PC'},
      breakpoints='FM7.2.4: executed program fetch trigger stops AFTER matching instruction; X/Y/P MOVE access trigger stops after FOLLOWING instruction',
      pipeline='FM7.2.7.3 rawPDB/PIL first; PABEX is would-execute instruction. Preserve raw proof independent of normalized PC.',
      limitations=['unit silicon and package unresolved','DSP pad routing/voltage inaccessible or unknown','no compatible controller/tool capability tested','ROM-security possibility not resolved for unit',
        'other core debug coupling configurable, DMA/ARM/peripherals not proved frozen','OnCE is intrusive and halting, not passive real-time trace'],
      provenance_plan={'slot':'captureY7 coefficient cursor andR4 history cursor; independently solvei fromY7=57B+4A*i+30 andR4=59F+28*i+0C; require samei in0..11',
        'bank':'captureXCC descriptor bank already used byA84..88; corroborate with active descriptor/ARM context, not patch position',
        'patch':'OnCE alone cannot recover full340-byteARM patch from noninvertibleDSP parameters. Additional coherentARM observation: original3BE60 selects model=[view+344+4*bank]; 3BBE8/3BC06 show model+0C points to pointercell containing bytebuffer; model+10 length must be340. Dump actualbuffer andhash.',
        'ARM_root':'runtime view root location/active invocation and coherentARM access still UNRESOLVED; may require MCUdebug alongsideOnCE. Do not execute3BE60 to discover it or guess rootaddress.',
        'event':'record current player/time/allocator state or separately qualified correlated eventlog; exact audible event identity may remain unqualified even with a numeric post snapshot'},
      CIM_caution='RM6.1.1 map putsOGDB atXFFFFFC; summary figure labelsYFFFFFC conflict. Resolve device-specific access before choosing injection opcode. DMAS is a stall INTERRUPT threshold, not a DMA freeze control.'))
    dump(out,'stock-readback-capabilities.json',dict(status='VERIFIED local memory READ; INSUFFICIENT complete coherent snapshot',
      stock_path='1F30A ->269E4 op1 ->private29344 or shared295BA ->SPI2 ->SHI44/156 ->HTX ->ARM scratch ->37B0C/20C90 logical MIDI reply',
      X_private='YES valid low15-bit address <8000 under24-bit transport',Y_private='YES same plus bit15 space selector',
      shared='YES [30000,38000) through existing extended path',arbitrary_address_ranges='NO universal read; peripheral/reserved/extra prefetch forbidden without separate proof',
      CPU_registers=False,hardware_stack=False,seam_trigger=False,diagnostic_status='selection1 test outputs only, not stock normal seam',
      incidental_saved_context='Y2000..2005 contains last SHI ISR scratch, not simultaneous complete seam register record',
      side_effects=json.loads((ROOT/'builds/phase16/final/read-side-effects.json').read_text()),
      safe_bounds='32 words fits reviewed scratch locally; not a globally enforced safety maximum. extra address+1 prefetch, tail padding and stale cache hazards persist',
      snapshot_transport_use='only read a future immutable sealed diagnostic buffer, after capture, and after logical/physical transport qualification',
      external_endpoint='UNRESOLVED USB vs DIN assignment; no invented serial/USB endpoint; no service packets generated'))
    order=[
      dict(step=0,action='conditional placement/coherence gate: inline JMP-style redirect, noJSR/DO or prior scratch-register setup',hazard='no proven freeP/RAM or IRQ exclusion; no assembly generated'),
      dict(step=1,action='absolute rawSR,OMR then A2/A1/A0,B2/B1/B0 if full-state capture required',hazard='full accumulator move can limit and set stickyS/L; use raw subfields. SaveSR BEFORE such transfers or masking'),
      dict(step=2,action='R/N/M raw registers via absolute stores without changing pointer/modifier first',hazard='cannot prepare destination pointer in unsavedR; extended absolute store encoding/access qualification needed'),
      dict(step=3,action='saveSP/SC/LA/LC and SR-LF/FV; EP/SZ if enabled; take SSL beforeSSH for each top frame',hazard='SSH read popsSP/SC and may reload extension/flags; full walk/restore proof required; do not call helper/useDO first'),
      dict(step=4,action='data registers if not already saved; then admit bounded pointer/counter workspace',hazard='all input registers clobbered by memory copier must already be saved'),
      dict(step=5,action='copy selected controls/history/mono+guard/group/tables in one excluded-writer epoch',hazard='no coherent epoch if SHI/peer/DMA can mutate ranges during copies; masking only after originalSR captured is itself perturbation'),
      dict(step=6,action='write version/range/slot/hash provenance, then commit marker last; restore state if future design proves this safe',hazard='no stock completion mailbox endpoint invented; READY header remains in new unallocated buffer; raw pipeline unavailable to hook')]
    dump(out,'capture-order.json',dict(status='CONCEPTUAL ONLY; not qualified executable sequence',steps=order,
      exact_state_limit='software self-capture cannot preserve the original prefetched pipeline/cache/elapsed cycles or guarantee simultaneous pre-interrupt state; stack walk is destructive. External OnCE raw-latch capture preferred for exact boundary.',
      external_sequence=['read immutable OnCE pipeline latches before GO','save rawSR/OMR/AGU/register subfields before clobber','save stack controls before anySSH pop','read selected memory only while all material writers excluded','archive raw commands/responses and metadata; no reset/GOTO/resume recipe authorized']))
    core_words=33+11+14+32+5+5 # data plus five Xglobals and Y7/10/19/1A/1C
    dump(out,'diagnostic-hook-requirements.json',dict(status='DESIGN HYPOTHESIS ONLY; not assembled, patched, reserved or tested',
      entry='inline future redirect at9D9; original generation must complete before firstcapture mutation',
      resource_estimate={'P_words':[160,320],'basis':'rough absolute register stores +bounded copy loops +stack handling +metadata/restore; instruction widths and exact stack algorithm unqualified',
       'core_data_words':core_words,'full_register_archive_words_estimate':43,'active_stack_words':'2*s,0<=s<=15 only ifSEN0; extension adds exact required words',
       'metadata_work_words_estimate':[24,48],'tables_words_upper_selected':832+512,
       'total_words_estimate_without_tables':[167,221],'table_inclusive_words_estimate':[1511,1565],
       'precision':'CALCULATED inventory / ESTIMATE code cost, not measured resource or placement proof'},
      clobbers='after saving: A/B/data/R/N workspace, CCR, address counters, stack walker; no preserve-after-clobber assumption',
      memory_allocation='UNRESOLVED. No diagnostic buffer address or stockRAM reservation. Existing highX work not promoted.',
      transport='future sealed blob can be read using stockX/Y read mechanism after capture; logical ready flag stored in blob, not an existing mailbox job',
      completion='new buffer commit marker consumed by future observer only; no stock host notification endpoint proved',
      exactness='instrumented snapshot, not untouched stock. Same raw selected live inputs may be captured conditionally; hardware pipeline/context and asynchronous coherence unresolved',
      flash_authorized=False))
    risk=[]
    for m in methods:
        risk.append(dict(method=m['method'],instruction_perturbation='forced debug instructions AFTER saved boundary' if m['rank']==1 else 'extra hook instructions' if m['rank'] in [2,3] else 'see acquisition path',
          cycle_perturbation='halt/walltime and peer/peripheral progression' if m['rank']==1 else 'unmeasured hook/ISR/debug timing',
          register_CCR_stack='must save BEFORE inspection/clobber; stackSSH read is destructive' if m['rank'] in [1,2,3] else 'no full register/stack observation',
          DMA_interrupt='no freeze assumed; exclude all material concurrentwriters or refuse',
          audio_history_validity='at trigger conditionally valid; subsequent audible continuity not guaranteed',
          rollback='NO flashing inherent' if m['firmware_patch']=='NO' else 'UNRESOLVED stock restore and device recovery, despite original source backup',
          device_risk=m['device_risk'],evidence=m['evidence']))
    table(out,'risk-comparison.csv',risk)
    schema=format_schema();dump(out,'snapshot-schema.json',schema)
    dump(out,'emulator-import-schema.json',dict(status='DESIGN contract only; existing generic stock-snapshot importer NOT IMPLEMENTED',
      files=dict(snapshot='manifest/schema above',registers='canonical architectural fixed-widthhex; no signeddecimal/floats/defaults',
       stack='initialSP/SC/LA/LC and indexed48bit frames high24/low24, plus conditional extension',metadata='raw method/trigger/TAP/core/board/patch provenance and immutable hashes',
       x_memory='concatenated unsigned24bit MSB-first3-byte words; sparse fragments address explicit',y_memory='same; separate space file; hashes perfragment andwholefile'),
      register_encoding={'word24':'6 uppercasehex characters','accumulator56':'14 uppercasehex, raw bit pattern fromA2:A1:A0','A2_B2':'2 hex characters',
        'R_N_M':'8 entries each, raw24bit. D fields may be omitted only in certified numeric profile, never for complete-state comparison',
        'SP':'raw24bit','SC':'raw5-bit represented as24bit hex, upper19 zero','LF':'SR bit15','FV':'SR bit16'},
      source_mapping={'ordinary':'DSP::writeReg typedTReg24; SP raw; LA/LC real values','accumulators':'DSP::writeReg(Reg_A/B,TReg56(raw56)), not directreadRegs().a; local core stores left-aligned internally',
        'SC':'typedTReg5 overload; do not confuse SR.SC bit13 with stack counter','M':'writeReg uses set_m deriving mMask/mModulo; direct struct assignment invalid',
        'stack':'writeReg Reg_SP selects physical index then Reg_SSL/Reg_SSH writes top IN PLACE (API unlike hardware MOVEC); restore initialSP/SC afterwards; extension needs qualified model',
        'SR':'getSR/writeRegReg_SR resolves CCR caches; lazy flags must not be imported as constructor defaults'},
      initialization_order=['validate hashes/boundary/writers/ranges before CPU','map P and sparse X/Y strictly; deny undefinedreads/peripherals','set actualOMR/SR andAGU through typed APIs','install active indexedstack andloop controls then restoreSP/SC/SR','apply explicit captured/derived/dead tags','set normalized9D9 PC last; qualified interpreter, stop BEFORE A95'],
      normalization={'exact9D9':'raw9D9 unchanged', '9DD_after9DC':'rawR0 must equalY7; no postretirement/mutation/IRQ; only numeric post prefix-equivalence, not equal hardware cycles/pipeline; archive raw9DD state'},
      refusal=['unknown material value','missing frame or stackoverflowmargin','SEN1 extension unsupported','selector/domain/count/modifier outside certified profile','unmapped table orscratchread','interveningwriter/pendingIRQ unmodeled','rawPC lacks pipeline boundary proof','patch modified but called original'],
      success_checks=['32 group words captured/result with exact integer arithmetic','all requiredpersistent mutations and originalguard effects accounted','stopA95 notexecuteperipheral tail','independent typedregister import/readback fixtures first'],
      original_instructions_executed=0))
    dump(out,'recommendation.json',dict(status='READY-FOR-ACQUISITION-DESIGN',evidence_level='CONDITIONAL architectural plausibility; board/tool/coherence gates OPEN',
      ranking=[m['method'] for m in methods[:3]],preferred_method=methods[0]['method'],preferred_capture='C: afterexecuted9DC, rawnext9DD; normalized9D9 only under explicit proof',
      exact9D9_alternative='32nd executed9D8 program breakpoint, confirmDOcompletion before9D9; higherqualification complexity',
      further_broad_static_RE=False,runtime_snapshot_necessary=True,noninvasive_debug='PLAUSIBLE electrically unmodified, but halting/injection means not behaviorally noninvasive',
      temporary_diagnostic_firmware_necessary='UNRESOLVED; not if OnCE qualifies, possibly if DSPaccess unavailable',hardware_design_justified=True,firmware_flashing_justified=False,
      recovery='Firmware below ARMbase08010000/bootloader/updater independence and restore after brokenDSP not established; backups do not prove device recovery',
      provenance_gate='DSP-only OnCE is not enough for fullARM patch/event identity; simultaneous/coherentARM model observation or qualified correlatedlog required. Root pointer and cross-debug coordination still unresolved.',
      next_step='Qualify board-specific DSP TAP exposure, actualsilicon/core mapping and controller pipeline/stack/coherence support from existing documentation; any physical inspection/test requires separate authorization. Do not connect or flash now.',
      acquired_snapshot=False,stock_execution=0,hardware_access=False))
    assert hashes=={p:sha(ROOT/p) for p in sources}
    dump(out,'validation.json',dict(status='TESTED design export/hash/byte checks only',source_hashes=hashes,
      reviewed_original_seam_rows=checked,documents=docs,design_only=True,hardware_access=False,network_access=False,
      assembled_hook=False,firmware_changes=False,CPU_execution=0,importer_implemented=False,acquired_snapshot=False,
      limitations='liveness profile conditional, code resources estimates, board/tool and concurrentwriter control unverified',
      previous_formula_erratum='Y post base S+12 meant12 decimal words. Correct hexadecimal expression S+0C; endS+1A gives14 words. Slot0 numeric range remains[5AB,5B9). Earlier exports preserved.'))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True)
    run(Path(p.parse_args().output_dir))
