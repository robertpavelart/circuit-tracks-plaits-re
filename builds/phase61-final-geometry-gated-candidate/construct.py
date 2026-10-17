"""Pinned offline construction. No hardware/transport imports. New artifacts only.

Native emitters are deliberately explicit; tests consume independently decoded
SYX bytes, not these Python functions as the implementation under test.
"""
from pathlib import Path
import sys,json,hashlib,struct
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
P=R/'builds/phase42-exact-rdiag-integration';S=R/'builds/phase43-hardware-test-candidate'
sys.path.insert(0,str(P/'source/tools'))
from thumb import *
BASE=0x08010000;SREC=0x20044d70;LIMIT=0x20002b44;TICK=0x2000081c
START=0x0806bd00
NAMES=['init','getter','watch','begin','snapshot','register','slow','binding','stride','invalidate','entry','export','authorize','raw','complete','fail','drain','crc','n32','bytes','packet_crc','un32']
L={n:START+0x600*i for i,n in enumerate(NAMES)}
assert max(L.values())<0x08078000
def sha(b):return hashlib.sha256(b).hexdigest()
def imm(a,r,v):a.emit(movw,r,v&65535);a.emit(movt,r,v>>16)
def ret(a):a.emit(bx_lr)
def save(a,mask=True):
 a.emit(raw,h(0xe92d)+h(0x50ff));a.emit(raw,h(0xf3ef)+h(0x8610));a.emit(raw,h(0xf3ef)+h(0x8700));a.emit(push_list,[6,7])
 if mask:a.emit(raw,h(0xb672))
def restore(a):
 a.emit(pop_list,[6,7]);a.emit(raw,h(0xf386)+h(0x8810));a.emit(raw,h(0xf387)+h(0x8c00));a.emit(raw,h(0xe8bd)+h(0x90ff))
def check(a,cond,target):
 # Conditional far branch with local inverted skip.
 inv={'eq':'ne','ne':'eq','hi':'ls','ls':'hi','lo':'hs','hs':'lo','mi':'pl','pl':'mi'}[cond]
 label='skip'+str(len(a.items));a.emit(b_cond,label,inv);a.emit(b_w,target);a.label(label)
def control(a,r=4):imm(a,r,SREC)
def failstore(a,r=4):a.emit(movs_imm,5,0x1d);a.emit(str_imm,5,r,0)
def finish(a):a.label('out');restore(a)

