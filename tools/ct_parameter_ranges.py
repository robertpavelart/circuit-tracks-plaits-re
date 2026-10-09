#!/usr/bin/env python3
"""Static constant propagation of recovered normal parameter callbacks.

Not a firmware emulator. Values used for sample/parameter arithmetic are opaque;
only address arithmetic, stack arguments and finite bank/slot premises are
propagated. Reviewed helper summaries expose destinations, never transmit data.
Unknown destinations/unsupported control flow are exported, not assumed safe.
"""
import argparse, csv, io, json, struct
from collections import deque
from pathlib import Path
from ct_static import ROOT, BASE, BIN_HASH, SYX_HASH, sha, save, engine
from ct_phase4_trace import arm_evidence
import ct_fw_tool

BANK_TABLE=0x805a384
SLOT_TABLE=0x8021478
TABLES=((BANK_TABLE,16,'bank'),(SLOT_TABLE,5,'slot'),
        (0x8021534,4,'namespace10'),(0x805b3b0,10,'namespace20'),(0x80215b8,3,'namespace21'))
# Function summaries: destination arguments only; numeric results stay unknown.
WRITERS={0x80292f8:['r2'],0x8028132:['r2','r3'],0x802819c:['r1','r2'],
 0x8028204:['r2','r3'],0x8028336:['r2','r3'],0x80283d8:['stack0','stack4','stack8','stack12','stack16'],
 0x8028430:['r3','stack0','stack4'],0x80284b2:['r1','r2'],
 0x8027de0:['stack0','stack4'],0x8027f34:['r3','stack0'],0x8027fa4:['stack0','stack4','stack8'],
 0x8028096:['r3','stack0'],0x8028378:['r2'],0x80284aa:['r2'],0x8028870:['r2'],0x80277d0:['r2'],
 0x802829c:['r2']}

def csvtext(rows):
    s=io.StringIO();keys=sorted(set().union(*(r.keys() for r in rows))) if rows else ['status']
    w=csv.DictWriter(s,fieldnames=keys);w.writeheader();w.writerows(rows);return s.getvalue()

