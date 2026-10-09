"""Check repeated static ledgers, guards, required reports and focused tests."""
import argparse,csv,json,subprocess,sys
from pathlib import Path
from ct_pregion_audit import ROOT,fresh,sha,write,dump,LO,HI
REQUIRED=['candidate-region.json','loader-coverage.csv','p-writers.csv','dma-destinations.csv',
          'dma-reconfiguration.csv','service-p-writers.csv','rom-bootstrap-writers.json',
          'memory-mode.json','execution-targets.csv','guard-band.json','reload-semantics.json',
          'qualification.json','validation.json']

def check(first,repeat,out):
    out=fresh(out);h=json.loads((first/'hashes.json').read_text());r=json.loads((repeat/'hashes.json').read_text())
    assert set(h)==set(r)
    for n,v in h.items():assert sha(first/n)==v==r[n]==sha(repeat/n),n
    for n in REQUIRED:
        assert n in h
        if n.endswith('.json'):json.loads((first/n).read_text())
        else:
            with (first/n).open(newline='') as f:assert list(csv.DictReader(f))
    guard=json.loads((first/'input-guards.json').read_text())
    for n,v in guard.items():assert sha(ROOT/n)==v,n
    q=json.loads((first/'qualification.json').read_text())
    assert q['candidate']==[LO,HI] and q['overall']=='REFUSED'
    assert q['ownership_classification']=='CONDITIONAL' and not q['safe_seven_word_P_state_qualified']
    assert not q['offline_patch_construction_justified'] and not q['hardware_debug_recommended']
    run=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','emulator/tests','-p','test_pregion_ownership.py','-v'],
        cwd=ROOT,capture_output=True,text=True)
    write(out/'contract-tests.txt',run.stdout+run.stderr)
    assert run.returncode==0 and 'Ran 12 tests' in run.stderr
    # Exercise output refusal: existing report destinations fail before reads/writes.
    refused=False
    try:fresh(first)
    except ValueError:refused=True
    assert refused
    result=dict(status='TESTED static evidence/repeat/guards PASS; ownershipREFUSED',required_reports=REQUIRED,
        repeated_members=len(h),guarded_inputs_unchanged=len(guard),tests=12,overwrite_refusal=True,
        source_bytes_verified=json.loads((first/'validation.json').read_text()),
        candidate=[LO,HI],stock_seven_words_qualified=False,hardware_or_firmware_actions=0,
        checker_sha256=sha(Path(__file__)))
    dump(out,'verification.json',result);dump(out,'hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps({k:result[k] for k in ['status','repeated_members','guarded_inputs_unchanged','tests']},indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser()
    for n in ['first','repeat','out']:a.add_argument('--'+n,type=Path,required=True)
    check(**{k:v.resolve() for k,v in vars(a.parse_args()).items()})
