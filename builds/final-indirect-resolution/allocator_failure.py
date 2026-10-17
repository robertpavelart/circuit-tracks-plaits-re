"""Isolated native allocator ABI check; no peripheral or hardware execution.

Stop before BKPT. A separate explicitly counterfactual continuation verifies
the post-BKPT return ABI; it does NOT emulate physical debug/fault routing.
"""
from inspect_bytes import A,O
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
import json,struct
STOP=0x807ff00
def case(entry,size,resume=False):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x8010000,0x80000);u.mem_write(0x8010000,A.image)
    u.mem_map(0x20000000,0x50000)
    u.mem_write(0x20002b44,struct.pack('<II',0x20044d70,0x20044d68))
    u.reg_write(UC_ARM_REG_SP,0x2004f000);u.reg_write(UC_ARM_REG_R0,size)
    u.reg_write(UC_ARM_REG_LR,STOP|1);trace=[];hit=[]
    def code(uc,pc,n,data):
        trace.append(hex(pc))
        if pc==STOP or pc==0x801d7f4:
            if pc==0x801d7f4:hit.append(dict(pc=hex(pc),r0=hex(uc.reg_read(UC_ARM_REG_R0)),r1=hex(uc.reg_read(UC_ARM_REG_R1))))
            uc.emu_stop()
    u.hook_add(UC_HOOK_CODE,code)
    u.emu_start(entry|1,0,count=200)
    if size>8:assert hit and u.reg_read(UC_ARM_REG_PC)==0x801d7f4
    else:assert not hit and u.reg_read(UC_ARM_REG_PC)==STOP
    if resume:
        assert hit
        u.emu_start(0x801d7f7,0,count=200) # begin at instruction AFTER BKPT
        assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_R0)==0xffffffff
    cursor=int.from_bytes(u.mem_read(0x20002b48,4),'little')
    assert cursor==(0x20044d70 if size==8 else 0x20044d68)
    return dict(entry=hex(entry),request_bytes=size,stopped_before_BKPT=bool(hit),
        counterfactual_resume_after_BKPT=resume,return_r0=hex(u.reg_read(UC_ARM_REG_R0)),
        cursor=hex(cursor),trace=trace)
rows=[case(0x801d7d8,8),case(0x801d7d8,12),case(0x801d7d8,12,True),case(0x801cfa4,12,True)]
assert A.word(0x801000c)==0x8059961
i=next(A.md.disasm(A.read(0x8059960,4),0x8059960,count=1))
assert i.mnemonic=='b' and i.operands[0].imm==0x8059960
result=dict(candidate_sha256=__import__('hashlib').sha256(A.image).hexdigest(),cases=rows,
    hardfault_vector='08059961',hardfault_handler='08059960: B 08059960',
    physical_BKPT_exception_routing='UNKNOWN: not modeled or observed; test stops before instruction',
    post_READY_reachability='UNKNOWN; these are allocator ABI inputs only',passed=True)
(O/'allocator-failure.json').write_text(json.dumps(result,indent=2)+'\n')
print('Four isolated allocator cases passed; BKPT routing was not modeled.')
