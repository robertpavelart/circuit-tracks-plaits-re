"""Phase19C-PARENT: targeted original parent evidence and closed execution gate.

Offline static collector, not a CPU replay. No device, network or native core
API. A structurally valid helper snapshot is not evidence of normal entry.
All exports require a fresh explicit directory within builds/phase19c-parent.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
from ct_stock_load_audit import verify_inputs, rows
import ct_fw_tool


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def direct_target(text):
    # DO operands and X/Y data addresses are deliberately not call edges.
    m = re.match(r'^(j\w+|b(?:ra|sr|eq|ne|cc|cs|ge|gt|le|lt|mi|pl|ec|es|lc|ls|nr|nn)) >?\$([0-9a-f]+)$', text)
    return int(m[2], 16) if m else None


def family_calls(mask):
    """Only local finite X7C&0C guard; no claim parent is reachable."""
    if mask is None:
        return None
    if mask not in (0, 4, 8, 12):
        raise ValueError('Require the masked two-bit value')
    return [0x1e80, 0x1ee5] if mask == 0 else [0x1ee5]


def require_normal_checkpoint():
    # There is intentionally no parameter accepting invented normal/stack flags.
    # Opening this gate requires a new instruction-backed predecessor proof.
    raise ValueError('NORMAL-PATH UNRESOLVED: no verified target-producing predecessor to P:1E15; no actual SP/SC/LF/FV checkpoint')


def fresh_output(path):
    path = path.resolve()
    allowed = (ROOT/'builds/phase19c-parent').resolve()
    if path.exists() or path == allowed or not path.is_relative_to(allowed):
        raise ValueError('Require fresh child directory under builds/phase19c-parent')
    return path


def collect(path):
    out = fresh_output(path)
    main, protected = verify_inputs()
    inputs = {}
    def read(name):
        p = ROOT/name
        inputs[name] = digest(p)
        return p.read_bytes()
    def old(name):
        return json.loads(read(name))
    def emit(name, value):
        with (out/name).open('x', encoding='utf-8', newline='\n') as f:
            json.dump(value, f, indent=2, sort_keys=True)
            f.write('\n')
    syx = ROOT/'original/circuittracks-firmware-4486.syx'
    arm = (ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    assert ct_fw_tool.decode_syx(syx)['firmware'] == arm
    assert ct_fw_tool.build_syx(syx, arm) == syx.read_bytes()
    manifest = old('firmware/dsp/build-4486/manifest.json')
    for b in manifest['blocks']:
        for k in ('stream', 'payload'):
            name = 'firmware/dsp/build-4486/'+b[k+'_file']
            read(name)
            assert inputs[name] == b[k+'_sha256']
    listing_name = 'builds/phase3-selection0-channel0.asm'
    read(listing_name)
    r = rows(ROOT/listing_name, main)
    words = [int.from_bytes(main[i:i+3], 'big') for i in range(0, len(main), 3)]
    def req(pc, text):
        assert r[pc]['text'] == text, (hex(pc), text, r[pc]['text'])
    for pc, text in {
        0x1e14:'rts', 0x1e15:'move r6,x:$1d3a', 0x1e17:'move r7,x:$1d3b',
        0x1e19:'jsr $1fb2', 0x1e1b:'move x:$007c,a', 0x1e1d:'and #$0c,a',
        0x1e1e:'jeq $1e31', 0x1e26:'jcc $1e82', 0x1e2f:'jmp $1e82',
        0x1e80:'jsr $1f5c', 0x1ee3:'jsr $1f13', 0x1ee5:'jsr $1f5c',
        0x1f10:'rts', 0x1f12:'rts', 0x1f5b:'rts',
        0xd99:'do #$0005,$0db0', 0xdae:'jsr >$0db2', 0xdb6:'jmp (r1)',
        0xdad:'move x:(r1+n1),r0', 0xda3:'move x:(r0)+,n1',
        0x19a5:'move x:(r3)+,r1', 0x19ac:'jsr (r1)',
        0x260:'jsr >$0cb8', 0x1fc:'jsr $198d', 0x12a:'jsr >$01d9',
        0x2655:'move #$50,n0', 0x2656:'move n0,x:$0038',
        0x2812:'move #>$000001,x0', 0x2814:'move x0,y:$0015',
        0x148:'sub x1,a a,x:(r0)+ a,y0', 0x149:'sub x1,b b,x:(r0)+',
        0x29ec:'move #$0029f6,r0', 0x29ee:'move #$0009db,r1',
        0x29f0:'do #$0037,$29f5', 0x29f3:'move x0,x:(r1)+',
    }.items():
        req(pc, text)
    dispatch = old('builds/phase12/final/effect-dispatch.json')
    assert [int(t['P_value'],16) for t in dispatch['table']] == words[0x29f6:0x2a2d]
    algorithms = words[0x29f6:0x2a05]
    wrappers = words[0x2a05:0x2a2d]
    assert len(algorithms) == 15 and len(wrappers) == 40
    assert all(v+1 != 0x1e15 for v in algorithms)
    assert 0x1e15 not in wrappers
    params = old('builds/phase12/final/normal-parameter-exclusions.json')
    assert all(not x['overlapping_recovered_parameter_intervals'] for x in params)
    preservation = old('builds/phase15/verified/inherited-cursor-preservation-obligations.json')
    local = old('builds/phase15/verified/local-mutation-exclusions.json')
    prefix = old('builds/phase12/final/effect-prefix-accesses.json')
    tail = old('builds/phase12/final/effect-tail-accesses.json')
    old_result = old('builds/phase19c-fullhelper/final/result.json')
    assert old_result['cases'] == 40 and old_result['original_opcodes'] == 385880
    for name, h in old('builds/phase19c-fullhelper/final/source-manifest.json').items():
        read(name)
        assert inputs[name] == h
    # Do not re-execute or reinterpret the already certified structural cases.
    old('builds/phase19c-fullhelper/checks/reproducibility.json')
    read('builds/phase19b/documentation/DSP56300FM.pdf')
    read('builds/phase19b-irq/documentation/DSP56300FM.pdf.txt')
    read('emulator/upstream/dsp56300/source/dsp56kEmu/dsp.cpp')
    out.mkdir(parents=True)
    parent = [x for pc,x in r.items() if 0x1e15 <= pc < 0x1f11]
    calls = [x for x in parent if x['text'].startswith('jsr ')]
    assert [x['PC'] for x in calls] == [0x1e19,0x1e80,0x1ee3,0x1ee5]
    loops = []
    for x in parent:
        if x['text'].startswith('do '):
            last = words[x['PC']+1]
            loops.append(dict(PC=x['PC'], body=x['PC']+x['words'], last_word_LA=last,
                continuation=last+1, instruction=x['text']))
    assert len(loops) == 10
    assert not any(a['body'] <= pc <= a['last_word_LA'] for a in loops for pc in (0x1e80,0x1ee5))
    # Only decoded control transfers: the 0C1E15 ALU opcode at2289 is no edge.
    external = [x for pc,x in r.items() if not 0x1e15 <= pc < 0x1f11
                and (direct_target(x['text']) is not None)
                and 0x1e15 <= direct_target(x['text']) < 0x1f11]
    assert external == []
    assert not any(re.search(r'\b(?:sp|sc|ssh|ssl|la|lc|sr|omr|m[0-7])\b', x['text']) for x in parent)
    assert not any(x['text'].startswith('rep ') for x in parent)
    peripherals = [x for x in parent if re.search(r'[xy]:\$fff[0-9a-f]{3}',x['text'])]
    assert peripherals == []
    nodes = []
    for x in parent:
        pc, text = x['PC'], x['text']
        next_pc = pc+x['words']
        edges = []
        target = direct_target(text)
        if text == 'rts':
            edges.append(dict(kind='RETURN',target=None))
        elif text.startswith('jsr '):
            edges.extend([dict(kind='CALL',target=target),dict(kind='CONTINUATION_IF_RETURN',target=next_pc)])
        elif target is not None:
            edges.append(dict(kind='BRANCH',target=target))
            if not text.startswith('jmp '): edges.append(dict(kind='FALLTHROUGH',target=next_pc))
        else:
            edges.append(dict(kind='SEQUENTIAL',target=next_pc))
        if text.startswith('do x:'):
            edges.append(dict(kind='DO_ZERO_SKIP_IF_COUNT0_AND_COMPATIBILITY_SC0',target=words[pc+1]+1))
        for a in loops:
            if pc+x['words']-1 == a['last_word_LA']:
                edges.append(dict(kind='DO_REPEAT_CONDITIONAL_COUNT',target=a['body']))
        nodes.append(dict(PC=pc, instruction=text, edges=edges))
    emit('parent-control-flow.json', dict(status='VERIFIED static instructions; not dynamic reachability',
        entry=0x1e15, end_exclusive=0x1f11, previous_RTS=0x1e14, exit_RTS=0x1f10,
        decoded_instruction_sites=len(parent), calls=calls, DO=loops, REP=[],
        explicit_stack_loop_register_writes=[], direct_peripheral_accesses=peripherals,
        external_decoded_direct_entries=external, nodes=nodes,
        branches=[dict(mask=m,helper_call_sites=family_calls(m)) for m in (0,4,8,12)],
        branch_premise='Original X7C&0C guard, finite counts, complete normal callee returns, no async clobber; X7C value unproved'))
    sites = dispatch['indirect_sites']
    assert {int(x['PC'],16) for x in sites} == {0xdb6,0xdbd,0xdc5,0xdcd,0xdec,0xdf9,0x19ac}
    emit('predecessors.json', dict(status='UNRESOLVED actual parent edge',
        scheduler_edges=[dict(PC=0x12a,target=0x1d9),dict(PC=0x260,target=0xcb8),dict(PC=0x1fc,target=0x198d)],
        sites=[dict(x, classification='NORMAL AUDIO descriptor dispatcher' if x['PC']=='0x19ac' else 'NORMAL EFFECT dispatcher/wrapper',
            parent_selection='UNRESOLVED; initialized/preserved valid targets exclude parent') for x in sites],
        effect_predicate='DB6: X[9EA+5*X95A+i] would need1E15; algorithm calls: X[9DB+X(95B+i)] plus1 would need1E15, legacy linear; i0..4',
        descriptor_predicate='19AC: descriptor+0 atX[EB+8*i], i0..13, would need1E15; M3/descriptor preservation required',
        no_direct_entry='No decoded direct edge to any instruction in parent; prior1E14 RTS prevents simple fallthrough',
        other_entries='Arbitrary corrupted/out-of-domain/computed targets not closed; not assumed normal or impossible',
        service_init='No recovered direct INIT or SERVICE caller; related init1F9B tail-jumps1F13, not parent/helper'))
    emit('initialized-targets.json',dict(status='VERIFIED conditional on executed initializer and retained tables/modifiers',
        effect_copy=dict(PC=[0x29ec,0x29ee,0x29f0,0x29f2,0x29f3],P=[0x29f6,0x2a2d],X=[0x9db,0xa12]),
        table=dispatch['table'],valid_selector_domains=dispatch['required_normal_domains'],
        descriptor_entries=[dict(X=0xeb+8*i,P=0x281 if i<12 else 0x202b if i==12 else 0x1a2b) for i in range(14)],
        descriptor_initializer=[0x2881,0x2892,0x2898,0x289a,0x28ac,0x28bc,0x28c7,0x28c9],
        parent_in_valid_effect_targets=False,parent_in_initialized_descriptors=False,
        normal_producers_and_preservation='UNRESOLVED; parameter exclusion is a subset, not universal write closure'))
    emit('stack-loop-obligations.json',dict(status='UNRESOLVED actual class; VERIFIED conditional instruction-derived accounting',
        actual_parent_SP=None,actual_parent_SC=None,actual_parent_FV=None,actual_resident_frames=None,
        parent_local_loop_at_helper=False,parent_local_DO_counts=[a['instruction'] for a in loops],
        effect_chain=dict(outer_DO=0xd99,LA=0xdaf,LC_min=1,LC_max=5,LF=1,
            FV='Not recovered stock entry; sealed counted-DO model clears FV, not a post-ROM proof',
            parent_entry_depth='s+5 where s is occupancy at1D9 entry, with all prior local loops closed and healthy resident stack',
            frames=['JSR260 toCB8 +1','DO D99 +2','JSR DAE toDB2 +1','tail JMP DB6 +0','algorithm JSR wrapper +1'],
            direct_DB6_parent_alternative='s+4 if mutable wrapper table instead supplies1E15 directly atDB6; no algorithm JSR; unproved target and pointer context',
            helper_pre_JSR_depth='d=parent entry depth, after prior parent callees/local loops have returned',
            helper_peak='d+6; inherited frames already counted in d',
            helper_returns='Would restore outer LA/LC/LF via original DO exits; not tested here',
            stock_or_model_compatibility='LF1 does not satisfy previous LF0 class; separate qualified active-loop replay required if target entry proved'),
        descriptor_chain=dict(loop='19A1..19B6 ordinary JLT, not DO; inherited LF/LA/LC still depend on caller',
            parent_entry_depth='s+2 via JSR1FC→198D andJSR19AC, s at1D9 entry; edge toparent unproved'),
        manual='DSP56300FM Rev5 PDF297..298 DO, PDF329 JSR, PDF408 RTS; shared hardware stack rules5.4.3',
        no_stack_seed='No stock CPU constructed; no prefix/return frame invented'))
    pointer_info=[]
    for family,values,pcs,definitions in [('A',[0x1800,0x1840,0x18e0],[0x1e76,0x1e7a,0x1e7e],[0x1e74,0x1e78,0x1e7c]),
                                         ('B',[0x19f0,0x1a30,0x1ad0],[0x1ed9,0x1edd,0x1ee1],[0x1ed7,0x1edb,0x1edf])]:
        for j,(v,pc,definition) in enumerate(zip(values,pcs,definitions)):
            req(definition,f'move #${v:06x},r0');req(pc,f'move r0,x:${0x1d40+j:04x}')
            pointer_info.append(dict(family=family,X=0x1d40+j,value=v,definition=definition,writer=pc,
                status='VERIFIED local immediate-to-store; actual parent execution UNRESOLVED'))
    emit('state-provenance.json',dict(pointers=pointer_info,
        counts=dict(X38=0x50,Y15=1,initializers=[0x2655,0x2656,0x2812,0x2814],
            formula='e=X38>>4=5; N=Y15<<e=32; X3A=N, X3B=N>>1=16 (parallel pre-subtraction stores)',
            computation=[0x140,0x141,0x142,0x143,0x145,0x146,0x147,0x148,0x149],
            normal_refresh_call=0x1f1,init_refresh_call=0x2657,
            status='VERIFIED publication relation; not all normal writers/retention; no count write in parent/helper'),
        cursors=dict(initializer_call=0x25e4,initializer=[0x260a,0x261a,0x261c,0x261d,0x261e,0x261f],
            cells=[dict(Y=b+j,X=values[j%2]) for b,values in [(0x1820,[0x2ccc,0x2cec]),(0x1a10,[0x2c02,0x2c24])] for j in range(16)],
            status='VERIFIED initialization and existing bounded helper preservation; normal foreign writers UNRESOLVED'),
        modifiers=dict(INIT=[0x2779,0x277b,0x277c,0x277d,0x277e,0x277f,0x2780,0x2781],value=0xffff,
            parent_direct_writes=[],temporary_M7=[0x265,0x27f],status='UNRESOLVED actual retained context; no local parent establishment'),
        symbolic_fields=['X7C guard','input scheduler/control state','actual stack/loop state','numerical coefficients/samples','foreign actor timing']))
    stores=[x for x in parent if re.search(r',[xy]:',x['text'])]
    direct_watched=[]
    for x in parent:
        for m in re.finditer(r'x:\$([0-9a-f]+)',x['text']):
            a=int(m[1],16)
            if 0x340 <= a < 0x360 or 0x5f00 <= a < 0x6000:direct_watched.append(x)
    assert direct_watched == []
    emit('memory-obligations.json',dict(status='STATIC operands/bounds only; no actual parent bus events',
        parent_store_sites=stores,direct_watched_operands=direct_watched,
        retained_local_cursor_exclusions=local,prefix_accesses=prefix,tail_accesses=tail,
        inherited_foreign_cursor_obligations=preservation,
        async_mutations='SHI19B indirect Y and198 indirect X; IRQ/mailbox/worker exclusions not supplied by parent; all remain UNRESOLVED',
        X35F='No direct operand, no local positive count publication; indirect/async actual path not closed',
        high_X='UNRESOLVED actual normal path; no observed/proven normal high-X writer supplied',
        to_203A='No original direct parent/helper call to203A; do not stitch',
        runtime_logs='Zero instructions; empty trace/watch files mean NOT EXECUTED, not measured non-interference'))
    try: require_normal_checkpoint()
    except ValueError as e: reason=str(e)
    emit('execution-gate.json',dict(status='UNRESOLVED / CLOSED',reason=reason,
        requested_entry=0x1e15,stock_CPU_instantiated=False,original_parent_opcodes=0,
        original_helper_opcodes_this_phase=0,checkpoint=None,run_attempted=False,
        missing=['instruction-backed normal target toparent','caller stack/loop frame provenance',
            'guard and live-data context','count/cursor/modifier preservation','async actor contract'],
        stop='User stop condition16: do not fabricate entry; no boot/scheduler/ROM archaeology automatically launched'))
    emit('watched-accesses.json',dict(status='NOT EXECUTED',events=[],monitored=['X35F','X[340,360)','X[5F00,6000)']))
    (out/'trace.jsonl').touch(exist_ok=False)
    emit('result.json',dict(status='STATIC investigation complete; normal parent execution CLOSED',
        normal_reach_1E80='UNRESOLVED',normal_reach_1EE5='UNRESOLVED',actual_stack_class='UNRESOLVED',
        actual_loop_class='UNRESOLVED; effect-chain candidate inherits LF1, outside testedLF0 class',
        high_X='UNRESOLVED',X35F_reads='UNRESOLVED actual path; no direct operand',X35F_writes='UNRESOLVED actual path; no direct operand',
        X35F_invariant='NOT-YET-DETERMINED',normal_runtime_evidence='No new NORMAL-PATH execution evidence; static predecessor constraints only',
        original_parent_opcodes=0,original_helper_opcodes_this_phase=0,
        theoretical_verified_256word_reservation='NO',firmware_implementation='NO',
        best_next_step='Targeted producer/preservation proof for normal effect selectorsX95A..95F and tableX9DB..A11: establish parent-selecting value or exclude this edge; avoid boot replay'))
    windows=[(0x1e14,0x1f13),(0x1f13,0x1f9b),(0x1fb2,0x1fd1),(0xc3e,0xcb8),(0xef2,0xf4f),
             (0x140,0x156),(0x1d9,0x200),(0x113,0x12d),(0x260,0x267),(0xd87,0xe18),
             (0x198d,0x19bf),(0x260a,0x262c),(0x2655,0x2658),(0x2779,0x278a),
             (0x2812,0x2815),(0x2881,0x28d3),(0x29ec,0x29f6)]
    with (out/'instruction-witnesses.asm').open('x',encoding='utf-8',newline='\n') as f:
        for pc,x in r.items():
            if any(lo<=pc<hi for lo,hi in windows):f.write(x['line']+'\n')
    for p in protected:inputs[p.relative_to(ROOT).as_posix()]=digest(p)
    for name in ['emulator/harness/parent/audit.py','emulator/tests/test_parent_gate.py','emulator/tests/verify_parent.py']:
        read(name)
    emit('provenance.json',dict(inputs=inputs,architecture='OriginalBE24DSP56300 words; existing byte-checked decoder',
        offline=True,codec_roundtrip=True,all_ten_extract_hashes=True,authentic_boot=False))
    verify_inputs()
    for name,h in inputs.items():assert digest(ROOT/name)==h,name
    emit('hashes.json',{p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()})
    print('Parent static gate CLOSED; 0 original instructions; fresh reproducible evidence: '+str(out))


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir',required=True,type=Path)
    ap.add_argument('--require-normal-replay',action='store_true',help='Refuse before creating output while the normal entry gate is closed')
    a=ap.parse_args()
    if a.require_normal_replay:require_normal_checkpoint()
    collect(a.output_dir)
