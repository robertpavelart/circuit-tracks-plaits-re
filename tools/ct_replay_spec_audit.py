#!/usr/bin/env python3
"""Phase18 STATIC specification exporter; no replay, firmware execution or device APIs."""
import argparse
import hashlib
import json
from pathlib import Path
from ct_static import ROOT, BIN_HASH, SYX_HASH
from ct_resource_audit import read_rows
import ct_fw_tool

CPP = '44353be2f0156cac970c6ab4f467ea1998b40605'
RUST = 'c60aeedb6a6014850204c71e53bc0cf5b3104222'
CANDIDATES = [
    dict(name='C++ dsp56300', commit=CPP, chosen=True, license='GPLv3; localLICENSE.md',
         execution='Interpreter first, DSP56K_FORCE_INTERPRETER=ON; optional JIT not qualified',
         instruction_coverage='DSP56300 opcode/parallel-move implementation; targeted corpus and unknown instruction trap required, not certified complete',
         DSP5672x='ISA relevant,56362 peripherals not turnkey56724 board',
         memory='P/X/Y arrays, external bridge/mirrors; custom separate space/core bus required',
         AGU='linear/modulo/bitreverse source exists; legacyFFFF mode must be validated',
         loops='DO/REP source exists; internal iterations bypass outer driver and some callbacks',
         interrupts='vector, stack/RTI and pending IRQ code exists; candidate56724 priorities validation required',
         peripherals='56362SHI/ESAI/DMA/timers;56724ICC/EMC mapping missing',
         interception='CPU/peripheral/bus routes plus DMA memcpy/fill fastpaths and loop instruction hooks must be mediated',
         build='CMake>=3.15,C++17,asmjit/base existing sources; interpreter option still linksasmjit; headlesstarget,no wx/GUI/plugins/VTune/network'),
    dict(name='Rust mborgerson toolkit', commit=RUST, chosen=False, license='MIT; localLICENSE',
         execution='Cranelift JIT; no separate interpreter identified in reviewed crate',
         instruction_coverage='DSP56300 decoder/JIT emitter; decoder validation not execution validation',
         DSP5672x='ISA relevant, no validated56724 peripheral model', memory='P/X/Y region buffers/callbacks',
         AGU='modulo/bitreverse helper exists; mode and effective-address fixtures required',
         loops='DO/REP/JIT loop emitters exist; audit optimized loops/event boundaries',
         interrupts='pending/fast/long IRQ state exists', peripherals='callback API for embedder models',
         interception='constant/dynamic buffer stores bypasswrite_memory; allRAMcallbacks or emitter hooks needed',
         build='Rust/Cargo,Cranelift/target-lexicon dependencies; no downloads/build inPhase18')
]

REGISTERS = [
    ('PC','VERIFIED INITIAL VALUE','0 at uploaded-image entry; stock0→100; not hardware ROM reset simulation'),
    ('SR','MUST BE MODELED','candidate reset/ROM masks not captured; execute109ORI MR,10Abset21,25F1ANDI MR; preserve stock mode includingDO0'),
    ('OMR','MUST BE MODELED','bootstrap setsbit7/22 andclears21; rest andROMhandoffunknown; named map profile cannot claim exactwholeOMR'),
    ('SP/SC','DERIVABLE BY RUNNING STOCK STARTUP','107/108 set0 before10FJSR'),
    ('SSH/SSL/systemstack/SZ','MUST BE MODELED','realstackpush/pop,DO nesting andISR scratch; no inventedreturnHALT instruction;SZ/resetundefined treatedexplicitly'),
    ('R0..R7','DERIVABLE BY RUNNING STOCK STARTUP','pathwrittenvalues;2779setsR0=0,otherR values from subsequent code; entryfixture declares each readbeforewrite'),
    ('N0..N7','CAN START UNKNOWN','only if no readbeforewrite;1F5C setsN1/N3=2,N4=-3,N5=-4; other liveN inputs must be modeled'),
    ('M0..M7','DERIVABLE BY RUNNING STOCK STARTUP','2779..2781 set00FFFF; later ringfilters change/restore; not synonymFFFFFF without mode validation'),
    ('A/B/X0/X1/Y0/Y1','CAN START UNKNOWN','only dominated scratch; known2779clearX0=0; consumed unknowns stop, never implicitzero'),
    ('LA/LC/loop flags','MUST BE MODELED','loopstack/DO/REP0 behavior, nestedloops,restore validated'),
    ('VBA/interruptmask/priorities/pendingIRQ','MUST BE MODELED','resetprofile plus stockperipheral configuration anddeterministicevents;no pretenddisabled-asnormal')
]

