#!/usr/bin/env python3
"""Offline Phase 17 evidence ledger. Does not build/run an emulator or use devices."""
import argparse
import hashlib
import json
from pathlib import Path
from ct_static import ROOT, BIN_HASH, SYX_HASH
import ct_fw_tool

SOURCES = [
    ('DSP56724EC', 'https://www.nxp.com/docs/en/data-sheet/DSP56724EC.pdf',
     'Rev2; overview, Table19, package figures30/31',
     'Two DSP56300 cores; 56724 is144-pin LQFP, 56725 is80-pin LQFP. Table19 lists DSPB56724AG and DSPB56725AF, not reported56725AG.'),
    ('DSP56724RM', 'https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf',
     'Rev1; sections4.3.5,6.2.1,6.2.3; chapters13,22',
     'Per-core OnCE; two chained4-bit TAP instruction registers. Debug entry can couple cores. ICC is internal. CHIDR differentiates724/725; no measured ID.'),
    ('AN2073', 'https://www.nxp.com/docs/en/application-note/AN2073.pdf',
     'Rev1; sections4,5,11',
     'DSP56300 OnCE register access requires Debug mode and stops normal operation. SC140 EOnCE real-time features cannot be transferred to this family.'),
    ('AN1839', 'https://www.nxp.com/docs/en/application-note/AN1839.pdf',
     'Rev1; sections1.2..1.5,4.4,4.5,4.7',
     'Forced memory-read instruction uses OGDB; example incrementsR0. Breakpoint comparators/counter and trace counter enter Debug mode. Flow buffer has12x25-bit entries and reads advance pointer.'),
    ('DSP56300FM', 'https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf',
     'Rev5; chapter7, reused Phase16 findings; full PDF retrieval failed this phase',
     'Reused flow-history/pipeline inspection evidence; not a continuous X/Y effective-address/data trace.'),
    ('AN2074', 'https://www.nxp.com/docs/en/application-note/AN2074.pdf',
     'Rev1; boundary scan and SAMPLE/PRELOAD',
     'Pin snapshots are boundary scan, not private-memory observation; test modes can drive pins.'),
    ('CircuitTracksReverseEngineering', 'https://github.com/userx14/CircuitTracksReverseEngineering',
     'README master, retrieved2026-10-06; mutable public source',
     'First-party board research reports DSPB56724AG, SDRAM/latch, TC2050-compatible header and references J3 photo/debugHeader.svg; source files not successfully retrieved.'),
    ('Teardown discussion', 'https://www.reddit.com/r/novationcircuit/comments/1g6r35j/',
     '2024-10-18 post;2025-08-17 component comment visible in indexed result',
     'Reports Tracks/Rhythm mainboardV3.2 and DSPB56725AG; contradicts repository and datasheet marking. No inspected package photo/pad continuity.'),
    ('C++ emulator', 'https://github.com/dsp56300/dsp56300',
     'Local commit44353be2f0156cac970c6ab4f467ea1998b40605',
     'Pinned source has56362 SHI/ESAI/DMA models, configurable write callback paths; not an established56724 complete board model.'),
    ('Rust toolkit', 'https://github.com/mborgerson/dsp56300',
     'Local commitc60aeedb6a6014850204c71e53bc0cf5b3104222',
     'Pinned source has region callbacks/interrupt core; JIT buffer stores bypass generic write_memory. No validated56724 peripheral model recovered.')
]

