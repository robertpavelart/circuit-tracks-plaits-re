"""Statistics at actual stock store sites, including transient send buffers."""
from master_path import OUT
from master_evidence import stats
from collections import defaultdict
import csv,json
SITES={0x1200:'bank_normalization',0xccd:'send_left',0xcce:'send_right',0xce0:'send_plus_input_left',0xce1:'send_plus_input_right',0x11e2:'delay_output_left',0x11e3:'delay_output_right',0xd51:'master_filter_input_left',0xd52:'master_filter_input_right',0x145f:'master_filter_output_left',0x1460:'master_filter_output_right',0x224f:'final_ring_left',0x2250:'final_ring_right'}
def extract(name):
 groups=defaultdict(list);rows=[]
 for line in (OUT/name/'traffic.txt').open():
  t=line.split()
  if len(t)!=8 or t[1]!='0' or t[5]!='W':continue
  try:b=int(t[0]);pc=int(t[2],16);a=int(t[4],16);v=int(t[6],16)
  except ValueError:continue
  if pc not in SITES:continue
  if pc==0x1200 and not (0x2df0<=a<0x2e10 or 0x2e50<=a<0x2e70):continue
  k=(b,pc,1 if pc==0x1200 and a>=0x2e50 else 0)
  q=groups[k];q.append(v)
  if len(q)==32:
   rows.append(dict(block=b,PC=f'{pc:X}',stage=SITES[pc],bank=k[2],**stats(q)));q.clear()
 with (OUT/name/'store-stage-statistics.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
 result=[]
 for pc,tag in SITES.items():
  q=[r for r in rows if r['PC']==f'{pc:X}']
  if q:result.append(dict(stage=tag,blocks_or_channels=len(q),peak=max(r['peak'] for r in q),nonzero=sum(r['nonzero'] for r in q),first_nonzero=next((r for r in q if r['nonzero']),None)))
 (OUT/name/'store-stage-summary.json').write_text(json.dumps(result,indent=2));print(name,'store-stage records',len(rows))
if __name__=='__main__':
 for name in ['before','both','mixer-send-FX-probe']:extract(name)
