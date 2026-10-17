"""Explicit ideal RCC oscillator/PLL service, separate from hook correction."""
from trace import *
rows=[]
# Stock must advance before attempting the same diagnostic fixture.
for variant in ('stock','diagnostic'):
 for entry in ('application','bootloader'):
  row=run(entry,variant,clock_model=True,limit=600000)
  rows.append(row)
  print(json.dumps(dict(variant=variant,entry=entry,stop=row['stop'],last_reads=row['last_MMIO_reads'][-3:]),indent=1),flush=True)
(O/'clock-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
