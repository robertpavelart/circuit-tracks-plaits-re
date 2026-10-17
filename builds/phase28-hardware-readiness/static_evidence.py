"""Record source identity and unchanged instruction spans; no image assembly."""
from inspect_code import *
import re

spans=[]
for p in sorted(O.glob('*.asm')):
 a=int(p.stem,16)
 addresses=[int(x,16) for x in re.findall(r'^([0-9a-f]{8}):',p.read_text(),re.M)]
 if not addresses:continue
 end=max(addresses)+2
 if a>=0x08010000:
  stock=STOCK[a-0x08010000:end-0x08010000]
  b13=PUBLISHED[a-0x08010000:end-0x08010000]
  spans.append(dict(file=p.name,start=hex(a),end_exclusive=hex(end),B13_identical=stock==b13,sha256=sha(stock)))

host=REF/'tools/ct_fw.py'
lines=host.read_text(encoding='utf8').splitlines()
result=dict(confidence='PROVEN',scope='Static spans and source identity, not a boot execution proof',
 stock_disassembly_spans=spans,
 host_encoder=dict(path=str(host),sha256=sha(host.read_bytes()),symbol='encode',
  excerpt=[dict(line=i+1,text=lines[i]) for i in range(116,130)]),
 bootloader_full_sha256=sha(FLASH),bootloader_64K_sha256=sha(FLASH[:65536]),
 bootloader_range=['0x08000000','0x08010000'],
 normal_application_selector=0,coefficient_bundle_selector=2,
 warning='Any nonidentical span must not be attributed to B1.3 solely from stock disassembly')
a=0x08021000;end=0x08021044
b=PUBLISHED[a-0x08010000:end-0x08010000]
(O/'B13-DIN-dispatch.txt').write_text('\n'.join(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in md.disasm(b,a))+'\n')
result['DIN_changed_bytes']=[hex(a+i) for i,(x,y) in enumerate(zip(STOCK[a-0x08010000:end-0x08010000],b)) if x!=y]
(O/'static-evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(spans=len(spans),nonidentical=[x for x in spans if not x['B13_identical']],host_sha256=result['host_encoder']['sha256']),indent=2))
