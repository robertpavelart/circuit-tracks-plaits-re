"""Prepare offline-only DSP scripts; never create an application image."""
import json,math,subprocess,sys
from environment import ROOT,REF,sha,MAN,authentic_session
OUT=ROOT/'builds/phase20j-coupled-replay'
EXE=OUT/'coupled.exe'
DS=REF/'ext/bin/dsptool.exe'
def asm(lines):
 r=subprocess.run([str(DS),'asm'],input='\n'.join(lines)+'\n',capture_output=True,text=True,check=True)
 words=[]
 for l in r.stdout.splitlines():
  assert not l.startswith('ERR'),(lines,l)
  words+=l.split()[1:]
 return ' '.join(words)
def run(name,ls):
 d=OUT/name;d.mkdir(exist_ok=True);(d/'job.txt').write_text('\n'.join(ls)+'\n')
 r=subprocess.run([str(EXE),'job.txt'],cwd=d,capture_output=True,text=True)
 (d/'output.txt').write_text(r.stdout+r.stderr)
 print(name,'exit',r.returncode,r.stdout[-700:],r.stderr[-700:],flush=True)
 return r
def probes():
 p=asm(['move #>$ffffff,m0','move #>$340000,r0','move #>$5a1234,x0','move x0,y:(r0)+','move #>$ab5678,x0','move x0,y:(r0)','move y:(r0)-,x1','move y:(r0),y0','move #>$e80000,r0','move x0,y:(r0)','nop'])
 # Explicit stop at length of actual snippet, not the diagnostic jmp target.
 n=len(p.split())-1
 ls=['REGION ring 340000 380000 ffff00','REGION capture e80000 ea8800 ffff00',f'P 7000 {p}','PC 7000',f'STOP {0x7000+n:x}','RUN','DUMPY 340000 2','DUMPY e80000 1','CORE 1','DUMPX 340000 2','DUMPY e80000 1']
 r=run('address-probe',ls);assert r.returncode==0
 assert r.stdout.count('5a1200 ab5600')==2 and r.stdout.count('ab5600')==4
 # Unknown and undeclared data must fail instead of returning zero.
 for name,cmd in [('unknown','DUMPY 340001 1'),('unbacked','DUMPY 380000 1')]:
  r=run('reject-'+name,['REGION ring 340000 380000 ffff00',cmd]);assert r.returncode==3
 p=asm(['move #>3,m0','move #>$340003,r0','move #>$123456,x0','move x0,y:(r0)+','move #>$654321,x0','move x0,y:(r0)+','nop'])
 r=run('modulo-probe',['REGION ring 340000 380000 ffff00','P 7000 '+p,'PC 7000',f'STOP {0x7000+len(p.split())-1:x}','RUN','DUMPY 340003 1','DUMPY 340000 1'])
 assert r.returncode==0 and '123400' in r.stdout and '654300' in r.stdout
 for name,code in [('branch','0af080 003bba'),('inner-do','060280 007004 0af080 003bba 000000')]:
  r=run('reject-'+name,['P 7000 '+code,'FREE 3bba','AUDIT','PC 7000','STOP 7005','RUN']);assert r.returncode==3 and 'FREE_P_EXECUTION' in r.stderr
 r=run('reject-pwrite',['AUDIT','P 3bba 123456']);assert r.returncode==3 and 'CANDIDATE_P_WRITE' in r.stderr
 r=run('reject-deadlock',['P 7000 0af080 007000','MAX 1000','PC 7000','STOP 7002','RUN']);assert r.returncode==3 and 'DEADLOCK_OR_INSTRUCTION_LIMIT' in r.stderr
def job(blocks=8,profile='original',prepare_only=False):
 w=json.loads((ROOT/'builds/phase20i-authentic-qualification/authentic-ARM-workload.json').read_text())
 d=OUT/f'{profile}-{blocks}';d.mkdir(exist_ok=True)
 p=ROOT/('builds/phase20d-midi-vpre/fixture/reference-core0.be24' if profile=='original' else 'builds/phase20g-dual-allocation/osc_only.be24')
 # Existing analysis streams copied byte-for-byte, no wait NOPs.
 for src,name in [(p,'core0.be24'),(ROOT/'builds/phase20g-dual-allocation/retained-core1.be24','core1.be24')]:
  (d/name).write_bytes(src.read_bytes())
 ls=['CORE 0','LOADP core0.be24 0','CORE 1','LOADP core1.be24 0','PC 100','STOP 10e','RUN','CORE 0',
     'REGION stock-delay 80000 100000 ffff00','REGION wave-pair 173000 175000 ffff00','REGION ring 340000 380000 ffff00','REGION capture e80000 ea8800 ffff00','PC 107','STOP 25f3','COUPLE']
 def writes(ws):
  for core,sp,a,v in ws:ls.extend([f'CORE {core}',f'{sp.upper()} {a:x} {v&0xffffff:06x}'])
 writes(w['init_writes']);ls+=['CORE 0','PC 25f3','STOP 113','COUPLE']
 for _,ws in w['initial_events']:writes(ws)
 s=authentic_session();s.events=[]
 lv={k:int(v,16) for k,v in MAN['report']['vcf20']['labels'].items()}
 s.capture('retained MIDI1 line enable',lv['c_vset'],0,1)
 if 'c_vsetosc' in lv:s.capture('retained MIDI1 oscillator disable',lv['c_vsetosc'],0,0)
 for msg in (bytes([0x90,60,100]),bytes([0x91,67,100]),bytes([0x99,36,100])):s.midi(msg)
 s.capture('actual retained-mode service',lv['c_vtick'])
 (d/'additional-ARM-stimulus.json').write_text(json.dumps(dict(events=s.events,scope='Actual ARM calls on authentic snapshot; reference SPI read replies remain modeled zero; voice allocation and routing require verification'),indent=2))
 for _,ws in s.events:writes(ws)
 n=p.stat().st_size//3
 ls+=['CORE 0','P 7000 0bf080 0001ed 0c7002',f'P {n:x} '+' '.join(['5a1234']*(0x4000-n)),f'FREE {n:x}','TRACE traffic.txt','AUDIT']
 for f in w['frames'][:blocks]:
  for _,ws in f['events']:writes(ws)
  b=f['block'];ring=[int(0x80000*math.sin(2*math.pi*(220+110*t)*(32*b+i)/48000))&0xffffff for i in range(32) for t in (0,1)]
  ls+=['CORE 0',f'BLOCK {b}','Y ffd 001000','Y 1000 '+' '.join(f'{v:06x}' for v in ring),'PC 7000','STOP 7002','COUPLE','DUMPX 2e10 64','DUMPY 800 64','DUMPX 2df0 32','DUMPX 2e50 32','DUMPX 37000 10','CHECK','SUMMARY']
 if prepare_only:return f'{profile}-{blocks}',ls
 return run(f'{profile}-{blocks}',ls)
