"""Qualification guards and arithmetic boundaries, no stock replay/hardware."""
import importlib.util, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ct_pstate_prepare import INIT, STATE
from ct_pstate_verify import normalize, program, instruction_equivalence, ownership
import tempfile

class PStateContract(unittest.TestCase):
    def test_exact_seed(self):
        seed=(ROOT/'builds/phase20c-pstate/source-v7/low-p/state-init.be24').read_bytes()
        self.assertEqual(len(seed),21)
        self.assertEqual([int.from_bytes(seed[i:i+3],'big') for i in range(0,21,3)],INIT)
        self.assertEqual(INIT,[0,0,0x200000,0,41943,0x200000,0])

    def test_region_cardinality_and_no_overlap(self):
        self.assertEqual(STATE+7,0x2d30)
        for name in ['low-p-v7','high-p-v7','high-x-v7']:
            p,l,_=program(ROOT/'builds/phase20c-pstate'/name)
            self.assertLess(l['done']+2,STATE)
            self.assertFalse(any(STATE<=a<STATE+7 for a in p))

    def test_only63_state_sites(self):
        p,_,_=program(ROOT/'builds/phase20c-pstate/high-p-v7')
        self.assertEqual(sum(s['assembly'].startswith('movem ') for s in p.values()),63)
        self.assertFalse(any('x:>$00002' in s['assembly'] for s in p.values()))

    def test_instruction_contract(self):
        base=ROOT/'builds/phase20a-regopt/final/dsp-first'
        for name in ['low-p-v7','high-p-v7','high-x-v7']:
            instruction_equivalence(base,ROOT/'builds/phase20c-pstate'/name)

    def test_standalone_never_promotes_ownership(self):
        with tempfile.TemporaryDirectory() as d:
            report=ownership(Path(d))
            self.assertEqual(report['overall'],'REFUSED')
            self.assertEqual(report['proven_owned_stock_P_words'],0)
            self.assertFalse(report['candidate_in_current_stock_upload'])
            self.assertFalse(report['stock_lifetime_pass'])
            self.assertEqual(report['operand_reference_count'],16)
            self.assertTrue(report['operand_words_byte_verified'])

    def test_pmemory_is_distinct_from_sample_buffer(self):
        self.assertEqual(normalize('movem p:>$002d2f,y0'),'move x:$000026,y0')
        self.assertNotEqual(STATE,0)

if __name__=='__main__': unittest.main()
