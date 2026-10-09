# Phase20B5 — bounded static sequencer provenance

No firmware CPU, Components launch, download, hardware, MIDI/SysEx, patching or
Plaits input. Reuse Phase20B4 seven-byte/macro arithmetic and Phase20B3 P657
structure. Fresh reports preserve all previous evidence.

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B plaits/seam/sequence/recover.py --output-dir builds/phase20b-sequence/reproduce-new
& $taskPython -B plaits/seam/sequence/recover.py --output-dir builds/phase20b-sequence/repeat-new
& $taskPython -B emulator/tests/test_sequence_context.py
& $taskPython -B plaits/seam/sequence/verify.py --suite-dir builds/phase20b-sequence/reproduce-new --repeat-dir builds/phase20b-sequence/repeat-new --output-dir builds/phase20b-sequence/checks-new
```

Canonical reports: `builds/phase20b-sequence/final/`; `repeat/` and validated
`checks-v2/` alongside. Earlier `checks/` preserves the repeat check before
the corruption-test fixture was corrected; use `checks-v2/` for test results.
Decoder evidence is reproducible with existing `tools/ct_static.py disasm --start
<address> --end <address> --output <fresh path>`. Each filename/listing records its
range; bytes are checked against the original image without requiring Capstone
for export/repeat. Literal pools/partial boundaries in linear listings are not
asserted executable. `clock-pattern-consumer.asm` is exploratory: only2520A's
BX LR stub is relevant; subsequent file routines are unrelated.

The constructor passes **12** as the final base parameter-count argument.139
is the separate packed note-key table domain; do not confuse it with automation
lanes or DSP voices. The exported graph distinguishes constructors, editor/view
storage, note recording and pending automation writers from audible dispatch.

**PARTIAL / STATIC STRATEGY EXHAUSTED.** No exact first note, active playback
branch, pre-note automation, allocated voice or numerical history is admitted.
The runtime snapshot is a specification, not an acquired or runnable checkpoint.
It separates post-only replay requirements from optional upstream event evidence.
