"""Native unmodified reader fragments; synthetic backend results, not NOR authentication."""
from pathlib import Path
import sys,json,struct
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
from inspect_reads import PUBLISHED
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *

def machine():
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x08000000,0x80000);u.mem_write(0x08010000,PUBLISHED[:])
    u.mem_map(0x20000000,0x50000)
    u.reg_write(UC_ARM_REG_SP,0x20008330);u.reg_write(UC_ARM_REG_LR,0x0807ff01)
    return u
def word(u,a,v):u.mem_write(a,struct.pack('<I',v))
def ret(u):u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
def run():
    rows=[]
    for status in (0,1,2):
        u=machine();payload=bytes(range(1,24));stale=b'\xa5'*23;seen={}
        word(u,0x20006968,0x2000ac94);word(u,0x2000ac94,0x20010000)
        word(u,0x2001000c,0x0807fe01);u.mem_write(0x20006868,stale)
        def identity_hook(u,a,n,d):
            if a==0x0807fe00:
                args=[u.reg_read(r) for r in (UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
                assert args==[0x81000,0x20006868,23]
                if status==0:u.mem_write(args[1],payload)
                u.reg_write(UC_ARM_REG_R0,status);ret(u)
            elif a==0x08025222:
                seen['at_first_return']=bytes(u.mem_read(0x20006868,23)).hex()
                seen['return_status']=u.reg_read(UC_ARM_REG_R0)
            elif a==0x0807ff00:u.emu_stop()
        u.hook_add(UC_HOOK_CODE,identity_hook);u.emu_start(0x0802520d,0,count=1000)
        before=payload if status==0 else stale
        assert seen['at_first_return']==before.hex()
        after=before[:14]+b'\0'+before[15:]
        assert bytes(u.mem_read(0x20006868,23))==after
        rows.append(dict(region='81000',synthetic_backend_status=status,**seen,normalizes_byte14_even_on_failure=True))
    for status in (0,1,2):
        u=machine();payload=bytes((i*37+9)&255 for i in range(512));stale=b'\xa5'*512;seen={}
        word(u,0x20006a00,0x20005148);word(u,0x20008330,0)
        u.mem_write(0x20005148,stale);u.reg_write(UC_ARM_REG_R6,0x080567ec);u.reg_write(UC_ARM_REG_R7,256)
        def resource_hook(u,a,n,d):
            if a==0x08047c6c:
                args=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
                assert args==[0x82000,0x20005148,512]
                if status==0:u.mem_write(args[1],payload)
                u.reg_write(UC_ARM_REG_R0,status);ret(u)
            elif a==0x08035ee6:
                seen['return_status']=u.reg_read(UC_ARM_REG_R0)
                assert bytes(u.mem_read(0x20005148,512))==(payload if status==0 else stale)
            elif a==0x0802968e:
                assert u.reg_read(UC_ARM_REG_R1)==0x20005148
                assert u.reg_read(UC_ARM_REG_R2)==512
                seen['upload_called_despite_status']=True;u.emu_stop()
        u.hook_add(UC_HOOK_CODE,resource_hook);u.emu_start(0x08035ed3,0,count=1000)
        assert seen['upload_called_despite_status']
        rows.append(dict(region='82000',synthetic_backend_status=status,**seen))
    result=dict(confidence='PROVEN',scope='Six native caller-boundary cases with synthetic backend success/failure; no physical completion or full boot simulated',cases=rows,passed=True)
    (OUT/'reader-boundaries.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=len(rows))))
if __name__=='__main__':run()