FEATURES = [
    # feature, keeps normal core running, debug modification, RAM, registers/flow, audio safety, source
    ('X/Y/P memory inspection', 'NO documented procedure', 'YES OCR/OPDB/OGDB',
     'No target RAM store required by simple read; debugger scratch and peripheral effects depend on implementation',
     'YES injected instructions/pipeline; exampleR0 increments', 'NO strict gate', 'AN2073sec5;AN1839sec4.7'),
    ('Arbitrary architectural register inspection', 'NO documented procedure', 'YES',
     'No RAM store required by primitive; save strategy not established',
     'Debug mode/forced instruction, register-specific effects', 'NO strict gate', 'AN1839sec1.4;AN2073sec5'),
    ('Background arbitrary memory bus access', 'UNRESOLVED/none documented for candidate OnCE',
     'UNRESOLVED', 'UNRESOLVED', 'UNRESOLVED', 'UNRESOLVED, not usable', 'No documented qualifying facility'),
    ('Flow-history capture', 'YES internal capture during normal execution',
     'Hardware history changes; reading changes pointer/OCR', 'No program/dataRAM log required',
     'No capture instruction injection; documented retrieval enters debug', 'Capture only, no safe live retrieval proved', 'AN1839sec1.5;FM7.2.5'),
    ('Flow-history retrieval', 'NO documented debug procedure', 'YES pointer/OCR',
     'No targetRAM store required', 'Debug mode/pipeline interaction', 'NO strict gate', 'AN1839sec4.4/4.5'),
    ('Instruction stepping/trace counter', 'NO continuous execution; halts afterN', 'YES OTC/OSCR',
     'No targetRAM store required', 'YES debug entry/execution control', 'NO', 'AN1839sec1.3'),
    ('P/X/Y memory watchpoint/data breakpoint', 'NO on configured trigger', 'YES comparators/counter/status',
     'No software patch required', 'YES debug entry; cross-core coupling possible', 'NO', 'AN1839sec1.2;RM22'),
    ('Continuous effective X/Y address+value trace', 'UNRESOLVED/none documented', 'UNRESOLVED',
     'UNRESOLVED', 'UNRESOLVED', 'UNRESOLVED, not usable', 'Flow history/watchpoints do not provide it'),
    ('JTAG boundary pin sample', 'Potentially normal pin operation; not verified board-safe', 'YES TAP/BSR',
     'No privateRAM data access', 'Instruction-dependent; do not substitute EXTEST/CLAMP/HIZ',
     'UNRESOLVED electrical/mode safety', 'AN2074;RM22'),
    ('SC140 EOnCE real-time transfer', 'Inapplicable to candidate DSP56300 OnCE', 'Inapplicable',
     'Inapplicable', 'Inapplicable', 'Not a candidate feature', 'AN2073sec5')
]

METHODS = [
    ('Targeted static analysis', 'PARTIAL EVIDENCE ONLY until universal domains closed',
     'PROOF possible only with complete writer/state closure; currently PARTIAL EVIDENCE',
     'No hardware risk', 'Low/moderate; broad census diminishing returns', 'None'),
    ('OnCE memory/register reads', 'PARTIAL EVIDENCE ONLY; halted snapshot not everyentry',
     'PARTIAL EVIDENCE; snapshots miss same-value/transient writes',
     'Fails nohalt gate', 'Moderate/high; board access unknown', 'High execution/debug-state disturbance'),
    ('OnCE write watchpoints', 'PARTIAL EVIDENCE ONLY; detects modeled comparator event, no loadvalue history',
     'PARTIAL EVIDENCE on access, halts on event; no universal noevent proof',
     'Fails nohalt gate', 'High board/debug validation', 'Debug entry and possible dualcore halt'),
    ('OnCE flow history', 'PARTIAL EVIDENCE ONLY for PCflow, NOT USEFUL for countvalue alone',
     'NOT USEFUL for effective X/Y writes alone',
     'Retrieval fails gate', 'High with shallow history', 'Debug entry and pointer changes'),
    ('Passive SPI2 capture', 'PARTIAL EVIDENCE ONLY for host producers; not internal values at203A',
     'PARTIAL EVIDENCE for host traffic only',
     'Future input-only sniffing may be lower risk; pads/loading unresolved', 'Moderate', 'Electrical loading/timing risk, no commands conceptually'),
    ('Passive ESAI capture', 'NOT USEFUL for direct count invariant',
     'NOT USEFUL for privateRAM ownership', 'Pads/loading unresolved', 'Moderate', 'Loading; output behavior only'),
    ('ICC/shared bus external capture', 'NOT USEFUL for privateRAM under recovered topology',
     'NOT USEFUL for privateRAM; ICC/shared memory internal',
     'No established accessible bus', 'Not presently feasible', 'ExternalEMC not internalICC'),
    ('GPIO handshakes capture', 'PARTIAL EVIDENCE ONLY for event timing, not value',
     'NOT USEFUL for ownership alone', 'Pads/loading unresolved', 'Low/moderate', 'Loading, no internal data'),
    ('Offline emulator with complete write/entry instrumentation',
     'SUFFICIENT for executed model traces; universal stock invariant UNRESOLVED',
     'STRONG EMPIRICAL EVIDENCE for validated modeled scenarios; PROOF only exhaustive justified model',
     'No hardware risk', 'Moderate targeted, high complete boardmodel', 'Model error, no stock hardware disturbance'),
    ('Instrumented custom firmware', 'PARTIAL EVIDENCE ONLY for altered execution unless fidelity justified',
     'STRONG EMPIRICAL EVIDENCE possible for modified scenarios, never automatic stockPROOF',
     'Rejected in current scope', 'High', 'Timing/RAM/logging/placement/recovery Heisenberg effects')
]

