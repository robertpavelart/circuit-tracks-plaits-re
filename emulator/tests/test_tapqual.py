"""Documentary design/refusal invariants, NOT hardware/controller qualification."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ct_tapqual import BASE, SRC, build, pin_rows, reports, ranges, coherence_rows, controllers


class TapQualification(unittest.TestCase):
    def test_no_connection_or_capture_admitted(self):
        r=reports()
        self.assertFalse(r['physical-readiness.json']['connection_justified'])
        self.assertFalse(r['tooling-readiness.json']['connection_justified'])
        self.assertFalse(r['future-session-plan.json']['probe_attachment'])
        self.assertFalse(r['future-session-plan.json']['dynamic_capture'])
        self.assertIsNone(r['tooling-readiness.json']['qualified_pair'])

    def test_connection_abort_conditions_complete(self):
        values=reports()['future-session-plan.json']['connection_refusal_if_unknown']
        for word in ['voltage','ground','TAP','electrical','reset','automatic']:
            self.assertTrue(any(word in v for v in values),word)

    def test_package_pins_and_no_invented_TRST(self):
        p={r['signal']:r for r in pin_rows()}
        for signal,a,b in [('TMS','101','55'),('TCK','102','56'),('TDI','103','57'),('TDO','104','58')]:
            self.assertEqual(p[signal]['DSP56724_144_LQFP'],a)
            self.assertEqual(p[signal]['DSP56725_80_LQFP'],b)
        self.assertEqual(p['TRST']['DSP56724_144_LQFP'],'not listed')
        self.assertTrue(all(r['board_net']=='UNRESOLVED' for r in p.values()))

    def test_dual_TAP_no_false_second_IDCODE(self):
        r=reports()['tap-architecture.json']
        self.assertEqual(sum(r['IR_bits']),r['combined_IR_bits'])
        self.assertEqual(r['combined_IR_bits'],8)
        self.assertFalse(r['JTAG0_IDCODE'])
        self.assertNotIn('IDCODE',r['JTAG0_instructions'])

    def test_every_slot_memory_count_and_private_domain(self):
        for slot in range(12):
            for group in range(2):
                rs=ranges(slot,group)
                self.assertEqual(sum(end-start for _,_,start,end,_ in rs)+10,100)
                self.assertTrue(all(0<=start<end<0x30000 for _,_,start,end,_ in rs))
        with self.assertRaises(ValueError): ranges(12,0)

    def test_Y_decimal12_erratum_retained(self):
        y=[r for r in ranges() if r[1]=='Y'][0]
        self.assertEqual(y[2:4],(0x5AB,0x5B9))
        self.assertEqual(sum(r['words'] for r in coherence_rows()[:7]),100)

    def test_no_unsupported_halt_order(self):
        r=reports()['writer-exclusion.json']
        self.assertTrue(r['no_universal_order'])
        self.assertIn('refuse',r['abort'])
        self.assertIn('not a freeze',r['DMAS'])

    def test_tool_support_not_upgraded(self):
        self.assertTrue(all(not r['connection_qualified'] for r in controllers()))
        r=reports()['tooling-readiness.json']
        self.assertEqual(r['status'],'PLAUSIBLE TOOLCHAIN')
        self.assertTrue(r['external_OnCE_preferred'])
        self.assertFalse(r['hook_preferred'])
        self.assertFalse(r['flashing_justified'])

    def test_breakpoint_requires_raw_boundary(self):
        r=reports()['breakpoint-state.json']
        self.assertIn('after',r['acknowledgement'])
        self.assertIn('9DD',r['expected_PABEX'])
        self.assertIn('56D800',r['expected_PIL'])
        self.assertIn('not sufficient',r['PC_warning'])
        self.assertIn('BEFORE',r['first_dump'][0])

    def test_model_root_not_invented(self):
        r=reports()['patch-correlation.json']
        self.assertIn('root must be observed',r['model_formula'])
        self.assertIn('pointer cell',r['data_formula'])
        self.assertTrue(any('cached' in x for x in r['forbidden_shortcuts']))

    def test_report_overwrite_and_source_path_refused(self):
        for p in [BASE,SRC,ROOT/'original',BASE/'../outside-tapqual-test']:
            with self.assertRaises(ValueError): build(p)


if __name__=='__main__': unittest.main()
