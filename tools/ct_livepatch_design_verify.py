"""Repeat and immutable-source checks for offline Phase20C design reports."""
import argparse,json,subprocess,sys,csv
from pathlib import Path
from ct_livepatch_design import ROOT,BASE,dump,sha


def verify(a,b,out):
    a=a.resolve();b=b.resolve();out=out.resolve()
    if out.exists() or out==BASE or not out.is_relative_to(BASE):raise ValueError('fresh checks child required')
    for p in [a,b]:
        if not p.is_relative_to(BASE) or not (p/'validation.json').is_file():raise ValueError('report inputs required')
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
    assert all(sha(ROOT/p)==h for p,h in v['source_hashes'].items())
    result=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/test_livepatch_design.py')],text=True,capture_output=True)
    if result.returncode:raise AssertionError(result.stdout+result.stderr)
    out.mkdir(parents=True)
    dump(out,'verification.json',dict(status='TESTED design and byte guards only',tests=result.stdout+result.stderr,
        byte_identical_repeat=True,source_guard_unchanged=True,CPU_execution=0,patch_or_flash_image_emitted=False,
        files={p.as_posix():sha(a/p) for p in files}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--suite-dir',type=Path,required=True)
    p.add_argument('--repeat-dir',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    x=p.parse_args();verify(x.suite_dir,x.repeat_dir,x.output_dir)
