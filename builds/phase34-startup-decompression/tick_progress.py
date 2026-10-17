"""Pre-scheduler ideal periodic SysTick, executing native handlers only.
No SVC/PendSV/RTOS context switching is fabricated if exception service stops.
"""
from trace import *
rows=[]
for variant in ('stock','diagnostic'):
 for entry in ('application','bootloader'):
  row=run(entry,variant,clock_model=True,nor_init=True,nor_identity=True,tick_model=True,limit=600000)
  rows.append(row);print(json.dumps(dict(variant=variant,entry=entry,stop=row['stop'],milestones=list(row['milestones']),native_interrupts=len(row['native_IRQs'])),indent=1),flush=True)
(O/'tick-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
