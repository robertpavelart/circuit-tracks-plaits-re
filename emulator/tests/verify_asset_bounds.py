"""Static artifact reproducibility and protected-input/core checks; no CPU run."""
import argparse,csv,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from ct_stock_load_audit import verify_inputs
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(first,repeat,out,probe):
 out=out.resolve();base=(ROOT/'builds/phase19c-assetbound').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh checks child required')
 files={p.name for p in first.iterdir() if p.is_file()}
 assert files=={p.name for p in repeat.iterdir() if p.is_file()}
 for n in files:assert (first/n).read_bytes()==(repeat/n).read_bytes(),n
 hashes=json.loads((first/'hashes.json').read_text());assert set(hashes)==files-{'hashes.json'}
 for n,h in hashes.items():assert sha(first/n)==h
 for n,h in json.loads((first/'inputs.json').read_text()).items():assert sha(ROOT/n)==h,n
 def rows(n):return list(csv.DictReader((first/n).open(encoding='utf8',newline='')))
 assert len(rows('records.csv'))==64 and len(rows('address-progression.csv'))==64
 assert len(rows('effective-intervals.csv'))==128 and len(rows('requested-cell-intersections.csv'))==2048
 rs=rows('requested-cell-intersections.csv')
 assert sum(x['predicate_domain_result']=='INTERSECTION POSSIBLE' for x in rs)==62*16
 assert all(not x['actual_intersection'] for x in rs)
 r=json.loads((first/'result.json').read_text())
 assert r['CPU_instructions_executed']==0 and r['actual_record_lengths'] is None
 assert not r['parent_replay_admitted'] and not r['target_bridge_recomputed']
 verify_inputs()
 import ct_fw_tool
 syx=ROOT/'original/circuittracks-firmware-4486.syx';b=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
 assert ct_fw_tool.decode_syx(syx)['firmware']==b and ct_fw_tool.build_syx(syx,b)==syx.read_bytes()
 for x in json.loads((ROOT/'firmware/dsp/build-4486/manifest.json').read_text())['blocks']:
  for k in ['stream','payload']:assert sha(ROOT/'firmware/dsp/build-4486'/x[k+'_file'])==x[k+'_sha256']
 unit=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/test_asset_bounds.py')],capture_output=True,text=True)
 assert unit.returncode==0,unit.stderr
 before={n:sha(first/n) for n in files}
 refusal=subprocess.run([sys.executable,'-B',str(ROOT/'tools/ct_asset_bounds.py'),'--probe-dir',str(probe),
  '--output-dir',str(first)],capture_output=True,text=True)
 assert refusal.returncode and before=={n:sha(first/n) for n in files}
 out.mkdir(parents=True)
 subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
  '--results',str(ROOT/'builds/phase19a/validated/results.json'),'--output',str(out/'unchanged-core-audit.json')],
  capture_output=True,check=True)
 for n,h in json.loads((ROOT/'builds/phase19c-fullhelper/final/source-manifest.json').read_text()).items():assert sha(ROOT/n)==h,n
 report=dict(status='PASS',canonical_files_identical=len(files),unit_tests=9,overwrite_refused=True,
  record_rows=64,interval_rows=128,cell_tests=2048,predicate_possible_rows=992,
  original_hashes_roundtrip_extracts_sealed_core_previous_helper='PASS',CPU_instructions_executed=0,
  normal_asset_family_closed=False,unit_output=unit.stderr)
 with (out/'reproducibility.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['first','repeat','output-dir','probe-dir']:p.add_argument('--'+n,required=True,type=Path)
 a=p.parse_args();verify(a.first,a.repeat,a.output_dir,a.probe_dir)
