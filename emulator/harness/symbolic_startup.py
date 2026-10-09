"""Fail-closed narrow symbolic transfer adapter for verified stock startup words.
Not a replacement DSP decoder/full emulator. Concrete19A core is unchanged.
Raw original words identify audited operations; unsupported operations STOP.
"""
import hashlib,json
from pathlib import Path
from partial_state import Partial,RegisterCell,ICC,BlockingUnknown,interrupt_eligibility

HASHES={'main':'b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855',
        'worker':'adf8da1b2b889d069eb52935dbdc4ce9092210d29df719937ca5ac5f62dfa91a'}

class Startup:
    def __init__(self,role,image):
        self.role=role;self.image=bytes(image)
        if hashlib.sha256(self.image).hexdigest()!=HASHES[role]:raise ValueError('Original stock identity mismatch')
        self.pc=0;self.count=0;self.trace=[];self.transaction_log=[]
        self.sr=Partial.unknown(role+' post-ROM SR')
        self.omr=Partial.unknown(role+' post-ROM OMR')
        self.pending=Partial.unknown(role+' post-ROM pending IRQ request',1)
        self.priority=Partial.unknown(role+' post-ROM PIC/request IPL',2)
        self.loop_address=Partial.unknown(role+' post-ROM LA')
        self.cells={a:RegisterCell(a,role+f' post-ROM Y:{a:06X} latch') for a in [0xfffffa,0xfffff9]}
        self.icc=ICC()
        self.regs={r:Partial.unknown(role+' post-ROM '+r) for r in ['R5','A24','Z']}
    def words(self,pc,count=1):
        if pc<0 or (pc+count)*3>len(self.image):raise BlockingUnknown('Invalid P fetch',dict(PC=pc,count=count))
        return tuple(int.from_bytes(self.image[3*i:3*i+3],'big') for i in range(pc,pc+count))
    def interrupt_boundary(self):
        decision=interrupt_eligibility(self.pending,self.priority,self.sr.extract(8,2))
        if decision.known_mask==0:
            raise BlockingUnknown('Unknown affects instruction-boundary interrupt recognition',
                dict(pending=self.pending.as_dict(),priority=self.priority.as_dict(),SR_I=self.sr.extract(8,2).as_dict(),
                     eligible=decision.as_dict(),propagation='ROM exit -> pending/request IPL/SR.I -> eligibility -> instruction vs handler',
                     witness_cases=[dict(pending=1,IPL=2,I=0,eligible=True),dict(pending=1,IPL=2,I=3,eligible=False)],
                     witness_scope='Permitted small-field completions, not seeded/executed stock states'))
        eligible=decision.require('instruction-boundary interrupt recognition')
        if eligible:raise BlockingUnknown('Eligible interrupt handler delivery not modeled',decision.as_dict())
    def loop_boundary(self,length):
        active=self.sr.bit(15)
        # Only support guaranteed inactive loop control, or definite non-end.
        end=self.loop_address.equal(Partial.concrete(self.pc+length-1,'audited instruction last-word address'))
        if active.known_mask==1 and active.known_value==0:return
        if end.known_mask==1 and end.known_value==0:return
        raise BlockingUnknown('Unknown inherited loop end can affect control/stack',dict(LF=active.as_dict(),LA=self.loop_address.as_dict(),end=end.as_dict()))
    def step(self):
        self.interrupt_boundary()
        op=self.words(self.pc);pc=self.pc;tx=[];outputs={};inputs={}
        if pc==0:
            length=1 if self.role=='main' else 2
            expected=(0x0c0100,) if self.role=='main' else (0x0af080,0x100)
            if self.words(pc,length)!=expected:raise ValueError('Entry witness mismatch')
            self.loop_boundary(length);self.pc=0x100
        elif self.role=='main' and pc in [0x100,0x101]:
            if op!=(0x0aba4d if pc==0x100 else 0x0ab96d,):raise ValueError('GPIO witness mismatch')
            self.loop_boundary(1)
            cell=self.cells[0xfffffa if pc==0x100 else 0xfffff9]
            inputs=dict(SR=self.sr.as_dict(),latch=cell.value.as_dict())
            change=cell.bit_operation(13,pc==0x101,f'original main P:{pc:06X}')
            carry=Partial(1,change['carry']['known_mask'],change['carry']['known_value'],tuple(change['carry']['provenance']))
            self.sr=self.sr.put(0,carry,f'P:{pc:06X} C=old latch bit13')
            tx=[dict(space='Y',operation='READ_MODIFY_WRITE',**change)]
            outputs=dict(SR=self.sr.as_dict(),latch=cell.value.as_dict());self.pc+=1
        elif self.role=='main' and pc==0x102:
            if self.words(pc,2)!=(0x5ef000,0xffffd4):raise ValueError('ICC witness mismatch')
            self.loop_boundary(2)
            self.sr.bit(17).require('A transfer arithmetic mode')
            if self.sr.bit(17).known_value:raise BlockingUnknown('16-bit transfer mode not qualified',self.sr.as_dict())
            inputs=self.icc.as_dict();data=self.icc.receive('original main P:000102')
            self.regs['A24']=data;outputs=dict(A24=data.as_dict(),ICC=self.icc.as_dict());self.pc+=2
            tx=[dict(space='Y',address=0xffffd4,operation='READ',value=data.as_dict())]
        elif self.role=='main' and pc==0x104:
            # Full CMP CCR updates/modes are not certified by this narrow adapter.
            raise BlockingUnknown('Full CMP flag/mode semantics not implemented; equality helper is a unit operation only',dict(PC=pc))
        else:raise BlockingUnknown('Unsupported stock instruction/peripheral behavior',dict(PC=pc,words=list(op)))
        self.count+=1
        self.transaction_log.extend(tx)
        self.trace.append(dict(type='SYMBOLIC_INSTRUCTION',role=self.role,PC=pc,opcode=list(self.words(pc,2 if pc==0 and self.role=='worker' or pc==0x102 else 1)),
            count=self.count,inputs=inputs,outputs=outputs,transactions=tx,next_PC=self.pc))
    def run(self,limit):
        try:
            for _ in range(limit):self.step()
            reason='Instruction budget reached'
        except BlockingUnknown as error:
            reason=error.reason
            self.trace.append(dict(type='BLOCKING',role=self.role,PC=self.pc,executed_instructions=self.count,
                                   reason=reason,dependency=error.dependency,opcode=list(self.words(self.pc))))
        return dict(role=self.role,stock_symbolic_instructions_executed=self.count,stop_PC=self.pc,reason=reason)

def bootstrap_history():
    old=Partial.unknown('ROM pass1 OMR before original shim')
    a,_=old.bset(7,'shim P1');a,_=a.bset(22,'shim P2');a,c=a.bclr(21,'shim P3')
    return dict(pre_second_ROM_OMR=a.as_dict(),pre_second_ROM_C=c.as_dict(),
        carry_expression='incoming ROM-pass1 OMR bit21; not necessarily numeric0',
        application_OMR=Partial.unknown('ROM pass2 may modify OMR; no write exclusion proven').as_dict(),
        application_C=Partial.unknown('ROM pass2 may modify C; no preservation proven',1).as_dict(),
        note='Carry modification knowledge in temporal provenance, not an unsupported post-ROM numeric seed')

def canonical_trace(trace):
    return ''.join(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n' for r in trace).encode()
