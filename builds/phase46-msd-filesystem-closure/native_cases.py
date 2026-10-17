"""Phase46 scoped native tests. Synthetic inputs are explicitly countermodels.
No cold boot, physical disk or complete USB execution is asserted.
"""
from pathlib import Path
import sys, json, struct, hashlib
sys.dont_write_bytecode = True
import inspect_storage as source
ROOT, OUT = source.ROOT, source.OUT
sys.path.insert(0, str(ROOT/'builds/phase42-exact-rdiag-integration'))
from environment import Physical, STOCK, PUBLISHED
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *

def fresh():
    e = Physical(); e.uc.mem_write(0x08010000, source.app)
    e.uc.mem_write(0x20000000, source.init)
    return e

def ret(e, value=0):
    e.uc.reg_write(UC_ARM_REG_R0, value)
    e.uc.reg_write(UC_ARM_REG_PC, e.uc.reg_read(UC_ARM_REG_LR)|1)

def provenance():
    rows=[]
    for name, image in [('stock', STOCK), ('B1.3', PUBLISHED[:]), ('corrected-diagnostic', source.app)]:
        e=fresh();e.uc.mem_write(0x08010000,image)
        e.uc.mem_write(0x20000000,b'\xa5'*0x3d04)
        expected,desc=source.decode(image)
        e.call(0x080596c4,0x0805b7c8,maxins=500000)
        actual=bytes(e.uc.mem_read(0x20000000,len(expected)))
        assert actual==expected
        rows.append(dict(image=name,image_sha256=hashlib.sha256(image).hexdigest(),descriptor=desc,
            table=actual[0x3788:0x37b0].hex(),table_equal=actual[0x3788:0x37b0]==source.init[0x3788:0x37b0]))
    e=fresh();e.uc.mem_write(0x20000000,b'\xa5'*0x50000)
    e.call(0x0800927c,0x08009694,maxins=500000)
    bootinit=bytes(e.uc.mem_read(0x20000004,11084))
    descriptor_pointer=e.call(0x0800865e,0x200000fc,0x20030000)
    descriptor_length=int.from_bytes(e.uc.mem_read(0x20030000,2),'little')
    usbdesc=bytes(e.uc.mem_read(descriptor_pointer,descriptor_length));interfaces=[];pos=0
    while pos<len(usbdesc):
        length,kind=usbdesc[pos:pos+2];assert length>=2
        if kind==4:interfaces.append(dict(number=usbdesc[pos+2],alternate=usbdesc[pos+3],
            usb_class=usbdesc[pos+5],subclass=usbdesc[pos+6],protocol=usbdesc[pos+7]))
        pos+=length
    assert pos==len(usbdesc) and all(i['usb_class']!=8 for i in interfaces)
    # Persist only initialized pointers and hashes, never a firmware or invented NOR payload.
    bootptr=[]
    for off in range(0,len(bootinit)-3,4):
        v=struct.unpack_from('<I',bootinit,off)[0]
        if 0x08000000<=v<0x08010000:
            bootptr.append(dict(ram=hex(0x20000004+off),pointer=hex(v)))
    return dict(applications=rows,boot=dict(native_decompressor='0x0800927c',descriptor='0x08009694',
        destination='0x20000004',length=len(bootinit),sha256=hashlib.sha256(bootinit).hexdigest(),code_pointers=bootptr,
        registered_class_record='0x200000fc',usb_descriptor_pointer=hex(descriptor_pointer),
        usb_descriptor=usbdesc.hex(),interfaces=interfaces))

