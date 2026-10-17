"""Stock first, diagnostic second. No firmware output, hardware or SDMMC model."""
import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
from trace import run
from svc import SVC
O=Path(__file__).resolve().parent
if __name__=='__main__':
 for variant in sys.argv[1:] or ['stock','diagnostic']:
  model=SVC()
  row=run('bootloader',variant,clock_model=True,nor_init=True,nor_identity=True,tick_model=True,limit=600000,svc_model=model)
  (O/f'{variant}.json').write_text(json.dumps(row,indent=2)+'\n')
  print(json.dumps(dict(variant=variant,stop=row['stop'],svc=model.result),indent=2),flush=True)
  assert model.returned and row['stop']['kind']=='next unsupported pending PendSV boundary'
