"""Focused symbolic contract tests. Concrete fixture values are not ROM seeds.
Positive peripheral tests contain no stock CPU/image. Original runs keep all
unproved fields unknown and must stop before their first instruction.
"""
import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'emulator/harness'))
from partial_state import Partial,RegisterCell,ICC,BlockingUnknown,interrupt_eligibility
from symbolic_startup import Startup,bootstrap_history

class PartialTests(unittest.TestCase):
    def test_unknown_cannot_be_zero(self):
        with self.assertRaises(BlockingUnknown):Partial.unknown('unproved word').require('value')
    def test_noncanonical_value_rejected(self):
        with self.assertRaises(ValueError):Partial(24,0,1)
    def test_known_and_width(self):
        self.assertEqual(Partial.concrete(0xffffff,'fixture').require('fixture'),0xffffff)
        with self.assertRaises(ValueError):Partial.concrete(0x1000000,'fixture')
    def test_gpio_clear_unknown_word(self):
        cell=RegisterCell(0xfffffa,'symbolic fixture latch');t=cell.bit_operation(13,False,'bitop')
        self.assertEqual(cell.value.known_mask,0x2000);self.assertEqual(cell.value.known_value,0)
        self.assertEqual(t['carry']['known_mask'],0)
    def test_gpio_set_unknown_word(self):
        cell=RegisterCell(0xfffff9,'symbolic fixture latch');cell.bit_operation(13,True,'bitop')
        self.assertEqual(cell.value.known_mask,0x2000);self.assertEqual(cell.value.known_value,0x2000)
    def test_unrelated_known_and_unknown_bits_preserved(self):
        v=Partial(24,0x80,0x80,('known fixture bit7',));after,c=v.bclr(13,'clear')
        self.assertEqual(after.known_mask,0x2080);self.assertEqual(after.known_value,0x80)
        self.assertEqual(c.known_mask,0);self.assertEqual(after.bit(12).known_mask,0)
    def test_carry_uses_old_bit(self):
        v=Partial(24,0x2000,0x2000,('known fixture bit13',));new,c=v.bclr(13,'clear')
        self.assertEqual(c.require('carry'),1);self.assertEqual(new.bit(13).require('bit13'),0)
    def test_small_bit_equivalence_classes(self):
        # Three finite fixture bits, not a24-bit state search or stock handoff.
        for number in range(8):
            value=((number&1)<<13)|((number&2)<<5)|((number&4)<<7)
            v=Partial.concrete(value,'finite fixture class')
            clear,c=v.bclr(13,'clear');setv,cs=v.bset(13,'set')
            self.assertEqual(clear.require('fixture'),value&~0x2000)
            self.assertEqual(setv.require('fixture'),value|0x2000)
            self.assertEqual(c.require('fixture'),(value>>13)&1)
            self.assertEqual(cs.require('fixture'),(value>>13)&1)
    def test_eq_unknown_blocks_branch(self):
        z=Partial.unknown('ICDR4').equal(Partial.concrete(0x30002,'compare literal'))
        with self.assertRaises(BlockingUnknown):z.require('conditional branch')
    def test_eq_known_mismatch_proves_false(self):
        v=Partial(24,1,1,('fixture lowbit',));z=v.equal(Partial.concrete(0x30002,'literal'))
        self.assertEqual(z.require('branch'),0)
    def test_all_material_uses_deny_unknown(self):
        for use in ['effective X address','P jump destination','DO count','REP count','DMA count','DMA address','modulo modifier']:
            with self.subTest(use=use),self.assertRaises(BlockingUnknown):Partial.unknown('fixture source').require(use)
    def test_no_pending_makes_mask_irrelevant(self):
        d=interrupt_eligibility(Partial.concrete(0,'synthetic no request',1),Partial.unknown('IPL',2),Partial.unknown('I',2))
        self.assertEqual(d.require('synthetic boundary'),0)
    def test_all_unresolved_irq_inputs_block(self):
        d=interrupt_eligibility(Partial.unknown('pending',1),Partial.unknown('IPL',2),Partial.unknown('I',2))
        with self.assertRaises(BlockingUnknown):d.require('interrupt eligibility')
    def test_masked_request_need_not_be_absent(self):
        d=interrupt_eligibility(Partial.unknown('pending',1),Partial.concrete(2,'fixture IPL',2),Partial.concrete(3,'fixture I',2))
        self.assertEqual(d.require('boundary'),0)
    def test_nmi_not_suppressed_by_mask3(self):
        d=interrupt_eligibility(Partial.concrete(1,'fixture pending',1),Partial.concrete(3,'fixture NMI',2),Partial.concrete(3,'fixture I',2))
        self.assertEqual(d.require('boundary'),1)
    def test_equal_mask_and_level_is_eligible(self):
        d=interrupt_eligibility(Partial.concrete(1,'pending',1),Partial.concrete(1,'IPL',2),Partial.concrete(1,'I',2))
        self.assertEqual(d.require('boundary'),1)
    def test_bootstrap_history_not_promoted_across_ROM(self):
        h=bootstrap_history();self.assertEqual(h['pre_second_ROM_OMR']['known_mask'],0x600080)
        self.assertEqual(h['pre_second_ROM_OMR']['known_value'],0x400080)
        self.assertEqual(h['pre_second_ROM_C']['known_mask'],0)
        self.assertEqual(h['application_OMR']['known_mask'],0)
        self.assertEqual(h['application_C']['known_mask'],0)
    def test_ICC_before_publication_unknown_not_30002(self):
        c=ICC();self.assertEqual(c.data.known_mask,0)
        with self.assertRaises(BlockingUnknown):c.receive('synthetic reader')
        self.assertEqual(c.transactions,[])
    def test_ICC_original_state_cannot_publish(self):
        c=ICC()
        with self.assertRaises(BlockingUnknown):c.publish(Partial.concrete(0x123456,'synthetic payload'),'fixture writer')
        self.assertEqual(c.data.known_mask,0);self.assertEqual(c.transactions,[])
    def test_ICC_qualified_pending_transfer_ACK(self):
        c=ICC();c.enable=Partial.concrete(1,'synthetic documented enabled case',1)
        c.pending=Partial.concrete(0,'synthetic empty-before-write case',1)
        payload=Partial.concrete(0x123456,'synthetic writer value')
        c.publish(payload,'fixture writer');self.assertEqual(c.pending.require('fixture'),1)
        self.assertEqual(c.receive('fixture reader'),payload)
        self.assertEqual(c.pending.require('fixture'),0);self.assertEqual(c.ack.require('fixture'),1)
        self.assertEqual(c.data,payload)
    def test_disabled_or_empty_read_not_invented(self):
        c=ICC();c.enable=Partial.concrete(0,'synthetic disabled case',1)
        with self.assertRaises(BlockingUnknown):c.receive('reader')
    def test_original_main_keeps_unknowns_and_stops(self):
        c=Startup('main',(ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin').read_bytes())
        result=c.run(8);self.assertEqual(result['stock_symbolic_instructions_executed'],0)
        self.assertEqual(result['stop_PC'],0);self.assertEqual(c.sr.known_mask,0)
        self.assertEqual(c.transaction_log,[])
    def test_original_worker_keeps_unknowns_and_stops(self):
        c=Startup('worker',(ROOT/'firmware/dsp/build-4486/selection0-channel1.payload24.bin').read_bytes())
        self.assertEqual(c.run(8)['stock_symbolic_instructions_executed'],0)
        self.assertEqual(c.pending.known_mask,0)
    def test_identity_abort_before_symbolic_execution(self):
        with self.assertRaises(ValueError):Startup('main',b'\x12\x34\x56')

if __name__=='__main__':unittest.main()
