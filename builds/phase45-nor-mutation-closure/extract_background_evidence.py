"""Read-only candidate/source evidence extraction for retained background producers.
Never imports builders or opens device transports. Outputs listings/JSON only.
"""
from pathlib import Path
import json, hashlib, struct
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
O=Path(__file__).resolve().parent; R=O.parents[1]
REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
C=R/'builds/phase44-preflash-redteam-closure/circuittracks-4486-nor-evidence-atomic-test.bin'
B=C.read_bytes(); A=0x08010000
assert hashlib.sha256(B).hexdigest()=='0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738'
old=(R/'builds/phase43-hardware-test-candidate/circuittracks-4486-nor-evidence-test.bin').read_bytes()
report=json.loads((R/'builds/phase42-exact-rdiag-integration/rebuilt-report.json').read_text(encoding='utf8'))
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True
ranges=[('persist19',0x806ae4c,0x806b4f8),('srcview',0x806b4f8,0x806b6cc),('stock_session_copy',0x802f63c,0x802f692),('stock_save_tail',0x802fe4c,0x802fe90),('content_write',0x803cc16,0x803cc34),('content_dispatch',0x803ca52,0x803caa4),('session_content_adapter',0x803c946,0x803c968),('content_queue',0x8022a46,0x8022de0),('content_file_write',0x8036b1c,0x8036ccc),('live_store_copy',0x803bbe2,0x803bc1e),('settings_read_query',0x8026bdc,0x8026c78)]
result={'confidence':'PROVEN','candidate_sha256':hashlib.sha256(B).hexdigest(),'scope':'Exact fixed candidate retained sections and native stock backend branches; not arbitrary-memory-corruption proof','ranges':[],'sources':{},'report_features':{}}
for group,a,end in ranges:
 chunk=B[a-A:end-A]; ins=list(md.disasm(chunk,a)); out=[]; calls=[]
 for i in ins:
  suffix=''
  if i.mnemonic.startswith('ldr') and '[pc,' in i.op_str:
   at=((i.address+4)&~3)+i.operands[-1].mem.disp
   if A<=at<=A+len(B)-4:suffix=f' ; [{at:08X}]={struct.unpack_from("<I",B,at-A)[0]:08X}'
  out.append(f'{i.address:08X}: {i.mnemonic:10} {i.op_str}'+suffix)
  if i.mnemonic in ('bl','b.w') and i.operands[0].type==2:calls.append({'at':hex(i.address),'to':hex(i.operands[0].imm)})
  elif i.mnemonic=='blx':calls.append({'at':hex(i.address),'indirect':i.op_str})
 (O/f'background-{group}.asm').write_text('\n'.join(out)+'\n',encoding='utf8')
 result['ranges'].append(dict(name=group,start=hex(a),end_exclusive=hex(end),sha256=hashlib.sha256(chunk).hexdigest(),unchanged_from_phase43=chunk==old[a-A:end-A],calls=calls))
for group in ('persist19','srcview','probe35s','rdiag'):
 result['report_features'][group]={k:v for k,v in report[group].items() if k not in ('listing','labels','flat')}
for name in ('persist19.py','srcview.py','build_sc35d8.py','build_sc19_1.py','build_sc19.py','probe35s.py','rdiag.py','vcf21.py','vcf21_dsp.py'):
 p=REF/'tools'/name; result['sources'][str(p)]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
result['live_store_vtable']={hex(a):hex(struct.unpack_from('<I',B,a-A)[0]) for a in range(0x805bbac,0x805bbc0,4)}
result['content_dispatch_offsets']={str(i):hex(0x8022b28+2*struct.unpack_from('<H',B,0x8022b28-A+2*i)[0]) for i in range(11)}
(O/'background-evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({'candidate_sha256':result['candidate_sha256'],'ranges':len(ranges),'unchanged':all(x['unchanged_from_phase43'] for x in result['ranges']),'content_op7':result['content_dispatch_offsets']['7'],'features':result['report_features'],'store_vtable':result['live_store_vtable']},indent=2))