def scsi(lba, count, lun=0):
    e=fresh();u=e.uc;trace=[];writes=[]
    cb=bytearray(16);cb[0]=0x2a;cb[2:6]=lba.to_bytes(4,'big');cb[7:9]=count.to_bytes(2,'big')
    u.mem_write(0x20022000,bytes(cb));u.mem_write(0x20006898,b'\0'*0x20)
    e.w32(0x2000689c,4096);e.w32(0x200068a0,8192)
    u.mem_write(0x200068d4,b'\0');u.mem_write(0x200067a8,b'\0')
    def hook(u,pc,n,d):
        if pc in (0x08057e44,0x08057e48):trace.append(hex(pc))
        if pc in (0x08057ef4,0x08024164,0x080241b8):
            writes.append(hex(pc));raise AssertionError('Write path admitted')
    u.hook_add(UC_HOOK_CODE,hook)
    result=e.call(0x0803b27c,0x20020000,lun,0x20022000)
    assert result==0xffffffff and trace==['0x8057e44','0x8057e48'] and not writes
    return dict(lba=hex(lba),count=count,lun=lun,result=hex(result),calls=trace,
        sense_key=e.r8(0x200067dc),asc_ascq=hex(e.r32(0x200067e0)),write_calls=writes)

def mode_setting(bit):
    e=fresh();u=e.uc;calls=[]
    # Real observer and real settings accessor; one pointer-returning setting record.
    obj=0x20022000;settings=0x20022100;record=0x20022200
    e.w32(obj+4,settings);e.w32(settings+4,0);e.w32(settings+0xc,record)
    e.w32(record+8,bit<<17)
    def hook(u,pc,n,d):
        if pc in (0x08036374,0x08036442,0x08036460):
            calls.append(hex(pc));ret(e)
    u.hook_add(UC_HOOK_CODE,hook)
    e.call(0x08029e30,obj)
    assert e.r8(0x200037bc)==bit
    return dict(setting_bit17=bit,mode=e.r8(0x200037bc),record=hex(e.r32(0x200037c0)),
        seam='USB class lock/register/rebuild only',usb_calls=calls)

def fat_mount():
    e=fresh();u=e.uc
    # Deliberately oversized but internally consistent FAT32 BPB; not unit data.
    sector=bytearray(4096);sector[0:3]=b'\xeb\x58\x90'
    struct.pack_into('<H',sector,11,4096);sector[13]=1
    struct.pack_into('<H',sector,14,1);sector[16]=1
    struct.pack_into('<I',sector,32,0x110000);struct.pack_into('<I',sector,36,0x1000)
    struct.pack_into('<I',sector,44,2);struct.pack_into('<H',sector,48,1)
    sector[82:87]=b'FAT32';sector[510:512]=b'\x55\xaa'
    fs=0x20023000;path=0x20022000;out=path+0x100;reads=[];writes=[]
    u.mem_write(fs,b'\0'*0x1040);u.mem_write(path,b'0:/\0');e.w32(path+0x40,path)
    e.w32(0x20005e5c,fs)
    def hook(u,pc,n,d):
        if pc==0x0801a75c or pc==0x0801a78a:ret(e,0)
        elif pc==0x0801a7c2:
            assert u.reg_read(UC_ARM_REG_R1)==2
            u.mem_write(u.reg_read(UC_ARM_REG_R2),struct.pack('<H',4096));ret(e)
        elif pc==0x0801a796:
            lba=u.reg_read(UC_ARM_REG_R2);reads.append(hex(lba))
            u.mem_write(u.reg_read(UC_ARM_REG_R1),bytes(sector) if lba==0 else b'\0'*4096);ret(e)
        elif pc==0x0801a7ac:
            writes.append(hex(u.reg_read(UC_ARM_REG_R2)));ret(e)
    u.hook_add(UC_HOOK_CODE,hook)
    result=e.call(0x080197a0,path+0x40,out,0,maxins=200000)
    assert result==0 and e.r8(fs)==3 and not writes
    data_base=e.r32(fs+0x34);n_fatent=e.r32(fs+0x20)
    mappings=[]
    for target,lba in [(0x81000,0xfffad),(0x82000,0xfffae)]:
        cluster=lba-data_base+2
        derived=e.call(0x08018698,fs,cluster)
        assert derived==lba and (0xd4000+4096*derived)&0xffffffff==target
        mappings.append(dict(cluster=hex(cluster),accepted_cluster_lt_n_fatent=cluster<n_fatent,
            native_sector=hex(derived),wrapped_physical_address=hex(target)))
    file_writes=[]
    for mapping in mappings:
        fil=0x20026000;buf=0x20028000;written=0x20027000
        u.mem_write(fil,b'\0'*0x1040);e.w32(fil,fs)
        u.mem_write(fil+4,bytes(u.mem_read(fs+6,2)))
        e.w32(fil+8,int(mapping['cluster'],16));u.mem_write(fil+0x10,b'\x02')
        u.mem_write(buf,b'\x5a'*4096);before=len(writes)
        status=e.call(0x08019e50,fil,buf,4096,written,maxins=200000)
        assert status==0 and e.r32(written)==4096
        assert writes[before:]==[mapping['native_sector']]
        file_writes.append(dict(status=status,bytes_written=e.r32(written),disk_lbas=writes[before:],
            physical_address=mapping['wrapped_physical_address']))
    return dict(input='Synthetic oversized FAT32 volume, not authenticated unit NOR',
        mount_result=result,type=e.r8(fs),n_fatent=hex(n_fatent),data_base=hex(data_base),
        total_sectors='0x110000',physical_partition_sectors='0x1f2c',read_lbas=reads,
        mount_writes=[],mappings=mappings,native_file_writes=file_writes,
        limitation='Native mount, cluster mapper and f_write with constructed FIL records; disk I/O modeled. Not unit data, full directory lookup, auto-save or cold-boot exploit')

