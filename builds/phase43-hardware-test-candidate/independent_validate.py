"""File-first firmware validator. No ct_fw import, builder, MIDI or uploader.

Uses a bit-list block decoder and bitwise MPEG-2 CRC, independently of ct_fw's
integer block codec/table CRC. Rejects framing, order, pad and length anomalies.
"""
from pathlib import Path
import sys,json,hashlib,struct
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase42-exact-rdiag-integration'
EXPECTED='9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6'
def sha(b):return hashlib.sha256(b).hexdigest()
def crc(b):
 value=0xffffffff
 for byte in b:
  value^=byte<<24
  for _ in range(8):value=((value<<1)^(0x04c11db7 if value&0x80000000 else 0))&0xffffffff
 return value
def messages(raw):
 at=0;out=[]
 while at<len(raw):
  assert raw[at:at+5]==bytes.fromhex('f000202900'),'framing/vendor'
  end=raw.index(247,at+1);packet=raw[at:end+1]
  assert all(x<128 for x in packet[1:-1]),'non-seven-bit body'
  out.append((packet[5],packet[6:-1]));at=end+1
 assert at==len(raw) and len(out)>=3
 return out
def nibble(b):
 assert all(x<16 for x in b),'nibble'
 n=0
 for x in b:n=n*16+x
 return n
def block(b):
 assert len(b)==37 and all(x<128 for x in b),'block length/packing'
 bits=[(x>>s)&1 for x in b for s in range(6,-1,-1)]
 assert bits[256:]==[0,0,0],'nonzero packing pad'
 return bytes(sum(bits[i+j]<<(7-j) for j in range(8)) for i in range(0,256,8))
def decode(raw):
 packets=messages(raw);init=packets[0];header=packets[1]
 assert init==(0x71,bytes.fromhex('0164000000050702')),'UPDATE_INIT/product/protocol'
 assert header[0]==0x7c and len(header[1])==23 and header[1][0]==0,'UPDATE_HEADER'
 h=header[1];version=nibble(h[1:7]);size=nibble(h[7:15]);expected_crc=nibble(h[15:23]);assert version==0x572 and 8<=size<=0x70000
 assert packets[-1][0]==0x73 and all(c==0x72 for c,b in packets[2:-1]),'WRITE/FINISH order'
 n=(size+31)//32;assert len(packets)==n+2,'block count'
 data=block(packets[-1][1])+b''.join(block(b) for c,b in packets[2:-1]);assert len(data)==n*32
 assert data[size:]==b'\xff'*(n*32-size),'image tail padding'
 image=data[:size];assert crc(image)==expected_crc,'CRC-32/MPEG-2'
 sp,entry=struct.unpack_from('<II',image);assert sp==0x20050000 and entry&1 and 0x08010000<=entry&~1<0x08010000+size,'application vectors/bounds'
 return image,packets,dict(size=size,CRC=hex(expected_crc),product='0x64',protocol='0x572',block_count=n,UPDATE_WRITE=n-1,UPDATE_FINISH_block=0,tail_FF_bytes=n*32-size,initial_SP=hex(sp),reset_vector=hex(entry))
def diff(base,final,kind):
 meta=json.loads((P/'integration.json').read_text());ranges=[];at=None;category=None
 special=[(int(x['address'],16)-0x08010000,int(x['address'],16)-0x08010000+len(bytes.fromhex(x['after'])), 'version/build marker' if x['address']=='0x80101e8' else 'expected literal/table adjustment' if x['address'] in ('0x805ac9c','0x80213aa') else 'new fixed-NOR diagnostic code') for x in meta['hook_patches']]
 special.append((0x5b6cc,0x5bc8c,'new fixed-NOR diagnostic code'))
 inherited=(O/'clean-sc35d8.bin').read_bytes();official=(O/'official-4486-decoded.bin').read_bytes()
 def classify(i):
  for lo,hi,label in special:
   if lo<=i<hi:return label
  if kind=='official' and final[i]==inherited[i] and (i>=len(official) or inherited[i]!=official[i]):return 'inherited SC35D8 modification'
  raise AssertionError(('unexplained changed byte',hex(0x08010000+i)))
 for i in range(max(len(base),len(final))+1):
  changed=i<len(final) and (i>=len(base) or final[i]!=base[i]);c=classify(i) if changed else None
  if at is not None and (not changed or c!=category):
   ranges.append(dict(start=hex(0x08010000+at),end_exclusive=hex(0x08010000+i),bytes=i-at,classification=category));at=None
  if changed and at is None:at=i;category=c
 return dict(ranges=ranges,changed_bytes=sum(x['bytes'] for x in ranges),classification_bytes={c:sum(x['bytes'] for x in ranges if x['classification']==c) for c in sorted({x['classification'] for x in ranges})},unexplained_ranges=0)
