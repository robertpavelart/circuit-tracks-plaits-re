"""File-first identity and exact byte-diff classification, independent decoder."""
from pathlib import Path
import sys,json,hashlib,shutil
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase62-final-preflight'
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'))
from independent_validate import decode,crc
sha=lambda b:hashlib.sha256(b).hexdigest()
name='circuittracks-nor-defect-closure-development';syx=(O/(name+'.syx')).read_bytes();image,_,details=decode(syx);assert image==(O/(name+'.bin')).read_bytes()
c=json.loads((O/'construction.json').read_text());old=json.loads((P/'frozen-candidate-identity.json').read_text());prior=(P/(old['candidate']+'.bin')).read_bytes();assert len(prior)==len(image)
allowed=[(0x080101e8,0x080101ee,'new compared header marker')]
for n,v in c['components'].items():allowed.append((int(v['address'],16),int(v['address'],16)+v['bytes'],n))
for n,v in c['trampolines'].items():allowed.append((int(v['address'],16),int(v['address'],16)+v['bytes'],n))
# Complete replaced component slots, including former reservation guard, are
# rebuilt from pinned clean source. Removed trailing old bytes are classified.
for n,a in c['layout'].items():
 if int(a,16)<0x08074100:allowed.append((int(a,16),min(int(a,16)+0x600,0x08074100),n+' rebuilt slot'))
changes=[]
for i,(a,b) in enumerate(zip(prior,image)):
 if a!=b:
  address=0x08010000+i;owners=[n for lo,hi,n in allowed if lo<=address<hi];assert owners,hex(address);changes.append(dict(address=hex(address),before=a,after=b,owner=owners[0]))
assert image[:0x1c8]==prior[:0x1c8] and image[0x1c8:0x1ee]!=prior[0x1c8:0x1ee]
result=dict(confidence='PROVEN',candidate=name,BIN_bytes=len(image),BIN_sha256=sha(image),SYX_bytes=len(syx),SYX_sha256=sha(syx),CRC=f'{crc(image):08X}',independent_decode=details,changed_bytes=len(changes),changes=changes,designation='DEVELOPMENT ONLY — NOT HARDWARE ELIGIBLE',marker='N63DEV',header_comparison_changed=True,passed=True,hardware_access=False)
(O/'development-identity.json').write_text(json.dumps(result,indent=2)+'\n')
rollback=O/'rollback';rollback.mkdir(exist_ok=True)
for n in ['circuittracks-firmware-4486-STOCK.syx','circuittracks-B1.3-manifest-matched.syx','ct_uploader-reference-pinned.html']:shutil.copyfile(P/'rollback'/n,rollback/n)
print('Independent decode / CRC / diff PASS',len(changes))
