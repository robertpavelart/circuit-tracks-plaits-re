"""Read-only candidate audit. No builder, emulator, MIDI or transport imports."""
from pathlib import Path
import json,hashlib,struct,collections
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
from capstone.arm import ARM_OP_IMM,ARM_OP_MEM,ARM_REG_PC
O=Path(__file__).resolve().parent;R=O.parents[1];BASE=0x08010000
P=R/'builds/phase63-defect-closure';Q=R/'builds/phase61-final-geometry-gated-candidate'
sha=lambda b:hashlib.sha256(b).hexdigest()
image=(P/'circuittracks-nor-defect-closure-development.bin').read_bytes()
assert sha(image)=='edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9'
meta=json.loads((P/'construction.json').read_text());oldmeta=json.loads((Q/'construction.json').read_text())
base=(R/'builds/phase43-hardware-test-candidate/clean-sc35d8.bin').read_bytes()
old=(Q/'circuittracks-final-geometry-gated-nor-test.bin').read_bytes()
assert sha(base)==meta['source_sha256'];assert sha(old)==oldmeta['BIN_sha256']
owners=[]
for kind in ('components','trampolines'):
 for name,c in meta[kind].items():
  at=int(c['address'],16)-BASE;end=at+c['bytes'];assert sha(image[at:end])==c['sha256'];owners.append((at,end,kind+':'+name))
for p in meta['patches']:
 at=int(p['address'],16)-BASE;b=bytes.fromhex(p['after']);assert image[at:at+len(b)]==b;owners.append((at,at+len(b),'explicit patch:'+p['address']))
def owner(i):
 matches=[n for a,b,n in owners if a<=i<b]
 if matches:return matches[0]
 if 0x5b6cc<=i<0x5bc8c and image[i]==255:return 'retired diagnostic pool cleared to FF'
 if i>=len(base) and image[i]==255:return 'FF append padding'
 return 'UNEXPLAINED'
def diff(before):
 rows=[]
 for i,b in enumerate(image):
  if i<len(before) and before[i]==b:continue
  name=owner(i)
  if rows and rows[-1]['end_exclusive']==BASE+i and rows[-1]['owner']==name:rows[-1]['end_exclusive']+=1;rows[-1]['bytes']+=1
  else:rows.append(dict(start=BASE+i,end_exclusive=BASE+i+1,bytes=1,owner=name))
 return dict(changed_bytes=sum(x['bytes'] for x in rows),unexplained_bytes=sum(x['bytes'] for x in rows if x['owner']=='UNEXPLAINED'),ranges=rows)
diffs={'SC35D8_to_Phase63':diff(base),'Phase61_to_Phase63':diff(old)}
assert all(x['unexplained_bytes']==0 for x in diffs.values()),'STOP: unexplained byte changes'
delta=[]
for kind in ('components','trampolines'):
 for n,c in meta[kind].items():
  previous=oldmeta[kind].get(n)
  if previous!=c:delta.append(dict(group=kind,name=n,before=previous,after=c))
(O/'classified-diffs.json').write_text(json.dumps(dict(candidate_sha256=sha(image),diffs=diffs,function_deltas=delta),indent=2)+'\n')
binding=[]
for number,name in [(64,'phase64-spi2-model-closure'),(65,'phase65-shi-model-closure'),(66,'phase66-usb-safety-classification')]:
 d=R/'builds'/name;hits=[]
 for p in d.glob('*.json'):
  s=p.read_text(encoding='utf-8');
  if sha(image) in s:hits.append(p.name)
 binding.append(dict(phase=number,BIN_sha256=sha(image),json_with_exact_hash=hits,status='HASH-BOUND' if hits else 'NOT HASH-BOUND',source_loader='startup.py'))
