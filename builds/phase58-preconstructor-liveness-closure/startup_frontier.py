"""Continue native startup after constructors until a real unsupported operation/loop."""
from pathlib import Path
import sys,json,collections
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import native_cases as prior
from constructor_probe import WATCH
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
def main():
    e=prior.Physical();u=e.uc;u.mem_write(0x08010000,prior.source.app)
    u.mem_map(0xe0042000,0x1000) # DBGMCU register shadow, not a ready/completion source.
    u.mem_write(0x20000000,bytes(0x50000));u.mem_write(0x20000000,prior.source.init)
    marker=bytes.fromhex('0123456789abcdef55aa55aa');u.mem_write(0x20044d70,marker)
    e.call(0x0805b958,0x0805b7d8,sp=0x2004fff8,maxins=100000)
    counts=collections.Counter();calls=[];ops=[];last=[];reason=None
    def hook(u,pc,n,d):
        counts[pc]+=1;last.append(pc)
        if len(last)>32:last.pop(0)
        if pc in WATCH:
            ops.append(dict(pc=hex(pc),kind=WATCH[pc]));raise RuntimeError('operation requires qualification')
        if counts[pc]>256:raise RuntimeError('repeated native wait/control frontier')
        ins=next(prior.source.md.disasm(bytes(u.mem_read(pc,n)),pc,count=1),None)
        if ins and ins.mnemonic in ('bl','blx'):
            t=u.reg_read(ins.operands[0].reg) if ins.mnemonic=='blx' else ins.operands[0].imm
            calls.append(dict(pc=hex(pc),target=hex(t&~1)))
    u.hook_add(UC_HOOK_CODE,hook)
    try:e.call(0x0801d3c8,sp=0x2004fff8,maxins=500000)
    except Exception as ex:reason=dict(type=type(ex).__name__,message=str(ex),pc=hex(u.reg_read(UC_ARM_REG_PC)))
    r=dict(confidence='PROVEN',scope='Native postconstructor startup with reset-zero shadow MMIO; stops instead of fabricating ready bits/IRQs or Storage completion',
        DBGMCU_shadow_added='0xe0042000..0xe0042fff, initial0',calls=calls,relevant_operations=ops,frontier=reason,last_PCs=[hex(p) for p in last],
        private_record_unchanged=bytes(u.mem_read(0x20044d70,12))==marker,first_mount_reached=False,full_scheduler_model=False)
    (OUT/'startup-frontier.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
