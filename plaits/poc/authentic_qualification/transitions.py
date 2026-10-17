"""Repeat preserved transition/flag vectors on authentic ARM RAM, keeping I/O models explicit."""
import json,struct
from environment import *
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1
LV={k:int(v,16) for k,v in MAN['report']['vcf20']['labels'].items()};LM={k:int(v,16) for k,v in MAN['report']['mpatch']['labels'].items()}
TAIL=0x20039789;BUF=0x20003d04;VIEW=0x2006c000;HAL=0x2000081c
def main():
    s=authentic_session();s.capture('init retained services',LV['c_vtick']);s.e.call(int(MAN['report']['sc17']['labels']['c_gfst'],16));gf=s.e.uc.reg_read(UC_ARM_REG_R0)
    vals=[bytes(s.e.uc.mem_read(TAIL+1+26*t,26))+bytes(s.e.uc.mem_read(gf+180+8*t,8)) for t in (0,1)]
    patch=None;trace=[];current='';tick=2000
    def code(u,a,n,data):
        if a in (0x08026d06,0x08026d34,0x0802d2ac,0x0804d5c0):
            trace.append(dict(type='modeled storage/lock or pad return boundary',pc=a,stage=current))
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1);return
        if a==LM['c_mpr']:
            u.mem_write(BUF,patch);u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,44);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
    def write(u,access,a,n,v,data):
        if TAIL<=a<TAIL+128 or gf<=a<gf+256:trace.append(dict(type='RAM write',pc=u.reg_read(UC_ARM_REG_PC),address=a,size=n,value=v,stage=current))
    s.e.uc.hook_add(UC_HOOK_CODE,code);s.e.uc.hook_add(UC_HOOK_MEM_WRITE,write)
    def load(t,flags):
        nonlocal patch
        b=b'CTM1'+bytes([flags,0])+vals[t];patch=b+bytes([sum(b[4:40])&255,1,0,0]);s.capture('restore',LM['c_mpload'],t,0)
    def send():
        nonlocal tick
        tick+=4;s.e.w32(HAL,tick);s.capture('service',LV['c_vtick'])
        return [dict(track=(a-0x3b80)//48,word=v,ACT=v&3,DFLAGS=(v>>8)&31) for _,sp,a,v in s.events[-1][1] if sp=='x' and a in (0x3b80,0x3bb0) and ((v>>16)&127)==19]
    old=json.loads((ROOT/'builds/phase20h-budget-qualification/arm-transitions.json').read_text())['transitions'];assert len(old)==78
    results=[];modes={'off':0,'line':1,'osc':3,'VA':7,'gran':11,'FXseq':5}
    for i,case in enumerate(old):
        current=f'preserved-transition-{i}';t=case['track'];s.events=[]
        load(t,case.get('source_patch_flags',modes[case['before']]));send()
        s.capture('note on',LV['c_vnon'],0x20011334,t+2,60+7*t,100)
        before=bytes(s.e.uc.mem_read(TAIL,128)).hex()
        if 'target_patch_flags' in case:load(t,case['target_patch_flags'])
        else:
            s.e.uc.mem_write(VIEW,bytes(64));s.e.uc.mem_write(VIEW+0x10,bytes([t]));s.capture('actual pad engine handler',LV['vp_tri'],VIEW)
        if case.get('repeat')==1:s.capture('automation sink',LV['c_vapply'],t,i%8,i%128)
        emitted=send();results.append(dict(vector=i,input=case,before=before,after=bytes(s.e.uc.mem_read(TAIL,128)).hex(),ACT_messages=emitted,events=s.events))
    flags=[]
    for t in (0,1):
        for f in range(64):
            current=f'flag-domain-{t}-{f}';s.events=[];load(t,f);emitted=send();got=next(w for w in emitted if w['track']==t)
            assert not(got['ACT']==1 and got['DFLAGS']&4)
            assert not(got['ACT']==2 and got['DFLAGS']&16 and got['DFLAGS']&4)
            flags.append(dict(track=t,patch_flags=f,**{k:v for k,v in got.items() if k!='track'}))
    out=dict(initialization='Authentic pinned ARM dump with existing B1.3 code; native c_gfst/c_settings and real objects',preserved_transition_vectors=len(results),results=results,flag_domain=flags,trace=trace,
        source_domain='For a selected track: on, oscillator, VA/velocity-engine bits, route and dual are the six Boolean inputs to ACT. All 64 combinations executed separately on both tracks. Tag/timestamp do not change ACT payload.',
        limits=['Storage record delivery/locks/save modeled, not a filesystem or RTOS replay','Pad view selector field modeled','Peripheral SPI responses and stock routing boundaries retain reference E/Shi models','No interrupt preemption or coupled core1'])
    (OUT/'authentic-transitions.json').write_text(json.dumps(out,indent=2)+'\n');print('78 preserved transitions completed; 128 flag-domain cases, zero invalid ACT combinations')
if __name__=='__main__':main()
