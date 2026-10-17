"""Conservative roots and indirect-source census; unresolved targets stay UNKNOWN."""
import json,collections,re
import byte_audit as A
from capstone.arm import ARM_OP_IMM,ARM_OP_REG,ARM_OP_MEM,ARM_REG_PC
O=A.O;R=A.R
targets={0x801cfa4,0x801d7d0,0x801d7d8,0x801d808,0x8037380}
roots={'Main post-READY loop':0x801d5a4,'UI loop':0x801d696,'Storage loop':0x805769c,'Content loop':0x8022ad0,'Idle hook':0x801d760,'Main parser':0x801eb30,'Main deferred queue':0x801cff4,'diagnostic':0x806f900,'BOT pump':0x801f37c}
for off in range(8,0x1c8,4):
 p=A.word(0x8010000+off)
 if p&1 and 0x8010000<p<0x8059990:roots[f'vector+{off:03x}']=p&~1
registry=[]
for obj in (0x20000354,0x20000360):
 count=A.read(obj,1)[0];base=A.word(obj+8)
 assert count<32
 for k in range(count):
  p=A.word(base+28*k+12);registry.append(dict(kind='timer',object=hex(obj),slot=k,source=hex(base+28*k+12),saved_target=hex(p),active=A.read(base+28*k+8,1)[0]))
  if p&1 and 0x8010000<p<0x8059990:roots[f'timer {obj:08x}/{k} saved callback']=p&~1
for table,name,n in [(0x805a444,'MIDI child',12),(0x805a480,'BOT child',12),(0x805b60c,'port type',6),(0x20003788,'SCSI backend',8),(0x805b180,'SD backend',8),(0x805b1ac,'NOR backend',8)]:
 for k in range(n):
  p=A.word(table+4*k)
  if p&1 and 0x8010000<p<0x8059990:roots[f'{name} slot{k*4:x}']=p&~1
