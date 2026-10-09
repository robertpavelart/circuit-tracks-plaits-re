"""Targeted offline backend contracts and unseeded normal-domain ledger.
No CPU, device, network or invented filesystem/metadata contents.
"""
import argparse,csv,json,struct
from pathlib import Path
from ct_stock_load_audit import ROOT,verify_inputs,rows,sha
from ct_asset_bounds import A0,MAX_ADV,MAX_L,WATCH

def name_index(s):
 """Pure transcription of1F1C0..218; filename-prefix bytes only, not a file."""
 if len(s)<3 or not (48<=s[0]<=57 and 48<=s[1]<=57):return 255
 if s[2]==95:return ((s[0]-48)*10+s[1]-48)&255
 if len(s)<4 or not 48<=s[2]<=57 or s[3]!=95:return 255
 return ((s[0]-48)*100+(s[1]-48)*10+s[2]-48)&255

def collect(out,probe):
 out=out.resolve();base=(ROOT/'builds/phase19c-backendbound').resolve();probe=probe.resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh BACKENDBOUND child required')
 payload,_=verify_inputs();inputs={}
 def read(p):
  p=Path(p);raw=p.read_bytes();inputs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 b=read(ROOT/'firmware/circuittracks-firmware-4486.bin');allins=[]
 for folder in [probe,ROOT/'builds/phase19c-assetbound/probe-canonical',ROOT/'builds/phase19c-hostwrite/probe-final']:
  for n,h in json.loads(read(folder/'hashes.json')).items():assert sha(read(folder/n))==h
  allins+=json.loads(read(folder/'instructions.json'))
 by={x['PC']:x for x in allins}
 for x in allins:
  raw=bytes.fromhex(x['raw']);assert b[x['PC']-0x8010000:x['PC']-0x8010000+len(raw)]==raw
 def req(pc,mn,s):assert by[pc]['mnemonic']==mn and s in by[pc]['operands'],(hex(pc),by.get(pc))
 for pc,mn,s in [(0x8026618,'add.w','sb, lsl #2'),(0x8026620,'ldr','[sp, #0x20]'),
  (0x8026630,'movs','#0x12'),(0x8026672,'blx','r3'),(0x8026674,'cmp','#1'),
  (0x801f11e,'str','[r1]'),(0x801f166,'str','[r6, #8]'),
  (0x8025ce4,'movs','#0x13'),(0x8025d84,'bl','#0x8019cc6'),
  (0x8025e30,'ldr','[r0, #0xc]'),(0x8019cf6,'ldr','[r7, #0xc]'),
  (0x8019cfa,'subs','r4, r0, r4'),(0x8019cfe,'bls.w','#0x8019e10'),
  (0x8019df4,'ldrb','[r3], #1'),(0x8019dfa,'strb','[r2], #1'),
  (0x801a158,'movpl','r4, r0'),(0x803ae9a,'bhs','#0x803aed2'),
  (0x805c24a,'ldr','[r0, #8]'),(0x8036b02,'blx','r5'),
  (0x8049b94,'bl','#0x802968e'),(0x80297d6,'b.w','#0x801eb1e'),
  (0x8019af4,'and','r7, r2, #0x3f'),(0x8019c04,'strb','[r4, #0x10]'),
  (0x8019be8,'str','[r4, #0xc]'),(0x801f20e,'uxtb','r0, r0')]:req(pc,mn,s)
 def word(a):return struct.unpack_from('<I',b,a-0x8010000)[0]
 assert word(0x8037268)==0x20003730 # actual asset backend base
 assert word(0x8037264)==0x20006914 # separate owner slot
 assert word(0x801f1ac)==0x20003738 and word(0x801f1b8)==0x2000690c
 assert word(0x8025df4)==0x805b150
 assert word(0x801eb2c)==0x40003000
 init=read(ROOT/'builds/phase19c-hostwrite/final-v3/arm-initialized-data.bin')
 assert sha(init)=='2db584abde65123402067c89720f5a10e12c40650b700d6af2f13ed93743e04f'
 assert init[0x3730:0x3738]==bytes([5,5,0,1,2,3,4,0])
 categories=[]
 for c in range(5):
  a=0x805a4f8+12*c;tag,capacity=b[a-0x8010000:a-0x8010000+2]
  suffix=word(a+8);s=b[suffix-0x8010000:].split(b'\0',1)[0].decode('ascii')
  categories.append(dict(category=c,tag=tag,capacity=capacity,suffix=s,
   table_PC=hex(a),field4=hex(word(a+4)),list_layout='40 bytes/entry, presence bitmap'))
 assert categories[2]['capacity']==64 and categories[2]['suffix']=='_PCM.wav'
 listing=ROOT/'builds/phase3-selection0-channel0.asm';read(listing);dsp=rows(listing,payload)
 for pc,s in [(0x163,'x:$0012'),(0x175,'x:$0010'),(0x185,'x:$0011'),
  (0x189,'x:$0011'),(0x199,'#15'),(0x19b,'y:(r0)+'),(0x19d,'x:(r0)+')]:assert s in dsp[pc]['text']
 read(ROOT/'builds/phase19c-assetbound/final-v2/result.json')
 out.mkdir(parents=True)
 def emit(n,v):
  with (out/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 def csvout(n,rs):
  with (out/n).open('x',encoding='utf8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
 emit('selection-contract.json',dict(entry='08026610',end='0802667C',
  signature=['r0=selection-container C','r1=backend B','r2=category k','r3=index i','stack flags'],
  asset_inputs=dict(type=4,category=2,index='0..63',scope='FF -> currently selected container',flags=0),
  input_classes=['C:runtime PROJECT-DATA association','B:INIT constructor-selected object',
   'k:BOUNDED ENUM from initialized type map','i:CONSTANT loop indices0..63',
   'flags:CONSTANT0','presence/names:filesystem directory PROJECT-DATA / external origin UNRESOLVED'],
  lookup='category=C[28+4*k]; list=category[2C]; presence bit gates entry=table+40*i',
  failure='flags.bit0=0 and missing =>0x12; backend open returns1=>1; other final statuses=>0',
  absent_flags1_fallback='construct path with /%02d%s; not taken by flags0 stock asset read',
  internal_category_bound=False,index_bound='presence bitmap capacity64 for category2',
  directory_name_index='2 or3 decimal digits followed by underscore; low8 conversion; aliases and duplicate overwrites possible',
  returned='Status only; existing backend B retains open file/path state',
  length_or_aggregate_checks=False,categories=categories))
 emit('backend-object-graph.json',dict(correction='Prior ASSETBOUND backend20006914+8 attribution is incorrect',
  owner=dict(slot='20006914',constructor='080263F8',publication='0801F166 = [2000690C+8]',
   allocation=64,fields={'0':'active selection byte','1..20':'name','24':'parent link',
    '28..38':'5 category pointers','3C':'parent container'},vtable='not stored by263F8; plain container'),
  backend=dict(slot='20003738',read_base_literal='08037268 ->20003730',
   asset_call='08036AF6 loads[20003730+8] then36B02 calls vtable+10',
   constructor='08025C98',publication='0801F11E',allocation=144,
   fields={'0':'vtable805B150','4':'active file structure pointer','8':'allocated0x1028-byte (4136) file storage',
    'C':'open flag','D..':'stored source path'},
   methods={hex(i):hex(word(0x805b150+i)&~1) if word(0x805b150+i) else None for i in range(0,44,4)},
   size_method='vtable1C ->25E1C: open?[B+4][C]:0',
   lifecycle='25CB8 reuse same open path, close on change, open/create;25D10 close'),
  unused_alleged_slot='2000691C not established as this read object; no generic alias census'))
 checks=[
  ('26610','presence','category2 index<64 AND bit set','missing =>12; no L/file-size check'),
  ('3AE90..9A','directory ingest','parsed byte index!=FF and <capacity64','invalid names/indices skipped'),
  ('25CB8..5D0C','open','same-path reuse; otherwise open status','mode13; low6bits stored as file flags; no maximum sample bytes'),
  ('19BD0..C04','size provenance','directory-record+1C ->u32 file+C; mode flags stored atfile+10','actual size known; depends on backing directory data'),
  ('25D4C..5D92','read wrapper','B.open!=0; seek if requested offset differs from file+14','seek status ignored; read status checked'),
  ('19CD4..CF2','read eligibility','out_count=0; valid object, saved error0, read flag bit0','return errors before copy'),
  ('19CF6..9D02','read extent','count=min(requested,file+C-file+14)','EOF clamps count; no WAV L comparison'),
  ('19DF4..E0E','copy','copies available source prefix to destination and advances file position/count','does not clear untouched destination suffix'),
  ('1A14C..158','seek extent','offset>size and write flag bit1 clear => clamp to size','mode13 has write bit1; clamp not unconditional'),
  ('1A1CE..1DA','seek allocation','write flag controls cluster allocation vs traversal','filesystem capacity/failure; no 64-asset budget'),
  ('1A20A..21A','seek size','successful extending seek may increase file+C','backend offset<=original_size not guaranteed'),
  ('36B08..12','worker count','out_count==requested =>status0 else4','loader49ABE/49B36 ignores status'),
  ('49A96','header destination','cleared64 bytes before read','early no-copy failure =>zero header; partial prefix can reach parser'),
  ('49B36..58','main destination','no per-read buffer clear; status ignored','short/error reads may retain transformed staging suffix'),
  ('51BA0','header L','unsigned L<=19200000','unchanged local bound; no coupled backend/aggregate L test')]
 csvout('backend-checks.csv',[dict(address=a,check=c,condition=v,consequence=e) for a,c,v,e in checks])
 records=[];progress=[];critical=[]
 for i in range(64):
  records.append(dict(record=i,category=2,capacity=64,presence='UNKNOWN bit[i]',
   path='UNKNOWN scanned entry path; nominal fallback /%02d_PCM.wav NOT used when absent',
   file_size='',L_actual='',normal_L_min='',normal_L_max='',
   parser_L_domain='[0,19200000] if accepted; not a proven normal source domain',
   absent_consequence='zero header, invalid,advance256 if selection fails before copy',
   source_class='filesystem-backed selected-container PCM-category entry; exact PROJECT/SESSION/EXTERNAL origin UNRESOLVED'))
  progress.append(dict(record=i,A_in_actual='',A_in_predicate_min=hex(A0+256*i),
   A_in_predicate_max=hex(A0+MAX_ADV*i),normal_upper_bound='UNRESOLVED; no stronger bound recovered',
   A_formula='580000+256*i+256*sum(valid_j*floor(L_j/512),j<i)',
   page='((A&FFFF00)-2)mod2^24',main='same strict guard as ASSETBOUND; low cells excluded',
   padding='256 words from S+N; normal interval UNRESOLVED',normal_sequence=None))
  for p in [0,0x100,0x900,0xa00]:
   critical.append(dict(record=i,page=hex(p),normal_result='IMPOSSIBLE UNDER NORMAL BOUNDS' if i<2 else 'UNRESOLVED',
    predicate_result='EXCLUDED' if i<2 else 'POSSIBLE',
    constraint='sum(q_j,j<i)=(page+n*1000000-580000-256*i)/256; normal domains/aggregate/storage constraints unknown',
    normal_witness='',X_space='STATE-DEPENDENT'))
 csvout('source-records.csv',records);csvout('normal-address-progression.csv',progress);csvout('critical-pages.csv',critical)
 csvout('requested-cells.csv',[dict(target=n,start=hex(a),end=hex(z),classification='UNRESOLVED',
  geometry='all main and first2 padding EXCLUDED; later padding POSSIBLE in predicate envelope',
  normal_witness='',whole_firmware_ownership='NOT evaluated') for n,a,z in WATCH])
 emit('x11-sequence.json',dict(classification='STATE-DEPENDENT',
  per_record=[['49A5E->297D6->1EB1E','storeAAAA to40003000; no SHI/X11 operation'],
   ['49ABE','blocking backend read; cross-task SHI interleaving not closed'],
   ['49AC4->29626','width24 mailboxX12 only'],['49AD0->294AC','page cursor X10; retainsX11'],
   ['49AD6->295E4','width16 mailboxX12 only'],['49B58/49B94','data writes selected by retainedX11.bit15']],
  last_record_sequence=[['49BA8->29344 Y2C','read header publishesY space'],
   ['49BBC..49BEA','scalarC00,C01,C02,C03; cache updates requested+1'],
   ['49C0A','scalar802C; preceding cachedC04 differs => private address miss, X11.bit15=1']],
  conditional_later_records='Y under serialized complete stock headers/cache/no foreign mutation; does not prove all normal interleavings',
  first_record='prior X11 value unknown',unknown='foreign host transfers/cache mutations during backend waits; no global alias closure'))
 emit('missing-offline-data.json',dict(stop_rule=True,needed=[
  'Unmodified offline copy of the selected source pack/container directory, retaining actual names/subdirectories and missing entries',
  'All indexed entries in its PCM category (indices0..63), including complete original files, byte sizes and directory listing',
  'Container selection context and relevant existing _SESSION.ncs/_META.ncm files or exported index/path metadata tying it to that directory',
  'If claiming a firmware-enforced partition budget: offline backing-volume geometry/partition allocation metadata, or original storage image'],
  first_minimum='PCM directory listing with indexed paths, file sizes and unmodified complete headers through the data-length field; full files needed for read-failure/consistency proof',
  not_requested='No live export, hardware connection or transmissions; use already available offline copies',
  residual_nonfile_obligation='X11 foreign ordering and exact normal transition ancestry remain independent'))
 emit('result.json',dict(asset_family='C still unresolved',X_space='STATE-DEPENDENT',
  CPU_instructions_executed=0,normal_aggregate_bound=None,normal_lengths=None,
  actual_normal_intersection=None,normal_asset_mutation_closed=False,
  backend_slot_correction='20003738, not2000691C',
  file_read_count_clamped=True,header_length_compared_to_file_size=False,
  read_only_seek_bound_unconditional=False,backend_open_mode=0x13,
  indices_capacity=64,missing_entries_permitted=True,main_exclusions_retained=True,
  first_two_exclusions_retained=True,parent_replay_admitted=False,target_bridge_recomputed=False,
  independent=['other host cache/order/ancestry','P204B','other DSP indirect writes'],
  best_next_step='Obtain existing offline selected PCM directory/files and selection metadata; compute actual cumulative metadata advancement without inventing lengths',
  stopping_rule='Data-dependent bound needs missing source files; no broader analysis launched'))
 for n in ['tools/ct_backend_bounds.py','tools/ct_backend_probe.py']:read(ROOT/n)
 emit('inputs.json',inputs);verify_inputs()
 emit('hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
 print('Backend contract,64 unseeded domains,256 critical-page tests; normal family UNRESOLVED')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['output-dir','probe-dir']:p.add_argument('--'+n,required=True,type=Path)
 a=p.parse_args();collect(a.output_dir,a.probe_dir)
