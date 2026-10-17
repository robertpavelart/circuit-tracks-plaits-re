"""Long authentic-ARM-initialized, reference-style core0 workload comparison."""
import collections,json,math,struct,subprocess
from environment import *
import dsp_session as DS
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PC,UC_ARM_REG_LR
LV={k:int(v,16) for k,v in MAN['report']['vcf20']['labels'].items()}
LM={k:int(v,16) for k,v in MAN['report']['mpatch']['labels'].items()}
LG={k:int(v,16) for k,v in MAN['report']['sc17']['labels'].items()}
TAIL=0x20039789;HAL=0x2000081c;BUF=0x20003d04;BLOCKS=4096
def capture():
    s=authentic_session();s.capture('initial mode/service tick',LV['c_vtick']);s.e.call(LG['c_gfst']);gf=s.e.uc.reg_read(UC_ARM_REG_R0)
    assert gf!=0
    objects=dict(CTX_receiver=0x20044cb8,TX_interface=0x20011334,settings_tail=TAIL,MasterFX_block=gf,DSP_dirty_groups=DS.DIRTY,HAL_tick=HAL)
    snapshots={name:bytes(s.e.uc.mem_read(a,64 if name!='HAL_tick' else 4)).hex() for name,a in objects.items()}
    initial_events=list(s.events)
    presets=[]
    for t in (0,1):
        vals=bytes(s.e.uc.mem_read(TAIL+1+26*t,26))+bytes(s.e.uc.mem_read(gf+180+8*t,8))
        presets.append(vals)
    patch=None;boundaries=[]
    def store(u,a,n,data):
        if a in (0x08026d06,0x08026d34,0x0802d2ac):
            boundaries.append(dict(type='modeled storage/lock/scheduler boundary',address=a))
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1);return
        if a==LM['c_mpr']:
            assert patch is not None
            boundaries.append(dict(type='modeled stored patch delivery',patch=patch.hex()))
            u.mem_write(BUF,patch);u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,44);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
    hook=s.e.uc.hook_add(UC_HOOK_CODE,store)
    def restore(t,flags):
        nonlocal patch
        b=b'CTM1'+bytes([flags,0])+presets[t];patch=b+bytes([sum(b[4:40])&255,1,0,0]);s.capture('patch restore',LM['c_mpload'],t,0)
    frames=[]
    for b in range(BLOCKS):
        s.events=[];actions=[]
        # Stock-note stimuli go through the actual MIDI receiver and parameter
        # flush. The reference SPI adapter's zero replies remain documented.
        if b%128==0:
            track=0 if b<1024 else 1 if b<2048 else (b//128)&1
            note=48+(b//128)%24;s.midi(bytes([0x90+track,note,100]));actions.append(dict(type='stock note_on',track=track,note=note))
        if b%128==64:
            track=0 if b<1024 else 1 if b<2048 else (b//128)&1
            note=48+(b//128)%24;s.midi(bytes([0x80+track,note,0]));actions.append(dict(type='stock note_off',track=track,note=note))
        if b%128==32:
            track=0 if b<1024 else 1 if b<2048 else (b//128)&1
            s.midi(bytes([0xb0+track,74,(b//128*13)%128]));actions.append(dict(type='stock filter parameter',track=track))
        if b>=2048 and b%256==0:
            s.midi(bytes([0x90,60,100]));s.midi(bytes([0x91,67,100]));actions.append(dict(type='requested simultaneous stock notes',status='Must verify distinct voice groups; no assumption'))
        if b>=2048 and b%64==0:
            s.midi(bytes([0x99,36+(b//64)%4,100]));actions.append(dict(type='stock drum trigger'))
        if b%256==0:
            for t in (0,1):
                flag=[1,11,5,0][(b//256+t)%4];restore(t,flag);actions.append(dict(type='real restore with modeled patch',track=t,flags=flag))
        if b%32==1:
            for t in (0,1):s.capture('automation sink',LV['c_vapply'],t,(b//32)%8,(b//32*7)%128)
            actions.append(dict(type='automation sink'))
        # Real Master FX service computes DSP parameters from initialized state.
        s.e.uc.mem_write(gf+6,bytes([0b111011 if b>=2048 and (b//256)%2 else 0]));s.e.w32(HAL,2000+2*b//3)
        s.capture('mode/FX/drum service',LV['c_vtick'])
        frames.append(dict(block=b,actions=actions,events=s.events))
        if b%1024==0:print('ARM stimulus',b,flush=True)
    s.e.uc.hook_del(hook)
    result=dict(init_writes=s.init_writes,initial_events=initial_events,frames=frames,objects=objects,object_snapshots=snapshots,patch_boundaries=boundaries,
        unsupported_unstubbed_restore=dict(entry=LM['c_mpload'],instruction_limit=20000000,stopped_PC=0x0801be62,result='did not return; no pass claimed',reason='Reference snapshot/single-thread harness does not service blocking storage lock/scheduler'),
        limitations=['Reference Shi SPI replies are zero, not live DSP feedback','Reference core0 spin waits are NOPed, no concurrent core1','Audio input is deterministic modeled stimulus','Stored patches, buffer locks and save boundary are modeled; actual patch validation/apply executes','HAL clock and callback schedule modeled; no hardware/interrupt timing'])
    (OUT/'authentic-ARM-workload.json').write_text(json.dumps(result,indent=2)+'\n');return result
def native(profile,w):
    folder=OUT/('long-'+profile);folder.mkdir(exist_ok=True)
    p=DS.dsp_program(PUBLISHED) if profile=='original' else (ROOT/f'builds/phase20g-dual-allocation/{profile}.be24').read_bytes()
    n=len(p)//3;prog=bytearray(p)
    for at in DS.SPIN_NOPS:prog[3*at:3*at+3]=bytes(3)
    (folder/'program.be24').write_bytes(prog)
    canary=[0x5a1234]*(0x4000-n)
    ls=['LOADP program.be24 0',f'FREETAIL {n:x}','MAX 20000000','HIST hist.txt','TRACE trace.bin','WATCHFILE watch.txt','WATCH X 2c46 33','WATCH X 2e10 64','WATCH X 3900 192','WATCH X 3b80 96','WATCH X 37000 32','PC 107','STOP 25f3','RUN']
    ls+=DS.Session._mem(w['init_writes']);ls+=['PC 25f3','STOP 113','RUN']
    for _,ws in w['initial_events']:ls+=DS.Session._mem(ws)
    ls+=['P 7000 0bf080 0001ed 0c7002','P %x %s'%(n,' '.join('%06x'%v for v in canary)),'RESETTRACE']
    dumps=[('X',0x2c46,33),('Y',0x800,64),('X',0x2e10,64),('X',0xeb,112),('X',0x57a,0x400),('Y',0x59f,0x400),('X',0x3a40,0x180),('X',0x3900,192),('X',0x3b80,96),('X',0x3d00,40),('X',0x37000,0x621)]
    for f in w['frames']:
        for _,ws in f['events']:ls+=DS.Session._mem(ws)
        ring=[int(0x80000*math.sin(2*math.pi*(220+110*t)*(32*f['block']+i)/48000))&0xffffff for i in range(32) for t in (0,1)]
        ls += ['Y ffd 001000','Y 1000 '+' '.join('%06x'%v for v in ring),'PC 7000','STOP 7002','RUN']
        # Output and all newly freed P words checked every block; expanded
        # semantic state snapshots every 64 blocks and on the last block.
        ls += ['DUMPX 2e10 64',f'DUMPP {n:x} {len(canary)}','REGDUMP']
        if f['block']%64==0 or f['block']==BLOCKS-1:ls +=[f'DUMP{sp} {ad:x} {count}' for sp,ad,count in dumps]
    (folder/'job.txt').write_text('\n'.join(ls)+'\n')
    r=subprocess.run([str(OUT/'dsptool-audit.exe'),'run','job.txt'],cwd=folder,capture_output=True,text=True);(folder/'output.txt').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(profile,r.returncode,r.stderr[-500:])
    ran=[l for l in r.stdout.splitlines() if l.startswith('RAN')];assert len(ran)==BLOCKS+2
    assert 'pc=0025f3' in ran[0] and 'pc=000113' in ran[1] and all('pc=007002' in l for l in ran[2:])
    for l in r.stdout.splitlines():
        if l.startswith(f'P {n:06x}:'):assert [int(v,16) for v in l.split(':')[1].split()]==canary
    print('Finished',profile,BLOCKS,'blocks',flush=True)
def main():
    if (OUT/'authentic-ARM-workload.json').exists():w=json.loads((OUT/'authentic-ARM-workload.json').read_text())
    else:w=capture()
    for p in ('original','osc_only','osc_va'):native(p,w)
if __name__=='__main__':
    # Preserve actual post-init params and mode tick before constructing frames.
    initial_events=[]
    # capture() sets this immediately after authentic initialization below.
    main()