def synchronization(blocks=8192):
 """Primitive validation, NOT the complete retained-audio qualification.

 Actual stock handshake/gather/wait routines, actual B1.3 core1 tasks.
 Two explicitly MODELED nonzero external words and modeled MIN stimulus.
 No oscillator outputs or Layout A regression inferred from this test.
 """
 d=OUT/'sync-primitives';d.mkdir(exist_ok=True)
 for src,name in [(ROOT/'builds/phase20d-midi-vpre/fixture/reference-core0.be24','core0.be24'),(ROOT/'builds/phase20g-dual-allocation/retained-core1.be24','core1.be24')]:
  (d/name).write_bytes(src.read_bytes())
 ls=['CORE 0','LOADP core0.be24 0','CORE 1','LOADP core1.be24 0','PC 100','STOP 10e','RUN','CORE 0','REGION fixture 173000 173002 ffff00','REGION ring 340000 380000 ffff00',
 'Y 173000 5a1234 ab5678','X 3a 000002']
 code='0bf080 000766 '+asm(['move #>$173000,x0','move x0,x:>$30002','move #>$173001,x0','move x0,x:>$30003','move #>$30004,x0','move x0,x:>$30000','move #>0,x0'])+' 0bf080 000775 000000'
 stop=0x7000+len(code.split())-1
 ls+=['P 7000 '+code,'FREE 4000','AUDIT']
 # Full memory access tracing for first/last blocks; all accesses still pass
 # through callbacks, counters and guard checks during unlogged blocks.
 for b in range(blocks):
  ls+=['CORE 0',f'BLOCK {b}']
  if b==0:ls+=['TRACE first-traffic.txt']
  if b==1:ls+=['TRACEOFF']
  if b==blocks-1:ls+=['TRACE last-traffic.txt']
  ls+=['PC 7000',f'STOP {stop:x}','COUPLE','DUMPX 30002 2',f'X 37000 {b+1:06x}',
       'X 37100 '+' '.join(f'{((b+1)*0x100+i*0x100)&0xffffff:06x}' for i in range(64)),
       'CORE 1','STEPS 2048','CORE 0','DUMPX 30002 2','DUMPX 37000 10',f'DUMPY {0x340000+(32*b)%0x20000:x} 32',f'DUMPY {0x360000+(32*b)%0x20000:x} 32','CHECK','SUMMARY']
 r=run('sync-primitives',ls)
 exact=r.stdout.count('0 X 030002: 5a1200 ab5600');checks=r.stdout.count('CHECK ')
 dumps=[l for l in r.stdout.splitlines() if l.startswith('0 X 030002:')]
 immediate=sum('5a1200 ab5600' in l for l in dumps[::2]);eventual=sum('5a1200 ab5600' in l for l in dumps[1::2])
 ring=[l for l in r.stdout.splitlines() if l.startswith('0 Y ')]
 ring_ok=0
 for b in range(blocks):
  for t in (0,1):
   expected=[((b+1)*0x100+(2*i+t)*0x100)&0xffff00 for i in range(32)]
   assert [int(v,16) for v in ring[2*b+t].split(':')[1].split()]==expected,(b,t)
  ring_ok+=1
 (d/'result.json').write_text(json.dumps(dict(blocks=blocks,exit=r.returncode,passed=r.returncode==0 and immediate==blocks and checks==blocks,exact_gather_at_stock_wait_return=immediate,exact_gather_after_additional_service=eventual,exact_ring_blocks=ring_ok,canary_checks=checks,input_authenticity='MODELED test words and modeled master MIN; not an audio qualification',program_sha256={name:sha((d/name).read_bytes()) for name in ('core0.be24','core1.be24')}),indent=2))
 assert r.returncode==0
 assert immediate==blocks,('Retained failing rapid-publication regression',immediate,blocks)
 assert checks==blocks
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='probe':probes()
 elif len(sys.argv)>1 and sys.argv[1]=='sync':synchronization()
 else:job(int(sys.argv[1]) if len(sys.argv)>1 else 8)

