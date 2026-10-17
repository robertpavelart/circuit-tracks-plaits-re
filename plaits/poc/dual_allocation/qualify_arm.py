"""Execute selected existing B1.3 Thumb pages; never build/save an app image."""
import base64,hashlib,json,struct,sys
import study
ROOT,REF=study.ROOT,study.REF
OUT=ROOT/'builds/phase20h-budget-qualification';OUT.mkdir(exist_ok=True)
study.setup()
import vcf21 as V,packio as PK
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ,UC_HOOK_MEM_READ_UNMAPPED,UC_HOOK_MEM_FETCH_UNMAPPED
from unicorn.arm_const import *
MAN=json.loads((REF/'firmware/b1.3/manifest.json').read_text())
LAB={sec:{k:int(v,16) for k,v in row.get('labels',{}).items()} for sec,row in MAN['report'].items() if isinstance(row,dict)}
L=LAB['vcf20'];ML=LAB['mpatch'];STOP=0x0807ff00;GF=0x20061000;VIEW=0x20062000
stock=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
line=next(l for l in (REF/'tools/rc_uploader.html').read_text(encoding='utf-8').splitlines() if l.startswith('const PATCHES = '))
OPS=json.loads(line[len('const PATCHES = '):].rstrip(';'))['B1.3']['ops']
def slice_existing(addr,n):
    lo=addr-0x08010000;hi=lo+n;cursor=0;pieces=[]
    for op in OPS:
        size=op[2] if op[0]==0 else len(base64.b64decode(op[1]));a=max(lo,cursor);b=min(hi,cursor+size)
        if a<b:
            chunk=stock[op[1]:op[1]+op[2]] if op[0]==0 else base64.b64decode(op[1]);pieces.append(chunk[a-cursor:b-cursor])
        cursor+=size
    out=b''.join(pieces)
    if len(out)!=n:raise RuntimeError(f'Absent existing application page {addr:x}')
    return out