def build_ops():
 out={}
 a=Asm(L['init']);save(a);imm(a,0,LIMIT);a.emit(ldr_imm,1,0,0);imm(a,2,SREC);a.emit(cmp_reg,1,2);check(a,'eq','out')
 imm(a,3,0x20044e58);a.emit(cmp_reg,1,3);check(a,'ne','out');a.emit(ldr_imm,1,0,4);a.emit(cmp_reg,1,2);check(a,'hi','out')
 a.emit(movs_imm,1,0)
 for k in (0,4,8):a.emit(str_imm,1,2,k)
 a.emit(raw,h(0xf3bf)+h(0x8f5f));a.emit(str_imm,2,0,0);finish(a);out['init']=a.assemble()[0]
 a=Asm(L['getter']);imm(a,0,0x20044d7c);imm(a,1,LIMIT);a.emit(ldr_imm,1,1,0);imm(a,2,SREC);a.emit(cmp_reg,1,2);a.emit(b_cond,'off','ne')
 a.emit(ldr_imm,1,0,0);imm(a,2,0x6f1d0c14);a.emit(cmp_reg,1,2);a.emit(b_cond,'ok','eq');a.emit(b_w,0x0805dc06)
 a.label('ok');ret(a);a.label('off');a.emit(movs_imm,0,0);ret(a);out['getter']=a.assemble()[0]
 a=Asm(L['watch']);a.emit(push_list,[0,1,2,3,4],lr=True);a.emit(bl,0x080599b8);control(a);a.emit(ldr_imm,1,4,0);a.emit(cmp_imm,1,0x13);a.emit(b_cond,'out','ne')
 imm(a,0,TICK);a.emit(ldr_imm,0,0,0);a.emit(ldr_imm,2,4,8);a.emit(subs_reg,0,0,2);imm(a,2,5000);a.emit(cmp_reg,0,2);a.emit(b_cond,'out','lo');a.emit(movs_imm,0,0x15);a.emit(str_imm,0,4,0)
 a.label('out');a.emit(pop_list,[0,1,2,3,4],pc=True);out['watch']=a.assemble()[0]
 a=Asm(L['invalidate']);save(a);control(a);failstore(a);finish(a);out['invalidate']=a.assemble()[0]
 a=Asm(L['begin']);save(a);control(a);a.emit(ldr_imm,0,4,0);a.emit(cmp_imm,0,0);a.emit(b_cond,'bad','ne');a.emit(movs_imm,0,0x16);a.emit(str_imm,0,4,0);a.emit(b,'out');a.label('bad');failstore(a);finish(a);out['begin']=a.assemble()[0]
 # Registration of drive0 is valid only from our first explicit mount wrapper.
 a=Asm(L['register']);save(a);a.emit(ldrb_imm,2,1,0);a.emit(cmp_imm,2,48);a.emit(b_cond,'out','ne');control(a);a.emit(ldr_imm,2,4,0);a.emit(cmp_imm,2,0x16);a.emit(b_cond,'bad','ne');imm(a,2,0x0801ae07);a.emit(ldr_sp,0,52);a.emit(cmp_reg,0,2);a.emit(b_cond,'out','eq');a.label('bad');failstore(a);finish(a);out['register']=a.assemble()[0]
 # Slow mount is allowed only while the first disk0 mount is in progress.
 a=Asm(L['slow']);save(a);imm(a,0,0x20000ab0);a.emit(cmp_reg,4,0);a.emit(b_cond,'out','ne');control(a);a.emit(ldr_imm,0,4,0);a.emit(cmp_imm,0,0x16);a.emit(b_cond,'out','eq');failstore(a);finish(a);out['slow']=a.assemble()[0]
 for name,reg,target in [('binding',0,0x20000aa0),('stride',1,0x20000a98)]:
  a=Asm(L[name]);save(a);imm(a,2,target);a.emit(cmp_reg,reg,2);a.emit(b_cond,'out','ne');control(a);a.emit(ldr_imm,2,4,0);a.emit(cmp_imm,2,0);a.emit(b_cond,'out','eq')
  if name=='stride':
   a.emit(cmp_imm,2,0x16);a.emit(b_cond,'bad','ne');imm(a,2,4096);a.emit(cmp_reg,0,2);a.emit(b_cond,'out','eq');a.label('bad')
  failstore(a);finish(a);out[name]=a.assemble()[0]
 # Snapshot: no calls, allocations, Storage or NOR; compact scalars are checked
 # before they are shifted into a 57-bit record. Host separately validates domains.
 a=Asm(L['snapshot']);save(a);control(a);a.emit(ldr_imm,1,4,0);a.emit(cmp_imm,1,0x16);check(a,'ne','out');a.emit(cmp_imm,0,0);check(a,'ne','bad')
 imm(a,7,0x20000a98)
 for off,val in [(0,0xd4000),(4,4096)]:
  a.emit(ldr_imm,0,7,off);imm(a,1,val);a.emit(cmp_reg,0,1);check(a,'ne','bad')
 imm(a,7,0x20000ab0);a.emit(ldrb_imm,0,7,1);a.emit(cmp_imm,0,0);check(a,'ne','bad')
 a.emit(ldrh_imm,0,7,12);imm(a,1,4096);a.emit(cmp_reg,0,1);check(a,'ne','bad')
 imm(a,0,0x20005e5c);a.emit(ldr_imm,0,0,0);a.emit(cmp_reg,0,7);check(a,'ne','bad')
 # Binding must be to the actual NOR wrapper and fixed geometry object.
 imm(a,0,0x20000aa0);a.emit(ldr_imm,1,0,4);imm(a,2,0x20006968);a.emit(ldr_imm,2,2,0);a.emit(cmp_reg,1,2);check(a,'ne','bad')
 a.emit(ldr_imm,1,0,8);imm(a,2,0x20000a98);a.emit(cmp_reg,1,2);check(a,'ne','bad')
 a.emit(movs_imm,5,0);a.emit(movs_imm,6,0)
 for off,shift in [(44,0),(36,13),(52,26),(32,39)]:
  a.emit(ldr_imm,0,7,off);imm(a,1,8191);a.emit(cmp_reg,0,1);check(a,'hi','bad')
  if shift<32:
   a.emit(lsls_imm,1,0,shift);a.emit(orrs_reg,5,1)
   if shift:a.emit(lsrs_imm,1,0,32-shift);a.emit(orrs_reg,6,1)
  else:a.emit(lsls_imm,1,0,shift-32);a.emit(orrs_reg,6,1)
 # root == fat + nfats*fatsz; bounded factors/type.
 a.emit(ldrb_imm,0,7,2);a.emit(cmp_imm,0,1);check(a,'lo','bad');a.emit(cmp_imm,0,2);check(a,'hi','bad');a.emit(subs_imm8,0,1);a.emit(lsls_imm,1,0,23);a.emit(orrs_reg,6,1)
 a.emit(adds_imm8,0,1);a.emit(ldr_imm,1,7,36);a.emit(raw,h(0x4348));a.emit(ldr_imm,1,7,44);a.emit(adds_reg,0,0,1);a.emit(ldr_imm,1,7,48);a.emit(cmp_reg,0,1);check(a,'ne','bad')
 a.emit(ldrb_imm,0,7,0);a.emit(cmp_imm,0,1);check(a,'lo','bad');a.emit(cmp_imm,0,2);check(a,'hi','bad');a.emit(subs_imm8,0,1);a.emit(lsls_imm,0,0,24);a.emit(orrs_reg,6,0)
 a.emit(ldrh_imm,0,7,10);a.emit(movs_imm,1,0)
 a.label('factor');a.emit(cmp_imm,0,1);a.emit(b_cond,'factor_ok','eq');a.emit(movs_imm,2,1);a.emit(tst_reg,0,2);check(a,'ne','bad');a.emit(lsrs_imm,0,0,1);a.emit(adds_imm8,1,1);a.emit(cmp_imm,1,7);check(a,'hi','bad');a.emit(b,'factor')
 a.label('factor_ok');a.emit(lsls_imm,1,1,20);a.emit(orrs_reg,6,1)
 a.emit(str_imm,5,4,4);a.emit(str_imm,6,4,8);a.emit(raw,h(0xf3bf)+h(0x8f5f));a.emit(movs_imm,0,0x11);a.emit(str_imm,0,4,0);a.emit(b,'out');a.label('bad');failstore(a);finish(a);out['snapshot']=a.assemble()[0]
 for name in ('complete','fail'):
  a=Asm(L[name]);save(a);control(a);a.emit(ldr_imm,0,4,0);a.emit(cmp_imm,0,0x13);a.emit(b_cond,'out','ne')
  if name=='complete':a.emit(movs_imm,0,0);a.emit(strb_imm,0,4,7)
  a.emit(movs_imm,0,0x14 if name=='complete' else 0x15);a.emit(str_imm,0,4,0);finish(a);out[name]=a.assemble()[0]
 return out

