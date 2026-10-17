"""Native B1.3 sequential READ10 with explicit peripheral/USB model boundaries.
No device I/O. Every synthetic read uses the same emulated physical buffer.
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
def sha(b):return hashlib.sha256(b).hexdigest()
TARGET=bpb()
FAT=bytes.fromhex('f8ffffffffffffff')+bytes(4088)
root=bytearray(4096);root[:11]=b'TRACKS     ';root[11]=0x10;root[26:28]=(2).to_bytes(2,'little')
ROOT_SECTOR=bytes(root)
SECTORS={64:TARGET,65:FAT,73:ROOT_SECTOR}
class Model:
    def __init__(self):
        self.e=e=fresh();self.u=u=e.uc;self.wrapper=e.r32(0x20006968);self.backend=e.r32(self.wrapper+4)
        e.w32(self.backend,0x0805b1ac);e.w32(self.backend+0xc,0x2000000)
        u.mem_write(self.backend+8,b'\1\1');u.mem_write(self.wrapper+0xc,b'\0\1');e.w32(self.wrapper+0x10,0)
        e.call(0x08038c10,1);u.mem_write(0x40024000,b'\xa5'*4096)
        self.pending=[];self.worker=False;self.yielded=False;self.hung=False;self.history=[]
        u.hook_add(UC_HOOK_CODE,self.hook)
    def hook(self,u,pc,n,d):
        e=self.e
        if pc in (0x08024164,0x080241b8,0x080241f0,0x08037494,0x080374d4,0x08037648,
                  0x0803cc16,0x0803cc34,0x0803cc54,0x0801859a,0x08018612):raise AssertionError(f'write/flush {pc:x}')
        if pc==0x08036708:
            raw=bytes(u.mem_read(e.r32(u.reg_read(UC_ARM_REG_R1)+4),24));self.pending.append(raw)
            assert int.from_bytes(raw[:2],'little')==1;ret(e,1)
        elif pc==0x0803675c:ret(e,len(self.pending))
        elif pc==0x08036732:
            u.mem_write(e.r32(u.reg_read(UC_ARM_REG_R1)+4),self.pending.pop(0));ret(e,1)
        elif pc==0x0801bde8:ret(e)
        elif pc==0x0801be60:
            assert not self.worker;self.yielded=True;u.emu_stop()
        elif pc==0x08037430:
            dst=u.reg_read(UC_ARM_REG_R2);length=u.reg_read(UC_ARM_REG_R3);addr=u.reg_read(UC_ARM_REG_R1)
            assert dst==0x40024000 and length==4096 and addr==0x94000+self.lba*4096
            assert bytes(u.mem_read(dst,length))==bytes(4096),'native response clear missing'
            if self.outcome in ('timeout','partial-timeout'):
                if self.outcome=='partial-timeout':u.mem_write(dst,self.source[:self.refresh])
                self.hung=True;u.emu_stop();return
            data=self.source[:self.refresh]
            if data:u.mem_write(dst,data)
            # Outcome/completion is modeled here, never asserted physical behavior.
            ret(e)
        elif pc==0x080240c4:self.status.append(u.reg_read(UC_ARM_REG_R0))
        elif pc==0x08024754:
            self.tx.append(bytes(u.mem_read(u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3))));ret(e)
        elif pc==0x08024770:ret(e)
    def read(self,lba,refresh=4096,outcome='completion',source=None):
        assert not self.hung,'no second request after modeled timeout'
        self.lba=lba;self.refresh=refresh;self.outcome=outcome;self.source=SECTORS[lba] if source is None else source
        self.tx=[];self.status=[];e=self.e;u=self.u;before=bytes(u.mem_read(0x40024000,4096))
        cb=bytearray(16);cb[0]=0x28;cb[2:6]=lba.to_bytes(4,'big');cb[7:9]=(1).to_bytes(2,'big')
        u.mem_write(0x20022000,bytes(cb));u.mem_write(0x20006898,bytes(0x20))
        e.w32(0x2000689c,4096);e.w32(0x200068a0,8192);e.w32(0x200067a4,4096)
        e.w32(0x200068cc,4096);e.w32(0x200068c8,len(self.history)+1)
        u.mem_write(0x200067a8,b'\x80');u.mem_write(0x200068d4,b'\0')
        u.reg_write(UC_ARM_REG_SP,0x20008330);u.reg_write(UC_ARM_REG_LR,0x0807ff01)
        for reg,v in ((UC_ARM_REG_R0,0x20020000),(UC_ARM_REG_R1,0),(UC_ARM_REG_R2,0x20022000)):u.reg_write(reg,v)
        pc=0x0803b27c
        for _ in range(20):
            self.yielded=False;u.emu_start(pc|1,0xffffffff,count=300000)
            if u.reg_read(UC_ARM_REG_PC)==0x0807ff00:break
            assert self.yielded
            ctx=u.context_save();self.worker=True
            try:
                u.reg_write(UC_ARM_REG_SP,0x2004e000);u.reg_write(UC_ARM_REG_LR,0x0807ff01);u.reg_write(UC_ARM_REG_R0,self.wrapper)
                u.emu_start(0x08024015,0xffffffff,count=100000)
                if self.hung:
                    assert not self.tx
                    record=dict(LBA=lba,outcome='timeout',USB_bytes=0,returned_512_hex=None,
                                buffer_512_hex=bytes(u.mem_read(0x40024000,512)).hex(),sync=e.r32(self.wrapper+0x10))
                    self.history.append(record);return None
                assert u.reg_read(UC_ARM_REG_PC)==0x0807ff00
            finally:
                if not self.hung:u.context_restore(ctx)
                self.worker=False
            ret(e);pc=u.reg_read(UC_ARM_REG_PC)
        else:raise AssertionError('model did not finish')
        assert len(self.tx)==1 and len(self.tx[0])==4096 and self.status==[0],(lba,len(self.tx),self.status,hex(u.reg_read(UC_ARM_REG_PC)))
        assert e.r8(self.backend+8)==1,'native release must restore constructor-bounded semaphore'
        data=self.tx[0];e.call(0x08026db0,0x20020000,maxins=100000)
        assert len(self.tx)==2 and self.tx[1][8:13]==bytes(5)
        self.history.append(dict(LBA=lba,outcome=outcome,refreshed_bytes=refresh,USB_bytes=4096,buffer=hex(0x40024000),
            previous_buffer_sha256=sha(before),returned_512_hex=data[:512].hex(),returned_4096_sha256=sha(data),CSW_status=0))
        return data
def structural(t):
    if t is None:return False
    try:decode({64:t});return True
    except ValueError:return False
def triple(t,c,t2):return t is not None and c is not None and t2 is not None and t==t2 and t!=c
def enhanced(t,c,t2):return triple(t,c,t2) and structural(t) and c[:4]==bytes.fromhex('f8ffffff')
