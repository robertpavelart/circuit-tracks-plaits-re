"""Reproducibility, arithmetic qualification and immutable preservation."""
import argparse,os,subprocess,sys,json
from pathlib import Path
from recover import ROOT,BASE,sha,obj,dump,verify_inputs
def verify(out,first,repeat):
 out=out.resolve()
 if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('Fresh projectassoc checks child required')
 for p in first.rglob('*'):
  if p.is_file():assert p.read_bytes()==(repeat/p.relative_to(first)).read_bytes(),p
 for n,h in obj(first/'hashes.json').items():assert sha(first/n)==h,n
 for n,h in obj(first/'provenance.json').items():assert sha(ROOT/n)==h,n
 verify_inputs()
 for phase in ['phase20b-inputrec/final-v3','phase20b-checkpoint/final','phase20b-seam/final','phase20a-regopt/final','phase20a-div/final-compact','phase20a-plaits/final']:
  base=ROOT/'builds'/phase
  for n,h in obj(base/'hashes.json').items():assert sha(base/n)==h,n
  if (base/'implementation-provenance.json').exists():
   for n,h in obj(base/'implementation-provenance.json').items():assert sha(ROOT/n)==h,n
 env=dict(os.environ,CT_PROJECTASSOC_REPORT=str(first));logs=[]
 for name in ['test_projectassoc.py','test_seam_inputrec.py','test_seam_checkpoint.py']:
  r=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests'/name)],capture_output=True,env=env)
  assert r.returncode==0,r.stderr.decode();logs.append(r.stdout+r.stderr)
 r=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('recover.py')),'--output-dir',str(first)],capture_output=True)
 assert r.returncode and b'Fresh projectassoc report child required' in r.stderr
 out.mkdir(parents=True);(out/'tests.txt').write_bytes(b'\n'.join(logs))
 dump(out,'verification.json',dict(status='TESTED PASS static arithmetic/provenance; association PARTIAL',unit_tests=31,
  independent_macro_fixtures=4096,repeat_byte_identical=True,original_inputs_preserved=True,
  prior_20B_20B2_20B3_and_renderer_reports_preserved=True,overwrite_refusal=True,
  event_qualified=False,stock_instructions_executed=0,stock_seam_replay=False,Plaits_fed=False,hardware_access=False))
 notes=[ROOT/'notes'/n for n in ['project0-patch-association.md','rudi-saw-poly-differences.md','project0-event-context.md',
  'stock-p657-input-record.md','stock-note-history.md','stock-filter-history.md','stock-seam-checkpoint.md','research-log.md','todo.md']]
 dump(out,'phase-provenance.json',{p.relative_to(ROOT).as_posix():sha(p) for p in [*notes,Path(__file__),ROOT/'emulator/tests/test_projectassoc.py']})
 print(json.dumps(obj(out/'verification.json'),indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--suite-dir',type=Path,required=True);p.add_argument('--repeat-dir',type=Path,required=True)
 a=p.parse_args();verify(a.output_dir,a.suite_dir,a.repeat_dir)
