# Static voice-event trace

No firmware execution, peripheral access, MIDI/SysEx transmission or binary
patching is involved. Scripts only read files and create fresh reports.
See `notes/voice-descriptor-map.md` for the reviewed instruction-level data flow.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_phase4_trace.py --output-dir builds/phase4-new
```

This consumes phase-3 DSP disassembly and bounded ARM reports listed in
`ARM_REPORTS`, checks machine-code bytes against the ARM image and DSP payload,
and verifies the codec baseline. It writes an address map for all twelve slots
and a bounded DSP excerpt. It is neither an emulator nor a proof of every annotation.

Regenerate decoding if necessary, using fresh output names:

```powershell
& $py -B tools/ct_static.py disasm --start 0x080219E8 --end 0x08021CE4 --output builds/events-new.asm
& $py -B tools/ct_dsp_disasm.py firmware/dsp/build-4486/selection0-channel0.payload24.bin --origin 0 --start 0 --end 0x2A5E --output builds/normal-dsp-new.asm
```

The second command needs the existing decoder documented in PHASE3.md.
Use `ct_phase4_trace.py --dsp-asm builds/normal-dsp-new.asm` to select it.
All outputs refuse overwrites. No new large tools were installed in phase 4.

External MIDI parser origin, UI bank names, physical DSP core/channel assignment
and every branch-dependent gain alias remain separately labeled in the map.
No absolute Hz, sample-rate calibration, recording or cycle budget was measured.
Formula examples evaluate reviewed integer expressions only.

Best next step: reconstruct one concrete parameter configuration and follow
both passes of P:0x77F symbolically to resolve final gain aliases and a complete
per-voice input/output contract before integration.
