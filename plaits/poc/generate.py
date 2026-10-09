"""Generate standalone assembler text, not Circuit code or hand-encoded words.
VariableSaw algebra derived from pinned MIT Mutable Instruments implementation.
Phase/frequency/PW Q2.22; audio/corrections/shape Q3.21. No immutable LUT.
"""
import argparse,json
from pathlib import Path
Q=1<<21;F=1<<22
class Program:
 def __init__(self):
  self.lines=[];self.names={n:0x20+i for i,n in enumerate(['phase','next','previous_pw','high','frequency','pw','shape'])}
  self.names.update({n:0x40+i for i,n in enumerate(['target_f','target_pw','target_shape'])})
  self.scratch=[];self.serial=0
 def slot(self,n):
  if n not in self.names:self.names[n]=0x80+len(self.scratch);self.scratch.append(n)
  return self.names[n]
 def mem(self,n):
  a=self.slot(n);return ('x:>$' if a>=64 else 'x:$')+f'{a:06x}'
 def operand(self,n):return f'#>${n&0xffffff:06x}' if isinstance(n,int) else self.mem(n)
 def emit(self,*ss):self.lines.extend(ss)
 def label(self,n):self.emit(n+':')
 def fresh(self,p):self.serial+=1;return p+str(self.serial)
 def load(self,n,r='a'):self.emit(f'move {self.operand(n)},{r}')
 def store(self,n,r='a'):self.emit(f'move {r},{self.mem(n)}')
 def assign(self,d,v):self.load(v);self.store(d)
 def add(self,d,a,b,sub=False):
  self.load(a);self.load(b,'x0');self.emit(('sub' if sub else 'add')+' x0,a');self.store(d)
 def shift(self,d,a,n):self.load(a);self.emit(f'{"asl" if n>0 else "asr"} #${abs(n):02x},a,a');self.store(d)
 def mul(self,d,a,b):
  # QQQ signed pairing is spelled y0,x0 in this audited assembler. x0,y0
  # instead matches its distinct mixed-signed form; runner checks opcodeD0.
  self.load(a,'x0');self.load(b,'y0');self.emit('mpy y0,x0,a','asl #$02,a,a');self.store(d)
 def ratio(self,d,n,den):
  self.load(n,'x0');self.load(den,'y0');self.emit('jsr >@ratio');self.store(d)
 def branch(self,a,b,cond,label):self.load(a);self.load(b,'x0');self.emit('cmp x0,a',cond+' >@'+label)
 def jump(self,n):self.emit('jmp >@'+n)
 def polynomial(self,d,t):
  # Integrated two-sample BLEP:3/16-t/2+3*t²/8-t⁴/16.
  self.mul('poly_t2',t,t);self.mul('poly_work','poly_t2',-Q//16)
  self.add('poly_work','poly_work',3*Q//8);self.mul('poly_work','poly_work',t)
  self.add('poly_work','poly_work',-Q//2);self.mul('poly_work','poly_work',t)
  self.add(d,'poly_work',3*Q//16)
 def ramp_setup(self,cur,target):
  self.add(cur+'_delta',target,cur,True)
  self.shift(cur+'_step',cur+'_delta',-5)
  self.shift('ramp_work',cur+'_step',5)
  self.add(cur+'_rem',cur+'_delta','ramp_work',True);self.assign(cur+'_err',0)
 def ramp_next(self,cur):
  self.add(cur,cur,cur+'_step');self.add(cur+'_err',cur+'_err',cur+'_rem')
  done=self.fresh('ramp_');self.branch(cur+'_err',32,'jlt',done)
  self.add(cur+'_err',cur+'_err',32,True);self.add(cur,cur,1);self.label(done)
 def build(self):
  self.label('render32')
  # Inputs are independently range-checked by harness; clamp exactly as source.
  below=self.fresh('lowfreq_');pw_ok=self.fresh('pwok_');pw_hi=self.fresh('pwhi_')
  self.branch('target_f',F//4,'jlt',below);self.assign('target_f',F//4)
  self.assign('target_pw',F//2);self.jump(pw_ok);self.label(below)
  self.shift('min_pw','target_f',1);self.add('max_pw',F,'min_pw',True)
  self.branch('target_pw','min_pw','jge',pw_hi);self.assign('target_pw','min_pw')
  self.label(pw_hi);self.branch('target_pw','max_pw','jle',pw_ok);self.assign('target_pw','max_pw')
  self.label(pw_ok)
  for cur,tar in [('frequency','target_f'),('pw','target_pw'),('shape','target_shape')]:self.ramp_setup(cur,tar)
  self.emit('move #>$000000,r0','do #$20,@block_end')
  self.label('sample')
  for cur in ['frequency','pw','shape']:self.ramp_next(cur)
  self.assign('this','next');self.assign('next',0)
  self.add('notch_amount',Q,'shape',True);self.add('phase','phase','frequency')
  no_cross=self.fresh('nocross_');wrap=self.fresh('wrap_');after=self.fresh('after_')
  self.branch('high',0,'jne',wrap);self.branch('phase','pw','jlt',wrap)
  self.label('pw_event')
  # PW crossing: preserve source if/else-if ordering, including delayed wrap.
  self.add('event_num','phase','pw',True)
  self.add('event_den','previous_pw','pw',True);self.add('event_den','event_den','frequency')
  self.ratio('t','event_num','event_den')
  self.shift('pw_audio','pw',-1);self.add('notch',round(1.2*Q),'pw_audio',True)
  self.assign('event_sign',1);self.assign('high',1);self.jump('event')
  self.label(wrap);self.branch('phase',F,'jlt',no_cross)
  self.label('wrap_event')
  self.add('phase','phase',F,True);self.ratio('t','phase','frequency')
  self.assign('notch',round(1.2*Q));self.assign('event_sign',0);self.assign('high',0)
  self.label('event')
  # Reformulate (1/pw+1/(1-pw))*f to avoid large standalone reciprocals.
  self.add('one_minus_pw',F,'pw',True)
  self.ratio('slope_a','frequency','pw');self.ratio('slope_b','frequency','one_minus_pw')
  self.add('triangle_step','slope_a','slope_b');self.mul('triangle_step','triangle_step','shape')
  self.mul('notch','notch','notch_amount')
  self.add('u',Q,'t',True)
  self.mul('blep_this','t','t');self.shift('blep_this','blep_this',-1)
  self.mul('blep_next','u','u');self.shift('blep_next','blep_next',-1)
  self.load('blep_next');self.emit('neg a');self.store('blep_next')
  self.polynomial('ibl_next','t');self.polynomial('ibl_this','u')
  self.mul('corr_this','notch','blep_this');self.mul('corr_next','notch','blep_next')
  self.mul('tri_this','triangle_step','ibl_this');self.mul('tri_next','triangle_step','ibl_next')
  is_wrap=self.fresh('iswrap_')
  self.branch('event_sign',0,'jeq',is_wrap)
  self.add('this','this','corr_this');self.add('next','next','corr_next')
  self.add('this','this','tri_this',True);self.add('next','next','tri_next',True);self.jump(after)
  self.label(is_wrap)
  self.add('this','this','corr_this',True);self.add('next','next','corr_next',True)
  self.add('this','this','tri_this');self.add('next','next','tri_next');self.jump(after)
  self.label(no_cross);self.label(after)
  fall=self.fresh('fall_');naive_end=self.fresh('naive_end_')
  self.branch('phase','pw','jge',fall)
  self.shift('notch_saw','phase',-1);self.ratio('triangle','phase','pw');self.jump(naive_end)
  self.label(fall);self.assign('notch_saw',round(1.2*Q))
  self.add('one_minus_pw',F,'pw',True);self.add('event_num','phase','pw',True)
  self.ratio('triangle','event_num','one_minus_pw');self.add('triangle',Q,'triangle',True)
  self.label(naive_end)
  self.mul('naive_a','notch_saw','notch_amount');self.mul('naive_b','triangle','shape')
  self.add('naive_a','naive_a','naive_b');self.add('next','next','naive_a')
  self.assign('previous_pw','pw')
  self.shift('output','this',1);self.add('output','output',Q,True)
  self.mul('output','output',round(5*Q/6))
  self.load('output');self.emit('move a,y:(r0)+')
  self.label('block_end');self.jump('done')
  # Exact positive integer restoring quotient,21 fractional bits, table-free.
  # X0 numerator, Y0 denominator; quotientQ3.21 inA; controls unchanged.
  self.label('ratio');self.emit('move x0,a','clr b')
  self.label('ratio_integer');self.emit('cmp y0,a','jlt >@ratio_fraction','sub y0,a')
  self.load(Q,'x1');self.emit('add x1,b');self.jump('ratio_integer')
  self.label('ratio_fraction');self.emit('move b1,'+self.mem('ratio_integer_q'),'clr b',
   'do #$15,@ratio_end','asl a','asl b','cmp y0,a','jlt >@ratio_bit_end','sub y0,a','add #$01,b')
  self.label('ratio_bit_end');self.emit('nop');self.label('ratio_end')
  self.load('ratio_integer_q','x1');self.emit('add x1,b','move b,a','rts')
  self.label('done')
  # Audited assembler accepts compact absolute branches below0x1000; all targets
  # are checked within that range by the runner. No > branch pseudo-syntax.
  return [s.replace('>@','@') for s in self.lines]

def generate(out):
 out=Path(out).resolve();base=Path(__file__).resolve().parents[2]/'builds/phase20a-plaits'
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh Phase20A child required')
 p=Program();lines=p.build();out.mkdir(parents=True)
 (out/'variablesaw.asm').write_text('\n'.join(lines)+'\n',encoding='utf8')
 (out/'layout.json').write_text(json.dumps(dict(origin=0x200,state_words=7,state_X=[0x20,0x27],
  control_X=[0x40,0x43],scratch_X=[0x80,0x80+len(p.scratch)],scratch_words=len(p.scratch),
  output_Y=[0,32],table_words=0,variables=p.names,render_samples=32,
  oscillator='Closest-source VariableSaw:stepBLEP+integratedBLEP;exact restoring ratios',
  domains={'phase_frequency_pw':'Q2.22','audio_shape_correction':'Q3.21'}),indent=2,sort_keys=True)+'\n')
 print('Assembly source generated; scratch',len(p.scratch),'state7; no machine words hand encoded')
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--output-dir',required=True);generate(a.parse_args().output_dir)
