"""Emulator-only native owner semantics. Fragments are never emitted as firmware.

ABI: R0 record; R1..R3 operation inputs. All registers/APSR/PRIMASK preserved.
Hooks from actual old owners to these fragments are NOT installed by this model.
"""
from pathlib import Path
import sys,struct,json,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase42-exact-rdiag-integration/source/tools'))
from thumb import *
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import native_cases as prior
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
STATE=0x20044d70;BASE=0x0807d000;ARG=0x2004f000
OPS=['init','begin','commit','getter','export','authorize','tick','invalidate','complete','fail','raw_start','parser_reset']
def fragments():
    result={}
    for idx,name in enumerate(OPS):
        base=BASE+idx*0x180;a=Asm(base)
        def emit(fn,*args,**kw):a.emit(fn,*args,**kw)
        def raw16(x):emit(raw,h(x))
        def cond(label,c):emit(b_cond,label,c)
        def m(rd,x):emit(movs_imm,rd,x)
        def load(rd,rn,off=0):emit(ldr_imm,rd,rn,off)
        def store(rd,rn,off=0):emit(str_imm,rd,rn,off)
        def cmpi(r,x):emit(cmp_imm,r,x)
        def cmpr(r,s):emit(cmp_reg,r,s)
        def mov(r,s):emit(mov_reg,r,s)
        def barrier():emit(raw,h(0xf3bf)+h(0x8f5f))
        def phase(rd=5):load(rd,0);m(4,7);raw16(0x4000|(4<<3)|rd) # ANDS rd,r4
        def setphase(p):
            load(5,0);m(4,7);raw16(0x4380|(4<<3)|5);m(4,p);emit(orrs_reg,5,4);store(5,0)
        emit(push_list,[0,1,2,3,4,5,6,7],lr=True)
        emit(raw,h(0xf3ef)+h(0x8700));emit(raw,h(0xf3ef)+h(0x8610));raw16(0xb672)
        if name=='init':
            load(4,1);cmpr(4,0);cond('out','eq');cmpr(4,3);cond('out','ne');cmpr(2,0);cond('out','hi')
            m(4,0);store(4,0);store(4,0,4);store(4,0,8);barrier();store(0,1)
        elif name=='begin':
            load(4,0);cmpi(4,0);cond('bad','ne');m(4,0x16);store(4,0);emit(b,'out')
            a.label('bad');setphase(13) # FAILED plus unexpected-event flag
        elif name=='commit':
            load(4,0);cmpi(4,0x16);cond('out','ne');store(1,0,4);store(2,0,8);barrier();m(4,0x11);store(4,0)
        elif name=='export':
            load(4,0);cmpi(4,0x11);cond('ok','eq');cmpi(4,0x12);cond('out','ne');a.label('ok')
            load(4,0,4);store(4,1);load(4,0,8);store(4,1,4);m(4,0x12);store(4,0)
        elif name=='authorize':
            # R1 token: epoch, exact geometry low/high, session, starttick.
            load(4,0);cmpi(4,0x12);cond('out','ne');load(4,1);cmpi(4,1);cond('out','ne')
            load(4,0,4);load(5,1,4);cmpr(4,5);cond('out','ne');load(4,0,8);load(5,1,8);cmpr(4,5);cond('out','ne')
            load(5,1,12);cmpi(5,1);cond('out','lo');cmpi(5,127);cond('out','hi')
            raw16((8<<6)|(5<<3)|5) # LSLS r5,r5,#8
            m(4,1);raw16((24<<6)|(4<<3)|4);emit(orrs_reg,5,4);m(4,2);emit(orrs_reg,5,4)
            store(5,0,4);load(4,1,16);store(4,0,8);barrier();m(4,0x13);store(4,0)
        elif name=='tick':
            phase();cmpi(5,3);cond('out','ne');load(4,0,8)
            raw16(0x1a00|(4<<6)|(1<<3)|5) # SUBS r5,r1,r4
            cmpr(5,2);cond('out','lo');setphase(5)
        elif name in ('invalidate','fail'):
            setphase(13 if name=='invalidate' else 5)
        elif name=='complete':
            phase();cmpi(5,3);cond('out','ne');m(4,0);emit(strb_imm,4,0,7);barrier();setphase(4)
        elif name=='raw_start':
            load(4,0);cmpi(4,0x13);cond('out','ne');cmpi(1,1);cond('out','ne')
            emit(ldrb_imm,4,0,4);cmpi(4,2);cond('out','ne');load(4,2);emit(adds_imm8,4,1);store(4,2)
        # getter/parser-reset intentionally never write the owned record.
        a.label('out');emit(raw,h(0xf386)+h(0x8810));emit(raw,h(0xf387)+h(0x8c00));emit(pop_list,[0,1,2,3,4,5,6,7],pc=True)
        code=a.assemble()[0];assert len(code)<0x180
        result[name]=(base,code)
    return result

