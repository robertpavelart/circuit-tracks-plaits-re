"""Static provenance refusal checks, not DSP execution or playback tests."""
import json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'plaits/seam/sequence'))
import recover
class SequenceContext(unittest.TestCase):
    def setUp(self):
        self.report=ROOT/'builds/phase20b-sequence/final'
    def data(self,name): return json.loads((self.report/name).read_text())
    def test_no_runtime_event_from_serialized_notes(self):
        e=self.data('first-note-event.json')
        self.assertEqual([r['raw'] for r in e['candidates']],[[51,18,0,106],[82,2,0,106]])
        self.assertIsNone(e['exact_first_dispatched_note']);self.assertFalse(e['qualified'])
    def test_geometry_partitions_pattern(self):
        p=self.data('pattern0-structure.json')
        self.assertEqual(32*28,896);self.assertEqual(936+12*32*6,p['bytes'])
        self.assertEqual(len(p['steps']),32);self.assertEqual(len(p['automation']),12)
        self.assertIsNone(p['active_pattern_length'])
    def test_empty_macro_lanes_do_not_force_runtime_value(self):
        p=self.data('pattern0-structure.json')
        self.assertTrue(all(v==255 for r in p['automation'][1]['step_records'] for v in r))
        self.assertEqual(p['automation'][9]['step_records'][0][0],127)
        self.assertEqual(self.data('equivalence.json')['first_note_runtime'],'INSUFFICIENT EVIDENCE')
    def test_each_missing_gate_refuses(self):
        fields=[True]*5+['MATERIALLY EQUIVALENT']
        self.assertTrue(recover.admitted(*fields))
        for i in range(6):
            f=fields.copy();f[i]=False if i<5 else 'INSUFFICIENT EVIDENCE'
            self.assertFalse(recover.admitted(*f))
    def test_snapshot_space_strides(self):
        rows=self.data('runtime-snapshot-minimum.json')['minimal_replay_ranges']
        self.assertEqual(rows[0]['slot0'],'[5AB,5BE)');self.assertEqual(rows[1]['slot0'],'[5AB,5B9)')
        self.assertNotEqual(0x4a,0x28)
        self.assertEqual(0x59f+0x1a,0x5b9)
    def test_no_replay_admission(self):
        q=self.data('qualification.json')
        self.assertFalse(q['checkpoint_resume']);self.assertEqual(q['original_instructions_executed'],0)
        self.assertEqual(q['static_strategy'],'EXHAUSTED')
    def test_truncated_pattern_refused(self):
        with self.assertRaises(ValueError): recover.parse_pattern(bytes(100))
    def test_overwrite_and_outside_refused(self):
        for p in [self.report,recover.BASE,ROOT/'notes']:
            with self.assertRaises(ValueError): recover.recover(p)
    def test_corrupt_disassembly_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.asm';p.write_text('08010000  ffff  corrupt\n')
            arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
            with self.assertRaises(ValueError): recover.arm_evidence(p,arm)
if __name__=='__main__': unittest.main()
