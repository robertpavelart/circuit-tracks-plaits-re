"""Offline P657 record/provenance qualification. Never instantiates a DSP CPU.

Only original cached data and byte-checked decoded instructions are used.
Concrete preset bytes do not supply corrected controls or retained histories.
Fresh output directory required; all numerical replay gates fail closed.
"""
import argparse,csv,hashlib,json,re,struct,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from ct_resource_audit import read_rows
from ct_phase4_trace import arm_evidence
from ct_stock_load_audit import verify_inputs
BASE=ROOT/'builds/phase20b-inputrec'
PREV=ROOT/'builds/phase20b-checkpoint/final'
ARCHIVE=ROOT/'builds/phase19c-assetdata/discovery/archives/fae30b90741bfaebfdd94b98e0f8d18fd7be9b1266e3f74291ea9fef02285fa5.zip'
DSP=ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin'
ARM=ROOT/'firmware/circuittracks-firmware-4486.bin'
BUNDLE=ROOT/'builds/phase19c-packlink/app-1.72.1/code/ember-dist/assets/main-DHaPxgL3.js'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p):return json.loads(p.read_text(encoding='utf8'))
def dump(out,name,data):
 with (out/name).open('x',encoding='utf8',newline='\n') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
def table(out,name,rows):
 with (out/name).open('x',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def stream_accesses(n):
 if not 1<=n<=20:raise ValueError('Only positive original constructor counts 1..20 qualified structurally')
 h=0x2fa;r=h+5
 accesses=[dict(P='67F',address=h,role='count')]
 for pc in [0x680,0x681,0x682,0x683]:accesses.append(dict(P=f'{pc:X}',address=h+pc-0x67f,role='first-row preload'))
 for i in range(n):
  for pc,role in [(0x688,'current destination'),(0x689,'NEXT source1'),(0x68b,'NEXT source2'),(0x68c,'NEXT factor'),(0x68e,'NEXT amount')]:
   accesses.append(dict(P=f'{pc:X}',iteration=i,address=r,role=role));r+=1
 return accesses
def bank_reads():
 r=0x2d5;rows=[]
 def add(pc,lane=-1):
  nonlocal r
  rows.append(dict(P=f'{pc:X}',iteration=lane,address=r));r+=1
 for i in range(3):
  for pc in [0x69a,0x69f,0x6a1,0x6ae]:add(pc,i)
 for pc in [0x6b6,0x6bb,0x6c0,0x6c5,0x6ca,0x6cf,0x6d4,0x6d8,0x6df,0x6e2,0x6e4,0x6ee,0x6f4,0x6fa,0x6fb,0x6fd,0x706]:add(pc)
 for i in range(3):
  for pc in [0x711,0x712]:add(pc,i)
 for i in range(2):add(0x745,i)
 assert r==0x2fa and len(rows)==37
 return rows
BLOCKERS=['no provenance-qualified exact-patch note/slot invocation or last-writer timeline',
 'runtime correction halfwords for control/depth IDs, smoothed X2E9 and X2FE+5*i, Y17C and Y126/Y131/Y135 unknown',
 'retained Y5AB..5AE and Y5B7/5B8 have no qualified last numerical writer',
 'material SR SM/SA/DM/S0/S1 and OMR memory mapping not closed',
 'material modifier retention, sentinel retention, hardware stack/loop prefix not closed',
 'natural generator/worker inputs and X2C66 guard not qualified']
def gate(categories):
 if any(not c['qualified'] for c in categories):return dict(result='REFUSED',admitted=False,CPU_instructions=0)
 raise ValueError('No numerical replay executor is supplied by this static provenance tool')
def recover(out):
 out=out.resolve()
 if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('Fresh inputrec report child required')
 verify_inputs();arm=ARM.read_bytes();raw=lambda a,n:arm[a-0x8010000:a-0x8010000+n]
 u=lambda a:struct.unpack('<I',raw(a,4))[0]
 original=read_rows(ROOT/'builds/phase3-selection0-channel0.asm',DSP.read_bytes())
 out.mkdir(parents=True);(out/'evidence').mkdir()
 # Independently invoke the existing real DSP56300 decoder on focused original ranges.
 spans=[(0x281,0x387),(0x657,0x759),(0xacc,0xb26),(0xbdd,0xcb8),(0x1a60,0x1acd),(0x1b7b,0x1b93)]
 fresh=[]
 for start,end in spans:
  dest=out/f'evidence/p{start:04x}-{end:04x}.asm'
  subprocess.run([sys.executable,'-B',str(ROOT/'tools/ct_dsp_disasm.py'),str(DSP),'--start',hex(start),'--end',hex(end),'--output',str(dest)],check=True,capture_output=True)
  decoded=read_rows(dest,DSP.read_bytes())
  for pc,v in decoded.items():assert original[pc]['text']==v['text']
  fresh.extend(dict(P=f'0x{pc:X}',**v) for pc,v in decoded.items() if 0x657<=pc<0x759)
 table(out,'p657-instructions.csv',fresh)
 checked=[]
 sources=[ROOT/'builds/phase9/entry/080273E4-08027D1A.asm',ROOT/'builds/phase9/boundary/08028132-080283D8.asm',
  ROOT/'builds/phase9/boundary/0802872C-080287B0.asm',ROOT/'builds/phase9/helper-closure/0802853C-080286AA.asm',
  ROOT/'builds/phase9/helper-closure/080286AA-0802872C.asm',ROOT/'builds/phase9/helper-closure/0803B8AC-0803B9A8.asm',
  ROOT/'builds/phase9/parameter-helpers/0803BD00-0803BD58.asm',ROOT/'builds/phase9/correction/080360B2-08036198.asm']
 for p in sources:checked.append(dict(path=p.relative_to(ROOT).as_posix(),instructions=arm_evidence(p,arm),sha256=sha(p)))
 q=(PREV/'immutable/selected-offline-patch.binary').read_bytes()
 assert len(q)==340 and q[:16].decode('ascii').rstrip()=='Rudi saw poly'
 assert sha(ARCHIVE)==ARCHIVE.stem
 with zipfile.ZipFile(ARCHIVE) as z:
  assert z.read('patches/patch_0.syx')[9:-1]==q
  projects=[]
  for name in z.namelist():
   if name.endswith('.ncs'):
    p=z.read(name);at=p.find(q[:16]);candidate=p[at:at+340] if at>=0 else None
    projects.append(dict(member=name,size=len(p),sha256=hashlib.sha256(p).hexdigest(),exact340_offset=p.find(q),
     name_offset=at,candidate_differences=[dict(offset=i,selected=a,project=b) for i,(a,b) in enumerate(zip(q,candidate or b'')) if a!=b],
     event_binding='UNRESOLVED; name/sequence storage does not establish exact-patch runtime slot/history'))
 js=BUNDLE.read_text(encoding='utf8');witnesses=[]
 for term in ['filter:bY.byteOffset(60).byteLength(9)','depth:wY.byteOffset(2).signed()','source1:wY.byteOffset(0)','new Uint8Array(n,158996,680)','macroSlots:bY.byteOffset(204).byteLength(17)']:
  at=js.index(term);witnesses.append(dict(character_offset=at,needle=term,excerpt=js[max(0,at-100):at+len(term)+200]))
 dump(out,'components-witnesses.json',dict(path=BUNDLE.relative_to(ROOT).as_posix(),sha256=sha(BUNDLE),executed=False,witnesses=witnesses))
 ids=obj(PREV/'reverse-index-provenance.json')['IDs'];reverse={v:i for i,v in enumerate(ids)}
 # Original table/literal decoding: ADR28550->2900C; LDR2856E/285DC->28FF4->805B5E0.
 assert u(0x8028ff4)==0x805b5e0
 source=lambda i:struct.unpack('<H',raw(0x802900c+2*i,2))[0]
 descriptors=[]
 for i in list(range(30,39))+list(range(94,174)):
  d=raw(0x805454c+8*i,8);offset=int.from_bytes(d[:2],'little')
  descriptors.append(dict(ID=i,offset=offset,raw_value=q[offset],descriptor_bytes=d.hex(),reverse_index=reverse.get(i,255),
   corrected_value=q[offset] if reverse.get(i,255)==255 else None,
   reason='360BE FF bypass' if reverse.get(i,255)==255 else 'runtime correction halfword at20005C28+2*index unknown'))
 dump(out,'patch-field-values.json',dict(source='selected immutable340 bytes; original getter3BD00 / correction360B2',fields=descriptors,
  filter_bytes=list(q[60:69]),note='raw file and uncorrected getter values are not active corrected DSP words'))
 control=[]
 for param,dest,writer,formula in [(31,'2E7','2794A','(corrected(ID31)<<24)>>8'),
  (36,'2E8','27964','(corrected(ID36)*u32(0803B9B8)) mod2^32 >>8'),
  (34,'3E7->2E9','2797E','282E4: mla AAAAAB*v+B7FFFFEC, then adds runtime halfword to upper16; DSP1AC1/1AC3->1B89 smoothing'),
  (38,'2EA','27998','28314: signed8(v-64); byte lookup805A340[abs]; positive*AAAAAB or negative*FF555555; upper24 transport'),
  (35,'2EB','279B2','corrected(ID35)*u32(0803B9B8); upper24 transport')]:
  d=next(v for v in descriptors if v['ID']==param)
  control.append(dict(destination='X:'+dest,patch_ID=param,offset=d['offset'],raw_value=d['raw_value'],
   reverse_index=d['reverse_index'],corrected_value='',ARM_sink=writer,conversion=formula,final_DSP_word='',
   status='VERIFIED byte/getter/operand chain; UNRESOLVED correction and retained smoother where applicable'))
 assert u(0x803b9b8)==0x01020408 and u(0x8028b68)==0xaaaaab and u(0x8028b74)==0xb7ffffec and u(0x8028b7c)==0xff555555
 table(out,'control-conversions.csv',control)
 mods=[]
 for i in range(20):
  s1,s2,amount,dest=q[124+4*i:128+4*i]
  a=0x2fb+5*i;entry=raw(0x805b5e0+2*dest,2)
  assert reverse.get(94+4*i,255)==255 and reverse.get(95+4*i,255)==255 and reverse.get(97+4*i,255)==255
  mods.append(dict(slot=i,record_header=f'X:{a:X}',source1_ID=94+4*i,source2_ID=95+4*i,depth_ID=96+4*i,destination_ID=97+4*i,
   raw_source1=s1,raw_source2=s2,raw_depth=amount,nominal_depth=amount-64,raw_destination=dest,
   source1_Y=f'{source(s1):X}',source2_Y=f'{source(s2):X}',factor_Y='10',destination_Y=f'{0x7c+entry[0]:X}',destination_conversion_type=entry[1],
   amount_X=f'{a+3:X}',amount_target_X=f'{0x3d0+i:X}',amount_DSP_value='',
   amount_producer='ARM285B8->target; DSP1A70..1A77->1B89 smoothing',
   status='VERIFIED pointers / CALCULATED nominal source bytes / UNRESOLVED corrected amount and retained smoother'))
 assert {v['destination_Y'] for v in mods}=={'7C','91'} and [v['slot'] for v in mods if v['destination_Y']=='91']==[0,2]
 table(out,'modulation-provenance.csv',mods)
 reads=bank_reads();formulas=list(csv.DictReader((ROOT/'builds/phase9/ranges-final/constructor-formulas.csv').open()))
 fields=[]
 for row in reads:
  a=row['address'];writers=[v for v in formulas if v['space']=='X' and int(v['encoded_base'],0)==a]
  smoothing={**{0x2d5+4*i:0x3ca+i for i in range(3)},**{0x2d6+4*i:0x3cd+i for i in range(3)},
   **{0x2d8+4*i:0x3e4+i for i in range(3)},**{0x2e1+i:0x3c4+i for i in range(6)},0x2e9:0x3e7,0x2ee:0x3e8,0x2f1:0x3e9}
  producer=';'.join(v['root']+'@'+v['site']+'->'+v['helper'] for v in writers)
  if a in smoothing:producer=f'DSP1A99..1ACB->1B7B/1B89 smoothing fromX:{smoothing[a]:X}; ARM target writer in constructor-formulas'
  fields.append(dict(field=f'X:{a:X}',consumer_P=row['P'],iteration=row['iteration'],
   category='NOTE-DERIVED' if a in [0x2f8,0x2f9] else 'PATCH-DERIVED',
   producer=producer or 'UNRESOLVED underlying producer; delegated helper/parameter field not numerically qualified',
   value='',lifetime='bank-shared runtime; note and parameter callbacks may change before block',
   status='VERIFIED consumed address under original bank0/linear AGU premise; numerical value UNRESOLVED'))
 extra=[('Y:0','GLOBAL','2A9','2D5'),('Y:1','VOICE-STATE','2AA','131'),('Y:2','GLOBAL','2AB/2AD;ARM2743C X298','A0'),('Y:3','GLOBAL','294/298','7C'),
  ('X:29','VOICE-STATE','2A0','57B'),('X:2B','VOICE-STATE','299 N7=44;2A1/2A2','5BF'),('X:40','GLOBAL','initialized block/rate scaling; retention unresolved',''),
  ('Y:10/12/13/14/15','CONSTANT','startup constant construction; retention conditional',''),('Y:A0..A3/A6','MODULATION-STATE','shared bank modulators;669/6A1/6A4/6A5',''),
  ('Y:131/135','VOICE-STATE','4D5 envelope/note preparation;6A7/6E2/6E4/6F8/6FD',''),('Y:148..14C','VOICE-STATE','ARM per-slot parameter preparation;6A0/743',''),
  ('Y:17C','MODULATION-STATE','66F read;674 smoothed update fromX5C3',''),('Y:126','VOICE-STATE','source7; per-voice state',''),
  ('X:5C3','VOICE-STATE','ARM21A5E zero on some start path;671',''),('X:98E+N2','CONSTANT','frequency-related table711..73E; incomingM2 still material','')]
 for field,category,producer,value in extra:
  fields.append(dict(field=field,consumer_P='657..758',iteration=-1,category=category,producer=producer,value=value,
   lifetime='runtime/preserved; stated concrete addresses CONDITIONAL on bound bank0/slot0 and original pointer transfer',status='PARTIAL source; entry numerical qualification incomplete'))
 # Every stream read, including the four LAST lookahead words; values retained unknown.
 for a in stream_accesses(20):
  fields.append(dict(field=f"X:{a['address']:X}",consumer_P=a['P'],iteration=a.get('iteration',-1),
   category='GLOBAL' if a['address']==0x2fa else ('UNKNOWN' if a['address']>=0x35f else 'MODULATION-STATE'),
   producer='286BC count=20 (deferred shrink possible)' if a['address']==0x2fa else ('ARM27A10 row or retained lookahead; see modulation-provenance'),
   value='20' if a['address']==0x2fa else '',lifetime='constructor/current runtime retention not a recorded invocation',status='VERIFIED access formula; active value CONDITIONAL/UNRESOLVED'))
 table(out,'p657-field-provenance.csv',fields)
 dump(out,'p657-input-record.json',dict(status='PARTIAL',function=dict(entry='657',return_P='758',callers=['33F trigger','37C normal preparation']),
  scope='bank0 slot0 original record formulas; no concrete invocation',control_base='X:2D5',control_words=37,control_end_exclusive='X:2FA',
  header='X:2FA',header_words=1,row_base='X:2FB',row_stride=5,
  row_fields=['source1 Y base + N5','source2 Y base + N6','absolute Y factor pointer','smoothed amount','absolute Y accumulation destination'],
  constructor_count=20,count_producer='27AE2/27AE4->2872C->286BC; publishes20 unless existing larger pending count defers; no compaction by nonzero amount',
  cursor_N5_N6='(Y1-131) = 0 for slot0 at67D/67E; must preserve full-accumulator transfers',
  stream_reads=stream_accesses(20),last_lookahead=['X35F->R5; Y:(R5+N5) read even final iteration','X360->R6','X361->R7','X362->X0'],
  last_lookahead_note='35F ARM286E4 clears0, but normal retention invariant unresolved;360..362 not dereferenced through next row; no fabricated sentinel',
  bank_reads=reads,clear='676/678 clearsY7C..9A; modulation690 writesY7C orY91 under selected original row/linear-AGU binding',
  outputs={'8F':dict(P='6D9',expression='MOVE_X_TO_A(X2E7); ADD(Y8Fmod); CLR_IFMI; MOVE_A_TO_Y'),
   '90':dict(P='6DE',expression='MOVE_Y_TO_A(Y90mod); ADD(X2E8 preloaded6D8); CLR_IFMI; MOVE_A_TO_Y'),
   '91':dict(P='6ED',expression='MOVE_X_TO_A(X2E9); ADD(Y14); MAC(Y131,X2EA); MAC(Y135,X2EB); ADD(Y91mod); CLR_IFMI; MOVE_A_TO_X0; MPY(Y13,X0); ASL; MOVE_A_TO_Y')},
  numeric_interpretation='signed24 memory, fractional MPY/MAC into56-bit accumulators; full transfers/overflow/saturation/scale depend on unqualified SR. Expressions are instruction sequences, not host float equations',
  mod8F90=dict(value=0,status='BOUNDED-PROOF conditional on original selected routing, linear address retention and no intervening alias; clear then no selected690 writer',not_a_CPU_measurement=True),
  direct_sinks='Y7D..9A; derived tailY9B..9E; X5BF..5C1',
  source_Y_accesses=['A0..A2 copy','A2,A3,A6 repeated lanes','131,135 voice terms','148..14C parameter terms','17C smoothed retained source','17D assignedY10','126 source7'],
  registers_used=['R0/R1/R2/R4/R5/R6/R7','N1/N2/N5/N6','M0/M1/M2/M4/M5/M6/M7'],
  no_full_initialization_or_side_effect_simulation=True))
 dump(out,'selected-note-event.json',dict(status='UNRESOLVED',event=None,bank=0,slot=0,patch='Rudi saw poly',
  note=None,velocity=None,tracked_pitch=None,target_pitch=None,pitch_seed=None,trigger_flags=None,gate_state=None,
  existing_project_candidates=projects,project_patch_offset=158996,
  source='installed Components conversion witness158996, cached archive; same-name candidate differs in7 bytes',
  reason='No exact patch/event/slot association or allocation history proven. Name match is insufficient; note literals not invented.',
  event_path='ARM497CA nonzero level->21DD4->21D86->219E8 allocation->21246 mailbox; target159/current12F/seed15C',
  allocation='217B4 bank0 candidates0..5; slot0 outcome requires lifecycle/readback; not guaranteed from note literal'))
 histories=[]
 for a,read,write,role in [(0x5ab,'ACC','AD0','previous nonlinear control'),(0x5ac,'AEE','AEF','derived nonlinear ramp history'),
  (0x5ad,'AF5','AF6','derived nonlinear ramp history'),(0x5ae,'BED/BF3','BFD','smoothed post control'),
  (0x5b7,'C2D/C33','C34','coefficient prior control'),(0x5b8,'C04/C2D','C08/C3C/C2A','recursive coefficient smoothing / prior peak')]:
  histories.append(dict(field=f'Y:{a:X}',classification='VOICE-STATE',boot_writer='2789 zero clear; initial epoch only',
   selected_path_reads=read,selected_path_writes=write,role=role,trigger_reset='outside33B loops[5AF,5B7) and[5BD,5C5)',
   last_writer_before_invocation='UNRESOLVED',value='',status='VERIFIED selected original access; UNRESOLVED runtime origin',
   completeness='selected-path writers enumerated; generic alias and unselected mode writer closure not claimed'))
 table(out,'history-provenance.csv',histories)
 dump(out,'history-initialization.json',dict(status='UNRESOLVED',selected_origin=None,values=None,
  candidates=[dict(origin='boot clear2789',value=0,admitted=False,reason='initial epoch; runtime calls and preservation not reconstructed'),
   dict(origin='trigger332..33E',admitted=False,reason='proven reset ranges exclude all six target words'),
   dict(origin='patch load / allocation / voice steal / mode change',admitted=False,reason='no bounded numerical last-writer chain recovered; patch getters and slot bank/mailbox updates do not establish retainedY histories')],
  no_zero_history_injected=True,no_full_boot_expansion=True))
 dump(out,'coefficient-values.json',dict(status='UNRESOLVED',words={f'Y:{a:X}':None for a in range(0xf64,0xf69)},
  original_last_writers={'F64':'C7E','F65':'C7D','F66':'C7C','F67':'C78','F68':'C65'},
  prerequisites='P657 controls, selectedBDD inputs and priorY5B7/5B8, arithmetic transfer modes and uploadedX1600..193F',
  original_execution=False,independent_numeric_reconstruction=False,reason='cannot numerically reconstruct with material unknowns; oracle not modified'))
 arithmetic=obj(PREV/'arithmetic-mode-state.json')
 arithmetic.update(p657=dict(required=['SM20 saturation mode','SA17 accumulator/address transfer behavior','DM14 multiplication mode','S0/S1 scaling and accumulator limiter transfer'],
  local_SR_writes=[],entry_CCR='P657 has no entry-condition branch before first arithmetic; later IFMI updated locally. Not proof all sticky bits irrelevant.',
  OMR='address/memory mapping and arithmetic/context obligations unresolved; no fabricated complete word'))
 dump(out,'arithmetic-context.json',arithmetic)
 agu=obj(PREV/'agu-state.json')
 agu['p657']=dict(R0='2D5->2FA then2D5..2F9 linear',R1='131+48=179',R2='57B+48=5C3 then7C clear cursor /98E frequency table',
  R4='7C->9B; transient destination7C/91',R5='131->modsource->131->135->tail9B',R6='A0->A3->modsource->A0; lane source accessesA2/A3/A6',
  R7='row absolute factor10 then131+23decimal=148',N5_N6=0,N5_after691=2,N1='Y7C modulation sum',
  N2='local0/quantized target713..71D',required_M='M0,M1,M2,M4,M5,M6,M7 entry retention unqualified; P657 does not set them',
  effective_addresses='CONDITIONAL on linear modifiers, bound descriptors, original full-accumulator pointer transfers')
 dump(out,'agu-context.json',agu)
 stack=obj(PREV/'stack-loop-state.json')
 stack['p657']=dict(calls=['33F->657 return341','37C->657 return37E'],
  owned_loops=['667 three-copy','676 clear31','685 N modulation rows','698 lanes3','70F lanes3','741 tail2'],
  normal_chain='19AC->281 ->37A->4D5 ->37C->657 ->37E->387 ->384->77F',
  trigger_chain='281 trigger reset->33F657 ->34137A ->4D5 ->37C657 (second call)',
  prefix=None,reason='original local DO loops close by758; inherited stack/loop prefix and interrupt eligibility remain unknown')
 dump(out,'caller-stack-context.json',stack)
 candidates=[dict(PC=pc,role=role,admitted=False,blocker=why) for pc,role,why in [
  ('33F','after trigger resets','histories not reset; event/state/modes/stack unknown'),('37A','before4D5','event/envelope/note history and global sources unknown'),
  ('657','control/modulation preparation','count/sentinel retention, corrected controls, modulator and envelope histories,modes,AGU,prefix'),
  ('387','prepared control consumer','Y8F/90/91 numerical transfer/input unknown'),('C2D','coefficient builder','prior smoothing histories,control words,table data,modes'),
  ('9D9','generation/post seam','natural original generator output/guard, material state unknown')]]
 table(out,'checkpoint-candidates.csv',candidates)
 dump(out,'selected-checkpoint.json',dict(status='REFUSED',PC=None,admitted=False,provenance_status='PARTIAL',blockers=BLOCKERS))
 admission=[]
 for row in csv.DictReader((PREV/'coefficient-provenance.csv').open()):
  field=row['field']
  if field.startswith('X:5') or field in ['Y:5AB','Y:5AE','Y:5B7/5B8']:
   admission.append(dict(field=field,value=row['candidate_value'],source=row['source'],qualified=False,
    status='CONDITIONAL source-backed expected value' if row['candidate_value'] else 'UNRESOLVED numerical value',
    blocker='natural invocation/context and retention not qualified' if row['candidate_value'] else 'see input/history/control provenance'))
 for field,source in [('Y:5AC','AEE/AEF'),('Y:5AD','AF5/AF6'),('Y:5B7','C34'),('Y:5B8','C08/C3C/C2A'),
  ('Y:F64..F68','C2D'),('SR/OMR','arithmetic-context.json'),('R/N/M','agu-context.json'),('SP/SC/LA/LC/LF/FV','caller-stack-context.json'),
  ('X:2C66 guard','natural generator/worker scratch'),('note/slot history','selected-note-event.json'),('row sentinel X:35F','286E4 clear; retention invariant still unresolved')]:
  admission.append(dict(field=field,value='',source=source,qualified=False,status='UNRESOLVED',blocker='material category-E not numerically closed'))
 table(out,'seam-admission-matrix.csv',admission)
 result=gate(admission)
 for directory in ['preparation-traces','stock-seam-traces']:
  (out/directory).mkdir();dump(out,directory+'/refusal.json',dict(**result,executed=False,blockers=BLOCKERS,PC_trace=None,cycles=None,measured_mutations=None))
 manifest={p.relative_to(ROOT).as_posix():sha(p) for p in [ARM,DSP,ARCHIVE,BUNDLE,Path(__file__),ROOT/'builds/phase3-selection0-channel0.asm',ROOT/'builds/phase9/ranges-final/constructor-formulas.csv',*sources]}
 dump(out,'provenance.json',manifest)
 dump(out,'validation.json',dict(status='PARTIAL',numeric_checkpoint='REFUSED',source_instructions_byte_checked=True,fresh_DSP_decode_ranges=spans,
  ARM_evidence=checked,p657_instruction_count=len(fresh),control_words=37,constructor_rows=20,stream_read_words=105,
  active_file_rows=[0,2],modulation_destinations=['Y:7C','Y:91'],stock_instructions_executed=0,preparation_replay=False,
  stock_seam_replay=False,coefficients_recovered=False,qualified_event=False,history_origin_qualified=False,
  Plaits_fed_justified=False,Phase20B_resume_numeric_replay=False,hardware_access=False,full_boot_expanded=False,
  best_next_step='recover one exact-patch event and bounded prior control/history timeline, including macro corrections and smoother origins, before CPU admission'))
 dump(out,'hashes.json',{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
 print(json.dumps(dict(status='PARTIAL / replay REFUSED',instructions_executed=0,output=str(out))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();recover(a.output_dir)
