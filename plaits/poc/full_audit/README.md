> Historical experiment scope, not the current global project stop point. [Current state](../../../docs/CURRENT_STATUS.md).

# Phase20E audit tools

Read-only source consumption from pinned `plaits/upstream` and the local B1.3 reference. Outputs stay under CIRCUIT; no firmware container or upload route is implemented.

1. Run the bundled Python with `-B plaits/poc/full_audit/inventory.py`. It verifies 183 pinned hashes, inventories 24 model slots and creates the host-only compatibility overlay and probe source.
2. Run `-B plaits/poc/full_audit/reclaim.py`. It uses a read-only assembler-cache shim, verifies the original MIDI DSP module against B1.3 bytes, and records assembler-only deletion counts. Modified program words remain in process memory and are not exported.
3. Run PowerShell `plaits/poc/full_audit/build.ps1`; then `builds/phase20e-full-plaits-audit/host-direct/plaits_probe.exe`, capturing stdout as `builds/phase20e-full-plaits-audit/host-probe.csv`.
4. Run `-B plaits/poc/full_audit/report.py`. It writes `notes/plaits-full-b13-feasibility.md`, machine-readable engine costs (unmeasured DSP costs remain null), and verifies unchanged reference/pinned sources.

The host probe renders each slot for 2048 blocks at size24. Object/arena accounting is measured on x64 MSVC, not DSP memory layout. Host microseconds are not DSP cycles. Terrain's abrupt-stimulus energy anomaly means this is a dependency/layout smoke test, not an audio-fidelity pass. Wavetable initialization demonstrably writes past its declared 64-pointer allocation into a 256-pointer map; the probe intentionally provides a large zero arena and reports allocator use and initialized extent separately.

The CMake file is an alternative host build entry point after inventory creates the compatibility overlay. Direct MSVC was used for the retained run because CMake/Ninja compiler ABI detection stalled. No pinned arithmetic source is edited; the separate overlay addresses GNU/MSVC declarations, attributes, M_PI and one unused empty table only.
