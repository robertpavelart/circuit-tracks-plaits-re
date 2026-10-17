"""Review old-staging dependencies in completed exact native transfer logs.

No updater rerun or image generation. Each read must be dominated by a recorded
erase/program of all its bytes. This is a selected-trace dependency proof, not
an argument that arbitrary boot/persistent paths have been enumerated.
"""
from pathlib import Path
import json,hashlib,sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase44-preflash-redteam-closure'
def add(ranges,a,b):
 out=[]
 for lo,hi in sorted(ranges+[(a,b)]):
  if out and lo<=out[-1][1]:out[-1]=(out[-1][0],max(hi,out[-1][1]))
  else:out.append((lo,hi))
 return out
def covered(ranges,a,b):return any(lo<=a and hi>=b for lo,hi in ranges)
def main():
 rows=[]
 for name in ('b13-to-candidate','candidate-to-official','candidate-to-b13'):
  path=P/('atomic-'+name+'-operations.json');raw=path.read_bytes();data=json.loads(raw)
  known=[];unknown=[];read_count=0;writes=0;erases=0
  for index,op in enumerate(data['operations']):
   a=int(op['start'],16);b=int(op['end_exclusive'],16)
   if op['kind']=='ERASE':known=add(known,a,b);erases+=1
   elif op['kind']=='WRITE':known=add(known,a,b);writes+=1
   elif op['kind']=='READ':
    read_count+=1
    if not covered(known,a,b):unknown.append(dict(index=index,start=hex(a),end_exclusive=hex(b),phase=op['phase']))
  assert not unknown,(name,unknown)
  summary=json.loads((P/('atomic-'+name+'-summary.json')).read_text())
  assert summary['actual_install_performed'] and not summary['silent_noop']
  rows.append(dict(transition=name,trace_sha256=hashlib.sha256(raw).hexdigest(),array_reads=read_count,
   prior_array_byte_dependencies=unknown,staged_old_bytes_read_before_replacement=False,
   writes=writes,erases=erases,final_installed_sha256=summary['final_installed_sha256'],
   method='Every recorded array read covered by prior native erase/program; supplied read values cannot depend on old staging bytes within selected trace'))
 root=R/'builds/phase43-hardware-test-candidate'
 images={'B1.3':None,'corrected':(P/'circuittracks-4486-nor-evidence-atomic-test.bin').read_bytes(),
  'official4486':(root/'official-4486-decoded.bin').read_bytes()}
 # Authenticate the published B1.3 reconstruction through its existing loader.
 sys.path.insert(0,str(R/'builds/phase42-exact-rdiag-integration'));from environment import PUBLISHED
 images['B1.3']=PUBLISHED[:]
 headers={k:v[0x1c8:0x1ee].hex() for k,v in images.items()}
 assert len(set(headers.values()))==3
 out=dict(confidence='PROVEN',scope='Selected three completed native transfers and inspected version branch, not complete reset or power-loss proof',transitions=rows,
  compared_header_bytes=38,compared_headers=headers,all_requested_transition_headers_differ=True,
  native_same_header_noop_control=json.loads((P/'header-noop-control.json').read_text()),
  invalid_partial_upload_scope='No claim of unconditional install after interrupted upload or CRC failure; these are rejected/unfinished, not successful named transitions',
  hardware_access=False,firmware_generated=False)
 (O/'update-dependency-review.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 print('All three exact native traces have zero old-array read dependencies; compared headers are distinct.')
if __name__=='__main__':main()