PERIPHERALS = [
    ('SHI','NOT REQUIRED FOR TARGETED REPLAY','Unit helper/countfixture hasnone; integratedhost changes needEVENT INJECTION plusminimal FIFO/status/HTX/width andstockvector44; noexternalSysEx'),
    ('ESAI','EVENT INJECTION SUFFICIENT','32two-slot frames/inputscript; stageDMA andvector3E withstockISR; noDAC/UI'),
    ('DMA','FULL MODEL REQUIRED for active channel modes','Minimum exact enabledTX4/RX0 stagingtransfers/rearm; everyDMAstorebuslogged; nonaudio modestrap; no fullunneededDMAdevice'),
    ('Timers','MINIMAL STUB SUFFICIENT','modeled read-only virtual counter for reachedFFFF88 timingreads; enabledtimerIRQ needsfaithfuleventsemantics,notzeroallregisters'),
    ('Interrupts','FULL MODEL REQUIRED','usedpriority/mask/fast-longentry,stack,RTI andarbitration boundaries; physicalcycles not claimed'),
    ('ICC/worker','MINIMAL STUB SUFFICIENT conditionally','derived sequential lookupworker adapter preservingqueuewrites/progress/handshake; dualstockworker fallback if writer/eventbehavior cannot match'),
    ('GPIO/handshake','MINIMAL STUB SUFFICIENT','latched config/readback andscriptedcommandlane/selectbits; nohost hardware'),
    ('PLL/CIM/EMC','MINIMAL STUB SUFFICIENT conditionally','explicit startupregister subset/clockprofile and externalinit readsemantics;missingbehaviorSTOP; no fakegenericregisterbank')
]

HOOK_PATHS = [
    ('CPU X/Y ordinary andabsolute/indirectstores','DSP::memWrite→Memory::dspWrite; pre/posttranslationlogical+physical bus mediation'),
    ('P writes/MOVEM/cache','DSP::memWriteP andMemory::set; validatecache invalidation forallaliases; log even samevalue'),
    ('MOVEP andbit/peripheralstores','DSP::memWritePeriph→peripheraladapter→bus; no RAM hook bypass'),
    ('parallel X/Y/L andreadmodifywrite','sameinstructiongroup two distinct accessordinals; preserve oldread/write ordering; no fakeatomiccoupling'),
    ('DO iterations','do_start internalexecInterpreter; opcodeentry hook eachiteration; hostouterstep not sufficient'),
    ('REP iterations','rep_exec direct cachedfunc calls; explicitrepeatedopcode hook andeventboundary required'),
    ('DMA','memCopy memcpy,getMemPtr,memFill directfastpaths must scalarize oremitperwordtransaction; externaldevice writes instrumented'),
    ('worker/ICC/shared alias','adapter/core actorwrites throughsharedbus withlogicalspace/core andcanonicalbacking ID'),
    ('host events/loader/checkpoint','logseparateorigin/phase;no unloggedarraymutation; startup/normal/service tags'),
    ('JIT directstores','disabledfirstprofile/assertforceinterpreter; any laterJIT needsconstant/dynamic/parallel/emittercomplete coverage'),
    ('output/peripheral-mediatedtransfers','bus commit for eachdestination;observationsusepeekwithoutFIFO/IRQ sideeffects'),
    ('unmapped accesses','logattempt+classification,STOPunless documentedexplicitaccesspolicy; never silentdiscard')
]

