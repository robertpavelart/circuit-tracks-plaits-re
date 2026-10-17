"""Architectural fixture tests, distinct from authentic reset controls.

Uses captured native bytes/frames. Variants change ONLY fixture CPU inputs,
not the stock/diagnostic replay or native task contexts. No fixture evidence
is presented as another native boot or as hardware behavior.
"""
import json
from svc import *
O=Path(__file__).resolve().parent
source=json.loads((O/'stock.json').read_text())['svc'];rows=[]
def fixture(psp=False,alignment=False,unprivileged=False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M7)
 for at,n in ((0x08000000,0x80000),(0x20000000,0x50000),(0xe000e000,0x2000)):u.mem_map(at,n)
 u.mem_write(0x08000000,ROM)
 for name in ('msp','psp'):
  u.reg_write(SPECIAL[name],source['pre'][name])
 for i,reg in enumerate(GENERAL):u.reg_write(reg,source['pre'][f'r{i}'])
 for name in ('xpsr','lr','basepri','primask','faultmask'):u.reg_write(SPECIAL[name],source['pre'][name])
 u.mem_write(0xe000ed08,struct.pack('<I',source['vector_base']))
 if psp:u.reg_write(UC_ARM_REG_PSP,source['restored']['psp'])
 selected='psp' if psp else 'msp'
 if alignment:u.reg_write(SPECIAL[selected],u.reg_read(SPECIAL[selected])-4)
 u.reg_write(UC_ARM_REG_CONTROL,(2 if psp else 0)|(1 if unprivileged else 0))
 u.reg_write(UC_ARM_REG_PC,0x080031c3)
 return u,SVC()
def ck(name,fn):
 fn();rows.append(dict(case=name,confidence='PROVEN',result='PASS',scope='architectural fixture, not full firmware execution'))
def roundtrip(psp=False,alignment=False,unprivileged=False):
 u,m=fixture(psp,alignment,unprivileged);before=snap(u)
 handler=m.enter(u,0x080031c2);entry=m.result
 assert handler==source['handler'] and entry['handler_entry']['ipsr']==11
 assert u.reg_read(UC_ARM_REG_SP)==u.reg_read(UC_ARM_REG_MSP)
 assert entry['padding']==(4 if alignment else 0)
 assert entry['entry_frame']['xpsr']&512==(512 if alignment else 0)
 entrymem=bytes(u.mem_read(entry['entry_frame_address'],32))
 resumed=m.leave(u,entry['entry_EXC_RETURN']);after=snap(u)
 assert resumed==0x080031c4 and after['pc']==resumed
 assert after['msp']==before['msp'] and after['psp']==before['psp']
 assert after['control']==before['control'] and after['ipsr']==0
 assert after['xpsr']==before['xpsr']
 assert all(after[f'r{i}']==before[f'r{i}'] for i in range(13))
 assert after['lr']==before['lr']
 assert bytes(u.mem_read(entry['entry_frame_address'],32))==entrymem
 try:m.leave(u,entry['entry_EXC_RETURN'])
 except AssertionError:pass
 else:raise AssertionError('double unstack accepted')
def rejection(kind):
 u,m=fixture();m.enter(u,0x080031c2);exc=0xfffffff9
 if isinstance(kind,int):exc=kind
 elif kind=='PSP out of range':exc=0xfffffffd;u.reg_write(UC_ARM_REG_PSP,0x20060000)
 elif kind=='unaligned PSP':exc=0xfffffffd;u.reg_write(UC_ARM_REG_PSP,0x20007e94)
 elif kind=='missing Thumb':u.mem_write(m.result['entry_frame_address']+28,struct.pack('<I',0))
 elif kind=='invalid PC':u.mem_write(m.result['entry_frame_address']+24,struct.pack('<I',0x20060000))
 elif kind=='nested frame':u.mem_write(m.result['entry_frame_address']+28,struct.pack('<I',0x0100000b))
 elif kind=='pending tail chain':u.mem_write(0xe000ed04,struct.pack('<I',0x1000000b))
 before=snap(u);mem=bytes(u.mem_read(0x20000000,0x50000))
 try:m.leave(u,exc)
 except AssertionError:pass
 else:raise AssertionError('invalid return accepted')
 assert snap(u)==before and bytes(u.mem_read(0x20000000,0x50000))==mem
def entry_rejection(kind):
 u,m=fixture()
 if kind=='nested handler':u.reg_write(UC_ARM_REG_IPSR,15)
 elif kind=='pending PendSV':u.mem_write(0xe000ed04,struct.pack('<I',1<<28))
 elif kind=='FP active':u.reg_write(UC_ARM_REG_CONTROL,4)
 elif kind=='masked SVC':u.reg_write(UC_ARM_REG_PRIMASK,1)
 elif kind=='BASEPRI blocks SVC':u.mem_write(0xe000ed1f,b'\xc0')
 elif kind=='unprivileged Thread':u.reg_write(UC_ARM_REG_CONTROL,1)
 before=snap(u);mem=bytes(u.mem_read(0x20000000,0x50000))
 try:m.enter(u,0x080031c2)
 except AssertionError:pass
 else:raise AssertionError('unsupported entry accepted')
 assert snap(u)==before and bytes(u.mem_read(0x20000000,0x50000))==mem
if __name__=='__main__':
 for psp in (False,True):
  for alignment in (False,True):
   ck(f'Thread {"PSP" if psp else "MSP"}, pad={alignment}',lambda:roundtrip(psp,alignment))
 for kind in (0,0xfffffff0,0xfffffff5,0xfffffff1,0xffffffed,0x080031c5,'PSP out of range','unaligned PSP','missing Thumb','invalid PC','nested frame','pending tail chain'):
  ck('reject '+(hex(kind) if isinstance(kind,int) else kind),lambda:rejection(kind))
 for kind in ('nested handler','pending PendSV','FP active','masked SVC','BASEPRI blocks SVC','unprivileged Thread'):ck('reject '+kind,lambda:entry_rejection(kind))
 (O/'regressions.json').write_text(json.dumps(rows,indent=2)+'\n');print(f'{len(rows)} architectural fixture checks PASS')
