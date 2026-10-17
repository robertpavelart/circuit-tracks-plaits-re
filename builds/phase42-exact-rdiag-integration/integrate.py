"""Exact SC35D8 derivative, internal BIN only. No firmware encoder or device I/O."""
from pathlib import Path
import sys,json,hashlib,types
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(O/'source/tools'))
from thumb import *
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
BASE=0x08010000;POOL=0x0806b6cc;END=0x0806bc8c
STATE=0x20044d70;ST=0x20044d7c;LIMIT=0x20002b44;MAGIC=0x4e4f5234
GST=0x0805dbcc;TICK=0x2000081c
def sha(b):return hashlib.sha256(b).hexdigest()
def imm(a,r,v):a.emit(movw,r,v&65535);a.emit(movt,r,v>>16)
def popw(rs,lr=False):return h(0xe8bd)+h(sum(1<<r for r in rs)|(1<<14 if lr else 0))
def gst(base):
 a=Asm(base);imm(a,0,ST);imm(a,3,LIMIT);a.emit(ldr_imm,1,3,0);imm(a,2,STATE);a.emit(cmp_reg,1,2);a.emit(b_cond,'ready','eq')
 imm(a,2,0x20044e58);a.emit(cmp_reg,1,2);a.emit(b_cond,'off','ne');a.emit(ldr_imm,1,3,4);imm(a,2,STATE);a.emit(cmp_reg,1,2);a.emit(b_cond,'off','hi')
 a.emit(str_imm,2,3,0);a.emit(movs_imm,1,0)
 for k in (4,8):a.emit(str_imm,1,2,k)
 imm(a,1,MAGIC);a.emit(str_imm,1,2,0);a.emit(b_w,0x0805dc06)
 a.label('ready');imm(a,1,STATE);a.emit(ldr_imm,2,1,0);imm(a,3,MAGIC);a.emit(cmp_reg,2,3);a.emit(b_cond,'off','ne')
 a.emit(ldr_imm,1,0,0);imm(a,2,0x6f1d0c14);a.emit(cmp_reg,1,2);a.emit(b_cond,'ok','eq');a.emit(b_w,0x0805dc06)
 a.label('ok');a.emit(raw,h(0x4770))
 a.label('off');a.emit(movs_imm,0,0);a.emit(raw,h(0x4770));return a.assemble()[0]
def watch(base):
 a=Asm(base);a.emit(push_list,[0,1,2,3,4],lr=True);a.emit(bl,0x080599b8)
 imm(a,0,LIMIT);a.emit(ldr_imm,0,0,0);imm(a,1,STATE);a.emit(cmp_reg,0,1);a.emit(b_cond,'out','ne')
 a.emit(ldr_imm,0,1,0);imm(a,2,MAGIC);a.emit(cmp_reg,0,2);a.emit(b_cond,'out','ne')
 a.emit(ldrb_imm,0,1,4);a.emit(cmp_imm,0,1);a.emit(b_cond,'out','ne')
 imm(a,0,TICK);a.emit(ldr_imm,0,0,0);a.emit(ldr_imm,2,1,8);a.emit(subs_reg,0,0,2);imm(a,2,5000);a.emit(cmp_reg,0,2);a.emit(b_cond,'out','lo')
 a.emit(movs_imm,0,3);a.emit(strb_imm,0,1,4)
 a.label('out');a.emit(pop_list,[0,1,2,3,4],pc=True);return a.assemble()[0]
