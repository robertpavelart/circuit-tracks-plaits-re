"""Offline refusal and numeric-fixture tests; never constructs a stock CPU."""
import unittest,sys
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'plaits/seam'))
from contract import readiness,require_qualified_checkpoint,ReplayRefused
from adapter import adapt32,adapt_stock32

class SeamTests(unittest.TestCase):
 def test_normal_checkpoint_refused(self):
  with self.assertRaisesRegex(ReplayRefused,'X:0x5AB'):require_qualified_checkpoint()
 def test_no_stock_scale_default(self):
  with self.assertRaisesRegex(ReplayRefused,'UNRESOLVED'):adapt_stock32([0]*32)
 def test_missing_provenance_is_explicit(self):
  r=readiness();self.assertFalse(r['admitted']);self.assertEqual(r['stock_instructions_executed'],0)
  self.assertIsNone(r['concrete_checkpoint']);self.assertTrue(all(x['value'] is None for x in r['blockers']))
 def test_gate_covers_request_obligations(self):
  bs={r['blocker'] for r in readiness()['blockers']}
  self.assertTrue({'CONTROL_FLOW','ARITHMETIC_TO_ADDRESS','EFFECTIVE_ADDRESS','ARITHMETIC_SCALING','MODIFIER','STACK_LOOP','GUARD_STATUS'}<=bs)
 def test_independent_fraction_rounding(self):
  vals=[-0x800000,-0x7fffff,-2097152,-33,-32,-31,-3,-2,-1,0,1,2,3,31,32,33,2097152,0x7fffff]
  words=(vals*2)[:32]
  for shift in range(-23,24):
   for limit in [1,31,1<<20,0x7fffff]:
    got,meta=adapt32(words,shift=shift,clip_limit=limit);ref=[]
    for v in words:
     x=Fraction(v)*(2**shift if shift>=0 else Fraction(1,2**(-shift)))
     a=abs(x);rounded=(2*a.numerator+a.denominator)//(2*a.denominator)
     rounded= -rounded if x<0 else rounded
     ref.append(max(-limit,min(limit,rounded)))
    self.assertEqual(got,ref);self.assertEqual(len(got),32);self.assertFalse(meta['stock_scale_qualified'])
 def test_ties_away_zero(self):
  got,_=adapt32(([-3,-1,1,3]*8),shift=-1,clip_limit=100)
  self.assertEqual(got[:4],[-2,-1,1,2])
 def test_explicit_symmetric_clipping(self):
  got,meta=adapt32(([-8388608,8388607]*16),shift=2,clip_limit=1<<21)
  self.assertEqual(got,[-(1<<21),1<<21]*16);self.assertEqual(meta['clipped_samples'],32)
 def test_invalid_block_length(self):
  with self.assertRaises(ValueError):adapt32([0]*33,shift=0,clip_limit=1)
 def test_invalid_word(self):
  with self.assertRaises(ValueError):adapt32([0]*31+[8388608],shift=0,clip_limit=1)
 def test_no_implicit_parameters(self):
  with self.assertRaises(TypeError):adapt32([0]*32)
 def test_hardware_and_RAM_gate_closed(self):
  r=readiness();self.assertFalse(r['hardware_access']);self.assertFalse(r['integration']);self.assertFalse(r['persistent_RAM_safety'])
if __name__=='__main__':unittest.main()
