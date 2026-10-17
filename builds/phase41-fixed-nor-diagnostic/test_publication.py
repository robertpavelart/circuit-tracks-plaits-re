"""Additional host-only output failure checks; no native replay repeated."""
from pathlib import Path
from unittest.mock import patch
import tempfile,json
from host import OneShot,DeviceLease
from test_offline import Clock,Fake,DATA
from evidence_protocol import synthetic_packets,NAMES
O=Path(__file__).resolve().parent
def main():
 checks=[]
 with tempfile.TemporaryDirectory(dir=O) as d:
  root=Path(d);clock=Clock();f=Fake(clock,synthetic_packets(37,DATA));dest=root/'rename-failure'
  c=OneShot(DeviceLease(f,clock),37)
  with patch('host.os.rename',side_effect=OSError('synthetic publication failure')):result=c.run(dest)
  assert result['status']=='FAILED' and not dest.exists() and not list(root.glob('.nor-staging-*')) and len(f.sent)==1
  checks.append(dict(case='atomic directory rename failure',confidence='PROVEN',accepted_files=0,staging_left=False,requests=1))
  dest=root/'existing';dest.mkdir();(dest/NAMES[0]).write_bytes(b'previous evidence')
  clock=Clock();f=Fake(clock,synthetic_packets(37,DATA));c=OneShot(DeviceLease(f,clock),37)
  assert c.run(dest)['status']=='FAILED' and f.sent==[] and (dest/NAMES[0]).read_bytes()==b'previous evidence'
  checks.append(dict(case='existing capture refused without sending',confidence='PROVEN',requests=0,prior_evidence_unchanged=True))
 (O/'publication-results.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
if __name__=='__main__':main()
