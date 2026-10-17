"""Use observed SPI-delivered init data; execute original DSP init/job code."""
from pathlib import Path
import json,subprocess
O=Path(__file__).resolve().parent;REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
m=json.loads((O/'peer-memory.json').read_text())['memory'];lines=['LOADP loaded-core0.be24 0','MAX 2000000','PC 107','STOP 25f3','RUN']
for space,words in m.items():
 for a,v in words.items():
  if not (space=='Y' and int(a,16)==0x2c):lines.append(f'{space} {int(a,16):x} {int(v,16):06x}')
lines+=['STOP 113','RUN','DUMPY 2b 3','P 7000 0bf080 001c53 0c7002']
for selector,word in [(2,0x080002),(3,0x094403),(4,0x0a8804),(5,0x0bcc05)]:
 lines += [f'Y 2c {word:06x}']
 for i in range(32 if selector==2 else 1024):
  lines+=['PC 7000','STOP 7002','RUN','DUMPY 2c 2']
  if i in (0,31,127,255,511,1023):lines+=['DUMPX 42 2','DUMPX 1b15 1']
(O/'peer-mailbox-observed-job.txt').write_text('\n'.join(lines)+'\n')
r=subprocess.run([str(REF/'ext/bin/dsptool.exe'),'run','peer-mailbox-observed-job.txt'],cwd=O,capture_output=True,text=True)
(O/'peer-mailbox-observed-output.txt').write_text(r.stdout+r.stderr);print('Native DSP mailbox probe saved; lines',len(r.stdout.splitlines()))
