"""Exact mount boundary, modeled native mounts, and small-RAM candidates. Offline only."""
from pathlib import Path
import sys,json,struct,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import native_cases as prior
sys.path.insert(0,str(ROOT/'builds/phase49-existing-geometry-reader'))
from geometry_parser import decode as geometry_decode
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
FS=0x20000ab0;DISK=0x20000aa0
def record(e):
    return b''.join(bytes(e.uc.mem_read(a,n)) for a,n in ((0x20000a98,8),(FS,14),(FS+0x20,24)))
def sector(spc=1):
    b=bytearray(4096);b[:3]=b'\xeb\x3c\x90';b[54:59]=b'FAT16'
    struct.pack_into('<H',b,11,4096);b[13]=spc;struct.pack_into('<H',b,14,1);b[16]=2
    struct.pack_into('<H',b,17,512);struct.pack_into('<H',b,19,7980);struct.pack_into('<H',b,22,4)
    b[510:512]=b'\x55\xaa';return bytes(b)
def mount_case(name,kind='valid',spc=1,seed_stale=True,wrap=False,pair=False):
    e=prior.Physical();u=e.uc;u.mem_write(0x08010000,prior.source.app)
    if not seed_stale:u.mem_write(FS,b'\0'*0x103c)
    else:
        # Old geometry deliberately differs from the incoming modeled volume.
        u.mem_write(FS,b'\0'*0x103c);u.mem_write(FS,b'\x03');e.w32(FS+0x20,0x123456)
        e.w32(FS+0x34,0x9988);u.mem_write(FS+6,b'\x77\x77')
    if wrap:u.mem_write(0x20005e58,b'\xff\xff')
    events=[];writes=[];boundaries=[];counts=0;raw=sector(spc)
    if kind=='invalid':raw=b'\0'*4096
    def hook(u,pc,n,d):
        nonlocal counts
        counts+=1
        if pc==0x0801b3b8:prior.ret(e,0) # UART log only seam
        elif pc in (0x0801a75c,0x0801a78a):prior.ret(e,0 if kind!='not-ready' and u.reg_read(UC_ARM_REG_R0)==0 else 1)
        elif pc==0x0801a7c2:
            assert u.reg_read(UC_ARM_REG_R1)==2
            u.mem_write(u.reg_read(UC_ARM_REG_R2),struct.pack('<H',4096));prior.ret(e,0)
        elif pc==0x0801a796:
            lba=u.reg_read(UC_ARM_REG_R2);events.append(dict(read_lba=lba,fs_type=e.r8(FS)))
            if kind=='io-error':prior.ret(e,1)
            else:u.mem_write(u.reg_read(UC_ARM_REG_R1),raw if lba==0 else b'\0'*4096);prior.ret(e,0)
        elif pc in (0x0801a7ac,0x08024164,0x080241b8):
            writes.append(hex(pc));raise AssertionError('mount reached array mutation')
        elif pc in (0x08019ab6,0x08019abe,0x08019a32,0x08019a4c):
            events.append(dict(at=hex(pc),fs_type=e.r8(FS),status=u.reg_read(UC_ARM_REG_R0)))
        elif pc==0x0801ae06:
            status=u.reg_read(UC_ARM_REG_R0)
            if u.reg_read(UC_ARM_REG_R4)!=DISK:
                events.append(dict(other_disk_mount_return=hex(u.reg_read(UC_ARM_REG_R4)),status=status))
                return
            b=record(e);r=dict(at=hex(pc),status=status,fs_type=e.r8(FS),record=b.hex(),
                registered_fs=hex(e.r32(0x20005e5c)),wrapper=hex(e.r32(DISK+4)),
                geometry_pointer=hex(e.r32(DISK+8)),disk_drive=e.r8(DISK+0xc))
            if status==0:
                assert e.r8(FS)==(2 if spc==1 else 1) and e.r32(FS+0x34)==13 and e.r32(FS+0x20)!=0x123456
                assert all(x['fs_type']==0 for x in events if 'read_lba' in x)
                try:r['parsed']=geometry_decode(b);r['legacy_parser_accepts']=True
                except ValueError as err:r['legacy_parser_accepts']=False;r['parser_rejection']=str(err)
            else:assert e.r8(FS)==0
            boundaries.append(r)
    u.hook_add(UC_HOOK_CODE,hook)
    before_regs={str(r):u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)}
    if pair:e.call(0x0801f0a8,maxins=200000)
    else:e.call(0x0801addc,DISK,maxins=200000)
    assert all(u.reg_read(int(r))==v for r,v in before_regs.items())
    assert boundaries and not writes
    ok=kind=='valid'
    assert (boundaries[0]['status']==0)==ok
    return dict(name=name,seams='UART logging and disk status/ioctl/read completions modeled; native registration, BPB parse and mount return execute',
        input='Synthetic coherent FAT16 BPB, not current-unit NOR',events=events,boundary=boundaries[0],
        persistent_calls=writes,supported_native_callee_registers_preserved=True,native_instructions_including_seam_entries=counts)
def inspect():
    images={'stock':prior.STOCK,'B1.3':prior.PUBLISHED[:],
       'SC35D8':(ROOT/'builds/phase43-hardware-test-candidate/clean-sc35d8.bin').read_bytes(),
       'corrected-diagnostic':prior.source.app}
    ranges=[(0x08019734,0x3a6),(0x0801addc,0x68),(0x0801ae90,0xb8),(0x0801f0a8,0x40),
       (0x08019a32,0x20),(0x0801d4b0,0x24),(0x0801859a,0x100)]
    result=[]
    for name,data in images.items():
        result.append(dict(name=name,sha256=hashlib.sha256(data).hexdigest(),ranges=[dict(start=hex(a),length=n,
            equal_stock=data[a-0x08010000:a-0x08010000+n]==prior.STOCK[a-0x08010000:a-0x08010000+n]) for a,n in ranges]))
    for a,n in ranges:
        (OUT/f'app-{a:08x}.asm').write_text(prior.source.listing('app',a,n),encoding='utf8')
    return result
def main():
    rows=[mount_case('fresh-valid',seed_stale=False),mount_case('stale-type-remount-valid'),
        mount_case('stale-type-invalid-BPB','invalid'),mount_case('stale-type-read-error','io-error'),
        mount_case('stale-type-not-ready','not-ready'),mount_case('native-ID-wrap',wrap=True),
        mount_case('different-valid-cluster-size',spc=2),mount_case('native-NOR-then-SD-constructor',pair=True)]
    valid=rows[0]['boundary']['parsed']
    assert all(not t['intersects_normal_writable_mapping'] for t in valid['targets'])
    ram=dict(confidence='PROVEN',scope='Concrete small-reservation candidate arithmetic, not global free-RAM proof',
        existing_state_start='0x20044d70',fixture_cursor='0x20044d68',headroom=8,
        compact_payload=46,compact_validity_bytes=1,compact_total=47,
        aligned_record_bytes=48,aligned_state_bytes=4,aligned_total=52,
        proposed_lower_limit=hex(0x20044d70-52),cursor_above_proposed_limit=0x20044d68-(0x20044d70-52),
        fixed_address_qualified=False)
    (OUT/'mount-cases.json').write_text(json.dumps(dict(confidence='PROVEN',cases=rows,passed=True),indent=2)+'\n')
    (OUT/'inspection.json').write_text(json.dumps(dict(images=inspect(),RAM_candidate=ram),indent=2)+'\n')
    print(json.dumps(dict(passed=True,native_mount_cases=len(rows),small_RAM_candidate=ram),indent=2))
if __name__=='__main__':main()