(O/'phase-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True
def ins(pc):return next(md.disasm(image[pc-BASE:pc-BASE+4],pc,count=1),None) if BASE<=pc<BASE+len(image) else None
def listing(pc,n):
 return '\n'.join(f'{i.address:08X}: {i.mnemonic:10} {i.op_str}' for i in md.disasm(image[pc-BASE:pc-BASE+n],pc))+'\n'
# Halfword scan deliberately over-approximates: candidates require code review.
targets={0x801cfa4,0x801d7d0,0x801d7d8,0x801d808};xrefs=[]
for off in range(0,len(image)-3,2):
 i=ins(BASE+off)
 if i and i.mnemonic in ('bl','b','b.w') and i.operands[0].type==ARM_OP_IMM and i.operands[0].imm in targets:
  xrefs.append(dict(pc=hex(i.address),target=hex(i.operands[0].imm),instruction=i.mnemonic+' '+i.op_str));(O/f'alloc-{i.address:08x}.asm').write_text(listing(i.address-24,64))
roots={'Main post-profile loop':0x801d5ac,'Main parser':0x801eb30,'Storage worker':0x8024014,'BOT':0x8026db0,'SCSI':0x803b27c,'class Init':0x80228a8,'class DataOut':0x80228d6,'diagnostic entry':0x806f900}
roots['USB HS IRQ vector']=struct.unpack_from('<I',image,0x174)[0]&~1
roots.update({'class DeInit':0x80228b4,'class Setup':0x80228c0,'class slot+18':0x80228e2,'class slot+1c':0x80228ee,'class slot+20':0x80228f8,'MIDI child Init':0x805b568,'BOT child Init':0x8058eb0,'BOT child DeInit':0x8058ec2,'BOT child Setup':0x8058ecc,'backend READ':0x8057e88,'backend WRITE':0x8057ef4})
rootresults={}
for name,root in roots.items():
 todo=[root];seen=set();indirect=[];reached=[]
 while todo:
  pc=todo.pop()
  if pc in seen or not BASE<=pc<BASE+len(image):continue
  seen.add(pc);i=ins(pc)
  if not i:continue
  if pc in targets:reached.append(hex(pc));continue
  m=i.mnemonic;ops=i.op_str;nxt=pc+i.size
  if m in ('tbb','tbh') or (m=='blx' and i.operands[0].type!=ARM_OP_IMM):indirect.append(dict(pc=hex(pc),instruction=m+' '+ops))
  if m in ('bx','bxj'): 
   if ops!='lr':indirect.append(dict(pc=hex(pc),instruction=m+' '+ops))
   continue
  if (m.startswith('pop') and 'pc' in ops):continue
  if m.startswith('ldr') and ops.startswith('pc,'):
   indirect.append(dict(pc=hex(pc),instruction=m+' '+ops));continue
  if m in ('b','b.w','bl','blx') and i.operands[0].type==ARM_OP_IMM:
   todo.append(i.operands[0].imm&~1)
   if m in ('b','b.w'):continue
  elif m.startswith('b') and i.operands and i.operands[-1].type==ARM_OP_IMM:todo.append(i.operands[-1].imm&~1)
  elif m in ('cbz','cbnz'):todo.append(i.operands[-1].imm&~1)
  todo.append(nxt)
 rootresults[name]=dict(root=hex(root),instruction_candidates=len(seen),allocator_targets=reached,unresolved_dispatch=indirect,scope='Direct-edge over-approximation; jump tables/virtual targets not silently resolved')
(O/'allocator-census.json').write_text(json.dumps(dict(candidate_sha256=sha(image),direct_candidates=xrefs,roots=rootresults,complete=False,confidence='UNKNOWN',scheduled_task_set='UNKNOWN: Main and Storage roots inspected; complete post-READY task/callback set not proven.',warning='Nonempty indirect dispatch means no-allocation closure is not yet proven.'),indent=2)+'\n')
saved=json.loads((R/'builds/phase66-usb-safety-classification/allocation-returns.json').read_text())['entries'];by={int(x['return_PC'])-4:x for x in saved}
rows=['caller,target,request_bytes,path,after_READY,before_or_during_capture,evidence']
for x in xrefs:
 obs=by.get(int(x['pc'],16));rows.append(','.join([x['pc'],x['target'],str(obs['bytes']) if obs else 'UNKNOWN','candidate xref; execution root unresolved','UNKNOWN','UNKNOWN','Phase66 startup observation' if obs else 'static candidate only']))
(O/'allocation-requests.csv').write_text('\n'.join(rows)+'\n')
for pc,n in [(0x801cfa4,0x22),(0x801d7d0,0x38),(0x8070b00,0x600),(0x8026db0,0x160),(0x8057e88,0x130),(0x8024130,0xa0),(0x8023f68,0xb0)]: (O/f'candidate-{pc:08x}.asm').write_text(listing(pc,n))
print('Diffs:',[(k,v['changed_bytes'],v['unexplained_bytes']) for k,v in diffs.items()]);print('Changed functions:',[(x['group'],x['name']) for x in delta]);print('Allocator xrefs',len(xrefs));print('Binding',binding)
