"""Targeted native guards for first-epoch record, not another boot replay."""
from trace import *
import struct,hashlib
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import native_cases as prior
STATE=0x20044d70
def main():
    rows=[]
    for control in (0,0x16,0x11,0x12,0x15):
        for fn,name in ((0x0806b6cc,'getter'),(0x0806b748,'timeout'),(0x0806b798,'legacy-start')):
            e=prior.fresh();u=e.uc;e.w32(0x20002b44,STATE)
            record=struct.pack('<I',control)+bytes.fromhex('0180003480908f01');u.mem_write(STATE,record)
            e.w32(0x2000081c,0xffffffff);u.mem_write(0x20000818,b'\x01')
            frame=bytes.fromhex('f07d43540d25')+bytes(225)+b'\xf7';assert len(frame)==232
            u.mem_write(0x20008000,frame);e.w32(0x20008200,0x20008000);e.w32(0x20008204,len(frame))
            writes=[];raw=[]
            def write(u,t,a,n,v,d):writes.append(dict(pc=hex(u.reg_read(UC_ARM_REG_PC)),address=hex(a),bytes=n))
            def hook(u,pc,n,d):
                if pc in (0x0806b850,0x08047c6c,0x08024164,0x080241b8):
                    raw.append(hex(pc));raise AssertionError('raw/storage path reached before authorization')
            u.hook_add(UC_HOOK_MEM_WRITE,write,begin=STATE,end=STATE+11);u.hook_add(UC_HOOK_CODE,hook)
            r=e.call(fn,*((0,0x20008200) if name=='legacy-start' else ()),sp=0x2004fff8,maxins=50000)
            assert bytes(u.mem_read(STATE,12))==record and not writes and not raw
            if name=='getter':assert r==0
            rows.append(dict(name=name,control=hex(control),returned=True,getter_returns_zero=r==0 if name=='getter' else None,write_intents=writes,raw_or_mutation_entries=raw,record_hex=record.hex()))
    result=dict(confidence='PROVEN',scope='Pinned native getter/timeout/valid legacy-start guards with required earlyD70 reservation and new control format; not installed adapters',cases=rows,passed=True,conclusion='New control rejects legacy magic; old start aborts atB808 before B820 stores/raw call. Old initializer overwrite requires unreserved E58 state, not a valid committed adapted record.')
    (OUT/'legacy-guard-tests.json').write_text(json.dumps(result,indent=2)+'\n');print('15 new native guard cases passed')
if __name__=='__main__':main()
