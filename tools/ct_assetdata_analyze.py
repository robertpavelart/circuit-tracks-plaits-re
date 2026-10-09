"""Analyze immutable existing archive snapshots, without audio decoding/devices.
Archive sample-array order is explicit; native filename/selection linkage is not
silently inferred. Address results use real bytes and the recovered loader model.
"""
import argparse,csv,hashlib,json,re,struct,zipfile
from pathlib import Path,PurePosixPath
from ct_stock_load_audit import ROOT,verify_inputs,sha
from ct_asset_bounds import A0,advance,emitted,page,WATCH,intersect
from ct_hostwrite_audit import intervals
from ct_backend_bounds import name_index

def wav_header(raw,size):
 """Exact stock64-byte header interpretation plus separate file consistency."""
 h=raw[:64].ljust(64,b'\0');u32=lambda o:struct.unpack_from('<I',h,o)[0]
 u16=lambda o:struct.unpack_from('<H',h,o)[0]
 q=u32(16);d=20+q
 r=dict(file_size=size,header_bytes=len(raw[:64]),fmt_size=q,channels=u16(22),
  sample_rate=u32(24),bit_depth=u16(34),format_tag=u16(20),RIFF_declared_end=u32(4)+8,
  data_offset=d+8,L=None,stock_predicate='UNRESOLVED',file_consistency='UNRESOLVED')
 if h[:4]!=b'RIFF' or h[8:12]!=b'WAVE' or h[12:16]!=b'fmt ':
  r['stock_predicate']='REJECTED';return r
 if d+8>64:
  r['reason']='data signature/length outside cleared/read64-byte header; ARM adjacent bytes unknown';return r
 r['L']=u32(d+4)
 accepted=(h[d:d+4]==b'data' and r['L']<=19200000 and r['channels']==1 and
  r['sample_rate']==48000 and r['bit_depth']==16)
 r['stock_predicate']='STOCK-PREDICATE ACCEPTED' if accepted else 'REJECTED'
 r['file_consistency']='VERIFIED complete declared regions' if (size>=d+8 and
  d+8+r['L']<=size and r['RIFF_declared_end']<=size) else 'MALFORMED extent/truncation'
 r['classification']='MALFORMED' if r['file_consistency'].startswith('MALFORMED') else r['stock_predicate']
 return r

