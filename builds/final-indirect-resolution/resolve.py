"""Focused static callback expansion. UNKNOWN edges never establish allocation absence."""
import ast,collections,json,csv
from inspect_bytes import A,O,listing
from capstone.arm import *
P=O.parent/'final-two-check-closure'
old=json.loads((P/'reachability.json').read_text())
tree=ast.parse((P/'reachability.py').read_text())
node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='manual' for t in n.targets))
manual=eval(compile(ast.Expression(node.value),'<old selected bindings>','eval'),{'A':A})
content=[0x803a478,0x803c90c,0x803c968,0x803c978,0x803c9a8,0x803c9c8,0x803cc6a]
manual[0x8022e22]=(content,'72-byte Content descriptors: callback+3C; builders3CA52/499AC/499E8, publishers3CBxx/3CCxx; seven nonzero stock publisher targets')
manual[0x80223c0]=([0x801da70],'RTC callback200069F0 set by22308; sole direct caller1DA62 supplies1DA71')
manual[0x8051936]=([0x8047830],'global200069E8 set by51968 from477DE ADR target47831')
manual[0x80519ac]=([0x8047828],'global200069E0 set by5193C from477D4 ADR target47829')
manual[0x803cb16]=([0x802d43c],'global200069B8 set by3CB1A at2D408 with ADR2D43D')
manual[0x803cb34]=([0x802d444],'global200069C0 set by3CB38 at2D412 with ADR2D445')
manual[0x803be48]=([0x8029a34],'global200069B0 set by3BE36 from sole caller29984, ADR29980 ->29A35')
manual[0x80240d8]=([0x8024e00],'Storage descriptor+10: fixed wrappers zero it; async241F0 sole caller24DB0 supplies ADR24DA2 ->24E01;26BDC template callback checked separately')
# Fixed secondary timer callbacks supplied in R3 to3C432; reject an unresolved
# producer rather than letting a saved callback value become a static bound.
idx=json.loads((O/'call-index.json').read_text())
timer_publishers=[]
for row in idx['0x803c432']:
    at=int(row['at'],16);found=None
    for pc in range(at-2,max(at-72,0x8010000)-1,-2):
        i=next(A.md.disasm(A.read(pc,4),pc,count=1),None)
        if i is None or i.address+i.size>at:continue
        if i.id in (ARM_INS_BL,ARM_INS_BLX):break
        try:written=i.regs_access()[1]
        except Exception:continue
        if ARM_REG_R3 not in written:continue
        if i.cc not in (ARM_CC_AL,ARM_CC_INVALID):break
        if i.id==ARM_INS_LDR and i.operands[1].type==ARM_OP_MEM and i.operands[1].mem.base==ARM_REG_PC:
            source=((pc+4)&~3)+i.operands[1].mem.disp;found=(A.word(source),hex(source));break
        if i.id in (ARM_INS_ADD,ARM_INS_ADDW) and i.operands[1].type==ARM_OP_REG and i.operands[1].reg==ARM_REG_PC and i.operands[2].type==ARM_OP_IMM:
            found=(((pc+4)&~3)+i.operands[2].imm,hex(pc));break
        if i.id in (ARM_INS_MOV,ARM_INS_MOVW) and i.operands[1].type==ARM_OP_IMM:
            found=(i.operands[1].imm,hex(pc));break
        break
    timer_publishers.append(dict(callsite=hex(at),source=found[1] if found else 'UNKNOWN',callback=hex(found[0]) if found else 'UNKNOWN'))
    if at in (0x802a984,0x804d2d8,0x804e364):
        # Exact boundary from function2A95E: the generic backwards halfword
        # search encountered a false instruction in the literal LDR's second half.
        boundary={0x802a984:0x802a97a,0x804d2d8:0x804d2ca,0x804e364:0x804e358}[at]
        p=next(A.md.disasm(A.read(boundary,4),boundary,count=1))
        assert p.operands[0].reg==ARM_REG_R3
        if p.id==ARM_INS_LDR:
            literal=((p.address+4)&~3)+p.operands[1].mem.disp
            value=A.word(literal)
        else:
            assert p.id in (ARM_INS_ADDW,ARM_INS_ADD) and p.operands[1].reg==ARM_REG_PC
            literal=boundary;value=((boundary+4)&~3)+p.operands[2].imm
        timer_publishers[-1].update(source=hex(literal),callback=hex(value))
    assert timer_publishers[-1]['callback']=='UNKNOWN' or int(timer_publishers[-1]['callback'],16)==0 or (int(timer_publishers[-1]['callback'],16)&1 and 0x8010000<int(timer_publishers[-1]['callback'],16)<0x8075100)
