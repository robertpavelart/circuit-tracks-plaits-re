"""Offline Phase20B7 evidence ledger. No target interface, network, or CPU execution.

Produces fresh reports only; refuses overwrites and does not import device tools.
Documentary qualifications are not measured board properties or capture results.
"""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'builds/phase20b-tapqual'
SRC = BASE / 'sources'
COMMIT = '8da0578d7bce3e134821ccf10911182788debc32'
RM = ROOT / 'builds/phase19b/documentation/DSP56724RM.pdf'
FM = ROOT / 'builds/phase19b/documentation/DSP56300FM.pdf'
PREVIOUS = ROOT / 'builds/phase20b-snapshot-design/final-v4'
DOC_URL = 'https://www.nxp.com/docs/en/data-sheet/DSP56724EC.pdf'
BOARD_URL = 'https://github.com/userx14/CircuitTracksReverseEngineering'
OPEN_URL = f'https://github.com/openocd-org/openocd/blob/{COMMIT}/src/target/'
SYMPHONY_URL = 'https://www.nxp.com/products/processors-and-microcontrollers/additional-mpu-mcus-architectures/digital-signal-processors/symphony-studio-development-tools:SYMPH_STUDIO'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dump(out, name, data):
    with (out / name).open('x', encoding='utf8', newline='\n') as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write('\n')


