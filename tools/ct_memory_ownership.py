#!/usr/bin/env python3
"""Conservative static interval witnesses plus exhaustive listing inventories.

Not a DSP emulator, global points-to solver, or proof of unused memory.
Unknown origins, bounds, modifiers and indirect transfers remain explicit.
"""
import argparse,csv,io,json,re
from pathlib import Path
from ct_static import ROOT,sha,BIN_HASH,SYX_HASH,save
from ct_resource_audit import read_rows,REGIONS
import ct_fw_tool

CANDIDATES={'X':(0x4000,0x6000),'Y':(0x3000,0x4000)}

def csv_text(items):
    out=io.StringIO()
    keys=sorted(set().union(*(r.keys() for r in items))) if items else ['status']
    w=csv.DictWriter(out,fieldnames=keys);w.writeheader();w.writerows(items)
    return out.getvalue()

def affine_loop(rows,lo,hi,count,bases,steps=None,status='VERIFIED instruction-derived interval'):
    """Compute address hulls for a reviewed branch-free loop with linear AGU.

    bases/steps/count are explicit reviewed premises, not inferred across calls.
    Multiple operands sharing a pointer use the preinstruction address; updates
    then advance it. Unsupported indexed forms reject instead of inventing bounds.
    """
    steps=steps or {};pos=dict(bases);touch=[]
    for pc in sorted(p for p in rows if lo<=p<hi):
        t=rows[pc]['text']
        if t.split()[0] in ('do','rep','jmp','bra','jsr','bsr','rts','rti'):
            raise ValueError('Control flow in reviewed affine body')
        updates={}
        for m in re.finditer(r'([xy]):(?:>)?\((r[0-7])(?:([+-])(\d+|n[0-7]))?\)(?:([+-])(n[0-7])?)?',t):
            sp,reg,sign,offset,post,stride=m.groups()
            if reg not in pos:raise ValueError(f'Unknown base {reg} at {pc:X}')
            off=0
            if offset:
                off=(steps[offset] if offset.startswith('n') else int(offset))*(-1 if sign=='-' else 1)
            touch.append(dict(pc=pc,space=sp.upper(),register=reg,address=pos[reg]+off))
            if post:
                delta=steps[stride] if stride else 1
                delta*= -1 if post=='-' else 1
                if reg in updates and updates[reg]!=delta:raise ValueError('Parallel AGU ambiguity')
                updates[reg]=delta
        for reg,delta in updates.items():pos[reg]+=delta
    result=[]
    for r in touch:
        delta=pos[r['register']]-bases[r['register']]
        last=r['address']+(count-1)*delta
        lower=min(r['address'],last);upper=max(r['address'],last)+1
        candidate=CANDIDATES.get(r['space'])
        result.append(dict(pc=f"P:0x{r['pc']:X}",space=r['space'],register=r['register'],
            start=f'0x{lower:X}',end_exclusive=f'0x{upper:X}',stride=delta,iterations=count,
            bounds_status=status,overlaps_candidate=bool(candidate and lower<candidate[1] and upper>candidate[0]),
            premise='reviewed linear AGU, explicit base/count; caller premises recorded in witnesses.json'))
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True)
    out=Path(p.parse_args().output_dir).resolve()
    if out==ROOT/'original' or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    if out.exists():raise SystemExit('Choose a fresh output directory')
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    syxp=ROOT/'original/circuittracks-firmware-4486.syx';syx=syxp.read_bytes()
    assert sha(arm)==BIN_HASH and sha(syx)==SYX_HASH
    decoded=ct_fw_tool.decode_syx(syxp)['firmware'];assert decoded==arm and ct_fw_tool.build_syx(syxp,decoded)==syx
    programs={};absolute=[];pointers=[];indirect=[];loops=[]
    for selection in [0,1]:
        for channel in [0,1]:
            name=f'selection{selection}-channel{channel}'
            payload=(ROOT/f'firmware/dsp/build-4486/{name}.payload24.bin').read_bytes()
            rows=read_rows(ROOT/f'builds/phase3-{name}.asm',payload);programs[name]=rows
            definitions={};last_pc=None
            for pc,r in rows.items():
                t=r['text'];op=t.split()[0]
                if last_pc is not None and pc!=last_pc:definitions={}
                last_pc=pc+r['words']
                context='normal' if selection==0 else 'diagnostic separate image'
                for m in re.finditer(r'([xy]):\$([0-9a-f]+)',t):
                    addr=int(m[2],16);sp=m[1].upper();c=CANDIDATES[sp]
                    absolute.append(dict(program=name,pc=f'P:0x{pc:X}',space=sp,start=f'0x{addr:X}',
                        end_exclusive=f'0x{addr+1:X}',context=context,instruction=t,
                        overlaps_candidate=c[0]<=addr<c[1],status='decoded absolute operand; may be data misdecoded as code'))
                for m in re.finditer(r'([xy]):(?:>)?\((r[0-7])[^)]*\)(?:[+-](?:n[0-7])?)?',t):
                    origin=definitions.get(m[2])
                    indirect.append(dict(program=name,pc=f'P:0x{pc:X}',space=m[1].upper(),operand=m[0],
                        lexical_constant_origin=origin,interval_status='UNRESOLVED (no interprocedural/modifier proof)',
                        start='0x0',end_exclusive='0x1000000',instruction=t,context=context))
                if op in ('do','rep'):
                    args=t[len(op):].strip();body_start=pc+r['words']
                    end=re.search(r',\$([0-9a-f]+)$',args)
                    body_end=int(end[1],16) if end else body_start+rows.get(body_start,{}).get('words',1)
                    count_expr=args.split(',')[0]
                    loops.append(dict(program=name,pc=f'P:0x{pc:X}',operation=op,count_expression=count_expr,
                        body_start=f'P:0x{body_start:X}',body_end_exclusive=f'P:0x{body_end:X}',
                        indirect_operand_count=sum(bool(re.search(r'[xy]:.*\(r',v['text'])) for q,v in rows.items() if body_start<=q<body_end),
                        bounds_status='UNRESOLVED unless separately reviewed witness',context=context,instruction=t))
                # This lexical origin hint is deliberately not a flow-sensitive proof.
                for reg in list(definitions):
                    if re.search(r','+reg+r'(?:\s|$)',t) or re.search(r'\('+reg+r'\)[+-]',t):definitions.pop(reg,None)
                for m in re.finditer(r'#(?:>)?\$([0-9a-f]+),(r[0-7])',t):
                    value=int(m[1],16);definitions[m[2]]=f'P:0x{pc:X}={value:#x}'
                    pointers.append(dict(program=name,pc=f'P:0x{pc:X}',register=m[2],value=f'0x{value:X}',
                        in_numeric_candidate=any(lo<=value<hi for lo,hi in CANDIDATES.values()),
                        status='immediate register value; pointer/space not inferred',instruction=t))
                if op.startswith(('j','b')) and op not in ('bset','bclr','bchg','btst'):definitions={}
                if op in ('do','rep','rts','rti'):definitions={}
    rows=programs['selection0-channel0'];worker=programs['selection0-channel1']
    assert 'do x1,$278a' in rows[0x2786]['text'] and '#$006000,x1' in rows[0x2784]['text']
    assert '#$00ffff,m0' in rows[0x2779]['text'] and '#$00,r0' in rows[0x2782]['text']
    assert 'do x1,$2792' in rows[0x278f]['text'] and '#$008000,x1' in rows[0x278d]['text']
    witnesses=[dict(name='normal boot clear',origin='P:2779..2786, caller P:25DE',phase='startup',
        base={'r0':0},count=0x6000,body=[0x2788,0x278a],linear=True),
      dict(name='shared boot clear',origin='P:278A..278F',phase='startup',base={'r0':0x30000},count=0x8000,body=[0x2791,0x2792],linear=True),
      dict(name='post result copy',origin='P:A21/A23; X:3A=32 premise',phase='runtime selected N=32',base={'r1':0x2d2e,'r5':0x2c46},count=32,body=[0xa27,0xa29],linear=True),
      dict(name='mono scale prefetch loop',origin='P:BE0/BE2 plus X:3A=32 premise; r1 already advanced once',phase='runtime selected N=32',base={'r1':0x2c47,'r6':0x2c68},count=32,body=[0xbe6,0xbe8],linear=True),
      dict(name='gain/mix loop',origin='P:A80..A8B, selected bank0, slot0, N=32',phase='runtime selected N=32',base={'r0':0x5bd,'r5':0x2c47,'r6':0x2df0},count=32,body=[0xa8d,0xa95],linear=True),
      dict(name='cached lane fill',origin='P:7AE/7AF/7B6/7B7; mode0; N=32',phase='request-free completion',base={'r1':0x2d74,'r7':0xa01},steps={'n1':2,'n7':3},count=16,body=[0x7ba,0x7bc],linear=True)]
    intervals=[]
    for w in witnesses:
        rr=affine_loop(rows,*w['body'],w['count'],w['base'],w.get('steps'),
             'VERIFIED startup bounds' if w['phase']=='startup' else 'VERIFIED conditional selected-path bounds')
        for r in rr:r.update(program='selection0-channel0',witness=w['name'],phase=w['phase'])
        intervals+=rr
    # Fully reviewed worker save wrapper uses a fixed, linear Y pointer 0..21.
    assert '#$00,r0' in worker[0x12d]['text'] and '#$00ffff,m0' in worker[0x12e]['text']
    intervals+= [dict(program='selection0-channel1',space='Y',start='0x0',end_exclusive='0x16',
        phase='interrupt wrapper',witness='P:133..148 saves; P:150..165 restores',bounds_status='VERIFIED wrapper local interval; private core Y',overlaps_candidate=False)]
    calls=json.loads((ROOT/'builds/phase3-arm-callers.json').read_text())
    hostcalls=[r for r in calls if int(r['target'],16) in [0x80292dc,0x80292f8,0x8029314,0x8029344,0x80294ac,0x80294ca,0x8029528,0x80295ba]]
    initialized=[]
    reconstructed=ROOT/'firmware/dsp/reconstructed-4486'
    manifest=json.loads((reconstructed/'manifest.json').read_text())
    for copy in manifest['table_copies']:
        raw=(reconstructed/copy['file']).read_bytes();assert sha(raw)==copy['sha256']
        space,addr=copy['destination'].split(':');base=int(addr,16)
        assert len(raw)==copy['words']*3
        for index in range(copy['words']):
            value=int.from_bytes(raw[index*3:index*3+3],'big')
            initialized.append(dict(space=space,address=f'0x{base+index:X}',value=f'0x{value:X}',
                source=copy['source'],copy_pc=copy['instruction'],
                in_numeric_candidate=any(lo<=value<hi for lo,hi in CANDIDATES.values()),
                status='VERIFIED copied value; not automatically a pointer; partial reviewed initialization'))
    clobbers=[
      ('r0','YES','restore E+0x31 before 9DD','NO; coefficient cursor then advanced','9DD first read'),
      ('r4','YES','restore S+0xC before selected post path','NO; post state advances','AA8 ACC and BDD BED/BFD'),
      ('r1/r3','NO incoming value, selected mode0 only','not needed for selected first uses','YES A19/A1B','mode0 enters A19'),
      ('r2/r5/r6/r7','selected incoming values not established as required','conservatively preserve until all helper branches reviewed','locally reset by AA8/BDD/C09/C06/A80..A86','no all-mode clobber proof'),
      ('A / incoming condition codes','NO at immediate entry','no incoming value required','9DD load and 9DE CMP redefine','later SR modes remain live'),
      ('B/x0/x1/y0/y1','UNRESOLVED all modes','conservative preserve','selected helpers redefine operands','not a full interprocedural liveness proof'),
      ('m0/m4','YES for pointer addressing','preserve expected modifier behavior','not generally reset at 9DD','r0/r4 indirect addressing'),
      ('other m registers','UNRESOLVED all modes','conservative preserve','AA8 changes/restores m5; others conditional','ADC/modulo semantics not inferred from numeric pointers'),
      ('n0..n7','UNRESOLVED all modes','conservative preserve pending complete liveness','AA8/BDD/filter/mixer redefine several','selected n1/n3/n4/n5 setup is explicit'),
      ('SR/MR','YES modes','preserve scaling/rounding and interrupt mask','CA2 sets scaling, CB6 clears it','incoming CCR is distinct from arithmetic mode'),
      ('SP/SC/SSH/SSL/LA/LC','YES caller/loop context','balanced calls and nested DO/REP, no loop-stack corruption','not repaired by 9DD','nested hardware loops and RTS AA7'),
      ('X:CC/X:2C/X:39..41','YES','preserve bank/context/block constants','consumed downstream','A84/A95 and helper loops'),
      ('X:2F30..2F34/shared queue/ICC','YES scheduler invariants','preserve/reset coherent request/completion state','global scheduler transitions only','759/775/198D/19BF'),
      ('retained X/Y voice/filter/envelope/gain state','YES','preserve upstream updates and expected phase lifecycle','post helpers evolve retained state','gate, note-follow, gain producer and 980..998 commit'),
      ('X:2C66 readable','YES prefetch','keep readable; do not place inaccessible boundary here','last prefetched value unused by selected block','BE2/BE6 and A89/A93 read 33 words')]
    classification=[dict(space=sp,start=f'0x{lo:X}',end_exclusive=f'0x{hi:X}',words=hi-lo,
        startup_status='VERIFIED written by normal clear; fails no-initialization-use criterion',
        runtime_status='UNRESOLVED indirect/host bounds; not proven persistently occupied',
        verified_available=False) for sp,(lo,hi) in CANDIDATES.items()]
    summary=dict(status='static conservative audit; not global points-to proof',syx_sha256=sha(syx),bin_sha256=sha(arm),roundtrip_identical=True,
        classifications=classification,minimum_allocations=[dict(words=n,proved=False) for n in [256,512,1024,2048,4096]],
        largest_verified_available=dict(X=0,Y=0),inventory_counts=dict(absolute=len(absolute),indirect=len(indirect),loops=len(loops),immediate_register_values=len(pointers)),
        caveats=['listing inventory is exhaustive for canonical rows, not reachable instruction proof',
                 'unknown indirect intervals deliberately cover all 24-bit addresses',
                 'lexical origins do not survive control flow as semantic guarantees',
                 'no absence-of-access or zero-filled-space proof is used'],
        worker=dict(queue='X shared starting 30002; producer endpoint X:30000',fetch='P:125 X:(r0), r0 from queued word, unrestricted 24-bit value',
                    result='P:126 X queue replacement; queue extent unbounded without producer endpoint proof',private_Y='[0,16) wrapper; no normal worker Y RAM table fetch found',
                    core_correlation='shared alias known under device map; private low X/Y not automatically core0 memory'),
        host=dict(ordinary_address_mask='0x7FFF',selector='bit15: Y if set',candidate_addresses_accepted=True,
                  fixed_callers_complete=False,normal_candidate_call_proven=False,
                  mailbox_selector6='P:1CB2..1CB5 copies 512 X:C00 words into host-derived Y:r5, no destination range check'),
        extension=dict(status='LIKELY POSSIBLE conditionally; ARM count/transport VERIFIED',payload_words=0x4000,total_stream_words=0x4002,
                    bytes=3*0x4002,hypothetical_ARM_end_offset=0x1f0+3*0x4002,next_stream_offset=0x8110,
                    caveat='physical core/mode/ROM acceptance and ARM data relocation not proven; no patch'),
        costs=dict(selected_major_loop_subtotal=4355,selected_post_major_loops=1408,post_result_copy=64,
                    finite_whole_service_bound=None,finite_sync_wait_bound=None,nominal_total_period_cycles=163840),
        gate=dict(RAM512='NOT-YET-DETERMINED',RAM1024='NOT-YET-DETERMINED',extension='NOT-YET-DETERMINED',
                  clobber='NOT-YET-DETERMINED',bypass='NOT-YET-DETERMINED',window='NOT-YET-DETERMINED',comparison='NOT-YET-DETERMINED'))
    out.mkdir(parents=True,exist_ok=False)
    for filename,data in [('absolute-intervals.csv',absolute),('indirect-origins.csv',indirect),('hardware-loops.csv',loops),
                          ('pointer-immediates.csv',pointers),('reachable-intervals.csv',intervals),('initialized-values.csv',initialized)]:save(out/filename,csv_text(data))
    save(out/'seam-clobbers.csv',csv_text([dict(state=s,live=live,must_preserve=preserve,restored_later=restored,evidence=ev) for s,live,preserve,restored,ev in clobbers]))
    save(out/'ownership.json',json.dumps(summary,indent=2)+'\n');save(out/'witnesses.json',json.dumps(witnesses,indent=2)+'\n')
    save(out/'host-call-candidates.json',json.dumps(hostcalls,indent=2)+'\n')
    save(out/'region-ledger.csv',csv_text([dict(space=s,start=f'0x{lo:X}',end_exclusive=f'0x{hi:X}',role=role,status=status) for s,lo,hi,role,status in REGIONS]))
    windows=[(0x156,0x1b4),(0x759,0x7c4),(0x980,0xaab),(0x1c53,0x1d41),(0x2779,0x27f8)]
    save(out/'reviewed-paths.asm','\n'.join(r['line'] for pc,r in rows.items() if any(lo<=pc<hi for lo,hi in windows))+'\n')
    print(json.dumps(summary['inventory_counts'],indent=2))

if __name__=='__main__':main()