def protocol_ops():
 out={}
 # Commands use fixed 232B stock parser ownership; only command14 and15 are new.
 a=Asm(L['entry']);a.emit(push_list,[0,1,2,3,4,5,6,7],lr=True);a.emit(sub_sp_imm,4)
 a.emit(ldr_imm,4,1,0);a.emit(ldr_imm,5,1,4);a.emit(cmp_imm,5,8);check(a,'lo','forward')
 for i,v in enumerate(b'\xf0\x7dCT'):a.emit(ldrb_imm,3,4,i);a.emit(cmp_imm,3,v);check(a,'ne','forward')
 a.emit(cmp_imm,0,0);check(a,'ne','out');a.emit(cmp_imm,5,232);check(a,'ne','out')
 imm(a,2,0x20000000);a.emit(cmp_reg,4,2);check(a,'lo','out');a.emit(mov_reg,3,4);a.emit(adds_imm8,3,232);imm(a,2,0x20010000);a.emit(cmp_reg,3,2);check(a,'hi','out')
 a.emit(ldrb_imm,3,4,5);a.emit(cmp_imm,3,1);check(a,'lo','out');a.emit(cmp_imm,3,127);check(a,'hi','out')
 a.emit(ldrb_imm,3,4,4);a.emit(cmp_imm,3,14);a.emit(b_cond,'geometry','eq');a.emit(cmp_imm,3,15);check(a,'ne','out');a.emit(movs_imm,6,31);a.emit(b,'padding');a.label('geometry');a.emit(movs_imm,6,6)
 a.label('padding');a.emit(mov_reg,2,4);a.emit(adds_reg,2,2,6);a.emit(movs_imm,3,231);a.emit(subs_reg,3,3,6)
 a.label('pad');a.emit(ldrb_imm,1,2,0);a.emit(cmp_imm,1,0);check(a,'ne','out');a.emit(adds_imm8,2,1);a.emit(subs_imm8,3,1);a.emit(b_cond,'pad','ne');a.emit(ldrb_imm,1,2,0);a.emit(cmp_imm,1,247);check(a,'ne','out')
 a.emit(ldrb_imm,3,4,4);a.emit(cmp_imm,3,14);a.emit(b_cond,'do_export','eq');a.emit(bl,L['authorize']);a.emit(cmp_imm,0,1);check(a,'ne','out');a.emit(movs_imm,6,0);a.emit(bl,L['raw']);a.emit(b,'out');a.label('do_export');a.emit(bl,L['export'])
 a.label('out');a.emit(add_sp_imm,4);a.emit(pop_list,[0,1,2,3,4,5,6,7],pc=True)
 a.label('forward');a.emit(add_sp_imm,4);a.emit(raw,h(0xe8bd)+h(0x40ff));a.emit(raw,bytes.fromhex('2de9f041'));a.emit(b_w,0x0801eb34);out['entry']=a.assemble()[0]
 # Bounded nibble decoder: R1 advances; R0 result or FFFFFFFF for invalid.
 a=Asm(L['un32']);a.emit(push_list,[2,3],lr=True);a.emit(movs_imm,0,0);a.emit(movs_imm,2,8)
 a.label('next');a.emit(ldrb_imm,3,1,0);a.emit(cmp_imm,3,15);a.emit(b_cond,'bad','hi');a.emit(lsls_imm,0,0,4);a.emit(orrs_reg,0,3);a.emit(adds_imm8,1,1);a.emit(subs_imm8,2,1);a.emit(b_cond,'next','ne');a.emit(pop_list,[2,3],pc=True);a.label('bad');imm(a,0,0xffffffff);a.emit(pop_list,[2,3],pc=True);out['un32']=a.assemble()[0]
 a=Asm(L['authorize']);a.emit(push_list,[4,5,6,7],lr=True);a.emit(sub_sp_imm,4);a.emit(raw,h(0xf3ef)+h(0x8710));a.emit(raw,h(0xb672));control(a,6);a.emit(ldrb_imm,1,4,5);a.emit(lsls_imm,1,1,25);a.emit(movs_imm,0,0x12);a.emit(orrs_reg,1,0);a.emit(ldr_imm,0,6,0);a.emit(cmp_reg,0,1);check(a,'ne','reject')
 a.emit(ldrb_imm,5,4,6);a.emit(cmp_imm,5,2);a.emit(b_cond,'mask_ok','eq');a.emit(cmp_imm,5,3);check(a,'ne','reject');a.label('mask_ok')
 a.emit(mov_reg,1,4);a.emit(adds_imm8,1,7);a.emit(bl,L['un32']);a.emit(cmp_imm,0,1);check(a,'ne','reject')
 for off in (4,8):a.emit(bl,L['un32']);a.emit(ldr_imm,2,6,off);a.emit(cmp_reg,0,2);check(a,'ne','reject')
 # All input consumed before active publication. Geometry remains live up to here.
 a.emit(ldrb_imm,0,4,5);a.emit(lsls_imm,0,0,8);a.emit(orrs_reg,0,5);a.emit(str_imm,0,6,4);imm(a,0,TICK);a.emit(ldr_imm,0,0,0);a.emit(str_imm,0,6,8);a.emit(movs_imm,0,0x13);a.emit(str_imm,0,6,0);a.emit(movs_imm,0,1);a.emit(b,'out')
 a.label('reject');a.emit(movs_imm,0,0);a.label('out');a.emit(raw,h(0xf387)+h(0x8810));a.emit(add_sp_imm,4);a.emit(pop_list,[4,5,6,7],pc=True);out['authorize']=a.assemble()[0]
 # Geometry response: F0 7D CT 4E session epoch32 low32 high32 CRC32 F7.
 a=Asm(L['export']);a.emit(push_list,[4,5,6,7],lr=True);a.emit(sub_sp_imm,52);a.emit(mov_reg,7,13);a.emit(mov_reg,5,4);a.emit(mov_reg,4,7);a.emit(adds_imm8,4,8)
 a.emit(raw,h(0xf3ef)+h(0x8310));a.emit(str_sp,3,48);a.emit(raw,h(0xb672));control(a,6);a.emit(ldr_imm,0,6,0);a.emit(cmp_imm,0,0x11);a.emit(b_cond,'reject','ne')
 for i,v in enumerate(b'\xf0\x7dCT\x4e'):a.emit(movs_imm,0,v);a.emit(strb_imm,0,4,i)
 a.emit(ldrb_imm,0,5,5);a.emit(strb_imm,0,4,5);a.emit(mov_reg,0,4);a.emit(adds_imm8,0,6);a.emit(movs_imm,1,1);a.emit(bl,L['n32'])
 for off in (4,8):a.emit(ldr_imm,1,6,off);a.emit(bl,L['n32'])
 a.emit(mov_reg,5,0);a.emit(ldrb_imm,1,4,5);a.emit(lsls_imm,1,1,25);a.emit(movs_imm,0,0x12);a.emit(orrs_reg,1,0);a.emit(str_imm,1,6,0);a.emit(ldr_sp,3,48);a.emit(raw,h(0xf383)+h(0x8810));a.emit(mov_reg,0,4);a.emit(adds_imm8,0,4);a.emit(movs_imm,1,26);a.emit(bl,L['packet_crc']);a.emit(mov_reg,1,0);a.emit(mov_reg,0,5);a.emit(bl,L['n32']);a.emit(movs_imm,1,247);a.emit(strb_imm,1,0,0)
 a.emit(bl,L['drain']);a.emit(cmp_imm,0,0);a.emit(b_cond,'failed','ne');a.emit(str_imm,4,7,0);a.emit(movs_imm,0,39);a.emit(str_imm,0,7,4);imm(a,0,0x200069f4);a.emit(ldr_imm,0,0,0);a.emit(movs_imm,1,1);a.emit(mov_reg,2,7);a.emit(bl,0x08020c90);a.emit(bl,L['drain']);a.emit(cmp_imm,0,0);a.emit(b_cond,'out','eq')
 a.label('failed');a.emit(bl,L['invalidate']);a.emit(b,'out');a.label('reject');a.emit(ldr_sp,3,48);a.emit(raw,h(0xf383)+h(0x8810));a.label('out');a.emit(add_sp_imm,52);a.emit(pop_list,[4,5,6,7],pc=True);out['export']=a.assemble()[0]
 return out

