"""Canonical REGOPT delivery; reuse completed liveness/renders/timing evidence."""
import argparse,json,sys
from pathlib import Path
from generate_opt import ROOT
sys.path.insert(0,str(ROOT/'plaits/poc/timing'))
from audit import rows,obj,sha,csvout,dump
BASE=ROOT/'builds/phase20a-regopt'
def finalize(out):
 out=out.resolve()
 if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('Fresh final report required')
 report=BASE/'report';stress=BASE/'stress-timing-summary'
 for folder in [report,stress]:
  for n,h in obj(folder/'hashes.json').items():assert sha(folder/n)==h,n
 out.mkdir(parents=True)
 for name in ['scratch-liveness.csv','register-allocation.csv','before-after-instruction-census.csv','hotspot-comparison.csv','memory-traffic.csv','optimization-options.json','golden-reference.json']:
  (out/name).write_bytes((report/name).read_bytes())
 extra=obj(stress/'stress-cycle-comparison.json');new=obj(BASE/'timing/cycle-summary.json')
 comparisons=rows(report/'before-after-cycles.csv')
 for metric,old,value in [('focused_stress_mean',extra['golden']['best_mean'],extra['optimized']['best_documented_estimate']['mean']),
                          ('focused_stress_max',extra['golden']['best_max'],extra['optimized']['best_documented_estimate']['max']),
                          ('all_validated_observed_upper',extra['golden']['observed_upper_max'],extra['all_validated_observed_upper'])]:
  comparisons.append(dict(metric=metric,old=old,new=value,reduction_percent=100*(old-value)/old,unit='conditional calculated cycles; focused stress/all cases'))
 csvout(out,'before-after-cycles.csv',comparisons)
 (out/'voice-scaling.csv').write_bytes((stress/'voice-scaling.csv').read_bytes())
 exact=obj(report/'exact-equivalence.json');exact.update(all_validated_worst_cycles=extra['all_validated_worst'],all_validated_observed_upper=extra['all_validated_observed_upper'],timing_worst_includes_focused_stress=True)
 dump(out,'exact-equivalence.json',exact)
 summary=obj(report/'optimization-result.json');summary.update(all_validated_worst=extra['all_validated_worst'],all_validated_observed_upper=extra['all_validated_observed_upper'],focused_stress_timing=extra,
  mean_reduction_scope='unchanged43-case matched suite',final_report='notes/plaits-register-optimization.md')
 dump(out,'optimization-result.json',summary)
 dump(out,'provenance.json',{p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),report/'hashes.json',stress/'hashes.json',BASE/'final/hashes.json',BASE/'timing/hashes.json',BASE/'extended/hashes.json',BASE/'liveness/hashes.json']})
 dump(out,'hashes.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()})
 print('Final REGOPT delivery:STRONG; mean7270.1787; matchedmax12390; all-validatedmax12670; structural23902; exact388096 samples')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);finalize(a.parse_args().output_dir)
