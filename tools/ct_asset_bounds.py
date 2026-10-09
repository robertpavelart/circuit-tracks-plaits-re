"""Offline ASSETBOUND predicate-domain algebra, not record contents or CPU replay.
All output paths must be fresh children of builds/phase19c-assetbound.
The upper-envelope model does not assert normal source independence or X space.
"""
import argparse,csv,json,struct
from pathlib import Path
from ct_stock_load_audit import ROOT,verify_inputs,sha
from ct_hostwrite_audit import intervals

A0=0x580000;LIMIT=0xe80000;MOD=1<<24;MAX_L=19200000
MAX_D=(MAX_L&0xfffffe00)>>1;MAX_ADV=256+MAX_D
WATCH=[('selectors',0x95a,0x960),('effect_table',0x9db,0xa12)]+[
 ('descriptor_'+hex(a),a,a+1) for a in range(0xeb,0x154,8)]

def page(a):return ((((a>>8)&0xffff)<<8)-2)&0xffffff
def advance(length,valid=True):
 if valid and not 0<=length<=MAX_L:raise ValueError('Outside recovered accepted length domain')
 return 256+((length&0xfffffe00)>>1) if valid else 256
def emitted(a,length,valid=True):
 """Actual main words for an aligned virtual A, using the strict chunk guard."""
 if a%256 or not A0<=a<=A0+64*MAX_ADV:raise ValueError('Outside asset envelope')
 if not valid:return 0
 advance(length)
 d=(length&0xfffffe00)>>1
 if a>=LIMIT:return 0 # no 32-bit addition wrap in this recovered domain
 full,part=divmod(d,1024)
 permitted=(LIMIT-1-a)//1024
 n=min(full,permitted)*1024
 if full<=permitted and part and a+n+part<LIMIT:n+=part
 return n
def first_residue(lo,hi,residue):
 a=lo+((residue-lo)%MOD)
 return a if a<=hi else None
def intersect(parts,lo,hi):return any(a<hi and b>lo for a,b in parts)

