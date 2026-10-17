"""Authenticated version comparison and bounded normal mount alternatives only.
Existing images are read, never built or emitted. Peripheral block reads modeled.
"""
from pathlib import Path
import sys,json,hashlib,struct
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import native_cases as old
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
def sha(b):return hashlib.sha256(b).hexdigest()
def versions():
    clean=ROOT/'builds/phase43-hardware-test-candidate/clean-sc35d8.bin'
    images={'official4486':old.STOCK,'SC35D8':clean.read_bytes(),'B1.3':old.PUBLISHED[:],
        'corrected-diagnostic':old.source.app}
    manifest=json.loads((old.source.REF/'firmware/sc35d8/manifest.json').read_text())
    assert sha(images['SC35D8'])==manifest['image_sha256']
    ranges=[('FatFs-module',0x0801855c,0x0801af48),('disk-volume-binding',0x0801f0a8,0x0801f1a8),
        ('NOR-geometry-query',0x080373ec,0x0803742e),('mount',0x080197a0,0x08019a50)]
    rows=[]
    for name,b in images.items():
        init,desc=old.source.decode(b)
        rows.append(dict(image=name,sha256=sha(b),bytes=len(b),ranges=[dict(name=label,start=hex(a),end=hex(z),
            sha256=sha(b[a-0x8010000:z-0x8010000]),equal_stock=b[a-0x8010000:z-0x8010000]==old.STOCK[a-0x8010000:z-0x8010000]) for label,a,z in ranges],
            initialized_geometry=init[0xa98:0xaa0].hex(),initialized_sha256=sha(init),
            sysex_dispatcher_bytes=b[0xeb30:0xeb38].hex()))
    assert all(all(r['equal_stock'] for r in x['ranges']) for x in rows)
    for a,z in [(0x080373ec,0x0803742e),(0x08019734,0x08019a50),(0x0801addc,0x0801ae44)]:
        (OUT/f'app-{a:08x}.asm').write_text(old.source.listing('app',a,z-a),encoding='utf8')
    return dict(confidence='PROVEN',scope='Exact existing artifacts, no rebuild; code equality is not mounted-state equality',
        SC35D8_existing_path=str(clean),SC35D8_manifest_path=str(old.source.REF/'firmware/sc35d8/manifest.json'),images=rows)
def mount(spc,nfats,root_entries,fat_sectors):
    e=old.fresh();u=e.uc;fs=0x20023000;path=0x20022000;reads=[];writes=[]
    sector=bytearray(4096);sector[:3]=b'\xeb\x3c\x90'
    struct.pack_into('<H',sector,11,4096);sector[13]=spc
    struct.pack_into('<H',sector,14,1);sector[16]=nfats
    struct.pack_into('<H',sector,17,root_entries);struct.pack_into('<H',sector,19,0x1f2c)
    sector[21]=0xf8;struct.pack_into('<H',sector,22,fat_sectors)
    sector[54:62]=b'FAT12   ' if spc==2 else b'FAT16   ';sector[510:512]=b'\x55\xaa'
    # Recognition uses FAT marker; class comes from count, not this cosmetic text.
    u.mem_write(fs,b'\0'*0x1040);u.mem_write(path,b'0:/\0');e.w32(path+0x40,path);e.w32(0x20005e5c,fs)
    def hook(u,pc,n,d):
        if pc in (0x0801a75c,0x0801a78a):old.ret(e,0)
        elif pc==0x0801a7c2:
            assert u.reg_read(UC_ARM_REG_R1)==2
            u.mem_write(u.reg_read(UC_ARM_REG_R2),struct.pack('<H',4096));old.ret(e)
        elif pc==0x0801a796:
            l=u.reg_read(UC_ARM_REG_R2);reads.append(l)
            assert l==0 # bounded normal superfloppy mount, no partition trick
            u.mem_write(u.reg_read(UC_ARM_REG_R1),bytes(sector));old.ret(e)
        elif pc==0x0801a7ac:writes.append(u.reg_read(UC_ARM_REG_R2));raise AssertionError('Mount unexpectedly wrote')
    u.hook_add(UC_HOOK_CODE,hook)
    status=e.call(0x080197a0,path+0x40,path+0x100,0,maxins=200000)
    assert status==0 and not writes
    return dict(sectors_per_cluster=spc,FAT_count=nfats,root_entries=root_entries,FAT_sectors=fat_sectors,
        total_sectors=0x1f2c,result=status,FAT_type=e.r8(fs),n_fatent=e.r32(fs+0x20),
        volume_base=e.r32(fs+0x28),FAT_base=e.r32(fs+0x2c),root_base=e.r32(fs+0x30),data_base=e.r32(fs+0x34),
        read_LBAs=reads,writes=writes,scope='Coherent bounded normal BPB model, not unit acquisition or formatter output')
def main():
    v=versions();cases=[mount(*x) for x in [(1,2,512,4),(2,2,512,2),(1,1,512,4),(1,2,1024,4)]]
    assert {x['FAT_type'] for x in cases}=={1,2}
    e=old.fresh();e.call(0x080373ec,0,3,0x20022000);assert e.r32(0x20022000)==4096
    r=dict(confidence='PROVEN',version_comparison=v,bounded_normal_mount_cases=cases,
        native_NOR_sector_query=dict(function='0x080373ec',operation=3,result=4096,hardware_access=False),
        current_unit_geometry_established=False)
    (OUT/'geometry-review.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(version_ranges_all_equal=True,normal_mount_cases=cases,sector_query=4096),indent=2))
if __name__=='__main__':main()
