"""Coupled native MSD -> queue wrapper -> worker -> backend -> SCSI/CSW slices.

Only queue payload movement, scheduler yield, physical DMA and USB TX/RX are
modeled. Backend bounds/semaphore/status, wrapper and worker are native B1.3.
Partial-completion cases are explicitly hypothetical faults, not silicon claims.
"""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase50-msd-readonly-geometry'))
from native_reads import fresh,ret,bpb
from geometry_from_sector import decode
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *

def run(kind,prior):
    e=fresh();u=e.uc;wrapper=e.r32(0x20006968);backend=e.r32(wrapper+4)
    e.w32(backend,0x0805b1ac) # native22F10 constructor's runtime vtable
    e.w32(backend+0xc,0xd4000 if kind=='bounds' else 0x2000000)
    u.mem_write(backend+8,bytes([0 if kind=='busy' else 1]))
    u.mem_write(wrapper+0xc,b'\0\1');e.w32(wrapper+0x10,0) # constructor23F2C pending/capacity
    e.call(0x08038c10,1)
    u.mem_write(0x40024000,prior)
    cb=bytearray(16);cb[0]=0x28;cb[2:6]=(64).to_bytes(4,'big');cb[7:9]=(1).to_bytes(2,'big')
    u.mem_write(0x20022000,bytes(cb));u.mem_write(0x20006898,b'\0'*0x20)
    e.w32(0x2000689c,4096);e.w32(0x200068a0,8192);e.w32(0x200067a4,4096)
    e.w32(0x200068cc,4096);e.w32(0x200068c8,0x5131) # BOT-admitted residue/tag, normally26DEE
    u.mem_write(0x200067a8,b'\x80');u.mem_write(0x200068d4,b'\0')
    pending=[];operations=[];tx=[];status=[];physical=[];worker=[False];yielded=[False]
    def hook(u,pc,n,d):
        if pc in (0x08024164,0x080241b8,0x080241f0,0x08037494,0x080374d4,0x08037648,
                  0x0803cc16,0x0803cc34,0x0803cc54,0x0801859a,0x08018612):raise AssertionError(f'write/flush {pc:x}')
        if pc==0x08036708:
            frame=u.reg_read(UC_ARM_REG_R1);ptr=e.r32(frame+4)
            raw=bytes(u.mem_read(ptr,24));pending.append(raw);operations.append(int.from_bytes(raw[:2],'little'));ret(e,1)
        elif pc==0x0803675c:ret(e,len(pending))
        elif pc==0x08036732:
            frame=u.reg_read(UC_ARM_REG_R1);u.mem_write(e.r32(frame+4),pending.pop(0));ret(e,1)
        elif pc==0x0801bde8:ret(e) # scheduler wake only
        elif pc==0x0801be60:
            assert not worker[0],'physical seam must not wait inside this completed-read model'
            yielded[0]=True;u.emu_stop()
        elif pc==0x08037430:
            addr=u.reg_read(UC_ARM_REG_R1);dst=u.reg_read(UC_ARM_REG_R2);nbytes=u.reg_read(UC_ARM_REG_R3)
            physical.append(dict(address=hex(addr),bytes=nbytes,buffer_before_sha256=hashlib.sha256(bytes(u.mem_read(dst,nbytes))).hexdigest()))
            assert addr==0xd4000 and nbytes==4096
            supplied=bpb() if kind=='normal' else bpb()[:512] if kind=='partial512-completion' else bpb()[:128]
            u.mem_write(dst,supplied)
            # Models the peripheral function returning after completion; not a
            # claim that physical errors actually cause this return.
            ret(e)
        elif pc==0x080240c4:status.append(u.reg_read(UC_ARM_REG_R0))
        elif pc==0x08024754:
            tx.append(bytes(u.mem_read(u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3))));ret(e)
        elif pc==0x08024770:ret(e)
    u.hook_add(UC_HOOK_CODE,hook)
    try:
        u.reg_write(UC_ARM_REG_SP,0x20008330);u.reg_write(UC_ARM_REG_LR,0x0807ff01)
        for reg,value in [(UC_ARM_REG_R0,0x20020000),(UC_ARM_REG_R1,0),(UC_ARM_REG_R2,0x20022000)]:u.reg_write(reg,value)
        pc=0x0803b27c
        for _ in range(20):
            yielded[0]=False;u.emu_start(pc|1,0xffffffff,count=300000)
            if u.reg_read(UC_ARM_REG_PC)==0x0807ff00:break
            assert yielded[0],hex(u.reg_read(UC_ARM_REG_PC))
            ctx=u.context_save();worker[0]=True
            try:e.call(0x08024014,wrapper,sp=0x2004e000,maxins=100000)
            finally:u.context_restore(ctx);worker[0]=False
            ret(e);pc=u.reg_read(UC_ARM_REG_PC)
        else:raise AssertionError('cooperative model did not finish')
        result=u.reg_read(UC_ARM_REG_R0)
    except Exception:
        print(dict(kind=kind,PC=hex(u.reg_read(UC_ARM_REG_PC)),pending=len(pending),operations=operations,status=status,physical=physical,sync=e.r32(wrapper+0x10)))
        raise
    assert result==0 and operations==[1] and len(tx)==1 and len(tx[0])==4096
    accepted=False;reason=None
    try:parsed=decode({64:tx[0]});accepted=True
    except ValueError as ex:reason=str(ex)
    # Finish native BOT status path after the data stage.
    e.call(0x08026db0,0x20020000,maxins=100000)
    assert len(tx)==2 and len(tx[1])==13 and tx[1][:4]==b'USBS'
    expected=2 if kind=='busy' else 1 if kind=='bounds' else 0
    assert status==[expected] and tx[1][8:13]==bytes(5),(kind,status,tx[1].hex(),backend,physical)
    if kind in ('busy','bounds'):assert tx[0]==bytes(4096) and not accepted and not physical
    if kind in ('normal','partial512-completion'):assert accepted
    return dict(kind=kind,prior_buffer_sha256=hashlib.sha256(prior).hexdigest(),wrapper=hex(wrapper),backend=hex(backend),
        wrapper_worker_backend_status=status,queued_operations=operations,physical_read_seam=physical,
        SCSI_return=result,USB_data_bytes=len(tx[0]),USB_data_sha256=hashlib.sha256(tx[0]).hexdigest(),
        CSW_hex=tx[1].hex(),CSW_status=tx[1][12],parser_accepted=accepted,parser_rejection=reason,
        persistent_write_or_FS_flush_calls=0,
        scope='Native status failure' if kind in ('busy','bounds') else 'Normal physical-read model' if kind=='normal' else 'Hypothetical incomplete DMA followed by completion-return seam; not a physical fault reproduction')
def main():
    cases=[run(k,p) for k in ('normal','busy','bounds','partial128-completion','partial512-completion') for p in (b'\xa5'*4096,bpb())]
    r=dict(confidence='PROVEN',scope='Native coupled slices with explicit model seams, no physical fault claim',cases=cases,
        previous_buffer_cleared=True,hardware_access=False,firmware_generated=False)
    (OUT/'read-cases.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(cases=len(cases),status_loss_cases=sum(c['kind'] in ('busy','bounds') for c in cases),
                         hypothetical_partial_accepted=sum(c['kind']=='partial512-completion' and c['parser_accepted'] for c in cases))))
if __name__=='__main__':main()
