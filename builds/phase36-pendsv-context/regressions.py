"""Native evidence assertions and isolated captured-state architectural tests.

Fixture mutations below never enter the authentic stock/diagnostic replay.
No synthetic task frame is supplied to the native boot controls.
"""
import json
from pendsv import *
SOURCE=json.loads((O/'stock.json').read_text());FIRST=SOURCE['PendSV'][0];rows=[]
def ck(name,fn):
 fn();rows.append(dict(case=name,confidence='PROVEN',result='PASS'))
def fixture():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M7)
 for a,n in ((0x08000000,0x80000),(0x20000000,0x50000),(0xe000e000,0x2000)):u.mem_map(a,n)
 u.mem_write(0x08000000,ROM)
 cap=FIRST['captured'];pre=cap['registers']
 for i,reg in enumerate(GENERAL):u.reg_write(reg,pre[f'r{i}'])
 for name in ('msp','psp','lr','basepri','primask','faultmask','xpsr','control'):u.reg_write(SPECIAL[name],pre[name])
 u.reg_write(UC_ARM_REG_PC,pre['pc']|1)
 for at,val in ((0xe000ed08,cap['VTOR']),(0xe000ed04,cap['ICSR']),(0xe000ed20,cap['SHPR3']),(0xe000ed24,cap['SHCSR']),(0xe000ed0c,cap['AIRCR'])):u.mem_write(at,struct.pack('<I',val))
 u.mem_write(cap['stack_window_address'],bytes.fromhex(cap['stack_window_hex']))
 u.mem_write(cap['MSP_stack_address'],bytes.fromhex(cap['MSP_stack_hex']))
 u.mem_write(cap['scheduler_base'],bytes.fromhex(cap['scheduler_hex']))
 for t in (cap['current_task'],FIRST['incoming']):
  u.mem_write(t['TCB'],bytes.fromhex(t['TCB_hex']));u.mem_write(t['saved_PSP'],bytes.fromhex(t['context_hex']))
 return u,Model()
def atomic_reject(fn,u):
 before=snap(u);ram_before=bytes(u.mem_read(0x20000000,0x50000));system_before=bytes(u.mem_read(0xe000e000,0x2000))
 try:fn()
 except AssertionError:pass
 else:raise AssertionError('unsupported fixture accepted')
 assert snap(u)==before and bytes(u.mem_read(0x20000000,0x50000))==ram_before and bytes(u.mem_read(0xe000e000,0x2000))==system_before
def roundtrip(padded):
 u,m=fixture()
 if padded:u.reg_write(UC_ARM_REG_PSP,u.reg_read(UC_ARM_REG_PSP)-4)
 before=snap(u);row={};handler=m.enter_pendsv(u,row)
 assert handler==0x0800312d and row['padding']==(4 if padded else 0)
 assert row['hardware_frame']['pc']==before['pc'],'asynchronous exception must not advance PC'
 assert row['hardware_frame_address']%8==0
 assert u.reg_read(UC_ARM_REG_IPSR)==14 and u.reg_read(UC_ARM_REG_SP)==before['msp']
 assert u.reg_read(UC_ARM_REG_CONTROL)==0 and u.reg_read(UC_ARM_REG_LR)==0xfffffffd
 assert r32(u,0xe000ed04)==0x80e and not r32(u,0xe000ed04)&(1<<28)
 assert r32(u,0xe000ed24)&(1<<10)
 m.leave_pendsv(u,row);after=snap(u)
 assert all(after[k]==before[k] for k in before),'entry/return failed exact CPU roundtrip'
 assert row['frame_consumptions']==1 and r32(u,0xe000ed04)==0x800
 assert not r32(u,0xe000ed24)&(1<<10)
 atomic_reject(lambda:m.leave_pendsv(u,row),u)
def invalid_context(kind):
 u,m=fixture();a=FIRST['incoming']['saved_PSP']
 if kind=='unaligned':a+=4
 elif kind=='below RAM':a=0x1ffffffc
 elif kind=='past RAM':a=0x20050004
 elif kind=='straddles RAM end':a=0x2004fffc
 elif kind=='invalid EXC_RETURN':u.mem_write(a+32,struct.pack('<I',0xfffffff5))
 elif kind=='FP EXC_RETURN':u.mem_write(a+32,struct.pack('<I',0xffffffed))
 elif kind=='no Thumb':u.mem_write(a+64,bytes(4))
 elif kind=='invalid PC':u.mem_write(a+60,struct.pack('<I',0x20060000))
 elif kind=='odd PC':u.mem_write(a+60,struct.pack('<I',0x08002fdf))
 elif kind=='Handler frame':u.mem_write(a+64,struct.pack('<I',0x0100000e))
 atomic_reject(lambda:validate_context(u,a),u)
