"""Offline Phase19B-SYMBOLIC export. No arbitrary handoff concrete assignments.
Partial-value operations are distinct from authentic architectural execution.
"""
import argparse,hashlib,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'emulator/harness'));sys.path.insert(0,str(ROOT/'emulator/tests'))
from partial_state import Partial,RegisterCell,ICC
from symbolic_startup import Startup,bootstrap_history,canonical_trace
from ct_stock_load_audit import verify_inputs
import test_partial_state
def sha(b):return hashlib.sha256(b).hexdigest()
def save(d,name,obj):
    data=obj if isinstance(obj,bytes) else (json.dumps(obj,indent=2,sort_keys=True)+'\n').encode()
    with (d/name).open('xb') as f:f.write(data)
def run(out):
    out=out.resolve()
    if out.exists() or not out.is_relative_to((ROOT/'builds/phase19b-symbolic').resolve()):raise ValueError('Fresh symbolic phase output required')
    main,_=verify_inputs();dsp=ROOT/'firmware/dsp/build-4486'
    extracts=json.loads((dsp/'manifest.json').read_text());input_hashes={}
    for b in extracts['blocks']:
        for k,h in [('stream_file','stream_sha256'),('payload_file','payload_sha256')]:
            input_hashes[b[k]]=sha((dsp/b[k]).read_bytes());assert input_hashes[b[k]]==b[h]
    out.mkdir(parents=True)
    suite=unittest.defaultTestLoader.loadTestsFromModule(test_partial_state)
    with (out/'unit-tests.txt').open('x',encoding='utf-8',newline='\n') as f:
        result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
    if not result.wasSuccessful():raise ValueError('Partial model tests failed')
    # unittest prints duration; exclude walltime from reproducible evidence.
    save(out,'tests.json',dict(status='TESTED PASS',count=result.testsRun,failures=len(result.failures),errors=len(result.errors),
          scope='Symbolic primitives/peripheral qualified fixtures + fail-closed original startup; no positive authentic stock coverage'))
    summaries=[]
    for role,data in [('main',main),('worker',(dsp/'selection0-channel1.payload24.bin').read_bytes())]:
        cpu=Startup(role,data);summary=cpu.run(16);summaries.append(summary)
        save(out,role+'-trace.jsonl',canonical_trace(cpu.trace))
        save(out,role+'-transactions.json',cpu.transaction_log)
        save(out,role+'-partial-final.json',dict(PC=cpu.pc,SR=cpu.sr.as_dict(),OMR=cpu.omr.as_dict(),
             pending=cpu.pending.as_dict(),priority=cpu.priority.as_dict(),ICC=cpu.icc.as_dict(),
             meaning='Partially specified symbolic analysis state, not concrete C++ CPU snapshot'))
        assert cpu.count==0 and cpu.transaction_log==[]
    at100=Startup('main',main);at100.pc=0x100
    save(out,'main-at100-gate.json',dict(entry_provenance='Static originalP0 JMP100; not an executed jump',
         result=at100.run(1),trace=at100.trace))
    # Pure local BCLR/BSET transfer functions: not CPU/stock execution.
    local=[]
    for addr,setbit,pc in [(0xfffffa,False,0x100),(0xfffff9,True,0x101)]:
        cell=RegisterCell(addr,f'Unresolved handoff Y:{addr:06X}')
        local.append(dict(PC=pc,scope='SYMBOLIC local documented latch/bit operation only; architectural IRQ/loop gate not bypassed',
                     transfer=cell.bit_operation(13,setbit,f'local semantic witness P:{pc:06X}')))
    save(out,'gpio-local-transfers.json',local)
    save(out,'bootstrap-partial-history.json',bootstrap_history())
    save(out,'ICC-partial-contract.json',dict(initial=ICC().as_dict(),actual_publication=False,actual_receive=False,
         supported_case='Enabled maskable transfer with known absent prior flag, real publisher then pending read/ACK',
         blocked_cases=['Unknown interrupt enable','Unknown previous pending/overrun behavior','Empty/disabled ACK case not qualified'],
         no_seeded_30002=True,fixture_payload='0x123456, synthetic only',
         source='DSP56724RM13.1.2/13.2.2; no generic latch stub'))
    ledger=[
       dict(field='SR.I + request/PIC state',category='C',first_use='Before original instruction fetch',
            reason='Eligible interrupt can replace next instruction with handler; pending absence is not implied by no event injection'),
       dict(field='SR.LF / LA / LC / stack',category='C conditional',first_use='Loop-end/IRQ processing if enabled',
            reason='Unused only if inactive loop/IRQ decision is proven; not arbitrary blanket stack zero requirement'),
       dict(field='SR.SA',category='C deferred',first_use='Main102 accumulator transfer mode',reason='16/24-bit organization differs; not consumed by local bit operation'),
       dict(field='OMR MS/MSW',category='B for low prefix addresses',first_use='Mapping',
            reason='Reviewed candidate privateP maps all coverP0/100; exact fullOMR not required for those addresses'),
       dict(field='OMR.SEN / XYS',category='C only on stack extension',first_use='First stack operation or eligible IRQ',
            reason='No explicit stack use100..106; do not set fullOMR tozero'),
       dict(field='SSH/SSL/SZ/EP',category='C only if stack/extension is actually used',first_use='Inherited IRQ/loop or later stack operation',
            reason='No numeric contents needed on the explicit five-instruction operand path; extension enable/operation controls relevance'),
       dict(field='X0/X1/Y0/Y1/B',category='Unused by explicit main100..106',first_use='Deferred; no blanket exact/zero requirement',
            reason='Later definitions and uses must be audited when reached'),
       dict(field='SP/SC',category='A on reviewed explicit call path',first_definition='Main107/108',
            first_use='Main10F explicitJSR; inheritedIRQ/loop exception separately gated'),
       dict(field='R0',category='A on reviewed scalar path',first_definition='Main10B',first_use='Main10D'),
       dict(field='R5 worker',category='A on reviewed publication path',first_definition='Worker105',first_use='Worker107/109'),
       dict(field='R/N/M remainder',category='Not used by explicit100..106',first_use='Deferred, not yet reached',
            reason='No claim that all later uses are dominated; modifiers not needed for direct latch addresses'),
       dict(field='InitialC',category='A local overwrite',first_definition='Main100 then101',
            reason='C fromoldbit13 can remainunknown; it does not choose JNE106, which readsZ'),
       dict(field='InitialZ/A',category='A local overwrite conditional on modes',first_definition='A at102;Z at104',
            reason='Unknown returnedICC data would make equality/branch uncertain; fullCMP not certified by newadapter'),
       dict(field='PCRG/PRRG unrelated bits',category='Propagated SYMBOLIC',first_use='100/101 local RMW',
            reason='Bit13 defined, unrelated masks preserved; actual pin/output trace not proved equivalent'),
    ]
    save(out,'first-use-ledger.json',ledger)
    save(out,'result.json',dict(status='BLOCKING genuine control dependency; success criterion NOT MET',summaries=summaries,
         original_main_instructions_executed=0,original_worker_instructions_executed=0,
         reaches_ICC_poll=False,worker_published_30002=False,main_received_30002=False,
         first_blocker='ROM-exit pending request/PIC IPL/SR.I -> interrupt eligibility -> beforeP0 instruction vsISR',
         longest_unconditional_authentic_prefix=0,
         OMR_and_C_history='Bootstrap-known modifications retained as historical partial constraints; secondROM preservation not proven',
         ROM_listing='Not uniquely necessary; evidence proving only live interrupt/loop/mode constraints can substitute. Current evidence insufficient.',
         next_step='Establish a narrowly sourced no-delivery/interrupt-mask+pending contract at first app boundary, then reevaluate partial loop guard',
         cooperative_scheduler='Not implemented: neither original core may begin; no staged completion fabricated',
         controlled_startup_continue=False,no_scheduler_or_Plaits=True))
    save(out,'source-manifest.json',{p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in [
         ROOT/'emulator/harness/partial_state.py',ROOT/'emulator/harness/symbolic_startup.py',
         ROOT/'emulator/tests/test_partial_state.py',Path(__file__)]})
    save(out,'integrity.json',dict(all_ten_input_hashes=input_hashes,original_SYX_BIN_checked=True,
         core_modified=False,concrete_stock_interpreter_executed=False,symbolic_architectural_stock_instructions_executed=0))
    verify_inputs()
    save(out,'hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file() and p.name!='unit-tests.txt'})
    print(f'{result.testsRun} focused tests PASS; original main/worker instruction counts0; interrupt-boundary dependency BLOCKING')
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',required=True,type=Path)
    run(ap.parse_args().output_dir)
