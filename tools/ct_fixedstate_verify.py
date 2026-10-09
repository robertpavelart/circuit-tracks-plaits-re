"""Repeat/export/refusal and immutable-source verification for Phase20C2."""
import argparse,csv,json,subprocess,sys
from pathlib import Path
from ct_fixedstate_audit import ROOT,BASE,sha,dump


def verify(a,b,out):
    a=a.resolve();b=b.resolve();out=out.resolve()
    if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('fresh fixedstate checks child required')
    for p in [a,b]:
        if not p.is_relative_to(BASE) or not (p/'validation.json').is_file():raise ValueError('fixedstate reports required')
    files=sorted(p.relative_to(a) for p in a.rglob('*') if p.is_file())
    assert files==sorted(p.relative_to(b) for p in b.rglob('*') if p.is_file())
    assert all((a/p).read_bytes()==(b/p).read_bytes() for p in files)
    for rel in files:
        p=a/rel
        if p.suffix=='.json':json.loads(p.read_text(encoding='utf8'))
        if p.suffix=='.csv':
            with p.open(encoding='utf8',newline='') as f:rr=list(csv.DictReader(f))
            assert rr and all(None not in r for r in rr)
    v=json.loads((a/'validation.json').read_text())
    assert v['overall_result']=='REFUSED' and not v['offline_patch_construction_justified']
    assert all(sha(ROOT/p)==h for p,h in v['source_hashes'].items())
    result=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/test_fixedstate_ownership.py')],capture_output=True,text=True)
    if result.returncode:raise AssertionError(result.stdout+result.stderr)
    out.mkdir(parents=True)
    dump(out,'verification.json',dict(status='TESTED offline design/arithmetic only',tests=result.stdout+result.stderr,
        repeat_byte_identical=True,sources_unchanged=True,qualified_sets=0,CPU_execution=0,hardware_actions=0,
        files={p.as_posix():sha(a/p) for p in files}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--suite-dir',required=True,type=Path)
    p.add_argument('--repeat-dir',required=True,type=Path);p.add_argument('--output-dir',required=True,type=Path)
    x=p.parse_args();verify(x.suite_dir,x.repeat_dir,x.output_dir)