WITNESSES = [
    ('builds/vendor/dsp56300/source/dsp56kEmu/peripherals.h', 'class Peripherals56362', 17),
    ('builds/vendor/dsp56300/source/dsp56kEmu/shi.h', 'Serial Host Interface of the DSP56362', 11),
    ('builds/vendor/dsp56300/source/dsp56kEmu/shi.cpp', 'void SHI::injectReceiveInterrupt', 19),
    ('builds/vendor/dsp56300/source/dsp56kEmu/jitconfig.h', 'memoryWritesCallCpp', 5),
    ('builds/vendor/dsp56300/source/dsp56kEmu/jitmem.cpp', 'if(m_block.getConfig().memoryWritesCallCpp', 8),
    ('builds/vendor/dsp56300/source/dsp56kEmu/jitmem.cpp', 'The parallel X:Y write did not honour', 12),
    ('builds/vendor/dsp56300/source/dsp56kEmu/memory.cpp', 'bool Memory::dspWrite', 18),
    ('builds/vendor/dsp56300-rust/crates/emu/src/core.rs', 'pub enum RegionKind', 24),
    ('builds/vendor/dsp56300-rust/crates/emu/src/core.rs', 'pub fn write_memory', 29),
    ('builds/vendor/dsp56300-rust/crates/emu/src/emit/mem.rs', 'pub(super) fn write_mem(', 18),
    ('builds/vendor/dsp56300-rust/crates/emu/src/emit/mem.rs', 'pub(super) fn write_mem_dyn(', 28),
    ('builds/vendor/dsp56300-rust/crates/emu/Cargo.toml', '[dependencies]', 12),
]

