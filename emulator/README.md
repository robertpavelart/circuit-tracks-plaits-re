# Offline synthetic DSP56300 fixtures

This is Phase19A's execution substrate, not a Circuit Tracks emulator.
No device API, MIDI/SysEx, updater, firmware loader or stock startup is exposed.
Only hand-auditable synthetic fixture programs were executed.

Core revision: `44353be2f0156cac970c6ab4f467ea1998b40605` (GPLv3).
AsmJit source dependency: `3577608cab0bc509f856ebf6e41b2f9d9f71acc4`.
DSP execution uses `DSP56K_FORCE_INTERPRETER=1` and a compile-time assertion.
AsmJit/JIT classes remain linked by the upstream implementation; JIT DSP execution
and JIT instrumentation are disabled. No toolchain was installed.

Run from the project root:

```powershell
./emulator/build.ps1 -BuildDir builds/phase19a/new-build
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B emulator/tests/run.py --exe builds/phase19a/new-build/ct_replay_fixture.exe --output-dir builds/phase19a/new-tests
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B emulator/tests/audit_paths.py --results builds/phase19a/new-tests/results.json --output builds/phase19a/new-audit.json
```

Fresh trace/test/audit paths are required. Final evidence is
`builds/phase19a/validated/`, `validated-repeat/`, and `reproducibility-final.json`.
The earlier `final/`, `repeat/` and original reproducibility report cover the
interim34-fixture suite, superseded by37 fixtures including remaining DMA branches.

Canonical source provenance is `harness/source-manifest.json` plus
`harness/harness-manifest.json`, exact `overlay/` files and the normalized
`instrumentation.patch` review diff. `upstream/provenance.json` records initial
preparation only and is superseded by those manifests. To reproduce the local
source tree at a fresh workspace path, use `harness/prepare.py --output-dir PATH`.
The source/site guard rejects changed or unregistered files; update manifests
only after explicit code review and new relevant coverage, never automatically
as a way to make a failed audit pass.

Generic fixture memory is explicitly zero initialized. This is not a stock
startup checkpoint. Configurable P/X/Y bounds, declared toy shared aliases,
selected read watches and explicit faults are implemented. Complete chip/ISA/
stock state, peripheral timing and worker fidelity remain unvalidated. Parallel
address-register metadata is null when ambiguous; fixture annotations do not
constitute a general stock semantic decoder. No allocation inference follows.
