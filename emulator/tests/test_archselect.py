"""Phase20C6 source/contract tests, never execute DSP or construct a patch."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ct_archselect import state_map,candidates,liveness,sites,fresh,obj
from ct_livepatch_design import original_rows,save_registers

class ArchSelect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=original_rows();cls.m=state_map()
    def test_complete_nominal_selected_regions_and_no_duplicates(self):
        self.assertEqual(len(self.m),552)
        pairs={(r['space'],int(r['address'],16)) for r in self.m}
        self.assertEqual(len(pairs),552)
        for space,a,b in [('X',0xEB,0xF3),('X',0x57A,0x5C4),('Y',0x11F,0x17F),('Y',0x59F,0x5C7)]:
            self.assertTrue(all((space,n) in pairs for n in range(a,b)))
    def test_word_roles_do_not_imply_ownership(self):
        allowed={'MUST RETAIN','GENERATOR-ONLY','AUXILIARY-ONLY','ALLOCATOR-OWNED','POST-OWNED','SHARED','UNKNOWN'}
        self.assertTrue(all(r['classification'] in allowed for r in self.m))
        self.assertFalse(any(r['takeover_ownership_qualified'] for r in self.m))
    def test_mailbox_timestamp_and_post_tail_not_surrendered(self):
        m={(r['space'],int(r['address'],16)):r for r in self.m}
        self.assertEqual(m['X',0x57A]['classification'],'MUST RETAIN')
        self.assertEqual(m['X',0x5C2]['classification'],'ALLOCATOR-OWNED')
        self.assertEqual(m['X',0x5C3]['classification'],'UNKNOWN')
        for a in range(0x5AB,0x5BF):self.assertEqual(m['X',a]['classification'],'POST-OWNED')
    def test_X_Y_equal_address_not_one_reclaimed_word(self):
        m={(r['space'],int(r['address'],16)):r for r in self.m}
        self.assertEqual(m['X',0x5A1]['classification'],'GENERATOR-ONLY')
        self.assertIn('interpolation10',m['X',0x5A1]['role'])
        self.assertIn('mask/mode',m['Y',0x5A1]['role'])
    def test_nominal_kernel_is_not_full_kernel_write_extent(self):
        self.assertEqual(self.r[0x3B5]['instruction'],'move #$90,n2')
        self.assertEqual(self.r[0x3BB]['instruction'],'move (r2)+n2,r2')
        self.assertEqual(self.r[0x3BF]['instruction'],'move x:(r2+n2),x0')
        self.assertEqual(self.r[0x3C2]['instruction'],'move a,x:(r2)+')
        self.assertEqual(0x1960+0x90,0x19F0)
        self.assertEqual(0x1960+2*0x90,0x1A80)
        self.assertEqual(self.r[0x97B]['instruction'],'move x:(r3+144),y0')
    def test_six_field_thinning_not_seven_word_certificate(self):
        c=candidates();self.assertEqual(len(c),84)
        self.assertFalse(any(r['qualified'] for r in c))
        thin=[int(r['address'],16) for r in c if r['proposed_takeover'].startswith('last-lane')]
        self.assertEqual(thin,[0x597,0x598,0x5A1,0x5A2,0x5A3,0x5A4])
    def test_auxiliary_pre_add_and_two_lane_sum_cannot_use_mono_only(self):
        self.assertEqual(self.r[0x9C8]['instruction'],'mpy +y0,x0,a x:(r0)+,x0 y:(r7)+,y1')
        self.assertEqual(self.r[0x9C9]['instruction'],'mpy +x0,y1,b x:(r0)+,x1')
        self.assertEqual(self.r[0x9CA]['instruction'],'add b,a a,x:(r3)')
        self.assertEqual(self.r[0x9CD]['instruction'],'move a,x:(r5)+')
    def test_guard_store_is_outside_final_mono_combiner(self):
        self.assertEqual(0x2C46+2*16,0x2C66)
        self.assertEqual(0x2C46+32,0x2C66)
        self.assertEqual(self.r[0x7F1]['instruction'],'add y0,a a1,x:(r2)+')
        old=obj('builds/phase20c-livepatch-design/final-v2/guard-tail-analysis.json')
        self.assertFalse(old['combiner_writes_guard'])
    def test_two_passes_and_natural_continuation(self):
        self.assertEqual(self.r[0x7F7]['instruction'],'jcs >$07fa')
        self.assertEqual(self.r[0x7F9]['instruction'],'move a1,y:(r4)')
        self.assertEqual(self.r[0x19E6]['instruction'],'jsr $077f')
        self.assertEqual(self.r[0x9B8]['instruction'],'move r0,y:$0007')
        self.assertEqual(self.r[0x9D9]['instruction'],'move y:$0007,r0')
    def test_same_post_boundary_does_not_prove_smaller_B_save_set(self):
        l=liveness(self.r)
        self.assertEqual(sum(r['saved_in_both'] for r in l),26)
        self.assertTrue(all(r['A_classification']==r['B_classification'] for r in l))
        self.assertEqual(len(save_registers()),26)
        self.assertNotIn('R0',save_registers())
    def test_foreground_dead_A_is_not_full_IRQ_caller_closure(self):
        l={r['field']:r for r in liveness(self.r)}
        self.assertIn('IRQ',l['A0']['A_classification'])
        self.assertEqual(self.r[0x9DD]['instruction'],'move x:(r0)+,a')
        self.assertEqual(self.r[0x168]['instruction'],'move a0,y:$2003')
    def test_origins_reviews_and_unknown_sets_not_one_site_count(self):
        m=sites(self.r)
        self.assertEqual(sum(r['architecture']=='A' and r['count_kind']=='KNOWN_ORIGIN_PROPOSED_EDIT' for r in m),5)
        self.assertEqual(sum(r['architecture']=='A' and r['count_kind']=='KNOWN_REVIEW_NO_EDIT' for r in m),10)
        self.assertEqual(sum(r['architecture']=='B' and r['count_kind']=='KNOWN_ANCHOR_NOT_FINITE_EDIT' for r in m),3)
        self.assertTrue(any(r['count_kind']=='UNRESOLVED_SITE_SET' for r in m))
    def test_existing_state_numeric_pass_not_patch_readiness(self):
        q=obj('builds/phase20c-pstate/final-v4/qualification.json')
        self.assertTrue(q['all_seven_states_exact']);self.assertEqual(q['owned_stock_P_words'],0)
        self.assertFalse(q['firmware_integration_ready'])
    def test_comparable_cost_subtotals_keep_unknown_glue(self):
        self.assertEqual(549+104+10+16+32+1+28,740)
        self.assertEqual(740+89+37,866)
        self.assertEqual(15343+5*18*33+416,18729)
        self.assertEqual(28708+416,29124)
    def test_outputs_refuse_original_base_or_existing_child(self):
        for p in [ROOT/'original',ROOT/'builds/phase20c-archselect',ROOT/'builds/phase20c-archselect/probe-v1']:
            with self.assertRaises(ValueError):fresh(p)

if __name__=='__main__':unittest.main()
