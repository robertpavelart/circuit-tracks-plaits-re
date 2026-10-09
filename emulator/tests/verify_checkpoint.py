"""Deterministic checkpoint evidence, native negative gates, and sealed19A audit."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ct_stock_load_audit import verify_inputs

def run(first,repeat,out,exe):
    out=out.resolve()
    if out.exists() or not out.is_relative_to((ROOT/'builds/phase19c-checkpoint').resolve()):raise ValueError('Fresh phase checks required')
    def data(d):return {p.name:p.read_bytes() for p in d.iterdir() if p.is_file()}
    a,b=data(first),data(repeat);assert a==b,'Nondeterministic checkpoint evidence'
    index=json.loads(a['hashes.json']);assert set(index)==set(a)-{'hashes.json'}
    for name,h in index.items():assert hashlib.sha256(a[name]).hexdigest()==h
    result=json.loads(a['result.json']);assert all(result['validation'].values())
    assert result['total_original_opcode_executions']==24656 and result['cursor_stores']==4096
    verify_inputs();out.mkdir(parents=True)
    subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/test_checkpoint_state.py'),'-v'],capture_output=True,check=True)
    subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
        '--results',str(ROOT/'builds/phase19a/validated/results.json'),
        '--output',str(out/'unchanged-core-audit.json')],capture_output=True,check=True)
    stock=ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin'
    tests=[]
    def reject(label,image,cases,trace):
        p=subprocess.run([str(exe),str(image),str(cases),str(trace)],capture_output=True,text=True)
        assert p.returncode!=0,label
        tests.append(dict(name=label,returncode=p.returncode,reason=p.stderr.strip()))
    bad=out/'unrelated-three-byte-input.bin';bad.write_bytes(b'\0\0\0')
    reject('Wrong image identity',bad,first/'cases.tsv',out/'wrong-image.jsonl')
    assert not (out/'wrong-image.jsonl').exists()
    before=hashlib.sha256((first/'trace.jsonl').read_bytes()).hexdigest()
    reject('Refuse overwrite',stock,first/'cases.tsv',first/'trace.jsonl')
    assert hashlib.sha256((first/'trace.jsonl').read_bytes()).hexdigest()==before
    for name,line in [('Out-of-domain cursor index','0 0 0 16 0 65535 0\n'),('Unqualified modifier','0 0 0 0 0 1 0\n'),('Unsupported full-helper control state','0 4 0 0 0 65535 0\n')]:
        p=out/(name.replace(' ','-')+'.tsv');p.write_text(line,encoding='ascii')
        trace=p.with_suffix('.jsonl');reject(name,stock,p,trace)
        assert trace.read_bytes()==b''
    report=dict(status='TESTED PASS',canonical_files_identical=len(a),checkpoint_schema_tests=6,negative_gates=tests,
        original_opcode_executions_per_invocation=24656,isolated_cursor_store_body_opcodes=24576,
        real_boot_instructions=0,full_helper_loop_executions=0,positive_count_consumer_loops=0,
        firmware_hashes_unchanged=True,sealed_core_guard=True,
        scope='Address-only symbolic checkpoint projections; no authentic full boot or universal persistence claim')
    with (out/'reproducibility.json').open('x',encoding='utf-8',newline='\n') as f:
        json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    print(f'{len(a)} canonical files identical;6 schema tests;5 refusal gates;sealed core/input hashes PASS')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['first','repeat','output-dir']:ap.add_argument('--'+n,required=True,type=Path)
    ap.add_argument('--exe',type=Path,default=ROOT/'builds/phase19c-checkpoint/core-build/ct_checkpoint.exe')
    a=ap.parse_args();run(a.first,a.repeat,a.output_dir,a.exe.resolve())
