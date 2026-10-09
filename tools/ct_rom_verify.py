"""Verify Phase19B-ROM reproducibility, unknown-state integrity and source guards."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from ct_stock_load_audit import verify_inputs
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--first',required=True,type=Path)
ap.add_argument('--repeat',required=True,type=Path);ap.add_argument('--output-dir',required=True,type=Path)
a=ap.parse_args();out=a.output_dir.resolve()
if out.exists() or not out.is_relative_to((ROOT/'builds/phase19b-rom').resolve()):raise ValueError('Fresh phase output required')
f={p.name:p.read_bytes() for p in a.first.iterdir() if p.is_file()}
r={p.name:p.read_bytes() for p in a.repeat.iterdir() if p.is_file()}
assert f==r,'Static comparison differs'
for name in ['main-handoff.json','worker-handoff.json']:
    m=json.loads(f[name]);assert m['execution_allowed'] is False and m['instruction_limit']==0
    for field in m['fields']:
        assert field['provenance']
        if field['set_explicitly']:assert field['field']=='PC' and field['value']==0
        else:assert field['value'] is None
    assert m['explicit_assignments']==[dict(field='PC',value=0,provenance='Verified boot header + documented start-address contract')]
assert json.loads(f['source-catalog.json'])['recovered_ROM_sources']==[]
g=json.loads(f['execution-gates.json']);assert not g['first_execution_justified'] and not g['resume19B2']
assert g['original_main_instructions_executed']==g['original_worker_instructions_executed']==0
verify_inputs()
out.mkdir(parents=True)
subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
    '--results',str(ROOT/'builds/phase19a/validated/results.json'),
    '--output',str(out/'unchanged-core-audit.json')],capture_output=True,check=True)
report=dict(status='TESTED PASS static integrity; ROM/first-execution BLOCKED',byte_identical_reports=len(f),
    both_manifests_no_guessed_state=True,original_instructions_executed=0,
    original_SYX_BIN_hashes_unchanged=True,source_guard_unchanged=True,
    report_SHA256={n:hashlib.sha256(b).hexdigest() for n,b in sorted(f.items())})
with (out/'reproducibility.json').open('x',encoding='utf-8',newline='\n') as p:
    json.dump(report,p,indent=2,sort_keys=True);p.write('\n')
print(f'TESTED PASS: {len(f)} identical reports; unknown-state manifests intact; firmware/core hashes preserved')