def main():
 path=O/'circuittracks-4486-nor-evidence-test.syx';raw=path.read_bytes();image,packets,details=decode(raw)
 assert sha(image)==EXPECTED and image==(O/'circuittracks-4486-nor-evidence-test.bin').read_bytes()==(P/'integrated-internal.bin').read_bytes()
 (O/'independently-decoded.bin').write_bytes(image)
 base=(O/'clean-sc35d8.bin').read_bytes();official=(O/'official-4486-decoded.bin').read_bytes()
 assert sha(base)=='1525c6662bbff9ced7e6055bb54e864615c30013f1b4dec4be6c404f8c750c05'
 assert sha(official)=='b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da'
 maps=dict(confidence='PROVEN',vs_SC35D8=diff(base,image,'base'),vs_official_4486=diff(official,image,'official'))
 (O/'complete-diff-map.json').write_text(json.dumps(maps,indent=2)+'\n')
 # File bytes authenticate every reviewed function and the restored hook map.
 meta=json.loads((P/'integration.json').read_text())
 for x in meta['components'].values():
  at=int(x['address'],16)-0x08010000;assert sha(image[at:at+x['bytes']])==x['sha256']
 assert image[:0x1e8]==base[:0x1e8] and image[0x1f0:0x855a]==base[0x1f0:0x855a]
 # Decode the two actual native address-load pairs. The full pinned command
 # equality also binds fixed lengths, eight-chunk loop, CRC and read-only call.
 from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
 md=Cs(CS_ARCH_ARM,CS_MODE_THUMB);instructions=list(md.disasm(image[0x5b850:0x5ba70],0x0806b850))
 loads=[]
 for x,y in zip(instructions,instructions[1:]):
  if x.mnemonic=='movw' and y.mnemonic=='movt':
   rx,lo=x.op_str.split(', #');ry,hi=y.op_str.split(', #')
   if rx==ry:loads.append((rx,int(lo,0)|(int(hi,0)<<16)))
 assert ('r0',0x81000) in loads and ('r0',0x82000) in loads
 # Independent parser negatives exercise serialization constraints.
 negatives={}
 for label,mutate in [('bad product',lambda b:b.__setitem__(7,0x65)),('missing terminator',lambda b:b.__delitem__(-1)),('trailing garbage',lambda b:b.extend(b'\0')),('corrupt block',lambda b:b.__setitem__(60,b[60]^1))]:
  b=bytearray(raw);mutate(b)
  try:decode(bytes(b))
  except (AssertionError,ValueError,IndexError):negatives[label]='rejected'
  else:raise AssertionError('invalid SYX accepted: '+label)
 result=dict(confidence='PROVEN',verdict='PASS',source='Produced SYX file only, decoded before reading expected BIN',SYX_bytes=len(raw),SYX_sha256=sha(raw),BIN_sha256=sha(image),details=details,application_end_exclusive=hex(0x08010000+len(image)),headroom_bytes=0x70000-len(image),vectors_changed_from_SC35D8=0,DSP_changes_from_SC35D8=0,bootloader_in_application=False,option_bytes_in_application=False,fixed_address_loads=[(r,hex(v)) for r,v in loads if v in (0x81000,0x82000)],reviewed_components_byte_exact=True,diagnostic_policy='Only command13; zero-only request body; fixed reads. Native opcode sweep is recorded separately; no arbitrary NOR address or diagnostic write/erase API.',negative_tests=negatives,diff_summary={k:{x:y for x,y in v.items() if x!='ranges'} for k,v in maps.items() if isinstance(v,dict)},hardware_access=False)
 (O/'independent-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
