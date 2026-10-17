"""Local read-only-source rollback provisioning; no network/device calls."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase42-exact-rdiag-integration'
sys.path.insert(0,str(P));from environment import PUBLISHED,REF
sys.path.insert(0,str(P/'source/tools'));import ct_fw
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'));from independent_validate import decode
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 d=O/'rollback';d.mkdir(exist_ok=True);rows=[]
 manifest_path=REF/'firmware/b1.3/manifest.json';m=json.loads(manifest_path.read_text());b13=PUBLISHED[:];bsyx=ct_fw.encode(b13)
 assert sha(b13)=='2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41' and sha(bsyx)==m['syx_sha256']=='6f07376b5983a5e0350d4883ae9ed57a69bc735320afde9f43ca75017b8e8736'
 official=R/'builds/phase43-hardware-test-candidate/rollback/circuittracks-firmware-4486-STOCK.syx';osy=official.read_bytes()
 assert sha(osy)=='bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd'
 for name,data,source in [('circuittracks-firmware-4486-STOCK.syx',osy,str(official)),('circuittracks-B1.3-manifest-matched.syx',bsyx,'Pinned official+COPY/ADD reconstruction, public B1.3 manifest '+str(manifest_path))]:
  img,_,_=decode(data)
  if 'B1.3' in name:assert img==b13
  (d/name).write_bytes(data);rows.append(dict(filename=name,bytes=len(data),sha256=sha(data),decoded_BIN_sha256=sha(img),source=source,hardware_tested_here=False))
 source=REF/'tools/ct_uploader.html';uploader=source.read_bytes();name='ct_uploader-reference-pinned.html';(d/name).write_bytes(uploader)
 assert m['syx_sha256'].encode() in uploader and sha(osy).encode() in uploader
 rows.append(dict(filename=name,bytes=len(uploader),sha256=sha(uploader),source=str(source),role='Exact reference uploader pinned for official4486/B1.3 rollback',executed=False))
 c=json.loads((O/'frozen-candidate-identity.json').read_text());permitted=c['SYX_sha256'].encode() in uploader
 result=dict(confidence='PROVEN',artifacts=rows,B13_exact_replay_image=True,official_Novation_origin_authentication='UNKNOWN: local reference/Phase43 byte match, no authenticated Novation-origin acquisition record located in inspected baseline/provenance notes',uploader_permits_frozen_candidate=permitted,candidate_update_tool_ready=permitted,hardware_access=False)
 (O/'rollback-provisioning.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
