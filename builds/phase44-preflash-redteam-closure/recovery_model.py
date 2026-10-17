"""Offline bootloader-owned updater/installer model; no port or image generation.

Native intake 080059c4, dispatcher 080059fa, native state methods 08007b08+
execute independently of application updater. Only storage/clock/UI/flash
completion are modeled. RAM boot object construction is explicit, not reset.
"""
from pathlib import Path
import sys,json,struct,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent; R=O.parents[1]; P=R/'builds/phase43-hardware-test-candidate'
sys.path.insert(0,str(R/'builds/phase42-exact-rdiag-integration'))
from environment import *
O=Path(__file__).resolve().parent
sys.path.insert(0,str(P));from independent_validate import messages,block
sys.path.insert(0,str(P/'source/tools'));from ct_fw import crc32_mpeg2
def sha256(b):return hashlib.sha256(b).hexdigest()
class Reset(Exception):pass
class Model:
 def __init__(self,app):
  self.e=Physical();self.u=u=self.e.uc;u.mem_write(0x20000000,b'\0'*0x50000)
  u.mem_write(0x08010000,b'\xff'*0x70000);u.mem_write(0x08010000,app)
  self.nor=bytearray(b'\xff'*0x2000000);self.ops=[];self.flash=[];self.paths=set();self.reset=False;self.jump=False
  # Distinct boot storage objects with modeled vtable endpoints. Selector0
  # descriptor layout is native {backend**, timer*, staging base=0}.
  for ob in [0x20041000,0x20041020]:self.e.w32(ob,0x20041100)
  for k in range(0,32,4):self.e.w32(0x20041100+k,0x0807f001+k)
  self.e.w32(0x20041040,0x20041000)
  self.e.w32(0x200054c8,0x20041000);self.e.w32(0x200054dc,0x20041000)
  self.e.w32(0x20000a80,0x20041060)
  self.e.w32(0x200009fc+0x1c,0x20041060)
  for state,vt in [(0x20000a1c,0x080097b4),(0x20000a30,0x080097c8),(0x20000a20,0x080097f0),(0x20000a24,0x08009804),(0x20000a28,0x08009818),(0x20000a2c,0x080097dc)]:self.e.w32(state,vt)
  for k,v in enumerate([0x20041040,0x20041020,0]):self.e.w32(0x20041060+4*k,v)
  self.e.w32(0x200054c4,0x20000a1c)
  self.e.w32(0x200054c0+8,0x20041000)
  self.u.hook_add(UC_HOOK_CODE,self.hook)
 def ret(self,v=0):self.u.reg_write(UC_ARM_REG_R0,v);self.u.reg_write(UC_ARM_REG_PC,self.u.reg_read(UC_ARM_REG_LR)|1)
 def reg(self,i):return self.u.reg_read(UC_ARM_REG_R0+i)
 def hook(self,u,pc,n,d):
  self.paths.add(pc)
  if pc==0x0800489c:self.ret(1);return
  if pc==0x08000bc0:self.ret(0);return
  if 0x0807f000<=pc<0x0807f080:
   slot=(pc-0x0807f000)//4
   if self.reg(0)==0x20041020:self.ret();return
   if slot==5:
    a,z=self.reg(1),self.reg(2);a&=~4095;z=(z+4095)&~4095
    self.nor[a:z]=b"\xff"*(z-a);self.ops.append(["ERASE",a,z])
   elif slot==3:
    a,b,n=self.reg(1),self.reg(2),self.reg(3);u.mem_write(b,bytes(self.nor[a:a+n]));self.ops.append(['READ',a,a+n])
   elif slot==4:
    a,b,n=self.reg(1),self.reg(2),self.reg(3);flag=self.e.r32(u.reg_read(UC_ARM_REG_SP))
    if flag:self.nor[a&~4095:(a&~4095)+4096]=b'\xff'*4096;self.ops.append(['ERASE',a&~4095,(a&~4095)+4096])
    data=bytes(u.mem_read(b,n));assert all((x&y)==y for x,y in zip(self.nor[a:a+n],data));self.nor[a:a+n]=data;self.ops.append(['WRITE',a,a+n])
   self.ret();return
  if pc in [0x08004cc6,0x08004ce0,0x0800440c,0x08004500,0x08004ae2,0x08005ff8,0x0800600e,0x08006006,0x08005d74]:self.ret();return
  if pc==0x08005c68:self.ret(crc32_mpeg2(bytes(self.nor[self.reg(0):self.reg(0)+self.reg(1)])));return
  if pc==0x08005c3c:self.ret(crc32_mpeg2(bytes(u.mem_read(self.reg(0),self.reg(1)))));return
  if pc==0x08006020:
   a=self.reg(0);bounds=[0x08010000,0x08018000,0x08020000,0x08040000,0x08080000]
   if a<bounds[-1]:z=bounds[bounds.index(a)+1];u.mem_write(a,b'\xff'*(z-a));self.flash.append(['ERASE',a,z])
   self.ret(1);return
  if pc==0x0800605e:
   a=self.reg(0);u.mem_write(a,struct.pack('<I',self.reg(1)));self.flash.append(['WRITE',a,a+4]);self.ret(1);return
  if pc==0x08003d06:self.jump=True;self.ret();return
  if pc==0x08007d56:self.reset=True;raise Reset()
 def call(self,fn,*args):
  try:return self.e.call(fn,*args,maxins=4000000)
  except Reset:return None
 def key_entry(self):
  self.u.mem_write(0x20040000,b'\x01')
  self.call(0x08003ab0,0,0x20040000)
  assert self.e.r8(0x20005378)==1
  assert self.call(0x08003b66,150)==1
 def packet(self,msg):
  self.u.mem_write(0x20040000,msg);self.u.mem_write(0x20040200,struct.pack('<II',0x20040000,len(msg)))
  self.call(0x080059c4,0,0x20040200)
 def seed(self,image,header=None):
  padded=image+b'\xff'*(-len(image)%32);self.nor[:len(padded)]=padded
  if header is None:
   vals=[0]+[int(c,16) for c in '000572'+f'{len(image):08x}'+f'{crc32_mpeg2(image):08x}'];header=bytes(vals)
  self.nor[0x80000:0x80017]=header
 def validate_install(self):self.call(0x08003b2a);self.call(0x08003b9a)
