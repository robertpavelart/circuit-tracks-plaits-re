"""Export Phase20A-BOUND evidence from immutable existing proof/replay artifacts."""
import argparse,csv,json,hashlib
from domain import *
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p):return json.loads(p.read_text())
def dump(out,n,x):
 with (out/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
def table(out,n,rr):
 with (out/n).open('x',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
def export(out):
 base=ROOT/'builds/phase20a-bound'
 if out.exists() or not out.resolve().is_relative_to(base):raise ValueError('Fresh delivery output required')
 proof=obj(base/'proof-final/proof.json');verification=obj(base/'verified-final/verification.json')
 targets=obj(base/'verified-final/validated-targets.json');ws=obj(base/'fixtures/witnesses.json')
 best=max(x['cycles'] for x in targets);upper=proof['global_upper'];assert best==13335 and upper==13379
 mean=obj(ROOT/'builds/phase20a-regopt/timing/cycle-summary.json')['best_mean']
 out.mkdir(parents=True)
 events=dict(status='PROVEN-BOUND / CONDITIONAL',F=F,Q=Q,block_samples=32,
  input_domains=dict(raw_frequency_words=[1,F//2],clamped_frequency_words=[1,H],raw_PW_words=[0,F],shape_words=[0,Q]),
  retained_boundary=dict(phase_interval=[0,F-1],high_values=[0,1],previous_PW_equals_current_PW=True,PW_interval='[2*f,F-2*f]'),
  interpolation='c(j)=c0+floor(j*(target-c0)/32), j=1..32; carry count=(target-c0) mod32',
  limits=dict(wraps_per_sample=1,PW_crossings_per_sample=1,combined_events_per_sample=1,wraps_per_block=8,PW_crossings_per_block=8,combined_events_per_block=16,
   ratio_calls_per_block=[32,80],concurrent_correction_kinds_per_event=2,current_next_terms_per_event=4,correction_pairs_per_block=32,correction_terms_per_block=64,
   carry_occurrences_per_ramp=[0,31],carry_occurrences_all_ramps=[0,93],minimum_wrap_spacing_samples=4),
  exclusion='PW and wrap use if/elif; PW sets high=1, wrap sets high=0; event kinds alternate. No shape/PW extreme suppresses correction arithmetic.',
  exceptional_first_sample='If ramping frequency upward from tiny retained f, PW may cross beyond F before wrap; next sample wraps. At most two k=1 ratios; W<=5,PW<=6. Tested fixture.',
  ratio_domains=dict(PW_t='[0,1)',wrap_t='[0,1), or [1,2) in the deferred-first-wrap case',
   f_over_PW='(0,1/2]',f_over_complement_PW='(0,1/2]',naive='[0,1), or [1,3/2) on deferred first PW event',helper_guard='zero denominator path unreachable for legal events'),
  search=obj(base/'search-deep/search.json'),proof_reference='notes/plaits-reachable-timing-bound.md; proof-final/proof.json',
  machine_complete_scope='104 branch-cost profiles, exact interpolation remainder identity, finite aggregate event/count/cooldown DP; not full exact 24-bit reachability')
 dump(out,'event-domain.json',events)
 conditions={
  0x203:('raw f < H','otherwise clamp f=H and force PW=F/2','BOOT/renderer block setup'),
  0x216:('raw PW >= 2*ft','otherwise lower clamp; cannot combine with upper clamp','CONTROL'),
  0x21c:('PW <= F-2*ft','otherwise upper clamp; maximum setup106 not111','CONTROL'),
  0x25c:('frequency error <32','carry count = delta_f mod32; each carry10 cycles','RAMP'),
  0x26c:('PW error <32','carry count = delta_PW mod32; each carry10 cycles','RAMP'),
  0x27c:('shape error <32','carry count = delta_shape mod32; each carry10 cycles','RAMP'),
  0x293:('high !=0','skips PW test; event kinds alternate','EVENT'),
  0x297:('phase < PW','when high=0, no event and naive must be lower branch','EVENT'),
  0x2b8:('phase < F','wrap only with high=1, because PW<F','EVENT'),
  0x345:('sign flag ==0 (wrap)','PW and wrap corrections both executed; sign changes additions/subtractions','EVENT'),
  0x36b:('phase >= PW','PW event upper, wrap lower, high=0 no-event lower; high=1 no-event either','NAIVE'),
  0x3aa:('denominator ==0','unreachable for legal state; no guard path included in normal bound','RATIO'),
  0x3ac:('remainder < denominator','k=0 normally, at most two k=1 calls in low-frequency first-sample exception; k2/3 unreachable','RATIO')}
 rr=[]
 for pc,r in P.items():
  if r['family']=='JCC':
   c,constraint,scope=conditions[pc];rr.append(dict(pc=f'P:0x{pc:X}',assembly=r['assembly'],taken_condition=c,constraint=constraint,scope=scope,status='PROVEN-BOUND / CALCULATED'))
 assert len(rr)==len(conditions);table(out,'branch-constraints.csv',rr)
 table(out,'ratio-call-bounds.csv',[
  dict(path='every sample naive waveform',minimum_per_block=32,maximum_per_block=32,calls_per_event=0,proof='exactly one branch call per sample'),
  dict(path='event interpolation t',minimum_per_block=0,maximum_per_block=16,calls_per_event=1,proof='8 PW plus8 wraps, exclusive and alternating'),
  dict(path='event slope normalization',minimum_per_block=0,maximum_per_block=32,calls_per_event=2,proof='two slopes per event, independent of shape weight'),
  dict(path='total',minimum_per_block=32,maximum_per_block=80,calls_per_event=3,proof='both endpoints tested from reset/evolved state')])
 cases=[]
 for i,w in enumerate(ws):
  cases.append(dict(case=i,trial=w['trial'],target_cycles=w['cycles'],ratio_calls=w['ratio_calls'],PW_events=w['PW'],wrap_events=w['wrap'],preparation_blocks=len(w['preparation']),
   initial_state=json.dumps(w['initial_state']),target_controls=json.dumps(w['controls']),preparation_controls=json.dumps(w['preparation']),status='TESTED exact output/state/PC/cycles twice'))
 cases.append(dict(case=len(ws),trial='minimum-ratio fixture',target_cycles=targets[-1]['cycles'],ratio_calls=32,PW_events=0,wrap_events=0,preparation_blocks=0,
   initial_state=json.dumps(RESET),target_controls=json.dumps([1,F//2,0]),preparation_controls='[]',status='TESTED exact twice'))
 table(out,'adversarial-cases.csv',cases)
 table(out,'reachable-cycle-maxima.csv',[dict(case=r['case'],target_block=r['target_block'],cycles=r['cycles'],upper_with_boundary=r['cycles']+12,ratio_calls=r['ratio_calls'],PW_events=r['PW'],wrap_events=r['wrap'],
  status='DSP-tested, CALCULATED timing, legal reset history') for r in targets])
 bound=dict(status='PROVEN-BOUND / CONDITIONAL',prior_validated_stress_maximum=12670,reachable_search_DSP_tested_maximum=best,
  prior_paths_measured_as_instruction_traces=True,physical_cycle_measurement=False,reachable_upper_with_boundary=best+12,tight_derived_upper=upper,
  residual_gap_from_estimated_witness=upper-best,pipeline_boundary_allowance=12,unresolved_ordering_gap=upper-(best+12),
  proof_components=proof,old_structural_upper=23902,reduction_cycles=23902-upper,reduction_percent=100*(23902-upper)/23902,
  old_bound_normal_partition_ladder=[dict(bound=23902,reason='general k0..3 helper, all main branches independently'),dict(bound=19678,reason='normal k0 helper49 instead of82; saves4224'),
   dict(bound=19673,reason='incompatible dual clamp saves5'),dict(bound=19643,reason='at most93 not96 ramp carries saves30'),
   dict(bound=upper,reason='event counts, high/naive coupling, four-sample wrap spacing; saves6264')],
  fixed_resources=dict(P_words=442,persistent_X=7,scratch_X=3,working_registers=16,output_Y=32,LUT_words=0),
  timing_assumptions='unchanged pinned DSP56300-family model; short stores2; private internal zero-wait memory; resident stack; noIRQ/DMA;12 boundary allowance',
  physical_Circuit_timing='UNRESOLVED',stock_workload_added=False,clock_Hz=246000000,conditional_block_budget=163840,
  exact_reachability_claim=False,claim='safe bound over legal state; DP is a conservative aggregate relaxation, not a reachable supremum certificate',
  search_max_is_global=False,verification=verification)
 dump(out,'tight-cycle-bound.json',bound)
 scaling=[]
 for n in [1,2,4,8,10,12]:
  for name,c in [('unchanged_matched_mean',mean),('reachable_DSP_tested',best),('reachable_with_boundary',best+12),('proven_conditional_upper',upper)]:
   total=n*c;left=163840-total;percent=100*left/163840
   margin='LARGE RAW MARGIN' if percent>=50 else 'USEFUL RAW MARGIN' if percent>=30 else 'TIGHT RAW MARGIN' if percent>=15 else 'INSUFFICIENT RAW MARGIN FOR COMFORT'
   scaling.append(dict(voices=n,model=name,cycles=total,budget=163840,utilization_percent=100*total/163840,remaining_cycles=left,remaining_percent=percent,margin=margin,
                       scope='conditional raw generators only, no polyphony implementation or stock processing'))
 table(out,'voice-scaling.csv',scaling)
 # Recheck protected data/source baselines. Never rewrite their files.
 sys.path.insert(0,str(ROOT/'tools'));from ct_stock_load_audit import verify_inputs
 verify_inputs()
 for root in [ROOT/'builds/phase20a-regopt/final',ROOT/'builds/phase20a-div/final-compact',ROOT/'builds/phase20a-plaits/final']:
  for name,h in obj(root/'implementation-provenance.json').items():assert sha(ROOT/name)==h,name
  for name,h in obj(root/'hashes.json').items():assert sha(root/name)==h,name
 source=[Path(__file__),Path(__file__).with_name('domain.py'),Path(__file__).with_name('prove.py'),Path(__file__).with_name('search.py'),Path(__file__).with_name('verify.py'),
  ROOT/'plaits/poc/regopt/timing_opt.py',ROOT/'plaits/poc/timing/audit.py',base/'proof-final/proof.json',base/'verified-final/verification.json',base/'search-deep/search.json',
  ROOT/'builds/phase19b/documentation/DSP56300FM.pdf',ROOT/'builds/phase19b/documentation/DSP56724RM.pdf']
 dump(out,'provenance.json',{p.relative_to(ROOT).as_posix():sha(p) for p in source})
 dump(out,'hashes.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()})
 print('bound delivery verified',best,upper,'immutable guards PASS',flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);export(a.parse_args().output_dir)