def streaming():
 src=(R/'builds/phase41-fixed-nor-diagnostic/stream.py').read_text();src=src[:src.index('\ndef load(u):')]
 src=src.replace('from environment import *','from pathlib import Path')
 src=src.replace("sys.path.insert(0,str(REF/'tools'));from thumb import *",'from thumb import *')
 for old,key in [('0x0807b000','raw'),('0x0807b600','crc'),('0x0807b800','drain'),('0x0807a6de','n32'),('0x0807a6ee','bytes'),('0x0807a708','packet_crc')]:src=src.replace(old,hex(L[key]))
 src=src.replace('FRAME=188;RAW=32;PACKET=16;GUARDS=(12,180)','FRAME=260;RAW=192;PACKET=16;GUARDS=(12,180)')
 src=src.replace("a.emit(ldrb_imm,5,4,5);a.emit(mov_reg,6,4)","imm(a,0,STATE);a.emit(ldrb_imm,5,0,5);a.emit(mov_reg,6,7)")
 src=src.replace("a.label('chunk')", "a.label('chunk');imm(a,0,STATE);a.emit(ldr_imm,1,0,0);a.emit(cmp_imm,1,0x13);a.emit(b_cond,'live','eq');a.emit(b_w,'finish');a.label('live');a.emit(ldrb_imm,1,0,4);a.emit(cmp_imm,5,0);a.emit(b_cond,'allowed','ne');a.emit(cmp_imm,1,3);a.emit(b_cond,'allowed','eq');a.emit(adds_imm8,5,1);a.label('allowed');a.emit(strb_imm,5,0,6);a.emit(movs_imm,1,1);a.emit(strb_imm,1,0,7)")
 src=src.replace("a.label('read_ok')", "a.label('read_ok');imm(a,0,STATE);a.emit(ldr_imm,1,0,0);a.emit(cmp_imm,1,0x13);a.emit(b_cond,'reply','eq');a.emit(b_w,'finish');a.label('reply');a.emit(movs_imm,1,2);a.emit(strb_imm,1,0,7)")
 # Coeff-only transfer uses the established nine-index protocol with identity
 # omitted: index1..8 plus completion9; total=512, base=82000.
 src=src.replace("imm(a,1,535)","a.emit(bl,'total')")
 # Completion base conditional on explicit mask, never host-supplied address.
 src=src.replace("imm(a,1,0x81000);a.emit(bl,"+hex(L['n32'])+")", "imm(a,1,0x81000);imm(a,2,STATE);a.emit(ldrb_imm,2,2,4);a.emit(cmp_imm,2,3);a.emit(b_cond,'cb','eq');imm(a,1,0x82000);a.label('cb');a.emit(bl,"+hex(L['n32'])+")")
 src=src.replace("a.emit(ldr_imm,1,7,8);a.emit(bl,"+hex(L['n32'])+");a.emit(bl,'send')", "a.emit(ldr_imm,1,7,8);a.emit(bl,"+hex(L['n32'])+");a.emit(bl,'send');a.emit(cmp_imm,0,0);a.emit(b_cond,'finish','ne');a.emit(bl,COMPLETE)")
 start=src.index(" # Restore the complete original fixed request")
 end=src.index(" a.emit(add_sp_imm,FRAME)",start)
 src=src[:start]+" a.emit(bl,FAIL)\n"+src[end:]
 # Bound USB drain by ACTIVE lifecycle, also works for preauth geometry export.
 src=src.replace("a.label('poll');", "a.label('poll');imm(a,0,STATE);a.emit(ldr_imm,0,0,0);a.emit(cmp_imm,0,0x15);a.emit(b_cond,'disconnected','eq');a.emit(cmp_imm,0,0x1d);a.emit(b_cond,'disconnected','eq');")
 src=src.replace(" return a.assemble()[0]\ndef crc_update", " a.label('total');imm(a,1,512);imm(a,2,STATE);a.emit(ldrb_imm,2,2,4);a.emit(cmp_imm,2,3);a.emit(b_cond,'totalret','ne');imm(a,1,535);a.label('totalret');a.emit(bx_lr)\n return a.assemble()[0]\ndef crc_update")
 ns=dict(globals(),__file__=str(O/'stream.py'),STATE=SREC,COMPLETE=L['complete'],FAIL=L['fail'])
 (O/'stream-generated-emitter.txt').write_text(src)
 exec(compile(src,str(O/'stream-generated-emitter.py'),'exec'),ns)
 return dict(raw=ns['command'](),drain=ns['drain'](),crc=ns['crc_update']()),src

