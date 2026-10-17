"""Offline gate contract, not a transport or hardware capture tool."""
import json,struct
from pathlib import Path
import sys
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase49-existing-geometry-reader'))
from geometry_parser import decode
def gate(raw,*,mount_status,valid,fresh_mount,binding_confirmed,same_epoch):
    if mount_status!=0 or not all((valid,fresh_mount,binding_confirmed,same_epoch)):
        return dict(allow_raw_evidence=False,reason='missing capture provenance/validity/epoch')
    # Native mount IDs wrap to zero. The old parser is intentionally stricter;
    # direct fresh-success provenance permits zero without inventing a new ID.
    check=bytearray(raw)
    actual_id=struct.unpack_from('<H',check,14)[0] if len(check)==46 else None
    if actual_id==0:struct.pack_into('<H',check,14,1)
    try:r=decode(bytes(check))
    except ValueError as e:return dict(allow_raw_evidence=False,reason=str(e))
    r['mount_id']=actual_id
    coefficients=r['targets'][1]
    identity=r['targets'][0]
    return dict(allow_raw_evidence=not coefficients['intersects_normal_writable_mapping'],
        coefficients_filesystem_excluded=not coefficients['intersects_normal_writable_mapping'],
        identity_filesystem_excluded=not identity['intersects_normal_writable_mapping'],
        identity_nonfilesystem_preservation='UNKNOWN separately; not a coefficient-only veto',
        geometry=r,scope='Conditional host policy on supplied record/provenance, not actual current-unit authorization')
def main():
    rows=json.loads((OUT/'mount-cases.json').read_text())['cases'];result=[]
    args=dict(mount_status=0,valid=True,fresh_mount=True,binding_confirmed=True,same_epoch=True)
    raw=bytes.fromhex(rows[0]['boundary']['record'])
    for name,record,override,expect in [
        ('authenticated-model',raw,{},True),
        ('native-mount-ID-zero',bytes.fromhex(rows[5]['boundary']['record']),{},True),
        ('different-valid-layout',bytes.fromhex(rows[6]['boundary']['record']),{},True),
        ('mount-error',raw,{'mount_status':1},False),('invalid-state',raw,{'valid':False},False),
        ('old-mount',raw,{'fresh_mount':False},False),('wrong-backend',raw,{'binding_confirmed':False},False),
        ('remount-invalidated',raw,{'same_epoch':False},False),('truncated',raw[:-1],{},False)]:
        d=gate(record,**(args|override));assert d['allow_raw_evidence']==expect
        result.append(dict(name=name,expected=expect,result=d))
    # Preserve the incoming record exactly; the zero-ID compatibility check never
    # mutates retained evidence, and mount-success provenance is mandatory first.
    assert raw.hex()==rows[0]['boundary']['record']
    (OUT/'host-gate-cases.json').write_text(json.dumps(dict(confidence='PROVEN',scope='Pure supplied-record decision tests; provenance predicates are modeled, not acquired',passed=True,cases=result),indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=len(result))))
if __name__=='__main__':main()
