"""Authenticate B1.3 selector records against native scatter initialization."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase42-exact-rdiag-integration'))
from environment import *
O=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools'));from ct_data_decode import decode
def main():
 e=Physical();u=e.uc;fixture=bytes(u.mem_read(0x20003c88,0x50))
 u.mem_write(0x08010000,b'\xff'*0x70000);u.mem_write(0x08010000,PUBLISHED[:])
 out,desc=decode(PUBLISHED[:]);u.mem_write(0x20000000,b'\xa5'*0x3d04)
 e.call(0x080596c4,0x0805b7c8,maxins=500000)
 actual=bytes(u.mem_read(0x20000000,len(out)))
 assert actual==out and actual[0x3c88:0x3cd8]==fixture
 rows=[]
 for k in range(4):
  p=e.r32(0x20003cc8+4*k)
  rows.append(dict(selector=k,record=hex(p),interface_pointer_address=hex(e.r32(p)),service_pointer=hex(e.r32(p+4)),base=hex(e.r32(p+8)),capacity=hex(e.r32(p+12))))
 result=dict(confidence='PROVEN',B13_image_sha256=PUBLISHED.hash,
  method='Actual B1.3 scatter descriptor0805B7C8 and native decompressor080596C4, independent decoder exact comparison, A5-poisoned output; no coldboot or constructors claimed',
  initialized_data_sha256=sha(actual),initialized_data_bytes=len(actual),fixture_selector_records_match=True,table_address='0x20003cc8',selectors=rows)
 (O/'b13-selector-provenance.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
