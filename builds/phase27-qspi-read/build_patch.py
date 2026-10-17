"""Build only an ARM fragment + exact patch plan. NOT YET HARDWARE-APPROVED.
Never emits an application image/SYX, invokes an uploader or opens a device.
"""
from pathlib import Path
import sys,json,struct
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'plaits/poc/authentic_qualification'))
from environment import REF,PUBLISHED,MAN,sha,STOCK
sys.path.insert(0,str(REF/'tools'))
from thumb import *
import ct_fw
from protocol import request,ADDRESS,SIZE,PAD,CMD
HOOK=0x0801eb30; ROUTER=0x08020c90; READ=0x08022f94
PROLOGUE=bytes.fromhex('2de9f041');BASE=0x08010000+len(PUBLISHED)
def arm_code():
 a=Asm(BASE);serial=[0]
 def imm(r,v):a.emit(movw,r,v&65535);a.emit(movt,r,v>>16)
 def bc(label,cond):
  inv={'eq':'ne','ne':'eq','hi':'ls','lo':'hs','hs':'lo','ls':'hi'}[cond]
  serial[0]+=1;n='skip'+str(serial[0]);a.emit(b_cond,n,inv);a.emit(b_w,label);a.label(n)
 def ptr(r,offset=32):a.emit(mov_reg,r,7);a.emit(adds_imm8,r,offset)
 def byte(offset,expected,label='return'):
  a.emit(mov_reg,0,4);a.emit(adds_imm8,0,offset);a.emit(ldrb_imm,1,0,0);a.emit(cmp_imm,1,expected);bc(label,'ne')
 a.label('entry');a.emit(push_list,[0,1,2,4,5,6,7],lr=True)
 a.emit(mov_reg,6,0);a.emit(ldr_imm,4,1,0);a.emit(ldr_imm,5,1,4)
 a.emit(cmp_imm,5,4);bc('forward','lo')
 for i,v in enumerate(b'\xf0\x7dCT'):byte(i,v,'forward')
 a.emit(cmp_imm,5,PAD);bc('return','ne');a.emit(cmp_imm,6,1);bc('return','hi')
 # A synchronous DMA wait is forbidden from exception/interrupt context.
 a.emit(raw,h(0xf3ef)+h(0x8005));a.emit(cmp_imm,0,0);bc('return','ne')
 a.emit(ldrb_imm,0,4,5);a.emit(cmp_imm,0,127);bc('return','hi')
 # Exact request only: no address/length/write values decoded into arguments.
 for i,v in enumerate(request(0)[4:23],4):
  if i!=5:byte(i,v)
 a.emit(mov_reg,0,4);a.emit(adds_imm8,0,23);a.emit(movs_imm,2,208)
 a.label('padding');a.emit(ldrb_imm,1,0,0);a.emit(cmp_imm,1,0);bc('return','ne')
 a.emit(adds_imm8,0,1);a.emit(subs_imm8,2,1);a.emit(b_cond,'padding','ne')
 a.emit(ldrb_imm,1,0,0);a.emit(cmp_imm,1,247);bc('return','ne')
 a.emit(bl,'command')
 a.label('return');a.emit(pop_list,[0,1,2,4,5,6,7],pc=True)
 a.label('forward');a.emit(raw,h(0xe8bd)+h(0x40f7));a.emit(raw,PROLOGUE);a.emit(b_w,HOOK+4)
 a.label('command');a.emit(push_list,[4,5,6,7],lr=True);a.emit(sub_sp_imm,508);a.emit(sub_sp_imm,40);a.emit(mov_reg,7,13)
 imm(0,0x20006968);a.emit(ldr_imm,0,0,0);a.emit(cmp_imm,0,0);bc('finish','eq')
 a.emit(ldr_imm,0,0,4);a.emit(cmp_imm,0,0);bc('finish','eq');a.emit(ldr_imm,1,0,0)
 imm(2,0x0805b1ac);a.emit(cmp_reg,1,2);bc('finish','ne')
 # Admit only the observed stock completion callback. The generic event
 # dispatcher otherwise permits additional indirect callback targets.
 a.emit(ldr_imm,1,0,4);a.emit(mov_reg,2,1);a.emit(adds_imm8,2,32)
 a.emit(ldrb_imm,3,2,4);a.emit(cmp_imm,3,1);bc('finish','ne')
 a.emit(ldr_imm,3,2,8);imm(2,0x08057651);a.emit(cmp_reg,3,2);bc('finish','ne')
 imm(1,ADDRESS);ptr(2);imm(3,SIZE);a.emit(bl,READ)
 a.emit(cmp_imm,0,0);bc('finish','ne')
 ptr(0);imm(1,SIZE);a.emit(bl,'crc');a.emit(str_imm,0,7,12)
 a.emit(movs_imm,5,0)
 a.label('packet');a.emit(movs_imm,0,CMD|64);a.emit(strb_imm,0,4,4)
 a.emit(movs_imm,0,0);a.emit(cmp_imm,5,8);a.emit(b_cond,'kind_ready','ne');a.emit(movs_imm,0,1)
 a.label('kind_ready');a.emit(strb_imm,0,4,6);a.emit(strb_imm,5,4,7)
 imm(1,ADDRESS);a.emit(cmp_imm,5,8);a.emit(b_cond,'addr_ready','eq')
 a.emit(lsls_imm,0,5,6);a.emit(adds_reg,1,1,0)
 a.label('addr_ready');a.emit(mov_reg,0,4);a.emit(adds_imm8,0,8);a.emit(bl,'p32')
 imm(1,SIZE);a.emit(bl,'p32')
 a.emit(movs_imm,1,64);a.emit(cmp_imm,5,8);a.emit(b_cond,'n_ready','ne');a.emit(movs_imm,1,4)
 a.label('n_ready');a.emit(strb_imm,1,0,0);a.emit(adds_imm8,0,1)
 a.emit(cmp_imm,5,8);a.emit(b_cond,'complete','eq')
 ptr(1);a.emit(lsls_imm,2,5,6);a.emit(adds_reg,1,1,2);a.emit(movs_imm,2,64);a.emit(bl,'pbytes');a.emit(b,'packet_crc')
 a.label('complete');a.emit(ldr_imm,1,7,12);a.emit(bl,'p32')
 a.label('packet_crc');a.emit(str_imm,0,7,16);a.emit(mov_reg,1,4);a.emit(adds_imm8,1,4);a.emit(subs_reg,1,0,1)
 a.emit(mov_reg,0,4);a.emit(adds_imm8,0,4);a.emit(bl,'crc');a.emit(mov_reg,1,0);a.emit(ldr_imm,0,7,16);a.emit(bl,'p32')
 a.emit(movs_imm,1,247);a.emit(strb_imm,1,0,0);a.emit(adds_imm8,0,1);a.emit(subs_reg,0,0,4)
 a.emit(str_imm,4,7,0);a.emit(str_imm,0,7,4)
 router_ptr=struct.unpack('<I',PUBLISHED[0x1edd0-0x10000:0x1edd4-0x10000])[0]
 imm(0,router_ptr);a.emit(ldr_imm,0,0,0);a.emit(movs_imm,1,1);a.emit(raw,h(0x40b1));a.emit(mov_reg,2,7);a.emit(bl,ROUTER)
 a.emit(adds_imm8,5,1);a.emit(cmp_imm,5,9);bc('packet','lo')
 a.label('finish');a.emit(add_sp_imm,40);a.emit(add_sp_imm,508);a.emit(pop_list,[4,5,6,7],pc=True)
 a.label('p32');a.emit(movs_imm,2,8)
 a.label('p32_loop');a.emit(lsrs_imm,3,1,28);a.emit(strb_imm,3,0,0);a.emit(adds_imm8,0,1);a.emit(lsls_imm,1,1,4);a.emit(subs_imm8,2,1);a.emit(b_cond,'p32_loop','ne');a.emit(bx_lr)
 a.label('pbytes');a.emit(ldrb_imm,3,1,0);a.emit(mov_reg,12,3);a.emit(lsrs_imm,3,3,4);a.emit(strb_imm,3,0,0)
 a.emit(mov_reg,3,12);a.emit(lsls_imm,3,3,28);a.emit(lsrs_imm,3,3,28);a.emit(strb_imm,3,0,1)
 a.emit(adds_imm8,0,2);a.emit(adds_imm8,1,1);a.emit(subs_imm8,2,1);a.emit(b_cond,'pbytes','ne');a.emit(bx_lr)
 a.label('crc');a.emit(push_list,[4,5,6],lr=True);imm(4,0x04c11db7);imm(6,0xffffffff)
 a.label('crc_byte');a.emit(ldrb_imm,3,0,0);a.emit(adds_imm8,0,1);a.emit(lsls_imm,3,3,24);a.emit(eors_reg,6,3);a.emit(movs_imm,5,8)
 a.label('crc_bit');a.emit(lsls_imm,6,6,1);a.emit(b_cond,'crc_no_xor','cc');a.emit(eors_reg,6,4)
 a.label('crc_no_xor');a.emit(subs_imm8,5,1);a.emit(b_cond,'crc_bit','ne');a.emit(subs_imm8,1,1);a.emit(b_cond,'crc_byte','ne')
 a.emit(mov_reg,0,6);a.emit(pop_list,[4,5,6],pc=True)
 return a.assemble()
