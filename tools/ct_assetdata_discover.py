"""Read-only bounded local metadata/archive discovery. No devices or network.
Only relevant ZIPs are copied byte-for-byte into fresh project evidence.
No user-file writes, symlink traversal, cloud hydration or full-disk crawl.
"""
import argparse,csv,hashlib,json,os,re,shutil,stat,zipfile
from pathlib import Path
from ct_stock_load_audit import ROOT,verify_inputs,sha

HINT=re.compile(r'circuit|novation|(?:^|[ _-])pcm(?:$|[ _-])',re.I)
ARCH={'.zip','.nupkg','.circuittrackspack','.circuitpack','.7z','.rar','.tar','.gz'}
def collect(out,roots,reuse=None):
 out=out.resolve();base=(ROOT/'builds/phase19c-assetdata').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh ASSETDATA child required')
 verify_inputs();out.mkdir(parents=True);(out/'archives').mkdir()
 candidates=[];inventory=[];coverage=[];errors=[];snaps=[];archive_entries=[]
 reused={x['sha256']:ROOT/x['snapshot'] for x in json.loads(reuse.read_text())} if reuse else {}
 for root in roots:
  root=root.absolute();count=dirs=skips=archives=0;stack=[root];seen=set()
  while stack:
   folder=stack.pop()
   if str(folder).lower() in seen:continue
   seen.add(str(folder).lower())
   try:entries=sorted(os.scandir(folder),key=lambda x:x.name.lower())
   except OSError as e:errors.append(dict(path=str(folder),error=type(e).__name__,scope='metadata enumeration'));continue
   dirs+=1
   for e in entries:
    p=Path(e.path)
    try:s=e.stat(follow_symlinks=False)
    except OSError as ex:errors.append(dict(path=str(p),error=type(ex).__name__,scope='stat'));continue
    attrs=getattr(s,'st_file_attributes',0)
    if attrs&(0x400|0x1000|0x40000|0x400000):skips+=1;continue
    if stat.S_ISDIR(s.st_mode):
     if e.name in {'.git','node_modules','__pycache__','.venv','venv'} or p==base:skips+=1;continue
     if p==ROOT/'builds/python-deps':skips+=1;continue
     stack.append(p);continue
    if not stat.S_ISREG(s.st_mode):continue
    count+=1
    if count>500000:errors.append(dict(path=str(root),error='500000-file metadata bound reached',scope='scan limit'));stack=[];break
    suffix=p.suffix.lower();in_cache='components' in str(root).lower() and 'cache' in str(p).lower()
    cache_external=in_cache and e.name.startswith('f_')
    relevant=(suffix in {'.ncs','.ncm','.circuittrackspack','.circuitpack'} or
     e.name.lower().endswith('_pcm.wav') or
     bool(HINT.search(str(p))) and suffix in {'.wav','.syx','.json'})
    if suffix not in ARCH and not cache_external and not relevant:continue
    inv=dict(path=str(p),size=s.st_size,mtime_ns=s.st_mtime_ns,
     reason='Components external-cache payload' if cache_external else 'archive/asset filename hint',
     inspected='metadata only',classification='UNRESOLVED hint, not dataset evidence')
    inventory.append(inv)
    try:
     iszip=(suffix in ARCH or cache_external) and zipfile.is_zipfile(p)
     if iszip:
      archives+=1
      with zipfile.ZipFile(p) as z:
       infos=z.infolist();names=[x.filename for x in infos];keys=[n for n in names if n.rsplit('/',1)[-1]=='index.json']
       indices=[]
       for n in keys:
        if z.getinfo(n).file_size>2*1024*1024:continue
        try:j=json.loads(z.read(n))
        except (ValueError,UnicodeError):continue
        if isinstance(j,dict) and j.get('product')=='circuit-tracks' and isinstance(j.get('samples'),list):
         indices.append((n,j))
       inv['inspected']='ZIP central directory and candidate index metadata'
       inv['classification']='Circuit Tracks archive dataset' if indices else 'No verified Circuit Tracks index found'
       if indices:
        # Stable read snapshot. No extraction of archive paths into user folders.
        before=p.stat();raw=p.read_bytes();after=p.stat()
        if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError('Source changed during snapshot')
        digest=sha(raw);dest=reused.get(digest,out/'archives'/f'{digest}.zip')
        if digest in reused:assert sha(dest.read_bytes())==digest
        if not dest.exists():
         with dest.open('xb') as f:f.write(raw)
        candidate=dict(path=str(p),size=len(raw),sha256=digest,mtime_ns=after.st_mtime_ns,
         container=str(p),archive_member='',reason='index.json product=circuit-tracks with samples list',
         classification='VERIFIED existing archive; selected native container UNRESOLVED')
        candidates.append(candidate)
        snaps.append(dict(source=str(p),snapshot=str(dest.relative_to(ROOT)),sha256=digest,size=len(raw),
         mtime_ns=after.st_mtime_ns,index_members=[n for n,j in indices],names=[j.get('name','') for n,j in indices]))
        for order,x in enumerate(infos):archive_entries.append(dict(archive_sha256=digest,listing_order=order,
         member=x.filename,size=x.file_size,compressed_size=x.compress_size,crc32=f'{x.CRC:08x}',
         ZIP_time=json.dumps(x.date_time),duplicate_count=names.count(x.filename)))
     elif relevant:
      # Cache firmware/config hints are catalogued, not mistaken for pack data.
      with p.open('rb') as f:
       h=hashlib.sha256()
       for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
      inv['classification']='Filename hint only; not a mapped native PCM dataset'
      candidates.append(dict(path=str(p),size=s.st_size,sha256=h.hexdigest(),mtime_ns=s.st_mtime_ns,
       container='',archive_member='',reason='asset/product filename hint',classification=inv['classification']))
    except (OSError,ValueError,zipfile.BadZipFile,RuntimeError) as ex:
     errors.append(dict(path=str(p),error=type(ex).__name__+': '+str(ex),scope='candidate read'))
   # Metadata walk only; no arbitrary binary scans in Documents/Downloads/Desktop.
  coverage.append(dict(root=str(root),regular_files=count,directories=dirs,skipped=skips,ZIP_inspected=archives,
   reparse_cloud_skipped=True,max_files=500000))
 def emit(n,v):
  with (out/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 def csvout(n,rs,keys):
  with (out/n).open('x',encoding='utf8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rs)
 csvout('local-candidates.csv',candidates,['path','size','sha256','mtime_ns','container','archive_member','reason','classification'])
 csvout('search-inventory.csv',inventory,['path','size','mtime_ns','reason','inspected','classification'])
 csvout('archive-listings.csv',archive_entries,['archive_sha256','listing_order','member','size','compressed_size','crc32','ZIP_time','duplicate_count'])
 emit('snapshots.json',snaps);emit('search-coverage.json',coverage);emit('search-errors.json',errors)
 emit('provenance.json',dict(offline=True,source_sha256=sha(Path(__file__).read_bytes()),
  user_files_modified=False,apps_launched=False,CPU_instructions_executed=0,
  scope='explicit likely roots; metadata first; ZIP index inspection; no browser/network authentication stores',
  limitations='No reparse/cloud placeholders, node_modules/venv/git, opaque nonZIP archives or recursive archive payloads',
  copied_archives=len({x['sha256'] for x in snaps})))
 verify_inputs();emit('hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
 print(json.dumps(dict(coverage=coverage,candidate_archives=len(snaps),errors=len(errors)),indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path)
 p.add_argument('--root',required=True,action='append',type=Path);p.add_argument('--reuse-snapshots',type=Path)
 a=p.parse_args();collect(a.output_dir,a.root,a.reuse_snapshots)
