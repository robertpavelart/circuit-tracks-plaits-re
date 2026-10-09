"""Seal repeated architecture reports and guarded evidence; no DSP execution."""
import argparse,csv,json,subprocess,sys
from pathlib import Path
from ct_archselect import ROOT,REQUIRED,fresh
from ct_pregion_audit import sha,write,dump
def check(first,repeat,out):
    out=fresh(out)
    h=json.loads((first/'hashes.json').read_text());r=json.loads((repeat/'hashes.json').read_text())
    assert set(h)==set(r)
    for n,v in h.items():assert sha(first/n)==v==r[n]==sha(repeat/n),n
    for n in REQUIRED:
        assert n in h
        if n.endswith('.json'):json.loads((first/n).read_text())
        else:
            with (first/n).open(newline='') as f:assert list(csv.DictReader(f))
    g=json.loads((first/'input-guards.json').read_text())
    for n,v in g.items():assert sha(ROOT/n)==v,n
    d=json.loads((first/'decision.json').read_text())
    assert d['result']=='SELECT-A' and d['qualified_reclaimed_words']==0
    assert d['offline_patch_now'] is False and d['flashing_now'] is False
    assert d['site_totals_complete'] is False and d['no_new_universal_writer_audit']
    t=json.loads((first/'offline-testability.json').read_text())
    assert t['finite_patch_candidate']==dict(A=False,B=False)
    assert not t['authentic_full_boot_required']
    v=json.loads((first/'validation.json').read_text())
    assert v['source_sha256']==sha(ROOT/'tools/ct_archselect.py')
    assert v['selected_map_words']==552 and v['candidate_words']==84
    assert v['stock_or_new_DSP_execution']==0 and not v['universal_writer_census_rerun']
    run=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','emulator/tests',
        '-p','test_archselect.py','-v'],cwd=ROOT,capture_output=True,text=True)
    write(out/'contract-tests.txt',run.stdout+run.stderr)
    assert run.returncode==0 and 'Ran 15 tests' in run.stderr
    refused=False
    try:fresh(first)
    except ValueError:refused=True
    assert refused
    result=dict(status='TESTED repeat/source/contracts PASS; SELECT-A conditional, patch NOT justified',
        requested_reports=len(REQUIRED),repeated_members=len(h),guarded_inputs_unchanged=len(g),tests=15,
        overwrite_refusal=True,selection='SELECT-A',complete_patch_ready=False,DSP_execution=0,
        firmware_or_hardware_actions=0,checker_sha256=sha(Path(__file__)))
    dump(out,'verification.json',result)
    dump(out,'hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser()
    for n in ['first','repeat','out']:a.add_argument('--'+n,type=Path,required=True)
    check(**{n:v.resolve() for n,v in vars(a.parse_args()).items()})