def build():
 assert PUBLISHED[HOOK-0x08010000:HOOK-0x08010000+4]==PROLOGUE
 code,labels=arm_code();end=BASE+len(code);assert BASE%4==0 and end<=0x08080000
 from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
 md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);ins=list(md.disasm(code,BASE));assert sum(i.size for i in ins)==len(code)
 (O/'arm-diagnostic.fragment.bin').write_bytes(code)
 (O/'arm-diagnostic.asm').write_text('\n'.join(f'{i.address:08x}: {i.mnemonic:9} {i.op_str}' for i in ins)+'\n')
 patch=b_w(HOOK,labels['entry'])
 marker_before=PUBLISHED[0x1e8:0x1ec];assert marker_before==b'B1.3'
 # Validate original packaging algorithms with existing bytes, without a new image.
 original=b''.join(c for _,c in PUBLISHED.parts)
 assert sha(original)==MAN['image_sha256'] and ct_fw.crc32_mpeg2(original)==int(MAN['crc32'],16)
 assert ct_fw.crc32_mpeg2(STOCK)==ct_fw.STOCK_4486['crc']
 plan=dict(status='NOT YET HARDWARE-APPROVED',base_B13_sha256=PUBLISHED.hash,base_B13_size=len(PUBLISHED),
  hook=dict(address=hex(HOOK),before=PROLOGUE.hex(),after=patch.hex(),bytes=4),
  installation_marker=dict(address='0x080101e8',before=marker_before.hex(),after=b'Q27R'.hex(),bytes=4,reason='Version-block must differ for a later normal bootloader installation; plan only'),
  append=dict(start=hex(BASE),end_exclusive=hex(end),bytes=len(code),sha256=sha(code)),
  total_patch_bytes=8+len(code),labels={n:hex(v) for n,v in labels.items()},
  application_base='0x08010000',physical_end='0x08080000',bootloader_patch_bytes=0,DSP_patch_bytes=0,
  stack_frame_bytes=548,own_max_stack_bytes=616,
  candidate_image_generated=False,candidate_SYX_generated=False,candidate_build_sha256=None,
  original_B13_CRC_matches=True,original_stock_CRC_matches=True)
 (O/'patch-plan.json').write_text(json.dumps(plan,indent=2)+'\n');return plan
if __name__=='__main__':print(json.dumps(build(),indent=2))
