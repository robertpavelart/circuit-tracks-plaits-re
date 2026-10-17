> Historical experiment scope, not the current global project stop point. [Current state](../../../docs/CURRENT_STATUS.md).

# Phase20B4 — project0 association and conditional macro equivalence

Offline cached data only. No Components execution, new dependency, firmware CPU,
hardware or Plaits input. Reuse completed P657 structure and selector proof.
Canonical output: `builds/phase20b-projectassoc/final-v2/`; repeat-v2/checks-v2 alongside.
`probe/` and `final/` preserve earlier exports before the fixed frequency addend
was resolved. Existing evidence is retained.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B plaits/seam/projectassoc/recover.py --output-dir builds/phase20b-projectassoc/new-report
& $py -B plaits/seam/projectassoc/recover.py --output-dir builds/phase20b-projectassoc/new-repeat
& $py -B plaits/seam/projectassoc/verify.py --suite-dir builds/phase20b-projectassoc/new-report --repeat-dir builds/phase20b-projectassoc/new-repeat --output-dir builds/phase20b-projectassoc/new-checks
```

Fresh output directories required. `evidence/` contains focused original ARM
decode windows; the original bytes are checked at each instruction. Data/literal
areas in linear listings are not asserted executable. No new P657 decode/census.
Installed decoder commands use `tools/ct_static.py disasm --start <address>
--end <address> --output <fresh path>`; existing Capstone dependency is used.

Two host integer models independently reconstruct original35F84 macro arithmetic
over the selected ascending assignment domains. These are conditional source-code
calculations, not executed ARM/DSP or event snapshots. Project-load macro values
can differ materially while event-time automation remains unknown. The gate never
admits an event from patch name, raw note-looking bytes or a partial chain.
