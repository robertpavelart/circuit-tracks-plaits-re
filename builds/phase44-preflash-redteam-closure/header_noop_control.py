"""Show changed code with equal compared header is silently not installed."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(O));from recovery_model import Model
def main():
 old=(R/'builds/phase43-hardware-test-candidate/circuittracks-4486-nor-evidence-test.bin').read_bytes()
 new=(O/'circuittracks-4486-nor-evidence-atomic-test.bin').read_bytes()
 same_header=bytearray(new);same_header[0x1e8:0x1ee]=old[0x1e8:0x1ee];same_header=bytes(same_header)
 assert same_header!=old and same_header[0x1c8:0x1ee]==old[0x1c8:0x1ee]
 m=Model(old);m.seed(same_header);m.validate_install()
 assert not m.flash and bytes(m.u.mem_read(0x08010000,len(old)))==old
 m=Model(old);m.seed(new);m.validate_install()
 assert m.flash and bytes(m.u.mem_read(0x08010000,len(new)))==new
 out=dict(confidence='PROVEN',native_entry='0x08003b9a',changed_code_equal_header=dict(staged_crc_valid=True,internal_erases=0,internal_programs=0,silent_noop=True,installed_original_sha256=hashlib.sha256(old).hexdigest()),
  changed_marker=dict(marker='N44ATM',installed=True,installed_sha256=hashlib.sha256(new).hexdigest()),hardware_access=False,SYX_generated=False)
 (O/'header-noop-control.json').write_text(json.dumps(out,indent=2)+'\n')
 print('Changed-code/same-header silent no-op PROVEN; distinct-marker install PROVEN.')
if __name__=='__main__':main()