timer_targets=sorted({int(r['callback'],16)&~1 for r in timer_publishers if r['callback']!='UNKNOWN' and int(r['callback'],16)!=0})
if all(r['callback']!='UNKNOWN' for r in timer_publishers):
    manual[0x803c42e]=(timer_targets,'secondary timer table200065C4 written only by3C432+R3; all17 direct publisher R3 values statically fixed')
# These enlarge coverage; their lifetime writer/alias closure is NOT asserted.
partial={0x801c8ae:([0x801eb30,0x801ebac,0x801ebb0,0x801ebfa,0x801ec14,0x8023ce8,0x80518f4,0x8051916,0x803cb0a,0x803cb26,0x8035680],
    'subscriber+8+4*i;251E8 plus inline5193C/3CB42/356B0; fixed initialization targets recovered, alias-complete writer closure UNKNOWN')}
timer=set()
for obj in (0x20000354,0x20000360,0x2000036c):
    count=A.read(obj,1)[0];base=A.word(obj+8)
    assert count<32
    for k in range(count):
        target=A.word(base+28*k+12)
        if target&1 and 0x8010000<target<0x8075100:timer.add(target&~1)
timer.update((0x80248b4,0x803c410,0x8056154,0x80561e4,0x805834a))
for site in (0x801e51e,0x8023528):partial[site]=(sorted(timer),'timer slot+0C;1E538 copy,1E52C writable-slot aliases; recovered targets union includes saved three timer registries and fixed live setters; complete alias writers UNKNOWN')
roots={k:int(v,16) for k,v in old['roots'].items()}
for target in content:roots[f'Content publisher target {target:08X}']=target
allocators={0x801cfa4,0x801d7d0,0x801d7d8,0x801d808,0x8037380}
def run(seed):
    q=collections.deque((v,[],k) for k,v in seed.items());seen=set();sites={};switches={};alloc=[];parents={}
    def chain(pc):
        path=[];used=set()
        while pc in parents and pc not in used:
            used.add(pc);path.append(hex(pc));pc=parents[pc]
        return [hex(pc)]+list(reversed(path))
    while q:
        pc,trace,root=q.popleft()
        if pc in seen or not 0x8010000<=pc<0x8010000+len(A.image):continue
        seen.add(pc);i=next(A.md.disasm(A.read(pc,4),pc,count=1),None)
        if i is None:continue
        def edge(t):
            t&=~1
            if t not in parents:parents[t]=pc
            q.append((t,(trace+[i])[-18:],root))
        if pc in allocators:
            alloc.append(dict(target=hex(pc),root=root,chain=chain(pc),classification='UNKNOWN',request_size='UNKNOWN until caller argument resolved'));continue
        m=i.mnemonic;op=i.op_str;unconditional=i.cc in (ARM_CC_AL,ARM_CC_INVALID)
        if i.id in (ARM_INS_TBB,ARM_INS_TBH):
            mem=i.operands[0].mem;reg=i.reg_name(mem.index);bound=None
            for p in reversed(trace[-12:]):
                if p.id==ARM_INS_CMP and len(p.operands)==2 and p.operands[0].type==ARM_OP_REG and p.reg_name(p.operands[0].reg)==reg and p.operands[1].type==ARM_OP_IMM:
                    bound=p.operands[1].imm;break
            if bound is not None and 0<=bound<256 and mem.base==ARM_REG_PC:
                width=1 if i.id==ARM_INS_TBB else 2;base=pc+4
                ts=[base+2*int.from_bytes(A.read(base+k*width,width),'little') for k in range(bound+1)]
                switches[pc]=dict(source=hex(base),targets=list(map(hex,ts)),status='local CMP-bound candidate')
                for t in ts:edge(t)
            else:sites[pc]=dict(callsite=hex(pc),source=op,targets=[],status='UNKNOWN',registration='No finite local switch bound',root=root)
            continue
        is_return=(i.id==ARM_INS_BX and op=='lr') or (i.id==ARM_INS_POP and 'pc' in op) or (i.id==ARM_INS_LDR and op.startswith('pc, [sp]'))
        if is_return:
            if not unconditional:edge(pc+i.size)
            continue
        is_indirect=(i.id in (ARM_INS_BLX,ARM_INS_BX) and i.operands[0].type!=ARM_OP_IMM) or (i.id==ARM_INS_LDR and op.startswith('pc,'))
        if is_indirect:
            ts,why=manual.get(pc,partial.get(pc,([],None)))
            status='BOUNDED NORMAL INITIALIZED TYPES' if pc in manual else 'UNKNOWN'
            source='; '.join(f'{p.address:08X} {p.mnemonic} {p.op_str}' for p in trace[-10:])
            sites[pc]=dict(callsite=hex(pc),source=source,registration=why or 'Object/argument register provenance: no complete constructor-to-use alias binding established',targets=list(map(hex,ts)),status=status,root=root,can_reach_allocator='UNKNOWN until target and downstream summaries close',maximum_request='UNKNOWN',classification='UNKNOWN')
            for t in ts:edge(t)
            if i.id in (ARM_INS_BX,ARM_INS_LDR) and unconditional:continue
        if i.id in (ARM_INS_BL,ARM_INS_BLX,ARM_INS_B) and i.operands[0].type==ARM_OP_IMM:
            edge(i.operands[0].imm)
            if i.id==ARM_INS_B and unconditional:continue
        elif i.id in (ARM_INS_CBZ,ARM_INS_CBNZ):edge(i.operands[-1].imm)
        edge(pc+i.size)
    return dict(nodes=len(seen),indirect_sites=list(sites.values()),switches={hex(k):v for k,v in switches.items()},allocator_endpoints=alloc)