def run(root,bank,slot,arm,cs):
    from capstone.arm import ARM_OP_IMM,ARM_OP_REG,ARM_OP_MEM,ARM_CC_AL,ARM_CC_INVALID
    from capstone.arm import ARM_SFT_LSL,ARM_SFT_LSR,ARM_SFT_ASR
    initial={f'r{i}':None for i in range(13)};initial.update(sp=0x70000000,lr=None)
    todo=deque([(root,initial,{},None)]);seen=set();writes=[];issues=[];calls=[]
    def reg(o):
        n=cs.reg_name(o.reg if hasattr(o,'reg') else o)
        return {'sb':'r9','sl':'r10','fp':'r11','ip':'r12'}.get(n,n)
    def signed(v,bits=32):return v-(1<<bits) if v&(1<<(bits-1)) else v
    def shift(v,kind,n):
        if v is None:return None
        if kind==ARM_SFT_LSL:return (v<<n)&0xffffffff
        if kind==ARM_SFT_LSR:return v>>n
        if kind==ARM_SFT_ASR:return (signed(v)>>n)&0xffffffff
        return v if not kind else None
    def value(o,r):
        v=(o.imm&0xffffffff) if o.type==ARM_OP_IMM else r.get(reg(o)) if o.type==ARM_OP_REG else None
        return shift(v,o.shift.type,o.shift.value)
    def address(o,r,pc):
        bn=cs.reg_name(o.mem.base); b=((pc+4)&~3) if bn=='pc' else r.get(reg(o.mem.base))
        if b is None:return None
        idx=0
        if o.mem.index:
            idx=r.get(reg(o.mem.index));idx=shift(idx,o.shift.type,o.shift.value)
            if idx is None:return None
        return (b+idx+o.mem.disp)&0xffffffff
    def load(a,n,mem):
        if a is None:return None
        if a==0x20006800 and n==1:return bank
        if a==0x20006801 and n==1:return slot
        if BASE<=a and a+n<=BASE+len(arm):return int.from_bytes(arm[a-BASE:a-BASE+n],'little')
        if all(a+i in mem and mem[a+i] is not None for i in range(n)):
            return sum(mem[a+i]<<(8*i) for i in range(n))
        return None
    def store(a,n,v,mem):
        if a is not None and 0x6fff0000<=a<0x70010000:
            for i in range(n):mem[a+i]=None if v is None else (v>>(8*i))&255
    def emit(pc,target,r,m):
        for arg in WRITERS[target]:
            v=load(r.get('sp')+int(arg[5:]),4,m) if arg.startswith('stack') and r.get('sp') is not None else r.get(arg)
            writes.append({'root':f'0x{root:08X}','bank':bank,'slot':slot,'site':f'0x{pc:08X}',
               'helper':f'0x{target:08X}','argument':arg,'encoded':v,
               'space':None if v is None else ('Y' if v&0x8000 else 'X'),
               'address':None if v is None else v&0x7fff,'words':1,
               'status':'UNRESOLVED destination' if v is None else 'VERIFIED conditional finite-domain address propagation'})
    steps=0
    while todo:
        pc,r,m,flags=todo.popleft();key=(pc,tuple(sorted(r.items())),tuple(sorted(m.items())),flags)
        if key in seen:continue
        seen.add(key);steps+=1
        if steps>1000:
            issues.append({'root':hex(root),'pc':hex(pc),'reason':'state limit; no absence claim'});break
        if not (0x8027094<=pc<0x8029000):
            if pc in WRITERS:emit(pc,pc,r,m)
            else:issues.append({'root':hex(root),'pc':hex(pc),'reason':'unreviewed tail target'})
            continue
        seq=list(cs.disasm(arm[pc-BASE:pc-BASE+4],pc,count=1))
        if not seq:
            issues.append({'root':hex(root),'pc':hex(pc),'reason':'decode failure'});continue
        i=seq[0];mn=i.mnemonic.split('.')[0];ops=i.operands; nxt=pc+i.size
        # No branch-dependent parameter-data value is assumed concrete.
        branch=mn in ('b','bl','bx','blx','cbz','cbnz') or (mn.startswith('b') and mn not in ('bic','bics','bfi','bfc'))
        if branch:
            imm=[o.imm for o in ops if o.type==ARM_OP_IMM]
            if mn in ('bx','blx'):
                if mn=='bx' and ops and reg(ops[0])=='lr':continue
                issues.append({'root':hex(root),'pc':hex(pc),'reason':'indirect branch/call'});continue
            target=imm[-1] if imm else None
            if mn.startswith('bl') and mn not in ('blt','ble','bls'):
                calls.append({'root':hex(root),'site':hex(pc),'target':hex(target)})
                if target in WRITERS:emit(pc,target,r,m)
                elif 0x80292dc<=target<0x80296e0:
                    issues.append({'root':hex(root),'pc':hex(pc),'reason':f'unreviewed SHI helper {target:X}'})
                for rr in ('r0','r1','r2','r3','r12','lr'):r[rr]=None
                todo.append((nxt,r,m,None));continue
            conditional=i.cc not in (ARM_CC_AL,ARM_CC_INVALID) or mn in ('cbz','cbnz')
            take=None
            if mn in ('cbz','cbnz'):
                v=value(ops[0],r)
                if v is not None:take=(v==0) if mn=='cbz' else (v!=0)
            elif flags is not None:
                left,right=flags
                checks={'beq':left==right,'bne':left!=right,'blt':signed(left)<signed(right),
                  'ble':signed(left)<=signed(right),'bge':signed(left)>=signed(right),'bgt':signed(left)>signed(right),
                  'blo':left<right,'bhs':left>=right,'bls':left<=right,'bhi':left>right}
                take=checks.get(mn)
            if not conditional or take is not False:todo.append((target,dict(r),dict(m),flags))
            if conditional and take is not True:todo.append((nxt,r,m,flags))
            continue
        if mn.startswith('pop'):
            if r['sp'] is None:issues.append({'root':hex(root),'pc':hex(pc),'reason':'unknown SP'});continue
            ret=False
            for o in ops:
                rr=reg(o);v=load(r['sp'],4,m);r['sp']+=4
                if rr=='pc':ret=True
                else:r[rr]=v
            if not ret:todo.append((nxt,r,m,flags))
            continue
        if mn.startswith('push'):
            regs=[reg(o) for o in ops];r['sp']-=4*len(regs)
            for k,rr in enumerate(regs):store(r['sp']+4*k,4,r.get(rr),m)
            todo.append((nxt,r,m,flags));continue
        if mn.startswith('it') or mn=='nop':todo.append((nxt,r,m,flags));continue
        old=dict(r); dst=reg(ops[0]) if ops and ops[0].type==ARM_OP_REG else None
        conditional=i.cc not in (ARM_CC_AL,ARM_CC_INVALID)
        if mn.startswith('cmp'):
            v=[value(o,r) for o in ops];flags=tuple(v) if len(v)==2 and None not in v else None
        elif mn.startswith(('str','ldr')) and len(ops)>=2 and ops[1].type==ARM_OP_MEM:
            a=address(ops[1],r,pc)
            n=1 if mn.startswith(('ldrb','ldrsb','strb')) else 2 if mn.startswith(('ldrh','ldrsh','strh')) else 4
            if mn.startswith('str'):store(a,n,r.get(dst),m)
            else:
                v=load(a,n,m)
                if v is not None and mn.startswith(('ldrsb','ldrsh')):v=signed(v,n*8)&0xffffffff
                r[dst]=v
            if i.writeback:
                bn=reg(ops[1].mem.base)
                if len(ops)>2 and ops[-1].type==ARM_OP_IMM:
                    r[bn]=None if r.get(bn) is None else (r[bn]+ops[-1].imm)&0xffffffff
                else:r[bn]=a
        elif dst is not None:
            v=None; args=[value(o,r) for o in ops[1:]]
            if mn.startswith('movt') and old.get(dst) is not None and args[0] is not None:v=(old[dst]&0xffff)|(args[0]<<16)
            elif mn.startswith(('movw','movs','mov')) and len(args)==1:v=args[0]
            elif mn in ('uxtb','uxth','sxtb','sxth') and args and args[0] is not None:
                bits=8 if mn.endswith('b') else 16;v=args[0]&((1<<bits)-1)
                if mn.startswith('sx'):v=signed(v,bits)&0xffffffff
            elif mn.startswith(('add','sub','rsb','mul','smulbb','lsl','lsr','asr','and','orr','eor','bic')):
                if len(args)==1:args=[old.get(dst),args[0]]
                if len(args)>=2 and None not in args:
                    a,b=args[:2]
                    if mn.startswith('add'):v=a+b
                    elif mn.startswith('sub'):v=a-b
                    elif mn.startswith('rsb'):v=b-a
                    elif mn.startswith('smulbb'):v=signed(a&0xffff,16)*signed(b&0xffff,16)
                    elif mn.startswith('mul'):v=a*b
                    elif mn.startswith('lsl'):v=a<<b
                    elif mn.startswith('lsr'):v=a>>b
                    elif mn.startswith('asr'):v=signed(a)>>b
                    elif mn.startswith('and'):v=a&b
                    elif mn.startswith('orr'):v=a|b
                    elif mn.startswith('eor'):v=a^b
                    elif mn.startswith('bic'):v=a&~b
            r[dst]=None if v is None else v&0xffffffff
            if i.update_flags:flags=(r[dst],0) if r[dst] is not None and mn.startswith(('sub','add')) else None
        # Conditional data transfers with unknown predicates lose differing values.
        if conditional:
            for rr in r:
                if old.get(rr)!=r[rr]:r[rr]=None
        todo.append((nxt,r,m,flags))
    return writes,issues,calls

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True)
    out=Path(p.parse_args().output_dir).resolve()
    if out.exists():raise SystemExit('Choose a fresh output directory')
    if out==ROOT/'original' or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes();syxp=ROOT/'original/circuittracks-firmware-4486.syx'
    assert sha(arm)==BIN_HASH and sha(syxp.read_bytes())==SYX_HASH
    info=ct_fw_tool.decode_syx(syxp);assert info['firmware']==arm
    assert ct_fw_tool.build_syx(syxp,arm)==syxp.read_bytes()
    cs=engine();tables=[];writes=[];issues=[];calls=[]
    for table,count,kind in TABLES:
        for idx in range(count):
            ptr=struct.unpack_from('<I',arm,table-BASE+idx*4)[0];root=ptr&~1
            tables.append({'table':hex(table),'kind':kind,'index':idx,'pointer':hex(ptr),'function':hex(root)})
            if root==0x8027a10:
                for b in (0,1):
                    for j in range(20):
                        for off in (0,1,2,4):writes.append({'root':f'0x{root:08X}','bank':b,'slot':None,
                          'site':'0x08027A5E/72/80/AB8','helper':'0x080292F8','argument':f'record{j}+{off}',
                          'encoded':0x2fb+0x172*b+5*j+off,'space':'X','address':0x2fb+0x172*b+5*j+off,
                          'words':1,'status':'VERIFIED reviewed counted loop; local b0/1 premise'})
                        writes.append({'root':f'0x{root:08X}','bank':b,'slot':None,'site':'0x08027AD6',
                          'helper':'0x080292F8','argument':f'tail{j}','encoded':0x3d0+0x172*b+j,
                          'space':'X','address':0x3d0+0x172*b+j,'words':1,'status':'VERIFIED reviewed counted loop; local b0/1 premise'})
                    writes.append({'root':f'0x{root:08X}','bank':b,'slot':None,'site':'0x08027AF0',
                          'helper':'0x080292F8','argument':'global','encoded':0x95,'space':'X','address':0x95,
                          'words':1,'status':'VERIFIED global word'})
                    for off in (0x2fa,0x35f):
                        writes.append({'root':f'0x{root:08X}','bank':b,'slot':None,'site':'0x08027AE4 -> 080286BC',
                          'helper':'0x080286BC','argument':f'conditional/deferred {off:X}',
                          'encoded':off+0x172*b,'space':'X','address':off+0x172*b,'words':1,
                          'status':'VERIFIED delegated address; conditional immediate fallback or later deferred dispatcher'})
                continue
            for b in (0,1):
                for s in (range(12) if kind=='slot' else (0,)):
                    ww,uu,cc=run(root,b,s,arm,cs);writes+=ww;issues+=uu;calls+=cc
    # Fit affine address formulas, then verify against every propagated point.
    groups={};formulas=[]
    for w in writes:
        key=(w['root'],w['site'],w['helper'],w['argument'])
        groups.setdefault(key,[]).append(w)
    for (root,site,helper,arg),ww in groups.items():
        known=[w for w in ww if w['encoded'] is not None]
        if not known:continue
        points={(w['bank'],w['slot'] or 0):w['encoded']&0xffff for w in known}
        base=points[(0,0)];bd=(points.get((1,0),base)-base)&0xffff
        sd=(points.get((0,1),base)-base)&0xffff
        fits=all(((base+bd*b+sd*s)&0xffff)==v for (b,s),v in points.items())
        formulas.append({'root':root,'site':site,'helper':helper,'argument':arg,
          'encoded_base':hex(base),'bank_stride':hex(bd),'slot_stride':hex(sd),
          'formula':f'encode16({hex(base)} + {hex(bd)}*bank + {hex(sd)}*slot)' if fits else 'UNRESOLVED non-affine finite set',
          'bank_domain':'0,1','slot_domain':'0..11' if any(w['slot'] not in (None,0) for w in known) else 'unused',
          'words':1,'space':known[0]['space'],'minimum':hex(min(w['address'] for w in known)),
          'maximum':hex(max(w['address'] for w in known)),
          'status':'VERIFIED finite-domain formula with reviewed helper/domain premises' if fits else 'UNRESOLVED'})
    for t in tables:
        ww=[w for w in writes if int(w['root'],16)==int(t['function'],16)]
        t.update({'normal_reachability':'recovered normal serialized callback path; BOOT/reentry separate',
            'selector_domain':'0,1 at dispatch' if t['kind']=='bank' else '0,1; slot0..11 at dispatch' if t['kind']=='slot' else t['kind'].replace('namespace','0x')+' parameter context; bank byte irrelevant to recovered destinations',
            'selector_read':'none; BX LR stub' if t['kind']=='bank' and t['index']>=10 else
                            'none; fixed global destinations' if t['function']=='0x8027afa' else 'none; context-specific constants' if t['kind'].startswith('namespace') else '20006800',
            'DSP_helpers':','.join(sorted({w['helper'] for w in ww})),
            'destination_constructors':t['function'] if ww else 'none',
            'word_count_per_callback':len({(w['site'],w['argument']) for w in ww}),
            'transfer_width':'one 24-bit word per sink;27A10 own101 plus2 delegated possible sinks'})
    # Exact finite destination sets and contiguous unions, not their enclosing hull.
    intervals=[]
    for space in ('X','Y'):
        addresses=sorted({w['address'] for w in writes if w['space']==space and w['address'] is not None})
        start=previous=None
        for a in addresses+[None]:
            if previous is not None and (a is None or a!=previous+1):
                intervals.append({'space':space,'start':hex(start),'end_exclusive':hex(previous+1),
                   'words':previous+1-start,'status':'recovered callback destination union; unknown records remain separate'})
                start=None
            if a is not None:
                if start is None:start=a
                previous=a
    provenance=[]
    for path in sorted((ROOT/'builds/phase9').rglob('*.asm')):
        provenance.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes()),
                           'checked_instructions':arm_evidence(path,arm)})
    summary={'mode':'static only','BIN_SHA256':sha(arm),'SYX_SHA256':sha(syxp.read_bytes()),
      'script_SHA256':sha(Path(__file__).read_bytes()),'roundtrip_identical':True,
      'premises':'recovered serialized callback paths set bank0/1; per-slot dispatcher sets slot0..11; helper summaries reviewed separately',
      'writes':len(writes),'unknown_destinations':sum(w['address'] is None for w in writes),
      'unsupported_paths':len(issues),'tables':tables,
      'limit':'not all ARM host traffic; no persistent DSP availability proof; opaque numeric helper side effects need reviewed summaries'}
    save(out/'callback-tables.csv',csvtext(tables));save(out/'parameter-writes.csv',csvtext(writes))
    save(out/'constructor-formulas.csv',csvtext(formulas))
    save(out/'parameter-intervals.csv',csvtext(intervals));save(out/'unsupported-paths.csv',csvtext(issues))
    save(out/'callback-call-edges.csv',csvtext(calls));save(out/'summary.json',json.dumps(summary,indent=2)+'\n')
    save(out/'evidence-integrity.json',json.dumps(provenance,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('writes','unknown_destinations','unsupported_paths')},indent=2))

if __name__=='__main__':main()