class ARM:
    def __init__(self):
        self.uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u=self.uc
        u.mem_map(0x20000000,0x70000);u.mem_map(STOP&~0xfff,4096);u.mem_write(STOP,b'\x00\xbf')
        self.pages={};self.trace=[];self.mail=[];self.calls=[];self.serial=0;self.incall=False;self.done=False;self.patch=None
        self.allowed=[(V.TAIL,V.TAIL+128),(GF,GF+512),(VIEW,VIEW+0x300),(PK.BUF,PK.BUF+4096),(V.HAL_TICK,V.HAL_TICK+4),(0x2006d000,0x2006f000),(V.ENGINE,V.ENGINE+0x80),(V.REC_GATE_OBJ,V.REC_GATE_OBJ+0x80),(V.TXOBJ,V.TXOBJ+0x40),(0x20063000,0x20063100),(0x20064000,0x20064400),(0x20065000,0x20066000)]
        self.stubs={LAB['sc17']['c_gfst']:('fixture allocated Master FX block',GF),LAB['sc14']['c_gst']:('fixture allocated SC14 block',GF-PK.GFX_OFF if hasattr(PK,'GFX_OFF') else GF),LAB['sc06']['c_settings']:('fixture settings object unavailable',0),V.SAVE_FN:('persistence storage boundary',None),PK.BUF_LOCK:('fixture buffer lock',0),PK.BUF_UNLOCK:('fixture buffer unlock',None)}
        u.hook_add(UC_HOOK_MEM_READ_UNMAPPED|UC_HOOK_MEM_FETCH_UNMAPPED,self.page)
        u.hook_add(UC_HOOK_CODE,self.code);u.hook_add(UC_HOOK_MEM_WRITE,self.write);u.hook_add(UC_HOOK_MEM_READ,self.read)
        u.mem_write(V.TAIL,bytes(128));u.mem_write(GF,bytes(512));u.mem_write(VIEW,bytes(64));u.mem_write(VIEW+0x10,b'\x00')
        # Declared stopped-sequencer fixture: four scalar engine stores and
        # recorder pattern pointers, neutral lane bytes. No scheduler assumed.
        for t in range(4):
            self.w32(V.ENGINE+0x30+4*t,0x20063000+0x20*t)
            self.w32(V.REC_GATE_OBJ+0x0c+4*t,0x20064000+0x100*t)
            self.w32(0x20064000+0x100*t+0x48,0x20065000)
        u.mem_write(0x20065000,bytes(0xca8));u.mem_write(0x20065000+0x3a8,bytes([64])*192)
        self.w32(V.TXOBJ+0x0c,VIEW+0x100);u.mem_write(VIEW+0x100,bytes([0,1,2,3]))
        self.stubs[V.CC_HELPER]=('MIDI output boundary',None)
        for labels in LAB.values():
            for name in ('c_non','c_noff'):
                if name in labels:self.stubs[labels[name]]=('older note-routing boundary after real vcf wrapper',None)
        self.tick=100;self.w32(V.HAL_TICK,self.tick)
    def page(self,u,access,a,n,v,data):
        p=a&~0xfff
        if not 0x08010000<=p<0x08080000:raise RuntimeError(f'Unmapped non-app address {a:x}')
        b=slice_existing(p,4096);u.mem_map(p,4096);u.mem_write(p,b);self.pages[p]=hashlib.sha256(b).hexdigest();return True
    def code(self,u,a,n,data):
        self.pc=a
        if a==STOP or a==V.T_PAD_RET or a==LAB['persist19']['c_dtick19']:
            self.done=True;u.emu_stop();return
        if a in self.stubs:
            why,ret=self.stubs[a];self.trace.append(dict(type='boundary',pc=a,reason=why))
            if ret is not None:u.reg_write(UC_ARM_REG_R0,ret)
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
        elif a==V.DSP_WRITE:
            w=dict(track=(u.reg_read(UC_ARM_REG_R2)-V.VB0)//V.VBS,address=u.reg_read(UC_ARM_REG_R2),space=u.reg_read(UC_ARM_REG_R0),wire=u.reg_read(UC_ARM_REG_R1),tick=self.tick)
            w['word']=w['wire']>>8;w['code']=(w['word']>>16)&127;w['value']=w['word']&65535;self.mail.append(w);self.trace.append(dict(type='mailbox',pc=a,**w));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
        elif a==ML['c_mpr']:
            if self.patch is None:raise RuntimeError('Unexpected patch storage read')
            self.trace.append(dict(type='boundary',pc=a,reason='fixture stored 44-byte patch read',patch=self.patch.hex()))
            u.mem_write(PK.BUF,self.patch);u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,44);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
        elif a==V.PARAM_GET:
            obj=u.reg_read(UC_ARM_REG_R0);param=u.reg_read(UC_ARM_REG_R1)
            assert 0x20063000<=obj<0x20063100 and param<3,(hex(obj),param)
            self.trace.append(dict(type='boundary',pc=a,reason='declared stopped engine scalar-store accessor',object=obj,param=param))
            u.reg_write(UC_ARM_REG_R0,obj+4*param);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
    def write(self,u,access,a,n,v,data):
        if self.incall:self.trace.append(dict(type='write',pc=self.pc,address=a,size=n,before=bytes(u.mem_read(a,n)).hex(),value=v))
    def read(self,u,access,a,n,v,data):
        if self.incall and 0x20000000<=a<0x20070000 and not any(lo<=a and a+n<=hi for lo,hi in self.allowed):raise RuntimeError(f'Undeclared fixture RAM read {a:x} PC {self.pc:x}')
    def w32(self,a,v):self.uc.mem_write(a,struct.pack('<I',v))
    def state(self):return dict(tail=bytes(self.uc.mem_read(V.TAIL,128)).hex(),gf=bytes(self.uc.mem_read(GF,512)).hex())
    def call(self,name,*args,regs=None):
        u=self.uc;begin=len(self.trace);m=len(self.mail);before=self.state();self.done=False;self.serial+=1
        fn=L.get(name,ML.get(name));assert fn is not None,name
        u.reg_write(UC_ARM_REG_SP,0x2006e000);u.reg_write(UC_ARM_REG_LR,STOP|1)
        for i,val in enumerate(args):u.reg_write(UC_ARM_REG_R0+i,val)
        for i,val in (regs or {}).items():u.reg_write(UC_ARM_REG_R0+i,val)
        self.incall=True
        try:u.emu_start(fn|1,0xffffffff,count=200000)
        except Exception as ex:raise RuntimeError((name,hex(u.reg_read(UC_ARM_REG_PC)),hex(u.reg_read(UC_ARM_REG_LR)),self.trace[-5:])) from ex
        finally:self.incall=False
        assert self.done,(name,hex(u.reg_read(UC_ARM_REG_PC)))
        rec=dict(id=self.serial,symbol=name,entry=fn,args=args,regs=regs,before=before,after=self.state(),ordered_events=self.trace[begin:],mail=self.mail[m:]);self.calls.append(rec);return rec
    def init(self):self.call('c_vtick')
    def pad(self,t):self.uc.mem_write(VIEW+0x10,bytes([t]));return self.call('vp_tri',VIEW)
    def send(self,ms=2):
        self.tick+=ms;self.w32(V.HAL_TICK,self.tick)
        return self.call('c_vtick')
    def load(self,t,flags):
        vals=bytes(v&255 for v in tuple(V.DEFAULTS[:26])+tuple(V.DEFAULTS_V2))
        b=b'CTM1'+bytes([flags,1])+vals;self.patch=b+bytes([sum(b[4:40])&255,1,0,0]);assert len(self.patch)==44
        return self.call('c_mpload',t,0)
