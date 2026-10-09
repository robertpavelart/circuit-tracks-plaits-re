"""Verify PACKLINK with real immutable archives and byte algebra only.

Does not run Components/firmware, build wire messages, decode audio, or access
devices. Existing local source reads are optional preservation checks.
"""
import argparse,csv,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ct_stock_load_audit import verify_inputs
from ct_packlink_audit import data_pack,data_unpack
from ct_backend_bounds import name_index

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p):return json.loads(p.read_text(encoding='utf8'))
def rows(p):
 with p.open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))

def verify(first,repeat,arm,out,originals):
 base=(ROOT/'builds/phase19c-packlink').resolve();out=out.resolve()
 if out.exists() or out==base or not out.is_relative_to(base):
  raise ValueError('Fresh PACKLINK checks child required')
 files={p.relative_to(first).as_posix() for p in first.rglob('*') if p.is_file()}
 assert files=={p.relative_to(repeat).as_posix() for p in repeat.rglob('*') if p.is_file()}
 for n in files:assert (first/n).read_bytes()==(repeat/n).read_bytes(),n
 for n,h in obj(first/'hashes.json').items():assert sha(first/n)==h,n
 for n,h in obj(first/'inputs.json').items():assert sha(ROOT/n)==h,n
 for w in obj(first/'source-witnesses.json'):
  raw=(ROOT/w['source']).read_bytes();s=raw.decode('utf8')
  assert hashlib.sha256(raw).hexdigest()==w['source_sha256']
  assert s[w['character_start']:w['character_end']]==w['excerpt']
  assert raw[w['UTF8_byte_start']:w['UTF8_byte_end']].decode('utf8')==w['excerpt']
 assert obj(arm/'provenance.json')['source_sha256']==sha(ROOT/'tools/ct_packlink_arm.py')
 assert obj(first/'input-manifest-status.json')[0]['all_other_members_verified']
 old=ROOT/'builds/phase19c-assetdata/final'
 rm=rows(old/'record-map.csv');pr=rows(old/'actual-address-progression.csv')
 native=rows(first/'mapped-native-progression.csv');ds=obj(old/'datasets.json')
 assert len(rm)==len(pr)==len(native)==768 and len(ds)==12
 bytes_checked=0;headers=0;missing=0;chunks={256:0,8192:0};small_tails=[]
 for snap in obj(ROOT/'builds/phase19c-assetdata/discovery-v2/snapshots.json'):
  archive=ROOT/snap['snapshot'];assert sha(archive)==snap['sha256']
  key=snap['sha256'][:16];records=[r for r in rm if r['dataset_id']==key]
  assert [int(r['record']) for r in records]==list(range(64))
  with zipfile.ZipFile(archive) as z:
   idx=json.loads(z.read('index.json'));A=0x580000
   for r in records:
    i=int(r['record']);assert idx['samples'][i]['url']==f'samples/sample_{i}.wav'
    assert name_index(f'{i:02d}_'.encode())==i
    if r['present']=='True':
     raw=z.read(r['member']);bytes_checked+=len(raw);headers+=1
     q=int.from_bytes(raw[16:20],'little');L=int.from_bytes(raw[24+q:28+q],'little')
     assert q==16 and L==int(r['L']) and len(raw)>=44+L
     assert (int.from_bytes(raw[22:24],'little'),int.from_bytes(raw[24:28],'little'),
             int.from_bytes(raw[34:36],'little'))==(1,48000,16)
     for size in chunks:
      for o in range(0,len(raw),size):
       chunk=raw[o:o+size];packed=data_pack(chunk)
       assert len(packed)==len(chunk)+(len(chunk)+6)//7
       assert all(x<128 for x in packed)
       assert data_unpack(packed)==chunk
       chunks[size]+=1
      tail=len(raw)%size
      if 0<tail<7:small_tails.append(dict(dataset_id=key,member=r['member'],chunk_size=size,
       source_tail_bytes=tail,encoded_tail_bytes=tail+(tail+6)//7,
       caveat='Pure byte inverse passes; authentic SDIV trap state not established'))
     A+=256+((L&0xfffffe00)>>1)
    else:
     missing+=1;assert r['member'] not in z.namelist() and not idx['samples'][i]['name']
     assert not r['L'];A+=256
   d=next(d for d in ds if d['dataset_id']==key)
   assert A==int(d['A64'],16) and A<0xe80000
 assert (headers,missing)==(733,35)
 for r,p,n in zip(rm,pr,native):
  assert (r['dataset_id'],r['record'])==(p['dataset_id'],p['record'])==(n['dataset_id'],n['record'])
  for k,v in p.items():
   if k!='scope':assert n[k]==v,(k,n[k],v)
  assert n['scope']=='SOURCE-DERIVED native mapping for completed identical import; not observed device state'
  assert int(n['native_slot'])==int(r['record'])
  assert n['native_L_status']==('VERIFIED IDENTICAL (transferred header)' if r['present']=='True' else 'ABSENT after successful DELETE')
 ids=rows(first/'archive-identities.csv')
 assert {x['name']:x['remote_id'] for x in ids if x['remote_id']}=={'MyPack_01':'530016','*New Pack1':'521732'}
 hist=obj(first/'historical-selection.json')
 assert len(hist['events'])==1 and hist['events'][0]['destination_packId']==23
 assert hist['events'][0]['pack_name']=='DLR / Sofa Sound' and not hist['queue_is_authoritative']
 result=obj(first/'result.json');assert result['selected_pack']=='UNRESOLVED'
 assert not result['normal_asset_family_closed'] and not result['parent_replay_admitted']
 policy=obj(first/'application-policy.json')
 assert int(policy['conservative_A64_bound'],16)==0x580000+9436800+240+64*256<0x1000000
 # Integer rounding boundary: JS Math.round(-.5) gives negative zero, not <0.
 assert (9436800-(9436800+240))/48000*100==-.5
 assert (9436800-(9436800+241))/48000*100<-.5
 _,protected=verify_inputs()
 import ct_fw_tool
 syx=ROOT/'original/circuittracks-firmware-4486.syx'
 b=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
 assert ct_fw_tool.decode_syx(syx)['firmware']==b
 assert ct_fw_tool.build_syx(syx,b)==syx.read_bytes()
 for x in obj(ROOT/'firmware/dsp/build-4486/manifest.json')['blocks']:
  for k in ['stream','payload']:
   assert sha(ROOT/'firmware/dsp/build-4486'/x[k+'_file'])==x[k+'_sha256']
 for n,h in obj(ROOT/'builds/phase19c-fullhelper/final/source-manifest.json').items():assert sha(ROOT/n)==h,n
 refusals=[]
 for script,args in [
  ('tools/ct_packlink_audit.py',['--arm-dir',str(arm),'--output-dir',str(first)]),
  ('tools/ct_packlink_arm.py',['--output-dir',str(arm)]),
  ('emulator/tests/verify_packlink.py',['--first',str(first),'--repeat',str(repeat),
    '--arm-dir',str(arm),'--output-dir',str(first)])]:
  p=subprocess.run([sys.executable,'-B',str(ROOT/script),*args],capture_output=True,text=True)
  assert p.returncode and 'Fresh PACKLINK' in p.stderr,(script,p.stderr)
  refusals.append(script)
 for n in files:assert (first/n).read_bytes()==(repeat/n).read_bytes(),n
 guards=[]
 if originals:
  app=obj(ROOT/'builds/phase19c-packlink/app-1.72.1/provenance.json')
  sources=[dict(path=app['source'],size=app['size'],mtime_ns=app['mtime_ns'],sha256=app['source_sha256'])]
  sources+=obj(ROOT/'builds/phase19c-packlink/metadata/sources.json')
  event=obj(ROOT/'builds/phase19c-packlink/event/provenance.json')
  sources.append(dict(path=event['source'],size=event['size'],mtime_ns=event['mtime_ns'],sha256=event['source_sha256']))
  sources+= [dict(path=x['source'],size=x['size'],mtime_ns=x['mtime_ns'],sha256=x['sha256'])
             for x in obj(ROOT/'builds/phase19c-assetdata/discovery-v2/snapshots.json')]
  for x in {x['path']:x for x in sources}.values():
   p=Path(x['path']);s=p.stat();assert (s.st_size,s.st_mtime_ns)==(x['size'],x['mtime_ns'])
   assert sha(p)==x['sha256'],p
   guards.append(dict(path=str(p),hash_size_mtime_unchanged=True))
 out.mkdir(parents=True)
 subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
  '--results',str(ROOT/'builds/phase19a/validated/results.json'),
  '--output',str(out/'unchanged-core-audit.json')],capture_output=True,check=True)
 report=dict(status='PASS',verifier_sha256=sha(Path(__file__)),repeat_identical_files=len(files),source_witnesses=len(obj(first/'source-witnesses.json')),
  real_WAVs_byte_checked=headers,actual_missing_slots_checked=missing,real_WAV_bytes_checked=bytes_checked,
  pure_data_chunks_checked=chunks,small_tails_CPU_state_unresolved=small_tails,
  native_map_reuse_rows=768,identity_links=2,historical_event_is_selection=False,
  original_firmware_roundtrip_all10_extracts_core_prior_helper='PASS',overwrite_refusals=refusals,
  original_user_sources_preserved=len(guards),CPU_instructions_executed=0,
  Components_executed=False,wire_messages_constructed_or_transmitted=False,normal_asset_family_closed=False)
 for n,v in [('reproducibility.json',report),('user-source-guards.json',guards)]:
  with (out/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(report,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['first','repeat','arm-dir','output-dir']:p.add_argument('--'+n,required=True,type=Path)
 p.add_argument('--verify-original-sources',action='store_true');a=p.parse_args()
 verify(a.first,a.repeat,a.arm_dir,a.output_dir,a.verify_original_sources)
