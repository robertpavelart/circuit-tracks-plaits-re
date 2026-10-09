"""Checkpoint schema/address-domain tests; no numeric symbolic-state substitution."""
import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('checkpoint_collect',ROOT/'emulator/harness/checkpoint/collect.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class CheckpointTests(unittest.TestCase):
    def test_schema_keeps_unknown_values(self):
        s=module.snapshot(module.cases()[0])
        for field in ['A','B','SR','OMR','SP','LC','LA']:
            self.assertIsNone(s['CPU'][field]['value'])
        self.assertEqual(s['CPU']['SR']['known_mask'],1<<13)
    def test_all32_cursor_cells_and_32_iterations(self):
        cs=[c for c in module.cases() if c['kind']==0]
        self.assertEqual(len(cs),4096)
        for f in range(2):
            for j in range(16):
                for m in [0xffff,0x3ff]:
                    for e in [0,1]:
                        group=[c for c in cs if (c['family'],c['j'],c['modifier'],c['encoding'])==(f,j,m,e)]
                        self.assertEqual([c['i'] for c in group],list(range(32)))
    def test_initialized_addresses_miss_targets(self):
        for f in range(2):
            for j in range(16):
                addresses=set(range(module.cursor(f,j),module.cursor(f,j)+32))
                self.assertFalse(addresses&set(range(0x340,0x360)))
                self.assertFalse(addresses&set(range(0x5f00,0x6000)))
    def test_35f_is_never_invented_positive(self):
        for c in module.cases():
            s=module.snapshot(c)
            if c['kind']==2:self.assertEqual(s['X'][str(0x35f)]['value'],0)
            if c['kind']==3:self.assertEqual(s['scope'],'CONSUMER_CALIBRATION_ONLY; positive-count publisher/reachability unproved')
    def test_arithmetic_shadow_not_concrete_snapshot(self):
        for e in [0,1]:
            c=dict(id=0,kind=0,family=0,j=0,i=0,modifier=0xffff,encoding=e)
            s=module.snapshot(c)
            self.assertIsNone(s['CPU']['A']['value']);self.assertIsNone(s['CPU']['B']['value'])
            self.assertEqual(s['CPU']['R7']['value'],0x2ccc)
    def test_zero_record_prefetch_subset(self):
        c=next(c for c in module.cases() if c['kind']==2)
        s=module.snapshot(c)
        self.assertEqual(set(s['X']),set(map(str,range(0x35f,0x364))))
        self.assertEqual(s['Y']['0']['value'],0)
        self.assertEqual(s['CPU']['N5']['value'],0)

if __name__=='__main__':unittest.main()
