"""Targeted safety/qualification tests; never execute a DSP or open a device."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('parent_audit',ROOT/'emulator/harness/parent/audit.py')
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class ParentGateTests(unittest.TestCase):
    def test_structural_state_cannot_open_normal_gate(self):
        with self.assertRaisesRegex(ValueError,'no verified target-producing predecessor'):
            audit.require_normal_checkpoint()

    def test_no_arbitrary_proof_override(self):
        with self.assertRaises(TypeError):
            audit.require_normal_checkpoint(normal=True,SP=3,LF=0)

    def test_opcode_looking_like_address_is_not_edge(self):
        for text in ['lsl a1,b','do #$0005,$0db0','move x:$1ee5,x1','dc $001e15']:
            self.assertIsNone(audit.direct_target(text))
        self.assertEqual(audit.direct_target('jsr $1f5c'),0x1f5c)
        self.assertEqual(audit.direct_target('jeq $1e31'),0x1e31)
        self.assertEqual(audit.direct_target('jsr >$0db2'),0xdb2)

    def test_guard_unknown_never_defaults_to_zero(self):
        self.assertIsNone(audit.family_calls(None))
        self.assertEqual(audit.family_calls(0),[0x1e80,0x1ee5])
        for x in [4,8,12]:self.assertEqual(audit.family_calls(x),[0x1ee5])
        with self.assertRaises(ValueError):audit.family_calls(3)

    def test_immutable_instruction_witness(self):
        payload,_=audit.verify_inputs()
        listing=ROOT/'builds/phase3-selection0-channel0.asm'
        self.assertEqual(audit.rows(listing,payload)[0x1e15]['text'],'move r6,x:$1d3a')
        changed=bytearray(payload);changed[0x1e15*3]^=1
        with self.assertRaisesRegex(ValueError,'byte mismatch'):
            audit.rows(listing,changed)

    def test_destination_confinement(self):
        for p in [ROOT/'original/new',ROOT/'firmware/new',ROOT/'builds/phase19c-parent',ROOT/'notes/new']:
            with self.assertRaises(ValueError):audit.fresh_output(p)

    def test_overwrite_refusal(self):
        base=ROOT/'builds/phase19c-parent'
        base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='test-',dir=base) as d:
            p=Path(d);sentinel=p/'sentinel';sentinel.write_bytes(b'preserve')
            with self.assertRaises(ValueError):audit.fresh_output(p)
            self.assertEqual(sentinel.read_bytes(),b'preserve')


if __name__=='__main__':unittest.main()
