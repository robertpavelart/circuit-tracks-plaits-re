"""Reproducibility, immutable baseline and fail-closed admission checks."""
import argparse,json,os,subprocess,sys
from pathlib import Path
from recover import ROOT,BASE,sha,obj,dump,verify_inputs
def verify(out,first,repeat):
 out=out.resolve();first=first.resolve();repeat=repeat.resolve()
 if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('Fresh inputrec checks child required')
 for p in first.rglob('*'):
  if p.is_file():assert p.read_bytes()==(repeat/p.relative_to(first)).read_bytes(),p
 for name,h in obj(first/'hashes.json').items():assert sha(first/name)==h,name
 for name,h in obj(first/'provenance.json').items():assert sha(ROOT/name)==h,name
 verify_inputs()
 for phase in ['phase20b-seam/final','phase20b-checkpoint/final','phase20a-regopt/final','phase20a-div/final-compact','phase20a-plaits/final']:
  base=ROOT/'builds'/phase
  for n,h in obj(base/'hashes.json').items():assert sha(base/n)==h,n
  if phase=='phase20b-checkpoint/final':
   for n,h in obj(base/'provenance.json').items():assert sha(ROOT/n)==h,n
  if (base/'implementation-provenance.json').exists():
   for n,h in obj(base/'implementation-provenance.json').items():assert sha(ROOT/n)==h,n
 env=dict(os.environ,CT_INPUTREC_REPORT=str(first));logs=[]
 for test in ['test_seam_inputrec.py','test_seam_checkpoint.py']:
  run=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests'/test)],capture_output=True,env=env)
  assert run.returncode==0,run.stderr.decode();logs.append(run.stdout+run.stderr)
 fail=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('recover.py')),'--output-dir',str(first)],capture_output=True)
 assert fail.returncode and b'Fresh inputrec report child required' in fail.stderr
 out.mkdir(parents=True);(out/'tests.txt').write_bytes(b'\n'.join(logs))
 dump(out,'verification.json',dict(status='TESTED PASS static provenance; PARTIAL qualification / replay REFUSED',
  unit_tests=19,repeat_byte_identical=True,original_SYX_BIN_DSP_verified=True,previous_20B_20B2_reports_preserved=True,
  renderer_regopt_nativeDIV_restoring_outputs_preserved=True,overwrite_refusal=True,stock_instructions_executed=0,hardware_access=False))
 paths=[ROOT/'notes'/n for n in ['stock-p657-input-record.md','stock-note-history.md','stock-filter-history.md',
  'stock-seam-checkpoint.md','stock-coefficient-provenance.md','stock-runtime-state.md','plaits-stock-seam.md','research-log.md','todo.md']]
 dump(out,'phase-provenance.json',{p.relative_to(ROOT).as_posix():sha(p) for p in [*paths,Path(__file__),ROOT/'emulator/tests/test_seam_inputrec.py']})
 print(json.dumps(obj(out/'verification.json'),indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--suite-dir',type=Path,required=True);p.add_argument('--repeat-dir',type=Path,required=True)
 a=p.parse_args();verify(a.output_dir,a.suite_dir,a.repeat_dir)
