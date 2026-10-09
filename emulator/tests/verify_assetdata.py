"""Actual-data cross-checks only; no invented samples, CPU or device activity."""
import argparse,csv,hashlib,json,subprocess,sys,wave,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from ct_stock_load_audit import verify_inputs
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(first,repeat,out,discovery,originals):
 out=out.resolve();base=(ROOT/'builds/phase19c-assetdata').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh checks child required')
 files={p.relative_to(first).as_posix() for p in first.rglob('*') if p.is_file()}
 assert files=={p.relative_to(repeat).as_posix() for p in repeat.rglob('*') if p.is_file()}
 for n in files:assert (first/n).read_bytes()==(repeat/n).read_bytes(),n
 for n,h in json.loads((first/'inputs.json').read_text()).items():assert sha(ROOT/n)==h,n
 for n,h in json.loads((first/'hashes.json').read_text()).items():assert sha(first/n)==h,n
 def rows(n):return list(csv.DictReader((first/n).open(encoding='utf8',newline='')))
 ds=json.loads((first/'datasets.json').read_text());pr=rows('actual-address-progression.csv');rm=rows('record-map.csv')
 assert len(ds)==12 and len(pr)==len(rm)==768
 assert len(rows('wav-metadata.csv'))==733
 assert all(x['stock_predicate']=='STOCK-PREDICATE ACCEPTED' and x['file_consistency']=='VERIFIED complete declared regions'
  for x in rows('wav-metadata.csv'))
 hit=rows('actual-padding-intersections.csv');assert len(hit)==24576
 assert all(x['geometric_result']=='NO GEOMETRIC OVERLAP' and x['X_write']=='NOT PROVEN' for x in hit)
 headers_checked=0
 for snap in json.loads((discovery/'snapshots.json').read_text()):
  key=snap['sha256'][:16];archive=ROOT/snap['snapshot'];assert sha(archive)==snap['sha256']
  rlist=[x for x in rm if x['dataset_id']==key];plist=[x for x in pr if x['dataset_id']==key]
  assert [int(x['record']) for x in rlist]==list(range(64))
  A=0x580000
  with zipfile.ZipFile(archive) as z:
   for r,p in zip(rlist,plist):
    assert int(p['A_in'],16)==A
    if r['present']=='True':
     with z.open(r['member']) as f:
      with wave.open(f,'rb') as w:
       assert (w.getnchannels(),w.getframerate(),w.getsampwidth())==(1,48000,2)
       assert w.getnframes()*2==int(r['L'])
     headers_checked+=1;B=int(r['L'])&0xfffffe00
    else:
     assert not r['L'];B=0
    # Independent instruction-loop calculation using observed lengths only.
    n=0;remaining=B;v=A
    while remaining:
     c=min(remaining,2048);end=(v+c//2)&0xffffffff
     if end>=0xe80000:break
     v=end;n+=c//2;remaining-=c
    R=256+B//2;assert int(r['R8'])==R and int(p['main_words'])==n
    assert n==B//2 # proves none of these actual archive-model main paths clips
    S=(((A&0xffff00)-2)&0xffffff)
    assert int(p['S'],16)==S and int(p['padding_start'],16)==S+n
    A=(A+R)&0xffffffff;assert int(p['A_out'],16)==A
    assert json.loads(p['padding_intervals'])==[[S+n,S+n+256]]
   d=next(x for x in ds if x['dataset_id']==key);assert int(d['A64'],16)==A
   assert A<0xe80000 and d['geometric_hit_rows']==0
 assert headers_checked==733
 for d in ds:
  m=first/'metadata'/f"{d['dataset_id']}-index.json";assert sha(m)==d['index_sha256']
  assert not d['universal_normal_proof'] and d['selected_on_device']=='UNRESOLVED'
 verify_inputs();import ct_fw_tool
 syx=ROOT/'original/circuittracks-firmware-4486.syx';b=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
 assert ct_fw_tool.decode_syx(syx)['firmware']==b and ct_fw_tool.build_syx(syx,b)==syx.read_bytes()
 for x in json.loads((ROOT/'firmware/dsp/build-4486/manifest.json').read_text())['blocks']:
  for k in ['stream','payload']:assert sha(ROOT/'firmware/dsp/build-4486'/x[k+'_file'])==x[k+'_sha256']
 before={n:sha(first/n) for n in files}
 refusal=subprocess.run([sys.executable,'-B',str(ROOT/'tools/ct_assetdata_analyze.py'),
  '--output-dir',str(first),'--discovery-dir',str(discovery)],capture_output=True,text=True)
 assert refusal.returncode and before=={n:sha(first/n) for n in files}
 source_guards=[]
 if originals:
  for x in rows('local-candidates.csv'):
   p=Path(x['path']);s=p.stat();assert sha(p)==x['sha256'],p
   assert s.st_size==int(x['size']) and s.st_mtime_ns==int(x['mtime_ns']),p
   source_guards.append(dict(path=str(p),content_hash_unchanged=True,size_mtime_unchanged=True))
 out.mkdir(parents=True)
 subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
  '--results',str(ROOT/'builds/phase19a/validated/results.json'),'--output',str(out/'unchanged-core-audit.json')],capture_output=True,check=True)
 for n,h in json.loads((ROOT/'builds/phase19c-fullhelper/final/source-manifest.json').read_text()).items():assert sha(ROOT/n)==h,n
 report=dict(status='PASS',repeat_identical_files=len(files),independent_WAV_header_checks=733,
  actual_record_arithmetic_checks=768,target_interval_checks=24576,zero_geometric_hits=True,
  zero_clipped_main_paths=True,zero_wrap=True,overwrite_refused=True,
  original_firmware_roundtrip_extract_core_prior_helper='PASS',original_user_files_checked=len(source_guards),
  CPU_instructions_executed=0,normal_asset_family_closed=False)
 for n,v in [('reproducibility.json',report),('user-source-guards.json',source_guards)]:
  with (out/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['first','repeat','output-dir','discovery-dir']:p.add_argument('--'+n,required=True,type=Path)
 p.add_argument('--verify-original-sources',action='store_true');a=p.parse_args()
 verify(a.first,a.repeat,a.output_dir,a.discovery_dir,a.verify_original_sources)
