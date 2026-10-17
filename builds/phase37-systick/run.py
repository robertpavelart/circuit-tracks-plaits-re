"""Native stock first; diagnostic only follows a completed stock control."""
import sys,json
sys.dont_write_bytecode=True
from trace import run
from systick import TickModel,O
if __name__=='__main__':
 for variant in sys.argv[1:] or ['stock','diagnostic']:
  m=TickModel();row=run('bootloader',variant,clock_model=True,nor_init=True,nor_identity=True,tick_model=True,limit=600000,svc_model=m)
  row.update(PendSV=m.switches,SysTick=m.ticks,SysTick_configuration=m.config,clock_MMIO=m.clock_mmio,final_architecture=m.final_state)
  (O/f'{variant}.json').write_text(json.dumps(row,indent=2)+'\n')
  print(json.dumps(dict(variant=variant,stop=row['stop'],ticks=len(m.ticks),switches=len(m.switches),final=m.final_state),indent=2),flush=True)
  assert m.ticks and all(x.get('frame_consumptions')==1 for x in m.ticks),'SysTick incomplete'
  assert all(x.get('frame_consumptions')==1 for x in m.switches),'PendSV incomplete'
  assert row['stop']['kind']=='missing authentic QSPI response','unexpected final boundary'
