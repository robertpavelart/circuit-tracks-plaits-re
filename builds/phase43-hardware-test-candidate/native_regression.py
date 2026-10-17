"""Final SYX-derived bytes: admission sweep, dormancy and native capture."""
from pathlib import Path
import sys,json,struct
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase42-exact-rdiag-integration'
sys.path.insert(0,str(P))
import environment as E
from environment import *
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O))
from independent_validate import decode
image,_,details=decode((O/'circuittracks-4486-nor-evidence-test.syx').read_bytes())
Original=E.Physical
class FinalPhysical(Original):
 def __init__(self):
  super().__init__();self.uc.mem_write(0x08010000,image)
def main():
 # Execute command decoder for every opcode on USB and DIN. Accepted command
 # is stopped at its entry, before any Storage operation, rather than stubbed
 # into fictitious successful data. All other requests must reach normal return.
 e=FinalPhysical();u=e.uc;seen=[];storage=[];rows=[]
 def code(u,pc,n,d):
  if pc==0x0806b850:seen.append(pc);u.emu_stop()
  if pc in (0x08047c6c,0x08022f94,0x08022fdc,0x08023078,0x08037494,0x080374d4):storage.append(pc);raise AssertionError('unexpected diagnostic Storage dispatch')
 u.hook_add(UC_HOOK_CODE,code)
 for port in (0,1):
  accepted=[]
  for cmd in range(256):
   e.w32(0x20002b44,0x20044e58);e.w32(0x20002b48,0x20044d68);u.mem_write(0x20044d70,bytes(12))
   data=b'\xf0\x7dCT'+bytes((cmd,37))+bytes(225)+b'\xf7'
   u.mem_write(0x2000a050,data);u.mem_write(0x200082f0,struct.pack('<II',0x2000a050,232))
   seen.clear()
   for reg,value in ((UC_ARM_REG_R0,port),(UC_ARM_REG_R1,0x200082f0),(UC_ARM_REG_R2,0),(UC_ARM_REG_SP,0x200082d8),(UC_ARM_REG_LR,0x0807ff01)):u.reg_write(reg,value)
   u.emu_start(0x0801eb31,0xffffffff,count=100000)
   if seen:accepted.append(cmd);assert port==0 and cmd==13 and e.r8(0x20044d74)==1
   else:assert u.reg_read(UC_ARM_REG_PC)==0x0807ff00 and e.r8(0x20044d74)==0
  assert accepted==([13] if port==0 else [])
  rows.append(dict(port=port,opcodes_tested=256,accepted=accepted,Storage_operations=0,confidence='PROVEN'))
 # Also reject a nonzero address-supplied payload for the sole valid opcode.
 e=FinalPhysical();u=e.uc;attempt=[]
 def no_reader(u,pc,n,d):
  if pc in (0x0806b850,0x08047c6c,0x08022fdc,0x08023078):attempt.append(pc);raise AssertionError('address-supplied command accepted')
 u.hook_add(UC_HOOK_CODE,no_reader)
 req=bytearray(b'\xf0\x7dCT\x0d\x25'+bytes(225)+b'\xf7');req[6:14]=bytes.fromhex('0000000000080100')
 u.mem_write(0x2000a050,bytes(req));u.mem_write(0x200082f0,struct.pack('<II',0x2000a050,232));e.call(0x0801eb30,0,0x200082f0,0,sp=0x200082d8);assert not attempt
 # Final binary through the already qualified native Main/RX/Storage/TX path.
 import replay
 replay.Physical=FinalPhysical
 from coupled import Exact
 m=Exact();assert m.e.r8(0x20044d74)==0 and not m.reads and not m.frames
 idle=bytes(m.u.mem_read(0x20044d70,12));cursor=m.e.r32(0x20002b48)
 m.task='IRQ'
 for _ in range(20):m.e.call(0x0805998c,sp=0x2004ff00)
 assert bytes(m.u.mem_read(0x20044d70,12))==idle and m.e.r32(0x20002b48)==cursor and not m.reads and not m.frames and not m.commands
 m.start();assert m.finish(1500);m.verify()
 result=dict(confidence='PROVEN',source='Final candidate SYX decoded from disk, injected before native initialization',opcode_sweeps=rows,address_payload_rejected=True,precommand=dict(latch='IDLE',record_unchanged_over_20_native_ticks=True,diagnostic_Storage_requests=0,diagnostic_NOR_reads=0,diagnostic_NOR_writes=0,allocator_cursor_unchanged=True),normal=m.summary(),scope='Bounded running-RAM replay; no complete peripheral cold boot or architectural exception scheduling',hardware_access=False,MIDI_ports_opened=0)
 (O/'native-regression.json').write_text(json.dumps(result,indent=2)+'\n');print('Native final-image regression PASS: 512 opcode/port cases, dormancy, full capture')
if __name__=='__main__':main()
