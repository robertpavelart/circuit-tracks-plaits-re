"""Address, writer, reader, latency and local artifact evidence for stock waves."""
import collections,hashlib,json,os,re,struct,subprocess,zipfile
from pathlib import Path
from environment import ROOT,REF,STOCK,sha
OUT=ROOT/'builds/phase20k-stock-wavetable'
def inventory():
 roots=[REF,Path(r'C:\Proj SSD\CODEX\Origin Backup SD'),ROOT/'firmware',ROOT/'builds/phase19b/documentation']
 records=[];counts=collections.Counter();suffixes={'.bin','.syx','.wav','.cpb','.ncs','.raw','.pcm','.rom','.img','.dat','.pdf'}
 for root in roots:
  for folder,dirs,files in os.walk(root):
   dirs[:]=[d for d in dirs if d not in ('.git','__pycache__','node_modules')]
   for n in files:
    p=Path(folder)/n;counts[p.suffix.lower()]+=1
    if p.suffix.lower() not in suffixes:continue
    # Dependency test media/databases are indexed but cannot supply application
    # lookup data without a traced firmware dependency. Avoid hashing compiler
    # databases and unrelated wxWidgets resources as authentic device content.
    dependency='ext/dsp56300/' in p.as_posix()
    if dependency:
     records.append(dict(path=str(p),bytes=p.stat().st_size,classification='DEPENDENCY SOFTWARE/TEST DATA; no stock loading edge',sha256=None));continue
    h=hashlib.sha256()
    with p.open('rb') as f:
     while b:=f.read(1024*1024):h.update(b)
    records.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest(),header=p.open('rb').read(16).hex(),classification='LOCAL SOURCE CANDIDATE; filename is not provenance'))
 archive=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main.zip');zrec=[]
 if archive.exists():
  with zipfile.ZipFile(archive) as z:
   for f in z.infolist():
    if Path(f.filename).suffix.lower() in suffixes:zrec.append(dict(path=f.filename,bytes=f.file_size,CRC32=f'{f.CRC:08x}'))
 (OUT/'artifact-inventory.json').write_text(json.dumps(dict(roots=[str(p) for p in roots],suffix_counts=counts,files=records,archive=str(archive),archive_candidates=zrec),indent=2))
 print('Inventory',len(records),'binary/content candidates, archive',len(zrec),flush=True)
def summarize():
 a=json.loads((OUT/'recovered.json').read_text());b=json.loads((OUT/'recovered-stock.json').read_text())
 assert a['families']==b['families'] and a['DSP_words_BE24_sha256']==b['DSP_words_BE24_sha256']
 # Original instruction source and constants; both DSP programs retain the
 # complete stock generation routines despite unrelated B1.3 hook patches.
 orig=(OUT/'generation-stock/core0.be24').read_bytes();mod=(OUT/'generation/core0.be24').read_bytes()
 assert orig[0x1c53*3:0x1e15*3]==mod[0x1c53*3:0x1e15*3]
 (OUT/'source-DSP-generators.be24').write_bytes(orig[0x1c53*3:0x1e15*3])
 (OUT/'source-ARM-constructor.bin').write_bytes(STOCK[0x25e28:0x25f18])
 (OUT/'source-first-coefficient.bin').write_bytes(STOCK[0x19678:0x1967c])
 writer_stats={};target={};job=-1
 for l in (OUT/'generation/generation-traffic.txt').open():
  t=l.split()
  if len(t)!=8:continue
  _,c,pc,sp,addr,op,v,origin=t;addr=int(addr,16);v=int(v,16)
  if sp=='Y' and addr==0x2c and op=='W' and origin=='HOST':job+=1;writer_stats[job]=collections.Counter()
  if sp=='Y' and op=='W' and 0x100000<=addr<0x179800:
   writer_stats[job][addr]+=1
   if 0x173000<=addr<0x175000:assert addr not in target;target[addr]=(pc,v)
 assert len(target)==8192 and {pc for pc,v in target.values()}=={'001ddf'}
 raw=b''.join(target[addr][1].to_bytes(3,'big') for addr in range(0x173000,0x175000))
 (OUT/'issued-stores.be24').write_bytes(raw)
 packed=b''.join((target[addr][1]>>8).to_bytes(2,'big') for addr in range(0x173000,0x175000))
 (OUT/'external-words.be16').write_bytes(packed)
 loaded=b''.join((int.from_bytes(packed[i:i+2],'big')<<8).to_bytes(3,'big') for i in range(0,len(packed),2))
 assert loaded==(OUT/'generation/tables.be24').read_bytes()
 # Observe exact consumption, including per-bank stock raw mono output.
 reads=collections.Counter();lat0=[];lat1=[];block_age=[];group=0;gen={};master=[];first=None
 for l in (OUT/'strict-64/traffic.txt').open():
  t=l.split()
  if t[:2]==['GATHER','DONE']:lat0.append(int(t[6])-int(t[4]));lat1.append(int(t[7])-int(t[5]));continue
  if t[:2]==['GATHER','CONSUME']:block_age.append(int(t[2])-int(t[5]));continue
  if len(t)!=8:continue
  block,c,pc,sp,addr,op,v,origin=t;block=int(block);addr=int(addr,16);v=int(v,16)
  if c=='1' and sp=='X' and op=='R' and 0x173000<=addr<0x175000:
   expected=int.from_bytes(loaded[3*(addr-0x173000):3*(addr-0x173000)+3],'big');assert v==expected;reads[pc]+=1
  if c=='0' and sp=='X' and addr==0xcc and op=='W':group=v
  if c=='0' and pc=='0009d8' and sp=='X' and 0x2c46<=addr<0x2c66 and op=='W':
   k=f'group{group}';s=gen.setdefault(k,dict(samples=0,nonzero=0,peak=0,first_nonzero_block=None));s['samples']+=1;s['nonzero']+=v!=0;s['peak']=max(s['peak'],abs(v-0x1000000 if v&0x800000 else v))
   if v and s['first_nonzero_block'] is None:s['first_nonzero_block']=block
 for l in (OUT/'strict-64/output.txt').read_text().splitlines():
  if l.startswith('0 X 002e10:'):master += [int(v,16) for v in l.split(':')[1].split()]
 result=dict(recovery=a,source_program_generator_bytes_identical=True,writer_ranges={j:dict(start=hex(min(v)),end_inclusive=hex(max(v)),distinct_words=len(v),stores=sum(v.values())) for j,v in writer_stats.items()},target_writer_PC='001DDF',target_reader_PC_counts=reads,issued_store_sha256=sha(raw),packed_BE16_sha256=sha(packed),packed_bytes=len(packed),exact_loaded_read_count=sum(reads.values()),generators=gen,gather=dict(completed=len(lat0),core0_fetch_latency=[min(lat0),max(lat0)],core1_fetch_latency=[min(lat1),max(lat1)],consumptions=len(block_age),audio_block_age=sorted(set(block_age)),stale_consumptions=0),master=dict(samples=len(master),nonzero=sum(v!=0 for v in master),peak=max(master,default=0)),table_provenance='QUALIFIED',full_audio_budget='UNQUALIFIED')
 (OUT/'evidence.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':
 import sys
 if '--inventory' in sys.argv:inventory()
 else:summarize()
