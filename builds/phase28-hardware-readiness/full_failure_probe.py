"""Run the actual phase27 handler until real IRQ/wait mismatch. No payload.
Preserve the live Main frame while executing the stock IRQ on a separate modeled
MSP. No wait acknowledgement or diagnostic return is synthesized.
"""
from inspect_code import *
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
P=R/'builds/phase27-qspi-read';sys.path.insert(0,str(P));from protocol import request
plan=json.loads((P/'patch-plan.json').read_text());s=authentic_session();e=s.e;u=e.uc
u.mem_map(0xa0001000,0x1000);u.mem_write(int(plan['append']['start'],16),(P/'arm-diagnostic.fragment.bin').read_bytes());u.mem_write(0x0801eb30,bytes.fromhex(plan['hook']['after']))
class NeedIRQ(Exception):pass
class Blocked(Exception):pass
irq_done=False;events=[];counts={};minsp=0xffffffff
def hook(u,pc,n,d):
 global minsp
 minsp=min(minsp,u.reg_read(UC_ARM_REG_SP));counts[hex(pc)]=counts.get(hex(pc),0)+1
 if pc==0x08022f94:events.append(dict(kind='actual_backend_read',args=[hex(u.reg_read(x)) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]))
 elif pc==0x08037596 and not irq_done:raise NeedIRQ()
 elif pc==0x0801ce60:
  events.append(dict(kind='OS_notification_endpoint',TCB=hex(u.reg_read(UC_ARM_REG_R0)),mask=hex(u.reg_read(UC_ARM_REG_R1))))
  u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
 elif pc==0x0801be1a:events.append(dict(kind='actual_wait',holder=hex(u.reg_read(UC_ARM_REG_R0)),mask=hex(u.reg_read(UC_ARM_REG_R1))))
 elif pc==0x0801cdc8:raise Blocked()
 elif pc==0x08020c90:raise AssertionError('unexpected reply before resolved completion')
u.hook_add(UC_HOOK_CODE,hook)
buf=0x20060100;msg=0x20060000;u.mem_write(buf,request(37));u.mem_write(msg,struct.pack('<II',buf,232))
entry=0x20008358-128
u.reg_write(UC_ARM_REG_SP,entry);u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,msg);u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_LR,0x0807ff01)
try:u.emu_start(0x0801eb31,0xffffffff,count=1000000)
except NeedIRQ:pass
else:raise AssertionError('did not enter read wait')
main_context=u.context_save();e.w32(0xa0001008,2)
assert e.r32(0xa0001018)==0x82000 and e.r32(0xa0001010)==511
u.reg_write(UC_ARM_REG_SP,0x20050000);u.reg_write(UC_ARM_REG_IPSR,108);u.reg_write(UC_ARM_REG_LR,0x0807ff01)
u.emu_start(0x080573e1,0xffffffff,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x0807ff00
irq_done=True;u.context_restore(main_context)
try:u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0xffffffff,count=100000)
except Blocked:pass
else:raise AssertionError('expected Main wait to block')
assert e.r32(0x20007758)==0 and e.r32(0x20008d40)&0x100 and e.r32(0x20005550)&1
assert not counts.get('0x80375b0',0)
result=dict(confidence='PROVEN',candidate='phase27 unchanged',result='FAIL: actual Main handler blocks after real stock QSPI IRQ',
 events=events,stopped_PC=hex(u.reg_read(UC_ARM_REG_PC)),Main_flag=hex(e.r32(0x20007758)),Storage_flag=hex(e.r32(0x20008d40)),
 controller_flag=hex(e.r32(0x20005550)),backend_semaphore=e.r8(0x20000380),
 controller_flag_check_reached=False,replies=0,minimum_SP=hex(minsp),
 modeled_inputs=['opaque completed DMA represented by SR.TCF=1; no payload bytes supplied','separate emulator IRQ stack at 0x20050000'],
 modeled_endpoint='OS notification 0x0801ce60 after actual flag store',
 no_synthetic_wait_success=True,hardware_access=False)
(O/'full-handler-failure.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
