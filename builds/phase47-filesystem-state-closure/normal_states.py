"""Offline normal FAT16 scenarios using authenticated mounted geometry.

Directory sectors are coherent minimal models, not a dump of the user's NOR.
Native FatFs and settings producer execute; physical block completions and
content service boundaries are modeled. No transport, firmware output or hardware.
"""
from pathlib import Path
import sys,struct,json,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import native_cases as old
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
FS=0x20000ab0
def entry(name,attr,cluster,size=0):
    r=bytearray(32);r[:11]=name;r[11]=attr
    struct.pack_into('<H',r,26,cluster);struct.pack_into('<I',r,28,size);return r
class Model:
    def __init__(self,size=128,present=True):
        self.e=old.Physical();self.u=self.e.uc;self.u.mem_write(0x08010000,old.source.app)
        self.writes=[];self.reads=[];self.sectors={};self.status=[];self.present=present;self.size=size
        # Keep authenticated mounted FAT16 geometry; invalidate only window cache.
        self.e.w32(FS+0x38,0xffffffff);self.u.mem_write(FS+3,b'\0')
        fat=bytearray(4*4096);struct.pack_into('<HHHHH',fat,0,0xfff8,0xffff,0xffff,0xffff,0xffff if present else 0)
        for start in (1,5):
            for k in range(4):self.sectors[start+k]=bytearray(fat[k*4096:(k+1)*4096])
        root=bytearray(4096);root[:32]=entry(b'TRACKS     ',0x10,2);self.sectors[9]=root
        tracks=bytearray(4096);tracks[:32]=entry(b'.          ',0x10,2);tracks[32:64]=entry(b'..         ',0x10,0)
        tracks[64:96]=entry(b'GLOBALS    ',0x10,3);self.sectors[13]=tracks
        glob=bytearray(4096)
        glob[:32]=entry(b'.          ',0x10,3);glob[32:64]=entry(b'..         ',0x10,2)
        if present:glob[64:96]=entry(b'00_GLOB CG ',0x20,4,size)
        self.sectors[14]=glob;self.sectors[15]=bytearray(4096)
        self.path=0x20022000;self.fil=0x20024000
        self.u.mem_write(self.path,b'0:/Tracks/Globals/00_GLOB.cg\0')
        self.u.hook_add(UC_HOOK_CODE,self.hook)
    def hook(self,u,pc,n,d):
        e=self.e
        if pc==0x0801a75c:old.ret(e,0)
        elif pc==0x0801a796:
            lba=u.reg_read(UC_ARM_REG_R2);count=u.reg_read(UC_ARM_REG_R3);buf=u.reg_read(UC_ARM_REG_R1)
            self.reads.append([lba,count]);u.mem_write(buf,b''.join(bytes(self.sectors.get(k,bytearray(4096))) for k in range(lba,lba+count)));old.ret(e)
        elif pc==0x08024164:
            a=u.reg_read(UC_ARM_REG_R1);buf=u.reg_read(UC_ARM_REG_R2);length=u.reg_read(UC_ARM_REG_R3)
            assert a>=0xd4000 and (a-0xd4000)%4096==0 and length%4096==0
            lba=(a-0xd4000)//4096
            self.writes.append(dict(start=hex(a),end=hex(a+length),length=length,lba=lba,
                kind='FAT WRITE' if 1<=lba<9 else 'DIRECTORY WRITE' if lba in (9,14) else 'DIRECT DATA WRITE',
                erase_first_requested=e.r32(u.reg_read(UC_ARM_REG_SP)),
                identity_overlap=a<0x81017 and a+length>0x81000,
                coefficients_overlap=a<0x82200 and a+length>0x82000))
            data=bytes(u.mem_read(buf,length))
            for k in range(length//4096):self.sectors[lba+k]=bytearray(data[k*4096:(k+1)*4096])
            old.ret(e,0)
        elif pc==0x0801a7c2:old.ret(e,0) # disk CTRL_SYNC completion, no invented array write
    def call(self,fn,*args):
        r=self.e.call(fn,*args,maxins=500000);self.status.append([hex(fn),r]);return r
    def open(self,mode=0x13):
        self.u.mem_write(self.fil,b'\0'*0x1028)
        return self.call(0x08019ae4,self.fil,self.path,mode)
    def unlink(self):return self.call(0x0801a440,self.path)
    def write128(self):
        assert self.open()==0
        payload=bytearray(self.u.mem_read(0x20039754,128));payload[0]=1
        self.u.mem_write(0x20039754,bytes(payload))
        assert self.call(0x0802d108,0x2003974c)==1
        self.u.mem_write(0x20028000,bytes(payload))
        assert self.call(0x08019e50,self.fil,0x20028000,128,0x20029000)==0
        assert self.call(0x0801a09a,self.fil)==0
    def result(self,name):
        assert not any(w['identity_overlap'] or w['coefficients_overlap'] for w in self.writes)
        return dict(name=name,scope='Coherent normal FAT16 directory model on authenticated fixture geometry; not actual unit directory allocation',
            status=self.status,reads=self.reads,writes=self.writes,physical_completion='modeled at NOR wrapper24164',
            identity_touched=False,coefficients_touched=False)
    def startup(self):
        obj=0x2003974c;payload=bytes(self.sectors[15][:128]);exists=self.present
        size=self.size if exists else 0
        # Native file read validates the modeled directory/chain before supplying
        # content-service responses to the real startup producer.
        assert self.open(1)==(0 if exists else 4)
        if exists:
            assert self.call(0x08019cc6,self.fil,0x20028000,min(size,128),0x20029000)==0
            payload=bytes(self.u.mem_read(0x20028000,min(size,128)))
            assert self.call(0x0801a09a,self.fil)==0
        events=[];validators=[]
        def content(u,pc,n,d):
            if pc==0x0802d108:validators.append('native0802D108')
            if pc==0x0803c9ca:events.append('SIZE');old.ret(self.e,size)
            elif pc==0x0803c8d4:
                events.append('READ');u.mem_write(u.reg_read(UC_ARM_REG_R3),payload);old.ret(self.e)
            elif pc==0x0803c97a:events.append('DELETE_AND_FLUSH');old.ret(self.e)
            elif pc==0x08035756:old.ret(self.e,0) # hardware configuration query seam
        h=self.u.hook_add(UC_HOOK_CODE,content)
        self.call(0x0802d060,obj)
        self.u.hook_del(h)
        if 'DELETE_AND_FLUSH' in events:assert self.unlink()==0
        assert ('DELETE_AND_FLUSH' in events)==(exists and size!=128 and size!=0)
        if size==128:assert validators==['native0802D108']
        return dict(events=events,size=size,validator_entries=validators,content_boundary='Native FAT read/delete executed before/after producer; no RTOS queue replay',
            validation='Actual native0802D108; no forced validation result',
            payload_source='Authenticated settings RAM snapshot for valid state; rejected-size scenario does not claim firmware origin')
def main():
    rows=[]
    for name,size,present,op in [('clean-valid',128,True,'none'),('missing-settings',0,False,'none'),
        ('ordinary-dirty-settings',128,True,'write'),('ordinary-file-deletion',128,True,'delete')]:
        m=Model(size,present)
        if op=='delete':assert m.unlink()==0
        elif op=='write':m.write128()
        else:
            assert m.open(1)==(0 if present else 4)
            if present:assert m.call(0x0801a09a,m.fil)==0
        rows.append(m.result(name))
    startup=[]
    for name,size,present in [('valid-settings',128,True),('missing-settings',0,False)]:
        m=Model(size,present)
        if size==128:m.sectors[15][:128]=bytes(m.u.mem_read(0x20039754,128))
        run=m.startup();startup.append(m.result(name)|dict(startup=run))
    m=Model(0,False)
    assert m.open()==0
    assert m.call(0x0801a09a,m.fil)==0
    m.present=True;m.size=0
    startup.append(m.result('native-created-empty-settings')|dict(startup=m.startup()))
    e=old.Physical();extrema=[]
    for cl in range(2,e.r32(FS+0x20)):
        lba=e.call(0x08018698,FS,cl);assert 13<=lba<=0x1f2b
        extrema.append(lba)
    result=dict(confidence='PROVEN',scope='Normal geometry and native file operations; not complete user-unit boot replay',
        cluster_mapping_count=len(extrema),min_lba=min(extrema),max_lba=max(extrema),cases=rows,startup=startup)
    (OUT/'normal-states.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