def entry_reject(kind):
 u,m=fixture()
 if kind=='PRIMASK':u.reg_write(UC_ARM_REG_PRIMASK,1)
 elif kind=='FAULTMASK':u.reg_write(UC_ARM_REG_FAULTMASK,1)
 elif kind=='BASEPRI C0':u.reg_write(UC_ARM_REG_BASEPRI,0xc0)
 elif kind=='BASEPRI F0':u.reg_write(UC_ARM_REG_BASEPRI,0xf0)
 elif kind=='no pending':u.mem_write(0xe000ed04,bytes(4))
 elif kind=='nested':u.reg_write(UC_ARM_REG_IPSR,11)
 elif kind=='FP active':u.reg_write(UC_ARM_REG_CONTROL,6)
 elif kind=='MSP Thread':u.reg_write(UC_ARM_REG_CONTROL,0)
 elif kind=='SysTick also pending':u.mem_write(0xe000ed04,struct.pack('<I',0x14000000))
 elif kind=='external pending':u.mem_write(0xe000e200,b'\1')
 atomic_reject(lambda:m.enter_pendsv(u,{}),u)
def return_reject(kind):
 u,m=fixture();row={};m.enter_pendsv(u,row)
 if isinstance(kind,int):u.reg_write(UC_ARM_REG_LR,kind)
 elif kind=='bad PSP':u.reg_write(UC_ARM_REG_PSP,0x20060000)
 elif kind=='unaligned PSP':u.reg_write(UC_ARM_REG_PSP,0x20007e84)
 elif kind=='no Thumb':u.mem_write(row['hardware_frame_address']+28,bytes(4))
 elif kind=='invalid PC':u.mem_write(row['hardware_frame_address']+24,struct.pack('<I',0x20060000))
 elif kind=='pending tail chain':u.mem_write(0xe000ed04,struct.pack('<I',0x1000080e))
 atomic_reject(lambda:m.leave_pendsv(u,row),u)
def native_checks():
 p=FIRST
 assert p['captured']['registers']['pc']==0x08002a6e and p['captured']['current_task']['name']=='IDLE'
 assert p['outgoing_saved_PSP']==0x20007e5c
 expected=[p['pre'][f'r{i}'] for i in range(4,12)]+[0xfffffffd]
 assert p['outgoing_software_frame_hex']==struct.pack('<9I',*expected).hex()
 assert p['incoming']['TCB']==0x20006488 and p['incoming']['saved_PSP']==0x2000643c
 assert p['restored']['pc']==0x08002fde and p['restored']['psp']==0x20006480 and p['restored']['control']==2
 assert all(p['restored'][f'r{i}']==0xa5a5a5a5 for i in range(4,12))
 assert p['unexpected_RAM_writes']==[] and p['frame_consumptions']==1
 assert not {0x0800313e,0x0800317a}&{x['pc'] for x in p['native_trace']},'FP path unexpectedly executed'
 assert p['ICSR_active']==0x80e and p['ICSR_return']==0x800
if __name__=='__main__':
 ck('A/B/C/D/H captured native PendSV save/scheduler/restore/pending consumption',native_checks)
 for padded in (False,True):ck(f'G architectural PSP entry/return padded={padded}, single consumption',lambda:roundtrip(padded))
 for k in ('unaligned','below RAM','past RAM','straddles RAM end','invalid EXC_RETURN','FP EXC_RETURN','no Thumb','invalid PC','odd PC','Handler frame'):ck('E/F reject next context '+k,lambda:invalid_context(k))
 for k in ('PRIMASK','FAULTMASK','BASEPRI C0','BASEPRI F0','no pending','nested','FP active','MSP Thread','SysTick also pending','external pending'):ck('reject unsupported entry '+k,lambda:entry_reject(k))
 for k in (0,0xfffffff5,0xfffffff9,0xffffffed,'bad PSP','unaligned PSP','no Thumb','invalid PC','pending tail chain'):ck('reject return '+str(k),lambda:return_reject(k))
 (O/'regressions.json').write_text(json.dumps(dict(checks=rows,native_second_PendSV=dict(confidence='UNKNOWN',observed_count=len(SOURCE['PendSV']),explanation='No second PendSV occurs before the first due post-scheduler SysTick boundary; no event fabricated.')),indent=2)+'\n')
 print(f'{len(rows)} native-evidence / architectural-fixture checks PASS; second PendSV not observed within bounded prefix')
