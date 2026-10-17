"""New offline candidate; never writes historical candidate directories.

Source transformations are asserted and saved for review. Strict DMA quarantine
retains the Main frame; it never cancels storage or forcibly releases ownership.
"""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
P=R/'builds/phase61-final-geometry-gated-candidate'
NAME='circuittracks-nor-defect-closure-development'

def replace(s,old,new):
 assert old in s,old
 return s.replace(old,new,1)

def module():
 s=(P/'construct.py').read_text()
 s=replace(s,"name='circuittracks-final-geometry-gated-nor-test'",f"name='{NAME}'")
 s=replace(s,"b'N61GEO'","b'N63DEV'")
 s=replace(s,"components=build_ops()|protocol_ops();", "components=build_ops()|protocol_ops()|status_ops();")
 s=replace(s,"a.emit(bl,L['authorize']);a.emit(cmp_imm,0,1);check(a,'ne','out');a.emit(movs_imm,6,0);a.emit(bl,L['raw']);a.emit(b,'out');a.label('do_export');a.emit(bl,L['export'])", "a.emit(bl,L['authorize']);a.emit(cmp_imm,0,1);a.emit(b_cond,'authorization_rejected','ne');a.emit(movs_imm,0,6);a.emit(ldrb_imm,1,4,5);a.emit(bl,L['status']);a.emit(movs_imm,6,0);a.emit(bl,L['raw']);a.emit(bl,L['classify']);a.emit(ldrb_imm,1,4,5);a.emit(bl,L['status']);a.emit(b,'out');a.label('authorization_rejected');a.emit(bl,L['classify']);a.emit(cmp_imm,0,5);a.emit(b_cond,'rejection_status','eq');a.emit(movs_imm,0,2);a.label('rejection_status');a.emit(ldrb_imm,1,4,5);a.emit(bl,L['status']);a.emit(b,'out');a.label('do_export');a.emit(bl,L['classify']);a.emit(ldrb_imm,1,4,5);a.emit(bl,L['status']);a.emit(cmp_imm,0,4);a.emit(b_cond,'out','ne');a.emit(bl,L['export'])")
 # Repeat readiness/geometry queries can replace an unconsumed export session.
 s=replace(s,"a.emit(cmp_imm,0,0x11);a.emit(b_cond,'reject','ne')", "a.emit(cmp_imm,0,0x11);a.emit(b_cond,'export_ready','eq');a.emit(lsls_imm,0,0,7);a.emit(lsrs_imm,0,0,7);a.emit(cmp_imm,0,0x12);a.emit(b_cond,'reject','ne');a.label('export_ready')")
 s=replace(s,"a=Asm(L['begin']);save(a);control(a);", "a=Asm(L['begin']);save(a);imm(a,1,0x20000ab0);a.emit(cmp_reg,0,1);a.emit(b_cond,'out','ne');control(a);")
 s=replace(s,"a.emit(cmp_imm,0,0);a.emit(b_cond,'bad','ne');a.emit(movs_imm,0,0x16)","a.emit(cmp_imm,0,0x11);a.emit(b_cond,'recheck','eq');a.emit(cmp_imm,0,0);a.emit(b_cond,'bad','ne');a.emit(movs_imm,0,0x16)")
 s=replace(s,"a.label('bad');failstore(a);finish(a);out['begin']", "a.label('recheck');a.emit(movs_imm,0,0x17);a.emit(str_imm,0,4,0);a.emit(b,'out');a.label('bad');failstore(a);finish(a);out['begin']")
 s=replace(s,"a.emit(cmp_imm,2,0x16);a.emit(b_cond,'bad','ne');imm(a,2,0x0801ae07)", "a.emit(cmp_imm,2,0x17);a.emit(b_cond,'registration_ok','eq');a.emit(cmp_imm,2,0x16);a.emit(b_cond,'bad','ne');a.label('registration_ok');imm(a,2,0x0801ae07)")
 s=replace(s,"a.emit(cmp_imm,0,0x16);a.emit(b_cond,'out','eq');failstore(a);finish(a);out['slow']", "a.emit(cmp_imm,0,0x17);a.emit(b_cond,'out','eq');a.emit(cmp_imm,0,0x16);a.emit(b_cond,'out','eq');failstore(a);finish(a);out['slow']")
 s=replace(s,"a.emit(cmp_imm,2,0x16);a.emit(b_cond,'bad','ne');imm(a,2,4096)", "a.emit(cmp_imm,2,0x17);a.emit(b_cond,'stride_mount','eq');a.emit(cmp_imm,2,0x16);a.emit(b_cond,'bad','ne');a.label('stride_mount');imm(a,2,4096)")
 # At AE06 the retained outer mount's R4 is disk object AA0, not FS AB0.
 s=replace(s,"a=Asm(L['snapshot']);save(a);control(a);", "a=Asm(L['snapshot']);save(a);imm(a,1,0x20000aa0);a.emit(cmp_reg,4,1);check(a,'ne','out');control(a);imm(a,1,LIMIT);a.emit(ldr_imm,2,1,0);a.emit(cmp_reg,2,4);check(a,'ne','out');a.emit(ldr_imm,2,1,4);a.emit(cmp_reg,2,4);check(a,'hi','out');")
 s=replace(s,"a.emit(cmp_imm,1,0x16);check(a,'ne','out');a.emit(cmp_imm,0,0)", "a.emit(cmp_imm,1,0x17);a.emit(b_cond,'snapshot_mount','eq');a.emit(cmp_imm,1,0x16);check(a,'ne','out');a.label('snapshot_mount');a.emit(cmp_imm,0,0)")
 s=replace(s,"a.emit(str_imm,5,4,4);a.emit(str_imm,6,4,8);", "a.emit(ldr_imm,0,4,0);a.emit(cmp_imm,0,0x17);a.emit(b_cond,'snapshot_first','ne');a.emit(ldr_imm,0,4,4);a.emit(cmp_reg,0,5);check(a,'ne','bad');a.emit(ldr_imm,0,4,8);a.emit(cmp_reg,0,6);check(a,'ne','bad');a.emit(b,'snapshot_commit');a.label('snapshot_first');a.emit(str_imm,5,4,4);a.emit(str_imm,6,4,8);a.label('snapshot_commit');")
 # Keep raw frame live until *all* independently observable owners are released.
 # The same guard runs before CPU reads and on EVERY raw exit. No forced writes.
 s=replace(s,"ns=dict(globals(),__file__=str(O/'stream.py')", "src=src.replace(\"a.label('read_ok');\",\"a.label('read_ok');a.emit(bl,'ownership_fence');\",1)\n src=src.replace(\"a.emit(add_sp_imm,FRAME)\",\"a.emit(bl,'ownership_fence');a.emit(add_sp_imm,FRAME)\",1)\n src=src.replace(\" a.label('total');\",FENCE+\" a.label('total');\",1)\n ns=dict(globals(),__file__=str(O/'stream.py')")
 ns=dict(__file__=str(O/'construct.py'),__name__='phase63_construction',FENCE=FENCE)
 (O/'reviewed-construction-source.txt').write_text(s)
 exec(compile(s,str(O/'reviewed-construction-source.txt'),'exec'),ns)
 from status_emitter import install
 install(ns)
 return ns

FENCE=""" a.label('ownership_fence');a.emit(push_list,[0,1,2,3],lr=True);a.emit(sub_sp_imm,4)
 a.label('ownership_poll');imm(a,0,0x400264b8);a.emit(ldr_imm,1,0,0);a.emit(movs_imm,2,1);a.emit(tst_reg,1,2);a.emit(b_cond,'ownership_wait','ne')
 a.emit(ldr_imm,1,0,4);a.emit(cmp_imm,1,0);a.emit(b_cond,'ownership_wait','ne')
 imm(a,0,0x20006968);a.emit(ldr_imm,0,0,0);a.emit(ldr_imm,1,0,16);a.emit(cmp_imm,1,0);a.emit(b_cond,'ownership_wait','ne')
 a.emit(ldr_imm,0,0,4);a.emit(ldrb_imm,1,0,8);a.emit(cmp_imm,1,1);a.emit(b_cond,'ownership_wait','ne')
 a.emit(add_sp_imm,4);a.emit(pop_list,[0,1,2,3],pc=True)
 a.label('ownership_wait');a.emit(bl,0x0801be60);a.emit(b,'ownership_poll')
"""

if __name__=='__main__':module()['main']()
