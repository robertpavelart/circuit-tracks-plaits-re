# Phase 3: offline DSP analysis

Inputs are read-only. No tool here opens hardware, transmits messages, flashes
or patches firmware. The Rust adapter disassembles words without executing them.

## Decoder

Source: https://github.com/mborgerson/dsp56300, commit
`c60aeedb6a6014850204c71e53bc0cf5b3104222`, MIT license.
Source and license are retained in `builds/vendor/dsp56300-rust/`.
Existing Rust 1.98.0 compiled only the core and disassembler libraries, which
have no external dependencies, plus the small local `dsp_disasm.rs` adapter.
Audit found a bounded enum transmute in core definitions; no networking,
device access or process launch in the compiled library sources.

`build_dsp_decoder.ps1` checks the pinned revision and refuses an existing
build directory. It invokes rustc directly, not cargo/build scripts/emulator.
The decoder's 135 tests and disassembler's 61 tests passed. No new toolchain
or dependencies were installed. Reuse the existing `builds/dsp-tools/` outputs.

A C++ alternative source snapshot in `builds/vendor/dsp56300/`, commit
`44353be2f0156cac970c6ab4f467ea1998b40605`, was inspected but not built or used.
No network is needed to reproduce the delivered analysis.

## Commands

Choose fresh output paths. Example PowerShell commands:

```powershell
$py = 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_dsp_boot.py --output builds/new-boot-records.json
& $py -B tools/ct_dsp_reconstruct.py --output-dir builds/new-memory
& $py -B tools/ct_dsp_disasm.py firmware/dsp/build-4486/selection0-channel0.payload24.bin --output builds/new-main.asm
& $py -B tools/ct_dsp_disasm.py firmware/dsp/build-4486/selection0-channel1.payload24.bin --output builds/new-worker.asm
& $py -B tools/ct_dsp_disasm.py firmware/dsp/build-4486/selection1-channel0.payload24.bin --output builds/new-test.asm
& $py -B tools/ct_dsp_disasm.py firmware/dsp/build-4486/selection1-channel1.payload24.bin --output builds/new-test-worker.asm
& $py -B tools/ct_dsp_disasm.py firmware/dsp/build-4486/bootstrap.payload24.bin --output builds/new-bootstrap.asm
& $py -B tools/ct_arm_calls.py --targets 0x080292F8 0x08029314 0x08029528 0x0801F51E --output builds/new-arm-calls.json
& $py -B tools/ct_dsp_protocol.py '00 80 2c'
& $py -B tools/ct_dsp_protocol.py '20 01 00'
& $py -B tools/ct_phase3_verify.py --output builds/new-verification.json
```

The build command, if a fresh build is required, is `./tools/build_dsp_decoder.ps1`.
On this host downloaded/compiled files may need approved outside-sandbox access.
No script escalates or installs automatically.

Verification uses canonical `builds/phase3-*.asm` and
`firmware/dsp/reconstructed-4486/`. It checks original/extraction hashes,
boot parser bounds and error rejection, NXP APR30 instruction examples, reviewed
ISR branch boundaries, protocol interpretation and copied table source bytes.

`ct_dsp_boot.py` does not invent nested record types. `ct_dsp_disasm.py` calls
the actual upstream decoder; whole-image sweeps include data and are not code
maps. `ct_dsp_protocol.py` interprets supplied bytes with explicit lane/space
context and never sends them. `ct_dsp_reconstruct.py` exports uploaded P words
and four reviewed startup table copies, not a fabricated complete RAM dump.
