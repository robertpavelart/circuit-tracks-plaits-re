"""Read-only reference loading and provenance for authentic qualification."""
import base64,hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
OUT=ROOT/'builds/phase20i-authentic-qualification';OUT.mkdir(exist_ok=True)
sys.dont_write_bytecode=True;sys.path.insert(0,str(REF/'tools'))
def protect(event,args):
    if event=='open' and isinstance(args[0],(str,bytes)):
        p=os.path.abspath(os.fsdecode(args[0]))
        if p.lower().startswith(str(REF).lower()+os.sep):
            mode=args[1] or '';flags=args[2] or 0
            if any(x in str(mode) for x in ('w','a','+','x')) or flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_APPEND):raise RuntimeError('Reference write rejected: '+p)
sys.addaudithook(protect)
def sha(data):return hashlib.sha256(data).hexdigest()
STOCK=(REF/'stock/circuittracks-firmware-4486-STOCK.bin').read_bytes()
MAN=json.loads((REF/'firmware/b1.3/manifest.json').read_text())
class Published:
    """Slice existing published COPY/ADD spans without creating an image file."""
    def __init__(self):
        line=next(l for l in (REF/'tools/rc_uploader.html').read_text(encoding='utf8').splitlines() if l.startswith('const PATCHES = '))
        self.parts=[];cursor=0;h=hashlib.sha256()
        for op in json.loads(line[len('const PATCHES = '):].rstrip(';'))['B1.3']['ops']:
            chunk=STOCK[op[1]:op[1]+op[2]] if op[0]==0 else base64.b64decode(op[1]);self.parts.append((cursor,chunk));cursor+=len(chunk);h.update(chunk)
        self.length=cursor;self.hash=h.hexdigest();assert self.hash==MAN['image_sha256'];assert self.length==int(MAN['image_size'],16)
    def __len__(self):return self.length
    def __getitem__(self,k):
        assert isinstance(k,slice)
        a,b,step=k.indices(self.length);assert step==1
        return b''.join(chunk[max(a-at,0):min(b-at,len(chunk))] for at,chunk in self.parts if at<b and at+len(chunk)>a)
PUBLISHED=Published()
def authentic_session():
    import dsp_session as DS
    OriginalE=DS.E
    class PublishedE(OriginalE):
        def __init__(self,img):
            assert img is PUBLISHED
            super().__init__(STOCK)
            for at,chunk in PUBLISHED.parts:self.uc.mem_write(0x08010000+at,chunk)
        def call(self,fn,*args,**kw):
            from unicorn.arm_const import UC_ARM_REG_PC
            ret=super().call(fn,*args,**kw)
            assert self.uc.reg_read(UC_ARM_REG_PC)==0x0807ff00,('ARM call did not return',hex(fn),hex(self.uc.reg_read(UC_ARM_REG_PC)))
            return ret
    DS.E=PublishedE
    try:s=DS.Session(PUBLISHED)
    finally:DS.E=OriginalE
    return s
def provenance():
    import capstone,unicorn
    assert capstone.__version__=='5.0.7' and unicorn.__version__=='2.1.4'
    files={}
    for p in (REF/'tools').rglob('*'):
        if p.is_file() and '__pycache__' not in str(p):files[str(p)]=sha(p.read_bytes())
    for p in [REF/'stock/circuittracks-firmware-4486-STOCK.bin',REF/'stock/circuittracks-firmware-4486-STOCK.syx',REF/'re/app.asm',REF/'ext/bin/dsptool.exe',REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin',REF/'ctre/Firmware-Analysis/ram_dump_firmware_0x08037988.bin',REF/'ext/dsp56300/source/dsp56kEmu/memory.cpp',REF/'ext/dsp56300/source/dsp56kEmu/memory.h']:
        files[str(p)]=sha(p.read_bytes())
    expected=['4f8ce3714e366d36ef668334aa92c194e95917b1','303437fcb2117b6d47b34df51409b0721f610db2'];dumps=[]
    for name,gitsha in zip(['dumpCT_flash_0x08000000.bin','ram_dump_firmware_0x08037988.bin'],expected):
        p=REF/'ctre/Firmware-Analysis'/name;b=p.read_bytes();blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();assert blob==gitsha
        dumps.append(dict(path=str(p),source='https://github.com/userx14/circuittracksreverseengineering',commit='d6aec9fc9d975d65f54ed5ca16c096227e6974ab',size=len(b),sha256=sha(b),git_blob_sha1=blob,confidence='PROVEN'))
    # Reproduce listing text in memory, with pinned Capstone; no reference write.
    md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB|capstone.CS_MODE_MCLASS);md.skipdata=True
    listing=''.join(f'{i.address:08x}: {i.mnemonic:<8} {i.op_str}'.rstrip()+'\n' for i in md.disasm(STOCK,0x08010000))
    actual=(REF/'re/app.asm').read_text();assert actual==listing,'Installed listing differs from verified stock disassembly'
    fl=(REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin').read_bytes()
    result=dict(dumps=dumps,stock_sha256=sha(STOCK),stock_size=len(STOCK),stock_matches_dump_application=fl[0x10000:0x10000+len(STOCK)]==STOCK,B13_image_sha256=PUBLISHED.hash,B13_image_size=len(PUBLISHED),B13_syx_manifest_sha256=MAN['syx_sha256'],listing_text_matches=True,capstone=capstone.__version__,unicorn=unicorn.__version__,dsptool_sha256=files[str(REF/'ext/bin/dsptool.exe')],DSP_commit=(REF/'ext/dsp56300/.git/HEAD').read_text().strip(),reference_before=files)
    (OUT/'provenance.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=provenance();print(json.dumps({k:v for k,v in r.items() if k!='reference_before'},indent=2))