class Native:
    def __init__(self,code):
        self.e=prior.Physical();self.u=self.e.uc;self.code=code;self.writes=[]
        for name,(base,b) in code.items():self.u.mem_write(base,b)
        self.u.mem_write(STATE-4,b'LEFT');self.u.mem_write(STATE+12,b'RIGH');self.u.mem_write(STATE,bytes(12))
        def hook(u,access,a,n,v,d):self.writes.append(dict(pc=hex(u.reg_read(UC_ARM_REG_PC)),address=hex(a),size=n,value=hex(v)))
        self.u.hook_add(UC_HOOK_MEM_WRITE,hook,begin=STATE-4,end=STATE+15)
    def call(self,name,*args,mask=0):
        u=self.u
        for i in range(13):u.reg_write(UC_ARM_REG_R0+i,0x1010101*i)
        for i,v in enumerate((STATE,*args)):u.reg_write(UC_ARM_REG_R0+i,v)
        u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_APSR,0xa8000000)
        regs=[u.reg_read(UC_ARM_REG_R0+i) for i in range(13)];flags=u.reg_read(UC_ARM_REG_APSR)
        self.e.call(self.code[name][0],STATE,*args,sp=0x2004fff8)
        assert [u.reg_read(UC_ARM_REG_R0+i) for i in range(13)]==regs and u.reg_read(UC_ARM_REG_APSR)==flags and u.reg_read(UC_ARM_REG_PRIMASK)==mask
        assert bytes(u.mem_read(STATE-4,4))==b'LEFT' and bytes(u.mem_read(STATE+12,4))==b'RIGH'
        return bytes(u.mem_read(STATE,12))
    def word(self):return self.e.r32(STATE)

