"""Existing strict-flow DSP emulator, kept alive across all observed SHI jobs."""
from pathlib import Path
import subprocess,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1]
class NativeDSP:
 def __init__(self,memory,output_dir=O):
  self.O=Path(output_dir)
  self.job=(self.O/'native-dsp-job.txt').open('w');self.out=(self.O/'native-dsp-output.txt').open('w');self.err=(self.O/'native-dsp-error.txt').open('w')
  self.p=subprocess.Popen([str(R/'builds/phase24-init-transition/coupled.exe'),'-'],cwd=self.O,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.err,text=True,bufsize=1)
  self.turns=0;self.pending=[]
  self.send(['FLOW 1','CORE 1','LOADP loaded-core1.be24 0','PC 100','STOP 10e','RUN','CORE 0','LOADP loaded-core0.be24 0',
   'REGION stock-delay 80000 100000 ffff00','REGION generated 100000 42a000 ffff00','REGION capture e80000 ea8800 ffff00','PC 107','STOP 25f3','COUPLE'])
  # Only bytes already delivered on this live ARM run's wire are admitted.
  lines=[]
  for sp,words in memory.items():
   for a,v in words.items():
    if not(sp=='Y' and a==0x2c):lines.append(f'{sp} {a:x} {v:06x}')
  self.send(lines+['STOP 113','COUPLE','SNAP'])
 def send(self,lines):
  self.job.write('\n'.join(lines)+'\n');self.job.flush();self.p.stdin.write('\n'.join(lines+['SYNC'])+'\n');self.p.stdin.flush();rows=[]
  while True:
   line=self.p.stdout.readline()
   if not line:raise RuntimeError('native DSP model stopped: '+(self.O/'native-dsp-error.txt').read_text())
   if line.strip()=='SYNC':break
   self.out.write(line);rows.append(line.rstrip())
  self.out.flush();return rows
 def write(self,sp,a,v):self.pending.append(f'{sp} {a:x} {v:06x}')
 def flush(self):
  if self.pending:self.send(['CORE 0']+self.pending);self.pending=[]
 def turn(self):
  self.flush();self.send(['CORE 0','TURN 113']);self.turns+=1
 def read(self,sp,a):
  self.flush();rows=self.send(['CORE 0',f'DUMP{sp} {a:x} 1'])
  return int(next(s.split(':',1)[1] for s in rows if s.startswith(f'0 {sp} ')),16)
 def close(self):
  if self.p.poll() is None:self.p.stdin.close();self.p.wait(timeout=30)
  self.job.close();self.out.close();self.err.close()
