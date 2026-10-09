"""Independent integer oracle for the standalone DSP program; not an emulator.
Derived from MIT VariableSaw (Emilie Gillet), using the stated fixed contract.
"""
import math
Q=1<<21;F=1<<22
def quant(x,u):return int(math.floor(x*u+.5))
def mul(a,b):return (a*b)>>21
def ratio(n,d):
 if n<0 or d<=0 or n>=4*d:raise ValueError(('invalid ratio domain',n,d))
 return (n<<21)//d
def integrated(t):
 v=mul(mul(t,t),-Q//16)+3*Q//8
 v=mul(v,t)-Q//2
 return mul(v,t)+3*Q//16
class Fixed:
 def __init__(self):self.phase=0;self.next=0;self.previous_pw=F//2;self.high=0;self.frequency=quant(.01,F);self.pw=F//2;self.shape=0
 def state(self):return [self.phase,self.next,self.previous_pw,self.high,self.frequency,self.pw,self.shape]
 def render32(self,f,pw,shape):
  ft=min(quant(f,F),F//4);pt=F//2 if ft>=F//4 else min(max(quant(pw,F),2*ft),F-2*ft)
  tar=[ft,pt,quant(shape,Q)];cur=[self.frequency,self.pw,self.shape]
  delta=[t-c for t,c in zip(tar,cur)];step=[d>>5 for d in delta];rem=[d-(s<<5) for d,s in zip(delta,step)];err=[0]*3
  out=[]
  for _ in range(32):
   for i in range(3):
    cur[i]+=step[i];err[i]+=rem[i]
    if err[i]>=32:err[i]-=32;cur[i]+=1
   self.frequency,self.pw,self.shape=cur
   this=self.next;self.next=0;na=Q-self.shape;self.phase+=self.frequency
   sign=None
   if not self.high and self.phase>=self.pw:
    t=ratio(self.phase-self.pw,self.previous_pw-self.pw+self.frequency)
    notch=quant(1.2,Q)-(self.pw>>1);sign=1;self.high=1
   elif self.phase>=F:
    self.phase-=F;t=ratio(self.phase,self.frequency)
    notch=quant(1.2,Q);sign=-1;self.high=0
   if sign is not None:
    ts=mul(ratio(self.frequency,self.pw)+ratio(self.frequency,F-self.pw),self.shape)
    notch=mul(notch,na);u=Q-t
    ct=mul(notch,mul(t,t)>>1);cn=mul(notch,-(mul(u,u)>>1))
    it=mul(ts,integrated(u));inn=mul(ts,integrated(t))
    self.next+=sign*(cn-inn);this+=sign*(ct-it)
   if self.phase<self.pw:ns=self.phase>>1;tri=ratio(self.phase,self.pw)
   else:ns=quant(1.2,Q);tri=Q-ratio(self.phase-self.pw,F-self.pw)
   self.next+=mul(ns,na)+mul(tri,self.shape);self.previous_pw=self.pw
   sample=mul(2*this-Q,quant(5/6,Q))
   if not -8388608<=sample<8388608:raise OverflowError(sample)
   out.append(sample)
  assert cur==tar
  return out
