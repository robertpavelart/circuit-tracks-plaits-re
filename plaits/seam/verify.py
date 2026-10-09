"""Static byte/guard/refusal exports and protected-file checks; offline only."""
import argparse,json,subprocess,sys,hashlib,csv
from pathlib import Path
from contract import ROOT
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p):return json.loads(p.read_text())
def verify(out,suite,repeat):
 base=ROOT/'builds/phase20b-seam'
 if out.exists() or not out.resolve().is_relative_to(base):raise ValueError('Fresh checks required')
 for p in suite.rglob('*'):
  if p.is_file():assert p.read_bytes()==(repeat/p.relative_to(suite)).read_bytes(),p.name
 for name,h in obj(suite/'hashes.json').items():assert sha(suite/name)==h,name
 for name,h in obj(suite/'provenance.json').items():assert sha(ROOT/name)==h,name
 rows=list(csv.DictReader((suite/'seam-instructions.csv').open()))
 payload=(ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin').read_bytes()
 for r in rows:
  pc=int(r['P'],16);assert payload[3*pc:3*(pc+int(r['word_count']))].hex()==r['opcode_words']
 for root in [ROOT/'builds/phase20a-regopt/final',ROOT/'builds/phase20a-div/final-compact',ROOT/'builds/phase20a-plaits/final']:
  for name,h in obj(root/'implementation-provenance.json').items():assert sha(ROOT/name)==h,name
  for name,h in obj(root/'hashes.json').items():assert sha(root/name)==h,name
 sys.path.insert(0,str(ROOT/'tools'));from ct_stock_load_audit import verify_inputs
 verify_inputs()
 upstream=ROOT/'plaits/upstream'
 for r in obj(upstream/'source-manifest.json')['files']:assert sha(upstream/r['path'])==r['sha256']
 run=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/test_stock_seam.py')],capture_output=True)
 assert run.returncode==0,run.stderr.decode()
 refusal=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('audit.py')),'--output-dir',str(suite)],capture_output=True)
 assert refusal.returncode!=0 and b'Fresh Phase20B' in refusal.stderr
 out.mkdir(parents=True)
 (out/'tests.txt').write_bytes(run.stdout+run.stderr)
 result=dict(status='TESTED PASS STATIC/REFUSAL',unit_tests=11,numeric_fixture_values=47*4*32,
  numeric_fixture_qualified_stock=False,byte_verified_instructions=len(rows),reports_repeat_byte_identical=True,
  overwrite_refusal_pass=True,immutable_renderer_baselines_core_original_DSP_upstream=True,
  stock_CPU_created=False,stock_instructions_executed=0,stock_audio_trace=False,Plaits_fed_stock_trace=False,
  runtime_validation='REFUSED; unresolved concrete branch/address/mode/stack/guard state',hardware_access=False)
 (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
 paths=list((ROOT/'plaits/seam').glob('*.py'))+[ROOT/'emulator/tests/test_stock_seam.py']
 (out/'source-provenance.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in paths},indent=2)+'\n')
 (out/'hashes.json').write_text(json.dumps({p.name:sha(p) for p in out.iterdir() if p.is_file()},indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);a.add_argument('--suite-dir',type=Path,required=True);a.add_argument('--repeat-dir',type=Path,required=True)
 ns=a.parse_args();verify(ns.output_dir,ns.suite_dir,ns.repeat_dir)
