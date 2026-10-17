"""Selected exact image through retained native updater/bootloader harness.
No live transport. All writes are Unicorn RAM/NOR-array or local evidence.
"""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
src=(R/'builds/phase44-preflash-redteam-closure/transition_replay.py').read_text()
src=src.replace("candidate = ((O/'circuittracks-4486-nor-evidence-atomic-test.bin') if atomic else (S/'circuittracks-4486-nor-evidence-test.bin')).read_bytes()","candidate = (O/'circuittracks-final-geometry-gated-nor-test.bin').read_bytes()")
src=src.replace("stream = ((O/'circuittracks-4486-nor-evidence-atomic-test.syx') if atomic else (S/'circuittracks-4486-nor-evidence-test.syx')).read_bytes()","stream = (O/'circuittracks-final-geometry-gated-nor-test.syx').read_bytes()")
exec(compile(src,str(O/'selected-transition-runner.py'),'exec'),dict(__file__=str(O/'install_replay.py'),__name__='__main__'))
