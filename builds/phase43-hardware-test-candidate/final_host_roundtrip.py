"""Final SYX native USB bytes through final standalone capture tool. Offline."""
from pathlib import Path
import sys,json,tempfile
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;P=O.parents[1]/'builds/phase42-exact-rdiag-integration'
sys.path.insert(0,str(O))
from native_regression import FinalPhysical
import replay
replay.Physical=FinalPhysical
from coupled import Exact
import capture_nor_evidence as C
from test_capture_tool import Fake,Clock
def main():
 m=Exact();m.start();assert m.finish(1500);m.verify()
 raw=b''.join(m.usb_bytes);wire=b''.join(raw[i+1:i+1+{4:3,5:1,6:2,7:3}[raw[i]&15]] for i in range(0,len(raw),4))
 with tempfile.TemporaryDirectory(dir=O) as d:
  root=Path(d);clock=Clock();link=Fake(clock,wire);dest=root/'evidence';result=C.run_capture(dest,lambda:link,clock,root/'attempt.json')
  assert result['status']=='SUCCESS' and len(link.sent)==1 and set(p.name for p in dest.iterdir())==set(C.NAMES)
  assert (dest/C.NAMES[0]).read_bytes()==m.payload[:23] and (dest/C.NAMES[1]).read_bytes()==m.payload[23:]
  lengths={p.name:p.stat().st_size for p in dest.iterdir()}
 (O/'final-host-roundtrip.json').write_text(json.dumps(dict(confidence='PROVEN',source='Final candidate SYX -> native emulated USB output -> final standalone host tool -> atomic files',origin='Synthetic emulated NOR bytes; not device evidence',result=result,lengths=lengths,requests=1,temporary_synthetic_files_removed=True,MIDI_ports_opened=0,hardware_access=False),indent=2)+'\n')
 print(result['message']);print('TRANSACTION STATUS = '+result['status']+' (SYNTHETIC OFFLINE)')
if __name__=='__main__':main()
