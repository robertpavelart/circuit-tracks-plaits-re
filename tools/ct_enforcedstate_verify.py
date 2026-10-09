"""Check repeatable design ledgers; never create or run a DSP image."""
import argparse,csv,json,subprocess,sys
from pathlib import Path
from ct_enforcedstate_design import ROOT,fresh,P_STATE
from ct_pregion_audit import sha,write,dump
REQUIRED=['storage-domain-comparison.csv','p204b-guard-options.csv',
 'dma-admission-design.json','service-write-guard.json','ownership-epoch.json',
 'selected-path-writers.csv','selected-path-readers.csv','save-strategy.csv',
 'feature-impact.csv','cycle-budget.json','code-size.json','failure-containment.json',
 'qualification.json','validation.json']

def check(first,repeat,out):
    out=fresh(out)
    h=json.loads((first/'hashes.json').read_text());r=json.loads((repeat/'hashes.json').read_text())
    assert set(h)==set(r)
    for name,v in h.items():assert sha(first/name)==v==r[name]==sha(repeat/name),name
    for name in REQUIRED:
        assert name in h
        if name.endswith('.json'):json.loads((first/name).read_text())
        else:
            with (first/name).open(newline='') as f:assert list(csv.DictReader(f))
    guards=json.loads((first/'input-guards.json').read_text())
    for name,v in guards.items():assert sha(ROOT/name)==v,name
    q=json.loads((first/'qualification.json').read_text())
    assert q['overall']=='PARTIAL' and q['seven_object']==list(P_STATE)
    for name in ['state_ownership_guaranteed_by_implemented_runtime',
                 'offline_patched_image_technically_justified','hardware_flashing_justified']:
        assert q[name] is False
    c=json.loads((first/'cycle-budget.json').read_text())
    s=json.loads((first/'code-size.json').read_text())
    assert c['complete_one_voice_upper'] is None and s['complete_added_P'] is None
    assert c['p204b']['record_count_normal_bound'] is None
    assert c['p204b']['q1_n20_partial_example']==29548
    assert s['known_partial_subtotal']==866 and s['planning_subtotal']==1626
    assert s['proposed_data_words']==102
    v=json.loads((first/'validation.json').read_text())
    assert not v['native_guard_code_assembled'] and not v['new_P7_candidate_executed']
    assert not v['data_objects_reserved']
    with (first/'writer-coverage-obligations.csv').open() as f:assert len(list(csv.DictReader(f)))==344
    run=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','emulator/tests',
        '-p','test_enforcedstate_design.py','-v'],cwd=ROOT,capture_output=True,text=True)
    write(out/'contract-tests.txt',run.stdout+run.stderr)
    assert run.returncode==0 and 'Ran 17 tests' in run.stderr
    refused=False
    try:fresh(first)
    except ValueError:refused=True
    assert refused
    result=dict(status='TESTED design ledger/repeat/guards PASS; runtime ownership PARTIAL',
        required_reports=REQUIRED,repeated_members=len(h),guarded_inputs_unchanged=len(guards),
        tests=17,overwrite_refusal=True,source_bytes_verified=v,
        complete_runtime_cost_proved=False,ownership_guaranteed=False,
        DSP_execution=0,firmware_or_hardware_actions=0,checker_sha256=sha(Path(__file__)))
    dump(out,'verification.json',result)
    dump(out,'hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps({k:result[k] for k in ['status','repeated_members','guarded_inputs_unchanged','tests']},indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser()
    for name in ['first','repeat','out']:a.add_argument('--'+name,type=Path,required=True)
    check(**{k:v.resolve() for k,v in vars(a.parse_args()).items()})
