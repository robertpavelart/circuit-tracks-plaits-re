"""Offline design/source invariants; not an assembled patch or hardware test."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ct_livepatch_design import BASE,build,original_rows,renderer_census,plans,extension,lifetime_rows,save_registers,sender_schedule


class LivePatchDesign(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=original_rows();cls.sites,cls.model=renderer_census();cls.p=plans(cls.model)

    def test_complete_combiner_retained(self):
        self.assertEqual(0x9D9-0x9B9,32)
        self.assertEqual(sum(r['words'] for pc,r in self.rows.items() if 0x9B9<=pc<0x9D9),32)
        self.assertEqual(self.rows[0x9CA]['instruction'],'add b,a a,x:(r3)')
        self.assertEqual(self.rows[0x9CD]['instruction'],'move a,x:(r5)+')
        self.assertEqual(self.p['dispatcher-design.json']['stock_work_removed'],0)

    def test_request_fallback_and_continuation_not_skipped(self):
        d=self.p['dispatcher-design.json'];live=self.p['replacement-liveins.json']
        self.assertEqual(d['interception'],'P:0x9B9')
        self.assertTrue(live['request_work_required'])
        self.assertIn('9BB',d['fallback'])
        self.assertIn('original9D9',d['selected'])
        self.assertIn('bank0',d['eligibility']) if 'bank0' in d['eligibility'] else self.assertIn('XCC=0',d['eligibility'])

    def test_guard_not_invented_or_written(self):
        g=self.p['guard-tail-analysis.json']
        self.assertFalse(g['combiner_writes_guard'])
        self.assertIn('never2C66',g['replacement_writes'])
        self.assertIn('iteration16',g['selected_producer'])
        # phasepair32, first-trackword16*2 =32 => bufferstart+32 =guard.
        self.assertEqual(0x2C46+16*2,0x2C66)

    def test_fixed_state_not_promoted_free(self):
        s=self.p['state-placement.json']
        self.assertIsNone(s['persistent_X_base'])
        self.assertEqual(s['persistent_words'],7)
        self.assertEqual(s['total_data_words_with_conservative_wrapper'],39)
        self.assertFalse(s['addresses_reserved'])
        self.assertTrue(all(not r['persistent_safe'] for r in lifetime_rows()))

    def test_preservation_and_transient_partition(self):
        self.assertEqual(len(save_registers()),26)
        self.assertNotIn('R0',save_registers())
        s=self.p['state-placement.json'];t=s['transient_candidate']['proposed_layout']
        self.assertEqual(t['controls'][1],t['spills'][0])
        self.assertEqual(t['spills'][1],t['save26'][0])
        self.assertEqual(sum(b-a for a,b in t.values()),32)
        self.assertEqual(self.p['replacement-clobbers.json']['loop_extra_entries'],3)

    def test_relocated_size_not_standalone_cost(self):
        self.assertEqual(self.model['absolute_X_sites'],81)
        self.assertEqual(self.model['absolute_control_sites'],26)
        self.assertEqual(self.model['all_long_renderer_P'],549)
        self.assertEqual(sum(r['added_words'] for r in self.sites),107)
        self.assertGreater(self.model['conditional_relocated_renderer_upper'],13379)
        self.assertEqual(self.p['cycle-budget.json']['added_P_template'],713)
        self.assertIsNone(self.p['cycle-budget.json']['total_incremental_cycles'])

    def test_extension_collision_and_transport_bound(self):
        e=extension()
        self.assertEqual(e['maximum_conditional_extension'],5538)
        self.assertEqual(e['source_end'],e['following_stream_start'])
        self.assertEqual(e['max_new_stream_bytes'],49158)
        self.assertLessEqual(e['maximum_conditional_payload']+2,0x7FFF)
        self.assertFalse(e['patched_payload_emitted'])

    def test_unsigned_halfword_is_positive_32bit_compare(self):
        for n in [0x2A5E,0x4000,0x8000,0xFFFD]:
            chunks=sender_schedule(n)
            self.assertEqual(sum(c['word_count'] for c in chunks),n+2)
            self.assertTrue(all(0<c['word_count']<=0xAA and c['byte_count']<=510 for c in chunks))
            self.assertEqual(chunks[-1]['source_byte_offset']+chunks[-1]['byte_count'],3*(n+2))
        for n in [0xFFFE,0xFFFF]:
            with self.assertRaises(ValueError):sender_schedule(n)

    def test_independent_readiness_and_deferred_snapshot(self):
        r=self.p['poc-contract.json']['readiness']
        self.assertFalse(r['runtime_snapshot_required'])
        for k in ['code_placement_proven','state_placement_proven','offline_patched_image_construction_justified','flashing_justified']:
            self.assertFalse(r[k])
        self.assertIn('REFUSED',self.p['poc-contract.json']['prototype'])

    def test_overwrite_and_original_paths_refused(self):
        for p in [BASE,ROOT/'original',ROOT/'firmware']:
            with self.assertRaises(ValueError):build(p)


if __name__=='__main__':unittest.main()
