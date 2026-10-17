"""Explicit RAM-only status packets; no Storage calls or raw retry path."""
def install(ns):
 ns['L'].update(status=0x08074100,status_drain=0x08074700,classify=0x08074400)
 a=ns
 source=SOURCE.replace('sub_sp_imm,36','sub_sp_imm,52').replace('add_sp_imm,36','add_sp_imm,52').replace('movs_imm,1,11','movs_imm,1,26').replace('adds_imm8,0,15','adds_imm8,0,30').replace('movs_imm,0,24','movs_imm,0,39')
 source=source.replace("a.emit(mov_reg,0,4);a.emit(adds_imm8,0,4);a.emit(movs_imm,1,26)","a.emit(mov_reg,0,4);a.emit(adds_imm8,0,15);a.emit(movs_imm,1,0);a.emit(movs_imm,2,15);a.label('status_pad');a.emit(strb_imm,1,0,0);a.emit(adds_imm8,0,1);a.emit(subs_imm8,2,1);a.emit(b_cond,'status_pad','ne');a.emit(mov_reg,0,4);a.emit(adds_imm8,0,4);a.emit(movs_imm,1,26)")
 exec(source,ns)

SOURCE=r'''
def status_ops():
 out={}
 # R0=status; R1=session. Preserve caller R4..R7 and return original status.
 a=Asm(L['status']);a.emit(push_list,[4,5,6,7],lr=True);a.emit(sub_sp_imm,36);a.emit(mov_reg,7,13);a.emit(mov_reg,6,0);a.emit(mov_reg,5,1);a.emit(mov_reg,4,7);a.emit(adds_imm8,4,8)
 for i,v in enumerate(b'\xf0\x7dCT\x4f'):a.emit(movs_imm,0,v);a.emit(strb_imm,0,4,i)
 a.emit(strb_imm,5,4,5);a.emit(strb_imm,6,4,6);a.emit(mov_reg,0,4);a.emit(adds_imm8,0,7);a.emit(movs_imm,1,1);a.emit(cmp_imm,6,1);a.emit(b_cond,'status_epoch','ne');a.emit(movs_imm,1,0);a.label('status_epoch');a.emit(bl,L['n32'])
 a.emit(mov_reg,0,4);a.emit(adds_imm8,0,4);a.emit(movs_imm,1,11);a.emit(bl,L['packet_crc']);a.emit(mov_reg,1,0);a.emit(mov_reg,0,4);a.emit(adds_imm8,0,15);a.emit(bl,L['n32']);a.emit(movs_imm,1,247);a.emit(strb_imm,1,0,0)
 a.emit(bl,L['status_drain']);a.emit(cmp_imm,0,0);a.emit(b_cond,'status_out','ne');a.emit(str_imm,4,7,0);a.emit(movs_imm,0,24);a.emit(str_imm,0,7,4);imm(a,0,0x200069f4);a.emit(ldr_imm,0,0,0);a.emit(movs_imm,1,1);a.emit(mov_reg,2,7);a.emit(bl,0x08020c90);a.emit(bl,L['status_drain'])
 a.label('status_out');a.emit(mov_reg,0,6);a.emit(add_sp_imm,36);a.emit(pop_list,[4,5,6,7],pc=True);out['status']=a.assemble()[0]
 a=Asm(L['classify']);control(a,2);a.emit(ldr_imm,2,2,0)
 for word,code in [(0,1),(0x16,1),(0x17,1),(0x11,4),(0x15,5),(0x1d,2),(0x18,3),(0x13,6),(0x14,7)]:
  label='class_'+str(word);a.emit(cmp_imm,2,word);a.emit(b_cond,label,'eq')
 a.emit(lsls_imm,2,2,7);a.emit(lsrs_imm,2,2,7);a.emit(cmp_imm,2,0x12);a.emit(b_cond,'class_17','eq');a.emit(movs_imm,0,2);ret(a)
 for word,code in [(0,1),(0x16,1),(0x17,1),(0x11,4),(0x15,5),(0x1d,2),(0x18,3),(0x13,6),(0x14,7)]:
  a.label('class_'+str(word));a.emit(movs_imm,0,code);ret(a)
 out['classify']=a.assemble()[0]
 # Separate bounded USB-only drain: FAILED/INVALID are valid response states.
 stream=streaming()[0]['drain'] # overridden below with original emitter namespace
 a=Asm(L['status_drain']);a.emit(push_list,[4,5,6],lr=True);imm(a,6,TICK);a.emit(ldr_imm,6,6,0)
 a.label('poll');imm(a,0,TICK);a.emit(ldr_imm,0,0,0);a.emit(subs_reg,0,0,6);imm(a,1,5000);a.emit(cmp_reg,0,1);a.emit(b_cond,'disconnected','hs')
 imm(a,0,0x200069f4);a.emit(ldr_imm,0,0,0);a.emit(ldr_imm,0,0,20);a.emit(ldr_imm,4,0,0);a.emit(mov_reg,0,4);a.emit(bl,0x08035a50)
 a.emit(ldr_imm,5,4,20);a.emit(ldr_imm,5,5,4);a.emit(ldr_imm,5,5,4);a.emit(ldr_imm,0,5,16);imm(a,1,0x274);a.emit(adds_reg,0,0,1);a.emit(ldrb_imm,0,0,0);a.emit(cmp_imm,0,3);a.emit(b_cond,'disconnected','ne')
 a.emit(ldr_imm,0,4,16);a.emit(ldrh_imm,1,0,0);a.emit(ldrh_imm,2,0,2);a.emit(cmp_reg,1,2);a.emit(b_cond,'yield','ne');a.emit(ldrb_imm,0,5,12);a.emit(cmp_imm,0,0);a.emit(b_cond,'yield','ne');a.emit(ldrb_imm,0,5,28);a.emit(cmp_imm,0,0);a.emit(b_cond,'yield','eq');a.emit(movs_imm,0,0);a.emit(pop_list,[4,5,6],pc=True)
 a.label('yield');a.emit(bl,0x0801be60);a.emit(b,'poll');a.label('disconnected');a.emit(movs_imm,0,1);a.emit(pop_list,[4,5,6],pc=True);out['status_drain']=a.assemble()[0]
 return out
'''
