"""Focused provenance/admission regressions. No stock CPU or hardware execution."""
import csv,json,os,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'plaits/seam/inputrec'))
import recover
REPORT=Path(os.environ.get('CT_INPUTREC_REPORT',str(ROOT/'builds/phase20b-inputrec/final-v3')))
def obj(n):return json.loads((REPORT/n).read_text())
def rows(n):
 with (REPORT/n).open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
class InputRecordTests(unittest.TestCase):
 def test_bank_reads_cover_exact37_words(self):
  r=recover.bank_reads();self.assertEqual([v['address'] for v in r],list(range(0x2d5,0x2fa)))
  self.assertEqual(next(v['address'] for v in r if v['P']=='6D4'),0x2e7)
  self.assertEqual(next(v['address'] for v in r if v['P']=='6DF'),0x2e9)
 def test_modulation_lookahead_is_retained(self):
  r=recover.stream_accesses(20);self.assertEqual(len(r),105)
  self.assertEqual([v['address'] for v in r[-4:]],[0x35f,0x360,0x361,0x362])
  self.assertEqual(recover.stream_accesses(1)[-1]['address'],0x303)
  with self.assertRaises(ValueError):recover.stream_accesses(0)
 def test_real_routes_write_Y91_input(self):
  r=rows('modulation-provenance.csv')
  self.assertEqual([int(v['slot']) for v in r if v['destination_Y']=='91'],[0,2])
  self.assertEqual({v['destination_Y'] for v in r},{'7C','91'})
  self.assertEqual((r[0]['source1_Y'],r[0]['source2_Y'],r[2]['source1_Y']),('17C','17C','126'))
 def test_zero_depth_is_not_assumed_after_correction(self):
  r=rows('modulation-provenance.csv');self.assertEqual(r[1]['nominal_depth'],'0')
  self.assertTrue(all(v['amount_DSP_value']=='' for v in r))
  f=obj('patch-field-values.json')['fields']
  self.assertTrue(all(next(v for v in f if v['ID']==i)['corrected_value'] is None for i in [31,34,35,36,38,96,100,104]))
 def test_same_name_project_is_not_exact_binding(self):
  r=obj('selected-note-event.json');self.assertIsNone(r['event']);self.assertIsNone(r['note'])
  p=r['existing_project_candidates'][0];self.assertEqual(p['name_offset'],158996)
  self.assertEqual([v['offset'] for v in p['candidate_differences']],[35,221,238,255,272,289,306])
  self.assertTrue(all(v['exact340_offset']==-1 for v in r['existing_project_candidates']))
 def test_retained_histories_outside_trigger_ranges(self):
  for r in rows('history-provenance.csv'):
   a=int(r['field'].split(':')[1],16);self.assertFalse(0x5af<=a<0x5b7 or 0x5bd<=a<0x5c5)
   self.assertEqual(r['value'],'');self.assertEqual(r['last_writer_before_invocation'],'UNRESOLVED')
 def test_no_fabricated_coefficients_or_modes(self):
  self.assertTrue(all(v is None for v in obj('coefficient-values.json')['words'].values()))
  r=obj('arithmetic-context.json');self.assertIsNone(r['SR']['SM']['value']);self.assertIsNone(r['OMR']['value'])
 def test_refuse_one_material_blocker_before_cpu(self):
  self.assertFalse(recover.gate([dict(qualified=True),dict(qualified=False)])['admitted'])
  with self.assertRaises(ValueError):recover.gate([dict(qualified=True)])
  r=obj('selected-checkpoint.json');self.assertIsNone(r['PC']);self.assertFalse(r['admitted'])
 def test_no_traces_or_Plaits_claims(self):
  for d in ['preparation-traces','stock-seam-traces']:
   r=obj(d+'/refusal.json');self.assertFalse(r['executed']);self.assertEqual(r['CPU_instructions'],0);self.assertIsNone(r['cycles'])
  r=obj('validation.json');self.assertFalse(r['Plaits_fed_justified']);self.assertFalse(r['Phase20B_resume_numeric_replay'])
 def test_matrix_keeps_expected_fields_conditional(self):
  r={v['field']:v for v in rows('seam-admission-matrix.csv')}
  for field,val in [('X:5AB','0'),('X:5AC','1'),('X:5B1','5'),('X:5B2','5')]:
   self.assertEqual(r[field]['value'],val);self.assertEqual(r[field]['qualified'],'False')
if __name__=='__main__':unittest.main()
