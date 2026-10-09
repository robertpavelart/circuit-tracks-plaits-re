"""Bounded ownership/refusal and arithmetic checks; never execute DSP firmware."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ct_fixedstate_audit import BASE,build,regions,sets,target_words,per_word_writers,readers,service_witness,layout,initialization,transient,fallback_design,nominal_host_projection


class FixedStateOwnership(unittest.TestCase):
    def test_tail_five_not_seven_and_next_slot(self):
        self.assertEqual(0x57A+0x45,0x5BF)
        self.assertEqual(0x57A+0x4A,0x5C4)
        self.assertEqual(0x5C4-0x5BF,5)
        self.assertEqual((0x57A+1)+71,0x5C2)
        self.assertEqual(0x5BF+7,0x5C6)

    def test_scratch_writer_domain_covers_every_seven_window(self):
        pairs=[0x2CCC+2*k+p for k in range(16) for p in range(2)]
        self.assertEqual(set(pairs),set(range(0x2CCC,0x2CEC)))
        cursor_writes=set(range(0x2CCC,0x2CEC))|set(range(0x2CEC,0x2D0C))
        for start in range(0x2CCC,0x2D0C-6):
            self.assertTrue(set(range(start,start+7))<=cursor_writes)
        self.assertEqual(len(range(0x2CCC,0x2D0C-6)),58)

    def test_known_writers_and_consumers_not_dead(self):
        self.assertTrue(any('73B' in r['PC'] for r in per_word_writers(0x5BF)))
        self.assertTrue(any('374' in r['PC'] for r in readers(0x5BF)))
        self.assertTrue(any('2DD' in r['PC'] for r in per_word_writers(0x5C2)))
        self.assertTrue(any('1BDB' in r['PC'] for r in readers(0x5C2)))
        self.assertTrue(any('08021A' in r['PC'] for r in per_word_writers(0x5C3)))

    def test_service_cache_independent_constructive_addressability(self):
        # Exhaust16-bit cache values for one target, plus both cases at every
        # watched cell. This tests arithmetic, not protocol/hardware execution.
        for cache in range(0x10000):
            w=service_witness(0x2CEC,cache)
            self.assertNotEqual(w['start'],cache)
            self.assertIn(0x2CEC,w['stores'])
        for a in target_words():
            for cache in [a,0xFFFF]:
                w=service_witness(a,cache)
                self.assertIn(a,w['stores']);self.assertEqual(w['stored_value'],0)

    def test_source_layout_exactly_seven_no_previous_phase_invented(self):
        x=layout()
        self.assertEqual(x['words'],7)
        self.assertEqual([r['original_X'] for r in x['fields']],list(range(0x20,0x27)))
        self.assertEqual([r['name'] for r in x['fields']],['phase','next','previous_pw','high','frequency','pw','shape'])
        self.assertTrue(x['no_separate_previous_phase'])
        self.assertEqual([r['exact_baseline_init'] for r in x['fields']],[0,0,0x200000,0,41943,0x200000,0])

    def test_frequency_sentinel_legal_ramp_is_positive(self):
        for c in [1,2,41943,0x100000]:
            for t in [1,2,41943,0x100000]:
                for k in range(33):self.assertGreaterEqual(c+(k*(t-c))//32,1)
        x=initialization()
        self.assertFalse(x['arbitrary_RAM_zero_assumption'])
        self.assertEqual(x['extra_persistent_flag_preferred'],0)
        self.assertIn('8 total',x['extra_flag_condition'])

    def test_no_candidate_qualified_no_short_free_block(self):
        for x in sets():
            self.assertEqual(len(x['words']),7);self.assertEqual(len(set(x['words'])),7)
            self.assertEqual(x['ranking'],'REJECTED')
            self.assertTrue(all(a>0x3F for a in x['words']))
        self.assertTrue(any(r['id']=='HIGH_X' and 'EXCLUDED' in r['pool_status'] for r in regions()))

    def test_temporary_is_independent_and_unproved(self):
        x=transient()
        self.assertFalse(x['allocated']);self.assertFalse(x['persistent_qualification'])
        self.assertEqual(sum(b-a for a,b in x['partition'].values()),32)
        self.assertIn('19D',x['asynchronous_blocker'])

    def test_exactly_two_fallbacks_neither_admitted(self):
        x=fallback_design({})
        self.assertIn('A',x);self.assertIn('B',x)
        self.assertFalse(x['images_or_firmware_modified'])
        self.assertEqual(x['B']['words'],7)
        self.assertEqual(x['B']['partial_module_data_total'],722)
        self.assertIn('not X',x['B']['space'])
        self.assertEqual(x['A']['conditional_X_example'],[0x57B,0x582])

    def test_nominal_scan_not_global_preservation_proof(self):
        x=nominal_host_projection()
        self.assertEqual(x['rows'],1500)
        self.assertIn('omits',x['supplement'])
        self.assertIn('no all-normal',x['limitation'])

    def test_overwrite_and_wrong_root_refused(self):
        for p in [BASE,ROOT/'original',ROOT/'firmware']:
            with self.assertRaises(ValueError):build(p)


if __name__=='__main__':unittest.main()
