"""Target-set/address-precision checks using immutable existing evidence only."""
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import ct_effect_target_bridge as audit


class TargetBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload,_=audit.verify_inputs()
        cls.words=[int.from_bytes(payload[i:i+3],'big') for i in range(0,len(payload),3)]
        cls.r=audit.rows(ROOT/'builds/phase3-selection0-channel0.asm',payload)
        cls.records=audit.enumerate_conditional(cls.words)

    def test_selector_boundary(self):
        self.assertEqual(audit.overlap(0x959,0x95a),[])
        self.assertEqual(audit.overlap(0x95a,0x95b),['selector95A'])
        self.assertEqual(audit.overlap(0x95b,0x960),['indices95B_95F'])

    def test_table_boundary(self):
        self.assertEqual(audit.overlap(0x9da,0x9db),[])
        self.assertEqual(audit.overlap(0x9db,0xa12),['effect_table'])
        self.assertEqual(audit.overlap(0xa12,0xa13),[])

    def test_descriptor_sparse_cells(self):
        for i in range(12):
            self.assertNotIn('descriptor0',audit.overlap(0xf2+8*i,0xf3+8*i))
            self.assertIn('descriptor0',audit.overlap(0xeb+8*i,0xec+8*i))

    def test_ddc_fallthrough_is_not_a_return(self):
        self.assertEqual(self.r[0xde5]['text'],'move y1,y:(r7)+')
        self.assertEqual(self.r[0xde6]['text'],'move #$000880,r6')
        self.assertEqual(self.r[0xdcf]['text'],'jsr >$0ddc')
        for w in [0xddc,0xdcf,0xdd3,0xde6]:self.assertEqual(audit.ROUTES[w][0],0xdec)

    def test_exact_conditional_records(self):
        self.assertEqual(len(self.records),640)
        self.assertEqual(sum(x['site']==0xdb6 for x in self.records),40)
        self.assertEqual(sum(x['site']!=0xdb6 for x in self.records),600)
        self.assertEqual({x['site'] for x in self.records},{0xdb6,0xdbd,0xdec,0xdf9})
        self.assertFalse(any(x['final_target']==0x1e15 for x in self.records))
        self.assertEqual(len({x['final_target'] for x in self.records if x['site']!=0xdb6}),11)

    def test_original_table_addresses_and_transform(self):
        for x in self.records:
            offset=x['table_address']-0x9db
            self.assertEqual(x['raw_table_value'],self.words[0x29f6+offset])
            expected=x['raw_table_value']+(0 if x['site']==0xdb6 else 1)
            self.assertEqual(x['final_target'],expected)

    def test_16bit_raw_word_constraint_not_selector_domain(self):
        # General transport representation arithmetic, not packet creation.
        self.assertFalse(any(((x&0xffff)<<8) in (0x1e14,0x1e15) for x in range(65536)))
        self.assertGreater((1&0xffff)<<8,14)


if __name__=='__main__':unittest.main()
