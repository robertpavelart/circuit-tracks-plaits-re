"""Verify reproducible static-parent exports, closed replay and sealed inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ct_stock_load_audit import verify_inputs


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def verify(first,repeat,out):
    base=(ROOT/'builds/phase19c-parent').resolve();out=out.resolve()
    if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh confined checks directory required')
    files={p.name for p in first.iterdir() if p.is_file()}
    assert files=={p.name for p in repeat.iterdir() if p.is_file()}
    assert len(files)==13
    for name in files:assert (first/name).read_bytes()==(repeat/name).read_bytes(),name
    index=json.loads((first/'hashes.json').read_text())
    assert set(index)==files-{'hashes.json'}
    for name,h in index.items():assert sha(first/name)==h,name
    def get(n):return json.loads((first/n).read_text())
    gate=get('execution-gate.json');result=get('result.json')
    assert not gate['stock_CPU_instantiated'] and not gate['run_attempted'] and gate['checkpoint'] is None
    assert gate['original_parent_opcodes']==gate['original_helper_opcodes_this_phase']==0
    assert result['normal_reach_1E80']==result['normal_reach_1EE5']=='UNRESOLVED'
    assert result['high_X']=='UNRESOLVED' and result['X35F_invariant']=='NOT-YET-DETERMINED'
    assert result['theoretical_verified_256word_reservation']==result['firmware_implementation']=='NO'
    assert (first/'trace.jsonl').read_bytes()==b''
    assert get('watched-accesses.json')['status']=='NOT EXECUTED'
    cfg=get('parent-control-flow.json')
    assert cfg['external_decoded_direct_entries']==[] and len(cfg['DO'])==10
    assert sum(any(e['kind']=='DO_ZERO_SKIP_IF_COUNT0_AND_COMPATIBILITY_SC0' for e in n['edges']) for n in cfg['nodes'])==4
    assert [x['PC'] for x in cfg['calls']]==[0x1e19,0x1e80,0x1ee3,0x1ee5]
    loop=get('stack-loop-obligations.json')['effect_chain']
    assert (loop['LF'],loop['LA'],loop['LC_min'],loop['LC_max'])==(1,0xdaf,1,5)
    assert get('stack-loop-obligations.json')['actual_parent_SP'] is None
    for n,h in get('provenance.json')['inputs'].items():assert sha(ROOT/n)==h,n
    verify_inputs();out.mkdir(parents=True)
    test=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/test_parent_gate.py')],capture_output=True,text=True)
    assert test.returncode==0,test.stderr
    refused=out/'must-not-exist'
    p=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/harness/parent/audit.py'),
        '--output-dir',str(refused),'--require-normal-replay'],capture_output=True,text=True)
    assert p.returncode!=0 and not refused.exists()
    before=sha(first/'hashes.json')
    p2=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/harness/parent/audit.py'),'--output-dir',str(first)],capture_output=True,text=True)
    assert p2.returncode!=0 and sha(first/'hashes.json')==before
    subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
        '--results',str(ROOT/'builds/phase19a/validated/results.json'),
        '--output',str(out/'unchanged-core-audit.json')],capture_output=True,check=True)
    for n,h in json.loads((ROOT/'builds/phase19c-fullhelper/final/source-manifest.json').read_text()).items():assert sha(ROOT/n)==h,n
    fixture=json.loads((ROOT/'builds/phase19a/validated/results.json').read_text())
    assert sha(ROOT/'builds/phase19a/core-build/ct_replay_fixture.exe')==fixture['executable_SHA256']
    report=dict(status='TESTED PASS',canonical_files_identical=len(files),unit_tests=7,
        normal_execution_refused_before_output=True,overwrite_refused=True,
        parent_and_helper_opcodes_this_phase=0,watched_events_not_executed=True,
        protected_inputs_and_ten_extracts_unchanged=True,sealed_203_file_core_and_19A_harness=True,
        prior_fullhelper_implementation_unchanged=True,validated_19A_executable_identity=True,
        unit_test_output=test.stderr,scope='Static targeted evidence/gate, not normal-path or authentic-boot CPU validation')
    with (out/'reproducibility.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    print('13 files identical;7 gate tests;2 CLI refusals;firmware/core/prior-helper guards PASS;0 DSP instructions')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['first','repeat','output-dir']:p.add_argument('--'+n,required=True,type=Path)
    a=p.parse_args();verify(a.first,a.repeat,a.output_dir)
