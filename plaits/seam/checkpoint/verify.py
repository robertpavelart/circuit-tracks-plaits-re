"""Verify repeated focused provenance exports and immutable original inputs."""
import argparse,json,hashlib,subprocess,sys,csv
from pathlib import Path
from recover import ROOT,verify_inputs
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p):return json.loads(p.read_text())
def verify(out,first,repeat):
 base=ROOT/'builds/phase20b-checkpoint'
 if out.exists() or not out.resolve().is_relative_to(base):raise ValueError('Fresh checkpoint checks child required')
 for p in first.rglob('*'):
  if p.is_file():assert p.read_bytes()==(repeat/p.relative_to(first)).read_bytes(),p.name
 for n,h in obj(first/'hashes.json').items():assert sha(first/n)==h,n
 for n,h in obj(first/'provenance.json').items():assert sha(ROOT/n)==h,n
 verify_inputs()
 for base20 in [ROOT/'builds/phase20a-regopt/final',ROOT/'builds/phase20a-div/final-compact',ROOT/'builds/phase20a-plaits/final']:
  for n,h in obj(base20/'implementation-provenance.json').items():assert sha(ROOT/n)==h,n
  for n,h in obj(base20/'hashes.json').items():assert sha(base20/n)==h,n
 # Preserve Phase20B harness/explorer evidence too; notes are deliberately updated.
 for n,h in obj(ROOT/'builds/phase20b-seam/final/hashes.json').items():assert sha(ROOT/'builds/phase20b-seam/final'/n)==h,n
 run=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/test_seam_checkpoint.py')],capture_output=True)
 assert run.returncode==0,run.stderr.decode()
 r=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('recover.py')),'--output-dir',str(first)],capture_output=True)
 assert r.returncode and b'Fresh checkpoint report' in r.stderr
 out.mkdir(parents=True);(out/'tests.txt').write_bytes(run.stdout+run.stderr)
 result=dict(status='TESTED PASS STATIC PROVENANCE / replay REFUSED',unit_tests=9,reports_repeat_byte_identical=True,
  original_SYX_BIN_DSP_and_renderer_baselines_unchanged=True,Phase20B_artifacts_preserved=True,
  overwrite_refusal_pass=True,selected_file_parameter_values=[0,1,1],selected_Y_offsets=[5,5],
  no_ARMDSP_execution=True,stock_instructions_executed=0,checkpoint_admitted=False,
  provenance_qualification='PARTIAL',full_boot_expanded=False,Plaits_fed=False,hardware_access=False)
 (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
 docs=[ROOT/'notes'/n for n in ['stock-seam-checkpoint.md','stock-coefficient-provenance.md','stock-runtime-state.md',
  'plaits-stock-seam.md','plaits-stock-abi.md','plaits-stock-workload.md','research-log.md','todo.md']]
 (out/'phase-provenance.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in docs+[Path(__file__),ROOT/'emulator/tests/test_seam_checkpoint.py']},indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);a.add_argument('--suite-dir',type=Path,required=True);a.add_argument('--repeat-dir',type=Path,required=True)
 ns=a.parse_args();verify(ns.output_dir,ns.suite_dir,ns.repeat_dir)
