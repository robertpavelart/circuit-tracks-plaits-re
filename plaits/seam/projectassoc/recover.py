"""Focused offline project0/material-equivalence audit. No ARM/DSP execution.

Bound original macro integer arithmetic independently of runtime histories.
Never promote a conditional load-boundary result to a selected-event snapshot.
"""
import argparse,csv,hashlib,json,struct,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from ct_phase4_trace import arm_evidence
from ct_stock_load_audit import verify_inputs
BASE=ROOT/'builds/phase20b-projectassoc'
PREV=ROOT/'builds/phase20b-inputrec/final-v3'
CHECKPOINT=ROOT/'builds/phase20b-checkpoint/final'
ARCHIVE=ROOT/'builds/phase19c-assetdata/discovery/archives/fae30b90741bfaebfdd94b98e0f8d18fd7be9b1266e3f74291ea9fef02285fa5.zip'
BUNDLE=ROOT/'builds/phase19c-packlink/app-1.72.1/code/ember-dist/assets/main-DHaPxgL3.js'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def obj(p):return json.loads(p.read_text(encoding='utf8'))
def dump(out,name,data):
 with (out/name).open('x',encoding='utf8',newline='\n') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
def table(out,name,rows):
 with (out/name).open('x',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def s8(v):return ((v+128)&255)-128
def s16(v):return ((v+32768)&65535)-32768
def sdiv(n,d):return (-1 if (n<0)!=(d<0) else 1)*(abs(n)//abs(d))
def original_term(value,start,end,depth):
 # 35FCC LDRSB end;35FD4 SXT span;35FDE abs;35FE8 signed position;
 # 35FF6 negative position=>0;36006 clamp;3600C/10 signed product*2;SDIV.
 span=s8(s8(end)-start)
 if span==0:span=1
 elif span<0:span=s8(-span)
 if span<=0:raise ValueError('Unqualified signed span')
 pos=s8(value-start)
 if pos<0:pos=0
 if span<s8(pos):pos=span
 return sdiv(s8(pos)*s8(depth-64)*2,span)
def independent_term(value,start,end,depth):
 # Independent rational expression, restricted to the selected legal ascending rows.
 if not (0<=value<=127 and 0<=start<=end<=127 and 0<=depth<=127):raise ValueError('Selected ascending-domain model only')
 denominator=end-start or 1
 numerator=2*(depth-64)*min(max(value-start,0),denominator)
 return sdiv(numerator,denominator)
def correction_state(q):
 sums=[0]*70;terms=[]
 for m in range(8):
  base=204+17*m;value=q[base]
  for j in range(4):
   d,a,e,k=q[base+1+4*j:base+5+4*j]
   if d:
    assert 1<=d<=70
    t=original_term(value,a,e,k);assert t==independent_term(value,a,e,k)
    sums[d-1]=s16(sums[d-1]+t)
   else:t=0
   terms.append(dict(macro=m,subslot=j,record_offset=base+1+4*j,value=value,destination=d,start=a,end=e,
    encoded_depth=k,signed_depth=k-64,contribution=t,skipped=d==0))
 return sums,terms
def corrected(q,param,ids,raw):
 d=raw(0x805454c+8*param,8);v=q[int.from_bytes(d[:2],'little')]
 # Selected affected fields are plain/signed encoded byte getter types1/2.
 if d[2] not in [1,2]:raise ValueError('unqualified getter')
 sums,_=correction_state(q)
 if param in ids and sums[ids.index(param)]:v=max(0,min(127,v+sums[ids.index(param)]))
 return v
def admit(equivalence,chain,event):
 return equivalence=='MATERIALLY EQUIVALENT' and chain and event
def recover(out):
 out=out.resolve()
 if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('Fresh projectassoc report child required')
 verify_inputs();arm_path=ROOT/'firmware/circuittracks-firmware-4486.bin';arm=arm_path.read_bytes()
 raw=lambda a,n:arm[a-0x8010000:a-0x8010000+n]
 u=lambda a:struct.unpack('<I',raw(a,4))[0]
 q=(CHECKPOINT/'immutable/selected-offline-patch.binary').read_bytes()
 assert len(q)==340 and sha(ARCHIVE)==ARCHIVE.stem
 with zipfile.ZipFile(ARCHIVE) as z:
  project=z.read('projects/project_0.ncs');assert z.read('patches/patch_0.syx')[9:-1]==q
 assert len(project)==160780 and project[:4]==b'USER' and struct.unpack_from('<I',project,4)[0]==160780
 cached=project[158996:159336];assert cached[:16]==q[:16]
 differences=[i for i,(a,b) in enumerate(zip(q,cached)) if a!=b]
 assert differences==[35,221,238,255,272,289,306]
 evidence=sorted((BASE/'evidence').glob('*.asm'))
 existing=[ROOT/'builds/phase9/correction/0803602A-080360B2.asm',ROOT/'builds/phase9/correction/080360B2-08036198.asm',
  ROOT/'builds/phase9/routing/0803BE20-0803BF20.asm',ROOT/'builds/phase9/routing/0803BB38-0803BCA0.asm',
  ROOT/'builds/phase9/entry/080273E4-08027D1A.asm',ROOT/'builds/phase9/boundary/08028132-080283D8.asm',
  ROOT/'builds/phase9/helper-closure/0802853C-080286AA.asm',
  ROOT/'builds/phase20b-checkpoint/evidence/arm-view-constructor.asm',ROOT/'builds/phase9/parameter-helpers/0803BD00-0803BD58.asm']
 checked=[dict(path=p.relative_to(ROOT).as_posix(),instructions=arm_evidence(p,arm),sha256=sha(p)) for p in evidence+existing]
 # The prior structural analysis is imported and hashed; no repeat P657 decoding.
 p657=obj(PREV/'p657-input-record.json');assert p657['control_words']==37
 ids=list(raw(0x805a2b0,70));assert ids==obj(CHECKPOINT/'reverse-index-provenance.json')['IDs']
 js=BUNDLE.read_text(encoding='utf8');witnesses=[]
 terms=['settings:bY.byteOffset(32).byteLength(4)','keyboardOctave:wY.byteOffset(3).signed()',
  'macroSlots:bY.byteOffset(204).byteLength(17)','value:wY.byteOffset(0),subSlots:bY.byteOffset(1).byteLength(4)',
  'destination:wY.byteOffset(0),start:wY.byteOffset(1),end:wY.byteOffset(2),depth:wY.byteOffset(3).signed()',
  'new Uint8Array(n,158996,680)','SYNTH_PATTERN_SIZE:3240','name:hR.byteOffset(16).byteLength(32)']
 for term in terms:
  at=js.index(term);witnesses.append(dict(character_offset=at,needle=term,excerpt=js[max(0,at-80):at+len(term)+160]))
 # Snapshot the precise patch macro destination-name array, not the unrelated MIDI template.
 at=js.index('y5=[');end=js.index('],v5=',at)+1
 names=json.loads(js[at+3:end]);assert len(names)==71
 va,ta=correction_state(q);vc,tc=correction_state(cached)
 out.mkdir(parents=True);(out/'immutable').mkdir()
 # Copies of cached sources for reproducibility; never edit the user's originals.
 (out/'immutable/project0.ncs').write_bytes(project)
 (out/'immutable/project0-synth0-patch.binary').write_bytes(cached)
 dump(out,'components-witnesses.json',dict(source=BUNDLE.relative_to(ROOT).as_posix(),sha256=sha(BUNDLE),executed=False,witnesses=witnesses,destination_names=names))
 diffrows=[];prov=[]
 for offset in differences:
  if offset==35:
   param=5;field='settings.keyboardOctave';classification='F';m=None
   destinations='UNRESOLVED note/UI source relevance; no proved direct DSP sink'
   detail='signed encoded values -1 / 0; not classified UI-only without consumer proof'
  else:
   m=(offset-204)//17;param=174+17*m;field=f'macroSlots[{m}].value';classification='E'
   ds=sorted({v['destination'] for v in ta if v['macro']==m and v['destination']})
   destinations=';'.join(f'{names[d]} / ID{ids[d-1]:X}' for d in ds)
   detail='runtime correction seed; macro destinations/start/end/depth bytes identical'
  d=raw(0x805454c+8*param,8);assert int.from_bytes(d[:2],'little')==offset
  diffrows.append(dict(offset=offset,project_file_offset=158996+offset,authored=q[offset],cached=cached[offset],field=field,
   macro_index='' if m is None else m,classification=classification,descriptor_ID=param,descriptor_address=f'0x{0x805454c+8*param:X}',
   descriptor_bytes=d.hex(),getter='36192->3BE3E->bank0 view3BBD6->3BD00',destinations=destinations,meaning=detail))
  prov.append(dict(offset=offset,field=field,classification=classification,
   model='settings32+3 signed' if m is None else f'204+17*{m}; macro value byte0; four subrows+1',
   original_read='projectF494 ID5 or full-copy+12' if m is None else f'projectF458..482 ID{param:X} or full-copy+12;35F90 reads value',
   correction='not corrected, ID5 absent from70 mapping' if m is None else '35F84..36018 adds signed truncated contributions atwork20005B10;3602A copies changes to20005C28;360B2 clips getter',
   active_for_selected_event='UNRESOLVED',DSP_reach=destinations,convergence='not proved' if m is None else 'conditional load/recompute differs for active destinations; later automation not closed'))
 table(out,'patch-byte-differences.csv',diffrows);table(out,'difference-provenance.csv',prov)
 corrections=[]
 for i,(a,c) in enumerate(zip(va,vc)):
  param=ids[i];d=raw(0x805454c+8*param,8);o=int.from_bytes(d[:2],'little')
  corrections.append(dict(destination=i+1,name=names[i+1],parameter_ID=param,offset=o,base_value=q[o],
   authored_correction=a,cached_correction=c,authored_corrected=max(0,min(127,q[o]+a)),cached_corrected=max(0,min(127,cached[o]+c)),
   relation='IDENTICAL' if a==c else 'DIFFERENT-AND-MATERIAL',
   scope='CALCULATED conditional complete3602A recompute using stored patch macro values; no automation snapshot'))
 table(out,'macro-corrections.csv',corrections)
 macros=[]
 for m in range(8):
  macros.append(dict(index=m,descriptor_ID=174+17*m,offset=204+17*m,authored_stored=q[204+17*m],cached_stored=cached[204+17*m],
   app_constructor_value=0,firmware_default=None,active_event_value=None,
   subslots=[dict(authored=a,cached=c,parameter_ID=ids[a['destination']-1] if a['destination'] else None,
    destination_name=names[a['destination']]) for a,c in zip(ta,tc) if a['macro']==m],
   event_automation='UNRESOLVED; stored values are not a playback snapshot'))
 dump(out,'macro-state.json',dict(status='VERIFIED stored values / CALCULATED conditional corrections / event UNRESOLVED',macros=macros,
  domain='value unipolar0..127; depth encoded64 is signed0; start/end are per-assignment boundaries, no common center assumed',
  original_formula='span=abs(s8(end-start)) or1; pos=clamp(s8(value-start),0,span); contribution=SDIV(2*pos*s8(depth-64),span), trunc toward0; sum signed16 per destination',
  work_clear='36042->1A7E4 r2=0->1A93C fills140 bytes;70 halfwords perbank',
  raw_vs_corrected='macro getter36192 reads raw descriptor bytes, not360B2; eight calls35F84 consume IDs174+17*m',
  recompute_gate='3602A complete on bank0 bound to these exact340-byte views; dirty-bit/callback commit and later automation not executed',
  independent_model='ascending-domain rational expression agrees with instruction-step model on all32 selected rows',
  authored_halfwords=va,cached_halfwords=vc))
 assert u(0x803b9b8)==0x01020408 and u(0x8028b68)==0xaaaaab
 def resonance(v):return ((v*u(0x803b9b8))&0xffffffff)>>8
 def env(v):
  signed=s8(v-64);t=raw(0x805a340+abs(signed),1)[0]
  factor=u(0x8028b68) if signed>=0 else u(0x8028b7c)
  return ((t*factor)&0xffffffff)>>8
 assert u(0x8028750)==0x805bcd0 and int.from_bytes(raw(0x805bcd4,2),'little')==0x590c
 def frequency_target(v):
  # 282F4 literal28750->805BCD0;LDRH[IP+4] is immutable590C.
  v=(v*u(0x8028b68)+u(0x8028b74))&0xffffffff
  return ((v+(0x590c<<16))&0xffffffff)>>8
 control=[]
 for field,param,fn,site in [('X:2E7',31,lambda v:(v<<16)&0xffffff,'2794A'),('X:2E8',36,resonance,'27964'),
  ('X:2EA',38,env,'27998'),('X:2EB',35,resonance,'279B2'),('X:3E7',34,frequency_target,'2797E')]:
  a=corrected(q,param,ids,raw);c=corrected(cached,param,ids,raw);x=fn(a);y=fn(c)
  control.append(dict(field=field,parameter_ID=param,authored_corrected=a,cached_corrected=c,
   authored_DSP=f'{x:06X}',cached_DSP=f'{y:06X}',ARM_sink=site,
   relation='IDENTICAL' if x==y else 'DIFFERENT-AND-MATERIAL',scope='CALCULATED conditional original ARM callback and upper24 transport; no observed DSP state'))
 table(out,'control-boundary.csv',control)
 dump(out,'frequency-target-provenance.json',dict(status='VERIFIED immutable source / CALCULATED conditional target words',
  P657_not_redecoded=True,ARM_helper='282E4..2830A',literal_PC='282F4->[28750]=805BCD0',
  LDRH_address='805BCD4',LDRH_value='590C',formula='upper24((AAAAAB*correctedID22+B7FFFFEC+(590C<<16)) mod2^32)',
  authored_target='19B6AA',cached_target='2FB6AA',current_X2E9=None,
  supersedes='Phase20B3 called the high-half addend runtime/unresolved; fixed FLASH literal resolves it. Retained X2E9 smoother still unknown'))
 material=[]
 for row in corrections:
  if row['authored_correction']!=row['cached_correction']:
   targets={25:'X3C5->X2E2 then6BB',34:'X3E7->X2E9 then6DF',36:'X2E8 then6D8/6DE',38:'X2EA then6E2/6E4',
    41:'Y per-slot envelope parameters->4D5',46:'Y per-slot envelope parameters->4D5',48:'Y per-slot envelope parameters->4D5',79:'X3F1 effects target27C52'}
   match=next((v for v in control if v['parameter_ID']==row['parameter_ID']),None)
   material.append(dict(field=f"ID{row['parameter_ID']:X} {row['name']}",authored=row['authored_corrected'],cached=row['cached_corrected'],
    authored_DSP=match['authored_DSP'] if match else '',cached_DSP=match['cached_DSP'] if match else '',
    relation='DIFFERENT-AND-MATERIAL',destination=targets[row['parameter_ID']],
    status='CALCULATED conditional stored-macro recompute; X2E8/X2EA nonconvergence proven at transfer boundary; histories not instantiated'))
 material.append(dict(field='ID5 keyboardOctave',authored=-1,cached=0,authored_DSP='',cached_DSP='',relation='UNRESOLVED',
  destination='event source/UI consumer not closed',status='VERIFIED signed model; not proved irrelevant for selected event'))
 for field,value in [('X5AB',0),('X5AC',1),('X5B1',5),('X5B2',5)]:
  material.append(dict(field=field,authored=value,cached=value,authored_DSP='',cached_DSP='',relation='IDENTICAL',
   destination='same original selectors/offsets',status='CONDITIONAL expected field; prior20B2 proof imported'))
 table(out,'material-equivalence.csv',material)
 identity=dict(status='PARTIAL',project_member='projects/project_0.ncs',archive=ARCHIVE.relative_to(ROOT).as_posix(),
  project_sha256=digest(project),project_signature='USER',declared_size=160780,project_name=project[16:48].decode('ascii').rstrip(),
  patch_name=cached[:16].decode('ascii').rstrip(),patch_offset=158996,patch_size=340,patch_sha256=digest(cached),
  authored_sha256=digest(q),pack_ID=None,archive_slot=0,physical_selected_pack=None,
  synth_identifier_records=[dict(track=i,offset=52580+8*i,bytes=list(project[52580+8*i:52588+8*i])) for i in range(2)],
  literal_ID_bytes=[0,32],literal_byte0_role='AF66 returns8-byte synth record;F18C compares byte0 with retained runtime property then selects full-copy versus macro-only update',
  ID_byte0_pack_slot_interpretation='UNRESOLVED exact native pack/patch-slot numbering; do not infer physical pack from archive name',
  bank0_binding='F442 chooses parameter view+344, sourcebase+26D14;3BE60 bank0 returns+344; prior constructor binds logical0',
  bank1_binding='F4AC view+348, sourcebase+26E68',
  load_branches=['F438 flag nonzero->F450 virtual+12 copies340 bytes via3BBE2',
   'F454..49C retained-identity branch updates8 macro values IDsAE+17*m plusID5 keyboardOctave'],
  bounded_merge='if preexisting active bank0 is authored340-byte patch, partial update changes exactly its seven differing bytes and yieldscached340-byte patch; tested byte reconstruction',
  retained_identity_and_active_branch=None,program_history=None)
 merged=bytearray(q)
 for m in range(8):merged[204+17*m]=cached[204+17*m]
 merged[35]=cached[35];assert bytes(merged)==cached
 dump(out,'patch-identity.json',identity)
 chain=dict(status='PARTIAL',qualified=False,project='project0',track_group_candidate=0,logical_bank0_patch_association=True,
  pattern_address_formula='AF46: projectbase+6540*track+2E4 fortrack0/1; eightCA8-stride patterns each; others useD7FC',
  pattern_group0_offset=740,pattern_stride=3240,patterns_per_group=8,step_stride=28,steps_per_pattern=32,
  layout_producers='ADB2..AE12 group init;B03E..B0BE32 step records; Components Gge16-pattern migration corroborates strides',
  event=None,native_pack=None,native_patch_slot=None,DSP_voice_slot=None,
  missing_edges=['selected playback pattern/step and note-field consumer','original automation schedule to macro/correction boundary',
   'event frontend track routing to497CA','allocation lifecycle/readback proving slot0'],
  no_guessed_association=True)
 dump(out,'event-bank-slot-chain.json',chain)
 dump(out,'selected-event.json',dict(status='UNRESOLVED',qualified=False,event=None,note=None,velocity=None,gate=None,length=None,
  pattern=None,step=None,track=None,bank=None,voice_slot=None,macro_values=None,automation=None,
  unqualified_layout_candidate=dict(file_offset=740,group=0,pattern_layout_index=0,step_layout_index=0,raw28=list(project[740:768]),
   explanation='data bytes and original stride only; no guessed note/velocity/gate decode or playback choice'),
  reason='material equivalence at chosen event and complete note/track/allocation chain not established'))
 inputs=[];byfield={v['field']:v for v in control}
 for a in range(0x2d5,0x2fa):
  field=f'X:{a:X}';c=byfield.get(field)
  inputs.append(dict(field=field,authored=c['authored_DSP'] if c else '',cached=c['cached_DSP'] if c else '',
   relation=c['relation'] if c else 'UNRESOLVED',
   scope='conditional original callback transport boundary' if c else 'runtime/correction/smoothing/event word not numerically qualified'))
 for field in ['countX2FA','rowsX2FB..35E','lookaheadX35F..362','Y17C','Y126','Y131','Y135','Y148..14C','Y:A0..A3/A6','Y8F','Y90','Y91','material_SR_OMR_AGU_stack']:
  inputs.append(dict(field=field,authored='',cached='',relation='UNRESOLVED',scope='row literals identical, but active source/amount/history/context retention incomplete'))
 already={v['field'] for v in inputs}
 with (PREV/'p657-field-provenance.csv').open(encoding='utf8',newline='') as f:
  for prior in csv.DictReader(f):
   if prior['field'] not in already:
    inputs.append(dict(field=prior['field'],authored='',cached='',relation='UNRESOLVED',
     scope='Imported20B3 '+prior['category']+' obligation; no event/mode/retention equality inferred'))
    already.add(prior['field'])
 table(out,'p657-material-inputs.csv',inputs)
 rowdata=[v for v in obj(PREV/'patch-field-values.json')['fields'] if v['ID'] in [94,95,96,97,102,103,104,105]]
 assert q[124:204]==cached[124:204]
 dump(out,'y91-provenance.json',dict(status='PARTIAL; no numericalY91',row_literals_identical=True,rows=[0,2],
  row0=list(q[124:128]),row2=list(q[132:136]),prior_structural_report='phase20b-inputrec/final-v3/p657-input-record.json',
  slot0_sources=['row0 Y17C*Y17C','row2 Y126*Y17D; factorY10'],row_fields=rowdata,
  direct_macro_depth_changes=False,depth_targets='selected macro assignments do not target destinations51/53 (row0/2 depths); corrections0 in complete stored-value recompute',
  nominal_depths=[49,4],amount_target_X=['3D0','3D2'],
  amount_target_words=[f'{raw(0x805a340+d,1)[0]*0xaaaa:06X}' for d in [49,4]],
  amount_target_provenance='CALCULATED conditional raw depths after complete stored-macro recompute; dest12 type2 selects285EA TBB entry285F0->28640, byte curve805A340*5555*512 then upper24 transport',
  smoothed_amount_X=['2FE','308'],smoothed_amount_values=None,
  indirect_macro_changes=['frequency ID22:13->46, target3E7 then retainedX2E9','env2 term ID26:97->83, transferX2EA1C0000->0CAAAA',
   'envelope IDs2E/30 and possibly note state change sourceY131/Y135; event path unresolved'],
  needed_preceding_state=['lastY17C andX5C3/shiftX40 before674','Y126 at source read and envelope stateY131/Y135',
   'X2FE/X308 previous smoothing words and number/timing of1B89 updates','X2E9 old smoother;282E4 high-half source now proven immutable590C',
   'full macro automation timeline, event/voice lifecycle and material CPU context'],value=None))
 dump(out,'history-opportunity.json',dict(status='UNRESOLVED',selected_event=None,nearest_qualified_origin=None,history_values=None,
  candidate_boundary='project loadEEFE:340-byte ARM patchview copy/selected controls; macro work clear3602A only initializes correction workspace',
  candidate_rejected_reason='project/parameter initialization does not establish last numerical writers ofY5AB..5AE/5B7/5B8; prior20B3 trigger exclusion retained',
  macro_work_clear_is_DSP_history_clear=False,preceding_project_event_sequence=None,no_boot_zero_substitution=True,no_DSP_execution=True))
 reasons=['load/recompute boundary materially differs; event-time automation convergence not proved',
  'pack/patch-slot identifiers and event playback/track routing not fully decoded','physical voice slot0 allocation and prior timeline unknown',
  'retainedY histories, smoothed controls and material CPU context unresolved']
 dump(out,'qualification.json',dict(overall_status='PARTIAL',cached_patch_event_classification='INSUFFICIENT EVIDENCE',
  conditional_load_boundary='MATERIALLY DIFFERENT',conditional_nonconvergent_fields=['X2E8','X2EA','ID22 target3E7'],
  exact_event_qualified=False,event_usage_admitted=admit('INSUFFICIENT EVIDENCE',False,False),
  blockers=reasons,stock_seam_replay=False,stock_instructions_executed=0,Plaits_fed=False,
  best_next_step='trace the original sequencer/automation consumer for project0 group0 pattern0, proving event routing and whether macros override the differing load values before its first note'))
 sources=[arm_path,ARCHIVE,BUNDLE,Path(__file__),PREV/'p657-input-record.json',PREV/'p657-field-provenance.csv',PREV/'hashes.json',CHECKPOINT/'immutable/selected-offline-patch.binary',*evidence,*existing]
 dump(out,'provenance.json',{p.relative_to(ROOT).as_posix():sha(p) for p in sources})
 dump(out,'validation.json',dict(status='PARTIAL association; conditional material difference CALCULATED',byte_differences=len(differences),
  all_fields_named=True,changed_macro_values=[1,2,3,4,5,6],assignments_identical=True,independent_macro_models_agree=True,
  differing_correction_destinations=[v['destination'] for v in corrections if v['relation']=='DIFFERENT-AND-MATERIAL'],
  partial_update_merges_to_cached_patch=True,ARM_evidence=checked,P657_structural_analysis_restarted=False,
  no_exact_event_or_active_macro_snapshot=True,stock_instructions_executed=0,hardware_access=False,Components_launched=False,
  downloaded=False,original_files_modified=False,Plaits_fed=False,stock_seam_replay=False))
 dump(out,'hashes.json',{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
 print(json.dumps(dict(status='PARTIAL',conditional_load_boundary='MATERIALLY DIFFERENT',event_admitted=False,output=str(out))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();recover(a.output_dir)
