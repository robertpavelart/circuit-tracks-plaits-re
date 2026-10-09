"""Reuse frozen timing rules; add documented six/24-bit immediate CMP forms."""
import argparse,json,sys
from pathlib import Path
from generate_opt import ROOT
sys.path.insert(0,str(ROOT/'plaits/poc/timing'))
import audit
original_classify=audit.classify
def classify(pc,s,size):
 r=original_classify(pc,s,size)
 if s.startswith('cmp #'):
  r['base']=2 if s.startswith('cmp #>') else 1
  r['source']='FM A-3 CMP immediate;13-45 unsigned6-bit zero extension or signed24'
 return r
def timing(suite,out):
 out=out.resolve();base=ROOT/'builds/phase20a-regopt'
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh REGOPT timing output required')
 for n,h in audit.obj(suite/'hashes.json').items():assert audit.sha(suite/n)==h,n
 out.mkdir(parents=True);audit.classify=classify
 result=audit.suite_counts(suite,out);audit.dump(out,'cycle-summary.json',result)
 audit.dump(out,'timing-assumptions.json',dict(original_model='builds/phase20a-timing/final/timing-assumptions.json',original_model_sha256=audit.sha(ROOT/'plaits/poc/timing/audit.py'),
  change='Documented CMP immediate nominal1/2; remaining rules unchanged',free_AGU_register_data='R1..7/N0..7 data registers only, never addressing; R0 postincrement ignores N0; M remainslinear',
  memory='private/internal/zero-wait; no IRQ/DMA; short-store ambiguity retained',native_helper_unchanged=True,
  extra_AGU_stalls=0,unconditional_Circuit_cycle_bound=None,source_sha256=audit.sha(Path(__file__))))
 audit.dump(out,'hashes.json',{p.name:audit.sha(p) for p in sorted(out.iterdir()) if p.is_file()})
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--suite-dir',type=Path,required=True);a.add_argument('--output-dir',type=Path,required=True)
 ns=a.parse_args();timing(ns.suite_dir.resolve(),ns.output_dir)