def digest(data): return hashlib.sha256(data).hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir', required=True)
    out = Path(ap.parse_args().output_dir).resolve()
    if out.exists(): raise SystemExit('Choose a fresh output directory')
    if ROOT/'original' == out or ROOT/'original' in out.parents: raise SystemExit('Protected original/')
    out.mkdir(parents=True)
    hashes = {}
    def read(name):
        raw = (ROOT/name).read_bytes(); hashes[name] = digest(raw); return raw
    def emit(name, value):
        with (out/name).open('x', encoding='utf-8') as f:
            json.dump(value, f, indent=2, sort_keys=True); f.write('\n')
    syx_path = ROOT/'original/circuittracks-firmware-4486.syx'
    arm = read('firmware/circuittracks-firmware-4486.bin')
    syx = read('original/circuittracks-firmware-4486.syx')
    assert digest(arm) == BIN_HASH and digest(syx) == SYX_HASH
    assert ct_fw_tool.decode_syx(syx_path)['firmware'] == arm
    assert ct_fw_tool.build_syx(syx_path, arm) == syx
    manifest = json.loads(read('firmware/dsp/build-4486/manifest.json'))
    for block in manifest['blocks']:
        for kind in ('stream', 'payload'):
            name = 'firmware/dsp/build-4486/'+block[kind+'_file']
            assert digest(read(name)) == block[kind+'_sha256']
    for name in ['notes/dsp-memory-map.md', 'notes/dsp-command-map.md',
                 'builds/phase16/final/read-side-effects.json',
                 'builds/phase16/final/safety-gate.json', 'builds/phase15/verified/cursors.json']:
        # Phase15 filename is optional; core evidence is otherwise required.
        if (ROOT/name).exists(): read(name)
    evidence = []
    for name, needle, count in WITNESSES:
        text = read(name).decode('utf-8')
        lines = text.splitlines()
        start = next(i for i, line in enumerate(lines) if needle in line)
        evidence.append({'path': name, 'first_line': start+1,
                         'lines': lines[start:start+count], 'SHA256': digest(text.encode('utf-8'))})
    emit('local-source-witnesses.json', evidence)
    emit('citations.json', [{'id': a, 'url': b, 'locator': c, 'finding': d,
                            'review_date': '2026-10-06', 'scope': 'document/source reading only'}
                           for a,b,c,d in SOURCES])
    emit('feature-matrix.json', [dict(zip(('feature','normal_execution_continues','debug_state',
          'program_data_RAM','stack_register_flow','real_time_audio_safe','source'), row)) for row in FEATURES])
    emit('mechanism-sufficiency.json', [dict(zip(('mechanism','X35F','high_X','safety','effort','behavior_risk'), row)) for row in METHODS])
    emit('silicon-and-board.json', {
        'DSP56300_payload': 'VERIFIED from prior bytechecked disassembly',
        'exact_part': 'STRONG HYPOTHESIS DSPB56724AG, unresolved actual unit/revision',
        'support': 'Firmware external-memory domains plus firstparty repo56724/SDRAM/latch report',
        'conflict': 'Indexed teardown comment56725AG; Table19 lists56725AF, notAG; no marking/photo verified',
        'conditional_package': '56724:144-pin20x20mm LQFP;56725:80-pin14x14mm LQFP',
        'conditional_cores': 'two24-bit DSP56300 cores; OnCE percore, not SC140 EOnCE',
        'conditional_TAP': 'two4bitIR chained; configurable debug coupling; no scan performed',
        'board_access': 'SOURCE-DERIVED TC2050-compatible debugheader report/J3 photo reference; exact numbered pinout not retrieved; DSP padsUNRESOLVED',
        'public_photos': ['https://github.com/userx14/CircuitTracksReverseEngineering/blob/master/Documentation/Mainboard-Photos/j3_debug_port.png'],
        'public_diagram': 'https://github.com/userx14/CircuitTracksReverseEngineering/blob/master/Documentation/Diagrams/debugHeader.svg',
        'fetch_limit': 'web could readREADME, not directory/diagram/photo; shell network denied; no undocumented pad guesses',
        'passive_SPI': 'logical SPI2/SHI link verified; reported PC1MOSI/PC2MISO/PD3SCK, no probe pads/net continuity established',
        'ICC': 'internal onchip, not a board signal bus; externalEMC if present doesnot expose privateRAM traffic'})
    emit('offline-emulator-gap-map.json', {
        'status': 'ASSESSMENT ONLY; no emulator built/run, no instrumentation implemented',
        'available_sources': ['C++44353be2f0156cac970c6ab4f467ea1998b40605', 'Rustc60aeedb6a6014850204c71e53bc0cf5b3104222'],
        'available_inputs': 'P payloads/loadrecords, reviewed bootclear/tablecopies/cursors, handlerPCs and hostprotocol',
        'not_sufficient_stock_state': 'full X/Y+register state, ROM/external tables, dualcore/shared map, pending interrupts, mailbox/DMA, host event ordering and transitions missing',
        'CPP': '56362SHI/ESAI/DMA and interrupt entry exist; need56724 mapping/ICC/dualcore/EMC validation. memoryWritesCallCpp routes reviewed single/parallel stores; complete accesscoverage andPC attribution not certified',
        'Rust': 'memoryregion callbacks/interrupt core; inline bufferstores bypasswrite_memory. callbacks for allRAM or emitter hooks require review, no claim oneAPI logsallwrites',
        'instrumentation_requirements': ['log everyeffective X/Y/P access inclsamevalue/parallelL writes',
             'log countload at203A and effective1F97 writes withcaller/register/modifier context',
             'coverCPU,JIT,DMA,ICC,shared aliases,externalmap/host producers',
             'explicit undefinedmemory/missingperipheral failure, never silentlyzero/ignore',
             'ISA/AGU/modulo/interrupt fixtures and independentdecoder/reference validation'],
        'narrow_scope': 'first isolated1F97/203A state-transition coverage specification; not fullaudio or synth emulation',
        'proof_limit': 'modeltrace witness isconditional, finite absence isnotstockproof; universalclosure needscomplete justified inputs/transitions or formal domains',
        'dependency_limit': 'RustJIT usesCranelift; no newlarge dependenciesinstalled, no existingemulator/difftestCLI executed'})
    emit('method-ranking.json', {
        'recommended_order': ['E offline emulator readiness/coverage audit', 'A targeted static premises',
                              'D passiveSPI conditionalfuturecorrelation', 'C existingflowhistory only',
                              'B OnCE snapshot/watchpoint', 'F customfirmwareinstrumentation'],
        'ranking_meaning': 'combined usefulness/safety, not hardware authorization; A safest/least effort, E highest offline causal potential',
        'future_firmware_risks': ['unproved P placement/overlays andrelocation', 'ISR/audio cycle budget and pipeline/register preservation',
             'no proven persistent X/Y logallocation', 'extra logtransportchangesSHI/mailbox timing',
             'observerchanges canhide/create aliases', 'rollback/bootloader recoveryunverified'],
        'future_firmware_status': 'conceptualonly; prohibited now, not evidence of stock safety'})
    emit('safety-gate.json', {
        'A_documented_nonhalting_state_preserving_memoryread': 'NO for documented candidateOnCE',
        'B_documented_sufficient_XY_write_trace': 'NO for reviewed facilities',
        'C_board_access_to_qualifying_facility': 'NOT-YET-DETERMINED',
        'D_passive_SPI_can_close_invariant': 'NO',
        'E_offline_emulator_plausibly_can_close': 'YES conditionally for modeledalias traces; stockproof remainsUNRESOLVED',
        'F_hardware_remain_disconnected': 'YES',
        'X35F_invariant': 'NOT-YET-DETERMINED', 'high_X_normal_availability': 'NOT-YET-DETERMINED',
        'service_robust': 'NO', 'hardware_action': 'NONE authorized/recommended',
        'best_next_step': 'static emulator-coverage/readiness specification for minimal1F97/203A replay, includingcomplete effectivewrite observability andevent/initialstate gaps; no build/run yet'})
    for name, h in hashes.items(): assert digest((ROOT/name).read_bytes()) == h
    emit('validation.json', {'inputs_SHA256': hashes, 'script_SHA256': digest(Path(__file__).read_bytes()),
          'baseline_hashes_match': True, 'extract_hashes_match': True, 'decoded_equals_BIN': True,
          'SYX_roundtrip_equal': True, 'local_source_needles_verified': True,
          'mode': 'RESEARCH+STATIC ONLY; no deviceaccess, emulator execution, firmware modifications'})

if __name__ == '__main__': main()
