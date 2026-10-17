"""Independent serialization decoder before inspecting construction metadata.
No builder/ct_fw/native emitter imports. No device APIs.
"""
from pathlib import Path
import sys,json,hashlib,struct
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];OLD=R/'builds/phase43-hardware-test-candidate'
sys.path.insert(0,str(OLD))
from independent_validate import decode,crc
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 raw=(O/'circuittracks-final-geometry-gated-nor-test.syx').read_bytes();image,packets,details=decode(raw)
 assert image==(O/'circuittracks-final-geometry-gated-nor-test.bin').read_bytes()
 m=json.loads((O/'construction.json').read_text());base=(OLD/'clean-sc35d8.bin').read_bytes()
 assert sha(base)==m['source_sha256'] and sha(image)==m['BIN_sha256'] and sha(raw)==m['SYX_sha256']
 assert image[:0x1e8]==base[:0x1e8] and image[0x1ee:0x855a]==base[0x1ee:0x855a]
 ranges=[];begin=None
 allowed=[(0x5b6cc,0x5bc8c),(len(base),len(image))]
 for x in m['patches']:at=int(x['address'],16)-0x08010000;b=bytes.fromhex(x['after']);assert image[at:at+len(b)]==b;allowed.append((at,at+len(b)))
 for group in ('components','trampolines'):
  for x in m[group].values():at=int(x['address'],16)-0x08010000;assert sha(image[at:at+x['bytes']])==x['sha256']
 for i in range(len(image)+1):
  changed=i<len(image) and (i>=len(base) or image[i]!=base[i])
  if changed:assert any(a<=i<b for a,b in allowed),hex(i)
  if changed and begin is None:begin=i
  if not changed and begin is not None:ranges.append(dict(start=hex(0x08010000+begin),end_exclusive=hex(0x08010000+i),bytes=i-begin));begin=None
 assert image[0x1c8:0x1ee]!=base[0x1c8:0x1ee] and image[0x1e8:0x1ee]==b'N61GEO'
 # Every changed prefix byte is an explicit hook. App-only framing cannot
 # address bootloader or option bytes; the install replay independently checks it.
 result=dict(confidence='PROVEN',passed=True,source='SYX file decoded before BIN/metadata reads',SYX_bytes=len(raw),SYX_sha256=sha(raw),BIN_bytes=len(image),BIN_sha256=sha(image),CRC=hex(crc(image)),details=details,app_end=hex(0x08010000+len(image)),headroom=0x70000-len(image),marker='N61GEO',DSP_bytes_unchanged_from_clean_SC35D8=True,bootloader_in_image=False,option_bytes_in_image=False,all_components_authenticated=True,diff_ranges=ranges,changed_bytes=sum(x['bytes'] for x in ranges),scope='Serialization and exact construction diff; semantic/read-only gates are separate native/static reviews')
 (O/'file-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='diff_ranges'},indent=2))
if __name__=='__main__':main()