def collect(out,discovery):
 out=out.resolve();discovery=discovery.resolve();base=(ROOT/'builds/phase19c-assetdata').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh ASSETDATA child required')
 verify_inputs();inputs={};allmanifest=[];wavs=[];records=[];progress=[];tests=[];summaries=[];errors=[]
 def read(p):
  raw=p.read_bytes();inputs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 for n,h in json.loads(read(discovery/'hashes.json')).items():assert sha(read(discovery/n))==h
 snaps=json.loads(read(discovery/'snapshots.json'));out.mkdir(parents=True);(out/'metadata').mkdir()
 for n in ['local-candidates.csv','search-coverage.json','search-errors.json']:
  with (out/n).open('xb') as f:f.write((discovery/n).read_bytes())
 for snap in snaps:
  archive=ROOT/snap['snapshot'];assert sha(read(archive))==snap['sha256']
  ds=snap['sha256'][:16]
  with zipfile.ZipFile(archive) as z:
   infos=z.infolist();names=[x.filename for x in infos];duplicates=[n for n in set(names) if names.count(n)>1]
   headers={};members={}
   for order,info in enumerate(infos):
    if info.is_dir():continue
    h=hashlib.sha256();first=b''
    with z.open(info) as f:
     for block in iter(lambda:f.read(1024*1024),b''):
      if not first:first=block[:64]
      h.update(block)
    item=dict(dataset_id=ds,archive_source=snap['source'],archive_sha256=snap['sha256'],
     member=info.filename,full_path=snap['source']+'::'+info.filename,size=info.file_size,
     sha256=h.hexdigest(),ZIP_listing_order=order,ZIP_mtime=json.dumps(info.date_time),
     duplicate_count=names.count(info.filename),reason='Member of metadata-verified Circuit Tracks archive')
    allmanifest.append(item);members[info.filename]=item
    if info.filename.lower().endswith('.wav'):
     meta=wav_header(first,info.file_size);headers[info.filename]=meta
     wavs.append(dict(dataset_id=ds,member=info.filename,sha256=h.hexdigest(),**meta))
   if len(snap['index_members'])!=1:errors.append(dict(dataset=ds,reason='Multiple index metadata roots'));continue
   index_name=snap['index_members'][0];index=z.read(index_name);j=json.loads(index)
   with (out/'metadata'/f'{ds}-index.json').open('xb') as f:f.write(index)
   prefix=str(PurePosixPath(index_name).parent);prefix='' if prefix=='.' else prefix+'/'
   samples=j['samples'];mapping_ok=(j.get('product')=='circuit-tracks' and len(samples)==64 and not duplicates)
   for i,s in enumerate(samples):
    mapping_ok &= (isinstance(s,dict) and s.get('url')==f'samples/sample_{i}.wav')
   A=A0;total_L=total_main=valid_n=missing_n=0;missing=[];unknown=[];geom=0
   for i in range(64):
    s=samples[i] if i<len(samples) and isinstance(samples[i],dict) else {}
    member=prefix+s.get('url','');present=member in headers
    m=headers.get(member);L=m['L'] if m else None
    blank_name=s.get('name','')==''
    complete_missing=mapping_ok and not present and member not in members and blank_name
    resolved=mapping_ok and (complete_missing or (present and m['stock_predicate']!='UNRESOLVED'))
    accepted=bool(present and m['stock_predicate']=='STOCK-PREDICATE ACCEPTED')
    R=advance(L,True) if resolved and accepted else 256 if resolved else None
    if accepted:valid_n+=1;total_L+=L
    if complete_missing:missing_n+=1;missing.append(i)
    if not resolved:unknown.append(i)
    scope='DATASET-SPECIFIC archive mapping; native slot/path/content preservation UNRESOLVED'
    records.append(dict(dataset_id=ds,pack_name=j.get('name',''),record=i,present=present,
     member=member,metadata_name=s.get('name',''),L=L if L is not None else '',
     stock_valid=accepted if resolved else '',status=m['stock_predicate'] if present else
      'MISSING in archive and metadata name empty' if complete_missing else 'UNRESOLVED absence',
     R8=R if R is not None else '',native_filename_index=name_index(PurePosixPath(member).name.encode()) if member else '',
     mapping_evidence='index.json samples[i].url == samples/sample_i.wav' if mapping_ok else 'UNRESOLVED',scope=scope))
    A_in=A;S=page(A) if A is not None else None
    N=emitted(A,L,accepted) if A is not None and resolved else None
    if N is not None:
     main=intervals(S,N);padstart=(S+N)&0xffffff;pad=intervals(padstart,256)
     A=(A+R)&0xffffffff;total_main+=N
    else:main=pad=None;padstart=None;A=None
    progress.append(dict(dataset_id=ds,record=i,A_in=hex(A_in) if A_in is not None else '',
     L=L if L is not None else '',R8=R if R is not None else '',A_out=hex(A) if A is not None else '',
     page_residue=hex(A_in&0xffff00) if A_in is not None else '',S=hex(S) if S is not None else '',
     main_words=N if N is not None else '',main_intervals=json.dumps(main),
     padding_start=hex(padstart) if padstart is not None else '',padding_words=256 if N is not None else '',
     padding_intervals=json.dumps(pad),padding_wrap=len(pad)>1 if pad is not None else '',
     actual_device_A='',space='STATE-DEPENDENT; SPACE UNRESOLVED',scope=scope))
    for part,parts in [('main',main),('padding',pad)]:
     for label,x,y in WATCH:
      hit=intersect(parts,x,y) if parts is not None else None
      if hit:geom+=1
      tests.append(dict(dataset_id=ds,record=i,part=part,target=label,target_start=hex(x),target_end=hex(y),
       geometric_result='GEOMETRIC OVERLAP' if hit else 'NO GEOMETRIC OVERLAP' if hit is False else 'UNRESOLVED',
       intervals=json.dumps(parts),page_residue=hex(A_in&0xffff00) if A_in is not None else '',
       X_write='NOT PROVEN',Y_write='NOT PROVEN',space='SPACE UNRESOLVED / STATE-DEPENDENT',scope=scope))
   project_urls=[prefix+p.get('url','') for p in j.get('projects',[]) if isinstance(p,dict)]
   summaries.append(dict(dataset_id=ds,name=j.get('name',''),product=j.get('product'),version=j.get('version'),
    source=snap['source'],archive_sha256=snap['sha256'],index_sha256=sha(index),sample_metadata_rows=len(samples),
    present_PCM_files=len(headers),accepted_count=valid_n,missing_indices=missing,unresolved_indices=unknown,
    projects_present=sum(n in members for n in project_urls),project_urls_missing=sum(n not in members for n in project_urls),
    duplicate_members=duplicates,slot_mapping_verified=mapping_ok,total_L=total_L,
    A64=hex(A) if A is not None else None,total_main_words=total_main,geometric_hit_rows=geom,
    selected_on_device='UNRESOLVED',native_mapping='UNRESOLVED; sample_i.wav does not pass firmware filename prefix parser',
    dataset_specific_model_exclusion=(not unknown and geom==0),
    native_asset_blocker='Not closed: actual selection/native PCM mapping and any transformations not proved',
    universal_normal_proof=False))
 def emit(n,v):
  with (out/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 def csvout(n,rs):
  keys=list(dict.fromkeys(k for r in rs for k in r))
  with (out/n).open('x',encoding='utf8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rs)
 csvout('dataset-manifest.csv',allmanifest);csvout('wav-metadata.csv',wavs);csvout('record-map.csv',records)
 csvout('actual-address-progression.csv',progress);csvout('actual-padding-intersections.csv',tests)
 emit('datasets.json',summaries);emit('analysis-errors.json',errors)
 emit('result.json',dict(offline=True,CPU_instructions_executed=0,archives_analyzed=len(summaries),
  WAVs_analyzed=len(wavs),records=len(records),geometric_hit_rows=sum(x['geometric_hit_rows'] for x in summaries),
  all_dataset_model_exclusions=all(x['dataset_specific_model_exclusion'] for x in summaries),
  suitable_archive_data_found=bool(summaries),native_selected_dataset_found=False,
  normal_asset_family_closed=False,parent_replay_admitted=False,target_bridge_recomputed=False,
  scope='ACTUAL-DATA archive content + DATASET-SPECIFIC loader algebra; native applicability remains qualified',
  still_missing=['Which cached pack (if any) is the selected native source',
   'Existing offline native PCM listing/selection metadata or documented archive-to-native slot/content preservation'],
  X11='STATE-DEPENDENT; no geometric-to-X-write promotion',
  best_next_step='Identify the selected native pack using existing offline selection metadata and verify archive-to-native slot/content preservation'))
 for n in ['tools/ct_assetdata_analyze.py','tools/ct_assetdata_discover.py','tools/ct_asset_bounds.py','tools/ct_backend_bounds.py']:
  read(ROOT/n)
 emit('inputs.json',inputs);verify_inputs()
 emit('hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
 print(json.dumps(summaries,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--output-dir',required=True,type=Path);p.add_argument('--discovery-dir',required=True,type=Path)
 a=p.parse_args();collect(a.output_dir,a.discovery_dir)
