"""Pure arithmetic tests. No metadata records, emulated CPU or packets seeded."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
from ct_asset_bounds import *

class Bounds(unittest.TestCase):
 def test_predicate_bound(self):
  self.assertEqual(advance(MAX_L),0x927d00)
  with self.assertRaises(ValueError):advance(MAX_L+1)
 def test_invalid_not_length_driven(self):
  self.assertEqual(advance(0xffffffff,False),256)
  self.assertEqual(emitted(A0,0xffffffff,False),0)
 def test_guard_strict(self):
  self.assertEqual(emitted(LIMIT-1024,2048),0)
  self.assertEqual(emitted(LIMIT-1280,2048),1024)
 def test_partial_chunk_discontinuity(self):
  self.assertEqual(emitted(A0,MAX_L),0x8ffc00)
  self.assertEqual(emitted(A0,(LIMIT-A0-256)*2),0x8fff00)
 def test_page_truncation(self):
  self.assertEqual(page(0x1000000),0xfffffe)
  self.assertEqual(page(0x1000100),0xfe)
  self.assertEqual(page(A0),page(A0+MOD))
 def test_padding_wrap_exact(self):
  self.assertEqual(intervals(0xfffffe,256),[[0xfffffe,MOD],[0,0xfe]])
  self.assertTrue(intersect(intervals(0xfffffe,256),0xfb,0xfc))
  self.assertFalse(intersect(intervals(0xfffffe,256),0x103,0x104))
 def test_progression_no32wrap(self):
  self.assertEqual(A0+64*MAX_ADV,0x24f74000)
  self.assertLess(A0+64*MAX_ADV+1024,1<<32)
 def test_first_two_and_later_pages(self):
  self.assertIsNone(first_residue(A0+256,A0+MAX_ADV,0))
  self.assertEqual(first_residue(A0+512,A0+2*MAX_ADV,0),MOD)
  self.assertGreaterEqual(2*(MAX_ADV-256),MOD-256)
 def test_emission_against_instruction_loop(self):
  # Domain boundary/guard arithmetic only; no assignments to64 records.
  for a in [A0,LIMIT-2048,LIMIT-1024,LIMIT-256,LIMIT,MOD]:
   for l in [0,511,512,1536,2048,2560,4096,MAX_L]:
    left=(l&~511);r4=a;n=0
    while left:
     chunk=min(left,2048);end=(r4+chunk//2)&0xffffffff
     if end>=LIMIT:break
     r4=end;n+=chunk//2;left-=chunk
    self.assertEqual(emitted(a,l),n,(a,l))
if __name__=='__main__':unittest.main()
