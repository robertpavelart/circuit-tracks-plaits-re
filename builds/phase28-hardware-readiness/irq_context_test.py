"""Execute real QSPI IRQ/flag/wait code on authenticated RAM. No payload/device.
Only external SR.TCF and scheduler-current-task selection are modeled inputs.
OS notification endpoint is observed/stubbed AFTER original holder flag write.
Main's actual blocking wait is stopped before executing a context switch.
"""
from inspect_code import *
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
class Waiting(Exception):pass
s=authentic_session();e=s.e;u=e.uc
u.mem_map(0xa0001000,0x1000)
k=w(0x0801cf90);main_tcb=e.r32(k+0x64);main_holder=e.r32(main_tcb+0x50)
storage_holder=e.r32(0x20006790);storage_tcb=e.r32(storage_holder)
controller=0x20005550;ctx=0x20000000
assert main_holder==0x20007750 and storage_holder==0x20008d38
initial=dict(Main_flags=hex(e.r32(main_holder+8)),Storage_flags=hex(e.r32(storage_holder+8)),scheduler_active=e.r8(0x20006a47))
assert e.r32(main_holder+8)==0 and e.r32(storage_holder+8)==0 and initial['scheduler_active']==1
trace=[];pcs={}
def hook(u,pc,n,d):
 pcs[hex(pc)]=pcs.get(hex(pc),0)+1
 if pc==0x0801ce60:
  trace.append(dict(kind='OS_notify_boundary',TCB=hex(u.reg_read(UC_ARM_REG_R0)),mask=hex(u.reg_read(UC_ARM_REG_R1))))
  u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
 elif pc==0x0801be1a:
  trace.append(dict(kind='actual_wait_entry',holder=hex(u.reg_read(UC_ARM_REG_R0)),mask=hex(u.reg_read(UC_ARM_REG_R1))))
 elif pc==0x0801cdc8:
  trace.append(dict(kind='actual_wait_blocks',holder=hex(u.reg_read(UC_ARM_REG_R4)),PC=hex(pc)))
  raise Waiting('original wait requests scheduler block; observer stops, no success injected')
u.hook_add(UC_HOOK_CODE,hook)
# Hardware completion is modeled at the peripheral status register only.
e.w32(0xa0001008,2)
u.reg_write(UC_ARM_REG_IPSR,108);e.call(0x080573e0,maxins=20000);u.reg_write(UC_ARM_REG_IPSR,0)
after_IRQ=dict(Main_flags=hex(e.r32(main_holder+8)),Storage_flags=hex(e.r32(storage_holder+8)),controller_flags=hex(e.r32(controller)))
assert e.r32(main_holder+8)==0 and e.r32(storage_holder+8)&0x100 and e.r32(controller)&1
try:e.call(0x08037596,ctx,maxins=50000)
except Waiting:blocked=True
else:blocked=False
assert blocked and pcs.get('0x80375b0',0)==0
main_trace=trace[:]
# Control: the same original completion wait in its intended Storage context.
e.w32(k+0x64,storage_tcb);pcs.clear();trace=[]
e.call(0x08037596,ctx,maxins=50000)
assert pcs.get('0x80375b0',0)==1 and not any(x['kind']=='actual_wait_blocks' for x in trace)
assert e.r32(storage_holder+8)&0x100==0
result=dict(confidence='PROVEN',verdict='phase27 direct-backend caller context rejected',initial=initial,
 QSPI_IRQ_vector=hex(w(0x080101b0)),IRQ_target_holder=hex(storage_holder),Main_wait_holder=hex(main_holder),
 after_actual_IRQ=after_IRQ,Main_wait_blocks_despite_controller_complete=True,Main_reaches_controller_flag_check=False,
 Storage_control_returns=True,Main_trace=main_trace,Storage_trace=trace,
 modeled_inputs=['SR.TCF=1 peripheral completion','Storage current-task selection in control case'],
 modeled_endpoint='0x0801ce60 notification observed after actual 0x0801be08 holder flag store',
 payload_bytes_supplied=False,hardware_access=False)
(O/'irq-context-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
