"""Reproduce old hook fault with descriptor/call-chain/state evidence."""
from trace import *
rows=[run(entry,variant,'legacy') for variant in ('stock','diagnostic') for entry in ('bootloader','application')]
(O/'legacy-fault-detail.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([dict(entry=x['entry'],variant=x['variant'],stop=x['stop'],registers=x['registers'],blocks=x['blocks']) for x in rows],indent=1))
