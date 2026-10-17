"""Narrow B1.3 SCSI/model tests. No endpoint/device/physical-NOR execution.

Seams: queue-drain returns idle; NOR wrapper read supplies synthetic ordinary BPB;
USB TX records bytes; USB low-level class reconfiguration recorded, not emulated.
"""
from pathlib import Path
import sys,json,struct,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase42-exact-rdiag-integration'))
from environment import Physical,PUBLISHED
sys.path.insert(0,str(ROOT/'tools'))
from ct_data_decode import decode
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
IMAGE=PUBLISHED[:];INIT,_=decode(IMAGE)
def ret(e,v=0):
    e.uc.reg_write(UC_ARM_REG_R0,v);e.uc.reg_write(UC_ARM_REG_PC,e.uc.reg_read(UC_ARM_REG_LR)|1)
def fresh():
    e=Physical();e.uc.mem_write(0x08010000,IMAGE);e.uc.mem_write(0x20000000,INIT);return e
def bpb():
    b=bytearray(4096);b[:3]=b'\xeb\x3c\x90';struct.pack_into('<H',b,11,4096);b[13]=1
    struct.pack_into('<H',b,14,1);b[16]=2;struct.pack_into('<H',b,17,512)
    struct.pack_into('<H',b,19,7980);b[21]=0xf8;struct.pack_into('<H',b,22,4)
    b[54:62]=b'FAT16   ';b[510:512]=b'\x55\xaa';return bytes(b)
def scsi(op,lba=0,count=1,mode=1):
    e=fresh();u=e.uc;trace=[];submitted=[];tx=[];barriers=[]
    e.call(0x08038c10,mode)
    cb=bytearray(16);cb[0]=op;cb[2:6]=lba.to_bytes(4,'big');cb[7:9]=count.to_bytes(2,'big')
    if op==0x12:cb[4]=36
    u.mem_write(0x20022000,bytes(cb));u.mem_write(0x20006898,b'\0'*0x20)
    e.w32(0x2000689c,4096);e.w32(0x200068a0,8192)
    e.w32(0x200067a4,4096*count if op==0x28 else 36 if op==0x12 else 8 if op==0x25 else 0);u.mem_write(0x200067a8,b'\x80')
    u.mem_write(0x200068d4,b'\0')
    def hook(u,pc,n,d):
        if pc in (0x08024164,0x080241b8,0x080241f0,0x08037494,0x080374d4,0x08037648,
                  0x0803cc16,0x0803cc34,0x0803cc54,0x0801859a,0x08018612):
            raise AssertionError(f'persistent/FS flush path {pc:x}')
        if pc==0x08023fd6:
            barriers.append('idle Storage queue drain (modeled)');ret(e)
        elif pc==0x08024130:
            addr=u.reg_read(UC_ARM_REG_R1);dst=u.reg_read(UC_ARM_REG_R2);length=u.reg_read(UC_ARM_REG_R3)
            submitted.append(dict(physical=hex(addr),bytes=length))
            u.mem_write(dst,(bpb()*max(1,count))[:length]);ret(e)
        elif pc==0x08024754:
            length=u.reg_read(UC_ARM_REG_R3);at=u.reg_read(UC_ARM_REG_R2)
            tx.append(bytes(u.mem_read(at,length)));ret(e)
        if pc in (0x08057e34,0x08057e44,0x08057e88):trace.append(hex(pc))
    u.hook_add(UC_HOOK_CODE,hook)
    result=e.call(0x0803b27c,0x20020000,0,0x20022000,maxins=300000)
    response=bytes(u.mem_read(0x40024000,36 if op==0x12 else 8))
    if op==0x28:
        assert result==0 and len(submitted)==1
        expected={1:0x94000,2:0xd4000,3:0}[mode]+lba*4096
        assert submitted==[dict(physical=hex(expected),bytes=4096)]
        assert tx==[bpb()] and len(barriers)==1
    else:assert result==0 and not submitted and not barriers
    return dict(opcode=hex(op),LUN=0,mode=mode,LBA=lba,blocks=count,result=result,
                callbacks=trace,NOR_reads=submitted,queue_barriers=barriers,
                response_prefix=response.hex(),TX_lengths=[len(x) for x in tx],
                persistent_write_or_FS_flush_calls=0,seams='idle queue barrier, wrapper NOR read, USB TX')
def modes(value):
    e=fresh();u=e.uc;calls=[]
    # Execute native composite rebuild, class registration and descriptor composition.
    # Only low-level USB-driver reset/config/start are modeled.
    def hook(u,pc,n,d):
        if pc in (0x08024804,0x08037ef0,0x08037f16,0x08037f26,0x08024630,0x080246a8):
            calls.append(hex(pc));ret(e)
        if pc in (0x0803cc16,0x0803cc34,0x0803cc54,0x08024164,0x080241b8):raise AssertionError('mode submitted persistence')
    u.hook_add(UC_HOOK_CODE,hook)
    # Actual stock vendor42 sub0 parser -> mode setter -> deferred callback.
    msg=IMAGE[0x149a8:0x149ad]+bytes([0x42,0,value,0xf7])
    u.mem_write(0x20022100,msg);e.w32(0x20022000,0x20022100);e.w32(0x20022004,len(msg))
    scheduled=[]
    def timer(u,pc,n,d):
        if pc==0x0801e538:scheduled.append(hex(e.r32(0x20006824)));ret(e)
    u.hook_add(UC_HOOK_CODE,timer)
    e.call(0x080248f0,0,0x20022000,0,maxins=300000)
    assert scheduled==['0x80248b5']
    e.call(0x080248b4,maxins=300000) # timer scheduling is a seam, callback is native
    result=dict(config_MIDI=1,config_MSD=value,internal_mode=e.r8(0x200037bc),
                window_record=hex(e.r32(0x200037c0)),class_count=e.r8(0x200000cc),
                registered_classes=[hex(e.r32(0x200000cc+8+i*4)) for i in range(e.r8(0x200000cc))],
                USB_driver_seams=calls,scheduled_callback=scheduled,persistent_write_calls=0)
    return result
def main():
    rows=[scsi(0),scsi(0x12),scsi(0x25)]+[scsi(0x28,lba=l,mode=m) for m,l in [(1,0),(1,0x40),(2,0),(3,0xd4)]]
    mode_rows=[modes(x) for x in (0,1,2,3)]
    e=fresh();desc=e.call(0x08058f86,0x20022000);raw=bytes(e.uc.mem_read(desc,40))
    result=dict(confidence='PROVEN',scope='Narrow exact-B1.3 native slices; modeled reads are not unit acquisition',
                image_sha256=hashlib.sha256(IMAGE).hexdigest(),SCSI=rows,modes=mode_rows,
                MSD_class_descriptor_address=hex(desc),MSD_class_descriptor_hex=raw.hex(),
                max_LUN_callback=e.call(0x08057fb0),write_protected=e.call(0x08057e48),
                hardware_access=False,MIDI_ports_opened=0)
    (OUT/'native-reads.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
