"""Observer ablation: no instruction register/memory diff observer in PendSV."""
import sys,json
sys.dont_write_bytecode=True
from trace import run
from pendsv import Model,O
m=Model(audit=False)
row=run('bootloader','stock',clock_model=True,nor_init=True,nor_identity=True,tick_model=True,limit=600000,svc_model=m)
row['PendSV']=m.switches
(O/'stock-minimal-observer.json').write_text(json.dumps(row,indent=2)+'\n')
baseline=json.loads((O/'stock.json').read_text())
assert row['stop']==baseline['stop'] and row['RAM_sha256']==baseline['RAM_sha256']
for k in ('captured','incoming','before_return','restored','outgoing_saved_PSP','outgoing_software_frame_hex','post_return_trace'):
 assert row['PendSV'][0][k]==baseline['PendSV'][0][k],k
print('Detailed observer and minimal native control agree on complete SRAM, CPU/context boundaries, incoming constructor frame and post-return prefix')
