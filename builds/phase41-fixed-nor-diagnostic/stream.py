"""In-memory-only chunked ARM prototype. No firmware/fragment/SYX is written.
Main retains a real stack frame while stock synchronous wrapper yields.
"""
from environment import *
O=Path(__file__).resolve().parent
sys.path.insert(0,str(REF/'tools'));from thumb import *
COMMAND=0x0807b000;CRC_UPDATE=0x0807b600;DRAIN=0x0807b800;TEMPLATE=0x0807bc00
FRAME=188;RAW=32;PACKET=16;GUARDS=(12,180)
def imm(a,r,v):a.emit(movw,r,v&65535);a.emit(movt,r,v>>16)
def command():
 a=Asm(COMMAND);a.emit(cmp_imm,6,0);a.emit(b_cond,'usb','eq');a.emit(bx_lr);a.label('usb')
 a.emit(push_list,[4,5,6,7],lr=True);a.emit(sub_sp_imm,FRAME);a.emit(mov_reg,7,13)
 # Input token captured from the validated live stock SysEx buffer.
 a.emit(ldrb_imm,5,4,5);a.emit(mov_reg,6,4);a.emit(adds_imm8,6,RAW);a.emit(mov_reg,4,7);a.emit(adds_imm8,4,PACKET)
 for i,v in enumerate(b'\xf0\x7dCT\x4d'):
  a.emit(movs_imm,0,v);a.emit(strb_imm,0,4,i)
 a.emit(strb_imm,5,4,5);imm(a,0,0xffffffff);a.emit(str_imm,0,7,8)
 # Explicit low-register pointer for offsets beyond the T1 STR range.
 for off in GUARDS:
  imm(a,0,0x30ca0000+off);a.emit(mov_reg,1,7);a.emit(adds_imm8,1,off);a.emit(str_imm,0,1,0)
 for off in (-4,64):
  imm(a,0,0x30ca0000+RAW+off);a.emit(mov_reg,1,6)
  a.emit(subs_imm8 if off<0 else adds_imm8,1,abs(off));a.emit(str_imm,0,1,0)
 a.emit(movs_imm,5,0)
 a.label('chunk')
 a.emit(cmp_imm,5,0);a.emit(b_cond,'not_identity','ne');imm(a,0,0x81000);a.emit(movs_imm,2,23);a.emit(b,'addr_ready');a.label('not_identity');a.emit(mov_reg,1,5);a.emit(subs_imm8,1,1);a.emit(lsls_imm,1,1,6);imm(a,0,0x82000);a.emit(adds_reg,0,0,1);a.emit(movs_imm,2,64);a.label('addr_ready')
 a.emit(mov_reg,1,6)
 a.emit(bl,0x08047c6c);a.emit(cmp_imm,0,0);a.emit(b_cond,'read_ok','eq');a.emit(b_w,'finish');a.label('read_ok')
 # Incremental MPEG-2 CRC, exactly over each completed raw chunk before reuse.
 a.emit(movs_imm,1,64);a.emit(cmp_imm,5,0);a.emit(b_cond,'crc_len','ne');a.emit(movs_imm,1,23);a.label('crc_len');a.emit(mov_reg,0,6);a.emit(ldr_imm,2,7,8)
 a.emit(bl,CRC_UPDATE);a.emit(str_imm,0,7,8)
 a.emit(movs_imm,0,0);a.emit(cmp_imm,5,0);a.emit(b_cond,'region_kind','eq');a.emit(movs_imm,0,1);a.label('region_kind');a.emit(strb_imm,0,4,6);a.emit(strb_imm,5,4,7)
 imm(a,1,0x81000);a.emit(cmp_imm,5,0);a.emit(b_cond,'meta_addr','eq');a.emit(mov_reg,0,5);a.emit(subs_imm8,0,1);a.emit(lsls_imm,0,0,6);imm(a,1,0x82000);a.emit(adds_reg,1,1,0);a.label('meta_addr')
 a.emit(mov_reg,0,4);a.emit(adds_imm8,0,8);a.emit(bl,0x0807a6de);imm(a,1,535);a.emit(bl,0x0807a6de)
 a.emit(movs_imm,1,64);a.emit(cmp_imm,5,0);a.emit(b_cond,'meta_len','ne');a.emit(movs_imm,1,23);a.label('meta_len');a.emit(strb_imm,1,0,0);a.emit(adds_imm8,0,1)
 a.emit(movs_imm,2,64);a.emit(cmp_imm,5,0);a.emit(b_cond,'encode_len','ne');a.emit(movs_imm,2,23);a.label('encode_len');a.emit(mov_reg,1,6);a.emit(bl,0x0807a6ee)
 a.emit(bl,'send');a.emit(cmp_imm,0,0);a.emit(b_cond,'sent','eq');a.emit(b_w,'finish');a.label('sent')
 a.emit(adds_imm8,5,1);a.emit(cmp_imm,5,9);a.emit(b_cond,'complete','hs');a.emit(b_w,'chunk')
 a.label('complete');a.emit(movs_imm,0,2);a.emit(strb_imm,0,4,6);a.emit(movs_imm,0,9);a.emit(strb_imm,0,4,7)
 a.emit(mov_reg,0,4);a.emit(adds_imm8,0,8);imm(a,1,0x81000);a.emit(bl,0x0807a6de)
 imm(a,1,535);a.emit(bl,0x0807a6de);a.emit(movs_imm,1,4);a.emit(strb_imm,1,0,0);a.emit(adds_imm8,0,1)
 a.emit(ldr_imm,1,7,8);a.emit(bl,0x0807a6de);a.emit(bl,'send')
 a.label('finish')
 # Restore the complete original fixed request before other stock callbacks
 # see the shared SysEx buffer. Token is the only variable request field.
 a.emit(ldrb_imm,5,4,5);a.emit(mov_reg,0,6);a.emit(subs_imm8,0,RAW)
 imm(a,1,TEMPLATE);a.emit(movs_imm,2,232)
 a.label('restore');a.emit(ldrb_imm,3,1,0);a.emit(strb_imm,3,0,0)
 a.emit(adds_imm8,0,1);a.emit(adds_imm8,1,1);a.emit(subs_imm8,2,1);a.emit(b_cond,'restore','ne')
 a.emit(mov_reg,0,6);a.emit(subs_imm8,0,RAW);a.emit(strb_imm,5,0,5)
 a.emit(add_sp_imm,FRAME);a.emit(pop_list,[4,5,6,7],pc=True)
 a.label('send');a.emit(push_list,[6],lr=True)
 a.emit(mov_reg,6,0);a.emit(mov_reg,1,4);a.emit(adds_imm8,1,4);a.emit(subs_reg,1,0,1)
 a.emit(mov_reg,0,4);a.emit(adds_imm8,0,4);a.emit(bl,0x0807a708)
 a.emit(mov_reg,1,0);a.emit(mov_reg,0,6);a.emit(bl,0x0807a6de)
 a.emit(movs_imm,1,247);a.emit(strb_imm,1,0,0);a.emit(adds_imm8,0,1);a.emit(subs_reg,0,0,4)
 a.emit(str_imm,4,7,0);a.emit(str_imm,0,7,4)
 # Pre-drain plus post-drain: no read or raw reuse until prior packet drains.
 a.emit(bl,DRAIN);a.emit(cmp_imm,0,0);a.emit(b_cond,'send_end','ne')
 imm(a,0,0x200069f4);a.emit(ldr_imm,0,0,0);a.emit(movs_imm,1,1);a.emit(mov_reg,2,7);a.emit(bl,0x08020c90)
 a.emit(bl,DRAIN);a.label('send_end');a.emit(pop_list,[6],pc=True)
 return a.assemble()[0]
