"""Execute pinned original ARM initialization posts and original DSP generators.
No synthesized lookup payload, image builder, hardware I/O or reference writes.
"""
import json,struct,subprocess,sys
from environment import ROOT,REF,STOCK,MAN,sha,authentic_session
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R5,UC_ARM_REG_PC,UC_ARM_REG_LR
OUT=ROOT/'builds/phase20k-stock-wavetable';OUT.mkdir(exist_ok=True)
def capture():
 s=authentic_session();s.events=[];s.shi.writes=[];s.shi.raw=[]
 polls=[];stop=[]
 def h(u,a,n,d):
  if a==0x08029344 and u.reg_read(UC_ARM_REG_R1)==0x802c:
   polls.append(dict(pc=a,reply=0x80000000,classification='MODELED ready reply for recording finite ARM post sequence; replay must independently complete real DSP jobs'))
   u.reg_write(UC_ARM_REG_R0,0x80000000);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
  if a==0x08035e48 and u.reg_read(UC_ARM_REG_R5)==3:
   stop.append(dict(pc=a,index=3,reason='Bounded capture after first three jobs and their subsequent ready poll; not complete initializer'))
   u.reg_write(UC_ARM_REG_PC,0x0807ff01)
 hk=s.e.uc.hook_add(UC_HOOK_CODE,h);s.e.call(0x08035e28,maxins=1000000);s.e.uc.hook_del(hk)
 assert stop
 writes=s._take();jobs=[v for c,sp,a,v in writes if c==0 and sp=='y' and a==0x2c]
 assert jobs==[0x80002,0x94403,0xa8804],jobs
 result=dict(init_writes=s.init_writes,posts=writes,jobs=jobs,polls=polls,stop=stop,pointers=list(struct.unpack('<3I',s.e.uc.mem_read(0x20005d40,12))),raw_SHI=s.shi.raw)
 assert result['pointers']==[0x100000,0x128800,0x151000]
 (OUT/'ARM-generator-posts.json').write_text(json.dumps(result,indent=2))
 # The source coefficient values are executable-code derived; preserve the
 # original flash source separately rather than inventing a source waveform.
 (OUT/'source-init-29382.bin').write_bytes(STOCK[0x19382:0x193bc])
 return result
def run(stock=False):
 w=capture();d=OUT/('generation-stock' if stock else 'generation');d.mkdir(exist_ok=True)
 import dsp_session as DS
 data=DS.dsp_program(STOCK) if stock else (ROOT/'builds/phase20d-midi-vpre/fixture/reference-core0.be24').read_bytes()
 (d/'core0.be24').write_bytes(data)
 ls=['CORE 0','LOADP core0.be24 0','REGION stock-delay 80000 100000 ffff00','REGION generated 100000 179800 ffff00','PC 107','STOP 25f3','MAX 10000000','RUN']
 ls += [f'{sp.upper()} {a:x} {v:06x}' for c,sp,a,v in w['init_writes'] if c==0]
 ls += ['PC 25f3','STOP 113','RUN','P 7100 0bf080 001c53 0c7102','TRACE generation-traffic.txt','AUDIT','MAX 100000000']
 for c,sp,a,v in w['posts']:
  assert c==0
  ls += [f'{sp.upper()} {a:x} {v:06x}']
  if sp=='y' and a==0x2c:ls+=['SERVICE 7100','SUMMARY']
 ls += ['SAVEY wave0.be24 100000 10000','SAVEY wave1.be24 128800 24000','SAVEY wave2.be24 151000 24000','SAVEY tables.be24 173000 2000','DUMPY 173000 16','DUMPY 174000 16']
 (d/'job.txt').write_text('\n'.join(ls)+'\n')
 r=subprocess.run([str(ROOT/'builds/phase20j-coupled-replay/coupled.exe'),'job.txt'],cwd=d,capture_output=True,text=True)
 (d/'output.txt').write_text(r.stdout+r.stderr);print(r.stdout[-2000:],r.stderr[-1000:]);assert r.returncode==0
 raw=(d/'tables.be24').read_bytes();assert len(raw)==0x2000*3
 seed=[v for c,sp,a,v in w['init_writes'] if c==0 and sp=='x' and 0xc00<=a<0x1000]
 assert len(seed)==1024 and all(v==min(0x7fffff,(1<<23)//(i+1)) for i,v in enumerate(seed))
 (OUT/'source-coefficients.be24').write_bytes(b''.join(v.to_bytes(3,'big') for v in seed))
 result=dict(stock_sha256=sha(STOCK),DSP_program_sha256=sha(data),source_code_sha256=sha((OUT/'source-init-29382.bin').read_bytes()),coefficient_words=1024,coefficient_sha256=sha((OUT/'source-coefficients.be24').read_bytes()),words=8192,target='173000..174FFF',DSP_words_BE24_sha256=sha(raw),nonzero=sum(raw[i:i+3]!=b'\0\0\0' for i in range(0,len(raw),3)),jobs=w['jobs'],families={n:dict(bytes=(d/n).stat().st_size,sha256=sha((d/n).read_bytes())) for n in ('wave0.be24','wave1.be24','wave2.be24')})
 (OUT/('recovered-stock.json' if stock else 'recovered.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run('--stock' in sys.argv)