def main():
    code=fragments();sys.path.insert(0,str(ROOT/'builds/phase56-geometry-snapshot-lifecycle'))
    from compact import decode,encode,fields
    native_mount=json.loads((OUT/'irq-inventory.json').read_text())['snapshots'][-1]
    captured=bytes.fromhex(native_mount['geometry_record_hex']);packed=encode(fields(captured));decode(packed)
    low,high=struct.unpack('<II',packed);rows=[]
    def mounted():
        n=Native(code);n.e.w32(ARG,0x20044e58);n.call('init',ARG,STATE-8,0x20044e58);assert n.e.r32(ARG)==STATE
        n.call('begin');n.call('commit',low,high);assert n.word()==0x11;return n
    for mask in (0,1):
        n=mounted();before=bytes(n.u.mem_read(STATE,12))
        for op,args in [('init',(ARG,STATE-8,0x20044e58)),('getter',()),('parser_reset',()),('tick',(0xffffffff,5000))]:
            assert n.call(op,*args,mask=mask)==before
        n.call('export',ARG+64,mask=mask);assert bytes(n.u.mem_read(ARG+64,8))==packed
        n.u.mem_write(ARG+128,struct.pack('<5I',1,low,high,37,0xfffffff0))
        assert bytes(n.u.mem_read(STATE+4,8))==packed
        n.call('authorize',ARG+128,mask=mask);assert n.word()==0x13
        n.e.w32(ARG+200,0);n.call('raw_start',1,ARG+200);assert n.e.r32(ARG+200)==1
        n.call('tick',(0xfffffff0+4999)&0xffffffff,5000);assert n.word()==0x13
        n.call('tick',(0xfffffff0+5000)&0xffffffff,5000);assert n.word()==0x15 and n.u.mem_read(STATE+7,1)[0]==1
        frozen=bytes(n.u.mem_read(STATE,12));n.call('complete');assert bytes(n.u.mem_read(STATE,12))==frozen
        n.call('authorize',ARG+128);n.call('raw_start',1,ARG+200);assert n.e.r32(ARG+200)==1
        rows.append(dict(case='export-authorize-wrap-timeout-late-success',initial_mask=mask,passed=True,write_intents=n.writes))
    for at in ('before-export','after-export','after-authorization'):
        n=mounted()
        if at!='before-export':n.call('export',ARG+64)
        n.u.mem_write(ARG+128,struct.pack('<5I',1,low,high,37,100))
        if at=='after-authorization':n.call('authorize',ARG+128)
        n.call('invalidate');frozen=bytes(n.u.mem_read(STATE,12));n.call('export',ARG+64);n.call('authorize',ARG+128)
        n.e.w32(ARG+200,0);n.call('raw_start',1,ARG+200);n.call('complete')
        assert bytes(n.u.mem_read(STATE,12))==frozen and n.e.r32(ARG+200)==0
        rows.append(dict(case='invalidate-'+at,passed=True))
    for kind in ('wrong-epoch','wrong-low','wrong-high','zero-session','large-session'):
        n=mounted();n.call('export',ARG+64);tok=[1,low,high,37,100]
        if kind=='wrong-epoch':tok[0]=2
        elif kind=='wrong-low':tok[1]^=1
        elif kind=='wrong-high':tok[2]^=1
        elif kind=='zero-session':tok[3]=0
        else:tok[3]=128
        n.u.mem_write(ARG+128,struct.pack('<5I',*tok));before=bytes(n.u.mem_read(STATE,12));n.call('authorize',ARG+128)
        assert bytes(n.u.mem_read(STATE,12))==before;rows.append(dict(case=kind,passed=True))
    n=mounted();n.call('export',ARG+64);n.u.mem_write(ARG+128,struct.pack('<5I',1,low,high,37,100));n.call('authorize',ARG+128);n.call('complete');assert n.word()==0x14
    n.call('authorize',ARG+128);assert n.word()==0x14;rows.append(dict(case='normal-terminal-one-shot',passed=True))
    sys.path.insert(0,str(ROOT/'builds/phase57-first-mount-provenance'))
    from first_epoch_model import State
    comparisons=[]
    for timeout in (False,True):
        n=Native(code);s=State();n.e.w32(ARG,0x20044e58)
        events=[('init',(ARG,STATE-8,0x20044e58)),('begin',()),('commit',(low,high)),('getter',()),('parser_reset',()),('export',(ARG+64,)),('tick',(1234,5000)),('authorize',(ARG+128,)),('raw_start',(1,ARG+200)),('tick',((0xfffffff0+(5000 if timeout else 4999))&0xffffffff,5000)),('complete',())]
        token=None;n.u.mem_write(ARG+128,struct.pack('<5I',1,low,high,37,0xfffffff0));n.e.w32(ARG+200,0)
        for op,args in events:
            got=n.call(op,*args)
            if op=='init':assert s.reserve()
            elif op=='begin':assert s.first_mount()
            elif op=='commit':assert s.commit(packed)
            elif op=='export':token=s.export()
            elif op=='authorize':assert s.authorize(token,now=0xfffffff0)
            elif op=='tick':s.tick(args[0])
            elif op=='complete':s.complete()
            assert got==bytes(s.r),(op,got.hex(),s.r.hex())
            comparisons.append(dict(timeout=timeout,event=op,state_hex=got.hex(),independent_oracle_equal=True))
    for name,(base,b) in code.items():(OUT/f'owner-{name}.asm').write_text('\n'.join(f'{i.address:08X}: {i.mnemonic} {i.op_str}' for i in prior.source.md.disasm(b,base))+'\n')
    r=dict(confidence='PROVEN',scope='Emulator-only native owner semantics and caller ABI, not installed call-site adapters or whole-image DMA/range-write closure',layout='control32 + geometry64, overlay only after exact-byte epoch1 authorization',state_bytes=12,geometry_hex=packed.hex(),cases=rows,oracle_comparisons=comparisons,fragments={k:dict(address=hex(a),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for k,(a,b) in code.items()},all_cases_passed=True,actual_old_owner_call_sites_replaced=False,full_lifetime_closed=False,code_persisted_as_binary=False)
    r.update(native_mount_record_hex=captured.hex(),geometry_source='Phase60 native successful mount at0801AE06 under Phase59 synthetic-BPB model',native_pack_or_capture_hook_installed=False)
    (OUT/'owner-model-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(cases=len(rows),native_owner_model=True,call_site_adapters=False)))
if __name__=='__main__':main()
