"""Native corrected scatter/constructor/reset-entry and bounded heap cases."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase46-msd-filesystem-closure'));import native_cases as N
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'));from independent_validate import decode
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
c=json.loads((O/'frozen-candidate-identity.json').read_text());image,_,_=decode((O/(c['candidate']+'.syx')).read_bytes());S=0x20044d70
def main():
 rows=[]
 for name,state in [('cold-zero',bytes(12)),('software-reset-FAILED',(0x15).to_bytes(4,'little')+b'\xa5'*8),('watchdog-reset-SUCCESS',(0x14).to_bytes(4,'little')+b'\x55'*8),('power-removal-uninitialized',b'\xa5'*12)]:
  e=N.Physical();u=e.uc;u.mem_write(0x08010000,image);u.mem_write(0x20000000,bytes(0x50000));u.mem_write(S,state)
  # Native reset scatter table includes initialized allocator fields and BSS;
  # same code path for reset causes; hardware reset/peripheral effects unmodeled.
  e.call(0x080596c4,0x0805b7c8,sp=0x2004fff8,maxins=500000)
  before=dict(cursor=hex(e.r32(0x20002b48)),limit=hex(e.r32(0x20002b44)),record=bytes(u.mem_read(S,12)).hex())
  e.call(0x0805b958,0x0805b7d8,sp=0x2004fff8,maxins=100000)
  after=dict(cursor=hex(e.r32(0x20002b48)),limit=hex(e.r32(0x20002b44)),record=bytes(u.mem_read(S,12)).hex())
  assert after['record']=='00'*12 and after['limit']==hex(S)
  rows.append(dict(case=name,before_constructor=before,after_constructor=after,geometry_valid=False,authorization=False,warm_reset_rearms_lifecycle=True))
 heap=[]
 for cursor,count in [(S-8,4),(S-4,4),(S,4),(S-8,9),(0x2000fe58,16)]:
  e=N.Physical();u=e.uc;u.mem_write(0x08010000,image);e.w32(0x20002b44,S);e.w32(0x20002b48,cursor);u.mem_write(S,b'RECORD123456');error=None
  try:ret=e.call(0x0801d7d0,count,sp=0x2004fff8)
  except Exception as ex:ret=None;error=repr(ex)
  end=cursor+((count+3)&~3);accepted=end<=S
  assert e.r32(0x20002b48)==(end if accepted else cursor)
  assert bytes(u.mem_read(S,12))==b'RECORD123456'
  if not accepted:assert error and u.reg_read(UC_ARM_REG_PC)==0x0801d7f4
  heap.append(dict(cursor_before=hex(cursor),request=count,rounded_bytes=(count+3)&~3,cursor_after=hex(e.r32(0x20002b48)),accepted=accepted,returned=ret,stop_PC=hex(u.reg_read(UC_ARM_REG_PC)),error=error,record_unchanged=True))
 ref=N.source.REF/'ctre/Firmware-Analysis/ram_dump_firmware_0x08037988.bin';ram=ref.read_bytes();fixture_cursor=int.from_bytes(ram[0x2b48:0x2b4c],'little')
 result=dict(confidence='PROVEN',candidate_sha256=c['BIN_sha256'],reset_cases=rows,heap_cases=heap,reference_running_RAM_source=str(ref),reference_RAM_sha256=hashlib.sha256(ram).hexdigest(),reference_cursor=hex(fixture_cursor),reference_remaining_margin=S-fixture_cursor,scope='Native scatter/constructor and nonoverflow allocation boundaries, NOT electrical reset, complete boot or exhaustive postboot callers',passed=True,hardware_access=False)
 (O/'heap-reset-tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
