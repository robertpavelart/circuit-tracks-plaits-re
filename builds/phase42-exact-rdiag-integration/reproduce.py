"""Exact SC35D8 admission gate only. Never encodes SYX or integrates new code.

All builder inputs are copied byte-exact into this phase's local source tree.
Call the builder API in the same order as linein3.main, omitting its encoder.
"""
from pathlib import Path
import sys,os,json,hashlib,importlib.metadata,traceback
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
LOCAL=O/'source'
def sha(b):return hashlib.sha256(b).hexdigest()
def gitblob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def save(n,v):(O/n).write_text(json.dumps(v,indent=2)+'\n')
def ranges(a,b,base=0x08010000):
 out=[];start=None
 for i in range(max(len(a),len(b))):
  diff=i>=len(a) or i>=len(b) or a[i]!=b[i]
  if diff and start is None:start=i
  if not diff and start is not None:out.append([hex(base+start),hex(base+i)]);start=None
 if start is not None:out.append([hex(base+start),hex(base+max(len(a),len(b)))])
 return out
def main():
 inputs=[]
 source_paths=sorted(list((REF/'tools').glob('*.py'))+list((REF/'tools').glob('*.json')))
 source_paths += [REF/'stock/circuittracks-firmware-4486-STOCK.bin',REF/'re/app.asm',REF/'firmware/sc35d8/manifest.json',REF/'firmware/sc35d8/PRUEBA.md']
 tool=REF/'ext/bin/dsptool.exe'
 if tool.exists():source_paths.append(tool)
 for p in source_paths:
  b=p.read_bytes();rel=p.relative_to(REF);dest=LOCAL/rel
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
  inputs.append(dict(path=str(p),local=str(dest),bytes=len(b),sha256=sha(b),git_blob_sha1=gitblob(b)))
 manifest=json.loads((LOCAL/'firmware/sc35d8/manifest.json').read_text())
 pin=dict(reference_commit=None,confidence='UNKNOWN',reason='Archive checkout has no .git/HEAD; no top-level commit is authenticated',
          historical_rdiag_revision='UNKNOWN as a commit; current source pinned by SHA-256/blob and tested by exact image reproduction',
          rdiag=next(x for x in inputs if x['path'].endswith('tools\\rdiag.py')),sources=inputs,
          expected=manifest,hardware_test_evidence=dict(path=str(REF/'docs/NOTAS.md'),line=1424,date='2026-10-09',scope='Repository reports boot/audio, USB rdiag and SD read/write success; not repeated'),
          python=sys.version,capstone=importlib.metadata.version('capstone'))
 save('inputs.json',pin)
 # Prevent all Python-level file mutations outside this phase (including a
 # DSP cache save) and any accidental firmware encoder call.
 def audit(event,args):
  if event=='open':
   path,mode,flags=args
   if isinstance(path,(str,bytes,os.PathLike)) and ((isinstance(mode,str) and any(x in mode for x in 'wax+')) or isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)):
    resolved=Path(os.fsdecode(path)).resolve()
    if not resolved.is_relative_to(O):raise PermissionError('write outside phase42: '+str(resolved))
 sys.addaudithook(audit)
 sys.path.insert(0,str(LOCAL/'tools'))
 os.environ['DSP_ASM_CACHE_UPDATE']='0'
 if tool.exists():os.environ['DSPTOOL']=str(LOCAL/'ext/bin/dsptool.exe')
 result=dict(confidence='UNKNOWN',verdict='UNQUALIFIED',gate='SC35D8 exact reproduction',new_command_integrated=False,SYX_generated=False,hardware_access=False)
 try:
  import build_sc35d8 as B
  import ct_fw
  def forbidden(*a,**k):raise RuntimeError('SYX generation forbidden in phase42')
  ct_fw.encode=forbidden
  stock=(LOCAL/'stock/circuittracks-firmware-4486-STOCK.bin').read_bytes()
  assert sha(stock)=='b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da'
  img,report=B.b182.b18.b6.b5.build(stock,LOCAL/'re/app.asm')
  img=bytearray(img)
  mark=B.b182.b18.sc.MARK_OFF
  img[mark:mark+6]=b'SC35D8'
  B.linein3.patch_hook(img,report,B.linein3.L2.patch_p)
  B.extra(img,report)
  image=bytes(img)
  actual=dict(image_size=hex(len(image)),image_sha256=sha(image),crc32=hex(ct_fw.crc32_mpeg2(image)))
  matches={k:actual[k]==manifest[k] for k in actual}
  result.update(actual=actual,expected={k:manifest[k] for k in actual},matches=matches,all_match=all(matches.values()),
                changed_ranges_relative_to_official=ranges(stock,image),app_base='0x08010000',export='rebuilt-sc35d8.bin')
  (O/'rebuilt-sc35d8.bin').write_bytes(image)
  save('rebuilt-report.json',report)
  if all(matches.values()):result.update(confidence='PROVEN',verdict='PASS',reason='Exact published manifest size, image SHA-256 and CRC reproduced')
  else:
   # The published manifest has disassembly/labels, not a second image byte
   # source. Compare report structure to identify the earliest supported
   # semantic/layout mismatch; do not invent expected artifact bytes.
   diffs=[]
   def compare(a,b,path='report'):
    if isinstance(a,dict) and isinstance(b,dict):
     for k in sorted(set(a)|set(b)):
      if k not in a:diffs.append(dict(path=path+'.'+k,expected=b[k],actual='ABSENT'))
      elif k not in b:diffs.append(dict(path=path+'.'+k,expected='ABSENT',actual=a[k]))
      else:compare(a[k],b[k],path+'.'+k)
    elif isinstance(a,list) and isinstance(b,list):
     for i in range(min(len(a),len(b))):compare(a[i],b[i],path+f'[{i}]')
     if len(a)!=len(b):diffs.append(dict(path=path+'.length',expected=len(b),actual=len(a)))
    elif a!=b:diffs.append(dict(path=path,expected=b,actual=a))
   compare(report,manifest['report'])
   save('report-differences.json',diffs)
   result.update(reason='STOP: published SC35D8 equality gate failed; no approximate-base integration',report_difference_count=len(diffs),first_report_differences=diffs[:12])
 except BaseException as exc:
  result.update(reason='STOP: exact reconstruction could not complete',error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc())
 result['reference_inputs_unchanged']=all(sha(Path(x['path']).read_bytes())==x['sha256'] for x in inputs)
 result['copied_sources_unchanged']=all(sha(Path(x['local']).read_bytes())==x['sha256'] for x in inputs)
 result['loaded_builder_sources']={n:str(m.__file__) for n,m in sys.modules.items() if getattr(m,'__file__',None) and Path(m.__file__).is_relative_to(LOCAL)}
 save('reproduction.json',result)
 print(json.dumps({k:v for k,v in result.items() if k not in ('changed_ranges_relative_to_official','loaded_builder_sources','traceback')},indent=2),flush=True)
if __name__=='__main__':main()
