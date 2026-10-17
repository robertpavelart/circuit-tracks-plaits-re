"""Native full SysEx dispatcher and deferred mode1/0 entry/exit.
Authenticated running RAM fixture, exact B1.3 code; USB HAL and scheduling modeled.
"""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase50-msd-readonly-geometry'))
from native_reads import Physical,IMAGE,ret
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
def main():
    e=Physical();u=e.uc;u.mem_write(0x08010000,IMAGE);traces=[];seams=[];schedule=[];phase=['']
    forbidden=(0x08023f68,0x0803cc16,0x0803cc34,0x0803cc54,0x08024164,0x080241b8,
      0x08037494,0x080374d4,0x08037648,0x08019a92,0x0801ae1c,0x0802d2ac,0x08039042)
    visited=set()
    def hook(u,pc,n,d):
        visited.add(pc)
        if pc in forbidden:raise AssertionError(f'{phase[0]} reached persistence/mount/reset {pc:x}')
        if pc==0x0801e538:
            schedule.append(hex(e.r32(0x20006824)));ret(e)
        elif pc==0x08024804:seams.append(dict(phase=phase[0],at=hex(pc),kind='USB disconnect delay'));ret(e)
        elif pc in (0x080381a8,0x08038280,0x080382c6,0x0803893e,0x08038b42,0x08038b04):
            seams.append(dict(phase=phase[0],at=hex(pc),kind='USB HAL register/peripheral boundary'));ret(e)
    u.hook_add(UC_HOOK_CODE,hook)
    try:
        for mode in (1,0,1,0):
            phase[0]=f'vendor42 mode{mode}'
            packet=IMAGE[0x149a8:0x149ad]+bytes([0x42,0,mode,0xf7])
            u.mem_write(0x20022000,packet);e.w32(0x20022100,0x20022000);e.w32(0x20022104,len(packet))
            e.call(0x0801eb30,0,0x20022100,0,maxins=200000)
            assert schedule[-1]=='0x80248b5'
            phase[0]=f'deferred mode{mode}'
            e.call(0x080248b4,maxins=200000)
            assert e.r8(0x200037bc)==mode
            traces.append(dict(request=mode,internal_mode=e.r8(0x200037bc),window=hex(e.r32(0x200037c0)),
                classes=[hex(e.r32(0x200000cc+8+4*i)) for i in range(e.r8(0x200000cc))],persistent_calls=0))
    except Exception:
        (OUT/'mode-model-checkpoint.json').write_text(json.dumps(dict(phase=phase[0],PC=hex(u.reg_read(UC_ARM_REG_PC)),
            seams=seams,traces=traces,scope='Incomplete model, not a firmware failure'),indent=2)+'\n',encoding='utf8')
        raise
    r=dict(confidence='PROVEN',scope='Full dispatcher and deferred class rebuild, HAL/scheduler seams; not physical USB enumeration or full scheduling',
        transitions=traces,seams=seams,visited_instruction_addresses=len(visited),forbidden_calls=0,
        hardware_access=False,MIDI_ports_opened=0)
    (OUT/'mode-cases.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
