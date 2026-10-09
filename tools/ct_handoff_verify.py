"""Reproduce static handoff comparison and test refusal of guessed state."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--first',required=True,type=Path)
ap.add_argument('--repeat',required=True,type=Path);ap.add_argument('--output-dir',required=True,type=Path)
a=ap.parse_args();out=a.output_dir.resolve()
if out.exists() or not out.is_relative_to((ROOT/'builds/phase19b-handoff').resolve()):
    raise ValueError('Fresh output under builds/phase19b-handoff required')
out.mkdir(parents=True)
first={p.name:p.read_bytes() for p in a.first.iterdir() if p.is_file()}
repeat={p.name:p.read_bytes() for p in a.repeat.iterdir() if p.is_file()}
assert first==repeat,'Static reports differ'
s=importlib.util.spec_from_file_location('handoff_gate',ROOT/'emulator/stock/handoff_gate.py')
module=importlib.util.module_from_spec(s);s.loader.exec_module(module)
manifest=json.loads(first['handoff-manifest.json']);positive=module.inspect(manifest)
assert positive['status']=='BLOCKED' and not positive['CPU_constructed']
negatives=[]
for name,field,value in [('guessed-SR','SR',0),('reset-as-GPIO-handoff','Y:PCRG',0x1e1),
                         ('preseed-worker-pointer','Y:ICDR4',0x30002)]:
    m=copy.deepcopy(manifest);next(f for f in m['fields'] if f['field']==field)['value']=value
    try:module.inspect(m)
    except ValueError as e:negatives.append(dict(test=name,status='TESTED PASS',reason=str(e)))
    else:raise AssertionError(name)
m=copy.deepcopy(manifest);m['execution_allowed']=True
try:module.inspect(m)
except ValueError as e:negatives.append(dict(test='force-execution-enable',status='TESTED PASS',reason=str(e)))
else:raise AssertionError('Execution enable accepted')
extracted=ROOT/'firmware/dsp/build-4486';mm=json.loads((extracted/'manifest.json').read_text())
hashes={}
for b in mm['blocks']:
    for key,hkey in [('stream_file','stream_sha256'),('payload_file','payload_sha256')]:
        h=hashlib.sha256((extracted/b[key]).read_bytes()).hexdigest()
        assert h==b[hkey];hashes[b[key]]=h
subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
    '--results',str(ROOT/'builds/phase19a/validated/results.json'),
    '--output',str(out/'unchanged-19a-source-audit.json')],check=True,capture_output=True)
result=dict(status='TESTED PASS',identical_static_reports=len(first),gate=positive,negative_tests=negatives,
            all_ten_extracted_hashes_unchanged=hashes,stock_worker_bootstrap_instructions_executed=0,
            script_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            gate_SHA256=hashlib.sha256((ROOT/'emulator/stock/handoff_gate.py').read_bytes()).hexdigest(),
            report_hashes={name:hashlib.sha256(b).hexdigest() for name,b in sorted(first.items())})
with (out/'reproducibility.json').open('x',encoding='utf-8',newline='\n') as f:
    json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
print(f'TESTED PASS: {len(first)} identical static reports, four guessed-state refusals, unchanged firmware/core hashes')