def table(out, name, rows):
    with (out / name).open('x', encoding='utf8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def pin_rows():
    rows = []
    def add(signal, p724, p725, direction, reset, pull, role, evidence):
        rows.append(dict(signal=signal, DSP56724_144_LQFP=p724,
            DSP56725_80_LQFP=p725, direction=direction, electrical_domain='IO_VDD, nominal 3.3 V',
            reset_state=reset, documented_pull=pull, role=role, evidence=evidence,
            status='VERIFIED package documentation; CONDITIONAL actual unit applicability',
            board_net='UNRESOLVED'))
    for signal, p724, p725 in [('TMS','101','55'),('TCK','102','56'),('TDI','103','57')]:
        add(signal,p724,p725,'input','input','internal pull-up; board external pulls unknown',
            'external TAP', 'RM PDF48/49 Figures2-1/2-2; PDF74 Table2-21')
    add('TDO','104','58','output','tri-state','none specified',
        'driven only Shift-IR/Shift-DR; falls with TCK', 'RM PDF48/49/74')
    add('RESET','111','63','Schmitt input','active low; resets both cores',
        'internal pull-up', 'boot modes latch on deassertion; no natural-seam reset', 'RM PDF48/49/52')
    add('PINIT/NMI','105','59','input','PLL/PEN initialization input',
        'internal pull-up', 'negative-edge NMI after reset; NOT a debug-request pin', 'RM PDF48/49/51')
    add('SCAN','144','80','input','input','internal pull-down; must remain low in normal operation',
        'manufacturing test; NOT TRST or TAP selection', 'RM PDF48/49/51')
    add('IO_VDD','12 29 48 58 72 81 107 132','5 33 49 75','power','power',
        'not applicable','I/O reference candidate, not permission for probe power', 'RM PDF48/49/50')
    add('IO_GND','13 30 49 59 71 82 108 133','6 34 50 76','ground','ground',
        'not applicable','verify actual board ground; do not infer from pad shape', 'RM PDF48/49/50')
    add('MODA0 MODB0 MODC0 MODD0','143 142 141 140','79 78 77; MODD0 not external',
        'input at reset','boot-mode inputs','see individual mux signal definitions',
        'core0 boot mode; NOT external core/TAP selection', 'RM PDF48/49; Table2-20')
    add('MODA1 MODB1 MODC1 MODD1','129 128 127 126','72 71 70; MODD1 not external',
        'input at reset','boot-mode inputs','see individual mux signal definitions',
        'core1 boot mode; NOT external core/TAP selection', 'RM PDF48/49; Table2-20')
    for signal, role in [('TRST','internal TAP reset shown in RM22; package pin NOT listed'),
                         ('DE / DEBUG_REQUEST / debug ACK','request/ack/status through OnCE/TAP; no distinct external package pin established'),
                         ('CORE/TAP SELECT','selected through two serial instruction registers; no dedicated external selector')]:
        add(signal,'not listed','not listed','not an established external signal',
            'not applicable','not applicable',role,'RM PDF48/49/74 and PDF457..460')
    return rows


def board_rows():
    return [dict(source=source, observation=observation, interpretation=interpretation,
        limitation=limit, status=status) for source,observation,interpretation,limit,status in [
        ('board-README.md + board_top_under_rf_shield_closer.jpeg',
         'Author lists DSPB56724AG; photographed LQFP marking appears consistent',
         '144-pin DSP56724AG strongly supported on photographed board',
         'No user-unit photo; mask/lot and exact actual unit unresolved', 'STRONGLY SUPPORTED'),
        ('board_bottom_full.jpeg', 'Circuit Rhythm/Tracks MAIN BOARD V3.2 FP002099-01; 2020 Novation/Focusrite',
         'public board revision provenance', 'not proof user has this revision', 'VERIFIED image observation'),
        ('board-j3.png + board_bottom_full.jpeg', 'J3 Programming Debug; ten gold pads and alignment holes',
         'TC2050-like candidate MCU footprint', 'physical connectivity not measured', 'VERIFIED visible layout'),
        ('board-debugHeader.svg', 'Author labels SWDIO/SWCLK/GND; resistor-to-3.3V and Vreg node; uncertain SWO/reset',
         'supports STM32 SWD interpretation of J3', 'third-party mapping; not independently verified; uncertain labels remain uncertain', 'STRONGLY SUPPORTED MCU header'),
        ('board_top_stm32.jpeg', 'STM32F745VEH6 marking visible', 'STM32 MCU on photographed board',
         'not a DSP debug controller or user-unit identity proof', 'VERIFIED image observation'),
        ('board_top_under_rf_shield_closer.jpeg', 'six through-hole pads beside DSP, one end square',
         'candidate worth later continuity identification; not a TAP label',
         'hidden layers and image detail prevent TCK/TMS/TDI/TDO package-to-pad tracing', 'UNRESOLVED connectivity'),
        ('board_top_full.jpeg', 'RF shield covers DSP region', 'shield/access may require disassembly',
         'no physical opening authorized; traces beneath package/shield not inferred', 'VERIFIED image observation'),
        ('local material inventory', 'prior project manuals and generated figures; no schematic established in inspected evidence',
         'package-to-board routing category E: impossible to determine with available imagery',
         'bounded project evidence review, not a claim no schematic exists anywhere', 'UNRESOLVED board routing')]]


def controllers():
    rows=[]
    def add(name,evidence,bp,regs,memory,stack,pipeline,dump_support,availability,practicality,rank):
        rows.append(dict(candidate=name,evidence=evidence,breakpoint=bp,registers=regs,XY_P=memory,
            hardware_stack_loop=stack,pipeline=pipeline,scriptable_dump=dump_support,
            availability_OS=availability,present_practicality=practicality,qualification_rank=rank,
            connection_qualified=False))
    add('NXP Symphony Studio + documented parallel/USB OnCE command-converter class',
        'Official product explicitly DSP56724/25 and custom GDB; DSPAUDIOEVM guide Sec1.2.1',
        'debugger advertised; exact hardware comparator behavior must qualify',
        'family/device debugger support documented','DSP memory debugger support; exact export qualify',
        'full active frames/raw extension export UNRESOLVED','PIL/PDB/PAB raw export UNRESOLVED',
        'custom GDB; automated complete raw bundle UNRESOLVED',
        'legacy 1.1.0 2008 ZIP 54.35MB/account; not downloaded; modern driver/OS unknown',
        'best documented exact-device vendor qualification candidate; no exact obtainable converter SKU qualified',1)
    add('OpenOCD dsp563xx backend + electrically qualified JTAG adapter (none chosen)',
        f'Pinned official source {COMMIT}; generic DSP563xx, not validated DSP56724 dual-TAP',
        'hardware comparator memory-P read/equal; one comparator available',
        '54 core regs including raw A/B slices; debug init changes SR/N0/N1/M0/M1',
        'X/Y/P read; 32-bit host containers masked24; R0/R1 temporarily changed',
        'SP/SC/LA/LC/EP/SZ and TOP SSH/SSL; no complete active-frame export',
        '25 OnCE cached regs incl PIL/PDB/PAB/12 flow; raw export not standard core reg file',
        'auditable commands/GDB; complete sparse bundle exporter not implemented',
        'source accessible; no local executable found; no build/install performed',
        'plain IR/DR scans and has_idcode requirement block unqualified dual-TAP use; per-target cache audit required',2)
    add('Lauterbach TRACE32 DSP56k + vendor-qualified controller/voltage adapter (none chosen)',
        'Official debugger_56000.pdf 2026; 563xx CPU list omits 56724/25; generic chain padding supported',
        'on-chip comparator documented; default program breakpoints are SOFTWARE/P writes',
        'family register support; exact 56724 unknown','family X/Y/P support; exact mapping qualify',
        'full raw active frames UNRESOLVED','all required raw latch export UNRESOLVED',
        'PRACTICE automation documented; complete raw bundle needs qualification',
        'current DSP56k-family products; actual DSP56724 support/SKU/availability unconfirmed',
        'commercial candidate only; LA7701 lacks multicore support; DE default and reset/auto writes need disable/qualification',3)
    add('Freescale Suite56 ads56300 + legacy parallel command converter',
        'DSPS56TOOLSUM Release6.3 (2000), 56300 hardware debugger',
        'family debugger advertised','family debugger advertised','family memory debugger advertised',
        'complete frames UNRESOLVED','raw pipeline UNRESOLVED','batch command files documented',
        'legacy parallel interface; modern drivers/dual56724 support not established',
        'legacy candidate, not an obtainable qualified pair',4)
    add('CodeWarrior-era converters / USB TAP branded hardware',
        'Symphony lists USB command converter class; no exact current SKU proven; 56800/E evidence not 56300',
        'UNRESOLVED','UNRESOLVED','UNRESOLVED','UNRESOLVED','UNRESOLVED','UNRESOLVED',
        'UNRESOLVED','brand/JTAG or DSC support alone insufficient',5)
    for name,evidence in [('P&E Micro','reviewed official current manuals/software; no positive DSP56300/56724 evidence'),
                          ('SEGGER J-Link','reviewed supported CPU architectures; no positive DSP56300/56724 evidence'),
                          ('generic FTDI/MPSSE JTAG adapter alone','can shift JTAG bits; does not supply DSP OnCE protocol/dual-chain semantics'),
                          ('community DSP emulator/disassembler in project','offline CPU/disassembly only; no physical OnCE acquisition backend established')]:
        add(name,evidence,'UNRESOLVED','UNRESOLVED','UNRESOLVED','UNRESOLVED','UNRESOLVED','UNRESOLVED',
            'not tested / no installation','not sufficient independently for this acquisition',6)
    add('DSPAUDIOEVM SDI USB/RS232 path',
        'guide Sec1.2.2 describes SPI/I2C real-time debug; distinct from Sec1.2.1 parallel OnCE',
        'not established OnCE','not established OnCE','not established OnCE','not established OnCE',
        'not established OnCE','not established OnCE','legacy EVM, not Circuit',
        'do not confuse SDI USB with OnCE controller or borrow EVM header pinout',6)
    return rows


def ranges(slot=0,group=0):
    if slot not in range(12) or group not in (0,1):
        raise ValueError('bounded selected profile only')
    q=0x57B+0x4A*slot; s=0x59F+0x28*slot
    return [('X mono + natural guard', 'X',0x2C46,0x2C67,'same-core generator9C6..9D8'),
            ('X post fields','X',q+0x30,q+0x38,'ARM SHI parameter ISR + same-core updates'),
            ('X post gain fields','X',q+0x40,q+0x43,'ARM SHI parameter ISR + same-core ramp'),
            ('Y post retained state','Y',s+0x0C,s+0x1A,'same-core post loop; possible indirect SHI writes require exclusion'),
            ('selected group mix','X',0x2DF0 if group==0 else 0x2E50,
                0x2E10 if group==0 else 0x2E70,'same-core earlier voice accumulation')]


def coherence_rows():
    rows=[]
    for name,space,start,end,writer in ranges():
        rows.append(dict(range=name,address_example_slot0=f'{space}:[0x{start:X},0x{end:X})',
            words=end-start,writer=writer,core_halt='ordinary same-core execution stops; debug GO IRQ behavior must qualify',
            peer='low internal RAM is core-private under captured valid OMR; shared region is [30000,38000)',
            DMA='halt is not proof of DMA freeze; exclude every active address/modulo domain',
            host='SPI/SHI FIFO may continue; ordinary ISR stopped but debug injections must exclude IRQ',
            requirement='document private mapping + DMA exclusion + no injected IRQ + pre/post epoch consistency',
            status='CONDITIONAL writer ownership; coherence UNRESOLVED'))
    for name,space,addresses in [('X globals','X','CC 39 3A 3B 40'),('Y globals','Y','7 10 19 1A 1C')]:
        rows.append(dict(range=name,address_example_slot0=f'{space}: {addresses}',words=5,
            writer='same core init/runtime; parameter/interrupt changes must be excluded',
            core_halt='ordinary same-core instructions stop, not guaranteed all writers',
            peer='private only with memory map corroborated',DMA='address-domain exclusion required',
            host='queued SHI and forced-instruction IRQ behavior unresolved',
            requirement='include same epoch and raw cursor/bank cross checks',status='UNRESOLVED writer exclusion'))
    for name,addresses,words,writer in [
        ('optional coefficient table','X:[1600,1940)',832,'ARM upload through same-core SHI / initialization'),
        ('conditional normalization domain','X: pointer from Y1C + M5',512,'table publisher/initialization; actual domain depends modifiers'),
        ('DSP register / stack / pipeline','raw architecture; not 100 memory words',0,'debugger forced instructions change latches/registers/stack'),
        ('ARM patch / bank / project','actual observed pointers only',0,'ARM CPU, caches, DMA, queued host changes'),
        ('peripherals / shared memory','SHI/ESAI, DMA and [30000,38000)',0,'peripherals/DMA/other core may run while selected core halted')]:
        rows.append(dict(range=name,address_example_slot0=addresses,words=words,writer=writer,
            core_halt='does not by itself prove epoch',peer='peer halt or bounded exclusion if relevant',
            DMA='observe non-destructively only after register side effects qualified; no guessed freeze bit',
            host='ARM halt does not cancel in-flight SPI/DMA or flush cache',
            requirement='capture or independently prove immutable matching epoch; refuse if ownership/race unknown',
            status='UNRESOLVED / CONDITIONAL'))
    return rows


def source_guards():
    paths = [ROOT/'original/circuittracks-firmware-4486.syx',
             ROOT/'firmware/circuittracks-firmware-4486.bin',
             ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin', RM, FM,
             ROOT/'builds/phase3-selection0-channel0.asm']
    paths += sorted(p for directory in [ROOT/'original', ROOT/'firmware']
                    for p in directory.rglob('*') if p.is_file() and p not in paths)
    paths += sorted(p for p in SRC.rglob('*') if p.is_file())
    paths += sorted(p for p in PREVIOUS.rglob('*') if p.is_file())
    prior=ROOT/'builds/phase20b-sequence'
    if prior.exists(): paths += sorted(p for p in prior.rglob('*') if p.is_file())
    paths += [Path(__file__).resolve()]
    for name in ['tools/ct_tapqual_verify.py','emulator/tests/test_tapqual.py',
                 'tools/ct_snapshot_design.py','tools/ct_snapshot_design_verify.py']:
        if (ROOT/name).exists(): paths.append(ROOT/name)
    return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}


