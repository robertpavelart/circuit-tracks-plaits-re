"""Seal repeated P-state evidence, unchanged inputs and six contract tests."""
import argparse, json, subprocess, sys
from pathlib import Path
from ct_pstate_prepare import ROOT, fresh, sha, write

def check(final,repeat,source,out):
    out=fresh(out)
    names=[]
    ff=json.loads((final/'hashes.json').read_text());rf=json.loads((repeat/'hashes.json').read_text())
    assert set(ff)==set(rf)
    for n,h in ff.items():
        assert sha(final/n)==h==rf[n]==sha(repeat/n),n
        names.append(n)
    guards=json.loads((source/'input-guards.json').read_text())
    for n,h in guards.items():assert sha(ROOT/n)==h,n
    protected={
        'original/circuittracks-firmware-4486.syx':'bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd',
        'firmware/circuittracks-firmware-4486.bin':'b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da',
        'firmware/dsp/build-4486/selection0-channel0.payload24.bin':'b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855'}
    for n,h in protected.items():assert sha(ROOT/n)==h
    test=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','emulator/tests','-p','test_pstate_contract.py','-v'],
        cwd=ROOT,capture_output=True,text=True)
    write(out/'contract-tests.txt',test.stdout+test.stderr)
    assert test.returncode==0 and 'Ran 6 tests' in test.stderr
    r=json.loads((final/'qualification.json').read_text())
    assert r['all_seven_states_exact'] and r['all_samples_vs_X_exact']
    assert r['owned_stock_P_words']==0 and not r['firmware_integration_ready']
    verdict=dict(status='TESTED PASS evidence/repeat/source guards; Circuit allocation REFUSED',
        repeated_reports_byte_identical=names,guarded_inputs_unchanged=len(guards),
        baseline_hashes=protected,contract_tests=6,hardware_actions=0,
        storage_verdict=r['overall'],physical_cycle_measurement=False,
        check_script_sha256=sha(Path(__file__)))
    write(out/'verification.json',json.dumps(verdict,indent=2,sort_keys=True)+'\n')
    write(out/'hashes.json',json.dumps({p.name:sha(p) for p in out.iterdir() if p.is_file()},indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:verdict[k] for k in ['status','guarded_inputs_unchanged','contract_tests','storage_verdict']},indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser()
    for n in ['final','repeat','source','out']:a.add_argument('--'+n,type=Path,required=True)
    check(**{k:v.resolve() for k,v in vars(a.parse_args()).items()})
