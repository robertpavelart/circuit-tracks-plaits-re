"""Stateless numeric adapter primitive, isolated host arithmetic only.

There is no selected stock scale. Caller must supply an explicit power-of-two
scale and symmetric clipping limit. Results in unit tests are numeric fixtures,
never stock-qualified samples. No memory address or firmware I/O occurs here.
"""
def adapt32(words,*,shift,clip_limit):
 if len(words)!=32:raise ValueError('Exactly32 samples required')
 if type(shift)!=int or not -23<=shift<=23:raise ValueError('Explicit integer shift required')
 if type(clip_limit)!=int or not 1<=clip_limit<=0x7fffff:raise ValueError('Explicit representable symmetric clip limit required')
 result=[];clips=0
 for v in words:
  if type(v)!=int or not -0x800000<=v<=0x7fffff:raise ValueError('signed24 Q3.21 sample required')
  a=abs(v)
  if shift>=0:a<<=shift
  else:a=(a+(1<<(-shift-1)))>>(-shift)
  a= -a if v<0 else a
  if a>clip_limit:a=clip_limit;clips+=1
  elif a< -clip_limit:a=-clip_limit;clips+=1
  result.append(a)
 return result,dict(rounding='nearest, half away from zero',clipped_samples=clips,
                    saturation='symmetric [-clip_limit,+clip_limit]',
                    arithmetic_headroom_bits=23-clip_limit.bit_length(),
                    persistent_words=0,stock_scale_qualified=False)

def adapt_stock32(words):
 from contract import ReplayRefused
 raise ReplayRefused('Stock word-per-Q3.21-unit scale and safe amplitude/headroom are UNRESOLVED; no default shift or guard policy')
