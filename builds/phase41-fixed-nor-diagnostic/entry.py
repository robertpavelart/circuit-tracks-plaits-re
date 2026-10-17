"""Offline entry prototype: rdiag signature, ownership and stock forwarding.

The sole experimental command is 13. All payload/padding bytes must be zero;
the host supplies no address or length. The low-level codec is reused from
the already-audited phase27 fragment, not a second MIDI transport.
"""
from environment import *
sys.path.insert(0,str(REF/'tools'))
from thumb import *
BASE=0x0807a414
def entry():
 a=Asm(BASE)
 a.emit(push_list,[0,1,2,4,5,6,7],lr=True)
 a.emit(ldr_imm,4,1,0);a.emit(ldr_imm,5,1,4)
 a.emit(cmp_imm,5,8);a.emit(b_cond,'forward','lo')
 for i,v in enumerate(b'\xf0\x7dCT'):
  a.emit(ldrb_imm,3,4,i);a.emit(cmp_imm,3,v);a.emit(b_cond,'forward','ne')
 a.emit(cmp_imm,0,0);a.emit(b_cond,'out','ne')
 a.emit(cmp_imm,5,232);a.emit(b_cond,'out','ne')
 # Reject runtime parser buffers outside the proven non-cacheable domain.
 a.emit(movw,2,0);a.emit(movt,2,0x2000);a.emit(cmp_reg,4,2);a.emit(b_cond,'out','lo')
 a.emit(mov_reg,3,4);a.emit(adds_imm8,3,232)
 a.emit(movw,2,0);a.emit(movt,2,0x2001);a.emit(cmp_reg,3,2);a.emit(b_cond,'out','hi')
 a.emit(lsls_imm,3,4,28);a.emit(cmp_imm,3,0);a.emit(b_cond,'out','ne')
 a.emit(ldrb_imm,3,4,4);a.emit(cmp_imm,3,13);a.emit(b_cond,'out','ne')
 a.emit(mov_reg,2,4);a.emit(adds_imm8,2,6);a.emit(movs_imm,3,225)
 a.label('padding');a.emit(ldrb_imm,1,2,0);a.emit(cmp_imm,1,0);a.emit(b_cond,'out','ne')
 a.emit(adds_imm8,2,1);a.emit(subs_imm8,3,1);a.emit(b_cond,'padding','ne')
 a.emit(ldrb_imm,1,2,0);a.emit(cmp_imm,1,247);a.emit(b_cond,'out','ne')
 a.emit(movs_imm,6,0);a.emit(bl,0x0807b000)
 a.label('out');a.emit(pop_list,[0,1,2,4,5,6,7],pc=True)
 a.label('forward');a.emit(raw,h(0xe8bd)+h(0x40f7));a.emit(raw,bytes.fromhex('2de9f041'));a.emit(b_w,0x0801eb34)
 return a.assemble()[0]
