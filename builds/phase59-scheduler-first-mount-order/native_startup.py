"""Phase59 native startup experiment. Emulator RAM/register shadows only; no firmware output."""
from pathlib import Path
import sys,json,collections,struct
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import native_cases as prior
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *

def main():
    extended='--peripheral-completion-model' in sys.argv
    valid='--valid-bpb' in sys.argv
    invalid_bpb='--invalid-bpb' in sys.argv
    early_tick='--early-systick' in sys.argv
    delay_clock=8 if '--delayed-clock' in sys.argv else 2
    delayed_storage='--delayed-storage' in sys.argv
    earliest_timer='--earliest-timer' in sys.argv
    queued='--queued-query' in sys.argv
    case=next((s.split('=',1)[1] for s in sys.argv if s.startswith('--case=')),None)
    sys.path.insert(0,str(ROOT/'builds/phase55-precleanup-geometry-snapshot'))
    from audit import sector
    bpb=sector()
    e=prior.Physical();u=e.uc
    u.mem_write(0x08010000,prior.source.app);u.mem_map(0xe0042000,0x1000)
    u.mem_write(0x20000000,bytes(0x50000));u.mem_write(0x20000000,prior.source.init)
    e.call(0x0801bc78,sp=0x2004fff8,maxins=1000) # authenticated reset clock/vector prefix, not a guessed VTOR.
    e.w32(0x20002b44,0x20044d70) # Phase58 authenticated early reservation model.
    marker=bytes.fromhex('0123456789abcdef55aa55aa');u.mem_write(0x20044d70,marker)
    e.call(0x0805b958,0x0805b7d8,sp=0x2004fff8,maxins=100000)
    counts=collections.Counter();calls=[];events=[];last=[];cache={};writes=[];action=[None];switches=[];operations=[];reads=[];pending_reads=[];launch=[];completion_due=[None]
    watch={0x08024164:'wrapper program',0x080241b8:'wrapper erase',0x08022fdc:'backend program',0x08023078:'backend erase',0x080374d4:'NOR program',0x08037494:'NOR erase',0x08037648:'NOR chip erase',0x08025228:'identity write',0x080197a0:'mount',0x08019a92:'mount registration',0x0801a7ac:'filesystem write',0x0801a440:'unlink',0x08023f68:'storage enqueue',0x08024014:'storage drain',0x08022a5c:'content enqueue',0x08022ae4:'content drain',0x0801e480:'timer configure',0x0801e51e:'timer callback'}
    watch.update({0x08057ef4:'MSD write callback',0x08019e50:'file write',0x08026c10:'query producer',0x0801af1e:'mapped filesystem write',0x0801e4be:'timer service',0x08036708:'ring enqueue',0x08036732:'ring dequeue',0x08057650:'NOR completion wait',0x08057664:'completion notify'})
    def hook(u,pc,n,d):
        counts[pc]+=1;last.append(pc)
        if len(last)>40:last.pop(0)
        if pc not in cache:cache[pc]=next(prior.source.md.disasm(bytes(u.mem_read(pc,n)),pc,count=1),None)
        ins=cache[pc]
        if early_tick and switches and not injected_tick and not u.reg_read(UC_ARM_REG_IPSR) and not u.reg_read(UC_ARM_REG_BASEPRI) and not u.reg_read(UC_ARM_REG_PRIMASK):
            action[0]=('early-tick',pc);u.emu_stop();return
        if valid and pc==0x08037596 and e.r8(0x20006a47):
            obj=e.r32(0x20006790)
            if obj:
                if delayed_storage:
                    completion_due[0]=e.r32(0x20006a28)+3
                    events.append(dict(pc=hex(pc),model='NOR completion notification deferred by three SysTick wake events',object=hex(obj)))
                else:
                    e.w32(obj+8,e.r32(obj+8)|0x100)
                    events.append(dict(pc=hex(pc),model='immediate NOR completion notification flag100 before observer wait; IRQ arbitration unmodeled',object=hex(obj)))
        if valid and pc==0x08037594 and e.r32(u.reg_read(UC_ARM_REG_R5)+4)==3:
            a=u.reg_read(UC_ARM_REG_R6)-3;u.mem_write(a,bytes.fromhex('ef4019'))
            events.append(dict(pc=hex(pc),model='synthetic JEDEC ID EF4019, 32MiB capacity',destination=hex(a)))
        if pc in watch:
            operations.append(dict(pc=hex(pc),kind=watch[pc],TCB=hex(e.r32(0x20006138)),args=[hex(u.reg_read(r)) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)],instruction_index=sum(counts.values())))
            if pc==0x08023f68:
                operations[-1]['request_words']=[hex(e.r32(u.reg_read(UC_ARM_REG_R1)+i*4)) for i in range(6)]
        if earliest_timer and pc==0x0801d698 and counts[pc]==1:
            for srv in (0x20000354,0x20000360):
                a=e.r32(srv+4)+10;u.mem_write(a,bytes([u.mem_read(a,1)[0]+1]))
            events.append(dict(pc=hex(pc),model='one pending timer-service tick each at earliest UI poll; timer IRQ producer not replayed'))
        if pc==0x08037430:
            row=dict(address=u.reg_read(UC_ARM_REG_R1),buffer=u.reg_read(UC_ARM_REG_R2),length=u.reg_read(UC_ARM_REG_R3));pending_reads.append(row);reads.append(row)
        if pc==0x0803748e and pending_reads:
            row=pending_reads.pop()
            if valid:
                data=bpb if not invalid_bpb and row['address']==0xd4000 and row['length']==4096 else bytes(row['length'])
                u.mem_write(row['buffer'],data);row['data_model']='synthetic FAT16 BPB at D4000' if data==bpb else 'synthetic zeros'
        if pc==0x0805999a and u.reg_read(UC_ARM_REG_IPSR)==15:
            action[0]=('popreturn',pc);u.emu_stop();return
        if pc==0x0801ae06:
            action[0]=('snapshot',pc);u.emu_stop();return
        if ins and ins.mnemonic=='bx' and u.reg_read(ins.operands[0].reg)>=0xfffffff0:
            action[0]=('exception-return',u.reg_read(ins.operands[0].reg));u.emu_stop();return
        if extended and not u.reg_read(UC_ARM_REG_IPSR) and not u.reg_read(UC_ARM_REG_PRIMASK) and not u.reg_read(UC_ARM_REG_BASEPRI) and e.r32(0xe000ed04)&(1<<28):
            action[0]=('pendsv',pc);u.emu_stop();return
        if extended and pc==0x0801bd90:
            # Explicit elapsed-time model, not an assertion that SysTick advances this counter.
            e.w32(0x2000081c,e.r32(0x2000081c)+1)
            if counts[pc]<4:events.append(dict(pc=hex(pc),model='one elapsed millisecond per clock-counter poll',counter='0x2000081c'))
        if extended and pc==0x0801c63c:
            a=u.reg_read(UC_ARM_REG_R4)
            if u.mem_read(a,1)[0]&2:
                u.mem_write(a,b'\x05');events.append(dict(pc=hex(pc),address=hex(a),model='SD command timeout status5 (card absent); not SD IRQ replay'))
        if extended and pc==0x0801b8de:
            a=u.reg_read(UC_ARM_REG_R0)
            if u.mem_read(a,1)[0]&2:
                u.mem_write(a,b'\x05');events.append(dict(pc=hex(pc),address=hex(a),model='SD command timeout visible to synchronous wrapper'))
        if pc==0x0801d9ea:
            launch.append(dict(current=hex(e.r32(0x20006138)),ready_bitmap=hex(e.r32(0x20006148)),ready_list=bytes(u.mem_read(0x200060d4,20)).hex(),timer_services={hex(a):bytes(u.mem_read(a,12)).hex() for a in (0x20000354,0x20000360)},storage_wrappers={hex(a):bytes(u.mem_read(e.r32(a),28)).hex() for a in (0x20006968,0x2000696c)}))
            events.append(dict(pc=hex(pc),event='first scheduler architectural launch boundary',current=hex(e.r32(0x20006138)),bitmap=hex(e.r32(0x20006148))))
            action[0]=('svc',pc);u.emu_stop();return
        if extended and pc==0x080375b6:
            a=u.reg_read(UC_ARM_REG_R0);v=e.r32(a)
            if not v&1:
                e.w32(a,v|1);events.append(dict(pc=hex(pc),address=hex(a),before=hex(v),after=hex(e.r32(a)),model='NOR controller completion status bit0; not IRQ replay'))
        # Exact loop predicates are supplied only after seeing the native loop twice.
        if counts[pc]==2 and pc in (0x0801b266,0x0801b274,0x0801b28a,0x0801b2b8):
            events.append(dict(pc=hex(pc),event='candidate-clock-wait',r4=hex(u.reg_read(UC_ARM_REG_R4))))
        if pc==0x0801b266 and counts[pc]==delay_clock:
            a=u.reg_read(UC_ARM_REG_R4);v=e.r32(a);e.w32(a,v|1<<17)
            events.append(dict(pc=hex(pc),address=hex(a),before=hex(v),after=hex(e.r32(a)),predicate='bit17 set'))
        if pc==0x0801b274 and counts[pc]==delay_clock:
            a=u.reg_read(UC_ARM_REG_R4);v=e.r32(a);e.w32(a,v|1<<29)
            events.append(dict(pc=hex(pc),address=hex(a),before=hex(v),after=hex(e.r32(a)),predicate='bit29 set'))
        if pc==0x0801b282 and counts[pc]==delay_clock:
            a=u.reg_read(UC_ARM_REG_R4);v=e.r32(a);e.w32(a,v|1<<25)
            events.append(dict(pc=hex(pc),address=hex(a),before=hex(v),after=hex(e.r32(a)),predicate='bit25 set'))
        if pc==0x0801b2a2:
            a=0x40023808;v=e.r32(a);e.w32(a,(v&~12)|8)
            events.append(dict(pc=hex(pc),address=hex(a),before=hex(v),after=hex(e.r32(a)),predicate='SWS[3:2]=2 after SW[1:0]=2'))
        if counts[pc]>10000:raise RuntimeError('unmodeled repeated native loop')
        if ins and ins.mnemonic in ('bl','blx'):
            t=u.reg_read(ins.operands[0].reg) if ins.mnemonic=='blx' else ins.operands[0].imm
            calls.append(dict(pc=hex(pc),target=hex(t&~1),r0=hex(u.reg_read(UC_ARM_REG_R0))))
    def wh(u,access,a,size,value,d):writes.append(dict(address=hex(a),size=size,value=hex(value),pc=hex(u.reg_read(UC_ARM_REG_PC))))
    u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,wh,begin=0x20044d70,end=0x20044d7b)
    reason=None
    frame=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_XPSR]
    def exception_enter(number,resume):
        assert u.reg_read(UC_ARM_REG_IPSR)==0
        psp=bool(u.reg_read(UC_ARM_REG_CONTROL)&2);sr=UC_ARM_REG_PSP if psp else UC_ARM_REG_MSP
        old=u.reg_read(sr);pad=4 if old&4 else 0;a=old-32-pad
        vals=[u.reg_read(r) for r in frame];vals[6]=resume;vals[7]=(vals[7]&~512)|(512 if pad else 0)
        u.mem_write(a,struct.pack('<8I',*vals));u.reg_write(sr,a)
        u.reg_write(UC_ARM_REG_CONTROL,0);u.reg_write(UC_ARM_REG_XPSR,(vals[7]&0xf80f0000)|0x01000000|number)
        u.reg_write(UC_ARM_REG_LR,0xfffffffd if psp else 0xfffffff9)
        e.w32(0xe000ed04,number)
        return e.r32(0x08010000+number*4)&~1
    def exception_leave(exc):
        assert exc in (0xfffffffd,0xfffffff9)
        sr=UC_ARM_REG_PSP if exc&4 else UC_ARM_REG_MSP;a=u.reg_read(sr)
        vals=struct.unpack('<8I',bytes(u.mem_read(a,32)));assert vals[7]&0x1000000 and not vals[7]&511
        for r,v in zip(frame[:6],vals[:6]):u.reg_write(r,v)
        u.reg_write(UC_ARM_REG_XPSR,vals[7]&~512);u.reg_write(sr,a+32+(4 if vals[7]&512 else 0));u.reg_write(UC_ARM_REG_CONTROL,2 if exc&4 else 0)
        e.w32(0xe000ed04,0)
        t=e.r32(0x20006138)
        switches.append(dict(TCB=hex(t),name=bytes(u.mem_read(t+0x34,10)).split(b'\0')[0].decode(),entry=hex(vals[6]),priority=e.r32(t+0x2c)))
        return vals[6]
    injected_tick=False;injected_queue=False
    try:
        u.reg_write(UC_ARM_REG_SP,0x2004fff8);u.reg_write(UC_ARM_REG_LR,0x0807ff01);pc=0x0801d3c8
        for boundary in range(300):
            action[0]=None;u.emu_start(pc|1,0xffffffff,count=1000000)
            if not action[0]:
                if extended and u.reg_read(UC_ARM_REG_PC)==0x0801d768:
                    assert e.r32(0xe000e010)&3==3 and not u.reg_read(UC_ARM_REG_PRIMASK) and not u.reg_read(UC_ARM_REG_BASEPRI)
                    if completion_due[0] is not None and e.r32(0x20006a28)>=completion_due[0]:
                        # Deliver the real native notification API without inventing a ready-list edit.
                        ctx=u.context_save();obj=e.r32(0x20006790)
                        e.w32(e.r32(0x20000000),e.r32(e.r32(0x20000000))|1)
                        e.call(0x0801bde8,obj,0x100,sp=u.reg_read(UC_ARM_REG_SP)-0x40,maxins=10000)
                        u.context_restore(ctx);completion_due[0]=None
                        events.append(dict(event='deferred completion delivered through native 1BDE8',tick=e.r32(0x20006a28),scope='modeled notification arrival, not native IRQ entry'))
                    events.append(dict(event='SysTick wake from native idle WFI',pc='0x0801d768',tick_before=e.r32(0x20006a28)))
                    pc=exception_enter(15,0x0801d768);continue
                raise RuntimeError('native instruction limit or ordinary return')
            kind,value=action[0]
            if kind=='snapshot':reason=dict(type='checkpoint',message='first native disk-mount return reached',pc=hex(value));break
            if kind=='svc':
                if queued and not injected_queue:
                    ctx=u.context_save()
                    req=e.call(0x0801cfa4,32,0x08026b22,sp=0x2004ff00,maxins=10000)
                    assert 0x20000000<=req<0x20044d70
                    u.mem_write(req,struct.pack('<6I',0,1,req+24,1,0,0))
                    e.call(0x08023f68,e.r32(0x20006968),req,sp=0x2004ff00,maxins=10000)
                    u.context_restore(ctx);injected_queue=True
                    events.append(dict(event='prepopulated well-formed NOR status query through native producer23F68',record=hex(req),scope='valid queue state; no normal boot producer claimed'))
                if early_tick:events.append(dict(event='early SysTick pending at first SVC; masked until native BASEPRI clear',BASEPRI=hex(u.reg_read(UC_ARM_REG_BASEPRI))))
                pc=exception_enter(11,value+2)
            elif kind=='early-tick':
                injected_tick=True;events.append(dict(event='early pending SysTick serviced at first eligible Thread instruction',pc=hex(value)))
                pc=exception_enter(15,value)
            elif kind=='pendsv':pc=exception_enter(14,value)
            elif kind=='exception-return':pc=exception_leave(value)
            elif kind=='popreturn':
                a=u.reg_read(UC_ARM_REG_MSP);r0,exc=struct.unpack('<2I',bytes(u.mem_read(a,8)))
                u.reg_write(UC_ARM_REG_R0,r0);u.reg_write(UC_ARM_REG_MSP,a+8);pc=exception_leave(exc)
        else:raise RuntimeError('architectural exception boundary limit')
    except Exception as ex:reason=dict(type=type(ex).__name__,message=str(ex),pc=hex(u.reg_read(UC_ARM_REG_PC)))
    tasks=[]
    for off in (0,4,8,12):
        obj=e.r32(0x2000677c+off)
        if obj:
            t=e.r32(obj);p=e.r32(t)
            tasks.append(dict(object=hex(obj),TCB=hex(t),priority=e.r32(t+0x2c),name=bytes(u.mem_read(t+0x34,10)).split(b'\0')[0].decode('ascii'),saved_stack=hex(p),context=bytes(u.mem_read(p,68)).hex(),notification=e.r32(obj+8)))
    result=dict(scope='Native corrected image; normal clock predicate releases only where explicitly listed',peripheral_completion_model=extended,events=events,calls=calls,frontier=reason,last_PCs=[hex(p) for p in last],private_writes=writes,private_unchanged=bytes(u.mem_read(0x20044d70,12))==marker,executed_instructions=sum(counts.values()),tasks=tasks,kernel=dict(current=hex(e.r32(0x20006138)),ready_bitmap=hex(e.r32(0x20006148)),ready_lists=bytes(u.mem_read(0x200060d4,100)).hex()),registers={n:hex(u.reg_read(v)) for n,v in [('r0',UC_ARM_REG_R0),('r1',UC_ARM_REG_R1),('r2',UC_ARM_REG_R2),('r4',UC_ARM_REG_R4),('sp',UC_ARM_REG_SP)]})
    result['switches']=switches
    result.update(operations=operations,physical_reads=reads,launch=launch,mount_return_status=u.reg_read(UC_ARM_REG_R0) if u.reg_read(UC_ARM_REG_PC)==0x0801ae06 else None,fs_type=e.r8(0x20000ab0),valid_BPB_model=valid,early_tick=early_tick,delayed_storage=delayed_storage,invalid_bpb=invalid_bpb,earliest_timer=earliest_timer,queued_query=queued,clock_release_iteration=delay_clock)
    result['timer_records_at_frontier']={hex(a):[dict(slot=i,raw=bytes(u.mem_read(e.r32(a+8)+i*28,28)).hex()) for i in range(e.r8(a))] for a in (0x20000354,0x20000360)}
    name=case+'.json' if case else 'modeled-valid-startup.json' if valid else 'modeled-startup.json' if extended else 'native-startup.json'
    (OUT/name).write_text(json.dumps(result,indent=2)+'\n')
    for a,n in [(0x0801b1a8,0x1c0),(0x0801ddd4,0xb0),(0x0801bd9c,0x140),(0x0801cabc,0x150),(0x0801d3c8,0x80),(0x0801c91c,0x1a0),(0x0801d16c,0xe0)]:
        (OUT/f'app-{a:08x}.asm').write_text(prior.source.listing('app',a,n))
    print(json.dumps({k:result[k] for k in ['frontier','mount_return_status','fs_type','private_unchanged','executed_instructions']},indent=2))
if __name__=='__main__':main()
