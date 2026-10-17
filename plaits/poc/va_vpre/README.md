> Historical experiment scope, not the current global project stop point. [Current state](../../../docs/CURRENT_STATUS.md).

# Phase20F admission and pinned-host VA oracle

The proposed layout failed admission: the 1177-word deletion removes the code shared with MIDI2. The test records all 4096 MIDI2 failures, rather than weakening the regression requirement. No new complete DSP engine was placed or implemented after that rejection. No reference file, hardware or application firmware container is touched.

Reproduction from CIRCUIT:

1. Bundled Python `-B plaits/poc/va_vpre/admission.py` verifies and exports DSP-only original/reduced caller fixtures and deterministic control streams.
2. PowerShell `plaits/poc/va_vpre/build.ps1` builds against the sealed Phase19A interpreter library. Run `builds/phase20f-va-vpre-admission/host/admission.exe builds/phase20f-va-vpre-admission builds/phase20f-va-vpre-admission/run-new` with a fresh output path.
3. PowerShell `plaits/poc/va_vpre/build_oracle.ps1` links original host engine objects from Phase20E with actual pinned Voice. Run `host-oracle/va_oracle.exe controls.tsv oracle-new` using full paths under the Phase20F build directory.
4. `report.py` verifies canonical `run-v1` and `oracle-v1`, including independent mixer arithmetic, unchanged pinned/reference hashes, and writes the report/verification/hashes. It does not automatically switch to exploratory output paths.

The native test uses only a caller stub in the original P tail. It includes existing fixture infrastructure but never calls its earlier overlay entry point. Complete writes and instruction traces remain available. Reduced-path timing measures a broken MIDI2 renderer, not Plaits CPU savings.

The host oracle always renders MODEL8 / VA_VARIANT2. The independent natural 12-sample stream is compared to a full-12-render FIFO scheduler delivering 32 samples. It proves host scheduling/sample/state equivalence, not fixed-point DSP numeric fidelity. No other engine is rendered. The next prerequisite is a real placement plan retaining MIDI2, rather than treating this failed deletion as free space.
