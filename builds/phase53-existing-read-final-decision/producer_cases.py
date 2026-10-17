"""Normal existing SCSI data-in producer sizes and low-window read binding.
No Phase52 target/control sequences; no physical storage or USB execution.
"""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase50-msd-readonly-geometry'))
from native_reads import fresh,ret
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
def data_in(op,allocation=255,evpd=False):
    e=fresh();u=e.uc;u.mem_write(0x40024000,b'\xa5'*4096)
    cb=bytearray(16);cb[0]=op;cb[1]=int(evpd);cb[4]=allocation
    u.mem_write(0x20022000,bytes(cb));u.mem_write(0x20006898,bytes(0x20))
    e.w32(0x200067a4,allocation);u.mem_write(0x200067a8,b'\x80')
    def code(u,pc,n,d):
        if pc in (0x08023f68,0x08024130,0x08024164,0x080241b8,0x0803cc16,0x0803cc34,0x0803cc54):raise AssertionError('Storage side effect')
    u.hook_add(UC_HOOK_CODE,code)
    try:result=e.call(0x0803b27c,0x20020000,0,0x20022000,maxins=100000)
    except Exception:
        print(dict(op=hex(op),PC=hex(u.reg_read(UC_ARM_REG_PC)),R0=hex(u.reg_read(UC_ARM_REG_R0)),R3=hex(u.reg_read(UC_ARM_REG_R3)),SP=hex(u.reg_read(UC_ARM_REG_SP))))
        raise
    assert result==0
    length=int.from_bytes(u.mem_read(0x200068d6,2),'little')
    data=bytes(u.mem_read(0x40024000,4096));modified=[i for i in range(4096) if data[i]!=0xa5]
    assert max(modified)<36 and data[36:512]==b'\xa5'*(512-36)
    assert all(data[i]!=0xa5 for i in range(length))
    return dict(opcode=hex(op),EVPD=evpd,allocation=allocation,generated_response_length=length,
                changed_offsets=modified,response_hex=data[:length].hex(),
                bytes36_through511_unchanged=True,persistent_or_storage_calls=0)
def low_lba(lba):
    e=fresh();u=e.uc;calls=[];e.call(0x08038c10,1)
    def hook(u,pc,n,d):
        if pc==0x08023fd6:ret(e)
        elif pc==0x08024130:
            calls.append(dict(address=hex(u.reg_read(UC_ARM_REG_R1)),bytes=u.reg_read(UC_ARM_REG_R3)));ret(e)
        elif pc in (0x08024164,0x080241b8):raise AssertionError('write')
    u.hook_add(UC_HOOK_CODE,hook)
    result=e.call(0x08057e88,0,0x40024000,lba,1,maxins=100000)
    assert result==0 and calls==[dict(address=hex(0x94000+lba*4096),bytes=4096)]
    return dict(USB_LBA=lba,physical_start=hex(0x94000+lba*4096),physical_end_inclusive=hex(0x94000+(lba+1)*4096-1),NOR_wrapper_reads=calls)
def main():
    commands=[data_in(0x12,36),data_in(0x12,255),data_in(0x12,255,True),data_in(3,18),data_in(3,255),
              data_in(0x1a),data_in(0x5a),data_in(0x25),data_in(0x23)]
    sectors=[low_lba(i) for i in range(64)]
    r=dict(confidence='PROVEN',scope='Native producers/binding; lower NOR wrapper and USB hardware not executed',
           commands=commands,mode1_LBAs_00_3F=sectors,max_non_NOR_generated_response_bytes=max(c['generated_response_length'] for c in commands),
           hardware_access=False,firmware_generated=False)
    (OUT/'producer-cases.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(SCSI_producer_cases=len(commands),low_window_bindings=len(sectors),max_generated_bytes=r['max_non_NOR_generated_response_bytes'])))
if __name__=='__main__':main()
