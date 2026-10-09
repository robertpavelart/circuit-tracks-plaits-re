"""Targeted read-only Components metadata hints; never opens databases writable.
Raw LevelDB/log matches are historical byte evidence, not authoritative live state.
Network/Cookies/authentication stores are excluded.
"""
import argparse,json,re
from pathlib import Path
from ct_stock_load_audit import ROOT,sha,verify_inputs
def collect(out,roaming):
 out=out.resolve();base=(ROOT/'builds/phase19c-packlink').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh PACKLINK child required')
 verify_inputs();ds=json.loads((ROOT/'builds/phase19c-assetdata/final/datasets.json').read_text())
 terms=['circuit-tracks','sample_','_PCM.wav','_SESSION.ncs','_META.ncm','selectedPack','packId']
 terms += [d['archive_sha256'] for d in ds]+[d['name'] for d in ds]
 paths=[]
 for folder in ['Cache/Cache_Data','Local Storage/leveldb','Session Storage']:
  p=roaming/folder
  if p.exists():paths += [x for x in p.iterdir() if x.is_file() and x.stat().st_size<=30000000 and x.name not in {'LOCK'}]
 out.mkdir(parents=True);(out/'json').mkdir();matches=[];manifest=[];documents=[]
 for p in sorted(paths):
  # Only cache text/header or small storage logs: PNG/ZIP/audio bodies excluded.
  head=p.open('rb').read(16)
  if head.startswith((b'PK',b'\x89PNG',b'RIFF',b'\xff\xd8')):continue
  raw=p.read_bytes();s=p.stat();found=[]
  for t in terms:
   for m in list(re.finditer(re.escape(t.encode()),raw))[:50]:
    found.append(dict(term=t,byte_offset=m.start()))
  if not found:continue
  digest=sha(raw);manifest.append(dict(path=str(p),size=len(raw),mtime_ns=s.st_mtime_ns,sha256=digest,
   scope='Raw historical cache/storage hints, not proven selected state'))
  matches.append(dict(path=str(p),sha256=digest,matches=found))
  try:j=json.loads(raw.decode('utf8'))
  except (ValueError,UnicodeError):continue
  # Existing JSON response evidence only; no tokens or neighboring stores copied.
  if any(b'circuit-tracks' in raw for _ in [0]):
   dest=out/'json'/f'{digest}.json'
   if not dest.exists():
    with dest.open('xb') as f:f.write(raw)
   documents.append(dict(source=str(p),snapshot=str(dest.relative_to(ROOT)),sha256=digest,
    top_keys=list(j) if isinstance(j,dict) else 'array',size=len(raw)))
 for n,v in [('matches.json',matches),('sources.json',manifest),('documents.json',documents)]:
  with (out/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 hashes={p.relative_to(out).as_posix():sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}
 with (out/'hashes.json').open('x',encoding='utf8') as f:json.dump(hashes,f,indent=2,sort_keys=True);f.write('\n')
 print('Matching metadata files',len(manifest),'JSON responses',len(documents))
 verify_inputs()
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path)
 p.add_argument('--roaming',required=True,type=Path);a=p.parse_args();collect(a.output_dir,a.roaming)
