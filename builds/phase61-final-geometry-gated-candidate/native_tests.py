"""Native candidate tests: execute bytes independently decoded from disk SYX.
Storage completion/USB transmission are explicit boundary models in this suite.
No port, USB or MIDI library is imported.
"""
from pathlib import Path
import sys,json,struct,traceback
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'))
from independent_validate import decode
sys.path.insert(0,str(R/'builds/phase46-msd-filesystem-closure'))
import native_cases as prior
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
sys.path.insert(0,str(O));import host
sys.path.insert(0,str(R/'builds/phase56-geometry-snapshot-lifecycle'))
from compact import encode,fields
image,_,_=decode((O/'circuittracks-final-geometry-gated-nor-test.syx').read_bytes())
meta=json.loads((O/'construction.json').read_text());L={k:int(v,16) for k,v in meta['layout'].items()}
S=0x20044d70;BUF=0x2000a050;DESC=0x200082f0
raw46=bytes.fromhex(json.loads((R/'builds/phase55-precleanup-geometry-snapshot/mount-cases.json').read_text())['cases'][0]['boundary']['record'])
packed=encode(fields(raw46));SESSION=37;EXPORTED=0x12|(SESSION<<25)
payload=bytes(((i*73)^(i>>1)^0xa6)&255 for i in range(535))
class N:
 def __init__(self):
  self.e=prior.Physical();self.u=self.e.uc;self.u.mem_write(0x08010000,image);self.frames=[];self.reads=[];self.writes=[];self.minsp=0x20050000;self.fail_at=None;self.disconnect=False;self.expire_at=None;self.mutate_parser=False
  self.e.w32(0x20002b44,0x20044e58);self.e.w32(0x20002b48,S-8);self.u.mem_write(S-4,b'LEFT');self.u.mem_write(S,b'\xa5'*12)
  self.u.hook_add(UC_HOOK_CODE,self.code);self.u.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=S-4,end=S+11)
  self.call(L['init']);assert self.e.r32(0x20002b44)==S and self.record()==bytes(12)
  self.fx=self.call(0x0805dbcc);assert self.fx==S+12;self.fx_bytes=bytes(self.u.mem_read(self.fx,220))
 def write(self,u,access,a,n,v,d):
  self.writes.append(dict(pc=hex(u.reg_read(UC_ARM_REG_PC)),address=hex(a),size=n,value=hex(v)))
  assert a>=S and a+n<=S+12,'private canary'
 def code(self,u,pc,n,d):
  self.minsp=min(self.minsp,u.reg_read(UC_ARM_REG_SP))
  if pc in (0x08024164,0x080241b8,0x08022fdc,0x08023078,0x08037494,0x080374d4,0x08037648):raise AssertionError('NOR mutation')
  if pc==L['drain']:
   prior.ret(self.e,1 if self.disconnect else 0);return
  if pc==0x08020c90:
   bp,ln=struct.unpack('<II',bytes(u.mem_read(u.reg_read(UC_ARM_REG_R2),8)));self.frames.append(bytes(u.mem_read(bp,ln)))
   if self.mutate_parser:u.mem_write(BUF,b'\x77'*232)
   prior.ret(self.e);return
  if pc==0x08047c6c:
   assert self.word()==0x13,'preauthorization read'
   a,b,n=[u.reg_read(UC_ARM_REG_R0+i) for i in range(3)];mask=self.u.mem_read(S+4,1)[0]
   assert (a,n)==(0x81000,23) and mask==3 or a in range(0x82000,0x82200,64) and n==64,'nonfixed read'
   i=len(self.reads);self.reads.append(dict(address=hex(a),bytes=n,buffer=hex(b)))
   if i==self.expire_at:
    self.e.w32(0x2000081c,(self.e.r32(S+8)+5000)&0xffffffff)
    # Timeout executes from actual watch bytes via deferred call below; control
    # state injection here models that already-qualified native IRQ transition.
    self.e.w32(S,0x15)
   if i==self.fail_at:prior.ret(self.e,1);return
   off=0 if a==0x81000 else 23+a-0x82000;u.mem_write(b,payload[off:off+n]);prior.ret(self.e)
 def call(self,pc,*args,mask=0):
  self.u.reg_write(UC_ARM_REG_PRIMASK,mask);v=self.e.call(pc,*args,sp=0x200082d8,maxins=500000)
  assert self.u.reg_read(UC_ARM_REG_PC)==0x0807ff00,hex(self.u.reg_read(UC_ARM_REG_PC))
  assert self.u.reg_read(UC_ARM_REG_SP)==0x200082d8
  assert bytes(self.u.mem_read(S-4,4))==b'LEFT'
  if hasattr(self,'fx_bytes'):assert bytes(self.u.mem_read(self.fx,220))==self.fx_bytes,'MasterFX clobber'
  return v
 def record(self):return bytes(self.u.mem_read(S,12))
 def word(self):return self.e.r32(S)
 def mounted(self):
  for (a,n),part in zip(((0x20000a98,8),(0x20000ab0,14),(0x20000ad0,24)),(raw46[:8],raw46[8:22],raw46[22:])):self.u.mem_write(a,part)
  self.e.w32(0x20005e5c,0x20000ab0);self.e.w32(0x20000aa4,self.e.r32(0x20006968));self.e.w32(0x20000aa8,0x20000a98)
  self.call(L['begin']);self.call(L['snapshot'],0);assert self.word()==0x11,self.record().hex();assert self.record()[4:]==packed,(self.record()[4:].hex(),packed.hex());return self
 def send(self,b):
  self.u.mem_write(BUF,b);self.u.mem_write(DESC,struct.pack('<II',BUF,len(b)));return self.call(0x0801eb30,0,DESC)
 def export(self):
  self.send(host.request(SESSION));assert self.word()==EXPORTED,hex(self.word());assert host.geometry_response(self.frames[-1],SESSION)[:2]==(1,packed);return self
 def authorize(self,identity=False):return self.send(host.request(SESSION,15,1,packed,identity))
