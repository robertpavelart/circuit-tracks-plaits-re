"""Offline codec/address tests; no CPU, device or selector/target state seeded."""
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from ct_arm_init_cache import expand,recover
from ct_hostwrite_audit import intervals,hits,asset_advance,MOD,DESCRIPTORS


class HostWriteTests(unittest.TestCase):
    def test_original_initialized_cache(self):
        data,tokens,r=recover()
        self.assertEqual(len(data),0x3d02)
        self.assertEqual(data[0x3d00:0x3d02],b'\xff\xff')
        self.assertEqual(r['CPU_instructions_executed'],0)
        self.assertEqual(len(tokens),574)
        self.assertEqual(tokens[-1]['source_end'],2582)

    def test_literal_decrement_before_first_copy(self):
        data,_=expand(bytes([3,ord('A'),ord('B')]))
        self.assertEqual(data,b'AB')

    def test_backreference_overlap(self):
        data,_=expand(bytes([2,ord('A'),0x11,1]))
        self.assertEqual(data,b'AAAA')

    def test_refuse_truncation_and_unknown_read(self):
        for data in [bytes([3,1]),bytes([0x11,0]),bytes([0x11,8])]:
            with self.assertRaises(ValueError):expand(data)

    def test_begin_below_selector_crossing(self):
        self.assertNotIn('selectors',hits(intervals(0x959,1)))
        self.assertIn('selectors',hits(intervals(0x959,2)))

    def test_begin_below_table_crossing(self):
        self.assertNotIn('effect_table',hits(intervals(0x9da,1)))
        self.assertIn('effect_table',hits(intervals(0x9da,2)))

    def test_sparse_descriptor_cells(self):
        for i,a in enumerate(DESCRIPTORS):
            self.assertIn('descriptor'+str(i),hits(intervals(a,1)))
            if i<12:self.assertNotIn('descriptor'+str(i),hits(intervals(a+7,1)))

    def test_wrap_and_zero(self):
        self.assertEqual(intervals(MOD-2,4),[[MOD-2,MOD],[0,2]])
        self.assertEqual(intervals(3,0),[])
        self.assertEqual(intervals(3,MOD),[[0,MOD]])

    def test_width_is_not_destination_exclusion(self):
        self.assertIn('effect_table',hits(intervals(0x9db,1)))
        self.assertEqual((0xffff<<8)&0xff,0)

    def test_asset_advance_is_metadata_not_emitted_count(self):
        self.assertEqual(asset_advance(0),256)
        self.assertEqual(asset_advance(511),256)
        self.assertEqual(asset_advance(512),512)
        self.assertEqual(asset_advance(0xffffffff),0x80000000)


if __name__=='__main__':unittest.main()
