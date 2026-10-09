# Offline firmware analysis

These scripts read local files only. They contain no MIDI, USB, serial-device,
debugger, flashing, or network operations. Outputs use exclusive creation;
`original/` is prohibited as a destination. Existing firmware stays untouched.
The original `ct_fw_tool.py` is unchanged; use its `roundtrip` command without
`--output`, since its other commands can overwrite paths.

Python available for this project:

```powershell
$py = 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_fw_tool.py roundtrip original/circuittracks-firmware-4486.syx
& ./tools/run_recon.ps1 -Python $py -OutputDirectory './builds/new-run'
```

Choose a fresh output directory for every run. The complete workflow is offline
after Capstone is installed. Capstone 5.0.9 is pinned in
`requirements-static.txt` and installed locally in `builds/python-deps`.
On this Windows host those installed dependency files were inaccessible to the
sandbox; the disassembly commands were run with approved external access.
The workflow fails on missing dependencies; it never installs tools itself.

Individual commands (all output paths must be fresh):

```powershell
& $py -B tools/ct_static.py baseline --output builds/new-baseline.json
& $py -B tools/ct_static.py survey --output builds/new-survey.json
& $py -B tools/ct_static.py xrefs --target 0x0801F5F0 --output builds/new-xrefs.json
& $py -B tools/ct_static.py disasm --start 0x0801F554 --end 0x0801F5C6 --output builds/new-upload.txt
& $py -B tools/ct_static.py extract --offset 0x1F0 --size 32544 --output builds/new-candidate.bin
& $py -B tools/ct_data_decode.py --output builds/new-data.bin --report builds/new-data.json
& $py -B tools/ct_dsp_extract.py --output-dir builds/new-dsp
& $py -B tools/ct_evidence.py --output builds/new-evidence.json
& $py -B tools/ct_verify.py --reports builds/repro --dsp firmware/dsp/build-4486
```

`survey` records 114 candidate vector entries and printable ASCII runs of four
or more characters. ASCII runs can contain accidental text in code/data; their
start can precede an actual string (the version at 0x080101CE is one example).
`xrefs` scans every halfword for branches, ADR, PC-relative ADDW/SUBW, literal
loads and MOVW/MOVT pairs, and every byte for pointers. Results are candidates:
code/data boundaries, alternate instruction alignment, register-derived
addresses, and indirect calls still require inspection.

`disasm` performs a bounded linear sweep with skipped undecodable bytes and
annotated literal loads; it does not identify functions automatically. Data can
decode as instructions. `ct_evidence.py` records only reviewed code ranges and
labels branches separately from calls; analyst names are not original symbols.

`ct_data_decode.py` translates the startup decompressor into Python to
reconstruct initialized data. It does not execute firmware or access device RAM.
Its compression is unrelated to the uncompressed DSP streams.
`ct_dsp_extract.py` exports exact header-inclusive streams, payload-only copies,
24-bit word listings and a provenance manifest. Channel numbers are ARM API
arguments; assigning them to physical DSP cores remains a hypothesis.
