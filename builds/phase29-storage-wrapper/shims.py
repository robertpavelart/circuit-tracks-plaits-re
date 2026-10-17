"""Emulator-only Thumb routines. No application, patch plan or binary is emitted.
Addresses in 0x20060000 are TEST ARENA, not physical SRAM ownership claims.
"""
from inspect_code import *
sys.path.insert(0,str(REF/'tools'));from thumb import *
STATE=0x20060010;REQ=0x20060040;PAYLOAD=0x20060080;PACKET=0x20060290;DESC=0x20060388
SUBMIT=0x0807b000;CALLBACK=0x0807b200;SERVICE=0x0807b400
def imm(a,r,v):a.emit(movw,r,v&65535);a.emit(movt,r,v>>16)
def submit():
 a=Asm(SUBMIT);a.emit(push_list,[4,5,6,7],lr=True);a.emit(sub_sp_imm,4)
 # r4=request frame, r6=input port arrive from unchanged phase27 validator.
 a.emit(cmp_imm,6,0);a.emit(b_cond,'end','ne') # focused USB-main fixture
 imm(a,5,STATE);a.emit(ldr_imm,0,5,0);a.emit(cmp_imm,0,0);a.emit(b_cond,'end','ne')
 # Preflight queue capacity to avoid the stock full-queue synchronous fallback.
 imm(a,7,0x20006968);a.emit(ldr_imm,7,7,0);a.emit(ldr_imm,0,7,8);a.emit(bl,0x0802212a)
 a.emit(cmp_imm,0,24);a.emit(b_cond,'end','lo')
 a.emit(ldrb_imm,0,4,5);a.emit(str_imm,0,5,8);a.emit(str_imm,6,5,12)
 a.emit(movs_imm,0,0);a.emit(str_imm,0,5,16);a.emit(str_imm,0,5,4)
 a.emit(movs_imm,0,1);a.emit(str_imm,0,5,0)
 imm(a,1,REQ)
 for off,v in ((0,1),(4,0x82000),(8,PAYLOAD),(12,512),(16,CALLBACK|1),(20,STATE)):
  imm(a,0,v);a.emit(str_imm,0,1,off)
 a.emit(mov_reg,0,7);a.emit(bl,0x08023f68)
 # Queue failure: restore idle; successful 0 keeps pending.
 a.emit(cmp_imm,0,0);a.emit(b_cond,'end','eq');a.emit(movs_imm,0,0);a.emit(str_imm,0,5,0)
 a.label('end');a.emit(add_sp_imm,4);a.emit(pop_list,[4,5,6,7],pc=True)
 return a.assemble()[0]
def callback():
 a=Asm(CALLBACK)
 # Stock worker passes (its copied request, userdata). Capture per-request
 # status now; wrapper+18 can change when another queued request completes.
 imm(a,2,0x20006968);a.emit(ldr_imm,2,2,0);a.emit(ldrb_imm,0,2,24)
 a.emit(str_imm,0,1,4);a.emit(raw,h(0xf3bf)+h(0x8f5f)) # DMB SY
 a.emit(movs_imm,0,2);a.emit(str_imm,0,1,0);a.emit(bx_lr)
 return a.assemble()[0]
