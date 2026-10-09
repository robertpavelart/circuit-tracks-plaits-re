"""Compare two fresh IRQ audit exports; verify sealed inputs/core and fail-closed gate."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from ct_stock_load_audit import verify_inputs

ROOT=Path(__file__).resolve().parents[1]

def run(first,repeat,out):
    out=out.resolve()
    if out.exists() or not out.is_relative_to((ROOT/'builds/phase19b-irq').resolve()):
        raise ValueError('Fresh phase19b-irq check output required')
    def read(d):return {p.name:p.read_bytes() for p in d.iterdir() if p.is_file()}
    a,b=read(first),read(repeat)
    assert a==b, 'Canonical reports differ'
    for d in [first,repeat]:
        index=json.loads((d/'hashes.json').read_text())
        assert set(index)==set(a)-{'hashes.json'}
        for name,expected in index.items():
            assert hashlib.sha256((d/name).read_bytes()).hexdigest()==expected
    gate=json.loads(a['gate.json'])
    assert gate['original_main_instructions']==gate['original_worker_instructions']==0
    assert gate['interrupt_contract']=='UNRESOLVED' and not gate['execution_authorized_by_gate']
    traces=json.loads(a['blocked-original-attempts.json'])
    for role,t in traces.items():
        assert t['transactions']==[] and len(t['trace'])==1 and t['trace'][0]['type']=='BLOCKING'
        assert t['trace'][0]['executed_instructions']==0
    assert all(c['actual_feasibility'].startswith('UNRESOLVED') for c in json.loads(a['conditional-classes.json']))
    verify_inputs()
    tests=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/test_partial_state.py'),'-v'],capture_output=True,text=True,check=True)
    assert 'Ran 24 tests' in tests.stderr and 'OK' in tests.stderr
    out.mkdir(parents=True)
    subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
        '--results',str(ROOT/'builds/phase19a/validated/results.json'),
        '--output',str(out/'unchanged-concrete-source-audit.json')],capture_output=True,check=True)
    report=dict(status='TESTED PASS',canonical_files_identical=len(a),partial_state_tests=24,
        static_predicate_cases=16,original_main=0,original_worker=0,
        firmware_unchanged=True,sealed_concrete_core_guard=True,
        scope='Evidence integrity and symbolic predicates; no successful authentic interrupt delivery/startup',
        hashes={n:hashlib.sha256(data).hexdigest() for n,data in sorted(a.items())})
    with (out/'reproducibility.json').open('x',encoding='utf-8',newline='\n') as f:
        json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    print(f'{len(a)} canonical files identical;24 partial tests;16 static predicate cases; zero original execution; guards PASS')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--first',required=True,type=Path);ap.add_argument('--repeat',required=True,type=Path)
    ap.add_argument('--output-dir',required=True,type=Path)
    a=ap.parse_args();run(a.first,a.repeat,a.output_dir)
