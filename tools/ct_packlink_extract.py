"""Read-only installed ASAR code snapshot for targeted pack import analysis.
No code is executed. Manifest offsets and available integrity hashes are checked.
"""
import argparse,json,struct
from pathlib import Path,PurePosixPath
from ct_stock_load_audit import ROOT,sha,verify_inputs

def collect(out,source):
 out=out.resolve();base=(ROOT/'builds/phase19c-packlink').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh PACKLINK child required')
 verify_inputs();before=source.stat();raw=source.read_bytes();after=source.stat()
 assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 a,total,payload,n=struct.unpack_from('<4I',raw)
 assert a==4 and total==payload+4 and n<=payload-4
 header=json.loads(raw[16:16+n]);start=8+total;manifest=[];out.mkdir(parents=True)
 def walk(node,prefix=''):
  for name,v in sorted(node.get('files',{}).items()):
   path=prefix+name
   if 'files' in v:walk(v,path+'/');continue
   manifest.append(dict(path=path,size=v.get('size'),offset=v.get('offset'),unpacked=v.get('unpacked',False),
    integrity=v.get('integrity'),link=v.get('link')))
   if path.startswith('node_modules/') or v.get('unpacked') or v.get('link'):continue
   if PurePosixPath(path).suffix not in {'.js','.map','.json','.html'}:return_unused=None;continue
   rel=PurePosixPath(path)
   assert not rel.is_absolute() and '..' not in rel.parts
   data=raw[start+int(v['offset']):start+int(v['offset'])+v['size']];assert len(data)==v['size']
   integ=v.get('integrity')
   if integ and integ.get('algorithm')=='SHA256':assert sha(data)==integ['hash']
   dest=out/'code'/Path(*rel.parts);dest.parent.mkdir(parents=True,exist_ok=True)
   with dest.open('xb') as f:f.write(data)
 walk(header)
 def emit(n,v):
  with (out/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 emit('asar-manifest.json',manifest)
 emit('provenance.json',dict(source=str(source),source_sha256=sha(raw),size=len(raw),mtime_ns=before.st_mtime_ns,
  data_base=start,manifest_header_bytes=n,offline=True,app_launched=False,user_modified=False,
  purpose='Static installed code only; library/package payloads not executed'))
 emit('hashes.json',{p.relative_to(out).as_posix():sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()})
 verify_inputs();print('Code files',len(list((out/'code').rglob('*'))),'ASAR',sha(raw))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--source',required=True,type=Path);p.add_argument('--output-dir',required=True,type=Path)
 a=p.parse_args();collect(a.output_dir,a.source)