def service():
 a=Asm(SERVICE);a.emit(push_list,[4,5,6,7],lr=True);a.emit(sub_sp_imm,4)
 imm(a,6,STATE);a.emit(ldr_imm,0,6,0);a.emit(cmp_imm,0,2);a.emit(b_cond,'active','eq');a.emit(b_w,'end');a.label('active')
 a.emit(ldr_imm,0,6,4);a.emit(cmp_imm,0,0);a.emit(b_cond,'success','eq');a.emit(b_w,'error');a.label('success')
 imm(a,4,PACKET);a.emit(ldr_imm,5,6,16)
 for off,v in enumerate(b'\xf0\x7dCT\x4d'):
  a.emit(movs_imm,0,v);a.emit(strb_imm,0,4,off)
 a.emit(ldr_imm,0,6,8);a.emit(strb_imm,0,4,5)
 a.emit(movs_imm,0,0);a.emit(cmp_imm,5,8);a.emit(b_cond,'kind','ne');a.emit(movs_imm,0,1)
 a.label('kind');a.emit(strb_imm,0,4,6);a.emit(strb_imm,5,4,7)
 imm(a,1,0x82000);a.emit(cmp_imm,5,8);a.emit(b_cond,'address','eq')
 a.emit(lsls_imm,0,5,6);a.emit(adds_reg,1,1,0)
 a.label('address');a.emit(mov_reg,0,4);a.emit(adds_imm8,0,8);a.emit(bl,0x0807a6de)
 imm(a,1,512);a.emit(bl,0x0807a6de)
 a.emit(movs_imm,1,64);a.emit(cmp_imm,5,8);a.emit(b_cond,'length','ne');a.emit(movs_imm,1,4)
 a.label('length');a.emit(strb_imm,1,0,0);a.emit(adds_imm8,0,1)
 a.emit(cmp_imm,5,8);a.emit(b_cond,'completion','eq')
 imm(a,1,PAYLOAD);a.emit(lsls_imm,2,5,6);a.emit(adds_reg,1,1,2);a.emit(movs_imm,2,64);a.emit(bl,0x0807a6ee)
 a.emit(b,'crc')
 a.label('completion');a.emit(mov_reg,7,0);imm(a,0,PAYLOAD);imm(a,1,512);a.emit(bl,0x0807a708)
 a.emit(mov_reg,1,0);a.emit(mov_reg,0,7);a.emit(bl,0x0807a6de)
 a.label('crc');a.emit(mov_reg,7,0);a.emit(mov_reg,1,4);a.emit(adds_imm8,1,4);a.emit(subs_reg,1,0,1)
 a.emit(mov_reg,0,4);a.emit(adds_imm8,0,4);a.emit(bl,0x0807a708)
 a.emit(mov_reg,1,0);a.emit(mov_reg,0,7);a.emit(bl,0x0807a6de)
 a.emit(movs_imm,1,247);a.emit(strb_imm,1,0,0);a.emit(adds_imm8,0,1);a.emit(subs_reg,0,0,4)
 imm(a,7,DESC);a.emit(str_imm,4,7,0);a.emit(str_imm,0,7,4)
 imm(a,0,0x200069f4);a.emit(ldr_imm,0,0,0);a.emit(movs_imm,1,1)
 # USB main output only in this focused scheduling fixture.
 a.emit(mov_reg,2,7);a.emit(bl,0x08020c90)
 a.emit(adds_imm8,5,1);a.emit(str_imm,5,6,16);a.emit(cmp_imm,5,9);a.emit(b_cond,'end','lo')
 a.emit(movs_imm,0,3);a.emit(str_imm,0,6,0);a.emit(b,'end') # draining; do not reuse yet
 a.label('error');a.emit(movs_imm,0,0);a.emit(str_imm,0,6,0)
 a.label('end');a.emit(add_sp_imm,4);a.emit(pop_list,[4,5,6,7],pc=True)
 return a.assemble()[0]
def load(u):
 for address,fn in ((SUBMIT,submit),(CALLBACK,callback),(SERVICE,service)):
  b=fn();u.mem_write(address,b)
  (O/f'{address:08x}-emulator.asm').write_text('\n'.join(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in md.disasm(b,address))+'\n')
 # Retain prior validator/helpers, replace only its command-call in emulator.
 p=R/'builds/phase27-qspi-read';u.mem_write(0x0807a414,(p/'arm-diagnostic.fragment.bin').read_bytes())
 u.mem_write(0x0807a59e,bl(0x0807a59e,SUBMIT))
 return dict(submit_bytes=len(submit()),callback_bytes=len(callback()),service_bytes=len(service()),
  note='Emulator-only instructions; not a firmware patch or qualified physical address allocation')
