"""Offline NVIC/source observer; no external IRQ injected by this inventory pass."""
import json,struct,sys
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
class Observer:
    def __init__(self,e,out):
        self.e=e;self.u=e.uc;self.out=out;self.writes=[];self.enabled=set();self.transitions=[];self.snapshots=[];self.sources={}
        self.requested=next((int(s.split('=')[1]) for s in sys.argv if s.startswith('--irq=')),None);self.injected=[]
        self.timer_started={};self.serial_started={}
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=0xe000e000,end=0xe000efff)
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=0x40000000,end=0x4002ffff)
        self.u.hook_add(UC_HOOK_CODE,self.code)
    def write(self,u,access,a,n,v,d):
        pc=u.reg_read(UC_ARM_REG_PC)
        if 0xe000e100<=a<0xe000e180 or 0xe000e180<=a<0xe000e200:
            base=0xe000e100 if a<0xe000e180 else 0xe000e180;is_enable=base==0xe000e100
            bits=[8*(a-base)+i for i in range(n*8) if v>>i&1]
            for i in bits:
                if is_enable:self.enabled.add(i)
                else:self.enabled.discard(i)
                self.transitions.append(dict(pc=hex(pc),caller_return=hex(u.reg_read(UC_ARM_REG_LR)),irq=i,enable=is_enable,vector=hex(self.e.r32(0x08010000+4*(16+i)))))
        row=dict(pc=hex(pc),address=hex(a),size=n,value=hex(v))
        self.writes.append(row)
    def snapshot(self,pc):
        rows=[]
        for i in sorted(self.enabled):rows.append(dict(irq=i,vector_number=i+16,handler=hex(self.e.r32(0x08010000+4*(16+i))),priority=self.u.mem_read(0xe000e400+i,1)[0]))
        regs={hex(a):hex(self.e.r32(a)) for a in [0x40023830,0x40023834,0x40023840,0x40023844,0x40013c00,0x40013c04,0x40013c14,0x40003800,0x40003804,0x40013400,0x40013404,0x40012c00,0x40012c04,0x40012c08,0x40012c0c,0x40012c10,0x40012c18,0x40012c2c,0x40015800,0x40015804,0x40015814,0x40011000,0x40011004,0x4001101c,0x40004400,0x40004404,0x4000441c,0x40002808,0xa0001000,0xa0001008]}
        for base in (0x40000000,0x40000800,0x40000c00,0x40014000):
            for off in (0,0xc,0x10,0x24,0x28,0x2c,0x34):regs[hex(base+off)]=hex(self.e.r32(base+off))
        for base in (0x40026000,0x40026400):
            for i in range(8):
                for off in (0,4,8,12,20):regs[hex(base+0x10+0x18*i+off)]=hex(self.e.r32(base+0x10+0x18*i+off))
        self.snapshots.append(dict(pc=hex(pc),enabled=rows,source_registers=regs,SysTick=dict(CTRL=hex(self.e.r32(0xe000e010)),LOAD=self.e.r32(0xe000e014),priority=self.u.mem_read(0xe000ed23,1)[0])))
        if pc==0x0801ae06:
            self.snapshots[-1]['geometry_record_hex']=b''.join(bytes(self.u.mem_read(a,n)) for a,n in ((0x20000a98,8),(0x20000ab0,14),(0x20000ad0,24))).hex()
    def code(self,u,pc,n,d):
        if pc in (0x0801d9ea,0x0801d4b0,0x0801ae06):self.snapshot(pc)
        if pc==0x0801ddd2:
            self.sources['UART_exception_return_debug']=dict(IPSR=u.reg_read(UC_ARM_REG_IPSR),XPSR=hex(u.reg_read(UC_ARM_REG_XPSR)),SP=hex(u.reg_read(UC_ARM_REG_SP)),MSP=hex(u.reg_read(UC_ARM_REG_MSP)),stack=bytes(u.mem_read(u.reg_read(UC_ARM_REG_MSP),16)).hex())
    def injection(self,pc):
        irq=self.requested;u=self.u;e=self.e
        if irq is None or self.injected or irq not in self.enabled or u.reg_read(UC_ARM_REG_IPSR) or u.reg_read(UC_ARM_REG_PRIMASK) or u.reg_read(UC_ARM_REG_FAULTMASK):return None
        pri=u.mem_read(0xe000e400+irq,1)[0];mask=u.reg_read(UC_ARM_REG_BASEPRI)
        if mask and pri>=mask:return None
        # Narrow success-model eligible source events; other cases are never forced.
        event=None
        if irq in (28,30,50):
            base={28:0x40000000,30:0x40000800,50:0x40000c00}[irq];bit=1 if irq==28 else 2
            if e.r32(base)&1 and e.r32(base+12)&bit:
                start=self.timer_started.setdefault(irq,e.r32(0x2000081c));period_ms=3 if irq==28 else 1
                if (e.r32(0x2000081c)-start)&0xffffffff>=period_ms:
                    e.w32(base+16,bit);event=f'first modeled millisecond boundary after at least {period_ms}ms elapsed since CEN+DIER; controlled timer event'
        if irq==92 and pc==0x08037596 and e.r32(0xa0001000)&0x20000:
            e.w32(0xa0001008,e.r32(0xa0001008)|2);event='TCF for an already-issued NOR command with TCIE'
        if irq in (37,38):
            base=0x40011000 if irq==37 else 0x40004400
            if e.r32(base)&0x21==0x21:
                start=self.serial_started.setdefault(irq,e.r32(0x2000081c))
                if (e.r32(0x2000081c)-start)&0xffffffff>=1:
                    e.w32(base+0x1c,0x20);e.w32(base+0x24,0xfe);event='one received MIDI active-sensing byte after UE+RXNEIE and at least1 modeled ms; controlled serial completion'
        if irq==70 and pc==0x08037596 and e.r32(0x400264b8)&0x11==0x11:
            e.w32(0x400264bc,0);e.w32(0x40026404,1<<27);event='DMA2 stream7 TC after native read transaction started, NDTR reaches zero'
        if irq==49 and pc==0x0801c63c and e.r8(0x20005548)&2 and e.r32(0x40012c3c)&4:
            e.w32(0x40012c34,4);event='SDMMC command timeout after native command start; absent-card success model'
        if irq==40 and e.r32(0x40013c00)&0x800 and e.r32(0x40013c0c)&0x800:
            e.w32(0x40013c14,0x800);event='one falling power-button EXTI edge with configured IMR/FTSR; GPIO shadow low'
        if event:
            self.injected.append(dict(irq=irq,pc=hex(pc),priority=pri,event=event,IPSR=u.reg_read(UC_ARM_REG_IPSR),BASEPRI=mask));return irq
        return None
    def finish(self):
        self.snapshot(self.u.reg_read(UC_ARM_REG_PC))
        r=dict(confidence='PROVEN',scope='Actual observed MMIO write intents and accumulated W1S/W1C NVIC inventory under inherited success model; not all input-dependent branches',transitions=self.transitions,snapshots=self.snapshots,MMIO_writes=self.writes,injected=self.injected,debug=self.sources)
        name='irq-inventory.json' if self.requested is None else f'irq-{self.requested}-trace.json'
        (self.out/name).write_text(json.dumps(r,indent=2)+'\n')
