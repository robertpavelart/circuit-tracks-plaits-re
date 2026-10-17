"""Show why the existing owned 12 bytes cannot yet hold the new schema."""
from pathlib import Path
import sys,json,struct
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase42-exact-rdiag-integration'))
from environment import Physical
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import inspect_storage as src
def main():
    packed=bytes.fromhex(json.loads((OUT/'compact-tests.json').read_text())['round_trips'][0]['compact_hex'])
    state=0x20044d70;e=Physical();u=e.uc
    for at,n in ((0x0806b6cc,124),(0x0806b748,80)):
        assert bytes(u.mem_read(at,n))==src.app[at-0x08010000:at-0x08010000+n]
    assert e.r32(0x20002b44)==0x20044e58 and e.r32(0x20002b48)<=state
    before=struct.pack('<I',0x11)+packed;u.mem_write(state,before)
    returned=e.call(0x0805dbcc);after=bytes(u.mem_read(state,12))
    assert returned==0x20044d7c and after!=before and after==struct.pack('<I',0x4e4f5234)+bytes(8)
    # Preserve the legacy magic but use its eight payload bytes as geometry:
    # the old SysTick owner interprets byte+4 as ACTIVE and writes quarantine.
    u.mem_write(state+4,packed);assert packed[0]==1
    e.w32(0x2000081c,(e.r32(state+8)+5001)&0xffffffff)
    e.call(0x0806b748);changed=bytes(u.mem_read(state+4,8));assert changed[0]==3 and changed!=packed
    r=dict(confidence='PROVEN',scope='Native existing getter/timeout ownership collision in emulator; no new firmware or safe-liveness assertion',
        region=['0x20044d70','0x20044d7b'],initialization_overwrites_record=True,
        before=before.hex(),after=after.hex(),legacy_timeout_corrupts_compact_record=True,
        compact_before=packed.hex(),compact_after=changed.hex(),existing_allocator_limit=hex(e.r32(0x20002b44)),
        native_getter='0x0805dbcc -> 0x0806b6cc',native_watch='0x0806b748',passed=True)
    (OUT/'liveness-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,collisions=2)))
if __name__=='__main__':main()