def main():
 pins=json.loads((P/'inputs.json').read_text())
 for x in pins['sources']:assert sha(Path(x['local']).read_bytes())==x['sha256']
 clean=(S/'clean-sc35d8.bin').read_bytes();assert sha(clean)=='1525c6662bbff9ced7e6055bb54e864615c30013f1b4dec4be6c404f8c750c05'
 components=build_ops()|protocol_ops();stream,src=streaming();components.update(stream)
 codec=(R/'builds/phase27-qspi-read/arm-diagnostic.fragment.bin').read_bytes()[0x2ca:];assert len(codec)==88
 components.update(n32=codec[:16],bytes=codec[16:42],packet_crc=codec[42:])
 # Relocated original instructions are emitted explicitly with no PC-relative
 # literals copied blindly. Entry trampolines retain LR/original tail semantics.
 tramp={};at=0x08075000
 def wrap(name,operation,original,back):
  nonlocal at
  a=Asm(at);a.emit(push_list,[0],lr=True);a.emit(bl,L[operation]);a.emit(raw,h(0xe8bd)+h(0x4001));a.emit(raw,original);a.emit(b_w,back);b=a.assemble()[0];tramp[name]=(at,b);at=(at+len(b)+3)&~3;return tramp[name][0]
 patches={}
 def patch(address,b):patches[address]=b
 # init is a function-entry branch: BL to init then original push+mov.
 patch(0x0805b958,b_w(0x0805b958,wrap('ctor','init',bytes.fromhex('10b50446'),0x0805b95c)))
 # Begin before native registration; preserve the native AE06 return address so
 # the registration adapter can prove this is the expected outer mount.
 a=Asm(at);a.emit(push_list,[0,1,2,3],lr=True);a.emit(sub_sp_imm,4);a.emit(bl,L['begin']);a.emit(add_sp_imm,4);a.emit(raw,h(0xe8bd)+h(0x400f));a.emit(b_w,0x08019a92);tramp['mount_begin']=(at,a.assemble()[0]);patch(0x0801ae02,bl(0x0801ae02,at));at+=0x40
 patch(0x08019a92,b_w(0x08019a92,wrap('registration','register',bytes.fromhex('13b582b0'),0x08019a96)))
 patch(0x080197ec,b_w(0x080197ec,wrap('slow_mount','slow',bytes.fromhex('00212170'),0x080197f0)))
 patch(0x0801ae3a,b_w(0x0801ae3a,wrap('binding','binding',bytes.fromhex('41600168'),0x0801ae3e)))
 # stride original has a short branch; reconstruct with absolute tail.
 patch(0x0801aede,b_w(0x0801aede,wrap('stride','stride',str_imm(0,1,4),0x0801aeee)))
 a=Asm(at);a.emit(push_list,[0],lr=True);a.emit(bl,L['snapshot']);a.emit(raw,h(0xe8bd)+h(0x4001));a.emit(movs_imm,1,0); # overwritten below: MOVS R1,R0, flags required
 a.items[-1]=('ins',(raw,(h(0x0001),),{}));a.emit(b_cond,'ok','eq');imm(a,0,0x0801af58);a.emit(b_w,0x0801ae14);a.label('ok');a.emit(ldrb_imm,1,4,12);imm(a,0,0x0801af68);a.emit(b_w,0x0801ae14)
 tramp['snapshot_return']=(at,a.assemble()[0]);patch(0x0801ae06,b_w(0x0801ae06,at));at+=0x60
 for address,name in [(0x0806b6cc,'getter'),(0x0806b748,'watch'),(0x0806b798,'entry'),(0x0806b850,'raw'),(0x0806bc46,'complete')]:patch(address,b_w(address,L[name]))
 patch(0x0805dbcc,b_w(0x0805dbcc,0x0806b6cc));patch(0x0805998e,bl(0x0805998e,0x0806b748));patch(0x0801eb30,b_w(0x0801eb30,0x0806b798))
 # Retain already qualified task/IRQ ownership fixes from Phase42.
 patch(0x080213aa,b_w(0x080213aa,0x0806b3c6));patch(0x0805ac9c,(0x0806b589).to_bytes(4,'little'));patch(0x080101e8,b'N61GEO')
 end=(at+3)&~3;image=bytearray(clean);image.extend(b'\xff'*(end-(BASE+len(image))))
 # Erase obsolete diagnostic bodies; only the five explicit redirected entries
 # remain. This also removes all old overlapping stores and raw read bypasses.
 image[0x5b6cc:0x5bc8c]=b'\xff'*(0x5bc8c-0x5b6cc)
 for name,b in components.items():
  assert len(b)<=0x600,(name,len(b));pos=L[name]-BASE;image[pos:pos+len(b)]=b
 for _,(pos,b) in tramp.items():image[pos-BASE:pos-BASE+len(b)]=b
 hooklist=[]
 for pos,b in patches.items():hooklist.append(dict(address=hex(pos),before=clean[pos-BASE:pos-BASE+len(b)].hex(),after=b.hex()));image[pos-BASE:pos-BASE+len(b)]=b
 assert len(image)<=0x70000
 import ct_fw
 image=bytes(image);syx=ct_fw.encode(image);assert ct_fw.decode(syx)['image']==image
 # Construction output is not designated final until all admission gates pass.
 name='circuittracks-final-geometry-gated-nor-test'
 (O/(name+'.bin')).write_bytes(image);(O/(name+'.syx')).write_bytes(syx)
 (O/'stream-generated-emitter.txt').write_text(src)
 from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
 md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
 for name,b in components.items():(O/(name+'.asm')).write_text('\n'.join(f'{i.address:08X}: {i.mnemonic} {i.op_str}' for i in md.disasm(b,L[name]))+'\n')
 for name,(pos,b) in tramp.items():(O/(name+'.asm')).write_text('\n'.join(f'{i.address:08X}: {i.mnemonic} {i.op_str}' for i in md.disasm(b,pos))+'\n')
 result=dict(confidence='PROVEN',designation='CONSTRUCTION OUTPUT — NOT APPROVED FOR HARDWARE',name=name,source_sha256=sha(clean),pinned_source_files=len(pins['sources']),BIN_bytes=len(image),BIN_sha256=sha(image),SYX_bytes=len(syx),SYX_sha256=sha(syx),CRC=hex(ct_fw.crc32_mpeg2(image)),application_end=hex(BASE+len(image)),headroom=0x70000-len(image),layout={k:hex(v) for k,v in L.items()},components={k:dict(address=hex(L[k]),bytes=len(b),sha256=sha(b)) for k,b in components.items()},trampolines={k:dict(address=hex(pos),bytes=len(b),sha256=sha(b)) for k,(pos,b) in tramp.items()},patches=hooklist,hardware_access=False)
 (O/'construction.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('layout','components','trampolines','patches')},indent=2))
if __name__=='__main__':main()

