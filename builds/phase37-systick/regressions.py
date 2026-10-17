"""Native result assertions plus distinct captured-state architecture fixtures."""
import json
from systick import *
D=json.loads((O/'stock.json').read_text());T=D['SysTick'][0];CAP=T['captured'];rows=[]
def ck(name,fn):fn();rows.append(dict(case=name,confidence='PROVEN',result='PASS'))
def fixture():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M7)
 for a,n in ((0x08000000,0x80000),(0x20000000,0x50000),(0xe000e000,0x2000)):u.mem_map(a,n)
 u.mem_write(0x08000000,ROM);pre=CAP['registers']
 for i,reg in enumerate(GENERAL):u.reg_write(reg,pre[f'r{i}'])
 for name in ('msp','psp','lr','control','basepri','primask','faultmask','xpsr'):u.reg_write(SPECIAL[name],pre[name])
 u.reg_write(UC_ARM_REG_PC,pre['pc']|1)
 for a,v in ((0xe000ed08,CAP['VTOR']),(0xe000ed04,CAP['ICSR']|(1<<26)),(0xe000ed20,CAP['SHPR3']),(0xe000ed24,CAP['SHCSR']),
  (0xe000e010,CAP['CTRL']),(0xe000e014,CAP['LOAD']),(0xe000e018,CAP['VAL_backing'])):u.mem_write(a,struct.pack('<I',v))
 u.mem_write(CAP['scheduler_base'],bytes.fromhex(CAP['scheduler_hex']))
 t=CAP['current_task'];u.mem_write(t['TCB'],bytes.fromhex(t['TCB_hex']));u.mem_write(t['saved_PSP'],bytes.fromhex(t['context_hex']))
 u.mem_write(CAP['stack_window_address'],bytes.fromhex(CAP['stack_window_hex']));u.mem_write(CAP['MSP_stack_address'],bytes.fromhex(CAP['MSP_stack_hex']))
 for a,v in ((0x20000008,CAP['clock_counter']),(0x20005518,CAP['handler_counter'])):u.mem_write(a,struct.pack('<I',v))
 u.mem_write(0x20000004,bytes([CAP['clock_increment_byte']]))
 assert snap(u)==CAP['registers'];return u,TickModel()
def execute(u,m,row):
 handler=m.enter_tick(u,row)
 def code(uc,pc,n,d):
  if pc==0x0800933e:uc.emu_stop()
 h=u.hook_add(UC_HOOK_CODE,code)
 try:u.emu_start(handler,0xffffffff,count=100)
 finally:u.hook_del(h)
 assert u.reg_read(UC_ARM_REG_PC)==0x0800933e
def atomic_reject(fn,u):
 before=snap(u);ram_before=bytes(u.mem_read(0x20000000,0x50000));sys_before=bytes(u.mem_read(0xe000e000,0x2000))
 try:fn()
 except AssertionError:pass
 else:raise AssertionError('unsupported fixture accepted')
 assert snap(u)==before and bytes(u.mem_read(0x20000000,0x50000))==ram_before and bytes(u.mem_read(0xe000e000,0x2000))==sys_before
def roundtrip(padded):
 u,m=fixture()
 if not padded:u.reg_write(UC_ARM_REG_PSP,u.reg_read(UC_ARM_REG_PSP)-4)
 before=snap(u);row={};execute(u,m,row)
 assert row['padding']==(4 if padded else 0) and row['hardware_frame_address']%8==0
 assert row['hardware_frame']['pc']==before['pc'] and row['hardware_frame']['xpsr']&512==(512 if padded else 0)
 assert r32(u,0xe000ed04)==0x80f and r32(u,0xe000ed24)&(1<<11)
 m.leave_tick(u,row);assert snap(u)==before
 assert u.reg_read(UC_ARM_REG_MSP)==before['msp'] and row['frame_consumptions']==1
 assert r32(u,0xe000ed04)==0x800 and r32(u,0xe000ed24)==CAP['SHCSR']
 assert r32(u,0x20000008)==CAP['clock_counter']+CAP['clock_increment_byte']
 assert r32(u,0x20005518)==CAP['handler_counter']+1
 atomic_reject(lambda:m.leave_tick(u,row),u)
def masked(which):
 u,m=fixture()
 reg,value={'BASEPRI':(UC_ARM_REG_BASEPRI,0xc0),'PRIMASK':(UC_ARM_REG_PRIMASK,1),'FAULTMASK':(UC_ARM_REG_FAULTMASK,1)}[which]
 u.reg_write(reg,value);assert not m.tick_eligible(u)
 pending=r32(u,0xe000ed04);atomic_reject(lambda:m.enter_tick(u,{}),u)
 assert r32(u,0xe000ed04)==pending and pending&(1<<26),'masked pending event lost'
 u.reg_write(reg,0);assert m.tick_eligible(u)
 row={};execute(u,m,row);m.leave_tick(u,row)
 assert row['frame_consumptions']==1 and not r32(u,0xe000ed04)&(1<<26)
