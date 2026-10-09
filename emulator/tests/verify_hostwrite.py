"""HOSTWRITE static reproducibility and preservation; no native CPU execution."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from ct_stock_load_audit import verify_inputs


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def verify(first,repeat,out,probe):
    out=out.resolve();base=(ROOT/'builds/phase19c-hostwrite').resolve()
    if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh confined checks required')
    files={p.name for p in first.iterdir() if p.is_file()};assert len(files)==19
    assert files=={p.name for p in repeat.iterdir() if p.is_file()}
    for n in files:assert (first/n).read_bytes()==(repeat/n).read_bytes(),n
    idx=json.loads((first/'hashes.json').read_text());assert set(idx)==files-{'hashes.json'}
    for n,h in idx.items():assert sha(first/n)==h,n
    def get(n):return json.loads((first/n).read_text())
    r=get('result.json');assert not r['target_bridge_recomputed'] and not r['active_parent_replay_justified']
    assert r['parent_DSP_instructions']==r['host_CPU_instructions']==0
    assert r['normal_host_can_produce_1E15']=='NOT-YET-DETERMINED'
    assert get('cache-semantics.json')['initialized_value']==0xffff
    assert all(x['classification']=='NOT-YET-DETERMINED' for x in get('requested-cell-classification.json'))
    assert len(get('requested-cell-classification.json'))==17
    for n,h in get('provenance.json')['inputs'].items():assert sha(ROOT/n)==h,n
    verify_inputs();out.mkdir(parents=True)
    unit=subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/test_hostwrite.py')],capture_output=True,text=True)
    assert unit.returncode==0,unit.stderr
    before=sha(first/'hashes.json')
    refusal=subprocess.run([sys.executable,'-B',str(ROOT/'tools/ct_hostwrite_audit.py'),
        '--output-dir',str(first),'--probe-dir',str(probe)],capture_output=True,text=True)
    assert refusal.returncode!=0 and sha(first/'hashes.json')==before
    subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
        '--results',str(ROOT/'builds/phase19a/validated/results.json'),
        '--output',str(out/'unchanged-core-audit.json')],capture_output=True,check=True)
    for n,h in json.loads((ROOT/'builds/phase19c-fullhelper/final/source-manifest.json').read_text()).items():assert sha(ROOT/n)==h,n
    report=dict(status='TESTED PASS',canonical_files_identical=len(files),unit_tests=10,overwrite_refused=True,
        cache_INITFFFF_verified=True,protected_inputs_extracts_and_sealed_core=True,previous_helper_unchanged=True,
        DSP_and_ARM_CPU_instructions=0,unit_test_output=unit.stderr,
        scope='Static codec/local protocol/conditional interval audit; complete normal effective host domains remainUNRESOLVED')
    with (out/'reproducibility.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    print('19 files identical;10 tests;overwrite refusal;firmware/extract/core/prior-helper guards PASS;0 CPU instructions')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['first','repeat','output-dir','probe-dir']:ap.add_argument('--'+n,required=True,type=Path)
    a=ap.parse_args();verify(a.first,a.repeat,a.output_dir,a.probe_dir)
