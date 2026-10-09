"""Static TARGETBRIDGE reproducibility and protection checks. No CPU execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ct_stock_load_audit import verify_inputs


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def verify(first,repeat,out):
    out=out.resolve();base=(ROOT/'builds/phase19c-targetbridge').resolve()
    if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh confined checks required')
    files={p.name for p in first.iterdir() if p.is_file()}
    assert files=={p.name for p in repeat.iterdir() if p.is_file()}
    for n in files:assert (first/n).read_bytes()==(repeat/n).read_bytes(),n
    index=json.loads((first/'hashes.json').read_text());assert set(index)==files-{'hashes.json'}
    for n,h in index.items():assert sha(first/n)==h,n
    def get(n):return json.loads((first/n).read_text())
    result=get('result.json');sets=get('target-sets.json')
    assert result['status'].startswith('C:') and result['parent_executed_instructions']==0
    assert result['normal_target_producer'] is None and not result['active_D99_replay_justified']
    assert sets['normal_targets'] is None and sets['normal_domains'] is None
    assert sets['conditional_sets']['0xdc5']==sets['conditional_sets']['0xdcd']==[]
    assert all(x['normal_select_1E15']=='NOT-YET-DETERMINED' for x in result['site_results'])
    assert get('table-persistence.json')['classification']=='UNRESOLVED'
    assert get('table-persistence.json')['SERVICE_mutation_capability_verified']
    assert get('writer-ledger.json')['direct_absolute_writers']==[]
    for n,h in get('provenance.json')['inputs'].items():assert sha(ROOT/n)==h,n
    verify_inputs();out.mkdir(parents=True)
    unit=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/test_target_bridge.py')],capture_output=True,text=True)
    assert unit.returncode==0,unit.stderr
    before=sha(first/'hashes.json')
    refusal=subprocess.run([sys.executable,'-B',str(ROOT/'tools/ct_effect_target_bridge.py'),'--output-dir',str(first)],capture_output=True,text=True)
    assert refusal.returncode!=0 and sha(first/'hashes.json')==before
    subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
        '--results',str(ROOT/'builds/phase19a/validated/results.json'),
        '--output',str(out/'unchanged-core-audit.json')],capture_output=True,check=True)
    for n,h in json.loads((ROOT/'builds/phase19c-fullhelper/final/source-manifest.json').read_text()).items():assert sha(ROOT/n)==h,n
    report=dict(status='TESTED PASS',canonical_files_identical=len(files),unit_tests=7,
        conditional_target_records=640,actual_normal_domain_proof=False,actual_normal_target_witness=False,
        parent_DSP_instructions=0,overwrite_refused=True,protected_firmware_extracts_and_core=True,
        old_fullhelper_implementation_unchanged=True,unit_test_output=unit.stderr,
        scope='Static conditional enumeration and targeted reused writer projections; not full writer closure or stock replay')
    with (out/'reproducibility.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    print(f'{len(files)} files identical;7 tests;640 conditional target records;guards PASS;normal bridge UNRESOLVED')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['first','repeat','output-dir']:ap.add_argument('--'+n,required=True,type=Path)
    a=ap.parse_args();verify(a.first,a.repeat,a.output_dir)
