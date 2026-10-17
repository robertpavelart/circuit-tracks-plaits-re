"""Run final local evidence scripts in dependency order, outputs phase34 only."""
from pathlib import Path
import subprocess,sys,json,time
O=Path(__file__).resolve().parent
rows=[]
for name in ('isolate.py','fault_detail.py','trace.py','oracle.py','instruction_control.py','poison_control.py','clock_progress.py','nor_progress.py','tick_progress.py','baseline_control.py','restart_prefix.py'):
 start=time.monotonic();p=subprocess.run([sys.executable,'-B',str(O/name)],capture_output=True,text=True)
 rows.append(dict(script=name,exit_code=p.returncode,elapsed_seconds=round(time.monotonic()-start,3)))
 if p.returncode:
  print(p.stdout);print(p.stderr);raise RuntimeError(name)
 print(name+' complete',flush=True)
(O/'run-log.json').write_text(json.dumps(rows,indent=2)+'\n')
