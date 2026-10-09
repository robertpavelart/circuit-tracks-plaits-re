"""Offline source-derived archive/native contract; no app or firmware execution.
Native names are formulas, not manufactured files. Existing maps are reused only
under completed unchanged transfer/presence premises; selected source stays unknown.
"""
import argparse,csv,io,json,struct
from pathlib import Path
from ct_stock_load_audit import ROOT,sha,verify_inputs
from ct_backend_bounds import name_index

APP=ROOT/'builds/phase19c-packlink/app-1.72.1'
ASSETS=ROOT/'builds/phase19c-assetdata/final'
def data_pack(raw):
 """Worker f bit packing only: no headers, messages or sending API."""
 out=bytearray()
 for k in range(0,len(raw),7):
  g=raw[k:k+7];out.append(sum(((v>>7)&1)<<i for i,v in enumerate(g)))
  out.extend(v&127 for v in g)
 return bytes(out)
def data_unpack(raw):
 """ARM392FC/partial39384 bit inverse, conditional on routine completing."""
 out=bytearray()
 for k in range(0,len(raw),8):
  g=raw[k:k+8]
  out.extend((v&127)|(((g[0]>>i)&1)<<7) for i,v in enumerate(g[1:]))
 return bytes(out)

def collect(out,arm):
 out=out.resolve();arm=arm.resolve();base=(ROOT/'builds/phase19c-packlink').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh PACKLINK child required')
 payload,_=verify_inputs();inputs={};witness=[];manifest_status=[]
 def read(p):
  raw=p.read_bytes();inputs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def obj(p):return json.loads(read(p))
 def csvread(p):return list(csv.DictReader(io.StringIO(read(p).decode('utf8'))))
 for folder in [APP,arm,ROOT/'builds/phase19c-packlink/metadata',ASSETS,
  ROOT/'builds/phase19c-backendbound/probe-canonical']:
  for n,h in obj(folder/'hashes.json').items():
   if n=='hashes.json':
    # Preserved historical metadata manifest included its just-opened empty self.
    # Check this precise defect; all evidence members are still verified below.
    assert folder==ROOT/'builds/phase19c-packlink/metadata' and h==sha(b'')
    manifest_status.append(dict(source=str(folder.relative_to(ROOT)),
     defect='Historical self entry hashes empty open file; excluded from member verification',
     original_preserved=True,all_other_members_verified=True))
    continue
   assert sha(read(folder/n))==h,(folder,n)
 provenance=obj(APP/'provenance.json');package=obj(APP/'code/package.json');assert package['version']=='1.72.1'
 js=APP/'code/ember-dist/assets/main-DHaPxgL3.js';s=read(js).decode('utf8')
 worker=APP/'code/ember-dist/assets/decode-worker-cLhwFYVI.js';ws=read(worker).decode('utf8')
 def span(label,text,p,anchor,extent):
  start=text.index(anchor);end=min(len(text),start+extent);excerpt=text[start:end]
  witness.append(dict(label=label,source=p.relative_to(ROOT).as_posix(),source_sha256=sha(p.read_bytes()),
   character_start=start,character_end=end,UTF8_byte_start=len(text[:start].encode()),
   UTF8_byte_end=len(text[:end].encode()),excerpt=excerpt))
 for label,a,n in [
  ('archive slot loader','N7=e=>class extends e{product="circuit-tracks"',2000),
  ('entity slots/setter','get fileData(){return this.binary}set fileData(e){this.binary=e}',1400),
  ('WAV sample/raw ZIP path','K0=class extends f0',2200),
  ('Tracks sample limits','J5=class extends K0',370),
  ('Tracks sample collection','d7=class extends H0',720),
  ('Sample aggregate/rounding gate','H0=class extends y0',730),
  ('Tracks aggregate constant','l7=9436800',180),
  ('Filename sanitizer','A1=r((e,t)=>',490),
  ('PCM enum','PCM:5',180),
  ('Sender rename types','{SESSION:LUe,PCM:zUe}=UD',180),
  ('payload clone','S8=class extends t4',1950),
  ('slot prefix rename','Q4=class extends t4',1050),
  ('native sample name source','get fileName(){let e=this.name',500),
  ('UI destination/gate','sendPack=sA(()=>({context:this,generator:function*(e){let t=!1;try{this.waiting=!0,this.transferRate=null',2150),
  ('pack sender','sendPackToCircuit=sA(',2150)]:span(label,s,js,a,n)
 span('worker data encoding',ws,worker,'function f(e)',550)
 span('worker explicit destination/slot/delete',ws,worker,'initContentTransfer({ data:',1250)
 assert 's[t].target.fileData=await i.async("arraybuffer")' in s
 assert 'set fileData(e){this.binary=e}' in s
 assert 'samples.checkSampleTime(BUe)' in s
 assert 'else this.buffers.push(this.createSysexMessage(8, s, o, r))' in ws
 b=read(ROOT/'firmware/circuittracks-firmware-4486.bin');ins=[]
 for folder in [arm,ROOT/'builds/phase19c-backendbound/probe-canonical']:
  ins+=obj(folder/'instructions.json')
 by={x['PC']:x for x in ins}
 for x in ins:
  r=bytes.fromhex(x['raw']);assert b[x['PC']-0x8010000:x['PC']-0x8010000+len(r)]==r
 def req(pc,mn,frag):assert by[pc]['mnemonic']==mn and frag in by[pc]['operands'],(hex(pc),by.get(pc))
 for pc,mn,f in [(0x8039578,'tbb','[pc, r1]'),(0x803958a,'movs','#4'),
  (0x8039754,'b','#0x8039b0e'),
  (0x8039b94,'bl','#0x803cc34'),(0x803cc40,'movs','#5'),
  (0x8036d6c,'bl','#0x8026680'),(0x80266b2,'bl','#0x803b04c'),
  (0x8036d7c,'bl','#0x802645e'),(0x8036c76,'movs','#1'),
  (0x8036c7a,'bl','#0x80367da'),(0x8036c94,'blx','ip'),
  (0x80393c2,'subs','r3, r3, #1'),(0x8039e96,'bl','#0x801f1c0'),
  (0x803981a,'str','[sp]'),(0x803676c,'push','lr'),
  (0x8036770,'cmp','#0xff'),(0x803678c,'bl','#0x801f1a2'),
  (0x80367c2,'bl','#0x8026064'),(0x8036f68,'mov.w','#0x1000'),
  (0x8036f8e,'blx','ip'),(0x8036fae,'blx','ip'),
  (0x8036fde,'bl','#0x802645e')]:req(pc,mn,f)
 # TBB table5 selectsPCM→internal4, and command8→delete dispatcher entry.
 assert b[0x803957c-0x8010000+2]==7
 assert b[0x8039734-0x8010000+7]==12
 assert b[0x803b10c-0x8010000:0x803b114-0x8010000]==b'/%02d%s\0'
 assert b[0x805c058-0x8010000:0x805c058-0x8010000+9]==b'_PCM.wav\0'
 ds=obj(ASSETS/'datasets.json');rm=csvread(ASSETS/'record-map.csv');maps=csvread(ASSETS/'actual-address-progression.csv')
 api=obj(ROOT/'builds/phase19c-packlink/metadata/json/2950cc97d1b324b162853f5ca05f4d2606b270f1e67938393dbed508a92f06f2.json')
 events=obj(ROOT/'builds/phase19c-packlink/event/events.json');eventp=obj(ROOT/'builds/phase19c-packlink/event/provenance.json')
 out.mkdir(parents=True)
 def emit(n,v):
  with (out/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 def csvout(n,rs):
  keys=list(dict.fromkeys(k for r in rs for k in r))
  with (out/n).open('x',encoding='utf8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rs)
 identities=[];mapped=[];cells=[]
 for d in ds:
  index=obj(ASSETS/'metadata'/f"{d['dataset_id']}-index.json")
  linked=[p for p in api['circuit_tracks_packs'] if p['metadata']==index]
  assert len(linked)<=1
  identities.append(dict(dataset_id=d['dataset_id'],name=d['name'],archive_sha256=d['archive_sha256'],
   cache_key=Path(d['source']).name,product=index['product'],version=index['version'],
   archive_embedded_id='',remote_id=linked[0]['id'] if linked else '',
   identity_evidence='Exact API metadata/index.json equality' if linked else 'Content hash + archive metadata only',
   remote_id_is_native_destination=False,installed_or_selected='UNRESOLVED'))
  assert d['slot_mapping_verified'] and d['geometric_hit_rows']==0
  mapped.append(dict(dataset_id=d['dataset_id'],name=d['name'],present=d['present_PCM_files'],
   absent_indices=json.dumps(d['missing_indices']),native_order='VERIFIED PRESERVED 0..63 for unedited mapped import',
   native_L='VERIFIED IDENTICAL for transferred header bytes',A64=d['A64'],
   reused_input='builds/phase19c-assetdata/final/actual-address-progression.csv',
   cell_classification='DATASET-SPECIFIC NORMAL ASSET EXCLUDED',
   premises='Complete unchanged import into corresponding clean slot set; checksum-skipped existing content must be identical; no subsequent foreign modification',
   actual_selected='UNRESOLVED'))
 assert len(rm)==len(maps)==768
 for r,p in zip(rm,maps):
  assert (r['dataset_id'],r['record'])==(p['dataset_id'],p['record'])
  i=int(r['record']);assert name_index(f'{i:02d}_'.encode())==i
  p=dict(p);p['scope']='SOURCE-DERIVED native mapping for completed identical import; not observed device state'
  p['native_slot']=i;p['native_L_status']='VERIFIED IDENTICAL (transferred header)' if r['present']=='True' else 'ABSENT after successful DELETE'
  cells.append(p)
 emit('source-witnesses.json',witness);emit('input-manifest-status.json',manifest_status)
 csvout('archive-identities.csv',identities)
 csvout('mapped-datasets.csv',mapped);csvout('mapped-native-progression.csv',cells)
 emit('historical-selection.json',dict(events=events,source=eventp,
  selected_pack_identity='UNRESOLVED: no association to current loader context',
  queue_is_authoritative=False,remote_ids_and_native_ids_are_separate=True))
 emit('content-contract.json',dict(app_version='1.72.1',ASAR_sha256=provenance['source_sha256'],
  archive_slot='samples[i]→model target at i; models constructed withslotIndex=i',
  body='ZIP arraybuffer→fileData setter→binary→push .slice(0)→reversible7-bit chunk encoding→ARM392FC→raw file writes',
  native_length='VERIFIED IDENTICAL for transferred archive header; all733 applicable headersfmt16',
  bytes='No resample/re-encode/header rewrite in ZIP path; complete file equality conditional on successful replacement/write',
  independent_audio_file_path='K0.loadFile may decode/render mono48kHz and re-encode if incompatible; not called by Tracks ZIP loader',
  transforms=['Archive load: none','Transfer: reversible packet bit packing only',
   'Native rename/copy worker36D82: raw read/write chunks up to4096, no WAV conversion'],
  decoder_tail_caveat='392FC uses SDIV with full-group count; encoded tails below8 bytes need nontrapping divide-by-zero state to complete; no authentic CPU state assumed',
  checksum_skip='CRC32+name test may reuse existing slot; offline identity of skipped content NOT established',
  missing='Reset model.binary toundefined; worker empty branch emits DELETE opcode8, no zeroWAV; firmware bitmap erase/unlink/reindex',
  presence_premises='Successful delete/write, no additional native duplicate-index entries/foreign writes',
  native_filename={'initial_missing':'%02d(index)+_PCM.wav (firmware fallback3B0B4)',
   'post_rename':'%02d(index)+_+sanitize(sanitize(name truncated to23 or PCM)+.wav), then7-bit char bytes',
   'observed_native_names':None,'parser':'1F1C0 sees00..63_ prefix and returns same i'},
  container='Explicit destinationpackId from modal; wiretype5→internal4→category2→3676C destination selection→26610 per-slot; 3676C FF means existing selection, FE rejects, ordinary IDs select via26064',
  current_selection='Import target is not evidence of actual current playback/container selection'))
 emit('application-policy.json',dict(scope='Recovered Components1.72.1 unchanged well-formed Tracks pack send route only',
  MAX_SAMPLES=9436800,unit='16-bit sample count; sumL/2',per_file_loadFile_max_bytes=9436844,
  archive_loadFile_validator_invoked=False,checkSampleTime_gate=True,
  rounding='Math.round((9436800-sumL/2)/48000*100)/100<0; allows at most240 excess samples on integer domain',
  conservative_A64_bound=hex(0x580000+9436800+240+64*256),
  implication='Below1000000; no lowpage wrap under scoped bound, but not a universal firmware/import policy',
  foreign_edit_directAPI_malformed_and_other_versions_closed=False))
 emit('gates.json',dict(A_slot_i_to_native_i='YES, recovered intended completed import path',
  B_native_L_equals_archive_L='YES for transferred archive header; skipped native slots unresolved',
  C_missing_preserved='YES after successful DELETE/reindex',D_selected_identity='NO; historical candidate DLRdestination23 only',
  E_remove_for_selected='NO selected native source not established',
  F_remove_for_twelve='Conditional YES for completed identical mapped datasets; actual installations unknown',
  G_universal_closed='NO',H_further_asset_analysis='NO without new offline native/selection evidence; static correspondence recovered',
  next_independent_blocker='P204B; not analyzed in this phase'))
 emit('result.json',dict(offline=True,CPU_instructions_executed=0,app_executed=False,packets_generated_or_sent=False,
  mapped_archives=12,header_length_sources=733,mapped_slots=768,geometry_hits=0,
  installed_app_scope='1.72.1',slot_mapping='VERIFIED PRESERVED',length_mapping='VERIFIED IDENTICAL on transferred headers',
  selected_pack='UNRESOLVED',normal_asset_family_closed=False,X11='STATE-DEPENDENT',
  parent_replay_admitted=False,target_bridge_recomputed=False,
  historical_candidate='DLR / Sofa Sound -> native destination23 (2024 event; not current selection)',
  stop_asset_branch=True,best_next_step='Move to the independent P204B producer/address-domain obligation, retaining scoped asset premises',
  verification_scope='Static source contracts + actual archive data, not observations of native install execution'))
 for n in ['tools/ct_packlink_audit.py','tools/ct_packlink_arm.py','tools/ct_packlink_extract.py','tools/ct_packlink_metadata.py','tools/ct_packlink_event.py']:read(ROOT/n)
 emit('inputs.json',inputs);verify_inputs()
 emit('hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
 print('12 scoped native mappings;733 actual header lengths;768 slots; selected identity UNRESOLVED')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path)
 p.add_argument('--arm-dir',required=True,type=Path);a=p.parse_args();collect(a.output_dir,a.arm_dir)