def crc_update():
 a=Asm(CRC_UPDATE);a.emit(push_list,[4,5,6],lr=True);imm(a,4,0x04c11db7);a.emit(mov_reg,6,2)
 a.label('byte');a.emit(ldrb_imm,3,0,0);a.emit(adds_imm8,0,1);a.emit(lsls_imm,3,3,24);a.emit(raw,h(0x405e)) # EORS r6,r3
 a.emit(movs_imm,5,8);a.label('bit');a.emit(lsls_imm,6,6,1);a.emit(b_cond,'no_xor','lo');a.emit(raw,h(0x4066)) # EORS r6,r4
 a.label('no_xor');a.emit(subs_imm8,5,1);a.emit(b_cond,'bit','ne');a.emit(subs_imm8,1,1);a.emit(b_cond,'byte','ne')
 a.emit(mov_reg,0,6);a.emit(pop_list,[4,5,6],pc=True);return a.assemble()[0]
def drain():
 a=Asm(DRAIN);a.emit(push_list,[4,5,6],lr=True)
 a.label('poll');imm(a,0,0x200069f4);a.emit(ldr_imm,0,0,0);a.emit(ldr_imm,0,0,20);a.emit(ldr_imm,4,0,0)
 a.emit(mov_reg,0,4);a.emit(bl,0x08035a50)
 a.emit(ldr_imm,5,4,20);a.emit(ldr_imm,5,5,4);a.emit(ldr_imm,5,5,4) # USB stream
 a.emit(ldr_imm,0,5,16);imm(a,1,0x274);a.emit(adds_reg,0,0,1);a.emit(ldrb_imm,0,0,0)
 a.emit(cmp_imm,0,3);a.emit(b_cond,'disconnected','ne')
 a.emit(ldr_imm,0,4,16);a.emit(ldrh_imm,1,0,0);a.emit(ldrh_imm,2,0,2);a.emit(cmp_reg,1,2);a.emit(b_cond,'yield','ne')
 a.emit(ldrb_imm,0,5,12);a.emit(cmp_imm,0,0);a.emit(b_cond,'yield','ne')
 a.emit(ldrb_imm,0,5,28);a.emit(cmp_imm,0,0);a.emit(b_cond,'yield','eq') # actual USB IN semaphore
 a.emit(movs_imm,0,0);a.emit(pop_list,[4,5,6],pc=True)
 a.label('yield');a.emit(bl,0x0801be60);a.emit(b,'poll')
 a.label('disconnected');a.emit(movs_imm,0,1);a.emit(pop_list,[4,5,6],pc=True)
 return a.assemble()[0]
def load(u):
 p=R/'builds/phase27-qspi-read'
 # Reuse only the 88-byte nibble/CRC codec tail. Never load the obsolete
 # phase27 direct-backend command or its address-supplied validator.
 codec=(p/'arm-diagnostic.fragment.bin').read_bytes()[0x2ca:]
 assert len(codec)==88
 u.mem_write(0x0807a6de,codec)
 from entry import entry
 u.mem_write(0x0807a414,entry())
 sys.path.insert(0,str(p));from evidence_protocol import request
 u.mem_write(TEMPLATE,request(0)) # immutable prototype data, never a firmware file
 for addr,fn in ((COMMAND,command),(CRC_UPDATE,crc_update),(DRAIN,drain)):
  b=fn();u.mem_write(addr,b)
  (O/f'{addr:08x}-prototype.asm').write_text('\n'.join(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in md.disasm(b,addr))+'\n')
 return dict(command_bytes=len(command()),incremental_crc_bytes=len(crc_update()),drain_bytes=len(drain()),frame_bytes=FRAME,
  payload_offset=RAW,packet_offset=PACKET,prototype_only=True)
