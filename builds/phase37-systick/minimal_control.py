"""Ablate detailed native exception observers; compare full final state."""
import json,sys
sys.dont_write_bytecode=True
from trace import run
from systick import TickModel,O
m=TickModel(audit=False)
row=run('bootloader','stock',clock_model=True,nor_init=True,nor_identity=True,tick_model=True,limit=600000,svc_model=m)
row.update(PendSV=m.switches,SysTick=m.ticks,SysTick_configuration=m.config,clock_MMIO=m.clock_mmio,final_architecture=m.final_state)
(O/'stock-minimal-observer.json').write_text(json.dumps(row,indent=2)+'\n')
base=json.loads((O/'stock.json').read_text())
assert row['stop']==base['stop'] and row['RAM_sha256']==base['RAM_sha256'] and row['final_architecture']==base['final_architecture']
for a,b in zip(row['PendSV'],base['PendSV']):
 for k in ('captured','incoming','before_return','restored','outgoing_saved_PSP'):assert a[k]==b[k],k
for a,b in zip(row['SysTick'],base['SysTick']):
 for k in ('captured','before_return','restored','after','legacy_comparison'):assert a[k]==b[k],k
print('Detailed/minimal observers match complete final SRAM, exception boundaries, task choices, SysTick effects and final CPU state')
