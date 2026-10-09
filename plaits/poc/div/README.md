# Standalone native DIV variant

Phase20A-DIV only; derived VariableSaw arithmetic retains the MIT notices in
../LICENSE. No Circuit image, hardware, stock allocation or integration.

Preferred variant:generate_compact.py (18-word guarded native helper).
generate_div.py retains the initially qualified22-word version. The immutable
restoring fallback remains ../generate.py; ../fixed_model.py remains the oracle.

build.ps1 uses existing MSVC/CMake and sealed Phase19A interpreter libraries.
qualify_compact.py runs isolated bit-level/integer fixtures before oscillator use.
collect_compact.py and verify_div.py adapt the existing full suite only for the
selected helper, fresh output root and new measured resource expectations.
compare.py verifies old/new samples, states, code prefix, controls and provenance,
then measures helper invocation/issued costs from complete traces.

runner.cpp adds helper/DIV counters to the original isolated runner and changes
its allowed output root. fixture.cpp reuses the unchanged baseline assembler
definitions, denies all data-memory/peripheral writes and exports each DIV state.
Neither modifies the sealed core or upstream source.

Use fresh children of builds/phase20a-div. Exact commands, contract, caveats and
measurements:notes/plaits-native-div.md. Canonical results:final-compact/,
fixtures-compact/, checks/, comparison/. Opcode counts are not hardware cycles.
