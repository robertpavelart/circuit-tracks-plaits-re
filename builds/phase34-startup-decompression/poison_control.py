"""No dictionary/history injection: the true decompressor overwrites poison."""
from trace import *
rows=[run(entry,variant,poison=True) for variant in ('stock','diagnostic') for entry in ('bootloader','application')]
for row in rows:
 b=row['blocks'][0];assert b['returned'] and set(bytes.fromhex(b['RAM_before']))=={0xa5}
(O/'poison-control.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Four poisoned-SRAM native decompression controls returned normally')
