"""Summarize existing rate-tagged cases separately; no renderer execution."""
import argparse
from pathlib import Path
from audit import BASE,NATIVE,obj,rows,csvout,dump,sha
def summarize(suite,out):
 out=out.resolve()
 if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('Fresh rate output required')
 for n,h in obj(suite/'hashes.json').items():assert sha(suite/n)==h
 out.mkdir(parents=True);blocks=rows(suite/'block-cycle-estimates.csv');cases=obj(NATIVE/'cases.json')
 records=[];pairs=[]
 for rate in [48000,48046.875]:
  budget=246000000*32/rate
  for scope,group in [('all_rate_tagged',[b for b in blocks if float(b['sample_rate'])==rate]),
                      ('matched_six_pitch_cases',[b for b in blocks if float(b['sample_rate'])==rate and b['name'].startswith('pitch')])]:
   values=[int(b['best_documented_estimate']) for b in group]
   mean=sum(values)/len(values);upper=max(int(b['structural_upper_bound']) for b in group)
   records.append(dict(rate_Hz=rate,scope=scope,blocks=len(values),best_min=min(values),best_mean=mean,best_max=max(values),
    trace_upper=max(int(b['observed_trace_upper_bound']) for b in group),structural_upper=upper,
    conditional_budget=budget,conditional_period_us=32/rate*1e6,conditional_mean_percent=100*mean/budget,
    conditional_worst_percent=100*max(values)/budget,conditional_structural_percent=100*upper/budget,
    caveat='all_rate_tagged has different case mixture; only matched_six_pitch_cases aligns controls/notes'))
  for c in cases:
   if c['rate']!=rate or not c['name'].startswith('pitch'):continue
   group=[b for b in blocks if int(b['case'])==c['id']];values=[int(b['best_documented_estimate']) for b in group]
   pairs.append(dict(MIDI=c['midi'],rate_Hz=rate,case=c['id'],blocks=len(values),best_min=min(values),best_mean=sum(values)/len(values),best_max=max(values),
    conditional_budget=budget,conditional_mean_percent=100*sum(values)/len(values)/budget))
 csvout(out,'rate-summary.csv',records);csvout(out,'matched-pitch-rate-comparison.csv',pairs)
 dump(out,'hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--suite-dir',type=Path,required=True);a.add_argument('--output-dir',type=Path,required=True)
 ns=a.parse_args();summarize(ns.suite_dir,ns.output_dir)