def bad_return(kind):
 u,m=fixture();row={};execute(u,m,row);a=row['hardware_frame_address']
 if isinstance(kind,int):u.mem_write(u.reg_read(UC_ARM_REG_MSP)+4,struct.pack('<I',kind))
 elif kind=='invalid PSP':u.reg_write(UC_ARM_REG_PSP,0x20060000)
 elif kind=='unaligned PSP':u.reg_write(UC_ARM_REG_PSP,a+4)
 elif kind=='no Thumb':u.mem_write(a+28,bytes(4))
 elif kind=='invalid PC':u.mem_write(a+24,struct.pack('<I',0x20060000))
 elif kind=='odd PC':u.mem_write(a+24,struct.pack('<I',0x08006ef3))
 elif kind=='Handler frame':u.mem_write(a+28,struct.pack('<I',0x0100000f))
 elif kind=='PendSV tail chain':u.mem_write(0xe000ed04,struct.pack('<I',0x1000080f))
 atomic_reject(lambda:m.leave_tick(u,row),u)
def bad_entry(kind):
 u,m=fixture()
 if kind=='no pending':u.mem_write(0xe000ed04,struct.pack('<I',0x800))
 elif kind=='disabled':u.mem_write(0xe000e010,bytes(4))
 elif kind=='no TICKINT':u.mem_write(0xe000e010,struct.pack('<I',5))
 elif kind=='nested':u.reg_write(UC_ARM_REG_IPSR,14)
 elif kind=='FP context':u.reg_write(UC_ARM_REG_CONTROL,6)
 elif kind=='PendSV also pending':u.mem_write(0xe000ed04,struct.pack('<I',0x14000800))
 elif kind=='external active':u.mem_write(0xe000e300,b'\1')
 atomic_reject(lambda:m.enter_tick(u,{}),u)
def native():
 assert T['captured']['registers']['pc']==0x08006ef2 and T['handler']==0x08009331 and T['vector_word']==0x0800003c
 assert T['padding']==4 and T['hardware_frame_address']==0x200063a0
 assert T['captured']['clock_counter']==7 and T['after']['clock_counter']==8
 assert T['captured']['handler_counter']==0 and T['after']['handler_counter']==1
 assert T['after']['kernel_counter']==T['captured']['kernel_counter']==0
 assert T['after']['scheduler_hex']==T['captured']['scheduler_hex']
 assert not T['PendSV_requested'] and T['pre']==T['restored'] and T['frame_consumptions']==1
 assert [x['incoming']['name'] for x in D['PendSV']]==['Main','UI','Storage']
 assert all(x['frame_consumptions']==1 and not x['unexpected_RAM_writes'] for x in D['PendSV'])
 assert all(T['legacy_comparison'][k] for k in ('scheduler_hex','clock_counter','handler_counter','kernel_counter','registers','current_TCB'))
 assert not T['legacy_comparison']['full_RAM_equal'] and T['legacy_RAM_differences'][0]['address']==0x200063a0
if __name__=='__main__':
 ck('A/B/E native padded SysTick, no PendSV, identical restored Thread state and legacy scheduler observables',native)
 for pad in (False,True):ck('F native-handler fixture padded='+str(pad),lambda:roundtrip(pad))
 for k in ('BASEPRI','PRIMASK','FAULTMASK'):ck('D mask retains pending until unmask '+k,lambda:masked(k))
 for k in (0,0xfffffff5,0xfffffff9,0xffffffed,'invalid PSP','unaligned PSP','no Thumb','invalid PC','odd PC','Handler frame','PendSV tail chain'):ck('G reject unsupported return '+str(k),lambda:bad_return(k))
 for k in ('no pending','disabled','no TICKINT','nested','FP context','PendSV also pending','external active'):ck('reject entry '+k,lambda:bad_entry(k))
 (O/'regressions.json').write_text(json.dumps(dict(checks=rows,
  C=dict(confidence='UNKNOWN',observed=False,explanation='Native SysTick never requests PendSV in this prefix; later Main/UI requests are separate Thread writes; no tail chain fabricated.'),
  H=dict(confidence='UNKNOWN',observed_ticks=len(D['SysTick']),explanation='Storage reaches the next unsupported QSPI read before a second post-scheduler tick is due.')),indent=2)+'\n')
 print(f'{len(rows)} checks PASS; no fabricated tick-produced PendSV or second tick')
