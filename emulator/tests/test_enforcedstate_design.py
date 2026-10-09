"""Design-spec boundary/refusal tests. No DSP guard or CPU is executed."""
import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ct_enforcedstate_design import (P_STATE,X_STATE,TMP,POLICY,SHADOW,FAULT,CODE_END,
    contains,cpu_commit_spec,dma_spec,quiescent_spec,jclr_classifier_cycles,fresh,obj)
from ct_pregion_audit import decode_dcr
from ct_livepatch_design import original_rows

class EnforcedStateDesign(unittest.TestCase):
    def test_seven_word_half_open_endpoints(self):
        for domain,space,span in [('P','P',P_STATE),('X','X',X_STATE)]:
            self.assertEqual(span[1]-span[0],7)
            for a in range(span[0],span[1]):
                self.assertEqual(cpu_commit_spec(space,a,domain),'DENY_STOCK')
            for a in [span[0]-1,span[1]]:
                self.assertEqual(cpu_commit_spec(space,a,domain),'PASS_IN_SPEC')

    def test_equal_integer_is_not_equal_memory_space(self):
        for a in range(*P_STATE):
            self.assertEqual(cpu_commit_spec('X',a,'P'),'PASS_IN_SPEC')
            self.assertEqual(cpu_commit_spec('Y',a,'P'),'PASS_IN_SPEC')
        for a in range(*X_STATE):
            self.assertEqual(cpu_commit_spec('Y',a,'X'),'PASS_IN_SPEC')

    def test_long_memory_requires_component_checks(self):
        self.assertEqual(cpu_commit_spec('L',X_STATE[0],'X'),'REQUIRE_SPLIT_X_Y_COMPONENTS')
        self.assertEqual(cpu_commit_spec('X',X_STATE[0],'X'),'DENY_STOCK')

    def test_control_page_and_invalid_inputs_fail_closed(self):
        for a in [0xFFF000,0xFFFFD0,0xFFFFEC,0xFFFFFF]:
            self.assertEqual(cpu_commit_spec('X',a,'P'),'CONTROL_ADMISSION')
        for s,a,d in [('Z',0,'P'),('X',-1,'P'),('X',0x1000000,'P'),('P',0,'Z')]:
            self.assertEqual(cpu_commit_spec(s,a,d),'DENY_INVALID_SPEC_INPUT')

    def test_every_DMA_channel_rejects_P_and_reserved_spaces(self):
        # Enumerate all source/destination-space combinations; DE does not
        # turn an unsafe configuration into an admissible one.
        for ch in range(8):
            for src in range(4):
                for dest in range(4):
                    for de in [0,1]:
                        r=dma_spec((de<<23)|(dest<<2)|src,ch)
                        if 3 in [src,dest]:self.assertEqual(r,'DENY_RESERVED_SPACE')
                        elif 2 in [src,dest]:self.assertEqual(r,'DENY_P_DMA_DURING_EPOCH')

    def test_pinned_audio_profile_and_uncertified_other_channels(self):
        for ch,v in [(0,0x285AC4),(1,0x286251)]:
            for de in [0,0x800000]:
                self.assertEqual(dma_spec(v|de,ch),'CONDITIONAL_NONP_CONFIG_REVIEW')
            self.assertEqual(dma_spec(v^0x100,ch),'DENY_AUDIO_PROFILE_CHANGE')
        for ch in range(2,8):
            self.assertEqual(dma_spec(0,ch),'CONDITIONAL_NONP_CONFIG_REVIEW')
        self.assertEqual(dma_spec(0,8),'DENY_INVALID_SPEC_INPUT')

    def test_DE_clear_alone_is_not_quiescence(self):
        self.assertTrue(quiescent_spec([0]*8,[1]*8,0))
        for ch in range(8):
            de=[0]*8;de[ch]=1
            self.assertFalse(quiescent_spec(de,[1]*8,0))
            dtd=[1]*8;dtd[ch]=0
            self.assertFalse(quiescent_spec([0]*8,dtd,0))
        self.assertFalse(quiescent_spec([0]*8,[1]*8,1))

    def test_missing_channel_snapshot_cannot_admit_epoch(self):
        self.assertFalse(quiescent_spec([],[],0))
        self.assertFalse(quiescent_spec([0]*7,[1]*7,0))
        self.assertFalse(quiescent_spec([0]*8,[1]*9,0))

    def test_bit_branch_false_penalty_is_not_dropped(self):
        self.assertEqual(jclr_classifier_cycles(0),4)
        self.assertEqual(jclr_classifier_cycles(0xFFF000),60)
        self.assertEqual(jclr_classifier_cycles(0xFFEFFF),59)
        self.assertEqual(jclr_classifier_cycles(0xFFFFFF),60)
        with self.assertRaises(ValueError):jclr_classifier_cycles(0x1000000)

    def test_proposed_frames_are_disjoint_and_not_free_memory_claims(self):
        spans=[POLICY,SHADOW,TMP,FAULT,P_STATE]
        for i,(a,b) in enumerate(spans):
            self.assertLess(a,b);self.assertGreater(a,CODE_END+1)
            for c,d in spans[i+1:]:self.assertGreaterEqual(max(a,c),min(b,d))
        self.assertEqual(sum(b-a for a,b in spans),102)
        self.assertEqual(TMP[1]-TMP[0],26+3+3)
        self.assertFalse(contains(P_STATE,FAULT[0]))

    def test_hardware_stack_cannot_hold_bounded_save_set_and_caller(self):
        minimum_paired=(26+1)//2
        self.assertEqual(minimum_paired+3,16)
        self.assertGreater(minimum_paired+3+1,16)

    def test_single_count_schema_cannot_disable_one_record(self):
        s=obj('builds/phase19c-p204b/final-v4/record-schema.json')
        self.assertIsNone(s['normal_positive_max'])
        rows=original_rows()
        self.assertEqual(rows[0x203A]['instruction'],'move x:(r0)+,x1')
        self.assertTrue(rows[0x2040]['instruction'].startswith('do x1,'))
        self.assertEqual(rows[0x204B]['instruction'],'move b,x:(r4)')

    def test_clean_whole_function_and_service_entry_windows(self):
        rows=original_rows()
        self.assertEqual(rows[0x202B]['words'],2)
        self.assertEqual(rows[0x2070]['instruction'],'rts')
        self.assertEqual(0x2071-0x202B,70)
        self.assertEqual(rows[0x198]['words'],1)
        self.assertEqual(rows[0x199]['words'],2)
        self.assertEqual(rows[0x19D]['instruction'],'move x0,x:(r0)+')

    def test_output_pointer_must_be_changed_inside_renderer(self):
        asm=(ROOT/'builds/phase20c-pstate/high-p-v7/program.asm').read_text()
        self.assertIn('move #>$000000,r0',asm)
        self.assertEqual(original_rows()[0x9D9]['instruction'],'move y:$0007,r0')

    def test_partial_costs_are_not_complete_bound(self):
        self.assertEqual(549+104+10+16+32+1,712)
        self.assertEqual(712+89+37+28,866)
        self.assertEqual(866+256+96+128+64+216,1626)
        self.assertEqual(CODE_END-0x2A5E,5374)
        self.assertGreater(344*24,5374)
        self.assertEqual(13379+1964+5*81*33+416+4+21*20,29548)

    def test_old_numeric_qualification_is_not_enforced_ownership(self):
        q=obj('builds/phase20c-pstate/final-v4/qualification.json')
        self.assertTrue(q['all_seven_states_exact'])
        self.assertEqual(q['owned_stock_P_words'],0)
        self.assertFalse(q['firmware_integration_ready'])

    def test_output_refusal_is_before_any_write(self):
        with self.assertRaises(ValueError):fresh(ROOT/'original')
        with self.assertRaises(ValueError):fresh(ROOT/'builds/phase20c-enforcedstate')
        with self.assertRaises(ValueError):fresh(ROOT/'builds/phase20c-enforcedstate/probe-v1')

if __name__=='__main__':unittest.main()