def document_evidence(out):
    result=[]
    for path,pages in [(RM,[48,49,50,51,52,74,75,76,77,78,118,119,457,458,459,460]),
                       (FM,[96,97,136,137,138,139,140,141,142,143]),
                       (SRC/'debugger_56000.pdf',[5,14,15,16,19,24,25])]:
        reader=PdfReader(path)
        for n in pages:
            text=reader.pages[n-1].extract_text()
            name=f'{path.stem}-pdf{n:03}.txt'
            (out/name).write_text(text,encoding='utf8',newline='\n')
            result.append(dict(source=path.relative_to(ROOT).as_posix(),source_sha256=sha(path),
                pdf_page=n,excerpt=name,excerpt_sha256=sha(out/name)))
    dump(out,'document-pages.json',result)
    markers={
        'dsp563xx.c':['static struct once_reg once_regs[]','if (!target->tap->has_idcode)',
            'static int dsp563xx_debug_init','sr &= ~(DSP563XX_SR_SA | DSP563XX_SR_SC)',
            'static int dsp563xx_save_context','static int dsp563xx_add_breakpoint'],
        'dsp563xx_once.c':['jtag_add_plain_dr_scan','jtag_add_plain_ir_scan'],
        'board-README.md':['DSPB56724AG'],
        'board-debugHeader.svg':['SWDIO','SWCLK']}
    locators=[]
    for name,needles in markers.items():
        lines=(SRC/name).read_text(encoding='utf8').splitlines()
        for needle in needles:
            hits=[(i,line.strip()) for i,line in enumerate(lines,1) if needle in line]
            if not hits: raise AssertionError(f'Missing documentary anchor: {name}: {needle}')
            for i,line in hits:
                locators.append(dict(source=name,line=i,anchor=needle,text=line))
    dump(out,'source-locators.json',locators)
    listing=(ROOT/'builds/phase3-selection0-channel0.asm').read_text()
    selected=[]
    for line in listing.splitlines():
        m=re.match(r'P:([0-9A-F]{6})\s+([0-9A-F]{6})',line)
        if m and (int(m[1],16)==0x100 or 0x9D8<=int(m[1],16)<=0x9E0): selected.append(line)
    if not any('P:0009DC  000000' in line for line in selected): raise AssertionError('9DC NOP absent')
    if not any('P:0009DD  56D800' in line for line in selected): raise AssertionError('9DD signature absent')
    dump(out,'program-signatures.json',dict(source='builds/phase3-selection0-channel0.asm',
         payload_sha256=sha(ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin'),
         lines=selected,status='VERIFIED offline listing; future P read must compare original loaded words'))


def reports():
    electrical=dict(status='CONDITIONAL package specification; actual board voltage UNRESOLVED',
        IO_VDD='3.3 V nominal; EC operating range 3.14..3.45 V',
        CORE_VDD='different power domain; not probe reference; actual grade qualify',
        five_volts='EC VIH maximum VIO+2 and absolute VIN maximum5.5 do not categorically exclude silicon tolerance; not permission for 5V probe or board drive',
        target_power='target powered normally; probe supply to target disabled; no back-power; adapter must accept actual Vref',
        ground='actual signal ground continuity and pin orientation mandatory',
        reset='RESET resets both DSP cores and re-latches modes; never use reset for natural seam capture',
        clock='EC Table13 maximum min(10 MHz,Fsys/3); min cycle100ns, pulse50ns, rise/fall<=3ns; TMS/TDI setup5ns/hold25ns; TDO valid44ns. Initial board-safe TCK not established.',
        pulls='internal TCK/TMS/TDI pull-ups; TDO tri-state outside scan. Board pulls/loading unknown.',
        minimum_preconnection_checks=['actual part/package/revision/orientation','powered-off net/ground continuity (future separately authorized)',
            'actual I/O Vref and controller input/output compatibility (future authorized measurement)',
            'target/probe power isolation, reset/TRST/DE mapping and automatic behavior',
            'TAP topology and driver clock constraints','controller startup has no reset, target-memory patch, clock/PLL/watchdog/COP/cache writes'])
    identity=dict(status='STRONGLY SUPPORTED photographed-board DSPB56724AG; actual user unit UNRESOLVED',
        photographed_board='Circuit Rhythm/Tracks MAIN BOARD V3.2 FP002099-01 (2020)',
        part='DSPB56724AG',package='144-pin LQFP 20x20mm 0.5mm pitch (EC Table19)',
        silicon_mask='UNRESOLVED',actual_unit='UNRESOLVED; no actual-unit inspection',
        alternative_package='DSP56725 80-pin documented for comparison; not selected by firmware inference alone',
        cores=2,core_architecture='DSP56300',per_core_OnCE=True,
        firmware_evidence='stock DSP56300 instruction/SHI behavior established earlier; upload channel not proof physical core identity',
        sources=['board-README.md','board_top_under_rf_shield_closer.jpeg','RM Chapter2/22','EC Table19'],electrical=electrical)
    architecture=dict(status='VERIFIED documentation; CONDITIONAL unit',
        chain='external TDI -> JTAG1 / core1 -> JTAG0 / core0 -> external TDO',IR_bits=[4,4],combined_IR_bits=8,
        JTAG0_instructions=dict(ENABLE_ONCE=6,DEBUG_REQUEST=7,BYPASS=15),
        JTAG1_instructions=dict(EXTEST=0,SAMPLE_RELOAD=1,IDCODE=2,CLAMP=3,HI_Z=4,ENABLE_ONCE=6,DEBUG_REQUEST=7,BYPASS=15),
        JTAG1_documented_IDCODE='0x01ED001D',JTAG0_IDCODE=False,
        OnCE_path='select ENABLE_ONCE in selected TAP, BYPASS other TAP; correctly padded IR/DR -> OnCE command/data registers -> core forced instruction/OGDB read',
        core_selection='serial IR instructions, not dedicated board pins; configurable coupled debug entry',
        controller_requirement='electrically qualified JTAG bit engine PLUS DSP56k-specific OnCE protocol, chain and raw-state handling',
        TRST='RM22 describes internal controller reset from on-chip POR; no external package TRST listed',
        prohibitions='no boundary EXTEST/HI_Z/SAMPLE drive sequence, reset or debug request issued in this phase')
    breakpoint=dict(status='VERIFIED manual retirement semantics; CONDITIONAL actual halt state',
        comparator='program fetch/execute match at P:0x9DC, hardware comparator ONLY; no software patch',
        matching_instruction='P:0x9DC = 000000 NOP',acknowledgement='after matching instruction executes (FM7.2.4)',
        expected_next='P:0x9DD only with no intervening interrupt/exception or coupled debug delay changing boundary',
        expected_PABEX='0x9DD would-execute address',expected_PIL='0x56D800 at expected P:0x9DD; verify raw latch',
        PABFR_PABDR_PDB='capture raw addresses/opcode; depend on pipeline state. No fabricated fixed values.',
        mono='all32 samples X[2C46,2C66) and natural guard X2C66 completed; 9DD not retired',
        DO='local generator loop completed at9D8; inherited LF/FV/stack frames may remain. Do not force LF=0,SP=0.',
        SR_stack='NOP changes neither SR nor stack; breakpoint debug entry, interrupts and injected inspection require separate audit',
        first_dump=['raw OnCE status/configuration and PIL/PDB BEFORE injected GO',
            'PABFR/PABDR/PABEX and all12 flow entries (complete cycle to preserve pointer)',
            'original SR/OMR, SP/SC/LA/LC, EP/SZ where enabled before destructive walk',
            'raw A2:A1:A0 and B2:B1:B0; raw R/N/M and data regs before using scratch',
            'SSL before SSH per frame; initial stack controls recorded and exact walk/restore qualified'],
        PC_warning='GUI/GDB PC reconstruction not sufficient boundary evidence',
        normalization='preserve raw9DD bundle; replay9D9 only under Phase20B6 rule (R0=Y7, unchanged prefix, no intervening IRQ/writer). Not cycle/pipeline equivalence.',
        unresolved=['exact controller full-frame walk/restoration','injected GO interrupt eligibility','OGDB XFFFFFC/YFFFFFC manual map inconsistency'])
    core=dict(status='DESIGN ONLY; physical core mapping UNRESOLVED',
        sequence=['qualify full dual-TAP chain without expecting IDCODE on JTAG0',
            'preserve raw debug/pipeline/state before any injection/halt side effects',
            'read CHIDR XFFFFF5 with qualified access:724 core0=000724 core1=010724 (725 analogues)',
            'compare immutable original P100 and P9D8..9E0 signatures, plus loaded-image coverage/hash where possible',
            'observe halted core raw PABEX/PIL and actual slot cursors at natural9DC match',
            'record core/TAP association and coupled-debug configuration; do not infer channel0=core0'],
        resets=False,PC_forcing=False,P_writes=False,program_signature_file='evidence/program-signatures.json',
        mapping_condition='CHIDR, P signatures and natural execution agree; ambiguity refuses capture',
        per_core_state='independent cache and OnCE latch preservation required; no shared global-latch overwrite')
    exclusion=dict(status='UNRESOLVED coherent acquisition; conditional design only',
        snapshot_words=100,selected_profile='routing0/nonlinear1/offsets5/5, independently observed',
        no_universal_order=True,
        DSP_first='seam state captured first, but ARM patch/queues may change before ARM halt; epoch mismatch unless excluded',
        ARM_first='changes host timing; in-flight SPI/DMA/SHI may continue; DSP can advance; not proof natural provenance',
        dual_DSP='documented coupled debug possible; does not freeze ARM or DMA/peripherals',
        preferred_conditional_scope='only private low X/Y owned by halted synth core, with ALL DMA destinations excluded and injected-IRQ exclusion proven; ARM provenance requires independently coherent publication epoch',
        prerequisites=['capture OMR and prove required ranges private/mapped','qualify halt and injected-instruction IRQ behavior',
            'exclude active DMA address/count/modulo coverage of every range, including peer-triggered ownership',
            'qualify pending SHI jobs and ARM SPI/DMA queues; do not drain by unrecorded firmware calls',
            'capture raw registers first and avoid reading destructive MMIO during ownership checks',
            'freeze/exclude ARM patch writers and observe publication/version/queue state from actual roots',
            'pre/post read equality is supplementary: not sufficient against ABA or unobserved writes'],
        abort='refuse snapshot if any required writer or epoch is unresolved; no guessed freeze register',
        DMAS='DMA stall interrupt threshold, not a freeze bit',
        physical_operations_performed=0)
    correlation=dict(status='CONDITIONAL design; actual runtime roots/epoch UNRESOLVED',
        model_formula='model = [view+0x344+4*bank] at ARM0x0803BE60; view root must be observed, never invented',
        data_formula='model+0x0C points to pointer cell, then actual byte buffer; model+0x10 length; require observed340 bytes (ARM3BBE8/3BC06)',
        snapshot_fields=['raw ARM registers at coherent halt','view/model/pointercell/buffer addresses with pointer chain bytes',
            'exact340 active bytes + SHA256 + observed length','logical bank and actual event/track/slot identity',
            'project identity from actual reachable runtime metadata, not cached project0 association',
            'publication state/pending queues/caches and halt order log','optional active correction data ARM20005C28+0x8C*bank (140bytes)'],
        slot_validation='solve i independently: Y7=57B+4A*i+30 and R4=59F+28*i+0C; require same integer i in0..11',
        group_validation='XCC selects group buffer; logical synth/track requires independent runtime correspondence',
        cache='debugger RAM view may differ from Cortex-M7 cache; qualify coherent RAM view without unrecorded clean/invalidate writes',
        forbidden_shortcuts=['no firmware getter call','no arbitrary root address','no cached project association as active proof','no inferred audible patch identity from numeric DSP state'])
    physical=dict(status='READY-FOR-PIN-VERIFICATION',scope='candidate six-pad footprint on documented public board ONLY',
        exposed_TAP_verified=False,routing_class='E: package-to-pad connections impossible to determine from available imagery',
        actual_unit='UNRESOLVED revision/identity',connection_justified=False,
        electrical=electrical,security='unit debug accessibility/lock state UNRESOLVED; MCU option bytes do not qualify DSP',
        future_pin_session_justified=True,future_pin_session_authorized=False)
    tooling=dict(status='PLAUSIBLE TOOLCHAIN',qualified_pair=None,
        preferred_vendor_qualification='NXP Symphony Studio + documented DSP56724 OnCE command-converter class; exact SKU/drivers/raw export must qualify',
        preferred_auditable_candidate='OpenOCD DSP563xx source + qualified adapter; dual-chain and raw export adaptation required before use',
        blocker=['plain IR/DR scans not chain-aware as supplied','JTAG0 no-IDCODE conflicts OpenOCD examine requirement',
            'raw OnCE cache global across instances; isolation audit','automatic SR/N/M alterations and comparator clearing',
            'only top SSH/SSL, not full inherited stack capture','exact electrical adapter/reset/auto-write behavior unknown'],
        external_OnCE_preferred=True,hook_preferred=False,
        rationale='OnCE not shown impractical; conditional no-firmware-patch path still ranked first',
        connection_justified=False,flashing_justified=False,download_or_install=False)
    connection_unknowns=['target debug voltage','ground reference','TAP identity/connectivity','controller electrical compatibility',
        'DSP reset consequences and no-reset entry mode','debugger automatic initialization/target memory writes']
    session=dict(status='DESIGN ONLY; no actions authorized by this report',
        connection_refusal_if_unknown=connection_unknowns,snapshot_refusal_if_unknown=['raw-state preservation','all required writer exclusion','ARM/DSP epoch correlation'],
        stages=[
            dict(stage=1,action='Separately authorized board inspection/powered-off pin verification; identify actual part/revision, ground and TAP routes',gate='this phase only specifies, does not authorize'),
            dict(stage=2,action='Separately authorized electrical qualification; actual Vref/power isolation/reset/clock/loading',gate='all connection unknowns resolved'),
            dict(stage=3,action='Bench-qualify chosen controller script with no auto memory patches/reset/init, raw pipeline/stack save and dual-chain support',gate='not qualified here; hardware breakpoint mode explicit'),
            dict(stage=4,action='Power target normally and attach only qualified target-referenced probe with probe target supply disabled under agreed power sequence',gate='separate authorization and adapter connection requirements; no assumed hot-plug permission'),
            dict(stage=5,action='Enumerate both TAPs and identify core by CHIDR/P signatures using saved state',gate='no reset/EXTEST/HI_Z/PC forcing/firmware writes; preserve original halt side effects'),
            dict(stage=6,action='Configure hardware-only P9DC breakpoint; run naturally and validate raw9DD retirement boundary',gate='qualification halt/setup disturbance logged; no P-word patch'),
            dict(stage=7,action='Capture raw OnCE/pipeline and original architectural state first',gate='no injection before preserving destructive latches; full stack procedure qualified'),
            dict(stage=8,action='Establish previously proven writer exclusion and epoch before memory/provenance reads',gate='no universal ARM/DSP halt ordering chosen; refuse on any race'),
            dict(stage=9,action='Export100-word selected sparse state, actual tables where necessary, correlated ARM340 bytes/bank/slot/project',gate='pre/post consistency supplementary; canonical24bit words, raw regs/logs retained'),
            dict(stage=10,action='Validate bundle offline; restore transient debug/register configuration only under qualified procedure and disconnect per adapter rules',gate='no target firmware/memory changes; documented debug-state writes/injected instructions remain real perturbations')],
        dynamic_capture=False,probe_attachment=False,firmware_writes=False,
        caveat='Literal zero target writes would rule out breakpoint configuration and injected debug reads. Goal is no firmware/memory patch; all debug/register side effects must be explicit.',
        next_step='separately authorize limited powered-off actual-board identification/continuity verification of candidate footprint, before any probe attachment')
    return {'dsp-identity.json':identity,'tap-architecture.json':architecture,
        'breakpoint-state.json':breakpoint,'core-identification.json':core,
        'writer-exclusion.json':exclusion,'patch-correlation.json':correlation,
        'physical-readiness.json':physical,'tooling-readiness.json':tooling,
        'future-session-plan.json':session}


def web_evidence():
    return [dict(url=url,locator=locator,findings=facts,archive=archive,
        consulted='2026-10-07',status='VERIFIED documentation; applicability qualified separately')
        for url,locator,facts,archive in [
        (DOC_URL,'Rev2 Table19, Table4 electrical, Table13 JTAG timings',
         'DSPB56724AG144LQFP; nominal3.3V I/O; JTAG clock/edge/input constraints',
         'web cached text; direct vendor fetch404; no full local EC PDF claimed'),
        (SYMPHONY_URL,'product features and downloads',
         'explicit DSP56724/25; custom GDB; USB/parallel converters; legacy54.35MB ZIP not fetched',
         'web text; direct fetch404; no local IDE archive'),
        ('https://www.nxp.com/docs/en/user-guide/DSP56720DBUG.pdf','Rev4 Sec1.2.1/1.2.2 and external OnCE P2',
         'OnCE parallel converter distinct from SDI USB/RS232 SPI/I2C debugging; EVM header is not Circuit pinout',
         'web cached text; direct404'),
        ('https://www.nxp.com/docs/en/supporting-information/DSPS56TOOLSUM.pdf','Release6.3 hardware debugger/batch',
         'legacy56300 debugger/parallel converter; no exact dual56724 qualification', 'web cached text; direct404'),
        ('https://www2.lauterbach.com/pdf/debugger_56000.pdf','PDF14/15/16/19/24/25',
         'software breakpoint default; CPU list lacks56724; chain padding; no-reset attach distinction; DE and COP behavior',
         'full PDF archived and hashed'),
        (OPEN_URL+'dsp563xx.c','source-locators.json plus c947..1021,2063',
         'raw latch cache, register mutation, IDCODE assumption, comparator path', 'full pinned source archived and hashed'),
        (OPEN_URL+'dsp563xx_once.c','lines42/76',
         'plain DR/IR scan helpers do not pad companion TAP automatically', 'full pinned source archived and hashed'),
        ('https://www.segger.com/products/debug-probes/j-link/technology/cpus-and-devices/overview-of-supported-cpus-and-devices/',
         'CPU architecture table','no positive56300/56724 support evidence in reviewed page','HTML archived'),
        ('https://www.pemicro.com/manuals/','current manual list','no positive56300/56724 support evidence in reviewed page','HTML archived'),
        (BOARD_URL,'README, Documentation/Mainboard-Photos and Diagrams/debugHeader.svg',
         'public revision/component/footprint evidence; no continuity proof', 'four photos + J3 + diagram + README + tree archived')]]


def build(out):
    out=out.resolve()
    if out.exists() or out==BASE or not out.is_relative_to(BASE) or out.is_relative_to(SRC):
        raise ValueError('A fresh report child under builds/phase20b-tapqual is required')
    before=source_guards()
    expected={'original/circuittracks-firmware-4486.syx':'bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd',
        'firmware/circuittracks-firmware-4486.bin':'b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da',
        'firmware/dsp/build-4486/selection0-channel0.payload24.bin':'b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855'}
    assert all(before[p]==h for p,h in expected.items())
    out.mkdir(parents=True)
    evidence=out/'evidence';evidence.mkdir()
    document_evidence(evidence)
    for name,data in reports().items(): dump(out,name,data)
    table(out,'tap-pins.csv',pin_rows())
    table(out,'board-evidence.csv',board_rows())
    table(out,'controller-support.csv',controllers())
    table(out,'coherence-writers.csv',coherence_rows())
    table(out,'header-comparison.csv',[
        dict(header='J3 Programming Debug',observed='10 pads; author SWDIO/SWCLK/GND map',
            classification='STRONGLY SUPPORTED STM32 SWD',discriminator='SWDIO/SWCLK to MCU, not DSP TDI/TDO/TMS/TCK',
            unresolved='actual unit/continuity, uncertain SWO/reset/resistor reference'),
        dict(header='six-pad footprint beside DSP',observed='six through-hole pads; no net labels proven',
            classification='UNRESOLVED candidate',discriminator='continuity to DSP101..104 plus valid IO_VDD/GND, orientation and no conflicting nets',
            unresolved='all nets; pin count/position alone insufficient')])
    dump(evidence,'web-evidence.json',web_evidence())
    assert before==source_guards(), 'Guarded sources changed'
    dump(out,'validation.json',dict(status='TESTED deterministic report/source consistency only',
        source_hashes=before,expected_original_hashes=expected,
        memory_words=sum(r['words'] for r in coherence_rows()[:7]),
        source_guard_unchanged=True,hardware_actions=0,firmware_changes=0,
        snapshot_acquired=False,CPU_execution=0,connection_gate='REFUSED',snapshot_gate='REFUSED',
        caveat='No measurements, actual controller tests, capture or board continuity. Reports are evidence-qualified design, not working hardware procedure.'))
    return out


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True,type=Path)
    args=parser.parse_args()
    build(args.output_dir)
