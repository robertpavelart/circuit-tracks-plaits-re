"""Corrected file-first native USB/host roundtrip and boot intake checks."""
from pathlib import Path
import sys,json,tempfile,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];S=R/'builds/phase43-hardware-test-candidate'
sys.path.insert(0,str(O));sys.path.insert(1,str(S));sys.path.insert(2,str(R/'builds/phase42-exact-rdiag-integration'))
from independent_validate import decode
import environment as E
raw=(O/'circuittracks-4486-nor-evidence-atomic-test.syx').read_bytes()
image,packets,validation=decode(raw)
expected=json.loads((O/'atomic-candidate-identity.json').read_text())
assert hashlib.sha256(image).hexdigest()==expected['BIN_sha256']
Previous=E.Physical
class Final(E.Physical):
 def __init__(self):super().__init__();self.uc.mem_write(0x08010000,image)
E.Physical=Final
from coupled import Exact
import capture_nor_evidence as C
from test_capture_tool import Fake,Clock
def main():
 m=Exact();m.start();assert m.finish(1500);m.verify()
 usb=b''.join(m.usb_bytes);wire=b''.join(usb[i+1:i+1+{4:3,5:1,6:2,7:3}[usb[i]&15]] for i in range(0,len(usb),4))
 with tempfile.TemporaryDirectory(dir=O) as d:
  root=Path(d);clock=Clock();link=Fake(clock,wire);dest=root/'evidence'
  result=C.run_capture(dest,lambda:link,clock,root/'attempt.json')
  assert result['status']=='SUCCESS' and len(link.sent)==1
  assert set(p.name for p in dest.iterdir())==set(C.NAMES)
  assert (dest/C.NAMES[0]).read_bytes()==m.payload[:23]
  assert (dest/C.NAMES[1]).read_bytes()==m.payload[23:]
  assert (root/'attempt.json').exists()
 E.Physical=Previous
 import recovery_model as B
 old=(S/'circuittracks-4486-nor-evidence-test.bin').read_bytes()
 n=B.Model(old);n.seed(image);n.validate_install()
 assert n.flash and bytes(n.u.mem_read(0x08010000,len(image)))==image
 # Native own bootloader intake, separately from app updater, corrupt state.
 n=B.Model(b'\xa5'*len(image));n.key_entry();n.nor[:0x90000]=b'\0'*0x90000
 for packet in B.raw_packets(raw):n.packet(packet)
 n.call(0x08007d06,n.e.r32(0x200054c4),0)
 assert n.reset and bytes(n.nor[:len(image)])==image
 n.validate_install();assert bytes(n.u.mem_read(0x08010000,len(image)))==image
 results=dict(confidence='PROVEN',source='Actual corrected SYX decoded independently',
  SYX_sha256=hashlib.sha256(raw).hexdigest(),BIN_sha256=hashlib.sha256(image).hexdigest(),
  native_USB_to_revised_host=result,requests=1,accepted_lengths=[23,512],origin='SYNTHETIC NOR test input, not hardware evidence',
  original_to_corrected_header_does_not_noop=True,corrected_bootloader_own_upload_accepted=True,
  final_installed_sha256=hashlib.sha256(bytes(n.u.mem_read(0x08010000,len(image)))).hexdigest(),
  recovery_operations=n.ops,hardware_access=False)
 (O/'atomic-supplement.json').write_text(json.dumps(results,indent=2)+'\n')
 print('Corrected native USB to revised host and own recovery intake PASS')
if __name__=='__main__':main()
