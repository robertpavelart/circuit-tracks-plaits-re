"""Offline design invariants, no hardware/capture/firmware execution."""
import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import ct_snapshot_design as d
class DesignChecks(unittest.TestCase):
    def test_all_architectural_registers_classified(self):
        fields={r['field']:r for r in d.live_fields()}
        for group in ['R','N','M']:
            for i in range(8): self.assertIn(f'{group}{i}',fields)
        for f in ['PC','SR','OMR','A','B','X0','X1','Y0','Y1','SP','SC','LA','LC','LF','FV']:self.assertIn(f,fields)
        self.assertEqual(fields['R4']['classification'],'A');self.assertEqual(fields['R0']['classification'],'D')
    def test_dead_fields_do_not_mean_guessed_constants(self):
        fields={r['field']:r for r in d.live_fields()}
        self.assertEqual(fields['Y:[8F,92)']['classification'],'D')
        self.assertIn('modifier',fields['Y:[F64,F69)']['condition'])
        self.assertIn('CONTENTS require capture',fields['X normalization table']['reason'])
    def test_minimum_stride_and_ranges(self):
        self.assertEqual(0x57b+0x30,0x5ab);self.assertEqual(0x59f+0x0c,0x5ab)
        self.assertNotEqual(0x4a,0x28);self.assertEqual(0x38-0x30+0x43-0x40,11)
        self.assertEqual(0x1a-0x0c,14)
        self.assertEqual(0x59f+0x1a,0x5b9)
    def test_methods_do_not_invent_arm_visibility(self):
        rows={r['method']:r for r in d.mechanisms()}
        self.assertEqual(rows['MCU SWD/JTAG alone']['DSP_registers'],'NO')
        self.assertEqual(rows['stock5E read service alone']['hardware_stack'],'NO')
        self.assertIn('UNRESOLVED',rows['stock5E read service alone']['evidence'])
    def test_schema_required_fields_are_defined(self):
        schema=d.format_schema()
        def walk(v):
            if isinstance(v,dict):
                if 'required' in v:self.assertTrue(set(v['required'])<=set(v.get('properties',{})))
                for x in v.values():walk(x)
            elif isinstance(v,list):
                for x in v:walk(x)
        walk(schema)
        self.assertEqual(schema['properties']['normalized_entry_pc']['const'],'0009D9')
        self.assertEqual(schema['properties']['stop_before_pc']['const'],'000A95')
    def test_raw_accumulator_encoding(self):
        schema=d.format_schema()['$defs']['registers']['properties']
        self.assertIn('{14}',schema['A']['anyOf'][0]['pattern'])
        self.assertEqual(schema['SC']['pattern'],'^[0-9A-F]{6}$')
    def test_no_unknown_material_admission(self):
        a=d.format_schema()['properties']['admission']['properties']
        self.assertEqual(a['unknown_material_fields']['maxItems'],0)
        self.assertTrue(a['values_are_observed']['const'])
    def test_all_overwrites_and_escape_refused(self):
        for p in [d.BASE,ROOT/'original',ROOT/'notes']:
            with self.assertRaises(ValueError):d.run(p)
if __name__=='__main__':unittest.main()
