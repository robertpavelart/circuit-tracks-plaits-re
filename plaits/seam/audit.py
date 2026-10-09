"""Byte-verified original seam map and fail-closed offline integration contract.

No stock execution is attempted without the requested provenance-qualified
checkpoint. Empty workload fields are null, not zero-cost claims or fake traces.
"""
import argparse,csv,hashlib,json,re,sys
from pathlib import Path
from contract import ROOT,readiness,require_qualified_checkpoint,ReplayRefused
sys.path.insert(0,str(ROOT/'tools'))
from ct_resource_audit import read_rows
from ct_stock_load_audit import verify_inputs

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(out,name,data):
 with (out/name).open('x',encoding='utf8',newline='\n') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
def table(out,name,rows):
 with (out/name).open('x',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def audit(out):
 base=ROOT/'builds/phase20b-seam'
 if out.exists() or not out.resolve().is_relative_to(base) or out.resolve()==base:raise ValueError('Fresh Phase20B-SEAM child required')
 verify_inputs()
 ppath=ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin'
 payload=ppath.read_bytes();assert sha(ppath)=='b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855'
 listing=ROOT/'builds/phase3-selection0-channel0.asm';rows=read_rows(listing,payload)
 for pc,text in {0x9d8:'move a,x:(r1)+',0x9d9:'move y:$0007,r0',0x9dd:'move x:(r0)+,a',0x9df:'jeq >$0a19',
  0xa1d:'jsr >$0bdd',0xbde:'jsr $0aa8',0xbe7:'mpy +y0,x0,a a,x:(r6)+',
  0xc9f:'move x0,x:(r1)+ y:(r4)+,y1',0xa93:'move x:(r5)+,y0',0x1beb:'movep x:$ffff88,a'}.items():assert rows[pc]['text']==text,(pc,rows[pc])
 out.mkdir(parents=True)
 rr=[]
 windows=[(0x9ac,0xcb8,'generator-tail/post/callees'),(0x470,0x4d5,'coefficient producers'),(0x198d,0x19f3,'descriptor/request-completion callers'),
  (0x1d9,0x281,'audio/group scheduler'),(0x11e9,0x1270,'group downstream'),(0x1be8,0x1c10,'per-voice timing bookkeeping'),(0x2779,0x2782,'modifier initialization')]
 for pc,r in sorted(rows.items()):
  roles=[role for lo,hi,role in windows if lo<=pc<hi]
  if roles:
   raw=payload[3*pc:3*(pc+r['words'])].hex()
   rr.append(dict(P=f'0x{pc:X}',opcode_words=raw,word_count=r['words'],instruction=r['text'],scope=';'.join(roles),status='VERIFIED bytes; not executed'))
 table(out,'seam-instructions.csv',rr)
 direct=[]
 for pc,r in rows.items():
  text=r['text'];op=text.split()[0];target=re.search(r'(?:>|\s)\$(0*9d[9d])\b',text,re.I)
  if target and op.startswith(('j','b')):direct.append(dict(pc=pc,text=text))
 seam=dict(selected_entry='P:0x9D9',first_post_dispatch='P:0x9DD',generation_last_store='P:0x9D8',
  predecessor='P:0x9C6 DO32 through0x9D8, natural fall-through after final store',direct_entry_candidates=direct,
  choice='include coefficient-pointer reload and3 NOPs before indirect load; no input sample math at9D9..9DC',
  successor=dict(mode0='A19->BDD->A1F->copy32->A7F',mode1or2='9EB->9FD subtract ->BDD->A09 add ->A1F->copy32->A7F',other='A15 pointer skip ->A7F, no BDD'),
  boundary='P:0xA95, immediately after32 group stores; no claim of caller return or downstream mixer execution',
  full_return='AA3 calls1BE8;1BEB unconditionally reads timer peripheralFFFF88; cannot silently emulate as0',
  pointers=dict(Y7='0x5AB, selected slot0 six-ramp producer9B8',R4='0x5AB, selected slot0 S+12',R0='reloaded fromY7 at9D9'),
  input=dict(space='X',start=0x2c46,end_exclusive=0x2c66,count=32,signed_bits=24,lanes=1,absolute_audio_scale=None,DC_normalized=None,safe_amplitude=None),
  group_output=dict(bank_zero='X:[2DF0,2E10)',bank_nonzero='X:[2E50,2E70)',count=32,bank_source='X:CC; captured by77F from descriptor bank'),
  mode0_coefficient_reads=['5AB mode','5AC/5AD nonlinear','5AE input scale','5AF/5B0 filter control','5B1/5B2 sequence offsets','5BB header','5BC gain delta','5BD gain current'],
  mode0_Y_state='5AB..5B8 under the reviewed nonlinear mode0/1 branch; exact mode-dependent footprint remains conditioned',
  instantiated_checkpoint=None,status='VERIFIED static local map / UNRESOLVED numeric checkpoint')
 dump(out,'seam-map.json',seam)
 live=readiness();live.update(pointer_and_buffer_contract=seam['pointers'],input=seam['input'],
  known_constants_conditioned_on_stock_initialization={'X39':5,'X3A':32,'X3B':16,'X3C':31,'X40':0},
  data_register_liveins='incoming A/B/CCR comparison values redefined locally; no all-mode liveout permission',
  pointer_liveins='R4; Y7 supplies R0 at selected9D9 entry; incoming AGU modifiers and arithmetic/loop modes remain required',
  stack_requirement='healthy resident prefix with room for up to4 extra entries for BDD/AA8/DO or BDD/C9D/DO; actual prefix and inherited LF/FV not admitted')
 dump(out,'seam-liveins.json',live)
 clobbers=dict(status='VERIFIED static potential union; not measured, no universal exact clobber certificate',
  region='P9D9..A94 plusAA8/BDD/C2D/C88/C9D selected reachable callees',
  potential_data_registers=['A','B','X0','X1','Y0','Y1','R0','R1','R2','R3','R4','R5','R6','R7','N1','N2','N3','N4','N5','N6'],
  examples={'R0':'9D9/r0 coefficient postincrements','R4':'AA8 state and A86 group pointer','M5':'ADC orB59 change, B24 orB75 restore fromY1A',
    'SR':'MAC/MACR/MPY/shift CCR; CA2 setsS1 andCB6 clearsS1', 'loops':'DO nesting; no concrete incoming stack assumed'},
  memory_outputs=['X raw/filter/scratch ranges','X group32 words','X current gain','Y retained nonlinear/filter/coefficient-control history'],
  output_register_flags='must treat as live until actual caller liveness closed')
 dump(out,'seam-clobbers.json',clobbers)
 guards=dict(status='VERIFIED selected conditional data flow / UNRESOLVED universal policy',address='X:0x2C66',
  selected_normalization_active=[dict(read='P:B1A',iteration=31,destination='B thenY0',use='prefetched next sample; no next iteration; not next output'),
   dict(read='P:A93',iteration=31,destination='Y0',use='gain-loop next sample; no next iteration; liveout register remains')],
  selected_normalization_skipped=[dict(read='P:BE6',iteration=31,destination='X0',use='BE7 executes a multiply on it while storing PREVIOUS A; newA not emitted as sample'),
   dict(read='P:A93',iteration=31,destination='Y0',use='reads filter-history word after overwrite, no33rd group sample')],
  overwrite='first C9D call: C9F writes Y-state X0 toX2C66 before recursion; old entry guard ceases to exist',
  MPY_flags='FM PDF378 (printed13-138): S,L,E,U,N,Z,V can change; C unchanged. Sticky/full liveout closure missing.',
  conditional_group32=True,guard_audio_term_unused_in_reviewed_prefetch=True,arbitrary_readable_word_safe_all_modes=None,
  duplicate_last_required=False,chosen_entry_policy=None,
  policies={p:'UNRESOLVED: no admitted complete seam state; not tested or selected' for p in ['duplicate_final','zero','preserved_previous','arbitrary_readable']})
 dump(out,'guard-word.json',guards)
 adapter=dict(status='TESTED isolated numeric primitive / stock binding UNRESOLVED',source='plaits/seam/adapter.py',samples=32,
  input='signed24 Q3.21',conversion='explicit caller shift; right shifts nearest ties away from0; symmetric explicit clipping limit',
  sign_preserved=True,scale_to_stock=None,headroom_to_stock=None,guard_policy=None,persistent_words=0,
  implementation='host harness only; no stock-facing default or guessed Q1.23 scale',DSP_P_words=None,DSP_cycles=None,DSP_scratch=None,DSP_clobbers=None,
  stock_adapter_refused=True,reason='signed24 storage is proved; absolute unit/gain/stability calibration is not')
 dump(out,'numeric-adapter.json',adapter)
 preservation=[]
 for name in ['R0','R1..R3','R4','R5..R7','N0..N7','M0..M7','A/B','X0/X1/Y0/Y1','SR modes/CCR','OMR','SP/SC/SSH/SSL','LA/LC/LF/FV']:
  preservation.append(dict(registers=name,Plaits='clobbered' if name in ['R0','R1..R3','R4','R5..R7','N0..N7','A/B','X0/X1/Y0/Y1'] else
                          'CCR and DO/JSR loop/stack state change; code does not write M or OMR',
   seam='R0 reload fromY7; preserve R4 and AGU/arithmetic/loop environment; other data liveins locally redefined, caller liveouts not closed',
   exact_save_words=None,save_restore_cycles=None,status='UNRESOLVED exact ABI; preservation obligation inventory'))
 table(out,'register-preservation.csv',preservation)
 state=dict(status='VERIFIED standalone / UNRESOLVED integrated sizes',per_voice_persistent_Plaits_X_words=7,
  per_block_controls_X_words=3,shared_renderer_scratch_X_words=3,working_scratch_registers=16,output_words=32,
  adapter_persistent_words=0,adapter_scratch_DSP_words=None,save_restore_spill_words=None,seam_glue_words=None,
  guard_readable_words=1,stock_filter_gain_state_reused_not_reclaimed=True,shared_immutable_LUT_words=0,
  no_stock_addresses_selected=True,standalone_literal_addresses='X0..2/X20..26/X30..32,Y0..1F overlap stock globals; isolated CPU contexts ONLY',
  persistent_RAM_safety=False)
 dump(out,'state-requirements.json',state)
 code=dict(status='VERIFIED baseline / UNRESOLVED integration overhead',renderer_P_words=442,adapter_P_words=None,
  call_glue_P_words=None,pitch_converter_P_words=None,total_added_P_words=None,
  standalone_exit='final JMP to harness stop, not a callable RTS entry/exit contract',
  direct_JSR_current_bytes_practical=False,call_architecture='UNRESOLVED; future remapping, call/return, modes, stack/register preservation first',
  possible_design_only_return_word=1,return_word_note='an appended RTS could add1P in a future separately qualified standalone module; NOT implemented',
  no_relocation_no_patch_no_payload_growth=True)
 dump(out,'code-requirements.json',code)
 refusal=readiness()
 for name in ['stock-baseline-traces','plaits-fed-traces']:
  (out/name).mkdir();dump(out/name,'refusal.json',dict(**refusal,trace_created=False,output_created=False,reason='request stopping rule: unresolved control/address/scaling/stack/mode inputs'))
 try:require_qualified_checkpoint()
 except ReplayRefused:pass
 else:raise AssertionError('Unqualified replay admitted')
 table(out,'block-cycle-costs.csv',[dict(case='not-admitted',blocks_executed=0,stock_issued=None,retained_cycles=None,adapter_cycles=None,
   status='REFUSED BEFORE CPU; zero executions is not zero workload')])
 table(out,'workload-breakdown.csv',[
  dict(layer='A',component='Plaits only',unit='per primitive',mean_cycles=7270.178723404255,tested_max=13335,derived_upper=13379,status='prior TESTED/CALCULATED/CONDITIONAL'),
  *[dict(layer=l,component=c,unit=u,mean_cycles=None,tested_max=None,derived_upper=None,status='UNRESOLVED; no replay/qualified timing') for l,c,u in
   [('B','numeric adapter','per voice'),('B','retained stock throughA94','per voice'),('C','bank routines/mixer','per bank/block'),
    ('separate','scheduler/FX/IRQ/DMA/timer waits','global/shared')]]])
 scaling=[]
 for n,groups in [(1,1),(2,2),(4,1),(10,None)]:
  c=n*13379
  scaling.append(dict(voices=n,groups=groups,generator_upper_subtotal=c,adapter_cycles=None,stock_per_voice_cycles=None,
   group_global_cycles=None,total_cycles=None,known_allowance_after_generator=163840-c,total_remaining=None,
   allowance_for_all_other_work_per_voice_if_no_group_cost=(163840-c)/n,
   status='CONDITIONAL generator component ONLY; complete path feasibility UNRESOLVED',
   formula='n*13379 + n*(adapter+stock_voice+call_glue) + sum(group_work) + shared_work'))
 table(out,'voice-scaling.csv',scaling)
 validation=dict(status='TESTED REFUSAL / VERIFIED STATIC MAP',stock_baseline_success=None,Plaits_fed_success=None,filter_gain_response=None,
  continuity_blocks=0,stock_instructions_executed=0,stock_cycles_measured=False,CPU_created=False,
  readiness={k:('NO' if k in ['offline_patch_design','hardware_flash','persistent_RAM_safety'] else 'UNRESOLVED') for k in
   ['local_seam_ABI_satisfied','retained_stock_processing','filter_gain_response','multi_block_continuity','one_voice_full_compute',
    'two_voice_full_compute','four_voice_full_compute','ten_voice_full_budget','register_save_restore_bounded','integrated_sizes_known',
    'offline_patch_design','hardware_flash','persistent_RAM_safety']},
  exact_blocker='X5AB/5AC control; X5B1/5B2 address; numeric/table/state/mode/stack/guard obligations',
  best_next_step='Recover one provenance-backed stock coefficient/state preparation checkpoint upstream of9D9, including mode/sequence offsets, SR/AGU/stack and normalization tables; replay only after gates close',
  static_instruction_rows=len(rr),standalone_renderer_unchanged=True,stock_payload_unchanged=True,
  hardware_access=False,flashing=False,patching=False,stock_RAM_reserved=False)
 dump(out,'validation.json',validation)
 inputs=[ppath,listing,ROOT/'notes/voice-output-contract.md',ROOT/'notes/voice-descriptor-map.md',ROOT/'builds/phase20a-bound/final/tight-cycle-bound.json',
         Path(__file__),Path(__file__).with_name('contract.py'),Path(__file__).with_name('adapter.py'),
         ROOT/'builds/phase19b/documentation/DSP56300FM.pdf',ROOT/'builds/phase19b/documentation/DSP56724RM.pdf']
 dump(out,'provenance.json',{p.relative_to(ROOT).as_posix():sha(p) for p in inputs})
 dump(out,'hashes.json',{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
 print('byte verified',len(rr),'rows; stock checkpoint refused beforeCPU; no invented workload',flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);audit(a.parse_args().output_dir)
