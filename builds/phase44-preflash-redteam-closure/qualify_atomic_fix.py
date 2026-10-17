"""Minimal candidate correction ONLY after original native race test fails.

Creates separately named phase44 artifacts; never overwrites phase43. Runs
inherited coupled native regressions using the corrected image in the emulator.
No hardware, uploader or transport DLL is imported.
"""
from pathlib import Path
import sys,json,hashlib,importlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];S=R/'builds/phase43-hardware-test-candidate'
sys.path.insert(0,str(O))
import success_atomicity as A
from thumb import b_w
import environment as E
sys.path.insert(0,str(S));from independent_validate import decode,crc
sys.path.insert(0,str(S/'source/tools'));import ct_fw

def main():
    evidence=json.loads((O/'success-atomicity.json').read_text())
    assert evidence['quarantine_overwrite_reproduced'] and not evidence['original_atomic']
    original=(S/'circuittracks-4486-nor-evidence-test.bin').read_bytes()
    assert hashlib.sha256(original).hexdigest()=='9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6'
    blob=A.fixed_fragment();fixed=bytearray(original)
    assert fixed[A.FIX-0x08010000:A.FIX-0x08010000+len(blob)]==b'\xff'*len(blob)
    fixed[A.START-0x08010000:A.START-0x08010000+4]=b_w(A.START,A.FIX)
    fixed[A.FIX-0x08010000:A.FIX-0x08010000+len(blob)]=blob
    # The native installer compares 38 header bytes, not the whole image.
    # A distinct marker is necessary or an original-candidate -> corrected-
    # candidate install can become a silent header-equality no-op.
    fixed[0x1e8:0x1ee]=b'N44ATM'
    fixed=bytes(fixed)
    changed=[i for i,(x,y) in enumerate(zip(original,fixed)) if x!=y]
    assert all(A.START<=0x08010000+i<A.START+4 or A.FIX<=0x08010000+i<A.FIX+len(blob) or 0x1e8<=i<0x1ee for i in changed)
    assert fixed[:0x1e8]==original[:0x1e8] and fixed[0x1ee:0x1f0]==original[0x1ee:0x1f0] and len(fixed)==len(original)
    name='circuittracks-4486-nor-evidence-atomic-test'
    syx=ct_fw.encode(fixed)
    decoded,packets,details=decode(syx)
    assert decoded==fixed and ct_fw.encode(decoded)==syx
    (O/(name+'.bin')).write_bytes(fixed);(O/(name+'.syx')).write_bytes(syx)
    result=dict(confidence='PROVEN',reason='Exact original candidate permits FAILED_QUARANTINED to be overwritten by SUCCESS at a native instruction boundary',
        original_candidate_valid_for_monotonic_terminal_contract=False,
        original_candidate_unchanged=True,new_candidate=name,bytes=len(fixed),SYX_bytes=len(syx),
        BIN_sha256=hashlib.sha256(fixed).hexdigest(),SYX_sha256=hashlib.sha256(syx).hexdigest(),CRC32_MPEG2=hex(crc(fixed)),
        changed_bytes_vs_phase43=len(changed),patch_ranges=[[hex(A.START),hex(A.START+4)],[hex(A.FIX),hex(A.FIX+len(blob))],['0x080101e8','0x080101ee']],
        marker='N44ATM',marker_reason='Avoid native 38-byte-header equality no-op versus original phase43 image',
        body_bytes=len(blob),image_growth=0,heap_delta_from_phase43=0,DSP_changes=0,vector_changes=0,bootloader_changes=0,option_byte_changes=0,
        independent_decode=details,roundtrip_exact=True,hardware_access=False,transmitted=False)
    (O/'atomic-candidate-identity.json').write_text(json.dumps(result,indent=2)+'\n')
    # Only image-loading changes; execute all inherited native test cases.
    Previous=E.Physical
    class AtomicPhysical(Previous):
        def __init__(self):
            super().__init__();self.uc.mem_write(0x08010000,fixed)
    E.Physical=AtomicPhysical
    # success_atomicity imports environment only, so coupled/test_native have not
    # yet bound their Physical. All fixed PCs and ownership fixtures remain.
    native=importlib.import_module('test_native')
    native.O=O
    native.main()
    result['full_inherited_native_case_count']=json.loads((O/'native-results.json').read_text())['case_count']
    (O/'atomic-candidate-identity.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
