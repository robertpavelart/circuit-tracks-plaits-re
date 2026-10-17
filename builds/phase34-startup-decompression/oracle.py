"""Independent byte-level scatter decompression oracle; never injects output."""
from trace import *

def decode(source):
 at=0;out=bytearray();tokens=0
 def byte():
  nonlocal at
  assert at<len(source);v=source[at];at+=1;return v
 while at<len(source):
  token=byte();tokens+=1;literal=token&3
  if literal==0:literal=byte()+3
  match=token>>4
  if match==15:match=byte()+15
  # Native loop enters at SUBS before its first literal copy: encoded bias1.
  for _ in range(literal-1):out.append(byte())
  if match:
   low=byte();high=(token>>2)&3
   if high==3:high=byte()
   offset=low+(high<<8)
   assert 0<offset<=len(out),(at,offset,len(out))
   for _ in range(match+2):out.append(out[-offset])
 return bytes(out),dict(tokens=tokens,source_bytes=at,output_bytes=len(out),dictionary='Only bytes already emitted in same block; no external history')

def main():
 rows=json.loads((O/'corrected-trace.json').read_text());results=[]
 for row in rows:
  e=Cold(row['variant']);u=e.uc
  for block in row['blocks']:
   src=int(block['compressed_source'],16);source=bytes(u.mem_read(src,block['compressed_bytes']))
   data,stats=decode(source)
   assert sha(source)==block['source_sha256'] and sha(data)==block['output_sha256'] and len(data)==block['output_bytes']
   results.append(dict(entry=row['entry'],variant=row['variant'],hooks=row['hooks'],**stats,output_sha256=sha(data),native_match=True,output_injected=False))
 (O/'oracle.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=1))
if __name__=='__main__':main()
