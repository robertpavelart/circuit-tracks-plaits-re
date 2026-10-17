"""OFFLINE ONLY. Decode 46 packed bytes: A98:8 || AB0:14 || AD0:24.

No acquisition, device, MIDI, network or firmware operations. Clean mounted
internal-volume records only. Syntactic validity does not authenticate a unit.
Exact BPB total sectors is not stored in these spans; report its possible range.
"""
import argparse
import json
import struct
from pathlib import Path

def decode(record):
    if len(record)!=46:
        raise ValueError('expected exactly 46 bytes: A98:8 || AB0:14 || AD0:24')
    base,stride=struct.unpack_from('<II',record)
    typ,drive,nfats,dirty,fsi,pad,mount,roots,spc,bps=struct.unpack_from('<6B4H',record,8)
    entries,fatsz,vol,fat,root,data=struct.unpack_from('<6I',record,22)
    def require(ok,msg):
        if not ok: raise ValueError(msg)
    require(typ in (1,2,3),'invalid/unmounted FAT type')
    require(drive==0,'not the internal drive')
    require(base==0xd4000,'unexpected internal partition physical base')
    require(stride==4096 and bps==stride,'invalid internal sector size/stride')
    require(spc in (1,2,4,8,16,32,64,128),'impossible cluster geometry')
    require(nfats in (1,2),'invalid FAT count')
    require(dirty==0 and fsi in (0,0x80),'not a clean supported status snapshot')
    require(mount!=0,'ambiguous zero mount ID: obtain corroborating mounted status')
    require(fatsz>0 and entries>2,'empty FAT/cluster range')
    n=entries-2
    expected=1 if n<0xff6 else 2 if n<0xfff6 else 3 if n<0xffffff6 else 0
    require(typ==expected,'FAT class inconsistent with cluster count')
    reserved=fat-vol
    require(reserved>0,'inconsistent reserved/FAT start')
    fatend=fat+nfats*fatsz
    rootsectors=roots*32//bps
    if typ in (1,2):
        require(roots>0 and roots*32%bps==0,'invalid fixed root size')
        require(root==fatend and data==root+rootsectors,'inconsistent FAT/root/data ranges')
        fatbytes=(entries*3+1)//2 if typ==1 else entries*2
    else:
        require(roots==0 and 2<=root<entries,'invalid FAT32 root cluster')
        require(data==fatend,'inconsistent FAT32 data start')
        fatbytes=entries*4
    require(fatsz*bps>=fatbytes,'FAT too small for cluster count')
    dataend=data+n*spc
    capacity=(0x2000000-base)//stride
    require(0<=vol<fat<fatend<=data<dataend<=capacity,'ranges outside bounded internal partition')
    # BPB floor division loses at most spc-1 unused trailing sectors.
    total_min=dataend-vol
    total_max=min(dataend+spc-1,capacity)-vol
    domains=[('FAT copies',base+fat*stride,base+fatend*stride),
             ('data clusters',base+data*stride,base+dataend*stride)]
    if typ in (1,2):domains.append(('fixed root',base+root*stride,base+data*stride))
    elif reserved>=2:domains.append(('possible FAT32 FSInfo',base+(vol+1)*stride,base+(vol+2)*stride))
    def target(a,z):
        return dict(start=hex(a),end_inclusive=hex(z),
                    intersects_normal_writable_mapping=any(a<end and z>=start for _,start,end in domains),
                    intersected_domains=[name for name,start,end in domains if a<end and z>=start])
    return dict(confidence='PROVEN',scope='Validated supplied bytes only; current-unit provenance and coherent acquisition are external prerequisites',
                FAT_type={1:'FAT12',2:'FAT16',3:'FAT32'}[typ],bytes_per_sector=bps,sectors_per_cluster=spc,
                physical_base=hex(base),volume_base=vol,reserved_sectors=reserved,FAT_count=nfats,FAT_size_sectors=fatsz,
                root_entries=roots,data_start=data,first_valid_cluster=2,last_valid_cluster=entries-1,
                mount_id=mount,window_dirty=dirty,FSInfo_flags=fsi,
                total_sectors=total_min if total_min==total_max else None,
                total_sectors_possible_range=[total_min,total_max],
                total_sectors_source='Derived from mounted bounds; BPB total itself is absent',
                writable_domains=[dict(name=name,start=hex(a),end_exclusive=hex(z)) for name,a,z in domains],
                targets=[target(0x81000,0x81016),target(0x82000,0x821ff)])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('record',type=Path)
    args=p.parse_args()
    try: result=decode(args.record.read_bytes())
    except (ValueError,OSError) as e:p.exit(2,f'REJECTED: {e}\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
