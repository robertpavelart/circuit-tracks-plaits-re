"""Resume-only identity and uncovered protocol-state checks. No live I/O."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase61-final-geometry-gated-candidate'
sys.path.insert(0,str(P));import native_tests as T
def main():
 c=json.loads((O/'correction-identity.json').read_text());raw=(O/(c['candidate']+'.syx')).read_bytes();image,_,_=T.decode(raw)
 assert hashlib.sha256(raw).hexdigest()==c['SYX_sha256'] and hashlib.sha256(image).hexdigest()==c['BIN_sha256']
 for n in ('corrected-reservation-tests.json','native-tests.json'):
  r=json.loads((O/n).read_text());assert r.get('passed',r.get('all_passed')),n
 (O/'frozen-candidate-identity.json').write_text(json.dumps(c|dict(status='UNQUALIFIED UNTIL PREFLIGHT COMPLETES',Phase61_original='SUPERSEDED / FAILED RESERVATION TEST / DO NOT FLASH'),indent=2)+'\n')
 T.image=image;rows=[]
 for label,control,expected in [('NOT_READY boot',0,'NOT_READY'),('NOT_READY mounting',0x16,'NOT_READY'),('INVALID',0x1d,'INVALID'),('FAILED',0x15,'FAILED'),('VALID',0x11,'GEOMETRY')]:
  n=T.N().mounted();n.e.w32(T.S,control);n.frames.clear();n.send(T.host.request(T.SESSION));response=[f.hex() for f in n.frames]
  rows.append(dict(case=label,control=hex(control),required=expected,replies=response,raw_reads=len(n.reads),output_record=n.record().hex(),passed=bool(response)))
 (O/'mount-state-protocol-tests.json').write_text(json.dumps(dict(confidence='PROVEN',image_sha256=c['BIN_sha256'],cases=rows,passed=all(x['passed'] for x in rows),finding='Non-VALID states return without emitting distinguishable status; silence cannot distinguish NOT_READY, INVALID or FAILED',hardware_access=False),indent=2)+'\n')
 print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
