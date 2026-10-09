"""Compare two Phase 19B1 exports and test abort-before-load safety gates."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--exe',required=True,type=Path)
ap.add_argument('--first',required=True,type=Path);ap.add_argument('--repeat',required=True,type=Path)
ap.add_argument('--output-dir',required=True,type=Path);a=ap.parse_args()
out=a.output_dir.resolve()
if out.exists() or not out.is_relative_to((root/'builds/phase19b').resolve()):
    raise ValueError('Fresh output under builds/phase19b required')
out.mkdir(parents=True)
first=a.first.resolve();repeat=a.repeat.resolve()
f={p.name:p.read_bytes() for p in first.iterdir() if p.is_file()}
r={p.name:p.read_bytes() for p in repeat.iterdir() if p.is_file()}
assert f==r,'Load exports nondeterministic'
for name in ['execution-trace.jsonl','runtime-transactions.jsonl','runtime-watch.jsonl']:
    assert not f[name], 'Unexpected runtime activity'
assert json.loads(f['validation.json'])['stock_instructions']==0
payload=root/'firmware/dsp/build-4486/selection0-channel0.payload24.bin'
before=payload.read_bytes()
invalid=out/'synthetic-invalid-input.dat';invalid.write_bytes(b'\x12\x34\x56')
cases=[]
for name,input_path,dest,error in [
    ('identity-mismatch',invalid,out/'must-not-be-created','Stock identity mismatch'),
    ('existing-output',payload,first,'Fresh output directory'),
    ('output-outside-phase',payload,root/'notes/must-not-be-created','Fresh output directory')]:
    p=subprocess.run([str(a.exe.resolve()),str(input_path),str(dest)],capture_output=True,text=True)
    assert p.returncode==42 and error in p.stderr,(name,p)
    if dest!=first:assert not dest.exists()
    cases.append(dict(name=name,status='TESTED PASS',exit_code=p.returncode,stderr=p.stderr.strip(),stock_load=False))
assert payload.read_bytes()==before
assert f=={p.name:p.read_bytes() for p in first.iterdir() if p.is_file()}
report=dict(status='TESTED PASS',byte_identical_files=len(f),
    hashes={n:hashlib.sha256(b).hexdigest() for n,b in sorted(f.items())},
    negatives=cases,stock_instructions_executed=0,
    execution_determinism='NOT TESTED: execution gate closed; empty logs are not startup evidence',
    scope='Deterministic loading, decoding, implementation reset probe and gate reporting only')
with (out/'reproducibility.json').open('x',encoding='utf-8',newline='\n') as p:
    json.dump(report,p,indent=2,sort_keys=True);p.write('\n')
print(f'TESTED PASS: {len(f)} identical exports; three negative safety gates; no stock execution')