result=run(roots)
summaries={}
all_targets=set(content)
for row in result['indirect_sites']:all_targets.update(int(x,16) for x in row.get('targets',[]))
for target in sorted(all_targets):
    s=run({f'callback {target:08X}':target});unknown=[x['callsite'] for x in s['indirect_sites'] if x['status']=='UNKNOWN']
    summaries[hex(target)]=dict(nodes=s['nodes'],allocator_endpoints=s['allocator_endpoints'],unknown_sites=unknown,classification='UNKNOWN' if unknown or s['allocator_endpoints'] else 'SAFE',max_request='UNKNOWN' if unknown or s['allocator_endpoints'] else 0)
for row in result['indirect_sites']:
    ss=[summaries[x] for x in row.get('targets',[])]
    if row['status']!='UNKNOWN' and ss and all(x['classification']=='SAFE' for x in ss):
        row.update(can_reach_allocator=False,maximum_request=0,classification='SAFE')
result.update(candidate_sha256=old['candidate_sha256'],roots={k:hex(v) for k,v in roots.items()},content_targets=list(map(hex,content)),content_summaries={hex(t):summaries[hex(t)] for t in content},target_summaries=summaries,secondary_timer_publishers=timer_publishers,complete=False,verdict='UNQUALIFIED',method='Conditional call IDs preserved; stack epilogues excluded from callback census. Known partial targets expand coverage without becoming lifetime bounds. Exact-byte static reasoning; no dynamic absence claim.')
(O/'resolution.json').write_text(json.dumps(result,indent=2)+'\n')
fields=['callsite','source','registration','targets','status','root','can_reach_allocator','maximum_request','classification']
with (O/'indirect-ledger.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for row in result['indirect_sites']:w.writerow({k:row.get(k,'UNKNOWN') for k in fields})
print('nodes',result['nodes'],'indirect sites',len(result['indirect_sites']),'UNKNOWN',sum(x['status']=='UNKNOWN' for x in result['indirect_sites']),'allocator endpoints',len(result['allocator_endpoints']))
print('secondary timer publishers',len(timer_publishers),'unresolved',sum(r['callback']=='UNKNOWN' for r in timer_publishers),'summarized targets',len(summaries))
