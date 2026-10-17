"""Record native process exits; a printed JSON result alone is insufficient."""
from pathlib import Path
import subprocess,json,sys
O=Path(__file__).resolve().parent;rows=[]
for args,label in ((['run.py','stock'],'stock'),(['run.py','diagnostic'],'diagnostic'),(['regressions.py'],'regressions'),(['minimal_control.py'],'minimal-observer')):
 p=subprocess.run([sys.executable,'-B',str(O/args[0]),*args[1:]],capture_output=True,text=True)
 (O/f'{label}-checked-run.log').write_text(p.stdout+p.stderr,encoding='utf8')
 rows.append(dict(script=args,exit_code=p.returncode));(O/'run-log.json').write_text(json.dumps(rows,indent=2)+'\n')
 assert p.returncode==0,(label,p.returncode,p.stderr[-2000:]);print(label,'PASS',flush=True)
