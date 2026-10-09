"""Full-helper reproducibility, prior differential gates, and fail-closed classes."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ct_stock_load_audit import verify_inputs
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def run(first,repeat,out,exe):
    out=out.resolve()
    if out.exists() or not out.is_relative_to((ROOT/'builds/phase19c-fullhelper').resolve()):raise ValueError('Fresh fullhelper checks required')
    files={p.name for p in first.iterdir() if p.is_file()};assert files=={p.name for p in repeat.iterdir() if p.is_file()}
    for name in files:
        with (first/name).open('rb') as a,(repeat/name).open('rb') as b:
            while True:
                aa=a.read(1<<20);bb=b.read(1<<20);assert aa==bb,name
                if not aa:break
    idx=json.loads((first/'hashes.json').read_text());assert set(idx)==files-{'hashes.json'}
    for name,h in idx.items():assert sha(first/name)==h
    r=json.loads((first/'result.json').read_text());assert r['cases']==40 and r['original_opcodes']==385880
    reports=json.loads((first/'run-reports.json').read_text());assert len(reports)==40
    for e in reports:
        assert e['differential_match'] and e['stack_and_loops_restored']
        assert e['body_writes']==512 and e['calls']==e['returns']==33 and e['DO_executions']==66
    assert json.loads((first/'watched-accesses.json').read_text())==[]
    finals=json.loads((first/'final-states.json').read_text());assert len(finals)==40
    for v in finals.values():assert v['CPU']['LF']==v['CPU']['FV']==0 and v['CPU']['SP']==v['CPU']['SC']
    verify_inputs();out.mkdir(parents=True)
    subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),'--results',str(ROOT/'builds/phase19a/validated/results.json'),
        '--output',str(out/'unchanged-core-audit.json')],capture_output=True,check=True)
    fixture=json.loads((ROOT/'builds/phase19a/validated/results.json').read_text())
    assert sha(ROOT/'builds/phase19a/core-build/ct_replay_fixture.exe')==fixture['executable_SHA256']
    tests=[];stock=ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin'
    def reject(name,image,cases,trace):
        p=subprocess.run([str(exe),str(image),str(cases),str(trace)],capture_output=True,text=True)
        assert p.returncode!=0,name
        tests.append(dict(name=name,returncode=p.returncode,reason=p.stderr.strip()))
    wrong=out/'unrelated-three-byte-input.bin';wrong.write_bytes(b'\0\0\0')
    reject('Wrong original identity',wrong,first/'cases.tsv',out/'wrong-image.jsonl');assert not (out/'wrong-image.jsonl').exists()
    before=sha(first/'trace.jsonl');reject('Overwrite refusal',stock,first/'cases.tsv',first/'trace.jsonl');assert sha(first/'trace.jsonl')==before
    negatives=[('Stack budget high','0 0 8 0 65535 0'),('Stack extension low','0 0 2 0 65535 0'),
        ('Active inherited loop unknown','0 0 3 0 65535 1'),('Unsupported descriptor','0 2 3 0 65535 0'),('Unqualified modifier','0 0 3 0 1 0')]
    for name,line in negatives:
        path=out/(name.replace(' ','-')+'.tsv');path.write_text(line+'\n',encoding='ascii');trace=path.with_suffix('.jsonl')
        reject(name,stock,path,trace);assert trace.read_bytes()==b''
    report=dict(status='TESTED PASS',canonical_files_identical=len(files),complete_helper_runs=40,
        original_opcodes_per_invocation=385880,per_run=9647,caller_JSR_per_run=1,
        body_stores_per_run=512,callee_calls_and_returns=32,DO_executions_per_run=66,
        differential_address_order_LC_stack_and_final_state=True,negative_gates=tests,
        original_firmware_unchanged=True,sealed203_file_core_guard=True,validated19A_binary_identity=True,
        scope='BOUNDED structural resident-stack/inactive-loop class; no authentic boot or normal ownership proof')
    with (out/'reproducibility.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    print(f'{len(files)} canonical files identical;40 complete-helper runs;7 refusal gates;core/firmware guards PASS')
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['first','repeat','output-dir']:ap.add_argument('--'+n,required=True,type=Path)
    ap.add_argument('--exe',type=Path,default=ROOT/'builds/phase19c-fullhelper/core-build/ct_fullhelper.exe')
    a=ap.parse_args();run(a.first,a.repeat,a.output_dir,a.exe.resolve())
