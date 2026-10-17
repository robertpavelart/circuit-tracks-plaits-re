"""Offline bounded internal-volume BPB decoder. No hardware or block-device I/O.

Input: --sector USB_LBA=LOCAL_FILE (repeat for MBR candidates if needed).
Binding contract: already established internal MSD mode1, USB sector4096,
NOR base94000, internal disk0 baseD4000 => internal LBA0 at USB LBA64.
Caller must supply provenance; FAT-looking bytes alone do not prove this binding.
"""
from pathlib import Path
import argparse,sys,struct,json,hashlib
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'phase49-existing-geometry-reader'))
from geometry_parser import decode as validate_geometry
ROOT_LBA=64
CAPACITY=7980
def require(ok,msg):
    if not ok:raise ValueError(msg)
def recognized(b):
    return b[510:512]==b'\x55\xaa' and b[0] in (0xe8,0xe9,0xeb) and (b[54:57]==b'FAT' or b[82:87]==b'FAT32')
def decode(sectors):
    for lba,b in sectors.items():
        require(isinstance(lba,int) and 64<=lba<64+CAPACITY,'USB LBA outside fixed mode1 internal-volume evidence domain')
        require(len(b)==4096,'each raw sector must be exactly 4096 bytes')
    require(ROOT_LBA in sectors,'need internal disk0 LBA0: USB LBA64')
    first=sectors[ROOT_LBA];partition=None;vol=0;examined=[ROOT_LBA]
    require(first[510:512]==b'\x55\xaa','missing sector0 boot/MBR signature')
    if recognized(first):vbr=first
    else:
        vbr=None
        for i in range(4):
            off=446+16*i;start,count=struct.unpack_from('<II',first,off+8)
            if not start:continue
            require(0<start<CAPACITY and 0<count<=CAPACITY-start,'partition outside bounded internal volume')
            usb=ROOT_LBA+start
            require(usb in sectors,f'need candidate partition sector at USB LBA{usb} before selecting a later entry')
            examined.append(usb)
            if recognized(sectors[usb]):
                vol=start;partition=dict(index=i,start=start,sectors=count);vbr=sectors[usb];break
        require(vbr is not None,'no stock-recognized FAT VBR in supplied primary candidates')
    u16=lambda o:struct.unpack_from('<H',vbr,o)[0]
    u32=lambda o:struct.unpack_from('<I',vbr,o)[0]
    bps=u16(11);spc=vbr[13];reserved=u16(14);nfats=vbr[16];roots=u16(17)
    total=u16(19) or u32(32);fatsz=u16(22) or u32(36)
    require(bps==4096,'BPB sector size must match internal 4096-byte backend')
    require(spc in (1,2,4,8,16,32,64,128),'impossible cluster geometry')
    require(reserved>0 and nfats in (1,2) and fatsz>0,'invalid reserved/FAT geometry')
    require(roots*32%bps==0,'unaligned fixed root')
    overhead=reserved+nfats*fatsz+roots*32//bps
    require(overhead<total and vol+total<=CAPACITY,'volume outside bounded internal backing store')
    if partition:require(total<=partition['sectors'],'BPB exceeds primary partition extent')
    n=(total-overhead)//spc
    typ=1 if n<0xff6 else 2 if n<0xfff6 else 3 if n<0xffffff6 else 0
    fat=vol+reserved;root=fat+nfats*fatsz if typ!=3 else u32(44);data=vol+overhead
    if typ==3:require(u16(42)==0 and roots==0,'unsupported FAT32 version/root geometry')
    # Reuse Phase49's checked geometry invariants. Clean/status fields here are
    # validator adapter constants, NOT captured RAM or evidence of a live mount.
    record=struct.pack('<II6B4H6I',0xd4000,4096,typ,0,nfats,0,0x80,0,1,roots,spc,bps,
                       n+2,fatsz,vol,fat,root,data)
    result=validate_geometry(record)
    for k in ('mount_id','window_dirty','FSInfo_flags'):result.pop(k)
    result.update(scope='Decoded supplied disk sectors; physical binding/provenance must be independently established; live mount/status not acquired',
        total_sectors=total,total_sectors_possible_range=[total,total],total_sectors_source='Exact BPB TotSec16 or TotSec32',
        FAT_base=fat,root_location=root,partition=partition,
        USB_binding=dict(internal_mode=1,MSD_base='0x94000',internal_disk_base='0xd4000',USB_LBA_of_internal_zero=64),
        sectors_examined=examined,unrelated_sectors_supplied=sorted(set(sectors)-set(examined)),
        live_mount_status='UNKNOWN',sector_hashes={str(k):hashlib.sha256(sectors[k]).hexdigest() for k in examined})
    return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sector',action='append',required=True,metavar='USB_LBA=FILE')
    args=p.parse_args();sectors={}
    try:
        for arg in args.sector:
            left,right=arg.split('=',1);lba=int(left,0);require(lba not in sectors,'duplicate sector argument')
            sectors[lba]=Path(right).read_bytes()
        print(json.dumps(decode(sectors),indent=2))
    except (ValueError,OSError,struct.error) as e:p.exit(2,f'REJECTED: {e}\n')
if __name__=='__main__':main()
