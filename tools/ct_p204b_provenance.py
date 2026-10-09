"""Targeted offline P203A/204B producer ledger; never instantiates a CPU.

Reuses prior writer/host/cursor evidence, reviews only the consumer, initialized
entry, neighboring source table and shared1B90 caller paths. No asset analysis,
generic indirect-write recensus, positive count or destination fixture.
"""
import argparse,csv,io,json,re
from pathlib import Path
from ct_stock_load_audit import ROOT,sha,verify_inputs,rows

WATCH=[('high-X',0x5f00,0x6000)]
WATCH += [(f'selector-{i:X}',i,i+1) for i in range(0x95a,0x960)]
WATCH += [('dispatch-table',0x9db,0xa12)]
WATCH += [(f'descriptor-{i:X}',i,i+1) for i in range(0xeb,0x15b,8)]
WATCH += [('count-self',0x35f,0x360)]
# Source bounds recovered at the actual callers, not an alias census.
WRAPPERS=[(0x1a9f,0x2e1,1,6),(0x1aa7,0x2d5,4,3),(0x1aaf,0x2d6,4,3),
 (0x1ab7,0x2d8,1,1),(0x1abb,0x2dc,1,1),(0x1abf,0x2e0,1,1),
 (0x1ac3,0x2e9,1,1),(0x1ac7,0x2ee,1,1),(0x1acb,0x2f1,1,1)]

def smoothing_domains():
 """Finite recovered caller states; no DSP memory/destination records created."""
 out=[]
 for pc,base,stride,count in [(0x1a77,0x2fe,5,20),(0x1a90,0x470,5,20)]:
  out.append(dict(caller=hex(pc),helper='P1B89/P1B90',bank=None,base=base,stride=stride,count=count,
   count_source='X2FA=20 from ARM27AE4→286DA' if pc==0x1a77 else 'X46C=20 from bank1 ARM286DA',
   addresses=[base+stride*i for i in range(count)],
   premises='Recovered source count20 retained, linear M1, original caller entry/context'))
 for pc,base,stride,count in WRAPPERS:
  for bank in [0,1]:
   a=base+0x172*bank
   out.append(dict(caller=hex(pc),helper='P1B7B→1B89 first call then fallthrough',bank=bank,
    base=a,stride=stride,count=count,count_source='Immediate N0 at reviewed caller',
    addresses=[a+stride*i for i in range(count)],
    premises='Original direct caller/context, linear M1; N3/R2/R5 preserved by1B89'))
 return out

