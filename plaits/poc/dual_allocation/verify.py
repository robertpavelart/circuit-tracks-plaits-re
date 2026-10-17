"""Verify protected inputs and record reproducible study artifact hashes."""
import hashlib,json
from study import ROOT,REF,OUT
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    inv=json.loads((ROOT/'builds/phase20e-full-plaits-audit/source-inventory.json').read_text())
    before=inv['reference_before'];changed=[p for p,h in before.items() if sha(REF/p)!=h]
    current={str(p.relative_to(REF)).replace('\\','/') for p in REF.rglob('*') if p.is_file()}
    added=sorted(current-set(before));assert not changed and not added,(changed,added)
    manifest=json.loads((ROOT/'plaits/upstream/source-manifest.json').read_text())
    for row in manifest['files']:assert sha(ROOT/'plaits/upstream'/row['path'])==row['sha256'],row['path']
    result=dict(reference_files_verified=len(before),reference_changed=changed,reference_added=added,pinned_source_files_verified=len(manifest['files']),
        artifacts={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for folder in [ROOT/'plaits/poc/dual_allocation',OUT] for p in folder.rglob('*') if p.is_file() and p.suffix in ('.py','.cpp','.ps1','.be24','.json') and p.name!='verification.json'})
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='artifacts'},indent=2))
if __name__=='__main__':main()