SCENARIOS = [
    dict(id=0,name='startup + idle block',source='stockstartup and derivedhostINIT tables/events; not allzeros inventedpreset',
         gate='ICC startupack;unmappedYclear/EMC behavior;XFFF andX193F publisher/table provenance;X13 enable',
         checks='bootclear/copies/cursors/descriptors,one integrated32-frame period,203A countloads andallhighX stores'),
    dict(id=1,name='one synth-group note',source='ARM219E8/21246 addressed publication;selectedslot/bank,targetY159,Y14D/lifecycle fields',
         gate='fullparameter/defaulttable prerequisites and exacteventwrite ordering;not a MIDI/UI implementation',
         checks='activation flags,note/phase/gain,203A samples;countwrite andhighX ledger'),
    dict(id=2,name='multiple slots',source='boundedslots0..5 then6..11;release/stolen lifecycle fromARM21C48 pathways',
         gate='six/six bank evidence,allocation/releasecondition andallrequiredfields;not randompokes',
         checks='sequentialdescriptors,scratchreuse,worker requests,ISRinterleavings'),
    dict(id=3,name='patch/parameter changes',source='documentedARMaddressednormalpublishers/bankselector destinations',
         gate='exactconversion/value-domain and eventorigin manifest;missingfieldSTOP',
         checks='cursor cells,descriptor targets,count35Fbank0 zero publisher,bothbanks andhighX'),
    dict(id=4,name='filter/effect activity',source='validimmutable55entrytable/+1 dispatch modes and stockeffect parameterwrites',
         gate='parent1E15 normalreach UNRESOLVED; separate1F5C callerA/B conditional fixtures,not forcednormalpath',
         checks='knowncursorXreach/no writeback,coefficient/statewrites;targetnotreached resultdistinct frompass'),
    dict(id=5,name='transport/state transition',source='documentedARMnormalenable/reset/bank transitionwrites ifrecovered',
         gate='exacttrigger/publisher orderingUNRESOLVED; mark BLOCKED ratherthan invented UIevent',
         checks='normalversusbootinit epochs,descriptor/cursorpreservation andcounts'),
]

VALIDATIONS = [
    ('image','exactpayloadhash/endian/length,0→100 and3E/44→1B4/156; no headerloadedasP'),
    ('core arithmetic','24bit sign/leftalign immediates,56bit accumulators,MAC rounding/saturation/scaling flags,parallel readbeforewrite'),
    ('AGU','00FFFF legacylinear vsFFFFFF;N=-3/-4,pre/postupdate,3FFringwrap,bitreverse andnonpow2 modulo modes actually reached'),
    ('loops','DO count0/1/2/32 underSRmode;stock203A zero-skip;REP0 semantics,extensions,nestedDO/REP;everyiterationhook/event'),
    ('stack IRQ','JSR/RTS,fastvectorJSR/longentry,SSH/SSL sideeffects,ISR maskpriority/preemption andRTIrestore'),
    ('memory hooks','absolute/indirect/parallelL/samevalue/P/MOVEP,DMA memcpy/fill/external,worker/shared aliases andloader event;oneobservedtxnperactualwordcommit'),
    ('startup','6000X/Y attempted clears,8000sharedclear;all4manifesttablecopies,cursoralternation,14descriptors;YoutsideRAMSTOPuntilpolicyproven'),
    ('scheduler','1D9occupancythreshold300,140N32/X3B16/X3C31,198D14entries,19BFbitmap,759handshake,775completion'),
    ('1F97 unit','parentA/B recordedfixtures;16outerx32stores=512 at1F97 perhelpercall;2x32 initialbufferclearstores separate;R7notwrittenback;Xreaches andlocalYcursorpreservation'),
    ('203A unit','202BentryR0=35F;loadordinal beforepostincrement;count0 skips204B only withvalidatedmode;syntheticcount1 controlfixture isnotnormalpublisherevidence'),
    ('voice/output','phasecommit selected7F9 once in completionpass;mono32X2C46..66,mixbank0/1,Xring2words/frame,YFFD+64'),
    ('differential','match independentstaticblock expectations and firstdivergence; interpreter/JIT agreement supplemental only, no physicaldifftest'),
    ('determinism','samecode/state/event/build/modelmanifest -> byteidenticalcanonicaltrace+finalstateSHA256; no walltime/random/threads'),
]

