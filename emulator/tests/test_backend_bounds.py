"""Offline contract arithmetic tests; no project files or metadata seeded."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
from ct_backend_bounds import name_index
from ct_asset_bounds import A0,MAX_ADV,first_residue,MOD
from ct_dsp_protocol import classify
class Contracts(unittest.TestCase):
 def test_decimal_index_domain(self):
  for i in range(64):self.assertEqual(name_index(f'{i:02d}_'.encode()),i)
 def test_three_digit_conversion_is_byte(self):
  for i in range(64):self.assertEqual(name_index(f'{256+i}_'.encode()),i)
 def test_prefix_rejection(self):
  for s in [b'',b'0_',b'AA_',b'00x',b'000x']:self.assertEqual(name_index(s),255)
 def test_private_last_y_setup(self):
  self.assertNotEqual((0xc03+1)&65535,0x802c)
  self.assertEqual(classify(bytes.fromhex('00802c'))['memory_space'],'Y')
 def test_page_retains_both_spaces(self):
  for space in ['X','Y']:
   self.assertEqual(classify(bytes.fromhex('105800'),saved_space=space)['memory_space'],space)
 def test_width_control_not_space_setup(self):
  for raw in ['200100','2000']:
   self.assertEqual(classify(bytes.fromhex(raw))['operation'],'control_mailbox')
 def test_no_first_two_critical_pages(self):
  for i in [0,1]:
   for residue in [0,256,0x900,0xa00]:
    self.assertIsNone(first_residue(A0+256*i,A0+MAX_ADV*i,residue))
 def test_later_predicate_envelope_not_normal_proof(self):
  for i in range(2,64):
   for residue in [0,256,0x900,0xa00]:
    self.assertEqual(first_residue(A0+256*i,A0+MAX_ADV*i,residue),MOD+residue)
if __name__=='__main__':unittest.main()
