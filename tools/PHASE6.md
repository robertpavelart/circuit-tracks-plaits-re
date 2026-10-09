# Static Phase 6 reproduction

From the project root in PowerShell, with existing Python and existing reports:

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_resource_audit.py --output-dir builds/phase6-audit
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_voice_contract.py --output-dir builds/phase6-corrected-contract
```

Choose a fresh directory for each run. Existing directories and original/
destinations are refused; firmware inputs are read only. No hardware is
accessed and no DSP code is executed. No new dependency is needed.

Prerequisites: Phase 3 canonical disassembly, reconstruction manifest,
Phase 4/5 ARM evidence reports and Phase 6 ARM reports named in the script.
The export is intentionally a conservative inventory, not a free-space proof.
Candidate CFG nodes may miss indirect targets and do not justify dead-code
removal. CSV ranges can overlap; indirect accesses remain unresolved.

`audit.json` contains decoded clock fields, conditional resource capacities,
source hashes/roundtrip status, buffer-base references, corrected loop costs,
voice-count scaling and unresolved transfers. `memory-map.csv` is the region
ledger; `access-inventory.csv` includes immediate, absolute and unresolved
indirect references. `candidate-code.asm` is byte-checked candidate traversal.

Phase 5 loop counts of 3,635 are superseded: X:3C=31 applies to two loops
previously counted with 15 iterations. Corrected subtotal is 4,355 issued
instructions, still not a cycle estimate or complete worst-case bound.
