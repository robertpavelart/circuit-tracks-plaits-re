"""Derive an instrumented Phase59 continuation without modifying its evidence."""
from pathlib import Path
import hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def main():
    src=ROOT/'builds/phase59-scheduler-first-mount-order/native_startup.py'
    s=src.read_text()
    s=s.replace('    e.call(0x0801bc78,', '    from irq_observer import Observer\n    observer=Observer(e,OUT)\n    e.call(0x0801bc78,',1)
    s=s.replace("    result['switches']=switches", "    observer.finish()\n    result['switches']=switches",1)
    s=s.replace('        ins=cache[pc]', '''        ins=cache[pc]
        irq=observer.injection(pc)
        if irq is not None:
            action[0]=('external',(irq,pc));u.emu_stop();return
        if u.reg_read(UC_ARM_REG_IPSR)>=16 and ins and ins.mnemonic.startswith('pop') and ins.operands[-1].reg==UC_ARM_REG_PC:
            cnt=len(ins.operands);sp=u.reg_read(UC_ARM_REG_MSP);exc=e.r32(sp+4*(cnt-1))
            if exc>=0xfffffff0:
                action[0]=('external-pop',(ins,cnt,exc));u.emu_stop();return''',1)
    s=s.replace("            elif kind=='pendsv':",'''            elif kind=='external':
                irq,resume=value;pc=exception_enter(irq+16,resume)
            elif kind=='external-pop':
                ins,cnt,exc=value;sp=u.reg_read(UC_ARM_REG_MSP)
                for i,op in enumerate(ins.operands[:-1]):u.reg_write(op.reg,e.r32(sp+4*i))
                u.reg_write(UC_ARM_REG_MSP,sp+4*cnt);pc=exception_leave(exc)
            elif kind=='pendsv':''',1)
    s=s.replace('        t=e.r32(0x20006138)\n        switches.append', '        t=e.r32(0x20006138)\n        if t==0:return vals[6] # external IRQ before native task creation has no TCB\n        switches.append',1)
    (OUT/'instrumented_startup.py').write_text(s)
    (OUT/'runner-provenance.txt').write_text('Phase59 input SHA256 '+hashlib.sha256(src.read_bytes()).hexdigest()+'\nDerived observer-only continuation; original file unchanged.\n')
if __name__=='__main__':main()
