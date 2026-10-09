"""Final preservation, reproducibility and overwrite-refusal gates (offline)."""
import argparse,json,subprocess,hashlib
from domain import ROOT,sys
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p):return json.loads(p.read_text())
def check(out):
 base=ROOT/'builds/phase20a-bound'
 if out.exists() or not out.resolve().is_relative_to(base):raise ValueError('Fresh checks output required')
 a=base/'final';b=base/'repeat-export'
 for p in a.iterdir():assert p.read_bytes()==(b/p.name).read_bytes(),p.name
 for n,h in obj(a/'hashes.json').items():assert sha(a/n)==h,n
 for n,h in obj(a/'provenance.json').items():assert sha(ROOT/n)==h,n
 for r in [ROOT/'builds/phase20a-regopt/final',ROOT/'builds/phase20a-div/final-compact',ROOT/'builds/phase20a-plaits/final']:
  for n,h in obj(r/'implementation-provenance.json').items():assert sha(ROOT/n)==h,n
  for n,h in obj(r/'hashes.json').items():assert sha(r/n)==h,n
 upstream=ROOT/'plaits/upstream';source=obj(upstream/'source-manifest.json')
 for r in source['files']:assert sha(upstream/r['path'])==r['sha256'],r['path']
 sys.path.insert(0,str(ROOT/'tools'));from ct_stock_load_audit import verify_inputs
 verify_inputs()
 refusals=[]
 for name,args in [
  ('search',['--output-dir',str(base/'search')]),
  ('verify',['--output-dir',str(base/'verified-final'),'--search-dir',str(base/'fixtures')]),
  ('prove',['--output-dir',str(base/'proof-final')]),
  ('export',['--output-dir',str(base/'final')])]:
  run=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name(name+'.py')),*args],capture_output=True)
  assert run.returncode and b'Fresh' in run.stderr,name
  refusals.append(name)
 # All refusal checks returned before writes. Final reports still unchanged.
 for p in a.iterdir():assert p.read_bytes()==(b/p.name).read_bytes(),p.name
 out.mkdir(parents=True)
 result=dict(status='TESTED PASS',canonical_exports_repeat_byte_identical=True,overwrite_refusal_gates=refusals,
             immutable_renderer_native_restoring_core_original_guards=True,unchanged_upstream_source_files=len(source['files']),
             bound=13379,reachable=13335,physical_timing_claim=False,hardware_access=False)
 (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 paths=list((ROOT/'plaits/poc/bound').glob('*'))+[ROOT/'notes'/n for n in ['plaits-reachable-timing-bound.md','plaits-cycle-audit.md','plaits-register-optimization.md','plaits-resource-comparison.md','research-log.md','todo.md']]
 (out/'source-and-notes-provenance.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in paths if p.is_file()},indent=2)+'\n')
 (out/'phase-evidence-hashes.json').write_text(json.dumps({p.relative_to(base).as_posix():sha(p) for p in sorted(base.rglob('*')) if p.is_file() and not p.is_relative_to(out)},indent=2)+'\n')
 print(json.dumps(result,indent=2))
from pathlib import Path
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);check(a.parse_args().output_dir)
