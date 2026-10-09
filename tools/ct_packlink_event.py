"""Read only already identified pack event bytes; export no telemetry identifiers.
Historical events are not a decoded current LevelDB state or device selection.
"""
import argparse,json,re
from pathlib import Path
from ct_stock_load_audit import ROOT,sha,verify_inputs
def collect(out,source):
 out=out.resolve();base=(ROOT/'builds/phase19c-packlink').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh PACKLINK child required')
 verify_inputs();before=source.stat();raw=source.read_bytes();after=source.stat()
 assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 records=[]
 for m in re.finditer(rb'"events"\s*:\s*',raw):
  try:v,end=json.JSONDecoder().raw_decode(raw[m.end():].decode('latin1'));events=json.loads(v)
  except (ValueError,TypeError):continue
  if not isinstance(events,list):continue
  for e in events:
   s=e.get('segmentation',{})
   if e.get('key')=='sendPack' and s.get('product')=='Circuit Tracks':
    records.append(dict(byte_offset=m.start(),key=e['key'],product=s['product'],
     pack_name=s.get('name'),destination_packId=s.get('packId'),pack_type=s.get('type'),
     timestamp=e.get('timestamp'),meaning='Historical queued app event; current native selection UNRESOLVED'))
 out.mkdir(parents=True)
 for n,v in [('events.json',records),('provenance.json',dict(source=str(source),source_sha256=sha(raw),
  size=len(raw),mtime_ns=before.st_mtime_ns,offline=True,authoritative_current_state=False,
  user_modified=False,private_telemetry_ids_exported=False))]:
  with (out/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(records,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True,type=Path)
 p.add_argument('--output-dir',required=True,type=Path);a=p.parse_args();collect(a.output_dir,a.source)
