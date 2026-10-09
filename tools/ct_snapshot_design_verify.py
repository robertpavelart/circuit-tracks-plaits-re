"""Verify design report reproducibility and source preservation; no importer/CPU."""
import argparse, json, sys, subprocess
from pathlib import Path
from ct_snapshot_design import ROOT,BASE,sha,dump
def verify(a,b,out):
    a=a.resolve();b=b.resolve();out=out.resolve()
    if out.exists() or out==BASE or not out.is_relative_to(BASE): raise ValueError('Fresh checks child required')
    files=sorted(p.relative_to(a) for p in a.rglob('*') if p.is_file())
    assert files==sorted(p.relative_to(b) for p in b.rglob('*') if p.is_file())
    assert all((a/p).read_bytes()==(b/p).read_bytes() for p in files)
    v=json.loads((a/'validation.json').read_text())
    assert all(sha(ROOT/p)==h for p,h in v['source_hashes'].items())
    tests=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/test_snapshot_design.py')],capture_output=True,text=True)
    if tests.returncode: raise AssertionError(tests.stdout+tests.stderr)
    out.mkdir(parents=True)
    dump(out,'verification.json',dict(status='TESTED design checks only',repeat_byte_identical=True,source_and_previous_reports_unchanged=True,
       tests=tests.stdout+tests.stderr,snapshot_acquired=False,CPU_execution=0,
       report_sha256={p.as_posix():sha(a/p) for p in files}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--suite-dir',required=True);p.add_argument('--repeat-dir',required=True);p.add_argument('--output-dir',required=True)
    x=p.parse_args();verify(Path(x.suite_dir),Path(x.repeat_dir),Path(x.output_dir))