def entry(base,command):
 a=Asm(base);a.emit(push_list,[0,1,2,4,5,6,7],lr=True)
 a.emit(ldr_imm,4,1,0);a.emit(ldr_imm,5,1,4);a.emit(cmp_imm,5,8);a.emit(b_cond,'forward','lo')
 for i,v in enumerate(b'\xf0\x7dCT'):
  a.emit(ldrb_imm,3,4,i);a.emit(cmp_imm,3,v);a.emit(b_cond,'forward','ne')
 a.emit(cmp_imm,0,0);a.emit(b_cond,'out','ne');a.emit(cmp_imm,5,232);a.emit(b_cond,'out','ne')
 a.emit(ldrb_imm,3,4,4);a.emit(cmp_imm,3,13);a.emit(b_cond,'out','ne')
 imm(a,2,0x20000000);a.emit(cmp_reg,4,2);a.emit(b_cond,'out','lo');a.emit(mov_reg,3,4);a.emit(adds_imm8,3,232);imm(a,2,0x20010000);a.emit(cmp_reg,3,2);a.emit(b_cond,'out','hi')
 a.emit(lsls_imm,3,4,28);a.emit(cmp_imm,3,0);a.emit(b_cond,'out','ne')
 a.emit(mov_reg,2,4);a.emit(adds_imm8,2,6);a.emit(movs_imm,3,225)
 a.label('pad');a.emit(ldrb_imm,1,2,0);a.emit(cmp_imm,1,0);a.emit(b_cond,'out','ne');a.emit(adds_imm8,2,1);a.emit(subs_imm8,3,1);a.emit(b_cond,'pad','ne')
 a.emit(ldrb_imm,1,2,0);a.emit(cmp_imm,1,247);a.emit(b_cond,'out','ne')
 a.emit(bl,GST);a.emit(cmp_imm,0,0);a.emit(b_cond,'out','eq')
 # Admission is atomic even for an adversarial direct nested invocation.
 a.emit(raw,h(0xf3ef)+h(0x8210));a.emit(raw,h(0xb672));imm(a,3,STATE)
 a.emit(ldrb_imm,1,3,4);a.emit(cmp_imm,1,0);a.emit(b_cond,'restore','ne')
 a.emit(movs_imm,1,1);a.emit(strb_imm,1,3,4);a.emit(ldrb_imm,1,4,5);a.emit(strb_imm,1,3,5)
 imm(a,0,TICK);a.emit(ldr_imm,0,0,0);a.emit(str_imm,0,3,8)
 a.emit(raw,h(0xf382)+h(0x8810));a.emit(movs_imm,6,0);a.emit(bl,command);a.emit(b,'out')
 a.label('restore');a.emit(raw,h(0xf382)+h(0x8810))
 a.label('out');a.emit(pop_list,[0,1,2,4,5,6,7],pc=True)
 a.label('forward');a.emit(raw,popw([0,1,2,4,5,6,7],True));a.emit(raw,bytes.fromhex('2de9f041'));a.emit(b_w,0x0801eb34)
 return a.assemble()[0]
def factories(layout):
 # Preserve phase41 arithmetic/codec/Storage schedule; add ownership stores,
 # active checks and terminal transitions. Never import/run its evidence writer.
 src=(R/'builds/phase41-fixed-nor-diagnostic/stream.py').read_text()
 for old,key in [('0x0807b000','command'),('0x0807b600','crc'),('0x0807b800','drain'),('0x0807bc00','template'),('0x0807a6de','n32'),('0x0807a6ee','bytes'),('0x0807a708','packet_crc')]:src=src.replace(old,hex(layout[key]))
 src=src[:src.index('\ndef load(u):')]
 src=src.replace("a.emit(ldrb_imm,5,4,5)","imm(a,0,STATE);a.emit(ldrb_imm,5,0,5)",1)
 src=src.replace("a.label('chunk')", "a.label('chunk');imm(a,0,STATE);a.emit(ldrb_imm,1,0,4);a.emit(cmp_imm,1,1);a.emit(b_cond,'still_active','eq');a.emit(b_w,'finish');a.label('still_active');a.emit(strb_imm,5,0,6);a.emit(movs_imm,1,1);a.emit(strb_imm,1,0,7)")
 src=src.replace("a.label('read_ok')", "a.label('read_ok');imm(a,0,STATE);a.emit(ldrb_imm,1,0,4);a.emit(cmp_imm,1,1);a.emit(b_cond,'live_reply','eq');a.emit(b_w,'finish');a.label('live_reply');a.emit(movs_imm,1,2);a.emit(strb_imm,1,0,7)")
 src=src.replace("a.label('complete');", "a.label('complete');")
 src=src.replace("a.emit(ldr_imm,1,7,8);a.emit(bl,"+hex(layout['n32'])+");a.emit(bl,'send')", "a.emit(ldr_imm,1,7,8);a.emit(bl,"+hex(layout['n32'])+");a.emit(bl,'send');a.emit(cmp_imm,0,0);a.emit(b_cond,'finish','ne');imm(a,0,STATE);a.emit(ldrb_imm,1,0,4);a.emit(cmp_imm,1,1);a.emit(b_cond,'finish','ne');a.emit(movs_imm,1,2);a.emit(strb_imm,1,0,4)")
 src=src.replace("a.label('finish')", "a.label('finish');imm(a,0,STATE);a.emit(ldrb_imm,1,0,4);a.emit(cmp_imm,1,2);a.emit(b_cond,'terminal','eq');a.emit(movs_imm,1,3);a.emit(strb_imm,1,0,4);a.label('terminal');a.emit(movs_imm,1,0);a.emit(strb_imm,1,0,7)")
 ns={'__file__':str(O/'stream.py'),'STATE':STATE}
 exec(compile(src,str(O/'phase41_emitter_adapted.py'),'exec'),ns)
 return ns
