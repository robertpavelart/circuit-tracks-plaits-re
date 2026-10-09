# Roadmap

## Completed

- firmware container / SYX reverse engineering
- exact stock round-trip
- DSP payload extraction
- DSP56300 emulator instrumentation
- bounded stock execution
- VariableSaw DSP56300 renderer
- native DIV optimization
- register/scratch optimization
- reachable timing bound
- stock seam mapping
- static checkpoint-limit study
- runtime-snapshot acquisition design
- software-only live-patch design
- bounded X-state ownership study

## Current

### Phase 20C3 — P-backed persistent state

Prove/disprove appended mutable P-state for:
- phase
- next
- previous_pw
- high
- frequency
- pw
- shape

Required:
- MOVEM legality
- runtime persistence
- code/data separation
- loader lifetime
- exact equivalence
- 2048-block continuity
- writer exclusion
- bounded timing

## After that

1. Resolve block-local save/workspace strategy.
2. Qualify extended DSP image layout/relocation.
3. Construct non-canonical offline patched DSP image.
4. Execute dispatcher → Plaits → `P:0x9D9` in emulator.
5. Verify stock fallback.
6. Close USB update/recovery gate.
7. Build a custom firmware candidate only after those gates pass.
8. First hardware PoC: one mono VariableSaw path.
9. Restore stock firmware and confirm rollback.
10. Only then consider Synth2, model switching and polyphony.
