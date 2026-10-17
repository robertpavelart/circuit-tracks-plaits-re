"""Native reservation-negative gate, exact serialized image; no device APIs.

Native snapshot/continuation execute. Only the stock logging sink is stubbed.
The mounted filesystem tuple is the existing synthetic Phase55 case; this is
an adversarial entry-state test, not a claim of an observed real boot failure.
"""
from pathlib import Path
import sys,json,struct,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase61-final-geometry-gated-candidate'
sys.path.insert(0,str(P));import native_tests as T
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
def run(image,label):
 # Install selected bytes before the fixture executes any native instruction.
 # Replacing already-executed code in Unicorn can leave translated blocks cached.
 T.image=image
 rows=[]
 cases=[('absent-zero',0x20044e58,0x20044d68,bytes(12)),
  ('absent-garbage',0x20044e58,0x20044d68,b'\xa5'*12),
  ('absent-partial-mounting',0x20044e58,0x20044d68,struct.pack('<I',0x16)+b'\xa5'*8),
  ('absent-cursor-overlaps',0x20044e58,0x20044e50,struct.pack('<I',0x16)+bytes(8)),
  ('wrong-limit-partial',0x20044d7c,0x20044d68,struct.pack('<I',0x16)+b'\x77'*8),
  ('reserved-limit-cursor-overlaps',0x20044d70,0x20044d78,struct.pack('<I',0x16)+b'\x77'*8),
  ('reserved-first-mount-control',0x20044d70,0x20044d68,struct.pack('<I',0x16)+b'\xa5'*8)]
 for name,limit,cursor,record in cases:
  n=T.N().mounted();u=n.u;e=n.e
  u.mem_write(0x08010000,image);e.w32(0x20002b44,limit);e.w32(0x20002b48,cursor);u.mem_write(T.S,record);n.writes.clear()
  # Reproduce the original ADDC caller frame, then execute the installed AE06
  # branch and original AE14 return/logging tail. No mount/Storage is stubbed
  # into a success here: R0 is the supplied status from the completed mount.
  sp=0x200082d8;u.mem_write(sp,struct.pack('<4I',0x22222222,0x44444444,0x55555555,0x0807ff01));u.reg_write(UC_ARM_REG_R4,0x20000aa0)
  def logging(u,pc,size,data):
   if pc==0x0801b3b8:T.prior.ret(e)
  u.hook_add(UC_HOOK_CODE,logging)
  error=None
  try:e.call(0x0801ae06,0,sp=sp,maxins=10000)
  except Exception as ex:error=repr(ex)
  actual=bytes(u.mem_read(T.S,12));reserved=limit==T.S
  valid=(actual[0]&7)==1
  returned=u.reg_read(UC_ARM_REG_PC)==0x0807ff00 and u.reg_read(UC_ARM_REG_SP)==sp+16
  expected=bool(reserved and cursor<=T.S)
  guards=bytes(u.mem_read(T.S-4,4))==b'LEFT' and bytes(u.mem_read(n.fx,220))==n.fx_bytes
  allocator_unchanged=e.r32(0x20002b44)==limit and e.r32(0x20002b48)==cursor
  passed=error is None and returned and guards and allocator_unchanged and (valid and actual[4:]==T.packed if expected else not n.writes and actual==record and not valid)
  rows.append(dict(case=name,passed=passed,heap_limit=hex(limit),heap_cursor=hex(cursor),input_record=record.hex(),output_record=actual.hex(),write_intents=n.writes,geometry_valid=valid,original_tail_returned=returned,neighbor_guards_preserved=guards,allocator_unchanged=allocator_unchanged,error=error))
 return dict(confidence='PROVEN',image_label=label,image_sha256=hashlib.sha256(image).hexdigest(),cases=rows,passed=all(x['passed'] for x in rows),scope='Exact native snapshot hook plus original mount return tail under synthetic valid mounted metadata; logging sink only is modeled',hardware_access=False,MIDI_ports_opened=0)
def main():
 name=sys.argv[1] if len(sys.argv)>1 else 'phase61'
 if name=='phase61':image=T.image
 else:
  from independent_validate import decode
  image,_,_=decode((O/name).read_bytes())
 result=run(image,name);(O/(('original-' if name=='phase61' else 'corrected-')+'reservation-tests.json')).write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