def collect(out):
 out=out.resolve();base=(ROOT/'builds/phase19c-p204b').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh P204B child required')
 payload,protected=verify_inputs();inputs={};arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
 def read(n):
  p=ROOT/n;v=p.read_bytes();inputs[n]=sha(v);return v
 def obj(n):return json.loads(read(n))
 def csvread(n):return list(csv.DictReader(io.StringIO(read(n).decode('utf8'))))
 listing='builds/phase3-selection0-channel0.asm';read(listing);dsp=rows(ROOT/listing,payload)
 def req(pc,t):assert dsp[pc]['text']==t,(hex(pc),dsp[pc]['text'],t)
 for pc,t in {
  0x2035:'asr a #$00035f,r0',0x203a:'move x:(r0)+,x1',0x203b:'move x:(r0)+,r5',
  0x203c:'move x:(r0)+,r6',0x203d:'move x:(r0)+,r7',0x203e:'move x:(r0)+,x0',
  0x203f:'move y:(r5+n5),y0',0x2040:'do x1,$204c',
  0x2043:'mpy +y1,y0,a x:(r0)+,r4',0x2045:'move a,x1 y:(r7),y0',
  0x2048:'move x:(r4),b a,y1',0x2049:'mac +x0,y1,b x:(r0)+,x0',
  0x204b:'move b,x:(r4)',0x2070:'rts',0x2788:'move x0,x:(r0)',
  0x28ac:'move #$00202b,r2',0x28bc:'move r2,x:(r1)+',
  0x19ac:'jsr (r1)',0x1fc:'jsr $198d',0x1a99:'move #$0003c4,r4',
  0x1b7c:'move r1,r2',0x1b7d:'move r4,r5',0x1b7e:'move #$000172,n2',
  0x1b82:'jsr $1b89',0x1b84:'move n3,n0',0x1b85:'move (r2)+n2,r2',
  0x1b87:'move r2,r1',0x1b89:'do n0,$1b91',0x1b8c:'tfr x0,a x:(r4)+,y0',
  0x1b90:'move a,x:(r1)+n1',0x1b91:'move (r4)-n4,r4',
  0x198:'move x:$0010,r0',0x19d:'move x0,x:(r0)+',0x1f97:'move b,x:(r7)+',
 }.items():req(pc,t)
 direct={int(m[1],16) for x in dsp.values()
  if (m:=re.fullmatch(r'jsr \$(1b89|1b7b)',x['text']))}
 assert direct=={0x1b89,0x1b7b}
 callers={pc:dsp[pc]['text'] for pc in dsp if dsp[pc]['text'] in ['jsr $1b89','jsr $1b7b']}
 assert set(callers)=={0x1a77,0x1a90,0x1b82}|{x[0] for x in WRAPPERS}
 # Confirm the wrapper's first caller and all inherited immediate R1/N0/N1 values.
 for pc,b,s,n in WRAPPERS:
  req(pc,'jsr $1b7b')
  for reg,want in [('r1',b),('n1',s),('n0',n)]:
   for p in sorted((p for p in dsp if 0x1a99<=p<pc),reverse=True):
    m=re.search(r'move #\$([0-9a-f]+),'+reg+r'$',dsp[p]['text'])
    if m:assert int(m[1],16)==want,(hex(pc),reg);break
   else:raise AssertionError((hex(pc),reg))
 # Existing operand census is evidence input; no new generic write census is made.
 old=obj('builds/phase14/current/DSP-X-L-write-census.json')
 assert old['absolute_X35F_writers']==[]
 abs_records=[x for x in old['entries'] if not x['indirect'] and
  0x360<=int(x['operand'].lstrip('$'),16)<0x3c4]
 assert not abs_records
 selected=[x for x in old['entries'] if int(x['PC'],16) in [0x19d,0x1b90,0x1f97,0x204b,0x2788]]
 for x in selected:assert dsp[int(x['PC'],16)]['text']==x['instruction']
 for n in ['builds/phase14/current/ARM-alias-ledger.json',
  'builds/phase14/current/asynchronous-paths.json','builds/phase14/current/worker-write-census.json',
  'builds/phase19c-hostwrite/final-v3/cache-semantics.json',
  'builds/phase19c-hostwrite/final-v3/DSP-cursor-lifecycle.json',
  'builds/phase15/verified/X-reach.json','builds/phase15/verified/async-ledger.json']:
  obj(n)
 params=csvread('builds/phase19c-hostwrite/final-v3/scalar-endpoints.csv')
 hits=[]
 for x in params:
  if x.get('space')!='X':continue
  try:a=int(x['address'])
  except (ValueError,KeyError):continue
  if 0x35f<=a<0x3c4:hits.append(x)
 assert len(hits)==1 and int(hits[0]['address'])==0x35f
 # Already decoded ARM witnesses only; no dependency or firmware execution.
 arm_lines=[];ar={}
 for n in ['builds/phase9/helper-closure/080286AA-0802872C.asm',
           'builds/phase9/entry/080273E4-08027D1A.asm',
           'builds/phase14/current/arm-witnesses.asm']:
  for line in read(n).decode().splitlines():
   m=re.match(r'([0-9A-Fa-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
   if not m:continue
   pc=int(m[1],16);raw=bytes.fromhex(m[2]);assert arm[pc-0x8010000:pc-0x8010000+len(raw)]==raw
   ar[pc]=m[3]
   if 0x8027a10<=pc<0x8027af8 or 0x80286bc<=pc<0x8028726 or 0x80269e4<=pc<0x8026abc:
    arm_lines.append(line)
 for pc,t in [(0x80286e0,'r1, #0'),(0x80286e4,'#0x80292f8'),
  (0x80286da,'#0x80292f8'),(0x8027ae2,'r0, #0x14')]:assert t in ar[pc],(hex(pc),ar[pc])
 # Targeted reuse of existing scalar-read edge/window evidence. No new caller
 # scan: constants can exclude the r35D precursor; inherited arguments cannot.
 reader_calls=obj('builds/phase19c-hostwrite/probe-final/targeted-calls.json')
 reader_calls=[x for x in reader_calls if x['target']==0x8029344]
 assert len(reader_calls)==19
 read_windows={}
 for n in ['builds/phase19c-hostwrite/probe-final/arm-windows.asm',
           'builds/phase3-arm-transport.asm','builds/phase9/boundary/08028132-080283D8.asm']:
  for line in read(n).decode().splitlines():
   m=re.match(r'([0-9A-Fa-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
   if not m:continue
   pc=int(m[1],16);raw=bytes.fromhex(m[2]);assert arm[pc-0x8010000:pc-0x8010000+len(raw)]==raw
   read_windows[pc]=line
 constants={0x8021810:0x35,0x80283ac:0x802f,0x802907a:0x8003,
  0x80290ec:9,0x80290f6:0x8008,0x8029126:9}
 reader_rows=[]
 for x in reader_calls:
  pc=x['PC'];raw=bytes.fromhex(x['raw']);assert arm[pc-0x8010000:pc-0x8010000+len(raw)]==raw
  value=constants.get(pc)
  if value is not None:
   prior='\n'.join(read_windows[p] for p in sorted(read_windows) if pc-0x90<=p<pc)
   # Confirm each fixed argument's recovered source without inventing reachability.
   assert re.search(r'#(?:'+hex(value)+'|'+str(value)+r')\b',prior),(hex(pc),value)
  reader_rows.append(dict(site=hex(pc),target='08029344',encoded_read=value,
   count_preimage='EXCLUDED: fixed argument notX35D' if value is not None else
    'SERVICE-ONLY accepted private35D possible' if pc==0x8026ad4 else
    'FROZEN prior asset evidence; not analyzed' if pc==0x8049ba8 else
    'UNRESOLVED inherited/variable argument and normal ordering',
   normal_positive_witness=False,scope='Existing halfword-edge candidates, not complete normal graph'))
 for pc,v in constants.items():assert v!=0x35d
 prior=obj('builds/phase19c-checkpoint/final/result.json')
 zero=obj('builds/phase19c-checkpoint/final/x35f-entries.json')
 assert len(zero)==2 and all(x['PC']==0x203a and x['value']==0 for x in zero)
 for n in ['builds/phase19c-checkpoint/final/hashes.json',
  'builds/phase19c-fullhelper/final/source-manifest.json',
  'builds/phase19c-packlink/final-v2/hashes.json']:
  obj(n) # Frozen provenance identity only; no asset decoding/recomputation.
 domains=smoothing_domains()
 assert all(not (0x35f<=a<0x3c4) for d in domains for a in d['addresses'])
 out.mkdir(parents=True)
 def emit(n,v):
  with (out/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 def csvout(n,rs):
  keys=list(dict.fromkeys(k for r in rs for k in r))
  with (out/n).open('x',encoding='utf8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rs)
 def txt(n,s):
  with (out/n).open('x',encoding='utf8',newline='\n') as f:f.write(s)
 windows=[(0x12d,0x140),(0x156,0x215),(0x198d,0x19bf),(0x1a60,0x1ad0),
  (0x1b7b,0x1b93),(0x202b,0x2071),(0x2779,0x278a),(0x28ac,0x28d3)]
 txt('dsp-witnesses.asm','\n'.join(dsp[p]['line'] for p in sorted(dsp) if any(a<=p<b for a,b in windows))+'\n')
 txt('arm-witnesses.asm','\n'.join(sorted(set(arm_lines)))+'\n')
 csvout('scalar-read-count-preimages.csv',reader_rows)
 txt('scalar-read-witnesses.asm','\n'.join(read_windows[p] for p in sorted(read_windows)
  if any(x['PC']-0x90<=p<=x['PC'] for x in reader_calls if x['PC']!=0x8049ba8))+'\n')
 # Local pinned primary manual; only selected pages, no web/source refetch.
 from pypdf import PdfReader
 manual='builds/phase19b/documentation/DSP56300FM.pdf';read(manual);pdf=PdfReader(ROOT/manual)
 pages=[100,295,296,297]
 txt('DO-LC-manual.txt','\n'.join(f'PDF page{i+1}\n'+pdf.pages[i].extract_text() for i in pages))
 emit('manual-provenance.json',dict(path=manual,SHA256=inputs[manual],pages_one_based=[i+1 for i in pages],
  sections=['5.4.4.3 / printed5-21','DO / printed13-56..58'],offline_existing_copy=True))
 fields=[]
 for f,reg,reader,desc in [
  (0,'R5',['203B','2044'],'Y source pointer: indexed read Y:(R5+N5) at203F/204A'),
  (1,'R6',['203C','2046'],'Y source pointer: indexed read Y:(R6+N6) at2042'),
  (2,'R7',['203D','2047'],'Y factor pointer: unindexed read Y:(R7) at2045'),
  (3,'X0',['203E','2049'],'MAC coefficient: current X0*Y1 added to B at2049'),
  (4,'R4',['2043'],'X destination: read at2048 then one unindexed store at204B')]:
  fields.append(dict(offset=f,address=f'X[360+5*k+{f}]',register=reg,readers=reader,
   use=desc,meaning_status='VERIFIED instruction behavior; musical semantics UNRESOLVED',
   initialization=dict(writer='P2788',value=0,
    scope='INIT-ONLY immediately-after-clear for words insideX[0,6000), including prospectivek0..19',
    address_condition='0<=360+5*k+offset<6000 with linear nonwrapped walk; larger normalk UNKNOWN'),
   writers=['INIT P2788','SERVICE private5E→P19D writes zero',
    'Normal SHI effective endpoint/foreign computed aliases UNRESOLVED'],
   normal_structured_producer='NOT RECOVERED',all_writer_reader_closure=False))
 emit('record-schema.json',dict(status='VERIFIED consumer schema under linear M0; not a populated normal table',
  base=0x360,stride=5,fields=fields,count_word=0x35f,count_loaded_PC=0x203a,
  count_latched_PC=0x2040,loop_last=0x204b,continuation=0x204c,
  architectural_LC_bits=24,normal_positive_min=None,normal_positive_max=None,
  hypothetical_capacity=20,capacity_status='HYPOTHESIS from adjacent3C4 source, no enforced limit',
  final_extra_prefetch='Four words at360+5*N through363+5*N, even after last active record',
  write_set='set of d_k, k in0..N-1; d_k=X[364+5*k] under linear table walk',
  unindexed_store=True,destination_modifier_relevant=False))
 count=[
  dict(writer='P2788',mode='INIT',caller='25DE→2779',value='0',address_domain='X[0,6000)',
   can_write_35F='VERIFIED YES',normal_positive='NO',scope='INIT-ONLY / after completed clear'),
  dict(writer='ARM080286E4→292F8→P19D',mode='NORMAL PARAMETER',caller='27AE4→2872C or2139A→286F6→286BC',
   value='r1=0 at286E0; serialized upper24=0',address_domain='35F+172*bank; bank0/1',
   can_write_35F='VERIFIED YES nominal bank0',normal_positive='NO on recovered coherent path',
   scope='NORMAL-PATH; actual cache/space ordering retained as independent premise'),
  dict(writer='ARM269E4→26A9A→292F8→P19D',mode='SERVICE',caller='request5E dispatcher',
   value='private byte>>8 =0',address_domain='Accepted private35F start',can_write_35F='VERIFIED YES capability',
   normal_positive='NOT NORMAL; direct nonzero value NO',scope='SERVICE-ONLY; no request executed'),
  dict(writer='P19D',mode='UNRESOLVED',caller='SHI receive156→198/199',value='received X0',
   address_domain='saved X10 with X11.bit15 clear, M0FFFF forced15C',can_write_35F='NOT-YET-DETERMINED normal',
   normal_positive='NOT-YET-DETERMINED',scope='Transport has normal/service users; no attained positive endpoint/state'),
  dict(writer='P1B90',mode='NORMAL PARAMETER',caller='All recovered1B89/1B7B caller paths',
   value='A=X[R1]+MAC interpolation terms',address_domain='Finite caller-specific sets in smoothing-domains.json',
   can_write_35F='VERIFIED NO under recovered count/modifier premises',normal_positive='NO in bounded class',
   scope='BOUNDED-PROOF; unknown computed entries/foreign source counts not excluded'),
  dict(writer='P1F97',mode='UNRESOLVED',caller='Effect parent1E15/helpers; normal parent entry unresolved',
   value='Accumulation B',address_domain='Preserved initialized cursors:2CCC..2D0B /2C02..2C21 /2C24..2C43',
   can_write_35F='VERIFIED NO checkpoint domain; NOT-YET-DETERMINED globally',normal_positive='NOT RECOVERED',
   scope='Prior BOUNDED-PROOF reused; no new cursor replay'),
  dict(writer='P204B',mode='NORMAL AUDIO',caller='descriptor14B→202B→203A→DO',value='B from read/MAC',
   address_domain='One address per destination field; normal positive record values UNKNOWN',
   can_write_35F='NOT-YET-DETERMINED; cannot first violate preserved zero in zero-skip mode',
   normal_positive='Positive invocation NOT RECOVERED',scope='Consumer self-alias obligation, not recovered positive producer'),
  dict(writer='Mailbox1C53/1D41, worker/other foreign context',mode='UNRESOLVED',caller='Inherited scoped ledgers',
   value='No count-specific positive publisher recovered',address_domain='Reviewed finite jobs exclude; residual state domains unclosed',
   can_write_35F='NOT-YET-DETERMINED globally',normal_positive='NOT RECOVERED',
   scope='Independent retained obligation; no generic recensus')]
 csvout('count-writers.csv',count)
 record=[dict(writer='P2788',mode='INIT',role='Zero clear',domain='X[0,6000)',
   record_relation='Includes all five fields in prospective20-position window',value_formula='0',
   produced_active_records=False,closure='INIT-ONLY; no count publication >0'),
  dict(writer='ARM27A5E/72/80/B8',mode='NORMAL PARAMETER',role='Neighbor source table fields0/1/2/4',
   domain='2FB+172*b+5*i+{0,1,2,4}; b0/1 i0..19',record_relation='Disjoint from compiled360..3C3',
   value_formula='Lookup/constant/source-pointer upper24; not compiled fields',produced_active_records=False,
   closure='VERIFIED finite nominal addresses, coherent transport premise'),
  dict(writer='P1B90',mode='NORMAL PARAMETER',role='Caller-specific interpolation X stores',
   domain='smoothing-domains.json',record_relation='Every recovered direct caller set excludes35F..3C3',
   value_formula='A after MAC',produced_active_records=False,closure='BOUNDED-PROOF under stated caller/modifier/count premises'),
  dict(writer='SERVICE5E→P19D',mode='SERVICE',role='Accepted private-word zero writes',
   domain='Selected count/record word',record_relation='Can clear, not direct nonzero compiled record builder',
   value_formula='LDRB>>8=0',produced_active_records=False,closure='SERVICE-ONLY, not normal evidence'),
  dict(writer='P19D',mode='UNRESOLVED',role='Shared normal/service transport sink',
   domain='Effective saved X10 cursor/space',record_relation='Compiled-word alias exclusion not closed',
   value_formula='Received X0',produced_active_records='UNRESOLVED',closure='No recovered count/table publication chain'),
  dict(writer='P1F97/P204B/remaining reused indirect context',mode='UNRESOLVED',role='Possible foreign address alias',
   domain='Existing conditional cursor/destination domains; global retention unresolved',
   record_relation='No attained normal record constructor',value_formula='Per-site arithmetic',
   produced_active_records='UNRESOLVED',closure='No broad alias recensus')]
 csvout('record-writers.csv',record)
 emit('smoothing-domains.json',domains)
 emit('source-table-separation.json',dict(ARM_table_base='2FB+172*b',words_per_source_record=5,
  count=20,count_source='27AE2→2872C→286DA at2FA+172*b',compiled_count='286E4 writes0 at35F+172*b',
  source_addresses=[[0x2fb+0x172*b+5*i+f for i in range(20) for f in [0,1,2,4]] for b in [0,1]],
  last_bank0_source_word=0x35e,compiled_start=0x360,compiled_word_overlap=False,
  threeC4='1A99 R4 feeds X-source read1B8C; R1 is output, not R4',
  compiled_fill_then_count='NOT ESTABLISHED',positive_count20_is_compiled=False))
 emit('count-latching.json',dict(status='VERIFIED ISA/instruction data flow',
  load='203A X35F→X1 before field/prefetch loads',latch='2040 DO X1→24-bit LC',
  X1_overwrite='2045 A→X1 for multiplication, after DO latch',
  later_X35F_write_effect='Does not reload current LC; changes later invocation count only unless another agent directly corrupts loop/control state',
  later_record_write_effect='Fields/destinations fetched during loop; no whole-table snapshot',
  current_count_self_store='d_k=35F would store new B for later invocations, but cannot first produce nonzero from zero-skip entry',
  critical_section='No IRQ mask, lock, barrier or positive count/table commit in202B..2070',
  SHI_audio_IRQ='Reviewed156..1B3 and1B4..1D8 do not directly assign X1 or LC; SHI may mutate memory through19D',
  all_async_exclusion=False,zero_SKIP='SR compatibility bit13 clear; zero then skips, legacy set executes65536',
  positive_architectural_domain=[1,0xffffff],normal_positive_domain=None))
 destinations=[dict(state='Immediately after P2788 clear',classification='INIT-ONLY',k='prospective0..19 only',
  destination_field='364+5*k',value_domain='0',normal_consumed_set='[] because count0 under zero-skip',
  bounds_proved_normal=False),dict(state='Existing zero-count checkpoint',classification='BOUNDED-PROOF',k='empty',
  destination_field='Not fetched for current record',value_domain='Not consumed',normal_consumed_set='[]',bounds_proved_normal=False),
  dict(state='All normal runtime',classification='UNRESOLVED',k='normalN/k domain UNKNOWN',
  destination_field='X[364+5*k] if linear walk preserved',value_domain='UNKNOWN; no attained positive normal record',
  normal_consumed_set='UNKNOWN, not fabricated interval',bounds_proved_normal=False)]
 csvout('destination-domains.csv',destinations)
 collisions=[]
 for n,lo,hi in WATCH:
  for state,result,scope in [('Existing zero-count checkpoint','VERIFIED NO','BOUNDED-PROOF; count0/zero-skip class only'),
   ('All normal Selection0','NOT-YET-DETERMINED','No defensible positive publisher or destination domain; not universal zero proof')]:
   collisions.append(dict(target=n,start=hex(lo),end_exclusive=hex(hi),state=state,result=result,
    exact_reachable_addresses='[]' if result=='VERIFIED NO' else 'UNKNOWN',scope=scope))
 csvout('collision-results.csv',collisions)
 emit('zero-path-preserved.json',dict(source='builds/phase19c-checkpoint/final/x35f-entries.json',entries=zero,
  original_report=prior,scope='Prior admitted checkpoint/calibration results unchanged; not rerun here',
  single_store_calibration_is_normal_positive_evidence=False,new_CPU_instructions=0))
 emit('entry-and-ordering.json',dict(function_start=0x202b,function_end_inclusive=0x2070,
  route='Audio block1D9..:1FC→198D;14 descriptors fromEB..153;19A5/19AC→X14B=202B→203A',
  mode='NORMAL AUDIO structural path with initialized descriptor/context retained',
  descriptor_init='28AC/28BC after twelve voice entries publishes202B at14B',
  normal_positive_entry='UNRESOLVED; no positive state proved',
  alternate_direct_edges='Prior entry census has no direct202B/203A edge; arbitrary computed interior entry not excluded',
  ARM_order='27A10 fills separate source fields/tails, then286DA publishes source count20, then286E4 compiled count0',
  compiled_record_count_coupling='UNRESOLVED; no compiled producer/order/commit recovered',
  boot_order='Increasing X clear reaches count35F before record360; after complete clear bothzero',
  runtime_snapshot_atomic=False))
 emit('scoped-alias-evidence.json',dict(selected_inherited_sites=selected,
  inherited_absolute_count_writers=[],inherited_absolute_record_writers=abs_records,
  nominal_scalar_count_hit=hits,nominal_scalar_record_hits=[],
  all_recovered_writers_are_complete=False,generic_recensus_performed=False,
  unknown_groups=['Host/cache/space/cursor ordering','Foreign Y cursor/AGU preservation',
   'Other inherited state-dependent aliases and actual entry ancestry','Worker physical/shared queue mapping'],
  assets='FROZEN PACKLINK results retained; no asset analysis performed'))
 emit('count-alias-preconditions.json',dict(status='VERIFIED necessary local address equations, not attained normal states',
  host19D=dict(count_alias='At198 savedX10 must equal35F andX11.bit15 must be0; receivedX0 must be nonzero to publish a positive raw LC value',
   cached_write='ARM requested encoded address equals cached20003D00 halfword; no fresh header, data follows effective saved DSP cursor/space',
   scalar_read_preimage='If sole intervening cursor operation is29344 private scalar read at r, cursor becomesr+2; count35F needs r=35D',
   destination_field_read_preimage='To alias record word364+5*k by that same r+2 rule, r=362+5*k; actual normal k/reader/ordering UNKNOWN',
   guarded_paths='286E4 and valid private5E byte writes carry0 even if redirected; neither can be the direct first positive store',
   normal_read35D_or_coupled_cached_sequence='NOT RECOVERED; no hypothetical sequence promoted to a normal witness'),
  cursor1F97=dict(count_alias='For retained linear32-store run from c: c<=35F<c+32, equivalently340<=c<360',
   record_field_alias='For field364+5*k: 364+5*k-31<=c<=364+5*k; normalk/c domainsUNKNOWN',
   known_initialized_cursors='All bounded initialized intervals exclude count/record window; foreign preservation/normal parent unresolved'),
  self204B=dict(count_alias='Consumed destination field must equal35F and body already active',
   first_positive='Impossible from count0/zero-skip entry without prior foreign count/control mutation',
   current_invocation='LC latched2040; count-cell changes alone affect later invocations'),
  smoothing1B90='All20 recovered caller/bank domains exclude count/prospective record window; larger foreign counts/other computed entries not licensed'))
 emit('result.json',dict(result_class='D',positive_normal_reachability='UNRESOLVED',
  normal_always_zero='NOT-YET-DETERMINED',recovered_normal_positive_publisher=False,
  normal_positive_count_domain=None,normal_destination_set=None,
  high_X='NOT-YET-DETERMINED',target_bridge_cells='NOT-YET-DETERMINED',count_self_alias='NOT-YET-DETERMINED',
  P204B_removed_as_blocker=False,parent_replay_admitted=False,target_bridge_recomputed=False,
  persistent_256_word_reservation=False,positive_checkpoint_admitted=False,
  CPU_instructions_executed=0,offline=True,asset_branch_reopened=False,
  remaining=['Effective host endpoint/cache/space/order tocount/table','Foreign cursor/modifier/entry preservation',
   'Independent other indirect writers/worker shared mapping'],
  best_next_step='Targeted P19D host cursor/cache provenance to35F and record words; recover an actual coherent normal positive publisher or exclusion before any replay',
  static_scope='Consumer schema,24-bit count latch,complete recovered1B90 direct callers; no universal alias/normal-state closure'))
 read('tools/ct_p204b_provenance.py');emit('inputs.json',inputs);verify_inputs()
 emit('hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
 print('Result D;20 bounded smoothing caller/bank domains; normal positive checkpoint absent; CPU0')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path)
 collect(p.parse_args().output_dir)
