"""Targeted static provenance tests; no CPU, device or preset synthesis."""
import unittest,sys,json,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'plaits/seam/checkpoint'))
import recover

class CheckpointTests(unittest.TestCase):
 def test_selected_pair_file_values(self):
  r=json.loads((ROOT/'builds/phase20b-checkpoint/final/selected-context.json').read_text())
  self.assertEqual([r['fixed_post_mode'],r['fixed_nonlinear_selector'],r['filter_pair_index']],[0,1,1])
  self.assertIsNone(r['instantiated_DSP_checkpoint'])
 def test_offsets_have_real_sources(self):
  rr=list(csv.DictReader((ROOT/'builds/phase20b-checkpoint/final/address-offset-provenance.csv').open()))
  self.assertEqual([int(r['offset_words']) for r in rr],[5,5])
  self.assertEqual([r['DSP_bank_source'] for r in rr],['X:0x2AC','X:0x2AD'])
  self.assertTrue(all(r['R5']=='0xF64' and r['target_space']=='Y' for r in rr))
 def test_all_kernel_coefficient_addresses(self):
  for offset in [5,10,20,25]:
   rr=recover.sequence_reads(0xf5f+offset)
   self.assertEqual(len(rr),161)
   self.assertEqual({r['address'] for r in rr},set(range(0xf5f+offset,0xf5f+offset+5)))
 def test_reverse_map_not_wrong_literal(self):
  r=json.loads((ROOT/'builds/phase20b-checkpoint/final/reverse-index-provenance.json').read_text())
  self.assertEqual(r['selector_IDs'],{'30':255,'32':255,'33':255})
  self.assertTrue(all(v not in r['IDs'] for v in [30,32,33]))
 def test_runtime_history_not_boot_zero(self):
  rr=list(csv.DictReader((ROOT/'builds/phase20b-checkpoint/final/coefficient-provenance.csv').open()))
  for r in rr:
   if r['field'] in ['Y:5AB','Y:5AE']:self.assertEqual(r['candidate_value'],'');self.assertEqual(r['value_status'],'UNRESOLVED')
 def test_checkpoint_stays_refused(self):
  r=json.loads((ROOT/'builds/phase20b-checkpoint/final/checkpoint-admission.json').read_text())
  self.assertEqual(r['result'],'REFUSED');self.assertEqual(r['phase_provenance_result'],'PARTIAL')
  self.assertFalse(r['admitted']);self.assertGreater(len(r['category_E_material']),0)
 def test_no_reset_stack(self):
  r=json.loads((ROOT/'builds/phase20b-checkpoint/final/stack-loop-state.json').read_text())
  for k in ['SC','prefix','LA','LC','LF','FV']:self.assertIsNone(r[k])
 def test_no_fake_trace_or_cycle_measurements(self):
  root=ROOT/'builds/phase20b-checkpoint/final'
  for d in ['upstream-trace','stock-seam-trace']:
   r=json.loads((root/d/'refusal.json').read_text());self.assertFalse(r['executed']);self.assertEqual(r['instructions'],0)
  for r in csv.DictReader((root/'stock-seam-cycles.csv').open()):self.assertEqual(r['cycles'],'')
 def test_no_Plaits_resume(self):
  r=json.loads((ROOT/'builds/phase20b-checkpoint/final/validation.json').read_text())
  self.assertFalse(r['Plaits_fed_justified']);self.assertFalse(r['Phase20B_resume_numeric_replay'])
if __name__=='__main__':unittest.main()