def collect(out,probe):
 out=out.resolve();probe=probe.resolve();base=(ROOT/'builds/phase19c-assetbound').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh ASSETBOUND child required')
 _,protected=verify_inputs();inputs={}
 b=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
 old=ROOT/'builds/phase19c-hostwrite/probe-final'
 allins=[]
 for folder in [probe,old]:
  hashes=json.loads((folder/'hashes.json').read_text())
  for name,h in hashes.items():
   p=folder/name;raw=p.read_bytes();assert sha(raw)==h
   inputs[p.relative_to(ROOT).as_posix()]=h
  allins+=json.loads((folder/'instructions.json').read_text())
 by={x['PC']:x for x in allins}
 for x in allins:
  raw=bytes.fromhex(x['raw']);assert b[x['PC']-0x8010000:x['PC']-0x8010000+len(raw)]==raw
 def req(pc,mn,s):assert by[pc]['mnemonic']==mn and s in by[pc]['operands'],hex(pc)
 for pc,mn,s in [(0x8051be4,'ldr','[r5, #4]'),(0x8051bea,'bhs','#0x8051c02'),
  (0x8051bf2,'ldreq','[r4, #0x18]'),(0x8051bfe,'cmpeq','#0x10'),
  (0x8049ad0,'bl','#0x80294ac'),(0x8049b18,'bhs','#0x8049b6e'),
  (0x8049b94,'bl','#0x802968e'),(0x8049a70,'blt','#0x8049a52')]:req(pc,mn,s)
 assert struct.unpack_from('<I',b,0x8051c0c-0x8010000)[0]==MAX_L+1
 for a,s in [(0x8051c10,b'RIFF'),(0x8051c18,b'WAVE'),(0x8051c20,b'fmt '),(0x8051c28,b'data')]:
  assert b[a-0x8010000:a-0x8010000+4]==s
 out.mkdir(parents=True)
 def emit(n,v):
  with (out/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 def csvout(n,rs):
  with (out/n).open('x',encoding='utf8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
 records=[];progress=[];effective=[];checks=[];page_domains=[];wraps=[]
 for i in range(64):
  lo=A0+i*256;hi=A0+i*MAX_ADV
  records.append(dict(record=i,source='Read-request selector (4,i,FF); queue opcode6; backend read via 36B02',
   header_buffer='2000665C; cleared/read 64 bytes, reused',concrete_L='',
   L_domain='valid: unsigned [0,19200000]; invalid: not used',
   source_class='Runtime read-request/header buffer VERIFIED; backing storage/normal data domain UNRESOLVED',
   validity='PROJECT-DATA; no record contents supplied',normal_domain='UNRESOLVED'))
  progress.append(dict(record=i,A_in_min=hex(lo),A_in_max=hex(hi),A_step=256,
   R8_min=256,R8_max=MAX_ADV,R8_step=256,A_out_min=hex(lo+256),A_out_max=hex(hi+MAX_ADV),
   exact_sequence='A_i=580000+256*i+256*sum(q_j,j<i); q_j=valid_j*floor(L_j/512)',
   page_formula='S=((A_i & FFFF00)-2) mod 2^24',actual_A='',actual_S='',
   domain='Predicate-permitted envelope; source correlations unresolved'))
  pages={a&0xffff00 for a in range(lo,min(hi,lo+MOD-256)+1,256)}
  # Enumerate at most 65536 pages, not arbitrary metadata words or record assignments.
  assert len(pages)==(1 if i==0 else (37501 if i==1 else 65536))
  page_domains.append(dict(record=i,distinct_pages=len(pages),every_page_permitted=len(pages)==65536,
   bit31_24_nonzero_possible=hi>=MOD,repeated_page_between_records_possible=i>=2,
   projection='A mod 2^24, aligned 256; no 32-bit progression wrap'))
  main_max=min(MAX_D,((LIMIT-1-lo)//256)*256) if lo<LIMIT else 0
  # Universal main envelope: virtual guard admits only A<limit, all A>=A0.
  main_env=[[A0-2,LIMIT-2]] if main_max else []
  # Padding contains main-end+256; for A>=limit it starts at fresh S with N=0.
  # First two records cannot project to low pages. Later envelope has all pages.
  pad_env=[[A0-2,max(hi+254,LIMIT+254)]] if i<2 else [[0,MOD]]
  effective.append(dict(record=i,part='main',N_min=0,N_max=main_max,
   chunk_words=1024,tail_words='0,256,512,768',width_bits=16,
   exact_intervals='split24(S,N(A,L)); N from strict pre-chunk guard',
   conservative_union=json.dumps(main_env),actual_interval='',space='X11.bit15 retained; X/Y UNRESOLVED'))
  effective.append(dict(record=i,part='padding',N_min=256,N_max=256,
   chunk_words=256,tail_words=0,width_bits=16,
   exact_intervals='split24((S+N) mod 2^24,256); no new setup/limit test',
   conservative_union=json.dumps(pad_env),actual_interval='',space='X11.bit15 retained; X/Y UNRESOLVED'))
  for name,x,y in WATCH:
   for part in ['main','padding']:
    witnesses=[]
    if part=='padding':
     # Existential PAGE residues; N=0 is allowed by invalid OR valid L<512.
     # Do not assign any L_j/header bytes to any record.
     for residue in [(x&~255),((x&~255)+256)&0xffffff]:
      a=first_residue(lo,hi,residue)
      if a is not None and intersect(intervals(page(a),256),x,y):
       witnesses.append(dict(page=hex(residue),A_condition=hex(a),
        condition='N=0; predicate permits invalid header or valid L<512; no source feasibility asserted',
        intervals=intervals(page(a),256)))
    status='INTERSECTION POSSIBLE' if witnesses else 'EXCLUDED FOR ALL VALID L'
    if part=='main':assert not intersect(main_env,x,y)
    if part=='padding':assert bool(witnesses)==(i>=2)
    checks.append(dict(record=i,part=part,target=name,target_start=hex(x),target_end=hex(y),
     predicate_domain_result=status,conditions=json.dumps(witnesses,sort_keys=True),
     normal_result='PROJECT-DATA DEPENDENT' if witnesses else 'NORMAL ASSET EXCLUDED (local stable/framed envelope)',
     actual_intersection='',X_space='Requires X11.bit15=0; not proven here'))
  w=first_residue(lo,hi,0)
  wraps.append(dict(record=i,wrap_possible=w is not None,condition='A mod 2^24=0; A>=E80000 => main N=0',
   A_condition=hex(w) if w is not None else '',padding_high='[FFFFFE,1000000)' if w is not None else '',
   padding_low='[0,FE)' if w is not None else '',actual_wrap='UNRESOLVED'))
 csvout('records.csv',records);csvout('address-progression.csv',progress)
 csvout('effective-intervals.csv',effective);csvout('requested-cell-intersections.csv',checks)
 emit('page-domains.json',page_domains);emit('wrap-domains.json',wraps)
 emit('header-predicate.json',dict(base='p=2000665C',fields={'p+0':'RIFF','p+8':'WAVE',
  'p+C':'fmt ','p+10':'u32 q; unchecked offset','p+14+q':'data','p+18+q':'L<=19200000',
  'p+16':'u16==1','p+18':'u32==48000','p+22':'u16==16'},
  unchecked=['q bounds','q==16','format tag p+14','RIFF size p+4','byte rate p+1C',
    'block align p+20','L even','actual file length','aggregate64 asset limit','read success'],
  source_buffer_bytes=64,stable_read_premise='No foreign mutation between repeated predicate and accessor',
  compare='52B8A bounded string compare; nonzero signature chars make equality exact four bytes'))
 emit('source-provenance.json',dict(selector=['u32 type=4','u32 index=i (0..63)','u32 scope=FF'],
  header_read=dict(call=0x8049abe,offset=0,bytes=64,destination=0x2000665c,status_ignored=True),
  queue=dict(wrapper=0x803cbd6,submit=0x803ca52,opcode=6,wait=0x8022a46,
   worker=0x8022ae4,table=0x8022b28,case6=0x8022bbe,read_handler=0x8036a7e),
  backend=dict(selection=0x80367da,select_call=0x8026610,global_object=0x20006914,
   object_field=8,read_virtual_offset=0x10,read_call=0x8036b02,
   completion_count_checked_at=0x8036b08,normal_validation='UNRESOLVED upstream'),
  progress_object=dict(address=0x20000a7c,init_vtable=0x805b9ec,
   methods=[0x8049c88,0x8049c96,0x8049c8a,0x8049cfa],
   role='Callbacks around loop; not a firmware-resident table of64 asset lengths'),
  callers=[dict(site=0x803cc46,wrapper=0x803cc44,inbound=[0x8030cbc,0x8030e10],
   role='Selection-change callback / load transition candidate; NORMAL PROJECT/SESSION label UNRESOLVED'),
   dict(site=0x805bfd0,wrapper=0x805bfcc,init_RAM_pointer=0x20000a8c,
   raw_compressed_pointer_match=0x805c628,
   role='INIT-ONLY callback pointer value verified; runtime callback ancestry UNRESOLVED')],
  actual_asset_headers_present=False,stable_header_and_ordered_complete_transfers='Local algebra premises, not async closure'))
 emit('result.json',dict(status='PROJECT-DATA DEPENDENT; normal asset family NOT CLOSED',
  CPU_instructions_executed=0,actual_record_lengths=None,record_count=64,conditional_on_completion=True,
  maximum_length=MAX_L,maximum_advance=MAX_ADV,maximum_A64=A0+64*MAX_ADV,
  arithmetic32_wrap=False,metadata_total_limit_checked=False,first_two_excluded=True,
  later_all_pages_predicate_permitted=True,main_all_low_targets_excluded=True,
  actual_normal_intersections=None,unconditional_fresh_page=True,scalar_cache_suppression=False,
  X_Y_space='Page write retains X11; no new normal X selector proof',
  target_bridge_recomputed=False,parent_replay_admitted=False,
  independent=['other host cache/order/ancestry','P204B','other DSP indirect writers'],
  best_next_step='Trace26610 and20006914+8 backend selection/read validation for accepted normal aggregate lengths; resolve retainedX11 space before claiming actual X intersections'))
 initp=ROOT/'builds/phase19c-hostwrite/final-v3/arm-initialized-data.bin'
 init=initp.read_bytes();assert sha(init)=='2db584abde65123402067c89720f5a10e12c40650b700d6af2f13ed93743e04f'
 assert struct.unpack_from('<I',init,0xa7c)[0]==0x805b9ec
 assert struct.unpack_from('<I',init,0xa8c)[0]==0x805bfcd
 inputs[initp.relative_to(ROOT).as_posix()]=sha(init)
 inputs['tools/ct_asset_bounds.py']=sha(Path(__file__).read_bytes())
 inputs['tools/ct_asset_probe.py']=sha((ROOT/'tools/ct_asset_probe.py').read_bytes())
 emit('inputs.json',inputs);verify_inputs()
 emit('hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
 print('64 symbolic records; 128 interval rows; 2048 cell tests; no record values seeded')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path)
 p.add_argument('--probe-dir',required=True,type=Path);a=p.parse_args();collect(a.output_dir,a.probe_dir)
