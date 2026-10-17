"""Bounded normal BPBs/MBR checked against native B1.3 mount; local bytes only."""
from pathlib import Path
import json,struct
from geometry_from_sector import decode
from native_reads import fresh,ret,bpb
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def native(sectors):
    e=fresh();u=e.uc;fs=0x20023000;path=0x20022000;reads=[]
    u.mem_write(fs,b'\0'*0x1040);u.mem_write(path,b'0:/\0');e.w32(path+0x40,path);e.w32(0x20005e5c,fs)
    def hook(u,pc,n,d):
        if pc in (0x0801a75c,0x0801a78a):ret(e)
        elif pc==0x0801a7c2:
            assert u.reg_read(UC_ARM_REG_R1)==2
            u.mem_write(u.reg_read(UC_ARM_REG_R2),struct.pack('<H',4096));ret(e)
        elif pc==0x0801a796:
            lba=u.reg_read(UC_ARM_REG_R2);reads.append(lba)
            u.mem_write(u.reg_read(UC_ARM_REG_R1),sectors[64+lba]);ret(e)
        elif pc==0x0801a7ac:raise AssertionError('mount writes')
    u.hook_add(UC_HOOK_CODE,hook)
    status=e.call(0x080197a0,path+0x40,path+0x100,0,maxins=200000)
    assert status==0
    return dict(status=status,FAT_type=e.r8(fs),n_fatent=e.r32(fs+0x20),FAT_size=e.r32(fs+0x24),
                volume=e.r32(fs+0x28),FAT_base=e.r32(fs+0x2c),root=e.r32(fs+0x30),data=e.r32(fs+0x34),reads=reads)
def main():
    cases=json.loads((ROOT/'builds/phase48-current-unit-geometry/geometry-review.json').read_text())['bounded_normal_mount_cases']
    inputs=[]
    for c in cases:
        b=bytearray(bpb());b[13]=c['sectors_per_cluster'];b[16]=c['FAT_count']
        struct.pack_into('<H',b,17,c['root_entries']);struct.pack_into('<H',b,22,c['FAT_sectors'])
        inputs.append(('superfloppy model',{64:bytes(b)}))
    m=bytearray(4096);m[510:512]=b'\x55\xaa';m[450]=6;struct.pack_into('<II',m,454,1,7979)
    b=bytearray(bpb());struct.pack_into('<H',b,19,7979)
    inputs.append(('primary MBR model',{64:bytes(m),65:bytes(b)}))
    positive=[]
    for name,sectors in inputs:
        parsed=decode(sectors);actual=native(sectors)
        assert parsed['last_valid_cluster']==actual['n_fatent']-1
        for pk,nk in [('FAT_size_sectors','FAT_size'),('volume_base','volume'),('FAT_base','FAT_base'),('root_location','root'),('data_start','data')]:
            assert parsed[pk]==actual[nk],(pk,parsed,actual)
        assert all(not t['intersects_normal_writable_mapping'] for t in parsed['targets'])
        positive.append(dict(name=name,parser=parsed,native=actual))
    negatives=[('missing internal sector',{}),('short sector',{64:bpb()[:-1]}),('wrong binding LBA',{0:bpb()}),
               ('missing MBR candidate',{64:bytes(m)})]
    for name,off,fmt,v in [('bad signature',510,'H',0),('bad bps',11,'H',512),('zero spc',13,'B',0),
       ('nonpower spc',13,'B',3),('zero reserved',14,'H',0),('bad FAT count',16,'B',3),
       ('root alignment',17,'H',513),('out of capacity',19,'H',7981),('empty FAT',22,'H',0),
       ('small FAT',22,'H',1),('no root',17,'H',0)]:
        b=bytearray(bpb());struct.pack_into('<'+fmt,b,off,v);negatives.append((name,{64:bytes(b)}))
    rejected=[]
    for name,s in negatives:
        try:decode(s)
        except ValueError as e:rejected.append(dict(name=name,reason=str(e)))
        else:raise AssertionError('accepted '+name)
    result=dict(confidence='PROVEN',scope='Native bounded normal synthetic BPB models, not actual-unit sectors',
                positive=positive,rejected=rejected,hardware_access=False)
    (OUT/'geometry-tests.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(native_matches=len(positive),rejections=len(rejected))))
if __name__=='__main__':main()
