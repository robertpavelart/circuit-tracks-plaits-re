"""Unmodified published B1.3 control, distinct from official-stock control."""
from trace import *
rows=[]
for entry in ('application','bootloader'):
 row=run(entry,'B13',clock_model=True,nor_init=True,nor_identity=True,tick_model=True,limit=600000)
 rows.append(row)
(O/'B13-control.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([dict(entry=x['entry'],stop=x['stop'],runtime=x['runtime_fields']) for x in rows],indent=1))