def settings_load(size):
    e=fresh();u=e.uc;obj=0x20022000;events=[]
    u.mem_write(obj,b'\0'*0xa0)
    def hook(u,pc,n,d):
        if pc==0x0803c9ca:
            events.append(dict(operation='SIZE',element=bytes(u.mem_read(u.reg_read(UC_ARM_REG_R1),12)).hex()));ret(e,size)
        elif pc==0x0803c8d4:
            events.append(dict(operation='READ',length=e.r32(u.reg_read(UC_ARM_REG_SP))));ret(e)
        elif pc==0x0802d108:
            # Deliberately choose invalid content for the 128-byte-size case.
            ret(e,0)
        elif pc==0x0802d142:
            events.append(dict(operation='RAM_DEFAULTS',seam=True));ret(e)
        elif pc==0x0803c97a:
            events.append(dict(operation='DELETE',element=bytes(u.mem_read(u.reg_read(UC_ARM_REG_R1),12)).hex()));ret(e)
        elif pc==0x08035756:ret(e,0)
    u.hook_add(UC_HOOK_CODE,hook)
    e.call(0x0802d060,obj,maxins=100000)
    assert any(x['operation']=='DELETE' for x in events)==(size!=0)
    return dict(size=size,content_validation='modeled invalid if size128; actual size branch executed',events=events,
        limit='Native startup producer branch; content service and defaults modeled, no actual filesystem deletion asserted')

def main():
    result=dict(confidence='PROVEN',scope='Native functions with explicit modeled seams; no hardware, cold boot or whole USB transport claim',
        provenance=provenance(),settings=[mode_setting(x) for x in (0,1)],
        scsi=[scsi(l,c,lun) for lun in (0,1) for l,c in [(0,1),(0x81,1),(0x82,1),(8191,1),(8192,1),(0xffffffff,1),(0xfffffff0,0x40),(0,0),(0,0xffff)]],
        fat=fat_mount(),settings_load=[settings_load(n) for n in (0,1,128)])
    (OUT/'native-cases.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='provenance' and k!='scsi'},indent=2))
    print('18 SCSI WRITE10 cases rejected by actual initialized write-protection callback')
if __name__=='__main__':main()
