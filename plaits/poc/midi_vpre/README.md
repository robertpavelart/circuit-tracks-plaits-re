> Historical experiment scope, not the current global project stop point. [Current state](../../../docs/CURRENT_STATUS.md).

# One-track offline vpre integration

Read `notes/plaits-midi-vpre-offline.md` for the exact evidence scope and gates.

`prepare.py` reads the CIRCUITS-HACKS uploader/manifest and reconstructs its image only in memory. It exports a DSP-only fixture under `builds/phase20d-midi-vpre/fixture`, never an application BIN/SYX. The reference repository is never imported as a Python module or modified.

`runner.cpp` links the unchanged Phase19A interpreter, relocates only sealed renderer operands/return convention, executes the actual reference DSP mailbox/vpre and stock strip mixer, and records strict data access, canaries, ABI, oracle inputs and the control track. Its P overlay is synthetic and cannot be used as a firmware allocation.

`experiment.py` supplies source-derived mailbox stimuli and independently verifies every rendered sample/state using the unchanged integer oracle. It does not emulate the ARM instruction path; missing authentic dumps/Unicorn remain explicit UNKNOWNs.

Build with `./plaits/poc/midi_vpre/build.ps1`. Use a fresh output directory for every runner invocation. The report gives safe offline reproduction commands. No uploader or hardware interface exists in this harness.
