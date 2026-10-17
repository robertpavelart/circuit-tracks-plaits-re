"""Native constructor execution from decoded initialized data; no hardware/image output."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import native_cases as prior
from capstone.arm import ARM_OP_MEM,ARM_REG_PC
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
WATCH={0x080197a0:'FatFs mount',0x08019a92:'FatFs register',0x0801addc:'disk mount',
       0x08024164:'NOR wrapper write',0x080241b8:'NOR wrapper erase',0x08022fdc:'NOR backend program',
       0x08023078:'NOR backend erase',0x080374d4:'NOR program primitive',0x08037494:'NOR erase primitive',
       0x08037648:'NOR chip erase',0x0801a7ac:'filesystem disk write',0x08019e50:'file write',
       0x0801a440:'unlink',0x08025228:'identity writer',0x08026c10:'NOR query enqueue'}
def main():
    cases=[]
    for fill,reserved in ((0,False),(0xa5,False),(0,True)):
        e=prior.Physical();u=e.uc;u.mem_write(0x08010000,prior.source.app)
        u.mem_write(0x20000000,bytes([fill])*0x50000)
        u.mem_write(0x20000000,prior.source.init);u.mem_write(0x20003d04,bytes(0x2d50))
        if reserved:e.w32(0x20002b44,0x20044d70)
        marker=bytes.fromhex('0123456789abcdef55aa55aa');u.mem_write(0x20044d70,marker)
        before=bytes(u.mem_read(0x20000000,0x50000));pcs=set();calls=[];seen=[];n=0;mmio=[];minsp=0x20050000;allocations=[];private_writes=[]
        def private_write(u,access,address,size,value,data):private_writes.append(dict(address=hex(address),bytes=size,pc=hex(u.reg_read(UC_ARM_REG_PC))))
        u.hook_add(UC_HOOK_MEM_WRITE,private_write,begin=0x20044d70,end=0x20044d7b)
        def hook(u,pc,size,data):
            nonlocal n,minsp
            n+=1;pcs.add(pc)
            minsp=min(minsp,u.reg_read(UC_ARM_REG_SP))
            if pc in WATCH:
                seen.append(dict(pc=hex(pc),kind=WATCH[pc]));raise RuntimeError('relevant operation reached')
            if pc==0x0801d7d0:allocations.append(dict(bytes=u.reg_read(UC_ARM_REG_R0),cursor=hex(e.r32(0x20002b48)),limit=hex(e.r32(0x20002b44))))
            ins=next(prior.source.md.disasm(bytes(u.mem_read(pc,size)),pc,count=1),None)
            if ins:
                for op in ins.operands:
                    if op.type==ARM_OP_MEM and op.mem.base and op.mem.base!=ARM_REG_PC:
                        a=u.reg_read(op.mem.base)+op.mem.disp
                        if op.mem.index:a+=u.reg_read(op.mem.index)
                        if 0x40000000<=a<0x60000000 or 0xa0000000<=a<0xa0010000 or 0xe0000000<=a<0xe0100000:
                            mmio.append(dict(pc=hex(pc),address=hex(a),instruction=ins.mnemonic+' '+ins.op_str))
            if ins and ins.mnemonic in ('bl','blx'):
                target=u.reg_read(ins.operands[0].reg) if ins.mnemonic=='blx' else ins.operands[0].imm
                calls.append(dict(pc=hex(pc),target=hex(target&~1)))
        u.hook_add(UC_HOOK_CODE,hook)
        error=None
        try:r=e.call(0x0805b958,0x0805b7d8,sp=0x2004fff8,maxins=500000)
        except Exception as ex:error=dict(type=type(ex).__name__,message=str(ex),pc=hex(u.reg_read(UC_ARM_REG_PC)))
        else:assert r==0x0805b7d8
        after=bytes(u.mem_read(0x20000000,0x50000));changed=[];start=None
        for i,(x,y) in enumerate(zip(before,after)):
            if x!=y and start is None:start=i
            elif x==y and start is not None:changed.append([hex(0x20000000+start),hex(0x20000000+i)]);start=None
        if start is not None:changed.append([hex(0x20000000+start),hex(0x20050000)])
        cases.append(dict(fill=fill,existing_capacity_reserved=reserved,instructions=n,error=error,returned=error is None,
            calls=calls,relevant_operations=seen,changed_RAM_ranges=changed,
            explicit_MMIO_operands=mmio,minimum_SP=hex(minsp),heap_cursor_after=hex(e.r32(0x20002b48)),allocations=allocations,
            private_write_intents=private_writes,private_record_unchanged=bytes(u.mem_read(0x20044d70,12))==marker,
            executed_PCs=sorted(hex(p) for p in pcs)))
    result=dict(confidence='PROVEN',scope='Native constructor table execution, initialized-data/BSS provenance exact, other RAM poisoned; MMIO initially zero shadow and no RTOS/IRQ dispatch, so not global boot proof',
        image_sha256=hashlib.sha256(prior.source.app).hexdigest(),cases=cases)
    (OUT/'constructor-cases.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([dict(fill=c['fill'],instructions=c['instructions'],returned=c['returned'],error=c['error'],relevant=c['relevant_operations']) for c in cases],indent=2))
if __name__=='__main__':main()