def main():
 admission=json.loads((O/'reproduction.json').read_text());assert admission['all_match']
 old=(O/'rebuilt-sc35d8.bin').read_bytes();assert sha(old)==admission['expected']['image_sha256']
 # Two-pass fixed layout, word aligned. Branch encodings have stable widths.
 L={k:POOL for k in ('gst','watch','entry','command','crc','drain','n32','bytes','packet_crc','template')}
 for _ in range(3):
  ns=factories(L);chunks={'gst':gst(L['gst']),'watch':watch(L['watch']),'entry':entry(L['entry'],L['command']),'command':ns['command'](),'crc':ns['crc_update'](),'drain':ns['drain']()}
  codec=(R/'builds/phase27-qspi-read/arm-diagnostic.fragment.bin').read_bytes()[0x2ca:]
  chunks.update(n32=codec[:16],bytes=codec[16:42],packet_crc=codec[42:])
  from evidence_protocol import request
  chunks['template']=request(0);at=POOL;new={}
  for k,b in chunks.items():new[k]=at;at=(at+len(b)+3)&~3
  if L==new:break
  L=new
 else:raise AssertionError('layout did not converge')
 assert at<=END,(hex(at),hex(END))
 img=bytearray(old);img[POOL-BASE:END-BASE]=b'\xff'*(END-POOL)
 for k,b in chunks.items():img[L[k]-BASE:L[k]-BASE+len(b)]=b
 patches={0x0801eb30:b_w(0x0801eb30,L['entry']),GST:b_w(GST,L['gst']),0x0805998e:bl(0x0805998e,L['watch']),0x080213aa:b_w(0x080213aa,0x0806b3c6),0x0805ac9c:(0x0806b589).to_bytes(4,'little'),0x080101e8:b'N42ONE'}
 for a,b in patches.items():img[a-BASE:a-BASE+len(b)]=b
 image=bytes(img);assert image[:0x1e8]==old[:0x1e8] and len(image)==len(old)
 import ct_fw
 result=dict(confidence='PROVEN',base_image_sha256=sha(old),image_size=hex(len(image)),image_sha256=sha(image),crc32=hex(ct_fw.crc32_mpeg2(image)),layout={k:hex(v) for k,v in L.items()},components={k:dict(address=hex(L[k]),bytes=len(b),sha256=sha(b)) for k,b in chunks.items()},code_bytes=sum(len(b) for k,b in chunks.items() if k!='template'),constant_bytes=len(chunks['template']),pool_bytes=END-POOL,used_pool_bytes=at-POOL,hook_patches=[dict(address=hex(a),before=old[a-BASE:a-BASE+len(b)].hex(),after=b.hex()) for a,b in patches.items()],state=dict(base=hex(STATE),bytes=12,heap_limit_before=hex(ST),heap_limit_after=hex(STATE),heap_delta=12,fields={'0..3':'magic','4':'IDLE=0 ACTIVE=1 SUCCESS=2 FAILED_QUARANTINED=3','5':'session','6':'global chunk 0..9; region derived','7':'read-owner1 / reply-owner2 / free0','8..11':'start tick; 5000-tick quarantine'}),vector_changes=0,DSP_changes=0,bootloader_changes=0,option_byte_changes=0,SYX_generated=False)
 (O/'integrated-internal.bin').write_bytes(image);(O/'integration.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('components','hook_patches')},indent=2))
if __name__=='__main__':main()
