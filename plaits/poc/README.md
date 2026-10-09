# Standalone VariableSaw-derived DSP56300 PoC

Phase20A study only. No Circuit image/peripherals, memory reservation or integration.
Pinned MI reference remains unmodified. Derived arithmetic is described in LICENSE
and notes/plaits-fixed-point.md; results in notes/plaits-variablesaw-poc.md.

Generate assembly using generate.py; build the reference/interpreter wrapper with
build.ps1; collect.py renders and repeats the complete suite; verify using
emulator/tests/verify_variablesaw.py. Fresh directories under builds/phase20a-plaits
are required. Uses existing installed tools and the sealed Phase19A library.

The program is708 words; oscillator state7, transient44, input3, output32, tables0.
All output is offline data. Native costs are issued opcodes, not hardware timing.
The future control/multivoice/stock filter/envelope architecture is unimplemented.

Phase20A-DIV adds a preferred native helper in div/ without changing this
restoring reference. Native variant700P, exact same samples/state, mean5138.4363
issued/32. See div/README.md and notes/plaits-native-div.md.
