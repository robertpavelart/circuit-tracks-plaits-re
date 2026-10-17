"""Deterministic fake transport/clock; synthetic payloads only."""
from pathlib import Path
import sys,json,tempfile
from unittest.mock import patch
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O));import host
from native_tests import N,SESSION,payload
def main():
 root=Path(tempfile.mkdtemp(prefix='atomic-run-',dir=O/'synthetic-host-tests'))
 n=N().mounted().export();geom=n.frames[0];n.authorize();frames=n.frames[1:];rows=[]
 variants=[('normal',frames),('truncated0',frames[:1]),('truncated4',frames[:5]),('truncated7',frames[:8]),('silence',[]),
 ('error0',[b'error']),('error4',frames[:4]+[b'error']),('error7',frames[:7]+[b'error']),
 ('duplicate chunk',frames[:1]+frames),('missing chunk',frames[:4]+frames[5:]),('reorder',frames[:3]+[frames[4],frames[3]]+frames[5:]),
 ('duplicate completion',frames+[frames[-1]]),('early completion',[frames[-1]])]
 corrupt=bytearray(frames[2]);corrupt[-2]^=1;variants.append(('CRC corruption',frames[:2]+[bytes(corrupt)]+frames[3:]))
 for name,stream in variants:
  now=[0.];sent=[];h=host.Session(sent.append,lambda:now[0]);h.start();h.accept(geom);assert len(sent)==2
  for f in stream:h.accept(f)
  if name!='normal':now[0]=11.;h.poll()
  d=root/name.replace(' ','-')
  p=d/'qspi_00082000_000821ff.bin'
  digest=h.finish(d)
  if name=='normal':assert h.state=='SUCCESS' and p.read_bytes()==payload[23:] and digest
  else:
   assert h.state=='FAILED' and h.device=='POWER-CYCLE REQUIRED' and not p.exists() and not list(d.glob('*.partial'))
   before=len(sent)
   try:h.start()
   except ValueError:pass
   else:raise AssertionError('retry allowed')
   h.accept(geom);h.poll();assert len(sent)==before==2
  rows.append(dict(case=name,passed=True,requests=len(sent),automatic_retries=0,evidence_created=p.exists(),status=h.state))
 for name,reply in [('geometry silence',None),('geometry malformed',b'bad'),('geometry CRC',geom[:-2]+bytes([geom[-2]^1])+geom[-1:])]:
  now=[0.];sent=[];h=host.Session(sent.append,lambda:now[0]);h.start()
  if reply:h.accept(reply)
  now[0]=11.;h.poll();assert h.state=='FAILED' and len(sent)==1;rows.append(dict(case=name,passed=True,requests=1,automatic_retries=0,evidence_created=False))
 # Optional identity is a separate explicit host choice, never inferred from
 # coefficient permission. It has its own geometry-domain safety decision.
 n=N().mounted().export();g=n.frames[0];n.authorize(True);sent=[];h=host.Session(sent.append,lambda:0.,identity=True);h.start();h.accept(g)
 for f in n.frames[1:]:h.accept(f)
 d=root/'optional-identity';assert h.finish(d);assert (d/'nor_00081000_00081016.bin').read_bytes()==payload[:23]
 rows.append(dict(case='separately authorized optional identity',passed=True,requests=2,automatic_retries=0,evidence_created=True))
 # A second-file IO failure must not expose even the first accepted filename.
 sent=[];h=host.Session(sent.append,lambda:0.,identity=True);h.start();h.accept(g)
 for f in n.frames[1:]:h.accept(f)
 failed=root/'injected-second-file-IO-error'
 with patch.object(host.os,'fsync',side_effect=[None,OSError('injected second-file failure')]):assert h.finish(failed) is None
 assert not failed.exists() and not list(root.glob('.capture-*')) and h.state=='FAILED' and len(sent)==2
 rows.append(dict(case='atomic optional pair second-file IO failure',passed=True,requests=2,automatic_retries=0,evidence_created=False))
 r=dict(confidence='PROVEN',passed=True,timeout_seconds=host.TIMEOUT,clock='controllable monotonic fake; total bound per geometry/capture stage',cases=rows,hardware_access=False,synthetic_data_only=True)
 (O/'host-tests.json').write_text(json.dumps(r,indent=2)+'\n');(O/'synthetic-host-tests/README.md').write_text('SYNTHETIC TEST OUTPUT ONLY. These files are not current-unit NOR evidence.\n');print('Host containment PASS',len(rows))
if __name__=='__main__':main()
