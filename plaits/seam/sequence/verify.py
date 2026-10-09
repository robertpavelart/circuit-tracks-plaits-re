"""Compare deterministic static exports and protect source/previous artifacts."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
from recover import ROOT, BASE, dump, sha
def verify(a,b,out):
    a=a.resolve();b=b.resolve();out=out.resolve()
    if out.exists() or out==BASE or not out.is_relative_to(BASE): raise ValueError('Fresh checks child required')
    files=sorted(p.name for p in a.iterdir() if p.is_file())
    assert files==sorted(p.name for p in b.iterdir() if p.is_file())
    assert all((a/f).read_bytes()==(b/f).read_bytes() for f in files)
    v=json.loads((a/'validation.json').read_text()); q=json.loads((a/'qualification.json').read_text())
    for relative,h in (v['input_hashes']|v['previous_report_hashes']).items(): assert sha(ROOT/relative)==h
    for e in v['evidence']: assert sha(ROOT/e['path'])==e['sha256']
    assert not q['event_admitted'] and not q['checkpoint_resume'] and q['original_instructions_executed']==0
    assert q['static_strategy']=='EXHAUSTED'
    tests=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/test_sequence_context.py')],capture_output=True,text=True)
    if tests.returncode: raise AssertionError(tests.stdout+tests.stderr)
    out.mkdir(parents=True)
    dump(out,'verification.json',dict(status='TESTED',repeat_byte_identical=True,inputs_and_previous_reports_preserved=True,
        original_instructions_executed=0,qualification_fail_closed=True,tests=tests.stdout+tests.stderr,
        report_sha256={f:sha(a/f) for f in files}))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--suite-dir',required=True);p.add_argument('--repeat-dir',required=True);p.add_argument('--output-dir',required=True)
    x=p.parse_args();verify(Path(x.suite_dir),Path(x.repeat_dir),Path(x.output_dir))