WITNESSES = [
    ('source/dsp56kEmu/dsp.h','ASMJIT_FORCE_INLINE void execInterpreter()',22),
    ('source/dsp56kEmu/dsp.cpp','void DSP::resetHW()',46),
    ('source/dsp56kEmu/dsp.cpp','while(reg.sc.var >= stackCount',9),
    ('source/dsp56kEmu/dsp.cpp','const auto repeatedOpPC',25),
    ('source/dsp56kEmu/dsp.cpp','bool DSP::memWrite(',37),
    ('source/dsp56kEmu/memory.cpp','bool Memory::dspWrite',18),
    ('source/dsp56kEmu/memory.h','void forEachAlias',26),
    ('source/dsp56kEmu/dma.cpp','memcpy(dst, src',3),
    ('source/dsp56kEmu/dma.cpp','void DmaChannel::memWrite',25),
    ('source/dsp56kEmu/dspconfig.h','#if !defined(DSP56K_FORCE_INTERPRETER)',6),
    ('source/dsp56kEmu/CMakeLists.txt','target_link_libraries(dsp56kEmu PUBLIC dsp56kBase asmjit)',11),
    ('source/dsp56kEmu/agu.h','static void updateAddressRegister',12)
]

def sha(data): return hashlib.sha256(data).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',required=True)
    out=Path(ap.parse_args().output_dir).resolve()
    if out.exists(): raise SystemExit('Choose a fresh output directory')
    if out == ROOT/'original' or ROOT/'original' in out.parents: raise SystemExit('Protected original/')
    out.mkdir(parents=True)
    hashes={}
    def read(name):
        raw=(ROOT/name).read_bytes();hashes[name]=sha(raw);return raw
    def emit(name,obj):
        with (out/name).open('x',encoding='utf-8') as f:
            json.dump(obj,f,indent=2,sort_keys=True);f.write('\n')
    arm=read('firmware/circuittracks-firmware-4486.bin');syx=read('original/circuittracks-firmware-4486.syx')
    assert sha(arm)==BIN_HASH and sha(syx)==SYX_HASH
    path=ROOT/'original/circuittracks-firmware-4486.syx'
    assert ct_fw_tool.decode_syx(path)['firmware']==arm
    assert ct_fw_tool.build_syx(path,arm)==syx
    manifest=json.loads(read('firmware/dsp/build-4486/manifest.json'))
    for block in manifest['blocks']:
        for kind in ('stream','payload'):
            assert sha(read('firmware/dsp/build-4486/'+block[kind+'_file']))==block[kind+'_sha256']
    rows_by_channel={}
    for channel in (0,1):
        prefix=f'builds/phase3-selection0-channel{channel}.asm'
        read(prefix)
        payload=read(f'firmware/dsp/build-4486/selection0-channel{channel}.payload24.bin')
        rows_by_channel[channel]=read_rows(ROOT/prefix,payload)
    rows=rows_by_channel[0]
    for pc,text in {0:'jmp $0100',0x203A:'move x:(r0)+,x1',0x204B:'move b,x:(r4)',
        0x1F97:'move b,x:(r7)+',0x2788:'move x0,x:(r0)',0x2789:'move x0,y:(r0)+',
        0x107:'movec #$00,sp',0x108:'movec #$00,sc'}.items():
        assert rows[pc]['text']==text,(pc,rows[pc]['text'])
    windows=[(0,8),(0x3E,0x46),(0x100,0x156),(0x1B4,0x281),(0x759,0x77F),
             (0xC9D,0xCB8),(0x198D,0x19F3),(0x1E15,0x1F9B),(0x202B,0x2071),
             (0x25DB,0x262C),(0x2779,0x28DD)]
    with (out/'stock-dsp-witnesses.asm').open('x',encoding='utf-8') as f:
        f.write('\n'.join(rows[pc]['line'] for lo,hi in windows for pc in sorted(rows) if lo<=pc<hi)+'\n')
    with (out/'worker-witnesses.asm').open('x',encoding='utf-8') as f:
        f.write('\n'.join(rows_by_channel[1][pc]['line'] for pc in sorted(rows_by_channel[1]) if 0x100<=pc<0x12B)+'\n')
    evidence=[]
    for name,needle,count in WITNESSES:
        full='builds/vendor/dsp56300/'+name;lines=read(full).decode('utf-8').splitlines()
        start=next(i for i,line in enumerate(lines) if needle in line)
        evidence.append(dict(path=full,first_line=start+1,lines=lines[start:start+count]))
    for name in ('builds/vendor/dsp56300/LICENSE.md','builds/vendor/dsp56300-rust/LICENSE',
                 'builds/vendor/dsp56300-rust/crates/emu/Cargo.toml',
                 'builds/vendor/dsp56300-rust/crates/emu/src/emit/mem.rs'):
        read(name)
    emit('core-source-witnesses.json',evidence)
    emit('emulator-candidates.json',CANDIDATES)
    emit('initial-register-requirements.json',[dict(register=a,classification=b,requirement=c) for a,b,c in REGISTERS])
    emit('peripheral-requirements.json',[dict(peripheral=a,classification=b,requirement=c) for a,b,c in PERIPHERALS])
    emit('write-hook-coverage.json',[dict(path=a,requirement=b,status='DESIGN; not implemented or validated') for a,b in HOOK_PATHS])
    emit('scenarios.json',dict(status='DESIGN ONLY; all scenarios UNEXECUTED',scenarios=SCENARIOS))
    emit('validation-requirements.json',[dict(test=a,requirements=b,status='NOT RUN') for a,b in VALIDATIONS])
    reconstruction=json.loads(read('firmware/dsp/reconstructed-4486/manifest.json'))
    emit('stock-image-and-copies.json',dict(p_load=reconstruction['p_load'],table_copies=reconstruction['table_copies'],
        initial_PC=0,reset_target='P100',ESAI_vector='P3E→1B4',SHI_vector='P44→156',
        worker_P_range='[0,16C)',worker_SHA256='adf8da1b2b889d069eb52935dbdc4ce9092210d29df719937ca5ac5f62dfa91a',
        immutable_image_policy='no opcodepatch/sentinel; stock selfwrites logged in modeledP and validatedcache',
        startup_waits=['102ICC030002','25F3XFFF!=0','2602X193F!=0'],
        memory_gap='Yclear[4000,6000) outsideconditionalYprivateRAM;startupEMCinitX40000 reads;explicitsemantics unresolved,STOPnot enlargeRAM'))
    emit('memory-profile.json',dict(status='CONDITIONAL DSP56724/core mapping, not verifiedphysicalunit',
        endpoint0=dict(P='[0,4000)',X='[0,6000)',Y='[0,4000)'),
        endpoint1=dict(P='[0,2000)',X='[0,2000)',Y='[0,2000)'),
        shared='[30000,38000), canonicalbacking onlyfor corroborated X/Y/P/coreviews',
        peripherals='sparse declaredX/Y maps; startsFFE000..FFFFFF decoderwindow, not contiguousRAM',
        external='sparseprovenanced tables/EMC regions, readuninitializedfault; no genericbigzeroarray',
        logical_address='24bitword;key(endpoint,space,address);numericX/Yprivateaddresses distinct',
        alias='explicittranslation + sharedbacking; loglogical/physical/canonicalID; no defaultallspacebridge',
        invalid_policy='logattempt+STOP; documenteddiscardpolicy onlyafter proof, no silentread0/writeignore',
        citations=['https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf#page=76']))
    emit('trace-schema.json',dict(status='SPECIFICATION ONLY',fields=[
        'global_seq','virtual_time','instruction_ordinal','actor','core','origin_phase','scenario','PC_or_null_for_nonCPU',
        'causal_PC','opcode_words','access_ordinal','logical_space','logical_address','canonical_backing_ID','canonical_offset',
        'old24_or_unknown','new24','Rn_index_or_null','Rn_before','Rn_after','Nn','Mn','SR','OMR',
        'call_path','interrupt_depth','event_ID','transaction_group','commit_status'],
        selected_reads=['X35F','X[340,360)','X[5F00,6000)','Y[1820,1830)','Y[1A10,1A20)'],
        preinstruction203A='separateENTRY record, actual35Freadtransaction andR0/modifier context;interruptfirst arbitration mustbedefined',
        high_X='allactors,samevaluestores,boot versusnormal classification,attempts andaliases;no observedstore!=freeRAM',
        determinism='singlethreaded virtualevents;fixed ordering;canonical UTF8sortedkeys JSONL,newlineLF,integers,no walltime/addresses; SHA256trace and finalstate',
        manifest='image/source/build/eventscript/model/map/fixturehashes and explicitprovenance/unknowns; outputdirfresh',
        logging='nonmutatingpeek;neverperipheralreadtoobtainoldvalue; no traceoverwrite/drop; budgetoverflowSTOP'))
    emit('scheduler-and-worker-contract.json',dict(
        path=['113 hostjobs→1C53/1FD1','X13gate→1D9ringthreshold','1EF..1F5 prepare140/19F3/759',
              '1FC→198D descriptorrequest inclX14B→202B→203A','workerqueue execution/progress',
              '1FE→19BF completion','200..22A groupwork','242..24E converge','260→CB8 effects','276→21C4output→27BYFFD'],
        p1F97='not a standalonefunction nor guaranteedstage;1E80/1EE5→1F5C→1F97,normalparentreach unresolved',
        worker_minimum='B derived deterministic adapter: sequential stock120/125/126 lookup+shared replacement/progress,reset759 handshake; logallwrites/preserve spaces,notinstantdone',
        worker_fidelity_order=['A executeunchangedchannel1 withsamecore','B derivedworkeradapter','C derived/prerecordedresponses boundtospecificsources','D existingrequestfreepath subset only'],
        worker_effort_order=['D subsetfixture','C strictresponsefixture','B generalderivedadapter','A dualstockcore'],
        worker_invalid='nozeroresults/unconditionalcompletion/queuebypass;requestfreefixture notcomplete normalaliascoverage',
        wait_policy='finiteinstruction/virtualevent budget,diagnosticpendingstate,STOPunfulfilled;noNOPpatch or forcedPC'))
    emit('implementation-gates.json',dict(status='DESIGN ONLY; no harness implementation',
        sequence=[dict(phase='19A',scope='headless pinned interpreter+strictmemorybus+everywrite/opcode/REP hooks+ISA/AGU/loop/IRQ/hookfixtures'),
                  dict(phase='19B',scope='immutable stockload+startup prefix/partialinit; map/OMR/EMC/hosttablegates before fullstartupclaim'),
                  dict(phase='19C',scope='scheduler/frame/IRQ/SHI andworkeradapter contracts;comparestockworker ifmateriallyrequired'),
                  dict(phase='20',scope='validated stockscenario replay,differentialtraces,coverage/invariant/highXreports')],
        stops=['unknowninstruction/code-data boundary','AGU/loopmode mismatch','unhookedstore/DMAfastpath','uninitializedread','unmappedstartupaccess',
               'missinghosttable/workerresult','schedulerdivergence','unknownmaterialworkerbehavior','nondeterminism','traceoverflow'],
        estimate='2stages tofirstvalidated stockprefix at19B;4plannedstages tointegratedtargetstockreplay at20;unresolvedgates mayaddwork,notdeadline',
        invariant='NOT-YET-DETERMINED',high_X='NOT-YET-DETERMINED',next='19A onlyafter explicitimplementationinstruction'))
    for name,h in hashes.items(): assert sha((ROOT/name).read_bytes())==h
    emit('validation.json',dict(inputs_SHA256=hashes,script_SHA256=sha(Path(__file__).read_bytes()),
        baseline_hashes_match=True,extract_hashes_match=True,decoded_equals_BIN=True,SYX_roundtrip_equal=True,
        DSP_bytes_checked=True,source_witnesses_checked=True,mode='DESIGN+STATIC ONLY; NO emulator/hardware/firmware execution'))

if __name__=='__main__': main()
