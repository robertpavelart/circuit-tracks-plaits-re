"""Partial bit values and qualified early peripheral contracts. No device APIs.
Unknown bits are NOT concrete zeros: value bits outside mask are canonical padding.
"""
from dataclasses import dataclass
from itertools import product

class BlockingUnknown(RuntimeError):
    def __init__(self,reason,dependency):
        super().__init__(reason);self.reason=reason;self.dependency=dependency

@dataclass(frozen=True)
class Partial:
    width:int
    known_mask:int
    known_value:int
    provenance:tuple=()
    def __post_init__(self):
        limit=(1<<self.width)-1
        if self.width<1 or self.known_mask&~limit or self.known_value&~self.known_mask:
            raise ValueError('Invalid partial bit encoding')
    @classmethod
    def unknown(cls,source,width=24):return cls(width,0,0,(source,))
    @classmethod
    def concrete(cls,value,source,width=24):return cls(width,(1<<width)-1,value,(source,))
    def bit(self,b):
        if not 0<=b<self.width:raise ValueError('Bit outside partial value')
        return Partial(1,(self.known_mask>>b)&1,(self.known_value>>b)&1,self.provenance)
    def extract(self,start,width):
        if width<1 or start<0 or start+width>self.width:raise ValueError('Field outside partial value')
        mask=(1<<width)-1
        return Partial(width,(self.known_mask>>start)&mask,(self.known_value>>start)&mask,self.provenance)
    def put(self,b,bit,source):
        if not 0<=b<self.width:raise ValueError('Bit outside partial value')
        if bit.width!=1:raise ValueError('One-bit value required')
        mask=(self.known_mask&~(1<<b))|(bit.known_mask<<b)
        value=(self.known_value&~(1<<b))|(bit.known_value<<b)
        return Partial(self.width,mask,value,tuple(sorted(set(self.provenance+bit.provenance+(source,)))))
    def bclr(self,b,source):return self.put(b,Partial.concrete(0,source,1),source),self.bit(b)
    def bset(self,b,source):return self.put(b,Partial.concrete(1,source,1),source),self.bit(b)
    def equal(self,other):
        if self.width!=other.width:raise ValueError('Width mismatch')
        sources=tuple(sorted(set(self.provenance+other.provenance)))
        shared=self.known_mask&other.known_mask
        if (self.known_value^other.known_value)&shared:return Partial(1,1,0,sources)
        if shared==(1<<self.width)-1:return Partial(1,1,1,sources)
        return Partial(1,0,0,sources)
    def require(self,use):
        if self.known_mask!=(1<<self.width)-1:
            raise BlockingUnknown('Unknown affects '+use,self.as_dict())
        return self.known_value
    def finite_values(self):
        if self.width>3:raise ValueError('Only documented small control fields may be enumerated')
        return [n for n in range(1<<self.width) if n&self.known_mask==self.known_value]
    def as_dict(self):return dict(width=self.width,known_mask=self.known_mask,known_value=self.known_value,provenance=list(self.provenance))

def interrupt_eligibility(pending,priority,mask):
    """Architecture IPL0..2 eligible when IPL>=I; IPL3 nonmaskable.
    Enumeration is <=32 small-field cases, not arbitrary24-bit brute force.
    """
    truth={int(bool(p and (level==3 or level>=m))) for p,level,m in
           product(pending.finite_values(),priority.finite_values(),mask.finite_values())}
    sources=tuple(sorted(set(pending.provenance+priority.provenance+mask.provenance)))
    return Partial(1,1,next(iter(truth)),sources) if len(truth)==1 else Partial(1,0,0,sources)

class RegisterCell:
    """Qualified configuration latch only; not generic peripheral emulation."""
    def __init__(self,address,source):
        self.address=address;self.value=Partial.unknown(source)
    def bit_operation(self,bit,set_bit,source):
        old=self.value
        self.value,carry=(old.bset if set_bit else old.bclr)(bit,source)
        return dict(address=self.address,old=old.as_dict(),new=self.value.as_dict(),carry=carry.as_dict())

class ICC:
    """Documented pending, enabled maskable-transfer case only.
    No fabricated handoff latch/flag values; undefined empty/disabled ACK cases stop.
    """
    def __init__(self):
        self.data=Partial.unknown('ROM exit peer ICDR3/ICDR4')
        self.pending=Partial.unknown('ROM exit ICC interrupt flag',1)
        self.ack=Partial.unknown('ROM exit ICC ACK',1)
        self.enable=Partial.unknown('ROM exit ICCR3.MIE',1)
        self.transactions=[]
    def publish(self,data,writer):
        if self.enable.require('ICC publication interrupt-enable decision')!=1:
            raise BlockingUnknown('Disabled-publication flag behavior not qualified',self.enable.as_dict())
        if self.pending.require('ICC previous pending-transfer/overrun behavior')!=0:
            raise BlockingUnknown('ICC overwrite/overrun behavior not qualified',self.pending.as_dict())
        self.data=data;self.pending=Partial.concrete(1,writer+' maskable transfer pending',1)
        self.transactions.append(dict(actor=writer,operation='ICDR3_WRITE',data=data.as_dict(),pending=self.pending.as_dict()))
    def receive(self,reader):
        if self.enable.require('ICC receive enable/ACK contract')!=1 or self.pending.require('ICC pending/ACK contract')!=1:
            raise BlockingUnknown('Empty/disabled ICC ACK behavior not qualified',dict(pending=self.pending.as_dict(),enable=self.enable.as_dict()))
        result=self.data;self.pending=Partial.concrete(0,reader+' clears flag',1)
        self.ack=Partial.concrete(1,reader+' acknowledges maskable transfer',1)
        self.transactions.append(dict(actor=reader,operation='ICDR4_READ',data=result.as_dict(),pending=self.pending.as_dict(),ACK=self.ack.as_dict()))
        return result
    def as_dict(self):return {n:getattr(self,n).as_dict() for n in ['data','pending','ack','enable']}
