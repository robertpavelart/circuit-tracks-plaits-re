"""Complete stress timing from existing per-block calculations; no renderer rerun."""
import argparse,sys
from pathlib import Path
from generate_opt import ROOT
sys.path.insert(0,str(ROOT/'plaits/poc/timing'))
import audit
from timing_opt import classify
def summarize(out):
 out=out.resolve();base=ROOT/'builds/phase20a-regopt'
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh stress summary required')
 calculated=base/'extended-timing/block-cycle-estimates.csv';bs=audit.rows(calculated)
 assert len(bs)==4608
 for b in bs:
  assert sum(int(b[k]) for k in ['nominal_base_cycles','address_extra_cycles','branch_penalty_cycles','arithmetic_stall_cycles','transfer_stall_cycles'])==int(b['best_documented_estimate'])
  assert int(b['observed_trace_upper_bound'])==int(b['best_documented_estimate'])+12
 optimized={}
 for model in ['lower_bound','best_documented_estimate','observed_trace_upper_bound']:
  values=[int(b[model]) for b in bs];optimized[model]=dict(min=min(values),mean=sum(values)/len(values),max=max(values))
 optimized['structural_upper']=max(int(b['structural_upper_bound']) for b in bs)
 optimized['worst_block']=max(bs,key=lambda b:int(b['best_documented_estimate']))
 # Generic aggregation avoids the original audit's named43-case summary scopes.
 audit.classify=classify;gold=audit.suite_counts(base/'extended-golden-timing-inputs',None)
 original=audit.obj(base/'timing/cycle-summary.json')
 allworst=max(original['best_max'],optimized['best_documented_estimate']['max']);allupper=allworst+12
 out.mkdir(parents=True)
 audit.dump(out,'stress-cycle-comparison.json',dict(status='CALCULATED / CONDITIONAL',blocks=4608,golden=gold,optimized=optimized,
  original_suite_worst=original['best_max'],all_validated_worst=allworst,all_validated_observed_upper=allupper,
  original_suite_mean_used_for_category=original['best_mean'],scope='same fixed timing model; private memory/noIRQ/noDMA',
  partial_export_note='extended-timing complete per-block CSVs retained; named representative-case export failed because focused cases have different names; this summary completes those calculations'))
 scaling=[]
 for rate in [48000,48046.875]:
  budget=246000000*32/rate
  for n in [1,2,4,8,10,12]:
   for model,c in [('original_suite_mean',original['best_mean']),('all_validated_worst',allworst),('all_validated_observed_upper',allupper),('structural_upper',original['structural_upper']['cycles'])]:
    value=n*c;scaling.append(dict(rate_Hz=rate,voices=n,model=model,cycles=value,conditional_budget=budget,conditional_block_percent=100*value/budget,remaining_cycles=budget-value,
     scope='raw arithmetic only; mean from matched43-case suite; worst includes focused stress'))
 audit.csvout(out,'voice-scaling.csv',scaling)
 audit.dump(out,'provenance.json',{'completed_optimizer_block_CSV':audit.sha(calculated),'golden_projection':audit.sha(base/'extended-golden-timing-inputs/hashes.json'),'source':audit.sha(Path(__file__))})
 audit.dump(out,'hashes.json',{p.name:audit.sha(p) for p in sorted(out.iterdir()) if p.is_file()})
 print('All validated worst cycles',allworst,'observed upper',allupper,'structural',optimized['structural_upper'],flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);summarize(a.parse_args().output_dir)
