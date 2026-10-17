"""Native stock control must pass before diagnostic. No binary outputs."""
import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
from trace import run
from pendsv import Model
O=Path(__file__).resolve().parent
if __name__=='__main__':
 for variant in sys.argv[1:] or ['stock','diagnostic']:
  m=Model();row=run('bootloader',variant,clock_model=True,nor_init=True,nor_identity=True,tick_model=True,limit=600000,svc_model=m)
  row['PendSV']=m.switches
  row['post_scheduler_scope']='STOP at first due ideal-cadence SysTick, task sleep, or other unsupported boundary; no new timer/peripheral behavior implemented'
  (O/f'{variant}.json').write_text(json.dumps(row,indent=2)+'\n')
  print(json.dumps(dict(variant=variant,stop=row['stop'],switches=len(m.switches),summaries=[{k:x[k] for k in ('incoming','restored','outgoing_saved_PSP') if k in x} for x in m.switches]),indent=2),flush=True)
  assert m.switches and all(x.get('frame_consumptions')==1 for x in m.switches),'PendSV incomplete'
  assert row['stop']['kind'].startswith('next unsupported'),'new unexpected stop'
