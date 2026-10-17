"""Bounded actual IRQ service for data-free NOR initialization commands only."""
from trace import *
rows=[]
for variant in ('stock','diagnostic'):
 for entry in ('application','bootloader'):
  row=run(entry,variant,clock_model=True,nor_init=True,limit=600000)
  rows.append(row);print(json.dumps(dict(variant=variant,entry=entry,stop=row['stop'],commands=row['NOR_commands'],IRQs=row['native_IRQs']),indent=1),flush=True)
(O/'nor-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
identity_rows=[]
for variant in ('stock','diagnostic'):
 for entry in ('application','bootloader'):
  row=run(entry,variant,clock_model=True,nor_init=True,nor_identity=True,limit=600000)
  identity_rows.append(row)
  print(json.dumps(dict(variant=variant,entry=entry,reference_part_identity='C22019, documented MX25L25645G; not observed user unit',stop=row['stop'],commands=row['NOR_commands'][-3:]),indent=1),flush=True)
(O/'reference-identity-progress.json').write_text(json.dumps(identity_rows,indent=2)+'\n')
