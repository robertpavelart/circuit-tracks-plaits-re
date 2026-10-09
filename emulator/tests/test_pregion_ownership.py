"""Focused P-region arithmetic and source/refusal contracts; no CPU/hardware."""
import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ct_pregion_audit import LO,HI,LOAD_END,CODE_LIMIT,dma_registers,decode_dcr,counter_a_interval,overlap,data_pc,obj

class PRegionOwnership(unittest.TestCase):
    def test_one_seven_word_candidate(self):
        self.assertEqual((LO,HI),(0x3ff0,0x3ff7));self.assertEqual(HI-LO,7)
        self.assertEqual(LO%16,0)
        self.assertLessEqual(LOAD_END,0x4000)
        self.assertEqual(LO-(CODE_LIMIT+2),2)
        self.assertEqual(LOAD_END-HI,2)

    def test_loader_framing_without_image_construction(self):
        self.assertEqual(6+3*LOAD_END,49137)
        self.assertEqual(LOAD_END+2,0x3ffb)
        self.assertLessEqual(LOAD_END,0xfffd)
        self.assertFalse(overlap(0,0x2a5e))
        self.assertTrue(overlap(0,LOAD_END))

    def test_all_eight_dma_register_sets(self):
        r=dma_registers();self.assertEqual(len(r),32)
        self.assertEqual(r[0xffffec],(0,'DCR'))
        self.assertEqual(r[0xffffee],(0,'DDR'))
        self.assertEqual(r[0xffffeb],(1,'DSR'))
        self.assertEqual(r[0xffffd0],(7,'DCR'))
        self.assertEqual(r[0xffffd2],(7,'DDR'))

    def test_recovered_audio_dma_is_not_P(self):
        for value,dest,src,drs in [(0x285ac4,1,0,11),(0x286251,0,1,12)]:
            d=decode_dcr(value)
            self.assertEqual(d['DDS'],dest);self.assertEqual(d['DSS'],src)
            self.assertEqual(d['DRS'],drs);self.assertEqual(d['DTM'],5)
            self.assertEqual(d['D3D'],0)
            self.assertEqual(decode_dcr(value|0x800000)['DE'],1)
            self.assertNotEqual(dest,2)

    def test_DMA_literal_transfer_arithmetic(self):
        self.assertEqual(counter_a_interval(0x29,2,5),[(0x29,0x2c)])
        self.assertEqual(counter_a_interval(0xffffa4,2,4),[(0xffffa4,0xffffa5)])
        self.assertEqual(counter_a_interval(LO,6,5),[(LO,HI)])
        self.assertEqual(counter_a_interval(0xffffff,1,5),[(0xffffff,0x1000000),(0,1)])
        with self.assertRaises(ValueError):counter_a_interval(LO,2,0)

    def test_proximity_is_not_overlap(self):
        self.assertFalse(overlap(LO-2,LO));self.assertFalse(overlap(HI,HI+2))
        self.assertTrue(overlap(LO,LO+1));self.assertTrue(overlap(HI-1,HI))

    def test_service_values_cannot_enable_P_DMA(self):
        # Both recovered op0 paths: private sends0; shared sendsconsumedbyte<<8.
        for byte in range(256):
            for word in [0,byte<<8]:
                self.assertEqual(decode_dcr(word)['DDS'],0)
                self.assertEqual(decode_dcr(word)['DE'],0)

    def test_paged_SHI_is_not_the_extended_mask(self):
        initial=((0xffff<<8)-2)&0xffffff
        self.assertEqual(initial,0xfffefe)
        for a in dma_registers():
            n=a-initial;self.assertGreaterEqual(n,0)
            self.assertEqual((initial+n)&0xffffff,a)
        # Necessary equations only: no normal sourcepage/context witness seeded.
        self.assertLessEqual(0x3ffff,0xffffd0)

    def test_vector_slot_exclusion_for_any_VBA(self):
        # FM101 forceslow8zero. OverapproximatevalidRM115 slots (andsecondword)
        # by all0..BF plusFC..FF; none ofF0..F6 appears. NoVBA seeded.
        offsets=set(range(0xc0))|set(range(0xfc,0x100))
        self.assertFalse(offsets&{a&255 for a in range(LO,HI)})

    def test_phantom_P_store_is_known_data(self):
        self.assertTrue(data_pc(0x28de))
        self.assertFalse(data_pc(0x28d9))
        self.assertTrue(data_pc(0x2309));self.assertFalse(data_pc(0x2304))

    def test_previous_runtime_count_domain_stays_unknown(self):
        schema=obj('builds/phase19c-p204b/final-v4/record-schema.json')
        self.assertIsNone(schema['normal_positive_min']);self.assertIsNone(schema['normal_positive_max'])
        self.assertFalse(schema['fields'][4]['all_writer_reader_closure'])
        self.assertTrue(schema['unindexed_store'])

    def test_numeric_pass_is_not_stock_allocation(self):
        old=obj('builds/phase20c-pstate/final-v4/qualification.json')
        self.assertTrue(old['all_seven_states_exact'])
        self.assertEqual(old['owned_stock_P_words'],0)
        self.assertFalse(old['firmware_integration_ready'])

if __name__=='__main__':unittest.main()