def mode(e,t):
    b=bytes(e.uc.mem_read(V.TAIL,128));on=(b[V.O_FLAGS]>>t)&1;osc=(b[V.O_FLAGS]>>(t+2))&1;va=(b[V.O_SIG]>>t)&1;gran=(b[V.O_SIG]>>(t+2))&1
    return 'off' if not on else 'FXseq' if not osc and va else 'line' if not osc else 'VA' if va else 'gran' if gran else 'osc'
def main():
    e=ARM();e.init();seq=[]
    # Actual pad-cycle instruction path, including active-note internal helper.
    for t in (0,1):
        for repeat in range(3):
            for step in range(7):
                old=mode(e,t);rec=e.pad(t);new=mode(e,t)
                if step==2:
                    e.call('c_vnon',V.TXOBJ,t+2,60+t*7,100)
                if repeat==1:
                    e.call('c_vapply',t,step%8,20+step*13)
                r=e.send(0 if repeat==2 else 2)
                seq.append(dict(track=t,repeat=repeat,before=old,after=new,pad_call=rec['id'],sender_call=r['id'],mail=r['mail']))
                if repeat!=2:
                    for _ in range(8):e.send()
    # Every valid patch mode, cross-restored from both old synthesis modes.
    for t in (0,1):
        for source in (0,3,7):
            for target in (1,11,5,0,3,7):
                e.load(t,source);e.send();old=mode(e,t)
                note=e.call('c_vnon',V.TXOBJ,t+2,60+t*7,100)
                r=e.load(t,target);s=e.send();seq.append(dict(track=t,source_patch_flags=source,target_patch_flags=target,before=old,after=mode(e,t),active_note_call=note['id'],restore_call=r['id'],sender_call=s['id'],mail=s['mail']))
                for _ in range(40):e.send()
                e.call('c_vnoff',V.TXOBJ,t+2,60+t*7,0)
    # All 64 patch flag combinations are checksum-valid transport inputs.
    exhaustive=[]
    for flags in range(64):
        e.load(0,flags);r=e.send();act=next((w for w in r['mail'] if w['track']==0 and w['code']==19),None);assert act is not None,flags
        a=act['value']&3;d=(act['value']>>8)&31
        assert not(a==1 and d&4) and not(a==2 and d&16 and d&4)
        exhaustive.append(dict(patch_flags=flags,ACT=a,DFLAGS=d,word=act['word'],restore_call=e.calls[-2]['id'],sender_call=r['id']))
    result=dict(scope='Actual existing B1.3 Thumb execution with explicit allocated-buffer/storage fixtures; not whole ARM boot/session',constants={k:getattr(V,k) for k in ('TAIL','O_FLAGS','O_SIG','O_RT','RT_AUX','RT_TAG','RT_NOTE','RT_VEL','RT_CNT','HAL_TICK','RATE_MS')},pages=e.pages,transitions=seq,patch_flag_cases=exhaustive,calls=e.calls,mail=e.mail,limits=['No authentic boot/heap checkpoint','Storage read, locks, allocated block providers, settings absence, save, scalar-store accessor and DSP/MIDI peripheral writes explicitly intercepted','Real vcf note wrapper and automation c_vapply executed; older note-routing boundary and full stock scheduler not run','Stock synth/drum activity not represented in bounded ARM fixtures'])
    (OUT/'arm-transitions.json').write_text(json.dumps(result,indent=2)+'\n')
    cold=[]
    for flags,sig in [(0,0),(255,255),(255,0xaf),(255,0xa6)]:
        z=ARM();z.uc.mem_write(V.TAIL+V.O_FLAGS,bytes([flags]));z.uc.mem_write(V.TAIL+V.O_SIG,bytes([sig]));z.init()
        for _ in range(8):z.send()
        cold.append(dict(initial_flags=flags,initial_signature=sig,calls=z.calls,mail=z.mail))
    (OUT/'cold-tail-fixtures.json').write_text(json.dumps(dict(scope='Actual c_vtick initialization on four declared tail inputs, not full stock boot',cases=cold),indent=2)+'\n')
    timeline=ARM();timeline.init();initial=[];initial_frames=[]
    for t in (0,1):timeline.load(t,1)
    for b in range(48):
        r=timeline.send();initial+=r['mail'];initial_frames.append(dict(block=b,ARM_call=r['id'],tick=timeline.tick,modes=[mode(timeline,t) for t in (0,1)],events=[],mail=r['mail']))
    frames=[]
    for block in range(256):
        events=[]
        if block%16==0:
            for t in (0,1):
                target=[1,11,5,0][(block//16+t)%4]
                r=timeline.load(t,target);events.append(dict(type='restore',call=r['id'],track=t,flags=target))
        if block%7==0:
            for t in (0,1):
                r=timeline.call('c_vnon',V.TXOBJ,t+2,48+(block%24),90);events.append(dict(type='note_on',call=r['id']))
        if block%7==3:
            for t in (0,1):
                r=timeline.call('c_vnoff',V.TXOBJ,t+2,48+((block-3)%24),0);events.append(dict(type='note_off',call=r['id']))
        if block%3==1:
            for t in (0,1):
                r=timeline.call('c_vapply',t,(block//3)%8,block%128);events.append(dict(type='automation_sink',call=r['id']))
        send=timeline.send(ms=(2*(block+1)//3)-(2*block//3))
        frames.append(dict(block=block,ARM_call=send['id'],tick=timeline.tick,modes=[mode(timeline,t) for t in (0,1)],events=events,mail=send['mail']))
    (OUT/'arm-retained-timeline.json').write_text(json.dumps(dict(initial_mail=initial,initial_frames=initial_frames,frames=frames,calls=timeline.calls,pages=timeline.pages,scope='Real mode restore/note/automation sink/sender on declared fixtures; 256 32-sample/48kHz scheduled frames after 48 initialization frames, not the stock scheduler or whole device'),indent=2)+'\n')
    print(json.dumps(dict(calls=len(e.calls),mail=len(e.mail),transitions=len(seq),patch_cases=len(exhaustive),pages=len(e.pages),stale_ACT_combinations=0)))
if __name__=='__main__':main()