def raw_packets(raw):
 at=0
 while at<len(raw):
  end=raw.index(247,at)+1;yield raw[at:end];at=end
def main():
 candidate=(P/'circuittracks-4486-nor-evidence-test.bin').read_bytes();official=(P/'official-4486-decoded.bin').read_bytes();b13=PUBLISHED[:]
 results=[]
 for name,image,app,mut in [('candidate_metadata',candidate,b13,None),('official_metadata',official,candidate,None),('b13_metadata',b13,candidate,None),('invalid_crc',official,candidate,'crc'),('partial_metadata',official,candidate,'partial'),('garbage_application',official,b'\xa5'*len(candidate),None),('interrupted_prior_install',official,b'\xff'*len(candidate),None),('valid_staged_invalid_application',candidate,b'\xff'*len(candidate),None),('same_header_install_noop',official,official,'same'),('lower_numeric_metadata_version',official,candidate,'lower')]:
  m=Model(app);m.seed(image)
  if mut=='lower':m.nor[0x80001:0x80007]=bytes(6)
  if mut=='crc':m.nor[0x80016]^=1
  if mut=='partial':m.nor[0x8000b:0x80017]=b'\xff'*12
  m.validate_install();installed=bytes(m.u.mem_read(0x08010000,len(image)))==image
  results.append(dict(case=name,installed=installed,internal_erase_count=sum(x[0]=='ERASE' for x in m.flash),internal_program_words=sum(x[0]=='WRITE' for x in m.flash),jump=m.jump,metadata_after=m.nor[0x80000:0x80017].hex(),metadata_cleared=False,paths=[hex(x) for x in sorted(m.paths)],operations=m.ops))
  assert installed if mut not in ('crc','partial') else not m.flash
  if mut=='same':assert not m.flash
 # Full original official stream through BOOTLOADER intake from corrupted state.
 uploads=[]
 for name,raw in [('candidate',(P/'circuittracks-4486-nor-evidence-test.syx').read_bytes()),('official',(P/'rollback/circuittracks-firmware-4486-STOCK.syx').read_bytes())]:
  m=Model(b'\xa5'*len(candidate));m.key_entry();m.nor[:0x90000]=b'\x00'*0x90000
  for msg in raw_packets(raw):m.packet(msg)
  state=m.e.r32(0x200054c4);m.call(0x08007d06,state,0)
  image=candidate if name=='candidate' else official
  assert m.reset and bytes(m.nor[:len(image)])==image
  assert any(x[0]=='WRITE' and x[1]==0x80000 for x in m.ops)
  metadata=m.nor[0x80000:0x80017].hex();m.validate_install();assert bytes(m.u.mem_read(0x08010000,len(image)))==image
  uploads.append(dict(case=name,accepted=True,reset=m.reset,metadata=metadata,staged_sha256=sha256(m.nor[:len(image)]),installed_sha256=sha256(bytes(m.u.mem_read(0x08010000,len(image)))),operations=m.ops,native_paths=[hex(x) for x in sorted(m.paths)]))
 out=dict(boot_flash_dump_sha256=sha256((REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin').read_bytes()),matrix=results,full_bootloader_uploads=uploads,hardware_access=False,port_imports=False,firmware_generated=False)
 (O/'recovery-results.json').write_text(json.dumps(out,indent=2)+'\n');print('recovery matrix',len(results),'full uploads',len(uploads))
if __name__=='__main__':main()

