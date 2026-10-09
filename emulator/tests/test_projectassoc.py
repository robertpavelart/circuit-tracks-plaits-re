"""Offline source equivalence/correction regressions, no firmware execution."""
import csv,json,os,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'plaits/seam/projectassoc'))
import recover
REPORT=Path(os.environ.get('CT_PROJECTASSOC_REPORT',str(ROOT/'builds/phase20b-projectassoc/final-v2')))
def obj(n):return json.loads((REPORT/n).read_text(encoding='utf8'))
def rows(n):
 with (REPORT/n).open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
class ProjectAssociationTests(unittest.TestCase):
 def test_seven_fields_not_name_metadata(self):
  r=rows('patch-byte-differences.csv');self.assertEqual([int(v['offset']) for v in r],[35,221,238,255,272,289,306])
  self.assertEqual(r[0]['field'],'settings.keyboardOctave')
  self.assertEqual([v['classification'] for v in r],['F']+['E']*6)
  self.assertEqual([int(v['descriptor_ID']) for v in r],[5,191,208,225,242,259,276])
 def test_stored_macro_values_are_not_event_snapshot(self):
  r=obj('macro-state.json')['macros']
  self.assertEqual([v['cached_stored'] for v in r],[0,126,11,84,51,58,73,0])
  self.assertTrue(all(v['active_event_value'] is None for v in r))
  self.assertEqual([v['authored_stored'] for v in r],[0,0,46,83,0,0,48,0])
 def test_independent_model_all_selected_assignment_domains(self):
  count=0
  for m in obj('macro-state.json')['macros']:
   for sub in m['subslots']:
    r=sub['authored']
    for value in range(128):
     self.assertEqual(recover.original_term(value,r['start'],r['end'],r['encoded_depth']),
      recover.independent_term(value,r['start'],r['end'],r['encoded_depth']));count+=1
  self.assertEqual(count,4096)
 def test_rounding_negative_contributions(self):
  self.assertEqual(recover.original_term(1,0,127,63),0)
  self.assertEqual(recover.original_term(126,0,127,63),-1)
  self.assertEqual(recover.original_term(127,0,127,63),-2)
  self.assertEqual(recover.original_term(11,12,109,105),0)
 def test_full_vectors_changed_eight_destinations(self):
  r=rows('macro-corrections.csv')
  self.assertEqual([int(v['destination']) for v in r if v['relation']!='IDENTICAL'],[18,21,22,25,27,31,33,46])
  d={int(v['parameter_ID']):v for v in r}
  self.assertEqual((d[36]['authored_corrected'],d[36]['cached_corrected']),('2','44'))
  self.assertEqual((d[38]['authored_corrected'],d[38]['cached_corrected']),('97','83'))
 def test_two_concrete_nonconvergent_transfers(self):
  r={v['field']:v for v in rows('control-boundary.csv')}
  self.assertEqual((r['X:2E8']['authored_DSP'],r['X:2E8']['cached_DSP']),('020408','2C58B1'))
  self.assertEqual((r['X:2EA']['authored_DSP'],r['X:2EA']['cached_DSP']),('1C0000','0CAAAA'))
  self.assertEqual(r['X:2E7']['authored_DSP'],r['X:2E7']['cached_DSP'])
  self.assertEqual((r['X:3E7']['authored_DSP'],r['X:3E7']['cached_DSP']),('19B6AA','2FB6AA'))
 def test_partial_update_does_not_restore_authored_bytes(self):
  r=obj('patch-identity.json');self.assertEqual(r['literal_ID_bytes'],[0,32]);self.assertIsNone(r['pack_ID'])
  self.assertTrue(obj('validation.json')['partial_update_merges_to_cached_patch'])
 def test_literal_pattern_bytes_not_fabricated_notes(self):
  r=obj('selected-event.json');self.assertFalse(r['qualified'])
  for key in ['event','note','velocity','gate','length','voice_slot','macro_values','automation']:self.assertIsNone(r[key])
  self.assertEqual(len(r['unqualified_layout_candidate']['raw28']),28)
 def test_row_literals_equal_does_not_close_Y91(self):
  r=obj('y91-provenance.json');self.assertTrue(r['row_literals_identical']);self.assertIsNone(r['value'])
  self.assertEqual(r['amount_target_words'],['31FFCE','02AAA8']);self.assertIsNone(r['smoothed_amount_values'])
 def test_macro_clear_not_history_clear(self):
  r=obj('history-opportunity.json');self.assertFalse(r['macro_work_clear_is_DSP_history_clear'])
  self.assertIsNone(r['nearest_qualified_origin']);self.assertIsNone(r['history_values'])
 def test_event_admission_rejects_partial_or_material_difference(self):
  for equivalence in ['MATERIALLY DIFFERENT','INSUFFICIENT EVIDENCE']:
   self.assertFalse(recover.admit(equivalence,True,True))
  self.assertFalse(recover.admit('MATERIALLY EQUIVALENT',False,True))
  self.assertFalse(recover.admit('MATERIALLY EQUIVALENT',True,False))
 def test_no_replay_promotion(self):
  r=obj('qualification.json');self.assertEqual(r['overall_status'],'PARTIAL');self.assertFalse(r['event_usage_admitted'])
  self.assertEqual(r['stock_instructions_executed'],0);self.assertFalse(r['stock_seam_replay']);self.assertFalse(r['Plaits_fed'])
if __name__=='__main__':unittest.main()
