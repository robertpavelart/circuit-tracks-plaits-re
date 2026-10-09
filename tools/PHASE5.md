# Static output-contract analysis

The tool does not emulate or execute firmware. It counts reviewed pointer
advances and selected hardware-loop bodies in existing real disassembly,
checks bytes, and exports two proven table segments.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_voice_contract.py --output-dir builds/phase5-new
```

Use a fresh directory. original/ and existing output directories are refused.
Required inputs: unchanged BIN/SYX, verified DSP payload, phase-3 DSP disassembly
and bounded ARM reports listed in the script. `--dsp-asm` selects regenerated
DSP decoding (see PHASE3.md).

Outputs:

- `contract.json`: source/codec checks, selected-slot map, coefficient aliases,
  block constants and conditional instruction counts.
- `dsp-output-path.asm`: 2,276 byte-checked reviewed instruction rows.
- `X-001600-001940.table24.bin`: 832 upper-24-bit words from ARM upload
  source 0x08052BB4; not a RAM dump.
- `Y-000E37-000E3E.waveinfo24.bin`: seven words of wave-info index1 copied
  from P:0x28E4; not generated waveform samples.

The loop subtotal is not a cycle bound. Explicit profile: three lookup-mask
lanes, nonzero Q+3, Q+4 zero, one repeat each, post mode zero, nonzero
normalization branch. No runtime preset snapshot is invented.
See `notes/voice-output-contract.md` for evidence and remaining ABI/numeric
questions. No hardware, emulator, patch or Plaits implementation was involved.