manual={
 0x801d010:([0x8022e08],'Main deferred queue: six Content publishers37310 all install thunk22E09; inner payload callback remains separate UNKNOWN'),
 0x8035698:([0x802096c],'UI callback global200069A8, installed by20906 with fixed target2096D'),
 0x8020bca:([0x8035a50],'three registered ports -> vtable805B60C+14'),
 0x8020d1a:([0x8035a50],'same port vtable+14'),0x8020d34:([0x8035a28],'same port vtable+10'),0x8020d72:([0x80359ce],'same port vtable+C'),
 0x8020d28:([0x801be78],'router+1C registered sleep/yield function'),
 0x803b49e:([0x8057e44],'SCSI table20003788+8 ready'),0x803b594:([0x8057e44],'same ready'),0x803b5b2:([0x8057e48],'same protection+C'),0x803b52e:([0x8057e88],'same read+10'),0x803b658:([0x8057ef4],'same write+14'),0x8058f02:([0x8057fb0],'same max LUN+18'),
 0x8024086:([A.word(0x805b180+8)&~1,A.word(0x805b1ac+8)&~1],'Storage op0: SD/NOR backend vtable+8'),
 0x8024096:([0x801abc0,0x8022f94],'Storage op1: SD/NOR backend read+C'),
 0x80240b2:([A.word(0x805b180+16)&~1,0x8022fdc],'Storage op2 backend write+10'),
 0x80240c2:([A.word(0x805b180+24)&~1,0x8023078],'Storage op3 backend erase+18'),
 0x80240ce:([A.word(0x805b180+28)&~1,0x80230f8],'Storage op4 backend flush+1C'),
}
def ins(pc):return next(A.md.disasm(A.read(pc,4),pc,count=1),None)
queue=collections.deque((pc,[],name) for name,pc in roots.items());seen=set();indirect={};tables={};allocations={};edges=[];parents={}
while queue:
 pc,trace,root=queue.popleft()
 if pc in seen or not 0x8010000<=pc<0x8010000+len(A.image):continue
 seen.add(pc);i=ins(pc)
 if not i:continue
 line=f'{pc:08X}: {i.mnemonic} {i.op_str}';history=(trace+[i])[-16:]
 def add(t,kind):
  t&=~1
  if t not in parents:parents[t]=(pc,kind)
  edges.append((pc,t,kind));queue.append((t,history,root))
 if pc in targets:
  allocations[pc]=dict(target=hex(pc),root=root,path_tail=[f'{v.address:08X}: {v.mnemonic} {v.op_str}' for v in history],request_bytes='UNKNOWN unless caller argument resolved',context='root-dependent',after_READY='possible conservative root path; predicates not all resolved',during_geometry='UNKNOWN',during_authorization='UNKNOWN',while_raw_pending='UNKNOWN');continue
 m=i.mnemonic;ops=i.op_str
 if m in ('tbb','tbh'):
  mem=i.operands[0].mem;reg=i.reg_name(mem.index);bound=None
  for prev in reversed(trace[-10:]):
   if prev.mnemonic.startswith('cmp') and len(prev.operands)==2 and prev.operands[0].type==ARM_OP_REG and prev.reg_name(prev.operands[0].reg)==reg and prev.operands[1].type==ARM_OP_IMM:
    bound=prev.operands[1].imm;break
  if bound is not None and 0<=bound<=255 and mem.base==ARM_REG_PC:
   base=pc+4;step=1 if m=='tbb' else 2;ts=[base+2*int.from_bytes(A.read(base+k*step,step),'little') for k in range(bound+1)]
   tables[pc]=dict(source=f'ROM[{base:08X}+{reg}*{step}]',range=[0,bound],targets=[hex(v) for v in ts],classification='bounded switch, preceding CMP/default branch retained')
   for t in ts:add(t,'switch')
  else:tables[pc]=dict(source=line,classification='UNKNOWN',reason='No local finite index bound established; no table bytes executed as instructions')
  continue
 indirect_call=(m.startswith('blx') and i.operands[0].type!=ARM_OP_IMM) or (m.startswith('bx') and ops!='lr') or (m.startswith('ldr') and ops.startswith('pc,'))
 if indirect_call:
  source='; '.join(f'{p.address:08X} {p.mnemonic} {p.op_str}' for p in trace[-7:])
  ts,why=manual.get(pc,([],None))
  indirect[pc]=dict(pc=hex(pc),instruction=m+' '+ops,root=root,function_pointer_source=why or source,allowed_targets=[hex(t) for t in ts],classification='BOUNDED under fixed registered-object invariants' if ts else 'UNKNOWN',reason=None if ts else 'Pointer loaded from argument/object/queue; complete writer/type or producer set not established. Saved execution is not a lifetime bound.')
  for t in ts:add(t,'bounded virtual callback')
  if m in ('bx','ldr','ldr.w'):continue
 if (m.startswith('pop') and 'pc' in ops) or (m=='bx' and ops=='lr'):continue
 if m in ('b','b.w','bl','blx') and i.operands[0].type==ARM_OP_IMM:
  add(i.operands[0].imm,'call' if m.startswith('bl') else 'branch')
  if m in ('b','b.w'):continue
 elif m.startswith('b') and i.operands and i.operands[-1].type==ARM_OP_IMM:add(i.operands[-1].imm,'conditional')
 elif m in ('cbz','cbnz'):add(i.operands[-1].imm,'conditional')
 add(pc+i.size,'next')
def chain(pc):
 out=[];s=set()
 while pc in parents and pc not in s:
  s.add(pc);out.append(hex(pc));pc=parents[pc][0]
 return list(reversed(out))
for pc,row in allocations.items():row['instruction_chain']=chain(pc)
report=dict(candidate_sha256='edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9',roots={k:hex(v) for k,v in roots.items()},saved_registrations=registry,instruction_nodes=len(seen),switches={hex(k):v for k,v in tables.items()},indirect_sites=list(indirect.values()),allocation_endpoints=list(allocations.values()),conclusion='D',complete=False,confidence='UNKNOWN',method='Conservative direct/bounded-switch/selected fixed-vtable closure. Unresolved sites are proof boundaries, not assumed harmless. Saved timer targets seed coverage but future timer writers remain to be bounded.')
(O/'reachability.json').write_text(json.dumps(report,indent=2)+'\n')
(O/'indirect-sources.tsv').write_text('PC\tclassification\tallowed_targets\tpointer_source\n'+''.join(f"{r['pc']}\t{r['classification']}\t{','.join(r['allowed_targets'])}\t{r['function_pointer_source']}\n" for r in indirect.values()))
print('roots',len(roots),'nodes',len(seen),'indirect',len(indirect),'unknown',sum(r['classification']=='UNKNOWN' for r in indirect.values()),'allocation targets',list(map(hex,allocations)))
