> Historical experiment scope, not the current global project stop point. [Current state](../../../docs/CURRENT_STATUS.md).

# Phase20B3 static input qualification

No CPU execution is enabled. Reuse the selected authored patch and earlier
selector provenance. Reports distinguish source bytes from active corrected
controls and retain all numerical unknowns. Use fresh output directories:

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B plaits/seam/inputrec/recover.py --output-dir builds/phase20b-inputrec/new-report
& $py -B plaits/seam/inputrec/recover.py --output-dir builds/phase20b-inputrec/new-repeat
& $py -B plaits/seam/inputrec/verify.py --suite-dir builds/phase20b-inputrec/new-report --repeat-dir builds/phase20b-inputrec/new-repeat --output-dir builds/phase20b-inputrec/new-checks
```

Canonical report: `builds/phase20b-inputrec/final-v3/`. It contains all requested
exports, fresh DSP decoding, control conversions and source manifests.
`final/` is an incomplete first export: its end address cut a two-word JSR.
`final-v2/` is an earlier successful export before the added control-conversion
table. Preserve both as development evidence; neither is the final report.
The corrected range ends at P:1ACD, an instruction boundary.

Tests exercise source association, last-row lookahead, correction dependence,
history exclusions and refusal before CPU execution. Byte checking establishes
source identity, not complete semantic or generic indirect-write coverage.
