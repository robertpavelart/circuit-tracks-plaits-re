"""Offline seam preflight. No device APIs, emulator import or guessed checkpoint.

Original stock entry cannot be admitted by naming a synthetic preset. Concrete
branch/address/scaling/stack fields require qualified evidence. Current evidence
leaves these null and therefore fails before any CPU or output-buffer creation.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def checkpoint_obligations():
 return [
  dict(field='X:0x5AB',value=None,role='post dispatch selector',producer='P:0x47D/47E',consumer='P:0x9DD..9E9',
       blocker='CONTROL_FLOW',reason='producer reads bank parameter; no qualified selected-preset value at this seam'),
  dict(field='X:0x5AC',value=None,role='nonlinear selector',producer='P:0x47F/480',consumer='P:0xAA8,AB0..AC8',
       blocker='CONTROL_FLOW',reason='selects nonlinear branches; a previous analyst mode-zero witness is not a concrete stock value'),
  dict(field='X:0x5AD / Y:0x5AB',value=None,role='nonlinear target and retained previous state',producer='P:0x481; retained Y state',consumer='P:0xACC..B1C',
       blocker='ARITHMETIC_TO_ADDRESS',reason='normalization/index result N5 selects X:(r5+n5); table and range depend on state'),
  dict(field='X:0x5AE',value=None,role='input multiplicative scale',producer='P:0x487',consumer='P:0xBDF,BE3,BE7',
       blocker='ARITHMETIC_SCALING',reason='no calibrated stock sample unit/headroom or selected coefficient value'),
  dict(field='X:0x5AF / X:0x5B0 / Y:0x5AE',value=None,role='recursive coefficient-control evolution',producer='P:0x48B,498; retained Y state',consumer='P:0xBEC..C09,C2D..C87',
       blocker='ARITHMETIC_TO_ADDRESS',reason='computed table row/index and coefficient interpolation need defensible numeric domains'),
  dict(field='X:0x5B1',value=None,role='first coefficient-sequence offset',producer='P:0x49A',consumer='P:0xC10..C18',
       blocker='EFFECTIVE_ADDRESS',reason='r5=0xF5F+word; cannot replace with an invented filter selection'),
  dict(field='X:0x5B2',value=None,role='second coefficient-sequence offset',producer='P:0x49B',consumer='P:0xC1A..C22',
       blocker='EFFECTIVE_ADDRESS',reason='r5=0xF5F+word; actual legal selected sequence unresolved'),
  dict(field='SR arithmetic/mode bits',value=None,role='SM,SA,DM,SC,scaling and rounding',producer='P:0x10A sets RM; ROM/other modes unresolved',consumer='MPY/MAC/MACR/full accumulator transfers; CA2/CB6 change S1',
       blocker='ARITHMETIC_SCALING',reason='reset defaults are not the authentic ROM handoff; do not silently set SR=0x300'),
  dict(field='M0..M7 / Y:0x19,0x1A',value=None,role='address generation and restore modifiers',producer='P:0x2779..2781 initialization, temporary mode writes/restore',consumer='indirect/postincrement accesses; ADC/B24',
       blocker='MODIFIER',reason='initialized 0xFFFF is known; preservation at selected entry and mode-specific restored modifiers are not qualified'),
  dict(field='SP/SC/SSH/SSL/LA/LC/LF/FV',value=None,role='inherited return/loop context',producer='caller chain plus completed local DOs',consumer='nested JSR/DO and return',
       blocker='STACK_LOOP',reason='actual or selected defensible resident-prefix/active-loop checkpoint missing; do not set depth/LF to zero'),
  dict(field='X:0x2C66 entry guard / sticky CCR',value=None,role='last preload and executed multiply',producer='neighbor scratch history',consumer='BE6/BE7 before first C9F overwrite; A93 reads later history',
       blocker='GUARD_STATUS',reason='selected output term is dead, but full CCR/state independence across unqualified modes is not proved'),
 ]

class ReplayRefused(ValueError):pass

def require_qualified_checkpoint():
 missing=checkpoint_obligations()
 # No override/default/guess flag. This is intentionally not a CPU constructor.
 raise ReplayRefused('; '.join(f"{r['field']}: {r['blocker']}" for r in missing))

def readiness():
 return dict(admitted=False,status='UNRESOLVED / REFUSED BEFORE CPU',entry=0x9d9,
             first_post_dispatch=0x9dd,group_boundary=0xa95,
             concrete_checkpoint=None,blockers=checkpoint_obligations(),
             stock_instructions_executed=0,hardware_access=False,
             integration=False,persistent_RAM_safety=False)
