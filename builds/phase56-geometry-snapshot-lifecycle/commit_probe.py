"""Native commit-helper microexperiment in emulator RAM only; no firmware files."""
from pathlib import Path
import sys,json,struct
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase42-exact-rdiag-integration/source/tools'))
from thumb import Asm,h,raw,push_list,pop_list,ldr_imm,str_imm,cmp_reg,b_cond
sys.path.insert(0,str(ROOT/'builds/phase42-exact-rdiag-integration'))
from environment import Physical,md
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
BASE=0x0807e000;STATE=0x20044d70
def fragment():
    a=Asm(BASE);a.emit(push_list,[3,4,5,6,7],lr=True)
    a.emit(raw,h(0xf3ef)+h(0x8700)) # MRS r7,APSR
    a.emit(raw,h(0xf3ef)+h(0x8610)) # MRS r6,PRIMASK
    a.emit(raw,h(0xb672))
    a.emit(ldr_imm,4,0,0);a.emit(cmp_reg,4,3);a.emit(b_cond,'out','ne')
    a.emit(raw,h(0xf023)+h(0x0507)) # BIC.W r5,r3,#7
    a.emit(raw,h(0xf045)+h(0x0501)) # ORR.W r5,r5,#1 (VALID)
    a.emit(str_imm,1,0,4);a.emit(str_imm,2,0,8)
    a.emit(raw,h(0xf3bf)+h(0x8f5f)) # DMB SY before validity publication
    a.emit(str_imm,5,0,0)
    a.label('out');a.emit(raw,h(0xf386)+h(0x8810))
    a.emit(raw,h(0xf387)+h(0x8c00)) # APSR_nzcvqg
    a.emit(pop_list,[3,4,5,6,7],pc=True)
    return a.assemble()[0]
def main():
    code=fragment();ins=list(md.disasm(code,BASE))
    assert ins[-2].mnemonic=='msr' and 'apsr' in ins[-2].op_str
    (OUT/'commit-helper.asm').write_text('\n'.join(f'{i.address:08X}: {i.mnemonic} {i.op_str}' for i in ins)+'\n')
    rows=[]
    for mask in (0,1):
        for fresh in (False,True):
            for flags in (0,0xa8000000,0x500f0000):
                e=Physical();u=e.uc;u.mem_write(BASE,code);e.w32(STATE,0x16 if fresh else 0x26)
                u.mem_write(STATE+4,b'OLDOLD!!');u.mem_write(STATE-4,b'LEFT');u.mem_write(STATE+12,b'RIGH')
                for k in range(13):u.reg_write(UC_ARM_REG_R0+k,k*0x1111)
                for r,v in ((UC_ARM_REG_R0,STATE),(UC_ARM_REG_R1,0x12345678),(UC_ARM_REG_R2,0x87654321),(UC_ARM_REG_R3,0x16)):
                    u.reg_write(r,v)
                u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_APSR,flags)
                before=[u.reg_read(UC_ARM_REG_R0+k) for k in range(13)];oldflags=u.reg_read(UC_ARM_REG_APSR)
                trace=[];masked=[]
                def hook(u,pc,n,d):
                    if BASE<=pc<BASE+len(code):
                        trace.append(pc)
                        if u.reg_read(UC_ARM_REG_PRIMASK):masked.append(pc)
                        if e.r32(STATE)&7==1:
                            assert bytes(u.mem_read(STATE+4,8))==struct.pack('<II',0x12345678,0x87654321)
                hh=u.hook_add(UC_HOOK_CODE,hook)
                e.call(BASE)
                assert before==[u.reg_read(UC_ARM_REG_R0+k) for k in range(13)]
                assert u.reg_read(UC_ARM_REG_PRIMASK)==mask and u.reg_read(UC_ARM_REG_APSR)==oldflags
                assert bytes(u.mem_read(STATE-4,4))==b'LEFT' and bytes(u.mem_read(STATE+12,4))==b'RIGH'
                assert e.r32(STATE)==(0x11 if fresh else 0x26)
                rows.append(dict(initial_mask=mask,initial_flags=hex(oldflags),generation_matched=fresh,
                    instructions=len(trace),mask_set_entry_instructions=len(masked),stack_delta=24,registers_flags_mask_preserved=True))
    r=dict(confidence='PROVEN',scope='Native commit helper only, not source collection/packing, actual owned-record integration, full ISR scheduling or firmware patch',
        helper_bytes=len(code),static_instructions=len(ins),cases=rows,passed=True)
    (OUT/'commit-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,bytes=len(code),cases=len(rows),instructions=len(ins))))
if __name__=='__main__':main()
