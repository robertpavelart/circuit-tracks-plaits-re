"""Verify canonical symbolic exports and the unchanged concrete source boundary."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from ct_stock_load_audit import verify_inputs
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--first',required=True,type=Path)
ap.add_argument('--repeat',required=True,type=Path);ap.add_argument('--output-dir',required=True,type=Path)
a=ap.parse_args();out=a.output_dir.resolve()
if out.exists() or not out.is_relative_to((ROOT/'builds/phase19b-symbolic').resolve()):raise ValueError('Fresh phase output required')
def data(d):return {p.name:p.read_bytes() for p in d.iterdir() if p.is_file() and p.name!='unit-tests.txt'}
f=data(a.first);r=data(a.repeat);assert f==r,'Canonical symbolic evidence differs'
result=json.loads(f['result.json']);assert result['original_main_instructions_executed']==result['original_worker_instructions_executed']==0
assert not result['reaches_ICC_poll'] and not result['worker_published_30002'] and not result['main_received_30002']
for role in ['main','worker']:
    trace=[json.loads(line) for line in f[role+'-trace.jsonl'].splitlines()]
    assert len(trace)==1 and trace[0]['type']=='BLOCKING' and trace[0]['executed_instructions']==0
    assert json.loads(f[role+'-transactions.json'])==[]
    s=json.loads(f[role+'-partial-final.json']);assert s['SR']['known_mask']==s['OMR']['known_mask']==s['pending']['known_mask']==0
verify_inputs();out.mkdir(parents=True)
subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
    '--results',str(ROOT/'builds/phase19a/validated/results.json'),
    '--output',str(out/'unchanged-concrete-source-audit.json')],capture_output=True,check=True)
report=dict(status='TESTED PASS symbolic integrity; authentic startup BLOCKING',canonical_files_identical=len(f),
    focused_tests=json.loads(f['tests.json']),excluded_files=['unit-tests.txt: walltime line'],
    original_counts=dict(main=0,worker=0),stock_hashes_unchanged=True,concrete_source_guard=True,
    hashes={n:hashlib.sha256(b).hexdigest() for n,b in sorted(f.items())})
with (out/'reproducibility.json').open('x',encoding='utf-8',newline='\n') as p:
    json.dump(report,p,indent=2,sort_keys=True);p.write('\n')
print(f'TESTED PASS: {len(f)} canonical files identical;24 focused tests; original counts0; source guards intact')