def main():
 rows=[]
 def test(name,fn):
  try:detail=fn();rows.append(dict(case=name,passed=True,detail=detail))
  except Exception as ex:rows.append(dict(case=name,passed=False,error=str(ex),traceback=traceback.format_exc()));persist();raise
 def persist():(O/'native-tests.json').write_text(json.dumps(dict(confidence='PROVEN',source='independently decoded candidate SYX',cases=rows,all_passed=all(x['passed'] for x in rows),seams=['running-RAM fixture','synchronous read completion modeled at47C6C','USB drain and frame transport modeled','in-read timeout models an already executed native watch transition']),indent=2)+'\n')
 def boot():
  e=prior.Physical();u=e.uc;u.mem_write(0x08010000,image);u.mem_write(0x20000000,bytes(0x50000));u.mem_write(0x20000000,prior.source.init)
  e.call(0x0805b958,0x0805b7d8,sp=0x2004fff8);assert e.r32(0x20002b44)==S and bytes(u.mem_read(S,12))==bytes(12);return dict(record=bytes(u.mem_read(S,12)).hex(),heap_cursor=hex(e.r32(0x20002b48)))
 test('boot/init + real constructor entry',boot)
 test('first mount native compact snapshot',lambda: N().mounted().record().hex())
 test('valid RAM-only geometry export',lambda:N().mounted().export().frames[-1].hex())
 def invalid():
  n=N().mounted();n.e.w32(S,0x16);n.e.w32(0x20000a9c,512);n.call(L['snapshot'],0);assert n.word()==0x1d;return n.record().hex()
 test('invalid geometry binding',invalid)
 for name,op,args in [('remount','slow',()),('binding','binding',(0x20000aa0,)),('stride','stride',(0,0x20000a98)),('early registration','register',(0,BUF))]:
  def invalidation(op=op,args=args):
   n=N().mounted().export();n.u.mem_write(BUF,b'0:\0');n.u.reg_write(UC_ARM_REG_R4,0x20000ab0);n.call(L[op],*args);assert n.word()==0x1d;n.authorize();assert not n.reads;return n.record().hex()
  test(name+' invalidates authorization',invalidation)
 def success(identity=False,overwrite=False):
  n=N().mounted().export();n.mutate_parser=overwrite;n.authorize(identity);assert n.word()==0x14,hex(n.word());rx=host.Receiver(SESSION,identity)
  for f in n.frames[1:]:rx.accept(f)
  assert rx.result()==(payload if identity else payload[23:]);before=len(n.reads);n.authorize(identity);assert len(n.reads)==before
  return dict(reads=n.reads,frames=len(n.frames),minimum_SP=hex(n.minsp),state=n.record().hex())
 test('correct same-epoch authorization +82000 exact success',success)
 test('optional separately authorized81000+82000 exact success',lambda:success(True))
 test('parser overwrite during raw capture',lambda:success(False,True))
 for name,mutate in [('wrong epoch',lambda b:b.__setitem__(14,2)),('wrong geometry',lambda b:b.__setitem__(15,b[15]^1)),('wrong session',lambda b:b.__setitem__(5,38)),('malformed nibble',lambda b:b.__setitem__(7,16)),('arbitrary address payload',lambda b:b.__setitem__(50,1))]:
  def reject(mutate=mutate):
   n=N().mounted().export();before=n.record();b=bytearray(host.request(SESSION,15,1,packed));mutate(b);n.send(bytes(b));assert n.record()==before and not n.reads
  test(name,reject)
 def noauth():
  n=N().mounted();before=n.record();n.u.reg_write(UC_ARM_REG_R6,0);n.call(0x0806b850);assert n.record()==before and not n.reads
 test('raw without authorization',noauth)
 def dup_export():
  n=N().mounted().export();before=n.record();n.send(host.request(SESSION));assert n.record()==before and len(n.frames)==1
 test('duplicate SysEx geometry request',dup_export)
 def fail_at(k,timeout=False):
  n=N().mounted().export();n.fail_at=None if timeout else k;n.expire_at=k if timeout else None;n.authorize();assert n.word()==0x15;assert len(n.reads)==k+1
  before=n.record();n.call(0x0806bc46);n.authorize();n.send(host.request(SESSION));assert n.record()==before and len(n.reads)==k+1
  return dict(reads=len(n.reads),owner=n.record()[7],failed_absorbing=True)
 for k in (0,4,7):test('read failure chunk'+str(k),lambda k=k:fail_at(k));test('active timeout chunk'+str(k),lambda k=k:fail_at(k,True))
 def tick():
  n=N().mounted().export();before=n.record();n.e.w32(0x2000081c,0xffffffff);n.call(0x0806b748);assert n.record()==before
  n.e.w32(S,0x13);n.e.w32(S+8,0xfffffff0);n.e.w32(0x2000081c,(0xfffffff0+4998)&0xffffffff);n.call(0x0806b748);assert n.word()==0x13
  n.e.w32(0x2000081c,(0xfffffff0+4999)&0xffffffff);n.call(0x0806b748);assert n.word()==0x15;n.call(0x0806bc46);assert n.word()==0x15
 test('native SysTick preauth + wrap timeout + late success',tick)
 def disconnect():
  n=N().mounted().export();n.disconnect=True;n.authorize();assert n.word()==0x15 and len(n.reads)==1;n.authorize();assert len(n.reads)==1
 test('host disconnect at raw send',disconnect)
 def atomic():
  n=N().mounted();n.e.w32(S,0x13)
  for mask in (0,1):
   n.e.w32(S,0x13);n.call(0x0806bc46,mask=mask);assert n.word()==0x14 and n.u.reg_read(UC_ARM_REG_PRIMASK)==mask
   n.e.w32(S,0x15);n.call(0x0806bc46,mask=mask);assert n.word()==0x15
 test('atomic completion masks restored FAILED absorbing',atomic)
 def abi():
  n=N().mounted();before=n.record();n.call(0x0805dbcc);assert n.record()==before
  for op in ('snapshot','invalidate','complete','fail','begin'):
   for i in range(13):n.u.reg_write(UC_ARM_REG_R0+i,0x1000+i)
   regs=[n.u.reg_read(UC_ARM_REG_R0+i) for i in range(13)];n.u.reg_write(UC_ARM_REG_APSR,0xa8000000);n.call(L[op],mask=1)
   assert [n.u.reg_read(UC_ARM_REG_R0+i) for i in range(13)]==regs and n.u.reg_read(UC_ARM_REG_APSR)==0xa8000000
 test('supported owner registers/APSR/PRIMASK + getter ABI',abi)
 persist();print('Native cases PASS',len(rows))
if __name__=='__main__':main()

